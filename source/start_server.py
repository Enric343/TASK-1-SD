import pika
import time
import redis


# Limpia redis
r = redis.Redis(host='localhost', port=7043)
r.flushdb()

while True:
    try:
        connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost', heartbeat=600))
        channel = connection.channel()
        channel.exchange_declare(exchange='discovery', exchange_type='fanout') # Declara el exchange discovery
        break
    except pika.exceptions.AMQPConnectionError as e:
        print(f"Error de connexión \"{e}\", volviendo a intentar en 5 segundos...")
        time.sleep(5)

# Servidor inicializado
print("Servidor de MyChat activo.")
