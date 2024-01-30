from django.shortcuts import render,redirect
from .models import *
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.views.decorators.csrf import csrf_exempt
from django.core.serializers import serialize
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password
from django.views.decorators.http import require_POST
from django.db.models import Q
from django.db import transaction
from django.db.models import Sum
from datetime import datetime
from django.db import IntegrityError
from django.db.models import Count
from datetime import timedelta
from django.db.models.functions import ExtractMonth
from django.db.models import Sum, F, Value
from django.db.models.functions import Coalesce
from django.db.models import Count, Max
from django.db.models.functions import ExtractMonth, ExtractYear,ExtractWeek
from django.http import HttpResponseRedirect
from django.http import JsonResponse
import json
from django.http import HttpResponse, JsonResponse,HttpResponseNotFound
from django.contrib.auth.hashers import check_password

def root_home(request):
    # Count the total number of students, consultants, countries, and universities
    total_students = Students.objects.count()
    

    # Count consultants where user_role is 6
    total_consultants = Users.objects.filter(user_role=5).count()

    total_countries = Countries.objects.count()
    total_universities = University.objects.count()

    # Get the current year
    current_year = timezone.now().year

    # Calculate rate percentage for students in the current year
    students_by_year = Students.objects.filter(created_at__year=current_year).count()
    student_rates = calculate_rate_percentage(current_year, Students, students_by_year)

    # Calculate rate percentage for consultants in the current year
    consultants_by_year = Users.objects.filter(user_role=5, created_at__year=current_year).count()
    consultant_rates = calculate_rate_percentage(current_year, Users, consultants_by_year)
    avg_time_on_site = calculate_avg_time_on_site(request.user.id)
    messages = Message.objects.all()
    unread_messages = messages.filter(is_read=False)
    unread_count = unread_messages.count()
    user_notifications = Notification.objects.filter(user=request.user, is_read=False)
    user_notifications.update(is_read=True)

    # user_data = None
    # if request.user.is_authenticated :
    #     user_data = Users.objects.filter(consultant_user=request.user).first()


        
    #     print("User Full Name:", user_data)
    #     print("User Email:", user_data.email)
        

    context = {
        'total_students': total_students,
        'total_consultants': total_consultants,
        'total_countries': total_countries,
        'total_universities': total_universities,
        'student_rates': student_rates,
        'consultant_rates': consultant_rates,
        'avg_time_on_site': avg_time_on_site,
        'messages': messages,
         'unread_count': unread_count,
         'notifications': user_notifications,
        #  'user_data': user_data,
         
    }

    return render(request, 'roottemplates/index.html', context)


def root_profile(request):
    if request.user.is_authenticated:
        print('user: ', request.user.email)
        user_id = request.user.id
        user = Users.objects.get(id=user_id)
        print('est. date: ', user.est_date)
        context = {
            'user': user,
        }
    return render(request, 'roottemplates/root_profile.html', context)
def save_root_profile(request, user_id):
    if request.method == 'POST' and request.user.is_authenticated:
        user = request.user
        if user.id == int(user_id):
         
            full_name = request.POST.get('full_name')


            website = request.POST.get('website')
            about = request.POST.get('about')
            old_password = request.POST.get('old_password')
            new_password = request.POST.get('new_password')
            confirm_password = request.POST.get('confirm_password')
            consultant_img = request.FILES.get('consultant_img')

            print('website: ', website)
            print('about: ', about)
            print('consultant_img: ', consultant_img)
            root_id = int(user_id)
            root = Users.objects.get(id=root_id)

            if  website and about:

                root.full_name = full_name


                root.website = website
                root.about = about

                if consultant_img:
                    root.consultant_img = consultant_img

                if old_password and  new_password and confirm_password:
                    if new_password == confirm_password:
                        if check_password(new_password, user.password):
                            user.set_password(new_password)
                        else:
                            return JsonResponse({'error': 'Wrong old password'})
                    else:
                        return JsonResponse({'error': 'Passwords do not match'})
                user.save()
                root.save()
                return JsonResponse({'success': True})
            else:
                return JsonResponse({'error': 'Please fill up all the required fields'})
        else:
            return JsonResponse({'error': 'Cannot update your account information due to security reasons'})
    else:
        return JsonResponse({'error': 'Invalid request'})
    



def calculate_rate_percentage(year, model, count):
    # Get the count for the previous year
    prev_year_count = model.objects.filter(created_at__year=year - 1).count()

    # Calculate rate percentage for the current year
    rate = 0.0
    increase_decrease = "No Change"

    if prev_year_count != 0:
        rate = ((count - prev_year_count) / prev_year_count) * 100

        if rate > 0:
            increase_decrease = "Increased"
        elif rate < 0:
            increase_decrease = "Decreased"

    return {'year': year, 'rate': rate, 'increase_decrease': increase_decrease}



def calculate_avg_time_on_site(user):
    # Calculate average time on site for the current user
    user_sessions = UserSession.objects.filter(user=user)

    if user_sessions.exists():
        total_duration = sum((session.end_time - session.start_time).total_seconds() for session in user_sessions)
        avg_duration = total_duration / user_sessions.count()
        avg_time_on_site = str(timedelta(seconds=avg_duration))
        return avg_time_on_site
    else:
        return "0"
