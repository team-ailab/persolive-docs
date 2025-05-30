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
    print("⚠️  pyaudio is not installed, real-time audio features are limited.")
    print("   Install: pip install pyaudio")


class AvatarChat:
    def __init__(self, api_server: str, api_key: str):
        self.api_server = api_server.rstrip("/")
        self.api_key = api_key
        self.session_id: Optional[str] = None
        self.chat_history: list[dict[str, str]] = []
        self.capability: list[str] = []  # Store capability information

        # Audio settings
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
        """Create session"""
        print("📝 Creating session...")

        data: dict = {"llm_type": llm_type, "tts_type": tts_type, "model_style": model_style, "prompt": prompt}

        if document:
            data["document"] = document
        if background_image:
            data["background_image"] = background_image
        if capability:
            # Filter out STF_WEBRTC for API-only mode compatibility
            filtered_capability = [cap for cap in capability if cap != "STF_WEBRTC"]
            if filtered_capability:
                data["capability"] = filtered_capability
            self.capability = capability  # Store original for later use

            if "STF_WEBRTC" in capability:
                print("ℹ️  STF_WEBRTC capability will be handled in API-only mode")
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
            print(f"✅ Session created: {self.session_id}")
            return self.session_id
        else:
            raise Exception(f"Session creation failed: {response.status_code} - {response.text}")

    def start_session(self):
        """Start session"""
        if not self.session_id:
            raise Exception("Session has not been created.")

        print("🚀 Starting session...")

        # Check if WebRTC connection is needed (only when STF_WEBRTC capability is present)
        needs_webrtc = False  # Always skip WebRTC for API-only mode

        # Note: STF_WEBRTC capability is supported but WebRTC connection is skipped for simplicity
        if "STF_WEBRTC" in self.capability:
            print("ℹ️  STF_WEBRTC capability detected, but using API-only mode for compatibility")

        # 1. ICE server information inquiry (only when WebRTC is needed)
        if needs_webrtc:
            try:
                print("🧊 Querying ICE server information...")
                ice_response = requests.get(f"{self.api_server}/api/v1/session/{self.session_id}/ice-servers/")
                if ice_response.status_code == 200:
                    print("✅ ICE server information query completed")
                else:
                    print(f"⚠️  ICE server query failed: {ice_response.status_code}")
            except Exception as e:
                print(f"⚠️  Error during ICE server query: {e}")

            # 2. Fake SDP exchange (WebRTC connection simulation)
            try:
                print("🔄 SDP exchange in progress...")
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
                    print("✅ SDP exchange completed")
                else:
                    print(f"⚠️  SDP exchange failed: {sdp_response.status_code} - {sdp_response.text}")
            except Exception as e:
                print(f"⚠️  Error during SDP exchange: {e}")
        else:
            print("ℹ️  Skipping WebRTC connection (API-only mode)")

        # 3. Send session start event
        response = requests.post(
            f"{self.api_server}/api/v1/session/{self.session_id}/event/create/",
            headers={"Content-Type": "application/json"},
            json={"event": "SESSION_START", "detail": "Session started via Python"},
        )

        if response.status_code == 201:
            print("✅ Session has been started.")
        else:
            raise Exception(f"Session start failed: {response.status_code} - {response.text}")

    def chat_text(self, message: str) -> str:
        """Chat with AI using text"""
        if not self.session_id:
            raise Exception("Session has not been started.")

        print(f"👤 You: {message}")

        # Add to conversation history
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

            # Process streaming response
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

            print()  # New line

            # Add to conversation history
            self.chat_history.append({"role": "AI", "content": ai_response})
            return ai_response
        else:
            raise Exception(f"LLM request failed: {response.status_code} - {response.text}")

    def generate_speech(self, text: str, save_path: Optional[str] = None) -> bytes:
        """Convert text to speech"""
        if not self.session_id:
            raise Exception("Session has not been started.")

        print("🔊 Generating speech...")

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
                print(f"💾 Audio file saved: {save_path}")

            return audio_data
        else:
            raise Exception(f"TTS request failed: {response.status_code} - {response.text}")

    def recognize_speech(self, audio_file_path: str) -> str:
        """Convert audio file to text"""
        if not self.session_id:
            raise Exception("Session has not been started.")

        # Check session status
        try:
            status = self.get_session_status()
            print(f"📊 Current session status: {status}")
            if status == "TERMINATED":
                raise Exception("Session has been terminated. Please start a new session.")
            elif status != "IN_PROGRESS":
                print(f"⚠️  Session is not in IN_PROGRESS state. Current: {status}")
        except Exception as e:
            print(f"⚠️  Session status check failed: {e}")
            raise e

        print("🎤 Recognizing speech...")

        # Check audio file details
        try:
            with wave.open(audio_file_path, "rb") as wf:
                frames = wf.getnframes()
                sample_rate = wf.getframerate()
                channels = wf.getnchannels()
                duration = frames / float(sample_rate)
                print(f"🎵 Audio info: {duration:.2f}s, {sample_rate}Hz, {channels}ch, {frames}frames")

                if duration < 0.5:
                    print("⚠️  Audio is too short. (Less than 0.5 seconds)")
                elif duration > 30:
                    print("⚠️  Audio is too long. (More than 30 seconds)")
        except Exception as e:
            print(f"⚠️  Audio file analysis failed: {e}")

        # Send audio file as multipart/form-data
        with open(audio_file_path, "rb") as f:
            # Check file size
            file_size = os.path.getsize(audio_file_path)
            print(f"📁 File size: {file_size} bytes")

            files = {"audio": (os.path.basename(audio_file_path), f, "audio/wav")}
            data = {"language": "ko"}

            response = requests.post(
                f"{self.api_server}/api/v1/session/{self.session_id}/stt/",
                files=files,
                data=data,
                timeout=30,  # 30 second timeout
                headers={"User-Agent": "PersoLive-Python-Client/1.0"},
            )

        print(f"📡 Response status: {response.status_code}")

        # Output detailed error information
        if response.status_code != 200:
            print(f"📋 Response headers: {dict(response.headers)}")
            try:
                error_detail = response.json()
                print(f"📝 Error details: {error_detail}")
            except:
                print(f"📝 Response content: {response.text[:500]}...")

        if response.status_code == 200:
            result = response.json()
            recognized_text = result["text"]
            print(f"✅ Recognized text: {recognized_text}")
            return recognized_text
        else:
            raise Exception(f"STT request failed: {response.status_code} - {response.text}")

    def start_recording(self):
        """Start real-time voice recording"""
        if not AUDIO_AVAILABLE:
            print("❌ Cannot record because pyaudio is not installed.")
            return

        if self.is_recording:
            print("⚠️  Already recording.")
            return

        print("🎤 Recording started... (Press Enter to stop)")

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

        # Execute recording in separate thread
        record_thread = threading.Thread(target=record)
        record_thread.start()

        # Wait for Enter input
        input()

        # Stop recording
        self.is_recording = False
        record_thread.join()

        stream.stop_stream()
        stream.close()
        audio.terminate()

        print("🛑 Recording stopped")

        # Save as WAV file
        timestamp = int(time.time())
        audio_file = f"recorded_{timestamp}.wav"

        # Check current directory
        current_dir = os.getcwd()
        full_path = os.path.abspath(audio_file)
        print(f"📂 Current directory: {current_dir}")
        print(f"📍 File save path: {full_path}")

        wf = wave.open(audio_file, "wb")
        wf.setnchannels(self.channels)
        wf.setsampwidth(audio.get_sample_size(self.audio_format))
        wf.setframerate(self.rate)
        wf.writeframes(b"".join(self.audio_frames))
        wf.close()

        # Verify save
        if os.path.exists(audio_file):
            file_size = os.path.getsize(audio_file)
            print(f"💾 Recording file saved: {audio_file} ({file_size} bytes)")
        else:
            print(f"❌ File save failed: {audio_file}")

        return audio_file

    def voice_chat(self) -> str:
        """Voice conversation (Recording → STT → LLM → TTS)"""
        # 1. Voice recording
        audio_file = self.start_recording()
        if not audio_file:
            return ""

        # Check file existence
        if not os.path.exists(audio_file):
            print(f"❌ Recording file not found: {audio_file}")
            return ""

        try:
            # 2. Speech recognition
            recognized_text = self.recognize_speech(audio_file)

            # 3. Chat with AI
            ai_response = self.chat_text(recognized_text)

            # 4. Speech synthesis
            timestamp = int(time.time())
            tts_file = f"ai_response_{timestamp}.wav"
            self.generate_speech(ai_response, tts_file)

            # 5. Audio playback (OS-specific)
            self.play_audio(tts_file)

            return ai_response

        except Exception as e:
            print(f"❌ Error during voice conversation: {e}")
            return ""

        finally:
            # Preserve temporary files for debugging
            # if os.path.exists(audio_file):
            #     os.remove(audio_file)
            print(f"🗂️  Recording file preserved: {audio_file} (for debugging)")

    def play_audio(self, audio_file: str):
        """Play audio file"""
        print(f"🔊 Playing audio: {audio_file}")

        import platform

        system = platform.system()

        if system == "Darwin":  # macOS
            os.system(f"afplay {audio_file}")
        elif system == "Linux":
            os.system(f"aplay {audio_file}")
        elif system == "Windows":
            os.system(f"powershell -c \"(New-Object Media.SoundPlayer '{audio_file}').PlaySync()\"")
        else:
            print("⚠️  Audio playback is not supported on this OS.")

    def end_session(self):
        """End session"""
        if not self.session_id:
            return

        print("🛑 Ending session...")

        response = requests.post(
            f"{self.api_server}/api/v1/session/{self.session_id}/event/create/",
            headers={"Content-Type": "application/json"},
            json={"event": "SESSION_END", "detail": "Session ended via Python"},
        )

        if response.status_code == 201:
            print("✅ Session has been ended.")
        else:
            print(f"⚠️  Session end failed: {response.status_code}")

        self.session_id = None

    def get_chat_history(self):
        """Return conversation history"""
        return self.chat_history

    def get_session_status(self) -> str:
        """Query session status"""
        if not self.session_id:
            raise Exception("Session has not been created.")

        response = requests.get(f"{self.api_server}/api/v1/session/{self.session_id}/")

        if response.status_code == 200:
            result = response.json()
            return result.get("status", "UNKNOWN")
        else:
            raise Exception(f"Session status query failed: {response.status_code} - {response.text}")

    def wait_for_session_ready(self, timeout: int = 30):
        """Wait until session becomes IN_PROGRESS state"""
        import time

        print("⏳ Waiting for session to be ready...")

        start_time = time.time()
        while time.time() - start_time < timeout:
            try:
                status = self.get_session_status()
                print(f"📊 Session status: {status}")

                if status == "IN_PROGRESS":
                    print("✅ Session ready!")
                    return True
                elif status == "TERMINATED":
                    raise Exception("Session has been terminated.")

                time.sleep(1)  # Wait 1 second

            except Exception as e:
                print(f"⚠️  Error during status check: {e}")
                time.sleep(1)

        raise Exception(f"Session was not ready within {timeout} seconds.")

    def recreate_session_if_needed(self):
        """Recreate session if needed"""
        try:
            status = self.get_session_status()
            if status == "TERMINATED":
                print("🔄 Session has been terminated, creating a new session...")
                return False  # Recreation needed
        except:
            print("🔄 Session status check failed, creating a new session...")
            return False  # Recreation needed

        return True  # Existing session can be used
