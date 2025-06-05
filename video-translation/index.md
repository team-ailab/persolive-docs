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

- Python 3.8+
- API key for the Perso.ai Live API service: Please contact our support team to obtain your API credentials.

## Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/team-ailab/persolive-docs.git
   cd video-translation
   ```

2. **Install Python dependencies:**
    ```bash
    # The script uses only the `requests` library for HTTP communication
    pip install requests
    ```

## Authentication

The system supports various authentication methods:

1. **Environment Variable (Recommended):**
   ```bash
   export EST_LIVE_API_KEY="your-api-key-here"
   python main.py
   ```

2. **Command Line Argument:**
   ```bash
   python main.py --api-key "your-api-key-here"
   ```

3. **Authentication Header (When using requests library):**
    ```python
    headers = {
        "Content-Type": "application/json",
        "PersoLive-APIKey": os.environ.get("EST_LIVE_API_KEY"),
    }
    ```

## Quick Start

### Basic Translation Workflow

The `main.py` script demonstrates a complete basic video translation workflow:

1. **Run the basic translation:**
   ```bash
   python main.py --input-url "https://samoonsikpoc.blob.core.windows.net/moonsikpoc/우영우_1_kor.mp4" --source-lang ko --target-lang en
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
   
   # With different source and target languages (Spanish)
   python main.py --input-url "URL" --source-lang ko --target-lang es
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
   # Basic modification (index 0)
   python modify_translation.py --project-id "pvtp-uuid" --script-index 0 --text "New text"

   # Basic modification (index 1)
   python modify_translation.py --project-id "pvtp-uuid" --script-index 1 --text "New text"

   # Basic modification (ID)
   python modify_translation.py --project-id "pvtp-uuid" --script-id "pvts-uuid" --text "New text"
   
   # With lip-sync enabled
   python modify_translation.py --project-id "pvtp-uuid" --script-index 0 --text "New text" --lipsync
   
   # Without watermark
   python modify_translation.py --project-id "pvtp-uuid" --script-index 0 --text "New text" --no-watermark
   
   # With different target language
   python modify_translation.py --project-id "pvtp-uuid" --script-index 0 --text "New text" --target-language ko
   ```

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
    "project_id": "string",             // Project unique ID (with pvtp- prefix)
    "user": "string",                   // User identifier  
    "source_language": "string",        // Source language code
    "input_file_type": "VIDEO",         // File type (VIDEO or AUDIO)
    "input_file_url": "string",         // Input file URL
    "input_file_source": "FILE_UPLOAD", // Input source (FILE_UPLOAD, YOUTUBE, TIKTOK)
    "input_file_name": "string",        // Input filename
    "input_file_video_duration_sec": null, // Video duration in seconds (null initially)
    "input_number_of_speakers": 1,      // Number of speakers detected
    "audio_subtitle_original": null,    // Original subtitle file URL (null initially)
    "audio_original_voiceonly": null,   // Original voice-only audio URL (null initially)
    "audio_original_background": null,  // Original background audio URL (null initially)
    "status": "CREATED",                // Project status (CREATED, READY, FAILED)
    "failure_reason": null,             // Failure reason if failed (null initially)
    "ready_target_languages": [],      // Array of languages ready for export
    "exports": [],                      // Array of project exports
    "scripts": [],                      // Array of project scripts
    "created_at": "datetime",           // Project creation timestamp
    "updated_at": "datetime"            // Project last update timestamp
}
```

### 2. Create Export

**Endpoint:** `POST /api/video_translator/v2/export/`

Initiates the translation and export process.

**Request Parameters:**
```json
{
    "project": "string",                // Required: Project ID (pvtp- format)
    "export_type": "string",            // Required: "INITIAL_EXPORT" or "PROOFREAD_EXPORT"
    "target_language": "string",        // Required: Target language code
    "server_label": "string",           // Required: "prod" for production
    "priority": 100,                    // Optional: 0-100, lower = higher priority (default: 100)
    "lipsync": false,                   // Optional: Enable lip-sync (default: false)
    "watermark": true,                  // Optional: Add watermark (default: true)
    "webhook_url": "string",            // Optional: Webhook URL for completion notification
    "webhook_retry": 10,                // Optional: Number of webhook retries (default: 10)
    "webhook_retry_delay_sec": 10,      // Optional: Webhook retry delay in seconds (default: 10)
    "perso_plan_name": "string"         // Optional: Plan name for billing
}
```

