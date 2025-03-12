-- Script to generate sample users with 'pending' role for testing

-- Create some sample users with mixed email domains
INSERT INTO "user" (
    id,  -- Added explicit ID field
    name, 
    email, 
    role, 
    profile_image_url, 
    api_key, 
    created_at, 
    updated_at, 
    last_active_at, 
    settings, 
    info, 
    oauth_sub
)
VALUES
    -- Users with @gsa.gov emails (should be updated by trigger)
    (
        1001,
        'Alice Johnson', 
        'alice.johnson@gsa.gov', 
        'pending', 
        '/user.png', 
        NULL, 
        EXTRACT(EPOCH FROM NOW()) * 1000, 
        EXTRACT(EPOCH FROM NOW()) * 1000, 
        EXTRACT(EPOCH FROM NOW()) * 1000, 
        '{"ui":{"version": "0.5.3"}}', 
        NULL, 
        NULL
    ),
    (
        1002,
        'Bob Smith', 
        'bob.smith@gsa.gov', 
        'pending', 
        '/user.png', 
        NULL, 
        EXTRACT(EPOCH FROM NOW()) * 1000, 
        EXTRACT(EPOCH FROM NOW()) * 1000, 
        EXTRACT(EPOCH FROM NOW()) * 1000, 
        '{"ui":{"version": "0.5.3"}}', 
        NULL, 
        NULL
    ),
    (
        1003,
        'Carlos Rodriguez', 
        'carlos@gsa.gov', 
        'pending', 
        '/user.png', 
        NULL, 
        EXTRACT(EPOCH FROM NOW()) * 1000, 
        EXTRACT(EPOCH FROM NOW()) * 1000, 
        EXTRACT(EPOCH FROM NOW()) * 1000, 
        '{"ui":{"version": "0.5.3"}}', 
        NULL, 
        NULL
    ),
    (
        1004,
        'Diana Lee', 
        'diana.lee@gsa.gov', 
        'pending', 
        '/user.png', 
        NULL, 
        EXTRACT(EPOCH FROM NOW()) * 1000, 
        EXTRACT(EPOCH FROM NOW()) * 1000, 
        EXTRACT(EPOCH FROM NOW()) * 1000, 
        '{"ui":{"version": "0.5.3"}}', 
        NULL, 
        NULL
    ),

    -- Users with other email domains (should remain 'pending')
    (
        1005,
        'Elon Matthews', 
        'elon@gmail.com', 
        'pending', 
        '/user.png', 
        NULL, 
        EXTRACT(EPOCH FROM NOW()) * 1000, 
        EXTRACT(EPOCH FROM NOW()) * 1000, 
        EXTRACT(EPOCH FROM NOW()) * 1000, 
        '{"ui":{"version": "0.5.3"}}', 
        NULL, 
        NULL
    ),
    (
        1006,
        'Fiona Clark', 
        'fiona.clark@company.org', 
        'pending', 
        '/user.png', 
        NULL, 
        EXTRACT(EPOCH FROM NOW()) * 1000, 
        EXTRACT(EPOCH FROM NOW()) * 1000, 
        EXTRACT(EPOCH FROM NOW()) * 1000, 
        '{"ui":{"version": "0.5.3"}}', 
        NULL, 
        NULL
    );

-- Verification query to see all the users we just created
SELECT id, name, email, role FROM "user" 
WHERE email IN (
    'alice.johnson@gsa.gov', 
    'bob.smith@gsa.gov', 
    'carlos@gsa.gov', 
    'diana.lee@gsa.gov', 
    'elon@gmail.com', 
    'fiona.clark@company.org'
)
ORDER BY id;