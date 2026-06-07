from django.contrib import admin
from django.contrib.auth.models import User
from .models import Section, SchoolClass, Subject, Parent, Student, Teacher


def activate_teachers(modeladmin, request, queryset):
    for teacher in queryset:
        teacher.user.is_active = True
        teacher.user.save()
    modeladmin.message_user(request, f'{queryset.count()} teacher(s) activated successfully.')

activate_teachers.short_description = 'Activate selected teachers'


def deactivate_teachers(modeladmin, request, queryset):
    for teacher in queryset:
        teacher.user.is_active = False
        teacher.user.save()
    modeladmin.message_user(request, f'{queryset.count()} teacher(s) deactivated.')

deactivate_teachers.short_description = 'Deactivate selected teachers'


def reset_teacher_password(modeladmin, request, queryset):
    for teacher in queryset:
        teacher.user.set_unusable_password()
        teacher.user.save()
        try:
            teacher.user.profile.must_change_password = True
            teacher.user.profile.save()
        except Exception:
            pass
    modeladmin.message_user(request, f'{queryset.count()} teacher password(s) reset. They must set a new password on next login.')

reset_teacher_password.short_description = 'Reset password (force re-set on next login)'


@admin.register(Section)
class SectionAdmin(admin.ModelAdmin):
    list_display = ['name']


@admin.register(SchoolClass)
class SchoolClassAdmin(admin.ModelAdmin):
    list_display = ['name', 'section']
    list_filter = ['section']


@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = ['name', 'school_class']
    list_filter = ['school_class']


@admin.register(Parent)
class ParentAdmin(admin.ModelAdmin):
    list_display = ['user', 'phone']
    search_fields = ['user__first_name', 'user__last_name']


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ['admission_number', 'first_name', 'surname', 'school_class', 'gender']
    list_filter = ['school_class', 'gender']
    search_fields = ['first_name', 'surname', 'admission_number']


def get_teacher_status(obj):
    return 'Active' if obj.user.is_active else 'Inactive'

get_teacher_status.short_description = 'Status'


@admin.register(Teacher)
class TeacherAdmin(admin.ModelAdmin):
    list_display = ['user', 'phone', get_teacher_status]
    search_fields = ['user__first_name', 'user__last_name']
    filter_horizontal = ['subjects']
    actions = [activate_teachers, deactivate_teachers, reset_teacher_password]

    def save_model(self, request, obj, form, change):
        # when a new teacher is saved, make sure their profile exists
        super().save_model(request, obj, form, change)
        from accounts.models import UserProfile
        profile, created = UserProfile.objects.get_or_create(user=obj.user)
        if created:
            profile.role = 'teacher'
            profile.phone = obj.phone
            profile.must_change_password = True
            profile.save()
        if not obj.user.has_usable_password():
            obj.user.set_unusable_password()
            obj.user.save()