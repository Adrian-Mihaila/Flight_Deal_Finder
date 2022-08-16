from notification_manager import NotificationManager
from datetime import datetime, timedelta
import time

notification_manager = NotificationManager()

# Run the method only once every day
# notification_manager.create_email()  # only for testing
while True:
    today = datetime.today()
    tomorrow = today.replace(day=today.day, hour=5, minute=0, second=0, microsecond=0) + timedelta(days=1)
    delta_t = tomorrow-today

    seconds_remaining = delta_t.seconds+1
    print(seconds_remaining)
    time.sleep(seconds_remaining)
    notification_manager.create_email()
    print("Mail Sent")