#!/bin/bash
# Script wrapper para ejecutar sospechoso-go
#
# Uso:
#   ./run-sospechoso-go.sh [GRUPO] [TARGET_REF]
#
# Ejemplos:
#   ./run-sospechoso-go.sh mccartney
#   ./run-sospechoso-go.sh wanda refs/heads/main
#   TARGET_REF=refs/remotes/origin/main ./run-sospechoso-go.sh tabuk

set -e

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Directorio del script
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
GO_PROJECT_DIR="$SCRIPT_DIR/sospechoso-go"

# Función para mostrar ayuda
show_help() {
    echo -e "${BLUE}🔍 Sospechoso-Go: Detector de Autores Latentes${NC}"
    echo ""
    echo "Uso:"
    echo "  $0 [GRUPO] [TARGET_REF]"
    echo ""
    echo "Argumentos:"
    echo "  GRUPO      Nombre del grupo a analizar (default: mccartney)"
    echo "  TARGET_REF Referencia objetivo específica (opcional)"
    echo ""
    echo "Variables de entorno:"
    echo "  TARGET_REF  Referencia objetivo (ej: refs/remotes/origin/main)"
    echo ""
    echo "Ejemplos:"
    echo "  $0 mccartney"
    echo "  $0 wanda refs/heads/main"
    echo "  TARGET_REF=refs/remotes/origin/main $0 tabuk"
    echo ""
    echo "Comandos especiales:"
    echo "  $0 test           # Ejecutar tests básicos"
    echo "  $0 test-single    # Test con un solo repositorio"
    echo "  $0 build          # Solo compilar"
    echo "  $0 benchmark      # Comparar con Python"
    echo "  $0 help           # Mostrar esta ayuda"
}

# Verificar si el directorio Go existe
if [ ! -d "$GO_PROJECT_DIR" ]; then
    echo -e "${RED}❌ Error: Directorio del proyecto Go no encontrado: $GO_PROJECT_DIR${NC}"
    exit 1
fi

cd "$GO_PROJECT_DIR"

# Manejar argumentos especiales
case "${1:-}" in
    "help"|"-h"|"--help")
        show_help
        exit 0
        ;;
    "test")
        echo -e "${BLUE}🧪 Ejecutando tests básicos...${NC}"
        make build >/dev/null 2>&1
        ./sospechoso-go test
        exit 0
        ;;
    "test-single")
        echo -e "${BLUE}🧪 Ejecutando test de repositorio completo...${NC}"
        make build >/dev/null 2>&1
        ./sospechoso-go test-single
        exit 0
        ;;
    "build")
        echo -e "${BLUE}🔨 Compilando proyecto...${NC}"
        make build
        echo -e "${GREEN}✅ Compilación completada${NC}"
        exit 0
        ;;
    "benchmark")
        echo -e "${BLUE}📊 Ejecutando benchmark...${NC}"
        make benchmark
        exit 0
        ;;
esac

# Configuración
GRUPO="${1:-mccartney}"
TARGET_REF_ARG="${2:-}"

# Si se pasó TARGET_REF como argumento, usarlo
if [ -n "$TARGET_REF_ARG" ]; then
    export TARGET_REF="$TARGET_REF_ARG"
fi

# Verificar que el directorio de grupos existe
GROUPS_DIR="/Users/drestrepo/Documents/groups/$GRUPO"
if [ ! -d "$GROUPS_DIR" ]; then
    echo -e "${RED}❌ Error: Directorio de grupo no encontrado: $GROUPS_DIR${NC}"
    echo -e "${YELLOW}💡 Grupos disponibles:${NC}"
    ls -1 "/Users/drestrepo/Documents/groups/" 2>/dev/null | head -5
    exit 1
fi

# Compilar si es necesario
if [ ! -f "sospechoso-go" ] || [ "main.go" -nt "sospechoso-go" ]; then
    echo -e "${YELLOW}🔨 Compilando proyecto...${NC}"
    make build >/dev/null 2>&1
fi

# Mostrar información de configuración
echo -e "${BLUE}🚀 Iniciando análisis${NC}"
echo -e "${BLUE}📁 Grupo:${NC} $GRUPO"
echo -e "${BLUE}📂 Directorio:${NC} $GROUPS_DIR"
if [ -n "${TARGET_REF:-}" ]; then
    echo -e "${BLUE}🎯 Target ref:${NC} $TARGET_REF"
fi

# Contar repositorios
REPO_COUNT=$(find "$GROUPS_DIR" -mindepth 1 -maxdepth 1 -type d | wc -l | tr -d ' ')
echo -e "${BLUE}📊 Repositorios:${NC} $REPO_COUNT"

echo ""

# Ejecutar análisis y medir tiempo
echo -e "${GREEN}⚡ Ejecutando análisis...${NC}"
start_time=$(date +%s)

./sospechoso-go "$GRUPO"
exit_code=$?

end_time=$(date +%s)
duration=$((end_time - start_time))

echo ""

if [ $exit_code -eq 0 ]; then
    echo -e "${GREEN}✅ Análisis completado exitosamente${NC}"
    echo -e "${BLUE}⏱️  Tiempo total:${NC} ${duration}s"
    
    # Mostrar información del archivo de resultados
    RESULTS_FILE="results_${GRUPO}_go.csv"
    if [ -f "$RESULTS_FILE" ]; then
        LINES=$(wc -l < "$RESULTS_FILE" | tr -d ' ')
        SIZE=$(du -h "$RESULTS_FILE" | cut -f1)
        echo -e "${BLUE}📋 Resultados:${NC} $((LINES-1)) commits sospechosos"
        echo -e "${BLUE}📄 Archivo:${NC} $RESULTS_FILE ($SIZE)"
        
        # Mostrar las primeras líneas como preview
        if [ $LINES -gt 1 ]; then
            echo ""
            echo -e "${YELLOW}🔍 Preview de resultados:${NC}"
            head -3 "$RESULTS_FILE" | tail -2 | cut -d',' -f1,4,11,23 | \
                sed 's/,/ | /g' | \
                while IFS= read -r line; do
                    echo -e "   ${GREEN}•${NC} $line"
                done
            if [ $LINES -gt 3 ]; then
                echo -e "   ${YELLOW}... y $((LINES-3)) más${NC}"
            fi
        fi
    fi
else
    echo -e "${RED}❌ Error en el análisis (código: $exit_code)${NC}"
    exit $exit_code
fi

echo ""
echo -e "${BLUE}🎉 ¡Listo! Revisa el archivo CSV para ver los resultados detallados.${NC}"
