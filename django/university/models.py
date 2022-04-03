# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models


class Course(models.Model):
    course_id = models.IntegerField()
    faculty = models.ForeignKey('Faculty', models.DO_NOTHING)
    name = models.CharField(max_length=200)
    acronym = models.CharField(max_length=10)
    course_type = models.CharField(max_length=2)
    year = models.IntegerField()
    url = models.CharField(max_length=2000)
    plan_url = models.CharField(max_length=2000)
    last_updated = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'course'
        unique_together = (('course_id', 'faculty', 'year'),)


class CourseUnit(models.Model):
    course_unit_id = models.IntegerField()
    course = models.ForeignKey(Course, models.DO_NOTHING)
    name = models.CharField(max_length=200)
    acronym = models.CharField(max_length=16)
    url = models.CharField(max_length=2000)
    course_year = models.IntegerField()
    semester = models.IntegerField()
    year = models.SmallIntegerField()
    schedule_url = models.CharField(max_length=2000, blank=True, null=True)
    last_updated = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'course_unit'
        unique_together = (('course_unit_id', 'course', 'year', 'semester'),)


class DjangoMigrations(models.Model):
    id = models.BigAutoField(primary_key=True)
    app = models.CharField(max_length=255)
    name = models.CharField(max_length=255)
    applied = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'django_migrations'


class Faculty(models.Model):
    acronym = models.CharField(unique=True, max_length=10, blank=True, null=True)
    name = models.TextField(blank=True, null=True)
    last_updated = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'faculty'


class Schedule(models.Model):
    day = models.PositiveIntegerField()
    duration = models.DecimalField(max_digits=3, decimal_places=1)
    start_time = models.DecimalField(max_digits=3, decimal_places=1)
    location = models.CharField(max_length=16)
    lesson_type = models.CharField(max_length=3)
    teacher_acronym = models.CharField(max_length=16)
    course_unit = models.ForeignKey(CourseUnit, models.DO_NOTHING)
    last_updated = models.DateTimeField()
    class_name = models.CharField(max_length=16)
    composed_class_name = models.CharField(max_length=16, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'schedule'
