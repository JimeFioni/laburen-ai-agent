#!/usr/bin/env python3
"""Test simplificado del webhook para WhatsApp"""

from fastapi import FastAPI
import uvicorn
import json

app = FastAPI()

# Mock del AI Agent para testing
class MockAIAgent:
    def process_message(self, message: str, phone: str) -> str:
        if "hola" in message.lower():
            return "¡Hola! 👋 Soy tu asistente de Laburen.com. ¿En qué puedo ayudarte?"
        elif "productos" in message.lower():
            return "📱 Tenemos increíbles productos disponibles:\n\n🖥️ Laptops desde $599\n📱 Smartphones desde $299\n⌚ Smartwatches desde $199\n\n¿Qué te interesa?"
        else:
            return f"Recibí tu mensaje: '{message}'. ¡Gracias por contactarnos! 🤖"

# Mock agent
ai_agent = MockAIAgent()

@app.get("/webhook")
def verify_webhook(
    mode: str = None,
    challenge: str = None, 
    token: str = None
):
    """Verificación del webhook"""
    if mode == "subscribe" and token == "laburen_verify_2024":
        print(f"✅ Webhook verificado")
        return int(challenge) if challenge else "OK"
    return {"error": "Forbidden"}

@app.post("/webhook")
async def whatsapp_webhook(request: dict):
    """Webhook para WhatsApp Business API"""
    try:
        print(f"📨 Webhook recibido: {json.dumps(request, indent=2)}")
        
        if "entry" in request:
            for entry in request["entry"]:
                for change in entry.get("changes", []):
                    if change.get("field") == "messages":
                        value = change.get("value", {})
                        messages = value.get("messages", [])
                        
                        for message in messages:
                            from_number = message.get("from", "")
                            message_body = ""
                            
                            if "text" in message:
                                message_body = message["text"].get("body", "")
                            
                            print(f"📱 Mensaje de {from_number}: {message_body}")
                            
                            if message_body:
                                ai_response = ai_agent.process_message(message_body, from_number)
                                print(f"🤖 Respuesta AI: {ai_response}")
                                print(f"📤 [SIMULADO] Enviaría respuesta a {from_number}")
        
        return {"status": "success"}
    
    except Exception as e:
        print(f"❌ Error: {e}")
        return {"status": "error", "message": str(e)}

@app.get("/test/{message}")
def test_agent(message: str):
    """Test directo del agente"""
    response = ai_agent.process_message(message, "test_user")
    return {"query": message, "response": response}

if __name__ == "__main__":
    print("🚀 Iniciando servidor de prueba...")
    uvicorn.run(app, host="127.0.0.1", port=8000)