# AI Studio API Guide

## Overview

The AI Studio API enables you to create AI-generated video content using Text-to-Speech (TTS) and Speech-to-Face (STF) technologies. Key features include:

- **Text-to-Speech (TTS)** conversion with multiple voice types and languages
- **Speech-to-Face (STF)** generation creating realistic avatar videos from audio
- **Multiple TTS types** including AI voices and Azure TTS services  
- **Various model styles** for different avatar appearances and poses
- **Audio format options** for different quality and compatibility needs
- **Real-time task monitoring** throughout the generation process

## Prerequisites

You need an API key issued by Perso.ai to use this service. Please contact our support team to obtain your API credentials.

- API Key: Contact Perso.ai support team
- Base URL: `https://live-api.perso.ai`

## Installation

**Python Version:** 3.8 or higher

**Required packages:**
```bash
pip install requests
```

The script uses only the `requests` library for HTTP communication and standard Python libraries (`json`, `os`, `time`, `urllib.parse`, `pathlib`).

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

### Check Available Types

Before creating content, you can check available TTS types and model styles:

1. **Check TTS types:**
   ```bash
   python main.py --check-types tts_type
   ```

2. **Check model styles:**
   ```bash
   python main.py --check-types modelstyle
   ```

### Basic TTS + STF Workflow

The `main.py` script demonstrates a complete AI video generation workflow:

1. **Basic usage:**
   ```bash
   python main.py --tts-text "Hello world" --tts-type "yuri" --stf-model-style "yuri-front_natural"
   ```

2. **The script will:**
   - Convert your text to speech using the specified TTS type
   - Generate a video with the specified avatar model style
   - Download the audio file locally
   - Provide the final video URL

3. **Available options:**
   ```bash
   # Basic generation
   python main.py --tts-text "Hello world"
   
   # Multiple texts
   python main.py --tts-text "Hello" "I am AI" "Nice to meet you"
   
   # Different TTS type
   python main.py --tts-text "안녕하세요" --tts-type "azuretts-ko-KR-InJoonNeural-sad"
   
   # Different model style
   python main.py --tts-text "Hello" --stf-model-style "indian_m_2_aaryan-side-white_jacket-natural"
   
   # Custom save directory
   python main.py --tts-text "Hello" --save-dir "./my-outputs"
   
   # Only TTS (skip video generation)
   python main.py --tts-text "Hello" --skip-stf
   
   # With custom API key
   python main.py --tts-text "Hello" --api-key "your-key"
   ```

### Complete Workflow Example

1. **Step 1 - Check Available Options:**
   ```bash
   # Check available TTS types
   python main.py --check-types tts_type
   
   # Check available model styles  
   python main.py --check-types modelstyle
   ```

2. **Step 2 - Generate Content:**
   ```bash
   # Generate video with default settings
   python main.py --tts-text "Hello, I am your AI assistant"
   
   # Generate with specific settings
   python main.py --tts-text "안녕하세요" --tts-type "azuretts-ko-KR-InJoonNeural-sad" --stf-model-style "yuri-front_natural"
   ```

3. **Step 3 - Review Results:**
   The script will output the local audio file path and the final video URL when completed.

## API Reference

### 1. Check Available Types

**Endpoint:** `GET /api/v1/settings/{type_name}/`

Retrieves available TTS types or model styles.

**Parameters:**
- `type_name`: `tts_type` or `modelstyle`

**Response:**
```json
[
    {
        "name": "string",
        "display_name": "string",
        "description": "string"
    }
]
```

### 2. Create TTS Task

**Endpoint:** `POST /api/studio/v1/task/tts/`

Creates a text-to-speech conversion task.

**Request Parameters:**
```json
{
    "agent": "string",                  // Required: Agent ID (default: "1")
    "tts_type": "string",              // Required: TTS type (e.g., "yuri", "azuretts-ko-KR-InJoonNeural-sad")
    "tts_audio_format": "string",      // Required: Audio format (e.g., "wav_16bit_32000hz_mono")
    "tts_text": ["string"]             // Required: Array of texts to convert
}
```

**Response:**
```json
{
    "task_id": "uuid",
    "status": "string",
    "created_at": "datetime"
}
```

### 3. Check TTS Task Status

**Endpoint:** `GET /api/studio/v1/task/tts/{task_id}/`

Monitors the progress of a TTS task.

**Response:**
```json
{
    "task_id": "uuid",
    "status": "string",                 // PENDING, IN_PROGRESS, COMPLETED, FAILED
    "tts_output_audio": "string",      // Audio file URL when completed
    "failure_reason": "string"         // Error details if failed
}
```

### 4. Create STF Task

**Endpoint:** `POST /api/studio/v1/task/stf/`

Creates a speech-to-face video generation task.

**Request Parameters (multipart/form-data):**
- `agent`: Agent ID (default: "1")
- `stf_model_style`: Model style (e.g., "yuri-front_natural")
- `stf_input_audio`: Audio file (binary upload)

**Response:**
```json
{
    "task_id": "uuid",
    "status": "string",
    "created_at": "datetime"
}
```

### 5. Check STF Task Status

**Endpoint:** `GET /api/studio/v1/task/stf/{task_id}/`

Monitors the progress of an STF task.

**Response:**
```json
{
    "task_id": "uuid",
    "status": "string",                 // PENDING, IN_PROGRESS, COMPLETED, FAILED
    "stf_output_video": "string",      // Video URL when completed
    "failure_reason": "string"         // Error details if failed
}
```

## Common TTS Types

Popular TTS types include:
- `yuri` - Default AI voice
- `azuretts-ko-KR-InJoonNeural-sad` - Korean male voice (sad tone)
- `azuretts-en-US-JennyNeural-cheerful` - English female voice (cheerful tone)
- `azuretts-ja-JP-NanamiNeural-gentle` - Japanese female voice (gentle tone)

## Common Model Styles

Popular model styles include:
- `yuri-front_natural` - Female avatar, front view, natural pose
- `indian_m_2_aaryan-side-white_jacket-natural` - Male avatar, side view, business attire
- `korean_f_1_suji-front-casual-natural` - Korean female avatar, casual style

## Audio Formats

Supported audio formats:
- `wav_16bit_32000hz_mono` - High quality WAV (default)
- `wav_16bit_16000hz_mono` - Standard quality WAV
- `mp3_128kbps` - Compressed MP3

## Status Values

- **PENDING**: Task queued for processing
- **IN_PROGRESS**: Task currently running
- **COMPLETED**: Task finished successfully  
- **FAILED**: Task encountered an error

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
- `413`: Payload Too Large - File too big
- `429`: Rate Limited - Too many requests
- `500`: Internal Server Error - Server issue
