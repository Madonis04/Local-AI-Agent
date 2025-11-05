# memory/vectorstore.py
import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer
import uuid
from datetime import datetime
from pathlib import Path
from config_manager import config
from logger import logger


class VectorMemoryStore:
    """
    Long-term memory storage using ChromaDB for semantic search.
    Stores and retrieves conversation history with semantic understanding.
    """
    
    def __init__(self):
        self.enabled = config.getboolean('Memory', 'use_vector_db', fallback=True)
        if not self.enabled:
            logger.info("Vector database disabled in config")
            return
            
        logger.info("Initializing vector memory store...")
        
        # Setup paths
        data_dir = Path(config.get('Paths', 'data_directory', fallback='.agent_data'))
        self.db_path = data_dir / 'chromadb'
        self.db_path.mkdir(parents=True, exist_ok=True)
        
        # Initialize ChromaDB
        try:
            self.client = chromadb.PersistentClient(
                path=str(self.db_path),
                settings=Settings(
                    anonymized_telemetry=False,
                    allow_reset=True
                )
            )
            
            # Get or create collection
            self.collection = self.client.get_or_create_collection(
                name="conversations",
                metadata={"description": "Agent conversation history"}
            )
            
            # Load embedding model
            embedding_model = config.get('Memory', 'embedding_model', fallback='all-MiniLM-L6-v2')
            logger.info(f"Loading embedding model: {embedding_model}")
            self.embedding_model = SentenceTransformer(embedding_model)
            
            logger.info(f"Vector memory initialized with {self.collection.count()} memories")
            
        except Exception as e:
            logger.error(f"Failed to initialize vector store: {e}")
            self.enabled = False
            raise
    
    def add_conversation(self, user_input: str, agent_response: str, tools_used: list = None):
        """
        Store a conversation exchange in the vector database.
        
        Args:
            user_input: What the user said
            agent_response: Agent's response
            tools_used: List of tools used (optional)
        """
        if not self.enabled:
            return
            
        try:
            # Create unique ID
            conv_id = str(uuid.uuid4())
            timestamp = datetime.now().isoformat()
            
            # Combine for embedding (semantic search on full context)
            combined_text = f"User: {user_input}\nAssistant: {agent_response}"
            
            # Generate embedding
            embedding = self.embedding_model.encode(combined_text).tolist()
            
            # Prepare metadata - use Unix timestamp for reliable sorting
            unix_timestamp = datetime.now().timestamp()
            
            metadata = {
                "timestamp": timestamp,
                "unix_timestamp": unix_timestamp,  # For reliable sorting
                "user_input": user_input,
                "agent_response": agent_response,
                "tools_used": ",".join(tools_used) if tools_used else "none",
                "date": datetime.now().strftime("%Y-%m-%d"),
                "time": datetime.now().strftime("%H:%M:%S")
            }
            
            # Add to collection
            self.collection.add(
                ids=[conv_id],
                embeddings=[embedding],
                documents=[combined_text],
                metadatas=[metadata]
            )
            
            logger.debug(f"Stored conversation in vector DB: {conv_id} at {unix_timestamp}")
            
            # Check if we need to cleanup old entries
            max_entries = config.getint('Memory', 'max_memory_entries', fallback=500)
            if self.collection.count() > max_entries:
                self._cleanup_old_entries()
                
        except Exception as e:
            logger.error(f"Error storing conversation: {e}")
    
    def search_similar_conversations(self, query: str, n_results: int = 5):
        """
        Search for similar past conversations using semantic search.
        
        Args:
            query: Search query
            n_results: Number of results to return
            
        Returns:
            List of relevant past conversations
        """
        if not self.enabled:
            return []
            
        try:
            # Generate query embedding
            query_embedding = self.embedding_model.encode(query).tolist()
            
            # Search
            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=min(n_results, self.collection.count())
            )
            
            # Format results
            conversations = []
            if results['ids'] and len(results['ids'][0]) > 0:
                for i, doc_id in enumerate(results['ids'][0]):
                    metadata = results['metadatas'][0][i]
                    conversations.append({
                        'id': doc_id,
                        'user_input': metadata.get('user_input', ''),
                        'agent_response': metadata.get('agent_response', ''),
                        'tools_used': metadata.get('tools_used', 'none'),
                        'timestamp': metadata.get('timestamp', ''),
                        'unix_timestamp': metadata.get('unix_timestamp', 0),
                        'date': metadata.get('date', ''),
                        'distance': results['distances'][0][i] if 'distances' in results else None
                    })
            
            logger.debug(f"Found {len(conversations)} similar conversations for query: {query}")
            return conversations
            
        except Exception as e:
            logger.error(f"Error searching conversations: {e}")
            return []
    
    def get_recent_conversations(self, n: int = 10):
        """Get the most recent N conversations."""
        if not self.enabled:
            return []
            
        try:
            # Get ALL conversations with metadata
            results = self.collection.get(
                include=['metadatas', 'documents']
            )
            
            conversations = []
            if results['ids']:
                for i, doc_id in enumerate(results['ids']):
                    metadata = results['metadatas'][i]
                    
                    # Get unix timestamp for sorting (fallback to parsing ISO timestamp)
                    unix_ts = metadata.get('unix_timestamp', None)
                    if unix_ts is None:
                        # Fallback: try to parse ISO timestamp
                        try:
                            iso_ts = metadata.get('timestamp', '')
                            if iso_ts:
                                dt = datetime.fromisoformat(iso_ts)
                                unix_ts = dt.timestamp()
                            else:
                                unix_ts = 0
                        except:
                            unix_ts = 0
                    
                    conversations.append({
                        'id': doc_id,
                        'user_input': metadata.get('user_input', ''),
                        'agent_response': metadata.get('agent_response', ''),
                        'tools_used': metadata.get('tools_used', 'none'),
                        'timestamp': metadata.get('timestamp', ''),
                        'unix_timestamp': float(unix_ts),
                        'date': metadata.get('date', ''),
                        'time': metadata.get('time', '')
                    })
            
            # Sort by unix timestamp (most recent first)
            conversations.sort(key=lambda x: x['unix_timestamp'], reverse=True)
            
            logger.debug(f"Retrieved {len(conversations[:n])} most recent conversations")
            return conversations[:n]
            
        except Exception as e:
            logger.error(f"Error getting recent conversations: {e}")
            return []
    
    def get_conversations_by_date(self, date_str: str):
        """
        Get all conversations from a specific date.
        
        Args:
            date_str: Date in YYYY-MM-DD format
        """
        if not self.enabled:
            return []
            
        try:
            results = self.collection.get(
                where={"date": date_str},
                include=['metadatas']
            )
            
            conversations = []
            if results['ids']:
                for i, doc_id in enumerate(results['ids']):
                    metadata = results['metadatas'][i]
                    
                    # Get unix timestamp
                    unix_ts = metadata.get('unix_timestamp', 0)
                    
                    conversations.append({
                        'id': doc_id,
                        'user_input': metadata.get('user_input', ''),
                        'agent_response': metadata.get('agent_response', ''),
                        'tools_used': metadata.get('tools_used', 'none'),
                        'timestamp': metadata.get('timestamp', ''),
                        'unix_timestamp': float(unix_ts),
                        'time': metadata.get('time', '')
                    })
            
            # Sort by unix timestamp (most recent first)
            conversations.sort(key=lambda x: x['unix_timestamp'], reverse=True)
            
            return conversations
            
        except Exception as e:
            logger.error(f"Error getting conversations by date: {e}")
            return []
    
    def get_statistics(self):
        """Get memory statistics."""
        if not self.enabled:
            return {"enabled": False}
            
        try:
            count = self.collection.count()
            
            # Get date range
            all_convs = self.collection.get(include=['metadatas'])
            dates = [m.get('date', '') for m in all_convs['metadatas']]
            dates = [d for d in dates if d]  # Remove empty
            
            stats = {
                "enabled": True,
                "total_conversations": count,
                "oldest_date": min(dates) if dates else "N/A",
                "newest_date": max(dates) if dates else "N/A",
                "database_path": str(self.db_path)
            }
            
            return stats
            
        except Exception as e:
            logger.error(f"Error getting statistics: {e}")
            return {"enabled": True, "error": str(e)}
    
    def _cleanup_old_entries(self):
        """Remove oldest entries when max is exceeded."""
        try:
            max_entries = config.getint('Memory', 'max_memory_entries', fallback=500)
            current_count = self.collection.count()
            
            if current_count > max_entries:
                # Get all entries with timestamps
                all_convs = self.collection.get(include=['metadatas'])
                
                # Sort by unix timestamp
                entries = []
                for i in range(len(all_convs['ids'])):
                    unix_ts = all_convs['metadatas'][i].get('unix_timestamp', 0)
                    entries.append((all_convs['ids'][i], float(unix_ts)))
                
                entries.sort(key=lambda x: x[1])  # Oldest first
                
                # Delete oldest entries
                to_delete = current_count - max_entries
                ids_to_delete = [entry[0] for entry in entries[:to_delete]]
                
                self.collection.delete(ids=ids_to_delete)
                logger.info(f"Cleaned up {to_delete} old memory entries")
                
        except Exception as e:
            logger.error(f"Error during cleanup: {e}")
