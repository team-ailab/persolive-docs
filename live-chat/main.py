import os

from avatar_chat import AUDIO_AVAILABLE, AvatarChat


def print_menu():
    print("\n" + "=" * 50)
    print("🤖 AI 아바타 대화 메뉴")
    print("=" * 50)
    print("1. 텍스트로 대화하기")
    print("2. 음성으로 대화하기 (녹음)")
    print("3. 음성 파일로 대화하기")
    print("4. 대화 히스토리 보기")
    print("5. 종료")
    print("=" * 50)


def main():
    # 설정값들 (실제 값으로 변경하세요)
    API_SERVER = "https://live-api.perso.ai"
    API_KEY = os.environ.get("EST_LIVE_API_KEY")
    LLM_TYPE = "gpt-35"
    TTS_TYPE = "yuri"
    STT_TYPE = "default"
    MODEL_STYLE = "yuri-front_natural"
    PROMPT = "plp-d432cb910983f1eed6511eba836ac14f"
    DOCUMENT = "pld-be1b50ffd908582d5f5f6fd08c177f6c"
    CAPABILITY = ["LLM", "TTS", "STT"]
    BACKGROUND_IMAGE = "plbi-ad61941c14a386803423f2cf7ecb999f"

    print("🚀 AI 아바타 대화 시스템 시작!")

    # 아바타 채팅 초기화
    chat = AvatarChat(API_SERVER, API_KEY)

    try:
        # 세션 생성 및 시작
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

        print("✅ 준비 완료! 아바타와 대화해보세요.")

        while True:
            print_menu()
            choice = input("선택하세요 (1-5): ").strip()

            if choice == "1":
                # 텍스트 대화
                print("\n💬 텍스트 대화 모드")
                while True:
                    user_input = input("\n👤 입력 (quit으로 메뉴로 돌아가기): ").strip()
                    if user_input.lower() == "quit" or user_input.lower() == "q":
                        break
                    if user_input:
                        ai_response = chat.chat_text(user_input)

                        # TTS 생성 여부 묻기
                        tts_choice = input("\n🔊 음성으로도 들어보시겠습니까? (y/N): ").strip().lower()
                        if tts_choice == "y":
                            import time

                            tts_file = f"ai_response_{int(time.time())}.wav"
                            chat.generate_speech(ai_response, tts_file)
                            chat.play_audio(tts_file)

            elif choice == "2":
                # 음성 대화
                if not AUDIO_AVAILABLE:
                    print("❌ pyaudio가 설치되지 않아 음성 기능을 사용할 수 없습니다.")
                    print("   설치: pip install pyaudio")
                    continue

                print("\n🎤 음성 대화 모드")
                print("아래에서 Enter를 누르면 녹음이 시작됩니다.")
                input("준비되면 Enter를 눌러주세요...")

                ai_response = chat.voice_chat()
                if ai_response:
                    print("\n✅ 대화 완료!")

            elif choice == "3":
                # 음성 파일로 대화
                print("\n📁 음성 파일 대화 모드")
                file_path = input("음성 파일 경로를 입력하세요: ").strip()

                try:
                    recognized_text = chat.recognize_speech(file_path)
                    ai_response = chat.chat_text(recognized_text)

                    # TTS 생성
                    import time

                    tts_file = f"ai_response_{int(time.time())}.wav"
                    chat.generate_speech(ai_response, tts_file)
                    chat.play_audio(tts_file)

                except Exception as e:
                    print(f"❌ 오류: {e}")
                    if "세션이 종료되었습니다" in str(e):
                        print("💡 해결방법: 프로그램을 다시 실행하여 새로운 세션을 시작해주세요.")

            elif choice == "4":
                # 대화 히스토리
                print("\n📜 대화 히스토리")
                history = chat.get_chat_history()
                if not history:
                    print("대화 히스토리가 없습니다.")
                else:
                    for i, msg in enumerate(history, 1):
                        role_emoji = "👤" if msg["role"] == "Human" else "🤖"
                        print(f"{i}. {role_emoji} {msg['role']}: {msg['content']}")

            elif choice == "5":
                # 종료
                print("\n👋 프로그램을 종료합니다.")
                break

            else:
                print("❌ 잘못된 선택입니다.")

    except KeyboardInterrupt:
        print("\n\n⚠️  사용자가 중단했습니다.")
    except Exception as e:
        print(f"\n❌ 오류 발생: {e}")
    finally:
        # 세션 정리
        chat.end_session()
        print("🧹 리소스 정리 완료")


if __name__ == "__main__":
    main()
