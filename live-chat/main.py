import argparse
import os
import time

from avatar_chat import AUDIO_AVAILABLE, AvatarChat


def parse_arguments():
    """Command line argument parser"""
    parser = argparse.ArgumentParser(
        description="AI Avatar Chat System - Interactive chat with AI avatars",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Basic usage with defaults
  python main.py
  
  # Custom configuration
  python main.py --llm-type gpt-4 --tts-type "azuretts-ko-KR-InJoonNeural-sad" --model-style "indian_m_2_aaryan-side-white_jacket-natural"
  
  # With custom prompt and document
  python main.py --prompt "plp-12345" --document "pld-67890"
  
  # Specify capabilities
  python main.py --capability LLM TTS STT
  
  # Check available settings
  python main.py --list-settings llm_type
  python main.py --list-settings tts_type
  python main.py --list-settings modelstyle
        """,
    )

    # API Configuration
    parser.add_argument(
        "--api-server",
        default="https://live-api.perso.ai",
        help="API server URL (default: https://live-api.perso.ai)",
    )
    parser.add_argument(
        "--api-key",
        help="API key (if not provided, will use EST_LIVE_API_KEY environment variable)",
    )

    # AI Configuration
    parser.add_argument(
        "--llm-type",
        default="gpt-35",
        help="LLM type to use (default: gpt-4o-mini)",
    )
    parser.add_argument(
        "--tts-type", default="yuri", help="TTS type to use (default: yuri)"
    )
    parser.add_argument(
        "--stt-type", default="default", help="STT type to use (default: default)"
    )
    parser.add_argument(
        "--model-style",
        default="yoori-front-khaki_overalls-nodded_loop",
        help="Avatar model style (default: yuri-front_natural)",
    )

    # Content Configuration
    parser.add_argument(
        "--prompt",
        help="Prompt ID (default: plp-d432cb910983f1eed6511eba836ac14f)",
    )
    parser.add_argument("--document", help="Document ID for AI context (optional)")
    parser.add_argument(
        "--capability",
        nargs="+",
        default=["LLM", "TTS", "STT"],
        choices=["LLM", "TTS", "STT"],
        help="Capabilities to enable for Python session (default: LLM TTS STT)",
    )
    parser.add_argument("--agent", help="Agent identifier (optional)")
    parser.add_argument(
        "--mcp-servers",
        help="MCP server ids",
    )
    parser.add_argument(
        "--tools",
        default=[],
        help="Tools for MCP",
    )

    # Settings Query
    parser.add_argument(
        "--list-settings",
        choices=["llm_type", "tts_type", "modelstyle"],
        help="List available settings and exit",
    )

    return parser.parse_args()


def print_menu():
    print("\n" + "=" * 50)
    print("🤖 AI Avatar Chat Menu")
    print("=" * 50)
    print("1. Chat with text")
    print("2. Chat with voice (recording)")
    print("3. Chat with voice file")
    print("4. View chat history")
    print("5. Launch avatar visualization")
    print("6. Check available settings")
    print("7. Exit")
    print("=" * 50)


def main():
    # Parse command line arguments
    args = parse_arguments()

    # Handle settings query and exit
    if args.list_settings:
        try:
            API_SERVER = args.api_server
            API_KEY = args.api_key or os.environ.get("EST_LIVE_API_KEY")

            if not API_KEY:
                print("❌ Error: API key is required for settings query.")
                return 1

            # Create temporary chat instance for settings query
            temp_chat = AvatarChat(API_SERVER, API_KEY)
            settings = temp_chat.get_available_settings(args.list_settings)

            print(f"\n📋 Available {args.list_settings}:")
            for i, setting in enumerate(settings, 1):
                print(f"{i:2d}. {setting['name']}")

            return 0
        except Exception as e:
            print(f"❌ Error getting settings: {e}")
            return 1

    # Set up configuration from arguments
    API_SERVER = args.api_server
    API_KEY = args.api_key or os.environ.get("EST_LIVE_API_KEY")
    LLM_TYPE = args.llm_type
    TTS_TYPE = args.tts_type
    STT_TYPE = args.stt_type
    MODEL_STYLE = args.model_style
    PROMPT = args.prompt
    DOCUMENT = args.document
    CAPABILITY = args.capability
    AGENT = args.agent
    MCP_SERVERS = args.mcp_servers
    TOOLS = args.tools

    if not API_KEY:
        print(
            "❌ Error: API key is required. Provide it via --api-key argument or EST_LIVE_API_KEY environment variable."
        )
        return 1

    print("🚀 AI Avatar Chat System starting!")
    print(f"🔗 API Server: {API_SERVER}")
    print("=" * 50)

    # Initialize avatar chat instance (but don't create session yet)
    chat = AvatarChat(API_SERVER, API_KEY)
    session_created = False

    try:
        while True:
            print_menu()
            choice = input("Choose option (1-7): ").strip()

            # For options that need Python session, create it if not exists
            if choice in ["1", "2", "3", "4", "6"] and not session_created:
                print(f"🤖 LLM Type: {LLM_TYPE}")
                print(f"🔊 TTS Type: {TTS_TYPE}")
                print(f"🎤 STT Type: {STT_TYPE}")
                print(f"👤 Model Style: {MODEL_STYLE}")
                print(f"📝 Prompt ID: {PROMPT}")
                if DOCUMENT:
                    print(f"📄 Document ID: {DOCUMENT}")
                print(f"⚡ Capabilities: {', '.join(CAPABILITY)}")
                print("=" * 50)

                # Create and start session
                chat.create_session(
                    llm_type=LLM_TYPE,
                    tts_type=TTS_TYPE,
                    stt_type=STT_TYPE,
                    model_style=MODEL_STYLE,
                    prompt=PROMPT,
                    document=DOCUMENT,
                    capability=CAPABILITY,
                    agent=AGENT,
                    mcp_servers=MCP_SERVERS,
                    tools=TOOLS,
                )
                chat.start_session()
                session_created = True
                print("✅ Ready! Start chatting with the avatar.")

            if choice == "1":
                # Text chat
                print("\n💬 Text Chat Mode")
                while True:
                    user_input = input("\n👤 Input (quit to return to menu): ").strip()
                    if user_input.lower() == "quit" or user_input.lower() == "q":
                        break
                    if user_input:
                        ai_response = chat.chat_text(user_input)

                        # Ask if user wants TTS
                        tts_choice = (
                            input("\n🔊 Would you like to hear it as speech? (y/N): ")
                            .strip()
                            .lower()
                        )
                        if tts_choice == "y":
                            tts_file = f"ai_response_{int(time.time())}.wav"
                            chat.generate_speech(ai_response, tts_file)
                            chat.play_audio(tts_file)

            elif choice == "2":
                # Voice chat
                if not AUDIO_AVAILABLE:
                    print(
                        "❌ pyaudio is not installed, voice features are unavailable."
                    )
                    print("   Install: pip install pyaudio")
                    continue

                print("\n🎤 Voice Chat Mode")
                print("Press Enter below to start recording.")
                input("Press Enter when ready...")

                ai_response = chat.voice_chat()
                if ai_response:
                    print("\n✅ Chat completed!")

            elif choice == "3":
                # Voice file chat
                print("\n📁 Voice File Chat Mode")
                file_path = input("Enter voice file path: ").strip()

                try:
                    recognized_text = chat.recognize_speech(file_path)
                    ai_response = chat.chat_text(recognized_text)

                    # Generate TTS
                    tts_file = f"ai_response_{int(time.time())}.wav"
                    chat.generate_speech(ai_response, tts_file)
                    chat.play_audio(tts_file)

                except Exception as e:
                    print(f"❌ Error: {e}")
                    if "Session has ended" in str(e):
                        print(
                            "💡 Solution: Restart the program to create a new session."
                        )

            elif choice == "4":
                # Chat history
                print("\n📜 Chat History")
                if not session_created:
                    print("No session created yet. No chat history available.")
                else:
                    history = chat.get_chat_history()
                    if not history:
                        print("No chat history available.")
                    else:
                        for i, msg in enumerate(history, 1):
                            role_emoji = "👤" if msg["role"] == "Human" else "🤖"
                            print(f"{i}. {role_emoji} {msg['role']}: {msg['content']}")

            elif choice == "5":
                # Launch avatar visualization (browser-only mode - no Python session needed)
                print("\n🎭 Browser Avatar Visualization (Independent Mode)")
                print(
                    "ℹ️  This mode uses browser-only WebRTC - no Python session required"
                )
                print(
                    "🔄 Browser creates its own session - independent from any Python session"
                )

                try:
                    stream_info = chat.get_video_stream_url()
                    if stream_info and isinstance(stream_info, dict):
                        print("\n✅ Ready for browser avatar visualization!")
                        print(f"   🌐 Mode: {stream_info.get('mode', 'browser_only')}")
                        print(f"   🔗 API Server: {stream_info.get('api_server')}")
                        print(f"   📖 Documentation: {stream_info.get('sdk_docs')}")
                        print(f"   💡 Path: {stream_info.get('browser_path')}")
                    elif stream_info:
                        print(f"🎥 Stream Info: {stream_info}")

                except Exception as e:
                    print(f"❌ Error launching avatar guidance: {e}")

            elif choice == "6":
                # Check available settings
                print("\n🔍 Available Settings")
                print("1. TTS Types")
                print("2. Model Styles")
                setting_choice = input("Choose setting type (1-2): ").strip()

                try:
                    if setting_choice == "1":
                        settings = chat.get_available_settings("tts_type")
                        print("\n🔊 Available TTS Types:")
                        for i, setting in enumerate(settings, 1):
                            print(
                                f"{i:2d}. {setting['name']} - {setting.get('display_name', 'N/A')}"
                            )
                    elif setting_choice == "2":
                        settings = chat.get_available_settings("modelstyle")
                        print("\n👤 Available Model Styles:")
                        for i, setting in enumerate(settings, 1):
                            print(
                                f"{i:2d}. {setting['name']} - {setting.get('display_name', 'N/A')}"
                            )
                    else:
                        print("❌ Invalid choice.")
                except Exception as e:
                    print(f"❌ Error getting settings: {e}")

            elif choice == "7":
                # Exit
                print("\n👋 Exiting program.")
                break

            else:
                print("❌ Invalid choice.")

    except KeyboardInterrupt:
        print("\n\n⚠️  Interrupted by user.")
    except Exception as e:
        print(f"\n❌ Error occurred: {e}")
    finally:
        # Clean up session only if it was created
        if session_created:
            chat.end_session()
            print("🧹 Resource cleanup completed")
        else:
            print("🧹 No session to clean up")

    return 0


if __name__ == "__main__":
    exit(main())
