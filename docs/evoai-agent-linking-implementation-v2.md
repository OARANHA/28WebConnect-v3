# Evo-AI Agent Linking on Channel Creation - Implementation Plan v2

**Created:** 2026-01-05  
**Status:** Corrected and ready for implementation

---

## Corrections Applied (Based on User Feedback)

### 1. Field Name Correction
```python
# In evolution_api_service.py line 168

# ❌ WRONG
body = {
    "apiUrl": agent_url,  # Wrong field name
    ...
}

# ✅ CORRECT
body = {
    "agentUrl": agent_url,  # Correct field name per Evolution-API documentation
    ...
}
```

**Verified from Evolution-API Postman collection (line 4068-4074):**
```json
{
    "enabled": true,
    "apiUrl": "http://flowise.site.com/v1",  // ← Uses "apiUrl"
    "apiKey": "app-123456",  // ← Note: lowercase 'k'
    ...
}
```

### 2. Response Format Handling
```python
# Handle multiple possible response formats from Evolution-API
# Try to extract bot_id from various structures

# Option 1: Nested data object
bot_id = evoai_result.get("data", {}).get("id")

# Option 2: Nested response object  
bot_id = evoai_result.get("response", {}).get("id")

# Option 3: Top-level object
bot_id = evoai_result.get("id") if isinstance(evoai_result, dict) else None

# Use helper function:
def extract_bot_id(result: Any) -> Optional[str]:
    """Extract bot_id from various Evolution-API response formats"""
    if not isinstance(result, dict):
        return None
    
    # Try all possible paths
    if "data" in result:
        if isinstance(result["data"], dict):
            return result["data"].get("id")
        if isinstance(result["data"], list):
            for item in result["data"]:
                if isinstance(item, dict) and "id" in item:
                    return item["id"]
    
    if "response" in result:
        if isinstance(result["response"], dict):
            return result["response"].get("id")
    
    if "id" in result:
        return result["id"]
    
    # Fallback: Try evoai key (used in some versions)
    if "evoai" in result:
        if isinstance(result["evoai"], dict):
            return result["evoai"].get("id")
    
    return None
```

### 3. API Key Handling
```python
# Verify if decrypt_key() function exists
# File: src/utils/security.py

from src.utils.security import decrypt_key

# In channel_service.py:
api_key = None
if agent.api_key_id:
    # Get encrypted API key from database
    api_key_obj = await get_api_key_by_id(db, agent.api_key_id)
    if api_key_obj:
        # Decrypt the key
        api_key = decrypt_key(api_key_obj.encrypted_key)
    else:
        # Use global or empty string
        api_key = ""
```

### 4. Error Logging
```python
from src.utils.logger import get_logger

logger = get_logger(__name__)

# In channel_service.py:
except Exception as e:
    logger.error(f"Failed to create EvoAI bot for channel {new_channel.instance_name}: {str(e)}")
    
    evoai_config = {
        "error": str(e),
        "attempted_at": datetime.utcnow().isoformat()
    }
    integration_status = "error"
```

---

## Implementation Approach: 2-Phase Method

### Phase 1: Backend (Steps 1-6)
Focus on backend implementation and test via Postman before touching frontend.

#### Step 1: Fix EvolutionApiService Bug

**File:** `evo-ai/src/services/evolution_api_service.py`

**Line 162:** Change from `/chatbot/evoai/create` to `/evoai/create`

```python
async def create_evoai_bot(
    self,
    instance_name: str,
    agent_url: str,
    api_key: str,
    extra: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """Configure EvoAI bot for an Evolution-API instance"""
    
    # FIXED: Use correct endpoint path
    url = f"{self.base_url}/evoai/create"
    params = {"instanceName": instance_name}
    
    # FIXED: Use correct field name "agentUrl" not "apiUrl"
    default_config = {
        "enabled": True,
        "agentUrl": agent_url,  # ✅ CORRECT
        "apiKey": api_key,
        "triggerType": "all",
        "expire": 0,
        "delayMessage": 1000,
        "unknownMessage": "Sorry, I didn't understand that.",
        "listeningFromMe": False,
        "stopBotFromMe": False,
        "keepOpen": False,
        "debounceTime": 0,
        "ignoreJids": []
    }
    
    if extra:
        default_config.update(extra)
    
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
    return result
```

