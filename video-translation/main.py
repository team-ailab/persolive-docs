import json
import os
import time

import requests

input_file_url = "https://samoonsikpoc.blob.core.windows.net/moonsikpoc/우영우_1_kor.mp4"
source_language = "ko"
target_language = "ta"

BASE_URL = "https://live-api.perso.ai"
headers = {
    "Content-Type": "application/json",
    "PersoLive-APIKey": os.environ.get("EST_LIVE_API_KEY"),
}

########## Project 생성

url = f"{BASE_URL}/api/video_translator/v2/project/"

payload = json.dumps(
    {
        "input_file_name": "test.mp4",
        "input_file_url": input_file_url,
        "source_language": source_language,
    }
)

response = requests.request("POST", url, headers=headers, data=payload, timeout=30)

data = response.json()

project_id = data["project_id"]

print(f"프로젝트 {project_id} 생성 완료\n\n")
print(data)

########## Export 생성

url = f"{BASE_URL}/api/video_translator/v2/export/"

payload = json.dumps(
    {
        "export_type": "INITIAL_EXPORT",
        "priority": 0,
        "server_label": "prod",
        "project": project_id,
        "target_language": target_language,
        "lipsync": False,
        "watermark": True,
    }
)

response = requests.request("POST", url, headers=headers, data=payload, timeout=30)
data = response.json()

export_id = data["projectexport_id"]

print(
    f"번역 요청 {export_id} (원본 언어: {source_language} 대상 언어: {target_language} 프로젝트: {project_id}) 생성 완료\n\n"
)

print(data)

while True:
    time.sleep(5)
    request = requests.get(url + f"{export_id}/", headers=headers, timeout=30)

    data = request.json()

    print(f"번역 요청 {export_id} 상태: {data['status']} ({data['status_detail']}) \n\n")

    if data["status"] == "COMPLETED":
        print(f"번역 요청 {export_id} 완료\n\n")
        print(data["video_output_video_with_lipsync"])
        break


########## Export 상태 확인

url = f"{BASE_URL}/api/video_translator/v2/project/{project_id}/"


response = requests.request("GET", url, headers=headers, data=payload, timeout=30)
data = response.json()

########## 번역 수정

script_id = data["scripts"][0]["projectscript_id"]

original_text = data["scripts"][0]["text_original"]

url = f"{BASE_URL}/api/video_translator/v2/script/{script_id}/"

payload = json.dumps(
    {
        # "text_original": "번역을 수정했습니다.",
        # "projectvoice": "pvtv-00000000000000123",
        "text_translated": "I've changed the translation.",
    }
)

response = requests.request("PATCH", url, headers=headers, data=payload, timeout=30)
data = response.json()


print(f"번역 수정 {script_id}: {data}\n\n")


########## 수정된 번역으로 음성생성 (필수)

url = f"{BASE_URL}/api/video_translator/v2/script/{script_id}/generate_audio/"


response = requests.request("POST", url, headers=headers)
data = response.json()


print(f"수정된 번역으로 음성생성 완료 {script_id}: {data}\n\n")
########## 수정된 번역으로 Export 재생성

url = f"{BASE_URL}/api/video_translator/v2/export/"

payload = json.dumps(
    {
        "export_type": "PROOFREAD_EXPORT",
        "server_label": "prod",
        "priority": 0,
        "project": project_id,
        "target_language": target_language,
        "lipsync": False,
        "watermark": True,
    }
)

response = requests.request("POST", url, headers=headers, data=payload, timeout=30)
data = response.json()

export_id = data["projectexport_id"]

print(
    f"번역 요청 {export_id} (원본 언어: {source_language} 대상 언어: {target_language} 프로젝트: {project_id}) 생성 완료\n\n"
)

print(data)

while True:
    time.sleep(5)
    request = requests.get(url + f"{export_id}/", headers=headers, timeout=30)

    data = request.json()

    print(f"번역 요청 {export_id} 상태: {data['status']} ({data['status_detail']}) \n\n")

    if data["status"] == "COMPLETED":
        print(f"번역 요청 {export_id} 완료\n\n")
        print(data["video_output_video_with_lipsync"])
        break
