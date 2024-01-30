from django.shortcuts import render,redirect
from .models import *
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import check_password
from datetime import datetime
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponse
from .serializers import ModelJSONEncoder
from django.db.models import Sum
from django.shortcuts import render, redirect
from .models import Maps, ConsultantDetails
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.db.models import Avg, F, ExpressionWrapper, fields
from django.db.models import F, Q
from django.db.models import Subquery, OuterRef
from django.db.models.functions import ExtractMonth, ExtractYear
from django.db.models import Count, F
from django.db.models import Sum, F, Case, When, Value, FloatField
from django.db.models.functions import TruncMonth
from django.contrib import messages
from django.http import HttpResponseServerError
from django.contrib.auth.decorators import login_required, user_passes_test

def is_consultant(user):
    return user.is_authenticated and user.user_type == 1


@login_required(login_url='login_user')
@user_passes_test(is_consultant, login_url='login_user')
def consultant_home(request):
    # Assuming consultant_id is related to the user
    consultant_id = request.user.id
    consultant = get_object_or_404(Users, id=consultant_id, user_role=5)

  

    # Calculate total credit and debit for the consultant
    total_credit = Balances.objects.filter(acc_pay_to=consultant_id).aggregate(Sum('acc_credit'))['acc_credit__sum'] or 0.0
    total_debit = Balances.objects.filter(acc_paid_by=consultant_id).aggregate(Sum('acc_debit'))['acc_debit__sum'] or 0.0
    print('total_debit:', total_debit)
    
    # Calculate total balance
    total_balance = total_credit - total_debit
    print("total_balance:", total_balance)

    # Count the number of students for the consultant
    total_students = Levels.objects.filter(consultant_id=consultant_id, status=1).count()
    total_students_all =  Students.objects.count()
    average_students = total_students_all / total_students if total_students != 0 else 0
    new_students_count = Students.objects.filter(
        ~Q(id__in=Subquery(Levels.objects.filter(consultant_id=OuterRef('id')).values('student_id')))
    ).count()
    print('new_students_count:', new_students_count)
    return render(request, 'Hodviews/index.html', {'total_balance': total_balance,  'total_students': total_students,'total_debit':total_debit,'average_students':average_students,'new_students_count':new_students_count,'consultant':consultant })

@login_required(login_url='login_user')
@user_passes_test(is_consultant, login_url='login_user')
def monthly_balance_chart(request):
    consultant_id = request.user.id

    # Get total credit and debit per month
    monthly_data = Balances.objects.filter(
        Q(acc_pay_to=consultant_id) | Q(acc_paid_by=consultant_id)
    ).annotate(month=TruncMonth('created_at')).values('month').annotate(
        total_credit=Sum('acc_credit'),
        total_debit=Sum('acc_debit')
    ).order_by('month')

    # Prepare data for chart
    labels = [entry['month'].strftime('%B %Y') for entry in monthly_data]
    credit_data = [entry['total_credit'] or 0.0 for entry in monthly_data]
    debit_data = [entry['total_debit'] or 0.0 for entry in monthly_data]

    # Prepare data to pass to the template
    chart_data = {
        'labels': labels,
        'credit_data': credit_data,
        'debit_data': debit_data,
    }

    return JsonResponse(chart_data)

@login_required(login_url='login_user')
@user_passes_test(is_consultant, login_url='login_user')
def consultant_ratings_json(request):
    consultant_id = request.user.id

    ratings = Review.objects.filter(consultant=consultant_id).values_list('rating', flat=True)
    average_rating = sum(ratings) / len(ratings) if ratings else 0

    # Set the highest rating to 5
    highest_rating = 5

    # Send the data in the format expected by the chart
    data = {
        'labels': ['Average Rating', 'Highest Rating'],
        'values': [average_rating, highest_rating],
    }

    return JsonResponse({'ratings_data': data})
