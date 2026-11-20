package com.landregistry.store;

import com.landregistry.domain.AuditEvent;
import com.landregistry.domain.AuthenticatorApplication;
import com.landregistry.domain.ChatMessage;
import com.landregistry.domain.GovernmentRecord;
import com.landregistry.domain.ListingPurpose;
import com.landregistry.domain.Notification;
import com.landregistry.domain.PropertyListing;
import com.landregistry.domain.PropertyStatus;
import com.landregistry.domain.PropertyType;
import com.landregistry.domain.StateAdmin;
import com.landregistry.domain.StoredFile;
import com.landregistry.domain.TransferCertificate;
import com.landregistry.domain.UserAccount;
import com.landregistry.security.Role;
import java.sql.ResultSet;
import java.sql.SQLException;
import java.sql.Timestamp;
import java.time.Instant;
import java.util.ArrayList;
import java.util.List;
import java.util.Optional;
import org.springframework.jdbc.core.JdbcTemplate;
import org.springframework.jdbc.support.GeneratedKeyHolder;
import org.springframework.jdbc.support.KeyHolder;
import org.springframework.transaction.annotation.Transactional;

/** Postgres-backed store. Enable by wiring datasource and registering this bean instead of InMemoryAppStore. */
public class JdbcAppStore implements AppStore {
    private final JdbcTemplate jdbc;

    public JdbcAppStore(JdbcTemplate jdbc) {
        this.jdbc = jdbc;
    }

    @Override
    public UserAccount saveUser(UserAccount user) {
        if (user.getId() == null) {
            KeyHolder keys = new GeneratedKeyHolder();
            jdbc.update(con -> {
                var ps = con.prepareStatement(
                        """
                        INSERT INTO app_user
                          (email, phone, password_hash, full_name, role, state, district, city, active, official_login, created_at)
                        VALUES (?,?,?,?,?,?,?,?,?,?,?)
                        """,
                        new String[] {"id"});
                ps.setString(1, user.getEmail());
                ps.setString(2, user.getPhone());
                ps.setString(3, user.getPasswordHash());
                ps.setString(4, user.getFullName());
                ps.setString(5, user.getRole().name());
                ps.setString(6, user.getState());
                ps.setString(7, user.getDistrict());
                ps.setString(8, user.getCity());
                ps.setBoolean(9, user.isActive());
                ps.setString(10, user.getOfficialLogin());
                ps.setTimestamp(11, Timestamp.from(user.getCreatedAt() == null ? Instant.now() : user.getCreatedAt()));
                return ps;
            }, keys);
            user.setId(keys.getKey().longValue());
        } else {
            jdbc.update(
                    """
                    UPDATE app_user SET email=?, phone=?, password_hash=?, full_name=?, role=?, state=?, district=?,
                      city=?, active=?, official_login=? WHERE id=?
                    """,
                    user.getEmail(), user.getPhone(), user.getPasswordHash(), user.getFullName(), user.getRole().name(),
                    user.getState(), user.getDistrict(), user.getCity(), user.isActive(), user.getOfficialLogin(),
                    user.getId());
        }
        return user;
    }

    @Override
    public Optional<UserAccount> user(Long id) {
        List<UserAccount> rows = jdbc.query("SELECT * FROM app_user WHERE id=?", this::mapUser, id);
        return rows.stream().findFirst();
    }

    @Override
    public Optional<UserAccount> userByEmail(String email) {
        List<UserAccount> rows = jdbc.query(
                "SELECT * FROM app_user WHERE lower(email)=lower(?)", this::mapUser, email);
        return rows.stream().findFirst();
    }

    @Override
    public List<UserAccount> users() {
        return jdbc.query("SELECT * FROM app_user ORDER BY id", this::mapUser);
    }

    @Override
    public List<UserAccount> authenticators() {
        return jdbc.query("SELECT * FROM app_user WHERE role='AUTHENTICATOR' ORDER BY id", this::mapUser);
    }

    @Override
    public List<UserAccount> authenticatorsInCity(String city) {
        if (city == null) {
            return List.of();
        }
        return jdbc.query(
                "SELECT * FROM app_user WHERE role='AUTHENTICATOR' AND active=TRUE AND lower(city)=lower(?) ORDER BY id",
                this::mapUser,
                city);
    }

