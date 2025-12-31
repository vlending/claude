-- ================================================
-- 먹은대로 (Eat-As-You-Eat) MVP Database Schema
-- PostgreSQL 15+
-- Version: 1.0
-- Date: 2025-12-31
-- ================================================

-- Extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- ================================================
-- 1. USERS & AUTHENTICATION
-- ================================================

CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL, -- bcrypt

    -- Profile
    gender VARCHAR(10) NOT NULL CHECK (gender IN ('male', 'female', 'other')),
    age_group VARCHAR(10) NOT NULL CHECK (age_group IN ('20s', '30s', '40s', '50s', '60s+')),
    height_cm NUMERIC(5,2),
    current_weight_kg NUMERIC(5,2),

    -- Goals (bit flags or JSON array)
    health_goals JSONB NOT NULL DEFAULT '[]', -- ["weight", "bp", "lipid", "glucose", "gerd"]

    -- Medications
    medications JSONB DEFAULT '[]', -- ["bp_med", "statin", "diabetes_med", "ppi", "other"]

    -- Allergies
    allergies JSONB DEFAULT '[]', -- ["dairy", "nuts", "gluten", "shellfish", "soy"]

    -- Settings
    timezone VARCHAR(50) DEFAULT 'Asia/Seoul',
    notification_enabled BOOLEAN DEFAULT TRUE,
    daily_report_time TIME DEFAULT '21:00:00',

    -- Metadata
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    last_login_at TIMESTAMP WITH TIME ZONE,
    is_active BOOLEAN DEFAULT TRUE
);

CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_created_at ON users(created_at);

-- ================================================
-- 2. HEALTH CHECK DATA
-- ================================================