@login_required(login_url='login_user')
@user_passes_test(is_consultant, login_url='login_user')
def consultant_gallery(request):
    print("User ID from request:", request.user.id)
    print("User: ", request.user)
    if request.method == 'POST':
        image = request.FILES.get('image')
        caption = request.POST.get('caption')
        print('image: ', image)

        consultant_id = request.user.id
        if image and caption and consultant_id:
            ConsultantImages.objects.create(
                image=image,
                caption=caption,
                consultant_id=consultant_id,
                created_at=timezone.now(),
                updated_at=timezone.now()
            )
            return redirect('consultant_gallery')  # Redirect to the same page after successful submission
        error_message = "Please provide all required information."
        return render(request, 'Hodviews/gallery.html', {'error_message': error_message})
    elif request.method == 'GET':
        # Filter images based on the correct consultant_id
        consultant_id = request.user.id  # Assuming the correct consultant_id is stored in the user model
        print("Consultant ID used for filtering images:", consultant_id)
        images = ConsultantImages.objects.filter(consultant_id=consultant_id)
        # for image in images:
        return render(request, 'Hodviews/gallery.html', {'images': images})
@login_required(login_url='login_user')
@user_passes_test(is_consultant, login_url='login_user')
def consultant_profile(request):
    if request.user.is_authenticated:
        print('user: ', request.user.email)
        user_id = request.user.id
        user = Users.objects.get(id=user_id)
        print('est. date: ', user.est_date)
        context = {
            'user': user,
        }
    return render(request, 'Hodviews/consultant_profile.html', context)

@login_required(login_url='login_user')
def save_consultant_profile(request, user_id):
    if request.method == 'POST' and request.user.is_authenticated:
        user = request.user
        if user.id == int(user_id):
            company_name = request.POST.get('company_name')
            full_name = request.POST.get('full_name')
            phone = request.POST.get('phone')
            land_phone = request.POST.get('land_phone')
            fax_no = request.POST.get('fax_no')
            date_str = request.POST.get('est_date')
            address = request.POST.get('address')
            website = request.POST.get('website')
            experience= request.POST.get('experience')
            designation= request.POST.get('designation')
            about = request.POST.get('about')
            old_password = request.POST.get('old_password')
            new_password = request.POST.get('new_password')
            confirm_password = request.POST.get('confirm_password')
            consultant_img = request.FILES.get('consultant_img')
            print('company_name: ', company_name)
            print('full_name: ', full_name)
            print('phone: ', phone)
            print('land_phone: ', land_phone)
            print('fax_no: ', fax_no)
            print('est_date: ', date_str)
            print('address: ', address)
            print('experiance: ', experience)
            print('website: ', website)
            print('about: ', about)
            print('consultant_img: ', consultant_img)
            consultant_id = int(user_id)
            consultant = Users.objects.get(id=consultant_id)
            if company_name and full_name and phone and date_str and address and website and about:
                
                consultant.company_name = company_name
                consultant.full_name = full_name
                consultant.phone = phone
                consultant.address = address
                consultant.website = website

                
                
                consultant.about = about
                if land_phone:
                    consultant.land_phone = land_phone
                if fax_no:
                    consultant.fax_no = fax_no
                if consultant_img:
                    consultant.consultant_img = consultant_img
                try:
                    est_date = datetime.strptime(date_str, "%B %d, %Y").strftime("%Y-%m-%d")
                except:
                    try:
                        est_date = datetime.strptime(date_str, "%b. %d, %Y").strftime("%Y-%m-%d")
                    except:
                        try:
                            est_date = date_str
                        except:
                            return JsonResponse({'error': 'Error parsing date'})
                if old_password and  new_password and confirm_password:
                    if new_password == confirm_password:
                        if check_password(new_password, user.password):
                            user.set_password(new_password)
                        else:
                            return JsonResponse({'error': 'Wrong old password'})
                    else:
                        return JsonResponse({'error': 'Passwords do not match'})
                user.save()
                consultant.save()
                consultant_details = ConsultantDetails.objects.get(consultant_id=consultant_id)
                consultant_details.experience = experience
                consultant_details.consultant_designation=designation
                consultant_details.save()

                print("consultant_details:")
                return JsonResponse({'success': True})
            else:
                return JsonResponse({'error': 'Please fill up all the required fields'})
        else:
            return JsonResponse({'error': 'Cannot update your account information due to security reasons'})
    else:
        return JsonResponse({'error': 'Invalid request'})
    


