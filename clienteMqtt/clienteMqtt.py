import asyncio, ssl, certifi, logging, os
import aiomqtt
#se coloca taskname para identificar la corrutina que se esta ejecutando
logging.basicConfig(format='%(asctime)s -[%(taskname)s] - %(levelname)s:%(message)s', 
level=logging.INFO, 
datefmt='%d/%m/%Y %H:%M:%S %z')


async def main():
    #direccion del broker desde el entorno
    broker = os.getenv('SERVIDOR')
    #Todo esto es el certificado
    tls_context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
    tls_context.verify_mode = ssl.CERT_REQUIRED
    tls_context.check_hostname = True
    tls_context.load_default_certs()

    try:
        async with aiomqtt.Client(
        broker,
        port=8883,
        tls_context=tls_context,
        ) as client:
            logging.info("Conectado al broker MQTT: {broker}")
            #suscribirse a un tema
    except aiomqtt.MqttError:
        logging.error(f"Error al conectar al broker MQTT")

if __name__ == "__main__":
    try: 
        asyncio.run(main())
    except KeyboardInterrupt:
        logging.info("Cliente MQTT detenido a mano")
