CREATE EXTENSION IF NOT EXISTS vector;
CREATE TABLE accessory_embeddings (
    id BIGSERIAL PRIMARY KEY,
    accessory_id TEXT NOT NULL,
    -- the game ID
    accessory_name TEXT NOT NULL,
    -- original name
    embedding VECTOR(768) -- dimension depends on model
);
-- Create an index for fast similarity search
CREATE INDEX ON accessory_embeddings USING hnsw (embedding vector_cosine_ops);
CREATE OR REPLACE FUNCTION match_accessory(
        query_embedding VECTOR(768),
        match_threshold FLOAT DEFAULT 0.7,
        match_count INT DEFAULT 3
    ) RETURNS TABLE (
        accessory_id TEXT,
        accessory_name TEXT,
        similarity FLOAT
    ) LANGUAGE plpgsql AS $$ BEGIN RETURN QUERY
SELECT ae.accessory_id,
    ae.accessory_name,
    1 - (ae.embedding <=> query_embedding) AS similarity
FROM accessory_embeddings ae
WHERE 1 - (ae.embedding <=> query_embedding) > match_threshold
ORDER BY ae.embedding <=> query_embedding
LIMIT match_count;
END;
$$;
ALTER TABLE accessory_embeddings ENABLE ROW LEVEL SECURITY;
-- Allow anyone to read (for querying embeddings from your app)
CREATE POLICY "Allow public read access" ON accessory_embeddings FOR
SELECT USING (true);
-- Allow inserts with service role or authenticated
CREATE POLICY "Allow insert access" ON accessory_embeddings FOR
INSERT WITH CHECK (true);