@login_required(login_url='login_user')
@user_passes_test(is_consultant, login_url='login_user')
def consultant_logo(request):
    if request.user.is_authenticated:
        user = request.user
        consultant = Users.objects.get(id=user.id)
        consultant_details, created_at = ConsultantDetails.objects.get_or_create(consultant_id=consultant.id)
        print('consultant_details logo: ', consultant_details.consultant_logo)
        context = {
            'consultant': consultant,
            'consultant_details': consultant_details,
        }
    return render(request, 'Hodviews/consultant_logo.html', context)
def save_logo(request):
    if request.method == 'POST':
        if request.user.is_authenticated:
            consultant_logo = request.FILES.get('logo')
            user = request.user
            consultant = Users.objects.get(id=user.id)
            consultant_details, created_at = ConsultantDetails.objects.get_or_create(consultant_id=consultant.id)
            print('consultant_logo: ', consultant_logo)
            consultant_details.consultant_logo = consultant_logo
            consultant_details.save()
            return JsonResponse({'success': True})
        else:
            return JsonResponse({'error': 'Unauthorized User'})



@login_required(login_url='login_user')
@user_passes_test(is_consultant, login_url='login_user')
def consultant_requirement(request):
    user = request.user
    consultant_details, created = ConsultantDetails.objects.get_or_create(consultant_id=user.id)

    if request.method == 'POST':
        consultant_requirement = request.POST.get('consultant_requirement')

        if consultant_details is not None:
            consultant_details.consultant_requirement = consultant_requirement
            consultant_details.status = consultant_details.status if consultant_details.status is not None else 1
            consultant_details.created_at = timezone.now()
            consultant_details.updated_at = timezone.now()
            consultant_details.save()

            messages.success(request, 'Consultant requirement updated successfully.')
            return redirect('consultant_requirement')

        messages.error(request, 'Error updating consultant requirement.')

    return render(request, 'Hodviews/consultant_requirement.html', {'consultant_details': consultant_details, 'created': created})



@login_required(login_url='login_user')
@user_passes_test(is_consultant, login_url='login_user')
def consultant_country(request):
    consultant_id = request.user.id

    all_countries = Countries.objects.all()

    saved_countries = ConsultantDetails.objects.filter(
        consultant_id=consultant_id,
        consultant_countries__isnull=False
    ).values('consultant_countries__country_id', 'consultant_countries__country_name').distinct()
    if request.method == 'POST':
        consultant_country_id = request.POST.get('consultant_countries')
        if consultant_country_id:

            selected_country = Countries.objects.get(country_id=consultant_country_id)
            print('selected_country:', selected_country)

            consultant_details, created = ConsultantDetails.objects.get_or_create(consultant_id=consultant_id)
           
            consultant_details.consultant_countries.add(selected_country)

            return redirect('consultant_country')  

    return render(request, 'Hodviews/consultant_country.html', {'saved_countries': saved_countries, 'all_countries': all_countries})






def delete_country(request):
    # Check if the request is a POST request and an Ajax request
    if request.method == 'POST' and request.headers.get('x-requested-with') == 'XMLHttpRequest':
        # Get the current user's consultant ID
        consultant_id = request.user.id
        # Get the country name from the POST data
        country_name = request.POST.get('country_name')
        try:
            # Get the ConsultantDetails instance for the current consultant
            consultant_details = get_object_or_404(ConsultantDetails, consultant_id=consultant_id)
            # Get the corresponding country instance
            country = get_object_or_404(Countries, country_name=country_name)
            # Remove the selected country from the consultant_details
            consultant_details.consultant_countries.remove(country)
            # Return a JSON response indicating success
            return JsonResponse({'success': True})
        except ConsultantDetails.DoesNotExist:
            # Return a JSON response indicating failure (ConsultantDetails not found)
            return JsonResponse({'success': False, 'error': 'ConsultantDetails not found'})
        except Countries.DoesNotExist:
            # Return a JSON response indicating failure (Country not found)
            return JsonResponse({'success': False, 'error': 'Country not found'})
        except Exception as e:
            # Return a JSON response indicating failure with the specific error message
            return JsonResponse({'success': False, 'error': f'An error occurred: {str(e)}'})
    # Return a JSON response indicating failure for invalid requests
    return JsonResponse({'success': False, 'error': 'Invalid request'})




