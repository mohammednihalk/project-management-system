from .models import Notification

def notification_count(request):
    if request.session.get('user_id'):
        count = Notification.objects.filter(
            user_id=request.session['user_id'],
            is_read=False
        ).count()
        return {'unread_count': count}
    return {}