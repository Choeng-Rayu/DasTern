-- User-related database functions for DasTern V2

-- Function to get current user ID (to be used with authentication system)
CREATE OR REPLACE FUNCTION current_user_id()
RETURNS UUID AS $$
BEGIN
    -- This function should be implemented based on your authentication system
    -- For now, it returns NULL, but in production it should extract user ID from JWT or session
    RETURN current_setting('app.current_user_id', true)::UUID;
EXCEPTION
    WHEN OTHERS THEN
        RETURN NULL;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Function to check if user has premium subscription
CREATE OR REPLACE FUNCTION user_has_premium_subscription(user_uuid UUID)
RETURNS BOOLEAN AS $$
DECLARE
    subscription_status TEXT;
    subscription_end TIMESTAMP;
BEGIN
    SELECT us.status, us.current_period_end
    INTO subscription_status, subscription_end
    FROM user_subscriptions us
    WHERE us.user_id = user_uuid
    AND us.status = 'active'
    ORDER BY us.created_at DESC
    LIMIT 1;
    
    -- Check if user has active premium subscription
    IF subscription_status = 'active' AND subscription_end > NOW() THEN
        RETURN TRUE;
    END IF;
    
    -- Also check direct subscription_tier in users table (for legacy support)
    SELECT subscription_tier INTO subscription_status
    FROM users 
    WHERE id = user_uuid;
    
    RETURN subscription_status = 'premium';
END;
$$ LANGUAGE plpgsql;

-- Function to get user's prescription count (for free tier limits)
CREATE OR REPLACE FUNCTION get_user_prescription_count(user_uuid UUID)
RETURNS INTEGER AS $$
DECLARE
    prescription_count INTEGER;
BEGIN
    SELECT COUNT(*)
    INTO prescription_count
    FROM prescriptions
    WHERE patient_id = user_uuid
    AND status != 'archived';
    
    RETURN COALESCE(prescription_count, 0);
END;
$$ LANGUAGE plpgsql;

-- Function to check if user can create new prescription (free tier limit)
CREATE OR REPLACE FUNCTION can_create_prescription(user_uuid UUID)
RETURNS BOOLEAN AS $$
DECLARE
    is_premium BOOLEAN;
    current_count INTEGER;
    max_prescriptions INTEGER;
BEGIN
    -- Check if user has premium subscription
    SELECT user_has_premium_subscription(user_uuid) INTO is_premium;
    
    -- Premium users have unlimited prescriptions
    IF is_premium THEN
        RETURN TRUE;
    END IF;
    
    -- Get current prescription count
    SELECT get_user_prescription_count(user_uuid) INTO current_count;
    
    -- Get max prescriptions for free tier (default 10)
    SELECT COALESCE((limits->>'max_prescriptions')::INTEGER, 10)
    INTO max_prescriptions
    FROM subscription_plans
    WHERE tier = 'free'
    AND is_active = TRUE
    LIMIT 1;
    
    RETURN current_count < max_prescriptions;
END;
$$ LANGUAGE plpgsql;

-- Function to get user's AI request count for current month
CREATE OR REPLACE FUNCTION get_monthly_ai_requests(user_uuid UUID)
RETURNS INTEGER AS $$
DECLARE
    request_count INTEGER;
BEGIN
    SELECT COUNT(*)
    INTO request_count
    FROM usage_analytics
    WHERE user_id = user_uuid
    AND event_type IN ('ai_report_generated', 'ai_chat_message', 'ai_ocr_correction')
    AND created_at >= date_trunc('month', NOW());
    
    RETURN COALESCE(request_count, 0);
END;
$$ LANGUAGE plpgsql;

-- Function to check if user can make AI request
CREATE OR REPLACE FUNCTION can_make_ai_request(user_uuid UUID)
RETURNS BOOLEAN AS $$
DECLARE
    is_premium BOOLEAN;
    current_requests INTEGER;
    max_requests INTEGER;
BEGIN
    -- Check if user has premium subscription
    SELECT user_has_premium_subscription(user_uuid) INTO is_premium;
    
    -- Free users cannot make AI requests
    IF NOT is_premium THEN
        RETURN FALSE;
    END IF;
    
    -- Get current month's AI request count
    SELECT get_monthly_ai_requests(user_uuid) INTO current_requests;
    
    -- Get max AI requests for premium tier
    SELECT COALESCE((limits->>'ai_requests')::INTEGER, 1000)
    INTO max_requests
    FROM subscription_plans
    WHERE tier = 'premium'
    AND is_active = TRUE
    LIMIT 1;
    
    -- -1 means unlimited
    IF max_requests = -1 THEN
        RETURN TRUE;
    END IF;
    
    RETURN current_requests < max_requests;
END;
$$ LANGUAGE plpgsql;

-- Function to create user invitation code for doctor-patient relationship
CREATE OR REPLACE FUNCTION generate_invitation_code()
RETURNS VARCHAR(50) AS $$
DECLARE
    code VARCHAR(50);
    code_exists BOOLEAN;
BEGIN
    LOOP
        -- Generate 8-character alphanumeric code
        code := upper(substring(md5(random()::text) from 1 for 8));
        
        -- Check if code already exists
        SELECT EXISTS(
            SELECT 1 FROM doctor_patient_relationships 
            WHERE invitation_code = code
        ) INTO code_exists;
        
        -- Exit loop if code is unique
        IF NOT code_exists THEN
            EXIT;
        END IF;
    END LOOP;
    
    RETURN code;
END;
$$ LANGUAGE plpgsql;

