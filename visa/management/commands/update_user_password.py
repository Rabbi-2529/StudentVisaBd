from django.contrib.auth.hashers import make_password
from django.core.management.base import BaseCommand
from visa.models import Users, Students, CustomUser

class Command(BaseCommand):
    help = 'Update passwords by hashing them for existing Users and Students'

    def handle(self, *args, **options):
        # Update passwords for existing Users
        users_instances = CustomUser.objects.all()

        for user_instance in users_instances:
            try:
                if not user_instance.password.startswith(('pbkdf2_sha256$', 'bcrypt$', 'argon2$')):
                    # Check if the password is not already hashed
                    user_instance.password = make_password(user_instance.password)

                    self.stdout.write(self.style.SUCCESS(f"Password hashed for User: {user_instance.email}"))

                consultant_user = Users.objects.filter(id=user_instance.id).first()
                student_user = Students.objects.filter(id=user_instance.id)
                if consultant_user:
                    if consultant_user.user_role != 5:
                        user_instance.user_type = 0

                    else:
                        user_instance.user_type = 1
                
                elif student_user:
                    user_instance.user_type = 2

                user_instance.save()

            except Exception as e:
                self.stdout.write(self.style.ERROR(f"Error processing User {user_instance.email}: {str(e)}"))

