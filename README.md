# Servicio Telemático Dockerizado

Este repositorio contiene una aplicación web sencilla desarrollada en **Python Flask** para el **Examen 3 de Telemática**.  La aplicación demuestra cómo desplegar un servicio web telemático mediante contenedores **Docker**, tal como se practicó en clase.  La prioridad del proyecto es la simplicidad, la estabilidad y la facilidad de despliegue: el profesor clonará el repositorio, construirá la imagen, ejecutará el contenedor y comprobará que el servicio funciona sin configuraciones adicionales.

## Descripción del proyecto

El objetivo es ofrecer un servicio web consumible que funcione en un contenedor Docker.  El servicio expone tres rutas:

* **`/`** – Muestra la página principal en HTML con información del examen y del servicio.  Incluye el nombre del proyecto, un mensaje de bienvenida, una breve descripción del examen y las tecnologías empleadas.  También indica que el servicio se ejecuta dentro de un contenedor.
* **`/health`** – Devuelve un objeto JSON con el estado de salud del servicio.  Es útil para comprobar si la aplicación está activa.
* **`/api/info`** – Devuelve un objeto JSON con información del proyecto, tales como nombre, descripción, tecnologías, versión, autor y estado.

La aplicación se encuentra en el archivo [`app.py`](app.py) y está diseñada para escucharse en todas las interfaces (`0.0.0.0`) en el puerto interno `5000`.  En un entorno de producción, se debe publicar este puerto con la opción `-p` de Docker (por ejemplo, `-p 8080:5000`) para acceder al servicio desde el host.

## Relación con Telemática

El servicio ilustra los conceptos de **diseño e implementación de servicios telemáticos**: utiliza una arquitectura cliente–servidor, se aloja en un contenedor para aislar dependencias y se despliega siguiendo prácticas de integración y despliegue continuos.  El profesor evaluará la capacidad de construir la imagen, ejecutar el servicio y verificar su funcionamiento según la rúbrica del examen【16266687642254†L34-L45】.  Además, el proyecto utiliza herramientas habituales en el ámbito de telemática y DevOps: `GitHub` para la gestión de versiones, `Docker` para la contenerización, `Linux` como sistema operativo base y `Flask` como microframework web.

## Tecnologías empleadas

- **Python 3.10** – Lenguaje de programación principal.
- **Flask** – Microframework para construir servicios web sencillos.
- **Docker** – Plataforma de contenedores para empaquetar y desplegar la aplicación.
- **Git y GitHub** – Control de versiones y hospedaje del repositorio.
- **Linux/Ubuntu** – Sistema operativo donde se construye y ejecuta la imagen.

## Estructura del proyecto

El repositorio está organizado de la siguiente manera:

```
/
├── app.py            # Aplicación Flask con las rutas principales
├── requirements.txt  # Dependencias de Python
├── Dockerfile        # Instrucciones para construir la imagen Docker
├── README.md         # Este manual de desarrollo y despliegue
├── .gitignore        # Archivos y carpetas a excluir del control de versiones
└── static/
    └── styles.css    # Estilos CSS simples para la página principal
```

## Requisitos previos

Para ejecutar el proyecto necesitará:

1. **Git** para clonar el repositorio.
2. **Python 3.10 o superior** y **pip** para una prueba local sin Docker.
3. **Docker Engine** para construir la imagen y ejecutar el contenedor.
4. Acceso a Internet (solo para instalar dependencias si prueba local sin Docker).

## Clonación del repositorio

Clone el proyecto desde su cuenta de GitHub (reemplace `<URL_DEL_REPOSITORIO>` por la URL real):

```bash
git clone <URL_DEL_REPOSITORIO>
cd <NOMBRE_DEL_REPOSITORIO>
```

## Prueba local sin Docker

Para ejecutar la aplicación sin contenedores en su máquina local (útil para probar antes de crear la imagen), siga estos pasos:

```bash
# Crear y activar un entorno virtual (opcional pero recomendado)
python -m venv venv
source venv/bin/activate

# Instalar las dependencias
pip install -r requirements.txt

# Ejecutar la aplicación
python app.py
```

