# llm_host/host_integration.py
import importlib
import inspect
import json
import pkgutil
import re
import time
from pathlib import Path
from llama_cpp import Llama

from agent.tools.base_tool import BaseTool
from config_manager import config
from logger import logger

# Import memory system
try:
    from memory.vectorstore import VectorMemoryStore
    MEMORY_AVAILABLE = True
except ImportError:
    MEMORY_AVAILABLE = False
    logger.warning("Memory system not available. Install: pip install chromadb sentence-transformers")


class LocalLLMClient:
    """Manages a persistent chat session using the llama-cpp-python library."""
    
    def __init__(self, model_path=None):
        if model_path is None:
            model_path = config.get('Paths', 'llm_model_path')
        
        logger.info("Loading LLM model with llama-cpp-python...")
        start_time = time.time()
        
        try:
            self.model = Llama(
                model_path=model_path,
                n_gpu_layers=config.getint('LLM', 'n_gpu_layers', fallback=-1),
                n_ctx=config.getint('LLM', 'n_ctx', fallback=4096),
                n_threads=config.getint('LLM', 'n_threads', fallback=6),
                verbose=False
            )
            end_time = time.time()
            logger.info(f"✅ Model loaded successfully in {end_time - start_time:.2f} seconds")
        except Exception as e:
            logger.critical(f"Failed to load model: {e}")
            raise
    
    def generate_response(self, prompt, history, temperature=None, max_tokens=None):
        """Generates a response using chat completion format."""
        logger.debug("Generating response...")
        start_time = time.time()
        
        # Use config values if not provided
        if temperature is None:
            temperature = config.getfloat('LLM', 'temperature', fallback=0.7)
        if max_tokens is None:
            max_tokens = config.getint('LLM', 'max_tokens', fallback=512)
        
        # Format messages
        messages = []
        for user_msg, agent_msg in history:
            messages.append({"role": "user", "content": user_msg})
            messages.append({"role": "assistant", "content": agent_msg})
        messages.append({"role": "user", "content": prompt})
        
        try:
            completion = self.model.create_chat_completion(
                messages=messages,
                max_tokens=max_tokens,
                temperature=temperature
            )
            response = completion['choices'][0]['message']['content'].strip()
            end_time = time.time()
            logger.debug(f"Response generated in {end_time - start_time:.2f} seconds")
            return response
        except Exception as e:
            logger.error(f"Error generating response: {e}")
            return f"Error: {str(e)}"