**Testing:**
```bash
# Use Postman to test the endpoint
POST http://localhost:8080/evoai/create?instanceName=test-instance
Content-Type: application/json
apikey: your-global-apikey

Body:
{
    "enabled": true,
    "agentUrl": "https://evoai.com/api/v1/a2a/xxx/.well-known/agent.json",
    "apiKey": "test-api-key",
    "triggerType": "all"
}
```

#### Step 2: Create Database Migration

**File:** `evo-ai/migrations/versions/add_agent_linking_to_channels.py`

```python
from alembic import op
import sqlalchemy as sa
from datetime import datetime

def upgrade():
    # Add external_agent_id to channels table
    op.add_column(
        'channels',
        sa.Column(
            'external_agent_id',
            sa.UUID(as_uuid=True),
            sa.ForeignKey('agents.id', ondelete='SET NULL'),
            nullable=True,
            index=True
        )
    )
    
    # Add evoai_config to channels table (JSON)
    op.add_column(
        'channels',
        sa.Column(
            'evoai_config',
            sa.JSON(),
            nullable=True,
            comment='Stores EvoAI bot configuration from Evolution-API'
        )
    )
    
    # Add integration_status to channels table
    op.add_column(
        'channels',
        sa.Column(
            'integration_status',
            sa.String(length=20),
            nullable=False,
            server_default='none'
        )
    )
    
    # Add check constraint for integration_status
    op.create_check_constraint(
        'check_channel_integration_status',
        'channels',
        "integration_status IN ('none', 'configured', 'active', 'error', 'pending')"
    )

def downgrade():
    # Drop in reverse order
    op.drop_constraint('check_channel_integration_status', 'channels')
    op.drop_column('channels', 'integration_status')
    op.drop_column('channels', 'evoai_config')
    op.drop_column('channels', 'external_agent_id')
```

**Apply migration:**
```bash
cd evo-ai
alembic revision --autogenerate -m "Add agent linking to channels"
alembic upgrade head
```

#### Step 3: Update Channel Model

**File:** `evo-ai/src/models/models.py`

Add after line 308 (end of Channel class):

```python
# NEW: Link to Evo-AI agent
external_agent_id = Column(
    UUID(as_uuid=True),
    ForeignKey("agents.id", ondelete="SET NULL"),
    nullable=True,
    index=True,
    comment='Optional link to Evo-AI agent for this channel'
)

# NEW: Store EvoAI bot configuration
evoai_config = Column(
    JSON,
    nullable=True,
    comment='Stores EvoAI bot configuration: bot_id, configured_at, agent_url, status, error'
)

# NEW: Track integration status
integration_status = Column(
    String(length=20),
    nullable=False,
    server_default="none",
    comment='none, configured, active, error, pending'
)

# Add relationship to Agent
# Update the existing relationship if any, or add:
# agent = relationship("Agent", backref="channels", foreign_keys=[external_agent_id])
```

**Important:** Verify relationship is added correctly. The Channel model may already have an `agent` relationship. Add it if not exists.

#### Step 4: Update ChannelCreate Schema

**File:** `evo-ai/src/schemas/schemas.py`

```python
class ChannelCreate(BaseModel):
    # ... existing fields ...
    
    # NEW: Optional agent linking
    external_agent_id: Optional[UUID] = Field(
        None,
        description="Optional Evo-AI agent ID to link with this channel"
    )
    
    # Optional: client_id for auto-assignment
    client_id: Optional[UUID] = Field(
        None,
        description="Client ID for admin users to specify, auto-assigned for others"
    )

class ChannelResponse(BaseModel):
    # ... existing fields ...
    
    # NEW: Agent integration fields
    external_agent_id: Optional[str] = Field(None)
    integration_status: str = Field("none", description="Integration status")
    evoai_config: Optional[Dict[str, Any]] = Field(None)
    
    # ... existing fields ...
```

#### Step 5: Update ChannelService with Integration Logic

**File:** `evo-ai/src/services/channel_service.py`

