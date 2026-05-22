-- Add Google Calendar event ID to bookings table
ALTER TABLE bookings ADD COLUMN IF NOT EXISTS google_calendar_event_id VARCHAR(255);

-- Add index for faster lookups
CREATE INDEX IF NOT EXISTS idx_bookings_calendar_event ON bookings(google_calendar_event_id);
