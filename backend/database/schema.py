"""
Database schema for ServiceLink AI using PostgreSQL (Neon DB)
"""

CREATE_TABLES_SQL = """
-- Service Providers Table
CREATE TABLE IF NOT EXISTS service_providers (
    provider_id VARCHAR(20) PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    owner_name VARCHAR(255) NOT NULL,
    service_type VARCHAR(100) NOT NULL,
    service_category VARCHAR(100) NOT NULL,
    address TEXT,
    area VARCHAR(100),
    city VARCHAR(100),
    rating DECIMAL(3,2),
    reviews_count INTEGER DEFAULT 0,
    total_jobs INTEGER DEFAULT 0,
    price_range VARCHAR(100),
    experience_years INTEGER,
    verified BOOLEAN DEFAULT TRUE,
    phone VARCHAR(50),
    whatsapp VARCHAR(50),
    email VARCHAR(255),
    languages TEXT,
    services_offered TEXT,
    emergency_available BOOLEAN DEFAULT FALSE,
    response_time_minutes INTEGER,
    availability JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Bookings Table
CREATE TABLE IF NOT EXISTS bookings (
    booking_id VARCHAR(20) PRIMARY KEY,
    customer_phone VARCHAR(50),
    customer_email VARCHAR(255),
    customer_name VARCHAR(255),
    customer_location TEXT NOT NULL,
    provider_id VARCHAR(20) REFERENCES service_providers(provider_id),
    provider_name VARCHAR(255),
    service_type VARCHAR(100) NOT NULL,
    urgency VARCHAR(50) DEFAULT 'normal',
    date VARCHAR(50),
    time VARCHAR(50),
    status VARCHAR(50) DEFAULT 'pending',
    distance_km DECIMAL(10,2),
    estimated_cost VARCHAR(100),
    cancellation_reason TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for better query performance
CREATE INDEX IF NOT EXISTS idx_providers_service_type ON service_providers(service_type);
CREATE INDEX IF NOT EXISTS idx_providers_city ON service_providers(city);
CREATE INDEX IF NOT EXISTS idx_providers_area ON service_providers(area);
CREATE INDEX IF NOT EXISTS idx_bookings_status ON bookings(status);
CREATE INDEX IF NOT EXISTS idx_bookings_customer_phone ON bookings(customer_phone);
CREATE INDEX IF NOT EXISTS idx_bookings_provider_id ON bookings(provider_id);
"""

DROP_TABLES_SQL = """
DROP TABLE IF EXISTS bookings CASCADE;
DROP TABLE IF EXISTS service_providers CASCADE;
"""
