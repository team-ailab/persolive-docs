# Video Translation API Guide

## Overview

The Video Translation API enables you to automatically translate video content from one language to another. Key features include:

- **Automatic speech recognition** and translation of video content
- **Voice synthesis** with natural-sounding audio in the target language  
- **Lip-sync** capabilities to match translated audio with original video
- **Script editing** functionality to modify translations before final output
- **Multiple export formats** including video with/without lip-sync
- **Real-time status tracking** throughout the translation process

## Prerequisites

You need an API key issued by Perso.ai to use this service. Please contact our support team to obtain your API credentials.

- API Key: Contact Perso.ai support team
- Base URL: `https://live-api.perso.ai`

## Installation

To run the example script (`main.py`), you need:

**Python Version:** 3.8 or higher

**Required packages:**
```bash
pip install requests
```

The example script uses only the `requests` library for HTTP communication and standard Python libraries (`json`, `os`, `time`).

## Authentication

You must include your API key in the request headers as follows:

```python
headers = {
    "Content-Type": "application/json",
    "PersoLive-APIKey": os.environ.get("EST_LIVE_API_KEY"),
}
```

**Environment Setup:**
```bash
export EST_LIVE_API_KEY="your-api-key-here"
```

## Quick Start

### Basic Translation Workflow

The `main.py` script demonstrates a complete basic video translation workflow:

1. **Run the basic translation:**
   ```bash
   python main.py --input-url "https://example.com/video.mp4" --source-lang ko --target-lang en
   ```

2. **The script will:**
   - Create a new translation project
   - Submit an initial export request  
   - Monitor the translation progress
   - Display the final video URLs when completed

3. **Available options:**
   ```bash
   # Basic translation
   python main.py --input-url "URL" --source-lang ko --target-lang en
   
   # With lip-sync enabled
   python main.py --input-url "URL" --source-lang ko --target-lang en --lipsync
   
   # Without watermark
   python main.py --input-url "URL" --source-lang ko --target-lang en --no-watermark
   
   # With custom API key
   python main.py --input-url "URL" --source-lang ko --target-lang en --api-key "your-key"
   ```

### Translation Modification Workflow

The `modify_translation.py` script allows you to edit specific translations and regenerate the final video:

1. **Modify a specific script by index:**
   ```bash
   python modify_translation.py --project-id "pvtp-uuid" --script-index 0 --text "New translation text"
   ```

2. **Modify a specific script by ID:**
   ```bash
   python modify_translation.py --project-id "pvtp-uuid" --script-id "pvts-uuid" --text "Modified translation"
   ```

3. **The script will:**
   - Fetch the project details and scripts
   - Update the specified script translation
   - Regenerate audio for the modified script
   - Create a new export with the updated content
   - Monitor the export progress until completion

4. **Available options:**
   ```bash
   # Basic modification
   python modify_translation.py --project-id "PROJECT_ID" --script-index 0 --text "New text"
   
   # With different target language
   python modify_translation.py --project-id "PROJECT_ID" --script-index 0 --text "New text" --target-language es
   
   # With lip-sync enabled
   python modify_translation.py --project-id "PROJECT_ID" --script-index 0 --text "New text" --lipsync
   
   # Without watermark
   python modify_translation.py --project-id "PROJECT_ID" --script-index 0 --text "New text" --no-watermark
   ```

### Complete Workflow Example

1. **Step 1 - Initial Translation:**
   ```bash
   python main.py --input-url "https://example.com/video.mp4" --source-lang ko --target-lang en
   # Note the project ID from the output (e.g., pvtp-12345...)
   ```

2. **Step 2 - Review and Modify (Optional):**
   ```bash
   # Modify the first script (index 0)
   python modify_translation.py --project-id "pvtp-12345..." --script-index 0 --text "Better translation"
   
   # Modify the third script (index 2)  
   python modify_translation.py --project-id "pvtp-12345..." --script-index 2 --text "Another improvement"
   ```

3. **Step 3 - Final Export:**
   The `modify_translation.py` script automatically creates a new export with your modifications. Each modification creates a separate export with all current translations included.

## API Reference

### 1. Create Project