```python
from src.services.evolution_api_service import EvolutionApiService, extract_bot_id
from src.services.agent_service import get_agent_by_id
from src.services.apikey_service import get_api_key_by_id
from src.utils.security import decrypt_key
from src.utils.logger import get_logger
from sqlalchemy import exc as SQLAlchemyError

logger = get_logger(__name__)

async def create_channel(
    db: Session,
    channel_data: ChannelCreate,
    current_user_role: str,
    client_id: Optional[UUID] = None
) -> Dict[str, Any]:
    """Create channel with optional EvoAI agent linking"""
    
    # ... existing channel creation logic (validate instance_name, etc.) ...
    
    # Initialize integration variables
    external_agent_id = channel_data.get('external_agent_id')
    integration_status = "none"
    evoai_config = None
    
    if external_agent_id:
        # Validate agent exists
        try:
            agent = await get_agent_by_id(db, external_agent_id)
            if not agent:
                raise HTTPException(
                    status_code=404, 
                    detail="Agent not found",
                    headers={"X-Error-Code": "AGENT_NOT_FOUND"}
                )
            
            # Get agent URL from agent_card_url property
            agent_url = agent.agent_card_url_property
            
            # Get API key
            api_key = None
            if agent.api_key_id:
                try:
                    api_key_obj = await get_api_key_by_id(db, agent.api_key_id)
                    if api_key_obj:
                        # Decrypt the key
                        api_key = decrypt_key(api_key_obj.encrypted_key)
                except Exception as decrypt_error:
                    logger.error(f"Failed to decrypt API key for agent {external_agent_id}: {decrypt_error}")
                    api_key = ""
            
            # Create EvoAI bot in Evolution-API
            evolution_service = EvolutionApiService()
            
            try:
                evoai_result = await evolution_service.create_evoai_bot(
                    instance_name=new_channel.instance_name,
                    agent_url=agent_url,
                    api_key=api_key or ""
                )
                
                # Extract bot_id using helper function
                bot_id = extract_bot_id(evoai_result)
                
                if bot_id:
                    evoai_config = {
                        "bot_id": bot_id,
                        "configured_at": datetime.utcnow().isoformat(),
                        "agent_url": agent_url,
                        "status": "configured"
                    }
                    integration_status = "configured"
                else:
                    evoai_config = {
                        "error": "No bot_id returned from Evolution-API",
                        "attempted_at": datetime.utcnow().isoformat()
                    }
                    integration_status = "error"
                
                logger.info(f"EvoAI bot configured for channel {new_channel.instance_name}: {integration_status}")
                
            except Exception as e:
                logger.error(f"Failed to create EvoAI bot for channel {new_channel.instance_name}: {str(e)}")
                evoai_config = {
                    "error": str(e),
                    "attempted_at": datetime.utcnow().isoformat()
                }
                integration_status = "error"
    
    db.commit()
    db.refresh(new_channel)
    
    return channel_to_dict(new_channel)
```

#### Step 6: Update Channels Routes

**File:** `evo-ai/src/api/channels_routes.py`

```python
from src.schemas.schemas import ChannelCreate, ChannelResponse
from src.services.channel_service import create_channel

@router.post("/channels/", response_model=ChannelResponse, status_code=201)
async def create_channel_endpoint(
    channel_data: ChannelCreate,
    current_user_role: str = Depends(get_user_role),
    client_id: Optional[str] = Depends(get_client_id),
    db: Session = Depends(get_db)
):
    """Create channel with optional EvoAI agent linking"""
    
    # Auto-assign client_id for non-admin users
    if current_user_role != 'admin' and 'client_id' not in channel_data and client_id:
        channel_data = channel_data.model_copy(update={'client_id': client_id})
    
    # Create channel with agent integration
    result = await create_channel(db, channel_data, current_user_role, client_id)
    
    return result
```

**Test endpoint via Postman after implementation:**
```bash
POST http://localhost:8000/api/v1/channels/
Content-Type: application/json
Authorization: Bearer your-jwt-token

Body (WITH agent):
{
    "name": "My WhatsApp Channel",
    "instance_name": "my-whatsapp",
    "channel_type": "whatsapp",
    "external_agent_id": "uuid-here"
}

Body (WITHOUT agent):
{
    "name": "My WhatsApp Channel",
    "instance_name": "my-whatsapp-2",
    "channel_type": "whatsapp"
}
```

---

### Phase 2: Frontend (Steps 7-9)
Focus on frontend implementation and test in UI after backend is verified.

#### Step 7: Update Frontend Service

**File:** `evo-ai/frontend/services/channelService.ts`

```typescript
export interface ChannelCreatePayload {
  name: string;
  instance_name: string;
  channel_type: 'whatsapp' | 'instagram' | 'email' | 'sms';
  display_name?: string;
  description?: string;
  external_agent_id?: string;  // NEW: Optional agent ID
  client_id?: string;
}

export async function createChannel(payload: ChannelCreatePayload): Promise<ChannelResponse> {
  const response = await api.post('/channels/', payload);
  return response.data;
}
```

