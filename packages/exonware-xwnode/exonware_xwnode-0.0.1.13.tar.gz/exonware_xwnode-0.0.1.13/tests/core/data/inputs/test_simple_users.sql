-- Simple User Query
-- Company: eXonware.com
-- Date: 07-Oct-2025

SELECT 
    user_id,
    name,
    email,
    created_at
FROM users
WHERE active = true
    AND created_at >= '2024-01-01'
ORDER BY created_at DESC
LIMIT 100;