def monthly_balance_chart(request):
    # Assuming 'created_at' is the date field in your Balances model
    monthly_data = Balances.objects.annotate(month=ExtractMonth('created_at')).values('month') \
        .annotate(credit=Sum('acc_credit'), debit=Sum('acc_debit')).order_by('month')

    labels = [get_month_name(month['month']) for month in monthly_data]
    credit_data = [month['credit'] for month in monthly_data]
    debit_data = [month['debit'] for month in monthly_data]

    context = {
        'labels': labels,
        'credit_data': credit_data,
        'debit_data': debit_data,
    }

    return JsonResponse(context, safe=False)

def get_month_name(month_number):
    # Replace this with your own method to get month names
    return ['JAN', 'FEB', 'MAR', 'APR', 'MAY', 'JUN', 'JUL', 'AUG', 'SEP', 'OCT', 'NOV', 'DEC'][month_number - 1]
from django.db.models import Sum, ExpressionWrapper, F, FloatField, Case, When, Value

def type_of_balance(request):
    # Assuming you have a field named 'pay_method' in your Balances model
    totals = Balances.objects.values('pay_method').annotate(
        total_amount=Coalesce(Sum('acc_credit'), 0.0)
    ).order_by('pay_method')

    # Convert the queryset to a list of dictionaries
    totals_list = list(totals)

    # Create a dictionary to hold the result
    result = {'payment_method_totals': totals_list}

    # Return the result in JSON format
    return JsonResponse(result)

def root_consultant_list_json(request):
    # Filter users based on the condition that active_status is not null
    rootconsultant = Users.objects.filter(
        user_role__in=[5],
        active_status__isnull=True
    ).exclude(
        id__in=CustomUser.objects.values('id')
    )

    # Extract specific fields from the queryset
    rootconsultant_data = rootconsultant.values('full_name', 'email', 'company_name', 'active_status')

    # Convert the queryset data to a list
    rootconsultant_list = list(rootconsultant_data)

    # Calculate the total count
    total_count = rootconsultant.count()

    # Return the JSON response with total count
    return JsonResponse({'rootconsultant': rootconsultant_list, 'total_count': total_count}, safe=False)


def count_consultant_perform(request):
    try:
        # Count occurrences of each consultant_id and get the last created_at
        consultant_counts = Levels.objects.filter(status=1).values('consultant_id').annotate(
            count=Count('consultant_id'),
            last_activity=Max('created_at')
        )

        # Return the result as JSON response
        return JsonResponse({'consultant_counts': list(consultant_counts)})
    except Exception as e:
        # Handle exceptions
        return JsonResponse({'error': str(e)}, status=500)
    

def count_students_monthly_entry(request):
    try:
        # Count occurrences of students entered each month
        students_counts = Students.objects.annotate(
            month=ExtractMonth('created_at'),
        ).values('month').annotate(count=Count('id'))

        # Return the result as JSON response
        return JsonResponse({'students_counts': list(students_counts)})
    except Exception as e:
        # Handle exceptions
        return JsonResponse({'error': str(e)}, status=500)
    

def count_students_yearly_entry(request):
    try:
        # Count occurrences of students entered each year
        students_counts = Students.objects.annotate(
            year=ExtractYear('created_at'),
        ).values('year').annotate(count=Count('id'))

        # Return the result as JSON response
        return JsonResponse({'students_counts': list(students_counts)})
    except Exception as e:
        # Handle exceptions
        return JsonResponse({'error': str(e)}, status=500)
    
def count_students_weekly_entry(request):
    try:
        # Count occurrences of students entered each week
        students_counts = Students.objects.annotate(
            week=ExtractWeek('created_at'),
        ).values('week').annotate(count=Count('id'))

        # Return the result as JSON response
        return JsonResponse({'students_counts': list(students_counts)})
    except Exception as e:
        # Handle exceptions
        return JsonResponse({'error': str(e)}, status=500)
    
def message_list(request):
    query = request.GET.get('q')
    messages = Message.objects.order_by('-created_at')

    if query:
        # If a search query is provided, filter messages based on the query
        messages = messages.filter(
            Q(subject__icontains=query) |  # You can adjust this based on your model fields
            Q(text__icontains=query)
        )

    context = {'messages': messages}
    return render(request, 'roottemplates/message_list.html', context)



def create_reply(request, message_id):
    if request.method == 'POST':
        reply_text = request.POST.get('reply_text')
        try:
            message = Message.objects.get(pk=message_id)
            reply = Reply.objects.create(
                message=message,
                email=request.user.email,  # Assuming you're using Django's authentication
                reply_text=reply_text,
                created_at=datetime.now()
            )
            return JsonResponse({'status': 'success'})
        except Message.DoesNotExist:
            return HttpResponseNotFound('Message not found')
    else:
        return HttpResponseNotFound('Method Not Allowed')

