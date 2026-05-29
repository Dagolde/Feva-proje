-- Seed initial roles and admin user for FEVA backend
-- Run with: psql -h localhost -p 5433 -U feva -d feva -f scripts/seed_admin.sql

-- Insert roles (if not exists)
INSERT INTO roles (id, name) VALUES (1, 'admin') ON CONFLICT (id) DO NOTHING;
INSERT INTO roles (id, name) VALUES (2, 'enumerator') ON CONFLICT (id) DO NOTHING;
INSERT INTO roles (id, name) VALUES (3, 'supervisor') ON CONFLICT (id) DO NOTHING;
INSERT INTO roles (id, name) VALUES (4, 'qa_officer') ON CONFLICT (id) DO NOTHING;

-- Insert admin user
-- Username: admin
-- Password: Admin@2026! (bcrypt hash below)
-- Email: admin@feva.test
INSERT INTO users (username, email, password_hash, role_id, lga_assignment, totp_enabled)
VALUES (
    'admin',
    'admin@feva.test',
    '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYqgdRrvZ0O',
    1,
    NULL,
    false
) ON CONFLICT (username) DO NOTHING;

-- Insert test enumerator
-- Username: test_enum
-- Password: Test@2026!
INSERT INTO users (username, email, password_hash, role_id, lga_assignment, totp_enabled)
VALUES (
    'test_enum',
    'test_enum@feva.test',
    '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYqgdRrvZ0O',
    2,
    ARRAY['TEST_LGA'],
    false
) ON CONFLICT (username) DO NOTHING;

SELECT 'Seeded roles and users successfully!' as result;