    @Override
    @Transactional
    public PropertyListing saveProperty(PropertyListing listing) {
        if (listing.getId() == null) {
            KeyHolder keys = new GeneratedKeyHolder();
            jdbc.update(con -> {
                var ps = con.prepareStatement(
                        """
                        INSERT INTO property_listing
                          (seller_id, buyer_id, purpose, type, status, title, state, district, city, address,
                           asking_price, measurements, khasra_number, ulpin, survey_number, khata_number,
                           khewat_number, khatauni_number, registry_detail, house_number, furnished,
                           flat_number, floor, bedrooms, extra_notes, ai_summary, officer_remarks, certificate_id,
                           latitude, longitude,
                           verification_report_id, verification_report_name, verification_report_type, verification_report_bytes,
                           virtual_jamabandi_id, virtual_jamabandi_name, virtual_jamabandi_type, virtual_jamabandi_bytes,
                           purchase_requested_at, sale_confirmed_at, transferred_at, created_at, updated_at)
                        VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
                        """,
                        new String[] {"id"});
                bindProperty(ps, listing);
                return ps;
            }, keys);
            listing.setId(keys.getKey().longValue());
        } else {
            jdbc.update(
                    """
                    UPDATE property_listing SET
                      seller_id=?, buyer_id=?, purpose=?, type=?, status=?, title=?, state=?, district=?, city=?,
                      address=?, asking_price=?, measurements=?, khasra_number=?, ulpin=?, survey_number=?,
                      khata_number=?, khewat_number=?, khatauni_number=?, registry_detail=?, house_number=?,
                      furnished=?, flat_number=?, floor=?, bedrooms=?, extra_notes=?, ai_summary=?, officer_remarks=?,
                      certificate_id=?, latitude=?, longitude=?,
                      verification_report_id=?, verification_report_name=?, verification_report_type=?, verification_report_bytes=?,
                      virtual_jamabandi_id=?, virtual_jamabandi_name=?, virtual_jamabandi_type=?, virtual_jamabandi_bytes=?,
                      purchase_requested_at=?, sale_confirmed_at=?, transferred_at=?, updated_at=?
                    WHERE id=?
                    """,
                    listing.getSellerId(), listing.getBuyerId(), listing.getPurpose().name(), listing.getType().name(),
                    listing.getStatus().name(), listing.getTitle(), listing.getState(), listing.getDistrict(),
                    listing.getCity(), listing.getAddress(), listing.getAskingPrice(), listing.getMeasurements(),
                    listing.getKhasraNumber(), listing.getUlpin(), listing.getSurveyNumber(), listing.getKhataNumber(),
                    listing.getKhewatNumber(), listing.getKhatauniNumber(), listing.getRegistryDetail(),
                    listing.getHouseNumber(), listing.getFurnished(), listing.getFlatNumber(), listing.getFloor(),
                    listing.getBedrooms(), listing.getExtraNotes(), listing.getAiSummary(), listing.getOfficerRemarks(),
                    listing.getCertificateId(), listing.getLatitude(), listing.getLongitude(),
                    fileId(listing.getVerificationReport()), fileName(listing.getVerificationReport()),
                    fileType(listing.getVerificationReport()), fileBytes(listing.getVerificationReport()),
                    fileId(listing.getVirtualJamabandi()), fileName(listing.getVirtualJamabandi()),
                    fileType(listing.getVirtualJamabandi()), fileBytes(listing.getVirtualJamabandi()),
                    ts(listing.getPurchaseRequestedAt()), ts(listing.getSaleConfirmedAt()),
                    ts(listing.getTransferredAt()), Timestamp.from(Instant.now()), listing.getId());
            jdbc.update("DELETE FROM property_paper WHERE property_id=?", listing.getId());
            jdbc.update("DELETE FROM property_photo WHERE property_id=?", listing.getId());
        }
        if (listing.getRegistryPapers() != null) {
            for (StoredFile paper : listing.getRegistryPapers()) {
                jdbc.update(
                        """
                        INSERT INTO property_paper (property_id, file_id, original_name, content_type, bytes)
                        VALUES (?,?,?,?,?)
                        """,
                        listing.getId(),
                        paper.getId(),
                        paper.getOriginalName(),
                        paper.getContentType(),
                        paper.getBytes());
            }
        }
        if (listing.getPropertyPhotos() != null) {
            int sort = 0;
            for (StoredFile photo : listing.getPropertyPhotos()) {
                jdbc.update(
                        """
                        INSERT INTO property_photo (property_id, file_id, original_name, content_type, bytes, sort_order)
                        VALUES (?,?,?,?,?,?)
                        """,
                        listing.getId(),
                        photo.getId(),
                        photo.getOriginalName(),
                        photo.getContentType(),
                        photo.getBytes(),
                        sort++);
            }
        }
        return listing;
    }

