"""
Courses App - Views
Course listing, detail, create, update, delete
Admin-only write access | Students get read-only
NAC LMS Backend | Dhruv Sharma
"""

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, AllowAny

from .models import Course
from .serializers import CourseSerializer, CourseDetailSerializer


class IsAdminUser(IsAuthenticated):
    """Custom permission — only admin role users can proceed."""
    def has_permission(self, request, view):
        return super().has_permission(request, view) and request.user.role == 'admin'


class CourseListView(APIView):
    """
    GET  /api/courses/       - List all active courses (paginated, public)
    POST /api/courses/       - Create new course (Admin only)
    """

    def get_permissions(self):
        if self.request.method == 'POST':
            return [IsAdminUser()]
        return [AllowAny()]

    def get(self, request):
        courses = Course.objects.filter(is_active=True)

        # Optional filters via query params
        category = request.query_params.get('category')
        level    = request.query_params.get('level')
        if category:
            courses = courses.filter(category=category)
        if level:
            courses = courses.filter(level=level)

        # Manual pagination
        page      = int(request.query_params.get('page', 1))
        page_size = 10
        start     = (page - 1) * page_size
        end       = start + page_size
        total     = courses.count()

        serializer = CourseSerializer(courses[start:end], many=True)
        return Response({
            'success':  True,
            'total':    total,
            'page':     page,
            'pages':    (total + page_size - 1) // page_size,
            'results':  serializer.data,
        })

    def post(self, request):
        serializer = CourseSerializer(data=request.data)
        if not serializer.is_valid():
            return Response({
                'success': False,
                'errors': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)

        course = serializer.save(created_by=request.user)
        return Response({
            'success': True,
            'message': 'Course created successfully.',
            'course':  CourseSerializer(course).data
        }, status=status.HTTP_201_CREATED)


class CourseDetailView(APIView):
    """
    GET    /api/courses/<id>/  - Course detail (public)
    PUT    /api/courses/<id>/  - Update course (Admin only)
    DELETE /api/courses/<id>/  - Delete course (Admin only)
    """

    def get_permissions(self):
        if self.request.method == 'GET':
            return [AllowAny()]
        return [IsAdminUser()]

    def get_object(self, pk):
        try:
            return Course.objects.get(pk=pk, is_active=True)
        except Course.DoesNotExist:
            return None

    def get(self, request, pk):
        course = self.get_object(pk)
        if not course:
            return Response({
                'success': False,
                'message': 'Course not found.'
            }, status=status.HTTP_404_NOT_FOUND)

        serializer = CourseDetailSerializer(course)
        return Response({'success': True, 'course': serializer.data})

    def put(self, request, pk):
        course = self.get_object(pk)
        if not course:
            return Response({'success': False, 'message': 'Course not found.'}, status=404)

        serializer = CourseSerializer(course, data=request.data, partial=True)
        if not serializer.is_valid():
            return Response({'success': False, 'errors': serializer.errors}, status=400)

        serializer.save()
        return Response({'success': True, 'message': 'Course updated.', 'course': serializer.data})

    def delete(self, request, pk):
        course = self.get_object(pk)
        if not course:
            return Response({'success': False, 'message': 'Course not found.'}, status=404)

        course.is_active = False  # Soft delete — never hard delete
        course.save()
        return Response({'success': True, 'message': 'Course removed successfully.'})
