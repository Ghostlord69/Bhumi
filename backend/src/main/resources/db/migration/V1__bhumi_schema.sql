-- Bhumi schema aligned with the in-app domain model

CREATE TABLE app_user (
    id              BIGSERIAL PRIMARY KEY,
    email           VARCHAR(255) NOT NULL UNIQUE,
    phone           VARCHAR(64),
    password_hash   VARCHAR(255) NOT NULL,
    full_name       VARCHAR(255) NOT NULL,
    role            VARCHAR(32)  NOT NULL,
    state           VARCHAR(128),
    district        VARCHAR(128),
    city            VARCHAR(128),
    active          BOOLEAN NOT NULL DEFAULT TRUE,
    official_login  VARCHAR(255),
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE government_record (
    khasra_number   VARCHAR(64) PRIMARY KEY,
    village         VARCHAR(255),
    city            VARCHAR(128) NOT NULL,
    district        VARCHAR(128) NOT NULL,
    owner_name      VARCHAR(255) NOT NULL,
    measurements    VARCHAR(255),
    owner_phone     VARCHAR(64),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE authenticator_application (
    id                  BIGSERIAL PRIMARY KEY,
    applicant_user_id   BIGINT NOT NULL REFERENCES app_user (id),
    full_name           VARCHAR(255) NOT NULL,
    personal_email      VARCHAR(255) NOT NULL,
    phone               VARCHAR(64),
    official_id_number  VARCHAR(128) NOT NULL,
    state               VARCHAR(128),
    district            VARCHAR(128),
    city                VARCHAR(128),
    status              VARCHAR(32) NOT NULL,
    created_at          TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE property_listing (
    id                      BIGSERIAL PRIMARY KEY,
    seller_id               BIGINT NOT NULL REFERENCES app_user (id),
    buyer_id                BIGINT REFERENCES app_user (id),
    purpose                 VARCHAR(32) NOT NULL,
    type                    VARCHAR(32) NOT NULL,
    status                  VARCHAR(64) NOT NULL,
    title                   VARCHAR(255) NOT NULL,
    state                   VARCHAR(128),
    district                VARCHAR(128),
    city                    VARCHAR(128),
    address                 TEXT,
    asking_price            DOUBLE PRECISION,
    measurements            VARCHAR(255),
    khasra_number           VARCHAR(64),
    registry_detail         TEXT,
    house_number            VARCHAR(64),
    furnished               BOOLEAN,
    flat_number             VARCHAR(64),
    floor                   INTEGER,
    bedrooms                INTEGER,
    extra_notes             TEXT,
    ai_summary              TEXT,
    officer_remarks         TEXT,
    certificate_id          BIGINT,
    purchase_requested_at   TIMESTAMPTZ,
    sale_confirmed_at       TIMESTAMPTZ,
    transferred_at          TIMESTAMPTZ,
    created_at              TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at              TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE property_paper (
    id               BIGSERIAL PRIMARY KEY,
    property_id      BIGINT NOT NULL REFERENCES property_listing (id) ON DELETE CASCADE,
    file_id          VARCHAR(64) NOT NULL,
    original_name    VARCHAR(255),
    content_type     VARCHAR(128),
    bytes            BYTEA NOT NULL
);

CREATE TABLE chat_message (
    id              BIGSERIAL PRIMARY KEY,
    property_id     BIGINT NOT NULL REFERENCES property_listing (id) ON DELETE CASCADE,
    sender_id       BIGINT NOT NULL REFERENCES app_user (id),
    body            TEXT NOT NULL,
    blocked         BOOLEAN NOT NULL DEFAULT FALSE,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE audit_event (
    id              BIGSERIAL PRIMARY KEY,
    actor_id        BIGINT,
    action          VARCHAR(64) NOT NULL,
    detail          TEXT,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE transfer_certificate (
    id                   BIGSERIAL PRIMARY KEY,
    property_id          BIGINT NOT NULL REFERENCES property_listing (id),
    certificate_number   VARCHAR(128) NOT NULL UNIQUE,
    khasra_number        VARCHAR(64),
    old_owner_name       VARCHAR(255),
    new_owner_name       VARCHAR(255),
    village              VARCHAR(255),
    city                 VARCHAR(128),
    district             VARCHAR(128),
    state                VARCHAR(128),
    measurements         VARCHAR(255),
    officer_id           BIGINT,
    officer_name         VARCHAR(255),
    issued_at            TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    pdf_bytes            BYTEA NOT NULL
);

CREATE TABLE notification (
    id              BIGSERIAL PRIMARY KEY,
    user_id         BIGINT NOT NULL REFERENCES app_user (id),
    channel         VARCHAR(32) NOT NULL,
    subject         VARCHAR(255) NOT NULL,
    body            TEXT NOT NULL,
    is_read         BOOLEAN NOT NULL DEFAULT FALSE,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- State / UT admins who approve authenticator applications (rows inserted manually)
CREATE TABLE state_admin (
    admin_id                BIGSERIAL PRIMARY KEY,
    user_id                 BIGINT NOT NULL UNIQUE REFERENCES app_user (id),
    state_union_territory   VARCHAR(128) NOT NULL,
    email                   VARCHAR(255) NOT NULL UNIQUE,
    phone                   VARCHAR(64) NOT NULL,
    full_name               VARCHAR(255) NOT NULL,
    active                  BOOLEAN NOT NULL DEFAULT TRUE,
    created_at              TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_property_status ON property_listing (status);
CREATE INDEX idx_property_city ON property_listing (city);
CREATE INDEX idx_notification_user ON notification (user_id, created_at DESC);
CREATE INDEX idx_chat_property ON chat_message (property_id);
CREATE INDEX idx_state_admin_state ON state_admin (lower(state_union_territory));
