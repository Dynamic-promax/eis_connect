from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Announcement


def get_role(user):
    try:
        return user.profile.role
    except Exception:
        return None


@login_required
def announcement_list(request):
    role = get_role(request.user)
    announcements = Announcement.objects.select_related('created_by').all()

    if role == 'teacher':
        announcements = announcements.filter(target__in=['all', 'teachers'])
    elif role == 'parent':
        announcements = announcements.filter(target__in=['all', 'parents', 'parents_students'])
    elif role == 'student':
        announcements = announcements.filter(target__in=['all', 'students', 'parents_students'])

    return render(request, 'communication/announcement_list.html', {
        'announcements': announcements,
        'role': role,
    })


@login_required
def create_announcement(request):
    role = get_role(request.user)

    if role != 'admin':
        messages.error(request, 'Only admin can post announcements.')
        return redirect('announcement_list')

    if request.method == 'POST':
        title = request.POST.get('title', '').strip()
        message_text = request.POST.get('message', '').strip()
        target = request.POST.get('target', 'all')
        is_pinned = request.POST.get('is_pinned') == 'on'

        if not title or not message_text:
            messages.error(request, 'Title and message are required.')
        else:
            Announcement.objects.create(
                title=title,
                message=message_text,
                target=target,
                created_by=request.user,
                is_pinned=is_pinned,
            )
            messages.success(request, f'Announcement "{title}" posted.')
            return redirect('announcement_list')

    return render(request, 'communication/create_announcement.html')


@login_required
def delete_announcement(request, pk):
    role = get_role(request.user)
    if role != 'admin':
        messages.error(request, 'Only admin can delete announcements.')
        return redirect('announcement_list')

    announcement = get_object_or_404(Announcement, pk=pk)
    announcement.delete()
    messages.success(request, 'Announcement deleted.')
    return redirect('announcement_list')


@login_required
def pin_announcement(request, pk):
    role = get_role(request.user)
    if role != 'admin':
        messages.error(request, 'Only admin can pin announcements.')
        return redirect('announcement_list')

    announcement = get_object_or_404(Announcement, pk=pk)
    announcement.is_pinned = not announcement.is_pinned
    announcement.save()
    messages.success(request, 'Announcement updated.')
    return redirect('announcement_list')