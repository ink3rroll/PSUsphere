from django.contrib import admin

# Register your models here.
from .models import College, Program, Organization, Student, OrgMember

admin.site.register(College)
@admin.register(Program)
class ProgramAdmin(admin.ModelAdmin):
    list_display = ("prog_name", "college",)

    search_fields = ("prog_name",)

@admin.register(Organization)
class OrganizationAdmin(admin.ModelAdmin):
    list_display = ("name", "college",)

    search_fields = ("name",)
@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ("student_id", "lastname", "firstname", "middlename", "program", "college",)

    search_fields = ("lastname", "firstname",)

    def college(self, obj):
        try:
            prog = Program.objects.get(prog_name=obj.program)
            return prog.college
        
        except Program.DoesNotExist:
            return None

@admin.register(OrgMember)
class OrgMemberAdmin(admin.ModelAdmin):
    list_display = ("student", "program", "organization", "date_joined",)

    search_fields = ("student_lastname", "student_firstname",)

    def program(self, obj):
        try:
            member = Student.objects.get(id=obj.student_id)
            return member.program
        
        except Student.DoesNotExist:
            return None
            