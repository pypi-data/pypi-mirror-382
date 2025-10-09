# XWQuery Script Documentation

**Generated:** 2025-01-27  
**Author:** Eng. Muhammad AlShehri  
**Company:** eXonware.com  
**Email:** connect@exonware.com  

## Overview

XWQuery Script is a comprehensive query language specification designed for xwnode that covers 50 distinct action headers. This document provides complete syntax specifications, Monaco editor integration guidance, and implementation details for building a production-grade query editor.

## Core Design Principles

### Editor-Facing Specifications

```spec
• Case: Keywords are CASE-INSENSITIVE (small or caps same)
• Statement end: Semicolon (;) optional at EOF, required between statements
• Comments: -- line, /* block */
• Whitespace/newlines: Insignificant except inside literals
• Identifiers: [A-Za-z_][A-Za-z0-9_]* or "quoted name"
• Strings: 'single-quoted' (escape: '' -> single quote)
• Numbers: INT, DECIMAL; Booleans: true/false; Null: null
• JSON literal: { ... }, [ ... ]
• Duration literal: INTERVAL '1d', '5m', '30s'
• Time: DATE '2025-01-01', TIMESTAMP '2025-01-01T12:00:00Z'
• Options: OPTIONS( key = value [, ...] ) // value: literal/identifier
• Pipeline operator: PIPE <source> |> <stage> |> <stage> ...
• Aliasing: <expr> AS <id> or <expr> <id>
• Placeholders (for client binding): ? or :name
```

## Complete Action Headers (50 Total)

### 1) SELECT - Data Retrieval and Projection

**Purpose**: Retrieve and project data from sources with filtering, grouping, and ordering capabilities.

```xquery
-- Basic selection
SELECT user_id, name, email FROM users WHERE active = true;

-- Complex projection with expressions
SELECT 
    user_id,
    CONCAT(first_name, ' ', last_name) AS full_name,
    CASE 
        WHEN age >= 18 THEN 'adult'
        ELSE 'minor'
    END AS age_group,
    COUNT(*) OVER (PARTITION BY department) AS dept_count
FROM users 
WHERE created_at >= '2024-01-01'
ORDER BY last_name ASC, first_name ASC
LIMIT 100;

-- Window functions
SELECT 
    product_id,
    price,
    LAG(price, 1) OVER (ORDER BY date) AS prev_price,
    ROW_NUMBER() OVER (PARTITION BY category ORDER BY price DESC) AS price_rank
FROM products;
```

### 2) INSERT - Data Insertion

**Purpose**: Insert new records into tables with conflict resolution.

```xquery
-- Simple insert
INSERT INTO users (name, email, age) VALUES ('John Doe', 'john@example.com', 30);

-- Bulk insert
INSERT INTO products (name, price, category) VALUES 
    ('Laptop', 999.99, 'Electronics'),
    ('Mouse', 29.99, 'Electronics'),
    ('Keyboard', 79.99, 'Electronics');

-- Insert with conflict resolution
INSERT INTO users (id, name, email) VALUES (1, 'John Doe', 'john@example.com')
ON CONFLICT (id) DO UPDATE SET 
    name = EXCLUDED.name,
    email = EXCLUDED.email,
    updated_at = NOW();

-- Insert from query
INSERT INTO user_stats (user_id, total_orders, total_spent)
SELECT 
    user_id,
    COUNT(*) as total_orders,
    SUM(amount) as total_spent
FROM orders 
WHERE order_date >= '2024-01-01'
GROUP BY user_id;
```

### 3) UPDATE - Data Modification

**Purpose**: Modify existing records with conditional updates.

```xquery
-- Simple update
UPDATE users SET last_login = NOW() WHERE user_id = 123;

-- Conditional update with joins
UPDATE products p
SET price = p.price * 0.9,
    discount_applied = true
FROM categories c
WHERE p.category_id = c.id 
    AND c.name = 'Electronics'
    AND p.price > 100;

-- Update with subquery
UPDATE users 
SET status = 'premium'
WHERE user_id IN (
    SELECT user_id 
    FROM orders 
    WHERE total_amount > 1000
    GROUP BY user_id
    HAVING COUNT(*) >= 5
);
```

### 4) DELETE - Data Removal

**Purpose**: Remove records with conditional deletion.

```xquery
-- Simple delete
DELETE FROM users WHERE last_login < '2023-01-01';

-- Delete with joins
DELETE FROM order_items oi
USING orders o
WHERE oi.order_id = o.id 
    AND o.status = 'cancelled'
    AND o.created_at < '2023-01-01';

-- Delete with subquery
DELETE FROM products 
WHERE category_id IN (
    SELECT id FROM categories WHERE discontinued = true
);
```

### 5) CREATE - Schema Definition

**Purpose**: Create database objects (tables, views, indexes, collections, streams).

```xquery
-- Create table
CREATE TABLE users (
    id BIGINT PRIMARY KEY,
    name TEXT NOT NULL,
    email TEXT UNIQUE,
    age INT CHECK (age >= 0),
    created_at TIMESTAMP DEFAULT NOW(),
    profile JSON
) OPTIONS(engine = 'native', compression = 'snappy');

-- Create view
CREATE VIEW active_users AS
SELECT user_id, name, email, last_login
FROM users 
WHERE status = 'active' AND last_login >= NOW() - INTERVAL '30 days';

-- Create index
CREATE INDEX idx_users_email ON users (email);
CREATE INDEX idx_orders_user_date ON orders (user_id, order_date);

-- Create collection (document store)
CREATE COLLECTION products (
    id UUID PRIMARY KEY,
    name TEXT,
    attributes JSON,
    tags ARRAY<TEXT>
) OPTIONS(engine = 'mongodb');

-- Create stream
CREATE STREAM user_events (
    event_id UUID,
    user_id BIGINT,
    event_type TEXT,
    event_data JSON,
    timestamp TIMESTAMP
) OPTIONS(retention = '7d', partitions = 4);
```

