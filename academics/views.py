from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from .models import Student, Teacher, SchoolClass, Subject, Section, Parent


@login_required
def student_list(request):
    students = Student.objects.select_related('school_class', 'parent').all()
    classes = SchoolClass.objects.all()
    selected_class = request.GET.get('class_id')

    if selected_class:
        students = students.filter(school_class_id=selected_class)

    return render(request, 'academics/student_list.html', {
        'students': students,
        'classes': classes,
        'selected_class': selected_class,
    })


@login_required
def add_student(request):
    classes = SchoolClass.objects.all()
    parents = Parent.objects.all()

    if request.method == 'POST':
        admission_number = request.POST.get('admission_number')
        first_name = request.POST.get('first_name')
        surname = request.POST.get('surname')
        gender = request.POST.get('gender')
        date_of_birth = request.POST.get('date_of_birth')
        class_id = request.POST.get('school_class')
        parent_id = request.POST.get('parent')
        passport = request.FILES.get('passport')

        if Student.objects.filter(admission_number=admission_number).exists():
            messages.error(request, 'A student with this admission number already exists.')
        elif User.objects.filter(username=admission_number).exists():
            messages.error(request, 'A user account with this admission number already exists.')
        else:
            # create user account with unusable password
            name_parts = first_name.strip().split(' ', 1)
            user = User.objects.create_user(
                username=admission_number,
                first_name=first_name,
                last_name=surname,
                password=None,
            )
            user.set_unusable_password()
            user.save()

            # create profile with student role
            from accounts.models import UserProfile
            UserProfile.objects.create(
                user=user,
                role='student',
                must_change_password=True,
            )

            # create student record linked to user
            student = Student(
                user=user,
                admission_number=admission_number,
                first_name=first_name,
                surname=surname,
                gender=gender,
                date_of_birth=date_of_birth or None,
                school_class_id=class_id,
                parent_id=parent_id or None,
                passport=passport,
            )
            student.save()

            messages.success(
                request,
                f'Student {first_name} {surname} added. '
                f'They can log in with admission number {admission_number} and set their password.'
            )
            return redirect('student_list')

    return render(request, 'academics/add_student.html', {
        'classes': classes,
        'parents': parents,
    })


@login_required
def teacher_list(request):
    teachers = Teacher.objects.select_related('user').prefetch_related('subjects').all()
    return render(request, 'academics/teacher_list.html', {'teachers': teachers})


@login_required
def class_list(request):
    sections = Section.objects.prefetch_related('classes').all()
    return render(request, 'academics/class_list.html', {'sections': sections})


@login_required
def subject_list(request):
    subjects = Subject.objects.select_related('school_class').all()
    classes = SchoolClass.objects.all()
    return render(request, 'academics/subject_list.html', {
        'subjects': subjects,
        'classes': classes,
    })


@login_required
def add_parent(request):
    students = Student.objects.select_related('school_class').all()

    if request.method == 'POST':
        parent_name = request.POST.get('parent_name')
        phone = request.POST.get('phone')
        address = request.POST.get('address', '')
        child_ids = request.POST.getlist('children')

        # phone number is the username
        if User.objects.filter(username=phone).exists():
            messages.error(request, f'A parent with phone number {phone} already exists.')
            return render(request, 'academics/add_parent.html', {'students': students})

        # split name into first and last
        name_parts = parent_name.strip().split(' ', 1)
        first_name = name_parts[0]
        last_name = name_parts[1] if len(name_parts) > 1 else ''

        # create user account with unusable password
        user = User.objects.create_user(
            username=phone,
            first_name=first_name,
            last_name=last_name,
            password=None,
        )
        user.set_unusable_password()
        user.save()

        # create profile with parent role
        from accounts.models import UserProfile
        UserProfile.objects.create(
            user=user,
            role='parent',
            phone=phone,
            must_change_password=True,
        )

        # create parent record
        parent = Parent.objects.create(
            user=user,
            phone=phone,
            address=address,
        )

        # link children
        if child_ids:
            Student.objects.filter(id__in=child_ids).update(parent=parent)

        messages.success(request, f'Parent {parent_name} added. They can log in with phone number {phone} and set their password.')
        return redirect('parent_list')

    return render(request, 'academics/add_parent.html', {'students': students})


@login_required
def parent_list(request):
    parents = Parent.objects.select_related('user').prefetch_related('children').all()
    return render(request, 'academics/parent_list.html', {'parents': parents})

@login_required
def add_teacher(request):
    if request.method == 'POST':
        full_name = request.POST.get('full_name', '').strip()
        phone = request.POST.get('phone', '').strip()
        email = request.POST.get('email', '').strip()
        subject_ids = request.POST.getlist('subjects')

        if User.objects.filter(username=phone).exists():
            messages.error(request, f'A user with phone number {phone} already exists.')
            subjects = Subject.objects.select_related('school_class').all()
            return render(request, 'academics/add_teacher.html', {'subjects': subjects})

        name_parts = full_name.split(' ', 1)
        first_name = name_parts[0]
        last_name = name_parts[1] if len(name_parts) > 1 else ''

        user = User.objects.create_user(
            username=phone,
            first_name=first_name,
            last_name=last_name,
            email=email,
            password=None,
        )
        user.set_unusable_password()
        user.save()

        from accounts.models import UserProfile
        UserProfile.objects.create(
            user=user,
            role='teacher',
            phone=phone,
            must_change_password=True,
        )

        teacher = Teacher.objects.create(user=user, phone=phone)
        if subject_ids:
            teacher.subjects.set(subject_ids)

        messages.success(
            request,
            f'Teacher {full_name} added. '
            f'They log in with phone number {phone} and set their password on first login.'
        )
        return redirect('teacher_list')

    subjects = Subject.objects.select_related('school_class').all()
    return render(request, 'academics/add_teacher.html', {'subjects': subjects})