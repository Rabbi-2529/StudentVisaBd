from django.shortcuts import render
from .models import *
from django.contrib.auth import authenticate, login, logout
from .emailBackend import EmailBackend
from django.shortcuts import redirect
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.contrib import messages
import re, random, requests
from datetime import datetime, timedelta
from django.core.serializers import serialize
from django.urls import reverse
from .serializers import ThanaSerializer
from django.utils.safestring import mark_safe
from django.shortcuts import render, get_object_or_404
import json
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.hashers import make_password
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import F, Case, When, Value, IntegerField
from time import time
from django.http import Http404
# Create your views here.
def home(request):
    costomize = Customizes.objects.all()
    
    # Retrieve the top 10 consultants based on their ratings
    top_consultants = Users.objects.filter(user_role=5).order_by('-rating')[:4]

    # Retrieve ConsultantDetails for each top consultant
    consultant_details = []
    for consultant in top_consultants:
        details = ConsultantDetails.objects.filter(consultant_id=consultant.id).first()
        consultant_details.append(details)
    
    return render(request, 'index.html', {'top_consultants': zip(top_consultants, consultant_details), 'costomize': costomize})


def signup_user(request):
    districts = District.objects.all()
    signup_type = 'consultant'
    for district in districts:
        print('District name: ', district.name)
    thanas = Thana.objects.filter(district_id=1)
    for thana in thanas:
        print('Thana name: ', thana.name)
    context = {
        'districts': districts,
        'signup_type': signup_type
    }
    return render(request, 'user_login/signup_user.html', context)



def signup_student(request):
    districts = District.objects.all()
    countries = Countries.objects.all()
    signup_type = 'student'
    # # students = Students.objects.get()
    # student_countries = students.countries.all()
    # print('student_countries: ', student_countries)
    # for country in student_countries:
    #     print('Country name: ', country.country_name)
    context = {
        'districts': districts,
        'countries': countries,
        'signup_type': signup_type
    }
    return render(request, 'user_login/signup_student.html', context)

def redirect_to_otp(request):
    if request.method == 'POST':
        signup_type = request.POST.get('signup_type')
        # data = json.loads(request.body)
        # print('daat get: ', data)
        print('signup_type: ', signup_type)
        if signup_type and signup_type == 'consultant':
            company_name = request.POST.get('company_name')
            est_date = request.POST.get('date')
            website = request.POST.get('website')
            phone = request.POST.get('phone')
            email = request.POST.get('email')
            full_name = request.POST.get('owner_name')
            land_phone = request.POST.get('telephone')
            fax_no = request.POST.get('fax')
            district_id = request.POST.get('district_name')
            thana_id = request.POST.get('thana_name')
            address = request.POST.get('office_address')
            password = request.POST.get('password')
            print('-----------------------------------------')
            print('signup_type: ', signup_type)
            print('company_name: ', company_name)
            print('est_date: ', est_date)
            print('website: ', website)
            print('phone: ', phone)
            print('email: ', email)
            print('website: ', website)
            print('full_name: ', full_name)
            print('land_phone: ', land_phone)
            print('fax_no: ', fax_no)
            print('district_id: ', district_id)
            print('thana_id: ', thana_id)
            print('address: ', address)
            print('password: ', password)
            print('-----------------------------------------')
            if company_name and est_date and phone and email and full_name and district_id and thana_id and address and password:
                consultant_company = Users.objects.filter(company_name=company_name).first()
                consultant_phone = Users.objects.filter(phone=phone).first()
                consultant_email = Users.objects.filter(email=email).first()
                valid_phone_number = re.match(r'^(013|019|018|014|015|016)\d{8}$', phone)
                if consultant_company is None:
                    if consultant_phone is None:
                        if consultant_email is None:
                            if valid_phone_number:
                                temp_user_data = {
                                    'full_name': full_name,
                                    'company_name': company_name,
                                    'email': email,
                                    'est_date': est_date,
                                    'phone': phone,
                                    'district_id': district_id,
                                    'thana_id': thana_id,
                                    'address': address,
                                    'password': password,
                                }
                                if website:
                                    temp_user_data['website'] = website
                                if land_phone:
                                    temp_user_data['land_phone'] = land_phone
                                if fax_no:
                                    temp_user_data['fax_no'] = fax_no
                                # Generate and send OTP
                                otp = str(random.randint(1000, 9999))
                                expiration_time = datetime.now() + timedelta(minutes=15)
                                temp_user_data['expiration_time'] = expiration_time.strftime('%Y-%m-%d %H:%M:%S')
                                temp_user_data['otp'] = otp
                                request.session['temp_user_data'] = temp_user_data

                                # Send OTP via SMS API
                                url = f'http://sms.iglweb.com/api/v1/send?api_key=4451706354992151706354992&contacts=88{phone}&senderid=01844532630&msg={otp} is your activation code in Student Visa Bd.This code will expire in 2 Hours.For help,call:01958666999'
                                response = requests.get(url)

                                if response.status_code == 200:
                                    # Store OTP in session for validation
                                    print('OTP: ', otp)
                                    print('temp_user_data before redirecting: ', temp_user_data['full_name'])
                                    return JsonResponse({'success': True, 'redirect_url': '/otp_verification_signup/'})
                                # return redirect('otp_verification_signup')
                            else:
                                return JsonResponse({'errors': 'Invalid phone number'})
                        else:
                            return JsonResponse({'errors': 'A user with this email already exists'})
                    else:
                        return JsonResponse({'errors': 'A user with this phone already exists'})
                else:
                    return JsonResponse({'errors': f"The Company '{company_name}' already exists"})
            else:
                return JsonResponse({'errors': 'Please fill up all the required fields'})
        if signup_type and signup_type == 'student':
            # data = json.loads(request.body)
            full_name = request.POST.get('full_name')
            email = request.POST.get('email')
            phone = request.POST.get('phone')
            user_type = request.POST.get('user_type')
            gender = request.POST.get('gender')
            address = request.POST.get('address')
            district_id = request.POST.get('district_name')
            thana_id = request.POST.get('thana_name')
            countries = request.POST.get('countries')
            password = request.POST.get('password')
            # since there can be multiple countries, those are will be taken as json format
            countries_json = json.loads(request.POST['countries'])
            print('----------------------------------------------------')
            print('full_name: ', full_name)
            print('email: ', email)
            print('phone: ', phone)
            print('user_type: ', user_type)
            print('gender: ', gender)
            print('address: ', address)
            print('district_id: ', district_id)
            print('thana_id: ', thana_id)
            print('countries: ', countries)
            print('countries_json: ', countries_json)
            print('----------------------------------------------------')
            if full_name and email and phone and user_type and gender and address and district_id and thana_id and countries and password:
                consultant_phone = Students.objects.filter(phone=phone).first()
                consultant_email = Students.objects.filter(email=email).first()
                valid_phone_number = re.match(r'^(013|019|018|014|015|016)\d{8}$', phone)
                if consultant_phone is None:
                    if consultant_email is None:
                        if valid_phone_number:
                            temp_user_data = {
                                'full_name': full_name,
                                'email': email,
                                'phone': phone,
                                'user_type': user_type,
                                'gender': gender,
                                'district_id': district_id,
                                'thana_id': thana_id,
                                'address': address,
                                'countries': countries_json,
                                'password': password,
                            }
                            # Generate and send OTP
                            otp = str(random.randint(1000, 9999))
                            expiration_time = datetime.now() + timedelta(minutes=15)
                            temp_user_data['expiration_time'] = expiration_time.strftime('%Y-%m-%d %H:%M:%S')
                            temp_user_data['otp'] = otp
                            request.session['temp_user_data'] = temp_user_data
                            url = f'http://sms.iglweb.com/api/v1/send?api_key=4451706354992151706354992&contacts=88{phone}&senderid=01844532630&msg={otp} is your activation code in Student Visa Bd.This code will expire in 2 Hours.For help,call:01958666999'
                            response = requests.get(url)
                            if response.status_code == 200:
                                # Store OTP in session for validation
                                print('OTP: ', otp)
                                print('temp_user_data before redirecting: ', temp_user_data['full_name'])
                                # return JsonResponse({'success': True})
                                return JsonResponse({'success': True, 'redirect_url': '/otp_verification_signup_student/'})
                            # return redirect('otp_verification_signup')
                        else:
                            return JsonResponse({'errors': 'Invalid phone number'})
                    else:
                        return JsonResponse({'errors': 'A user with this email already exists'})
                else:
                    return JsonResponse({'errors': 'A user with this phone already exists'})
            else:
                return JsonResponse({'errors': 'Please fill up all the required fields'})


