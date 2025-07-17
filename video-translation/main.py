import argparse
import json
import os
import time
from urllib.parse import urlparse

import requests


def parse_arguments():
    """Command line argument parser"""
    parser = argparse.ArgumentParser(
        description="Video Translation API Client",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py --input-url "https://example.com/video.mp4" --source-lang ko --target-lang en
  python main.py --input-url "https://example.com/video.mp4" --source-lang ko --target-lang en --lipsync --no-watermark
        """,
    )

    # Required arguments
    parser.add_argument(
        "--input-url",
        default="https://samoonsikpoc.blob.core.windows.net/moonsikpoc/우영우_1_kor.mp4",
        help="Public URL to the input video file",
    )
    parser.add_argument("--source-lang", default="ko", help="Source language code (e.g., 'ko', 'en', 'ja')")
    parser.add_argument("--target-lang", default="en", help="Target language code (e.g., 'ko', 'en', 'ja')")

    # Optional arguments
    parser.add_argument("--input-name", help="Input file name (if not provided, will be extracted from URL)")
    parser.add_argument(
        "--base-url",
        default="https://live-api.perso.ai",
        help="API base URL (default: https://live-api.perso.ai)",
    )
    parser.add_argument("--lipsync", action="store_true", help="Enable lip-sync in the output video")
    parser.add_argument("--no-watermark", action="store_true", help="Disable watermark in the output video")
    parser.add_argument(
        "--api-key",
        help="API key (if not provided, will use EST_LIVE_API_KEY environment variable)",
    )
    parser.add_argument("--server-label", default="", help="Server label (default: empty - use any available server)")

    return parser.parse_args()


def extract_filename_from_url(url):
    """Extract filename from URL"""
    parsed_url = urlparse(url)
    filename = os.path.basename(parsed_url.path)
    return filename if filename else "video.mp4"


def main():
    # Parse command line arguments
    args = parse_arguments()

    # Set up variables from arguments
    input_file_url = args.input_url
    source_language = args.source_lang
    target_language = args.target_lang
    input_file_name = args.input_name or extract_filename_from_url(input_file_url)
    BASE_URL = args.base_url
    lipsync = args.lipsync
    watermark = not args.no_watermark  # Reverse the logic since no_watermark is the flag

    # Set up API key
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

    print("🎬 Starting video translation...")
    print(f"📁 Input file: {input_file_name}")
    print(f"🔗 Input URL: {input_file_url}")
    print(f"🌍 Source language: {source_language}")
    print(f"🌍 Target language: {target_language}")
    print(f"💋 Lip-sync: {'Enabled' if lipsync else 'Disabled'}")
    print(f"🏷️  Watermark: {'Enabled' if watermark else 'Disabled'}")
    print("=" * 50)

    ########## Create Project

    url = f"{BASE_URL}/api/video_translator/v2/project/"

    payload = json.dumps(
        {
            "input_file_name": input_file_name,
            "input_file_url": input_file_url,
            "source_language": source_language,
        }
    )

    response = requests.request("POST", url, headers=headers, data=payload, timeout=30)

    data = response.json()

    project_id = data["project_id"]

    print(f"✅ Project {project_id} created successfully\n")
    print(data)

    ########## Create Export

    url = f"{BASE_URL}/api/video_translator/v2/export/"

    payload = json.dumps(
        {
            "export_type": "INITIAL_EXPORT",
            "priority": 0,
            "server_label": args.server_label,
            "project": project_id,
            "target_language": target_language,
            "lipsync": lipsync,
            "watermark": watermark,
        }
    )

    response = requests.request("POST", url, headers=headers, data=payload, timeout=30)
    if response.status_code >= 400:
        print(f"❌ Error: {response.json()}")
        return 1

    data = response.json()

    export_id = data["projectexport_id"]

    print(
        f"🚀 Translation request {export_id} (source: {source_language} target: {target_language} project: {project_id}) created successfully\n"
    )

    print(data)

    while True:
        time.sleep(5)
        request = requests.get(url + f"{export_id}/", headers=headers, timeout=30)

        data = request.json()

        print(f"⏳ Translation request {export_id} status: {data['status']} ({data['status_detail']})\n")

        if data["status"] == "COMPLETED":
            print(f"🎉 Translation request {export_id} completed!\n")
            print(f"🎥 Output video (with lip-sync): {data.get('video_output_video_with_lipsync', 'N/A')}")
            print(f"🎥 Output video (without lip-sync): {data.get('video_output_video_without_lipsync', 'N/A')}")
            print(f"\n📋 Project ID: {project_id}")
            print(
                f"💡 To modify translations, use: python modify_translation.py --project-id {project_id} --script-index 0 --text 'Your new translation'"
            )
            break
        elif data["status"] == "FAILED":
            print(f"❌ Translation request {export_id} failed: {data.get('status_detail', 'Unknown error')}")
            break

    return 0


if __name__ == "__main__":
    exit(main())
