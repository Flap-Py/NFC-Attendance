# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from jsonfield import JSONField

from django.db import models
from django.contrib.auth.models import AbstractUser


# Create your models here.
class NFCUser(AbstractUser):
    """
    User model for authentication.
    name:      Name of the user
    username:  Username of the user
    password:  Password of the user
    type:      Admin/Faculty/Student
    email:     Email id of the user
    lastClass: Json storing last class timings of all courses
    """
    # objects = UserManager()
    name = models.CharField(max_length=20)
    userTypes = (
        ('Faculty', 'Faculty'), 
        ('Student', 'Student'),
        ('Admin', 'Admin'))
    type = models.CharField(max_length=10, choices=userTypes)
    year = models.CharField(
        max_length=1,
        choices=(('1', '1'), ('2', '2'), ('3', '3'), ('4', '4'))
        )
    branch=models.CharField(
        max_length=3,
        choices=(('CCE', 'CCE'), ('CSE', 'CSE'), ('ECE', 'ECE'), ('MME', 'MME'))
        )
    clist = JSONField()
    lastClass = JSONField()

class LectureSlot(models.Model):
    """
    Model       for course lecture time slot.
    date:       Date of the lecture
    time:       Time of the lecture
    lt:         Lecture hall number for the lecture
    courseCode: Unique course code
    """
    ltnum = ((1, 1), (2, 2), (3, 3), (4, 4))
    date = models.DateField()
    time = models.TimeField()
    lt = models.CharField(max_length=4, choices=ltnum)
    courseCode = models.CharField(max_length=10)

class Course(models.Model):
    """
    The object for course.
    courseCode: The course code for the course
    numClasses: The number of classes of the course (default=0)
    """
    year = models.CharField(
        max_length=1,
        choices=(('1', '1'), ('2', '2'), ('3', '3'), ('4', '4'), ('5', 'Other'))
        )
    branch=models.CharField(
        max_length=3,
        choices=(('CCE', 'CCE'), ('CSE', 'CSE'), ('ECE', 'ECE'), ('MME', 'MME'))
        )
    courseCode = models.CharField(max_length=10)
    numClasses = models.IntegerField(default=0)
    studentList = JSONField()