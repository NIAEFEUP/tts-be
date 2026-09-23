from datetime import timedelta
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.utils import timezone

from exchange.models import DirectExchange, DirectExchangeParticipants, ExchangeAdmin
from university.controllers.ExchangeValidationController import ExchangeValidationController
from university.controllers.SigarraController import SigarraController, SigarraResponse
from university.models import Class, Course, CourseUnit, Faculty

COURSE_UNIT_ID = 100
STUDENT_A = "202400001"
STUDENT_B = "202400002"


def lesson(class_name, day=2):
    """A practical lesson in the shape SIGARRA's schedule endpoints return."""
    return {
        "turma_sigla": class_name,
        "turmas": [{"turma_sigla": class_name}],
        "ocorrencia_id": COURSE_UNIT_ID,
        "ucurr_sigla": "PROG",
        "tipo": "TP",
        "dia": day,
        "hora_inicio": 9 * 3600,
        "aula_duracao": 2,
    }


class FakeSigarra:
    """Stands in for SIGARRA: each student's official schedule, plus every class's lessons."""

    def __init__(self, student_classes):
        self.student_classes = student_classes

    def get_student_schedule(self, nmec):
        return SigarraResponse([lesson(self.student_classes[str(nmec)])], 200)

    def get_class_schedule(self, course_unit_id, class_name):
        # Fresh lists on every call: callers mutate the result
        return SigarraResponse(([lesson(class_name)], []), 200)


class DirectExchangeValidationTest(TestCase):
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
        for name in ("1LEIC01", "1LEIC02", "1LEIC03"):
            Class.objects.create(name=name, course_unit=course_unit, last_updated=now)

        User = get_user_model()
        cls.admin = User.objects.create(username="admin")
        ExchangeAdmin.objects.create(username="admin")

    def setUp(self):
        self.client.force_login(self.admin)
        patch.object(SigarraController, "login").start()
        self.addCleanup(patch.stopall)

    def use_sigarra(self, student_classes):
        fake = FakeSigarra(student_classes)
        patch.object(SigarraController, "get_student_schedule", side_effect=fake.get_student_schedule).start()
        patch.object(SigarraController, "get_class_schedule", side_effect=fake.get_class_schedule).start()

    def create_exchange(self, moves, accepted, date=None):
        """moves: list of (nmec, goes_from, goes_to)"""
        exchange = DirectExchange.objects.create(
            issuer_name="Student", issuer_nmec=moves[0][0], accepted=accepted,
            date=date or timezone.now(),
        )
        for nmec, goes_from, goes_to in moves:
            DirectExchangeParticipants.objects.create(
                participant_name="Student", participant_nmec=nmec,
                class_participant_goes_from=goes_from, class_participant_goes_to=goes_to,
                course_unit="PROG", course_unit_id=str(COURSE_UNIT_ID),
                direct_exchange=exchange, accepted=accepted,
            )
        return exchange

    def validate(self, exchange):
        return self.client.get(f"/exchange/direct/validate/{exchange.id}")

    def test_accepted_exchange_is_reported_valid(self):
        # SIGARRA still has the students in their original classes: the exchange is
        # accepted in TTS but has not been applied in SIGARRA yet.
        self.use_sigarra({STUDENT_A: "1LEIC01", STUDENT_B: "1LEIC02"})
        exchange = self.create_exchange(
            [(STUDENT_A, "1LEIC01", "1LEIC02"), (STUDENT_B, "1LEIC02", "1LEIC01")], accepted=True,
        )

        response = self.validate(exchange)

        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()["valid"])
        exchange.refresh_from_db()
        self.assertTrue(exchange.accepted)
        self.assertFalse(exchange.canceled)

    def test_valid_response_returns_the_new_last_validated(self):
        self.use_sigarra({STUDENT_A: "1LEIC01", STUDENT_B: "1LEIC02"})
        exchange = self.create_exchange(
            [(STUDENT_A, "1LEIC01", "1LEIC02"), (STUDENT_B, "1LEIC02", "1LEIC01")], accepted=True,
        )
        DirectExchange.objects.filter(id=exchange.id).update(last_validated=timezone.now() - timedelta(days=3))

        response = self.validate(exchange)

        exchange.refresh_from_db()
        self.assertEqual(response.json()["last_validated"], exchange.last_validated.isoformat())
        self.assertGreater(exchange.last_validated, timezone.now() - timedelta(minutes=1))

    def test_invalid_exchange_is_reported_but_not_canceled(self):
        # Student A is no longer in the class they would exchange from
        self.use_sigarra({STUDENT_A: "1LEIC03", STUDENT_B: "1LEIC02"})
        exchange = self.create_exchange(
            [(STUDENT_A, "1LEIC01", "1LEIC02"), (STUDENT_B, "1LEIC02", "1LEIC01")], accepted=True,
        )

        response = self.validate(exchange)

        self.assertEqual(response.status_code, 400)
        self.assertFalse(response.json()["valid"])
        exchange.refresh_from_db()
        self.assertTrue(exchange.accepted)
        self.assertFalse(exchange.canceled)

    def test_other_accepted_exchanges_are_still_replayed(self):
        # A already accepted 1LEIC01 -> 1LEIC03, so a pending 1LEIC01 -> 1LEIC02 is invalid
        self.use_sigarra({STUDENT_A: "1LEIC01", STUDENT_B: "1LEIC02"})
        self.create_exchange(
            [(STUDENT_A, "1LEIC01", "1LEIC03")], accepted=True,
            date=timezone.now() - timedelta(days=1),
        )
        pending = self.create_exchange(
            [(STUDENT_A, "1LEIC01", "1LEIC02"), (STUDENT_B, "1LEIC02", "1LEIC01")], accepted=False,
        )

        self.assertFalse(ExchangeValidationController().validate_direct_exchange(pending.id).status)

    def test_pending_exchange_without_conflicts_is_valid(self):
        self.use_sigarra({STUDENT_A: "1LEIC01", STUDENT_B: "1LEIC02"})
        pending = self.create_exchange(
            [(STUDENT_A, "1LEIC01", "1LEIC02"), (STUDENT_B, "1LEIC02", "1LEIC01")], accepted=False,
        )

        self.assertTrue(ExchangeValidationController().validate_direct_exchange(pending.id).status)
