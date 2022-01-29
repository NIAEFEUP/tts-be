from django.db import models


class Course(models.Model):
    id = models.IntegerField(primary_key=True)
    course_id = models.IntegerField(unique=True)
    acronym = models.CharField(max_length=10)
    name = models.CharField(max_length=200)
    course_type = models.CharField(max_length=2)
    url = models.CharField(max_length=2000)
    plan_url = models.CharField(max_length=2000)
    plan_id = models.IntegerField()
    year = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'course'


class CourseFaculty(models.Model):
    faculty = models.ForeignKey('Faculty', models.DO_NOTHING)
    course = models.ForeignKey(Course, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'course_faculty'


class Faculty(models.Model):
    id = models.IntegerField(primary_key=True)
    acronym = models.CharField(unique=True, max_length=10)
    name = models.CharField(max_length=200)

    class Meta:
        managed = False
        db_table = 'faculty'