**Endpoint:** `POST /api/video_translator/v2/project/`

Creates a new video translation project.

**Request Parameters:**
```json
{
    "input_file_name": "string",        // Required: Original filename
    "input_file_url": "string",         // Required: Public URL to video file
    "source_language": "string"         // Required: Source language code (e.g., "ko", "en")
}
```

**Response:**
```json
{
    "project_id": "uuid",
    "status": "string",
    "created_at": "datetime"
}
```

### 2. Create Export

**Endpoint:** `POST /api/video_translator/v2/export/`

Initiates the translation and export process.

**Request Parameters:**
```json
{
    "export_type": "string",            // Required: "INITIAL_EXPORT" or "PROOFREAD_EXPORT"
    "priority": "integer",              // Optional: 0-10, higher = more priority
    "server_label": "string",           // Required: "prod" for production
    "project": "uuid",                  // Required: Project ID from step 1
    "target_language": "string",        // Required: Target language code
    "lipsync": "boolean",              // Optional: Enable lip-sync (default: false)
    "watermark": "boolean"             // Optional: Add watermark (default: true)
}
```

**Response:**
```json
{
    "projectexport_id": "uuid",
    "status": "string",
    "progress": "integer",
    "progress_total": "integer"
}
```

### 3. Check Export Status

**Endpoint:** `GET /api/video_translator/v2/export/{export_id}/`

Monitors the progress of an export request.

**Response:**
```json
{
    "projectexport_id": "uuid",
    "status": "string",                 // PENDING, IN_PROGRESS, COMPLETED, FAILED
    "status_detail": "string",
    "progress": "integer",
    "progress_total": "integer",
    "video_output_video_with_lipsync": "string",    // Final video URL when completed
    "video_output_video_without_lipsync": "string"
}
```

### 4. Get Project Details

**Endpoint:** `GET /api/video_translator/v2/project/{project_id}/`

Retrieves project information including generated scripts.

**Response:**
```json
{
    "project_id": "uuid",
    "source_language": "string",
    "status": "string",
    "scripts": [
        {
            "projectscript_id": "uuid",
            "order": "integer",
            "start_ms": "integer",
            "end_ms": "integer",
            "text_original": "string",
            "text_translated": "string"
        }
    ],
    "exports": [...],
    "created_at": "datetime"
}
```

### 5. Update Script Translation

**Endpoint:** `PATCH /api/video_translator/v2/script/{script_id}/`

Modifies the translated text for a specific script segment.

**Request Parameters:**
```json
{
    "text_translated": "string",        // Optional: New translated text
    "text_original": "string",          // Optional: Modified original text  
    "projectvoice": "string"            // Optional: Voice ID for this segment
}
```

**Response:**
```json
{
    "projectscript_id": "uuid",
    "text_translated": "string",
    "audio_updated_to_current": "boolean"
}
```

### 6. Generate Audio for Modified Script

**Endpoint:** `POST /api/video_translator/v2/script/{script_id}/generate_audio/`

Regenerates audio for a script segment after modification. This step is **required** after updating any script text.

**Request:** No body required

**Response:**
```json
{
    "status": "string",
    "message": "string"
}
```

## Language Codes

Supported language codes include:
- `ko` - Korean
- `en` - English  
- `ja` - Japanese
- `zh` - Chinese
- `es` - Spanish
- `fr` - French
- `de` - German
- `ta` - Tamil
- And many more...

## Export Types

- **INITIAL_EXPORT**: First translation attempt with automatically generated scripts
- **PROOFREAD_EXPORT**: Final export after manual script modifications

## Status Values

- **PENDING**: Request queued for processing
- **IN_PROGRESS**: Translation/export currently running
- **COMPLETED**: Process finished successfully  
- **FAILED**: Process encountered an error

## Error Handling

Always check the HTTP status code and response body for error details:

```python
if response.status_code >= 400:
    print(f"Error {response.status_code}: {response.text}")
```

Common error codes:
- `400`: Bad Request - Invalid parameters
- `401`: Unauthorized - Invalid API key
- `404`: Not Found - Resource doesn't exist
- `429`: Rate Limited - Too many requests
- `500`: Internal Server Error - Server issue
