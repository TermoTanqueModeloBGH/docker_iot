import asyncio, ssl, certifi, logging, os
import aiomqtt
#se coloca taskname para identificar la corrutina que se esta ejecutando
logging.basicConfig(format='%(asctime)s -[%(taskName)s] - %(levelname)s:%(message)s', 
level=logging.INFO, 
datefmt='%d/%m/%Y %H:%M:%S %z')

async def escuchar(client, topic):
    #se utiliza un filtro para escuchar solo los mensajes del tema especificado
    async with client.messages.filter(topic) as messages:
        async for message in messages:
            logging.info(f"Mensaje recibido en el tema {message.topic}: {message.payload.decode('utf-8')}")

async def main():
    #direccion del broker desde el entorno
    broker = os.environ['SERVIDOR']
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
        )as client:
            logging.info(f"Conectado al broker MQTT: {broker}")
            #obtiene los topicos del entorno
            topico1=os.environ['TOPICO1']
            topico2=os.environ['TOPICO2']

            #suscribe a los topicos
            await client.subscribe(topico1)
            await client.subscribe(topico2)
            #Creacion de las tareas para escuchar los mensajes de cada topico
            tarea1=asyncio.create_task(escuchar(client, topico1), name="Tarea-Topico1")
            tarea2=asyncio.create_task(escuchar(client, topico2), name="Tarea-Topico2")
            #mantener las tareas corriendo para escuchar los mensajes de ambos topicos
            #gather espera a que ambas tareas terminen, lo cual no sucedera hasta que se salga por interrupcion manual
            await asyncio.gather(tarea1, tarea2) 
    except aiomqtt.MqttError:
        logging.error(f"Error al conectar al broker MQTT")

if __name__ == "__main__":
    try: 
        asyncio.run(main())
    except KeyboardInterrupt:
        logging.info("Cliente MQTT detenido a mano")