@csrf_exempt
def get_chat_history(request, message_id):
  message = get_object_or_404(Message, id=message_id)
  replies = message.reply_set.all().order_by('created_at')
  data = {
    'message': {
      'subject': message.subject,
      'message': message.message,
      'created_at': message.created_at,
    },
    'replies': [{
      'text': reply.reply_text,
      'email': reply.email,
      'created_at': reply.created_at,
    } for reply in replies],
  }
  return JsonResponse(data)






def root_customize(request):
    # Check if there is an existing Customize instance
    instance = Customizes.objects.first()

    if request.method == 'POST':
        description = request.POST.get('description')
        status = request.POST.get('status')
        image = request.FILES.get('image')  # Assuming your form has a file input with name 'image'

        if instance:  # Update operation
            instance.description = description
            instance.status = status
            if image:  # Update image only if a new one is provided
                instance.image = image
            instance.updated_at = timezone.now()
            operation_type = "updated"
        else:  # Create operation
            instance = Customizes(
                description=description,
                status=status,
                created_at=timezone.now(),
                updated_at=timezone.now()
            )
            if image:
                instance.image = image
            operation_type = "created"

        instance.save()

        messages.success(request, f"Customization {operation_type} successfully.")
    
    context = {'instance': instance}

    return render(request, 'roottemplates/customize.html', {'instance': instance})
def offer_letters(request):
    # Check if there is an existing OfferLetters instance
    instance = OfferLetters.objects.first()

    if request.method == 'POST':
        title = request.POST.get('title')
        description = request.POST.get('description')
        status = 1  # Set the status to 1

        # Handle the image field
        image = request.FILES.get('image')

        if instance:  # Update operation
            instance.title = title
            instance.description = description
            instance.status = status
            if image:
                instance.image = image
            instance.updated_at = timezone.now()
            operation_type = "updated"
        else:  # Create operation
            instance = OfferLetters(
                title=title,
                description=description,
                status=status,
                created_at=timezone.now(),
                updated_at=timezone.now()
            )
            if image:
                instance.image = image
            operation_type = "created"

        instance.save()

        messages.success(request, f"Offer letter {operation_type} successfully.")

    return render(request, 'roottemplates/offer_latter.html', {'instance': instance})

def root_countries(request):
    # Fetch the list of countries
    country_list = Countries.objects.all()

    return render(request, 'roottemplates/countries.html', {'country_list': country_list})

def delete_country(request, country_id):
    country_list = Countries.objects.all()

    if request.method == 'POST':
        country = get_object_or_404(Countries, pk=country_id)
        country.delete()
        return JsonResponse({'success': True, 'message': 'Country deleted successfully!'})

    country_list_json = serialize('json', country_list, fields=('country_id', 'country_name', 'country_flag', 'country_howtoapply'))
    return JsonResponse({'country_list': country_list_json}, safe=False)

@csrf_exempt
def edit_country(request, country_id):
    # Fetch the country to be edited
    country = get_object_or_404(Countries, pk=country_id)

    if request.method == 'POST':
        # Handle the edit operation
        country_name = request.POST.get('country_name')
        country_flag = request.POST.get('country_flag')
        country_howtoapply = request.POST.get('country_howtoapply')
        country.country_name = country_name
        country.country_flag = country_flag
        country.country_howtoapply = country_howtoapply
        country.save()

        messages.success(request, 'Country updated successfully!')
        return redirect('root_countries')  # Replace 'your_redirect_view_name' with the actual view name

    return render(request, 'roottemplates/edit_country.html', {'country': country})




def consultant_wise_scholarship(request):
    # Fetch all users with user_type=1
    consultants = Users.objects.filter(user_role=5)

    if request.method == 'POST':
        scow_text = request.POST.get('scow_text')
        scow_whocanapply = request.POST.get('scow_whocanapply')
        scow_status = request.POST.get('scow_status')
        consultant_id = request.POST.get('consultant_id')

        consultant_instance = Users.objects.get(id=consultant_id)

        # Create a new instance without checking for an existing one
        instance = ConsultantWises(
            scow_text=scow_text,
            scow_whocanapply=scow_whocanapply,
            scow_status=scow_status,
            scow_consultant_id=consultant_instance.id,
            created_at=timezone.now(),
            updated_at=timezone.now()
        )
        if not scow_status:
            instance.scow_status = 1
        operation_type = "created"

        instance.save()

        messages.success(request, f"Consultant Wise Scholarship {operation_type} successfully.")

    # Fetch all instances of ConsultantWises
    instances = ConsultantWises.objects.all()

    return render(request, 'roottemplates/consultant_wise_scholarship.html', {'instances': instances, 'consultants': consultants})


def consultant_wise_scholarship(request):
    # Fetch all users with user_type=1
    consultants = Users.objects.filter(user_role=5)

    if request.method == 'POST':
        scow_text = request.POST.get('scow_text')
        scow_whocanapply = request.POST.get('scow_whocanapply')
        scow_status = request.POST.get('scow_status')
        scow_title = request.POST.get('scow_title')
        consultant_id = request.POST.get('consultant_id')

        consultant_instance = Users.objects.get(id=consultant_id)

        # Create a new instance without checking for an existing one
        instance = ConsultantWises(
            scow_text=scow_text,
            scow_whocanapply=scow_whocanapply,
            scow_status=scow_status,
            scow_consultant_id=consultant_instance.id,
            scow_title=consultant_instance.scow_title,
            created_at=timezone.now(),
            updated_at=timezone.now()
        )
        if not scow_status:
            instance.scow_status = 1
        operation_type = "created"

        instance.save()

        messages.success(request, f"Consultant Wise Scholarship {operation_type} successfully.")

    # Fetch all instances of ConsultantWises
    instances = ConsultantWises.objects.all()

    return render(request, 'roottemplates/consultant_wise_scholarship.html', {'instances': instances, 'consultants': consultants})




