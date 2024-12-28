from mozilla_django_oidc.auth import OIDCAuthenticationBackend
from university.controllers.SigarraController import SigarraController
from university.models import UserCourseUnits, Class

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
        sigarra_controller = sigarra_controller.get_student_course_unit_classes(user.username)
        if sigarra_controller.status_code == 200:
            for item in sigarra_controller.data:
                (course_unit_id, class_acronym) = item
                corresponding_class = Class.objects.filter(course_unit__id=course_unit_id, name=class_acronym).first()

                print(f"Class {class_acronym} not found for course unit {course_unit_id}")
                if not corresponding_class:
                    continue

                user_course_unit = UserCourseUnits(
                    user_nmec=user.username, 
                    course_unit_id=course_unit_id, 
                    class_field=corresponding_class
                )
                user_course_unit.save()


        return user

    def update_user(self, user, claims):
        user.first_name = claims.get('given_name', '')
        user.last_name = claims.get('family_name', '').split(' ')[-1]
        user.save()

        UserCourseUnits.objects.filter(user_nmec=user.username).delete()

        # Fetch course units
        sigarra_controller = SigarraController()
        sigarra_controller = sigarra_controller.get_student_course_unit_classes(user.username)
        if sigarra_controller.status_code == 200:
            for item in sigarra_controller.data:
                (course_unit_id, class_acronym) = item
                corresponding_class = Class.objects.filter(course_unit__id=course_unit_id, name=class_acronym).first()
                # In MEIC and LEIC, theoretical classes classes are not added to the user
                if not corresponding_class:
                    continue

                user_course_unit = UserCourseUnits(
                    user_nmec=user.username, 
                    course_unit_id=course_unit_id, 
                    class_field=corresponding_class
                )
                user_course_unit.save()

        return user
    
