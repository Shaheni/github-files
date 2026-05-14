# Camera & Voice API Quick Reference

## Camera Endpoints

### 1. Get Camera Status
```
GET /api/camera/status
```
**Response:**
```json
{
  "state": "running",
  "running": true,
  "frame_count": 1250,
  "frames_buffered": 2,
  "last_frame_time": 1234567890.123,
  "error": null,
  "camera_index": 0,
  "resolution": "640x480",
  "fps": 30
}
```

### 2. Start Camera
```
POST /api/camera/start
```
**Response:**
```json
{
  "success": true,
  "message": "Camera started",
  "state": "initializing"
}
```

### 3. Stop Camera
```
POST /api/camera/stop
```
**Response:**
```json
{
  "success": true,
  "message": "Camera stopped"
}
```

### 4. Stream Video
```
GET /api/camera/video_feed
```
**Response:** MJPEG video stream
**Usage:**
```html
<img src="http://127.0.0.1:5050/api/camera/video_feed" />
```

---

## Voice Endpoints

### 1. Get Voice Status
```
GET /api/voice/status
```
**Response:**
```json
{
  "state": "listening",
  "running": true,
  "queue_size": 2,
  "queue_max": 10,
  "command_count": 45,
  "error_count": 3,
  "last_command": "home position",
  "error": null,
  "timeout_seconds": 10,
  "phrase_timeout_seconds": 5,
  "supported_commands": ["home position", "grab object", ...]
}
```

### 2. Start Voice Recognition
```
POST /api/voice/start
```
**Response:**
```json
{
  "success": true,
  "message": "Voice recognition started",
  "state": "listening"
}
```

### 3. Stop Voice Recognition
```
POST /api/voice/stop
```
**Response:**
```json
{
  "success": true,
  "message": "Voice recognition stopped"
}
```

### 4. Get Supported Commands
```
GET /api/voice/commands
```
**Response:**
```json
{
  "commands": {
    "home position": [90, 90, 90, 90, 90, 90],
    "grab object": [45, 120, 120, 90, 90, 90]
  },
  "total": 2
}
```

### 5. Get Next Command
```
GET /api/voice/command/next
```
**Response (if command available):**
```json
{
  "command": {
    "text": "home position",
    "timestamp": 1234567890.123,
    "confidence": "high"
  },
  "queue_size": 1
}
```
**Response (if no command):** 204 No Content

### 6. Get Queue Status
```
GET /api/voice/queue
```
**Response:**
```json
{
  "queue_size": 2,
  "queue_max": 10
}
```

### 7. Clear Queue
```
DELETE /api/voice/queue
```
**Response:**
```json
{
  "success": true,
  "cleared": 2
}
```

---

## Frontend Implementation Examples

### JavaScript: Start Camera
```javascript
async function startCamera() {
  try {
    const response = await fetch('http://127.0.0.1:5050/api/camera/start', {
      method: 'POST'
    });
    const result = await response.json();
    console.log('Camera started:', result);
  } catch (error) {
    console.error('Camera start error:', error);
  }
}
```

### JavaScript: Fetch Voice Status
```javascript
async function getVoiceStatus() {
  try {
    const response = await fetch('http://127.0.0.1:5050/api/voice/status');
    const status = await response.json();
    console.log('Voice status:', status);
    console.log('Queue size:', status.queue_size);
    console.log('Last command:', status.last_command);
  } catch (error) {
    console.error('Status fetch error:', error);
  }
}
```

### JavaScript: Process Voice Commands
```javascript
async function processVoiceCommands() {
  const response = await fetch('http://127.0.0.1:5050/api/voice/command/next');
  
  if (response.status === 204) {
    console.log('No commands in queue');
    return;
  }
  
  const data = await response.json();
  const command = data.command;
  
  console.log('Recognized:', command.text);
  
  // Send to robot motion endpoint
  await fetch('http://127.0.0.1:5050/api/robot/command', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      servo1: command.angles[0],
      servo2: command.angles[1],
      servo3: command.angles[2],
      servo4: command.angles[3],
      servo5: command.angles[4],
      servo6: command.angles[5]
    })
  });
}
```

### HTML: Display Video Feed
```html
<div class="video-container">
  <h3>Live Camera Feed</h3>
  <img 
    id="videoFeed" 
    src="http://127.0.0.1:5050/api/camera/video_feed"
    alt="Robot Camera"
    width="640"
    height="480"
  />
</div>
```

### HTML: Camera Controls
```html
<div class="camera-controls">
  <button onclick="startCamera()">Start Camera</button>
  <button onclick="stopCamera()">Stop Camera</button>
  <button onclick="cameraStatus()">Get Status</button>
</div>
```

### HTML: Voice Controls
```html
<div class="voice-controls">
  <button onclick="startVoice()">Start Listening</button>
  <button onclick="stopVoice()">Stop Listening</button>
  <button onclick="checkCommands()">Check Queue</button>
  <div id="voiceStatus">Status: Unknown</div>
</div>
```

---

## Error Handling

### Camera Errors
- **503 Service Unavailable**: Camera not running
- **500 Internal Error**: Camera initialization failed
- **409 Conflict**: Camera already running

### Voice Errors
- **409 Conflict**: Voice already running
- **500 Internal Error**: Initialization failed
- **204 No Content**: Queue is empty

---

## Polling Strategy

### Camera
```javascript
// Poll status every 5 seconds
setInterval(async () => {
  const status = await fetch('/api/camera/status').then(r => r.json());
  console.log('Frames captured:', status.frame_count);
}, 5000);
```

### Voice
```javascript
// Poll for commands every 1 second
setInterval(async () => {
  const response = await fetch('/api/voice/command/next');
  if (response.status !== 204) {
    const data = await response.json();
    processCommand(data.command);
  }
}, 1000);
```

---

## Key Points

✅ Camera runs in background thread (non-blocking)  
✅ Voice listens continuously when started  
✅ Both support start/stop control  
✅ Commands queue automatically  
✅ Status available on-demand  
✅ All errors handled gracefully  
✅ Resources cleanup on shutdown  
✅ Production-grade reliability  

---

**Ready for frontend integration!**
