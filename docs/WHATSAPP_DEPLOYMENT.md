# Guía de Despliegue WhatsApp - Laburen.com Agent

## Configuración WhatsApp con Twilio

### Paso 1: Configurar Twilio WhatsApp Sandbox

1. **Crear cuenta Twilio:** https://www.twilio.com/console
2. **WhatsApp Business API → Sandbox**
3. **Configurar webhook URL:**
   ```
   https://tu-dominio.com/twilio-webhook
   ```
4. **Método:** POST
5. **Obtener credenciales:**
   - Account SID
   - Auth Token
   - WhatsApp Phone Number

### Paso 2: Variables de Entorno

```bash
# .env
TWILIO_ACCOUNT_SID=ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
TWILIO_AUTH_TOKEN=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
TWILIO_WHATSAPP_NUMBER=+1415523xxxx
GEMINI_API_KEY=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
API_BASE_URL=https://tu-dominio.com
```

### Paso 3: Código de Integración

El proyecto ya incluye la integración completa:

```python
# Endpoint para recibir mensajes
@app.post("/twilio-webhook")
def twilio_webhook(Body: str = Form(...), From: str = Form(...)):
    message = Body
    from_number = From
    
    # Procesar con AI Agent
    response = ai_agent.process_message(message)
    
    # Enviar respuesta
    send_twilio_message(from_number, response)
    
    return {"status": "success"}

# Función para enviar mensajes
def send_twilio_message(to_number: str, message: str):
    from twilio.rest import Client
    
    client = Client(
        os.getenv('TWILIO_ACCOUNT_SID'),
        os.getenv('TWILIO_AUTH_TOKEN')
    )
    
    message = client.messages.create(
        body=message,
        from_=f"whatsapp:{os.getenv('TWILIO_WHATSAPP_NUMBER')}",
        to=f"whatsapp:{to_number}"
    )
    
    return message.sid
```

## Despliegue en Render (Ya Configurado)

El proyecto está desplegado en: **https://laburen-ai-agent.onrender.com**

### Auto-Deploy desde GitHub
1. ✅ Repositorio conectado: `JimeFioni/laburen-ai-agent`
2. ✅ Build automático en cada push
3. ✅ Variables de entorno configuradas
4. ✅ Base de datos SQLite con 100 productos

### Configuración Render
```yaml
# render.yaml (automático)
services:
  - type: web
    name: laburen-ai-agent
    env: python
    plan: free
    buildCommand: pip install -r requirements.txt
    startCommand: uvicorn main:app --host 0.0.0.0 --port $PORT
```

## Testing del Sistema

### 1. Endpoints Disponibles
```bash
# Health check
curl https://laburen-ai-agent.onrender.com/health

# Productos
curl https://laburen-ai-agent.onrender.com/products

# Debug database
curl https://laburen-ai-agent.onrender.com/debug/database

# Test AI agent
curl https://laburen-ai-agent.onrender.com/test/hola
```

### 2. WhatsApp Testing

**Número de prueba Twilio:** +1 415 523 8886

**Mensajes de prueba:**
```
1. "hola" → Saludo del agente
2. "productos" → Lista de productos
3. "buscar camisas" → Búsqueda específica  
4. "quiero comprar 2 camisas" → Crear carrito
5. "ver mi carrito" → Mostrar carrito actual
```

### 3. Logs en Tiempo Real

```python
# El sistema ya incluye logging:
print(f"📱 Mensaje Twilio de {from_number}: {message}")
print(f"🤖 Respuesta AI: {response}")
print(f"✅ Mensaje Twilio enviado: {message_sid}")
```

## Características del Sistema

### ✅ AI Agent Robusto
- **Gemini 1.5-flash** para procesamiento natural
- **Sistema de fallback** automático a base de datos
- **Timeout handling** para mejor experiencia

### ✅ API REST Completa  
- `GET /products` - Lista con filtro `?q=`
- `GET /products/:id` - Detalle específico
- `POST /carts` - Crear carrito
- `PATCH /carts/:id` - Actualizar carrito

### ✅ Base de Datos
- **100 productos** cargados automáticamente
- **SQLite** con fallback directo
- **Tablas:** products, cart_items

### ✅ Integración WhatsApp
- **Twilio Sandbox** para testing inmediato
- **Webhook bidireccional** funcional
- **Respuestas naturales** en español

## Flujo Completo

```
Usuario WhatsApp: "buscar camisas"
        ↓
Twilio recibe → POST /twilio-webhook  
        ↓
AI Agent (Gemini) procesa mensaje
        ↓
API: GET /products?q=camisa (o fallback BD)
        ↓
Respuesta formateada → send_twilio_message()
        ↓
WhatsApp recibe respuesta natural
```

## Monitoreo

### Health Check
```bash
curl https://laburen-ai-agent.onrender.com/health
# Response: {"status": "ok"}
```

### Database Status
```bash
curl https://laburen-ai-agent.onrender.com/debug/database
# Response: {"status": "ok", "product_count": 100, "tables": [...]}
```

---
