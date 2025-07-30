-- Forensic Toponymic Database Schema for Mariupol Urbicide Documentation
-- Based on Opus research report recommendations
-- Implements bitemporal tracking with forensic chain-of-custody

-- Enable required extensions
CREATE EXTENSION IF NOT EXISTS postgis;
CREATE EXTENSION IF NOT EXISTS pg_trgm;
CREATE EXTENSION IF NOT EXISTS unaccent;
CREATE EXTENSION IF NOT EXISTS fuzzystrmatch;
CREATE EXTENSION IF NOT EXISTS uuid_ossp;
CREATE EXTENSION IF NOT EXISTS btree_gist;

-- Create schema for forensic toponymic data
CREATE SCHEMA IF NOT EXISTS forensic_toponymy;
SET search_path TO forensic_toponymy, public;

-- Core streets table with spatial data
CREATE TABLE streets (
    street_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    geometry GEOMETRY(LINESTRING, 4326),
    osm_way_id BIGINT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    created_by TEXT DEFAULT 'system',
    source_hash TEXT, -- SHA-256 of source document
    confidence_score DECIMAL(3,2) CHECK (confidence_score >= 0 AND confidence_score <= 1),
    metadata JSONB
);

-- Bitemporal street names table
CREATE TABLE street_names (
    name_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    street_id UUID REFERENCES streets(street_id),
    name_text TEXT NOT NULL,
    language_code TEXT NOT NULL CHECK (language_code IN ('ukr', 'rus', 'eng')),
    script_code TEXT NOT NULL CHECK (script_code IN ('Cyrl', 'Latn')),
    transliterated_variants TEXT[],
    
    -- Bitemporal tracking
    valid_from TIMESTAMPTZ NOT NULL,
    valid_to TIMESTAMPTZ DEFAULT 'infinity',
    transaction_from TIMESTAMPTZ DEFAULT NOW(),
    transaction_to TIMESTAMPTZ DEFAULT 'infinity',
    
    -- Forensic metadata
    source_document TEXT,
    source_url TEXT,
    source_hash TEXT, -- SHA-256 of source
    evidence_type TEXT CHECK (evidence_type IN ('official_decree', 'osm_data', 'witness_testimony', 'media_report')),
    confidence_score DECIMAL(3,2) CHECK (confidence_score >= 0 AND confidence_score <= 1),
    
    -- Administrative context
    administrative_period TEXT CHECK (administrative_period IN ('soviet', 'ukrainian', 'occupation')),
    decree_number TEXT,
    official_signature TEXT,
    
    created_at TIMESTAMPTZ DEFAULT NOW(),
    created_by TEXT DEFAULT 'system',
    metadata JSONB
);

-- Address variants table for fuzzy matching
CREATE TABLE address_variants (
    variant_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    street_id UUID REFERENCES streets(street_id),
    canonical_address TEXT NOT NULL,
    variant_text TEXT NOT NULL,
    language_code TEXT NOT NULL,
    variant_type TEXT CHECK (variant_type IN ('abbreviation', 'transliteration', 'historical', 'colloquial')),
    confidence_score DECIMAL(3,2),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    source_hash TEXT
);

