# AI Avatar Chat System

The AI Avatar Chat System provides an interactive Python interface for real-time conversations with AI avatars. It supports text chat, voice conversations, and browser-based avatar visualization through WebRTC.

## Overview

This system enables:
- **Text Chat**: Type messages and receive AI responses
- **Voice Chat**: Record voice messages and receive audio responses  
- **Voice File Processing**: Upload audio files for speech recognition
- **Settings Discovery**: Browse available LLM, TTS types and model styles
- **Browser Avatar Visualization**: Real-time avatar chat with WebRTC video streaming

## Prerequisites

You need an API key issued by Perso.ai to use this service. Please contact our support team to obtain your API credentials.

- Python 3.8+
- API key for the Perso.ai Live API service: Please contact our support team to obtain your API credentials.
- Optional: `pyaudio` for voice recording features (for voice chat)
- Modern web browser (Chrome/Firefox) for avatar visualization (for browser avatar visualization)

## Installation

1. **Clone the repository:**
   ```bash
   # for live chat
   git clone https://github.com/team-ailab/persolive-docs.git
   cd live-chat
   ```

2. **Install Python dependencies:**
   ```bash
   # The script uses only the `requests` library for HTTP communication
   pip install requests
   
   # Optional: for voice recording features
   pip install pyaudio
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

### Basic Usage

1. **Start the interactive system:**
   ```bash
   python main.py
   ```

2. **Available menu options:**
   - **Text Chat**: Type messages and receive text responses
   - **Voice Chat**: Record voice messages and receive audio responses
   - **Voice File Chat**: Upload audio files for processing
   - **Chat History**: View previous conversation messages
   - **Launch Avatar Visualization**: Get guidance for browser-based avatar chat
   - **Check Available Settings**: Browse available TTS types and model styles
   - **Exit**: Clean up and terminate the session

### Configuration Options

**Custom AI configuration:**
```bash
# Use different LLM and TTS types
python main.py --llm-type gpt-35 --tts-type "yuri"

# Use different avatar model style
python main.py --model-style "yuri-front_natural"

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

**API server and API key configuration:**
```bash
python main.py --api-server "https://platform.perso.ai" --api-key "your-api-key"
```

**Capability selection:**
```bash
# Use default capabilities (recommended)
python main.py --capability LLM TTS STT

# Enable subset of capabilities  
python main.py --capability LLM TTS  # Text-only mode
python main.py --capability LLM      # Chat without audio
```

**Text normalization configuration:**
```bash
# Use custom text normalization configuration and locale
python main.py --text_normalization_config "test" --text_normalization_locale "en-US"

# Korean locale
python main.py --text_normalization_config "test" --text_normalization_locale "ko-KR"

# English locale
python main.py --text_normalization_config "test" --text_normalization_locale "en-US"

# Japanese locale  
python main.py --text_normalization_config "test" --text_normalization_locale "ja-JP"
```
### Complete Workflow Example

when you start the chat system, you can see the menu.

```bash
python main.py
```

1. **Option 1 - Start Basic Chat:**
   ```bash
   # Choose option 1 from the menu
   # Type your message and receive AI responses
   ```

2. **Option 2 - Try Voice Chat:**
   ```bash
   # Ensure pyaudio is installed
   pip install pyaudio
   
   # Choose option 2 from the menu
   # Record your voice message and receive audio response
   ```

3. **Option 3 - Try Voice File Chat:**
   ```bash
   # Choose option 3 from the menu
   # Upload an audio file and receive text response
   ```

4. **Option 4 - View Chat History:**
   ```bash
   # Choose option 4 from the menu
   # View previous conversation messages
   ```

5. **Option 5 - Browser Avatar Visualization:**
   ```bash
   # Choose option 5 from the menu
   # Follow the guidance to open browser-based avatar chat
   ```

6. **Option 6 - Check Available Settings:**
   ```bash
   # Choose option 6 from the menu
   # Browse available LLM types, TTS types and model styles
   ```