@login_required(login_url='login_user')
@user_passes_test(is_consultant, login_url='login_user')
def consultant_scholarship(request):
    success_message = None

    if request.method == 'POST':
        schp_description = request.POST.get('schp_description')
        apply_process = request.POST.get('apply_process')
        
        # Assuming consultant_id should be set to the currently logged-in user's ID
        consultant_id = request.user.id

        # Current timestamp for created_at and updated_at
        now = timezone.now()

        try:
            # Create a new scholarship instance
            scholarship = ScholarShips.objects.create(
                schp_description=schp_description,
                apply_process=apply_process,
                consultant_id=consultant_id,
                created_at=now,
                updated_at=now
            )

            # Set the success message
            success_message = "Scholarship added successfully."

        except Exception as e:
            
            return render(request, 'Hodviews/consultant_scholarship.html', {'error_message': f"Error: {e}"})

    # Render a form or any other relevant content for GET requests
    return render(request, 'Hodviews/consultant_scholarship.html', {'success_message': success_message})






@login_required(login_url='login_user')
@user_passes_test(is_consultant, login_url='login_user')
def consultant_map(request):
    success_message = None
    error_message = None
    existing_map_location = None  # Initialize with None

    if request.method == 'POST':
        map_location = request.POST.get('map_location')
        consultant_id = request.user.id
        now = timezone.now()

        try:
            map_instance = Maps.objects.get(consultant_id=consultant_id)
            existing_map_location = map_instance.map_location  # Set existing_map_location if it exists

            map_instance.map_location = map_location
            map_instance.updated_at = now
            map_instance.save()

            success_message = "Map updated successfully."

        except Maps.DoesNotExist:
            # If the map doesn't exist, create a new one
            map_instance = Maps.objects.create(
                map_location=map_location,
                consultant_id=consultant_id,
                created_at=now,
                updated_at=now
            )

            consultant_details = ConsultantDetails.objects.get(consultant_id=consultant_id)
            consultant_details.consultant_maplocations.add(map_instance)

            success_message = "Map added successfully."

        except ConsultantDetails.DoesNotExist:
            error_message = "Error: ConsultantDetails not found for the given consultant_id."
        except Exception as e:
            error_message = f"Error: {str(e)}"

    else:
        # If it's a GET request, try to retrieve the existing map_location
        consultant_id = request.user.id
        try:
            map_instance = Maps.objects.get(consultant_id=consultant_id)
            existing_map_location = map_instance.map_location  # Set existing_map_location if it exists
        except Maps.DoesNotExist:
            pass  # Handle the case when the map doesn't exist

    return render(request, 'Hodviews/consultant_map.html', {'success_message': success_message, 'error_message': error_message, 'existing_map_location': existing_map_location})

def linkpage(request):
    return render(request,'Hodviews/linkpage.html')



from django.shortcuts import render, redirect
from django.utils import timezone
from .models import Colors
@login_required(login_url='login_user')
@user_passes_test(is_consultant, login_url='login_user')
def consultant_color(request):
    consultant_id = request.user.id

    try:
        consultant_colors = Colors.objects.get(consultant_id=consultant_id)
    except Colors.DoesNotExist:
        consultant_colors = None

    success_message = None
    error_message = None

    if request.method == 'POST':
        header_color = request.POST.get('header_color')
        content_color = request.POST.get('content_color')
        footer_color = request.POST.get('footer_color')

        print("header_color:", header_color)
        print("content_color:", content_color)
        print("footer_color:", footer_color)

        if header_color is not None and content_color is not None and footer_color is not None:
            now = timezone.now()

            try:
                if consultant_colors:
                    consultant_colors.header_color = header_color
                    consultant_colors.content_color = content_color
                    consultant_colors.footer_color = footer_color
                    consultant_colors.updated_at = now
                    consultant_colors.save()
                else:
                    Colors.objects.create(
                        header_color=header_color,
                        content_color=content_color,
                        footer_color=footer_color,
                        consultant_id=consultant_id,
                        created_at=now,
                        updated_at=now
                    )

                success_message = "Color settings successfully saved."
            except Exception as e:
                error_message = f"Error saving colors: {str(e)}"
                print(error_message)
                return HttpResponseServerError(error_message)

    return render(request, 'Hodviews/consultant_color.html', {
        'consultant_colors': consultant_colors,
        'success_message': success_message,
        'error_message': error_message
    })

