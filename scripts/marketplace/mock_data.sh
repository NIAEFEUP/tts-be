# It is fine to use the password like this because this is only intended to use
# in development environments and it will only be available so
PGPASSWORD='root' psql -h localhost -p 5432 -U root -d tts -f mock_data.sql
