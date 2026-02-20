-- FrameForge Community Posts Table
-- Run this in your Supabase Dashboard → SQL Editor

CREATE TABLE IF NOT EXISTS posts (
  id         UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  name       TEXT NOT NULL,
  title      TEXT NOT NULL,
  rating     INTEGER NOT NULL CHECK (rating BETWEEN 1 AND 5),
  video_url  TEXT NOT NULL,
  created_at TIMESTAMPTZ DEFAULT now()
);

-- Enable Row Level Security (recommended)
ALTER TABLE posts ENABLE ROW LEVEL SECURITY;

-- Allow anyone to read posts (public community feed)
CREATE POLICY "Public posts are viewable by everyone"
  ON posts FOR SELECT
  USING (true);

-- Allow anyone to insert posts (open community submissions)
CREATE POLICY "Anyone can submit a post"
  ON posts FOR INSERT
  WITH CHECK (true);
