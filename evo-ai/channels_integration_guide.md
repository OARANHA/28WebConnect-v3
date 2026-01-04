# Channels Integration Guide

## Overview
This guide explains how the Channels page integrates with Evolution API for WhatsApp instance management.

## Architecture

```
Frontend (Next.js) → Backend (FastAPI) → Evolution API
```

### Components:
1. **Frontend**: `evo-ai_tmp_clone/frontend/app/channels/page.tsx`
2. **Backend API**: `evo-ai_tmp_clone/src/api/channels_routes.py`
3. **Evolution Service**: `evo-ai_tmp_clone/src/services/evolution_api_service.py`
4. **Settings**: `evo-ai_tmp_clone/src/config/settings.py`

## Configuration

### Environment Variables (.env)
```bash
# Evolution API Configuration
EVOLUTION_API_BASE_URL=http://evolution-api:8080
EVOLUTION_API_APIKEY=gAAAAABpWHLgMPpcz6vQaYxXh_dpmh2OPlRjNSDlZpXF_0gSFjooz89o6SKs6crE2B0t8FvBPbsVzv8UCaI0-C4nFInZFtwTdw
```

### Docker Compose Services
- **evoai-backend**: Port 8000 - Main backend
- **evolution-api**: Port 8080 - WhatsApp gateway
- **evoai-frontend**: Port 8002 - Web interface

## API Endpoints

### Channels API (Backend)

| Method | Endpoint | Description |
|---------|-----------|-------------|
| GET | `/api/v1/channels/` | List all instances |
| POST | `/api/v1/channels/` | Create new instance |
| POST | `/api/v1/channels/{instance}/connect` | Connect instance (get QR) |
| GET | `/api/v1/channels/{instance}/state` | Get connection state |
| GET | `/api/v1/channels/{instance}/qr` | Get QR code |
| DELETE | `/api/v1/channels/{instance}/logout` | Logout instance |
| DELETE | `/api/v1/channels/{instance}` | Delete instance (Admin only) |
| POST | `/api/v1/channels/{instance}/bot` | Link EvoAI bot |

### Evolution API Endpoints

| Method | Endpoint | Description |
|---------|-----------|-------------|
| POST | `/instance/create` | Create new instance |
| GET | `/instance/fetchInstances` | List all instances |
| GET | `/instance/connect/{instance}` | Connect and get QR code |
| GET | `/instance/connectionState/{instance}` | Get connection state |
| DELETE | `/instance/logout/{instance}` | Logout instance |
| DELETE | `/instance/delete/{instance}` | Delete instance |

## Channel Creation Request Schema

```typescript
interface ChannelCreateRequest {
  instanceName: string;           // Required: Instance name
  qrcode?: boolean;               // Optional: Generate QR code (default: true)
  integration?: string;             // Optional: Integration type (default: WHATSAPP-BAILEYS)
  token?: string;                  // Optional: Instance token
  number?: string;                 // Optional: Phone number
  
  // Optional Settings
  rejectCall?: boolean;
  msgCall?: string;
  groupsIgnore?: boolean;
  alwaysOnline?: boolean;
  readMessages?: boolean;
  readStatus?: boolean;
  syncFullHistory?: boolean;
  
  // Optional Webhook
  webhook?: {
    url: string;
    byEvents?: boolean;
    base64?: boolean;
    headers?: Record<string, string>;
    events?: string[];
  };
  
  // Optional Proxy
  proxyHost?: string;
  proxyPort?: string;
  proxyProtocol?: string;
  proxyUsername?: string;
  proxyPassword?: string;
}
```

## Channel Response Schema

```typescript
interface Channel {
  id: string;
  name: string;
  type: string;                    // "whatsapp", "instagram", "email", "sms"
  description?: string;
  status: string;                   // "connected", "disconnected", "connecting"
  phoneNumber?: string;
  messagesToday?: number;
}
```

## Connection States

| State | Description |
|--------|-------------|
| `open` | Instance is connected and ready |
| `connecting` | Instance is connecting |
| `close` | Instance is disconnected |
| `refused` | Connection refused |

## Troubleshooting

### 404 Errors on `/api/v1/channels`
**Cause**: Channels router not properly registered in main.py

**Solution**: Ensure router is included:
```python
# In src/main.py
app.include_router(src.api.channels_routes.router)
```

### Evolution API Connection Errors
**Cause**: Wrong base URL or API key

**Solution**: Check environment variables:
```bash
# Verify Evolution API is running
curl http://localhost:8080/

# Verify API key
curl -H "apikey: YOUR_KEY" http://localhost:8080/instance/fetchInstances
```

### QR Code Not Showing
**Cause**: Instance not yet connected

**Solution**: Call `/connect` endpoint first:
```typescript
await api.post(`/api/v1/channels/${instance}/connect`);
```

## Security

### Admin-Only Operations
Delete instance operation is restricted to admin users only. The backend checks user role before allowing deletion.

### Authentication
- Frontend uses JWT token from cookies
- Backend validates token via `get_jwt_token` middleware
- Evolution API uses `apikey` header

## Next Steps

1. Restart services after configuration changes:
   ```bash
   docker-compose restart evoai-backend evolution-api
   ```

2. Test instance creation:
   ```bash
   curl -X POST http://localhost:8000/api/v1/channels \
     -H "Authorization: Bearer YOUR_TOKEN" \
     -H "Content-Type: application/json" \
     -d '{"instanceName": "test-instance", "integration": "WHATSAPP-BAILEYS"}'
   ```

3. Monitor logs:
   ```bash
   docker-compose logs -f evoai-backend
   docker-compose logs -f evolution-api
   ```
