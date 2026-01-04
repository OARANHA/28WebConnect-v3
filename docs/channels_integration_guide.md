# Evo AI Channels Integration Guide (Evolution API v2.3)

This document explains how the Channels feature in Evo AI integrates with Evolution API, the end-to-end flow, configuration, endpoints, frontend UX, and troubleshooting. It consolidates the final working solution adopted by the team.

## Overview

- Frontend calls only Evo AI (FastAPI) endpoints under `/api/v1/channels`.
- Evo AI acts as a secure proxy/adapter to Evolution API (server-to-server).
- Evolution API key is never exposed to the browser.
- Channel creation in Evo AI provisions the corresponding instance in Evolution API.
- Connect returns QR/pairing data so the operator can scan and finalize the session.
- Optional: link an EvoAI bot to the Evolution instance after connection.

## Architecture

- Frontend (Next.js 15) → Evo AI Backend (FastAPI) → Evolution API
- Secure: Evolution API credentials are only used on the server side.
- Resilient: Backend has retry/backoff for critical requests and consistent error handling.

## Configuration

Backend (container/env):
- `EVOLUTION_API_BASE_URL` (recommended: `http://evolution-api:8080` when using docker compose)
- `EVOLUTION_API_APIKEY` (Evolution API key)
- `APP_URL` (e.g., `http://localhost:8000`) – used to construct EvoAI bot callback URLs when linking bots

Note:
- Do NOT use `http://localhost:8080` for the backend-to-Evolution connection in docker; use the docker service name: `http://evolution-api:8080`.

Frontend:
- `NEXT_PUBLIC_API_BASE_URL` pointing to Evo AI backend (e.g., `http://localhost:8000/api/v1`).

## Backend Endpoints (Evo AI)

All routes are registered under `/api/v1/channels`. To avoid 404s with `redirect_slashes=False`, the collection endpoints accept both with and without trailing slash.

- `GET /api/v1/channels` and `GET /api/v1/channels/` – list channels (fetch instances from Evolution API)
- `POST /api/v1/channels` and `POST /api/v1/channels/` – create channel (provisions Evolution API instance)
  - Body schema (Pydantic `ChannelCreateRequest`) aligned with Evolution API v2.3. Typical fields:
    - `instanceName: string` (required)
    - `integration: string` (e.g., `WHATSAPP_BAILEYS`) – optional depending on setup
    - `qrcode: boolean` – suggests QR session
- `POST /api/v1/channels/{instance}/connect` – start/connect an instance (Evolution API connect)
- `GET /api/v1/channels/{instance}/state` – connection state (Evolution API connectionState)
- `GET /api/v1/channels/{instance}/qr` – helper that normalizes `{ qrcode, pairingCode, ref }` if available
- `DELETE /api/v1/channels/{instance}/logout` – logout instance
- `DELETE /api/v1/channels/{instance}` – delete instance
- `POST /api/v1/channels/{instance}/bot` – link EvoAI bot in Evolution API for this instance

Implementation details:
- EvolutionApiService encapsulates HTTP calls with headers `{ apikey: EVOLUTION_API_APIKEY }` and timeouts.
- Endpoints use path parameters per Evolution API v2.3:
  - `/instance/connect/{instance}`
  - `/instance/connectionState/{instance}`
  - `/instance/logout/{instance}`
  - `/instance/delete/{instance}`
- Retry/backoff enabled for critical requests (3 attempts with small backoff).
- Audit logs are created for `list`, `create`, `connect`, `state`, `qr`, `logout`, `delete`, `bot_linked` actions with minimal non-sensitive details.

## Frontend UX (/channels)

- List of instances (channels). Empty state shows "Add new channel" without red error toasts.
- Create channel dialog – collects `instanceName` (and optional fields as needed).
- Connect opens a QR modal that shows:
  - QR image (base64/data URL)
  - Pairing code and ref when available
  - Live status (connected, connecting, awaiting QR, closed, unknown)
  - "Regenerate QR" (calls connect again)
  - "Link Bot" action (manual trigger) – available in modal and when connected
- Auto-link EvoAI bot when state becomes `connected` (also available as manual button in the card).
- Status badges/labels use normalized mapping from Evolution API response.
- Robust to varying payload shapes (accepts qrcode/qr/base64/image; pairingCode/pairing_code; ref/reference; status/state/message).

## Security

- JWT required for all `/channels` routes on Evo AI.
- Evolution API key is server-only and injected in requests by the backend service.
- Errors from Evolution API are logged server-side and surfaced to the client with appropriate HTTP codes.

## Troubleshooting

- 404 on `/api/v1/channels`:
  - Cause: router not registered or trailing slash issue with `redirect_slashes=False`.
  - Fix: ensure router imported and included; accept both `"/"` and `""` in collection routes or enable `redirect_slashes=True`.
- 401/403 when calling Evolution API:
  - Check `EVOLUTION_API_APIKEY` and `EVOLUTION_API_BASE_URL`.
- Timeout/connection error to Evolution API:
  - Use `http://evolution-api:8080` inside docker. Confirm service is healthy.
- QR not shown:
  - Check `/channels/{instance}/state` and `/channels/{instance}/qr` – see if the Evolution API is returning QR/pairing fields; verify integration and instance status.

## Validation Steps

1) From Evo AI container, validate Evolution API connectivity:
   ```bash
   docker compose exec evoai-backend sh -lc 'curl -s -H "apikey: $AUTHENTICATION_API_KEY" "$EVOLUTION_API_BASE_URL/instance/fetchInstances"'
   ```
   Expect JSON (empty array on fresh install).

2) UI workflow (/channels):
   - Create channel (instance).
   - Connect → QR modal shows QR/pairing/ref.
   - Scan QR and wait for `connected`.
   - Link Bot (auto and/or manual).
   - Logout/Delete as needed.

## References

- Evolution-API v2.3 Postman collection: see `Evolution-API-v2.3.-.postman_collection.json` in the repo root.
- Evo AI services: `src/services/evolution_api_service.py`, `src/api/channels_routes.py`.
- Frontend: `frontend/app/channels/page.tsx`, `frontend/services/channelService.ts`, `frontend/lib/env.ts`.

## Notes for Developers

- Keep backend as the single integration layer with Evolution API to avoid leaking secrets.
- When adding new operations, mirror Evolution API v2.3 path/params and normalize outputs for the frontend.
- Prefer explicit router registration in `src/main.py` and centralize API versioning with `API_PREFIX`.
- Consider adding Playwright/E2E tests for the Channels flow (create → connect/QR → connected → link bot → logout/delete).
