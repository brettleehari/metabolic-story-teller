-- GlucoLens MVP2 Database Schema Updates
-- This script adds tables for authentication, alerts, and integrations

-- ==================== REFRESH TOKENS (for JWT) ====================

CREATE TABLE IF NOT EXISTS refresh_tokens (
    id BIGSERIAL PRIMARY KEY,
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    token VARCHAR(500) UNIQUE NOT NULL,
    expires_at TIMESTAMPTZ NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_refresh_tokens_user ON refresh_tokens(user_id);
CREATE INDEX IF NOT EXISTS idx_refresh_tokens_token ON refresh_tokens(token);
CREATE INDEX IF NOT EXISTS idx_refresh_tokens_expires ON refresh_tokens(expires_at);

-- ==================== ALERT CONFIGURATIONS ====================

CREATE TABLE IF NOT EXISTS alert_configs (
    id BIGSERIAL PRIMARY KEY,
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    alert_type VARCHAR(50) NOT NULL,  -- 'high_glucose', 'low_glucose', 'pattern_detected', 'anomaly'
    threshold_value NUMERIC(6,2),     -- Threshold for numeric alerts (e.g., glucose level)
    enabled BOOLEAN DEFAULT true,
    delivery_methods JSONB DEFAULT '["websocket"]'::jsonb,  -- ['websocket', 'email', 'push']
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_alert_configs_user ON alert_configs(user_id);
CREATE INDEX IF NOT EXISTS idx_alert_configs_type ON alert_configs(alert_type);
CREATE INDEX IF NOT EXISTS idx_alert_configs_enabled ON alert_configs(enabled);

-- ==================== ALERT HISTORY ====================

CREATE TABLE IF NOT EXISTS alerts (
    id BIGSERIAL PRIMARY KEY,
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    alert_type VARCHAR(50) NOT NULL,
    message TEXT NOT NULL,
    data JSONB,                       -- Additional alert data
    delivered BOOLEAN DEFAULT false,
    read_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_alerts_user ON alerts(user_id, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_alerts_type ON alerts(alert_type);
CREATE INDEX IF NOT EXISTS idx_alerts_unread ON alerts(user_id, read_at) WHERE read_at IS NULL;

-- ==================== HEALTHKIT INTEGRATION STATUS ====================

CREATE TABLE IF NOT EXISTS healthkit_sync_status (
    id BIGSERIAL PRIMARY KEY,
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE UNIQUE,
    last_sync_at TIMESTAMPTZ,
    last_glucose_reading TIMESTAMPTZ,
    last_sleep_reading TIMESTAMPTZ,
    last_activity_reading TIMESTAMPTZ,
    sync_enabled BOOLEAN DEFAULT true,
    sync_frequency_minutes INTEGER DEFAULT 60,  -- How often to sync
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_healthkit_user ON healthkit_sync_status(user_id);
CREATE INDEX IF NOT EXISTS idx_healthkit_enabled ON healthkit_sync_status(sync_enabled);

-- ==================== API KEYS (for external integrations) ====================

CREATE TABLE IF NOT EXISTS api_keys (
    id BIGSERIAL PRIMARY KEY,
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    key_name VARCHAR(100) NOT NULL,
    api_key VARCHAR(500) UNIQUE NOT NULL,
    scopes JSONB DEFAULT '[]'::jsonb,  -- ['read:glucose', 'write:glucose', 'read:insights']
    is_active BOOLEAN DEFAULT true,
    last_used_at TIMESTAMPTZ,
    expires_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_api_keys_user ON api_keys(user_id);
CREATE INDEX IF NOT EXISTS idx_api_keys_key ON api_keys(api_key);
CREATE INDEX IF NOT EXISTS idx_api_keys_active ON api_keys(is_active);

-- ==================== PREDICTIONS (for ML forecasting) ====================

CREATE TABLE IF NOT EXISTS glucose_predictions (
    id BIGSERIAL PRIMARY KEY,
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    prediction_time TIMESTAMPTZ NOT NULL,  -- When prediction was made
    forecast_time TIMESTAMPTZ NOT NULL,    -- Time being predicted
    predicted_value NUMERIC(5,1) NOT NULL,
    confidence_lower NUMERIC(5,1),         -- Lower bound of confidence interval
    confidence_upper NUMERIC(5,1),         -- Upper bound of confidence interval
    model_version VARCHAR(50),
    actual_value NUMERIC(5,1),             -- Filled in after actual reading
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_predictions_user_time ON glucose_predictions(user_id, forecast_time DESC);
CREATE INDEX IF NOT EXISTS idx_predictions_forecast ON glucose_predictions(forecast_time);

-- ==================== SESSIONS (for WebSocket connection tracking) ====================

CREATE TABLE IF NOT EXISTS user_sessions (
    id BIGSERIAL PRIMARY KEY,
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    session_id VARCHAR(500) UNIQUE NOT NULL,
    ip_address VARCHAR(50),
    user_agent TEXT,
    connected_at TIMESTAMPTZ DEFAULT NOW(),
    disconnected_at TIMESTAMPTZ,
    is_active BOOLEAN DEFAULT true
);

CREATE INDEX IF NOT EXISTS idx_sessions_user ON user_sessions(user_id);
CREATE INDEX IF NOT EXISTS idx_sessions_active ON user_sessions(is_active);

-- ==================== HELPER FUNCTIONS ====================

-- Function to clean up expired refresh tokens
CREATE OR REPLACE FUNCTION cleanup_expired_refresh_tokens()
RETURNS INTEGER AS $$
DECLARE
    deleted_count INTEGER;
BEGIN
    DELETE FROM refresh_tokens WHERE expires_at < NOW();
    GET DIAGNOSTICS deleted_count = ROW_COUNT;
    RETURN deleted_count;
END;
$$ LANGUAGE plpgsql;

-- Function to mark alerts as delivered
CREATE OR REPLACE FUNCTION mark_alerts_delivered(alert_ids BIGINT[])
RETURNS INTEGER AS $$
DECLARE
    updated_count INTEGER;
BEGIN
    UPDATE alerts
    SET delivered = true
    WHERE id = ANY(alert_ids) AND delivered = false;
    GET DIAGNOSTICS updated_count = ROW_COUNT;
    RETURN updated_count;
END;
$$ LANGUAGE plpgsql;

-- ==================== DEFAULT DATA ====================

-- Insert default alert configs for test user
INSERT INTO alert_configs (user_id, alert_type, threshold_value, enabled)
VALUES
    ('00000000-0000-0000-0000-000000000001', 'high_glucose', 180.0, true),
    ('00000000-0000-0000-0000-000000000001', 'low_glucose', 70.0, true)
ON CONFLICT DO NOTHING;

-- Success message
DO $$
BEGIN
    RAISE NOTICE '✅ GlucoLens MVP2 schema updated successfully!';
    RAISE NOTICE '   - Refresh tokens table created';
    RAISE NOTICE '   - Alert system tables created';
    RAISE NOTICE '   - HealthKit integration table created';
    RAISE NOTICE '   - API keys table created';
    RAISE NOTICE '   - Predictions table created';
    RAISE NOTICE '   - User sessions table created';
END $$;
