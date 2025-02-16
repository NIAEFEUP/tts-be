# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models

class Course(models.Model):
    id = models.IntegerField(primary_key=True)
    faculty = models.ForeignKey('Faculty', models.DO_NOTHING)
    name = models.CharField(max_length=200)
    acronym = models.CharField(max_length=10)
    course_type = models.CharField(max_length=2)
    year = models.IntegerField()
    url = models.CharField(max_length=2000)
    plan_url = models.CharField(max_length=2000)
    last_updated = models.DateTimeField()

    class Meta:
        managed = True
        db_table = 'course'
        unique_together = (('id', 'faculty', 'year'),)

class CourseUnit(models.Model):
    id = models.IntegerField(primary_key=True, null=False)
    course = models.ForeignKey(Course, models.DO_NOTHING)
    name = models.CharField(max_length=200, null=False)
    acronym = models.CharField(max_length=16, null=False)
    url = models.CharField(max_length=2000, null=False)
    semester = models.IntegerField(null=False)
    year = models.SmallIntegerField(null=False)
    schedule_url = models.CharField(max_length=2000, blank=True, null=True, default="")
    last_updated = models.DateTimeField(null=False)
    hash = models.CharField(max_length=64, blank=True, null=True, default="")

    class Meta:
        managed = True
        db_table = 'course_unit'
        unique_together = (('id', 'course', 'year', 'semester'),)

class CourseMetadata(models.Model):
    course = models.OneToOneField(Course, models.DO_NOTHING, primary_key=True)  # The composite primary key (course_id, course_unit_id, course_unit_year) found, that is not supported. The first column is selected.
    course_unit = models.ForeignKey('CourseUnit', models.DO_NOTHING)
    course_unit_year = models.IntegerField()
    ects = models.FloatField()

    class Meta:
        managed = True
        db_table = 'course_metadata'
        unique_together = (('course', 'course_unit', 'course_unit_year'), ('course', 'course_unit', 'course_unit_year'),)

class Class(models.Model):
    id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=31, null=False)
    course_unit = models.ForeignKey('CourseUnit', models.DO_NOTHING)
    last_updated = models.DateTimeField()

    class Meta:
        managed = True
        db_table = 'class'
        unique_together = (('name', 'course_unit'),)

class CourseUnitEnrollmentOptions(models.Model):
    course_unit = models.ForeignKey(CourseUnit, models.DO_NOTHING)
    enrolling = models.BooleanField(blank=True, null=True)
    course_unit_enrollment = models.ForeignKey('CourseUnitEnrollments', models.DO_NOTHING)
    date = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'course_unit_enrollment_options'


class CourseUnitEnrollments(models.Model):
    user_nmec = models.CharField(max_length=32)
    accepted = models.BooleanField(blank=True, null=True)
    admin_state = models.CharField(max_length=32)
    date = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'course_unit_enrollments'


