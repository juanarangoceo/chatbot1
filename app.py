import os
import openai
from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
from dotenv import load_dotenv

try:
    from prompt_ventas import PROMPT_VENTAS_CAFETERA  # Importamos el prompt
except ImportError:
    print("⚠️ ERROR: No se pudo importar el prompt de ventas. Verifica que prompt_ventas.py existe.")
    PROMPT_VENTAS_CAFETERA = "Eres un asistente de ventas experto en cafeteras espresso."

# Cargar variables de entorno desde .env
load_dotenv()

# Configurar API Key de OpenAI
openai.api_key = os.getenv("OPENAI_API_KEY")

# Verificar si la API Key se cargó correctamente
if not openai.api_key:
    print("❌ ERROR: No se encontró la API Key en el archivo .env")
    exit(1)

print(f"✅ API Key detectada correctamente: {openai.api_key[:5]}...")

# Inicializar Flask
app = Flask(__name__)

@app.route("/", methods=["GET"])
def home():
    return "🤖 Chatbot de Ventas con IA está activo."

@app.route("/whatsapp", methods=["POST"])
def whatsapp():
    """Recibe mensajes de WhatsApp y responde con OpenAI."""
    incoming_msg = request.values.get("Body", "").strip()
    sender = request.values.get("From", "")

    print(f"📩 Mensaje recibido de {sender}: {incoming_msg}")

    response_text = generar_respuesta_ia(incoming_msg)

    resp = MessagingResponse()
    resp.message(response_text)

    return str(resp)

def generar_respuesta_ia(mensaje):
    """Genera una respuesta usando OpenAI GPT con el prompt de ventas especializado."""
    try:
        print(f"🔄 Enviando mensaje a OpenAI: {mensaje}")

        # Llamada a OpenAI con el prompt de ventas especializado
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": PROMPT_VENTAS_CAFETERA},  # Usamos el prompt importado
                {"role": "user", "content": mensaje}
            ]
        )
        respuesta = response['choices'][0]['message']['content'].strip()
        print(f"✅ Respuesta de OpenAI: {respuesta}")
        return respuesta

    except openai.OpenAIError as e:
        print(f"⚠️ ERROR con OpenAI: {e}")
        return "Lo siento, hubo un problema con el servicio de OpenAI."

    except Exception as e:
        print(f"⚠️ ERROR inesperado: {e}")
        return "Lo siento, hubo un error inesperado."

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
