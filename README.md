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

### ¿Por qué el Dockerfile usa Python si el Tetris es JavaScript?

Es habitual preguntarse por qué la imagen Docker se basa en `python:3.10-slim` cuando el juego ya no usa Pygame. La respuesta es que el proyecto tiene **dos capas distintas**, no una sola tecnología:

| Parte | Tecnología | Dónde se ejecuta |
|-------|------------|------------------|
| **Servicio web (requerimiento del examen)** | Python + Flask + Gunicorn | Servidor (contenedor Docker / nube) |
| **Tetris (contenido interactivo)** | JavaScript + Canvas | **Navegador del usuario** (cliente) |

El examen solicita un **servicio telemático web desplegado en contenedores**. Ese servicio es la aplicación Flask: entrega la página HTML, los archivos estáticos (`tetris.js`, `tetris.css`, estilos) y los endpoints JSON (`/health`, `/api/info`). El Tetris **no se ejecuta dentro del contenedor en Python**; el servidor solo **sirve** esos archivos y el navegador los descarga y ejecuta al abrir `http://IP:8080`.

Por eso el `Dockerfile` incluye Python:

1. **`app.py`** implementa el microservicio web con Flask.
2. **Gunicorn** actúa como servidor WSGI de producción (más estable que `flask run`).
3. **No hay Pygame ni lógica de juego en Python** en este repositorio: el motor del Tetris vive en `static/tetris/tetris.js`.

**Analogía:** es el mismo esquema que muchas aplicaciones web: el servidor entrega HTML, CSS y JavaScript; la lógica interactiva corre en el equipo del usuario. El contenedor “corre Python” porque **aloja el servicio web**; el Tetris “corre JavaScript” porque es la experiencia en el cliente.

**Qué se evalúa con este diseño:**

- Contenedor Docker con servicio web funcional → Python + Flask + Gunicorn.
- Servicio consumible desde el navegador → página con Tetris en JS y APIs JSON.
- Cumplimiento del enunciado (servicio telemático en red, no aplicación de escritorio aislada).

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
- **Docker Engine** con plugin **Compose v2** (comando `docker compose`, no `docker-compose` antiguo)
- **curl** (para pruebas en terminal; en Ubuntu: `sudo apt install -y curl`)
- En AWS: instancia **Ubuntu** con puerto **8080** (TCP) abierto en el Security Group

> **Nota sobre permisos:** en Linux recién instalado, Docker suele requerir `sudo` o agregar el usuario al grupo `docker` (ver sección AWS).

---

## Despliegue rápido (recomendado)

Desde la raíz del repositorio (Linux, macOS o Windows con Docker Desktop):

```bash
git clone https://github.com/JuanseQH/examen-telematica.git
cd examen-telematica

# Opción A: docker compose (reinicio automático unless-stopped)
docker compose up -d --build

# Si aparece "permission denied" en el socket de Docker, use:
# sudo docker compose up -d --build

# Opción B: script en Linux/AWS (detecta sudo automáticamente)
chmod +x scripts/deploy.sh
./scripts/deploy.sh
```

Verificar:

```bash
docker compose ps
curl -fsS http://localhost:8080/health
curl -fsS http://localhost:8080/api/info
```

Abrir en el navegador: `http://localhost:8080` (o `http://IP_PUBLICA:8080` en la nube).

---

## Despliegue manual con Docker

Equivalente a `docker compose`, sin usar el archivo YAML. **No mezcle** ambos métodos a la vez con el mismo nombre de contenedor.

```bash
# Desde la raíz del repositorio (donde está el Dockerfile)
docker build -t examen-telematica:latest .

docker run -d \
  --restart unless-stopped \
  -p 8080:5000 \
  --name examen-telematica \
  examen-telematica:latest

docker ps
docker logs examen-telematica
```

Detener y eliminar:

```bash
docker stop examen-telematica
docker rm examen-telematica
```

Reconstruir desde cero (tras cambiar código):

```bash
docker compose down
docker compose up -d --build

# O, si usó solo docker run:
docker stop examen-telematica && docker rm examen-telematica
docker rmi examen-telematica:latest
docker build -t examen-telematica:latest .
docker run -d --restart unless-stopped -p 8080:5000 --name examen-telematica examen-telematica:latest
```

