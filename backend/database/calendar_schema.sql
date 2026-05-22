-- Calendar System Schema for ServiceLink AI
-- Database-based calendar (no Google Calendar API needed)

CREATE TABLE IF NOT EXISTS provider_calendar (
    id SERIAL PRIMARY KEY,
    provider_id VARCHAR(20) REFERENCES service_providers(provider_id),
    date DATE NOT NULL,
    time_slot VARCHAR(10) NOT NULL,
    is_booked BOOLEAN DEFAULT FALSE,
    booking_id VARCHAR(20),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_calendar_provider_date ON provider_calendar(provider_id, date);
CREATE INDEX idx_calendar_booking ON provider_calendar(booking_id);

-- Generate default time slots for all providers (9 AM to 6 PM)
-- This will be populated by the migration script
