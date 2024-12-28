from mozilla_django_oidc.auth import OIDCAuthenticationBackend
from university.controllers.SigarraController import SigarraController
from university.models import UserCourseUnits

class CustomOIDCAuthentationBackend(OIDCAuthenticationBackend):
    
    def create_user(self, claims):
        user = super(CustomOIDCAuthentationBackend, self).create_user(claims)

        user.first_name = claims.get('given_name', '')
        user.last_name = claims.get('family_name', '').split(' ')[-1] 
        user.username = claims.get('nmec', '')
        user.password = "" # User does not have password
        user.save()

        # Fetch course units
        sigarra_controller = SigarraController()
        sigarra_controller = sigarra_controller.get_student_course_units(user.username)
        if sigarra_controller.status_code == 200:
            for course_unit_id in sigarra_controller.data:
                user_course_unit = UserCourseUnits(user_nmec=user.username, course_unit_id=course_unit_id)
                user_course_unit.save()


        return user

    def update_user(self, user, claims):
        user.first_name = claims.get('given_name', '')
        user.last_name = claims.get('family_name', '')
        user.save()

        UserCourseUnits.objects.filter(user_nmec=user.username).delete()

        sigarra_controller = SigarraController()
        sigarra_controller = sigarra_controller.get_student_course_units(user.username)
        if sigarra_controller.status_code == 200:
            for course_unit_id in sigarra_controller.data:
                user_course_unit = UserCourseUnits.objects.get(user_nmec=user.username, course_unit_id=course_unit_id)
                user_course_unit.save() 
                

        return user
    
