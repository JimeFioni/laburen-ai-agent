# Arquitectura - Laburen.com WhatsApp AI Agent

## Diagrama de Arquitectura

```
┌─────────────────┐    HTTP POST     ┌─────────────────────────┐
│                 │   /twilio-webhook │                         │
│   WhatsApp      │ ───────────────→  │      FastAPI App        │
│   (Usuario)     │                   │    (Render Cloud)       │
│                 │ ←─────────────────│                         │
└─────────────────┘    Respuesta      └───────────┬─────────────┘
                                                   │
        ┌─────────────────┐                      │
        │                 │                      │
        │   Twilio API    │ ←────────────────────┘
        │   WhatsApp      │    send_message()
        │   Sandbox       │
        └─────────────────┘

                    ┌─────────────────────────┐
                    │      AI Agent           │
                    │   (Gemini 1.5-flash)   │
                    └───────────┬─────────────┘
                                │
                    ┌───────────▼─────────────┐
                    │     API Endpoints       │
                    │  GET  /products         │
                    │  GET  /products/:id     │
                    │  POST /carts            │
                    │  PATCH /carts/:id       │
                    └───────────┬─────────────┘
                                │
                    ┌───────────▼─────────────┐
                    │   SQLite Database       │
                    │                         │
                    │  ┌─────────────────┐   │
                    │  │   products      │   │
                    │  │  (100 items)    │   │
                    │  └─────────────────┘   │
                    │                         │
                    │  ┌─────────────────┐   │
                    │  │   cart_items    │   │
                    │  └─────────────────┘   │
                    └─────────────────────────┘
```

## Flujo de Operación

### 1. Mensaje de WhatsApp
```
Usuario: "buscar camisas"
   ↓
Twilio recibe → POST /twilio-webhook
   ↓
AI Agent procesa con Gemini
   ↓
GET /products?q=camisa (con fallback a BD)
   ↓
Respuesta formateada → Twilio → WhatsApp
```

### 2. Sistema de Fallback
```
API Request → Timeout (>30s)
   ↓
Fallback automático → Acceso directo SQLite
   ↓
SELECT * FROM products WHERE name LIKE '%busqueda%'
   ↓
Respuesta sin interrupción
```

## Stack Tecnológico

**Backend:**
- FastAPI (Python 3.13)
- SQLite + SQLAlchemy
- Google Gemini 1.5-flash
- Pandas (carga Excel)

**Integración:**
- Twilio WhatsApp API
- Render Cloud (deployment)
- GitHub (CI/CD)

**Endpoints API:**
```
GET    /products         # Lista con filtro ?q=
GET    /products/:id     # Detalle específico  
POST   /carts           # Crear carrito
PATCH  /carts/:id       # Actualizar carrito
POST   /twilio-webhook  # Recibe mensajes WhatsApp
```

**Base de Datos:**
```sql
products: id, name, description, price, stock
cart_items: id, product_id, qty, added_at
```