@login_required(login_url='login_user')
@user_passes_test(is_consultant, login_url='login_user')
def consultant_intro(request):
    # Initialize variables
    success_message = None
    consultant = None
    customize = None

    if request.method == 'POST':
        # Retrieve form data from the POST request
        consultant_bio = request.POST.get('consultant_bio')
        consultant_intro = request.POST.get('consultant_intro')
        consultant_description = request.POST.get('consultant_description')

        # Get the currently logged-in user
        user = request.user
        consultant_id = user.id

        # Current timestamp for created_at and updated_at
        now = timezone.now()

        try:
            # Attempt to retrieve the existing consultant details
            consultant = ConsultantDetails.objects.get(consultant_id=consultant_id)
            consultant.consultant_bio = consultant_bio
            consultant.consultant_intro = consultant_intro
            consultant.consultant_description = consultant_description
            consultant.updated_at = now
            consultant.save()

            # Update or create Customizes instance based on consultant_id
            customize, created = Customizes.objects.update_or_create(
                consultant_id=consultant_id,
                defaults={
                    'description': consultant_description,
                    'image': request.FILES.get('image'),  # Assuming the file input name is 'image'
                    'status': 1
                }
            )

            success_message = "Consultant details updated successfully."

        except ConsultantDetails.DoesNotExist:
            # If consultant details do not exist, create a new instance
            consultant = ConsultantDetails.objects.create(
                consultant_id=consultant_id,
                consultant_bio=consultant_bio,
                consultant_intro=consultant_intro,
                consultant_description=consultant_description,
                created_at=now,
                updated_at=now
            )

            # Create Customizes instance for the new consultant
            customize = Customizes.objects.create(
                consultant_id=consultant_id,
                image=request.FILES.get('image'),  # Assuming the file input name is 'image'
                status=1
            )

            success_message = "Consultant details added successfully."

    # Retrieve the latest consultant details for display
    consultant = ConsultantDetails.objects.filter(consultant_id=request.user.id).first()
    customize = Customizes.objects.filter(consultant_id=request.user.id).first()


    # Render the template with relevant context
    return render(request, 'Hodviews/consultant_intro.html', {
        'success_message': success_message,
        'consultant': consultant,
        'customize': customize
    })
@login_required(login_url='login_user')
@user_passes_test(is_consultant, login_url='login_user')
def student_list(request):
    students = Students.objects.all()
    student_details = StudentDetails.objects.all()

    student_levels = []

    # Retrieve "My Lead" data using the update_my_lead view
    my_lead_data = update_my_lead(request)
    print("my_lead_data:", my_lead_data);

    for student in students:
        # Retrieve all matching StudentDetails records for the current student
        student_details_list = StudentDetails.objects.filter(dets_regs_id=student.id)

        # If there are no matching records, skip the current student
        if not student_details_list.exists():
            continue

        for student_detail in student_details_list:
            consultants_viewed_count = Levels.objects.filter(student_id=student.id).order_by('-created_at').first()

            if consultants_viewed_count is None:
                level = 1
            elif consultants_viewed_count.level_1 is not None:
                level = 2
            elif consultants_viewed_count.level_2 is not None:
                level = 3
            elif consultants_viewed_count.level_3 is not None:
                level = 4
            else:
                level = 5

            # Check if the current student has the consultant in their favorites list
            is_favorite = False
            if student_detail.dets_favconsultantlist and str(request.user.id) in student_detail.dets_favconsultantlist.split(','):
                is_favorite = True

            student_levels.append({'student': student, 'level': level, 'is_favorite': is_favorite, 'student_detail': student_detail})

    context = {
        'student_levels': student_levels,
        'student_details': student_details,
        'my_lead_included': my_lead_data,  # Include "My Lead" data in the context
    }

    return render(request, 'Hodviews/student_list.html', context)

@login_required(login_url='login_user')
@user_passes_test(is_consultant, login_url='login_user')
def update_my_lead(request):
    user = request.user

    student_levels = Levels.objects.filter(consultant_id=user.id)

    data = []
    for student_level in student_levels:
        for i in range(1, 6):
            student_id_field = getattr(student_level, f'level_{i}', None)
            if student_id_field is not None:
                student = Students.objects.get(id=student_id_field)
                data.append({
                    'id': student.id,
                    'full_name': student.full_name,
                    'email': student.email,
                    'phone': student.phone,
                    'gender': student.gender,
                    'address': student.address,
                    'country_name': student.countries.first().country_name if student.countries.first() else 'N/A',
                })

    return data


