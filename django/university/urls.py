from django.urls import path, include

from university.routes.MarketplaceExchangeView import MarketplaceExchangeView
from university.routes.auth.Csrf import Csrf
from university.routes.exchange.DirectExchangeView import DirectExchangeView
from university.routes.exchange.export.ExchangeExportView import ExchangeExportView
from university.routes.exchange.options.ExchangeOptionsView import ExchangeOptionsView
from university.routes.student.course_units.eligible.StudentEligibleCourseUnits import StudentEligibleCourseUnits
from university.routes.student.exchange.StudentReceivedExchangesView import StudentReceivedExchangesView
from university.routes.student.exchange.StudentSentExchangesView import StudentSentExchangesView
from university.routes.student.schedule.StudentScheduleView import StudentScheduleView
from university.routes.auth.InfoView import InfoView
from university.routes.student.StudentPhotoView import StudentPhotoView
from university.routes.exchange.card.metadata.ExchangeCardMetadataView import ExchangeCardMetadataView
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
    path('student/schedule', StudentScheduleView.as_view()),
    path('student/exchange/sent/', StudentSentExchangesView.as_view()),
    path('student/exchange/received/', StudentReceivedExchangesView.as_view()),
    path('student/course_units/eligible', StudentEligibleCourseUnits.as_view()),
    path('student/<str:nmec>/photo', StudentPhotoView.as_view()),
    path('verify_direct_exchange/<str:token>', views.verify_direct_exchange),
    path('student_data/<str:codigo>/', views.student_data),
    path('exchange/marketplace/', MarketplaceExchangeView.as_view()),
    path('exchange/direct/', DirectExchangeView.as_view()),
    path('exchange/options/', ExchangeOptionsView.as_view()),
    path('exchange/export/', ExchangeExportView.as_view()),
    path('course_unit/<int:course_unit_id>/exchange/metadata', ExchangeCardMetadataView.as_view()),
    path('course_unit/<int:course_unit_id>/', views.course_unit_by_id),
    path('class/<int:course_unit_id>/', views.classes),
    path('professors/<int:slot>/', views.professor),
    path('course_unit/hash', views.get_course_unit_hashes),
    path('oidc-auth/', include('mozilla_django_oidc.urls')),
]
