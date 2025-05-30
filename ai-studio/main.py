import json
import os
import time
import urllib.parse
from pathlib import Path

import requests

BASE_URL = "https://live-api.perso.ai"
headers = {
    "Content-Type": "application/json",
    "PersoLive-APIKey": os.environ.get("EST_LIVE_API_KEY"),
}


def download_file(url: str, save_dir: str = "user-uploads") -> str:
    """URL에서 파일을 다운로드하고 로컬 경로를 반환합니다."""
    # 저장 디렉토리 생성
    Path(save_dir).mkdir(parents=True, exist_ok=True)

    # URL에서 파일 이름 추출
    parsed_url = urllib.parse.urlparse(url)
    file_path = parsed_url.path
    file_name = os.path.basename(file_path)

    # 파일 저장 경로
    save_path = os.path.join(save_dir, file_name)

    # 파일 다운로드
    response = requests.get(url, stream=True, timeout=30)
    response.raise_for_status()

    with open(save_path, "wb") as f:
        for chunk in response.iter_content(chunk_size=8192):
            f.write(chunk)

    return save_path


def check_types(type="tts_type"):
    """사용 가능한 TTS(Text To Speech) 타입들을 확인합니다."""
    url = f"{BASE_URL}/api/v1/settings/{type}/"

    try:
        response = requests.get(url, headers=headers, timeout=30)
        print(f"Status Code: {response.status_code}")

        if response.status_code == 200:
            types = response.json()
            print(f"사용 가능한 {type} 타입들: {[n['name'] for n in types]}")
        else:
            print(f"Error: {response.text}")

    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")


def tts_task(
    tts_text=["안녕하세요", "저는 AI 아바타입니다", "어떻게 도와드릴까요?"], tts_type="azuretts-ko-KR-InJoonNeural-sad"
):
    """TTS 작업을 수행합니다."""
    url = f"{BASE_URL}/api/studio/v1/task/tts/"

    payload = json.dumps(
        {
            "agent": "1",
            "tts_type": tts_type,
            "tts_audio_format": "wav_16bit_32000hz_mono",
            "tts_text": tts_text,
        }
    )
    response = requests.post(url, headers=headers, data=payload, timeout=30)
    data = response.json()
    if response.status_code >= 400:
        print(response.status_code)
        print(response.text)
        return

    while True:
        time.sleep(5)
        response = requests.get(url + f"{data['task_id']}/", headers=headers, timeout=30)
        data = response.json()
        print(f"TTS 작업 상태: {data['status']}")
        if data["status"] == "COMPLETED":
            audio_url = data["tts_output_audio"]
            local_path = download_file(audio_url)
            print(f"오디오 파일이 다운로드 되었습니다: {local_path}")
            return local_path


def stf_task(stf_input_audio, stf_model_style="indian_m_2_aaryan-side-white_jacket-natural"):
    """STF(Speech To Face) 작업을 수행합니다."""
    url = f"{BASE_URL}/api/studio/v1/task/stf/"

    # multipart/form-data를 위해 Content-Type 헤더 제거
    upload_headers = headers.copy()
    upload_headers.pop("Content-Type", None)

    data = {
        "agent": "1",
        "stf_model_style": stf_model_style,
    }

    files = {"stf_input_audio": open(stf_input_audio, "rb")}  # 파일 객체

    response = requests.post(url, headers=upload_headers, data=data, files=files, timeout=30)
    data = response.json()
    if response.status_code >= 400:
        print(response.status_code)
        print(response.text)
        return

    while True:
        time.sleep(5)
        response = requests.get(url + f"{data['task_id']}/", headers=headers, timeout=30)
        data = response.json()
        print(f"STF 작업 상태: {data['status']}")
        if data["status"] == "COMPLETED":
            print(data["stf_output_video"])
            return data["stf_output_video"]


if __name__ == "__main__":
    # check_types(type="modelstyle")  # type: tts_type, modelstyle
    local_path = tts_task(tts_text=["안녕하세요", "저는 AI 아바타입니다", "어떻게 도와드릴까요?"], tts_type="yuri")
    stf_task(stf_input_audio=local_path, stf_model_style="yuri-front_natural")
