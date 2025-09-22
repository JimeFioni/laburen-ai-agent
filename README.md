# 🛍️ Laburen.com AI Sales Agent

> **Desafío Técnico**: Agente de IA que vende productos mediante API propia con WhatsApp

[![FastAPI](https://img.shields.io/badge/FastAPI-0.117.1-009688.svg)](https://fastapi.tiangolo.com)
[![Python](https://img.shields.io/badge/Python-3.13+-blue.svg)](https://python.org)
[![Gemini](https://img.shields.io/badge/Gemini-1.5--flash-4285F4.svg)](https://ai.google.dev)
[![SQLite](https://img.shields.io/badge/Database-SQLite-003B57.svg)](https://sqlite.org)

## 🎥 Demo Video

<div style="position: relative; padding-bottom: 65.01809408926417%; height: 0;"><iframe src="https://www.loom.com/embed/6e0fd0fcd5bc4322ace48c116c91e1db?sid=ce2ae782-8b0f-498b-9b8f-34ab08b8c58a" frameborder="0" webkitallowfullscreen mozallowfullscreen allowfullscreen style="position: absolute; top: 0; left: 0; width: 100%; height: 100%;"></iframe></div>

> 🚀 **Video demo**: Mira el AI Agent funcionando en tiempo real con WhatsApp + Gemini AI

## 🚀 Quick Start

```bash
# 1. Clonar repositorio
git clone https://github.com/JimeFioni/laburen-ai-agent.git
cd laburen-ai-agent

# 2. Instalar dependencias  
pip install -r requirements.txt

# 3. Configurar variables de entorno
cp .env.example .env
# Editar .env con tus API keys

# 4. Ejecutar servidor (desarrollo local)
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# 5. Probar agente
curl http://localhost:8000/test/hola
```

**📱 Interfaz web**: Ve a http://localhost:8000/docs *(desarrollo local)*
**🌐 Demo en vivo**: https://laburen-ai-agent.onrender.com *(producción)*

> **Nota:** En desarrollo local usa puerto 8000, en producción (Render) usa puerto dinámico $PORT

## ✨ Características

### 🤖 Agente de IA Inteligente
- **Google Gemini 1.5-flash** con procesamiento de lenguaje natural
- **Consumo real de API** (no simulado) con fallback directo a BD
- **Respuestas naturales** en español con emojis
- **Sistema robusto** con timeout handling y fallback automático

### 🛒 API REST Completa
- ✅ `GET /products` - Lista productos con filtro (`?q=término`)
- ✅ `GET /products/:id` - Detalle de producto específico
- ✅ `POST /carts` - Crear carrito con items
- ✅ `PATCH /carts/:id` - Actualizar carrito existente
- ✅ Validaciones de stock automáticas
- ✅ Sistema de fallback BD para alta disponibilidad

### 📊 Base de Datos
- **100 productos reales** cargados desde Excel automáticamente
- **SQLite** con inicialización automática en startup
- **Fallback directo** cuando API HTTP tiene problemas
- **Estructura optimizada** para búsquedas rápidas

### 📱 WhatsApp Integración
- ✅ **Meta WhatsApp Business API** configurado
- ✅ **Twilio WhatsApp Sandbox** para demos sin aprobación
- ✅ Webhook bidireccional funcionando en producción
- ✅ Testing interface en `/test/{mensaje}`

## 📁 Estructura del Proyecto

```
Laburen.com/
├── main.py                 # 🚀 Aplicación principal (FastAPI + Agente IA)
├── products.xlsx          # 📊 Datos de productos (100 items)
├── laburen_app.db         # 💾 Base de datos SQLite
├── requirements.txt       # 📦 Dependencias Python
├── .env.example          # ⚙️ Variables de entorno
├── docs/                 # 📚 Documentación completa
│   ├── README.md         # Arquitectura y diagramas
│   ├── ARCHITECTURE.md   # Detalles técnicos 
│   └── WHATSAPP_DEPLOYMENT.md  # Guía de despliegue
└── Desafio Tecnico AI Engineer - Laburen.com.txt  # 📋 Especificación
```

## 🎯 Funcionalidades del Agente

### Comandos Soportados

| Mensaje | Funcionalidad | API Endpoint |
|---------|---------------|--------------|
| `"hola"` | Saludo y bienvenida | - |
| `"productos"` | Lista catálogo completo | `GET /products` |
| `"buscar camisa"` | Búsqueda específica | `GET /products?q=camisa` |
| `"quiero comprar..."` | Crear carrito | `POST /carts` + `GET /products` |

### Ejemplo de Conversación

```
👤 Usuario: "hola"
🤖 Agente: "¡Hola! 👋 Soy tu asistente de Laburen.com
           🛍️ Puedo ayudarte a:
           • Ver productos
           • Buscar productos específicos  
           • Crear carritos de compra
           ¿Qué te interesa?"

👤 Usuario: "buscar camisa azul"
🤖 Agente: "🔍 RESULTADOS PARA 'CAMISA AZUL':
           🔸 Camisa L Azul
              💰 $25.99
              📦 Stock: 15
              ID: 15"

👤 Usuario: "quiero comprar esa camisa"
🤖 Agente: "🛒 CARRITO CREADO (ID: 1)
           🔸 Camisa L Azul
              Cantidad: 1
              💰 Total: $25.99"
```

## 🧪 Testing

### API Endpoints
```bash
# Productos
GET http://localhost:8000/products
GET http://localhost:8000/products/1
GET http://localhost:8000/products?q=camisa

# Carritos
POST http://localhost:8000/carts
Content-Type: application/json
{"items": [{"product_id": 1, "qty": 2}]}

# Agente IA
GET http://localhost:8000/test/hola
GET http://localhost:8000/test/productos
GET http://localhost:8000/test/buscar%20azul
```

### WhatsApp Testing
1. **Desarrollo**: Testing directo con endpoints `/test/{mensaje}`
2. **Producción**: Twilio WhatsApp Sandbox → https://laburen-ai-agent.onrender.com/twilio-webhook

**📱 Para probar WhatsApp en vivo:**
- Configurar webhook en Twilio Console: `https://laburen-ai-agent.onrender.com/twilio-webhook`
- Enviar mensaje al número sandbox de Twilio
- El agente responde automáticamente procesando con Gemini AI

## ⚙️ Configuración

### Variables de Entorno (.env)
```bash
# Requerido para el agente de IA
GEMINI_API_KEY=tu_gemini_api_key_aqui

# Para deployment en producción
API_BASE_URL=https://tu-app.onrender.com

# Para WhatsApp (opcional)
WHATSAPP_TOKEN=tu_whatsapp_token
WHATSAPP_VERIFY_TOKEN=tu_verify_token

# Para Twilio WhatsApp Sandbox (demo)
TWILIO_ACCOUNT_SID=tu_twilio_account_sid
TWILIO_AUTH_TOKEN=tu_twilio_auth_token
TWILIO_WHATSAPP_NUMBER=+14155238886
```

### Dependencias (requirements.txt)
```
fastapi==0.117.1
uvicorn==0.24.0
sqlalchemy==2.0.43
pandas==2.1.3
openpyxl==3.1.2
requests==2.32.5
google-generativeai==0.8.3
twilio==9.3.6
python-dotenv==1.1.1
pydantic==2.7.4
```

## 🏗️ Arquitectura

```
WhatsApp/Twilio → Webhook → Agente IA → API REST → SQLite Database
                               ↓              ↓
                          Google Gemini   Fallback BD
                          1.5-flash       Direct Access
```

**Consulta la documentación completa en `/docs`**

## 🚀 Despliegue Producción

### Render (Actual)
```bash
# Auto-deploy desde GitHub
# URL: https://laburen-ai-agent.onrender.com
```

### Variables de entorno en Render
```
GEMINI_API_KEY=tu_gemini_key
API_BASE_URL=https://laburen-ai-agent.onrender.com
TWILIO_ACCOUNT_SID=tu_twilio_sid
TWILIO_AUTH_TOKEN=tu_twilio_token
TWILIO_WHATSAPP_NUMBER=+14155238886
```

**Ver guía completa**: [docs/WHATSAPP_DEPLOYMENT.md](docs/WHATSAPP_DEPLOYMENT.md)

## 🎉 Demo en Vivo

**🔗 API Producción**: https://laburen-ai-agent.onrender.com/docs  
**🧪 Testing**: https://laburen-ai-agent.onrender.com/test/hola  
**📱 WhatsApp**: Twilio Sandbox +1 415 523 8886
**🔍 Debug**: https://laburen-ai-agent.onrender.com/debug/database

---

### 📞 Contacto
**Desarrollado para el desafío técnico de Laburen.com**  
**Desarrolladora**: [Jimena Fioni](https://www.linkedin.com/in/jimena-fioni/) 💼  
**Fecha**: Septiembre 2025  
**Stack**: Python + FastAPI + Gemini AI + WhatsApp API + Twilio  
**Repo**: https://github.com/JimeFioni/laburen-ai-agent

*¿Listo para probarlo en WhatsApp?* 🚀