### 6) ALTER - Schema Modification

**Purpose**: Modify existing database objects.

```xquery
-- Add column
ALTER TABLE users ADD COLUMN phone TEXT;

-- Drop column
ALTER TABLE users DROP COLUMN old_field;

-- Rename table
ALTER TABLE old_users RENAME TO users;

-- Modify column
ALTER TABLE users ALTER COLUMN age TYPE INT;

-- Set options
ALTER TABLE users SET OPTIONS(compression = 'gzip', ttl = '1y');
```

### 7) DROP - Schema Removal

**Purpose**: Remove database objects.

```xquery
-- Drop table
DROP TABLE IF EXISTS old_users CASCADE;

-- Drop view
DROP VIEW user_summary;

-- Drop index
DROP INDEX idx_old_index;
```

### 8) MERGE - Upsert Operations

**Purpose**: Insert or update records based on conditions.

```xquery
-- Basic merge
MERGE INTO users u
USING new_users n ON u.email = n.email
WHEN MATCHED THEN 
    UPDATE SET 
        name = n.name,
        last_updated = NOW()
WHEN NOT MATCHED THEN 
    INSERT (email, name, created_at) 
    VALUES (n.email, n.name, NOW());

-- Complex merge with conditions
MERGE INTO inventory i
USING sales s ON i.product_id = s.product_id
WHEN MATCHED AND s.quantity > 0 THEN
    UPDATE SET 
        stock = i.stock - s.quantity,
        last_sale = s.sale_date
WHEN NOT MATCHED THEN
    INSERT (product_id, stock, last_updated)
    VALUES (s.product_id, -s.quantity, s.sale_date);
```

### 9) LOAD - Data Ingestion

**Purpose**: Load data from external sources.

```xquery
-- Load CSV
LOAD DATA INTO users 
FROM 's3://bucket/users.csv'
FORMAT csv
OPTIONS(
    header = true,
    sep = ',',
    quote = '"',
    compression = 'gzip'
);

-- Load JSON
LOAD DATA INTO events
FROM 'https://api.example.com/events.json'
FORMAT json
OPTIONS(
    schema = 'auto',
    batch_size = 1000
);

-- Load Parquet
LOAD DATA INTO analytics_data
FROM 'hdfs://cluster/data/analytics.parquet'
FORMAT parquet
OPTIONS(
    schema = 'provided',
    credentials = { "profile": "production" }
);
```

### 10) STORE - Data Export

**Purpose**: Export data to external destinations.

```xquery
-- Store to CSV
STORE (
    SELECT user_id, name, email, total_orders
    FROM user_summary
    WHERE total_orders > 10
)
TO 's3://exports/top_users.csv'
FORMAT csv
MODE OVERWRITE
OPTIONS(header = true, compression = 'gzip');

-- Store to JSON
STORE (
    SELECT * FROM products WHERE category = 'Electronics'
)
TO 'api://products/electronics'
FORMAT json
MODE APPEND;

-- Store with partitioning
STORE (
    SELECT * FROM daily_metrics
)
TO 's3://analytics/daily/'
FORMAT parquet
PARTITION BY date
MODE OVERWRITE;
```

### 11) WHERE - Conditional Filtering

**Purpose**: Filter rows based on conditions.

```xquery
-- Basic conditions
SELECT * FROM users WHERE age > 18 AND status = 'active';

-- Complex conditions
SELECT * FROM orders 
WHERE order_date BETWEEN '2024-01-01' AND '2024-12-31'
    AND (status = 'completed' OR status = 'shipped')
    AND total_amount > 100
    AND customer_id IN (SELECT id FROM premium_customers);

-- Pattern matching
SELECT * FROM products 
WHERE name LIKE '%laptop%' 
    AND description ILIKE '%gaming%'
    AND tags @> '["electronics", "computers"]';

-- JSON conditions
SELECT * FROM user_profiles 
WHERE profile #> '$.preferences.theme' = '"dark"'
    AND profile #> '$.settings.notifications' = 'true';
```

### 12) FILTER - Pipeline Filtering

**Purpose**: Filter data in pipeline operations.

```xquery
-- Pipeline filtering
PIPE users
|> FILTER age > 18 AND status = 'active'
|> FILTER last_login >= NOW() - INTERVAL '30 days'
|> PROJECT user_id, name, email;

-- Complex filter conditions
PIPE orders
|> FILTER order_date >= '2024-01-01'
|> FILTER total_amount > (
    SELECT AVG(total_amount) FROM orders WHERE order_date >= '2024-01-01'
)
|> EXTEND profit_margin = (total_amount - cost) / total_amount
|> FILTER profit_margin > 0.2;
```

### 13) OPTIONAL - Outer Join Semantics

**Purpose**: Perform optional joins that preserve all rows from the left side.

```xquery
-- Optional join
SELECT u.name, p.title as profile_title
FROM users u
OPTIONAL JOIN user_profiles p ON u.id = p.user_id;

-- Multiple optional joins
SELECT 
    u.name,
    p.title,
    a.city
FROM users u
OPTIONAL JOIN user_profiles p ON u.id = p.user_id
OPTIONAL JOIN addresses a ON u.id = a.user_id AND a.type = 'primary';
```

### 14) UNION - Result Combination

**Purpose**: Combine results from multiple queries.

```xquery
-- Basic union
SELECT name, 'user' as type FROM users
UNION
SELECT name, 'admin' as type FROM admins;

-- Union with ordering
SELECT name, created_at FROM users
UNION ALL
SELECT name, created_at FROM admins
ORDER BY created_at DESC;

-- Complex union
SELECT 
    user_id,
    'order' as event_type,
    order_date as event_date,
    total_amount as amount
FROM orders
UNION
SELECT 
    user_id,
    'refund' as event_type,
    refund_date as event_date,
    -refund_amount as amount
FROM refunds
ORDER BY event_date;
```