class DirectExchange(models.Model):
    issuer_name = models.CharField(max_length=256)
    issuer_nmec = models.CharField(max_length=32)
    accepted = models.BooleanField()
    canceled = models.BooleanField(blank=True, null=True)
    date = models.DateTimeField(blank=True, null=True)
    admin_state = models.CharField(max_length=32)
    marketplace_exchange = models.ForeignKey('MarketplaceExchange', models.DO_NOTHING, db_column='marketplace_exchange', blank=True, null=True)
    hash = models.CharField(unique=True, max_length=64, blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'direct_exchange'


class DirectExchangeParticipants(models.Model):
    participant_name = models.CharField(max_length=256)
    participant_nmec = models.CharField(max_length=32)
    class_participant_goes_from = models.CharField(max_length=16)
    class_participant_goes_to = models.CharField(max_length=16)
    course_unit = models.CharField(max_length=64)
    course_unit_id = models.CharField(max_length=16)
    direct_exchange = models.ForeignKey(DirectExchange, models.DO_NOTHING, db_column='direct_exchange')
    accepted = models.BooleanField()
    date = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'direct_exchange_participants'

class ExchangeAdmin(models.Model):
    username = models.CharField(unique=True, max_length=32)

    class Meta:
        managed = True
        db_table = 'exchange_admin'

class ExchangeAdminCourseUnits(models.Model):
    exchange_admin = models.ForeignKey(ExchangeAdmin, models.DO_NOTHING)
    course_unit = models.ForeignKey(CourseUnit, models.DO_NOTHING)

    class Meta:
        managed = True
        db_table = 'exchange_admin_course_units'


class ExchangeAdminCourses(models.Model):
    exchange_admin = models.ForeignKey(ExchangeAdmin, models.DO_NOTHING)
    course = models.ForeignKey(Course, models.DO_NOTHING)

    class Meta:
        managed = True
        db_table = 'exchange_admin_courses'


class ExchangeExpirations(models.Model):
    course_unit = models.ForeignKey(CourseUnit, models.DO_NOTHING)
    active_date = models.DateTimeField()
    end_date = models.DateTimeField()

    class Meta:
        managed = True
        db_table = 'exchange_expirations'


class ExchangeUrgentRequestOptions(models.Model):
    course_unit = models.ForeignKey(CourseUnit, models.DO_NOTHING)
    class_user_goes_from = models.CharField(max_length=16)
    class_user_goes_to = models.CharField(max_length=16)
    exchange_urgent_request = models.ForeignKey('ExchangeUrgentRequests', models.DO_NOTHING)
    date = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'exchange_urgent_request_options'


class ExchangeUrgentRequests(models.Model):
    user_nmec = models.CharField(max_length=32)
    message = models.CharField(max_length=2048)
    accepted = models.BooleanField(blank=True, null=True)
    admin_state = models.CharField(max_length=32)
    date = models.DateTimeField(blank=True, null=True)
    hash = models.CharField(unique=True, max_length=64, blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'exchange_urgent_requests'


class Faculty(models.Model):
    acronym = models.CharField(primary_key=True, max_length=10)
    name = models.TextField(blank=True, null=True)
    last_updated = models.DateTimeField()

    class Meta:
        managed = True
        db_table = 'faculty'


class Info(models.Model):
    date = models.DateTimeField(primary_key=True)

    class Meta:
        managed = True
        db_table = 'info'


class MarketplaceExchange(models.Model):
    issuer_name = models.CharField(max_length=256)
    issuer_nmec = models.CharField(max_length=32)
    accepted = models.BooleanField()
    canceled = models.BooleanField(blank=True, null=True)
    date = models.DateTimeField(blank=True, null=True)
    hash = models.CharField(unique=True, max_length=64, blank=True, null=True)
    admin_state = models.CharField(max_length=32)

    class Meta:
        managed = True
        db_table = 'marketplace_exchange'


class MarketplaceExchangeClass(models.Model):
    marketplace_exchange = models.ForeignKey(MarketplaceExchange, models.DO_NOTHING, db_column='marketplace_exchange')
    course_unit_name = models.CharField(max_length=256)
    course_unit_acronym = models.CharField(max_length=256)
    course_unit_id = models.CharField(max_length=256)
    class_issuer_goes_from = models.CharField(max_length=16)
    class_issuer_goes_to = models.CharField(max_length=16)
    date = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'marketplace_exchange_class'


class Professor(models.Model):
    id = models.IntegerField(primary_key=True)
    professor_acronym = models.CharField(max_length=32, blank=True, null=True)
    professor_name = models.CharField(max_length=100, blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'professor'


class Slot(models.Model):
    id = models.IntegerField(primary_key=True)
    lesson_type = models.CharField(max_length=3)
    day = models.IntegerField()
    start_time = models.DecimalField(max_digits=3, decimal_places=1)
    duration = models.DecimalField(max_digits=3, decimal_places=1)
    location = models.CharField(max_length=31)
    is_composed = models.IntegerField()
    professor_id = models.IntegerField(blank=True, null=True)
    last_updated = models.DateTimeField()

    class Meta:
        managed = True
        db_table = 'slot'


class SlotClass(models.Model):
    slot = models.OneToOneField(Slot, models.DO_NOTHING, primary_key=True)  # The composite primary key (slot_id, class_id) found, that is not supported. The first column is selected.
    class_field = models.ForeignKey(Class, models.DO_NOTHING, db_column='class_id')  # Field renamed because it was a Python reserved word.

    class Meta:
        managed = True
        db_table = 'slot_class'
        unique_together = (('slot', 'class_field'), ('slot', 'class_field'),)


class SlotProfessor(models.Model):
    slot = models.OneToOneField(Slot, models.DO_NOTHING, primary_key=True)  # The composite primary key (slot_id, professor_id) found, that is not supported. The first column is selected.
    professor = models.ForeignKey(Professor, models.DO_NOTHING)

    class Meta:
        managed = True
        db_table = 'slot_professor'
        unique_together = (('slot', 'professor'), ('slot', 'professor'),)


class StudentCourseMetadata(models.Model):
    nmec = models.CharField(max_length=255)
    fest_id = models.IntegerField()
    course = models.ForeignKey(Course, models.DO_NOTHING)

    class Meta:
        managed = True
        db_table = 'student_course_metadata'


class UserCourseUnits(models.Model):
    user_nmec = models.CharField(max_length=32)
    course_unit = models.ForeignKey(CourseUnit, models.DO_NOTHING)
    class_field = models.ForeignKey(Class, models.DO_NOTHING, db_column='class_id')  # Field renamed because it was a Python reserved word.

    class Meta:
        managed = True
        db_table = 'user_course_units'
