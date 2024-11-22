from django.shortcuts import render
from django.views.generic.list import ListView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from studentorg.models import Organization, OrgMember, Student, College, Program
from studentorg.forms import OrganizationForm, OrgMemberForm, StudentForm, CollegeForm, ProgramForm
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from typing import Any
from django.db.models.query import QuerySet
from django.db.models import Q
from django.http import JsonResponse
from django.db.models import Count

def timeline_chart_data(request):
    data = (
        OrgMember.objects.values('date_joined')
        .annotate(member_count=Count('id'))
        .order_by('date_joined')
    )
    labels = [entry['date_joined'].strftime('%Y-%m-%d') for entry in data]
    counts = [entry['member_count'] for entry in data]

    response_data = {
        "labels": labels,  
        "datasets": [
            {
                "label": "New Members",
                "data": counts,  
                "backgroundColor": "rgba(54, 162, 235, 0.5)",  
                "borderColor": "rgba(54, 162, 235, 1)",
                "borderWidth": 1,
            }
        ],
    }

    return JsonResponse(response_data)

class ChartView(ListView):
    template_name = 'dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context

    def get_queryset(self, *args, **kwargs):
        pass

def popular_organization_by_college(request):
    # Aggregate membership counts grouped by college and organization
    data = (
        OrgMember.objects
        .values('organization__college__college_name', 'organization__name')
        .annotate(member_count=Count('id'))
        .order_by('organization__college__college_name', '-member_count')
    )

    # Organize data to find the most popular organization for each college
    college_data = {}
    for entry in data:
        college_name = entry['organization__college__college_name']
        organization_name = entry['organization__name']
        member_count = entry['member_count']

        if college_name not in college_data:
            college_data[college_name] = {
                "organization": organization_name,
                "members": member_count
            }

    # Prepare data for Chart.js
    labels = list(college_data.keys())  # Colleges
    counts = [info['members'] for info in college_data.values()]  # Membership counts
    organizations = [info['organization'] for info in college_data.values()]  # Organization names

    response_data = {
        "labels": labels,  # x-axis (colleges)
        "datasets": [
            {
                "label": "Most Popular Organization",
                "data": counts,  # y-axis (member counts)
                "backgroundColor": "rgba(75, 192, 192, 0.5)",  # Chart.js styling
                "borderColor": "rgba(75, 192, 192, 1)",
                "borderWidth": 1,
            }
        ],
        "organization_names": organizations,  # Custom info for tooltip or display
    }

    return JsonResponse(response_data)

def membership_distribution_by_organization(request):
    # Aggregate the count of members per organization
    data = (
        OrgMember.objects
        .values('organization__name')  # Group by organization name
        .annotate(member_count=Count('id'))  # Count members
        .order_by('-member_count')  # Sort by member count
    )

    # Prepare data for Chart.js
    labels = [entry['organization__name'] for entry in data]  # Organization names
    counts = [entry['member_count'] for entry in data]  # Membership counts

    response_data = {
        "labels": labels,  # Labels for the chart
        "datasets": [
            {
                "label": "Membership Distribution",
                "data": counts,  # Data for the chart
                "backgroundColor": [
                    "rgba(255, 99, 132, 0.5)",
                    "rgba(54, 162, 235, 0.5)",
                    "rgba(255, 206, 86, 0.5)",
                    "rgba(75, 192, 192, 0.5)",
                    "rgba(153, 102, 255, 0.5)",
                    "rgba(255, 159, 64, 0.5)",
                ],  # Colors for each section
                "borderColor": [
                    "rgba(255, 99, 132, 1)",
                    "rgba(54, 162, 235, 1)",
                    "rgba(255, 206, 86, 1)",
                    "rgba(75, 192, 192, 1)",
                    "rgba(153, 102, 255, 1)",
                    "rgba(255, 159, 64, 1)",
                ],
                "borderWidth": 1,
            }
        ],
    }

    return JsonResponse(response_data)


def bubble_chart_data(request):
    # Aggregate data by college
    data = (
        College.objects.annotate(
            org_count=Count('organization'),  # Number of organizations in the college
            member_count=Count('organization__orgmember'),  # Number of members across all orgs in the college
            student_count=Count('program__student')  # Total students in the college
        )
        .values('college_name', 'org_count', 'member_count', 'student_count')
    )

    # Prepare data for Chart.js
    chart_data = []
    for entry in data:
        chart_data.append({
            "x": entry['member_count'],  # x-axis: number of members
            "y": entry['org_count'],  # y-axis: number of organizations
            "r": entry['student_count'] / 10  # Bubble size: scaled total students
        })

    labels = [entry['college_name'] for entry in data]  # College names

    response_data = {
        "datasets": [
            {
                "label": "Colleges",
                "data": chart_data,
                "backgroundColor": "rgba(54, 162, 235, 0.5)",
                "borderColor": "rgba(54, 162, 235, 1)",
                "borderWidth": 1,
            }
        ],
        "labels": labels,  # For custom tooltip display
    }

    return JsonResponse(response_data)

def scatter_plot_data(request):
    # Aggregate data by college
    data = (
        College.objects.annotate(
            org_count=Count('organization'),  # Number of organizations in the college
            member_count=Count('organization__orgmember')  # Number of members across all organizations in the college
        )
        .values('college_name', 'org_count', 'member_count')
    )

    # Prepare data for Chart.js
    chart_data = []
    for entry in data:
        chart_data.append({
            "x": entry['org_count'],  # x-axis: number of organizations
            "y": entry['member_count'],  # y-axis: number of members
            "college": entry['college_name']  # College name for tooltips
        })

    response_data = {
        "datasets": [
            {
                "label": "Colleges",
                "data": chart_data,
                "backgroundColor": "rgba(75, 192, 192, 0.5)",
                "borderColor": "rgba(75, 192, 192, 1)",
                "borderWidth": 1,
            }
        ],
    }

    return JsonResponse(response_data)