def country_wise_scholarship_list(request):
    scholarships = CountryWises.objects.all()

    # Fetch related country information for each scholarship
    scholarship_data = []
    for scholarship in scholarships:
        country = Countries.objects.get(country_id=scholarship.scw_country_id)
        scholarship_data.append({
            'scholarship': scholarship,
            'country_name': country.country_name,
        })

    return render(request, 'roottemplates/country_wise_scholarship_list.html', {'scholarship_data': scholarship_data})


def edit_scholarship(request, scw_id):
    scholarship = get_object_or_404(CountryWises, pk=scw_id)
    countries = Countries.objects.all()

    if request.method == 'POST':
        scw_text = request.POST.get('scw_text')
        scw_title=request.POST.get('scw_title')
        scw_whocanapply = request.POST.get('scw_whocanapply')
        scw_status = request.POST.get('scw_status')
        scw_country_id = request.POST.get('scw_country_id')

        if 'scw_image' in request.FILES:
            scholarship.scw_image = request.FILES['scw_image']

        scholarship.scw_text = scw_text
        scholarship.scw_title=scw_title
        scholarship.scw_whocanapply = scw_whocanapply
        scholarship.scw_status = scw_status
        scholarship.scw_country_id = scw_country_id
        scholarship.save()

        messages.success(request, "Consultant Wise Scholarship successfully updated.")

    scholarship_data = {
        'scw_text': scholarship.scw_text,
        'scw_whocanapply': scholarship.scw_whocanapply,
        'scw_status': scholarship.scw_status,
        'scw_country_id': scholarship.scw_country_id,
        'scw_image': scholarship.scw_image,
        'scw_title': scholarship.scw_title  # Include the image in the data
    }

    return render(request, 'roottemplates/edit_scholarship_form.html', {'scholarship_data': scholarship_data, 'scw_id': scw_id, 'countries': countries})

@require_POST
def delete_scholarship(request, scw_id):
    scholarship = get_object_or_404(CountryWises, pk=scw_id)
    scholarship.delete()

    return JsonResponse({'success': True, 'message': 'Scholarship deleted successfully', 'scw_id': scw_id})




def country_wise_scholarship(request):
    countries = Countries.objects.all()

    if request.method == 'POST':
        scw_text = request.POST.get('scw_text')
        scw_whocanapply = request.POST.get('scw_whocanapply')
        scw_status = request.POST.get('scw_status')
        scw_country_id = request.POST.get('country_id')
        scw_image = request.FILES.get('scw_image')  # Assuming the file input name is 'scw_image'

        try:
            scw_country_id = int(scw_country_id)
        except ValueError:
            messages.error(request, "Invalid country selected.")
            return render(request, 'roottemplates/country_wise_scholarship.html', {'country': countries})

        instance = CountryWises(
            scw_text=scw_text,
            scw_whocanapply=scw_whocanapply,
            scw_status=scw_status,
            scw_country_id=scw_country_id,
            scw_image=scw_image,
            created_at=timezone.now(),
            updated_at=timezone.now()
        )

        if not scw_status:
            instance.scw_status = 1

        operation_type = "created"
        instance.save()
        messages.success(request, f"Country Wise Scholarship {operation_type} successfully.")

    instances = CountryWises.objects.all()

    return render(request, 'roottemplates/country_wise_scholarship.html', {'instances': instances, 'country': countries})


def university_wise_scholarship(request):
    universities = University.objects.all()

    if request.method == 'POST':
        uw_text = request.POST.get('uw_text')
        uw_whocanapply = request.POST.get('uw_whocanapply')
        uw_status = request.POST.get('uw_status')
        uw_university_id = request.POST.get('university_id')

        university_instance = get_object_or_404(University, university_id=uw_university_id)

        instance = UniversityWise(
            uw_text=uw_text,
            uw_whocanapply=uw_whocanapply,
            uw_status=uw_status,
            uw_university_id=university_instance.id,
            created_at=timezone.now(),
            updated_at=timezone.now()
        )

        if not uw_status:
            instance.uw_status = 1

        operation_type = "created"
        instance.save()

        messages.success(request, f"University Wise Scholarship {operation_type} successfully.")

    instances = UniversityWise.objects.all()

    return render(request, 'roottemplates/university_wise_scholarship.html', {'instances': instances, 'universities': universities})



def root_users_list(request):
    # Filter users based on the condition that permission is not granted
    root_users = Users.objects.filter(user_role__in=[2, 3, 4]).exclude(id__in=CustomUser.objects.values('id'))

    context = {'root_users': root_users}
    return render(request, 'roottemplates/rootuser_list.html', context)






