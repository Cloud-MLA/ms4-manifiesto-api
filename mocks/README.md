# mocks/

Mini-servidores FastAPI que simulan MS1, MS2 y MS3 mientras Guillermo/Mariano/Edinson terminan sus servicios. Solo para **desarrollo local** — no van a producción.

Cada mock responde con JSON precargado en `data/` (subset del seed, coherente entre los 3).

## Uso

```bash
# Levantar los 3 mocks + MS4 juntos:
docker compose -f mocks/docker-compose.mocks.yml up --build

# Probar el manifiesto:
curl http://localhost:8004/api/manifiesto/6058
```

## Cuando lleguen los servicios reales

Solo cambias las URLs en el `.env` de MS4 (o en la env del contenedor):

```
MS1_BASE_URL=http://10.0.1.15:8001    # IP de la VM-PROD donde corre MS1
MS2_BASE_URL=http://10.0.1.15:8002
MS3_BASE_URL=http://10.0.1.15:8003
```

y reinicias MS4. El código no cambia.
