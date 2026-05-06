import asyncio, ssl, certifi, logging, os
import aiomqtt

logging.basicConfig(format='%(asctime)s - cliente mqtt - %(levelname)s:%(message)s', 
level=logging.INFO, 
datefmt='%d/%m/%Y %H:%M:%S %z')

async def topico1(client,topic):
    async with client.messages().filter(topic=topic) as messages:
        async for message in messages:
            logging.info(f"CORRUTINA {topic}: {message.payload.decode('utf-8')}")

async def main():
    #Todo esto es el certificado
    tls_context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
    tls_context.verify_mode = ssl.CERT_REQUIRED
    tls_context.check_hostname = True
    tls_context.load_default_certs()

    async with aiomqtt.Client(
        os.environ['SERVIDOR'],
        port=8883,
        tls_context=tls_context,
    ) as client:
        await client.subscribe(os.environ['TOPICO'])

if __name__ == "__main__":
    asyncio.run(main())