-- Function to validate doctor-patient relationship
CREATE OR REPLACE FUNCTION validate_doctor_patient_access(doctor_uuid UUID, patient_uuid UUID)
RETURNS BOOLEAN AS $$
DECLARE
    relationship_exists BOOLEAN;
BEGIN
    SELECT EXISTS(
        SELECT 1 FROM doctor_patient_relationships
        WHERE doctor_id = doctor_uuid
        AND patient_id = patient_uuid
        AND status = 'active'
    ) INTO relationship_exists;
    
    RETURN relationship_exists;
END;
$$ LANGUAGE plpgsql;

-- Function to get user's active medication reminders
CREATE OR REPLACE FUNCTION get_active_reminders(user_uuid UUID)
RETURNS TABLE(
    reminder_id UUID,
    medication_name VARCHAR(200),
    dosage VARCHAR(200),
    next_reminder_time TIMESTAMP,
    reminder_times TIME[]
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        mr.id,
        m.name,
        m.dosage,
        -- Calculate next reminder time
        (CURRENT_DATE + (
            SELECT t FROM unnest(mr.reminder_times) t 
            WHERE t > CURRENT_TIME 
            ORDER BY t LIMIT 1
        ))::TIMESTAMP as next_reminder_time,
        mr.reminder_times
    FROM medication_reminders mr
    JOIN medications m ON mr.medication_id = m.id
    WHERE mr.patient_id = user_uuid
    AND mr.is_active = TRUE
    AND (mr.end_date IS NULL OR mr.end_date >= CURRENT_DATE)
    ORDER BY next_reminder_time;
END;
$$ LANGUAGE plpgsql;

-- Function to log medication reminder action
CREATE OR REPLACE FUNCTION log_medication_reminder(
    reminder_uuid UUID,
    action_status VARCHAR(20),
    action_notes TEXT DEFAULT NULL
)
RETURNS VOID AS $$
DECLARE
    scheduled_time TIMESTAMP;
BEGIN
    -- Calculate the scheduled time for this reminder
    SELECT (CURRENT_DATE + CURRENT_TIME)::TIMESTAMP INTO scheduled_time;
    
    -- Insert log entry
    INSERT INTO medication_reminder_logs (
        reminder_id,
        scheduled_time,
        actual_time,
        status,
        notes
    ) VALUES (
        reminder_uuid,
        scheduled_time,
        NOW(),
        action_status,
        action_notes
    );
    
    -- Update reminder statistics
    UPDATE medication_reminders
    SET 
        completed_doses = CASE 
            WHEN action_status = 'taken' THEN completed_doses + 1
            ELSE completed_doses
        END,
        missed_doses = CASE 
            WHEN action_status = 'missed' THEN missed_doses + 1
            ELSE missed_doses
        END,
        updated_at = NOW()
    WHERE id = reminder_uuid;
END;
$$ LANGUAGE plpgsql;

-- Function to clean up expired sessions
CREATE OR REPLACE FUNCTION cleanup_expired_sessions()
RETURNS INTEGER AS $$
DECLARE
    deleted_count INTEGER;
BEGIN
    DELETE FROM user_sessions
    WHERE expires_at < NOW();
    
    GET DIAGNOSTICS deleted_count = ROW_COUNT;
    RETURN deleted_count;
END;
$$ LANGUAGE plpgsql;

-- Function to archive old prescriptions (for data management)
CREATE OR REPLACE FUNCTION archive_old_prescriptions(days_old INTEGER DEFAULT 365)
RETURNS INTEGER AS $$
DECLARE
    archived_count INTEGER;
BEGIN
    UPDATE prescriptions
    SET status = 'archived',
        updated_at = NOW()
    WHERE created_at < (NOW() - INTERVAL '1 day' * days_old)
    AND status = 'completed';
    
    GET DIAGNOSTICS archived_count = ROW_COUNT;
    RETURN archived_count;
END;
$$ LANGUAGE plpgsql;

-- Function to get user statistics (for admin dashboard)
CREATE OR REPLACE FUNCTION get_user_statistics()
RETURNS TABLE(
    total_users BIGINT,
    active_users BIGINT,
    premium_users BIGINT,
    doctors BIGINT,
    patients BIGINT,
    new_users_this_month BIGINT
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        COUNT(*) as total_users,
        COUNT(*) FILTER (WHERE is_active = TRUE) as active_users,
        COUNT(*) FILTER (WHERE subscription_tier = 'premium') as premium_users,
        COUNT(*) FILTER (WHERE role = 'doctor') as doctors,
        COUNT(*) FILTER (WHERE role = 'patient') as patients,
        COUNT(*) FILTER (WHERE created_at >= date_trunc('month', NOW())) as new_users_this_month
    FROM users;
END;
$$ LANGUAGE plpgsql;

-- Function to get prescription statistics
CREATE OR REPLACE FUNCTION get_prescription_statistics()
RETURNS TABLE(
    total_prescriptions BIGINT,
    completed_prescriptions BIGINT,
    processing_prescriptions BIGINT,
    avg_ocr_confidence NUMERIC,
    prescriptions_this_month BIGINT
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        COUNT(*) as total_prescriptions,
        COUNT(*) FILTER (WHERE status = 'completed') as completed_prescriptions,
        COUNT(*) FILTER (WHERE status = 'processing') as processing_prescriptions,
        ROUND(AVG(ocr_confidence_score), 4) as avg_ocr_confidence,
        COUNT(*) FILTER (WHERE created_at >= date_trunc('month', NOW())) as prescriptions_this_month
    FROM prescriptions;
END;
$$ LANGUAGE plpgsql;