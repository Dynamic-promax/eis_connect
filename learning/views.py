from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from .models import Note, Assignment, AssignmentSubmission, ClassVideo
from academics.models import SchoolClass, Subject, Teacher, Student
from results.models import SessionTerm


def get_role(user):
    try:
        return user.profile.role
    except Exception:
        return None


# ─── NOTES ────────────────────────────────────────────────────────────────────

@login_required
def note_list(request):
    role = get_role(request.user)
    session_terms = SessionTerm.objects.all()
    classes = SchoolClass.objects.all()
    notes = Note.objects.select_related(
        'teacher', 'subject', 'school_class', 'session_term'
    )

    selected_class = request.GET.get('class_id')
    selected_term = request.GET.get('term_id')
    selected_subject = request.GET.get('subject_id')

    if role == 'student':
        try:
            student = request.user.student_profile
            notes = notes.filter(school_class=student.school_class)
            classes = SchoolClass.objects.filter(id=student.school_class.id)
        except Exception:
            notes = Note.objects.none()

    elif role == 'parent':
        try:
            parent = request.user.parent_profile
            child_classes = parent.children.values_list('school_class', flat=True)
            notes = notes.filter(school_class__in=child_classes)
        except Exception:
            notes = Note.objects.none()

    elif role == 'teacher':
        try:
            teacher = request.user.teacher_profile
            notes = notes.filter(teacher=teacher)
        except Exception:
            notes = Note.objects.none()

    if selected_class:
        notes = notes.filter(school_class_id=selected_class)
    if selected_term:
        notes = notes.filter(session_term_id=selected_term)
    if selected_subject:
        notes = notes.filter(subject_id=selected_subject)

    subjects = Subject.objects.all()

    return render(request, 'learning/note_list.html', {
        'notes': notes,
        'classes': classes,
        'session_terms': session_terms,
        'subjects': subjects,
        'selected_class': selected_class,
        'selected_term': selected_term,
        'selected_subject': selected_subject,
        'role': role,
    })


@login_required
def upload_note(request):
    role = get_role(request.user)
    if role not in ['teacher', 'admin']:
        messages.error(request, 'You do not have permission to upload notes.')
        return redirect('note_list')

    session_term = SessionTerm.objects.filter(is_active=True).first()

    try:
        teacher = request.user.teacher_profile
        subjects = teacher.subjects.select_related('school_class').all()
        classes = SchoolClass.objects.filter(
            id__in=subjects.values_list('school_class', flat=True)
        )
    except Exception:
        subjects = Subject.objects.select_related('school_class').all()
        classes = SchoolClass.objects.all()
        teacher = None

    if request.method == 'POST':
        topic = request.POST.get('topic')
        week = request.POST.get('week')
        description = request.POST.get('description', '')
        subject_id = request.POST.get('subject_id')
        class_id = request.POST.get('class_id')
        file = request.FILES.get('file')

        if not file:
            messages.error(request, 'Please select a file to upload.')
            return render(request, 'learning/upload_note.html', {
                'subjects': subjects,
                'classes': classes,
                'session_term': session_term,
            })

        allowed = ['pdf', 'doc', 'docx', 'ppt', 'pptx', 'jpg', 'jpeg', 'png']
        ext = file.name.split('.')[-1].lower()
        if ext not in allowed:
            messages.error(request, f'File type .{ext} is not allowed. Use PDF, Word, PowerPoint, or image.')
            return render(request, 'learning/upload_note.html', {
                'subjects': subjects,
                'classes': classes,
                'session_term': session_term,
            })

        if not session_term:
            messages.error(request, 'No active term. Ask admin to set one.')
            return render(request, 'learning/upload_note.html', {
                'subjects': subjects,
                'classes': classes,
                'session_term': session_term,
            })

        subject = get_object_or_404(Subject, id=subject_id)
        school_class = get_object_or_404(SchoolClass, id=class_id)

        if teacher:
            note_teacher = teacher
        else:
            note_teacher = Teacher.objects.first()

        Note.objects.create(
            teacher=note_teacher,
            school_class=school_class,
            subject=subject,
            session_term=session_term,
            topic=topic,
            week=week,
            description=description,
            file=file,
        )

        messages.success(request, f'Note "{topic}" uploaded successfully.')
        return redirect('note_list')

    return render(request, 'learning/upload_note.html', {
        'subjects': subjects,
        'classes': classes,
        'session_term': session_term,
    })


@login_required
def delete_note(request, pk):
    note = get_object_or_404(Note, pk=pk)
    role = get_role(request.user)

    try:
        is_owner = note.teacher.user == request.user
    except Exception:
        is_owner = False

    if role == 'admin' or is_owner:
        note.file.delete(save=False)
        note.delete()
        messages.success(request, 'Note deleted successfully.')
    else:
        messages.error(request, 'You cannot delete this note.')

    return redirect('note_list')


