# Frontend Development Guide

## Getting Started

### Prerequisites
- Node.js >= 18.0.0
- npm or yarn
- Git
- Code editor (VS Code recommended)
- Flask backend running locally

### Initial Setup

```bash
# Clone repository
git clone <repo-url>
cd client

# Install dependencies
npm install

# Create environment file
cp .env.example .env

# Start development server
npm run dev
```

Visit `http://127.0.0.1:3000` in browser.

## Project Structure

```
client/
├── src/
│   ├── api/                    # Backend communication
│   │   └── robotApi.js         # All API calls, retry logic
│   ├── components/             # Reusable UI components
│   │   ├── ErrorBoundary.jsx
│   │   ├── ServoControls.jsx
│   │   ├── StatusPanel.jsx
│   │   ├── TelemetryPanel.jsx
│   │   ├── ConnectionStatus.jsx
│   │   └── EmergencyControls.jsx
│   ├── config/                 # Configuration
│   │   └── env.js
│   ├── constants/              # Constants and defaults
│   │   └── servoConfig.js
│   ├── pages/                  # Page components
│   │   └── Dashboard.jsx
│   ├── styles/                 # CSS styles
│   │   └── dashboard.css
│   ├── utils/                  # Utilities
│   │   ├── logger.js
│   │   └── validation.js
│   ├── App.jsx                 # Root component
│   └── main.jsx                # Entry point
├── index.html                  # HTML template
├── vite.config.js              # Vite configuration
├── package.json                # Dependencies
├── .env.example                # Environment template
├── .gitignore
├── README.md                   # User guide
├── FRONTEND_ARCHITECTURE.md    # Technical architecture
├── DEVELOPMENT_GUIDE.md        # This file
└── PRODUCTION_CHECKLIST.md     # Deployment checklist
```

## Development Workflow

### 1. Make Code Changes

Example: Modify ServoControls.jsx

```jsx
// Add new feature to component
export default function ServoControls({ ... }) {
  // Your code here
}
```

### 2. Test Locally

```bash
# Dev server automatically reloads changes
npm run dev

# Or run production build to test
npm run build
npm run preview
```

### 3. Verify API Integration

```bash
# Check backend is running
curl http://127.0.0.1:5050/api/health

# Monitor network requests in browser DevTools
# Check console for logged operations
```

### 4. Test Error Scenarios

```bash
# Stop backend to test offline detection
# Disconnect Arduino to test hardware error
# Send invalid servo values to test validation
# Inspect error handling and UI responses
```

### 5. Commit Changes

```bash
git add .
git commit -m "feat: descriptive commit message"
git push origin branch-name
```

## Common Tasks

### Adding a New Component

1. Create file in `src/components/MyComponent.jsx`
2. Add JSDoc comments
3. Import and use in Dashboard or parent component
4. Test integration with backend
5. Update README if user-facing

Example:
```jsx
/**
 * MyComponent - Brief description
 * Longer description of what it does
 */

export default function MyComponent({ prop1, prop2 }) {
  return (
    <div>
      {/* Your JSX */}
    </div>
  );
}
```

### Modifying API Calls

Edit `src/api/robotApi.js`:

```javascript
/**
 * New API function
 * @param {Object} params - parameters
 * @returns {Promise<Object>} response
 */
export async function newApiFunction(params) {
  try {
    const result = await withRetry(() =>
      apiClient.post('/api/new-endpoint', params)
    );
    logger.info('Operation successful', result.data);
    return { ...result.data, type: 'success' };
  } catch (err) {
    return normalizeError(err, 'newApiFunction');
  }
}
```

### Adding Configuration

1. Add to `.env.example`
2. Add to `src/config/env.js`
3. Use via `import { VAR_NAME } from '../config/env'`

### Adding Validation

Edit `src/utils/validation.js`:

```javascript
/**
 * Validate new input type
 * @param {any} value
 * @returns {Object} { isValid: boolean, error?: string }
 */
export function validateNewInput(value) {
  if (!value) {
    return { isValid: false, error: 'Value required' };
  }
  return { isValid: true };
}
```

### Styling Changes

Edit `src/styles/dashboard.css`:

```css
/* Follow existing patterns */
.new-component {
  padding: 12px;
  border: 1px solid #ddd;
  border-radius: 6px;
}

.new-component.active {
  background: #eef5ff;
  color: #0066cc;
}
```

## Debugging

### Browser DevTools

1. **Console Tab** — Check logs and errors
2. **Network Tab** — Monitor API calls
3. **React DevTools** — Inspect component state
4. **Performance Tab** — Check render times

### Common Issues

**"Backend unavailable" error**
```bash
# Check backend is running
curl http://127.0.0.1:5050/api/health

# Check .env VITE_BACKEND_URL is correct
cat .env
```

**Servo controls not working**
```javascript
// Check in browser console
// Look for validation errors
// Verify servo values in valid ranges
// Check API response in Network tab
```

