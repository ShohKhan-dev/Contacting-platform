from .models import User
from .models import Notification

def notifications(request):
    all_notifications = Notification.objects.filter(is_read=False)

    message_notifications = all_notifications.filter(notification_type="message")
    new_join_notifications = all_notifications.filter(notification_type="new_join")


    return {'notifications': all_notifications, 'message_notifications': message_notifications, 'new_join_notifications': new_join_notifications}


def users(request):
    users = User.objects.all().exclude(is_superuser=True)

    return {'users': users}
