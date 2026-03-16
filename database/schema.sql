CREATE TABLE IF NOT EXISTS campaigns (
    campaign_id INTEGER PRIMARY KEY,
    campaign_name TEXT,
    platform TEXT,
    industry TEXT,
    budget REAL,
    impressions INTEGER,
    clicks INTEGER,
    conversions INTEGER,
    cost REAL,
    roi REAL,
    region TEXT,
    funnel_stage TEXT
);

CREATE TABLE IF NOT EXISTS audience_segments (
    segment_id INTEGER PRIMARY KEY,
    industry TEXT,
    company_size TEXT,
    role TEXT,
    region TEXT,
    historical_roi REAL,
    cac REAL
);

CREATE TABLE IF NOT EXISTS platform_metrics (
    platform TEXT PRIMARY KEY,
    avg_ctr REAL,
    avg_cvr REAL,
    avg_cac REAL,
    avg_roi REAL
);

CREATE TABLE IF NOT EXISTS messaging_themes (
    theme_id INTEGER PRIMARY KEY,
    theme TEXT,
    target_role TEXT,
    platform TEXT,
    conversion_rate REAL,
    notes TEXT
);

CREATE TABLE IF NOT EXISTS keywords (
    keyword TEXT PRIMARY KEY,
    category TEXT,
    search_volume INTEGER,
    trend_score REAL
);