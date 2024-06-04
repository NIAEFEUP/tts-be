from django.urls import path 
from . import views  

# URLConf
urlpatterns = [
    path('faculty/', views.faculty),
    path('course/<int:year>', views.course),
    path('course_units/<int:course_id>/<int:year>/<int:semester>/', views.course_units), 
    path('course_unit/<int:course_unit_id>/', views.course_unit_by_id),
    path('class/<int:course_unit_id>/', views.classes),
    path('statistics/', views.data),
    path('professors/<int:slot>/', views.professor),
    path('info/', views.info)
]