    private void bindProperty(java.sql.PreparedStatement ps, PropertyListing listing) throws SQLException {
        ps.setLong(1, listing.getSellerId());
        if (listing.getBuyerId() == null) {
            ps.setObject(2, null);
        } else {
            ps.setLong(2, listing.getBuyerId());
        }
        ps.setString(3, listing.getPurpose().name());
        ps.setString(4, listing.getType().name());
        ps.setString(5, listing.getStatus().name());
        ps.setString(6, listing.getTitle());
        ps.setString(7, listing.getState());
        ps.setString(8, listing.getDistrict());
        ps.setString(9, listing.getCity());
        ps.setString(10, listing.getAddress());
        if (listing.getAskingPrice() == null) {
            ps.setObject(11, null);
        } else {
            ps.setDouble(11, listing.getAskingPrice());
        }
        ps.setString(12, listing.getMeasurements());
        ps.setString(13, listing.getKhasraNumber());
        ps.setString(14, listing.getUlpin());
        ps.setString(15, listing.getSurveyNumber());
        ps.setString(16, listing.getKhataNumber());
        ps.setString(17, listing.getKhewatNumber());
        ps.setString(18, listing.getKhatauniNumber());
        ps.setString(19, listing.getRegistryDetail());
        ps.setString(20, listing.getHouseNumber());
        if (listing.getFurnished() == null) {
            ps.setObject(21, null);
        } else {
            ps.setBoolean(21, listing.getFurnished());
        }
        ps.setString(22, listing.getFlatNumber());
        if (listing.getFloor() == null) {
            ps.setObject(23, null);
        } else {
            ps.setInt(23, listing.getFloor());
        }
        if (listing.getBedrooms() == null) {
            ps.setObject(24, null);
        } else {
            ps.setInt(24, listing.getBedrooms());
        }
        ps.setString(25, listing.getExtraNotes());
        ps.setString(26, listing.getAiSummary());
        ps.setString(27, listing.getOfficerRemarks());
        if (listing.getCertificateId() == null) {
            ps.setObject(28, null);
        } else {
            ps.setLong(28, listing.getCertificateId());
        }
        if (listing.getLatitude() == null) {
            ps.setObject(29, null);
        } else {
            ps.setDouble(29, listing.getLatitude());
        }
        if (listing.getLongitude() == null) {
            ps.setObject(30, null);
        } else {
            ps.setDouble(30, listing.getLongitude());
        }
        ps.setString(31, fileId(listing.getVerificationReport()));
        ps.setString(32, fileName(listing.getVerificationReport()));
        ps.setString(33, fileType(listing.getVerificationReport()));
        ps.setBytes(34, fileBytes(listing.getVerificationReport()));
        ps.setString(35, fileId(listing.getVirtualJamabandi()));
        ps.setString(36, fileName(listing.getVirtualJamabandi()));
        ps.setString(37, fileType(listing.getVirtualJamabandi()));
        ps.setBytes(38, fileBytes(listing.getVirtualJamabandi()));
        ps.setTimestamp(39, ts(listing.getPurchaseRequestedAt()));
        ps.setTimestamp(40, ts(listing.getSaleConfirmedAt()));
        ps.setTimestamp(41, ts(listing.getTransferredAt()));
        ps.setTimestamp(42, Timestamp.from(listing.getCreatedAt() == null ? Instant.now() : listing.getCreatedAt()));
        ps.setTimestamp(43, Timestamp.from(listing.getUpdatedAt() == null ? Instant.now() : listing.getUpdatedAt()));
    }

    private static String fileId(StoredFile f) {
        return f == null ? null : f.getId();
    }

    private static String fileName(StoredFile f) {
        return f == null ? null : f.getOriginalName();
    }

    private static String fileType(StoredFile f) {
        return f == null ? null : f.getContentType();
    }

    private static byte[] fileBytes(StoredFile f) {
        return f == null ? null : f.getBytes();
    }

    private static StoredFile toFile(String id, String name, String type, byte[] bytes) {
        if (bytes == null || bytes.length == 0) {
            return null;
        }
        StoredFile f = new StoredFile();
        f.setId(id);
        f.setOriginalName(name);
        f.setContentType(type);
        f.setBytes(bytes);
        return f;
    }

    @Override
    public Optional<PropertyListing> property(Long id) {
        List<PropertyListing> rows = jdbc.query("SELECT * FROM property_listing WHERE id=?", this::mapProperty, id);
        Optional<PropertyListing> listing = rows.stream().findFirst();
        listing.ifPresent(this::loadMedia);
        return listing;
    }

