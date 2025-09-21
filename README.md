# 🛍️ Laburen.com AI Sales Agent

> **Desafío Técnico Completado**: Agente de IA que vende productos mediante API propia con WhatsApp

[![FastAPI](https://img.shields.io/badge/FastAPI-0.117.1-009688.svg)](https://fastapi.tiangolo.com)
[![Python](https://img.shields.io/badge/Python-3.13+-blue.svg)](https://python.org)
[![OpenAI](https://img.shields.io/badge/OpenAI-GPT--3.5--turbo-green.svg)](https://openai.com)
[![SQLite](https://img.shields.io/badge/Database-SQLite-003B57.svg)](https://sqlite.org)

## 🚀 Quick Start

```bash
# 1. Instalar dependencias  
pip install -r requirements.txt

# 2. Ejecutar servidor
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# 3. Probar agente
curl http://localhost:8000/test/hola
```

**📱 Ya está funcionando**: Ve a http://localhost:8000/docs

## ✨ Características

### 🤖 Agente de IA Inteligente
- **OpenAI GPT-3.5-turbo** con Function Calling
- **Consumo real de API** (no simulado)
- **Respuestas naturales** en español con emojis
- **Fallback logic** sin API key de OpenAI

### 🛒 API REST Completa
- ✅ `GET /products` - Lista productos con filtro
- ✅ `GET /products/:id` - Detalle de producto  
- ✅ `POST /carts` - Crear carrito
- ✅ `PATCH /carts/:id` - Actualizar carrito
- ✅ Validaciones de stock automáticas

### 📊 Base de Datos
- **100 productos** cargados desde Excel automáticamente
- **SQLite** (desarrollo) / **PostgreSQL** ready (producción)
- **SQLAlchemy ORM** con validaciones

### 📱 WhatsApp Ready
- Webhook configurado para WhatsApp Business API
- Testing interface en `/test/{mensaje}`

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
1. **Local**: Usar ngrok + webhook local
2. **Producción**: Deploy en Railway/Render + Meta webhook

## ⚙️ Configuración

### Variables de Entorno (.env)
```bash
# Opcional - mejora las respuestas del agente
OPENAI_API_KEY=tu_api_key_aqui

# Para WhatsApp (producción)
WHATSAPP_TOKEN=tu_whatsapp_token
WHATSAPP_VERIFY_TOKEN=tu_verify_token
```

### Dependencias (requirements.txt)
```
fastapi==0.104.1
uvicorn==0.24.0
sqlalchemy==2.0.23
pandas==2.1.3
openpyxl==3.1.2
requests==2.32.5
openai==1.108.1
python-dotenv==1.1.1
```

## 🏗️ Arquitectura

```
WhatsApp → Webhook → Agente IA → API REST → Database
                       ↓
                   OpenAI GPT-3.5
                   Function Calling
```

**Consulta la documentación completa en `/docs`**

## 🚀 Despliegue Producción

### Railway (Recomendado)
```bash
railway login
railway init  
railway deploy
```

### Render/Heroku
- Build: `pip install -r requirements.txt`
- Start: `uvicorn main:app --host 0.0.0.0 --port $PORT`

**Ver guía completa**: [docs/WHATSAPP_DEPLOYMENT.md](docs/WHATSAPP_DEPLOYMENT.md)

## 📊 Criterios del Desafío - Status

| Criterio | Peso | Status | Implementación |
|----------|------|--------|----------------|
| **Diseño conceptual** | 20% | ✅ | Diagramas + docs completas |
| **Backend & API** | 25% | ✅ | Todos endpoints + extras |
| **Integración AI** | 45% | ✅ | OpenAI + Function Calling |
| **Presentación** | 10% | ✅ | Documentación + código limpio |

## 🎉 Demo en Vivo

**🔗 API**: http://localhost:8000/docs  
**🧪 Testing**: http://localhost:8000/test/hola  
**📱 WhatsApp**: Ready para webhook

---

### 📞 Contacto
**Desarrollado para el desafío técnico de Laburen.com**  
**Fecha**: Enero 2025  
**Stack**: Python + FastAPI + OpenAI + WhatsApp API  

*¿Listo para probarlo en WhatsApp?* 🚀