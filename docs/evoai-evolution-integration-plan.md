# Evo-AI + Evolution-API Integration Automation Plan

## Overview

This document outlines the plan for automating the integration between Evo-AI agents and Evolution-API WhatsApp channels, eliminating the need for manual configuration.

---

## Problem Statement

Currently, when creating an Evo-AI agent with an external agent URL, users must manually:
1. Navigate to Evolution-API instance
2. Go to Integrations → EvoAI
3. Click "+ EvoAI"
4. Paste the Agent URL and API Key into a modal
5. Save the configuration

This manual process is error-prone and time-consuming, especially in multi-tenant environments.

---

## Evolution-API EvoAI Endpoints (from Postman Collection)

Based on the Evolution-API v2.3 Postman collection, the following EvoAI endpoints are available:

### 1. Create EvoAI Bot
```http
POST {{baseUrl}}/evoai/create/{{instance}}
```

**Request Body:**
```json
{
    "enabled": true,
    "apiUrl": "http://flowise.site.com/v1",
    "apiKey": "app-123456",
    "triggerType": "keyword",
    "triggerOperator": "equals",
    "triggerValue": "teste",
    "expire": 0,
    "keywordFinish": "#SAIR",
    "delayMessage": 1000,
    "unknownMessage": "Mensagem não reconhecida",
    "listeningFromMe": false,
    "stopBotFromMe": false,
    "keepOpen": false,
    "debounceTime": 0,
    "ignoreJids": []
}
```

### 2. Find EvoAI Bots
```http
GET {{baseUrl}}/evoai/find/{{instance}}
```

### 3. Fetch Specific EvoAI Bot
```http
GET {{baseUrl}}/evoai/fetch/:evoaiId/{{instance}}
```

### 4. Update EvoAI Bot
```http
PUT {{baseUrl}}/evoai/update/:evoaiId/{{instance}}
```

### 5. Delete EvoAI Bot
```http
DELETE {{baseUrl}}/evoai/delete/:evoaiId/{{instance}}
```

### 6. Session Management
- **Change Session Status:** `POST /evoai/changeStatus/{{instance}}`
- **Fetch Sessions:** `GET /evoai/fetchSessions/:evoaiId/{{instance}}`

### 7. Default Settings
- **Set Settings:** `POST /evoai/settings/{{instance}}`
- **Fetch Settings:** `GET /evoai/fetchSettings/{{instance}}`

---

## Current Evo-AI Implementation

### EvolutionApiService (evolution_api_service.py)

Currently has:
- `create_evoai_bot()` method for creating EvoAI integrations
- Instance management methods (create, connect, delete, etc.)
- Basic channel management capabilities

### Agent Model (models.py)

- Has `agent_card_url` property: `/api/v1/a2a/{id}/.well-known/agent.json`
- Has custom `agent_card_url` field for externally configured URLs
- Associated with `api_key_id` for authentication

### Channel Model (models.py)

- Links to `client_id` for multi-tenancy
- Has `instance_name` mapping to Evolution-API instances
- Has `config` JSON field for storing integration data
- Stores `channel_type` (whatsapp, instagram, email, sms)

---

## Proposed Architecture

```mermaid
flowchart TD
    A[User creates Agent in Evo-AI] --> B[Agent Saved with agent_card_url]
    B --> C[User creates Channel in Evo-AI]
    C --> D[Select Agent from dropdown]
    D --> E[Channel linked to Agent via external_agent_id]
    E --> F[Auto-call to Evolution-API]
    F --> G[POST /evoai/create/{{instance}}]
    G --> H[EvoAI bot configured in Evolution-API]
    H --> I[Messages flow through Evolution-API]
    I --> J[EvoAI endpoint receives messages]
    J --> K[Agent processes and responds]
    K --> L[Response sent back via Evolution-API]
```

---

## Implementation Plan

### Phase 1: Database Changes

#### 1.1 Add Agent Reference to Channel Model

```python
# evo-ai/src/models/models.py

class Channel(Base):
    # ... existing fields ...
    
    # New field for linking to Evo-AI agent
    external_agent_id = Column(
        UUID(as_uuid=True),
        ForeignKey("agents.id", ondelete="SET NULL"),
        nullable=True
    )
    
    # Store EvoAI bot configuration
    evoai_config = Column(JSON, nullable=True)
    
    # Track integration status
    integration_status = Column(String, nullable=False, default="none")
    # Values: none, configured, active, error
```

#### 1.2 Create Migration

```bash
make alembic-revision message="Add agent integration to channels"
```

### Phase 2: Backend Service Enhancements

#### 2.1 Expand EvolutionApiService