### 15) BETWEEN - Range Conditions

**Purpose**: Filter values within a range.

```xquery
-- Numeric range
SELECT * FROM products WHERE price BETWEEN 50 AND 200;

-- Date range
SELECT * FROM orders 
WHERE order_date BETWEEN '2024-01-01' AND '2024-12-31';

-- String range
SELECT * FROM users 
WHERE name BETWEEN 'A' AND 'M';

-- NOT BETWEEN
SELECT * FROM products 
WHERE price NOT BETWEEN 10 AND 100;
```

### 16) LIKE - Pattern Matching

**Purpose**: Match text patterns with wildcards.

```xquery
-- Basic LIKE
SELECT * FROM products WHERE name LIKE '%laptop%';

-- Case-insensitive ILIKE
SELECT * FROM users WHERE email ILIKE '%@gmail.com';

-- Multiple patterns
SELECT * FROM products 
WHERE name LIKE '%gaming%' 
    OR name LIKE '%pro%'
    OR name LIKE '%premium%';

-- Escape characters
SELECT * FROM files WHERE path LIKE '/data/%/%.csv' ESCAPE '/';
```

### 17) IN - Membership Testing

**Purpose**: Test if values are in a set.

```xquery
-- Simple IN
SELECT * FROM users WHERE status IN ('active', 'premium', 'vip');

-- IN with subquery
SELECT * FROM products 
WHERE category_id IN (
    SELECT id FROM categories WHERE parent_id = 1
);

-- NOT IN
SELECT * FROM users 
WHERE user_id NOT IN (
    SELECT user_id FROM banned_users
);

-- IN with expressions
SELECT * FROM orders 
WHERE (user_id, order_date) IN (
    SELECT user_id, MAX(order_date) 
    FROM orders 
    GROUP BY user_id
);
```

### 18) TERM - Text Search

**Purpose**: Perform term-based text search.

```xquery
-- Basic term search
SELECT * FROM articles 
WHERE TERM(content, 'machine learning');

-- Term with options
SELECT * FROM products 
WHERE TERM(description, 'wireless headphones', 
    OPTIONS(
        fuzzy = true,
        boost = 2.0,
        analyzer = 'english'
    )
);

-- Multiple term searches
SELECT * FROM documents 
WHERE TERM(title, 'python') 
    AND TERM(content, 'programming')
    AND TERM(tags, 'tutorial');
```

### 19) RANGE - Range Queries

**Purpose**: Perform range-based searches.

```xquery
-- Numeric range
SELECT * FROM products 
WHERE RANGE(price, 
    OPTIONS(
        gte = 100,
        lte = 500
    )
);

-- Date range
SELECT * FROM events 
WHERE RANGE(timestamp,
    OPTIONS(
        gte = '2024-01-01T00:00:00Z',
        lt = '2024-02-01T00:00:00Z'
    )
);

-- Open ranges
SELECT * FROM products 
WHERE RANGE(rating,
    OPTIONS(
        gt = 4.0  -- greater than 4.0
    )
);
```

### 20) HAS - Existence Testing

**Purpose**: Test for field or path existence.

```xquery
-- Field existence
SELECT * FROM users WHERE HAS(phone);

-- JSON path existence
SELECT * FROM user_profiles 
WHERE HAS(profile #> '$.preferences.theme');

-- Array element existence
SELECT * FROM products 
WHERE HAS(tags, 'electronics');

-- Complex existence
SELECT * FROM documents 
WHERE HAS(content) 
    AND HAS(metadata #> '$.author')
    AND NOT HAS(metadata #> '$.draft');
```

### 21) MATCH - Graph Pattern Matching

**Purpose**: Match graph patterns and relationships.

```xquery
-- Basic pattern matching
MATCH (u:User)-[:FRIENDS_WITH]->(f:User)
WHERE u.age > 25
RETURN u.name, f.name;

-- Complex patterns
MATCH (u:User)-[:PURCHASED]->(p:Product)<-[:PURCHASED]-(other:User)
WHERE u.id = 123
RETURN other.name, COUNT(p) as common_purchases
ORDER BY common_purchases DESC;

-- Multiple relationships
MATCH (u:User)-[:WORKS_AT]->(c:Company)-[:LOCATED_IN]->(city:City)
WHERE city.name = 'San Francisco'
RETURN u.name, c.name, city.name;

-- Variable length paths
MATCH (u:User)-[:FRIENDS_WITH*1..3]->(friend:User)
WHERE u.id = 123
RETURN friend.name, LENGTH(path) as degrees_separation;
```

### 22) JOIN - Table Joins

**Purpose**: Combine data from multiple tables.

```xquery
-- Inner join
SELECT u.name, o.total_amount
FROM users u
INNER JOIN orders o ON u.id = o.user_id;

-- Left outer join
SELECT u.name, p.title
FROM users u
LEFT OUTER JOIN user_profiles p ON u.id = p.user_id;

-- Multiple joins
SELECT 
    u.name,
    o.order_date,
    p.name as product_name,
    oi.quantity
FROM users u
INNER JOIN orders o ON u.id = o.user_id
INNER JOIN order_items oi ON o.id = oi.order_id
INNER JOIN products p ON oi.product_id = p.id;

-- Self join
SELECT 
    e1.name as employee,
    e2.name as manager
FROM employees e1
LEFT JOIN employees e2 ON e1.manager_id = e2.id;
```

### 23) WITH - Common Table Expressions

**Purpose**: Define temporary named result sets.

