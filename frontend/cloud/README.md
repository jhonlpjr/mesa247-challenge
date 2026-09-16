# Frontend en Cloud Run

Esta carpeta contiene una imagen multi-stage: Vite compila la aplicación y Nginx
sirve los archivos estáticos en el puerto `8080` requerido por Cloud Run. Nginx
también conserva el fallback de React Router al refrescar una ruta profunda.

## Construcción y despliegue

Ejecutar los comandos desde `frontend/`:

```bash
gcloud builds submit \
  --tag REGION-docker.pkg.dev/PROJECT_ID/REPOSITORY/mesa247-frontend:latest \
  -f cloud/Dockerfile \
  --build-arg VITE_API_BASE_URL=https://BACKEND_URL .

gcloud run deploy mesa247-frontend \
  --image REGION-docker.pkg.dev/PROJECT_ID/REPOSITORY/mesa247-frontend:latest \
  --region REGION \
  --port 8080 \
  --allow-unauthenticated
```

`VITE_API_BASE_URL` queda incorporada en el bundle durante la construcción; si
cambia la URL del backend, se debe construir una nueva imagen. Después de conocer
la URL final del frontend, agréguela a `CORS_ORIGINS` del servicio backend.

El endpoint `/healthz` devuelve `200 OK` y puede usarse para comprobaciones
operativas.
