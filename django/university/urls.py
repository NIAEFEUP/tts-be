from django.urls import path 
from . import views  

# URLConf
urlpatterns = [
    path('faculty/', views.faculty),
    path('course/', views.course),
    path('course_units/<int:course_id>/<int:semester>/', views.course_units), 
    path('course_units_by_year/<int:course_id>/<int:semester>/', views.course_units_by_year),
    path('schedule/<int:course_unit_id>/', views.schedule)
]
    