7. **Option 7 - Exit:**

## API Reference

### 1. Create Session

**Endpoint:** `POST /api/v1/session/`

Creates a new chat session with the AI avatar.

**Request Parameters:**
```json
{
    "model_style": "string",                    // Optional: Avatar model style name (e.g., "yuri-front_natural")
    "llm_type": "string",                       // Optional: LLM type name (e.g., "gpt-35", "gpt-4")
    "tts_type": "string",                       // Optional: TTS type name (e.g., "yuri", "k_idol_m_3_yoon_hajin")
    "stt_type": "string",                       // Optional: STT type name (e.g., "default")
    "capability": ["string"],                   // Optional: Array of capability names (e.g., ["LLM", "TTS", "STT"])
    "prompt": "string",                         // Optional: Prompt ID (e.g., "plp-d432cb910983f1eed6511eba836ac14f")
    "background_image": "string",               // Optional: Background image ID
    "document": "string",                       // Optional: Document ID (for AI context)
    "agent": "string",                          // Optional: Agent identifier
    "padding_left": "float",                    // Optional: Avatar left padding (-1.0 to 1.0)
    "padding_top": "float",                     // Optional: Avatar top padding (0.0 to 1.0)
    "padding_height": "float",                  // Optional: Avatar height scaling (0 to 5)
    "text_normalization_config": "string",      // Optional: Text normalization configuration name (e.g., "test")
    "text_normalization_locale": "string",      // Optional: Text normalization locale (e.g., "en-US", "ko-KR", "ja-JP")
    "extra_data": "object"                      // Optional: Additional session data
}
```

**Response:**
```json
{
    "session_id": "string",                     // Generated unique session ID
    "created_at": "datetime",                   // Session creation timestamp
    "status": "CREATED",                        // Session status (always CREATED for new sessions)
    "prompt": "string",                         // Prompt ID if provided
    "capability": ["string"],                   // Array of capability names
    "document": "string",                       // Document ID if provided
    "llm_type": "string",                       // LLM type name if provided
    "tts_type": "string",                       // TTS type name if provided
    "stt_type": "string",                       // STT type name if provided
    "model_style": "string",                    // Model style name if provided
    "agent": "string",                          // Agent identifier if provided
    "padding_left": "float",                    // Avatar left padding if provided
    "padding_top": "float",                     // Avatar top padding if provided
    "padding_height": "float",                  // Avatar height scaling if provided
    "text_normalization_config": "string",      // Text normalization config if provided
    "text_normalization_locale": "string",      // Text normalization locale if provided
    "background_image": "string",               // Background image ID if provided
    "extra_data": "object"                      // Additional session data if provided
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

1. **Clone the repository:**
   ```bash
   git clone https://github.com/est-perso-live/perso-live-sdk-sample.git
   ```

2. **Access the web interface:**
   - Path: `./perso-live-sdk-sample/js/src/index.html`
   - Open in browser

3. **Configure avatar settings in browser:**
   - **API server** - Set the API server URL
   - **API key** - Set the API key
   - **LLM/TTS configuration** - Select LLM, TTS types
   - **AI Human style selection** - Choose from various avatar appearances and poses
   - **(Optional) Background** - Set custom background images for the avatar
   - **(Optional) Prompt** - Set custom prompt for the avatar
   - **(Optional) Intro Message** - Set custom intro message for the avatar
   - **(Optional) Document** - Set custom document for the avatar
   - **(Optional) Screen Orientation** - Choose from various screen orientations
   - **(Optional) Position control** - Adjust avatar positioning with padding parameters

4. **Browser creates independent session:**
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

error codes:
- `400`: Bad Request - Invalid parameters or session state
- `401`: Unauthorized - Invalid API key
- `404`: Not Found - Session doesn't exist
- `413`: Payload Too Large - Audio file too big
- `429`: Rate Limited - Too many requests
- `500`: Internal Server Error - Server issue