```python
# evo-ai/src/services/evolution_api_service.py

class EvolutionApiService:
    # ... existing methods ...
    
    async def find_evoai_bots(self, instance_name: str) -> List[Dict[str, Any]]:
        """List all EvoAI bots configured for an instance"""
        url = f"{self.base_url}/chatbot/evoai/find"
        params = {"instanceName": instance_name}
        # ... implementation
    
    async def fetch_evoai_bot(self, instance_name: str, evoai_id: str) -> Dict[str, Any]:
        """Fetch specific EvoAI bot configuration"""
        url = f"{self.base_url}/chatbot/evoai/fetch/{evoai_id}"
        params = {"instanceName": instance_name}
        # ... implementation
    
    async def update_evoai_bot(
        self, 
        instance_name: str, 
        evoai_id: str, 
        agent_url: str, 
        api_key: str,
        enabled: bool = True
    ) -> Dict[str, Any]:
        """Update EvoAI bot configuration"""
        url = f"{self.base_url}/chatbot/evoai/update/{evoai_id}"
        params = {"instanceName": instance_name}
        body = {
            "enabled": enabled,
            "apiUrl": agent_url,
            "apiKey": api_key,
            # ... other fields
        }
        # ... implementation
    
    async def delete_evoai_bot(self, instance_name: str, evoai_id: str) -> Dict[str, Any]:
        """Delete EvoAI bot configuration"""
        url = f"{self.base_url}/chatbot/evoai/delete/{evoai_id}"
        params = {"instanceName": instance_name}
        # ... implementation
    
    async def configure_evoai_for_channel(
        self,
        instance_name: str,
        agent_url: str,
        api_key: str,
        config: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Automatically configure EvoAI bot when a channel is linked to an agent.
        This is the main automation method.
        """
        url = f"{self.base_url}/chatbot/evoai/create"
        params = {"instanceName": instance_name}
        
        default_config = {
            "enabled": True,
            "apiUrl": agent_url,
            "apiKey": api_key,
            "triggerType": "all",  # All messages trigger the bot
            "expire": 0,  # No session expiration
            "delayMessage": 1000,
            "unknownMessage": "Sorry, I didn't understand that.",
            "listeningFromMe": False,
            "stopBotFromMe": False,
            "keepOpen": False,
            "debounceTime": 0,
            "ignoreJids": []
        }
        
        if config:
            default_config.update(config)
        
        async def _req():
            async with httpx.AsyncClient(timeout=DEFAULT_TIMEOUT) as client:
                resp = await client.post(
                    url, 
                    headers=self._headers(), 
                    params=params, 
                    json=default_config
                )
                resp.raise_for_status()
                return resp.json()
        
        result = await self._with_retries(_req)
        
        # Store the EvoAI bot ID returned by Evolution-API
        return result
```

#### 2.2 Enhance Channel Service

