-- schema.sql

PRAGMA foreign_keys = ON; -- Enforce foreign key constraints

-- Table for the main salary report information
CREATE TABLE SalaryReports (
    ReportID INTEGER PRIMARY KEY, -- Auto-incrementing is default for INTEGER PRIMARY KEY
    Country TEXT,
    YearsCodePro REAL, -- Use REAL for potential non-integer years or NULLs
    ConvertedCompYearly REAL, -- Use REAL for currency or NULLs
    Year INTEGER
);

-- Table for unique tags and their types
CREATE TABLE Tags (
    TagID INTEGER PRIMARY KEY,
    TagName TEXT NOT NULL,
    TagType TEXT NOT NULL,
    UNIQUE(TagName, TagType) -- Ensure no duplicate tag/type combinations
);

-- Linking table for the many-to-many relationship
CREATE TABLE SalaryReportTags (
    ReportID INTEGER NOT NULL,
    TagID INTEGER NOT NULL,
    PRIMARY KEY (ReportID, TagID), -- Composite primary key prevents duplicate links
    FOREIGN KEY (ReportID) REFERENCES SalaryReports(ReportID) ON DELETE CASCADE,
    FOREIGN KEY (TagID) REFERENCES Tags(TagID) ON DELETE CASCADE
);

-- Optional: Indexes for performance on lookups/joins
CREATE INDEX idx_report_year ON SalaryReports(Year);
CREATE INDEX idx_tag_name ON Tags(TagName);
CREATE INDEX idx_link_tagid ON SalaryReportTags(TagID);
CREATE INDEX idx_tag_type ON Tags(TagType);