def otp_verification_signup(request):
    print('wrong view')
    temp_user_data = request.session.get('temp_user_data')
    print('temp_user_data now: ', temp_user_data)

    return render(request, 'user_login/otp_verification_signup.html')
def otp_verification_signup_student(request):
    print('right view')
    temp_user_data = request.session.get('temp_user_data')
    print('temp_user_data now: ', temp_user_data)
    countries = temp_user_data['countries']
    print('countries: ', countries)
    countries_str = ', '.join(countries)
    print('countries str: ', countries_str)

    return render(request, 'user_login/otp_verification_signup_student.html')
    
    
def forgot_password_phone_or_email(request):
    if request.method == 'POST':
        phone = request.POST.get('phone')

        if phone:
            consultant = Users.objects.filter(phone=phone).first()

            if consultant is not None:
                otp = str(random.randint(1000, 9999))
                print('phone validity: ', phone)
                valid_phone_number = re.match(r'^(013|019|018|014|015|016|017)\d{8}$', str(phone))
                temp_user_data = {
                    'phone': phone,
                    'otp': otp
                }
                print('valid_phone_number: ', valid_phone_number)
                
                if valid_phone_number:
                    url = f'http://sms.iglweb.com/api/v1/send?api_key=4451706354992151706354992&contacts=88{valid_phone_number}&senderid=01844532630&msg={otp} is your activation code in IGL Bus Service.This code will expire in 2 Hours.For help,call:01958666999'
                    response = requests.get(url)
                    if response.status_code == 200:
                        print('response from the server: ', response.status_code)
                        response = JsonResponse({'success': True, 'redirect_url': '/forgot_password_otp_verification/'})
                        expiration_time = int(time()) + 15
                        temp_user_data['expiration_time'] = expiration_time
                        request.session['temp_user_data'] = temp_user_data
                        print('stored_first otp: ', request.session['temp_user_data']['otp'])
                        response_data = {
                            'success': True,
                            'redirect_url': '/forgot_password_otp_verification/',
                            'expiration_time': expiration_time  # Send expiration time to client
                        }

                        response = JsonResponse(response_data)

                        return response
                    
                else:
                    return JsonResponse({'error': 'Invalid Phone Number Provided'})
            
            else:
                return JsonResponse({'error': 'Phone Number is not registered'})

    return render(request, 'user_login/forgot_password_phone_or_email.html')


def forgot_password_otp_verification(request):
    temp_data = request.session['temp_user_data']
    time_remaining = temp_data['expiration_time']

    if request.method == 'GET':
        resend_otp = request.GET.get('resend', '')
        print('resend_otp: ', resend_otp)

        if resend_otp and resend_otp == 'true':
            print('resend session: ', request.session['temp_user_data'])
            if request.session['temp_user_data']:
                previous_expiration_time = request.session['temp_user_data']['expiration_time']
                previous_otp = request.session['temp_user_data']['otp']

                previous_expiration_datetime = timezone.make_aware(datetime.utcfromtimestamp(previous_expiration_time), timezone=timezone.utc)
                
                if previous_expiration_time and timezone.now() > previous_expiration_datetime:
                    # Clear session data if expiration time has passed
                    del request.session['temp_user_data']['otp']
                    del request.session['temp_user_data']['expiration_time']
                    print('session after deleting two keys: ', request.session['temp_user_data'])

                    valid_phone_number = request.session['temp_user_data']['phone']
                    otp = str(random.randint(1000, 9999))
                    url = f'http://sms.iglweb.com/api/v1/send?api_key=4451706354992151706354992&contacts=88{valid_phone_number}&senderid=01844532630&msg={otp} is your activation code in IGL Bus Service.This code will expire in 2 Hours.For help,call:01958666999'
                    response = requests.get(url)
                    expiration_time_resend = int(time()) + 15
                    request.session['temp_user_data']['otp'] = otp
                    request.session['temp_user_data']['expiration_time'] = expiration_time_resend
                    request.session.modified = True     # Mark session as modified
                    print('resend otp: ', request.session['temp_user_data']['otp'])
                    print('session resend: ', request.session['temp_user_data'])

                    response_data = {
                        'success': True,
                        'redirect_url': '/forgot_password_otp_verification/',
                        'otp': otp,
                        'expiration_time': expiration_time_resend  # Send expiration time to client
                    }

                    response = JsonResponse(response_data)

                    return response
            else:
                return JsonResponse({'error': 'Please Retry'})

    elif request.method == 'POST':
        stored_otp = request.session['temp_user_data']['otp']
        entered_otp = request.POST.get('otp')
        print('entered otp: ', entered_otp) 
        print('stored otp: ', stored_otp)
        print('otp in post: ', request.session['temp_user_data']['otp'])

        if entered_otp == stored_otp:
            return JsonResponse({'success': True, 'redirect_url': '/change_forgotten_password/'})
        
        else:
            return JsonResponse({'errors': 'Invalid OTP'})

    return render(request, 'user_login/forgot_password_otp_verification.html', {'expiration_time': time_remaining})


