from django.urls import path, include

from university.routes.course_unit.CourseUnitEnrollmentView import CourseUnitEnrollmentView
from university.routes.exchange.AdminMarketplaceView import AdminMarketplaceView
from university.routes.MarketplaceExchangeView import MarketplaceExchangeView
from university.routes.auth.Csrf import Csrf
from university.routes.exchange.DirectExchangeView import DirectExchangeView
from university.routes.exchange.export.ExchangeExportView import ExchangeExportView
from university.routes.exchange.options.ExchangeOptionsView import ExchangeOptionsView
from university.routes.student.course_units.eligible.StudentEligibleCourseUnits import StudentEligibleCourseUnits
from university.routes.student.exchange.StudentReceivedExchangesView import StudentReceivedExchangesView
from university.routes.student.exchange.StudentSentExchangesView import StudentSentExchangesView
from university.routes.student.schedule.StudentScheduleView import StudentScheduleView
from university.routes.exchange.ExchangeCancelView import ExchangeCancelView
from university.routes.auth.InfoView import InfoView
from university.routes.exchange.AdminExchangeRequestRejectView import AdminExchangeRequestRejectView
from university.routes.exchange.AdminExchangeRequestAcceptView import AdminExchangeRequestAcceptView
from university.routes.student.StudentPhotoView import StudentPhotoView
from university.routes.exchange.card.metadata.ExchangeCardMetadataView import ExchangeCardMetadataView
from university.routes.exchange.verify.ExchangeVerifyView import ExchangeVerifyView
from university.routes.admin.AdminExchangeCoursesView import AdminExchangeCoursesView
from university.routes.admin.AdminExchangeCourseUnitsView import AdminExchangeCourseUnitsView
from university.routes.exchange.ExchangeUrgentView import ExchangeUrgentView
from university.routes.student.StudentCourseMetadataView import StudentCourseMetadataView
from university.routes.exchange.AdminRequestAwaitingInformationView import AdminRequestAwaitingInformationView
from university.routes.exchange.ExchangeCourseUnitPeriodView import ExchangeCourseUnitPeriodView
from university.routes.exchange.ExchangeCoursePeriodView import ExchangeCoursePeriodView
from university.routes.exchange.ExchangeCourseUnitPeriodDetailView import ExchangeCourseUnitPeriodDetailView
from university.routes.exchange.ExchangeCoursePeriodDetailView import ExchangeCoursePeriodDetailView
from university.routes.admin.AdminExchangeCourseUnitPeriodsView import AdminExchangeCourseUnitPeriodsView
from university.routes.admin.AdminExchangeCoursePeriodsView import AdminExchangeCoursePeriodsView



from university.middleware.exchange_admin import exchange_admin_required
from university.routes.exchange.verify.DirectExchangeValidationView import DirectExchangeValidationView

from tts_be.settings import FEDERATED_AUTH

from . import views
from mozilla_django_oidc import views as oidc_views


# URLConf
urlpatterns = [
    path('faculty/', views.faculty),
    path('course/<int:year>', views.course),
    path('course_units/<int:course_id>/<int:year>/<int:semester>/', views.course_units),
    path('professors/<int:schedule>/', views.professor),
    path('info/', views.info),
    path('auth/info/', InfoView.as_view()),
    path('csrf/', Csrf.as_view()),
    path('admin/courses/', AdminExchangeCoursesView.as_view()),
    path('student/schedule', StudentScheduleView.as_view(), name="auth-student-schedule"),
    path('student/<str:nmec>/schedule', exchange_admin_required(StudentScheduleView.as_view()), name="student-schedule"),
    path('student/exchange/sent/', StudentSentExchangesView.as_view()),
    path('student/exchange/received/', StudentReceivedExchangesView.as_view()),
    path('student/<str:nmec>/<int:course_id>/metadata', exchange_admin_required(StudentCourseMetadataView.as_view())),
    path('student/course_units/eligible', StudentEligibleCourseUnits.as_view()),
    path('student/<str:nmec>/photo', StudentPhotoView.as_view()),
    path('exchange/verify/<str:token>', ExchangeVerifyView.as_view()),
    path('student_data/<str:codigo>/', views.student_data),
    path('exchange/marketplace/', MarketplaceExchangeView.as_view()),
    path('exchange/direct/', DirectExchangeView.as_view(), name="direct_exchange"),
    path('exchange/direct/<int:id>', DirectExchangeView.as_view(), name="direct_exchange-id"),
    path('exchange/direct/validate/<int:id>', DirectExchangeValidationView.as_view()),
    path('exchange/options/', ExchangeOptionsView.as_view()),
    path('exchange/<str:request_type>/<int:id>/cancel/', ExchangeCancelView.as_view()),
    path('exchange/export/csv', ExchangeExportView.as_view()),
    path('exchange/urgent/', ExchangeUrgentView.as_view()),
    path('course_unit/<int:course_unit_id>/exchange/metadata', ExchangeCardMetadataView.as_view()),
    path('course_unit/<int:course_unit_id>/', views.course_unit_by_id),
    path('class/<int:course_unit_id>/', views.classes),
    path('professors/<int:slot>/', views.professor),
    path('course_unit/hash', views.get_course_unit_hashes),
    path('course_unit/enrollment/', CourseUnitEnrollmentView.as_view()), 
    path('oidc-auth/', include('mozilla_django_oidc.urls')),
    path('exchange/admin/courses/', exchange_admin_required(AdminExchangeCoursesView.as_view())),
    path('exchange/admin/course_units/', AdminExchangeCourseUnitsView.as_view()),
    path('exchange/admin/marketplace', exchange_admin_required(AdminMarketplaceView.as_view())),
    path('exchange/admin/course_unit/<int:course_unit_id>/period/', ExchangeCourseUnitPeriodView.as_view()),
    path('exchange/admin/course_unit/periods/', AdminExchangeCourseUnitPeriodsView.as_view()),
    path('exchange/admin/course/<int:course_id>/period/', ExchangeCoursePeriodView.as_view()),
    path('exchange/admin/courses/periods/', AdminExchangeCoursePeriodsView.as_view()),
    path('exchange/admin/course_unit/<int:course_unit_id>/period/<int:period_id>/', ExchangeCourseUnitPeriodDetailView.as_view()),
    path('exchange/admin/course/<int:course_id>/period/<int:period_id>/', ExchangeCoursePeriodDetailView.as_view()),
    path('exchange/admin/request/<str:request_type>/<int:id>/reject/', exchange_admin_required(AdminExchangeRequestRejectView.as_view())),
    path('exchange/admin/request/<str:request_type>/<int:id>/accept/', exchange_admin_required(AdminExchangeRequestAcceptView.as_view())),
    path('exchange/admin/request/<str:request_type>/<int:id>/awaiting-information/', exchange_admin_required(AdminRequestAwaitingInformationView.as_view())),
    path('api/oidc-auth/callback/', oidc_views.OIDCAuthenticationCallbackView.as_view(), name="api_oidc_authentication_callback")
]

if FEDERATED_AUTH == 0:
    urlpatterns.append(path('sigarra_login/', views.sigarra_login))
