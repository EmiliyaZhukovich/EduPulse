-- Create Keycloak database
CREATE DATABASE keycloak_db;

-- Initialize Edupulse database tables (will be created by SQLAlchemy)
-- Groups data
INSERT INTO groups (name, faculty, year, created_at) VALUES
  ('Группа 1', 'Технический факультет', 1, NOW()),
  ('Группа 2', 'Технический факультет', 2, NOW()),
  ('Группа 3', 'Гуманитарный факультет', 1, NOW()),
  ('Группа 4', 'Гуманитарный факультет', 2, NOW()),
  ('Группа 5', 'Экономический факультет', 1, NOW());

-- You can add sample survey links here if needed
