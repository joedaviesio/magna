-- Magna Supabase Schema
-- Run this in the Supabase SQL Editor

-- Chat messages table
CREATE TABLE chat_messages (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    session_id UUID NOT NULL,
    role TEXT NOT NULL CHECK (role IN ('user', 'assistant')),
    content TEXT NOT NULL,
    sources JSONB,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Analytics table for tracking usage
CREATE TABLE analytics (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    event_type TEXT NOT NULL,
    session_id UUID,
    query TEXT,
    detected_act TEXT,
    sources_count INTEGER,
    response_time_ms INTEGER,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Popular topics aggregation
CREATE TABLE topic_stats (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    act_name TEXT NOT NULL,
    query_count INTEGER DEFAULT 1,
    last_queried TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(act_name)
);

-- Indexes for performance
CREATE INDEX idx_chat_messages_session ON chat_messages(session_id);
CREATE INDEX idx_chat_messages_created ON chat_messages(created_at);
CREATE INDEX idx_analytics_created ON analytics(created_at);
CREATE INDEX idx_analytics_event_type ON analytics(event_type);
CREATE INDEX idx_topic_stats_count ON topic_stats(query_count DESC);

-- Enable Row Level Security (optional but recommended)
ALTER TABLE chat_messages ENABLE ROW LEVEL SECURITY;
ALTER TABLE analytics ENABLE ROW LEVEL SECURITY;
ALTER TABLE topic_stats ENABLE ROW LEVEL SECURITY;

-- Allow anonymous inserts (for the backend service)
CREATE POLICY "Allow anonymous inserts" ON chat_messages FOR INSERT WITH CHECK (true);
CREATE POLICY "Allow anonymous inserts" ON analytics FOR INSERT WITH CHECK (true);
CREATE POLICY "Allow anonymous upserts" ON topic_stats FOR ALL USING (true) WITH CHECK (true);
