-- Locate coordinates + physical verification report + virtual jamabandi (Postgres)

ALTER TABLE property_listing
    ADD COLUMN IF NOT EXISTS latitude DOUBLE PRECISION,
    ADD COLUMN IF NOT EXISTS longitude DOUBLE PRECISION,
    ADD COLUMN IF NOT EXISTS verification_report_id VARCHAR(64),
    ADD COLUMN IF NOT EXISTS verification_report_name VARCHAR(255),
    ADD COLUMN IF NOT EXISTS verification_report_type VARCHAR(128),
    ADD COLUMN IF NOT EXISTS verification_report_bytes BYTEA,
    ADD COLUMN IF NOT EXISTS virtual_jamabandi_id VARCHAR(64),
    ADD COLUMN IF NOT EXISTS virtual_jamabandi_name VARCHAR(255),
    ADD COLUMN IF NOT EXISTS virtual_jamabandi_type VARCHAR(128),
    ADD COLUMN IF NOT EXISTS virtual_jamabandi_bytes BYTEA;
