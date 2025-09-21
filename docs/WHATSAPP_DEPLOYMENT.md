# Guía de Despliegue WhatsApp - Laburen.com Agent

## Configuración WhatsApp Business API

### Opción 1: Meta for Developers (Oficial - Recomendado)

#### Paso 1: Crear App en Meta for Developers
1. Ve a https://developers.facebook.com/
2. Crear nueva app → Tipo: "Business"
3. Agregar producto "WhatsApp Business API"
4. Configurar número de teléfono de prueba

#### Paso 2: Configurar Webhook
```bash
# URL del webhook (cuando despliegues tu app)
https://tu-dominio.com/webhook/whatsapp

# Verify Token (define uno personalizado)
mi_token_secreto_123

# Eventos a suscribir:
- messages
- message_deliveries  
```

#### Paso 3: Variables de Entorno
```bash
# .env
WHATSAPP_TOKEN=EAAxxxxxxxxxxxxxxxxxxxxxxx
WHATSAPP_VERIFY_TOKEN=mi_token_secreto_123
```

### Opción 2: Twilio WhatsApp API (Más Simple)

#### Configuración Rápida
1. Cuenta Twilio → WhatsApp Business API
2. Sandbox number para pruebas
3. Webhook URL: `https://tu-app.com/webhook/whatsapp`

```python
# Agregar a main.py para Twilio
from twilio.twiml.messaging_response import MessagingResponse

@app.post("/webhook/whatsapp/twilio")
def whatsapp_webhook_twilio(Body: str = Form(...), From: str = Form(...)):
    response = ai_agent.process_message(Body, From)
    
    twiml = MessagingResponse()
    twiml.message(response)
    
    return str(twiml)
```

## Despliegue en la Nube

### Opción 1: Railway (Recomendado para pruebas)

```bash
# 1. Instalar Railway CLI
npm install -g @railway/cli

# 2. Login y deploy
railway login  
railway init
railway deploy
```

**railway.json:**
```json
{
  "build": {
    "builder": "nixpacks"
  },
  "deploy": {
    "startCommand": "uvicorn main:app --host 0.0.0.0 --port $PORT"
  }
}
```

### Opción 2: Render

1. Conectar repo GitHub
2. Build command: `pip install -r requirements.txt`
3. Start command: `uvicorn main:app --host 0.0.0.0 --port $PORT`

### Opción 3: Heroku

```bash
# Procfile
web: uvicorn main:app --host 0.0.0.0 --port $PORT

# runtime.txt  
python-3.13.0
```

## Configuración para Producción

### 1. Agregar Verificación de Webhook

```python
# Agregar a main.py
@app.get("/webhook/whatsapp")
def verify_webhook(mode: str = Query(alias="hub.mode"), 
                  token: str = Query(alias="hub.verify_token"),
                  challenge: str = Query(alias="hub.challenge")):
    """Verificación de webhook para Meta"""
    verify_token = os.getenv('WHATSAPP_VERIFY_TOKEN')
    
    if mode == "subscribe" and token == verify_token:
        return int(challenge)
    else:
        raise HTTPException(status_code=403, detail="Forbidden")
```

### 2. Mejorar Webhook para WhatsApp Real

```python
@app.post("/webhook/whatsapp")
def whatsapp_webhook(request: dict):
    """Webhook mejorado para WhatsApp Business API"""
    try:
        # Extraer mensaje desde estructura de Meta
        entry = request.get('entry', [{}])[0]
        changes = entry.get('changes', [{}])[0]
        value = changes.get('value', {})
        messages = value.get('messages', [])
        
        if messages:
            message = messages[0]
            from_number = message.get('from')
            text = message.get('text', {}).get('body', '')
            
            # Procesar con agente
            response = ai_agent.process_message(text, from_number)
            
            # Enviar respuesta (implementar send_whatsapp_message)
            send_whatsapp_message(from_number, response)
            
        return {"status": "success"}
        
    except Exception as e:
        print(f"Error webhook: {e}")
        return {"status": "error"}

def send_whatsapp_message(to_number: str, message: str):
    """Enviar mensaje via WhatsApp Business API"""
    import requests
    
    url = f"https://graph.facebook.com/v17.0/{PHONE_NUMBER_ID}/messages"
    headers = {
        "Authorization": f"Bearer {os.getenv('WHATSAPP_TOKEN')}",
        "Content-Type": "application/json"
    }
    
    data = {
        "messaging_product": "whatsapp",
        "to": to_number,
        "text": {"body": message}
    }
    
    response = requests.post(url, headers=headers, json=data)
    return response.json()
```

## Testing del Agente

### 1. Testing Local
```bash
# Terminal 1: Ejecutar servidor
uvicorn main:app --reload --port 8000

# Terminal 2: Testear endpoints
curl http://localhost:8000/test/hola
curl http://localhost:8000/test/productos
curl "http://localhost:8000/test/quiero%20comprar"
```

### 2. Testing con ngrok (Webhook local)
```bash
# Instalar ngrok
brew install ngrok

# Exponer puerto local
ngrok http 8000

# Usar URL de ngrok en Meta webhook config
https://abc123.ngrok.io/webhook/whatsapp
```

### 3. Testing en Producción
1. Deplorar aplicación
2. Configurar webhook en Meta/Twilio
3. Enviar mensaje de WhatsApp al número de prueba
4. Verificar logs del servidor

## Monitoreo y Debugging

### Logs Importantes
```python
# Agregar logging a main.py
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@app.post("/webhook/whatsapp")  
def whatsapp_webhook(Body: str = Form(...), From: str = Form(...)):
    logger.info(f"📱 Mensaje de {From}: {Body}")
    
    response = ai_agent.process_message(Body, From)
    
    logger.info(f"🤖 Respuesta: {response}")
    return {"message": response}
```

### Health Checks
```python
@app.get("/health")
def health_check():
    """Health check para monitoring"""
    return {
        "status": "ok",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0",
        "database": "connected",
        "ai_agent": "ready"
    }
```

## Checklist Pre-Deployment

- [ ] Variables de entorno configuradas (.env)
- [ ] Base de datos con productos cargados
- [ ] Webhook endpoint implementado y testeado
- [ ] SSL/HTTPS configurado (requerido por WhatsApp)
- [ ] Rate limiting implementado (opcional)
- [ ] Logging configurado
- [ ] Health checks funcionando
- [ ] Dominio/URL pública disponible

## Comandos de Prueba Final

Una vez desplegado, envía estos mensajes por WhatsApp:

```
1. "hola" → Mensaje de bienvenida
2. "productos" → Lista de productos  
3. "buscar camisa" → Búsqueda específica
4. "quiero comprar camisa azul" → Creación de carrito
```

---

**¡Listo para probar en vivo!** 🚀

El agente debe responder de forma natural y consumir la API correctamente.