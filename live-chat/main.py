import argparse
import os

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
        help="Capabilities to enable (default: LLM TTS STT)",
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
    print("5. Exit")
    print("=" * 50)


def main():
    # Parse command line arguments
    args = parse_arguments()

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
        )
        chat.start_session()

        print("✅ Ready! Start chatting with the avatar.")

        while True:
            print_menu()
            choice = input("Choose option (1-5): ").strip()

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
                            import time

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
                    import time

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
