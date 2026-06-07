import base64
import random
import string
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.utils import timezone
from .models import UserProfile
from communication.models import Announcement


def login_view(request):
    if request.user.is_authenticated:
        return redirect_by_role(request.user)

    if request.method == 'POST':
        username = request.POST.get('username').strip()
        password = request.POST.get('password')

        # check if this is a first-time user with no password set
        try:
            user_obj = User.objects.get(username=username)
            if not user_obj.has_usable_password():
                token = base64.urlsafe_b64encode(str(user_obj.id).encode()).decode()
                return redirect(f'/set-password/?token={token}')
        except User.DoesNotExist:
            pass

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect_by_role(user)
        else:
            messages.error(request, 'Invalid username or password.')

    return render(request, 'accounts/login.html')


def redirect_by_role(user):
    try:
        role = user.profile.role
    except Exception:
        return redirect('/admin/')

    if role == 'admin':
        return redirect('admin_dashboard')
    elif role == 'teacher':
        return redirect('teacher_dashboard')
    elif role == 'parent':
        return redirect('parent_dashboard')
    elif role == 'student':
        return redirect('student_dashboard')
    elif role == 'accountant':
        return redirect('admin_dashboard')
    else:
        return redirect('/admin/')


def logout_view(request):
    logout(request)
    return redirect('login')


def set_password_view(request):
    token = request.GET.get('token') or request.POST.get('token')

    if not token:
        return redirect('login')

    try:
        user_id = int(base64.urlsafe_b64decode(token.encode()).decode())
        user = User.objects.get(id=user_id)
    except Exception:
        messages.error(request, 'Invalid or expired link.')
        return redirect('login')

    if request.method == 'POST':
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')

        if password1 != password2:
            messages.error(request, 'Passwords do not match.')
        elif len(password1) < 6:
            messages.error(request, 'Password must be at least 6 characters.')
        else:
            user.set_password(password1)
            user.save()
            try:
                user.profile.must_change_password = False
                user.profile.save()
            except Exception:
                pass
            login(request, user)
            messages.success(request, 'Password set successfully. Welcome!')
            return redirect_by_role(user)

    return render(request, 'accounts/set_password.html', {
        'token': token,
        'username': user.username,
        'full_name': user.get_full_name(),
    })


def forgot_password_view(request):
    step = request.session.get('forgot_step', 1)

    if request.method == 'POST':
        if step == 1:
            username = request.POST.get('username', '').strip()
            try:
                user = User.objects.get(username=username)
                if not user.has_usable_password():
                    messages.error(request, 'This account has not set a password yet. Use the login page to set one.')
                    return render(request, 'accounts/forgot_password.html', {'step': 1})

                # generate 6-digit PIN
                pin = ''.join(random.choices(string.digits, k=6))
                user.profile.reset_pin = pin
                user.profile.reset_pin_created = timezone.now()
                user.profile.save()

                request.session['forgot_username'] = username
                request.session['forgot_step'] = 2

                # show pin on screen since school has no email/SMS yet
                messages.success(
                    request,
                    f'Your reset PIN is: {pin} — Enter it below. '
                    f'(In production this will be sent by SMS.)'
                )
                return render(request, 'accounts/forgot_password.html', {'step': 2})

            except User.DoesNotExist:
                messages.error(request, 'No account found with that username.')

        elif step == 2:
            pin_entered = request.POST.get('pin', '').strip()
            username = request.session.get('forgot_username')

            try:
                user = User.objects.get(username=username)
                time_diff = timezone.now() - user.profile.reset_pin_created
                if time_diff.seconds > 600:
                    messages.error(request, 'PIN has expired. Please start again.')
                    request.session['forgot_step'] = 1
                elif user.profile.reset_pin != pin_entered:
                    messages.error(request, 'Incorrect PIN. Try again.')
                else:
                    request.session['forgot_step'] = 3
                    return render(request, 'accounts/forgot_password.html', {'step': 3})
            except User.DoesNotExist:
                messages.error(request, 'Session expired. Please start again.')
                request.session['forgot_step'] = 1

        elif step == 3:
            password1 = request.POST.get('password1')
            password2 = request.POST.get('password2')
            username = request.session.get('forgot_username')

            if password1 != password2:
                messages.error(request, 'Passwords do not match.')
                return render(request, 'accounts/forgot_password.html', {'step': 3})
            elif len(password1) < 6:
                messages.error(request, 'Password must be at least 6 characters.')
                return render(request, 'accounts/forgot_password.html', {'step': 3})
            else:
                try:
                    user = User.objects.get(username=username)
                    user.set_password(password1)
                    user.save()
                    user.profile.reset_pin = ''
                    user.profile.save()
                    request.session.pop('forgot_step', None)
                    request.session.pop('forgot_username', None)
                    messages.success(request, 'Password reset successfully. You can now log in.')
                    return redirect('login')
                except User.DoesNotExist:
                    messages.error(request, 'Session expired. Please start again.')
                    return redirect('forgot_password')

    return render(request, 'accounts/forgot_password.html', {'step': step})

