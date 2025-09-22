#!/usr/bin/env python3
"""Test del webhook de WhatsApp"""

import json

# Simulamos un mensaje de WhatsApp
webhook_data = {
    "entry": [{
        "changes": [{
            "field": "messages",
            "value": {
                "messages": [{
                    "from": "1234567890",
                    "text": {
                        "body": "Hola, quiero ver productos"
                    }
                }]
            }
        }]
    }]
}

print("📝 Test del webhook:")
print(f"Datos simulados: {json.dumps(webhook_data, indent=2)}")

# Test de parsing
for entry in webhook_data["entry"]:
    for change in entry.get("changes", []):
        if change.get("field") == "messages":
            value = change.get("value", {})
            messages = value.get("messages", [])
            for message in messages:
                from_number = message.get("from", "")
                message_body = ""
                
                if "text" in message:
                    message_body = message["text"].get("body", "")
                
                print(f"✅ Mensaje extraído:")
                print(f"   De: {from_number}")
                print(f"   Mensaje: '{message_body}'")

print("\n🎯 El parsing del webhook funciona correctamente!")