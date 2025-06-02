# AI Avatar Chat API Guide

## Overview

The AI Avatar Chat API enables real-time interactive conversations with AI avatars. This system combines multiple AI technologies to create immersive chat experiences. Key features include:

- **Session-based chat** with persistent conversation history
- **Multi-modal interaction** supporting text, voice, and visual communication
- **Real-time Text-to-Speech (TTS)** with natural-sounding avatar voices
- **Speech-to-Text (STT)** for voice input processing
- **Large Language Model (LLM)** integration for intelligent responses
- **Avatar visualization** with customizable model styles and backgrounds
- **Live voice chat** with real-time audio recording and playback
- **Flexible capability selection** (LLM, TTS, STT, STF_WEBRTC for browser streaming)

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

**Optional package for voice features:**
```bash
pip install pyaudio  # Required for real-time voice recording
```

The script uses the `requests` library for HTTP communication and standard Python libraries. The `pyaudio` package is only needed for real-time voice recording functionality.

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

### Basic Interactive Chat

The `main.py` script provides a complete interactive chat interface:

1. **Basic usage with defaults:**
   ```bash
   python main.py
   ```

2. **The script will:**
   - Create a new chat session with the AI avatar
   - Start an interactive menu system
   - Provide multiple chat modes (text, voice, file)
   - Maintain conversation history
   - Clean up resources when finished

3. **Available chat modes:**
   - **Text Chat**: Type messages and receive text responses
   - **Voice Chat**: Record voice messages and receive audio responses
   - **Voice File Chat**: Upload audio files for processing
   - **Chat History**: View previous conversation messages

### Configuration Options

**Custom AI configuration:**
```bash
# Use different LLM and TTS types
python main.py --llm-type gpt-4 --tts-type "azuretts-ko-KR-InJoonNeural-sad"

# Use different avatar model style
python main.py --model-style "indian_m_2_aaryan-side-white_jacket-natural"

# Specify custom prompt and document
python main.py --prompt "plp-12345" --document "pld-67890"
```

**Avatar visualization configuration:**
```bash
# Custom avatar positioning
python main.py --model-style "yuri-front_natural" --padding-left 0.2 --padding-top 0.1 --padding-height 1.5

# With background image
python main.py --background-image "pbi-12345" --model-style "korean_f_1_soohyun-side-pink_cardigan-natural"

# Specify agent identifier
python main.py --agent "custom-agent-1"
```

**Settings discovery:**
```bash
# Check available TTS types
python main.py --list-settings tts_type

# Check available model styles  
python main.py --list-settings modelstyle
```

**API server configuration:**
```bash
# Use custom API server
python main.py --api-server "https://custom-api.example.com"

# Use specific API key
python main.py --api-key "your-api-key"
```

**Capability selection:**
```bash
# Enable only specific capabilities
python main.py --capability LLM TTS STT

# For browser WebRTC streaming (required for avatar visualization)
python main.py --capability LLM TTS STT STF_WEBRTC
```

### Complete Workflow Example

1. **Step 1 - Start Basic Chat:**
   ```bash
   # Start with default settings
   python main.py
   
   # Choose option 1 (Text Chat) from the menu
   # Type your message and receive AI responses
   ```

2. **Step 2 - Try Voice Chat:**
   ```bash
   # Ensure pyaudio is installed
   pip install pyaudio
   
   # Start the chat system
   python main.py
   
   # Choose option 2 (Voice Chat) from the menu
   # Record your voice message and receive audio response
   ```

3. **Step 3 - Advanced Configuration:**
   ```bash
   # Use Korean TTS with specific avatar
   python main.py --tts-type "azuretts-ko-KR-InJoonNeural-sad" --model-style "yuri-front_natural"
   
   # Custom prompt for specific use case
   python main.py --prompt "plp-customer-service" --document "pld-knowledge-base"
   ```

## API Reference

### 1. Create Session

**Endpoint:** `POST /api/v1/session/`

Creates a new chat session with the AI avatar.