def toggle_dark_mode(request):
    current = request.session.get('dark_mode', False)
    request.session['dark_mode'] = not current
    next_url = request.META.get('HTTP_REFERER', '/')
    return redirect(next_url)

@login_required
def admin_dashboard(request):
    from academics.models import Student, Teacher, SchoolClass
    from results.models import Result, SessionTerm

    context = {
    'total_students': Student.objects.count(),
    'total_teachers': Teacher.objects.count(),
    'total_classes': SchoolClass.objects.count(),
    'pending_results': Result.objects.filter(status='pending').count(),
    'active_term': SessionTerm.objects.filter(is_active=True).first(),
    'recent_announcements': Announcement.objects.all()[:3],
    }
    return render(request, 'accounts/admin_dashboard.html', context)


@login_required
def teacher_dashboard(request):
    from academics.models import Teacher
    from results.models import Result

    try:
        teacher = request.user.teacher_profile
        assigned_subjects = teacher.subjects.select_related('school_class').all()
        results_submitted = Result.objects.filter(teacher=teacher).count()
        results_pending = Result.objects.filter(teacher=teacher, status='pending').count()
        results_approved = Result.objects.filter(teacher=teacher, status='approved').count()
    except Exception:
        assigned_subjects = []
        results_submitted = 0
        results_pending = 0
        results_approved = 0

    context = {
        'assigned_subjects': assigned_subjects,
        'total_subjects': len(list(assigned_subjects)),
        'results_submitted': results_submitted,
        'results_pending': results_pending,
        'results_approved': results_approved,
        'recent_announcements': Announcement.objects.filter(
            target__in=['all', 'teachers']
        )[:3],
    }
    return render(request, 'accounts/teacher_dashboard.html', context)


@login_required
def parent_dashboard(request):
    children = []
    try:
        parent = request.user.parent_profile
        children = parent.children.select_related('school_class').all()
    except Exception:
        pass
    
    context = {
        'children': children,
        'recent_announcements': Announcement.objects.filter(
            target__in=['all', 'parents', 'parents_students']
        )[:3],
    }

    return render(request, 'accounts/parent_dashboard.html', {'children': children})


@login_required
def student_dashboard(request):
    student = None
    try:
        student = request.user.student_profile
    except Exception:
        pass
    
    context = {
        'student': student,
        'recent_announcements': Announcement.objects.filter(
            target__in=['all', 'students', 'parents_students']
        )[:3],
    }   

    return render(request, 'accounts/student_dashboard.html', {'student': student})

def create_password_view(request):
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')

        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            messages.error(request, 'No account found with that username.')
            return render(request, 'accounts/create_password.html')

        if user.has_usable_password():
            messages.error(
                request,
                'This account already has a password. Use Forgot Password instead.'
            )
            return render(request, 'accounts/create_password.html')

        if password1 != password2:
            messages.error(request, 'Passwords do not match.')
            return render(request, 'accounts/create_password.html')

        if len(password1) < 6:
            messages.error(request, 'Password must be at least 6 characters.')
            return render(request, 'accounts/create_password.html')

        user.set_password(password1)
        user.save()
        try:
            user.profile.must_change_password = False
            user.profile.save()
        except Exception:
            pass

        login(request, user)
        messages.success(request, 'Password created successfully. Welcome!')
        return redirect_by_role(user)

    return render(request, 'accounts/create_password.html')

@login_required
def learning_games(request):
    return render(request, 'accounts/learning_games.html')