```xquery
-- Basic CTE
WITH top_customers AS (
    SELECT user_id, SUM(total_amount) as total_spent
    FROM orders
    GROUP BY user_id
    HAVING SUM(total_amount) > 1000
)
SELECT u.name, tc.total_spent
FROM users u
INNER JOIN top_customers tc ON u.id = tc.user_id;

-- Recursive CTE
WITH RECURSIVE category_tree AS (
    SELECT id, name, parent_id, 0 as level
    FROM categories
    WHERE parent_id IS NULL
    
    UNION ALL
    
    SELECT c.id, c.name, c.parent_id, ct.level + 1
    FROM categories c
    INNER JOIN category_tree ct ON c.parent_id = ct.id
)
SELECT * FROM category_tree ORDER BY level, name;
```

### 24) OUT - Graph Traversal (Outgoing)

**Purpose**: Traverse outgoing relationships in graphs.

```xquery
-- Basic outgoing traversal
OUT(FRIENDS_WITH) DEPTH 2 FROM (SELECT * FROM users WHERE id = 123);

-- Limited depth
OUT(PURCHASED) DEPTH 1..3 FROM (SELECT * FROM users WHERE age > 25);

-- With conditions
OUT(WORKS_AT) FROM (
    MATCH (u:User) WHERE u.department = 'Engineering'
) WHERE company.size > 1000;
```

### 25) IN_TRAVERSE - Graph Traversal (Incoming)

**Purpose**: Traverse incoming relationships in graphs.

```xquery
-- Basic incoming traversal
IN_TRAVERSE(PURCHASED) DEPTH 2 FROM (SELECT * FROM products WHERE id = 456);

-- Find who purchased this product
IN_TRAVERSE(PURCHASED) FROM (
    SELECT * FROM products WHERE name LIKE '%laptop%'
) WHERE user.age > 18;
```

### 26) PATH - Path Finding

**Purpose**: Find paths between nodes in graphs.

```xquery
-- Shortest path
PATH((a:User)-[:FRIENDS_WITH*1..4]->(b:User))
WHERE a.id = 123 AND b.id = 456;

-- All paths with conditions
PATH((u:User)-[:PURCHASED]->(p:Product)<-[:PURCHASED]-(other:User))
WHERE u.id = 123
OPTIONS(
    max_depth = 3,
    path_limit = 100
);
```

### 27) RETURN - Result Projection

**Purpose**: Project and return specific fields from queries.

```xquery
-- Basic return
MATCH (u:User) WHERE u.age > 25
RETURN u.name, u.email, u.age;

-- Return with expressions
MATCH (u:User)-[:PURCHASED]->(p:Product)
RETURN 
    u.name,
    COUNT(p) as purchase_count,
    AVG(p.price) as avg_price;

-- Return distinct
MATCH (u:User)-[:FRIENDS_WITH]->(f:User)
RETURN DISTINCT f.name;
```

### 28) PROJECT - Field Projection

**Purpose**: Project specific fields in pipeline operations.

```xquery
-- Basic projection
PROJECT user_id, name, email ON users;

-- Project with expressions
PROJECT 
    user_id,
    CONCAT(first_name, ' ', last_name) AS full_name,
    CASE WHEN age >= 18 THEN 'adult' ELSE 'minor' END AS age_group
ON users;

-- Project with exclusions
PROJECT * EXCEPT (password, ssn, internal_notes) ON users;
```

### 29) EXTEND - Field Addition

**Purpose**: Add computed fields to existing data.

```xquery
-- Basic extension
EXTEND 
    full_name = CONCAT(first_name, ' ', last_name),
    age_group = CASE WHEN age >= 18 THEN 'adult' ELSE 'minor' END
ON users;

-- Extension with window functions
EXTEND 
    row_number = ROW_NUMBER() OVER (ORDER BY created_at),
    total_count = COUNT(*) OVER ()
ON users;
```

### 30) FOREACH - Iteration

**Purpose**: Iterate over collections and perform operations.

```xquery
-- Basic foreach
FOREACH user IN (SELECT * FROM users WHERE status = 'inactive') DO {
    INSERT INTO user_archive (user_id, archived_at) 
    VALUES (user.id, NOW());
    
    DELETE FROM user_sessions WHERE user_id = user.id;
};

-- Foreach with conditions
FOREACH order IN (SELECT * FROM orders WHERE status = 'pending') DO {
    IF (order.created_at < NOW() - INTERVAL '7 days') THEN {
        UPDATE orders SET status = 'cancelled' WHERE id = order.id;
    }
};
```

### 31) LET - Variable Assignment

**Purpose**: Assign values to variables for reuse.

```xquery
-- Basic let
LET max_date = (SELECT MAX(order_date) FROM orders);
SELECT * FROM orders WHERE order_date = max_date;

-- Multiple lets
LET 
    start_date = '2024-01-01',
    end_date = '2024-12-31',
    min_amount = 100;

SELECT * FROM orders 
WHERE order_date BETWEEN start_date AND end_date
    AND total_amount >= min_amount;
```

### 32) FOR_IN - Collection Iteration

**Purpose**: Iterate over collections in expressions.

```xquery
-- Basic for-in
SELECT 
    user_id,
    FOR tag IN tags RETURN tag
FROM user_profiles;

-- For-in with conditions
SELECT 
    product_id,
    FOR review IN reviews 
    WHERE review.rating >= 4 
    RETURN review.comment
FROM products;
```

### 33) DESCRIBE - Schema Information

**Purpose**: Get information about database objects.

```xquery
-- Describe table
DESCRIBE TABLE users;

-- Describe view
DESCRIBE VIEW user_summary;

-- Describe collection
DESCRIBE COLLECTION products;
```

### 34) CONSTRUCT - Data Transformation

**Purpose**: Transform data into different formats.