```python
# evo-ai/src/services/channel_service.py

async def create_channel(
    db: Session,
    channel_data: ChannelCreate,
    current_user_role: str,
    client_id: Optional[UUID] = None
) -> Dict[str, Any]:
    """Create channel with automatic EvoAI integration"""
    
    # ... existing channel creation logic ...
    
    # Check if agent is linked
    if channel_data.external_agent_id:
        # Fetch agent details
        agent = db.query(Agent).filter(Agent.id == channel_data.external_agent_id).first()
        if not agent:
            raise HTTPException(status_code=404, detail="Agent not found")
        
        # Get agent's API key
        api_key = None
        if agent.api_key_id:
            key_obj = db.query(ApiKey).filter(ApiKey.id == agent.api_key_id).first()
            if key_obj:
                api_key = decrypt_key(key_obj.encrypted_key)
        
        # Get agent URL
        agent_url = agent.agent_card_url_property
        
        # Configure EvoAI in Evolution-API
        evolution_service = EvolutionApiService()
        evoai_result = await evolution_service.configure_evoai_for_channel(
            instance_name=new_channel.instance_name,
            agent_url=agent_url,
            api_key=api_key or "",
            config=channel_data.evoai_config
        )
        
        # Store EvoAI configuration in channel
        if evoai_result.get("success") or evoai_result.get("status") == "success":
            new_channel.evoai_config = {
                "bot_id": evoai_result.get("id") or evoai_result.get("data", {}).get("id"),
                "configured_at": datetime.utcnow().isoformat(),
                "agent_url": agent_url
            }
            new_channel.integration_status = "configured"
            db.commit()
        else:
            new_channel.integration_status = "error"
            new_channel.evoai_config = {
                "error": evoai_result.get("message", "Unknown error"),
                "attempted_at": datetime.utcnow().isoformat()
            }
            db.commit()
            # Log error for retry
    
    return channel_to_dict(new_channel)

async def update_channel_integration(
    db: Session,
    channel_id: UUID,
    agent_id: Optional[UUID] = None
) -> Dict[str, Any]:
    """Update channel's EvoAI integration"""
    
    channel = db.query(Channel).filter(Channel.id == channel_id).first()
    if not channel:
        raise HTTPException(status_code=404, detail="Channel not found")
    
    evolution_service = EvolutionApiService()
    
    # If linking to an agent
    if agent_id and agent_id != channel.external_agent_id:
        # Remove old bot if exists
        if channel.evoai_config and "bot_id" in channel.evoai_config:
            await evolution_service.delete_evoai_bot(
                instance_name=channel.instance_name,
                evoai_id=channel.evoai_config["bot_id"]
            )
        
        # Configure new bot
        agent = db.query(Agent).filter(Agent.id == agent_id).first()
        if agent:
            agent_url = agent.agent_card_url_property
            api_key = get_agent_api_key(db, agent)
            
            result = await evolution_service.configure_evoai_for_channel(
                instance_name=channel.instance_name,
                agent_url=agent_url,
                api_key=api_key
            )
            
            channel.external_agent_id = agent_id
            if result.get("success"):
                channel.evoai_config = {
                    "bot_id": result.get("id"),
                    "configured_at": datetime.utcnow().isoformat()
                }
                channel.integration_status = "configured"
            else:
                channel.integration_status = "error"
    
    # If unlinking agent
    elif not agent_id and channel.external_agent_id:
        # Delete EvoAI bot
        if channel.evoai_config and "bot_id" in channel.evoai_config:
            await evolution_service.delete_evoai_bot(
                instance_name=channel.instance_name,
                evoai_id=channel.evoai_config["bot_id"]
            )
        
        channel.external_agent_id = None
        channel.evoai_config = None
        channel.integration_status = "none"
    
    db.commit()
    return channel_to_dict(channel)
```

### Phase 3: API Routes

#### 3.1 Update Channel Routes

```python
# evo-ai/src/api/channels_routes.py

from src.schemas.schemas import ChannelCreate, ChannelUpdate

# Update ChannelCreate schema to include external_agent_id
@router.post("/channels/", response_model=ChannelResponse)
async def create_channel_endpoint(
    channel_data: ChannelCreate,
    current_user_role: str = Depends(get_user_role),
    client_id: Optional[str] = Depends(get_client_id),
    db: Session = Depends(get_db)
):
    """Create channel with automatic EvoAI integration"""
    if current_user_role != 'admin' and 'client_id' not in channel_data and client_id:
        channel_data.client_id = client_id
    
    result = await create_channel(db, channel_data, current_user_role, client_id)
    return result

@router.put("/channels/{channel_id}/integration", response_model=ChannelResponse)
async def update_channel_integration_endpoint(
    channel_id: str,
    agent_id: Optional[str] = None,
    current_user_role: str = Depends(get_user_role),
    client_id: Optional[str] = Depends(get_client_id),
    db: Session = Depends(get_db)
):
    """Update channel's EvoAI integration (link/unlink agent)"""
    channel_uuid = UUID(channel_id)
    agent_uuid = UUID(agent_id) if agent_id else None
    
    result = await update_channel_integration(db, channel_uuid, agent_uuid)
    return result

@router.get("/channels/{channel_id}/evoai-status", response_model=Dict[str, Any])
async def get_evoai_status_endpoint(
    channel_id: str,
    db: Session = Depends(get_db)
):
    """Get EvoAI integration status for a channel"""
    channel_uuid = UUID(channel_id)
    channel = db.query(Channel).filter(Channel.id == channel_uuid).first()
    if not channel:
        raise HTTPException(status_code=404, detail="Channel not found")
    
    # Check actual status in Evolution-API
    evolution_service = EvolutionApiService()
    bots = await evolution_service.find_evoai_bots(channel.instance_name)
    
    return {
        "channel_id": channel_id,
        "channel_name": channel.name,
        "instance_name": channel.instance_name,
        "local_status": channel.integration_status,
        "local_config": channel.evoai_config,
        "remote_bots": bots
    }

@router.post("/channels/{channel_id}/sync-evoai", response_model=Dict[str, Any])
async def sync_evoai_endpoint(
    channel_id: str,
    current_user_role: str = Depends(get_user_role),
    db: Session = Depends(get_db)
):
    """Manually sync EvoAI configuration for a channel"""
    channel_uuid = UUID(channel_id)
    channel = db.query(Channel).filter(Channel.id == channel_uuid).first()
    if not channel:
        raise HTTPException(status_code=404, detail="Channel not found")
    
    if not channel.external_agent_id:
        raise HTTPException(status_code=400, detail="No agent linked to this channel")
    
    # Sync with Evolution-API
    channel_service = ChannelService()
    result = await channel_service.sync_evoai_integration(db, channel_uuid)
    return result
```

