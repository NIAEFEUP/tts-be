from django.urls import path 
from . import views  

# URLConf
urlpatterns = [
    path('faculty/', views.faculty),
    path('course/<int:year>', views.course),
    path('course_units/<int:course_id>/<int:year>/<int:semester>/', views.course_units), 
    path('course_units_by_year/<int:course_id>/<int:year>/<int:semester>/', views.course_units_by_year), 
    path('course_last_year/<int:course_id>/', views.course_last_year),
    path('schedule/<int:course_unit_id>/', views.schedule),
    path('statistics/', views.data),
    path('professors/<int:schedule>/', views.professor),
    path('info/', views.info),
    path('login/', views.login),
    path('logout/', views.logout),
    path('student_schedule/<int:student>/', views.student_schedule),
    path('schedule_sigarra/<int:course_unit_id>/', views.schedule_sigarra),
    path('submit_direct_exchange/', views.submit_direct_exchange),
    path('verify_direct_exchange/<str:token>', views.verify_direct_exchange),
    path('students_per_course_unit/<int:course_unit_id>/', views.students_per_course_unit),
    path('submit_markeplace_exchange/', views.submit_marketplace_exchange)
]

