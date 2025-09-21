from fastapi import FastAPI, Form, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import sqlite3
import pandas as pd
import json
import os
import requests
from datetime import datetime
from openai import OpenAI
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# Crear aplicación FastAPI
app = FastAPI(
    title="Laburen.com API",
    description="API para agente de IA que vende productos",
    version="1.0.0"
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Modelos Pydantic
class Product(BaseModel):
    id: int
    name: str
    description: str
    price: float
    stock: int

class CartItem(BaseModel):
    product_id: int
    qty: int

class CartCreate(BaseModel):
    items: List[CartItem]

class CartResponse(BaseModel):
    id: int
    items: List[dict]
    total_amount: float
    total_items: int
    created_at: str

# Funciones de base de datos
def init_db():
    """Inicializar base de datos SQLite"""
    conn = sqlite3.connect('laburen_app.db')
    cursor = conn.cursor()
    
    # Crear tabla productos
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            description TEXT,
            price REAL NOT NULL,
            stock INTEGER NOT NULL
        )
    ''')
    
    # Crear tabla carritos
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS carts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            items TEXT NOT NULL,
            total_amount REAL NOT NULL,
            total_items INTEGER NOT NULL,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    conn.commit()
    conn.close()

def load_products():
    """Cargar productos desde Excel"""
    if not os.path.exists('products.xlsx'):
        print("❌ No se encontró products.xlsx")
        return
    
    try:
        df = pd.read_excel('products.xlsx')
        print(f"✅ Excel leído: {len(df)} productos")
        
        conn = sqlite3.connect('laburen_app.db')
        cursor = conn.cursor()
        
        # Limpiar productos existentes
        cursor.execute('DELETE FROM products')
        
        # Insertar productos nuevos
        for _, row in df.iterrows():
            name = f"{row.get('TIPO_PRENDA', '')} {row.get('TALLA', '')} {row.get('COLOR', '')}".strip()
            description = f"{row.get('CATEGORÍA', '')} - {row.get('DESCRIPCIÓN', '')}".strip(' - ')
            price = float(row.get('PRECIO_50_U', 0.0))
            stock = int(row.get('CANTIDAD_DISPONIBLE', 0))
            
            cursor.execute('''
                INSERT INTO products (name, description, price, stock)
                VALUES (?, ?, ?, ?)
            ''', (name, description, price, stock))
        
        conn.commit()
        conn.close()
        print(f"✅ {len(df)} productos cargados")
        
    except Exception as e:
        print(f"❌ Error cargando productos: {e}")

# Inicializar al arrancar
init_db()
load_products()

# Endpoints de la API

@app.get("/")
def root():
    return {
        "message": "Laburen.com API",
        "version": "1.0.0",
        "docs": "/docs"
    }

@app.get("/products", response_model=List[Product])
def get_products(q: Optional[str] = None):
    """Lista productos con filtro opcional"""
    conn = sqlite3.connect('laburen_app.db')
    cursor = conn.cursor()
    
    if q:
        cursor.execute('''
            SELECT id, name, description, price, stock 
            FROM products 
            WHERE name LIKE ? OR description LIKE ?
        ''', (f'%{q}%', f'%{q}%'))
    else:
        cursor.execute('SELECT id, name, description, price, stock FROM products')
    
    products = []
    for row in cursor.fetchall():
        products.append(Product(
            id=row[0],
            name=row[1],
            description=row[2],
            price=row[3],
            stock=row[4]
        ))
    
    conn.close()
    return products

@app.get("/products/{product_id}", response_model=Product)
def get_product(product_id: int):
    """Obtiene un producto específico"""
    conn = sqlite3.connect('laburen_app.db')
    cursor = conn.cursor()
    
    cursor.execute('SELECT id, name, description, price, stock FROM products WHERE id = ?', (product_id,))
    row = cursor.fetchone()
    conn.close()
    
    if not row:
        raise HTTPException(status_code=404, detail="Product not found")
    
    return Product(
        id=row[0],
        name=row[1],
        description=row[2],
        price=row[3],
        stock=row[4]
    )

@app.post("/carts", response_model=CartResponse, status_code=201)
def create_cart(cart_data: CartCreate):
    """Crea un carrito nuevo"""
    conn = sqlite3.connect('laburen_app.db')
    cursor = conn.cursor()
    
    # Validar productos y calcular totales
    cart_items = []
    total_amount = 0.0
    total_items = 0
    
    for item in cart_data.items:
        # Verificar producto existe y tiene stock
        cursor.execute('SELECT id, name, price, stock FROM products WHERE id = ?', (item.product_id,))
        product = cursor.fetchone()
        
        if not product:
            conn.close()
            raise HTTPException(status_code=404, detail=f"Product {item.product_id} not found")
        
        if product[3] < item.qty:  # stock < qty
            conn.close()
            raise HTTPException(status_code=400, detail=f"Insufficient stock for {product[1]}")
        
        cart_items.append({
            "product_id": item.product_id,
            "name": product[1],
            "price": product[2],
            "qty": item.qty
        })
        
        total_amount += product[2] * item.qty
        total_items += item.qty
    
    # Guardar carrito
    cursor.execute('''
        INSERT INTO carts (items, total_amount, total_items, created_at)
        VALUES (?, ?, ?, ?)
    ''', (json.dumps(cart_items), total_amount, total_items, datetime.now().isoformat()))
    
    cart_id = cursor.lastrowid
    conn.commit()
    conn.close()
    
    return CartResponse(
        id=cart_id,
        items=cart_items,
        total_amount=total_amount,
        total_items=total_items,
        created_at=datetime.now().isoformat()
    )

@app.get("/carts/{cart_id}", response_model=CartResponse)
def get_cart(cart_id: int):
    """Obtiene un carrito específico"""
    conn = sqlite3.connect('laburen_app.db')
    cursor = conn.cursor()
    
    cursor.execute('SELECT id, items, total_amount, total_items, created_at FROM carts WHERE id = ?', (cart_id,))
    row = cursor.fetchone()
    conn.close()
    
    if not row:
        raise HTTPException(status_code=404, detail="Cart not found")
    
    return CartResponse(
        id=row[0],
        items=json.loads(row[1]),
        total_amount=row[2],
        total_items=row[3],
        created_at=row[4]
    )

@app.patch("/carts/{cart_id}", response_model=CartResponse)
def update_cart(cart_id: int, cart_data: CartCreate):
    """Actualiza un carrito existente"""
    conn = sqlite3.connect('laburen_app.db')
    cursor = conn.cursor()
    
    # Verificar que existe el carrito
    cursor.execute('SELECT id FROM carts WHERE id = ?', (cart_id,))
    if not cursor.fetchone():
        conn.close()
        raise HTTPException(status_code=404, detail="Cart not found")
    
    # Recalcular totales
    cart_items = []
    total_amount = 0.0
    total_items = 0
    
    for item in cart_data.items:
        if item.qty <= 0:
            continue  # Saltar items con qty 0 (eliminar)
            
        cursor.execute('SELECT id, name, price, stock FROM products WHERE id = ?', (item.product_id,))
        product = cursor.fetchone()
        
        if not product:
            conn.close()
            raise HTTPException(status_code=404, detail=f"Product {item.product_id} not found")
        
        if product[3] < item.qty:
            conn.close()
            raise HTTPException(status_code=400, detail=f"Insufficient stock for {product[1]}")
        
        cart_items.append({
            "product_id": item.product_id,
            "name": product[1],
            "price": product[2],
            "qty": item.qty
        })
        
        total_amount += product[2] * item.qty
        total_items += item.qty
    
    # Actualizar carrito
    cursor.execute('''
        UPDATE carts 
        SET items = ?, total_amount = ?, total_items = ?
        WHERE id = ?
    ''', (json.dumps(cart_items), total_amount, total_items, cart_id))
    
    conn.commit()
    conn.close()
    
    return CartResponse(
        id=cart_id,
        items=cart_items,
        total_amount=total_amount,
        total_items=total_items,
        created_at=datetime.now().isoformat()
    )

@app.get("/health")
def health():
    return {"status": "ok"}

import requests
from openai import OpenAI

# Agente de IA inteligente que consume la API
class AIAgent:
    def __init__(self):
        self.api_key = os.getenv('OPENAI_API_KEY', '')
        self.client = OpenAI(api_key=self.api_key) if self.api_key else None
        self.base_url = "http://localhost:8000"
        
    def process_message(self, message: str, phone: str) -> str:
        """Procesa mensajes usando OpenAI y consume la API"""
        
        # Si no hay API key de OpenAI, usar lógica simple
        if not self.client:
            return self._simple_logic(message)
        
        # Usar OpenAI con funciones para consumir la API
        try:
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {
                        "role": "system",
                        "content": """Eres un asistente de ventas de Laburen.com. 
                        
Tienes acceso a estas funciones:
- get_products: Lista productos con filtro opcional
- get_product_detail: Detalle de un producto específico  
- create_cart: Crea un carrito con productos
- update_cart: Actualiza un carrito existente

IMPORTANTE:
- Siempre sé amigable y usa emojis
- Ayuda al cliente a encontrar productos y crear carritos
- Si el cliente quiere comprar algo, usa create_cart
- Si el cliente quiere cambiar un carrito, usa update_cart
- Presenta los productos de forma atractiva con precios

Responde en español y sé conversacional."""
                    },
                    {"role": "user", "content": message}
                ],
                functions=[
                    {
                        "name": "get_products",
                        "description": "Obtiene lista de productos, con filtro opcional",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "search_query": {
                                    "type": "string",
                                    "description": "Término de búsqueda opcional para filtrar productos"
                                }
                            }
                        }
                    },
                    {
                        "name": "get_product_detail", 
                        "description": "Obtiene detalles de un producto específico",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "product_id": {
                                    "type": "integer",
                                    "description": "ID del producto"
                                }
                            },
                            "required": ["product_id"]
                        }
                    },
                    {
                        "name": "create_cart",
                        "description": "Crea un nuevo carrito con productos",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "items": {
                                    "type": "array",
                                    "items": {
                                        "type": "object",
                                        "properties": {
                                            "product_id": {"type": "integer"},
                                            "qty": {"type": "integer"}
                                        }
                                    },
                                    "description": "Lista de productos y cantidades"
                                }
                            },
                            "required": ["items"]
                        }
                    },
                    {
                        "name": "update_cart",
                        "description": "Actualiza un carrito existente",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "cart_id": {
                                    "type": "integer",
                                    "description": "ID del carrito a actualizar"
                                },
                                "items": {
                                    "type": "array",
                                    "items": {
                                        "type": "object",
                                        "properties": {
                                            "product_id": {"type": "integer"},
                                            "qty": {"type": "integer"}
                                        }
                                    },
                                    "description": "Lista actualizada de productos y cantidades"
                                }
                            },
                            "required": ["cart_id", "items"]
                        }
                    }
                ],
                function_call="auto"
            )
            
            message_response = response.choices[0].message
            
            # Si OpenAI quiere llamar una función
            if message_response.function_call:
                function_name = message_response.function_call.name
                function_args = json.loads(message_response.function_call.arguments)
                
                # Ejecutar la función correspondiente
                if function_name == "get_products":
                    result = self.get_products_api(function_args.get('search_query'))
                elif function_name == "get_product_detail":
                    result = self.get_product_detail_api(function_args['product_id'])
                elif function_name == "create_cart":
                    result = self.create_cart_api(function_args['items'])
                elif function_name == "update_cart":
                    result = self.update_cart_api(function_args['cart_id'], function_args['items'])
                else:
                    result = "Función no encontrada"
                
                # Segunda llamada con el resultado de la función
                second_response = self.client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {
                            "role": "system",
                            "content": """Eres un asistente de ventas de Laburen.com. 
                            Presenta la información de forma amigable con emojis."""
                        },
                        {"role": "user", "content": message},
                        message_response,
                        {
                            "role": "function",
                            "name": function_name,
                            "content": str(result)
                        }
                    ]
                )
                
                return second_response.choices[0].message.content
            
            else:
                return message_response.content
                
        except Exception as e:
            print(f"Error con OpenAI: {e}")
            return self._simple_logic(message)
    
    def _simple_logic(self, message):
        """Lógica simple cuando no hay OpenAI API key"""
        msg = message.lower().strip()
        
        if "hola" in msg or "buenos" in msg or "hi" in msg:
            return "¡Hola! 👋 Soy tu asistente de Laburen.com\n\n🛍️ Puedo ayudarte a:\n• Ver productos\n• Buscar productos específicos\n• Crear carritos de compra\n\n¿Qué te interesa?"
        
        elif "productos" in msg or "catalogo" in msg or "ver" in msg:
            return self.get_products_api()
        
        elif "buscar" in msg or "busca" in msg:
            search_term = msg.replace("buscar", "").replace("busca", "").strip()
            return self.get_products_api(search_term if search_term else None)
        
        else:
            return "🤔 Puedo ayudarte con:\n\n• 'productos' - Ver catálogo\n• 'buscar [término]' - Buscar específico\n• 'quiero comprar...' - Crear carrito\n\n¿Qué necesitas?"
    
    def get_products_api(self, search_query=None):
        """Consume GET /products de la API"""
        try:
            url = f"{self.base_url}/products"
            params = {"q": search_query} if search_query else {}
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            products = response.json()
            
            if not products:
                return "❌ No se encontraron productos"
            
            if search_query:
                result = f"🔍 *RESULTADOS PARA '{search_query.upper()}'*\n\n"
            else:
                result = "🛍️ *PRODUCTOS DISPONIBLES:*\n\n"
            
            for product in products[:10]:  # Máximo 10 productos
                result += f"🔸 *{product['name']}*\n"
                result += f"   💰 ${product['price']:.2f}\n"
                result += f"   📦 Stock: {product['stock']}\n"
                result += f"   ID: {product['id']}\n\n"
            
            if len(products) > 10:
                result += f"... y {len(products) - 10} productos más"
            
            return result
            
        except requests.exceptions.RequestException as e:
            return f"❌ Error conectando con la API: {e}"
        except Exception as e:
            return f"❌ Error: {e}"
    
    def get_product_detail_api(self, product_id):
        """Consume GET /products/:id de la API"""
        try:
            response = requests.get(f"{self.base_url}/products/{product_id}", timeout=10)
            response.raise_for_status()
            
            product = response.json()
            
            result = f"🔍 *DETALLE DEL PRODUCTO*\n\n"
            result += f"🔸 *{product['name']}*\n"
            result += f"📝 {product['description']}\n"
            result += f"💰 ${product['price']:.2f}\n"
            result += f"📦 Stock: {product['stock']}\n"
            result += f"🆔 ID: {product['id']}"
            
            return result
            
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 404:
                return "❌ Producto no encontrado"
            return f"❌ Error HTTP: {e}"
        except Exception as e:
            return f"❌ Error: {e}"
    
    def create_cart_api(self, items):
        """Consume POST /carts de la API"""
        try:
            data = {"items": items}
            response = requests.post(f"{self.base_url}/carts", json=data, timeout=10)
            response.raise_for_status()
            
            cart = response.json()
            
            result = f"� *CARRITO CREADO* (ID: {cart['id']})\n\n"
            
            for item in cart['items']:
                result += f"🔸 {item['name']}\n"
                result += f"   Cantidad: {item['qty']}\n"
                result += f"   Precio: ${item['price']:.2f}\n"
                result += f"   Subtotal: ${item['price'] * item['qty']:.2f}\n\n"
            
            result += f"📊 *RESUMEN:*\n"
            result += f"Total items: {cart['total_items']}\n"
            result += f"💰 *Total: ${cart['total_amount']:.2f}*"
            
            return result
            
        except requests.exceptions.HTTPError as e:
            return f"❌ Error al crear carrito: {e.response.text}"
        except Exception as e:
            return f"❌ Error: {e}"
    
    def update_cart_api(self, cart_id, items):
        """Consume PATCH /carts/:id de la API"""
        try:
            data = {"items": items}
            response = requests.patch(f"{self.base_url}/carts/{cart_id}", json=data, timeout=10)
            response.raise_for_status()
            
            cart = response.json()
            
            result = f"🔄 *CARRITO ACTUALIZADO* (ID: {cart['id']})\n\n"
            
            if not cart['items']:
                result += "🗑️ Carrito vacío\n"
            else:
                for item in cart['items']:
                    result += f"🔸 {item['name']}\n"
                    result += f"   Cantidad: {item['qty']}\n"
                    result += f"   Precio: ${item['price']:.2f}\n"
                    result += f"   Subtotal: ${item['price'] * item['qty']:.2f}\n\n"
            
            result += f"📊 *RESUMEN:*\n"
            result += f"Total items: {cart['total_items']}\n"
            result += f"💰 *Total: ${cart['total_amount']:.2f}*"
            
            return result
            
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 404:
                return "❌ Carrito no encontrado"
            return f"❌ Error al actualizar carrito: {e.response.text}"
        except Exception as e:
            return f"❌ Error: {e}"

# Instanciar agente
ai_agent = AIAgent()

@app.post("/webhook/whatsapp")
def whatsapp_webhook(Body: str = Form(...), From: str = Form(...)):
    """Webhook para WhatsApp"""
    try:
        response = ai_agent.process_message(Body, From)
        print(f"📱 {From}: {Body}")
        print(f"🤖 Respuesta: {response}")
        return {"message": response}
    except Exception as e:
        print(f"❌ Error: {e}")
        return {"message": "Lo siento, hubo un error. Intenta de nuevo."}

@app.get("/webhook/whatsapp")
def verify_whatsapp_webhook(
    mode: str = Query(alias="hub.mode"), 
    token: str = Query(alias="hub.verify_token"),
    challenge: str = Query(alias="hub.challenge")
):
    """Verificación de webhook para WhatsApp Business API"""
    verify_token = os.getenv('WHATSAPP_VERIFY_TOKEN', 'laburen_verify_2024')
    
    if mode == "subscribe" and token == verify_token:
        print(f"✅ Webhook verificado con token: {token}")
        return int(challenge)
    else:
        print(f"❌ Verificación fallida. Mode: {mode}, Token: {token}")
        raise HTTPException(status_code=403, detail="Forbidden")

@app.get("/test/{message}")
def test_bot(message: str):
    """Probar el bot sin WhatsApp"""
    response = ai_agent.process_message(message, "test_user")
    return {"query": message, "response": response}

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)