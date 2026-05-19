# Servicio Telemático Dockerizado

**Examen 3 — Telemática**  
**Autor:** Juan Sebastián Quintero Hwernández  
**Repositorio:** [https://github.com/JuanseQH/examen-telematica](https://github.com/JuanseQH/examen-telematica)

Servicio web telemático desplegado en contenedores Docker. Incluye una aplicación **Flask** con página principal interactiva (Tetris en el navegador), endpoints JSON de salud e información, y automatización de construcción mediante **Dockerfile**, **docker compose** y **GitHub Actions** (desarrollo continuo).

El profesor puede clonar el repositorio, construir la imagen y ejecutar el contenedor **sin configuración adicional**.

---

## Descripción del servicio

| Ruta | Descripción |
|------|-------------|
| `GET /` | Página HTML con Tetris web, información del examen y enlaces a la API |
| `GET /health` | JSON de estado del servicio (`status: ok`) — útil para balanceadores y monitoreo |
| `GET /api/info` | JSON con metadatos del proyecto, tecnologías, autor y rutas |

La aplicación escucha en `0.0.0.0:5000` dentro del contenedor. En producción se publica con `-p 8080:5000` (host **8080** → contenedor **5000**).

### Tetris web

El juego en el navegador (`static/tetris/`) está basado en la lógica de un Tetris propio, adaptado a **JavaScript + Canvas** para ejecutarse como servicio web consumible.

---

## Arquitectura y escalabilidad

- **Cliente–servidor:** navegador (HTML/JS) ↔ Flask (API + plantillas).
- **Contenedor stateless:** no depende de disco local; apto para réplicas.
- **Health check:** `/health` para comprobar disponibilidad (Docker `HEALTHCHECK` y `docker compose`).
- **Escalamiento horizontal (concepto):** se pueden levantar varias instancias del mismo contenedor detrás de un balanceador; todas exponen `/health` y sirven la misma imagen.
- **Producción:** **Gunicorn** (WSGI) en lugar del servidor de desarrollo de Flask.

---

## Estructura del proyecto

```
/
├── app.py                 # Aplicación Flask (rutas y factory)
├── requirements.txt       # Dependencias Python (Flask, Gunicorn)
├── Dockerfile             # Build automatizado de la imagen
├── docker-compose.yml     # Despliegue con reinicio automático
├── .dockerignore          # Excluye venv, .git, etc.
├── .github/workflows/ci.yml  # CI: build Docker en cada push
├── scripts/deploy.sh      # Script de despliegue en Linux/AWS
├── README.md              # Este manual
├── templates/
│   └── index.html         # Página principal
└── static/
    ├── styles.css         # Estilos de la página
    └── tetris/
        ├── tetris.js      # Motor del juego (Canvas)
        └── tetris.css     # Estilos del juego
```

---

## Requisitos previos

- **Git**
- **Docker Engine** y **Docker Compose** (plugin `compose` v2)
- En AWS: instancia **Ubuntu** con puerto **8080** abierto en el Security Group

---

## Despliegue rápido (recomendado)

Desde la raíz del repositorio:

```bash
git clone https://github.com/JuanseQH/examen-telematica.git
cd examen-telematica

# Opción A: docker compose (reinicio automático unless-stopped)
docker compose up -d --build

# Opción B: script en Linux/AWS
chmod +x scripts/deploy.sh
./scripts/deploy.sh
```

Verificar:

```bash
docker compose ps
curl http://localhost:8080/health
curl http://localhost:8080/api/info
```

Abrir en el navegador: `http://localhost:8080` (o `http://IP_PUBLICA:8080` en la nube).

---

## Despliegue manual con Docker

```bash
docker build -t examen-telematica .
docker run -d --restart unless-stopped -p 8080:5000 --name examen-telematica examen-telematica
docker ps
docker logs examen-telematica
```

Detener y eliminar:

```bash
docker stop examen-telematica
docker rm examen-telematica
```

---

## Despliegue en Ubuntu / AWS

```bash
# 1. Conectar por SSH
ssh -i tu-clave.pem ubuntu@IP_PUBLICA

# 2. Instalar Docker
sudo apt update
sudo apt install -y git docker.io docker-compose-v2
sudo systemctl enable --now docker
sudo usermod -aG docker $USER
# Cerrar sesión y volver a entrar para aplicar el grupo docker

# 3. Clonar y desplegar
git clone https://github.com/JuanseQH/examen-telematica.git
cd examen-telematica
docker compose up -d --build

# 4. Abrir en el Security Group de AWS: puerto TCP 8080 (origen 0.0.0.0/0 o tu IP)

# 5. Probar desde su PC
curl http://IP_PUBLICA:8080/health
```

En el navegador: `http://IP_PUBLICA:8080`

---

## Desarrollo continuo (CI/CD)

En cada **push** o **pull request** a `main`, GitHub Actions (`.github/workflows/ci.yml`):

1. Construye la imagen Docker.
2. Ejecuta un contenedor de prueba.
3. Verifica que `/health` y `/api/info` respondan.

Flujo recomendado de trabajo:

```text
código local → git commit → git push → CI valida build → servidor AWS: git pull && docker compose up -d --build
```

---

## Prueba local sin Docker

```bash
python -m venv venv
# Windows:  .\venv\Scripts\Activate.ps1
# Linux:    source venv/bin/activate
pip install -r requirements.txt
python app.py
```

Abrir [http://localhost:5000](http://localhost:5000).

Para simular producción local con Gunicorn:

```bash
gunicorn --bind 0.0.0.0:5000 --workers 2 app:app
```

---

## Modificación del proyecto

| Qué cambiar | Dónde |
|-------------|--------|
| Rutas o JSON de la API | `app.py` |
| Página principal / textos | `templates/index.html` |
| Estilos generales | `static/styles.css` |
| Lógica del Tetris | `static/tetris/tetris.js` |
| Estilos del juego | `static/tetris/tetris.css` |
| Dependencias Python | `requirements.txt` + reconstruir imagen |
| Puerto o workers | `Dockerfile`, `docker-compose.yml` |

Tras cambios en producción:

```bash
docker compose up -d --build
```

---

## Dockerfile (resumen)

1. Imagen base `python:3.10-slim`
2. Instalación de dependencias desde `requirements.txt`
3. Copia del código de la aplicación
4. `HEALTHCHECK` contra `/health`
5. Arranque con **Gunicorn** (`app:app`)

---

## Uso de GitHub y trazabilidad

```bash
git add .
git commit -m "Descripción clara del cambio"
git push origin main
```

Commits sugeridos para evidenciar evolución: estructura inicial → Flask → Docker → Tetris web → Gunicorn/CI → documentación.

---

## Checklist de entrega (rúbrica)

### 40 % — Docker, nube y estabilidad

- [x] `Dockerfile` en la raíz
- [x] Build automatizado (`docker build` / `docker compose build`)
- [x] Contenedor con `--restart unless-stopped` (en `docker-compose.yml`)
- [x] Gunicorn para producción
- [x] `HEALTHCHECK` en imagen
- [ ] **Usted:** desplegar en AWS y confirmar `http://IP_PUBLICA:8080/health`

### 20 % — README y código comentado

- [x] README con despliegue local, Docker, AWS y modificación
- [x] Código comentado en `app.py`, `Dockerfile`, `tetris.js`

### 30 % — Repositorio GitHub

- [x] Repositorio público con historial de commits
- [x] Enlace: https://github.com/JuanseQH/examen-telematica

### 10 % — Funcionamiento para usuarios

- [x] `/`, `/health`, `/api/info` operativos
- [x] Tetris jugable en navegador
- [ ] **Usted:** prueba final desde navegador contra IP pública AWS

---

## Enlace de entrega

Entregar al profesor:

**https://github.com/JuanseQH/examen-telematica**

Tras desplegar en AWS, indicar también la URL de consumo, por ejemplo: `http://EC2_IP_PUBLICA:8080`

---

## Conclusión

Proyecto listo para evaluación: servicio telemático contenerizado, documentado, versionado en GitHub, con CI y despliegue reproducible. La verificación final en AWS confirma el 40 % restante de la rúbrica relacionado con servidor en la nube.
