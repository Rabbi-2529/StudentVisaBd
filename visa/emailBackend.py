from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import check_password
from django.contrib.auth.backends import ModelBackend
from .models import Students, Users


class EmailBackend(ModelBackend):
    def authenticate(self, request=None, email=None, password=None, **kwargs):
        UserModel = get_user_model()

        try:
            # Check if the email exists in the Users model
            user = UserModel.objects.get(email=email)
            print('user in email backend: ', user)

            # Check the password
            if user.check_password(password):
                return user
            else:
                print('no user in email backend')
                return None

        except UserModel.DoesNotExist:
            # Email doesn't exist, return None
            return None




    # def authenticate(self, request=None, email=None, phone=None, password=None, **kwargs):
    #     UserModel = get_user_model()

    #     try:
    #         # Check if the email or phone exists in the Users model
    #         if email:
    #             user = UserModel.objects.get(email=email)
    #             if user.check_password(password):
    #                 return user
    #         else:
    #             print('no real user')
    #             return None
    #     except UserModel.DoesNotExist:
    #         return None
    #     #     

    #     if user.check_password(password):
    #         return user

    #     else:
    #         print('no user last')
    #         return None