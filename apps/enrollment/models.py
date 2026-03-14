"""
Enrollment App - Models & Views
Student course enrollment management
NAC LMS Backend | Dhruv Sharma
"""

# ── models.py content ──────────────────────────────────────────────────────────

from django.db import models
from apps.authentication.models import User
from apps.courses.models import Course


class Enrollment(models.Model):
    student    = models.ForeignKey(User, on_delete=models.CASCADE, related_name='enrollments')
    course     = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='enrollments')
    enrolled_at= models.DateTimeField(auto_now_add=True)
    is_active  = models.BooleanField(default=True)  # False = unenrolled

    class Meta:
        db_table        = 'enrollments'
        unique_together = ('student', 'course')  # Prevent duplicate enrollments
        ordering        = ['-enrolled_at']

    def __str__(self):
        return f"{self.student.name} → {self.course.title}"


class Progress(models.Model):
    enrollment       = models.OneToOneField(Enrollment, on_delete=models.CASCADE, related_name='progress')
    completion_pct   = models.FloatField(default=0.0)   # 0.0 to 100.0
    modules_completed= models.PositiveIntegerField(default=0)
    last_accessed    = models.DateTimeField(auto_now=True)
    is_certified     = models.BooleanField(default=False)

    class Meta:
        db_table = 'progress'

    def check_certification(self):
        """Auto-certify when 100% complete."""
        if self.completion_pct >= 100.0 and not self.is_certified:
            self.is_certified = True
            self.save()
        return self.is_certified

    def __str__(self):
        return f"{self.enrollment} — {self.completion_pct}%"