---

## Despliegue en Ubuntu / AWS

```bash
# 1. Conectar por SSH (Ubuntu en EC2)
ssh -i ruta/a/tu-clave.pem ubuntu@IP_PUBLICA

# 2. Instalar Git, Docker y Compose
sudo apt update
sudo apt install -y git curl docker.io docker-compose-plugin
sudo systemctl enable --now docker

# 3. Permisos Docker (elija UNA opción)
# Opción A — inmediata: usar sudo en cada comando docker (recomendado la primera vez)
# Opción B — permanente: agregar usuario al grupo docker y reconectar SSH
sudo usermod -aG docker "$USER"
# Cerrar sesión SSH, volver a entrar, luego: docker ps

# 4. Clonar y desplegar
git clone https://github.com/JuanseQH/examen-telematica.git
cd examen-telematica
sudo docker compose up -d --build
# Sin sudo, si ya aplicó la opción B del paso 3:
# docker compose up -d --build

# 5. Verificar en el servidor
sudo docker compose ps
curl -fsS http://localhost:8080/health

# 6. Security Group de AWS: regla de entrada TCP puerto 8080

# 7. Probar desde su PC (reemplace IP_PUBLICA)
curl -fsS http://IP_PUBLICA:8080/health
```

En el navegador: `http://IP_PUBLICA:8080`

### Solución de problemas frecuentes

| Error | Causa | Solución |
|-------|--------|----------|
| `permission denied` en `/var/run/docker.sock` | Usuario sin permisos Docker | `sudo docker compose ...` o agregar al grupo `docker` y reconectar SSH |
| `docker compose: command not found` | Falta plugin Compose | `sudo apt install -y docker-compose-plugin` |
| `curl: command not found` | curl no instalado | `sudo apt install -y curl` |
| No carga en el navegador externo | Puerto cerrado en AWS | Abrir **8080/TCP** en el Security Group de la instancia |
| Conflicto de nombre de contenedor | Contenedor previo activo | `sudo docker compose down` y volver a ejecutar `up` |

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

Ejecutar siempre **desde la raíz del repositorio** (donde está `app.py`):

```bash
cd examen-telematica

python -m venv venv
# Windows (PowerShell):
.\venv\Scripts\Activate.ps1
# Linux / macOS:
source venv/bin/activate

pip install -r requirements.txt
python app.py
```

Abrir [http://localhost:5000](http://localhost:5000) (puerto **5000** en local; en Docker se publica como **8080**).

Para simular producción local con Gunicorn (mismo servidor que usa el contenedor):

```bash
# Con el entorno virtual activado y desde la raíz del repo
gunicorn --bind 0.0.0.0:5000 --workers 2 --threads 2 --timeout 60 app:app
```

Probar: [http://localhost:5000/health](http://localhost:5000/health)

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

Tras cambios en producción (en el servidor o local):

```bash
git pull
docker compose down
docker compose up -d --build
# En AWS sin grupo docker: sudo docker compose up -d --build
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

## Demostración en AWS (acceso para el profesor)

Además de clonar el repositorio y ejecutar el contenedor localmente, dejé configurada una **instancia de prueba en AWS** donde verifiqué el despliegue completo del servicio.

| Recurso | Valor |
|---------|--------|
| URL del servicio | [http://3.89.181.137:8080](http://3.89.181.137:8080) |
| Health check | [http://3.89.181.137:8080/health](http://3.89.181.137:8080/health) |
| API info | [http://3.89.181.137:8080/api/info](http://3.89.181.137:8080/api/info) |

**Importante:** la instancia EC2 puede estar **apagada** cuando no se esté evaluando, para evitar costos innecesarios. Si el profesor desea revisar el servicio en esa URL, le pido que me avise con anticipación (correo o Teams); en cuanto lo indique, **encenderé la instancia** y ejecutaré el contenedor con:

```bash
cd examen-telematica
sudo docker compose up -d --build
```

De ese modo el servicio quedará disponible en la IP indicada para su revisión. La entrega formal del examen sigue siendo el repositorio de GitHub; esta URL es un complemento opcional de demostración en la nube.

---

## Enlace de entrega

Entregar al profesor:

**https://github.com/JuanseQH/examen-telematica**

---
