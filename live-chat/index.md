# AI Avatar Chat System

The AI Avatar Chat System provides an interactive Python interface for real-time conversations with AI avatars. It supports text chat, voice conversations, and browser-based avatar visualization through WebRTC.

## Overview

This system enables:
- **Text Chat**: Type messages and receive AI responses
- **Voice Chat**: Record voice messages and receive audio responses  
- **Voice File Processing**: Upload audio files for speech recognition
- **Settings Discovery**: Browse available TTS types and model styles
- **Browser Avatar Visualization**: Real-time avatar chat with WebRTC video streaming

## Prerequisites

- Python 3.7+
- API key for the Perso.ai Live API service
- Optional: `pyaudio` for voice recording features
- Modern web browser (Chrome/Firefox) for avatar visualization

## Installation

1. **Install Python dependencies:**
   ```bash
   pip install requests
   
   # Optional: for voice recording features
   pip install pyaudio
   ```

2. **Set up API credentials:**
   ```bash
   # Set environment variable
   export EST_LIVE_API_KEY="your-api-key-here"
   
   # Or pass as command line argument
   python main.py --api-key "your-api-key-here"
   ```

## Authentication

The system supports two authentication methods:

1. **Environment Variable (Recommended):**
   ```bash
   export EST_LIVE_API_KEY="your-api-key-here"
   python main.py
   ```

2. **Command Line Argument:**
   ```bash
   python main.py --api-key "your-api-key-here"
   ```

## Quick Start

### Basic Usage

1. **Start the interactive system:**
   ```bash
   python main.py
   ```

2. **The script will:**
   - Show an interactive menu system
   - Create sessions only when needed (lazy loading)
   - Provide multiple chat modes and browser avatar guidance
   - Clean up resources when finished

3. **Available menu options:**
   - **Text Chat**: Type messages and receive text responses
   - **Voice Chat**: Record voice messages and receive audio responses
   - **Voice File Chat**: Upload audio files for processing
   - **Chat History**: View previous conversation messages
   - **Launch Avatar Visualization**: Get guidance for browser-based avatar chat
   - **Check Available Settings**: Browse available TTS types and model styles

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
# Use default capabilities (recommended)
python main.py --capability LLM TTS STT

# Enable subset of capabilities  
python main.py --capability LLM TTS  # Text-only mode
python main.py --capability LLM      # Chat without audio
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

3. **Step 3 - Browser Avatar Visualization:**
   ```bash
   # Start the system
   python main.py
   
   # Choose option 5 (Launch Avatar Visualization)
   # Follow the guidance to open browser-based avatar chat
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
Available capability options for Python sessions:
- `LLM` - Large Language Model for text conversations
- `TTS` - Text-to-Speech for audio generation
- `STT` - Speech-to-Text for voice input

**Note:** Browser avatar visualization uses independent WebRTC capabilities managed by the web SDK.

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
