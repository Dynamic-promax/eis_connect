from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from .models import Result, SessionTerm
from academics.models import Student, Subject, SchoolClass, Teacher


@login_required
def upload_result(request):
    teacher = get_object_or_404(Teacher, user=request.user)
    subjects = teacher.subjects.select_related('school_class').all()
    session_term = SessionTerm.objects.filter(is_active=True).first()
    students = []
    selected_subject = None
    selected_class = None

    if request.GET.get('subject_id') and request.GET.get('class_id'):
        selected_subject = get_object_or_404(Subject, id=request.GET.get('subject_id'))
        selected_class = get_object_or_404(SchoolClass, id=request.GET.get('class_id'))
        students = Student.objects.filter(school_class=selected_class)

    if request.method == 'POST':
        subject_id = request.POST.get('subject_id')
        class_id = request.POST.get('class_id')
        selected_subject = get_object_or_404(Subject, id=subject_id)
        selected_class = get_object_or_404(SchoolClass, id=class_id)
        students = Student.objects.filter(school_class=selected_class)

        if not session_term:
            messages.error(request, 'No active session/term found. Ask admin to set one.')
            return redirect('upload_result')

        saved = 0
        for student in students:
            ca = request.POST.get(f'ca_{student.id}')
            exam = request.POST.get(f'exam_{student.id}')

            if ca and exam:
                try:
                    ca = float(ca)
                    exam = float(exam)

                    if ca > 40:
                        messages.error(request, f'CA score for {student.get_full_name()} cannot exceed 40.')
                        continue
                    if exam > 60:
                        messages.error(request, f'Exam score for {student.get_full_name()} cannot exceed 60.')
                        continue

                    result, created = Result.objects.update_or_create(
                        student=student,
                        subject=selected_subject,
                        session_term=session_term,
                        defaults={
                            'school_class': selected_class,
                            'teacher': teacher,
                            'ca_score': ca,
                            'exam_score': exam,
                            'status': 'pending',
                        }
                    )
                    saved += 1
                except ValueError:
                    messages.error(request, f'Invalid scores for {student.get_full_name()}.')

        if saved:
            messages.success(request, f'Scores saved for {saved} student(s). Awaiting admin approval.')
            return redirect('upload_result')

    return render(request, 'results/upload_result.html', {
        'subjects': subjects,
        'students': students,
        'selected_subject': selected_subject,
        'selected_class': selected_class,
        'session_term': session_term,
    })


@login_required
def pending_results(request):
    results = Result.objects.filter(status='pending').select_related(
        'student', 'subject', 'school_class', 'teacher', 'session_term'
    )
    classes = SchoolClass.objects.all()
    selected_class = request.GET.get('class_id')

    if selected_class:
        results = results.filter(school_class_id=selected_class)

    return render(request, 'results/pending_results.html', {
        'results': results,
        'classes': classes,
        'selected_class': selected_class,
    })


@login_required
def approve_result(request, pk):
    result = get_object_or_404(Result, pk=pk)
    result.status = 'approved'
    result.approved_at = timezone.now()
    result.save()
    messages.success(request, f'Result approved for {result.student.get_full_name()}.')
    return redirect('pending_results')


@login_required
def approve_class_results(request):
    if request.method == 'POST':
        class_id = request.POST.get('class_id')
        session_term_id = request.POST.get('session_term_id')

        updated = Result.objects.filter(
            school_class_id=class_id,
            session_term_id=session_term_id,
            status='pending'
        ).update(status='approved', approved_at=timezone.now())

        messages.success(request, f'{updated} result(s) approved successfully.')
        return redirect('pending_results')

    return redirect('pending_results')


@login_required
def view_result(request):
    user = request.user
    session_terms = SessionTerm.objects.all().order_by('-session')
    results = []
    selected_student = None
    selected_term = None

    try:
        role = user.profile.role
    except:
        role = None

    if role == 'parent':
        try:
            parent = user.parent_profile
            children = parent.children.all()
        except:
            children = []

        student_id = request.GET.get('student_id')
        term_id = request.GET.get('term_id')

        if student_id and term_id:
            selected_student = get_object_or_404(Student, id=student_id)
            selected_term = get_object_or_404(SessionTerm, id=term_id)

            if selected_student.parent == parent:
                results = Result.objects.filter(
                    student=selected_student,
                    session_term=selected_term,
                    status='approved'
                ).select_related('subject')

        return render(request, 'results/view_result.html', {
            'children': children,
            'session_terms': session_terms,
            'results': results,
            'selected_student': selected_student,
            'selected_term': selected_term,
        })

    elif role == 'student':
        try:
            selected_student = user.student_profile
        except:
            selected_student = None

        term_id = request.GET.get('term_id')
        if term_id and selected_student:
            selected_term = get_object_or_404(SessionTerm, id=term_id)
            results = Result.objects.filter(
                student=selected_student,
                session_term=selected_term,
                status='approved'
            ).select_related('subject')

        return render(request, 'results/view_result.html', {
            'session_terms': session_terms,
            'results': results,
            'selected_student': selected_student,
            'selected_term': selected_term,
        })

    elif role in ['admin', 'teacher']:
        students = Student.objects.select_related('school_class').all()
        student_id = request.GET.get('student_id')
        term_id = request.GET.get('term_id')

        if student_id and term_id:
            selected_student = get_object_or_404(Student, id=student_id)
            selected_term = get_object_or_404(SessionTerm, id=term_id)
            results = Result.objects.filter(
                student=selected_student,
                session_term=selected_term,
                status='approved'
            ).select_related('subject')

        return render(request, 'results/view_result.html', {
            'students': students,
            'session_terms': session_terms,
            'results': results,
            'selected_student': selected_student,
            'selected_term': selected_term,
        })

    return redirect('login')


@login_required
def class_result_sheet(request):
    classes = SchoolClass.objects.all()
    session_terms = SessionTerm.objects.all()
    selected_class = None
    selected_term = None
    students_results = []

    class_id = request.GET.get('class_id')
    term_id = request.GET.get('term_id')

    if class_id and term_id:
        selected_class = get_object_or_404(SchoolClass, id=class_id)
        selected_term = get_object_or_404(SessionTerm, id=term_id)
        students = Student.objects.filter(school_class=selected_class)

        for student in students:
            results = Result.objects.filter(
                student=student,
                session_term=selected_term,
                status='approved'
            ).select_related('subject')
            total = sum(r.total_score for r in results)
            students_results.append({
                'student': student,
                'results': results,
                'total': total,
                'count': results.count(),
            })

    return render(request, 'results/class_result_sheet.html', {
        'classes': classes,
        'session_terms': session_terms,
        'selected_class': selected_class,
        'selected_term': selected_term,
        'students_results': students_results,
    })