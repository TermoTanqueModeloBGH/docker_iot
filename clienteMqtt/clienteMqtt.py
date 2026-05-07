import asyncio, ssl, certifi, logging, os
import aiomqtt
#se coloca taskname para identificar la corrutina que se esta ejecutando
logging.basicConfig(format='%(asctime)s -[%(taskName)s] - %(levelname)s:%(message)s', 
level=logging.INFO, 
datefmt='%d/%m/%Y %H:%M:%S %z')

async def escuchar(client, topic):
     async for message in client.messages:
        if message.topic.matches(topic):
            logging.info(f"Mensaje recibido en el tema {message.topic}: "f"{message.payload.decode('utf-8')}")

async def conteo(cont):
    while True:
        await asyncio.sleep(3)
        cont["contador"] += 1
        logging.info(f"Contador: {cont['contador']}")

async def publicar(client, cont, topic):
    while True:
        await asyncio.sleep(5)
        valor_publicar = cont["contador"]
        await client.publish(topic, payload=str(valor_publicar))
        logging.info(f"Publicado en el tema {topic}: {valor_publicar}")

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

            #contador con dicionario 
            cont={"contador": 0}

            #obtiene los topicos del entorno
            topico1=os.environ['TOPICO1']
            topico2=os.environ['TOPICO2']

            #suscribe a los topicos
            await client.subscribe(topico1)
            await client.subscribe(topico2)

            #Creacion de las tareas para escuchar los mensajes de cada topico
            tarea1=asyncio.create_task(escuchar(client, topico1), name="Tarea-Topico1")
            tarea2=asyncio.create_task(escuchar(client, topico2), name="Tarea-Topico2")
            tarea3=asyncio.create_task(conteo(cont), name="Tarea-Conteo")
            tarea4=asyncio.create_task(publicar(client, cont, os.environ['TOPICO3']), name="Tarea-Publicar")

            #mantener las tareas corriendo para escuchar los mensajes de ambos topicos
            #gather espera a que ambas tareas terminen, lo cual no sucedera hasta que se salga por interrupcion manual
            await asyncio.gather(tarea1, tarea2, tarea3, tarea4) 

    except aiomqtt.MqttError:
        logging.error(f"Error al conectar al broker MQTT")

if __name__ == "__main__":
    try: 
        asyncio.run(main())
    except KeyboardInterrupt:
        logging.info("Cliente MQTT detenido a mano")