```xquery
-- JSON construction
CONSTRUCT {
    "user_id": user_id,
    "name": name,
    "email": email,
    "preferences": preferences
} FROM users WHERE active = true;

-- XML construction
CONSTRUCT 
    <user id="{user_id}">
        <name>{name}</name>
        <email>{email}</email>
    </user>
FROM users;

-- Graph construction
CONSTRUCT (u:User {id: user_id, name: name}) 
FROM users u;
```

### 35) ORDER BY - Result Sorting

**Purpose**: Sort query results.

```xquery
-- Basic ordering
SELECT * FROM users ORDER BY name ASC;

-- Multiple columns
SELECT * FROM orders 
ORDER BY order_date DESC, total_amount ASC;

-- Null handling
SELECT * FROM products 
ORDER BY price ASC NULLS LAST;

-- Expression ordering
SELECT * FROM users 
ORDER BY LENGTH(name) DESC, name ASC;
```

### 36) GROUP BY - Data Grouping

**Purpose**: Group data for aggregation.

```xquery
-- Basic grouping
SELECT department, COUNT(*) as employee_count
FROM employees
GROUP BY department;

-- Multiple grouping
SELECT 
    department,
    job_title,
    COUNT(*) as count,
    AVG(salary) as avg_salary
FROM employees
GROUP BY department, job_title;

-- Grouping sets
SELECT 
    department,
    job_title,
    COUNT(*) as count
FROM employees
GROUP BY GROUPING SETS (
    (department),
    (job_title),
    (department, job_title),
    ()
);
```

### 37) SUM - Summation Aggregation

**Purpose**: Calculate sum of numeric values.

```xquery
-- Basic sum
SELECT SUM(total_amount) as total_revenue FROM orders;

-- Conditional sum
SELECT 
    SUM(CASE WHEN status = 'completed' THEN total_amount ELSE 0 END) as completed_revenue,
    SUM(CASE WHEN status = 'cancelled' THEN total_amount ELSE 0 END) as cancelled_revenue
FROM orders;

-- Sum with grouping
SELECT 
    user_id,
    SUM(total_amount) as user_total
FROM orders
GROUP BY user_id;
```

### 38) COUNT - Counting Aggregation

**Purpose**: Count rows or distinct values.

```xquery
-- Basic count
SELECT COUNT(*) as total_users FROM users;

-- Count distinct
SELECT COUNT(DISTINCT user_id) as unique_customers FROM orders;

-- Conditional count
SELECT 
    COUNT(CASE WHEN age >= 18 THEN 1 END) as adults,
    COUNT(CASE WHEN age < 18 THEN 1 END) as minors
FROM users;

-- Count with grouping
SELECT 
    category,
    COUNT(*) as product_count
FROM products
GROUP BY category;
```

### 39) AVG - Average Aggregation

**Purpose**: Calculate average of numeric values.

```xquery
-- Basic average
SELECT AVG(price) as avg_price FROM products;

-- Average with grouping
SELECT 
    category,
    AVG(price) as avg_category_price
FROM products
GROUP BY category;

-- Weighted average
SELECT 
    SUM(price * quantity) / SUM(quantity) as weighted_avg_price
FROM order_items;
```

### 40) MIN - Minimum Aggregation

**Purpose**: Find minimum values.

```xquery
-- Basic minimum
SELECT MIN(price) as min_price FROM products;

-- Minimum with grouping
SELECT 
    category,
    MIN(price) as min_category_price
FROM products
GROUP BY category;

-- Minimum date
SELECT MIN(order_date) as first_order FROM orders;
```

### 41) MAX - Maximum Aggregation

**Purpose**: Find maximum values.

```xquery
-- Basic maximum
SELECT MAX(price) as max_price FROM products;

-- Maximum with grouping
SELECT 
    category,
    MAX(price) as max_category_price
FROM products
GROUP BY category;

-- Maximum date
SELECT MAX(order_date) as last_order FROM orders;
```

### 42) DISTINCT - Duplicate Removal

**Purpose**: Remove duplicate rows or values.

```xquery
-- Row-level distinct
SELECT DISTINCT department, job_title FROM employees;

-- Partial distinct
SELECT DISTINCT ON (department) 
    department, 
    name, 
    salary
FROM employees
ORDER BY department, salary DESC;

-- Aggregate distinct
SELECT 
    COUNT(DISTINCT user_id) as unique_customers,
    COUNT(DISTINCT product_id) as unique_products
FROM orders;
```

### 43) SUMMARIZE - KQL-like Aggregation

**Purpose**: Perform Kusto-like summarization operations.

```xquery
-- Basic summarize
SUMMARIZE 
    total_orders = count(),
    total_revenue = sum(total_amount),
    avg_order_value = avg(total_amount)
ON orders;

-- Summarize by grouping
SUMMARIZE BY user_id
    total_orders = count(),
    total_spent = sum(total_amount),
    first_order = min(order_date),
    last_order = max(order_date)
ON orders;

-- Complex summarize
SUMMARIZE BY department, job_title
    employee_count = count(),
    avg_salary = avg(salary),
    min_salary = min(salary),
    max_salary = max(salary),
    salary_range = max(salary) - min(salary)
ON employees;
```

### 44) AGGREGATE WINDOW - Time-based Aggregation

**Purpose**: Perform time-windowed aggregations.

```xquery
-- Time window aggregation
AGGREGATE WINDOW 1h USING sum(total_amount)
PARTITION BY user_id
ORDER BY order_date
ON orders;

-- Session window
AGGREGATE WINDOW SESSION 30m USING count()
PARTITION BY user_id
ORDER BY event_time
ON user_events;

-- Hop window
AGGREGATE WINDOW 1d HOP 1h USING avg(price)
PARTITION BY category
ORDER BY timestamp
ON price_history;
```

### 45) SLICING - Array/List Operations

**Purpose**: Slice arrays and lists.

