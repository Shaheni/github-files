# AI Robotics Command Center Backend API Documentation (CORRECTED)

**Release Date:** May 14, 2026
**Scope:** USB-tethered Arduino robot arm demo (Flask backend)

---

## Overview

This document describes the REST API for the backend controlling a 6-DOF robot arm via Arduino (USB, PySerial). All endpoints, request/response formats, and error handling reflect the CORRECTED, demo-stable implementation:

- NO automatic retries (single send only)
- MAX queue size = 3 (prevents spam)
- Only REAL runtime state exposed (no fake telemetry)
- Manual recovery for errors

---

## Table of Contents

1. [Architecture](#architecture)
2. [Endpoints](#endpoints)
		- [POST /api/robot/command](#1-send-robot-motion-command)
		- [POST /api/robot/stop](#2-emergency-stop)
		- [POST /api/robot/reset](#3-reset-motion-engine)
		- [GET /api/robot/status](#4-get-robot-status)
		- [GET /api/telemetry](#5-get-telemetry)
		- [GET /api/health](#6-health-check)
3. [Serial Protocol](#serial-protocol)
4. [Servo Constraints](#servo-constraints)
5. [Execution Model](#execution-model)
6. [Error Handling](#error-handling)
7. [Testing & Recovery](#testing--recovery)

---

## Architecture

**Stack:**
- Python Flask backend (routes/controllers/services)
- PySerial for Arduino communication
- Synchronous FIFO command queue (max 3)
- No async, no retries, no fake telemetry

**Flow:**
Frontend → /api/robot/command → motion_engine → command_mapper → serial_service → Arduino

---

## Endpoints

### 1. Send Robot Motion Command

**POST /api/robot/command**

**Request:**
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

**Response (Success):**
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

**Response (Queue Full):**
```json
{
	"success": false,
	"state": "idle",
	"queue_size": 3,
	"error": "Queue full: 3 commands pending"
}
```

**Response (Timeout/Error):**
```json
{
	"success": false,
	"state": "error",
	"queue_size": 0,
	"error": "No response from Arduino - check serial connection"
}
```

---

### 2. Emergency Stop

**POST /api/robot/stop**

**Request:** (no body)

**Response:**
```json
{
	"success": true,
	"state": "stopped",
	"message": "Motion queue cleared"
}
```

---

### 3. Reset Motion Engine

**POST /api/robot/reset**

**Request:** (no body)

**Response:**
```json
{
	"success": true,
	"message": "Motion engine reset to idle"
}
```

---

### 4. Get Robot Status

**GET /api/robot/status**

**Response:**
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

---

### 5. Get Telemetry (Real State Only)

**GET /api/telemetry**

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

---

### 6. Health Check (Real Verification)

**GET /api/health**

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

## Serial Protocol

- **Packet Format:** `val1,val2,val3,val4,val5,val6\n` (comma-separated, newline-terminated)
- **Example:** `90,90,90,90,90,90\n`
- **Responses:**
		- `OK\n` (success)
		- `INVALID_PACKET\n` (parse error)
		- `ROBOT_READY\n` (startup)

---

## Servo Constraints

| Servo   | Min | Max |
|---------|-----|-----|
| Servo1  |  0  | 180 |
| Servo2  | 10  | 170 |
| Servo3  | 10  | 170 |
| Servo4  |  0  | 180 |
| Servo5  |  0  | 180 |
| Servo6  |  0  | 180 |

---

## Execution Model

1. Validate request (all 6 servos, within bounds)
2. Check queue size (max 3)
3. Add to queue if space
4. Execute when idle
5. Send packet ONCE (no retries)
6. Wait for Arduino response (0.5s timeout)
7. On OK → success, next command
8. On error/timeout → error state, manual retry required

---

## Error Handling

- **Validation error:** Returns 400 with error message
- **Queue full:** Returns 429 with error message
- **Serial/timeout error:** Returns 500 with error message, enters error state
- **Manual recovery:** Operator must POST /api/robot/reset to clear error

---

## Testing & Recovery

**Test single command:**
```bash
POST /api/robot/command {"servo1":90,...}
→ Should succeed if Arduino connected
```

**Test queue limit:**
```bash
Send 4 commands rapidly
→ 4th should fail with "Queue full"
```

**Test error recovery:**
```bash
Disconnect Arduino mid-command
→ Command fails with timeout
→ POST /api/robot/reset to recover
```

**Test health check:**
```bash
GET /api/health (before Arduino connected)
→ arduino_responsive: false

GET /api/health (after Arduino connects)
→ arduino_responsive: true
```

---

## What NOT to Do (Demo Phase)

- Do NOT add automatic retries
- Do NOT expose fake telemetry
- Do NOT increase queue size
- Do NOT migrate frameworks
- Do NOT add AI/CV/SocketIO features yet

---

## Contact

For questions, contact the backend maintainer.