### Phase 4: Frontend Updates

#### 4.1 Update Channel Creation Form

```typescript
// evo-ai/frontend/app/channels/page.tsx

interface ChannelFormData {
  name: string;
  instance_name: string;
  channel_type: 'whatsapp' | 'instagram' | 'email' | 'sms';
  client_id?: string;
  external_agent_id?: string;  // NEW: Link agent
  evoai_config?: Record<string, any>;
}

// Add agent selection dropdown
const [agents, setAgents] = useState<Agent[]>([]);
const [selectedAgent, setSelectedAgent] = useState<string | null>(null);

// Fetch agents for selection
useEffect(() => {
  fetchAgents();
}, []);

// In the channel creation form:
<Select
  value={formData.external_agent_id}
  onValueChange={(value) => setSelectedAgent(value)}
>
  <SelectTrigger>
    <SelectValue placeholder="Select an agent (optional)" />
  </SelectTrigger>
  <SelectContent>
    {agents.map((agent) => (
      <SelectItem key={agent.id} value={agent.id}>
        <div className="flex flex-col">
          <span className="font-medium">{agent.name}</span>
          <span className="text-xs text-muted-foreground">
            {agent.agent_card_url}
          </span>
        </div>
      </SelectItem>
    ))}
  </SelectContent>
</Select>

// When an agent is selected, show EvoAI configuration options
{selectedAgent && (
  <div className="space-y-4">
    <h3>EvoAI Integration</h3>
    <p className="text-sm text-muted-foreground">
      Agent URL: {getSelectedAgentUrl()}
    </p>
    <Checkbox
      checked={formData.evoai_config?.enabled}
      onCheckedChange={(checked) => setEvoaiConfig({...formData.evoai_config, enabled: checked})}
    >
      Enable EvoAI bot
    </Checkbox>
    {/* Additional EvoAI config options */}
  </div>
)}
```

#### 4.2 Channel List with Integration Status

```typescript
// Add integration status indicator to channel cards
<ChannelCard className="relative">
  <Badge 
    variant={channel.integration_status === 'configured' ? 'success' : 'destructive'}
    className="absolute top-2 right-2"
  >
    {channel.integration_status === 'configured' && 'EvoAI Active'}
    {channel.integration_status === 'error' && 'Integration Error'}
  </Badge>
  
  {/* Link/Unlink Agent Button */}
  <Button
    variant="outline"
    size="sm"
    onClick={() => handleAgentLink(channel)}
  >
    {channel.external_agent_id ? 'Unlink Agent' : 'Link Agent'}
  </Button>
</ChannelCard>
```

### Phase 5: Webhook Handling

#### 5.1 EvoAI Response Handler

```python
# evo-ai/src/api/evoai_webhook_routes.py

from fastapi import APIRouter, Request, BackgroundTasks
from src.services.evolution_api_service import EvolutionApiService

router = APIRouter(prefix="/evoai", tags=["EvoAI"])

@router.post("/webhook/{channel_id}")
async def evoai_webhook_handler(
    channel_id: str,
    request: Request,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """
    Handle EvoAI webhook responses from Evolution-API.
    When a message is received by EvoAI bot, it sends a response here.
    """
    channel_uuid = UUID(channel_id)
    channel = db.query(Channel).filter(Channel.id == channel_uuid).first()
    if not channel:
        return {"status": "error", "message": "Channel not found"}
    
    if not channel.external_agent_id:
        return {"status": "error", "message": "No agent linked"}
    
    # Parse webhook payload
    payload = await request.json()
    
    # Forward to EvoAI agent for processing
    evolution_service = EvolutionApiService()
    
    # Agent URL
    agent_url = channel.evoai_config.get("agent_url")
    
    # Send to EvoAI agent
    response = await evolution_service.send_to_evoai_agent(
        agent_url=agent_url,
        message=payload,
        agent_id=str(channel.external_agent_id)
    )
    
    # Evolution-API will send the response back to the user
    return {"status": "success", "processed": True}
```

### Phase 6: Session Management

#### 6.1 Track EvoAI Sessions

