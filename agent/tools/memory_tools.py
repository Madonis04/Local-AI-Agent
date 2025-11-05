# agent/tools/memory_tools.py
from agent.tools.base_tool import BaseTool
from logger import logger


class SearchMemoryTool(BaseTool):
    """Search past conversations semantically."""
    
    name = "search_memory"
    description = "Search past conversations by meaning/topic. Argument: search query (e.g., 'system monitoring')"
    
    def __init__(self, llm_client):
        super().__init__()
        self.llm_client = llm_client
        self.memory = None  # Will be injected by Agent
    
    def execute(self, argument: str) -> str:
        try:
            if not self.memory:
                return "Error: Memory system not available."
            
            if not argument or argument.strip() == "":
                return "Error: Please provide a search query."
            
            logger.info(f"Searching memory for: {argument}")
            results = self.memory.search_similar_conversations(argument, n_results=5)
            
            if not results:
                return "No relevant conversations found in memory."
            
            # Format results
            output = f"Found {len(results)} relevant conversations:\n\n"
            for i, conv in enumerate(results, 1):
                output += f"{i}. [{conv['date']}]\n"
                output += f"   User: {conv['user_input'][:100]}...\n"
                output += f"   Agent: {conv['agent_response'][:100]}...\n"
                if conv['tools_used'] != 'none':
                    output += f"   Tools: {conv['tools_used']}\n"
                output += "\n"
            
            return output.strip()
            
        except Exception as e:
            logger.error(f"Error in search_memory: {e}")
            return f"Error searching memory: {str(e)}"


class RecentConversationsTool(BaseTool):
    """Get recent conversation history."""
    
    name = "recent_conversations"
    description = "Get recent conversation history. Argument: number of conversations (default: 10)"
    
    def __init__(self, llm_client):
        super().__init__()
        self.llm_client = llm_client
        self.memory = None  # Will be injected by Agent
    
    def execute(self, argument: str) -> str:
        try:
            if not self.memory:
                return "Error: Memory system not available."
            
            # Parse number of conversations
            try:
                n = int(argument) if argument else 10
                n = max(1, min(n, 50))  # Limit between 1-50
            except:
                n = 10
            
            logger.info(f"Getting {n} recent conversations")
            results = self.memory.get_recent_conversations(n)
            
            if not results:
                return "No conversations found in memory yet."
            
            # Format results
            output = f"Last {len(results)} conversations:\n\n"
            for i, conv in enumerate(results, 1):
                output += f"{i}. [{conv['date']} {conv['timestamp'].split('T')[1][:8]}]\n"
                output += f"   User: {conv['user_input'][:80]}...\n"
                output += f"   Agent: {conv['agent_response'][:80]}...\n\n"
            
            return output.strip()
            
        except Exception as e:
            logger.error(f"Error in recent_conversations: {e}")
            return f"Error getting recent conversations: {str(e)}"


class MemoryStatsTool(BaseTool):
    """Get memory system statistics."""
    
    name = "memory_stats"
    description = "Show memory system statistics. No argument needed."
    
    def __init__(self, llm_client):
        super().__init__()
        self.llm_client = llm_client
        self.memory = None  # Will be injected by Agent
    
    def execute(self, argument: str) -> str:
        try:
            if not self.memory:
                return "Error: Memory system not available."
            
            stats = self.memory.get_statistics()
            
            if not stats.get('enabled', False):
                return "Memory system is disabled."
            
            output = "Memory System Statistics:\n\n"
            output += f"Total Conversations: {stats.get('total_conversations', 0)}\n"
            output += f"Date Range: {stats.get('oldest_date', 'N/A')} to {stats.get('newest_date', 'N/A')}\n"
            output += f"Database Path: {stats.get('database_path', 'N/A')}\n"
            
            return output.strip()
            
        except Exception as e:
            logger.error(f"Error in memory_stats: {e}")
            return f"Error getting memory stats: {str(e)}"


class ConversationsByDateTool(BaseTool):
    """Get conversations from a specific date."""
    
    name = "conversations_on_date"
    description = "Get all conversations from a specific date. Argument: date in YYYY-MM-DD format (e.g., '2025-11-05')"
    
    def __init__(self, llm_client):
        super().__init__()
        self.llm_client = llm_client
        self.memory = None  # Will be injected by Agent
    
    def execute(self, argument: str) -> str:
        try:
            if not self.memory:
                return "Error: Memory system not available."
            
            if not argument or argument.strip() == "":
                return "Error: Please provide a date in YYYY-MM-DD format."
            
            date_str = argument.strip()
            logger.info(f"Getting conversations for date: {date_str}")
            results = self.memory.get_conversations_by_date(date_str)
            
            if not results:
                return f"No conversations found on {date_str}."
            
            # Format results
            output = f"Conversations on {date_str} ({len(results)} total):\n\n"
            for i, conv in enumerate(results, 1):
                output += f"{i}. [{conv['time']}]\n"
                output += f"   User: {conv['user_input'][:80]}...\n"
                output += f"   Agent: {conv['agent_response'][:80]}...\n"
                if conv['tools_used'] != 'none':
                    output += f"   Tools: {conv['tools_used']}\n"
                output += "\n"
            
            return output.strip()
            
        except Exception as e:
            logger.error(f"Error in conversations_on_date: {e}")
            return f"Error getting conversations by date: {str(e)}"
