from src.services.notification_service import NotificationService

service = NotificationService()

def handle_appointment_confirmed(event: dict):
    data = event["data"]
    service.create_notification(
        user_id=data["patient_id"],
        appointment_id=data["appointment_id"],
        title="Lịch khám đã được xác nhận",
        message=f"Lịch khám với bác sĩ {data['doctor_name']} vào {data['appointment_date']} {data['appointment_time']} đã được xác nhận."
    )
    print(f"✅ Notification saved for confirmed appointment {data['appointment_id']}")

def handle_appointment_cancelled(event: dict):
    data = event["data"]
    service.create_notification(
        user_id=data["patient_id"],
        appointment_id=data["appointment_id"],
        title="Lịch khám đã bị hủy",
        message=f"Lịch khám với bác sĩ {data['doctor_name']} vào {data['appointment_date']} {data['appointment_time']} đã bị hủy. Lý do: {data.get('cancellation_reason')}"
    )
    print(f"✅ Notification saved for cancelled appointment {data['appointment_id']}")
