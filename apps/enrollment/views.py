"""
Enrollment App - Views
Enroll, unenroll, list enrolled courses, check status, update progress
NAC LMS Backend | Dhruv Sharma
"""

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated

from apps.courses.models import Course
from .models import Enrollment, Progress


class EnrollView(APIView):
    """
    POST /api/enrollment/enroll/
    Enroll the logged-in student in a course.
    Prevents duplicate enrollments automatically.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        course_id = request.data.get('course_id')

        # Validate course exists
        try:
            course = Course.objects.get(pk=course_id, is_active=True)
        except Course.DoesNotExist:
            return Response({
                'success': False,
                'message': 'Course not found or no longer available.'
            }, status=status.HTTP_404_NOT_FOUND)

        # Check if already enrolled
        existing = Enrollment.objects.filter(
            student=request.user,
            course=course
        ).first()

        if existing:
            if existing.is_active:
                return Response({
                    'success': False,
                    'message': f'You are already enrolled in "{course.title}".'
                }, status=status.HTTP_400_BAD_REQUEST)
            else:
                # Re-enroll (previously unenrolled)
                existing.is_active = True
                existing.save()
                enrollment = existing
        else:
            # Fresh enrollment
            enrollment = Enrollment.objects.create(
                student=request.user,
                course=course
            )
            # Create a progress tracker for this enrollment
            Progress.objects.create(enrollment=enrollment)

        return Response({
            'success':     True,
            'message':     f'Successfully enrolled in "{course.title}"!',
            'enrollment_id': enrollment.id,
            'enrolled_at': enrollment.enrolled_at,
        }, status=status.HTTP_201_CREATED)


class UnenrollView(APIView):
    """
    DELETE /api/enrollment/unenroll/<course_id>/
    Remove a student from a course (soft delete).
    """
    permission_classes = [IsAuthenticated]

    def delete(self, request, course_id):
        try:
            enrollment = Enrollment.objects.get(
                student=request.user,
                course_id=course_id,
                is_active=True
            )
        except Enrollment.DoesNotExist:
            return Response({
                'success': False,
                'message': 'You are not enrolled in this course.'
            }, status=status.HTTP_404_NOT_FOUND)

        enrollment.is_active = False
        enrollment.save()

        return Response({
            'success': True,
            'message': 'Successfully unenrolled from the course.'
        })


class MyCoursesView(APIView):
    """
    GET /api/enrollment/my-courses/
    List all courses the logged-in student is enrolled in.
    Includes progress info.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        enrollments = Enrollment.objects.filter(
            student=request.user,
            is_active=True
        ).select_related('course', 'progress')

        data = []
        for e in enrollments:
            progress = getattr(e, 'progress', None)
            data.append({
                'enrollment_id':  e.id,
                'enrolled_at':    e.enrolled_at,
                'course': {
                    'id':       e.course.id,
                    'title':    e.course.title,
                    'category': e.course.category,
                    'level':    e.course.level,
                    'duration': e.course.duration_days,
                },
                'progress': {
                    'completion_pct':    progress.completion_pct if progress else 0,
                    'modules_completed': progress.modules_completed if progress else 0,
                    'is_certified':      progress.is_certified if progress else False,
                }
            })

        return Response({
            'success': True,
            'total':   len(data),
            'courses': data
        })


class EnrollmentStatusView(APIView):
    """
    GET /api/enrollment/status/<course_id>/
    Check if current user is enrolled in a specific course.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request, course_id):
        enrollment = Enrollment.objects.filter(
            student=request.user,
            course_id=course_id,
            is_active=True
        ).first()

        return Response({
            'success':     True,
            'is_enrolled': enrollment is not None,
            'enrolled_at': enrollment.enrolled_at if enrollment else None,
        })


class UpdateProgressView(APIView):
    """
    PUT /api/enrollment/progress/<course_id>/
    Update a student's progress in a course.
    Auto-certifies when completion reaches 100%.
    """
    permission_classes = [IsAuthenticated]

    def put(self, request, course_id):
        try:
            enrollment = Enrollment.objects.get(
                student=request.user,
                course_id=course_id,
                is_active=True
            )
            progress = enrollment.progress
        except (Enrollment.DoesNotExist, Progress.DoesNotExist):
            return Response({
                'success': False,
                'message': 'Enrollment or progress record not found.'
            }, status=status.HTTP_404_NOT_FOUND)

        completion = request.data.get('completion_pct', progress.completion_pct)
        modules    = request.data.get('modules_completed', progress.modules_completed)

        # Clamp between 0 and 100
        progress.completion_pct    = max(0.0, min(100.0, float(completion)))
        progress.modules_completed = int(modules)
        progress.save()

        # Auto-check certification eligibility
        is_certified = progress.check_certification()

        return Response({
            'success':          True,
            'completion_pct':   progress.completion_pct,
            'modules_completed':progress.modules_completed,
            'is_certified':     is_certified,
            'message':          '🎉 Congratulations! Certificate unlocked!' if is_certified else 'Progress updated.'
        })
