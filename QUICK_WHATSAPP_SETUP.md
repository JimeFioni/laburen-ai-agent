# 🚀 Setup Rápido para Testing WhatsApp

## Opción 1: Testing Local con ngrok (5 minutos)

### 1. Instalar ngrok
```bash
# Mac
brew install ngrok

# O descargar desde: https://ngrok.com/download
```

### 2. Exponer servidor local
```bash
# Terminal 1: Ejecutar tu aplicación
cd "/Users/Jime/Desktop/Laburen.com"
source venv/bin/activate
uvicorn main:app --reload --port 8000

# Terminal 2: Exponer con ngrok
ngrok http 8000
```

### 3. Configurar WhatsApp Sandbox (Meta)
1. Ve a https://developers.facebook.com/
2. Crea app → Business → WhatsApp Business API  
3. Usa la URL de ngrok: `https://abc123.ngrok.io/webhook/whatsapp`
4. Verify token: `laburen_verify_2024`

### 4. Variables de entorno
```bash
# Crear .env
WHATSAPP_VERIFY_TOKEN=laburen_verify_2024
```

## Opción 2: Deploy Gratuito en Railway (10 minutos)

### 1. Preparar para deploy
```bash
# Crear Procfile
echo "web: uvicorn main:app --host 0.0.0.0 --port \$PORT" > Procfile
```

### 2. Deploy en Railway
```bash
# Instalar CLI
npm install -g @railway/cli

# Login y deploy  
railway login
railway init
railway deploy
```

### 3. Configurar webhook
- URL: `https://tu-app.railway.app/webhook/whatsapp`
- Configurar en Meta for Developers

## 🧪 Testing Commands

Una vez configurado, envía estos mensajes por WhatsApp:

```
✅ "hola" → Saludo del agente
✅ "productos" → Lista de productos  
✅ "buscar camisa" → Búsqueda específica
✅ "quiero una camisa azul" → Creación de carrito
```

---

**¡En 5-10 minutos tendrás el agente funcionando en WhatsApp!** 📱