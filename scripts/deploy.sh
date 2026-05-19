#!/usr/bin/env bash
# Script de despliegue automatizado (Ubuntu/AWS o cualquier host con Docker)
# Si obtiene "permission denied", ejecute: sudo ./scripts/deploy.sh
set -euo pipefail

if docker info >/dev/null 2>&1; then
  DOCKER="docker"
else
  echo "==> Usando sudo (usuario sin permisos en el grupo docker)"
  DOCKER="sudo docker"
fi

echo "==> Construyendo imagen..."
$DOCKER compose build

echo "==> Levantando servicio (puerto 8080 -> 5000, reinicio automático)..."
$DOCKER compose up -d

echo "==> Estado del contenedor:"
$DOCKER compose ps

IP=$(hostname -I 2>/dev/null | awk '{print $1}')
echo ""
echo "Listo. Pruebe:"
echo "  http://${IP:-localhost}:8080/"
echo "  http://${IP:-localhost}:8080/health"
echo "  http://${IP:-localhost}:8080/api/info"