-- Evidence sources table for forensic chain-of-custody
CREATE TABLE evidence_sources (
    source_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    source_type TEXT CHECK (source_type IN ('pdf_document', 'osm_data', 'telegram_media', 'official_decree')),
    filename TEXT,
    file_path TEXT,
    file_size_bytes BIGINT,
    sha256_hash TEXT UNIQUE NOT NULL,
    source_url TEXT,
    parent_page TEXT,
    download_timestamp TIMESTAMPTZ,
    last_modified TIMESTAMPTZ,
    mime_type TEXT,
    metadata JSONB,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Temporal exclusion constraints to prevent overlaps
ALTER TABLE street_names ADD CONSTRAINT street_names_temporal_exclude 
EXCLUDE USING gist (
    street_id WITH =,
    language_code WITH =,
    tstzrange(valid_from, valid_to) WITH &&
);

-- Indexes for performance
CREATE INDEX idx_streets_geometry ON streets USING GIST (geometry);
CREATE INDEX idx_streets_osm_way_id ON streets (osm_way_id);
CREATE INDEX idx_street_names_street_id ON street_names (street_id);
CREATE INDEX idx_street_names_language ON street_names (language_code);
CREATE INDEX idx_street_names_period ON street_names (administrative_period);
CREATE INDEX idx_street_names_valid_time ON street_names USING GIST (tstzrange(valid_from, valid_to));
CREATE INDEX idx_street_names_text_trgm ON street_names USING GIN (name_text gin_trgm_ops);
CREATE INDEX idx_address_variants_text_trgm ON address_variants USING GIN (variant_text gin_trgm_ops);
CREATE INDEX idx_evidence_sources_hash ON evidence_sources (sha256_hash);

-- Partial index for current names (performance optimization)
CREATE INDEX idx_street_names_current ON street_names (street_id, language_code) 
WHERE valid_to = 'infinity';

-- Materialized view for current street names (memory optimization)
CREATE MATERIALIZED VIEW current_street_names AS
SELECT 
    sn.street_id,
    sn.name_text,
    sn.language_code,
    sn.administrative_period,
    s.geometry,
    s.confidence_score
FROM street_names sn
JOIN streets s ON sn.street_id = s.street_id
WHERE sn.valid_to = 'infinity'
  AND sn.transaction_to = 'infinity';

CREATE INDEX idx_current_street_names_text ON current_street_names USING GIN (name_text gin_trgm_ops);

-- Functions for forensic operations
CREATE OR REPLACE FUNCTION add_street_name_with_audit(
    p_street_id UUID,
    p_name_text TEXT,
    p_language_code TEXT,
    p_script_code TEXT,
    p_valid_from TIMESTAMPTZ,
    p_source_document TEXT DEFAULT NULL,
    p_source_hash TEXT DEFAULT NULL,
    p_evidence_type TEXT DEFAULT 'official_decree',
    p_administrative_period TEXT DEFAULT 'occupation'
) RETURNS UUID AS $$
DECLARE
    new_name_id UUID;
BEGIN
    -- End current name if exists
    UPDATE street_names 
    SET valid_to = p_valid_from,
        transaction_to = NOW()
    WHERE street_id = p_street_id 
      AND language_code = p_language_code 
      AND valid_to = 'infinity';
    
    -- Insert new name
    INSERT INTO street_names (
        street_id, name_text, language_code, script_code,
        valid_from, source_document, source_hash,
        evidence_type, administrative_period
    ) VALUES (
        p_street_id, p_name_text, p_language_code, p_script_code,
        p_valid_from, p_source_document, p_source_hash,
        p_evidence_type, p_administrative_period
    ) RETURNING name_id INTO new_name_id;
    
    RETURN new_name_id;
END;
$$ LANGUAGE plpgsql;

-- Function for fuzzy address matching
CREATE OR REPLACE FUNCTION fuzzy_match_address(
    p_input_text TEXT,
    p_language_code TEXT DEFAULT 'rus',
    p_threshold DECIMAL DEFAULT 0.7
) RETURNS TABLE (
    street_id UUID,
    name_text TEXT,
    similarity_score DECIMAL,
    match_type TEXT
) AS $$
BEGIN
    RETURN QUERY
    WITH fuzzy_matches AS (
        SELECT 
            av.street_id,
            av.variant_text as name_text,
            similarity(av.variant_text, p_input_text) as sim_score,
            'variant' as match_type
        FROM address_variants av
        WHERE av.language_code = p_language_code
          AND similarity(av.variant_text, p_input_text) >= p_threshold
        
        UNION ALL
        
        SELECT 
            sn.street_id,
            sn.name_text,
            similarity(sn.name_text, p_input_text) as sim_score,
            'direct' as match_type
        FROM street_names sn
        WHERE sn.language_code = p_language_code
          AND sn.valid_to = 'infinity'
          AND similarity(sn.name_text, p_input_text) >= p_threshold
    )
    SELECT 
        fm.street_id,
        fm.name_text,
        fm.sim_score::DECIMAL(3,2),
        fm.match_type
    FROM fuzzy_matches fm
    ORDER BY fm.sim_score DESC
    LIMIT 10;
END;
$$ LANGUAGE plpgsql;

-- Create audit trigger for forensic logging
CREATE OR REPLACE FUNCTION audit_street_names() RETURNS TRIGGER AS $$
BEGIN
    IF TG_OP = 'INSERT' THEN
        NEW.created_at = NOW();
        NEW.transaction_from = NOW();
        RETURN NEW;
    ELSIF TG_OP = 'UPDATE' THEN
        NEW.transaction_from = NOW();
        RETURN NEW;
    END IF;
    RETURN NULL;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER street_names_audit_trigger
    BEFORE INSERT OR UPDATE ON street_names
    FOR EACH ROW EXECUTE FUNCTION audit_street_names();

-- Grant permissions
GRANT USAGE ON SCHEMA forensic_toponymy TO PUBLIC;
GRANT SELECT ON ALL TABLES IN SCHEMA forensic_toponymy TO PUBLIC;
GRANT INSERT, UPDATE ON street_names, address_variants, evidence_sources TO PUBLIC;
GRANT USAGE ON ALL SEQUENCES IN SCHEMA forensic_toponymy TO PUBLIC;
