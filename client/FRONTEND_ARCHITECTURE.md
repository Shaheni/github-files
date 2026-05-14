# Frontend Architecture Documentation

## Overview

Production-grade React + Vite frontend for controlling USB-tethered robot arm. Built for stability, reliability, and maintainability.

## Core Principles

1. **Simplicity** — No unnecessary abstractions
2. **Reliability** — Fail gracefully with clear error messages
3. **Debuggability** — Comprehensive logging throughout
4. **Accessibility** — WCAG AA compliance
5. **Performance** — Lightweight, fast rendering

## Architecture Layers

```
┌─────────────────────────────────────────┐
│         UI Components                   │
│  (Dashboard, ServoControls, Panels)     │
├─────────────────────────────────────────┤
│      Business Logic Layer                │
│  (Dashboard state, polling, callbacks)   │
├─────────────────────────────────────────┤
│        API Client Layer                  │
│  (robotApi.js - HTTP, retry, error)     │
├─────────────────────────────────────────┤
│      Backend Flask Server                │
└─────────────────────────────────────────┘
```

## Module Breakdown

### `src/api/robotApi.js`

**Purpose:** Centralized backend API communication

**Responsibilities:**
- HTTP requests via axios with timeout
- Request retry with exponential backoff
- Error normalization to consistent format
- Detailed logging of API operations
- Type checking and response validation

**Key Functions:**
- `sendRobotCommand(angles)` — Submit servo command
- `getRobotStatus()` — Get motion state
- `getTelemetry()` — Get telemetry data
- `healthCheck()` — Verify backend/Arduino
- `emergencyStop()` — Immediate stop
- `resetRobot()` — Reset to idle

**Error Handling:**
- `backend_offline` — No network response
- `validation` — Invalid input (400)
- `queue_full` — Command queue full (429)
- `hardware` — Arduino comm error (500)

### `src/pages/Dashboard.jsx`

**Purpose:** Main application state and orchestration

**Responsibilities:**
- Backend state polling (every 1000ms)
- Error state tracking (poll failures)
- Backend offline detection
- Component coordination
- Callback management

**State Variables:**
- `status` — Robot motion status
- `telemetry` — Real-time telemetry data
- `health` — Backend/Arduino health
- `loading` — Initial load indicator
- `backendOffline` — Connection loss detection
- `pollErrors` — Failed poll attempts

**Data Flow:**
```
fetchAll() → Promise.all([status, telemetry, health])
    ↓
Set state if successful
    ↓
Re-render components with new data
    ↓
Display in UI panels
```

### `src/components/ServoControls.jsx`

**Purpose:** Robot servo control interface

**Responsibilities:**
- 6 servo sliders and numeric inputs
- Real-time validation with user feedback
- Command submission and sending state
- Prevent rapid repeated submissions
- Format payload for backend

**Key Features:**
- Per-servo range validation (uses SERVO_LIMITS)
- Debouncing via sending state
- Clear error messages
- Disabled state during submission
- Accessible form with ARIA labels

### `src/components/StatusPanel.jsx`

**Purpose:** Display robot execution status

**Responsibilities:**
- Show execution state (idle/executing/error/stopped)
- Display queue size (X / 3)
- Last command tracking
- Error message display
- Loading state handling

### `src/components/TelemetryPanel.jsx`

**Purpose:** Display real hardware telemetry

**Responsibilities:**
- Serial connection status
- Serial port name
- Last Arduino response
- Execution state
- Queue information
- Last error message

**Note:** Only displays REAL data (no fake battery/temperature/etc)

### `src/components/ConnectionStatus.jsx`

**Purpose:** Visual connection indicator

**Responsibilities:**
- Backend availability detection
- Arduino responsiveness check
- Clear status messages
- Color-coded indicators (green/yellow/red)

**States:**
- `Connected & Ready` — Both backend and Arduino ready
- `Serial Only` — Backend ready, Arduino not responding
- `Backend Offline` — Backend unavailable
- `Not Connected` — Neither available
- `Checking...` — Initial load

### `src/components/ErrorBoundary.jsx`

**Purpose:** React-level error handling

**Responsibilities:**
- Catch React component errors
- Prevent white screen of death
- Log errors for debugging
- Provide recovery button
- Show error details in development

**Error Scenarios:**
- Component render errors
- Event handler exceptions
- Lifecycle method errors
- Async callback errors

### `src/constants/servoConfig.js`

**Purpose:** Centralized configuration constants

**Contains:**
- `DEFAULT_ANGLES` — [90, 90, 90, 90, 90, 90]
- `SERVO_LIMITS` — Per-servo min/max ranges
- `MAX_QUEUE_SIZE` — 3 (prevents spam)
- `BACKEND_URL` — Server address
- `POLLING_INTERVAL_MS` — 1000ms

### `src/config/env.js`

**Purpose:** Environment variable loading

**Features:**
- Loads from .env file via Vite
- Defaults to standard values
- Type-safe configuration
- Single source of truth

**Variables:**
- `VITE_BACKEND_URL` — Backend server
- `VITE_REQUEST_TIMEOUT` — HTTP timeout
- `VITE_POLLING_INTERVAL` — Status poll interval
- `VITE_MAX_RETRIES` — API retry attempts

