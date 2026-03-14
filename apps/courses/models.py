"""
Courses App - Models
Course catalog for NAC LMS
NAC LMS Backend | Dhruv Sharma
"""

from django.db import models
from apps.authentication.models import User


class Course(models.Model):
    CATEGORY_CHOICES = [
        ('fullstack',   'Full Stack Development'),
        ('data',        'Data Analytics'),
        ('marketing',   'Digital Marketing'),
        ('hr',          'Human Resource'),
        ('sales',       'Sales'),
        ('product',     'Product Management'),
        ('business',    'Business Analysis'),
    ]
    LEVEL_CHOICES = [
        ('beginner',     'Beginner'),
        ('intermediate', 'Intermediate'),
        ('advanced',     'Advanced'),
    ]

    title         = models.CharField(max_length=200)
    description   = models.TextField()
    category      = models.CharField(max_length=50, choices=CATEGORY_CHOICES)
    level         = models.CharField(max_length=20, choices=LEVEL_CHOICES, default='beginner')
    duration_days = models.PositiveIntegerField(help_text='Duration in days')
    price         = models.DecimalField(max_digits=8, decimal_places=2, default=0.00)
    instructor    = models.CharField(max_length=150)
    is_active     = models.BooleanField(default=True)
    created_by    = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='courses_created')
    created_at    = models.DateTimeField(auto_now_add=True)
    updated_at    = models.DateTimeField(auto_now=True)

    class Meta:
        db_table  = 'courses'
        ordering  = ['-created_at']

    def __str__(self):
        return self.title

    @property
    def enrollment_count(self):
        return self.enrollments.filter(is_active=True).count()
