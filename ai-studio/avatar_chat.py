# avatar_chat.py
import base64
import json
import os
import threading
import time
import wave
from typing import Optional

import requests

try:
    import pyaudio

    AUDIO_AVAILABLE = True
except ImportError:
    AUDIO_AVAILABLE = False
    print("⚠️  pyaudio가 설치되지 않아 실시간 음성 기능이 제한됩니다.")
    print("   설치: pip install pyaudio")


class AvatarChat:
    def __init__(self, api_server: str, api_key: str):
        self.api_server = api_server.rstrip("/")
        self.api_key = api_key
        self.session_id: Optional[str] = None
        self.chat_history: list[dict[str, str]] = []

        # 오디오 설정
        self.audio_format = pyaudio.paInt16 if AUDIO_AVAILABLE else None
        self.channels = 1
        self.rate = 16000
        self.chunk = 1024
        self.is_recording = False
        self.audio_frames: list[bytes] = []

    def create_session(
        self,
        llm_type: str,
        tts_type: str,
        model_style: str,
        prompt: str,
        document: Optional[str] = None,
        background_image: Optional[str] = None,
        capability: Optional[list[str]] = None,
        stt_type: Optional[str] = None,
    ) -> Optional[str]:
        """세션 생성"""
        print("📝 세션 생성 중...")

        data: dict = {"llm_type": llm_type, "tts_type": tts_type, "model_style": model_style, "prompt": prompt}

        if document:
            data["document"] = document
        if background_image:
            data["background_image"] = background_image
        if capability:
            data["capability"] = capability
        if stt_type:
            data["stt_type"] = stt_type

        response = requests.post(
            f"{self.api_server}/api/v1/session/",
            headers={"PersoLive-APIKey": self.api_key, "Content-Type": "application/json"},
            json=data,
        )

        if response.status_code == 201:
            result = response.json()
            self.session_id = result["session_id"]
            print(f"✅ 세션 생성됨: {self.session_id}")
            return self.session_id
        else:
            raise Exception(f"세션 생성 실패: {response.status_code} - {response.text}")

    def start_session(self):
        """세션 시작"""
        if not self.session_id:
            raise Exception("세션이 생성되지 않았습니다.")

        print("🚀 세션 시작 중...")

        # WebRTC 연결이 필요한지 확인 (STF_WEBRTC capability가 있는 경우에만)
        needs_webrtc = False  # 기본값: WebRTC 불필요

        # 1. ICE 서버 정보 조회 (WebRTC 필요한 경우만)
        if needs_webrtc:
            try:
                print("🧊 ICE 서버 정보 조회 중...")
                ice_response = requests.get(f"{self.api_server}/api/v1/session/{self.session_id}/ice-servers/")
                if ice_response.status_code == 200:
                    print("✅ ICE 서버 정보 조회 완료")
                else:
                    print(f"⚠️  ICE 서버 조회 실패: {ice_response.status_code}")
            except Exception as e:
                print(f"⚠️  ICE 서버 조회 중 오류: {e}")

            # 2. 가짜 SDP 교환 (WebRTC 연결 시뮬레이션)
            try:
                print("🔄 SDP 교환 중...")
                fake_sdp = {
                    "type": "offer",
                    "sdp": "v=0\r\no=- 123456 0 IN IP4 127.0.0.1\r\ns=-\r\nt=0 0\r\nm=audio 9 UDP/TLS/RTP/SAVPF 0\r\nc=IN IP4 0.0.0.0\r\na=inactive\r\n",
                }

                sdp_response = requests.post(
                    f"{self.api_server}/api/v1/session/{self.session_id}/exchange/",
                    headers={"Content-Type": "application/json"},
                    json={"client_sdp": fake_sdp},
                )

                if sdp_response.status_code == 200:
                    print("✅ SDP 교환 완료")
                else:
                    print(f"⚠️  SDP 교환 실패: {sdp_response.status_code} - {sdp_response.text}")
            except Exception as e:
                print(f"⚠️  SDP 교환 중 오류: {e}")
        else:
            print("ℹ️  WebRTC 연결 건너뛰기 (API 전용 모드)")

        # 3. 세션 시작 이벤트 전송
        response = requests.post(
            f"{self.api_server}/api/v1/session/{self.session_id}/event/create/",
            headers={"Content-Type": "application/json"},
            json={"event": "SESSION_START", "detail": "Session started via Python"},
        )

        if response.status_code == 201:
            print("✅ 세션이 시작되었습니다.")
        else:
            raise Exception(f"세션 시작 실패: {response.status_code} - {response.text}")

    def chat_text(self, message: str) -> str:
        """텍스트로 AI와 대화"""
        if not self.session_id:
            raise Exception("세션이 시작되지 않았습니다.")

        print(f"👤 You: {message}")

        # 대화 히스토리에 추가
        self.chat_history.append({"role": "Human", "content": message})

        response = requests.post(
            f"{self.api_server}/api/v1/session/{self.session_id}/llm/",
            headers={"Content-Type": "application/json"},
            json={"message": message, "clear_history": False},
            stream=True,
        )

        if response.status_code == 200:
            print("🤖 AI: ", end="", flush=True)
            ai_response = ""

            # 스트리밍 응답 처리
            for line in response.iter_lines():
                if line:
                    line_str = line.decode("utf-8")
                    if line_str.startswith("data: "):
                        try:
                            data = json.loads(line_str[6:])
                            if data.get("status") == "success":
                                sentence = data.get("sentence", "")
                                print(sentence, end="", flush=True)
                                ai_response += sentence
                        except json.JSONDecodeError:
                            continue

            print()  # 줄바꿈

            # 대화 히스토리에 추가
            self.chat_history.append({"role": "AI", "content": ai_response})
            return ai_response
        else:
            raise Exception(f"LLM 요청 실패: {response.status_code} - {response.text}")

    def generate_speech(self, text: str, save_path: Optional[str] = None) -> bytes:
        """텍스트를 음성으로 변환"""
        if not self.session_id:
            raise Exception("세션이 시작되지 않았습니다.")

        print("🔊 음성 생성 중...")

        response = requests.post(
            f"{self.api_server}/api/v1/session/{self.session_id}/tts/",
            headers={"Content-Type": "application/json"},
            json={"text": text},
        )

        if response.status_code == 200:
            result = response.json()
            audio_data = base64.b64decode(result["audio"])

            if save_path:
                with open(save_path, "wb") as f:
                    f.write(audio_data)
                print(f"💾 음성 파일 저장됨: {save_path}")

            return audio_data
        else:
            raise Exception(f"TTS 요청 실패: {response.status_code} - {response.text}")

    def recognize_speech(self, audio_file_path: str) -> str:
        """음성 파일을 텍스트로 변환"""
        if not self.session_id:
            raise Exception("세션이 시작되지 않았습니다.")

        # 세션 상태 확인
        try:
            status = self.get_session_status()
            print(f"📊 현재 세션 상태: {status}")
            if status == "TERMINATED":
                raise Exception("세션이 종료되었습니다. 새로운 세션을 시작해주세요.")
            elif status != "IN_PROGRESS":
                print(f"⚠️  세션이 IN_PROGRESS 상태가 아닙니다. 현재: {status}")
        except Exception as e:
            print(f"⚠️  세션 상태 확인 실패: {e}")
            raise e

        print("🎤 음성 인식 중...")

        # 오디오 파일 상세 정보 확인
        try:
            with wave.open(audio_file_path, "rb") as wf:
                frames = wf.getnframes()
                sample_rate = wf.getframerate()
                channels = wf.getnchannels()
                duration = frames / float(sample_rate)
                print(f"🎵 오디오 정보: {duration:.2f}초, {sample_rate}Hz, {channels}채널, {frames}프레임")

                if duration < 0.5:
                    print("⚠️  오디오가 너무 짧습니다. (0.5초 미만)")
                elif duration > 30:
                    print("⚠️  오디오가 너무 깁니다. (30초 초과)")
        except Exception as e:
            print(f"⚠️  오디오 파일 분석 실패: {e}")

        # 오디오 파일을 multipart/form-data로 전송
        with open(audio_file_path, "rb") as f:
            # 파일 크기 확인
            file_size = os.path.getsize(audio_file_path)
            print(f"📁 파일 크기: {file_size} bytes")

            files = {"audio": (os.path.basename(audio_file_path), f, "audio/wav")}
            data = {"language": "ko"}

            response = requests.post(
                f"{self.api_server}/api/v1/session/{self.session_id}/stt/",
                files=files,
                data=data,
                timeout=30,  # 30초 타임아웃
                headers={"User-Agent": "PersoLive-Python-Client/1.0"},
            )

        print(f"📡 응답 상태: {response.status_code}")

        # 상세한 에러 정보 출력
        if response.status_code != 200:
            print(f"📋 응답 헤더: {dict(response.headers)}")
            try:
                error_detail = response.json()
                print(f"📝 에러 상세: {error_detail}")
            except:
                print(f"📝 응답 내용: {response.text[:500]}...")

        if response.status_code == 200:
            result = response.json()
            recognized_text = result["text"]
            print(f"✅ 인식된 텍스트: {recognized_text}")
            return recognized_text
        else:
            raise Exception(f"STT 요청 실패: {response.status_code} - {response.text}")

    def start_recording(self):
        """실시간 음성 녹음 시작"""
        if not AUDIO_AVAILABLE:
            print("❌ pyaudio가 설치되지 않아 녹음할 수 없습니다.")
            return

        if self.is_recording:
            print("⚠️  이미 녹음 중입니다.")
            return

        print("🎤 녹음 시작... (Enter를 눌러 종료)")

        self.is_recording = True
        self.audio_frames = []

        audio = pyaudio.PyAudio()
        stream = audio.open(
            format=self.audio_format, channels=self.channels, rate=self.rate, input=True, frames_per_buffer=self.chunk
        )

        def record():
            while self.is_recording:
                data = stream.read(self.chunk)
                self.audio_frames.append(data)

        # 별도 스레드에서 녹음 실행
        record_thread = threading.Thread(target=record)
        record_thread.start()

        # Enter 입력 대기
        input()

        # 녹음 종료
        self.is_recording = False
        record_thread.join()

        stream.stop_stream()
        stream.close()
        audio.terminate()

        print("🛑 녹음 종료")

        # WAV 파일로 저장
        timestamp = int(time.time())
        audio_file = f"recorded_{timestamp}.wav"

        # 현재 디렉토리 확인
        current_dir = os.getcwd()
        full_path = os.path.abspath(audio_file)
        print(f"📂 현재 디렉토리: {current_dir}")
        print(f"📍 파일 저장 경로: {full_path}")

        wf = wave.open(audio_file, "wb")
        wf.setnchannels(self.channels)
        wf.setsampwidth(audio.get_sample_size(self.audio_format))
        wf.setframerate(self.rate)
        wf.writeframes(b"".join(self.audio_frames))
        wf.close()

        # 저장 확인
        if os.path.exists(audio_file):
            file_size = os.path.getsize(audio_file)
            print(f"💾 녹음 파일 저장됨: {audio_file} ({file_size} bytes)")
        else:
            print(f"❌ 파일 저장 실패: {audio_file}")

        return audio_file

    def voice_chat(self) -> str:
        """음성으로 대화 (녹음 → STT → LLM → TTS)"""
        # 1. 음성 녹음
        audio_file = self.start_recording()
        if not audio_file:
            return ""

        # 파일 존재 확인
        if not os.path.exists(audio_file):
            print(f"❌ 녹음 파일을 찾을 수 없습니다: {audio_file}")
            return ""

        try:
            # 2. 음성 인식
            recognized_text = self.recognize_speech(audio_file)

            # 3. AI와 대화
            ai_response = self.chat_text(recognized_text)

            # 4. 음성 합성
            timestamp = int(time.time())
            tts_file = f"ai_response_{timestamp}.wav"
            self.generate_speech(ai_response, tts_file)

            # 5. 음성 재생 (OS별)
            self.play_audio(tts_file)

            return ai_response

        except Exception as e:
            print(f"❌ 음성 대화 중 오류: {e}")
            return ""

        finally:
            # 잠시 후 임시 파일 삭제 (디버깅을 위해 주석 처리)
            # if os.path.exists(audio_file):
            #     os.remove(audio_file)
            print(f"🗂️  녹음 파일 보존됨: {audio_file} (디버깅용)")

    def play_audio(self, audio_file: str):
        """음성 파일 재생"""
        print(f"🔊 음성 재생: {audio_file}")

        import platform

        system = platform.system()

        if system == "Darwin":  # macOS
            os.system(f"afplay {audio_file}")
        elif system == "Linux":
            os.system(f"aplay {audio_file}")
        elif system == "Windows":
            os.system(f"powershell -c \"(New-Object Media.SoundPlayer '{audio_file}').PlaySync()\"")
        else:
            print("⚠️  음성 재생을 지원하지 않는 OS입니다.")

    def end_session(self):
        """세션 종료"""
        if not self.session_id:
            return

        print("🛑 세션 종료 중...")

        response = requests.post(
            f"{self.api_server}/api/v1/session/{self.session_id}/event/create/",
            headers={"Content-Type": "application/json"},
            json={"event": "SESSION_END", "detail": "Session ended via Python"},
        )

        if response.status_code == 201:
            print("✅ 세션이 종료되었습니다.")
        else:
            print(f"⚠️  세션 종료 실패: {response.status_code}")

        self.session_id = None

    def get_chat_history(self):
        """대화 히스토리 반환"""
        return self.chat_history

    def get_session_status(self) -> str:
        """세션 상태 조회"""
        if not self.session_id:
            raise Exception("세션이 생성되지 않았습니다.")

        response = requests.get(f"{self.api_server}/api/v1/session/{self.session_id}/")

        if response.status_code == 200:
            result = response.json()
            return result.get("status", "UNKNOWN")
        else:
            raise Exception(f"세션 상태 조회 실패: {response.status_code} - {response.text}")

    def wait_for_session_ready(self, timeout: int = 30):
        """세션이 IN_PROGRESS 상태가 될 때까지 대기"""
        import time

        print("⏳ 세션이 준비될 때까지 대기 중...")

        start_time = time.time()
        while time.time() - start_time < timeout:
            try:
                status = self.get_session_status()
                print(f"📊 세션 상태: {status}")

                if status == "IN_PROGRESS":
                    print("✅ 세션 준비 완료!")
                    return True
                elif status == "TERMINATED":
                    raise Exception("세션이 종료되었습니다.")

                time.sleep(1)  # 1초 대기

            except Exception as e:
                print(f"⚠️  상태 확인 중 오류: {e}")
                time.sleep(1)

        raise Exception(f"세션이 {timeout}초 내에 준비되지 않았습니다.")

    def recreate_session_if_needed(self):
        """필요시 세션 재생성"""
        try:
            status = self.get_session_status()
            if status == "TERMINATED":
                print("🔄 세션이 종료되어 새로운 세션을 생성합니다...")
                return False  # 재생성 필요
        except:
            print("🔄 세션 상태 확인 실패, 새로운 세션을 생성합니다...")
            return False  # 재생성 필요

        return True  # 기존 세션 사용 가능
