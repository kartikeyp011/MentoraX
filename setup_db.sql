-- MentoraX Database Setup Script
-- Run this script to create the database and all required tables

CREATE DATABASE IF NOT EXISTS MentoraX;
USE MentoraX;

-- Users table
CREATE TABLE IF NOT EXISTS users (
    user_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(255) NOT NULL UNIQUE,
    password VARCHAR(64) NOT NULL,
    degree VARCHAR(255) DEFAULT NULL,
    career_goal VARCHAR(255) DEFAULT NULL,
    resume_url TEXT DEFAULT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Sessions table
CREATE TABLE IF NOT EXISTS sessions (
    session_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    session_token VARCHAR(255) NOT NULL UNIQUE,
    expires_at DATETIME NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
);

-- Skills catalog
CREATE TABLE IF NOT EXISTS skills (
    skill_id INT AUTO_INCREMENT PRIMARY KEY,
    skill_name VARCHAR(100) NOT NULL UNIQUE,
    description TEXT DEFAULT NULL
);

-- User-skill mapping
CREATE TABLE IF NOT EXISTS user_skills (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    skill_id INT NOT NULL,
    proficiency INT DEFAULT 3 CHECK (proficiency BETWEEN 1 AND 5),
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
    FOREIGN KEY (skill_id) REFERENCES skills(skill_id) ON DELETE CASCADE,
    UNIQUE KEY unique_user_skill (user_id, skill_id)
);

-- Opportunities (jobs, internships, etc.)
CREATE TABLE IF NOT EXISTS opportunities (
    opportunity_id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    link TEXT,
    source VARCHAR(100),
    location VARCHAR(255),
    deadline DATE DEFAULT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Opportunity-skill mapping
CREATE TABLE IF NOT EXISTS opportunity_skills (
    id INT AUTO_INCREMENT PRIMARY KEY,
    opportunity_id INT NOT NULL,
    skill_id INT NOT NULL,
    FOREIGN KEY (opportunity_id) REFERENCES opportunities(opportunity_id) ON DELETE CASCADE,
    FOREIGN KEY (skill_id) REFERENCES skills(skill_id) ON DELETE CASCADE,
    UNIQUE KEY unique_opp_skill (opportunity_id, skill_id)
);

-- Saved/bookmarked opportunities
CREATE TABLE IF NOT EXISTS saved_opportunities (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    opportunity_id INT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
    FOREIGN KEY (opportunity_id) REFERENCES opportunities(opportunity_id) ON DELETE CASCADE,
    UNIQUE KEY unique_saved (user_id, opportunity_id)
);

-- Learning resources
CREATE TABLE IF NOT EXISTS resources (
    resource_id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    url TEXT,
    skill_id INT DEFAULT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (skill_id) REFERENCES skills(skill_id) ON DELETE SET NULL
);

-- ============================================
-- Seed Data: Common tech skills
-- ============================================
INSERT IGNORE INTO skills (skill_name, description) VALUES
('Python', 'General-purpose programming language widely used in web dev, data science, and AI'),
('JavaScript', 'Core language for web development, both frontend and backend'),
('Java', 'Object-oriented language used in enterprise applications and Android development'),
('C++', 'High-performance language used in systems programming and game development'),
('SQL', 'Structured Query Language for managing relational databases'),
('HTML/CSS', 'Markup and styling languages for building web pages'),
('React', 'JavaScript library for building user interfaces'),
('Node.js', 'JavaScript runtime for server-side development'),
('Machine Learning', 'Building systems that learn from data to make predictions'),
('Data Analysis', 'Extracting insights from data using statistical and computational methods'),
('Git', 'Version control system for tracking code changes'),
('Docker', 'Containerization platform for packaging applications'),
('AWS', 'Amazon Web Services cloud computing platform'),
('REST APIs', 'Designing and consuming RESTful web services'),
('MongoDB', 'NoSQL document database for flexible data storage'),
('TypeScript', 'Typed superset of JavaScript for scalable applications'),
('Django', 'Python web framework for rapid development'),
('Flask', 'Lightweight Python web framework'),
('FastAPI', 'Modern Python web framework for building APIs'),
('TensorFlow', 'Open-source machine learning framework by Google'),
('PyTorch', 'Deep learning framework by Meta'),
('Kubernetes', 'Container orchestration platform'),
('CI/CD', 'Continuous Integration and Continuous Deployment practices'),
('Agile', 'Agile project management methodology'),
('Communication', 'Effective verbal and written communication skills'),
('Problem Solving', 'Analytical and logical problem-solving abilities'),
('Data Structures', 'Fundamental computer science data organization concepts'),
('Algorithms', 'Step-by-step procedures for solving computational problems'),
('Linux', 'Open-source operating system used in servers and development'),
('Cybersecurity', 'Protecting systems, networks, and data from digital attacks');

SELECT CONCAT('✅ Database setup complete! Created ', COUNT(*), ' skills.') as status FROM skills;