class OrganizationDeleteView(DeleteView):
    model = Organization
    template_name = 'org_del.html'
    success_url = reverse_lazy('organization-list')

class OrgMemberDeleteView(DeleteView):
    model = OrgMember
    template_name = 'org_member_del.html'
    success_url = reverse_lazy('orgmember-list')

class StudentDeleteView(DeleteView):
    model = Student
    template_name = 'student_del.html'
    success_url = reverse_lazy('student-list')

class CollegeDeleteView(DeleteView):
    model = College
    template_name = 'college_del.html'
    success_url = reverse_lazy('college-list')

class ProgramDeleteView(DeleteView):
    model = Program
    template_name = 'program_del.html'
    success_url = reverse_lazy('program-list')


class OrganizationUpdateView(UpdateView):
    model = Organization
    form_class = OrganizationForm
    template_name = 'org_edit.html'
    success_url = reverse_lazy('organization-list')

class OrgMemberUpdateView(UpdateView):
    model = OrgMember
    form_class = OrgMemberForm
    template_name = 'org_member_edit.html'
    success_url = reverse_lazy('orgmember-list')

class StudentUpdateView(UpdateView):
    model = Student
    form_class = StudentForm
    template_name = 'student_edit.html'
    success_url = reverse_lazy('student-list')

class CollegeUpdateView(UpdateView):
    model = College
    form_class = CollegeForm
    template_name = 'college_edit.html'
    success_url = reverse_lazy('college-list')

class ProgramUpdateView(UpdateView):
    model = Program
    form_class = ProgramForm
    template_name = 'program_edit.html'
    success_url = reverse_lazy('program-list')


@method_decorator(login_required, name='dispatch')
class HomePageView(ListView):
    model = Organization
    context_object_name = 'home'
    template_name = "home.html"

class OrganizationList(ListView):
    model = Organization
    context_object_name = 'organization'
    template_name = 'org_list.html'
    paginate_by = 5

    def get_queryset(self, *args, **kwargs):
        qs = super(OrganizationList, self).get_queryset(*args, **kwargs)
        if self.request.GET.get("q") is not None:
            query = self.request.GET.get('q')
            qs = qs.filter(Q(name__icontains=query) | Q(description__icontains=query) | Q(college__college_name__icontains=query))
        return qs


class OrgMemberList(ListView):
    model = OrgMember
    context_object_name = 'orgmember'
    template_name = 'org_member_list.html'
    paginate_by = 5

    def get_queryset(self, *args, **kwargs):
        qs = super(OrgMemberList, self).get_queryset(*args, **kwargs)
        if self.request.GET.get("q") is not None:
            query = self.request.GET.get('q')
            qs = qs.filter(Q(student__firstname__icontains=query) | Q(student__lastname__icontains=query) | Q(student__middlename__icontains=query) | Q(organization__name__icontains=query) | Q(student__program__prog_name__icontains=query))
        return qs

class StudentList(ListView):
    model = Student
    context_object_name = 'student'
    template_name = 'student_list.html'
    paginate_by = 5

    def get_queryset(self, *args, **kwargs):
        qs = super(StudentList, self).get_queryset(*args, **kwargs)
        if self.request.GET.get("q") is not None:
            query = self.request.GET.get('q')
            qs = qs.filter(Q(student_id__icontains=query) | Q(firstname__icontains=query) | Q(lastname__icontains=query) | Q(middlename__icontains=query) | Q(program__college__college_name__icontains=query) | Q(program__prog_name__icontains=query))
        return qs

class CollegeList(ListView):
    model = College
    context_object_name = 'college'
    template_name = 'college_list.html'
    paginate_by = 5

    def get_queryset(self, *args, **kwargs):
        qs = super(CollegeList, self).get_queryset(*args, **kwargs)
        if self.request.GET.get("q") is not None:
            query = self.request.GET.get('q')
            qs = qs.filter(Q(college_name__icontains=query))
        return qs

class ProgramList(ListView):
    model = Program
    context_object_name = 'program'
    template_name = 'program_list.html'
    paginate_by = 5

    def get_queryset(self, *args, **kwargs):
        qs = super(ProgramList, self).get_queryset(*args, **kwargs)
        if self.request.GET.get("q") is not None:
            query = self.request.GET.get('q')
            qs = qs.filter(Q(prog_name__icontains=query) | Q(college__college_name__icontains=query))
        return qs

class OrganizationCreateView(CreateView):
    model = Organization
    form_class = OrganizationForm
    template_name = 'org_add.html'
    success_url = reverse_lazy('organization-list')

class OrgMemberCreateView(CreateView):
    model = OrgMember
    form_class = OrgMemberForm
    template_name = 'org_member_add.html'
    success_url = reverse_lazy('orgmember-list')

class StudentCreateView(CreateView):
    model = Student
    form_class = StudentForm
    template_name = 'student_add.html'
    success_url = reverse_lazy('student-list')

class CollegeCreateView(CreateView):
    model = College
    form_class = CollegeForm
    template_name = 'college_add.html'
    success_url = reverse_lazy('college-list')

class ProgramCreateView(CreateView):
    model = Program
    form_class = ProgramForm
    template_name = 'program_add.html'
    success_url = reverse_lazy('program-list')



# Create your views here.