**Request Parameters:**
```json
{
    "llm_type": "string",           // Optional: LLM type (default: "gpt-35")
    "tts_type": "string",           // Optional: TTS type (default: "yuri")
    "stt_type": "string",           // Optional: STT type (default: "default")
    "model_style": "string",        // Optional: Avatar model style (default: "yuri-front_natural")
    "prompt": "string",             // Optional: Prompt ID (default: "plp-d432cb910983f1eed6511eba836ac14f")
    "document": "string",           // Optional: Document ID for context
    "background_image": "string",   // Optional: Background image ID
    "capability": ["string"],       // Optional: Capabilities array (default: ["LLM", "TTS", "STT"])
    "agent": "string",              // Optional: Agent identifier
    "padding_left": "float",        // Optional: Avatar padding left (-1.0 to 1.0)
    "padding_top": "float",         // Optional: Avatar padding top (0.0 to 1.0)
    "padding_height": "float"       // Optional: Avatar padding height (0 to 5)
}
```

**Response:**
```json
{
    "session_id": "string",
    "created_at": "datetime",
    "status": "CREATED"
}
```

### 2. Start Session

**Endpoint:** `POST /api/v1/session/{session_id}/event/create/`

Initializes the session for active communication.

**Request Parameters:**
```json
{
    "event": "SESSION_START",
    "detail": "Session started via Python"
}
```

**Response:**
```json
{
    "status": "success",
    "message": "Event created"
}
```

### 3. Text Chat (LLM)

**Endpoint:** `POST /api/v1/session/{session_id}/llm/`

Sends a text message to the AI and receives a streaming response.

**Request Parameters:**
```json
{
    "message": "string",            // Required: User message
    "clear_history": "boolean"      // Optional: Clear conversation history (default: false)
}
```

**Response (Streaming):**
```json
// Streaming response with Server-Sent Events
data: {"status": "success", "sentence": "Hello, how can I help you today?"}
data: {"status": "success", "sentence": " I'm here to assist you."}
```

### 4. Text-to-Speech (TTS)

**Endpoint:** `POST /api/v1/session/{session_id}/tts/`

Converts text to speech audio using the session's TTS settings.

**Request Parameters:**
```json
{
    "text": "string"                // Required: Text to convert to speech
}
```

**Response:**
```json
{
    "audio": "base64_string",       // Base64 encoded audio data
    "format": "wav"
}
```

### 5. Speech-to-Text (STT)

**Endpoint:** `POST /api/v1/session/{session_id}/stt/`

Converts audio file to text using speech recognition.

**Request Parameters (multipart/form-data):**
- `audio`: Audio file (WAV format recommended)
- `language`: Language code (e.g., "ko", "en")

**Response:**
```json
{
    "text": "string",               // Recognized text from audio
    "confidence": "float"          // Recognition confidence score
}
```

### 6. Get Session Status

**Endpoint:** `GET /api/v1/session/{session_id}/`

Retrieves current session information and status.

**Response:**
```json
{
    "session_id": "string",
    "status": "string",             // CREATED, EXCHANGED, IN_PROGRESS, TERMINATED
    "llm_type": {
        "name": "string",
        "display_name": "string"
    },
    "tts_type": {
        "name": "string", 
        "display_name": "string"
    },
    "model_style": {
        "name": "string",
        "display_name": "string"
    },
    "prompt": {
        "prompt_id": "string",
        "title": "string"
    },
    "created_at": "datetime",
    "duration_sec": "integer"
}
```

### 7. End Session

**Endpoint:** `POST /api/v1/session/{session_id}/event/create/`

Gracefully terminates the chat session.

**Request Parameters:**
```json
{
    "event": "SESSION_END",
    "detail": "Session ended via Python"
}
```

**Response:**
```json
{
    "status": "success",
    "message": "Event created"
}
```

### 8. Get Available Settings

**Available endpoints for retrieving configuration options:**

- **GET** `/api/v1/settings/tts_type/` - Available TTS types
- **GET** `/api/v1/settings/stt_type/` - Available STT types  
- **GET** `/api/v1/settings/modelstyle/` - Available avatar model styles

