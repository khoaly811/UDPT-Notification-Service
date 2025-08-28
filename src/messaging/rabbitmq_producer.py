from config import settings
import pika, json

class RabbitMQProducer:
    def __init__(self):
        creds = pika.PlainCredentials(settings.rabbitmq.user, settings.rabbitmq.password)
        self.connection = pika.BlockingConnection(
            pika.ConnectionParameters(
                host=settings.rabbitmq.host,
                port=settings.rabbitmq.port,
                virtual_host="/",
                credentials=creds
            )
        )
        print("khoa beo 1:", settings.rabbitmq.exchange, settings.rabbitmq.queue)
        self.channel = self.connection.channel()
        self.channel.exchange_declare(exchange=settings.rabbitmq.exchange,
                                      exchange_type="direct", durable=True)
        self.channel.queue_declare(queue=settings.rabbitmq.queue, durable=True)
        self.channel.queue_bind(exchange=settings.rabbitmq.exchange,
                                queue=settings.rabbitmq.queue,
                                routing_key=settings.rabbitmq.routing_key)
        print("khoa beo 2:", settings.rabbitmq.exchange, settings.rabbitmq.queue)


    def publish(self, message: dict):
        body = json.dumps(message)
        self.channel.basic_publish(
            exchange=settings.rabbitmq.exchange,
            routing_key=settings.rabbitmq.routing_key,
            body=body,
            properties=pika.BasicProperties(delivery_mode=2)
        )
        print(f"[x] Sent {body}")

    def close(self):
        self.connection.close()
