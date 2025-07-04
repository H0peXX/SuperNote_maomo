-- 1. USERS
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    username VARCHAR UNIQUE,
    email VARCHAR UNIQUE,
    password_hash VARCHAR,
    created_at TIMESTAMP DEFAULT NOW()
);


-- 2. TEAMS
CREATE TABLE teams (
    id UUID PRIMARY KEY,
    name VARCHAR UNIQUE,
    description TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);

-- 3. TEAM MEMBERS
CREATE TABLE team_members (
    id UUID PRIMARY KEY,
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    team_id UUID REFERENCES teams(id) ON DELETE CASCADE,
    role VARCHAR, -- e.g., 'admin', 'member'
    joined_at TIMESTAMP DEFAULT NOW()
);

-- 4. PDF FILES
CREATE TABLE pdf_files (
    id UUID PRIMARY KEY,
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    team_id UUID REFERENCES teams(id) ON DELETE SET NULL,
    file_name VARCHAR,
    original_text TEXT,
    formatted_text TEXT,
    summary TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);

-- 5. TEAM SUMMARY (รวม note/summaries ของทีม)
CREATE TABLE team_summary (
    id UUID PRIMARY KEY,
    team_id UUID REFERENCES teams(id) ON DELETE CASCADE,
    aggregated_summary TEXT,
    updated_at TIMESTAMP DEFAULT NOW()
);

-- 6. TEAM SUMMARY - PDF FILES (ความสัมพันธ์ระหว่างสรุปรวมกับ PDF)
CREATE TABLE team_summary_pdf (
    id UUID PRIMARY KEY,
    team_summary_id UUID REFERENCES team_summary(id) ON DELETE CASCADE,
    pdf_file_id UUID REFERENCES pdf_files(id) ON DELETE CASCADE
);
