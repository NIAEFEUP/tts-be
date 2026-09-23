from unittest.mock import patch

from django.core.cache import cache
from django.test import TestCase
from django.utils import timezone

from university.controllers.ClassController import ClassController
from university.controllers.SigarraController import SigarraController, SigarraResponse
from university.models import Class, Course, CourseUnit, Faculty, Slot, SlotClass

COURSE_UNIT_ID = 100


def calendarios_lesson(lesson_id, class_name="1LEIC01"):
    """A lesson in the shape the SIGARRA calendarios API returns."""
    return {
        "id": lesson_id,
        "week_days": ["Segunda-feira"],
        "hour_start": "09:00:00",
        "hour_end": "11:00:00",
        "ucs": [{"sigarra_id": COURSE_UNIT_ID}],
        "typology": {"acronym": "TP"},
        "rooms": [{"acronym": "B001"}],
        "classes": [{"acronym": class_name}],
        "persons": [],
    }


class ClassScheduleSyncTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        now = timezone.now()
        faculty = Faculty.objects.create(acronym="feup", name="FEUP", last_updated=now)
        course = Course.objects.create(
            id=1, faculty=faculty, name="L.EIC", acronym="L.EIC", course_type="L",
            year=2025, url="", plan_url="", last_updated=now,
        )
        course_unit = CourseUnit.objects.create(
            id=COURSE_UNIT_ID, course=course, name="Programming", acronym="PROG", url="",
            semester=1, year=1, last_updated=now,
        )
        klass = Class.objects.create(name="1LEIC01", course_unit=course_unit, last_updated=now)
        slot = Slot.objects.create(
            id=5000, lesson_type="TP", day=0, start_time=9, duration=2, location="B001",
            is_composed=0, last_updated=now,
        )
        SlotClass.objects.create(slot=slot, class_field=klass)

    def setUp(self):
        cache.clear()
        self.addCleanup(cache.clear)
        patch.object(SigarraController, "login").start()
        self.addCleanup(patch.stopall)

    def sigarra_returns(self, lessons):
        return patch.object(
            SigarraController, "get_course_schedule", return_value=SigarraResponse(lessons, 200),
        ).start()

    def slot_ids(self, classes):
        return {slot["id"] for class_ in classes for slot in class_["slots"]}

    def test_empty_sigarra_schedule_keeps_existing_timetable(self):
        self.sigarra_returns([])

        classes = ClassController.get_classes(COURSE_UNIT_ID)

        self.assertEqual(self.slot_ids(classes), {5000})
        self.assertTrue(Slot.objects.filter(id=5000).exists())

    def test_empty_sigarra_schedule_is_cached(self):
        get_course_schedule = self.sigarra_returns([])

        ClassController.get_classes(COURSE_UNIT_ID)
        ClassController.get_classes(COURSE_UNIT_ID)

        self.assertEqual(get_course_schedule.call_count, 1)

    def test_lessons_no_longer_in_sigarra_are_still_removed(self):
        self.sigarra_returns([calendarios_lesson(5001)])

        classes = ClassController.get_classes(COURSE_UNIT_ID)

        self.assertEqual(self.slot_ids(classes), {5001})
        self.assertFalse(Slot.objects.filter(id=5000).exists())

    def test_failed_sigarra_request_keeps_existing_timetable_and_is_retried(self):
        get_course_schedule = patch.object(
            SigarraController, "get_course_schedule", return_value=SigarraResponse(None, 500),
        ).start()

        classes = ClassController.get_classes(COURSE_UNIT_ID)
        ClassController.get_classes(COURSE_UNIT_ID)

        self.assertEqual(self.slot_ids(classes), {5000})
        self.assertEqual(get_course_schedule.call_count, 2)
