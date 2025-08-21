import argparse
import json
import os
import time
import urllib.parse
from pathlib import Path

import requests


def parse_arguments():
    """Command line argument parser"""
    parser = argparse.ArgumentParser(
        description="AI Studio API Client - TTS and STF (Speech-to-Face) Tasks",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Basic TTS + STF workflow
  python main.py --tts-text "Hello world" --tts-type "yuri" --stf-model-style "yuri-front_natural"
  
  # Multiple TTS texts
  python main.py --tts-text "Hello" "I am AI" --tts-type "azuretts-ko-KR-InJoonNeural-sad"
  
  # Check available types (optional)
  python main.py --check-types tts_type
  python main.py --check-types modelstyle
  
  # Custom save directory
  python main.py --tts-text "Hello" --save-dir "./my-outputs"
        """,
    )

    parser.add_argument(
        "--check-types",
        choices=["tts_type", "modelstyle"],
        help="Check available TTS types or model styles",
    )

    # TTS text input (default when check-types is not used)
    parser.add_argument(
        "--tts-text",
        nargs="+",
        default=["hello"],
        help="Text(s) to convert to speech (can provide multiple texts)",
    )

    # TTS/STF arguments (required when not checking types)
    parser.add_argument(
        "--tts-type",
        default="yuri",
        help="TTS type to use (default: yuri)",
    )
    parser.add_argument(
        "--stf-model-style",
        default="yoori-front-khaki_overalls-nodded_loop",
        help="STF model style (default: yuri-front_natural)",
    )
    parser.add_argument(
        "--tts-audio-format",
        default="wav_16bit_32000hz_mono",
        help="TTS audio format (default: wav_16bit_32000hz_mono)",
    )
    parser.add_argument(
        "--base-url",
        default="https://live-api.perso.ai",
        help="API base URL (default: https://live-api.perso.ai)",
    )
    parser.add_argument("--agent", default="1", help="Agent ID (default: 1)")
    parser.add_argument(
        "--save-dir",
        default="user-uploads",
        help="Directory to save downloaded files (default: user-uploads)",
    )
    parser.add_argument(
        "--api-key",
        help="API key (if not provided, will use EST_LIVE_API_KEY environment variable)",
    )
    parser.add_argument(
        "--skip-stf",
        action="store_true",
        help="Skip STF (Speech-to-Face) generation",
    )
    parser.add_argument(
        "--skip-photo-avatar",
        action="store_true",
        help="Skip Photo Avatar generation",
    )
    parser.add_argument(
        "--photo-avatar-input-image",
        default="https://sa01persosaasdev.blob.core.windows.net/user-uploads/perso-studio-task/test/photo_avartar_sonic.jpg?sp=r&st=2025-08-21T01:24:51Z&se=2025-11-21T09:39:51Z&spr=https&sv=2024-11-04&sr=b&sig=mUuh%2B%2FKCwmrlBbszVbdI4pywOFZkpb%2BZ%2B3t3Zt5Q%2Fso%3D",
        help="Input image file path or URL for Photo Avatar",
    )
    return parser.parse_args()


def download_file(url: str, save_dir: str = "user-uploads") -> str:
    """Download file from URL and return local path."""
    # Create save directory
    Path(save_dir).mkdir(parents=True, exist_ok=True)

    # Extract filename from URL
    parsed_url = urllib.parse.urlparse(url)
    file_path = parsed_url.path
    file_name = os.path.basename(file_path)

    # Save file path
    save_path = os.path.join(save_dir, file_name)

    # Download file
    response = requests.get(url, stream=True, timeout=30)
    response.raise_for_status()

    with open(save_path, "wb") as f:
        for chunk in response.iter_content(chunk_size=8192):
            f.write(chunk)

    return save_path


def check_types(base_url: str, headers: dict, type_name: str = "tts_type"):
    """Check available TTS (Text To Speech) types."""
    url = f"{base_url}/api/v1/settings/{type_name}/"

    try:
        response = requests.get(url, headers=headers, timeout=30)
        print(f"📡 Status Code: {response.status_code}")

        if response.status_code == 200:
            types = response.json()
            type_names = [n["name"] for n in types]
            print(f"✅ Available {type_name} types ({len(type_names)} items):")
            for i, name in enumerate(type_names, 1):
                print(f"  {i:2d}. {name}")
        else:
            print(f"❌ Error: {response.text}")

    except requests.exceptions.RequestException as e:
        print(f"❌ Request failed: {e}")


def tts_task(
    base_url: str,
    headers: dict,
    tts_text: list,
    tts_type: str = "yuri",
    tts_audio_format: str = "wav_16bit_32000hz_mono",
    agent: str = "1",
):
    """Perform TTS task."""
    print("🎵 Starting TTS task...")
    print(f"📝 Texts: {tts_text}")
    print(f"🔊 TTS Type: {tts_type}")
    print(f"🎛️  Audio Format: {tts_audio_format}")

    url = f"{base_url}/api/studio/v1/task/tts/"

    payload = json.dumps(
        {
            "agent": agent,
            "tts_type": tts_type,
            "tts_audio_format": tts_audio_format,
            "tts_text": tts_text,
        }
    )
    response = requests.post(url, headers=headers, data=payload, timeout=30)
    data = response.json()

    if response.status_code >= 400:
        print(f"❌ TTS request failed: {response.status_code}")
        print(response.text)
        return None

    print(f"⏳ TTS task started (Task ID: {data['task_id']})")

    while True:
        time.sleep(5)
        response = requests.get(
            url + f"{data['task_id']}/", headers=headers, timeout=30
        )
        data = response.json()
        print(f"⏳ TTS task status: {data['status']}")

        if data["status"] == "COMPLETED":
            audio_url = data["tts_output_audio"]
            return audio_url
        elif data["status"] == "FAILED":
            print(f"❌ TTS task failed: {data.get('failure_reason', 'Unknown error')}")
            return None


def stf_task(
    base_url: str,
    headers: dict,
    stf_input_audio: str,
    stf_model_style: str = "yuri-front_natural",
    agent: str = "1",
):
    """Perform STF (Speech To Face) task."""
    print("🎭 Starting STF task...")
    print(f"🎵 Input audio: {stf_input_audio}")
    print(f"👤 Model style: {stf_model_style}")

    url = f"{base_url}/api/studio/v1/task/stf/"

    # Remove Content-Type header for multipart/form-data
    upload_headers = headers.copy()
    upload_headers.pop("Content-Type", None)

    data = {
        "agent": agent,
        "stf_model_style": stf_model_style,
    }

    try:
        with open(stf_input_audio, "rb") as f:
            files = {
                "stf_input_audio": (os.path.basename(stf_input_audio), f, "audio/wav")
            }
            response = requests.post(
                url, headers=upload_headers, data=data, files=files, timeout=30
            )
    except FileNotFoundError:
        print(f"❌ Audio file not found: {stf_input_audio}")
        return None

    data = response.json()
    if response.status_code >= 400:
        print(f"❌ STF request failed: {response.status_code}")
        print(response.text)
        return None

    print(f"⏳ STF task started (Task ID: {data['task_id']})")

    while True:
        time.sleep(5)
        response = requests.get(
            url + f"{data['task_id']}/", headers=headers, timeout=30
        )
        data = response.json()
        print(f"⏳ STF task status: {data['status']}")

        if data["status"] == "COMPLETED":
            video_url = data["stf_output_video"]
            print("✅ STF task completed!")
            print(f"🎥 Output video: {video_url}")
            return video_url
        elif data["status"] == "FAILED":
            print(f"❌ STF task failed: {data.get('failure_reason', 'Unknown error')}")
            return None


def photo_avatar_task(
    base_url: str,
    headers: dict,
    photo_avatar_input_image: str,
    photo_avatar_input_audio: str,
    agent: str = "1",
):
    """Perform Photo Avatar task."""
    print("🎭 Starting Photo Avatar task...")
    print(f"🖼️ Input image: {photo_avatar_input_image}")
    print(f"🎵 Input audio: {photo_avatar_input_audio}")

    url = f"{base_url}/api/studio/v1/task/photoavatar/"

    # Remove Content-Type header for multipart/form-data
    upload_headers = headers.copy()
    upload_headers.pop("Content-Type", None)

    data = {
        "agent": agent,
    }
    files = {}

    try:
        if photo_avatar_input_image.startswith(("http://", "https://")):
            # URL인 경우 data에 추가
            data["photoavatar_input_image_url"] = photo_avatar_input_image
        else:
            # 파일인 경우 files에 추가
            with open(photo_avatar_input_image, "rb") as f:
                files["photoavatar_input_image"] = (
                    os.path.basename(photo_avatar_input_image),
                    f,
                    "image/jpeg",
                )

        if photo_avatar_input_audio.startswith(("http://", "https://")):
            # URL인 경우 data에 추가
            data["photoavatar_input_audio_url"] = photo_avatar_input_audio
        else:
            # 파일인 경우 files에 추가
            with open(photo_avatar_input_audio, "rb") as f:
                files["photoavatar_input_audio"] = (
                    os.path.basename(photo_avatar_input_audio),
                    f,
                    "audio/wav",
                )
    except FileNotFoundError as e:
        print(f"❌ {e}")
        return None

    if files:
        response = requests.post(
            url, headers=upload_headers, data=data, files=files, timeout=30
        )
    else:
        response = requests.post(url, headers=upload_headers, data=data, timeout=30)

    data = response.json()
    if response.status_code >= 400:
        print(f"❌ Photo Avatar request failed: {response.status_code}")
        print(response.text)
        return None

    print(f"⏳ Photo Avatar task started (Task ID: {data['task_id']})")

    while True:
        time.sleep(5)
        response = requests.get(
            url + f"{data['task_id']}/", headers=headers, timeout=30
        )
        data = response.json()
        print(f"⏳ Photo Avatar task status: {data['status']}")

        if data["status"] == "COMPLETED":
            video_url = data["photoavatar_output_video"]
            print("✅ Photo Avatar task completed!")
            return video_url
        elif data["status"] == "FAILED":
            print(
                f"❌ Photo Avatar task failed: {data.get('failure_reason', 'Unknown error')}"
            )
            return None


def main():
    # Parse command line arguments
    args = parse_arguments()

    # Set up API configuration
    base_url = args.base_url
    api_key = args.api_key or os.environ.get("EST_LIVE_API_KEY")

    if not api_key:
        print(
            "❌ Error: API key is required. Provide it via --api-key argument or EST_LIVE_API_KEY environment variable."
        )
        return 1

    headers = {
        "Content-Type": "application/json",
        "PersoLive-APIKey": api_key,
    }

    print("🤖 AI Studio API Client")
    print(f"🔗 Base URL: {base_url}")
    print("=" * 50)

    # Check types mode (optional)
    if args.check_types:
        check_types(base_url, headers, args.check_types)
        return 0

    # TTS + STF workflow mode
    if not args.tts_text:
        print("❌ Error: --tts-text is required for TTS/STF workflow")
        return 1

    # TTS task
    audio_url = tts_task(
        base_url=base_url,
        headers=headers,
        tts_text=args.tts_text,
        tts_type=args.tts_type,
        tts_audio_format=args.tts_audio_format,
        agent=args.agent,
    )

    local_audio_path = download_file(audio_url, args.save_dir)
    print(f"✅ Audio file downloaded: {local_audio_path}")

    if not local_audio_path:
        print("❌ TTS task failed.")
        return 1

    print("\n🎉 TTS task completed successfully!")
    print(f"🎵 Audio URL: {audio_url}")
    print(f"🎵 Audio file: {local_audio_path}")

    # STF task
    if not args.skip_stf:
        video_url = stf_task(
            base_url=base_url,
            headers=headers,
            stf_input_audio=local_audio_path,
            stf_model_style=args.stf_model_style,
            agent=args.agent,
        )

        if not video_url:
            print("❌ STF task failed.")
            return 1

        print("\n🎉 STF task completed successfully!")
        print(f"🎥 Video URL: {video_url}")

    # Photo Avatar task
    if not args.skip_photo_avatar:
        video_url = photo_avatar_task(
            base_url=base_url,
            headers=headers,
            photo_avatar_input_image=args.photo_avatar_input_image,
            photo_avatar_input_audio=audio_url,
            agent=args.agent,
        )

        if not video_url:
            print("❌ Photo Avatar task failed.")
            return 1

        print("\n🎉 Photo Avatar task completed successfully!")
        print(f"🎥 Video URL: {video_url}")

    print("\n🎉 All tasks completed successfully!")
    return 0


if __name__ == "__main__":
    exit(main())