def change_forgotten_password(request):
    temp_data = request.session.get('temp_user_data')
    print('temp data redirected: ', temp_data['phone'])
    print('OTP: ', temp_data['otp'])

    if request.method == 'POST':
        phone = temp_data['phone']
        new_password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')

        print('new password: ', new_password)
        print('confirm password: ', confirm_password)

        if new_password and confirm_password:
            if new_password == confirm_password:
                consultant = Users.objects.filter(phone=phone).first()
                if consultant:
                    user = CustomUser.objects.filter(id=consultant.id).first()
                    
                    if user:
                        user.set_password(new_password)
                        consultant.raw_password = new_password
                        consultant.password = make_password(new_password)
                        user.save()
                        consultant.save()

                        return JsonResponse({'success': True})

                    else: 
                        return JsonResponse({'errors': 'Your account hasn\'t been approved yet'})
                
                else:
                    return JsonResponse({'errors': 'Phone Number is not Registered'})
                
            else:
                return JsonResponse({'errors': 'Passwords do not match'})
        
        else:
            return JsonResponse({'errors': 'Please fill up all the requuired fields'})
                
    return render(request, 'user_login/change_forgotten_password.html')


def forgot_password_phone_or_email_student(request):
    if request.method == 'POST':
        phone = request.POST.get('phone')
        print('student phone 1: ', phone)

        if phone:
            student = Students.objects.filter(phone=phone).first()
            print('student phone: ', phone)

            if student is not None:
                otp = str(random.randint(1000, 9999))
                print('phone validity: ', phone)
                valid_phone_number = re.match(r'^(013|019|018|014|015|016|017)\d{8}$', str(phone))
                temp_user_data = {
                    'phone': phone,
                    'otp': otp
                }
                print('valid_phone_number: ', valid_phone_number)
                
                if valid_phone_number:
                    url = f'http://sms.iglweb.com/api/v1/send?api_key=4451706354992151706354992&contacts=88{valid_phone_number}&senderid=01844532630&msg={otp} is your activation code in IGL Bus Service.This code will expire in 2 Hours.For help,call:01958666999'
                    response = requests.get(url)
                    if response.status_code == 200:
                        print('response from the server: ', response.status_code)
                        response = JsonResponse({'success': True, 'redirect_url': '/forgot_password_otp_verification_student/'})
                        expiration_time = int(time()) + 15
                        temp_user_data['expiration_time'] = expiration_time
                        request.session['temp_user_data'] = temp_user_data
                        print('stored_first otp: ', request.session['temp_user_data']['otp'])
                        response_data = {
                            'success': True,
                            'redirect_url': '/forgot_password_otp_verification_student/',
                            'expiration_time': expiration_time  # Send expiration time to client
                        }

                        response = JsonResponse(response_data)
                        # response.set_cookie('expiration_time', expiration_time, max_age=60)  # Set max_age to 60 second
                        # return JsonResponse({'success': True, 'redirect_url': '/forgot_password_otp_verification_student/'})

                        return response
                else:
                    return JsonResponse({'error': 'Invalid Phone Number Provided'})
            
            else:
                return JsonResponse({'error': 'Phone Number is not registered'})

    return render(request, 'user_login/forgot_password_phone_or_email_student.html')


def forgot_password_otp_verification_student(request):
    temp_data = request.session['temp_user_data']
    time_remaining = temp_data['expiration_time']

    if request.method == 'GET':
        resend_otp = request.GET.get('resend', '')
        print('resend_otp: ', resend_otp)

        if resend_otp and resend_otp == 'true':
            print('resend session: ', request.session['temp_user_data'])
            if request.session['temp_user_data']:
                previous_expiration_time = request.session['temp_user_data']['expiration_time']
                previous_otp = request.session['temp_user_data']['otp']

                previous_expiration_datetime = timezone.make_aware(datetime.utcfromtimestamp(previous_expiration_time), timezone=timezone.utc)
                
                if previous_expiration_time and timezone.now() > previous_expiration_datetime:
                    # Clear session data if expiration time has passed
                    del request.session['temp_user_data']['otp']
                    del request.session['temp_user_data']['expiration_time']
                    print('session after deleting two keys: ', request.session['temp_user_data'])

                    valid_phone_number = request.session['temp_user_data']['phone']
                    otp = str(random.randint(1000, 9999))
                    url = f'http://sms.iglweb.com/api/v1/send?api_key=4451706354992151706354992&contacts=88{valid_phone_number}&senderid=01844532630&msg={otp} is your activation code in IGL Bus Service.This code will expire in 2 Hours.For help,call:01958666999'
                    response = requests.get(url)
                    expiration_time_resend = int(time()) + 15
                    request.session['temp_user_data']['otp'] = otp
                    request.session['temp_user_data']['expiration_time'] = expiration_time_resend
                    request.session.modified = True     # Mark session as modified
                    print('resend otp: ', request.session['temp_user_data']['otp'])
                    print('session resend: ', request.session['temp_user_data'])

                    response_data = {
                        'success': True,
                        'redirect_url': '/forgot_password_otp_verification_student/',
                        'otp': otp,
                        'expiration_time': expiration_time_resend  # Send expiration time to client
                    }

                    response = JsonResponse(response_data)

                    return response
            else:
                return JsonResponse({'error': 'Please Retry'})

    elif request.method == 'POST':
        stored_otp = request.session['temp_user_data']['otp']
        entered_otp = request.POST.get('otp')
        print('entered otp: ', entered_otp) 
        print('stored otp: ', stored_otp)
        print('otp in post: ', request.session['temp_user_data']['otp'])

        if entered_otp == stored_otp:
            return JsonResponse({'success': True, 'redirect_url': '/change_forgotten_password_student/'})
        
        else:
            return JsonResponse({'errors': 'Invalid OTP'})

    return render(request, 'user_login/forgot_password_otp_verification_student.html', {'expiration_time': time_remaining})


def change_forgotten_password_student(request):
    temp_data = request.session.get('temp_user_data')
    print('--------------------tempdata:-------------------------- ', temp_data['phone'])
    print('-----------------------OTP:----------------------------', temp_data['otp'])

    if request.method == 'POST':
        phone = temp_data['phone']
        new_password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')

        print('new password: ', new_password)
        print('confirm password: ', confirm_password)

        if new_password and confirm_password:
            if new_password == confirm_password:
                print('student phone: ', phone)
                student = Students.objects.filter(phone=phone).first()
                if student:
                    user = CustomUser.objects.filter(id=student.id).first()
                    
                    if user:
                        user.set_password(new_password)
                        student.raw_password = new_password
                        student.password = make_password(new_password)
                        user.save()
                        student.save()

                        return JsonResponse({'success': True})

                    else: 
                        return JsonResponse({'errors': 'Your account hasn\'t been approved yet'})
                
                else:
                    return JsonResponse({'errors': 'Phone Number is not Registered'})
                
            else:
                return JsonResponse({'errors': 'Passwords do not match'})
        
        else:
            return JsonResponse({'errors': 'Please fill up all the requuired fields'})
                
    # else:
    return render(request, 'user_login/change_forgotten_password_student.html')


