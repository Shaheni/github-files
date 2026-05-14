# Robot Arm Control Frontend

Production-grade React + Vite frontend for controlling USB-tethered robot arm via Flask backend.

## Features

- **Real-time servo control** with 6 independent servo sliders
- **Live status monitoring** of robot execution state and queue
- **Backend health checks** with automatic offline detection
- **Emergency stop** always available
- **Input validation** before command submission
- **Error boundaries** for graceful error handling
- **Retry logic** with exponential backoff for reliability
- **Comprehensive logging** for production debugging
- **Accessibility** compliant UI with ARIA labels
- **Responsive design** for desktop and mobile

## Requirements

- Node.js >= 18.0.0
- npm or yarn
- Flask backend running on http://127.0.0.1:5050

## Installation

```bash
# Install dependencies
npm install
```

## Configuration

Create a `.env` file from `.env.example`:

```bash
cp .env.example .env
```

Update values as needed:

```env
VITE_BACKEND_URL=http://127.0.0.1:5050
VITE_REQUEST_TIMEOUT=10000
VITE_POLLING_INTERVAL=1000
VITE_MAX_RETRIES=2
```

## Development

Start development server:

```bash
npm run dev
```

Frontend will be available at `http://127.0.0.1:3000`

## Production Build

```bash
npm run build
```

Output will be in `dist/` directory. Deploy to any static hosting service.

## Production Deployment

### Local Testing

```bash
npm run build
npm run preview
```

### Docker Deployment

```dockerfile
FROM node:18-alpine AS builder
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

FROM node:18-alpine
WORKDIR /app
RUN npm install -g serve
COPY --from=builder /app/dist ./dist
EXPOSE 3000
CMD ["serve", "-s", "dist", "-l", "3000"]
```

### Nginx Configuration

```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        root /var/www/robot-control/dist;
        try_files $uri $uri/ /index.html;
    }

    location /api {
        proxy_pass http://127.0.0.1:5050;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

## Architecture

- `src/api/robotApi.js` — Centralized backend API client with retry logic
- `src/components/` — Reusable React UI components
- `src/pages/Dashboard.jsx` — Main control dashboard
- `src/constants/servoConfig.js` — Shared configuration constants
- `src/config/env.js` — Environment configuration loader
- `src/utils/logger.js` — Production logging utility
- `src/utils/validation.js` — Input validation utilities

## API Integration

Frontend communicates with backend via REST API:

- **POST /api/robot/command** — Send servo command
- **GET /api/robot/status** — Get robot motion status
- **GET /api/telemetry** — Get telemetry data
- **GET /api/health** — Check backend health
- **POST /api/robot/stop** — Emergency stop
- **POST /api/robot/reset** — Reset robot

All endpoints include automatic retry logic (exponential backoff) and comprehensive error handling.

## Key Features

### Error Handling

- Automatic retry with exponential backoff (100ms, 300ms, 900ms)
- Error boundary component catches React errors
- Normalized error types: `backend_offline`, `validation`, `queue_full`, `hardware`
- Detailed logging for debugging

### State Management

- Immediate data fetch on mount (no initial empty UI)
- Periodic polling every 1000ms for live updates
- Backend offline detection
- Poll error counting and warnings

### Validation

- Server-side and client-side servo angle validation
- Prevents invalid submissions
- Clear error messages
- Input sanitization

### Accessibility

- ARIA labels on all interactive elements
- Focus management
- Live regions for status updates
- Semantic HTML
- Keyboard navigation support

## Performance

- Lightweight (no heavy UI libraries)
- Minimal bundle size (< 150KB gzipped)
- Efficient re-renders using React hooks
- Request deduplication and caching ready

## Browser Support

- Chrome/Edge: Latest 2 versions
- Firefox: Latest 2 versions
- Safari: Latest 2 versions
- Mobile browsers: Latest versions

## Production Best Practices

1. **Environment Configuration** — Use `.env` for deployment-specific settings
2. **HTTPS** — Always use HTTPS in production
3. **CORS** — Configure backend CORS for your domain
4. **Rate Limiting** — Implement on backend if needed
5. **Monitoring** — Integrate with error tracking service
6. **Logging** — Send logs to centralized logging service
7. **Health Checks** — Regular backend availability monitoring

## Troubleshooting

### "Backend unavailable" error

1. Verify Flask backend is running: `python backend/app.py`
2. Check backend URL in `.env` matches actual backend address
3. Verify backend CORS settings allow frontend origin
4. Check firewall/network connectivity

### Servo command fails

1. Check Arduino is connected to laptop via USB
2. Verify serial port is correct in backend `settings.py`
3. Check servo angle values are within limits
4. Run backend tests: `python Test/test_robot_backend.py`

### Polling errors

1. Check network connectivity
2. Verify backend is responding to `/api/health`
3. Check browser console for detailed error logs

## Development Notes

- All API calls go through `src/api/robotApi.js` for consistency
- Error normalization happens in robotApi.js
- Logging statements help debug production issues
- Components are intentionally simple for maintainability

## License

MIT

## Contact

For issues or questions, contact the engineering team.

