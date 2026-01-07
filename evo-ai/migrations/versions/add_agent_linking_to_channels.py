"""add_agent_linking_to_channels

Revision ID: add_agent_linking_to_channels
Revises: add_channels_table
Create Date: 2026-01-05 03:00:00.000000

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "add_agent_linking_to_channels"
down_revision: Union[str, None] = "add_channels_table"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # 1) Add external_agent_id column (type only)
    op.add_column(
        'channels',
        sa.Column(
            'external_agent_id',
            sa.UUID(as_uuid=True),
            nullable=True
        )
    )

    # 2) Create index for external_agent_id
    op.create_index(
        'ix_channels_external_agent_id',
        'channels',
        ['external_agent_id'],
        unique=False
    )

    # 3) Create foreign key to agents.id
    op.create_foreign_key(
        'fk_channels_external_agent_id_agents',
        'channels',
        'agents',
        ['external_agent_id'],
        ['id'],
        ondelete='SET NULL'
    )

    # 4) Add evoai_config column (JSON)
    op.add_column(
        'channels',
        sa.Column(
            'evoai_config',
            sa.JSON(),
            nullable=True
        )
    )

    # 5) Add integration_status column
    op.add_column(
        'channels',
        sa.Column(
            'integration_status',
            sa.String(length=20),
            nullable=False,
            server_default='none'
        )
    )

    # 6) Add check constraint for integration_status
    op.create_check_constraint(
        'check_channel_integration_status',
        'channels',
        "integration_status IN ('none', 'configured', 'active', 'error', 'pending')"
    )


def downgrade() -> None:
    """Downgrade schema."""
    # Drop in reverse order
    op.drop_constraint('check_channel_integration_status', 'channels', type_='check')
    op.drop_column('channels', 'integration_status')
    op.drop_column('channels', 'evoai_config')

    # Drop foreign key and index before dropping column
    op.drop_constraint('fk_channels_external_agent_id_agents', 'channels', type_='foreignkey')
    op.drop_index('ix_channels_external_agent_id', table_name='channels')
    op.drop_column('channels', 'external_agent_id')