def get_consultant_balance(consultant_id):

    total_credit = Balances.objects.filter(acc_pay_to=consultant_id).aggregate(Sum('acc_credit'))['acc_credit__sum'] or 0.0
    total_debit = Balances.objects.filter(acc_paid_by=consultant_id).aggregate(Sum('acc_debit'))['acc_debit__sum'] or 0.0
    current_balance = total_credit - total_debit
    return current_balance



@login_required(login_url='login_user')
@user_passes_test(is_consultant, login_url='login_user')
def update_balance(request, lead, student_id):
    student = get_object_or_404(Students, id=student_id)
    student_details = StudentDetails.objects.filter(dets_regs_id=student_id).first()
    # Get the rates for the current consultant
    rates_data = Rates.objects.filter(rate_added_to=request.user.id).first()
    if not rates_data:
        return JsonResponse({"error": "Rate not found for the consultant and student combination."})
    # Determine the rate based on the lead
    if lead == 1:
        rate = rates_data.first_rate
    elif lead == 2:
        rate = rates_data.second_rate
    elif lead == 3:
        rate = rates_data.third_rate
    elif lead == 4:
        rate = rates_data.four_rate
    elif lead == 5:
        rate = rates_data.five_rate
    else:
        rate = 0.0
    # Check if there is sufficient balance
    current_balance = get_consultant_balance(request.user.id)
    if current_balance < rate:
        return JsonResponse({"error": "Insufficient balance."})
    else:
        # Deduct the rate from the balance
        balance = Balances(
            acc_paid_by=request.user.id,
            acc_pay_to=student_id,
            acc_debit=rate,  # Deduct the rate
            created_at=timezone.now(),
            updated_at=timezone.now(),
        )
        balance.save()
        # Check the current level of the student
        # current_level = getattr(student, f'level_{lead}', None)
        # If the current level is None or less than the lead, update it to the lead
        # if current_level is None or current_level < lead:
        # print('lead: ', lead)
        # print('current level: ', current_level)
        # print('done')
        # setattr(student, f'level_{lead}', student.id)
        # student.save()
        # Save the level information in the Levels model
        
        level_model = Levels(
            balance_id=balance.id,
            student_id=student.id,
            consultant_id=request.user.id,
            status=1,  # You may need to adjust this based on your logic
            created_at=timezone.now(),
            updated_at=timezone.now(),
        )

        # set the level of the student with stduent id in the corresponding level
        setattr(level_model, f'level_{lead}', student.id)
        level_model.save()

        student_data = {
            "id": student.id,
            "full_name": student.full_name,
            "student_user": student.student_user.id,
            "email": student.email,
            "phone": student.phone,
            "address": student.address,
            "phone": student.phone,
            "gender": student.gender,
        }

        context = {'lead': lead, 'student_level': {'student': student_data, 'level': lead}, 'student_details': student_details, }
        # Return JSON response
        return JsonResponse(context, encoder=ModelJSONEncoder)
    


@login_required(login_url='login_user')
@user_passes_test(is_consultant, login_url='login_user')
def consultant_feedback_list(request):
    consultant_id = request.user.id
    feedback_list = HomeFeedback.objects.filter(consultant=consultant_id)
    
    # Get the count of new notifications
    new_notifications_count = feedback_list.filter(fdk_status=1).count()

    return render(request, 'Hodviews/consultant_feedback_list.html', {'feedback_list': feedback_list, 'consultant_id': consultant_id, 'new_notifications_count': new_notifications_count})

@login_required(login_url='login_user')
@user_passes_test(is_consultant, login_url='login_user')
def feedback_details_modal(request, feedback_id):
    feedback = get_object_or_404(HomeFeedback, id=feedback_id)
    return JsonResponse({'msg': feedback.fdk_msg})


@login_required(login_url='login_user')
@user_passes_test(is_consultant, login_url='login_user')
def delete_feedback(request, feedback_id):
    feedback = get_object_or_404(HomeFeedback, id=feedback_id)
    feedback.delete()
    return JsonResponse({'message': 'Feedback deleted successfully'})