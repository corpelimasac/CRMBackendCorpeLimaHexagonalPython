#!/bin/bash
# ============================================
# Script para cambiar entre entornos
# ============================================

set -e

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

show_help() {
    echo "============================================"
    echo "🌍 Cambiar Entorno de CRM Backend"
    echo "============================================"
    echo ""
    echo "Uso: ./switch-env.sh [entorno]"
    echo ""
    echo "Entornos disponibles:"
    echo "  dev         → Desarrollo (SQLite local)"
    echo "  prod        → Producción (MySQL cloud)"
    echo "  staging     → Staging (opcional)"
    echo ""
    echo "Ejemplos:"
    echo "  ./switch-env.sh dev"
    echo "  ./switch-env.sh prod"
    echo ""
}

if [ $# -eq 0 ]; then
    show_help
    exit 1
fi

ENV=$1

case $ENV in
    dev|development)
        if [ ! -f "$SCRIPT_DIR/.env.development" ]; then
            echo "❌ Error: .env.development no existe"
            exit 1
        fi
        cp "$SCRIPT_DIR/.env.development" "$SCRIPT_DIR/.env"
        echo "✅ Configuración cambiada a DESARROLLO"
        echo "🗄️  Base de datos: SQLite local"
        echo "🐛 Debug: Activado"
        ;;

    prod|production)
        if [ ! -f "$SCRIPT_DIR/.env.production" ]; then
            echo "❌ Error: .env.production no existe"
            exit 1
        fi

        echo "⚠️  ¡CUIDADO! Vas a usar la base de datos de PRODUCCIÓN"
        read -p "¿Estás seguro? (yes/no): " confirm

        if [ "$confirm" != "yes" ]; then
            echo "❌ Operación cancelada"
            exit 1
        fi

        cp "$SCRIPT_DIR/.env.production" "$SCRIPT_DIR/.env"
        echo "✅ Configuración cambiada a PRODUCCIÓN"
        echo "🗄️  Base de datos: MySQL cloud"
        echo "🐛 Debug: Desactivado"
        ;;

    *)
        echo "❌ Error: Entorno '$ENV' no reconocido"
        show_help
        exit 1
        ;;
esac

echo ""
echo "Configuración actual en .env:"
grep "^ENVIRONMENT=" "$SCRIPT_DIR/.env" || echo "ENVIRONMENT no configurado"
echo ""
echo "Para iniciar la aplicación ejecuta:"
echo "  python -m uvicorn app.main:app --reload"