**Response:**
```json
{
    "projectexport_id": "string",       // Export unique ID (with pvte- prefix)
    "project": "string",                // Project ID
    "webhook_url": "string",            // Webhook URL if provided
    "webhook_retry": 10,                // Webhook retry count
    "webhook_retry_delay_sec": 10,      // Webhook retry delay
    "priority": 100,                    // Export priority
    "server_label": "string",           // Server label
    "perso_plan_name": "string",        // Plan name
    "target_language": "string",        // Target language code
    "project_script": "object",         // Project script snapshot (JSON)
    "export_type": "string",            // Export type
    "progress": 0,                      // Current progress (0-100)
    "progress_total": 0,                // Total progress steps
    "status": "PENDING",                // Export status (PENDING, ENQUEUED, PROCESSING, COMPLETED, FAILED)
    "status_detail": null,              // Detailed status information
    "failure_reason": null,             // Failure reason if failed
    "failure_reason_detail": null,      // Detailed failure information
    "input_blob_video": null,           // Input video blob URL (null initially)
    "output_blob_video": null,          // Output video blob URL (null initially)
    "lipsync": false,                   // Lip-sync enabled
    "watermark": true,                  // Watermark enabled
    "audio_subtitle_original": null,    // Original subtitle file URL
    "audio_subtitle_translated": null,  // Translated subtitle file URL
    "audio_original_voiceonly": null,   // Original voice-only audio URL
    "audio_original_background": null,  // Original background audio URL
    "audio_original_script": null,      // Original script data (JSON)
    "audio_translated_voiceonly": null, // Translated voice-only audio URL
    "audio_translated_background": null, // Translated background audio URL
    "audio_stats": null,                // Audio statistics (JSON)
    "video_output_video_with_lipsync": null,    // Final video URL with lip-sync
    "video_output_video_without_lipsync": null, // Final video URL without lip-sync
    "audio_translated_voice_per_speaker": null, // Per-speaker translated audio
    "audio_original_voice_per_speaker": null,   // Per-speaker original audio
    "audio_translated_voice_whole": null,       // Complete translated audio
    "video_analysis_report": null,      // Video analysis report (JSON)
    "video_log": null,                  // Video processing log
    "created_at": "datetime"            // Export creation timestamp
}
```

### 3. Check Export Status

**Endpoint:** `GET /api/video_translator/v2/export/{export_id}/`

Monitors the progress of an export request.

**Response:**
```json
{
    "projectexport_id": "string",       // Export unique ID
    "project": "string",                // Project ID
    "webhook_url": "string",            // Webhook URL
    "webhook_retry": 10,                // Webhook retry count
    "webhook_retry_delay_sec": 10,      // Webhook retry delay
    "priority": 100,                    // Export priority
    "server_label": "string",           // Server label
    "perso_plan_name": "string",        // Plan name
    "target_language": "string",        // Target language code
    "project_script": "object",         // Project script snapshot (JSON)
    "export_type": "string",            // Export type (INITIAL_EXPORT, PROOFREAD_EXPORT)
    "progress": 85,                     // Current progress (0-100)
    "progress_total": 100,              // Total progress steps
    "status": "string",                 // PENDING, ENQUEUED, PROCESSING, COMPLETED, FAILED
    "status_detail": "string",          // Detailed status (AUDIO_TRANSLATION_RUNNING, VIDEO_TRANSLATION_RUNNING, etc.)
    "failure_reason": "string",         // Failure reason if failed
    "failure_reason_detail": "string",  // Detailed failure information
    "input_blob_video": "string",       // Input video blob URL
    "output_blob_video": "string",      // Output video blob URL
    "lipsync": false,                   // Lip-sync enabled
    "watermark": true,                  // Watermark enabled
    "audio_subtitle_original": "string",    // Original subtitle file URL
    "audio_subtitle_translated": "string",  // Translated subtitle file URL
    "audio_original_voiceonly": "string",   // Original voice-only audio URL
    "audio_original_background": "string",  // Original background audio URL
    "audio_original_script": "object",      // Original script data (JSON)
    "audio_translated_voiceonly": "string", // Translated voice-only audio URL
    "audio_translated_background": "string", // Translated background audio URL
    "audio_stats": "object",                // Audio statistics (JSON)
    "video_output_video_with_lipsync": "string",    // Final video URL with lip-sync (when completed)
    "video_output_video_without_lipsync": "string", // Final video URL without lip-sync (when completed)
    "audio_translated_voice_per_speaker": "string", // Per-speaker translated audio
    "audio_original_voice_per_speaker": "string",   // Per-speaker original audio
    "audio_translated_voice_whole": "string",       // Complete translated audio
    "video_analysis_report": "object",      // Video analysis report (JSON)
    "video_log": "string",                  // Video processing log
    "created_at": "datetime"                // Export creation timestamp
}
```