**Response format:**
```json
[
    {
        "name": "string",
        "display_name": "string",
        "description": "string"
    }
]
```

### 9. Get Video Stream URL

**Endpoint:** `GET /api/v1/session/{session_id}/`

Retrieves video stream information for avatar visualization.

**Response:**
```json
{
    "session_id": "string",
    "status": "string",
    "stream_url": "string",
    "model_style": {
        "name": "string",
        "display_name": "string"
    },
    "background_image": "string"
}
```

**Note:** Full avatar visualization with WebRTC video streaming is best experienced through the web SDK in a browser environment. The Python implementation provides configuration and session management capabilities.

## Common Configuration Values

### LLM Types
Popular LLM types include:
- `gpt-35` - GPT-3.5 Turbo (default)
- `gpt-4` - GPT-4 for enhanced reasoning
- `gpu-4o` - GPU-4o for enhanced reasoning

### TTS Types
Popular TTS types include:
- `yuri` - Default AI voice (female)
- `azuretts-ko-KR-InJoonNeural-sad` - Korean male voice (sad tone)
- `azuretts-en-US-JennyNeural-cheerful` - English female voice (cheerful)
- `azuretts-ja-JP-NanamiNeural-gentle` - Japanese female voice (gentle)

### STT Types
Popular STT types include:
- `default` - Default speech recognition

### Model Styles
Popular avatar model styles include:
- `yuri-front_natural` - Female avatar, front view, natural pose (default)
- `indian_m_2_aaryan-side-white_jacket-natural` - Male avatar, side view, business attire
- `korean_f_1_soohyun-side-pink_cardigan-natural` - Korean female avatar, casual style

### Capabilities
Available capability options:
- `LLM` - Large Language Model for text conversations
- `TTS` - Text-to-Speech for audio generation
- `STT` - Speech-to-Text for voice input
- `STF_WEBRTC` - Speech-to-Face with WebRTC for real-time video streaming (required for browser avatar visualization)

### Session Status Values
- **CREATED**: Session created but not started
- **EXCHANGED**: WebRTC connection established (if applicable)
- **IN_PROGRESS**: Session active and ready for communication
- **TERMINATED**: Session ended

## Error Handling

Always check the HTTP status code and response body for error details:

```python
if response.status_code >= 400:
    print(f"Error {response.status_code}: {response.text}")
```

Common error codes:
- `400`: Bad Request - Invalid parameters or session state
- `401`: Unauthorized - Invalid API key
- `404`: Not Found - Session doesn't exist
- `413`: Payload Too Large - Audio file too big
- `429`: Rate Limited - Too many requests
- `500`: Internal Server Error - Server issue

## Interactive Menu System

The script provides an interactive menu with the following options:

1. **Chat with text** - Type messages and receive text responses
2. **Chat with voice (recording)** - Record voice messages (requires pyaudio)
3. **Chat with voice file** - Upload and process audio files
4. **View chat history** - Display conversation history
5. **Launch avatar visualization** - Start real-time avatar experience in browser
6. **Check available settings** - Browse available TTS types and model styles
7. **Exit** - Clean up and terminate the session

### Avatar Visualization Features

- **Model style selection** - Choose from various avatar appearances and poses
- **Background customization** - Set custom background images for the avatar
- **Position control** - Adjust avatar positioning with padding parameters:
  - `padding_left`: Horizontal position (-1.0 to 1.0)
  - `padding_top`: Vertical position (0.0 to 1.0) 
  - `padding_height`: Avatar size scaling (0 to 5)
- **Settings discovery** - Query available TTS types and model styles
- **Configuration viewing** - Inspect current session and avatar settings

## Best Practices

1. **Session Management**: Always call `end_session()` to clean up resources
2. **Error Handling**: Check session status before making API calls
3. **Audio Quality**: Use good quality audio for better STT results
4. **Rate Limiting**: Respect API rate limits for production use
5. **Resource Cleanup**: Remove temporary audio files after processing
