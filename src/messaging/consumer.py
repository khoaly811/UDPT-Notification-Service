import pika, json
from config.settings import settings
from src.messaging.prescription_handler import handle_prescription_ready
from src.messaging.appointment_handler import (
    handle_appointment_confirmed,
    handle_appointment_cancelled
)

# Map event_type -> handler function
HANDLERS = {
    "prescription_ready": handle_prescription_ready,
    "appointment_confirmed": handle_appointment_confirmed,
    "appointment_cancelled": handle_appointment_cancelled,
}

def callback(ch, method, properties, body):
    try:
        event = json.loads(body)
        event_type = event.get("event_type")
        print(f"📩 Received event: {event_type}")

        handler = HANDLERS.get(event_type)
        if handler:
            handler(event)
        else:
            print(f"⚠️ No handler for event_type={event_type}")
    except Exception as e:
        print("❌ Error processing event:", e)

def start_consumer():
    params = pika.ConnectionParameters(
        host=settings.rabbitmq.host,
        port=settings.rabbitmq.port,
        virtual_host=settings.rabbitmq.virtual_host,
        credentials=pika.PlainCredentials(
            settings.rabbitmq.username,
            settings.rabbitmq.password
        ),
    )
    connection = pika.BlockingConnection(params)
    channel = connection.channel()

    # declare queues khớp với producers
    channel.queue_declare(queue="prescription_notifications", durable=True, arguments={'x-message-ttl': 86400000})
    channel.queue_declare(queue="appointment.confirmed", durable=True, arguments={'x-message-ttl': 86400000})
    channel.queue_declare(queue="appointment.cancelled", durable=True, arguments={'x-message-ttl': 86400000})

    # consume từ nhiều queue
    channel.basic_consume(queue="prescription_notifications", on_message_callback=callback, auto_ack=True)
    channel.basic_consume(queue="appointment.confirmed", on_message_callback=callback, auto_ack=True)
    channel.basic_consume(queue="appointment.cancelled", on_message_callback=callback, auto_ack=True)

    print("👂 Waiting for notifications...")
    channel.start_consuming()