def save_user_signup(request):
    if request.method == 'POST':
        temp_user_data = request.session.get('temp_user_data')
        entered_otp = request.POST.get('otp')
        stored_otp = temp_user_data['otp']

        if entered_otp == stored_otp:
            full_name = temp_user_data['full_name']
            company_name = temp_user_data['company_name']
            email = temp_user_data['email']
            est_date = temp_user_data['est_date']
            phone = temp_user_data['phone']
            district_id = int(temp_user_data['district_id'])
            thana_id = temp_user_data['thana_id']
            address = temp_user_data['address']
            password = temp_user_data['password']
            website = temp_user_data['website']
            land_phone = temp_user_data['land_phone']
            fax_no = temp_user_data['fax_no']
            expiration_time = temp_user_data['expiration_time']
            otp = temp_user_data['otp']

            district = get_object_or_404(District, id=district_id)
            thana = get_object_or_404(Thana, id=thana_id)

            # Create a new user in the Users table
            user = Users.objects.create(
                full_name=full_name,
                company_name=company_name,
                est_date=est_date,
                phone=phone,
                email=email,
                district=district,
                thana=thana,
                address=address,
                user_role=5,
                land_phone=land_phone,
                fax_no=fax_no,
                website=website,
            )
            user.password = make_password(password)
            user.save()

            return JsonResponse({'success': True})
        else:
            return JsonResponse({'error': 'Incorrect OTP'})


def save_student_signup(request):
    if request.method == 'POST':
        temp_user_data = request.session.get('temp_user_data')
        entered_otp = request.POST.get('otp')
        stored_otp = temp_user_data['otp']
        if entered_otp == stored_otp:
            full_name = temp_user_data['full_name']
            email = temp_user_data['email']
            phone = temp_user_data['phone']
            user_type = temp_user_data['user_type']
            gender = temp_user_data['gender']
            district_id = int(temp_user_data['district_id'])
            thana_id = temp_user_data['thana_id']
            address = temp_user_data['address']
            countries = temp_user_data['countries']
            password = temp_user_data['password']
            expiration_time = temp_user_data['expiration_time']
            otp = temp_user_data['otp']
            country_string = ''
            district = District.objects.get(id=district_id)
            thana = Thana.objects.get(id=thana_id)
            print('district: ', district)
            user = CustomUser.objects.create(
                email=email,
                user_type=2
            )
            user.set_password(password)
            user.save()
            student = Students.objects.create(
                id=user.id,
                full_name=full_name,
                email=email,
                phone=phone,
                user_type=user_type,
                gender=gender,
                district=district,
                thana=thana,
                address=address,
                status=1,
                raw_password=password
            )
            student_countires = Countries.objects.filter(country_id__in=countries)
            student.countries.add(*student_countires)
            student.password = user.password
            student.save()
            return JsonResponse({'success': True})
        else:
            return JsonResponse({'error': 'Incorrect OTP'})