def create_root(request):
    if request.method == 'POST':
        full_name = request.POST.get('full_name')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        raw_password = request.POST.get('password')
        user_role = request.POST.get('user_role')

        # Create a new Users instance with both raw and hashed passwords
        new_users_instance = Users.objects.create(
            full_name=full_name,
            email=email,
            phone=phone,
            raw_password=raw_password,
            password=make_password(raw_password),
            user_role=user_role,
            created_at=timezone.now(),
            updated_at=timezone.now(),
        )

        # Create a CustomUser regardless of permission

        messages.success(request, 'Root user  created successfully.')

        return redirect('root_users_list')

    return render(request, 'roottemplates/create_root.html')

def grant_permission(request, user_id):
    # Get the Users instance using user_id
    user_instance = Users.objects.get(pk=user_id)

    # Check if permission is granted
    if some_condition_is_met():
        # Create a CustomUser with the user details
        new_root_user = CustomUser.objects.create(
            id=user_id,

            email=user_instance.email,
            password=user_instance.password,
            user_type=0,
            last_active=timezone.now(),
        )
        print('new_root_user:', new_root_user)

        messages.success(request, 'Root user and CustomUser created successfully.')
    else:
        messages.success(request, 'Root user created successfully. Permission not granted for CustomUser.')

    return redirect('root_users_list')

def some_condition_is_met():

    return True 


def root_consultant_list(request):
    # Filter users based on the condition that active_status is not null
    rootconsultant = Users.objects.filter(
        user_role__in=[5],
        active_status__isnull=True
    ).exclude(
        id__in=CustomUser.objects.values('id')
    )

    context = {'rootconsultant': rootconsultant}
    return render(request, 'roottemplates/rootconsultant_list.html', context)

def grant_permission_consultant(request, user_id):
    try:
        # Get the Users instance using user_id
        user_instance = Users.objects.get(pk=user_id)

        # Check if permission is granted
        if some_condition_is_met():
            with transaction.atomic():
                # Use the user_id explicitly as the ID for CustomUser
                new_root_user = CustomUser.objects.create(
                    id=user_id,
                    email=user_instance.email,
                    password=user_instance.password,
                    user_type=1,
                    last_active=timezone.now(),
                )

            # Set the active_status to 1 when permission is granted
            user_instance.active_status = 1
            user_instance.save()

            messages.success(request, 'Consultant created successfully.')
        else:
            # Set the active_status to 0 when rejecting the consultant
            user_instance.active_status = 0
            user_instance.save()

            messages.success(request, 'Permission not granted for Consultant. Consultant rejected.')

    except Users.DoesNotExist:
        messages.error(request, 'Consultant not found.')

    return redirect('root_consultant_list')

@require_POST
def reject_consultant(request, user_id):
    try:
        # Get the Users instance using user_id
        user_instance = Users.objects.get(pk=user_id)

        # Set the active_status to 0 when rejecting the consultant
        user_instance.active_status = 0
        user_instance.save()

        messages.success(request, 'Consultant rejected successfully.')
    except Users.DoesNotExist:
        messages.error(request, 'Consultant not found.')

    return redirect('root_consultant_list')



def activeconsultant(request):
    active_consultants = Users.objects.filter(active_status=1, consultant_user__user_type=1).select_related('consultant_user')

    consultant_data = [
        {
            'id': user.id,
            'company_name': user.company_name,
            'full_name': user.full_name,
            'email': user.email,
            'phone': user.phone,
            'registration': user.created_at.strftime('%Y-%m-%d %H:%M:%S') if user.created_at else None,
            'last_active': user.consultant_user.last_active if user.consultant_user else None,
        }
        for user in active_consultants
    ]

    return JsonResponse({'consultants': consultant_data}, safe=False)

def active_consultant_details(request, user_id):
    print(f'Received user ID: {user_id}')  # Debugging line

    consultant = get_object_or_404(Users, id=user_id, active_status=1)

    consultant_data = {
        'full_name': consultant.full_name,
        'email': consultant.email,
        'phone': consultant.phone,
        'company_name': consultant.company_name,
        'website': consultant.website,
        'address': consultant.address,
    }

    return JsonResponse({'consultant': consultant_data})



def suspend_account(request, user_id):
    # Get the user to be suspendedd
    user = get_object_or_404(Users, id=user_id)

    # Suspend the account (update the active_status or any other relevant field)
    user.active_status = 2
    user.suspension_time = timezone.now()  # Assuming 2 represents suspended status, adjust as needed
    user.save()

    # You can return a success message or any other relevant information
    return JsonResponse({'message': 'Account suspended successfully'})


def suspend_list(request):
    # Retrieve a list of suspended users
    suspended_users = Users.objects.filter(active_status=2)  # Assuming 2 represents suspended status, adjust as needed

    # Create a list of dictionaries containing user information
    user_list = [{
        'id': user.id,
        'company_name': user.company_name,
        'full_name': user.full_name,
        'email': user.email,
        'phone': user.phone,
        'suspension_time': user.suspension_time.strftime('%Y-%m-%d %H:%M:%S') if user.suspension_time else None,
    } for user in suspended_users]

    # Return a JSON response with the user list
    return JsonResponse({'suspended_users': user_list})


