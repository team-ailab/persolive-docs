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
# Check available LLM types
python main.py --list-settings llm_type

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
    "model_style": "string",        // Optional: Avatar model style name (e.g., "yuri-front_natural")
    "llm_type": "string",           // Optional: LLM type name (e.g., "gpt-35", "gpt-4")
    "tts_type": "string",           // Optional: TTS type name (e.g., "yuri", "azuretts-ko-KR-InJoonNeural-sad")
    "stt_type": "string",           // Optional: STT type name (e.g., "default")
    "capability": ["string"],       // Optional: Array of capability names (e.g., ["LLM", "TTS", "STT", "STF_WEBRTC"])
    "prompt": "string",             // Optional: Prompt ID (e.g., "plp-d432cb910983f1eed6511eba836ac14f")
    "background_image": "string",   // Optional: Background image ID
    "document": "string",           // Optional: Document ID (for AI context)
    "agent": "string",              // Optional: Agent identifier
    "padding_left": "float",        // Optional: Avatar left padding (-1.0 to 1.0)
    "padding_top": "float",         // Optional: Avatar top padding (0.0 to 1.0)
    "padding_height": "float",      // Optional: Avatar height scaling (0 to 5)
    "extra_data": "object"          // Optional: Additional session data
}
```

**Response:**
```json
{
    "session_id": "string",         // Generated unique session ID
    "created_at": "datetime",       // Session creation timestamp
    "status": "CREATED",            // Session status (always CREATED for new sessions)
    "prompt": "string",             // Prompt ID if provided
    "capability": ["string"],       // Array of capability names
    "document": "string",           // Document ID if provided
    "llm_type": "string",           // LLM type name if provided
    "tts_type": "string",           // TTS type name if provided
    "stt_type": "string",           // STT type name if provided
    "model_style": "string",        // Model style name if provided
    "agent": "string",              // Agent identifier if provided
    "padding_left": "float",        // Avatar left padding if provided
    "padding_top": "float",         // Avatar top padding if provided
    "padding_height": "float",      // Avatar height scaling if provided
    "background_image": "string",   // Background image ID if provided
    "extra_data": "object"          // Additional session data if provided
}
```

### 2. Start Session

**Endpoint:** `POST /api/v1/session/{session_id}/event/create/`

Initializes the session for active communication by creating a SessionEvent.

**Request Parameters:**
```json
{
    "event": "SESSION_START",       // Required: Event type (SESSION_START, SESSION_DURING, SESSION_LOG, SESSION_END, SESSION_ERROR, SESSION_TTS, SESSION_STT, SESSION_LLM)
    "detail": "string"              // Optional: Event detail description
}
```

**Response:**
```json
{
    "sessionevent_id": "uuid",      // Generated unique event ID
    "created_at": "datetime",       // Event creation timestamp
    "detail": "string",             // Event detail description
    "terminate": false,             // Whether this event terminates the session (read-only)
    "terminate_reason": "string",   // Termination reason if applicable (read-only)
    "event": "SESSION_START"        // Event type
}
```

### 3. Text Chat (LLM)

**Endpoint:** `POST /api/v1/session/{session_id}/llm/`

Sends a text message to the AI and receives a streaming response.

**Request Parameters:**
```json
{
    "message": "string",            // Required: User message
    "clear_history": true           // Required: Whether to clear conversation history
}
```

**Response (Streaming):**
```
Content-Type: text/plain

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
    "audio": "base64_string"        // Base64 encoded audio data
}
```

### 5. Speech-to-Text (STT)

**Endpoint:** `POST /api/v1/session/{session_id}/stt/`

Converts audio file to text using speech recognition.

**Request Parameters (multipart/form-data):**
- `audio`: Audio file (required)
- `language`: Language code (optional, e.g., "ko", "en")

**Response:**
```json
{
    "text": "string"                // Recognized text from audio
}
```

### 6. Get Session Status

**Endpoint:** `GET /api/v1/session/{session_id}/`

Retrieves current session information and status.

**Response:**
```json
{
    "session_id": "string",         // Unique session identifier
    "client_sdp": "object",         // Client SDP information (nullable)
    "server_sdp": "object",         // Server SDP information (nullable)
    "prompt": {                     // Prompt information (nullable)
        "prompt_id": "string",
        "title": "string",
        "content": "string"
    },
    "document": "string",           // Document ID if provided (nullable)
    "llm_type": {                   // LLM type information (nullable)
        "name": "string",
        "display_name": "string"
    },
    "model_style": {                // Model style information (nullable)
        "name": "string",
        "display_name": "string"
    },
    "tts_type": {                   // TTS type information (nullable)
        "name": "string",
        "display_name": "string"
    },
    "stt_type": {                   // STT type information (nullable)
        "name": "string",
        "display_name": "string"
    },
    "ice_servers": "object",        // ICE servers configuration (nullable)
    "status": "string",             // Session status (CREATED, EXCHANGED, IN_PROGRESS, TERMINATED)
    "termination_reason": "string", // Termination reason if ended (nullable)
    "duration_sec": "integer",      // Session duration in seconds
    "created_at": "datetime",       // Session creation timestamp
    "session_acls": ["string"],     // Array of session ACL names
    "padding_left": "float",        // Avatar left padding (nullable)
    "padding_top": "float",         // Avatar top padding (nullable)
    "padding_height": "float",      // Avatar height scaling (nullable)
    "background_image": {           // Background image information (nullable)
        "backgroundimage_id": "string",
        "title": "string",
        "image": "string",
        "created_at": "datetime"
    },
    "extra_data": "object"          // Additional session data (nullable)
}
```

### 7. End Session

**Endpoint:** `POST /api/v1/session/{session_id}/event/create/`

Gracefully terminates the chat session by creating a termination event.

**Request Parameters:**
```json
{
    "event": "SESSION_END",         // Required: Must be SESSION_END
    "detail": "string"              // Optional: Termination reason description
}
```

**Response:**
```json
{
    "sessionevent_id": "uuid",      // Generated unique event ID
    "created_at": "datetime",       // Event creation timestamp
    "detail": "string",             // Event detail description
    "terminate": false,             // Whether this event terminates the session (read-only)
    "terminate_reason": "string",   // Termination reason if applicable (read-only)
    "event": "SESSION_END"          // Event type
}
```

### 8. Get Available Settings

**Available endpoints for retrieving configuration options:**

#### TTS Types
**Endpoint:** `GET /api/v1/settings/tts_type/`

**Response:**
```json
[
    {
        "name": "string",           // TTS type identifier
        "display_name": "string",   // Human-readable name
        "description": "string"     // TTS type description
    }
]
```

#### Model Styles
**Endpoint:** `GET /api/v1/settings/modelstyle/`

**Response:**
```json
[
    {
        "name": "string",           // Model style identifier  
        "display_name": "string",   // Human-readable name
        "description": "string"     // Model style description
    }
]
```

#### STT Types
**Endpoint:** `GET /api/v1/settings/stt_type/`

**Response:**
```json
[
    {
        "name": "string",           // STT type identifier
        "display_name": "string",   // Human-readable name
        "description": "string"     // STT type description
    }
]
```

#### Session Capabilities
**Endpoint:** `GET /api/v1/settings/capability/`

**Response:**
```json
[
    {
        "name": "string",           // Capability name (LLM, TTS, STT, STF_ONPREMISE, STF_WEBRTC)
        "description": "string"     // Capability description
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

### Capability Types
Available capability options:
- `LLM` - Large Language Model for text conversations
- `TTS` - Text-to-Speech for audio generation  
- `STT` - Speech-to-Text for voice input
- `STF_ONPREMISE` - Speech-to-Face on-premise processing
- `STF_WEBRTC` - Speech-to-Face with WebRTC streaming

### Session Status Values
- `CREATED` - Session created but not started
- `EXCHANGED` - WebRTC connection established (if applicable)  
- `IN_PROGRESS` - Session active and ready for communication
- `TERMINATED` - Session ended

### Session Event Types
- `SESSION_START` - Session initialization event
- `SESSION_DURING` - Ongoing session activity
- `SESSION_LOG` - Session logging event
- `SESSION_END` - Session termination event
- `SESSION_ERROR` - Session error event
- `SESSION_TTS` - Text-to-speech event
- `SESSION_STT` - Speech-to-text event
- `SESSION_LLM` - Language model interaction event

### Session Termination Reasons
- `GRACEFUL_TERMINATION` - Session ended normally
- `SESSION_EXPIRED_BEFORE_CONNECTION` - Session timed out before connection
- `SESSION_LOST_AFTER_CONNECTION` - Connection lost during session
- `SESSION_MISC_ERROR` - Miscellaneous error occurred
- `MAX_ACTIVE_SESSION_QUOTA_EXCEEDED` - Too many active sessions
- `MAX_MIN_PER_SESSION_QUOTA_EXCEEDED` - Per-session time limit exceeded
- `TOTAL_MIN_PER_MONTH_QUOTA_EXCEEDED` - Monthly quota limit exceeded

### LLM Types
Popular LLM types include:
- `gpt-35` - GPT-3.5 Turbo (default)
- `gpt-4` - GPT-4 for enhanced reasoning
- `gpt-4o` - GPT-4 Omni for enhanced reasoning

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

### Browser Avatar Visualization

For real-time avatar chat with video streaming, use the browser-based web SDK:

**Prerequisites:**
- Download the SDK sample from: https://github.com/est-perso-live/perso-live-sdk-sample
- Clone or download the repository to your local machine

1. **Access the web interface:**
   - Path: `./perso-live-sdk-sample/js/src/index.html`
   - Open in Chrome or Firefox browser

2. **Configure avatar settings in browser:**
   - **Model style selection** - Choose from various avatar appearances and poses
   - **Background customization** - Set custom background images for the avatar  
   - **Position control** - Adjust avatar positioning with padding parameters
   - **TTS/STT configuration** - Select voice and speech recognition types

3. **Browser creates independent session:**
   - The web SDK creates its own session with avatar-specific parameters
   - No connection to Python sessions - completely independent
   - WebRTC video streaming works only in browser environment

**Note:** Browser avatar visualization uses independent WebRTC capabilities managed by the web SDK.

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

**Note:** "Launch avatar visualization" provides guidance for browser-based avatar chat using the web SDK, which creates its own independent sessions.

## Best Practices

1. **Session Management**: Always call `end_session()` to clean up resources
2. **Error Handling**: Check session status before making API calls
3. **Audio Quality**: Use good quality audio for better STT results
4. **Rate Limiting**: Respect API rate limits for production use
5. **Resource Cleanup**: Remove temporary audio files after processing