    @Override
    public List<PropertyListing> properties() {
        List<PropertyListing> list = jdbc.query("SELECT * FROM property_listing ORDER BY id", this::mapProperty);
        list.forEach(this::loadMedia);
        return list;
    }

    private void loadMedia(PropertyListing listing) {
        List<StoredFile> papers = jdbc.query(
                "SELECT * FROM property_paper WHERE property_id=?",
                (rs, row) -> {
                    StoredFile f = new StoredFile();
                    f.setId(rs.getString("file_id"));
                    f.setOriginalName(rs.getString("original_name"));
                    f.setContentType(rs.getString("content_type"));
                    f.setBytes(rs.getBytes("bytes"));
                    return f;
                },
                listing.getId());
        listing.setRegistryPapers(new ArrayList<>(papers));
        List<StoredFile> photos = jdbc.query(
                "SELECT * FROM property_photo WHERE property_id=? ORDER BY sort_order, id",
                (rs, row) -> {
                    StoredFile f = new StoredFile();
                    f.setId(rs.getString("file_id"));
                    f.setOriginalName(rs.getString("original_name"));
                    f.setContentType(rs.getString("content_type"));
                    f.setBytes(rs.getBytes("bytes"));
                    return f;
                },
                listing.getId());
        listing.setPropertyPhotos(new ArrayList<>(photos));
    }

    @Override
    public AuthenticatorApplication saveApplication(AuthenticatorApplication application) {
        if (application.getId() == null) {
            KeyHolder keys = new GeneratedKeyHolder();
            jdbc.update(con -> {
                var ps = con.prepareStatement(
                        """
                        INSERT INTO authenticator_application
                          (applicant_user_id, full_name, personal_email, phone, official_id_number, state, district, city, status, created_at)
                        VALUES (?,?,?,?,?,?,?,?,?,?)
                        """,
                        new String[] {"id"});
                ps.setLong(1, application.getApplicantUserId());
                ps.setString(2, application.getFullName());
                ps.setString(3, application.getPersonalEmail());
                ps.setString(4, application.getPhone());
                ps.setString(5, application.getOfficialIdNumber());
                ps.setString(6, application.getState());
                ps.setString(7, application.getDistrict());
                ps.setString(8, application.getCity());
                ps.setString(9, application.getStatus());
                ps.setTimestamp(10, Timestamp.from(application.getCreatedAt() == null ? Instant.now() : application.getCreatedAt()));
                return ps;
            }, keys);
            application.setId(keys.getKey().longValue());
        } else {
            jdbc.update(
                    """
                    UPDATE authenticator_application SET applicant_user_id=?, full_name=?, personal_email=?, phone=?,
                      official_id_number=?, state=?, district=?, city=?, status=? WHERE id=?
                    """,
                    application.getApplicantUserId(), application.getFullName(), application.getPersonalEmail(),
                    application.getPhone(), application.getOfficialIdNumber(), application.getState(),
                    application.getDistrict(), application.getCity(), application.getStatus(), application.getId());
        }
        return application;
    }

    @Override
    public Optional<AuthenticatorApplication> application(Long id) {
        return jdbc.query("SELECT * FROM authenticator_application WHERE id=?", this::mapApplication, id)
                .stream().findFirst();
    }

    @Override
    public List<AuthenticatorApplication> applications() {
        return jdbc.query("SELECT * FROM authenticator_application ORDER BY id", this::mapApplication);
    }

    @Override
    public ChatMessage saveMessage(ChatMessage message) {
        KeyHolder keys = new GeneratedKeyHolder();
        jdbc.update(con -> {
            var ps = con.prepareStatement(
                    "INSERT INTO chat_message (property_id, sender_id, body, blocked, created_at) VALUES (?,?,?,?,?)",
                    new String[] {"id"});
            ps.setLong(1, message.getPropertyId());
            ps.setLong(2, message.getSenderId());
            ps.setString(3, message.getBody());
            ps.setBoolean(4, message.isBlocked());
            ps.setTimestamp(5, Timestamp.from(message.getCreatedAt() == null ? Instant.now() : message.getCreatedAt()));
            return ps;
        }, keys);
        message.setId(keys.getKey().longValue());
        return message;
    }

    @Override
    public List<ChatMessage> messagesForProperty(Long propertyId) {
        return jdbc.query(
                "SELECT * FROM chat_message WHERE property_id=? ORDER BY id",
                this::mapMessage,
                propertyId);
    }

    @Override
    public void audit(Long actorId, String action, String detail) {
        jdbc.update(
                "INSERT INTO audit_event (actor_id, action, detail, created_at) VALUES (?,?,?,?)",
                actorId, action, detail, Timestamp.from(Instant.now()));
    }

