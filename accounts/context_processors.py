from communication.models import Announcement


def ticker_announcements(request):
    if not request.user.is_authenticated:
        return {}

    try:
        role = request.user.profile.role
    except Exception:
        return {}

    if role in ['admin', 'accountant']:
        anns = Announcement.objects.all()[:6]
    elif role == 'teacher':
        anns = Announcement.objects.filter(target__in=['all', 'teachers'])[:6]
    elif role == 'parent':
        anns = Announcement.objects.filter(target__in=['all', 'parents', 'parents_students'])[:6]
    elif role == 'student':
        anns = Announcement.objects.filter(target__in=['all', 'students', 'parents_students'])[:6]
    else:
        anns = Announcement.objects.none()

    return {'ticker_announcements': anns}


def dark_mode(request):
    return {'dark_mode': request.session.get('dark_mode', False)}