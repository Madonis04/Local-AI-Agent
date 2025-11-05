# main.py
from llm_host.host_integration import LocalLLMClient, Agent
from logger import logger


def main():
    """CLI interface for the AI agent."""
    print("Local AI Agent starting...")
    
    # Initialize LLM and Agent
    try:
        llm_client = LocalLLMClient()
        agent = Agent(llm_client)
    except Exception as e:
        print(f"❌ Failed to initialize agent: {e}")
        logger.critical(f"Failed to initialize agent: {e}")
        return
    
    print("✅ Agent is ready. Type 'exit' or 'quit' to end.\n")
    
    # Main conversation loop
    while True:
        try:
            user_input = input("You: ").strip()
            
            # Check for exit commands
            if user_input.lower() in ['exit', 'quit', 'bye']:
                print("Exiting agent.")
                break
            
            # Skip empty inputs
            if not user_input:
                continue
            
            # Process the command
            agent_response = agent.process_command(user_input)
            
            # Print clean response
            print(f"\nAgent: {agent_response}\n")
        
        except KeyboardInterrupt:
            print("\n\nExiting agent.")
            break
        except Exception as e:
            print(f"\n❌ Error: {e}")
            logger.error(f"Error in main loop: {e}")


if __name__ == "__main__":
    main()