```xquery
-- Basic slicing
SELECT tags[1:3] as first_three_tags FROM products;

-- Step slicing
SELECT items[::2] as even_items FROM arrays;

-- Reverse slicing
SELECT items[::-1] as reversed_items FROM arrays;

-- Open bounds
SELECT items[:5] as first_five, items[5:] as rest FROM arrays;
```

### 46) INDEXING - Array/Object Access

**Purpose**: Access elements by index or key.

```xquery
-- Array indexing
SELECT tags[0] as first_tag FROM products;

-- Object key access
SELECT profile['theme'] as user_theme FROM user_profiles;

-- JSON path indexing
SELECT data #> '$.user.preferences.theme' as theme FROM configs;

-- Nested indexing
SELECT items[0]['name'] as first_item_name FROM orders;
```

### 47) ASK - Existence Queries

**Purpose**: Check for existence of data.

```xquery
-- Row existence
ASK (SELECT 1 FROM users WHERE email = 'admin@example.com');

-- Graph existence
ASK (MATCH (u:User)-[:ADMIN]->(s:System) WHERE u.id = 123);

-- JSON existence
ASK VALUE EXISTS(profile #> '$.preferences.theme');

-- Complex existence
ASK (
    SELECT 1 FROM orders o
    INNER JOIN users u ON o.user_id = u.id
    WHERE u.status = 'premium' AND o.total_amount > 1000
);
```

### 48) SUBSCRIPTION - Real-time Data Streaming

**Purpose**: Subscribe to real-time data streams.

```xquery
-- Query stream subscription
SUBSCRIBE (
    SELECT user_id, event_type, event_data, timestamp
    FROM user_events
    WHERE event_type IN ('login', 'logout', 'purchase')
)
WINDOW 5s
OUTPUT 'ws://api.example.com/events';

-- Table changefeed
SUBSCRIBE TABLE orders
COLUMNS (id, user_id, status, total_amount)
WHERE status = 'completed'
OUTPUT 'kafka://orders.completed';

-- Graph topic subscription
SUBSCRIBE MATCH (u:User)-[r:PURCHASED]->(p:Product)
WHERE p.category = 'Electronics'
OUTPUT 'kafka://electronics.purchases';
```

### 49) MUTATION - Transactional Operations

**Purpose**: Perform multiple operations in a transaction.

```xquery
-- Basic mutation
MUTATION {
    INSERT INTO users (name, email) VALUES ('John', 'john@example.com');
    INSERT INTO user_profiles (user_id, theme) VALUES (LAST_INSERT_ID(), 'dark');
    UPDATE user_stats SET total_users = total_users + 1;
}
TRANSACTION READ COMMITTED;

-- Complex mutation
MUTATION {
    UPDATE orders SET status = 'cancelled' WHERE id = 123;
    INSERT INTO order_history (order_id, action, timestamp) 
    VALUES (123, 'cancelled', NOW());
    UPDATE inventory SET stock = stock + (
        SELECT quantity FROM order_items WHERE order_id = 123
    );
}
TRANSACTION SERIALIZABLE;
```

### 50) Advanced Pipeline Operations

**Purpose**: Complex data processing pipelines.

```xquery
-- Multi-stage pipeline
PIPE user_events
|> FILTER event_type = 'purchase'
|> EXTEND 
    hour = DATE_TRUNC('hour', timestamp),
    revenue = event_data #> '$.amount'
|> SUMMARIZE BY hour
    total_revenue = sum(revenue),
    purchase_count = count()
|> PROJECT 
    hour,
    total_revenue,
    purchase_count,
    avg_order_value = total_revenue / purchase_count
|> ORDER BY hour DESC;

-- Conditional pipeline
PIPE users
|> FILTER status = 'active'
|> EXTEND 
    user_segment = CASE 
        WHEN total_orders > 100 THEN 'vip'
        WHEN total_orders > 10 THEN 'regular'
        ELSE 'new'
    END
|> PROJECT user_id, name, user_segment, total_orders
|> ORDER BY total_orders DESC;
```


## Grammar Specifications

### Expressions & Precedence

```ebnf
expr ::= literal | id | id'.'id | '(' expr ')'
| expr '[' index ']' // indexing
| expr '#>' jsonPath // JSON-path
| func '(' [argList] ')' // functions/aggregates
| '-' expr | '+' expr | 'NOT' expr
| expr '^' expr
| expr ('*'|'/') expr
| expr ('+'|'-') expr
| expr ('||'|CONCAT) expr
| expr compOp expr // = != < <= > >=
| expr 'IS' ['NOT'] 'NULL'
| expr ['NOT'] 'BETWEEN' expr 'AND' expr
| expr ['NOT'] 'IN' '(' query | list ')'
| expr ['NOT'] ('LIKE'|'ILIKE') pattern [ 'ESCAPE' char ]
| 'EXISTS' '(' query ')'

compOp ::= '=' | '!=' | '<>' | '<' | '>' | '<=' | '>='

list ::= expr {',' expr}
index ::= INT | ':' INT [':' INT] | ':' | INT ':' [INT]
jsonPath ::= '$' ('.'key | '[' INT | '*' ']')*
func ::= id
argList ::= expr {',' expr}
```

### SELECT Statement