class Agent:
    """The core AI agent using ReAct framework with long-term memory."""
    
    def __init__(self, llm_client):
        self.llm_client = llm_client
        self.history = []  # Short-term memory (current session)
        self.max_history = config.getint('Agent', 'conversation_history_length', fallback=10)
        self.enable_error_recovery = config.getboolean('Agent', 'enable_error_recovery', fallback=True)
        self.max_retries = config.getint('Agent', 'max_retries', fallback=2)
        
        # Initialize long-term memory
        self.memory = None
        if MEMORY_AVAILABLE and config.getboolean('Memory', 'use_vector_db', fallback=True):
            try:
                self.memory = VectorMemoryStore()
                logger.info("Long-term memory enabled")
            except Exception as e:
                logger.error(f"Failed to initialize memory: {e}")
                self.memory = None
        else:
            logger.info("Long-term memory disabled")
        
        # Load tools
        self.tools = self.load_tools()
        self.system_prompt = self.build_system_prompt()
        
        tool_names = list(self.tools.keys())
        logger.info(f"✅ Agent initialized with {len(self.tools)} tools")
        
        # Log tool categories
        daily_tools = [t for t in tool_names if t in ['calculate', 'set_reminder', 'clipboard', 'weather', 'screenshot']]
        memory_tools = [t for t in tool_names if 'memory' in t or 'conversation' in t]
        web_tools = [t for t in tool_names if t in ['google_search', 'scrape_webpage', 'read_webpage', 'download_file', 'url_info']]
        
        if daily_tools:
            logger.info(f"📅 Daily tools loaded ({len(daily_tools)}): {daily_tools}")
        else:
            logger.warning("⚠️  Daily tools not found! Check agent/tools/daily_tools.py")
        
        if memory_tools:
            logger.info(f"🧠 Memory tools loaded ({len(memory_tools)}): {memory_tools}")
        
        if web_tools:
            logger.info(f"🌐 Web tools loaded ({len(web_tools)}): {web_tools}")
        else:
            logger.warning("⚠️  Web tools not found! Check agent/tools/web_tools.py")
    
    def load_tools(self):
        """Dynamically loads all tool classes from the agent/tools directory."""
        tools = {}
        tools_package_path = "agent.tools"
        
        try:
            # Get the tools directory path
            from agent import tools as tools_module
            tools_dir = Path(tools_module.__file__).parent
            
            # Iterate through all Python files in the tools directory
            for tool_file in tools_dir.glob('*.py'):
                if tool_file.name.startswith('_') or tool_file.name == 'base_tool.py':
                    continue
                
                module_name = tool_file.stem
                
                try:
                    # Import the module
                    module = importlib.import_module(f"{tools_package_path}.{module_name}")
                    
                    # Find all tool classes in the module
                    for name, obj in inspect.getmembers(module, inspect.isclass):
                        if issubclass(obj, BaseTool) and obj is not BaseTool:
                            # Instantiate the tool
                            tool_instance = obj(llm_client=self.llm_client)
                            
                            # If it's a memory tool, inject the shared memory instance
                            if hasattr(tool_instance, 'memory'):
                                tool_instance.memory = self.memory
                            
                            tools[tool_instance.name] = tool_instance
                            logger.debug(f"Loaded tool: {tool_instance.name}")
                
                except Exception as e:
                    logger.error(f"Error loading module {module_name}: {e}")
                    continue
        
        except Exception as e:
            logger.error(f"Error scanning tools directory: {e}")
        
        return tools
    
    def build_system_prompt(self):
        """Builds the system prompt that instructs the LLM on how to use tools."""
        prompt = """You are a helpful AI assistant with tools. ALWAYS use exact tool names (case-sensitive).

CRITICAL RULES:
1. When user requests match a tool, output ONLY the tool action JSON
2. Format: {"tool": "exact_name", "argument": "value"}
3. Do NOT add extra text, explanations, or "Action:" prefix
4. Output ONLY the JSON when using a tool

TOOL USAGE (use these EXACT names):
- "search google for X" → {"tool": "google_search", "argument": "X"}
- "scrape webpage URL" → {"tool": "scrape_webpage", "argument": "URL"}
- "calculate X" → {"tool": "calculate", "argument": "X"}
- "remind me X" → {"tool": "set_reminder", "argument": "X"}
- "what did we discuss" → {"tool": "recent_conversations", "argument": "5"}

Available tools:
"""
        for tool_name, tool_instance in self.tools.items():
            prompt += f"- {tool_name}: {tool_instance.description}\n"
        
        prompt += "\n📚 EXAMPLES (output ONLY JSON):\n\n"
        
        prompt += 'User: calculate 10 plus 20\n'
        prompt += '{"tool": "calculate", "argument": "10 + 20"}\n\n'
        
        prompt += 'User: what is 5 times 6\n'
        prompt += '{"tool": "calculate", "argument": "5 * 6"}\n\n'
        
        prompt += 'User: what did we discuss?\n'
        prompt += '{"tool": "recent_conversations", "argument": "5"}\n\n'
        
        return prompt
    
    def process_command(self, user_input, retry_count=0):
        """Process user input and execute tools if needed."""
        logger.info(f"Processing: {user_input}")
        
        # Construct full prompt
        full_prompt = f"{self.system_prompt}\nUser: {user_input}"
        
        # Get LLM response
        raw_llm_response = self.llm_client.generate_response(full_prompt, self.history)
        logger.debug(f"Raw LLM Response: {raw_llm_response[:200]}...")
        
        agent_response = None
        tools_used = []
        
        # Try multiple patterns to detect JSON
        action_json = None
        
        # Pattern 1: Look for "Action: {...}"
        action_match = re.search(r'Action:\s*(\{.*?\})', raw_llm_response, re.DOTALL)
        if action_match:
            action_json = action_match.group(1)
        
        # Pattern 2: Look for standalone JSON (starts with { and contains "tool")
        if not action_json:
            json_match = re.search(r'\{[^}]*"tool"[^}]*\}', raw_llm_response)
            if json_match:
                action_json = json_match.group(0)
        
        # Pattern 3: Try to parse entire response as JSON
        if not action_json:
            try:
                test_json = json.loads(raw_llm_response.strip())
                if 'tool' in test_json:
                    action_json = raw_llm_response.strip()
            except:
                pass
        
        # If we found JSON, try to execute the tool
        if action_json:
            try:
                action_json_str = action_json.replace("'", '"')
                action_data = json.loads(action_json_str)
                
                tool_name = action_data.get('tool')
                tool_argument = action_data.get('argument', '')
                
                if tool_name in self.tools:
                    logger.info(f"Executing tool: {tool_name} with argument: {tool_argument}")
                    tools_used.append(tool_name)
                    
                    try:
                        agent_response = self.tools[tool_name].execute(tool_argument)
                        
                        # Check for errors and retry if enabled
                        if self.enable_error_recovery and "Error" in agent_response and retry_count < self.max_retries:
                            logger.warning(f"Tool execution error, retrying... (attempt {retry_count + 1}/{self.max_retries})")
                            return self.process_command(user_input, retry_count + 1)
                    
                    except Exception as e:
                        logger.error(f"Tool execution failed: {e}")
                        agent_response = f"Error executing tool {tool_name}: {str(e)}"
                else:
                    agent_response = f"Error: Tool '{tool_name}' not found. Available tools: {list(self.tools.keys())}"
                    logger.error(agent_response)
            
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse tool action JSON: {e}")
                agent_response = "Error: Could not parse tool action."
            except Exception as e:
                logger.error(f"Error processing tool action: {e}")
                agent_response = f"Error: {str(e)}"
        
        # If no action found, use conversational response
        if agent_response is None:
            # Clean up response
            if "Thought:" in raw_llm_response:
                agent_response = raw_llm_response.split("Thought:")[0].strip()
            else:
                agent_response = raw_llm_response
        
        # Update short-term history (current session)
        self.history.append((user_input, agent_response))
        if len(self.history) > self.max_history:
            self.history.pop(0)
        
        # Log conversation
        logger.log_conversation(user_input, agent_response, tools_used if tools_used else None)
        
        # Store in long-term memory
        if self.memory:
            try:
                self.memory.add_conversation(user_input, agent_response, tools_used if tools_used else [])
                logger.debug("Conversation stored in memory")
            except Exception as e:
                logger.error(f"Error storing conversation in memory: {e}")
        
        return agent_response
    
    def clear_history(self):
        """Clear short-term conversation history (current session only)."""
        self.history.clear()
        logger.info("Short-term conversation history cleared")
