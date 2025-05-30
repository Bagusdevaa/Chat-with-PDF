"""create_documents_conversations_messages_tables

Revision ID: b23f40c92ce6
Revises: 631f40b92be5
Create Date: 2023-05-30 15:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from datetime import datetime
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = 'b23f40c92ce6'
down_revision = '631f40b92be5'
branch_labels = None
depends_on = None


def upgrade():
    # Update users table with new fields
    op.add_column('users', sa.Column('first_name', sa.String(50), nullable=True))
    op.add_column('users', sa.Column('last_name', sa.String(50), nullable=True))
    op.add_column('users', sa.Column('reset_token', sa.String(100), nullable=True))
    op.add_column('users', sa.Column('reset_token_expiry', sa.DateTime(), nullable=True))
    op.add_column('users', sa.Column('last_login', sa.DateTime(), nullable=True))
    op.add_column('users', sa.Column('api_key', sa.String(100), nullable=True))
    op.create_index('ix_users_api_key', 'users', ['api_key'], unique=True)
    
    # Create documents table
    op.create_table(
        'documents',
        sa.Column('id', sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column('user_id', sa.BigInteger(), nullable=False),
        sa.Column('filename', sa.String(255), nullable=False),
        sa.Column('original_filename', sa.String(255), nullable=False),
        sa.Column('file_path', sa.String(255), nullable=False),
        sa.Column('file_size', sa.Integer(), nullable=False),
        sa.Column('mime_type', sa.String(100), nullable=False, server_default='application/pdf'),
        sa.Column('upload_date', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('processed', sa.Boolean(), nullable=False, server_default=sa.text('0')),
        sa.Column('session_id', sa.String(100), nullable=True),
        sa.Column('page_count', sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create conversations table
    op.create_table(
        'conversations',
        sa.Column('id', sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column('user_id', sa.BigInteger(), nullable=False),
        sa.Column('document_id', sa.BigInteger(), nullable=False),
        sa.Column('title', sa.String(255), nullable=False, server_default='New Conversation'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP')),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default=sa.text('1')),
        sa.ForeignKeyConstraint(['document_id'], ['documents.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create messages table
    op.create_table(
        'messages',
        sa.Column('id', sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column('conversation_id', sa.BigInteger(), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('role', sa.String(10), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('tokens_used', sa.Integer(), nullable=True),
        sa.Column('context_pages', sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(['conversation_id'], ['conversations.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )


def downgrade():
    # Drop tables in reverse order
    op.drop_table('messages')
    op.drop_table('conversations')
    op.drop_table('documents')
    
    # Remove new columns from users table
    op.drop_index('ix_users_api_key', table_name='users')
    op.drop_column('users', 'api_key')
    op.drop_column('users', 'last_login')
    op.drop_column('users', 'reset_token_expiry')
    op.drop_column('users', 'reset_token')
    op.drop_column('users', 'last_name')
    op.drop_column('users', 'first_name')
