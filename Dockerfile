# Entorno del curso · Teoría de la Computación · 2027-1
# IPN · Escuela Superior de Cómputo
#
# Construir y prender:   docker compose up -d --build
# Entrar a trabajar:     docker compose exec teoria bash
# Comprobar el entorno:  bash extras/comprobar.sh        (ya dentro)
#
# Cada línea está explicada en docker_tutorial.md, partes 6 y 7.

FROM python:3.12-slim-trixie

# Para versionar y editar sin salir del contenedor
RUN apt-get update && apt-get install -y --no-install-recommends \
        git nano \
    && rm -rf /var/lib/apt/lists/*

# Dos avisos de pip que dentro de un contenedor no aplican y que se leen como
# errores sin serlo: que se instala como root, y que hay una versión nueva de pip.
ENV PIP_ROOT_USER_ACTION=ignore \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Flet para la interfaz gráfica y pytest para las pruebas, con la versión fijada.
# No se instala ninguna biblioteca de autómatas: los algoritmos del curso se
# programan en Python puro.
RUN pip install --no-cache-dir \
        "flet[web]==0.86.5" \
        pytest==8.3.4

# Acentos, hora de la Ciudad de México, y Flet como página web en el puerto
# 8550, porque dentro del contenedor no hay pantalla donde abrir una ventana
ENV LANG=C.UTF-8 \
    TZ=America/Mexico_City \
    FLET_FORCE_WEB_SERVER=true \
    FLET_SERVER_PORT=8550

WORKDIR /trabajo
CMD ["bash"]
