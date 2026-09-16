# Backend en Cloud Run

Esta carpeta contiene el contenedor de FastAPI. El proceso escucha en `0.0.0.0` y
usa automáticamente el puerto `PORT` asignado por Cloud Run (8080 como fallback).

## Construcción y despliegue

Ejecutar los comandos desde `backend/`:

```bash
gcloud builds submit \
  --tag REGION-docker.pkg.dev/PROJECT_ID/REPOSITORY/mesa247-backend:latest \
  -f cloud/Dockerfile .

gcloud run deploy mesa247-backend \
  --image REGION-docker.pkg.dev/PROJECT_ID/REPOSITORY/mesa247-backend:latest \
  --region REGION \
  --port 8080 \
  --allow-unauthenticated \
  --set-env-vars CORS_ORIGINS=https://FRONTEND_URL
```

`CORS_ORIGINS` acepta una lista separada por comas. `DATABASE_URL` se configura
como variable de entorno en Cloud Run y no se incluye en la imagen.

Antes de activar el servicio se deben ejecutar `alembic upgrade head` y el seed
correspondiente contra la base de datos del entorno. No se ejecutan al iniciar el
contenedor para evitar que cada instancia intente modificar el esquema.

## Persistencia

SQLite funciona para una demostración local, pero el disco de una instancia de
Cloud Run es efímero y no debe usarse como almacenamiento de producción. Para
producción se debe elegir una base administrada (por ejemplo Cloud SQL), su driver
compatible y configurar `DATABASE_URL` y la conectividad antes del despliegue.

El backend ya está preparado para recibir esa configuración sin cambios en el
contenedor.