```ebnf
selectStmt ::= 'SELECT' [ 'DISTINCT' [ 'ON' '(' exprList ')' ] ]
selectList
[ 'FROM' fromItems ]
[ whereClause ]
[ groupBy ]
[ having ]
[ windowSpec ]
[ orderBy ]
[ limitOffset ]

selectList ::= selectItem {',' selectItem}
selectItem ::= expr [ 'AS' id ]

fromItems ::= fromItem {',' fromItem}
fromItem ::= source [ joinChain ]
joinChain ::= joinSpec { joinSpec }
joinSpec ::= joinKind 'JOIN' source joinCond

joinKind ::= 'INNER' | 'LEFT' ['OUTER'] | 'RIGHT' ['OUTER'] | 'FULL' ['OUTER'] | 'CROSS'
joinCond ::= 'ON' expr | 'USING' '(' idList ')'

whereClause ::= 'WHERE' expr
groupBy ::= 'GROUP' 'BY' exprList [ groupingSets ]
groupingSets::= 'GROUPING' 'SETS' '(' groupSet {',' groupSet} ')'
groupSet ::= '(' exprList ')' | '(' ')' | expr

having ::= 'HAVING' expr
windowSpec ::= 'WINDOW' id 'AS' '(' windowDef ')'
windowDef ::= [ 'PARTITION' 'BY' exprList ] [ 'ORDER' 'BY' orderList ] [ frameClause ]

frameClause ::= ('ROWS'|'RANGE'|'GROUPS') frameBounds
frameBounds ::= 'BETWEEN' framePoint 'AND' framePoint | framePoint
framePoint ::= 'UNBOUNDED' 'PRECEDING' | 'CURRENT' 'ROW' | INT 'PRECEDING' | INT 'FOLLOWING'

orderBy ::= 'ORDER' 'BY' orderList
orderList ::= orderItem {',' orderItem}
orderItem ::= expr [ 'ASC' | 'DESC' ] [ 'NULLS' 'FIRST' | 'NULLS' 'LAST' ]

limitOffset ::= 'LIMIT' INT [ 'OFFSET' INT ]
exprList ::= expr {',' expr}
idList ::= id {',' id}
query ::= selectStmt | valuesStmt | (other statements returning rows)
```

### Graph Operations (MATCH)

```ebnf
MATCHclause ::= 'MATCH' pattern [ 'WHERE' expr ] [ 'RETURN' returnItems ]

pattern ::= path {',' path}
path ::= node patternTail*
patternTail ::= rel node

node ::= '(' [ id ] [ ':' label {':' label} ] [ props ] ')'
rel ::= '-' '[' [ id ] [ ':' type {':' type} ] [ props ] ']' '->'

label ::= id
type ::= id
props ::= '{' propList '}'
propList ::= id ':' expr {',' id ':' expr}

returnItems ::= returnItem {',' returnItem}
returnItem ::= expr [ 'AS' id ]
```

### Pipeline Operations

```ebnf
pipeQuery ::= 'PIPE' source pipeStage { '|>' pipeStage }
pipeStage ::= filterStage | extendStage | projectStmt | summarizeSt | aggWindowSt

filterStage ::= 'FILTER' expr
extendStage ::= 'EXTEND' assignList 'ON' source
projectStmt ::= 'PROJECT' projectList 'ON' source
```

### Subscription & Streaming

```ebnf
subscribeSt ::= 'SUBSCRIBE' '(' query | source ')'
[ 'WHERE' expr ] [ 'WINDOW' winSpec ] [ 'OUTPUT' sink ]

winSpec ::= INT ('s'|'m'|'h') | 'SESSION' INT 'm'
sink ::= STRING | 'STDOUT' | 'WEBSOCKET' '(' uri ')'
```

## Monaco Editor Integration

### Tokenizer Rules

```typescript
const tokenizerRules = {
  TOKEN_KW: /(?i)\b(SELECT|INSERT|UPDATE|DELETE|CREATE|ALTER|DROP|MERGE|LOAD|STORE|WHERE|FILTER|OPTIONAL|UNION|BETWEEN|LIKE|IN|TERM|RANGE|HAS|MATCH|JOIN|WITH|OUT|IN_TRAVERSE|PATH|RETURN|PROJECT|EXTEND|FOREACH|LET|FOR|DESCRIBE|CONSTRUCT|ORDER|BY|GROUP|HAVING|SUMMARIZE|AGGREGATE|WINDOW|SLICING|INDEXING|ASK|SUBSCRIBE|SUBSCRIPTION|MUTATION|VALUES|INTO|FROM|ON|USING|AS|SET|OPTIONS|TABLE|VIEW|INDEX|COLLECTION|STREAM|DISTINCT|LIMIT|OFFSET|NULLS|FIRST|LAST|EXISTS|NOT|AND|OR|IS|TRUE|FALSE|NULL)\b/,
  ID: /[A-Za-z_][A-Za-z0-9_]*/,
  QID: /"([^"]|(""))*"/,
  INT: /[0-9]+/,
  DECIMAL: /[0-9]+\.[0-9]+/,
  STRING: /'([^']|(''))*'/,
  COMMENT_LINE: /--[^\n]*/,
  COMMENT_BLOCK: /\/\*.*?\*\//,
  WS: /[\s\t\r\n]+/,
  SYMS: /[(),.;=*<>!+-/^%|#,:\[\]{}]/
};
```

### Autocomplete Strategy

```typescript
const autocompleteSuggestions = {
  afterSELECT: ['DISTINCT', '*', 'columns'],
  afterFROM: ['tables', 'views', 'MATCH'],
  afterJOIN: ['INNER', 'LEFT', 'RIGHT', 'FULL', 'CROSS', 'ON', 'USING'],
  afterWHERE: ['columns', 'functions', 'operators'],
  insideMATCH: [':Label', '{prop:}'],
  afterORDERBY: ['columns', 'expressions', 'ASC', 'DESC'],
  afterGROUPBY: ['columns', 'expressions'],
  afterAGGREGATE: ['WINDOW', '1m', '5m', '1h', '1d', 'SESSION 30m'],
  afterOPTIONS: ['engine', 'parallelism', 'retries', 'timezone']
};
```

### Snippets

