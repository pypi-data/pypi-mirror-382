CREATE OR REPLACE FUNCTION get_file_count()
RETURNS INTEGER AS $$
DECLARE
    file_count INTEGER;
BEGIN
    SELECT COUNT(*) INTO file_count
    FROM file;

    RETURN file_count;
END;
$$ LANGUAGE plpgsql;