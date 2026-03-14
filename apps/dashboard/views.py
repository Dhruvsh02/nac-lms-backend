"""
Dashboard App - Views
Student + Admin analytics and summary endpoints
NAC LMS Backend | Dhruv Sharma
"""

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Avg, Count

from apps.enrollment.models import Enrollment, Progress
from apps.courses.models import Course
from apps.authentication.models import User


class StudentDashboardView(APIView):
    """
    GET /api/dashboard/student/
    Returns the logged-in student's full learning summary.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user

        enrollments = Enrollment.objects.filter(
            student=user, is_active=True
        ).select_related('course', 'progress')

        total_enrolled  = enrollments.count()
        completed       = 0
        certified       = 0
        avg_completion  = 0.0
        courses_data    = []

        for e in enrollments:
            p = getattr(e, 'progress', None)
            pct = p.completion_pct if p else 0.0
            if pct >= 100:
                completed += 1
            if p and p.is_certified:
                certified += 1
            avg_completion += pct
            courses_data.append({
                'course_title':      e.course.title,
                'category':          e.course.category,
                'completion_pct':    pct,
                'modules_completed': p.modules_completed if p else 0,
                'is_certified':      p.is_certified if p else False,
                'last_accessed':     p.last_accessed if p else None,
            })

        if total_enrolled > 0:
            avg_completion = round(avg_completion / total_enrolled, 1)

        return Response({
            'success': True,
            'student': {
                'name':            user.name,
                'email':           user.email,
            },
            'summary': {
                'total_enrolled':  total_enrolled,
                'completed':       completed,
                'in_progress':     total_enrolled - completed,
                'certified':       certified,
                'avg_completion':  avg_completion,
            },
            'courses': courses_data
        })


class AdminDashboardView(APIView):
    """
    GET /api/dashboard/admin/
    Platform-wide stats. Admin role required.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if request.user.role != 'admin':
            return Response({
                'success': False,
                'message': 'Admin access required.'
            }, status=403)

        total_students   = User.objects.filter(role='student', is_active=True).count()
        total_courses    = Course.objects.filter(is_active=True).count()
        total_enrollments= Enrollment.objects.filter(is_active=True).count()
        certified_count  = Progress.objects.filter(is_certified=True).count()

        # Top 5 most enrolled courses
        top_courses = (
            Course.objects
            .filter(is_active=True)
            .annotate(enroll_count=Count('enrollments'))
            .order_by('-enroll_count')[:5]
        )
        top_courses_data = [
            {'title': c.title, 'category': c.category, 'enrollments': c.enroll_count}
            for c in top_courses
        ]

        return Response({
            'success': True,
            'platform_stats': {
                'total_students':    total_students,
                'total_courses':     total_courses,
                'total_enrollments': total_enrollments,
                'certificates_issued': certified_count,
            },
            'top_courses': top_courses_data,
        })
