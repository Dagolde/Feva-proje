-- Seed dropdown configuration data for FEVA mobile app
-- Run this after migrations to populate dropdown options

-- Clear existing data
TRUNCATE TABLE dropdown_config;

-- Street Types
INSERT INTO dropdown_config (category, value, label, sort_order, version) VALUES
('street_type', 'avenue', 'Avenue', 1, 1),
('street_type', 'boulevard', 'Boulevard', 2, 1),
('street_type', 'close', 'Close', 3, 1),
('street_type', 'crescent', 'Crescent', 4, 1),
('street_type', 'drive', 'Drive', 5, 1),
('street_type', 'lane', 'Lane', 6, 1),
('street_type', 'road', 'Road', 7, 1),
('street_type', 'street', 'Street', 8, 1),
('street_type', 'way', 'Way', 9, 1);

-- Surface Types
INSERT INTO dropdown_config (category, value, label, sort_order, version) VALUES
('surface_type', 'asphalt', 'Asphalt', 1, 1),
('surface_type', 'concrete', 'Concrete', 2, 1),
('surface_type', 'gravel', 'Gravel', 3, 1),
('surface_type', 'dirt', 'Dirt', 4, 1),
('surface_type', 'paved_blocks', 'Paved Blocks', 5, 1),
('surface_type', 'unpaved', 'Unpaved', 6, 1);

-- Street Conditions
INSERT INTO dropdown_config (category, value, label, sort_order, version) VALUES
('street_condition', 'excellent', 'Excellent', 1, 1),
('street_condition', 'good', 'Good', 2, 1),
('street_condition', 'fair', 'Fair', 3, 1),
('street_condition', 'poor', 'Poor', 4, 1),
('street_condition', 'very_poor', 'Very Poor', 5, 1);

-- Building Types
INSERT INTO dropdown_config (category, value, label, sort_order, version) VALUES
('building_type', 'residential', 'Residential', 1, 1),
('building_type', 'commercial', 'Commercial', 2, 1),
('building_type', 'industrial', 'Industrial', 3, 1),
('building_type', 'mixed_use', 'Mixed Use', 4, 1),
('building_type', 'institutional', 'Institutional', 5, 1),
('building_type', 'religious', 'Religious', 6, 1),
('building_type', 'educational', 'Educational', 7, 1),
('building_type', 'healthcare', 'Healthcare', 8, 1),
('building_type', 'government', 'Government', 9, 1),
('building_type', 'recreational', 'Recreational', 10, 1);

-- Building Conditions
INSERT INTO dropdown_config (category, value, label, sort_order, version) VALUES
('building_condition', 'excellent', 'Excellent', 1, 1),
('building_condition', 'good', 'Good', 2, 1),
('building_condition', 'fair', 'Fair', 3, 1),
('building_condition', 'poor', 'Poor', 4, 1),
('building_condition', 'very_poor', 'Very Poor', 5, 1),
('building_condition', 'under_construction', 'Under Construction', 6, 1),
('building_condition', 'abandoned', 'Abandoned', 7, 1);
