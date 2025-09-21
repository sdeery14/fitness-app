-- Initialize the database for OpenAI Agents session history
-- This script will be run when the PostgreSQL container starts for the first time

-- Create the sessions table as per OpenAI Agents documentation
-- The table structure will be created automatically by SQLAlchemy when the application runs
-- This file can be used for any additional initialization if needed

-- Enable some useful PostgreSQL extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- The OpenAI Agents SQLAlchemy session store will automatically create the required tables:
-- - agent_sessions (stores session metadata)
-- - agent_messages (stores conversation messages)

-- Our custom tables will be created by SQLAlchemy as well:
-- - users (user accounts)
-- - user_sessions (links users to their agent sessions)  
-- - user_profiles (extended user information for fitness)
-- - user_measurements (historical height/weight records)
