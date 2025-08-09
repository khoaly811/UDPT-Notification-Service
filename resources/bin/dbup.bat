@echo off

setlocal enabledelayedexpansion

cd .

call :echoStep "Starting Docker containers..."
docker-compose up -d
if !errorlevel! neq 0 (
    call :echoErr "Error starting Docker containers. Exiting script."
    exit /b !errorlevel!
)

call :echoStatus "Waiting to establish connections to all containers..."
set MAX_ATTEMPTS=40
set INTERVAL=5

for /L %%i in (1,1,%MAX_ATTEMPTS%) do (
    set "all_ready=true"

    REM Check Redis connection
    docker exec -i redis_container redis-cli ping >nul 2>&1
    if !errorlevel! neq 0 (
        call :echoStatus "Wait for Redis connection to be ready."
        set "all_ready=false"
    )

    REM Check MongoDB connection
    docker exec -i mongo_container /usr/bin/mongosh --eval "db.runCommand({ping:1})" >nul 2>&1
    if !errorlevel! neq 0 (
        call :echoStatus "Wait For MongoDB connection to be ready."
        set "all_ready=false"
    )

    REM Check Postgres connection
    docker exec -i postgres_container pg_isready -U postgres >nul 2>&1
    if !errorlevel! neq 0 (
        call :echoStatus "Wait for Postgres connection to be ready."
        set "all_ready=false"
    )

    REM Exit loop if all connections are ready
    if "!all_ready!"=="true" (
        call :echoStatus "Connections to all containers established successfully!"
        goto all_connections_ready
    )

    call :echoStatus "Retrying in %INTERVAL% seconds..."
    timeout /t %INTERVAL% >nul
)

call :echoErr "Unable to establish connections to all containers after %MAX_ATTEMPTS% time."
exit /b 1

:all_connections_ready
call :echoStatus "All containers are ready."
call :echoStep "Migration data base..."

call :echoStatus "Mounting migration scripts for mongoDB container..."
set "mongo_error=0"
docker cp ".\resources\scripts\mongoDB" mongo_container:/scripts/
if !errorlevel! neq 0 (
    set "mongo_error=1"
    call :echoErr "Failed to copy migration scripts to MongoDB container."
    exit /b !errorlevel!
)

call :echoStatus "Executing all .js scripts inside MongoDB container..."
for %%f in (.\resources\scripts\mongoDB\*.js) do (
    echo Running %%~nxf...
    docker exec -i mongo_container /usr/bin/mongosh /scripts/%%~nxf
    if !errorlevel! neq 0 (
        set "mongo_error=1"
        call :echoErr "Failed to execute %%~nxf inside MongoDB. Continuing with the next file..."
    )
)
if !mongo_error! equ 0 (
    call :echoSuccess "MongoDB has been initialized successfully with JavaScript scripts!"
)

call :echoStatus "Mounting mirgation scripts to Redis cointainter..."
set "redis_error=0"
docker cp ".\resources\scripts\redis" redis_container:/data/
if !errorlevel! neq 0 (
    set "redis_error=1"
    call :echoErr "Failed to copy migration scripts to Redis container."
    exit /b !errorlevel!
)

call :echoStatus "Restoring all .rdb files inside Redis container..."
for %%f in (.\resources\scripts\redis\*.rdb) do (
    echo Restoring %%~nxf...
    docker exec -i redis_container sh -c "cat /data/redis/%%~nxf | redis-cli --pipe"
    if !errorlevel! neq 0 (
        set "redis_error=1"
        call :echoErr "Failed to restore %%~nxf into Redis. Continuing with the next file..."
    )
)
if !redis_error! equ 0 (
    call :echoSuccess "Redis has been initialized successfully with data!"
)
REM --- Postgres Migration Step ---
call :echoStatus "Mounting migration scripts to Postgres container..."
set "postgres_error=0"
docker cp ".\resources\scripts\postgres" postgres_container:/scripts/
if !errorlevel! neq 0 (
    set "postgres_error=1"
    call :echoErr "Failed to copy migration scripts to Postgres container."
    exit /b !errorlevel!
)

call :echoStatus "Migrating all .sql scripts inside Postgres container..."
for %%f in (.\resources\scripts\postgres\*.sql) do (
    echo Running %%~nxf...
    docker exec -i postgres_container psql -U postgres -d postgres -f /scripts/%%~nxf
    if !errorlevel! neq 0 (
        set "postgres_error=1"
        call :echoErr "Failed to execute %%~nxf inside Postgres. Continuing with the next file..."
    )
)
if !postgres_error! equ 0 (
    call :echoSuccess "Postgres has been initialized successfully with SQL scripts!"
)

call :echoSuccess "All services have been initialized successfully!"

REM --- Color echo functions ---
:echoStatus
REM Print [STATUS] in cyan, rest normal
echo|set /p="[36mINFO[0m: "
echo %~1
goto :eof

:echoSuccess
REM Print [SUCCESS] in green, rest normal
echo|set /p="[32mSUCCESS[0m: "
echo %~1
goto :eof

:echoErr
REM Print [ERR] in red,1 rest normal
echo|set /p="[31mERR[0m: "
echo %~1
goto :eof

:echoStep
REM Print [STEP] in yellow, rest normal
echo|set /p="[33mSTEP[0m: "
echo %~1
goto :eof