CREATE TABLE health_checks (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,

    -- Metadata
    check_date DATE NOT NULL,
    institution VARCHAR(255), -- 검진 병원명
    source_file_url TEXT, -- S3 URL of uploaded report
    parse_confidence NUMERIC(3,2) DEFAULT 0.0, -- 0.0 ~ 1.0
    is_manual_entry BOOLEAN DEFAULT FALSE,

    -- Blood Pressure
    bp_systolic INTEGER, -- mmHg
    bp_diastolic INTEGER, -- mmHg

    -- Glucose
    fasting_glucose INTEGER, -- mg/dL
    hba1c NUMERIC(4,2), -- %

    -- Lipid Panel
    total_cholesterol INTEGER, -- mg/dL
    ldl_cholesterol INTEGER, -- mg/dL
    hdl_cholesterol INTEGER, -- mg/dL
    triglycerides INTEGER, -- mg/dL

    -- Liver Function
    ast INTEGER, -- U/L
    alt INTEGER, -- U/L
    ggt INTEGER, -- U/L

    -- Kidney Function
    creatinine NUMERIC(4,2), -- mg/dL
    egfr NUMERIC(5,1), -- mL/min/1.73m²

    -- Other
    uric_acid NUMERIC(4,2), -- mg/dL
    waist_cm NUMERIC(5,2), -- cm
    bmi NUMERIC(4,2), -- kg/m²

    -- Risk Levels (auto-computed)
    risk_profile JSONB, -- {"bp": "high", "lipid": "moderate", "glucose": "normal", ...}

    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_health_checks_user_id ON health_checks(user_id);
CREATE INDEX idx_health_checks_check_date ON health_checks(check_date DESC);

-- ================================================
-- 3. MEALS
-- ================================================

CREATE TABLE meals (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,

    -- Timing
    meal_time TIMESTAMP WITH TIME ZONE NOT NULL,
    meal_type VARCHAR(20), -- 'breakfast', 'lunch', 'dinner', 'snack'

    -- Images
    pre_photo_url TEXT, -- 식전 사진 (S3 URL)
    post_photo_url TEXT, -- 식후 사진 (S3 URL)

    -- User Input
    user_text TEXT, -- 사용자가 입력한 메뉴/재료 설명
    user_adjustments JSONB, -- {"portion": 0.5, "no_sauce": true, ...}

    -- AI Analysis
    detected_foods JSONB NOT NULL DEFAULT '[]',
    -- [{"name": "삼겹살", "portion": "150g", "confidence": 0.85}, ...]

    -- Nutritional Values
    total_kcal INTEGER,
    carbs_g NUMERIC(6,2),
    protein_g NUMERIC(6,2),
    fat_g NUMERIC(6,2),
    saturated_fat_g NUMERIC(6,2),
    fiber_g NUMERIC(6,2),
    sugar_g NUMERIC(6,2),
    sodium_mg INTEGER,

    -- Pre-meal Decision
    decision VARCHAR(10), -- 'RED', 'YELLOW', 'GREEN'
    decision_reasoning JSONB, -- [{"reason": "...", "metric": "sodium", "value": 1200}, ...]
    alternative_suggestions JSONB, -- [{"name": "...", "why": "..."}, ...]

    -- Flags
    health_flags JSONB, -- ["high_sodium", "high_sugar", "gerd_trigger", ...]

    -- AI Metadata
    model_version VARCHAR(50),
    confidence NUMERIC(3,2) DEFAULT 0.0, -- Overall confidence 0.0 ~ 1.0
    assumptions TEXT[], -- ["1인분 기준", "소스 포함 가정", ...]

    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_meals_user_id ON meals(user_id);
CREATE INDEX idx_meals_meal_time ON meals(meal_time DESC);
CREATE INDEX idx_meals_decision ON meals(decision);

-- ================================================
-- 4. DAILY SUMMARIES
-- ================================================

CREATE TABLE daily_summaries (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    date DATE NOT NULL,

    -- Aggregated Nutrition
    total_kcal INTEGER DEFAULT 0,
    total_carbs_g NUMERIC(7,2) DEFAULT 0,
    total_protein_g NUMERIC(7,2) DEFAULT 0,
    total_fat_g NUMERIC(7,2) DEFAULT 0,
    total_sodium_mg INTEGER DEFAULT 0,
    total_sugar_g NUMERIC(7,2) DEFAULT 0,

    -- Meal Counts
    meal_count INTEGER DEFAULT 0,
    pre_meal_count INTEGER DEFAULT 0, -- 식전 업로드 횟수
    red_count INTEGER DEFAULT 0,
    yellow_count INTEGER DEFAULT 0,
    green_count INTEGER DEFAULT 0,

    -- Goal Scores (0~100)
    weight_score INTEGER DEFAULT 0,
    bp_score INTEGER DEFAULT 0,
    lipid_score INTEGER DEFAULT 0,
    glucose_score INTEGER DEFAULT 0,
    gerd_score INTEGER DEFAULT 0,

    -- Missions
    missions_completed JSONB DEFAULT '[]', -- ["sodium_under_800", "no_late_night", ...]

    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),

    UNIQUE(user_id, date)
);

CREATE INDEX idx_daily_summaries_user_date ON daily_summaries(user_id, date DESC);

-- ================================================
-- 5. WEEKLY REPORTS
-- ================================================

CREATE TABLE weekly_reports (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,

    week_start_date DATE NOT NULL, -- Monday
    week_end_date DATE NOT NULL,   -- Sunday

    -- Avg Scores
    avg_weight_score INTEGER,
    avg_bp_score INTEGER,
    avg_lipid_score INTEGER,
    avg_glucose_score INTEGER,
    avg_gerd_score INTEGER,

    -- Analysis
    top_3_problems JSONB, -- [{"issue": "...", "frequency": 5}, ...]
    top_3_wins JSONB, -- [{"habit": "...", "days": 6}, ...]
    next_week_missions JSONB, -- [{"mission": "...", "points": 20}, ...]

    -- Stats
    total_meals INTEGER,
    avg_kcal_per_day INTEGER,
    streak_days INTEGER,

    -- Metadata
    generated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),

    UNIQUE(user_id, week_start_date)
);

