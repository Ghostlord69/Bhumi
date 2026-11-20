package com.landregistry.certificate;

import com.landregistry.domain.TransferCertificate;
import com.lowagie.text.Document;
import com.lowagie.text.Element;
import com.lowagie.text.Font;
import com.lowagie.text.FontFactory;
import com.lowagie.text.PageSize;
import com.lowagie.text.Paragraph;
import com.lowagie.text.Rectangle;
import com.lowagie.text.pdf.PdfContentByte;
import com.lowagie.text.pdf.PdfWriter;
import java.awt.Color;
import java.io.ByteArrayOutputStream;
import java.time.ZoneId;
import java.time.format.DateTimeFormatter;
import org.springframework.stereotype.Service;

@Service
public class CertificateService {
    private static final DateTimeFormatter DATE = DateTimeFormatter.ofPattern("dd MMMM yyyy")
            .withZone(ZoneId.of("Asia/Kolkata"));

    public byte[] render(TransferCertificate cert) {
        try {
            ByteArrayOutputStream out = new ByteArrayOutputStream();
            Document document = new Document(PageSize.A4, 48, 48, 56, 56);
            PdfWriter writer = PdfWriter.getInstance(document, out);
            document.open();

            PdfContentByte canvas = writer.getDirectContent();
            Rectangle page = document.getPageSize();
            canvas.setColorStroke(new Color(31, 107, 69));
            canvas.setLineWidth(2.5f);
            canvas.rectangle(28, 28, page.getWidth() - 56, page.getHeight() - 56);
            canvas.stroke();
            canvas.setLineWidth(0.8f);
            canvas.rectangle(34, 34, page.getWidth() - 68, page.getHeight() - 68);
            canvas.stroke();

            Font title = FontFactory.getFont(FontFactory.TIMES_BOLD, 18, new Color(18, 35, 26));
            Font subtitle = FontFactory.getFont(FontFactory.HELVETICA_BOLD, 12, new Color(31, 107, 69));
            Font body = FontFactory.getFont(FontFactory.TIMES_ROMAN, 11, Color.DARK_GRAY);
            Font label = FontFactory.getFont(FontFactory.HELVETICA_BOLD, 10, Color.BLACK);
            Font small = FontFactory.getFont(FontFactory.HELVETICA, 9, Color.GRAY);

            Paragraph emblem = new Paragraph("◉", FontFactory.getFont(FontFactory.HELVETICA, 28, new Color(196, 165, 116)));
            emblem.setAlignment(Element.ALIGN_CENTER);
            document.add(emblem);

            Paragraph gov = new Paragraph("GOVERNMENT OF HARYANA", title);
            gov.setAlignment(Element.ALIGN_CENTER);
            document.add(gov);

            Paragraph dept = new Paragraph("District Land Records & Registration Office", subtitle);
            dept.setAlignment(Element.ALIGN_CENTER);
            dept.setSpacingAfter(6);
            document.add(dept);

            Paragraph heading = new Paragraph("CERTIFICATE OF TRANSFER OF OWNERSHIP", title);
            heading.setAlignment(Element.ALIGN_CENTER);
            heading.setSpacingBefore(10);
            heading.setSpacingAfter(18);
            document.add(heading);

            document.add(line("Certificate No.", cert.getCertificateNumber(), label, body));
            document.add(line("Date of Issue", DATE.format(cert.getIssuedAt()), label, body));
            document.add(line("District", cert.getDistrict() + ", " + cert.getState(), label, body));
            document.add(line("Tehsil / City", cert.getCity(), label, body));
            document.add(line("Village", nullToDash(cert.getVillage()), label, body));
            document.add(line("Khasra / Survey No.", nullToDash(cert.getKhasraNumber()), label, body));
            document.add(line("Measurements", nullToDash(cert.getMeasurements()), label, body));
            document.add(line("Previous Owner", nullToDash(cert.getOldOwnerName()), label, body));
            document.add(line("New Owner (Transferee)", nullToDash(cert.getNewOwnerName()), label, body));
            document.add(line("Property Reference", "Listing #" + cert.getPropertyId(), label, body));
            document.add(line("Issuing Officer", nullToDash(cert.getOfficerName()), label, body));

            Paragraph declaration = new Paragraph(
                    "\nThis is to certify that, pursuant to verification of registry papers and government land records "
                            + "maintained by the District Land Records Office, the ownership of the above-mentioned property "
                            + "has been transferred and the government record has been updated accordingly. "
                            + "This certificate is issued for the purpose of proving lawful transfer of ownership "
                            + "and may be produced before competent authorities.",
                    body);
            declaration.setSpacingBefore(14);
            declaration.setSpacingAfter(28);
            document.add(declaration);

            Paragraph seal = new Paragraph(
                    "______________________________\nOfficial Seal & Signature\nPatwari / Tehsildar\n" + cert.getCity(),
                    small);
            seal.setAlignment(Element.ALIGN_RIGHT);
            document.add(seal);

            Paragraph footer = new Paragraph(
                    "\nGenerated by Bhumi Land Registry (demo). Not a substitute for a stamped physical registry deed.",
                    small);
            footer.setAlignment(Element.ALIGN_CENTER);
            footer.setSpacingBefore(36);
            document.add(footer);

            document.close();
            return out.toByteArray();
        } catch (Exception ex) {
            throw new IllegalStateException("Could not generate transfer certificate", ex);
        }
    }

    private Paragraph line(String key, String value, Font label, Font body) {
        Paragraph p = new Paragraph();
        p.add(new com.lowagie.text.Chunk(key + ":  ", label));
        p.add(new com.lowagie.text.Chunk(value == null ? "—" : value, body));
        p.setSpacingAfter(6);
        return p;
    }

    private String nullToDash(String value) {
        return value == null || value.isBlank() ? "—" : value;
    }
}
