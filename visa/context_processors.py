# visa/context_processors.py

from .models import Users,ConsultantDetails

def user_data(request):
    # Your logic to retrieve user data
    user_data = None
    if request.user.is_authenticated:
        user_data = Users.objects.filter(consultant_user=request.user).first()
    return {'user_data': user_data}



def consultant_details(request):
    consultant_details = None
    if request.user.is_authenticated:
        consultant_details = ConsultantDetails.objects.filter(consultant_id=request.user.id).first()
    return {'consultant_details': consultant_details}



def consultant_user_details(request):
    consultant_user_details = None
    if request.user.is_authenticated:
        consultant_user_details = Users.objects.filter(consultant_user=request.user).first()
    return {'consultant_user_details': consultant_user_details}