CREATE INDEX idx_weekly_reports_user_week ON weekly_reports(user_id, week_start_date DESC);

-- ================================================
-- 6. GAMIFICATION
-- ================================================

CREATE TABLE user_gamification (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,

    -- Streak
    current_streak INTEGER DEFAULT 0,
    longest_streak INTEGER DEFAULT 0,
    last_logged_date DATE,

    -- Badges
    badges JSONB DEFAULT '[]',
    -- [{"badge_id": "streak_7", "earned_at": "2025-01-01"}, ...]

    -- Points
    total_points INTEGER DEFAULT 0,

    -- Level (optional)
    level INTEGER DEFAULT 1,

    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),

    UNIQUE(user_id)
);

CREATE INDEX idx_gamification_user_id ON user_gamification(user_id);

-- ================================================
-- 7. NOTIFICATIONS
-- ================================================

CREATE TABLE notifications (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,

    type VARCHAR(50) NOT NULL, -- 'daily_report', 'weekly_report', 'mission', 'badge'
    title VARCHAR(255) NOT NULL,
    body TEXT NOT NULL,

    -- Delivery
    is_read BOOLEAN DEFAULT FALSE,
    sent_at TIMESTAMP WITH TIME ZONE,
    read_at TIMESTAMP WITH TIME ZONE,

    -- Metadata
    data JSONB, -- Additional context

    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_notifications_user_id ON notifications(user_id);
CREATE INDEX idx_notifications_sent_at ON notifications(sent_at DESC);
CREATE INDEX idx_notifications_is_read ON notifications(is_read);

-- ================================================
-- 8. FILE UPLOADS
-- ================================================

CREATE TABLE file_uploads (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,

    file_type VARCHAR(50) NOT NULL, -- 'health_check', 'meal_pre', 'meal_post'
    file_url TEXT NOT NULL, -- S3 URL
    file_size_bytes BIGINT,
    mime_type VARCHAR(100),

    -- Reference
    reference_id UUID, -- health_check.id or meal.id

    -- Metadata
    uploaded_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_file_uploads_user_id ON file_uploads(user_id);
CREATE INDEX idx_file_uploads_reference_id ON file_uploads(reference_id);

-- ================================================
-- 9. AUDIT LOG (Optional for MVP)
-- ================================================

CREATE TABLE audit_logs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id) ON DELETE SET NULL,

    action VARCHAR(100) NOT NULL, -- 'login', 'upload_meal', 'update_profile'
    resource_type VARCHAR(50),
    resource_id UUID,

    ip_address INET,
    user_agent TEXT,

    timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_audit_logs_user_id ON audit_logs(user_id);
CREATE INDEX idx_audit_logs_timestamp ON audit_logs(timestamp DESC);

-- ================================================
-- TRIGGERS
-- ================================================

-- Auto-update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_health_checks_updated_at BEFORE UPDATE ON health_checks
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_meals_updated_at BEFORE UPDATE ON meals
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_daily_summaries_updated_at BEFORE UPDATE ON daily_summaries
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_gamification_updated_at BEFORE UPDATE ON user_gamification
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- ================================================
-- VIEWS
-- ================================================

-- User Health Profile (최신 검진 + 사용자 정보)
CREATE VIEW v_user_health_profile AS
SELECT
    u.id AS user_id,
    u.email,
    u.gender,
    u.age_group,
    u.height_cm,
    u.current_weight_kg,
    u.health_goals,
    u.medications,
    u.allergies,
    hc.*,
    ROW_NUMBER() OVER (PARTITION BY u.id ORDER BY hc.check_date DESC) AS rn
FROM users u
LEFT JOIN health_checks hc ON u.id = hc.user_id
WHERE u.is_active = TRUE;

-- Recent Meals (최근 30일)
CREATE VIEW v_recent_meals AS
SELECT
    m.*,
    u.email,
    u.health_goals
FROM meals m
JOIN users u ON m.user_id = u.id
WHERE m.meal_time >= NOW() - INTERVAL '30 days'
ORDER BY m.meal_time DESC;

-- ================================================
-- SAMPLE DATA (for testing)
-- ================================================

-- Insert test user
INSERT INTO users (email, password_hash, gender, age_group, health_goals, medications, allergies)
VALUES (
    'test@example.com',
    crypt('password123', gen_salt('bf')),
    'male',
    '40s',
    '["weight", "bp", "lipid", "gerd"]'::jsonb,
    '["bp_med", "ppi"]'::jsonb,
    '["nuts"]'::jsonb
);

-- Insert test health check
INSERT INTO health_checks (
    user_id,
    check_date,
    bp_systolic,
    bp_diastolic,
    fasting_glucose,
    total_cholesterol,
    ldl_cholesterol,
    hdl_cholesterol,
    triglycerides,
    risk_profile
)
SELECT
    id,
    '2025-01-15',
    145,
    92,
    108,
    220,
    150,
    42,
    180,
    '{"bp": "high", "lipid": "moderate", "glucose": "borderline"}'::jsonb
FROM users WHERE email = 'test@example.com';

-- ================================================
-- DATABASE CONSTRAINTS & RULES
-- ================================================

-- Ensure BMI is realistic
ALTER TABLE users ADD CONSTRAINT check_weight_range
    CHECK (current_weight_kg IS NULL OR (current_weight_kg >= 30 AND current_weight_kg <= 300));

ALTER TABLE users ADD CONSTRAINT check_height_range
    CHECK (height_cm IS NULL OR (height_cm >= 100 AND height_cm <= 250));

-- Ensure meal nutritional values are non-negative
ALTER TABLE meals ADD CONSTRAINT check_kcal_positive
    CHECK (total_kcal IS NULL OR total_kcal >= 0);

ALTER TABLE meals ADD CONSTRAINT check_sodium_positive
    CHECK (sodium_mg IS NULL OR sodium_mg >= 0);

-- Ensure scores are 0-100
ALTER TABLE daily_summaries ADD CONSTRAINT check_scores_range
    CHECK (
        (weight_score BETWEEN 0 AND 100) AND
        (bp_score BETWEEN 0 AND 100) AND
        (lipid_score BETWEEN 0 AND 100) AND
        (glucose_score BETWEEN 0 AND 100) AND
        (gerd_score BETWEEN 0 AND 100)
    );

-- ================================================
-- INDEXES FOR PERFORMANCE
-- ================================================

-- Composite index for daily meal queries
CREATE INDEX idx_meals_user_date ON meals(user_id, DATE(meal_time) DESC);

-- Index for gamification streak queries
CREATE INDEX idx_gamification_streak ON user_gamification(user_id, current_streak DESC);

-- ================================================
-- COMMENTS
-- ================================================

COMMENT ON TABLE users IS '사용자 프로필 및 건강 목표';
COMMENT ON TABLE health_checks IS '건강검진 데이터 (업로드된 검진표에서 추출)';
COMMENT ON TABLE meals IS '식사 기록 (식전/식후 사진 + AI 분석 결과)';
COMMENT ON TABLE daily_summaries IS '일일 영양 요약 및 목표별 점수';
COMMENT ON TABLE weekly_reports IS '주간 리포트 (자동 생성)';
COMMENT ON TABLE user_gamification IS '게임화 요소 (스트릭, 배지, 포인트)';
COMMENT ON TABLE notifications IS '푸시 알림 및 인앱 알림';
COMMENT ON TABLE file_uploads IS '파일 업로드 메타데이터 (S3 URL)';
COMMENT ON TABLE audit_logs IS '감사 로그 (보안 및 디버깅)';

-- ================================================
-- END OF SCHEMA
-- ================================================