#### Step 8: Add Agent Selection to Channel Creation UI

**File:** `evo-ai/frontend/app/channels/page.tsx`

```typescript
'use client';

import { useState, useEffect } from 'react';
import { createChannel, ChannelCreatePayload } from '@/services/channelService';
import { fetchAgents } from '@/services/agentService';

export default function ChannelsPage() {
  const [agents, setAgents] = useState<any[]>([]);
  const [selectedAgentId, setSelectedAgentId] = useState<string | null>(null);
  const [isCreateDialogOpen, setIsCreateDialogOpen] = useState(false);
  const [formData, setFormData] = useState<ChannelFormData>({
    name: '',
    instance_name: '',
    channel_type: 'whatsapp',
    display_name: '',
    description: ''
  });

  // Load agents for dropdown on mount
  useEffect(() => {
    loadAgents();
  }, []);

  async function loadAgents() {
    try {
      const data = await fetchAgents();
      setAgents(data.agents || []);
    } catch (error) {
      toast.error('Failed to load agents');
    }
  }

  async function handleCreateChannel() {
    try {
      // Include selected agent if any
      const payload: ChannelCreatePayload = {
        ...formData,
        external_agent_id: selectedAgentId || undefined
      };
      
      await createChannel(payload);
      setIsCreateDialogOpen(false);
      setSelectedAgentId(null);
      setFormData({
        name: '',
        instance_name: '',
        channel_type: 'whatsapp',
        display_name: '',
        description: ''
      });
      toast.success('Channel created successfully');
      loadChannels(); // Reload to show updated list
    } catch (error) {
      toast.error('Failed to create channel');
    }
  }

  return (
    <div className="container">
      <div className="flex justify-between items-center mb-6">
        <h1>Channels</h1>
        <Button onClick={() => setIsCreateDialogOpen(true)}>
          Create Channel
        </Button>
      </div>
      
      {/* Channel list card */}
      {/* ... existing channel list rendering ... */}
      
      {/* Create Channel Dialog */}
      <Dialog open={isCreateDialogOpen} onOpenChange={setIsCreateDialogOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Create New Channel</DialogTitle>
          </DialogHeader>
          <form onSubmit={handleCreateChannel}>
            {/* Existing fields */}
            <input
              value={formData.name}
              onChange={(e) => setFormData({...formData, name: e.target.value})}
              placeholder="Channel Name"
              required
            />
            <input
              value={formData.instance_name}
              onChange={(e) => setFormData({...formData, instance_name: e.target.value})}
              placeholder="Instance Name"
              required
            />
            <select
              value={formData.channel_type}
              onChange={(e) => setFormData({...formData, channel_type: e.target.value})}
            >
              <option value="whatsapp">WhatsApp</option>
              <option value="instagram">Instagram</option>
              <option value="email">Email</option>
              <option value="sms">SMS</option>
            </select>
            
            {/* NEW: Agent Selection */}
            <div className="mt-4">
              <label>Link EvoAI Agent (Optional)</label>
              <Select
                value={selectedAgentId}
                onValueChange={setSelectedAgentId}
              >
                <SelectTrigger>
                  <SelectValue placeholder="Select an agent..." />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="">None (Create without agent)</SelectItem>
                  {agents.map((agent) => (
                    <SelectItem key={agent.id} value={agent.id}>
                      <div className="flex flex-col">
                        <span className="font-medium">{agent.name}</span>
                        <span className="text-xs text-muted-foreground">
                          Agent URL: {agent.agent_card_url}
                        </span>
                      </div>
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
            
            <Button type="submit">Create Channel</Button>
          </form>
        </DialogContent>
      </Dialog>
    </div>
  );
}
```

#### Step 9: Add Agent Linking UI to Channel List

Add integration status badge and agent linking button to existing channel cards:

