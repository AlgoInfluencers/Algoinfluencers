# AlgoInfluencers - Network Error Debugging Guide

## Problem Summary
The frontend was receiving an `AxiosError: Network Error` when trying to connect to the backend API endpoints.

## Root Causes Fixed

### 1. **Hardcoded API URLs**
   - **Issue**: Backend URL was hardcoded as `http://localhost:8000/` in each component
   - **Risk**: Fails if frontend is accessed from a different hostname or the API URL changes
   - **Fix**: Created centralized API configuration in `src/lib/api.ts` with environment variable support

### 2. **Missing Environment Configuration**
   - **Issue**: No environment file to manage API base URL
   - **Fix**: Created `.env.local` with `NEXT_PUBLIC_API_BASE_URL=http://localhost:8000`

### 3. **Lack of API Client Abstraction**
   - **Issue**: Each component independently imported and configured Axios
   - **Fix**: Centralized Axios configuration in `src/lib/api.ts` with typed API methods

## Changes Made

### Files Created:
- **`frontend/.env.local`** - Environment variables for development
- **`frontend/.env.example`** - Template for environment configuration
- **`frontend/src/lib/api.ts`** - Centralized API client with typed methods

### Files Modified:
- **`frontend/src/components/NetworkGraph.tsx`** - Now uses `api.network.getGraph()`
- **`frontend/src/components/SimulationPanel.tsx`** - Now uses `api.simulation.run()`
- **`frontend/src/components/ViralPrediction.tsx`** - Now uses `api.predict.viralProbability()`

## Verification Checklist

### ✅ Backend Status
- [ ] Backend is running on `http://localhost:8000`
  ```bash
  cd backend
  python -m uvicorn app.main:app --reload
  ```

- [ ] CORS is configured for frontend
  - Allows: `http://localhost:3000`
  - Check: [backend/app/main.py](backend/app/main.py)

- [ ] Test health endpoint:
  ```bash
  curl http://localhost:8000/health
  # Expected: {"status": "ok", "service": "algoinfluencers-backend"}
  ```

### ✅ Frontend Configuration
- [ ] Environment file exists: `frontend/.env.local`
- [ ] Contains: `NEXT_PUBLIC_API_BASE_URL=http://localhost:8000`
- [ ] API module exists: `frontend/src/lib/api.ts`
- [ ] All components use centralized API client

### ✅ Frontend Startup
- [ ] Dependencies installed:
  ```bash
  cd frontend
  npm install
  ```

- [ ] Development server running:
  ```bash
  npm run dev
  # Expected: Available at http://localhost:3000
  ```

- [ ] No TypeScript errors in components

## Testing the Connection

### 1. Check Network Tab in Browser DevTools
- Open `http://localhost:3000` in browser
- Open DevTools (F12) → Network tab
- Look for API requests to `http://localhost:8000/api/*`
- Check response status (should be 200 OK)

### 2. Check Console for Errors
- In DevTools → Console tab
- Should NOT see `AxiosError: Network Error`
- API responses should be logged successfully

### 3. Manual API Test from Frontend
Run in browser DevTools Console:
```javascript
// Test network endpoint
const res = await fetch('http://localhost:8000/api/network/');
const data = await res.json();
console.log(data);
```

## Configuration Management

### Development (.env.local)
```
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000
```

### Production (.env.production)
```
NEXT_PUBLIC_API_BASE_URL=https://api.algoinfluencers.com
```

### Docker/Remote Deployment
```
# If backend runs on different host
NEXT_PUBLIC_API_BASE_URL=http://backend-service:8000
```

## Common Issues & Solutions

### Issue: Still getting "Network Error"
1. **Check backend is running**: `curl http://localhost:8000/health`
2. **Verify CORS origin matches**: Frontend must be on `localhost:3000`
3. **Check firewall**: Port 8000 should be accessible from port 3000
4. **Restart services**: Kill and restart both backend and frontend

### Issue: Requests to wrong URL
1. **Clear Next.js cache**: `rm -rf .next`
2. **Reinstall modules**: `rm -rf node_modules && npm install`
3. **Check environment file**: Verify `.env.local` has correct URL

### Issue: CORS errors in console
- Error message: "Access to XMLHttpRequest has been blocked by CORS policy"
- Solution: Backend CORS middleware needs `http://localhost:3000` in allowed origins
- Check: [backend/app/main.py](backend/app/main.py) line 13-16

## API Endpoints Reference

All endpoints now used through typed `api` object in `src/lib/api.ts`:

```typescript
// Network data
api.network.getGraph()          // GET /api/network/
api.network.getInfluencers()    // GET /api/network/influencers
api.network.getStats()          // GET /api/network/stats

// Simulations
api.simulation.run({ ... })     // POST /api/simulation/run

// Predictions
api.predict.viralProbability({ ... })  // POST /api/predict/
```

## Next Steps

1. **Restart frontend**: `npm run dev`
2. **Monitor backend logs**: Watch for requests from `127.0.0.1:3000`
3. **Test each feature**: Network graph, simulation, prediction
4. **Check browser DevTools**: Verify requests and responses

## Support

If issues persist:
1. Provide DevTools Network tab screenshot
2. Show browser console error message
3. Check backend logs for crash or error messages
