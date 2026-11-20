package com.landregistry.certificate;

import com.landregistry.domain.PropertyListing;
import com.landregistry.domain.StoredFile;
import com.landregistry.domain.UserAccount;
import java.awt.Color;
import java.awt.Font;
import java.awt.Graphics2D;
import java.awt.RenderingHints;
import java.awt.image.BufferedImage;
import java.io.ByteArrayOutputStream;
import java.nio.charset.StandardCharsets;
import java.util.UUID;
import java.util.zip.CRC32;
import javax.imageio.ImageIO;
import org.springframework.stereotype.Service;

/** Generates a demo virtual jamabandi PNG with embedded bhumi_meta for later AI short-circuit. */
@Service
public class VirtualJamabandiService {

    public StoredFile generate(PropertyListing listing, UserAccount owner) {
        try {
            BufferedImage image = new BufferedImage(900, 1200, BufferedImage.TYPE_INT_RGB);
            Graphics2D g = image.createGraphics();
            g.setRenderingHint(RenderingHints.KEY_TEXT_ANTIALIASING, RenderingHints.VALUE_TEXT_ANTIALIAS_ON);
            g.setColor(new Color(252, 248, 235));
            g.fillRect(0, 0, 900, 1200);
            g.setColor(new Color(40, 60, 40));
            g.setFont(new Font("SansSerif", Font.BOLD, 28));
            g.drawString("BHUMI — Virtual Jamabandi (Demo)", 40, 60);
            g.setFont(new Font("SansSerif", Font.PLAIN, 18));
            int y = 120;
            y = line(g, y, "Owner", owner != null ? owner.getFullName() : "Owner");
            y = line(g, y, "Address", nullSafe(listing.getAddress()) + ", " + nullSafe(listing.getCity()));
            y = line(g, y, "District / State", nullSafe(listing.getDistrict()) + " / " + nullSafe(listing.getState()));
            y = line(g, y, "ULPIN", nullSafe(listing.getUlpin()));
            y = line(g, y, "Khasra / Survey", first(listing.getKhasraNumber(), listing.getSurveyNumber()));
            y = line(g, y, "Khata", nullSafe(listing.getKhataNumber()));
            y = line(g, y, "Khewat", nullSafe(listing.getKhewatNumber()));
            y = line(g, y, "Khatauni", nullSafe(listing.getKhatauniNumber()));
            y = line(g, y, "Measurements", nullSafe(listing.getMeasurements()));
            if (listing.getLatitude() != null && listing.getLongitude() != null) {
                y = line(g, y, "Lat / Lng", listing.getLatitude() + ", " + listing.getLongitude());
            }
            g.setFont(new Font("SansSerif", Font.ITALIC, 14));
            g.drawString("Not an official government document — classroom demo only.", 40, 1140);
            g.dispose();

            ByteArrayOutputStream raw = new ByteArrayOutputStream();
            ImageIO.write(image, "png", raw);
            String meta = metaJson(listing, owner);
            byte[] png = injectTextChunk(raw.toByteArray(), "bhumi_meta", meta);

            StoredFile file = new StoredFile();
            file.setId(UUID.randomUUID().toString());
            file.setOriginalName("virtual-jamabandi-" + listing.getId() + ".png");
            file.setContentType("image/png");
            file.setBytes(png);
            return file;
        } catch (Exception ex) {
            throw new IllegalStateException("Could not generate virtual jamabandi", ex);
        }
    }

    private static int line(Graphics2D g, int y, String label, String value) {
        g.setColor(new Color(80, 80, 80));
        g.drawString(label + ":", 40, y);
        g.setColor(Color.BLACK);
        g.drawString(value == null || value.isBlank() ? "—" : value, 220, y);
        return y + 36;
    }

    private static String metaJson(PropertyListing listing, UserAccount owner) {
        String ownerName = owner == null ? "" : escape(owner.getFullName());
        return "{"
                + "\"ulpin\":\"" + escape(listing.getUlpin()) + "\","
                + "\"khasraNumber\":\"" + escape(listing.getKhasraNumber()) + "\","
                + "\"surveyNumber\":\"" + escape(listing.getSurveyNumber()) + "\","
                + "\"khataNumber\":\"" + escape(listing.getKhataNumber()) + "\","
                + "\"khewatNumber\":\"" + escape(listing.getKhewatNumber()) + "\","
                + "\"khatauniNumber\":\"" + escape(listing.getKhatauniNumber()) + "\","
                + "\"ownerName\":\"" + ownerName + "\","
                + "\"village\":\"" + escape(listing.getCity()) + "\","
                + "\"district\":\"" + escape(listing.getDistrict()) + "\","
                + "\"state\":\"" + escape(listing.getState()) + "\","
                + "\"areaAcres\":null,"
                + "\"measurements\":\"" + escape(listing.getMeasurements()) + "\","
                + "\"landType\":\"AGRICULTURAL\","
                + "\"latitude\":" + (listing.getLatitude() == null ? "null" : listing.getLatitude()) + ","
                + "\"longitude\":" + (listing.getLongitude() == null ? "null" : listing.getLongitude())
                + "}";
    }

    private static String escape(String s) {
        if (s == null) return "";
        return s.replace("\\", "\\\\").replace("\"", "\\\"");
    }

    private static String nullSafe(String s) {
        return s == null ? "" : s;
    }

    private static String first(String a, String b) {
        if (a != null && !a.isBlank()) return a;
        return nullSafe(b);
    }

    /** Insert a PNG tEXt chunk before IEND so PIL can read image.info['bhumi_meta']. */
    static byte[] injectTextChunk(byte[] png, String key, String value) throws Exception {
        byte[] keyword = key.getBytes(StandardCharsets.ISO_8859_1);
        byte[] text = value.getBytes(StandardCharsets.ISO_8859_1);
        byte[] data = new byte[keyword.length + 1 + text.length];
        System.arraycopy(keyword, 0, data, 0, keyword.length);
        data[keyword.length] = 0;
        System.arraycopy(text, 0, data, keyword.length + 1, text.length);

        byte[] type = "tEXt".getBytes(StandardCharsets.US_ASCII);
        byte[] length = intBytes(data.length);
        CRC32 crc = new CRC32();
        crc.update(type);
        crc.update(data);
        byte[] crcBytes = intBytes((int) crc.getValue());

        int iend = indexOf(png, new byte[]{0, 0, 0, 0, 'I', 'E', 'N', 'D'});
        if (iend < 0) {
            return png;
        }
        ByteArrayOutputStream out = new ByteArrayOutputStream(png.length + data.length + 12);
        out.write(png, 0, iend);
        out.write(length);
        out.write(type);
        out.write(data);
        out.write(crcBytes);
        out.write(png, iend, png.length - iend);
        return out.toByteArray();
    }

    private static byte[] intBytes(int n) {
        return new byte[]{
                (byte) ((n >>> 24) & 0xff),
                (byte) ((n >>> 16) & 0xff),
                (byte) ((n >>> 8) & 0xff),
                (byte) (n & 0xff)
        };
    }

    private static int indexOf(byte[] hay, byte[] needle) {
        outer:
        for (int i = 0; i <= hay.length - needle.length; i++) {
            for (int j = 0; j < needle.length; j++) {
                if (hay[i + j] != needle[j]) continue outer;
            }
            return i;
        }
        return -1;
    }
}