### 4. Get Project Details

**Endpoint:** `GET /api/video_translator/v2/project/{project_id}/`

Retrieves project information including generated scripts.

**Response:**
```json
{
    "project_id": "string",             // Project unique ID
    "user": "string",                   // User identifier
    "source_language": "string",        // Source language code
    "input_file_type": "VIDEO",         // File type (VIDEO, AUDIO)
    "input_file_url": "string",         // Input file URL
    "input_file_source": "FILE_UPLOAD", // Input source (FILE_UPLOAD, YOUTUBE, TIKTOK)
    "input_file_name": "string",        // Input filename
    "input_file_video_duration_sec": 120, // Video duration in seconds
    "input_number_of_speakers": 2,      // Number of speakers detected
    "audio_subtitle_original": "string", // Original subtitle file URL
    "audio_original_voiceonly": "string", // Original voice-only audio URL
    "audio_original_background": "string", // Original background audio URL
    "status": "READY",                  // Project status (CREATED, READY, FAILED)
    "failure_reason": null,             // Failure reason if failed
    "ready_target_languages": ["en", "ja"], // Languages ready for export
    "exports": [                        // Array of project exports
        {
            "projectexport_id": "string",
            "export_type": "INITIAL_EXPORT",
            "target_language": "en",
            "status": "COMPLETED",
            // ... other export fields
        }
    ],
    "scripts": [                        // Array of project scripts
        {
            "projectscript_id": "string",
            "project": "string",
            "order": 0,
            "source_language": "ko",
            "target_language": "en",
            "projectvoice": "string",
            "start_ms": 1000,
            "end_ms": 5000,
            "duration_ms": 4000,
            "text_original": "안녕하세요",
            "text_translated": "Hello",
            "text_translated_original_match": true,
            "semantic_match_rate": 0.95,
            "isometric_match_rate": 0.88,
            "audio_clip": "string",
            "audio_updated_to_current": true,
            "audio_stats": "object"
        }
    ],
    "created_at": "datetime",           // Project creation timestamp
    "updated_at": "datetime"            // Project last update timestamp
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
    "projectvoice": "string",           // Optional: Voice ID for this segment (projectvoice ID)
    "source_language": "string",        // Optional: Source language code
    "target_language": "string",        // Optional: Target language code
    "start_ms": 1000,                   // Optional: Start time in milliseconds
    "end_ms": 5000,                     // Optional: End time in milliseconds
    "duration_ms": 4000,                // Optional: Duration in milliseconds
    "order": 0,                         // Optional: Script order/sequence number
    "semantic_match_rate": 0.95,        // Optional: Semantic match rate (0.0-1.0)
    "isometric_match_rate": 0.88        // Optional: Isometric match rate (0.0-1.0)
}
```

