#!/usr/bin/env bash
# Script de despliegue automatizado (Ubuntu/AWS o cualquier host con Docker)
set -euo pipefail

echo "==> Construyendo imagen..."
docker compose build

echo "==> Levantando servicio (puerto 8080 -> 5000, reinicio automático)..."
docker compose up -d

echo "==> Estado del contenedor:"
docker compose ps

echo ""
echo "Listo. Pruebe:"
echo "  http://$(hostname -I | awk '{print $1}'):8080/"
echo "  http://$(hostname -I | awk '{print $1}'):8080/health"
echo "  http://$(hostname -I | awk '{print $1}'):8080/api/info"
