
CREATE EXTENSION IF NOT EXISTS vector;

CREATE TABLE duolingo_chunks (
    id SERIAL PRIMARY KEY,
    section_title TEXT,
    source TEXT,
    chunk_text TEXT,
    embedding VECTOR(1536)
);