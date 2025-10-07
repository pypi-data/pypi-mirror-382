CREATE OR REPLACE FUNCTION get_test_text(input_test_id INTEGER)
RETURNS TEXT AS $$
DECLARE
    test_text TEXT;
BEGIN
    SELECT t.test_text INTO test_text
    FROM test AS t
    WHERE t.test_id = input_test_id;

    RETURN test_text;
END;
$$ LANGUAGE plpgsql;
