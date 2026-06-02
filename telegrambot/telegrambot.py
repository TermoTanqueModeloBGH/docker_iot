import os
import logging
import ssl
import certifi
import aiomqtt
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

#Para ver los logs del bot
logging.basicConfig(format='%(asctime)s - TelegramBot - %(levelname)s - %(message)s', level=logging.INFO)
logging.getLogger("httpx").setLevel(logging.WARNING)

#Token del bot, se obtiene de la variable de entorno
token=os.environ["TB_TOKEN"]

#Configuración del broker MQTT
MQTT_BROKER = os.environ.get("MQTT_SERVER", "mosquitto") 
MQTT_PORT = 8883  # Puerto MQTTS seguro con TLS/SSL 
MQTT_USER = os.environ.get("MQTT_USER", None)
MQTT_PASS = os.environ.get("MQTT_USER_PASS", None)

#Direccion MAC del pico W
DEVICE_MAC = os.environ.get("DEVICE_MAC", "AA:BB:CC:DD:EE:FF") 

async def enviar_mqtt(topico_extension: str, payload: str):

    topico_completo = f"{DEVICE_MAC}/{topico_extension}"

    tls_context = ssl.create_default_context(cafile=certifi.where())
  
    async with aiomqtt.Client(
        hostname=MQTT_BROKER,
        port=MQTT_PORT,
        username=MQTT_USER,
        password=MQTT_PASS,
        tls_context=tls_context
    )as client:
        await client.publish(topico_completo, payload=payload, qos=1)
        logging.info(f"MQTT: Publicado -> Topico: {topico_completo}, Mensaje: {payload}")

# COMANDOS DE TELEGRAM

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    "comando /start: bienvenida al usuario junto a los comandos disponibles"
    mensaje=(
        "Bienvenido al panel de control del termotasto\n"
        "Comandos disponibles:\n"
        "/setpoint <numero> - Establece la temperatura objetivo\n"
        "/periodo <segundos> - Establece el periodo de lectura del sensor\n"
        "/modo <auto/manual> - Cambia el modo del termotasto\n"
        "/rele <on/off> - En modo manual, enciende o apaga el rele\n"
        "/destello -> Hace parpedear el led fisico del pico W"
    )
    await update.message.reply_text(mensaje)

async def setpoint(update: Update, context: ContextTypes.DEFAULT_TYPE):
    "comando /setpoint <numero>: establece la temperatura objetivo"
    if not context.args:
        await update.message.reply_text("Uso: /setpoint <numero>. Ejemplo: /setpoint 20")
        return 
    valor=context.args[0]
    try:
        float(valor)  # Verificar que el valor es un número valido
        await enviar_mqtt("setpoint", valor)
        await update.message.reply_text(f"Temperatura objetivo establecida a {valor}°C")
    except ValueError:
        await update.message.reply_text("Por favor, ingresa un número válido para el setpoint.")
    except Exception as e:
        await update.message.reply_text(f"Error de comunicacion MQTT: {e}")

async def periodo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    "comando /periodo <segundos>: establece el periodo de lectura del sensor"
    if not context.args:
        await update.message.reply_text("Uso: /periodo <segundos>. Ejemplo: /periodo 10")
        return 
    valor=context.args[0]
    try:
        int(valor)  # Verificar que el valor es un número valido
        await enviar_mqtt("periodo", valor)
        await update.message.reply_text(f"Periodo de lectura establecido a {valor} segundos")
    except ValueError:
        await update.message.reply_text("Por favor, ingresa un número válido para el periodo.")
    except Exception as e:
        await update.message.reply_text(f"Error de comunicacion MQTT: {e}")

async def modo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    "comando /modo <auto/manual>: cambia el modo del termotasto"
    if not context.args:
        await update.message.reply_text("Uso: /modo <auto/manual>. Ejemplo: /modo auto")
        return
    
    modo=context.args[0].lower()

    if modo not in ["auto", "manual"]:
        await update.message.reply_text("Che amigo, ingresa 'auto' o 'manual' para el modo.🤬🤬🤬😡😡🤬🤬🤬👺👹")
        return
    
    try:
        await enviar_mqtt("modo", modo)
        await update.message.reply_text(f"Modo cambiado a {modo.upper()}")
    except Exception as e:
        await update.message.reply_text(f"Error de comunicacion MQTT: {e}")

async def rele(update: Update, context: ContextTypes.DEFAULT_TYPE):
    "comando /rele <on/off>: enciende o apaga el rele en modo manual"
    if not context.args:
        await update.message.reply_text("Uso: /rele <on/off>. Ejemplo: /rele on")
        return
    estado=context.args[0].upper()
    
    if estado not in ["ON", "OFF"]:
        await update.message.reply_text("Por favor, ingresa 'ON' o 'OFF' para el rele.")
        return
   
    Payload_rele = "1" if estado == "ON" else "0"

    try:
        await enviar_mqtt("rele", Payload_rele)
        await update.message.reply_text(f"Orden enviada para poner el rele {estado}")
    except Exception as e:
        await update.message.reply_text(f"Error de comunicacion MQTT: {e}")

async def destello(update: Update, context: ContextTypes.DEFAULT_TYPE):
    "comando /destello: hace parpadear el led físico del pico W"
    try:
        await enviar_mqtt("destello", "1")
        await update.message.reply_text("Destello activado")
    except Exception as e:
        await update.message.reply_text(f"Error de comunicacion MQTT: {e}")

#MAIN

def main():
    "funcion principal: configura el bot y lo pone a escuchar los comandos"
    app = Application.builder().token(token).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("setpoint", setpoint))
    app.add_handler(CommandHandler("periodo", periodo))
    app.add_handler(CommandHandler("modo", modo))
    app.add_handler(CommandHandler("rele", rele))
    app.add_handler(CommandHandler("destello", destello))

    app.run_polling()

    if __name__ == "__main__":
        main()