from src.services.notification_service import NotificationService
import requests

service = NotificationService()
APPOINTMENT_SERVICE_URL = "http://localhost:8005"

def handle_prescription_ready(event: dict):
    data = event["data"]
    prescription_id = data["prescription_id"]
    appointment_id = data["appointment_id"]
    dispense_id = data["dispense_id"]
    code = data.get("prescription_code")

    # Gọi appointment-service để lấy patient_id
    try:
        url = f"{APPOINTMENT_SERVICE_URL}/appointments/{appointment_id}"
        resp = requests.get(url, timeout=5.0)
        if resp.status_code == 200:
            appointment = resp.json()
            patient_id = appointment["patient_id"]
            service.create_notification(
                user_id=patient_id,
                prescription_id=prescription_id,
                appointment_id=appointment_id,
                dispense_id=dispense_id,
                prescription_code=code
            )
            print(f"✅ Notification saved for prescription {prescription_id}")
        else:
            print("⚠️ Could not fetch appointment info")
    except Exception as e:
        print("⚠️ Error contacting appointment-service:", e)