    @Override
    public List<AuditEvent> audits() {
        return jdbc.query("SELECT * FROM audit_event ORDER BY id", (rs, row) -> {
            AuditEvent e = new AuditEvent();
            e.setId(rs.getLong("id"));
            long actor = rs.getLong("actor_id");
            e.setActorId(rs.wasNull() ? null : actor);
            e.setAction(rs.getString("action"));
            e.setDetail(rs.getString("detail"));
            Timestamp ts = rs.getTimestamp("created_at");
            if (ts != null) {
                e.setCreatedAt(ts.toInstant());
            }
            return e;
        });
    }

    @Override
    public void putGovernment(GovernmentRecord record) {
        String khasra = record.getKhasraNumber().trim();
        Timestamp updated = Timestamp.from(record.getUpdatedAt() == null ? Instant.now() : record.getUpdatedAt());
        int updatedRows = jdbc.update(
                """
                UPDATE government_record SET
                  ulpin=?, survey_number=?, khata_number=?, khewat_number=?, khatauni_number=?,
                  village=?, city=?, district=?, owner_name=?, measurements=?, owner_phone=?, updated_at=?
                WHERE khasra_number=?
                """,
                blankToNull(record.getUlpin()),
                blankToNull(record.getSurveyNumber()),
                blankToNull(record.getKhataNumber()),
                blankToNull(record.getKhewatNumber()),
                blankToNull(record.getKhatauniNumber()),
                record.getVillage(),
                record.getCity(),
                record.getDistrict(),
                record.getOwnerName(),
                record.getMeasurements(),
                record.getOwnerPhone(),
                updated,
                khasra);
        if (updatedRows == 0) {
            jdbc.update(
                    """
                    INSERT INTO government_record
                      (khasra_number, ulpin, survey_number, khata_number, khewat_number, khatauni_number,
                       village, city, district, owner_name, measurements, owner_phone, updated_at)
                    VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)
                    """,
                    khasra,
                    blankToNull(record.getUlpin()),
                    blankToNull(record.getSurveyNumber()),
                    blankToNull(record.getKhataNumber()),
                    blankToNull(record.getKhewatNumber()),
                    blankToNull(record.getKhatauniNumber()),
                    record.getVillage(),
                    record.getCity(),
                    record.getDistrict(),
                    record.getOwnerName(),
                    record.getMeasurements(),
                    record.getOwnerPhone(),
                    updated);
        }
    }

    @Override
    public Optional<GovernmentRecord> government(String khasra) {
        if (khasra == null) {
            return Optional.empty();
        }
        return jdbc.query(
                        "SELECT * FROM government_record WHERE lower(khasra_number)=lower(?)",
                        this::mapGovernment,
                        khasra.trim())
                .stream().findFirst();
    }

    @Override
    public Optional<GovernmentRecord> governmentByUlpin(String ulpin) {
        if (ulpin == null || ulpin.isBlank()) {
            return Optional.empty();
        }
        return jdbc.query(
                        "SELECT * FROM government_record WHERE upper(ulpin)=upper(?)",
                        this::mapGovernment,
                        ulpin.trim())
                .stream().findFirst();
    }

    @Override
    public Optional<GovernmentRecord> governmentBySurvey(String surveyNumber) {
        if (surveyNumber == null || surveyNumber.isBlank()) {
            return Optional.empty();
        }
        return jdbc.query(
                        "SELECT * FROM government_record WHERE lower(survey_number)=lower(?)",
                        this::mapGovernment,
                        surveyNumber.trim())
                .stream().findFirst();
    }

    @Override
    public List<GovernmentRecord> governmentRecords() {
        return jdbc.query("SELECT * FROM government_record ORDER BY khasra_number", this::mapGovernment);
    }

    private static String blankToNull(String value) {
        return value == null || value.isBlank() ? null : value.trim();
    }