def suspended_consultant_details(request, user_id):
    consultant = get_object_or_404(Users, id=user_id, active_status=2)

    consultant_data = {
        'full_name': consultant.full_name,
        'email': consultant.email,
        'phone': consultant.phone,
        'company_name': consultant.company_name,
        'website': consultant.website,
        'address': consultant.address,
    }

    return JsonResponse({'consultant': consultant_data})
    
    
    
    
def free_account(request, user_id):
   
    user = get_object_or_404(Users, id=user_id, user_role=5)
    user.active_status = 3
    user.save()
    return JsonResponse({'message': 'Free account processed successfully'})


def free_list(request):

    free_users = Users.objects.filter(active_status=3)


    user_list = [{
        'id': user.id,
        'company_name': user.company_name,
        'full_name': user.full_name,
        'email': user.email,
        'phone': user.phone,
       
      
    } for user in free_users]


    return JsonResponse({'free_users': user_list})

def free_consultant_details(request, user_id):
    consultant = get_object_or_404(Users, id=user_id, active_status=3)

    consultant_data = {
        'full_name': consultant.full_name,
        'email': consultant.email,
        'phone': consultant.phone,
        'company_name': consultant.company_name,
        'website': consultant.website,
        'address': consultant.address,
       
    }

    return JsonResponse({'consultant': consultant_data})





def activate_basic_account(request, user_id):
    # Get the user with status 2 and user role 4 (adjust as needed)
    user = get_object_or_404(Users, id=user_id, user_role=5)
    user.active_status = 4  # Assuming 4 represents an active status for basic users, adjust as needed
    user.save()
    return JsonResponse({'message': 'Basic account activated successfully'})

def basic_list(request):
    # Retrieve a list of users with status 2 and user role 4 (adjust as needed)
    basic_users = Users.objects.filter(active_status=4)

    # Create a list of dictionaries containing user information
    user_list = [{
        'id': user.id,
        'company_name': user.company_name,
        'full_name': user.full_name,
        'email': user.email,
        'phone': user.phone,
        # Include any additional fields as needed
    } for user in basic_users]

    # Return a JSON response with the user list
    return JsonResponse({'basic_users': user_list})

def basic_user_details(request, user_id):
    consultant = get_object_or_404(Users, id=user_id, active_status=4)
     
    # Create a dictionary containing user details
    consultant_data = {
        'full_name': consultant.full_name,
        'email': consultant.email,
        'phone': consultant.phone,
        'company_name': consultant.company_name,
        # Include any additional fields as needed
    }

    # Return a JSON response with the user details
    return JsonResponse({'consultant': consultant_data})



def activate_premium_account(request, user_id):
    # Get the user with status 2 and user role 4 (adjust as needed)
    user = get_object_or_404(Users, id=user_id, user_role=5)
    user.active_status = 5  # Assuming 4 represents an active status for basic users, adjust as needed
    user.save()
    return JsonResponse({'message': 'Preminum account activated successfully'})


def premium_list(request):
    # Retrieve a list of users with status 2 and user role 4 (adjust as needed)
    premium_users = Users.objects.filter(active_status=5)

    # Create a list of dictionaries containing user information
    user_list = [{
        'id': user.id,
        'company_name': user.company_name,
        'full_name': user.full_name,
        'email': user.email,
        'phone': user.phone,
        # Include any additional fields as needed
    } for user in premium_users]

    # Return a JSON response with the user list
    return JsonResponse({'premium_users': user_list})


def preimum_user_details(request, user_id):
    consultant = get_object_or_404(Users, id=user_id, active_status=5)
     
    # Create a dictionary containing user details
    consultant_data = {
        'full_name': consultant.full_name,
        'email': consultant.email,
        'phone': consultant.phone,
        'company_name': consultant.company_name,
        # Include any additional fields as needed
    }

    # Return a JSON response with the user details
    return JsonResponse({'consultant': consultant_data})



def activate_account(request, user_id):
    user = get_object_or_404(Users, id=user_id)


    user.active_status = 1
    user.save()


    return JsonResponse({'message': 'Account activated successfully'})




def inactive_students_list(request):

    inactive_students = Students.objects.filter(status=0)


    student_list = [{
        'id': student.id,
        'full_name': student.full_name,
        'email': student.email,
        'phone': student.phone,
        'registration': student.created_at.strftime('%Y-%m-%d %H:%M:%S') if student.created_at else None,

        'status': student.status
    } for student in inactive_students]
    


    context = {'inactive_students': student_list}


    return render(request, 'roottemplates/student_list.html', context)


def students_details(request, student_id):
    
    student = get_object_or_404(Students, id=student_id)
    print(f"Type of 'status': {type(student.status)}")

    student_details = {
        'id': student.id,
        'full_name': student.full_name,
        'email': student.email,
        'phone': student.phone,
        'user_type': student.user_type,
        'gender': student.gender,
        'status': student.status,
        'created_at': student.created_at.strftime('%Y-%m-%d %H:%M:%S') if student.created_at else None,
    }
    print('student_details:', student_details)


    return JsonResponse({'student_details': student_details})