# ─── ASSIGNMENTS ───────────────────────────────────────────────────────────────

@login_required
def assignment_list(request):
    role = get_role(request.user)
    session_terms = SessionTerm.objects.all()
    classes = SchoolClass.objects.all()
    assignments = Assignment.objects.select_related(
        'teacher', 'subject', 'school_class', 'session_term'
    )

    selected_class = request.GET.get('class_id')
    selected_term = request.GET.get('term_id')

    if role == 'student':
        try:
            student = request.user.student_profile
            assignments = assignments.filter(school_class=student.school_class)
            classes = SchoolClass.objects.filter(id=student.school_class.id)
        except Exception:
            assignments = Assignment.objects.none()

    elif role == 'parent':
        try:
            parent = request.user.parent_profile
            child_classes = parent.children.values_list('school_class', flat=True)
            assignments = assignments.filter(school_class__in=child_classes)
        except Exception:
            assignments = Assignment.objects.none()

    elif role == 'teacher':
        try:
            teacher = request.user.teacher_profile
            assignments = assignments.filter(teacher=teacher)
        except Exception:
            assignments = Assignment.objects.none()

    if selected_class:
        assignments = assignments.filter(school_class_id=selected_class)
    if selected_term:
        assignments = assignments.filter(session_term_id=selected_term)

    return render(request, 'learning/assignment_list.html', {
        'assignments': assignments,
        'classes': classes,
        'session_terms': session_terms,
        'selected_class': selected_class,
        'selected_term': selected_term,
        'role': role,
        'now': timezone.now(),
    })


@login_required
def upload_assignment(request):
    role = get_role(request.user)
    if role not in ['teacher', 'admin']:
        messages.error(request, 'You do not have permission to upload assignments.')
        return redirect('assignment_list')

    session_term = SessionTerm.objects.filter(is_active=True).first()

    try:
        teacher = request.user.teacher_profile
        subjects = teacher.subjects.select_related('school_class').all()
        classes = SchoolClass.objects.filter(
            id__in=subjects.values_list('school_class', flat=True)
        )
    except Exception:
        subjects = Subject.objects.select_related('school_class').all()
        classes = SchoolClass.objects.all()
        teacher = None

    if request.method == 'POST':
        title = request.POST.get('title')
        instruction = request.POST.get('instruction')
        subject_id = request.POST.get('subject_id')
        class_id = request.POST.get('class_id')
        deadline = request.POST.get('deadline')
        file = request.FILES.get('file')

        if not session_term:
            messages.error(request, 'No active term. Ask admin to set one.')
            return render(request, 'learning/upload_assignment.html', {
                'subjects': subjects,
                'classes': classes,
                'session_term': session_term,
            })

        if file:
            allowed = ['pdf', 'doc', 'docx', 'ppt', 'pptx', 'jpg', 'jpeg', 'png']
            ext = file.name.split('.')[-1].lower()
            if ext not in allowed:
                messages.error(request, f'File type .{ext} not allowed.')
                return render(request, 'learning/upload_assignment.html', {
                    'subjects': subjects,
                    'classes': classes,
                    'session_term': session_term,
                })

        subject = get_object_or_404(Subject, id=subject_id)
        school_class = get_object_or_404(SchoolClass, id=class_id)

        if teacher:
            assign_teacher = teacher
        else:
            assign_teacher = Teacher.objects.first()

        Assignment.objects.create(
            teacher=assign_teacher,
            school_class=school_class,
            subject=subject,
            session_term=session_term,
            title=title,
            instruction=instruction,
            file=file,
            deadline=deadline,
        )

        messages.success(request, f'Assignment "{title}" uploaded successfully.')
        return redirect('assignment_list')

    return render(request, 'learning/upload_assignment.html', {
        'subjects': subjects,
        'classes': classes,
        'session_term': session_term,
    })


@login_required
def assignment_detail(request, pk):
    assignment = get_object_or_404(Assignment, pk=pk)
    role = get_role(request.user)
    submission = None

    if role == 'student':
        try:
            student = request.user.student_profile
            submission = AssignmentSubmission.objects.filter(
                assignment=assignment, student=student
            ).first()
        except Exception:
            pass

    return render(request, 'learning/assignment_detail.html', {
        'assignment': assignment,
        'submission': submission,
        'role': role,
        'now': timezone.now(),
    })