    @Override
    public TransferCertificate saveCertificate(TransferCertificate certificate) {
        if (certificate.getId() == null) {
            KeyHolder keys = new GeneratedKeyHolder();
            jdbc.update(con -> {
                var ps = con.prepareStatement(
                        """
                        INSERT INTO transfer_certificate
                          (property_id, certificate_number, khasra_number, old_owner_name, new_owner_name, village,
                           city, district, state, measurements, officer_id, officer_name, issued_at, pdf_bytes)
                        VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)
                        """,
                        new String[] {"id"});
                ps.setLong(1, certificate.getPropertyId());
                ps.setString(2, certificate.getCertificateNumber());
                ps.setString(3, certificate.getKhasraNumber());
                ps.setString(4, certificate.getOldOwnerName());
                ps.setString(5, certificate.getNewOwnerName());
                ps.setString(6, certificate.getVillage());
                ps.setString(7, certificate.getCity());
                ps.setString(8, certificate.getDistrict());
                ps.setString(9, certificate.getState());
                ps.setString(10, certificate.getMeasurements());
                if (certificate.getOfficerId() == null) {
                    ps.setObject(11, null);
                } else {
                    ps.setLong(11, certificate.getOfficerId());
                }
                ps.setString(12, certificate.getOfficerName());
                ps.setTimestamp(13, Timestamp.from(certificate.getIssuedAt() == null ? Instant.now() : certificate.getIssuedAt()));
                ps.setBytes(14, certificate.getPdfBytes());
                return ps;
            }, keys);
            certificate.setId(keys.getKey().longValue());
        }
        return certificate;
    }

    @Override
    public Optional<TransferCertificate> certificate(Long id) {
        return jdbc.query("SELECT * FROM transfer_certificate WHERE id=?", this::mapCertificate, id)
                .stream().findFirst();
    }

    @Override
    public Notification saveNotification(Notification notification) {
        if (notification.getId() == null) {
            KeyHolder keys = new GeneratedKeyHolder();
            jdbc.update(con -> {
                var ps = con.prepareStatement(
                        "INSERT INTO notification (user_id, channel, subject, body, is_read, created_at) VALUES (?,?,?,?,?,?)",
                        new String[] {"id"});
                ps.setLong(1, notification.getUserId());
                ps.setString(2, notification.getChannel());
                ps.setString(3, notification.getSubject());
                ps.setString(4, notification.getBody());
                ps.setBoolean(5, notification.isRead());
                ps.setTimestamp(6, Timestamp.from(notification.getCreatedAt() == null ? Instant.now() : notification.getCreatedAt()));
                return ps;
            }, keys);
            notification.setId(keys.getKey().longValue());
        } else {
            jdbc.update(
                    "UPDATE notification SET user_id=?, channel=?, subject=?, body=?, is_read=? WHERE id=?",
                    notification.getUserId(), notification.getChannel(), notification.getSubject(),
                    notification.getBody(), notification.isRead(), notification.getId());
        }
        return notification;
    }

    @Override
    public Optional<Notification> notification(Long id) {
        return jdbc.query("SELECT * FROM notification WHERE id=?", this::mapNotification, id).stream().findFirst();
    }

    @Override
    public List<Notification> notificationsForUser(Long userId) {
        return jdbc.query(
                "SELECT * FROM notification WHERE user_id=? ORDER BY created_at DESC",
                this::mapNotification,
                userId);
    }

    @Override
    public long userCount() {
        Long count = jdbc.queryForObject("SELECT COUNT(*) FROM app_user", Long.class);
        return count == null ? 0 : count;
    }

    @Override
    public StateAdmin saveStateAdmin(StateAdmin admin) {
        if (admin.getAdminId() == null) {
            KeyHolder keys = new GeneratedKeyHolder();
            jdbc.update(con -> {
                var ps = con.prepareStatement(
                        """
                        INSERT INTO state_admin
                          (user_id, state_union_territory, email, phone, full_name, active, created_at)
                        VALUES (?,?,?,?,?,?,?)
                        """,
                        new String[] {"admin_id"});
                ps.setLong(1, admin.getUserId());
                ps.setString(2, admin.getStateUnionTerritory());
                ps.setString(3, admin.getEmail());
                ps.setString(4, admin.getPhone());
                ps.setString(5, admin.getFullName());
                ps.setBoolean(6, admin.isActive());
                ps.setTimestamp(7, Timestamp.from(admin.getCreatedAt() == null ? Instant.now() : admin.getCreatedAt()));
                return ps;
            }, keys);
            admin.setAdminId(keys.getKey().longValue());
        } else {
            jdbc.update(
                    """
                    UPDATE state_admin SET user_id=?, state_union_territory=?, email=?, phone=?, full_name=?, active=?
                    WHERE admin_id=?
                    """,
                    admin.getUserId(), admin.getStateUnionTerritory(), admin.getEmail(), admin.getPhone(),
                    admin.getFullName(), admin.isActive(), admin.getAdminId());
        }
        return admin;
    }

    @Override
    public Optional<StateAdmin> stateAdminByUserId(Long userId) {
        return jdbc.query("SELECT * FROM state_admin WHERE user_id=?", this::mapStateAdmin, userId)
                .stream().findFirst();
    }

