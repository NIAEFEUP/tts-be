from mozilla_django_oidc.auth import OIDCAuthenticationBackend
from university.controllers.SigarraController import SigarraController
from university.controllers.StudentController import StudentController
from university.models import UserCourseUnits, Class

class CustomOIDCAuthentationBackend(OIDCAuthenticationBackend):
    
    def create_user(self, claims):
        user = super(CustomOIDCAuthentationBackend, self).create_user(claims)

        user.first_name = claims.get('given_name', '')
        user.last_name = claims.get('family_name', '').split(' ')[-1] 
        user.username = claims.get('nmec', '')
        user.password = "" # User does not have password
        user.save()

        return user

    def update_user(self, user, claims):
        user.first_name = claims.get('given_name', '')
        user.last_name = claims.get('family_name', '').split(' ')[-1]
        user.save()

        return user
    
