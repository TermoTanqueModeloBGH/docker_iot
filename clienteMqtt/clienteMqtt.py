import asyncio, ssl, certifi, logging, os
import aiomqtt
#se coloca taskname para identificar la corrutina que se esta ejecutando
logging.basicConfig(format='%(asctime)s -[%(taskName)s] - %(levelname)s:%(message)s', 
level=logging.INFO, 
datefmt='%d/%m/%Y %H:%M:%S %z')

async def escuchar(client, t1, t2):
     async for message in client.messages:
        payload=message.payload.decode('utf-8')
        if message.topic.matches(t1):
            asyncio.create_task(atencion1(message.topic, payload), name="Topico-1")
        elif message.topic.matches(t2):
            asyncio.create_task(atencion2(message.topic, payload), name="Topico-2")

async def atencion1(topico, dato):
    logging.info(f"Mensaje recibido en {topico}: {dato}")

async def atencion2(topico, dato):
    logging.info(f"Mensaje recibido en {topico}: {dato}")

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
            tarea1=asyncio.create_task(escuchar(client, topico1, topico2), name="Tarea Escuchar")
            tarea2=asyncio.create_task(conteo(cont), name="Tarea Conteo")
            tarea3=asyncio.create_task(publicar(client, cont, os.environ['TOPICO3']), name="Tarea Publicar")

            #mantener las tareas corriendo para escuchar los mensajes de ambos topicos
            #gather espera a que ambas tareas terminen, lo cual no sucedera hasta que se salga por interrupcion manual
            await asyncio.gather(tarea1, tarea2, tarea3) 

    except aiomqtt.MqttError:
        logging.error(f"Error al conectar al broker MQTT")

if __name__ == "__main__":
    try: 
        asyncio.run(main())
    except KeyboardInterrupt:
        logging.info("Cliente MQTT detenido a mano")
