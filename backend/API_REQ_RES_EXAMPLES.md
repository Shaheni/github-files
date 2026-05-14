# API Request and Response Examples (CORRECTED)

This document provides example requests and responses for the main backend API endpoints. All examples reflect REAL execution model with NO automatic retries and MAX queue size of 3.

---

## 1. Send Robot Motion Command

**Endpoint:**
```
POST /api/robot/command
```

**Request Example (Home Position):**
```json
{
  "servo1": 90,
  "servo2": 90,
  "servo3": 90,
  "servo4": 90,
  "servo5": 90,
  "servo6": 90
}
```

**Response (Success - Command Queued):**
```json
{
  "success": true,
  "state": "executing",
  "queue_size": 0,
  "error": null
}
```

**Response (Validation Error):**
```json
{
  "success": false,
  "state": "idle",
  "queue_size": 0,
  "error": "servo2 out of bounds: 180 (valid: 10-170)"
}
```

**Response (Queue Full - Max 3 Commands):**
```json
{
  "success": false,
  "state": "idle",
  "queue_size": 3,
  "error": "Queue full: 3 commands pending"
}
```

**Response (Hardware Timeout - No Automatic Retry):**
```json
{
  "success": false,
  "state": "error",
  "queue_size": 0,
  "error": "No response from Arduino - check serial connection"
}
```

---

## 2. Emergency Stop

**Endpoint:**
```
POST /api/robot/stop
```

**Request Example:**
```
(no body)
```

**Response:**
```json
{
  "success": true,
  "state": "stopped",
  "message": "Motion queue cleared"
}
```

---

## 3. Reset Motion Engine

**Endpoint:**
```
POST /api/robot/reset
```

**Request Example:**
```
(no body)
```

**Response:**
```json
{
  "success": true,
  "message": "Motion engine reset to idle"
}
```

---

## 4. Get Robot Status

**Endpoint:**
```
GET /api/robot/status
```

**Response (Idle State):**
```json
{
  "motion": {
    "state": "idle",
    "queue_size": 0,
    "max_queue_size": 3,
    "last_command": "90,90,90,90,90,90",
    "last_result": {
      "success": true,
      "response": "OK",
      "error": null
    },
    "last_error": null
  },
  "serial": {
    "connected": true,
    "port": "COM5",
    "baud_rate": 115200,
    "last_response": "OK"
  }
}
```

**Response (Error State - Manual Retry Required):**
```json
{
  "motion": {
    "state": "error",
    "queue_size": 0,
    "max_queue_size": 3,
    "last_command": "90,90,90,90,90,90",
    "last_result": {
      "success": false,
      "response": "TIMEOUT",
      "error": "No response from Arduino - check serial connection"
    },
    "last_error": "No response from Arduino - check serial connection"
  },
  "serial": {
    "connected": true,
    "port": "COM5",
    "baud_rate": 115200,
    "last_response": "TIMEOUT"
  }
}
```

---

## 5. Get Telemetry (Real State Only)

**Endpoint:**
```
GET /api/telemetry
```

**Response:**
```json
{
  "execution_state": "idle",
  "queue_size": 0,
  "max_queue_size": 3,
  "last_command": "90,90,90,90,90,90",
  "last_error": null,
  "serial_connected": true,
  "serial_port": "COM5",
  "last_arduino_response": "OK"
}
```

**Note:** Fake telemetry (battery, temperature, speed, latency) removed. Only REAL runtime state exposed for engineering credibility.

---

## 6. Health Check (Real Verification)

**Endpoint:**
```
GET /api/health
```

**Response (All Systems Ready):**
```json
{
  "status": "ok",
  "backend_ready": true,
  "serial_connected": true,
  "arduino_responsive": true,
  "last_arduino_response": "OK"
}
```

**Response (Arduino Not Connected):**
```json
{
  "status": "ok",
  "backend_ready": true,
  "serial_connected": false,
  "arduino_responsive": false,
  "last_arduino_response": null
}
```

---

## Key Differences from Prototype

1. **NO Automatic Retries** — Single send only, timeout = error state
2. **Queue Limit = 3** — Prevents frontend spam
3. **Real Telemetry Only** — No fake battery/temperature/speed
4. **Manual Recovery** — Operator must manually retry or reset
5. **Real Health Check** — Verifies actual Arduino communication
