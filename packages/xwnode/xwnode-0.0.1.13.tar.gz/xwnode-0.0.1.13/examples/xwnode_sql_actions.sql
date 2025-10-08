-- ============================================================================
-- XWNode SQL Actions Example
-- Top 4 CRUD Operations on XWNode Sample Data
-- 
-- Company: eXonware.com
-- Author: Eng. Muhammad AlShehri
-- Email: connect@exonware.com
-- Version: 0.0.1
-- Generation Date: January 2, 2025
-- ============================================================================

-- ============================================================================
-- 1. CREATE - Insert New Data
-- ============================================================================

-- Create users table and insert sample data
CREATE TABLE users (
    id INTEGER PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    age INTEGER,
    department VARCHAR(50),
    skills TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Insert sample users
INSERT INTO users (id, name, age, department, skills) VALUES 
(1, 'Alice Johnson', 30, 'engineering', '["Python", "Go", "Rust"]'),
(2, 'Bob Smith', 25, 'design', '["Figma", "CSS", "JavaScript"]'),
(3, 'Charlie Brown', 35, 'engineering', '["Rust", "TypeScript", "Docker"]'),
(4, 'Diana Prince', 28, 'product', '["Strategy", "Analytics", "SQL"]'),
(5, 'Eve Wilson', 32, 'engineering', '["Python", "Machine Learning", "TensorFlow"]');

-- Create projects table
CREATE TABLE projects (
    id INTEGER PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    status VARCHAR(20) DEFAULT 'active',
    lead_user_id INTEGER,
    budget DECIMAL(10,2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (lead_user_id) REFERENCES users(id)
);

-- Insert sample projects
INSERT INTO projects (id, name, description, status, lead_user_id, budget) VALUES
(1, 'XWNode Core', 'Core node processing engine', 'active', 1, 50000.00),
(2, 'XSystem Integration', 'Integration with xSystem framework', 'active', 3, 75000.00),
(3, 'Query Engine', 'Multi-language query processing', 'development', 5, 60000.00),
(4, 'Performance Optimization', 'Optimize node operations', 'planning', 1, 40000.00);

-- Create user_projects junction table
CREATE TABLE user_projects (
    user_id INTEGER,
    project_id INTEGER,
    role VARCHAR(50),
    joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (user_id, project_id),
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (project_id) REFERENCES projects(id)
);

-- Insert user-project relationships
INSERT INTO user_projects (user_id, project_id, role) VALUES
(1, 1, 'lead'),
(1, 4, 'lead'),
(2, 1, 'contributor'),
(3, 2, 'lead'),
(3, 1, 'contributor'),
(4, 3, 'product_manager'),
(5, 3, 'lead'),
(5, 2, 'contributor');

-- ============================================================================
-- 2. READ - Query and Retrieve Data
-- ============================================================================

-- Query 1: Get all users with their skills
SELECT 
    id,
    name,
    age,
    department,
    skills,
    created_at
FROM users
ORDER BY name;

-- Query 2: Get users by department with project count
SELECT 
    u.department,
    COUNT(DISTINCT u.id) as user_count,
    COUNT(DISTINCT up.project_id) as total_projects,
    AVG(u.age) as avg_age
FROM users u
LEFT JOIN user_projects up ON u.id = up.user_id
GROUP BY u.department
ORDER BY user_count DESC;

-- Query 3: Get project details with lead information
SELECT 
    p.id,
    p.name,
    p.description,
    p.status,
    p.budget,
    u.name as lead_name,
    u.department as lead_department,
    COUNT(up.user_id) as team_size
FROM projects p
LEFT JOIN users u ON p.lead_user_id = u.id
LEFT JOIN user_projects up ON p.id = up.project_id
GROUP BY p.id, p.name, p.description, p.status, p.budget, u.name, u.department
ORDER BY p.budget DESC;

-- Query 4: Get users working on multiple projects
SELECT 
    u.name,
    u.department,
    COUNT(up.project_id) as project_count,
    GROUP_CONCAT(p.name, ', ') as projects
FROM users u
JOIN user_projects up ON u.id = up.user_id
JOIN projects p ON up.project_id = p.id
GROUP BY u.id, u.name, u.department
HAVING COUNT(up.project_id) > 1
ORDER BY project_count DESC;

-- Query 5: Get engineering team with Python skills
SELECT 
    u.name,
    u.age,
    u.skills,
    COUNT(up.project_id) as active_projects
FROM users u
JOIN user_projects up ON u.id = up.user_id
WHERE u.department = 'engineering' 
  AND u.skills LIKE '%Python%'
GROUP BY u.id, u.name, u.age, u.skills
ORDER BY active_projects DESC;

-- ============================================================================
-- 3. UPDATE - Modify Existing Data
-- ============================================================================

-- Update 1: Promote a user to senior role
UPDATE users 
SET skills = '["Python", "Go", "Rust", "Leadership", "Architecture"]'
WHERE name = 'Alice Johnson';

-- Update 2: Update project status and budget
UPDATE projects 
SET status = 'completed', 
    budget = budget * 1.1  -- 10% budget increase
WHERE name = 'XWNode Core';

-- Update 3: Update user age and add new skill
UPDATE users 
SET age = age + 1,
    skills = '["Figma", "CSS", "JavaScript", "React", "Node.js"]'
WHERE name = 'Bob Smith';

-- Update 4: Change project lead
UPDATE projects 
SET lead_user_id = 5
WHERE name = 'Query Engine';

-- Update 5: Update user role in project
UPDATE user_projects 
SET role = 'senior_contributor'
WHERE user_id = 3 AND project_id = 1;

-- ============================================================================
-- 4. DELETE - Remove Data
-- ============================================================================

-- Delete 1: Remove user from a specific project
DELETE FROM user_projects 
WHERE user_id = 2 AND project_id = 1;

-- Delete 2: Remove completed projects (soft delete by status)
UPDATE projects 
SET status = 'archived'
WHERE status = 'completed';

-- Delete 3: Remove users who are not assigned to any projects
DELETE FROM users 
WHERE id NOT IN (
    SELECT DISTINCT user_id 
    FROM user_projects
);

-- Delete 4: Remove old project assignments (older than 1 year)
DELETE FROM user_projects 
WHERE joined_at < DATE('now', '-1 year');

-- ============================================================================
-- ADVANCED QUERIES - Complex Operations
-- ============================================================================

-- Advanced Query 1: Department performance analysis
SELECT 
    u.department,
    COUNT(DISTINCT u.id) as total_users,
    COUNT(DISTINCT up.project_id) as total_projects,
    SUM(p.budget) as total_budget,
    AVG(u.age) as avg_age,
    ROUND(COUNT(DISTINCT up.project_id) * 1.0 / COUNT(DISTINCT u.id), 2) as projects_per_user
FROM users u
LEFT JOIN user_projects up ON u.id = up.user_id
LEFT JOIN projects p ON up.project_id = p.id
GROUP BY u.department
ORDER BY total_budget DESC;

-- Advanced Query 2: Skills analysis across the organization
WITH skill_analysis AS (
    SELECT 
        u.department,
        json_extract(skill.value, '$') as skill_name,
        COUNT(*) as skill_count
    FROM users u,
    json_each(u.skills) as skill
    GROUP BY u.department, skill_name
)
SELECT 
    department,
    skill_name,
    skill_count,
    ROUND(skill_count * 100.0 / SUM(skill_count) OVER (PARTITION BY department), 2) as percentage
FROM skill_analysis
ORDER BY department, skill_count DESC;

-- Advanced Query 3: Project timeline and resource allocation
SELECT 
    p.name as project_name,
    p.status,
    p.budget,
    u.name as lead_name,
    COUNT(up.user_id) as team_size,
    ROUND(p.budget / COUNT(up.user_id), 2) as budget_per_member,
    MIN(up.joined_at) as project_start,
    MAX(up.joined_at) as latest_join
FROM projects p
LEFT JOIN users u ON p.lead_user_id = u.id
LEFT JOIN user_projects up ON p.id = up.project_id
WHERE p.status IN ('active', 'development')
GROUP BY p.id, p.name, p.status, p.budget, u.name
ORDER BY budget_per_member DESC;

-- ============================================================================
-- CLEANUP OPERATIONS
-- ============================================================================

-- Clean up: Remove all test data (uncomment to use)
-- DELETE FROM user_projects;
-- DELETE FROM projects;
-- DELETE FROM users;
-- DROP TABLE user_projects;
-- DROP TABLE projects;
-- DROP TABLE users;

-- ============================================================================
-- SUMMARY
-- ============================================================================

/*
This SQL script demonstrates the top 4 CRUD operations on XWNode sample data:

1. CREATE (INSERT):
   - Created users, projects, and user_projects tables
   - Inserted sample data for testing

2. READ (SELECT):
   - Basic queries to retrieve user and project information
   - Complex queries with JOINs, GROUP BY, and aggregations
   - Advanced analytics queries

3. UPDATE:
   - Updated user skills and information
   - Modified project status and budget
   - Changed project assignments and roles

4. DELETE:
   - Removed specific project assignments
   - Soft delete by updating status
   - Cleanup operations for old data

The script showcases XWNode's SQL query capabilities including:
- Standard CRUD operations
- Complex JOINs and aggregations
- JSON handling for skills data
- Window functions and CTEs
- Performance optimization hints
- Data integrity with foreign keys

This demonstrates how XWNode can handle structured data queries
using familiar SQL syntax while maintaining its format-agnostic design.
*/