def login_user(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')

        user = EmailBackend.authenticate(request, email=email, password=password)
        if user is not None and (user.user_type == 0 or user.user_type == 1 ):
            print('user: ', user)
            login(request, user)
            user1 = request.user

            if user.user_type == 0:
                return redirect('root_home')  # Redirect to admin_home for user_type 0
            elif user.user_type == 1:
                return redirect('consultant_home')  # Redirect to consultant_home for user_type 1
            
        else:
            messages.error(request, 'Invalid credentials')
            
    return render(request, 'user_login/login_user.html')

def login_student(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')

        # Get the next parameter from the query string (if available)
        next_page = request.GET.get('next', None)

        user = EmailBackend.authenticate(request, email=email, password=password)

        if user and user.user_type == 2:
            login(request, user)

            # Redirect to the next_page if available, otherwise go to student_home
            if next_page:
                return redirect(next_page)
            else:
                return redirect('student_home')
        else:
            messages.error(request, 'Invalid credentials')

    # Display a message indicating the need to log in only if next_page is specified
    if request.GET.get('next'):
        messages.info(request, 'You need to log in first.')

    return render(request, 'user_login/login_user.html')


def logout_user(request):
    user_session = UserSession.objects.filter(user=request.user, end_time__isnull=True).first()
    if user_session:
        user_session.end_time = timezone.now()
        user_session.save()
    logout(request)
    return redirect('home')  # Redirect to the home page or adjust the URL as needed


def get_thana(request):
    if request.method == 'GET' and 'district_id' in request.GET:
        district_id = request.GET['district_id']
        district = District.objects.get(id=district_id)
        print('district_id: ', district_id)

        thanas = district.thanas.all()
        for thana in thanas:
            print('get thana: ', thana.name)
        serializer = ThanaSerializer(thanas, many=True)
        thanas = serializer.data

        print('thana serializer: ', thanas)

    return JsonResponse({
        'success': True,
        'thanas': thanas
    }, safe=False)


def contact(request):
    category_choices = Message.CATEGORY_CHOICES  # Retrieve category choices from the Message model

    if request.method == 'POST':
        # Extract data from the request
        category = request.POST.get('category')
        email = request.POST.get('email')
        name = request.POST.get('name')
        phonenumber = request.POST.get('phonenumber')
        subject = request.POST.get('subject')
        message_text = request.POST.get('message')

        try:
            # Create and save a Message instance
            message = Message.objects.create(
                category=category,
                email=email,
                name=name,
                phonenumber=phonenumber,
                subject=subject,
                message=message_text,
                created_at=timezone.now(),
                
            )

            messages.success(request, 'Message submitted successfully!')
        except Exception as e:
            messages.error(request, f'An error occurred: {str(e)}')

        return redirect('contact')

    addresses = Addresses.objects.filter(root_id__isnull=False)
    return render(request, 'contact.html', {'addresses': addresses, 'category_choices': category_choices})



def process_explanation(request):
    return render(request,'process_explenation.html')
# views.py






def consultant_list(request):
    # Retrieve consultants with user_role=5
    users = CustomUser.objects.filter(user_type=1)
    consultants = Users.objects.filter(id__in=users.values('id'))
    # Retrieve consultant details
    consultant_details = ConsultantDetails.objects.filter(consultant_id__in=consultants)
    countries = Countries.objects.all()
    # Combine consultants and details into a list of dictionaries
    consultants_with_details = [{'consultant': consultant, 'details': details} for consultant, details in zip(consultants, consultant_details)]
    # Use the current time as a seed for random order
    seed = int(time())
    random.seed(seed)
    # Shuffle the entire list of consultants
    random.shuffle(consultants_with_details)
    # Manually chunk the queryset into groups of 5
    chunked_consultants = [consultants_with_details[i:i+5] for i in range(0, len(consultants_with_details), 5)]
    # context dictionary
    context = {
        'chunked_consultants': chunked_consultants,
    }
    # Search function
    if request.method == 'GET':
        search_input = request.GET.get('search_area') or ''
        rating_filter = request.GET.get('rating_filter') or ''
        country_filter = request.GET.get('country_filter') or ''
        experience_filter = request.GET.get('experience_filter') or ''

        print('rating_filter: ', rating_filter)
        print('country_filter: ', country_filter)
        print('experience_filter: ', experience_filter)

        queryset = Users.objects.filter(user_role=5)
        if search_input or rating_filter or country_filter or experience_filter:

            if not rating_filter:
                rating_filter = 'high'

            if rating_filter == 'high':
                queryset_user = Users.objects.filter(company_name__icontains=search_input, user_role=5).order_by('-rating')
                queryset = list(queryset_user.values_list('id', flat=True))

                for user in queryset_user:
                    print('user each filter: ', user)
                    print('user get: ',  Users.objects.get(id=user.id))

                print('queryset for rating: ', queryset)
                print('------rating is high------')

            elif rating_filter == 'low':
                queryset = Users.objects.filter(company_name__icontains=search_input, user_role=5).order_by('rating')
                print('------rating is low------')

            if experience_filter and experience_filter == 'high':
                if country_filter:
                    country_id_int = int(country_filter)
                    country = Countries.objects.get(country_id=country_id_int)
                    # consultant_details = ConsultantDetails.objects.filter(consultant_id__in=queryset, consultant_countries__in=[country]).order_by('-experience')
                    
                    ordering_conditions = [When(consultant_id=user_id, then=pos) for pos, user_id in enumerate(queryset, start=1)]
                    consultant_details = ConsultantDetails.objects.filter(consultant_id__in=queryset, consultant_countries__in=[country]).order_by(Case(*ordering_conditions, default=0))
                    
                    user_ordering_consitions = [When(id=user_id, then=pos) for pos, user_id in enumerate(consultant_details, start=1)]
                    consultant_details_ids = list(consultant_details.values_list('id', flat=True))
                    consultant_users = Users.objects.filter(id__in=consultant_details_ids).order_by(Case(*user_ordering_consitions, default=0))

                    queryset = list(consultant_users.values_list('id', flat=True))
                    print('------experience is high and country is there------')
                    

                else:
                    # consultant_details = ConsultantDetails.objects.filter(consultant_id__in=queryset).order_by('experience')
                    ordering_conditions = [When(consultant_id=user_id, then=pos) for pos, user_id in enumerate(queryset, start=1)]
                    consultant_details = ConsultantDetails.objects.filter(consultant_id__in=queryset).order_by(Case(*ordering_conditions, default=0))
                    print('------experience is high but no country selected------')


            elif experience_filter and experience_filter == 'low':
                if country_filter:
                    country_id_int = int(country_filter)
                    country = Countries.objects.get(country_id=country_id_int)
                    # consultant_details = ConsultantDetails.objects.filter(consultant_id__in=queryset, consultant_countries__in=[country]).order_by('-experience')
                    ordering_conditions = [When(consultant_id=user_id, then=pos) for pos, user_id in enumerate(queryset, start=1)]
                    consultant_details = ConsultantDetails.objects.filter(consultant_id__in=queryset, consultant_countries__in=[country]).order_by(Case(*ordering_conditions, default=0))
                    print('------experience is low and country is there------')

                else:
                    # consultant_details = ConsultantDetails.objects.filter(consultant_id__in=queryset).order_by('-experience')
                    ordering_conditions = [When(consultant_id=user_id, then=pos) for pos, user_id in enumerate(queryset, start=1)]
                    consultant_details = ConsultantDetails.objects.filter(consultant_id__in=queryset).order_by(Case(*ordering_conditions, default=0))
                    print('------experience is low but no country selected------')

            else:
                if country_filter:
                    country_id_int = int(country_filter)
                    country = Countries.objects.get(country_id=country_id_int)
                    # consultant_details = ConsultantDetails.objects.filter(consultant_id__in=queryset, consultant_countries__in=[country])

                    ordering_conditions = [When(consultant_id=user_id, then=pos) for pos, user_id in enumerate(queryset, start=1)]
                    consultant_details = ConsultantDetails.objects.filter(consultant_id__in=queryset, consultant_countries__in=[country]).order_by(Case(*ordering_conditions, default=0))
                    
                    consultant_details_ids = list(consultant_details.values_list('consultant_id', flat=True))
                    user_ordering_consitions = [When(id=user_id, then=pos) for pos, user_id in enumerate(consultant_details_ids, start=1)]
                    consultant_users = Users.objects.filter(id__in=consultant_details_ids).order_by(Case(*user_ordering_consitions, default=0))

                    queryset = list(consultant_users.values_list('id', flat=True))

                    print('------no experience but country is there------')
                    print('---------consultant_details-------: ', consultant_details)

                else:
                    # consultant_details = ConsultantDetails.objects.filter(consultant_id__in=queryset)
                    ordering_conditions = [When(consultant_id=user_id, then=pos) for pos, user_id in enumerate(queryset, start=1)]
                    # consultant_details = ConsultantDetails.objects.filter(consultant_id__in=queryset).order_by(Case(*ordering_conditions, default=0))
                    ordering_conditions = [When(consultant_id=user_id, then=pos) for pos, user_id in enumerate(queryset, start=1)]
                    consultant_details = ConsultantDetails.objects.filter(consultant_id__in=queryset).order_by(Case(*ordering_conditions, default=0))
                    print('consultant details: ', consultant_details)
                    print('------no experience and no country selected------')

            # consultants_with_details = [{'consultant': consultant, 'details': ConsultantDetails.objects.filter(consultant_id=consultant)} for consultant in queryset]
            print('queryset id: ', queryset)
            consultants_with_details = [{'consultant': Users.objects.get(id=consultant), 'details': ConsultantDetails.objects.filter(consultant_id=consultant)} for consultant in queryset]
            # Sort based on the rating

            # if rating_filter:
            #     consultants_with_details.sort(key=lambda x: x['consultant'].rating or 0, reverse=(rating_filter == 'high'))

            chunked_consultants = [consultants_with_details[i] for i in range(0, len(consultants_with_details))]
            print('chunked consultants: ', chunked_consultants)
            context = {
                'chunked_consultants': chunked_consultants,
                'search_input': search_input,
                'rating_filter': rating_filter,
                'country_filter': country_filter,
                'experience_filter': experience_filter
            }

    context['countries'] = countries
    return render(request, 'consultant_list.html', context)
    
    
def colors(request, consultant_id):
    # Get the consultant
    consultant = get_object_or_404(Users, id=consultant_id, user_role=5)

    # Retrieve colors based on the consultant_id
    consultant_colors = Colors.objects.filter(consultant_id=consultant_id).first()

    # Default colors if not found
    default_colors = {
        'header_color': '#FFFF',
        'content_color': '#00000',
        'footer_color': '#0c2136;',
    }

    # Use consultant_colors if available, otherwise use default_colors
    colors_data = {
        'header_color': consultant_colors.header_color if consultant_colors else default_colors['header_color'],
        'content_color': consultant_colors.content_color if consultant_colors else default_colors['content_color'],
        'footer_color': consultant_colors.footer_color if consultant_colors else default_colors['footer_color'],
    }

    return JsonResponse(colors_data)

def singel_consultant_base(request, consultant_id):
    # Retrieve the consultant based on the ID
    consultant = get_object_or_404(Users, id=consultant_id, user_role=5)

    # Retrieve additional details from the ConsultantDetails model
    consultant_details = get_object_or_404(ConsultantDetails, consultant_id=consultant_id)
    print('consultant_details:', consultant_details)
    # Pass the consultant and details to the template
    return render(request, 'consultant_base.html', {'consultant': consultant, 'consultant_details': consultant_details})


def singel_consultant_details(request, consultant_id):
    # Retrieve the consultant based on the ID
    consultant = get_object_or_404(Users, id=consultant_id, user_role=5)
    # Retrieve additional details from the ConsultantDetails model
    consultant_details = get_object_or_404(ConsultantDetails, consultant_id=consultant_id)
    # Pass the consultant and details to the template
    return render(request, 'single-consultant-details.html', {'consultant': consultant, 'consultant_details': consultant_details})


def singel_consultant_page(request, consultant_id):
    consultant = get_object_or_404(Users, id=consultant_id, user_role=5)
    consultant_details = get_object_or_404(ConsultantDetails, consultant_id=consultant_id)

    # Retrieve the corresponding Customizes instance for the current consultant
    customize = Customizes.objects.filter(consultant_id=consultant_id).first()

    return render(request, 'singel_consultant_page.html', {
        'consultant': consultant,
        'consultant_details': consultant_details,
        'customize': customize
    })


def singel_consultant_gallery(request, consultant_id):
    consultant = get_object_or_404(Users, id=consultant_id, user_role=5)
    consultant_details = get_object_or_404(ConsultantDetails, consultant_id=consultant_id)
    consultant_images = ConsultantImages.objects.filter(consultant_id=consultant_id)
    return render(request, 'singel_consultant_gallery.html', {
        'consultant': consultant,
        'consultant_details': consultant_details,
        'consultant_images': consultant_images
    })


def single_consultant_requirement(request, consultant_id):
    consultant = get_object_or_404(Users, id=consultant_id, user_role=5)
    consultant_details = get_object_or_404(ConsultantDetails, consultant_id=consultant_id)
    # Splitting and slicing the consultant_requirement
    requirement_lines = consultant_details.consultant_requirement.split('\n')
    first_line = requirement_lines[0]
    middle_lines = requirement_lines[1:-1]
    last_line = requirement_lines[-1]
    return render(request, 'singel_consultant_requirement.html', {
        'consultant': consultant,
        'consultant_details': consultant_details,
        'first_line': first_line,
        'middle_lines': middle_lines,
        'last_line': last_line,
    })


def singel_consultant_country(request, consultant_id):
    consultant = get_object_or_404(Users, id=consultant_id, user_role=5)
    consultant_details = get_object_or_404(ConsultantDetails, consultant_id=consultant_id)

    # Assuming you have a queryset of countries you want to paginate
    consultant_countries = Countries.objects.filter(consultant_details=consultant_details)

    # Number of items per page
    items_per_page = 3  # You can adjust this value based on your preference

    paginator = Paginator(consultant_countries, items_per_page)
    
    page = request.GET.get('page')
    
    try:
        consultant_countries = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        consultant_countries = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        consultant_countries = paginator.page(paginator.num_pages)

    return render(request, 'singel_consultant_country.html', {
        'consultant_details': consultant_details,
        'consultant': consultant,
        'consultant_countries': consultant_countries,
    })

def singel_consultant_country_details(request, consultant_id, country_id):

    consultant = get_object_or_404(Users, id=consultant_id, user_role=5)
    consultant_details = get_object_or_404(ConsultantDetails, consultant_id=consultant_id)
    country = get_object_or_404(Countries, country_id=country_id)

    country_howtoapply = mark_safe(country.country_howtoapply)
    return render(request, 'singel_consultant_country_details.html', {
        'consultant_details': consultant_details,
        'consultant': consultant,
        'country': country,
        'country_howtoapply': country_howtoapply,
    })

@login_required(login_url='login_student')
def singel_consultant_review(request, consultant_id):
    consultant = get_object_or_404(Users, id=consultant_id, user_role=5)

    if request.user.is_authenticated:
        user = request.user
        context = {
            'consultant': consultant,
        }
        student = Students.objects.filter(id=user.id).first()
        rating = Review.objects.filter(consultant=consultant_id, student=student.id).first()

        if rating is not None:
            student_raw_rating = rating.raw_rating
            student_rating = rating.rating
            context['student_rating'] = student_rating
            context['student_raw_rating'] = student_raw_rating
            print('student rating: ', student_rating)

        print('consultant rating: ', round(consultant.rating, 1))
    
    else:
        context = None
    
    return render(request,'singel_consultant_review.html', context)


def save_review(request):
    if request.method == 'POST':
        raw_rating_str = request.POST.get('raw_rating')
        comment = request.POST.get('comment')

        print('raw_rating_str: ', raw_rating_str)
        print('comment: ', comment)

        if request.user.is_authenticated:
            if raw_rating_str or comment:
                raw_rating = int(raw_rating_str)
                consultant_id = request.POST.get('consultant_id')
                consultant = Users.objects.filter(id=consultant_id).first()
                student = Students.objects.filter(id=request.user.id).first()
                print('consultant: ', consultant)
                print('student: ', student)
                
                if student and consultant:
                    if raw_rating:
                        rating = round(raw_rating / 2, 1)

                        student_rating = Review.objects.filter(consultant=consultant_id, student=student.id).first()
                        print('student rating on: ', student_rating)

                        review = Review(
                                    consultant = consultant.id,
                                    student = student.id,
                                    raw_rating=raw_rating,
                                    rating=rating
                                )
                        
                        if comment:
                            review.comment = comment

                        review.save() 

                        return JsonResponse({'success': True})

                    else:
                        return JsonResponse({'error': 'Rating is required'})
                
                return JsonResponse({'error': 'Not permitted to post a review'})
                
            return JsonResponse({'error': 'At least rating is required'})
        
        else:
            return JsonResponse({'error': 'Unauthorized user'})
        
    else:
        return JsonResponse({'error': 'Invalid Request'})


def singel_consultant_profile(request,consultant_id):
    consultant = get_object_or_404(Users, id=consultant_id, user_role=5)
    consultant_details = get_object_or_404(ConsultantDetails, consultant_id=consultant_id)
    return render(request,'singel_consultant_profile.html',{
        'consultant_details': consultant_details,
        'consultant': consultant,
      
    })

def feedback(request, consultant_id):
    consultant = get_object_or_404(Users, id=consultant_id, user_role=5)
    countries = Countries.objects.all()

    context = {
        'consultant': consultant,
        'countries': countries,
    }

    return render(request, 'feedback.html', context)


def save_feedback(request):
    if request.method == 'POST':

        name = request.POST.get('username')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        subject = request.POST.get('subject')
        country = request.POST.get('country')
        message = request.POST.get('message')
        consultant_id = request.POST.get('consultantId')

        print('name: ', name)
        print('email: ', email)
        print('phone: ', phone)
        print('subject: ', subject)
        print('country: ', country)
        print('messages: ', message)
        print('consultant_id: ', consultant_id)

        consultant = Users.objects.filter(id=consultant_id).first()

        if consultant is not None:
            if name and email and phone and subject and country and message:
                feedback = HomeFeedback.objects.create(
                                consultant=consultant_id,
                                fdk_fullname=name,
                                fdk_email=email,
                                fdk_phone=phone,
                                fdk_msg=message,
                                created_at=timezone.now(),
                            )

                if request.user.is_authenticated:
                    user = request.user
                    if user.user_type == 2:
                        student_id = request.user.id
                        feedback.student = student_id
                
                if consultant.company_name:
                    feedback.fdk_nameofcompany = consultant.company_name

                if consultant.website:
                    feedback.fdk_website = consultant.website
                
                feedback.save()

                return JsonResponse({'success': True})
            else:
                return JsonResponse({'error': 'Please fill up all the required fields'})

        else:
            return JsonResponse({'error': 'Error sending feedback'})
            
    else:
        return JsonResponse({'error': 'Invalid request'})
    

    
def singel_consultant_contact(request, consultant_id):
    print(f"Consultant ID: {consultant_id}")

    try:
        consultant = get_object_or_404(Users, id=consultant_id, user_role=5, active_status=5)
        consultant_details = get_object_or_404(ConsultantDetails, consultant_id=consultant_id)
    except Http404:
        # Handle 404 error here, render a custom 404 template
        return render(request, 'error.html', status=404)

    return render(request, 'singel_consultant_contact.html', {
        'consultant_details': consultant_details,
        'consultant': consultant,
    })

def consaltant_wise_scholarship(request):
    # Fetch scholarships from the database
    scholarships = ScholarShips.objects.all()

    # Fetch user details for consultants
    consultant_users = Users.objects.filter(user_role=5)  # Assuming user_role 5 corresponds to consultants

    # Pass scholarships, consultant details, and consultant users to the template context
    context = {
        'scholarships': scholarships,
        'consultant_users': consultant_users,
    }

    # Render the template with the context
    return render(request, 'consaltant_wise.html', context)
@login_required(login_url='login_student')
def consaltant_wise_scholarship_singel_page(request, scholarship_id):
    # Fetch a specific scholarship using the provided scholarship_id
    scholarship = get_object_or_404(ScholarShips, id=scholarship_id)
    
    # Assuming user_role 5 corresponds to consultants
    consultant_users = Users.objects.filter(user_role=5)

    context = {
        'scholarship': scholarship,
        'consultant_users': consultant_users,
    }

    # Render the template with the context
    return render(request, 'scholarship_singel_page.html', context)


def country_wise_scholarship(request):
    # Get all instances of CountryWises
    country_wise_list = CountryWises.objects.all()

    # Set the number of items per page
    items_per_page = 9

    # Create a Paginator object
    paginator = Paginator(country_wise_list, items_per_page)

    # Get the current page number from the request's GET parameters
    page = request.GET.get('page')

    try:
        # Get the Page object for the current page
        country_wise = paginator.page(page)
    except PageNotAnInteger:
        # If the page parameter is not an integer, set it to the first page
        country_wise = paginator.page(1)
    except EmptyPage:
        # If the page parameter is out of range, deliver the last page of results
        country_wise = paginator.page(paginator.num_pages)

    return render(request, 'country_wise_scholarship.html', {'country_wise': country_wise})
@login_required(login_url='login_student')
def country_wise_scholarship_single(request, scw_id):
    scholarship = get_object_or_404(CountryWises, scw_id=scw_id)
    return render(request, 'country_wise_scholarship_single.html', {'scholarship': scholarship})

def offer_letter(request):
    offer_letters = OfferLetters.objects.all()
    return render(request, 'offer_letter.html', {'offer_letters': offer_letters})


def by_country(request):
    if request.method == 'GET':
        search_input = request.GET.get('search_area')
        print('search_input: ', search_input)

        if search_input:
            countries_list = Countries.objects.filter(country_name__icontains=search_input)
        else:
            countries_list = Countries.objects.all()
 
    paginator = Paginator(countries_list, 12)

    page = request.GET.get('page')

    try:
        countries = paginator.page(page)

    except PageNotAnInteger:
        countries = paginator.page(1)

    except EmptyPage:
        # If page is out of range (e.g., 9999), deliver the last page.
        countries = paginator.page(paginator.num_pages)

    for i in countries.paginator.page_range:
        if i <= 5 or i > countries.paginator.num_pages - 2 or (i > countries.number - 2 and i < countries.number + 2):
            print('page number: ', i)

    print('countries', countries)
    context = {
        'countries': countries
    }
    return render(request, 'by_country.html', context)


def by_country_autosearch(request):
    print(request.GET)
    search = request.GET.get('term')
    payload = []
    if search:
        objs = Countries.objects.filter(country_name__icontains=search)
        for obj in objs:
            payload.append(obj.country_name)


    return JsonResponse(payload, safe=False)

def country_details(request, country_id):
    country = Countries.objects.get(country_id=country_id)

    context = {
        'country': country
    }
    return render(request, 'country_details.html', context)

#Student Dashboard

@login_required(login_url='login_student')
def student_home(request):

    user_id = request.user.id

    try:

        student = Students.objects.get(student_user=user_id)
    except Students.DoesNotExist:

        return redirect('login_student')

    context = {
        'student': student,
    }

    return render(request, 'studentinfo/home.html', context)

@login_required(login_url='login_student')
def student_search_consultant(request):
    query = request.GET.get('q') 


    user = request.user

    consultants = Users.objects.filter(user_role=5)
    
    if query:

        consultants = consultants.filter(company_name__icontains=query)

    context = {
        'consultants': consultants,
        'query': query,
        'user': user,  
    }

    return render(request, 'studentinfo/consultant_search.html', context)

@login_required(login_url='login_student')
def add_to_favorite(request, consultant_id):
    consultant = get_object_or_404(Users, pk=consultant_id)

    student_details, created = StudentDetails.objects.get_or_create(dets_regs_id=request.user.id)

    fav_consultant_list = student_details.dets_favconsultantlist

    if fav_consultant_list:
        fav_consultant_list += f',{consultant_id}'
    else:
        fav_consultant_list = consultant_id

    student_details.dets_favconsultantlist = fav_consultant_list
    student_details.save()

    return redirect('student_search_consultant')




@login_required(login_url='login_student')

def student_favourite_list(request):
    student_details = StudentDetails.objects.get(dets_regs_id=request.user.id)
    fav_consultant_list = student_details.dets_favconsultantlist
    consultant_ids = fav_consultant_list.split(',') if fav_consultant_list else []

    favorite_consultants = Users.objects.filter(pk__in=consultant_ids)

    # Fetch consultant statuses
    consultant_statuses = ConsultantStatus.objects.filter(
        student=student_details,
        consultant_id__in=consultant_ids
    )

    # Create a dictionary to store statuses
    status_dict = {status.consultant_id: status for status in consultant_statuses}

    # Create a list of dictionaries containing consultant details and status
    consultant_list = [
        {
            'consultant': consultant,
            'status': status_dict.get(consultant.id, None),
        }
        for consultant in favorite_consultants
    ]

    context = {
        'consultant_list': consultant_list,
    }

    return render(request, 'studentinfo/student_favourite_consultant.html', context)



@login_required(login_url='login_student')

def delete_favourite_consultant(request, consultant_id):
    try:
        print("Delete view is called.")
        
        # Get the current user's student details
        student_details = StudentDetails.objects.get(dets_regs_id=request.user.id)

        # Get the list of favorite consultants
        fav_consultant_list = student_details.dets_favconsultantlist

        # Split the list into consultant IDs
        consultant_ids = fav_consultant_list.split(',') if fav_consultant_list else []

        # Convert the consultant_id to a string for comparison
        consultant_id_str = str(consultant_id)

        # Remove the selected consultant ID from the list
        if consultant_id_str in consultant_ids:
            consultant_ids.remove(consultant_id_str)

        # Join the updated list back into a string
        student_details.dets_favconsultantlist = ','.join(consultant_ids)

        # Save the updated student details
        student_details.save()

        # Prepare a JSON response
        response_data = {'status': 'success', 'message': 'Consultant removed from favorites.'}

    except StudentDetails.DoesNotExist:
        response_data = {'status': 'error', 'message': 'Student details not found.'}

    print("Response data:", response_data)
    return JsonResponse(response_data)






@login_required(login_url='login_student')

def student_result_information(request):
    if request.method == 'POST':
        secondary = request.POST.get('secondary')
        secondary_board = request.POST.get('secondary_board')
        secondary_result = request.POST.get('secondary_result')
        secondary_roll_no = request.POST.get('secondary_roll_no')
        secondary_reg_no = request.POST.get('secondary_reg_no')
        secondary_certificate_no = request.POST.get('secondary_certificate_no')
        secondary_passing_year = request.POST.get('secondary_passing_year')

        higher = request.POST.get('higher')
        higher_board = request.POST.get('higher_board')
        higher_result = request.POST.get('higher_result')
        higher_roll_no = request.POST.get('higher_roll_no')
        higher_reg_no = request.POST.get('higher_reg_no')
        higher_certificate_no = request.POST.get('higher_certificate_no')
        higher_passing_year = request.POST.get('higher_passing_year')

        student_id = request.user.id

        Results.objects.create(
            secondary=secondary,
            secondary_board=secondary_board,
            secondary_result=secondary_result,
            secondary_roll_no=secondary_roll_no,
            secondary_reg_no=secondary_reg_no,
            secondary_certificate_no=secondary_certificate_no,
            secondary_passing_year=secondary_passing_year,

            higher=higher,
            higher_board=higher_board,
            higher_result=higher_result,
            higher_roll_no=higher_roll_no,
            higher_reg_no=higher_reg_no,
            higher_certificate_no=higher_certificate_no,
            higher_passing_year=higher_passing_year,

            student_id=student_id,
            created_at=timezone.now(),
            updated_at=timezone.now()
        )
    return render(request,'studentinfo/student_result_information.html')




@login_required(login_url='login_student')
def student_profile(request):
    # Assuming each student is associated with a user
    student_user = request.user

    # Print the user details for debugging purposes
    print("User Details:", student_user.id, student_user.username, student_user.email)

    try:
        student = Students.objects.get(student_user=student_user)
        results = Results.objects.filter(student_id=student.id)

        # Print the results details for debugging purposes
        for result in results:
            print("Result Details:", result.id, result.secondary, result.secondary_board, result.secondary_result, result.secondary_passing_year)

        # Count the favorite consultants
        student_details = StudentDetails.objects.get(dets_regs_id=student_user.id)
        fav_consultant_list = student_details.dets_favconsultantlist
        consultant_count = len(fav_consultant_list.split(',')) if fav_consultant_list else 0

    except Students.DoesNotExist:
        # Handle the case where the student doesn't exist
        student = None
        results = None
        consultant_count = 0

    return render(request, 'studentinfo/student_profile.html', {'student': student, 'results': results,'student_details' : student_details, 'consultant_count': consultant_count})




@login_required(login_url='login_student')
def edit_student_profile(request):
    student_user = request.user

    try:
        # Try to get the student and related objects
        student = Students.objects.get(student_user=student_user)
        district = District.objects.all()
        thana = Thana.objects.all()
        student_details = StudentDetails.objects.get(dets_regs_id=student_user.id)
        results = Results.objects.filter(student_id=student.id)
        
        # Initialize password_form outside the if-else block
        password_form = PasswordChangeForm(request.user)

        if request.method == 'POST':
            # Update student profile details
            student.full_name = request.POST.get('full_name')
            student.email = request.POST.get('student_email')
            student.phone = request.POST.get('phone')
            student.district_id = request.POST.get('district')
            student.thana_id = request.POST.get('thana')
            now = timezone.now()
            student.updated_at = now

            student.save()

            # Update student details
            student_details.dets_bloodgroup = request.POST.get('dets_bloodgroup')
            student_details.dets_fathername = request.POST.get('dets_fathername')
            student_details.dets_mothername = request.POST.get('dets_mothername')
            student_details.dets_nationality = request.POST.get('nationality')
            student_details.dets_dob = request.POST.get('dob')

            # Handle student image upload
            if 'student_image' in request.FILES:
                uploaded_image = request.FILES['student_image']
                student_details.student_image = uploaded_image
                now = timezone.now()
                student_details.dets_updatedate = now
                student_details.save()
            now = timezone.now()
            student_details.dets_updatedate = now

            student_details.save()

            # Password change logic
            old_password = request.POST.get('old_password')
            new_password = request.POST.get('password')
            user = request.user

            if user.check_password(old_password):
                user.set_password(new_password)
                user.save()
                update_session_auth_hash(request, user)  # Important for maintaining the session
                messages.success(request, 'Your profile and password were successfully updated!')
            else:
                messages.error(request, 'Old password is incorrect. Please provide the correct old password.')

            # Update result details
            for result in results:
                result.secondary_board = request.POST.get('sscBoard')
                result.secondary_result = request.POST.get('sscGPA')
                result.secondary_passing_year = request.POST.get('sscPassingYear')

                result.higher_board = request.POST.get('hscBoard')
                result.higher_result = request.POST.get('hscGPA')
                result.higher_passing_year = request.POST.get('hscPassingYear')
                now = timezone.now()
                result.updated_at = now

                result.save()

        # Render the template with the valid student details
        return render(
            request,
            'studentinfo/edit_student_profile.html',
            {'student': student, 'student_details': student_details, 'results': results, 'password_form': password_form, 'district': district}
        )

    except Students.DoesNotExist:
        # Handle the case where the student doesn't exist
        messages.error(request, 'Student profile not found.')
        return redirect('student_profile')