```typescript
const snippets = {
  MERGE: {
    prefix: 'merge',
    body: [
      'MERGE INTO ${1:target} USING ${2:source} ON ${3:condition}',
      'WHEN MATCHED THEN UPDATE SET ${4:assignments}',
      'WHEN NOT MATCHED THEN INSERT (${5:columns}) VALUES (${6:values});'
    ]
  },
  SUBSCRIBE: {
    prefix: 'subscribe',
    body: [
      'SUBSCRIBE (${1:query})',
      'WINDOW ${2:5s}',
      'OUTPUT ${3:ws://endpoint};'
    ]
  },
  PIPE: {
    prefix: 'pipe',
    body: [
      'PIPE ${1:source}',
      '|> FILTER ${2:condition}',
      '|> EXTEND ${3:assignments}',
      '|> PROJECT ${4:columns};'
    ]
  }
};
```

## Error Handling & Linting

### Validation Rules

```typescript
const validationRules = {
  requireFROM: 'SELECT with unqualified columns requires FROM clause',
  disallowOrderByWithoutOutput: 'ORDER BY requires SELECT/RETURN output',
  validateGroupBy: 'Non-aggregated select items must be in GROUP BY',
  validateJoinUsing: 'JOIN ... USING keys must exist on both sides',
  checkMergeBranches: 'MERGE must have at least one WHEN branch',
  warnUpdateDeleteWithoutWhere: 'UPDATE/DELETE without WHERE clause',
  checkLoadStoreFormat: 'LOAD/STORE FORMAT must support file extension',
  validateMatchPattern: 'MATCH node/edge labels must be identifiers',
  forbidNegativeWindowFrames: 'Window frames cannot be negative/overlapping',
  requireSubscribeOutput: 'SUBSCRIBE requires OUTPUT or default sink'
};
```

## Standard Library Functions

### Scalar Functions
- **Math**: ABS, CEIL, FLOOR, ROUND
- **String**: LENGTH, LOWER, UPPER, SUBSTRING, CONCAT
- **Null**: COALESCE, NULLIF
- **Date/Time**: NOW, DATE_TRUNC(unit, ts), EXTRACT(unit FROM ts)
- **JSON**: JSON_EXTRACT(json, path), JSON_SET(json, path, value), JSON_REMOVE(json, path)
- **Search**: TERM(field, val), RANGE(field, opts), HAS(field|path)

### Aggregates
- **Standard**: COUNT, SUM, AVG, MIN, MAX
- **Advanced**: COUNT(DISTINCT), PERCENTILE, ARG_MIN, ARG_MAX

## Options Configuration

### Universal Options

```xquery
OPTIONS(
  engine = 'spark' | 'native' | 'duckdb',
  parallelism = 8,
  retries = 3,
  timezone = 'UTC',
  on_error = 'abort' | 'skip' | 'retry'
)
```

### Load/Store Specific

```xquery
OPTIONS(
  header = true, 
  sep = ',', 
  quote = '"', 
  escape = '"',
  compression = 'gzip' | 'snappy' | 'none',
  schema = 'auto' | 'infer' | 'provided',
  credentials = { "profile": "default" }
)
```

### Subscribe Options

```xquery
OPTIONS(
  backpressure = 'drop' | 'buffer' | 'block',
  heartbeat_ms = 5000
)
```

## Reserved Words

```spec
SELECT, INSERT, UPDATE, DELETE, CREATE, ALTER, DROP, MERGE, LOAD, STORE,
WHERE, FILTER, OPTIONAL, UNION, BETWEEN, LIKE, IN, TERM, RANGE, HAS, MATCH,
JOIN, WITH, OUT, IN, IN_TRAVERSE, PATH, RETURN, PROJECT, EXTEND, FOREACH,
LET, FOR, DESCRIBE, CONSTRUCT, ORDER, BY, GROUP, HAVING, SUMMARIZE,
AGGREGATE, WINDOW, SLICING, INDEXING, ASK, SUBSCRIBE, SUBSCRIPTION, MUTATION,
VALUES, INTO, FROM, ON, USING, AS, SET, OPTIONS, TABLE, VIEW, INDEX, COLLECTION, STREAM,
DISTINCT, LIMIT, OFFSET, NULLS, FIRST, LAST, EXISTS, NOT, AND, OR, IS, TRUE, FALSE, NULL
```

## Implementation Notes

### AST Structure

```typescript
interface Program {
  statements: Statement[];
}

type Statement = 
  | SelectStatement
  | InsertStatement
  | UpdateStatement
  | DeleteStatement
  | CreateStatement
  | AlterStatement
  | DropStatement
  | MergeStatement
  | LoadStatement
  | StoreStatement
  | FilterStage
  | OptionalJoin
  | UnionQuery
  | MatchClause
  | OutStatement
  | InStatement
  | PathStatement
  | ReturnStatement
  | ProjectStatement
  | ExtendStage
  | ForeachStatement
  | LetStatement
  | ForInStatement
  | DescribeStatement
  | ConstructStatement
  | SummarizeStatement
  | AggWindowStatement
  | AskStatement
  | SubscribeStatement
  | MutationStatement;
```

### TypeScript Integration

For Monaco editor integration, implement:

1. **Language Definition**: Define XWQuery as a new language in Monaco
2. **Tokenization**: Implement tokenizer with case-insensitive keyword recognition
3. **Autocomplete**: Provide context-aware suggestions based on current position
4. **Validation**: Real-time syntax and semantic validation
5. **Snippets**: Pre-built templates for common patterns
6. **Formatting**: Auto-formatting with proper indentation

## References

- **ANSI SQL-2016**: DISTINCT, DISTINCT ON variants, GROUPING SETS/ROLLUP/CUBE, WINDOW/OVER
- **Cypher 9**: Pattern matching, quantifiers, graph traversal
- **SPARQL 1.1**: ASK queries, graph patterns
- **Kusto**: SUMMARIZE, streaming/subscriptions
- **Flux**: AggregateWindow, time-based operations

---

**Status**: Complete specification covering all 50 action headers  
**Monaco Ready**: Full editor integration specifications provided  
**Production Grade**: Enterprise-ready with comprehensive error handling and validation