### `src/utils/logger.js`

**Purpose:** Production-grade logging utility

**Functions:**
- `logger.debug()` — Development only
- `logger.info()` — General information
- `logger.warn()` — Warning conditions
- `logger.error()` — Error conditions

**Features:**
- Timestamp on all logs
- Development-only debug logs
- Error sending capability (ready)
- Consistent format

### `src/utils/validation.js`

**Purpose:** Input validation utilities

**Functions:**
- `validateServoValue(idx, value)` — Single servo validation
- `validateAllServos(angles)` — All servos validation
- `sanitizeServoAngles(angles)` — Clip values to valid ranges

**Validation Rules:**
- Servo1, 4, 5, 6: 0-180°
- Servo2, 3: 10-170°
- All values must be integers

## Data Flow Diagram

```
User Interacts with UI
    ↓
ServoControls.handleChange() → Validate, Update state
    ↓
ServoControls.handleSubmit() → robotApi.sendRobotCommand()
    ↓
robotApi → axios → Backend /api/robot/command
    ↓
Backend processes, returns response
    ↓
Normalized response → ServoControls → Show success/error
    ↓
Dashboard.fetchAll() → Updates all state
    ↓
UI components re-render with new data
```

## State Management

### Global State (Dashboard)
- Managed via React hooks (useState)
- Updated via polling (setInterval)
- No Redux/Zustand needed for this scale

### Component State (ServoControls)
- Servo angles (0-180)
- Submission error
- Sending flag (prevents double-submit)

### Component State (EmergencyControls)
- Stopping flag
- Resetting flag

## Error Handling Strategy

### Frontend Layer
1. **Validation** — Client-side input validation
2. **Error Boundary** — Catch React errors
3. **Try/Catch** — Async operation errors
4. **Normalization** — Consistent error format

### API Layer (robotApi.js)
1. **Timeout** — Request timeout (10s)
2. **Network Errors** — Detect backend offline
3. **HTTP Status Codes** — Map to error types
4. **Retry Logic** — Exponential backoff

### User Feedback
1. **Error Messages** — Clear, actionable text
2. **Status Indicators** — Visual feedback
3. **Disabled States** — Prevent invalid actions
4. **Loading States** — Clear async progress

## Performance Considerations

### Bundle Size
- React + ReactDOM: ~40KB gzipped
- Axios: ~10KB gzipped
- App code: ~30KB gzipped
- **Total: ~80KB gzipped**

### Render Performance
- useCallback hooks prevent unnecessary renders
- useMemo for computed values
- No re-renders during polling (smart updates)

### Network Performance
- Single concurrent poll (Promise.all)
- Retry backoff prevents hammering
- Request timeout prevents hanging
- Conditional re-fetch on critical errors

## Security Considerations

### Input Validation
- Client-side validation (UX feedback)
- Server-side validation (security)
- Numeric only servo angles
- Range checks per servo

### API Communication
- HTTPS required in production
- CORS configured on backend
- No sensitive data in frontend
- Logs don't contain secrets

### Error Exposure
- Production: Minimal error details
- Development: Full error information
- Console logs only in DEV mode

## Testing Strategy

### Unit Tests (Ready to implement)
- Validation functions
- Error normalization
- State transitions

### Integration Tests (Ready to implement)
- Mock API responses
- Dashboard state management
- Component interactions

### E2E Tests (Ready to implement)
- Full user workflows
- Real backend integration
- Hardware simulation

## Deployment Options

### Static Hosting (Vercel, Netlify)
```bash
npm run build
# Deploy dist/ folder
```

### Docker Container
```dockerfile
FROM node:18
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build
EXPOSE 3000
CMD ["npm", "run", "preview"]
```

### Traditional Server (Nginx + Node)
```bash
npm run build
# Serve dist/ via Nginx
# Proxy /api to backend
```

## Monitoring & Observability

### Browser Console Logs
- App startup logged
- API calls tracked
- Errors logged with context
- Performance metrics available

### Error Tracking (Ready to integrate)
- Sentry/Rollbar integration
- Error boundary sends errors
- API errors logged
- Unhandled rejections tracked

### Performance Monitoring (Ready to integrate)
- Core Web Vitals
- API response times
- Render times
- User interaction latency

## Maintenance Guidelines

### Adding New Features
1. Create component in `src/components/`
2. Add API call to `src/api/robotApi.js`
3. Integrate into Dashboard
4. Add JSDoc comments
5. Test error scenarios
6. Update README

### Debugging Production Issues
1. Check browser console logs
2. Review API response format
3. Verify backend health endpoint
4. Check network tab for failures
5. Review server logs
6. Check for timeout errors

### Dependency Updates
1. Test locally before updating
2. Check for breaking changes
3. Verify bundle size
4. Test with real hardware
5. Update package-lock.json

## Future Enhancements

### Potential Improvements (Not in Scope)
- Real-time WebSocket updates
- Advanced telemetry visualization
- Command history/replay
- Motion recording
- Offline mode with queue persistence
- Multi-user support
- Advanced error recovery

### Note
These are for future phases. Keep current implementation simple and focused on demo reliability.

---

**Document Version:** 1.0.0  
**Last Updated:** May 14, 2026  
**Status:** Production Ready
