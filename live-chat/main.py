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
  
  # Avatar visualization with custom positioning
  python main.py --model-style "yuri-front_natural" --background-image "pbi-12345" --padding-left 0.2 --padding-top 0.1 --padding-height 1.5
  
  # Check available settings
  python main.py --list-settings tts_type
  python main.py --list-settings modelstyle
        """,
    )

    # API Configuration
    parser.add_argument(
        "--api-server", default="https://live-api.perso.ai", help="API server URL (default: https://live-api.perso.ai)"
    )
    parser.add_argument("--api-key", help="API key (if not provided, will use EST_LIVE_API_KEY environment variable)")

    # AI Configuration
    parser.add_argument("--llm-type", default="gpt-35", help="LLM type to use (default: gpt-35)")
    parser.add_argument("--tts-type", default="yuri", help="TTS type to use (default: yuri)")
    parser.add_argument("--stt-type", default="default", help="STT type to use (default: default)")
    parser.add_argument(
        "--model-style", default="yuri-front_natural", help="Avatar model style (default: yuri-front_natural)"
    )

    # Content Configuration
    parser.add_argument(
        "--prompt",
        default="plp-d432cb910983f1eed6511eba836ac14f",
        help="Prompt ID (default: plp-d432cb910983f1eed6511eba836ac14f)",
    )
    parser.add_argument("--document", help="Document ID (optional)")
    parser.add_argument("--background-image", help="Background image ID (optional)")
    parser.add_argument(
        "--capability",
        nargs="+",
        default=["LLM", "TTS", "STT"],
        choices=["LLM", "TTS", "STT", "STF_WEBRTC"],
        help="Capabilities to enable (default: LLM TTS STT). Add STF_WEBRTC for browser WebRTC streaming",
    )

    # Avatar Visualization Configuration
    parser.add_argument("--padding-left", type=float, help="Avatar padding left (-1.0 to 1.0)")
    parser.add_argument("--padding-top", type=float, help="Avatar padding top (0.0 to 1.0)")
    parser.add_argument("--padding-height", type=float, help="Avatar padding height (0 to 5)")
    parser.add_argument("--agent", help="Agent identifier (optional)")

    # Settings Query
    parser.add_argument("--list-settings", choices=["tts_type", "modelstyle"], help="List available settings and exit")

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
                print(f"{i:2d}. {setting['name']} - {setting.get('display_name', 'N/A')}")

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
    BACKGROUND_IMAGE = args.background_image
    PADDING_LEFT = args.padding_left
    PADDING_TOP = args.padding_top
    PADDING_HEIGHT = args.padding_height
    AGENT = args.agent

    if not API_KEY:
        print(
            "❌ Error: API key is required. Provide it via --api-key argument or EST_LIVE_API_KEY environment variable."
        )
        return 1

    print("🚀 AI Avatar Chat System starting!")
    print(f"🔗 API Server: {API_SERVER}")
    print(f"🤖 LLM Type: {LLM_TYPE}")
    print(f"🔊 TTS Type: {TTS_TYPE}")
    print(f"🎤 STT Type: {STT_TYPE}")
    print(f"👤 Model Style: {MODEL_STYLE}")
    print(f"📝 Prompt ID: {PROMPT}")
    if DOCUMENT:
        print(f"📄 Document ID: {DOCUMENT}")
    if BACKGROUND_IMAGE:
        print(f"🖼️  Background Image ID: {BACKGROUND_IMAGE}")
    if PADDING_LEFT is not None:
        print(f"⬅️  Padding Left: {PADDING_LEFT}")
    if PADDING_TOP is not None:
        print(f"⬆️  Padding Top: {PADDING_TOP}")
    if PADDING_HEIGHT is not None:
        print(f"📏 Padding Height: {PADDING_HEIGHT}")
    if AGENT:
        print(f"🤖 Agent: {AGENT}")
    print(f"⚡ Capabilities: {', '.join(CAPABILITY)}")
    print("=" * 50)

    # Initialize avatar chat
    chat = AvatarChat(API_SERVER, API_KEY)

    try:
        # Create and start session
        chat.create_session(
            llm_type=LLM_TYPE,
            tts_type=TTS_TYPE,
            stt_type=STT_TYPE,
            model_style=MODEL_STYLE,
            prompt=PROMPT,
            document=DOCUMENT,
            capability=CAPABILITY,
            background_image=BACKGROUND_IMAGE,
            padding_left=PADDING_LEFT,
            padding_top=PADDING_TOP,
            padding_height=PADDING_HEIGHT,
            agent=AGENT,
        )
        chat.start_session()

        print("✅ Ready! Start chatting with the avatar.")

        while True:
            print_menu()
            choice = input("Choose option (1-7): ").strip()

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
                        tts_choice = input("\n🔊 Would you like to hear it as speech? (y/N): ").strip().lower()
                        if tts_choice == "y":
                            tts_file = f"ai_response_{int(time.time())}.wav"
                            chat.generate_speech(ai_response, tts_file)
                            chat.play_audio(tts_file)

            elif choice == "2":
                # Voice chat
                if not AUDIO_AVAILABLE:
                    print("❌ pyaudio is not installed, voice features are unavailable.")
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
                        print("💡 Solution: Restart the program to create a new session.")

            elif choice == "4":
                # Chat history
                print("\n📜 Chat History")
                history = chat.get_chat_history()
                if not history:
                    print("No chat history available.")
                else:
                    for i, msg in enumerate(history, 1):
                        role_emoji = "👤" if msg["role"] == "Human" else "🤖"
                        print(f"{i}. {role_emoji} {msg['role']}: {msg['content']}")

            elif choice == "5":
                # Launch avatar visualization
                print("\n🎭 Launching Avatar Visualization")
                print("🚀 Preparing real-time avatar experience...")
                try:
                    config = chat.get_avatar_configuration()
                    if "error" in config:
                        print(f"❌ Error: {config['error']}")
                    else:
                        print(f"🆔 Session ID: {config.get('session_id', 'N/A')}")
                        print(f"📊 Status: {config.get('status', 'N/A')}")

                        model_style = config.get("model_style", {})
                        if model_style:
                            print(
                                f"👤 Avatar: {model_style.get('display_name', 'N/A')} ({model_style.get('name', 'N/A')})"
                            )

                        bg_image = config.get("background_image")
                        if bg_image:
                            print(f"🖼️  Background: {bg_image}")
                        else:
                            print("🖼️  Background: Default")

                        capabilities = config.get("capabilities", [])
                        print(f"⚡ Active Features: {', '.join(capabilities)}")

                        created_at = config.get("created_at")
                        if created_at:
                            print(f"🕐 Session Started: {created_at}")

                        # Try to get video stream info
                        stream_info = chat.get_video_stream_url()
                        if stream_info and isinstance(stream_info, dict):
                            print("\n🎬 Ready for Real-Time Avatar Chat!")
                            print(f"   📱 Session ID: {stream_info.get('session_id')}")
                            print(f"   🔥 Status: {stream_info.get('status')}")
                            print(f"   📖 SDK Guide: {stream_info.get('sdk_docs')}")
                            print(f"   💡 Next Step: {stream_info.get('instructions')}")
                        elif stream_info:
                            print(f"🎥 Stream Info: {stream_info}")

                except Exception as e:
                    print(f"❌ Error launching avatar: {e}")

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
                            print(f"{i:2d}. {setting['name']} - {setting.get('display_name', 'N/A')}")
                    elif setting_choice == "2":
                        settings = chat.get_available_settings("modelstyle")
                        print("\n👤 Available Model Styles:")
                        for i, setting in enumerate(settings, 1):
                            print(f"{i:2d}. {setting['name']} - {setting.get('display_name', 'N/A')}")
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
        # Clean up session
        chat.end_session()
        print("🧹 Resource cleanup completed")

    return 0


if __name__ == "__main__":
    exit(main())
