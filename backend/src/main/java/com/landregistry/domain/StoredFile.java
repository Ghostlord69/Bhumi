package com.landregistry.domain;

public class StoredFile {
    private String id;
    private String originalName;
    private String contentType;
    private byte[] bytes;

    public String getId() { return id; }
    public void setId(String id) { this.id = id; }
    public String getOriginalName() { return originalName; }
    public void setOriginalName(String originalName) { this.originalName = originalName; }
    public String getContentType() { return contentType; }
    public void setContentType(String contentType) { this.contentType = contentType; }
    public byte[] getBytes() { return bytes; }
    public void setBytes(byte[] bytes) { this.bytes = bytes; }
}