    @Override
    public Optional<StateAdmin> stateAdmin(Long adminId) {
        return jdbc.query("SELECT * FROM state_admin WHERE admin_id=?", this::mapStateAdmin, adminId)
                .stream().findFirst();
    }

    @Override
    public List<StateAdmin> stateAdmins() {
        return jdbc.query("SELECT * FROM state_admin ORDER BY admin_id", this::mapStateAdmin);
    }

    private StateAdmin mapStateAdmin(ResultSet rs, int row) throws SQLException {
        StateAdmin a = new StateAdmin();
        a.setAdminId(rs.getLong("admin_id"));
        a.setUserId(rs.getLong("user_id"));
        a.setStateUnionTerritory(rs.getString("state_union_territory"));
        a.setEmail(rs.getString("email"));
        a.setPhone(rs.getString("phone"));
        a.setFullName(rs.getString("full_name"));
        a.setActive(rs.getBoolean("active"));
        a.setCreatedAt(instant(rs.getTimestamp("created_at")));
        return a;
    }

    private UserAccount mapUser(ResultSet rs, int row) throws SQLException {
        UserAccount u = new UserAccount();
        u.setId(rs.getLong("id"));
        u.setEmail(rs.getString("email"));
        u.setPhone(rs.getString("phone"));
        u.setPasswordHash(rs.getString("password_hash"));
        u.setFullName(rs.getString("full_name"));
        u.setRole(Role.valueOf(rs.getString("role")));
        u.setState(rs.getString("state"));
        u.setDistrict(rs.getString("district"));
        u.setCity(rs.getString("city"));
        u.setActive(rs.getBoolean("active"));
        u.setOfficialLogin(rs.getString("official_login"));
        Timestamp created = rs.getTimestamp("created_at");
        if (created != null) {
            u.setCreatedAt(created.toInstant());
        }
        return u;
    }

    private PropertyListing mapProperty(ResultSet rs, int row) throws SQLException {
        PropertyListing p = new PropertyListing();
        p.setId(rs.getLong("id"));
        p.setSellerId(rs.getLong("seller_id"));
        long buyer = rs.getLong("buyer_id");
        p.setBuyerId(rs.wasNull() ? null : buyer);
        p.setPurpose(ListingPurpose.valueOf(rs.getString("purpose")));
        p.setType(PropertyType.valueOf(rs.getString("type")));
        p.setStatus(PropertyStatus.valueOf(rs.getString("status")));
        p.setTitle(rs.getString("title"));
        p.setState(rs.getString("state"));
        p.setDistrict(rs.getString("district"));
        p.setCity(rs.getString("city"));
        p.setAddress(rs.getString("address"));
        double price = rs.getDouble("asking_price");
        p.setAskingPrice(rs.wasNull() ? null : price);
        p.setMeasurements(rs.getString("measurements"));
        p.setKhasraNumber(rs.getString("khasra_number"));
        p.setUlpin(rs.getString("ulpin"));
        p.setSurveyNumber(rs.getString("survey_number"));
        p.setKhataNumber(rs.getString("khata_number"));
        p.setKhewatNumber(rs.getString("khewat_number"));
        p.setKhatauniNumber(rs.getString("khatauni_number"));
        p.setRegistryDetail(rs.getString("registry_detail"));
        p.setHouseNumber(rs.getString("house_number"));
        boolean furnished = rs.getBoolean("furnished");
        p.setFurnished(rs.wasNull() ? null : furnished);
        p.setFlatNumber(rs.getString("flat_number"));
        int floor = rs.getInt("floor");
        p.setFloor(rs.wasNull() ? null : floor);
        int bedrooms = rs.getInt("bedrooms");
        p.setBedrooms(rs.wasNull() ? null : bedrooms);
        p.setExtraNotes(rs.getString("extra_notes"));
        p.setAiSummary(rs.getString("ai_summary"));
        p.setOfficerRemarks(rs.getString("officer_remarks"));
        long cert = rs.getLong("certificate_id");
        p.setCertificateId(rs.wasNull() ? null : cert);
        double lat = rs.getDouble("latitude");
        p.setLatitude(rs.wasNull() ? null : lat);
        double lng = rs.getDouble("longitude");
        p.setLongitude(rs.wasNull() ? null : lng);
        p.setVerificationReport(toFile(
                rs.getString("verification_report_id"),
                rs.getString("verification_report_name"),
                rs.getString("verification_report_type"),
                rs.getBytes("verification_report_bytes")));
        p.setVirtualJamabandi(toFile(
                rs.getString("virtual_jamabandi_id"),
                rs.getString("virtual_jamabandi_name"),
                rs.getString("virtual_jamabandi_type"),
                rs.getBytes("virtual_jamabandi_bytes")));
        p.setPurchaseRequestedAt(instant(rs.getTimestamp("purchase_requested_at")));
        p.setSaleConfirmedAt(instant(rs.getTimestamp("sale_confirmed_at")));
        p.setTransferredAt(instant(rs.getTimestamp("transferred_at")));
        p.setCreatedAt(instant(rs.getTimestamp("created_at")));
        p.setUpdatedAt(instant(rs.getTimestamp("updated_at")));
        return p;
    }

