@echo off
echo "[STEP]: Stopping and removing containers..."
docker-compose down

echo "[STEP]: Clean up data from containers..."
IF EXIST "resources\logs" (
    for /d %%D in ("resources\logs\*") do rd /s /q "%%D"
    del /q "resources\logs\*"
)

echo "[STATUS]: Successfully removed containers and data."