```python
# evo-ai/src/services/evoai_session_service.py

class EvoAISessionService:
    """Manage EvoAI bot sessions for conversations"""
    
    async def get_active_sessions(
        self, 
        channel_id: UUID, 
        remote_jid: str
    ) -> Optional[Dict[str, Any]]:
        """Get active session for a contact"""
        # Query Redis or database for active session
    
    async def create_session(
        self,
        channel_id: UUID,
        remote_jid: str,
        agent_id: UUID
    ) -> str:
        """Create new session and return session ID"""
        # Store session in Redis with TTL
        # Return session_id for tracking
    
    async def update_session_state(
        self,
        session_id: str,
        state: Dict[str, Any]
    ) -> None:
        """Update session state"""
        # Update state in Redis
    
    async def close_session(self, session_id: str) -> None:
        """Close active session"""
        # Mark session as closed
```

---

## Features Suggested

### 1. Automatic Integration on Channel Creation
- When creating a WhatsApp channel, automatically configure EvoAI bot if an agent is selected
- Store EvoAI bot ID and configuration in channel's `evoai_config` field
- Show integration status in channel list

### 2. Agent Linking/Unlinking
- Ability to link multiple agents to a channel with priority order
- Switch active agent without deleting old configuration
- Unlink agent and remove EvoAI bot from Evolution-API

### 3. Integration Status Monitoring
- Real-time status check of EvoAI bots
- Automatic retry on failed configurations
- Health checks for active integrations

### 4. Session Management
- Track conversation sessions per contact
- Session expiration and cleanup
- Handoff to human support when needed

### 5. Message Flow Tracking
- Log all messages sent through EvoAI integration
- Response time monitoring
- Error tracking and alerting

### 6. Advanced Configuration
- Trigger type configuration (all messages, keyword-based, regex)
- Session timeout settings
- Custom unknown message responses
- Language-specific configurations

### 7. Webhook Retry Logic
- Automatic retry on webhook failures
- Queue system for high volume
- Dead letter queue for failed messages

### 8. Multi-Agent Support
- Load balance across multiple agents
- Agent selection based on intent detection
- Failover between agents

---

## Security Considerations

1. **API Key Encryption**: Store EvoAI API keys encrypted in database
2. **Permission Checks**: Only channel owners can modify integrations
3. **Webhook Validation**: Validate webhook signatures from Evolution-API
4. **Rate Limiting**: Prevent abuse of webhook endpoints
5. **Audit Logging**: Log all integration configuration changes

---

## Testing Strategy

### Unit Tests
- Test EvolutionApiService methods
- Test channel creation with agent linking
- Test webhook handler
- Test session management

### Integration Tests
- Test full flow: create agent → create channel → verify EvoAI bot
- Test message flow: send message → EvoAI processes → response
- Test error scenarios: invalid agent, connection failures

### End-to-End Tests
- Create agent and channel in UI
- Send WhatsApp message through Evolution-API
- Verify EvoAI response
- Check session tracking

---

## Migration Plan

### Step 1: Database Schema Update
```bash
# Create migration for new fields
alembic revision --autogenerate -m "Add agent integration to channels"

# Apply migration
alembic upgrade head
```

### Step 2: Backend Implementation
1. Update EvolutionApiService with new methods
2. Enhance ChannelService with integration logic
3. Add new routes for integration management
4. Create webhook handler for EvoAI responses

### Step 3: Frontend Updates
1. Add agent selection to channel creation form
2. Add integration status indicators to channel list
3. Add integration configuration modal
4. Add agent linking/unlinking actions

### Step 4: Testing
1. Run unit tests
2. Run integration tests
3. Perform manual testing in staging
4. Deploy to production and monitor

---

## Success Criteria

- [ ] Users can select an agent when creating a channel
- [ ] EvoAI bot is automatically configured in Evolution-API
- [ ] Integration status is visible in the UI
- [ ] Messages flow correctly through the integration
- [ ] Sessions are tracked and managed
- [ ] Errors are handled gracefully with retry logic
- [ ] Audit logs track all configuration changes
- [ ] Multi-tenant isolation is maintained

---

## Appendix: Evolution-API URL Pattern

Based on the Postman collection, the EvoAI endpoints use the following pattern:

```
{{baseUrl}}/evoai/{{action}}/{{instance}}
```

Where:
- `baseUrl`: Evolution-API base URL (e.g., http://localhost:8080)
- `action`: create, find, fetch, update, delete, changeStatus, settings
- `instance`: Instance name (channel.instance_name)

For create with instance context:
```
{{baseUrl}}/evoai/create?instanceName={{instance}}
```

Or using path parameter:
```
{{baseUrl}}/evoai/create/{{instance}}
```

---

**Document Version:** 1.0  
**Created:** 2026-01-04  
**Author:** Architecture Team