def activate_student_account(request, student_id):
    student = get_object_or_404(Students, id=student_id)


    student.status = 1
    student.save()


    return JsonResponse({'message': 'Student account activated successfully'})


def active_student_list(request):


    active_students = Students.objects.filter(status=1)
    active_students_details = []
    for student in active_students:
        student_details = {
            'id': student.id,
            'full_name': student.full_name,
            'email': student.email,
            'phone': student.phone,
        
            'gender': student.gender,

            'created_at': student.created_at.strftime('%Y-%m-%d %H:%M:%S') if student.created_at else None,
        }
        active_students_details.append(student_details)

    # Return a JSON response with the list of active student details
    return JsonResponse({'active_students_details': active_students_details})



def active_student_details(request, student_id):
    try:
        student = Students.objects.get(id=student_id)

        # Fetch related Results
        results = Results.objects.filter(student_id=student_id)
        results_data = serialize('json', results)

        student_details = {
            'id': student.id,
            'full_name': student.full_name,
            'email': student.email,
            'phone': student.phone,
            'address': student.address,
            'status': student.status,
            'created_at': student.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            'results': results_data,
            # Add more fields as needed
        }

        # Fetch details from the Results model
        results_details = []
        for result in results:
            result_details = {
          
              
                'secondary_board': result.secondary_board,
                'secondary_result': result.secondary_result,
                'secondary_roll_no': result.secondary_roll_no,
                'secondary_reg_no': result.secondary_reg_no,
                'secondary_certificate_no': result.secondary_certificate_no,
                'secondary_passing_year': result.secondary_passing_year,
                'secondary_certificate_copy': result.secondary_certificate_copy,
                'higher': result.higher,
                'higher_board': result.higher_board,
                'higher_result': result.higher_result,
                'higher_roll_no': result.higher_roll_no,
                'higher_reg_no': result.higher_reg_no,
                'higher_certificate_no': result.higher_certificate_no,
                'higher_passing_year': result.higher_passing_year,
                'higher_certificate_copy': result.higher_certificate_copy,
                'created_at': result.created_at.strftime('%Y-%m-%d %H:%M:%S') if result.created_at else None,
                'updated_at': result.updated_at.strftime('%Y-%m-%d %H:%M:%S') if result.updated_at else None,
            }
            results_details.append(result_details)

        return JsonResponse({'student_details': student_details, 'results_details': results_details})
    except Students.DoesNotExist:
        return JsonResponse({'error': 'Student not found'}, status=404)
    
def verify_student_account(request, student_id):
    student = get_object_or_404(Students, id=student_id)
    student.status = 2
    student.save()
    return JsonResponse({'message': 'Student account activated successfully'})


def verify_student_list(request):
    # Filter students with status code 1 (Active)
    verify_students = Students.objects.filter(status=2)

    # Prepare a list of active student details
    verify_students_details = []
    for student in verify_students:
        student_details = {
            'id': student.id,
            'full_name': student.full_name,
            'email': student.email,
            'phone': student.phone,
        
            'gender': student.gender,

            'created_at': student.created_at.strftime('%Y-%m-%d %H:%M:%S') if student.created_at else None,
        }
        verify_students_details.append(student_details)

    # Return a JSON response with the list of active student details
    return JsonResponse({'verify_students_details': verify_students_details})


def verify_student_details(request, student_id):
    try:
        student = Students.objects.get(id=student_id)

        # Fetch related Results
        results = Results.objects.filter(student_id=student_id)
        results_data = serialize('json', results)

        student_details = {
            'id': student.id,
            'full_name': student.full_name,
            'email': student.email,
            'phone': student.phone,
            'address': student.address,
            'status': student.status,
            'created_at': student.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            'results': results_data,
           
        }

      
        results_details = []
        for result in results:
            result_details = {
          
              
                'secondary_board': result.secondary_board,
                'secondary_result': result.secondary_result,
                'secondary_roll_no': result.secondary_roll_no,
                'secondary_reg_no': result.secondary_reg_no,
                'secondary_certificate_no': result.secondary_certificate_no,
                'secondary_passing_year': result.secondary_passing_year,
                'secondary_certificate_copy': result.secondary_certificate_copy,
                'higher': result.higher,
                'higher_board': result.higher_board,
                'higher_result': result.higher_result,
                'higher_roll_no': result.higher_roll_no,
                'higher_reg_no': result.higher_reg_no,
                'higher_certificate_no': result.higher_certificate_no,
                'higher_passing_year': result.higher_passing_year,
                'higher_certificate_copy': result.higher_certificate_copy,
                'created_at': result.created_at.strftime('%Y-%m-%d %H:%M:%S') if result.created_at else None,
                'updated_at': result.updated_at.strftime('%Y-%m-%d %H:%M:%S') if result.updated_at else None,
            }
            results_details.append(result_details)

        return JsonResponse({'student_details': student_details, 'results_details': results_details})
    except Students.DoesNotExist:
        return JsonResponse({'error': 'Student not found'}, status=404)
    




