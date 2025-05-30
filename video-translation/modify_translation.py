import argparse
import json
import os
import time

import requests


def parse_arguments():
    """Command line argument parser"""
    parser = argparse.ArgumentParser(
        description="Video Translation Script Modifier",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python modify_translation.py --project-id "pvtp-uuid" --script-id "pvts-uuid" --text "New translation text"
  python modify_translation.py --project-id "pvtp-uuid" --script-index 0 --text "Modified translation"
        """,
    )

    # Required arguments
    parser.add_argument(
        "--project-id",
        required=True,
        help="Project ID from the initial translation",
    )

    # Script identification (either script-id or script-index)
    script_group = parser.add_mutually_exclusive_group(required=True)
    script_group.add_argument(
        "--script-id",
        help="Specific script ID to modify",
    )
    script_group.add_argument(
        "--script-index",
        type=int,
        help="Script index (0-based) to modify",
    )

    parser.add_argument(
        "--text",
        required=True,
        help="New translated text",
    )

    # Optional arguments
    parser.add_argument(
        "--base-url", default="https://live-api.perso.ai", help="API base URL (default: https://live-api.perso.ai)"
    )
    parser.add_argument("--target-language", default="en", help="Target language code (default: en)")
    parser.add_argument("--lipsync", action="store_true", help="Enable lip-sync in the output video")
    parser.add_argument("--no-watermark", action="store_true", help="Disable watermark in the output video")
    parser.add_argument("--api-key", help="API key (if not provided, will use EST_LIVE_API_KEY environment variable)")

    return parser.parse_args()


def get_project_scripts(base_url, headers, project_id):
    """Get project details including scripts"""
    url = f"{base_url}/api/video_translator/v2/project/{project_id}/"
    response = requests.get(url, headers=headers, timeout=30)

    if response.status_code >= 400:
        raise Exception(f"Failed to get project details: {response.status_code} - {response.text}")

    return response.json()


def modify_script(base_url, headers, script_id, new_text):
    """Modify script translation"""
    url = f"{base_url}/api/video_translator/v2/script/{script_id}/"

    payload = json.dumps(
        {
            "text_translated": new_text,
        }
    )

    response = requests.patch(url, headers=headers, data=payload, timeout=30)

    if response.status_code >= 400:
        raise Exception(f"Failed to modify script: {response.status_code} - {response.text}")

    return response.json()


def generate_audio(base_url, headers, script_id):
    """Generate audio for modified script"""
    url = f"{base_url}/api/video_translator/v2/script/{script_id}/generate_audio/"

    response = requests.post(url, headers=headers, timeout=30)

    if response.status_code >= 400:
        raise Exception(f"Failed to generate audio: {response.status_code} - {response.text}")

    return response.json()


def create_proofread_export(base_url, headers, project_id, target_language, lipsync=False, watermark=True):
    """Create a new export with modified translations"""
    url = f"{base_url}/api/video_translator/v2/export/"

    payload = json.dumps(
        {
            "export_type": "PROOFREAD_EXPORT",
            "server_label": "prod",
            "priority": 0,
            "project": project_id,
            "target_language": target_language,
            "lipsync": lipsync,
            "watermark": watermark,
        }
    )

    response = requests.post(url, headers=headers, data=payload, timeout=30)

    if response.status_code >= 400:
        raise Exception(f"Failed to create export: {response.status_code} - {response.text}")

    return response.json()


def wait_for_export_completion(base_url, headers, export_id):
    """Wait for export to complete"""
    url = f"{base_url}/api/video_translator/v2/export/{export_id}/"

    while True:
        time.sleep(5)
        response = requests.get(url, headers=headers, timeout=30)

        if response.status_code >= 400:
            raise Exception(f"Failed to check export status: {response.status_code} - {response.text}")

        data = response.json()
        print(f"⏳ Export {export_id} status: {data['status']} ({data.get('status_detail', 'N/A')})")

        if data["status"] == "COMPLETED":
            return data
        elif data["status"] == "FAILED":
            raise Exception(f"Export failed: {data.get('status_detail', 'Unknown error')}")


def main():
    # Parse command line arguments
    args = parse_arguments()

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

    try:
        print("🔍 Getting project details...")
        project_data = get_project_scripts(args.base_url, headers, args.project_id)

        if not project_data.get("scripts"):
            print("❌ No scripts found in this project.")
            return 1

        # Determine script ID
        if args.script_id:
            script_id = args.script_id
            # Verify script exists
            script_found = any(script["projectscript_id"] == script_id for script in project_data["scripts"])
            if not script_found:
                print(f"❌ Script ID {script_id} not found in project.")
                return 1
        else:
            # Use script index
            if args.script_index >= len(project_data["scripts"]):
                print(
                    f"❌ Script index {args.script_index} is out of range. Project has {len(project_data['scripts'])} scripts."
                )
                return 1
            script_id = project_data["scripts"][args.script_index]["projectscript_id"]

        print(f"📝 Modifying script {script_id}...")
        modify_result = modify_script(args.base_url, headers, script_id, args.text)
        print(f"✅ Script modified successfully: {modify_result}")

        print("🎵 Generating audio for modified script...")
        audio_result = generate_audio(args.base_url, headers, script_id)
        print(f"✅ Audio generation completed: {audio_result}")

        print("🚀 Creating new export with modified translation...")
        watermark = not args.no_watermark
        export_result = create_proofread_export(
            args.base_url, headers, args.project_id, args.target_language, args.lipsync, watermark
        )

        export_id = export_result["projectexport_id"]
        print(f"✅ Export {export_id} created successfully")

        print("⏳ Waiting for export to complete...")
        final_result = wait_for_export_completion(args.base_url, headers, export_id)

        print("🎉 Export completed successfully!")
        print(f"🎥 Output video (with lip-sync): {final_result.get('video_output_video_with_lipsync', 'N/A')}")
        print(f"🎥 Output video (without lip-sync): {final_result.get('video_output_video_without_lipsync', 'N/A')}")

        return 0

    except Exception as e:
        print(f"❌ Error: {e}")
        return 1


if __name__ == "__main__":
    exit(main())
