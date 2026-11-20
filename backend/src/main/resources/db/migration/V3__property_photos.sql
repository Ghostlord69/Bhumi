CREATE TABLE IF NOT EXISTS property_photo (
    id               BIGSERIAL PRIMARY KEY,
    property_id      BIGINT NOT NULL REFERENCES property_listing (id) ON DELETE CASCADE,
    file_id          VARCHAR(64) NOT NULL,
    original_name    VARCHAR(255),
    content_type     VARCHAR(128),
    bytes            BYTEA NOT NULL,
    sort_order       INTEGER NOT NULL DEFAULT 0
);

CREATE INDEX IF NOT EXISTS ix_property_photo_property ON property_photo (property_id, sort_order);