**Polling not updating**
```javascript
// Check polling interval in .env
// Verify backend /api/telemetry endpoint
// Check for network errors in console
```

### Logging for Debugging

```javascript
import { logger } from '../utils/logger';

// Debug logs only show in dev mode
logger.debug('Debug info', { data: value });

// Info logs always show
logger.info('Operation complete', { result: data });

// Warnings and errors always show
logger.warn('Potential issue', { status: state });
logger.error('Operation failed', { error: err.message });
```

## Code Style Guidelines

### JSDoc Comments
```javascript
/**
 * Brief function description
 * 
 * @param {type} paramName - description
 * @returns {type} description
 */
```

### Component Structure
```jsx
/**
 * ComponentName - Brief description
 * Detailed description
 */

import React, { useState, useCallback } from 'react';
// imports

/**
 * ComponentName Component
 * @param {Object} props - component props
 */
export default function ComponentName({ prop1, prop2 }) {
  const [state, setState] = useState(initialValue);

  const handleEvent = useCallback((arg) => {
    // handler logic
  }, [dependencies]);

  return (
    // JSX
  );
}
```

### Naming Conventions
- Components: PascalCase (ServoControls.jsx)
- Functions: camelCase (handleSubmit, fetchData)
- Constants: UPPER_SNAKE_CASE (MAX_QUEUE_SIZE)
- Files: match export name
- CSS classes: kebab-case (.servo-controls)

## Testing

### Manual Testing Checklist

- [ ] Component renders without errors
- [ ] All user interactions work
- [ ] Form validation works
- [ ] API integration works
- [ ] Error states handled correctly
- [ ] Loading states visible
- [ ] Mobile responsive
- [ ] Keyboard navigation works
- [ ] No console errors

### Testing Different Scenarios

```bash
# Backend offline
# 1. Stop Flask server
# 2. Try to submit command
# 3. Verify error message shows
# 4. Verify "Backend Offline" indicator

# Hardware disconnected
# 1. Disconnect Arduino
# 2. Send command
# 3. Verify timeout error
# 4. Verify retry logic

# Invalid servo values
# 1. Enter value > max range
# 2. Verify validation error
# 3. Try to submit (should fail)
# 4. Fix value and resubmit
```

## Performance Tips

### React Performance
- Use useCallback for callbacks
- Use useMemo for expensive computations
- Avoid creating objects/arrays in render
- Use proper dependencies arrays

### Network Performance
- Check bundle size: `npm run build`
- Monitor API response times
- Use browser DevTools Performance tab
- Check for unnecessary re-renders

### Development Performance
- Dev server hot reload is fast
- Check build time regularly
- Profile with Vite analyzer if needed

## Git Workflow

### Branch Naming
- `feature/description` — New features
- `fix/description` — Bug fixes
- `docs/description` — Documentation
- `refactor/description` — Code improvements

### Commit Messages
```bash
git commit -m "feat: add servo range validation"
git commit -m "fix: prevent double command submission"
git commit -m "docs: update API documentation"
git commit -m "refactor: simplify error handling"
```

### Creating Pull Requests
1. Create feature branch
2. Make changes with descriptive commits
3. Push to GitHub
4. Create PR with description
5. Link related issues
6. Request review
7. Address feedback
8. Merge when approved

## Helpful Resources

- [React Documentation](https://react.dev)
- [Vite Guide](https://vitejs.dev/guide/)
- [Axios Documentation](https://axios-http.com/)
- [MDN Web Docs](https://developer.mozilla.org/)
- [Web Accessibility](https://www.a11y-101.com/)

## Troubleshooting Development

### npm install fails
```bash
# Clear cache and reinstall
npm cache clean --force
rm -rf node_modules package-lock.json
npm install
```

### Port 3000 already in use
```bash
# Use different port
npx vite --port 3001
```

### Backend connection issues
```bash
# Verify backend running
ps aux | grep flask

# Check backend logs
tail -f backend.log

# Test backend endpoint
curl -v http://127.0.0.1:5050/api/health
```

### Hot reload not working
```bash
# Restart dev server
# Clear browser cache
# Check vite.config.js

# Manual reload
Ctrl+Shift+R (hard refresh)
```

## Getting Help

1. Check console logs (F12)
2. Review FRONTEND_ARCHITECTURE.md
3. Search similar issues in git history
4. Check backend logs for API errors
5. Ask team members for pairing

## Best Practices

✅ **DO:**
- Write clean, simple code
- Add JSDoc comments
- Handle errors gracefully
- Log important operations
- Test before committing
- Keep components small
- Use constants for magic numbers
- Validate all inputs

❌ **DON'T:**
- Hardcode values
- Ignore errors
- Create massive components
- Skip validation
- Use inline callbacks in JSX
- Add console.log and leave it
- Over-engineer solutions
- Skip testing

---

**Happy coding!** 🚀

For questions, check FRONTEND_ARCHITECTURE.md or reach out to the team.