**Response:**
```json
{
    "projectscript_id": "string",       // Script unique ID (with pvts- prefix)
    "project": "string",                // Project ID
    "order": 0,                         // Script sequence order
    "source_language": "ko",            // Source language code
    "target_language": "en",            // Target language code
    "projectvoice": "string",           // Voice ID for this segment
    "start_ms": 1000,                   // Start time in milliseconds
    "end_ms": 5000,                     // End time in milliseconds
    "duration_ms": 4000,                // Duration in milliseconds
    "text_original": "안녕하세요",      // Original text
    "text_translated": "Hello there",   // Updated translated text
    "text_translated_original_match": false, // Whether translation matches original
    "semantic_match_rate": 0.95,        // Semantic similarity rate
    "isometric_match_rate": 0.88,       // Length/timing match rate
    "audio_clip": "string",             // Audio clip file URL
    "audio_updated_to_current": false,  // Whether audio reflects current text
    "audio_stats": "object"             // Audio generation statistics (JSON)
}
```

### 6. Generate Audio for Modified Script

**Endpoint:** `POST /api/video_translator/v2/script/{script_id}/generate_audio/`

Regenerates audio for a script segment after modification. This step is **required** after updating any script text.

**Request:** No body required

**Response:**
```json
{
    "projectscript_id": "string",       // Script unique ID
    "project": "string",                // Project ID
    "order": 0,                         // Script sequence order
    "source_language": "ko",            // Source language code
    "target_language": "en",            // Target language code
    "projectvoice": "string",           // Voice ID for this segment
    "start_ms": 1000,                   // Start time in milliseconds
    "end_ms": 5000,                     // End time in milliseconds
    "duration_ms": 4000,                // Duration in milliseconds
    "text_original": "안녕하세요",         // Original text
    "text_translated": "Hello there",   // Translated text
    "text_translated_original_match": false, // Whether translation matches original
    "semantic_match_rate": 0.95,        // Semantic similarity rate
    "isometric_match_rate": 0.88,       // Length/timing match rate
    "audio_clip": "string",             // Updated audio clip file URL
    "audio_updated_to_current": true,   // Audio now reflects current text
    "audio_stats": "object"             // Audio generation statistics (JSON)
}
```

## Export Types

- **INITIAL_EXPORT**: First translation attempt with automatically generated scripts. Creates baseline translation and generates initial scripts for the project.
- **PROOFREAD_EXPORT**: Final export after manual script modifications. Used after editing translations via the script update API.

## Status Values

### Project Status
- **CREATED**: Project created, initial export needed to generate scripts
- **READY**: Initial export completed, scripts available, proofread export possible
- **FAILED**: Initial export failed, no further processing possible

### Export Status
- **PENDING**: Export queued for processing
- **ENQUEUED**: Export enqueued on server, waiting to be processed
- **PROCESSING**: Export currently running
- **COMPLETED**: Export finished successfully  
- **FAILED**: Export encountered an error

### Export Status Detail
- **AUDIO_TRANSLATION_PENDING**: Waiting for audio translation to start
- **AUDIO_TRANSLATION_RUNNING**: Audio translation in progress
- **VIDEO_TRANSLATION_PENDING**: Waiting for video translation to start
- **VIDEO_TRANSLATION_RUNNING**: Video translation in progress
- **COMPLETED**: All processing completed

## Failure Reasons

### Project Failure Reasons
- **AUDIO_PIPELINE_FAILED**: Audio processing pipeline failed
- **AUDIO_CELEBRITY_FAILED**: Audio contains celebrity voice (not allowed)
- **AUDIO_NO_STREAM**: Video has no audio stream
- **VIDEO_PIPELINE_FAILED**: Video processing pipeline failed
- **INPUT_VIDEO_DOWNLOAD_FAILED**: Could not download input video
- **API_ERROR**: API error occurred
- **UNKNOWN**: Unknown error
- **TIMEOUT**: Processing timed out

### Export Failure Reasons
- **AUDIO_PIPELINE_FAILED**: Audio processing pipeline failed
- **AUDIO_CELEBRITY_FAILED**: Audio contains celebrity voice (not allowed)
- **AUDIO_NO_STREAM**: Video has no audio stream
- **AUDIO_NO_VOICE**: No voice found in audio
- **VIDEO_PIPELINE_FAILED**: Video processing pipeline failed
- **QUEUE_FULL**: Server queue is full
- **API_ERROR**: API error occurred
- **UNKNOWN**: Unknown error
- **TIMEOUT**: Processing timed out

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
