-- Drop tables if they already exist (removes them to start fresh)
DROP TABLE IF EXISTS users CASCADE;
DROP TABLE IF EXISTS roles CASCADE;

-- 1. Create the 'roles' table
CREATE TABLE roles (
    role_id SERIAL PRIMARY KEY,
    name VARCHAR(50) UNIQUE NOT NULL
);

-- Insert the default access roles needed for the application
INSERT INTO roles (name) VALUES
    ('admin'),
    ('user');

-- 2. Create the 'users' table
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    created_at DATE NOT NULL DEFAULT CURRENT_DATE,
    login VARCHAR(100) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    role_id INTEGER NOT NULL,
    FOREIGN KEY (role_id) REFERENCES roles (role_id) ON DELETE RESTRICT
);
