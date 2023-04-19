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
    path('professors/<int:schedule_id>/', views.professor)
]