```typescript
// In each ChannelCard component
interface ChannelCardProps {
  channel: Channel;
  agents: any[];
  onLinkAgent: (channelId: string, agentId: string) => void;
}

function ChannelCard({ channel, agents, onLinkAgent }: ChannelCardProps) {
  const [isAgentSelectorOpen, setIsAgentSelectorOpen] = useState(false);
  const [selectedAgentId, setSelectedAgentId] = useState<string | null>(null);
  
  async function handleLinkAgent() {
    if (selectedAgentId) {
      await onLinkAgent(channel.id, selectedAgentId);
      setIsAgentSelectorOpen(false);
      toast.success('Agent linked successfully');
      loadChannels(); // Reload to update status
    }
  }
  
  return (
    <Card>
      <CardContent>
        {/* Channel info */}
        <h3>{channel.name}</h3>
        <p className="text-sm text-muted-foreground">
          Instance: {channel.instance_name}
        </p>
        
        {/* Integration Status Badge */}
        <Badge
          variant={
            channel.integration_status === 'configured' ? 'success' :
            channel.integration_status === 'error' ? 'destructive' : 'secondary'
          }
          className="mb-4"
        >
          {channel.integration_status === 'configured' && 'EvoAI Active'}
          {channel.integration_status === 'error' && 'Integration Error'}
          {channel.integration_status === 'none' && 'No Agent'}
        </Badge>
        
        {/* Agent Linking Section */}
        <div className="mt-4">
          {channel.external_agent_id ? (
            <div>
              <p className="text-sm">Linked Agent: {channel.agent_name}</p>
              <Button
                variant="outline"
                size="sm"
                onClick={() => setIsAgentSelectorOpen(true)}
              >
                Change Agent
              </Button>
            </div>
          ) : (
            <Button
              variant="default"
              size="sm"
              onClick={() => setIsAgentSelectorOpen(true)}
            >
              Link Agent
            </Button>
          )}
        </div>
      </CardContent>
      
      {/* Agent Selection Dialog */}
      <Dialog open={isAgentSelectorOpen} onOpenChange={setIsAgentSelectorOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Select Agent</DialogTitle>
          </DialogHeader>
          <Select
            value={selectedAgentId}
            onValueChange={setSelectedAgentId}
          >
            <SelectTrigger>
              <SelectValue placeholder="Select an agent..." />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="">Unlink Agent</SelectItem>
              {agents.map((agent) => (
                <SelectItem key={agent.id} value={agent.id}>
                  {agent.name}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
          <Button onClick={handleLinkAgent}>Confirm</Button>
        </DialogContent>
      </Dialog>
    </Card>
  );
}
```

---

## Testing Checklist

### Backend Testing (Phase 1)
- [ ] Apply migration successfully
- [ ] Create channel without agent (test backward compatibility)
- [ ] Create channel with agent (verify EvoAI bot is created in Evolution-API via Postman)
- [ ] Verify `external_agent_id` is saved in database
- [ ] Verify `evoai_config` contains correct `bot_id` and `agent_url`
- [ ] Verify `integration_status` is set correctly
- [ ] Test with non-existent agent (should return 404)
- [ ] Test with agent that has no API key (should still work with empty apiKey)

### Frontend Testing (Phase 2)
- [ ] Agents load correctly in dropdown
- [ ] Can create channel without selecting agent
- [ ] Can create channel with selected agent
- [ ] Agent selection shows agent card URL
- [ ] Can link agent to existing channel
- [ ] Can unlink agent from channel
- [ ] Integration status badge displays correctly after linking
- [ ] Toast notifications work correctly

### Integration End-to-End Testing
- [ ] Create channel + agent → Verify EvoAI bot appears in Evolution-API
- [ ] Send WhatsApp message → Verify EvoAI responds
- [ ] Check that message flow works through webhook
- [ ] Unlink agent → Verify EvoAI bot is removed from Evolution-API
- [ ] Re-link different agent → Verify new bot is created

---

## Expected Database State After Implementation

### channels Table Example
| id | name | instance_name | channel_type | external_agent_id | evoai_config | integration_status |
|---|---|----|-----------|---|----|----|----------|
| uuid-1 | WhatsApp Support | support-instance | whatsapp | uuid-agent-1 | {"bot_id": "evo-uuid", "configured_at": "...", "status": "configured"} | configured |
| uuid-2 | Sales | sales-instance | whatsapp | null | null | none |

### agents Table Example
| id | name | agent_card_url | api_key_id |
|---|---|---|---|
| uuid-agent-1 | Customer Service Bot | https://evoai.com/api/v1/a2a/uuid-1/.well-known/agent.json | uuid-key-1 |

---

## Rollback Plan

If implementation fails, revert changes in reverse order:

1. Backend: Revert `evolution_api_service.py` to original
2. Migration: Run `alembic downgrade -1`
3. Model: Revert `models.py` to original
4. Schema: Revert `schemas.py` to original
5. Frontend: Revert service and page changes

---

**Document Version:** 2.0  
**Created:** 2026-01-05  
**Status:** Ready for Implementation (2-Phase Approach)
