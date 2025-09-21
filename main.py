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
import google.generativeai as genai

# Agente de IA inteligente que consume la API
class AIAgent:
    def __init__(self):
        self.api_key = os.getenv('GEMINI_API_KEY', '')
        if self.api_key:
            genai.configure(api_key=self.api_key)
            self.model = genai.GenerativeModel('gemini-1.5-flash')
        else:
            self.model = None
        self.base_url = "http://localhost:8000"
        
    def process_message(self, message: str, phone: str) -> str:
        """Procesa mensajes usando Gemini y consume la API"""
        
        # Si no hay API key de Gemini, usar lógica simple
        if not self.model:
            return self._simple_logic(message)
        
        # Usar Gemini para procesar el mensaje
        try:
            # Crear el prompt con información sobre las funciones disponibles
            system_prompt = """Eres un asistente de ventas de Laburen.com. 

Tienes acceso a estas funciones de API:
- GET /products: Lista productos (opcional ?search=término)
- GET /products/{id}: Detalle de producto específico
- POST /carts: Crea carrito con productos
- PATCH /carts/{id}: Actualiza carrito existente

INSTRUCCIONES:
- Siempre sé amigable y usa emojis
- Ayuda al cliente a encontrar productos y crear carritos
- Si menciona comprar/carrito, pregunta qué productos y cantidades
- Presenta productos con nombre, precio y descripción
- Responde en español y sé conversacional

IMPORTANTE: Analiza el mensaje del usuario y determina si necesitas:
1. Mostrar productos (usa: ACCION:get_products)
2. Buscar productos (usa: ACCION:search_products:término_búsqueda)  
3. Ver detalle producto (usa: ACCION:get_product:ID)
4. Crear carrito (usa: ACCION:create_cart:productos_y_cantidades)
5. Solo conversar (responde directamente)

"""

            full_prompt = f"{system_prompt}\n\nUsuario: {message}"
            
            response = self.model.generate_content(full_prompt)
            response_text = response.text
            
            # Verificar si Gemini quiere ejecutar alguna acción
            if "ACCION:" in response_text:
                lines = response_text.split('\n')
                for line in lines:
                    if "ACCION:" in line:
                        action_line = line.strip()
                        
                        if "get_products" in action_line:
                            products_result = self.get_products_api()
                            # Segunda llamada con los resultados
                            follow_up_prompt = f"""Usuario preguntó: {message}

Productos disponibles:
{products_result}

Presenta esta información de forma amigable con emojis, incluyendo nombres, precios y una breve descripción."""
                            
                            final_response = self.model.generate_content(follow_up_prompt)
                            return final_response.text
                        
                        elif "search_products:" in action_line:
                            search_term = action_line.split("search_products:")[1].strip()
                            search_result = self.get_products_api(search_term)
                            
                            follow_up_prompt = f"""Usuario buscó: {message}

Resultados de búsqueda para "{search_term}":
{search_result}

Presenta los resultados de forma atractiva con emojis."""
                            
                            final_response = self.model.generate_content(follow_up_prompt)
                            return final_response.text
                        
                        elif "get_product:" in action_line:
                            try:
                                product_id = int(action_line.split("get_product:")[1].strip())
                                product_result = self.get_product_detail_api(product_id)
                                
                                follow_up_prompt = f"""Usuario preguntó por producto: {message}

Detalle del producto:
{product_result}

Presenta esta información de forma detallada y atractiva con emojis."""
                                
                                final_response = self.model.generate_content(follow_up_prompt)
                                return final_response.text
                            except:
                                pass
            
            # Si no hay acciones específicas, devolver la respuesta directa
            return response_text.replace("ACCION:", "").strip()
                
        except Exception as e:
            print(f"Error con Gemini: {e}")
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

# Para Render deployment - siempre usar la variable PORT
port = int(os.getenv("PORT", 10000))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=port)