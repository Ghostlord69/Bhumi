-- ULPIN (Bhu-Aadhaar) and supporting land identifiers

ALTER TABLE government_record
    ADD COLUMN IF NOT EXISTS ulpin VARCHAR(14),
    ADD COLUMN IF NOT EXISTS survey_number VARCHAR(64),
    ADD COLUMN IF NOT EXISTS khata_number VARCHAR(64),
    ADD COLUMN IF NOT EXISTS khewat_number VARCHAR(64),
    ADD COLUMN IF NOT EXISTS khatauni_number VARCHAR(64);

CREATE UNIQUE INDEX IF NOT EXISTS ux_government_record_ulpin
    ON government_record (ulpin)
    WHERE ulpin IS NOT NULL AND ulpin <> '';

CREATE INDEX IF NOT EXISTS ix_government_record_survey
    ON government_record (lower(survey_number))
    WHERE survey_number IS NOT NULL AND survey_number <> '';

ALTER TABLE property_listing
    ADD COLUMN IF NOT EXISTS ulpin VARCHAR(14),
    ADD COLUMN IF NOT EXISTS survey_number VARCHAR(64),
    ADD COLUMN IF NOT EXISTS khata_number VARCHAR(64),
    ADD COLUMN IF NOT EXISTS khewat_number VARCHAR(64),
    ADD COLUMN IF NOT EXISTS khatauni_number VARCHAR(64);