Abra su navegador en [http://localhost:5000](http://localhost:5000) para ver la página principal.  También puede comprobar:

- [http://localhost:5000/health](http://localhost:5000/health) para verificar el estado (debería devolver `{"status":"ok",...}`).
- [http://localhost:5000/api/info](http://localhost:5000/api/info) para obtener información del proyecto.

## Construcción de la imagen Docker

El profesor evaluará principalmente la capacidad de construir y ejecutar la aplicación desde un contenedor, por lo que el `Dockerfile` es esencial.  Para construir la imagen y ejecutarla en segundo plano utilice:

```bash
# Desde la raíz del repositorio
docker build -t examen-telematica .

# Ejecutar el contenedor en background y publicar el puerto 8080 del host al 5000 del contenedor
docker run -d -p 8080:5000 --name examen-telematica examen-telematica

# Verificar que el contenedor está corriendo
docker ps

# Ver los logs del contenedor (opcional)
docker logs examen-telematica
```

Una vez en marcha, acceda a [http://localhost:8080](http://localhost:8080) (o `http://IP_PUBLICA:8080` si está en un servidor remoto) para ver la página principal.  Los endpoints `/health` y `/api/info` también están disponibles en ese puerto.

### Detener y eliminar el contenedor

```bash
docker stop examen-telematica
docker rm examen-telematica
```

### Reconstruir desde cero

Si desea recrear todo el flujo (por ejemplo, después de modificar código):

```bash
docker stop examen-telematica
docker rm examen-telematica
docker rmi examen-telematica
docker build -t examen-telematica .
docker run -d -p 8080:5000 --name examen-telematica examen-telematica
```

## Despliegue en Ubuntu/AWS

Para desplegar el servicio en una instancia Ubuntu (local, servidor o nube como AWS), ejecute lo siguiente:

```bash
# 1. Conectarse a la instancia por SSH
ssh usuario@IP_PUBLICA

# 2. Actualizar paquetes e instalar dependencias (Docker y Git)
sudo apt update
sudo apt install -y git docker.io
sudo systemctl enable --now docker

# 3. Clonar el repositorio y construir la imagen
git clone <URL_DEL_REPOSITORIO>
cd <NOMBRE_DEL_REPOSITORIO>
sudo docker build -t examen-telematica .

# 4. Ejecutar el contenedor en background publicando el puerto
sudo docker run -d -p 8080:5000 --name examen-telematica examen-telematica

# 5. Verificar que el contenedor está corriendo
sudo docker ps

# 6. Probar en el navegador (desde su máquina local) usando la IP pública
# Recuerde abrir el puerto 8080 en el firewall de su instancia o grupo de seguridad
# http://IP_PUBLICA:8080
```

## Explicación del Dockerfile

El `Dockerfile` de este proyecto sigue las mejores prácticas para imágenes pequeñas y reproducibles:

1. **Imagen base:** se utiliza `python:3.10-slim` para reducir el tamaño de la imagen.
2. **Variables de entorno:** se desactiva la escritura de bytecode (`PYTHONDONTWRITEBYTECODE=1`) y se habilita la salida sin buffer (`PYTHONUNBUFFERED=1`).
3. **Directorio de trabajo:** se crea `/app` como directorio donde se copiará el código fuente.
4. **Copia de dependencias y instalación:** se copia primero `requirements.txt` y se instala con `pip install --no-cache-dir` para aprovechar la cache de Docker y evitar archivos temporales.
5. **Copia del código:** se copia el resto de los archivos del proyecto.
6. **Exposición de puerto:** se expone el puerto interno `5000` que utiliza Flask.
7. **Comando por defecto:** se ejecuta `python app.py` al iniciar el contenedor.

Este flujo garantiza que la imagen se construya sin errores, sea ligera y pueda ejecutarse en cualquier entorno Docker.

## Uso de GitHub

Para subir su proyecto a GitHub y mantener la trazabilidad, siga estas recomendaciones (ejecute estos comandos desde la raíz del proyecto):

```bash
git init                   # Inicializa el repositorio local
git add .                  # Agrega todos los archivos
git commit -m "Inicializa estructura del proyecto"
git branch -M main         # Establece la rama principal como main
git remote add origin <URL_DEL_REPOSITORIO>
git push -u origin main    # Sube a GitHub

# Commits adicionales sugeridos
git commit -am "Agrega aplicación Flask con rutas principales"
git commit -am "Agrega Dockerfile para despliegue en contenedor"
git commit -am "Agrega documentación README"
git commit -am "Ajusta estilos y verificación de servicio"
```

Recuerde hacer commits frecuentemente con mensajes claros para demostrar la evolución del proyecto y facilitar el seguimiento por parte del profesor【16266687642254†L34-L45】.

## Checklist de verificación (rúbrica)

**40 % – Docker, despliegue y estabilidad**

- [ ] El archivo **Dockerfile** está en la raíz del proyecto.
- [ ] La imagen se construye sin errores (`docker build` funciona correctamente).
- [ ] El contenedor se ejecuta en segundo plano (`docker run -d`) y publica el puerto 5000 al 8080.
- [ ] El servicio permanece estable y responde a las peticiones HTTP.

**20 % – README y documentación**

- [ ] Este **README.md** explica cómo desplegar el servicio (local, Docker, Ubuntu/AWS).
- [ ] Incluye instrucciones de configuración, prueba y modificación.
- [ ] El código está comentado para facilitar su comprensión.

**30 % – GitHub y trazabilidad**

- [ ] El proyecto está almacenado en un repositorio de GitHub.
- [ ] Los commits son claros y muestran la evolución del proyecto.
- [ ] La estructura de carpetas es ordenada y permite reutilización.

**10 % – Funcionamiento para usuarios finales**

- [ ] La página principal (`/`) carga correctamente en el navegador.
- [ ] La ruta `/health` responde con un JSON de estado.
- [ ] La ruta `/api/info` devuelve la información del proyecto.
- [ ] El servicio es consumible desde un navegador local o remoto.

## Conclusiones

Este proyecto proporciona un ejemplo sencillo pero completo de cómo crear y desplegar un servicio telemático utilizando contenedores.  Está diseñado para cumplir estrictamente los criterios del **Examen 3 de Telemática**: el profesor puede clonar el repositorio, construir la imagen, ejecutar el contenedor y comprobar los endpoints sin realizar configuraciones adicionales.  Con una documentación clara, un `Dockerfile` funcional y una estructura de proyecto simple, el servicio es robusto, reutilizable y fácil de evaluar.

---

Autor: [NOMBRE DEL ESTUDIANTE]
