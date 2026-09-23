from django.contrib.auth import get_user_model
from django.test import TestCase
from django.utils import timezone

from exchange.models import (
    DirectExchange,
    DirectExchangeParticipants,
    ExchangeAdmin,
    ExchangeUrgentRequestOptions,
    ExchangeUrgentRequests,
    UserCourseUnits,
)
from university.models import Class, Course, CourseUnit, Faculty


class AdminExchangeRequestAcceptViewTest(TestCase):
    ISSUER_NMEC = "202400001"

    @classmethod
    def setUpTestData(cls):
        now = timezone.now()
        faculty = Faculty.objects.create(acronym="feup", name="FEUP", last_updated=now)
        course = Course.objects.create(
            id=1, faculty=faculty, name="L.EIC", acronym="L.EIC", course_type="L",
            year=2025, url="", plan_url="", last_updated=now,
        )
        cls.course_unit = CourseUnit.objects.create(
            id=100, course=course, name="Programming", acronym="PROG", url="",
            semester=1, year=1, last_updated=now,
        )
        cls.class_from = Class.objects.create(name="1LEIC01", course_unit=cls.course_unit, last_updated=now)
        cls.class_to = Class.objects.create(name="1LEIC02", course_unit=cls.course_unit, last_updated=now)

        User = get_user_model()
        cls.admin = User.objects.create(username="admin")
        ExchangeAdmin.objects.create(username="admin")

    def setUp(self):
        self.client.force_login(self.admin)
        self.enrollment = UserCourseUnits.objects.create(
            user_nmec=self.ISSUER_NMEC, course_unit=self.course_unit, class_field=self.class_from,
        )

    def create_urgent_request(self, goes_to="1LEIC02"):
        urgent_request = ExchangeUrgentRequests.objects.create(
            issuer_name="Student", issuer_nmec=self.ISSUER_NMEC, message="please",
            accepted=False, admin_state="untreated",
        )
        ExchangeUrgentRequestOptions.objects.create(
            class_issuer_goes_from="1LEIC01", class_issuer_goes_to=goes_to,
            course_unit=self.course_unit, exchange_urgent_request=urgent_request,
        )
        return urgent_request

    def accept(self, request_type, id):
        return self.client.put(f"/exchange/admin/request/{request_type}/{id}/accept/")

    def test_accepting_urgent_request_moves_issuer_to_target_class(self):
        urgent_request = self.create_urgent_request()

        response = self.accept("urgent_exchange", urgent_request.id)

        self.assertEqual(response.status_code, 200)
        urgent_request.refresh_from_db()
        self.assertTrue(urgent_request.accepted)
        self.assertEqual(urgent_request.admin_state, "treated")
        self.enrollment.refresh_from_db()
        self.assertEqual(self.enrollment.class_field, self.class_to)

    def test_accepting_urgent_request_resolves_composed_class_names(self):
        urgent_request = self.create_urgent_request(goes_to="1LEIC02+1LEIC03")

        response = self.accept("urgent_exchange", urgent_request.id)

        self.assertEqual(response.status_code, 200)
        self.enrollment.refresh_from_db()
        self.assertEqual(self.enrollment.class_field, self.class_to)

    def test_urgent_request_is_left_untouched_when_target_class_does_not_exist(self):
        urgent_request = self.create_urgent_request(goes_to="9LEIC99")

        response = self.accept("urgent_exchange", urgent_request.id)

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()["error"], "class-not-found")
        urgent_request.refresh_from_db()
        self.assertFalse(urgent_request.accepted)
        self.assertEqual(urgent_request.admin_state, "untreated")
        self.enrollment.refresh_from_db()
        self.assertEqual(self.enrollment.class_field, self.class_from)

    def test_accepting_unknown_urgent_request_returns_404(self):
        response = self.accept("urgent_exchange", 999999)

        self.assertEqual(response.status_code, 404)

    def test_accepting_direct_exchange_moves_participants(self):
        exchange = DirectExchange.objects.create(
            issuer_name="Student", issuer_nmec=self.ISSUER_NMEC, accepted=True,
        )
        DirectExchangeParticipants.objects.create(
            participant_name="Student", participant_nmec=self.ISSUER_NMEC,
            class_participant_goes_from="1LEIC01", class_participant_goes_to="1LEIC02",
            course_unit="PROG", course_unit_id=str(self.course_unit.id),
            direct_exchange=exchange, accepted=True,
        )

        response = self.accept("direct_exchange", exchange.id)

        self.assertEqual(response.status_code, 200)
        exchange.refresh_from_db()
        self.assertEqual(exchange.admin_state, "treated")
        self.enrollment.refresh_from_db()
        self.assertEqual(self.enrollment.class_field, self.class_to)

    def test_direct_exchange_is_left_untouched_when_target_class_does_not_exist(self):
        exchange = DirectExchange.objects.create(
            issuer_name="Student", issuer_nmec=self.ISSUER_NMEC, accepted=True,
        )
        DirectExchangeParticipants.objects.create(
            participant_name="Student", participant_nmec=self.ISSUER_NMEC,
            class_participant_goes_from="1LEIC01", class_participant_goes_to="9LEIC99",
            course_unit="PROG", course_unit_id=str(self.course_unit.id),
            direct_exchange=exchange, accepted=True,
        )

        response = self.accept("direct_exchange", exchange.id)

        self.assertEqual(response.status_code, 400)
        exchange.refresh_from_db()
        self.assertEqual(exchange.admin_state, "untreated")
        self.enrollment.refresh_from_db()
        self.assertEqual(self.enrollment.class_field, self.class_from)
