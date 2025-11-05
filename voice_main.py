# voice_main.py
from llm_host.host_integration import LocalLLMClient, Agent
from voice.voice_interface import VoiceInterface
from logger import logger
from config_manager import config


def main():
    """Voice interface for the AI agent."""
    print("🎤 Local AI Agent - Voice Mode")
    print("=" * 60)
    
    # Initialize LLM and Agent
    try:
        print("\n📡 Initializing AI Agent...")
        llm_client = LocalLLMClient()
        agent = Agent(llm_client)
        print("✅ Agent initialized")
    except Exception as e:
        print(f"❌ Failed to initialize agent: {e}")
        logger.critical(f"Failed to initialize agent: {e}")
        return
    
    # Initialize Voice Interface
    try:
        print("\n🎤 Initializing Voice Interface...")
        voice = VoiceInterface()
        
        if not voice.enabled:
            print("\n⚠️  Voice interface is disabled in config.ini")
            print("Set [Voice] enabled = true to use voice mode")
            return
        
        print("✅ Voice interface ready")
    except Exception as e:
        print(f"❌ Failed to initialize voice interface: {e}")
        logger.error(f"Failed to initialize voice interface: {e}")
        return
    
    print("\n" + "=" * 60)
    print("🎙️  Voice Mode Active")
    print("=" * 60)
    print("\nCommands:")
    print("  - Speak your command, then press Enter")
    print("  - Type 'text' to switch to text mode")
    print("  - Type 'test' to test voice interface")
    print("  - Type 'mute' to disable voice output (text only)")
    print("  - Type 'unmute' to enable voice output")
    print("  - Type 'exit' or 'quit' to end")
    print()
    
    # Main conversation loop
    mode = "voice"
    voice_output_enabled = True
    
    while True:
        try:
            if mode == "voice":
                # Voice input mode
                print("\n🎤 Listening... (Press Enter when done speaking)")
                command = input("Press Enter to start recording (or type command): ").strip().lower()
                
                if command == 'exit' or command == 'quit':
                    print("Exiting agent.")
                    break
                elif command == 'text':
                    mode = "text"
                    print("✏️  Switched to text mode")
                    continue
                elif command == 'test':
                    voice.test_voice()
                    continue
                elif command == 'mute':
                    voice_output_enabled = False
                    print("🔇 Voice output muted (text only)")
                    continue
                elif command == 'unmute':
                    voice_output_enabled = True
                    print("🔊 Voice output enabled")
                    continue
                elif command:
                    # User typed something
                    user_input = command
                else:
                    # Record voice
                    user_input = voice.voice_input()
                    
                    if not user_input:
                        print("❌ Could not understand audio. Please try again.")
                        continue
                    
                    print(f"\n🗣️  You said: {user_input}")
            
            else:
                # Text input mode
                user_input = input("\n💬 You (text): ").strip()
                
                if user_input.lower() in ['exit', 'quit', 'bye']:
                    print("Exiting agent.")
                    break
                elif user_input.lower() == 'voice':
                    mode = "voice"
                    print("🎤 Switched to voice mode")
                    continue
                elif user_input.lower() == 'mute':
                    voice_output_enabled = False
                    print("🔇 Voice output muted")
                    continue
                elif user_input.lower() == 'unmute':
                    voice_output_enabled = True
                    print("🔊 Voice output enabled")
                    continue
                elif not user_input:
                    continue
            
            # Process command
            print("\n🤔 Processing...")
            agent_response = agent.process_command(user_input)
            
            # Output response (always show on screen)
            print(f"\n🤖 Agent:\n{agent_response}\n")
            
            # Speak response if enabled
            if voice_output_enabled:
                print("🔊 Speaking response...")
                voice.voice_output(agent_response)
                print("✅ Done speaking\n")
        
        except KeyboardInterrupt:
            print("\n\nExiting agent.")
            break
        except Exception as e:
            print(f"\n❌ Error: {e}")
            logger.error(f"Error in voice mode: {e}")


if __name__ == "__main__":
    main()
