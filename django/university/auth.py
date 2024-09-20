from django.contrib.auth.models import AbstractUser

class CustomOIDCAuthentationBackend(OIDCAuthenticationBackend):
    
    def create_user(self, claims):
        user = super(CustomOIDCAuthentationBackend, self).create_user(claims)

        print("claims: ", claims)

        user.first_name = claims.get('given_name', '')
        user.last_name = claims.get('family_name', '')
        user.username = claims.get('nmec', '')
        user.save()

        return user

    def update_user(self, user, claims):
        # user.first_name = claims.get('given_name', '')
        # user.last_name = claims.get('family_name', '')
        user.save()

        return user
    