@login_required
def submit_assignment(request, pk):
    assignment = get_object_or_404(Assignment, pk=pk)
    role = get_role(request.user)

    if role != 'student':
        messages.error(request, 'Only students can submit assignments.')
        return redirect('assignment_detail', pk=pk)

    try:
        student = request.user.student_profile
    except Exception:
        messages.error(request, 'Student profile not found.')
        return redirect('assignment_list')

    if assignment.is_overdue():
        messages.error(request, 'Deadline has passed. You can no longer submit.')
        return redirect('assignment_detail', pk=pk)

    if AssignmentSubmission.objects.filter(assignment=assignment, student=student).exists():
        messages.error(request, 'You have already submitted this assignment.')
        return redirect('assignment_detail', pk=pk)

    if request.method == 'POST':
        file = request.FILES.get('file')
        text_answer = request.POST.get('text_answer', '')

        AssignmentSubmission.objects.create(
            assignment=assignment,
            student=student,
            file=file,
            text_answer=text_answer,
        )
        messages.success(request, 'Assignment submitted successfully.')
        return redirect('assignment_detail', pk=pk)

    return redirect('assignment_detail', pk=pk)


@login_required
def view_submissions(request, pk):
    assignment = get_object_or_404(Assignment, pk=pk)
    role = get_role(request.user)

    if role not in ['teacher', 'admin']:
        messages.error(request, 'You do not have permission to view submissions.')
        return redirect('assignment_list')

    submissions = AssignmentSubmission.objects.filter(
        assignment=assignment
    ).select_related('student')

    return render(request, 'learning/view_submissions.html', {
        'assignment': assignment,
        'submissions': submissions,
    })


@login_required
def delete_assignment(request, pk):
    assignment = get_object_or_404(Assignment, pk=pk)
    role = get_role(request.user)

    try:
        is_owner = assignment.teacher.user == request.user
    except Exception:
        is_owner = False

    if role == 'admin' or is_owner:
        if assignment.file:
            assignment.file.delete(save=False)
        assignment.delete()
        messages.success(request, 'Assignment deleted.')
    else:
        messages.error(request, 'You cannot delete this assignment.')

    return redirect('assignment_list')

@login_required
def grade_submission(request, pk):
    submission = get_object_or_404(AssignmentSubmission, pk=pk)
    role = get_role(request.user)

    if role not in ['teacher', 'admin']:
        messages.error(request, 'You do not have permission to grade submissions.')
        return redirect('assignment_list')

    # make sure teacher owns this assignment
    try:
        if role == 'teacher':
            teacher = request.user.teacher_profile
            if submission.assignment.teacher != teacher:
                messages.error(request, 'You can only grade your own assignments.')
                return redirect('assignment_list')
    except Exception:
        pass

    if request.method == 'POST':
        score = request.POST.get('score')
        teacher_remark = request.POST.get('teacher_remark', '')

        try:
            score = float(score)
            max_score = 100

            # calculate grade from score
            if score >= 70:
                grade = 'A'
            elif score >= 60:
                grade = 'B'
            elif score >= 50:
                grade = 'C'
            elif score >= 45:
                grade = 'D'
            elif score >= 40:
                grade = 'E'
            else:
                grade = 'F'

            submission.score = score
            submission.grade = grade
            submission.teacher_remark = teacher_remark
            submission.graded_at = timezone.now()
            submission.is_graded = True
            submission.save()

            messages.success(
                request,
                f'Submission graded. {submission.student.get_full_name()} '
                f'scored {score}/100 — Grade {grade}.'
            )
            return redirect('view_submissions', pk=submission.assignment.pk)

        except ValueError:
            messages.error(request, 'Please enter a valid score.')

    return render(request, 'learning/grade_submission.html', {
        'submission': submission,
    })


@login_required
def my_assignment_grade(request, pk):
    assignment = get_object_or_404(Assignment, pk=pk)
    role = get_role(request.user)
    submission = None

    if role == 'student':
        try:
            student = request.user.student_profile
            submission = AssignmentSubmission.objects.filter(
                assignment=assignment,
                student=student
            ).first()
        except Exception:
            pass

    elif role == 'parent':
        try:
            parent = request.user.parent_profile
            children = parent.children.all()
            submission = AssignmentSubmission.objects.filter(
                assignment=assignment,
                student__in=children
            ).first()
        except Exception:
            pass

    return render(request, 'learning/my_assignment_grade.html', {
        'assignment': assignment,
        'submission': submission,
        'role': role,
    })
    
    from .models import ClassVideo


