-- Drop and recreate the history table to support both ID types
DROP TABLE IF EXISTS user_role_change_history;

CREATE TABLE user_role_change_history (
    change_id SERIAL PRIMARY KEY,
    user_id VARCHAR NOT NULL,  -- Using VARCHAR to support both integer IDs and UUIDs
    email VARCHAR NOT NULL,
    old_role VARCHAR NOT NULL,
    new_role VARCHAR NOT NULL,
    update_time TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_by VARCHAR DEFAULT CURRENT_USER
);

-- Begin the update transaction
BEGIN;

-- Insert into history table
WITH pending_users_to_update AS (
    SELECT CAST(id AS VARCHAR) AS id, email, role
    FROM "user"
    WHERE role = 'pending'
    AND email ~ '@gsa\.gov'
)
INSERT INTO user_role_change_history (user_id, email, old_role, new_role)
SELECT 
    id,
    email, 
    'pending', 
    'user'
FROM pending_users_to_update;

-- Update the actual users table
UPDATE "user"
SET 
    role = 'user',
    updated_at = EXTRACT(EPOCH FROM NOW()) * 1000
WHERE CAST(id AS VARCHAR) IN (
    SELECT user_id 
    FROM user_role_change_history 
    WHERE update_time > (CURRENT_TIMESTAMP - INTERVAL '5 minutes')
);

-- Commit the changes
COMMIT;

-- Verify the changes
SELECT id, name, email, role
FROM "user"
WHERE email ~ '@gsa\.gov'
ORDER BY email;

-- Check the history table
SELECT * FROM user_role_change_history
WHERE update_time > (CURRENT_TIMESTAMP - INTERVAL '5 minutes')
ORDER BY email;