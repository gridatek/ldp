-- Sample analytics queries for Iceberg tables

-- Daily event counts
SELECT
    date,
    event_type,
    COUNT(*) as event_count
FROM local.db.events
GROUP BY date, event_type
ORDER BY date DESC, event_count DESC;

-- User activity summary
SELECT
    user_id,
    COUNT(DISTINCT event_type) as unique_events,
    COUNT(*) as total_events,
    MIN(timestamp) as first_event,
    MAX(timestamp) as last_event
FROM local.db.events
GROUP BY user_id
ORDER BY total_events DESC;

-- Time-based aggregation
SELECT
    DATE_TRUNC('hour', timestamp) as hour,
    COUNT(*) as event_count
FROM local.db.events
WHERE date >= CURRENT_DATE - INTERVAL 7 DAYS
GROUP BY hour
ORDER BY hour DESC;
