# Desafío Técnico · Customer Success Engineer para **Laburen.com**


Diseña y demuestra, de punta a punta, cómo un agente de IA puede vender productos mediante una API propia y una base de datos en PostgreSQL. El reto se divide en una **fase conceptual** (soft) y una **fase práctica** (técnica). Todo el material debe ser 100 % ejecutable.

IMPORTANTE: No se busca un BOT (serie de menues en un chat), se espera un agente de IA capaz de ejecutar solicitudes HTTP

---

## 1. Fase Conceptual · Diseño del Agente de IA
1. **Mapa de flujo**
   - Ilustra (diagrama de flujo o secuencia) cómo el agente atiende a un cliente que:  
     1. explora productos,  
     2. crea un carrito  
     3. (extra) edita el carrito si el usuario lo pide.
2. **Arquitectura de alto nivel**  
   - Componentes principales: LLM, API REST, base de datos, servicios externos (Whatsapp).  

> **Formato de entrega:** PDF o Markdown de máx. 2 páginas con los endpoints + diagrama de flujo de interacción del agente.

---

## 2. Fase Práctica · API & Base de Datos
### 2.1 Fuente de datos
Se proveerá un archivo `products.xlsx` con N filas. Cada fila representa un producto.

### 2.2 Base de datos
Crea el esquema mínimo siguiente (puedes ampliarlo):


| Tabla        | Campos clave                                                   | Notas                                              |
|--------------|----------------------------------------------------------------|----------------------------------------------------|
| `products`   | `id` (PK), `name`, `description`, `price`, `stock`             | 				                     |
| `carts`      | `id` (PK), `created_at`, `updated_at`                          | Un carrito por conversación.                       |
| `cart_items` | `id` (PK), `cart_id` (FK), `product_id` (FK), `qty`            |                                                    |


### 2.3 Endpoints requeridos
| Método    | Ruta            | Descripción                                                                               | Códigos HTTP     |
|-----------|-----------------|-------------------------------------------------------------------------------------------|------------------|
| **GET**   | `/products`     | Lista con filtro opcional `?q=` por nombre/descr.                                         | 200, 500         |
| **GET**   | `/products/:id` | Detalle de un producto                                                                    | 200, 404         |
| **POST**  | `/carts`        | Crea un carrito y añade ítems. Body: `{ items:[{product_id, qty}] }`                      | 201, 404         |
| **PATCH** | `/carts/:id`    | **(Extra)** Actualiza cantidades o elimina ítems. Body: `{ items:[{product_id, qty}] }`   | 200, 404         |

**Requisitos técnicos**

- Node.js ≥ 18 o Python ≥ 3.10.  
- ORM permitido (Sequelize, Prisma, SQLAlchemy, etc.) o SQL puro.  
- Sin autenticación ni manejo de usuarios.  
- Variables sensibles en `.env`;.

---

## 3. Fase Práctica · Integración del Agente
1. **LLM / framework libre** (OpenAI Functions, LangChain, etc.) podes usar gemini de google que su api tiene una capa gratis.  
2. El agente debe:  
   - Mostrar productos (consume `GET /products`).  
   - Crear un carrito (consume `POST /carts`) al recibir intención de compra.  
   - **(Extra)** Editar un carrito (consume `PATCH /carts/:id`).  
3. Interface: desplegar en un numero de test de Whatsapp API.

---

## 4. Entregables
| Nº | Elemento                                                | Forma                                   |
|----|---------------------------------------------------------|-----------------------------------------|
| 1  | Repositorio GitHub                                      | Código                                  |
| 2  | Diagrama(s) & documento conceptual                      | Carpeta `/docs`                         |
| 3  | Numero del agente desplegado y consumiendo la API       | Whatsapp                                |

---

## 5. Criterios de Evaluación
| Peso | Competencia          | Detalle                                               |
|------|----------------------|-------------------------------------------------------|
| 20 % | Diseño conceptual    | Claridad, viabilidad, métricas                        |
| 25 % | Backend & API        | Calidad del modelo de datos, manejo de errores        |
| 45 % | Integración AI       | Correcto consumo de la API, relevancia de respuestas  |
| 10 % | Presentación & docu. | Orden, brevedad, facilidad para correr la prueba      |

---

### Entrega
A partir del siguiente dia a la entrega del challenge comienza la cuenta de 5 dias para la entrega del challenge.
Se espera poder hacer el test del agente directamente por Whatsapp en vivo y ver el consumo de la API.

¡Éxitos!