    private AuthenticatorApplication mapApplication(ResultSet rs, int row) throws SQLException {
        AuthenticatorApplication a = new AuthenticatorApplication();
        a.setId(rs.getLong("id"));
        a.setApplicantUserId(rs.getLong("applicant_user_id"));
        a.setFullName(rs.getString("full_name"));
        a.setPersonalEmail(rs.getString("personal_email"));
        a.setPhone(rs.getString("phone"));
        a.setOfficialIdNumber(rs.getString("official_id_number"));
        a.setState(rs.getString("state"));
        a.setDistrict(rs.getString("district"));
        a.setCity(rs.getString("city"));
        a.setStatus(rs.getString("status"));
        a.setCreatedAt(instant(rs.getTimestamp("created_at")));
        return a;
    }

    private ChatMessage mapMessage(ResultSet rs, int row) throws SQLException {
        ChatMessage m = new ChatMessage();
        m.setId(rs.getLong("id"));
        m.setPropertyId(rs.getLong("property_id"));
        m.setSenderId(rs.getLong("sender_id"));
        m.setBody(rs.getString("body"));
        m.setBlocked(rs.getBoolean("blocked"));
        m.setCreatedAt(instant(rs.getTimestamp("created_at")));
        return m;
    }

    private GovernmentRecord mapGovernment(ResultSet rs, int row) throws SQLException {
        GovernmentRecord g = new GovernmentRecord(
                rs.getString("khasra_number"),
                rs.getString("village"),
                rs.getString("city"),
                rs.getString("district"),
                rs.getString("owner_name"),
                rs.getString("measurements"));
        g.setUlpin(rs.getString("ulpin"));
        g.setSurveyNumber(rs.getString("survey_number"));
        g.setKhataNumber(rs.getString("khata_number"));
        g.setKhewatNumber(rs.getString("khewat_number"));
        g.setKhatauniNumber(rs.getString("khatauni_number"));
        g.setOwnerPhone(rs.getString("owner_phone"));
        g.setUpdatedAt(instant(rs.getTimestamp("updated_at")));
        return g;
    }

    private TransferCertificate mapCertificate(ResultSet rs, int row) throws SQLException {
        TransferCertificate c = new TransferCertificate();
        c.setId(rs.getLong("id"));
        c.setPropertyId(rs.getLong("property_id"));
        c.setCertificateNumber(rs.getString("certificate_number"));
        c.setKhasraNumber(rs.getString("khasra_number"));
        c.setOldOwnerName(rs.getString("old_owner_name"));
        c.setNewOwnerName(rs.getString("new_owner_name"));
        c.setVillage(rs.getString("village"));
        c.setCity(rs.getString("city"));
        c.setDistrict(rs.getString("district"));
        c.setState(rs.getString("state"));
        c.setMeasurements(rs.getString("measurements"));
        long officer = rs.getLong("officer_id");
        c.setOfficerId(rs.wasNull() ? null : officer);
        c.setOfficerName(rs.getString("officer_name"));
        c.setIssuedAt(instant(rs.getTimestamp("issued_at")));
        c.setPdfBytes(rs.getBytes("pdf_bytes"));
        return c;
    }

    private Notification mapNotification(ResultSet rs, int row) throws SQLException {
        Notification n = new Notification();
        n.setId(rs.getLong("id"));
        n.setUserId(rs.getLong("user_id"));
        n.setChannel(rs.getString("channel"));
        n.setSubject(rs.getString("subject"));
        n.setBody(rs.getString("body"));
        n.setRead(rs.getBoolean("is_read"));
        n.setCreatedAt(instant(rs.getTimestamp("created_at")));
        return n;
    }

    private Timestamp ts(Instant instant) {
        return instant == null ? null : Timestamp.from(instant);
    }

    private Instant instant(Timestamp timestamp) {
        return timestamp == null ? null : timestamp.toInstant();
    }
}
