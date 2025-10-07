@echo off
REM ============================================
REM Script para cambiar entre entornos (Windows)
REM ============================================

setlocal

if "%1"=="" (
    goto :show_help
)

if /i "%1"=="dev" goto :dev
if /i "%1"=="development" goto :dev
if /i "%1"=="prod" goto :prod
if /i "%1"=="production" goto :prod
goto :invalid

:dev
    if not exist ".env.development" (
        echo [ERROR] .env.development no existe
        exit /b 1
    )
    copy /Y ".env.development" ".env" >nul
    echo [OK] Configuracion cambiada a DESARROLLO
    echo [INFO] Base de datos: SQLite local
    echo [INFO] Debug: Activado
    goto :end

:prod
    if not exist ".env.production" (
        echo [ERROR] .env.production no existe
        exit /b 1
    )

    echo [ATENCION] Vas a usar la base de datos de PRODUCCION
    set /p confirm="Estas seguro? (yes/no): "

    if not "%confirm%"=="yes" (
        echo [CANCELADO] Operacion cancelada
        exit /b 1
    )

    copy /Y ".env.production" ".env" >nul
    echo [OK] Configuracion cambiada a PRODUCCION
    echo [INFO] Base de datos: MySQL cloud
    echo [INFO] Debug: Desactivado
    goto :end

:invalid
    echo [ERROR] Entorno '%1' no reconocido
    goto :show_help

:show_help
    echo ============================================
    echo Cambiar Entorno de CRM Backend
    echo ============================================
    echo.
    echo Uso: switch-env.bat [entorno]
    echo.
    echo Entornos disponibles:
    echo   dev         - Desarrollo (SQLite local)
    echo   prod        - Produccion (MySQL cloud)
    echo.
    echo Ejemplos:
    echo   switch-env.bat dev
    echo   switch-env.bat prod
    echo.
    exit /b 1

:end
    echo.
    echo Configuracion actual en .env:
    findstr /B "ENVIRONMENT=" .env 2>nul || echo ENVIRONMENT no configurado
    echo.
    echo Para iniciar la aplicacion ejecuta:
    echo   python -m uvicorn app.main:app --reload
    echo.

endlocal