def consultant_credit_balance(request):
    if request.method == 'POST':
        consultant_id = request.POST.get('consultant_id')
        payment_method = request.POST.get('payment_method')
        payment_status = request.POST.get('payment_status')
        reference = request.POST.get('reference')
        amount = request.POST.get('amount')

        # Perform validation and update database accordingly
        # Example: Assuming you have a Balances model with appropriate fields

        try:
            balance = Balances.objects.create(
                acc_pay_to=consultant_id,
                pay_method=payment_method,
                payment_status=payment_status,
                acc_pay_ref=reference,
                acc_credit=amount,
                acc_deal_type=1,
                created_at=datetime.now(),
                updated_at=datetime.now() # Assuming 1 represents deal_type credit
            )

            # You might want to perform additional actions or checks here

            messages.success(request, 'Credit balance added successfully.')
        except Exception as e:
            messages.error(request, f'Error: {e}')

        return redirect('consultant_credit_balance')  # Redirect to the same page after submission

    # Handle GET requests or other scenarios
    # Add logic as needed

    # You may need to retrieve the list of consultants for the dropdown
    consultants = Users.objects.filter(user_role=5)  # Assuming user_role=5 corresponds to consultants

    # Pass the payment method and payment status choices to the template
    payment_method_choices = Balances._meta.get_field('pay_method').choices
    payment_status_choices = Balances._meta.get_field('payment_status').choices

    context = {
        'consultants': consultants,
        'payment_method_choices': payment_method_choices,
        'payment_status_choices': payment_status_choices,
    }
    return render(request, 'roottemplates/consultant_credit_balance.html', context)


def consultant_rates(request):
    # Retrieve all consultants
    consultants = Users.objects.filter(user_role=5)  # Assuming user_role=5 corresponds to consultants

    # Pass the consultants to the template
    context = {'consultants': consultants}
    return render(request, 'roottemplates/consultant_rates.html', context)


def get_existing_rates(request, consultant_id):
    existing_rates = Rates.objects.filter(rate_added_to=consultant_id).first()
    if existing_rates:
        return JsonResponse({
            'success': True,
            'existing_rates': {
                'first_rate': existing_rates.first_rate,
                'second_rate': existing_rates.second_rate,
                'third_rate': existing_rates.third_rate,
                'four_rate': existing_rates.four_rate,
                'five_rate': existing_rates.five_rate,
            },
        })
    return JsonResponse({'success': False, 'message': 'No existing rates for the given consultant.'})

def add_or_update_rates(request, consultant_id):
    if request.method == 'POST':
        # Retrieve the consultant
        consultant = get_object_or_404(Users, id=consultant_id)

        # Retrieve rate data from the POST request
        first_rate = request.POST.get('first_rate')
        second_rate = request.POST.get('second_rate')
        third_rate = request.POST.get('third_rate')
        four_rate = request.POST.get('four_rate')
        five_rate = request.POST.get('five_rate')

        # Get existing rates
        existing_rates = Rates.objects.filter(rate_added_to=consultant_id)


        # If rates are already added, update them
        if existing_rates.exists():
            existing_rates = existing_rates.first()
            existing_rates.first_rate = first_rate
            existing_rates.second_rate = second_rate
            existing_rates.third_rate = third_rate
            existing_rates.four_rate = four_rate
            existing_rates.five_rate = five_rate
            existing_rates.save()
        else:
            # If rates are not added, create a new record
            Rates.objects.create(
                rate_added_by=request.user.id,
                rate_added_to=consultant.id,
                first_rate=first_rate,
                second_rate=second_rate,
                third_rate=third_rate,
                four_rate=four_rate,
                five_rate=five_rate,
            )

        # Return a JsonResponse with success message
        return JsonResponse({'success': True, 'message': 'Rates added/updated successfully.'})
    



def add_address(request):
    existing_address = None

    if request.method == 'POST':
        # Assuming you get the address details from the request, modify as needed
        office_name = request.POST.get('office_name')
        address = request.POST.get('address')
        hotline = request.POST.get('hotline')
        phone = request.POST.get('phone')
        email = request.POST.get('email')

        # Set root_id based on the id of the currently logged-in user
        root_id = request.user.id if request.user.is_authenticated else None

        try:
            # Try to create a new address with a unique root_id
            new_address = Addresses.objects.create(
                office_name=office_name,
                address=address,
                hotline=hotline,
                phone=phone,
                email=email,
                root_id=root_id
            )
            messages.success(request, 'Address added successfully!')
        except IntegrityError:
            # If a duplicate root_id is detected, get the existing address
            existing_address = Addresses.objects.get(root_id=root_id)

            # Update the existing address with the new details
            existing_address.office_name = office_name
            existing_address.address = address
            existing_address.hotline = hotline
            existing_address.phone = phone
            existing_address.email = email
            existing_address.save()
            messages.success(request, 'Address updated successfully!')

         # Redirect to a view that lists all addresses

    # Fetch existing address for the current root_id if it exists
    existing_address = Addresses.objects.filter(root_id=request.user.id).first()

    return render(request, 'roottemplates/add_address.html', {'existing_address': existing_address})