@login_required
def video_list(request):
    role = get_role(request.user)
    videos = ClassVideo.objects.select_related(
        'teacher', 'subject', 'school_class', 'session_term'
    )

    if role == 'student':
        try:
            student = request.user.student_profile
            videos = videos.filter(school_class=student.school_class)
        except Exception:
            videos = ClassVideo.objects.none()

    elif role == 'parent':
        try:
            parent = request.user.parent_profile
            child_classes = parent.children.values_list('school_class', flat=True)
            videos = videos.filter(school_class__in=child_classes)
        except Exception:
            videos = ClassVideo.objects.none()

    elif role == 'teacher':
        try:
            teacher = request.user.teacher_profile
            videos = videos.filter(teacher=teacher)
        except Exception:
            videos = ClassVideo.objects.none()

    classes = SchoolClass.objects.all()
    session_terms = SessionTerm.objects.all()
    selected_class = request.GET.get('class_id')
    selected_term = request.GET.get('term_id')

    if selected_class:
        videos = videos.filter(school_class_id=selected_class)
    if selected_term:
        videos = videos.filter(session_term_id=selected_term)

    return render(request, 'learning/video_list.html', {
        'videos': videos,
        'classes': classes,
        'session_terms': session_terms,
        'selected_class': selected_class,
        'selected_term': selected_term,
        'role': role,
    })


@login_required
def upload_video(request):
    role = get_role(request.user)
    if role not in ['teacher', 'admin']:
        messages.error(request, 'You do not have permission to upload videos.')
        return redirect('video_list')

    session_term = SessionTerm.objects.filter(is_active=True).first()

    try:
        teacher = request.user.teacher_profile
        subjects = teacher.subjects.select_related('school_class').all()
        classes = SchoolClass.objects.filter(
            id__in=subjects.values_list('school_class', flat=True)
        )
    except Exception:
        subjects = Subject.objects.select_related('school_class').all()
        classes = SchoolClass.objects.all()
        teacher = None

    if request.method == 'POST':
        title = request.POST.get('title')
        description = request.POST.get('description', '')
        week = request.POST.get('week')
        subject_id = request.POST.get('subject_id')
        class_id = request.POST.get('class_id')
        video_file = request.FILES.get('video_file')
        video_url = request.POST.get('video_url', '').strip()

        if not video_file and not video_url:
            messages.error(request, 'Please upload a video file or provide a video URL.')
            return render(request, 'learning/upload_video.html', {
                'subjects': subjects, 'classes': classes, 'session_term': session_term,
            })

        if video_file:
            allowed = ['mp4', 'webm', 'mkv', 'avi', 'mov']
            ext = video_file.name.split('.')[-1].lower()
            if ext not in allowed:
                messages.error(request, f'File type .{ext} not allowed. Use MP4, WebM, MKV, AVI, or MOV.')
                return render(request, 'learning/upload_video.html', {
                    'subjects': subjects, 'classes': classes, 'session_term': session_term,
                })

        if not session_term:
            messages.error(request, 'No active term. Ask admin to set one.')
            return render(request, 'learning/upload_video.html', {
                'subjects': subjects, 'classes': classes, 'session_term': session_term,
            })

        subject = get_object_or_404(Subject, id=subject_id)
        school_class = get_object_or_404(SchoolClass, id=class_id)
        video_teacher = teacher if teacher else Teacher.objects.first()

        ClassVideo.objects.create(
            teacher=video_teacher,
            school_class=school_class,
            subject=subject,
            session_term=session_term,
            title=title,
            description=description,
            week=week,
            video_file=video_file,
            video_url=video_url,
        )

        messages.success(request, f'Video "{title}" uploaded successfully.')
        return redirect('video_list')

    return render(request, 'learning/upload_video.html', {
        'subjects': subjects,
        'classes': classes,
        'session_term': session_term,
    })


@login_required
def video_detail(request, pk):
    video = get_object_or_404(ClassVideo, pk=pk)
    role = get_role(request.user)

    embed_url = None
    if video.video_url:
        url = video.video_url
        if 'youtube.com/watch?v=' in url:
            video_id = url.split('watch?v=')[1].split('&')[0]
            embed_url = f'https://www.youtube.com/embed/{video_id}'
        elif 'youtu.be/' in url:
            video_id = url.split('youtu.be/')[1].split('?')[0]
            embed_url = f'https://www.youtube.com/embed/{video_id}'
        else:
            embed_url = url

    return render(request, 'learning/video_detail.html', {
        'video': video,
        'role': role,
        'embed_url': embed_url,
    })


@login_required
def delete_video(request, pk):
    video = get_object_or_404(ClassVideo, pk=pk)
    role = get_role(request.user)

    try:
        is_owner = video.teacher.user == request.user
    except Exception:
        is_owner = False

    if role == 'admin' or is_owner:
        if video.video_file:
            video.video_file.delete(save=False)
        video.delete()
        messages.success(request, 'Video deleted.')
    else:
        messages.error(request, 'You cannot delete this video.')

    return redirect('video_list')