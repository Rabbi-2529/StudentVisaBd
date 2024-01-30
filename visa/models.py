# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has on_delete set to the desired behavior
#   * Remove managed = False lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone
from django.core.validators import MaxValueValidator, MinValueValidator

class CustomUser(AbstractUser):
    USER_TYPE_CHOICES = (
        (0, 'Root'),
        (1, "Consultant"),
        (2, "Student"),
    )
    username = models.CharField(max_length=20, null=True, blank=True)
    user_type = models.IntegerField(choices=USER_TYPE_CHOICES, default=0)
    last_active = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.email
    
    db_table = 'CustomUser'



class Addresses(models.Model):
    id = models.BigAutoField(primary_key=True)
    consultant_id = models.IntegerField(null=True)
    root_id=models.IntegerField(null=True)
    office_name = models.CharField(max_length=255)
    address = models.CharField(max_length=255)
    hotline = models.CharField(max_length=255)
    phone = models.CharField(max_length=255)
    email = models.CharField(max_length=255)
    created_at = models.DateTimeField(blank=True, null=True)
    updated_at = models.DateTimeField(blank=True, null=True)
    class Meta:
        db_table = 'addresses'

class Message(models.Model):
    CATEGORY_CHOICES = [
        ('General Inquiry', 'General Inquiry'),
        ('Visa Application', 'Visa Application'),
        ('Document Submission', 'Document Submission'),
        ('Appointment Request', 'Appointment Request'),
        
        
    ]

    category = models.CharField(max_length=255, choices=CATEGORY_CHOICES)
    email = models.EmailField()
    name = models.CharField(max_length=255)
    phonenumber = models.CharField(max_length=20)  # Assuming phone numbers are stored as strings
    subject = models.CharField(max_length=255)
    message = models.TextField()
    created_at = models.DateTimeField(blank=True, null=True)
    is_read = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.category} - {self.subject} - {self.name}"
    
class Notification(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    message = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    def __str__(self):
        return f'{self.user.username} - {self.message}'
    
class Reply(models.Model):
    message = models.ForeignKey(Message, on_delete=models.CASCADE)
    email = models.EmailField()
    reply_text = models.TextField(null=True)
    created_at = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return f"Reply to: {self.message.subject} - {self.email}"

class Balances(models.Model):
    acc_paid_by = models.IntegerField(blank=True, null=True)
    acc_pay_to = models.IntegerField(blank=True, null=True)
    acc_pay_std_id = models.IntegerField(blank=True, null=True)
    pay_method = models.IntegerField(choices=[
        (1, 'Cash'),
        (2, 'Bank Deposit'),
        (3, 'Check'),
    ], blank=True, null=True)
    payment_status = models.IntegerField(choices=[
        (1, 'Paid'),
        (2, 'Checking'),
    ], blank=True, null=True)
    acc_pay_ref = models.CharField(max_length=255, blank=True, null=True)
    acc_credit = models.FloatField(blank=True, null=True)
    acc_debit = models.FloatField(blank=True, null=True)
    acc_deal_type = models.IntegerField(blank=True, null=True)
    created_at = models.DateTimeField(blank=True, null=True)
    updated_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        db_table = 'balances'


class Colors(models.Model):
    header_color = models.CharField(max_length=255)
    content_color = models.CharField(max_length=255)
    footer_color = models.CharField(max_length=255)
    consultant_id = models.IntegerField()
    created_at = models.DateTimeField(blank=True, null=True)
    updated_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        db_table = 'colors'


class Countries(models.Model):
    country_id = models.AutoField(primary_key=True)
    country_name = models.CharField(max_length=30)
    country_code = models.CharField(max_length=10, blank=True, null=True)
    country_flag = models.CharField(max_length=60)
    country_howtoapply = models.TextField(db_column='country_howToApply')  # Field name made lowercase.
    country_insertdate = models.DateField(db_column='country_insertDate', blank=True, null=True)  # Field name made lowercase.
    country_updatedate = models.DateField(db_column='country_updateDate', blank=True, null=True)  # Field name made lowercase.
    country_status = models.IntegerField(blank=True, null=True)

    class Meta:
        db_table = 'countries'

class University(models.Model):
    university_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)
    abbreviation = models.CharField(max_length=20)
    established_date = models.DateField(blank=True, null=True)
    website = models.URLField(max_length=200, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    status = models.IntegerField(default=0)  # You may adjust the default value based on your requirements
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    countries = models.ForeignKey(Countries, on_delete=models.SET_NULL, null=True, blank=True, related_name='universities')

    class Meta:
        db_table = 'universities'
class UniversityWise(models.Model):
    uw_id = models.AutoField(primary_key=True)
    uw_university_id = models.IntegerField(unique=True)
    uw_text = models.TextField()
    uw_whocanapply = models.TextField(db_column='uw_whoCanApply', blank=True, null=True)
    uw_status = models.IntegerField()
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(default=timezone.now)

    

    class Meta:
        db_table = 'university_wises'

class Customizes(models.Model):
    description = models.TextField(blank=True, null=True)
    consultant_id=models.CharField(max_length=20, blank=True,null=True)
    image = models.ImageField(upload_to='customizes/', blank=True, null=True)  # Add this line for the image field
    status = models.IntegerField()
    created_at = models.DateTimeField(blank=True, null=True)
    updated_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        db_table = 'customizes'


class ConsultantDetails(models.Model):
    consultant_id = models.IntegerField()
    consultant_customizes = models.ManyToManyField(Customizes, related_name='consultant_customizes', null=True)
    consultant_img = models.ImageField(blank=True, null=True)
    experience=models.IntegerField(null=True ,blank=True)
    consultant_maplocation = models.TextField(db_column='consultant_mapLocation', blank=True, null=True)  # Field name made lowercase.
    consultant_requirement = models.TextField(blank=True, null=True)
    consultant_logo = models.ImageField(upload_to='consultant/', blank=True, null=True)
    consultant_facebook = models.CharField(max_length=50, blank=True, null=True)
    consultant_website = models.CharField(max_length=150, blank=True, null=True)
    consultant_twitter = models.CharField(max_length=50, blank=True, null=True)
    consultant_googleplus = models.CharField(max_length=50, blank=True, null=True)
    consultant_countries = models.ManyToManyField(Countries, related_name='consultant_details',null=True)
    status = models.IntegerField(default=0)
    consultant_experience = models.IntegerField(blank=True, null=True)
    consultant_designation=models.CharField(max_length=60,blank=True)
    consultant_bio = models.CharField(max_length=150, null=True, blank=True)
    consultant_intro = models.CharField(max_length=150, null=True, blank=True)
    consultant_description = models.CharField(max_length=150, null=True, blank=True)
    created_at = models.DateTimeField(blank=True, null=True)
    updated_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        db_table = 'consultant_details'
        managed= True



class ConsultantImages(models.Model):
    id = models.BigAutoField(primary_key=True)
    image = models.ImageField(upload_to='consultant/', blank=True, null=True)
    caption = models.CharField(max_length=255)
    consultant_id = models.IntegerField()
    created_at = models.DateTimeField(blank=True, null=True)
    updated_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        db_table = 'consultant_images'


class ConsultantWises(models.Model):
    scow_id = models.AutoField(primary_key=True)
    scow_consultant_id = models.IntegerField(unique=True)
    scow_text = models.TextField()
    scow_whocanapply = models.TextField(db_column='scow_whoCanApply', blank=True, null=True)  # Field name made lowercase.
    scow_status = models.IntegerField()
    created_at = models.DateTimeField(blank=True, null=True)
    updated_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        db_table = 'consultant_wises'





class CountryAdds(models.Model):
    consultant_id = models.IntegerField()
    country_id = models.IntegerField()
    created_at = models.DateTimeField(blank=True, null=True)
    updated_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        db_table = 'country_adds'


class CountryWises(models.Model):
    scw_id = models.AutoField(primary_key=True)
    scw_country_id = models.IntegerField(unique=True)
    scw_title=models.CharField(max_length=500,blank=True,null=True)
    scw_text = models.TextField()
    scw_whocanapply = models.TextField(db_column='scw_whoCanApply', blank=True, null=True)
    scw_status = models.IntegerField()
    scw_image = models.ImageField(upload_to='country_wise_scholarship_images/', blank=True, null=True)
    created_at = models.DateTimeField(blank=True, null=True)
    updated_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        db_table = 'country_wises'



class FailedJobs(models.Model):
    id = models.PositiveBigIntegerField(primary_key=True)
    connection = models.TextField()
    queue = models.TextField()
    payload = models.TextField()
    exception = models.TextField()
    failed_at = models.DateTimeField()

    class Meta:
        db_table = 'failed_jobs'


class Galleries(models.Model):
    image = models.CharField(max_length=255)
    caption = models.CharField(max_length=255)
    consultant_id = models.IntegerField()
    status = models.IntegerField()
    created_at = models.DateTimeField(blank=True, null=True)
    updated_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        db_table = 'galleries'


class HomeFeedback(models.Model):
    # fdk_id = models.AutoField(primary_key=True)
    consultant = models.IntegerField()
    student = models.IntegerField(null=True, blank=True)
    fdk_fullname = models.CharField(db_column='fdk_fullName', max_length=30)  # Field name made lowercase.
    fdk_email = models.CharField(max_length=30)
    fdk_phone = models.CharField(max_length=15, blank=True, null=True)
    fdk_nameofcompany = models.CharField(db_column='fdk_nameOfCompany', max_length=30, blank=True, null=True)  # Field name made lowercase.
    fdk_website = models.CharField(max_length=20, blank=True, null=True)
    fdk_msg = models.TextField()
    fdk_status = models.IntegerField(default=1, null=True)
    created_at = models.DateTimeField(blank=True, null=True)
    updated_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        db_table = 'home_feedback'
        # engine = 'InnoDB'

    def __str__(self):
        return self.fdk_nameofcompany


class Review(models.Model):
    consultant = models.IntegerField()
    student = models.IntegerField()
    raw_rating = models.IntegerField()
    rating = models.FloatField(default=0, validators=[MinValueValidator(1), MinValueValidator(5)])
    comment = models.TextField(null=True, blank=True, max_length=1000)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'review'

    def __str__(self):
        return str(self.rating)
    
    def save(self, *args, **kwargs):
            super().save(*args, **kwargs)

            student_ratings = Review.objects.filter(consultant=self.consultant, student=self.student)
            consultant  = Users.objects.filter(id=self.consultant).first()
            student = Students.objects.filter(id=self.student)

            if consultant is not None and student is not None:
                if len(student_ratings) > 1:
                    consultant.rating = self.rating
                    print('student rating: ', student_ratings)
                
                else:
                    if consultant.no_of_ratings == 0 and consultant.rating == 0.0:
                        consultant.rating = self.rating
                        consultant.no_of_ratings += 1

                    else:
                        # total_rating = sum(review.raw_rating for review in reviews)
                        total_ratings = consultant.rating * consultant.no_of_ratings
                        new_total_ratings = total_ratings + self.rating
                        num_ratings = consultant.no_of_ratings + 1
                        new_rating = round(new_total_ratings / num_ratings, 1)
                        consultant.rating = new_rating
                        consultant.no_of_ratings += 1

                consultant.save()
class Levels(models.Model):
    balance_id = models.IntegerField()
    student_id = models.IntegerField()
    consultant_id = models.IntegerField()
    level_1 = models.IntegerField(blank=True, null=True)
    level_2 = models.IntegerField(blank=True, null=True)
    level_3 = models.IntegerField(blank=True, null=True)
    level_4 = models.IntegerField(blank=True, null=True)
    level_5 = models.IntegerField(blank=True, null=True)
    status = models.IntegerField()
    created_at = models.DateTimeField(blank=True, null=True)
    updated_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        db_table = 'levels'

    def save(self, *args, **kwargs):
        # Check if the student_id and consultant_id match in StudentDetails
        student_details = StudentDetails.objects.filter(dets_regs_id=self.student_id, dets_favconsultantlist__contains=str(self.consultant_id))
        if student_details.exists():
            student_details = student_details.first()
            consultant_status, created = ConsultantStatus.objects.get_or_create(student=student_details, consultant_id=self.consultant_id)
            consultant_status.status = StudentDetails.VIEWED  # Set status to VIEWED (1)
            consultant_status.save()

        super().save(*args, **kwargs)

class Maps(models.Model):
    id = models.BigAutoField(primary_key=True)
    map_location = models.TextField(blank=True, null=True)
    consultant_id = models.IntegerField(blank=True, null=True)
    created_at = models.DateTimeField(blank=True, null=True)
    updated_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        db_table = 'maps'


class Migrations(models.Model):
    id = models.PositiveIntegerField(primary_key=True)
    migration = models.CharField(max_length=255)
    batch = models.IntegerField()

    class Meta:
        db_table = 'migrations'


class OfferLetters(models.Model):
    id = models.BigAutoField(primary_key=True)
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    status = models.IntegerField()
    created_at = models.DateTimeField(blank=True, null=True)
    updated_at = models.DateTimeField(blank=True, null=True)

    # Add the image field
    image = models.ImageField(upload_to='offer_letter_images/', blank=True, null=True)

    class Meta:
        db_table = 'offer_letters'


class PasswordResets(models.Model):
    email = models.CharField(max_length=255)
    token = models.CharField(max_length=255)
    created_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        db_table = 'password_resets'


class Rates(models.Model):
    id = models.BigAutoField(primary_key=True)
    rate_added_by = models.IntegerField()
    rate_added_to = models.IntegerField()
    first_rate = models.FloatField(blank=True, null=True)
    second_rate = models.FloatField(blank=True, null=True)
    third_rate = models.FloatField(blank=True, null=True)
    four_rate = models.FloatField(blank=True, null=True)
    five_rate = models.FloatField(blank=True, null=True)
    created_at = models.DateTimeField(blank=True, null=True)
    updated_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        db_table = 'rates'


class Results(models.Model):
    id = models.BigAutoField(primary_key=True)
    secondary = models.IntegerField()
    secondary_board = models.CharField(max_length=100, blank=True, null=True)
    secondary_result = models.FloatField()
    secondary_roll_no = models.CharField(max_length=50, blank=True, null=True)
    secondary_reg_no = models.CharField(max_length=50, blank=True, null=True)
    secondary_certificate_no = models.CharField(max_length=255, blank=True, null=True)
    secondary_passing_year = models.IntegerField(blank=True, null=True)
    secondary_certificate_copy = models.CharField(max_length=255, blank=True, null=True)
    higher = models.IntegerField()
    higher_board = models.CharField(max_length=50, blank=True, null=True)
    higher_result = models.FloatField()
    higher_roll_no = models.CharField(max_length=50, blank=True, null=True)
    higher_reg_no = models.CharField(max_length=50, blank=True, null=True)
    higher_certificate_no = models.CharField(max_length=255, blank=True, null=True)
    higher_passing_year = models.IntegerField(blank=True, null=True)
    higher_certificate_copy = models.CharField(max_length=255, blank=True, null=True)
    student_id = models.IntegerField()
    created_at = models.DateTimeField(blank=True, null=True)
    updated_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        db_table = 'results'


class ScholarShips(models.Model):
    schp_description = models.TextField(blank=True, null=True)
    apply_process = models.TextField(blank=True, null=True)
    consultant_id = models.IntegerField(blank=True, null=True)
    created_at = models.DateTimeField(blank=True, null=True)
    updated_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        db_table = 'scholar_ships'

        

class District(models.Model):
    # district_id = models.CharField(max_length=30, primary_key=True)
    name = models.CharField(max_length=30)
    lat = models.FloatField(blank=True, null=True)
    lon = models.FloatField(blank=True, null=True)
    website = models.CharField(max_length=100, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'district'


class Thana(models.Model):
    district = models.ForeignKey(District, on_delete=models.CASCADE, related_name='thanas')
    name = models.CharField(max_length=30)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'thana'


class StudentDetails(models.Model):
    WAITING = 0
    VIEWED = 1

    STATUS_CHOICES = [
        (WAITING, 'Waiting'),
        (VIEWED, 'Viewed'),
    ]
    dets_id = models.AutoField(primary_key=True)
    dets_regs_id = models.IntegerField()
    dets_bloodgroup = models.CharField(db_column='dets_bloodGroup', max_length=5, blank=True, null=True)  # Field name made lowercase.
    dets_fathername = models.CharField(db_column='dets_fatherName', max_length=30, blank=True, null=True)  # Field name made lowercase.
    dets_mothername = models.CharField(db_column='dets_motherName', max_length=30, blank=True, null=True)  # Field name made lowercase.
    dets_nationality = models.CharField(max_length=15, blank=True, null=True)
    dets_dob = models.DateField(blank=True, null=True)
    student_image = models.ImageField(upload_to='student_images/', blank=True, null=True)
    dets_thumbnaillink = models.CharField(db_column='dets_thumbnailLink', max_length=60, blank=True, null=True)  # Field name made lowercase.
    dets_favconsultantlist = models.CharField(db_column='dets_favConsultantList', max_length=120, blank=True, null=True)  # Field name made lowercase.
    dets_updatedate = models.DateField(db_column='dets_updateDate', blank=True, null=True)  # Field name made lowercase.
    dets_status = models.IntegerField(default=0)


    class Meta:
        db_table = 'student_details'

class ConsultantStatus(models.Model):
    student = models.ForeignKey('StudentDetails', on_delete=models.CASCADE)
    consultant_id = models.IntegerField()
    status = models.IntegerField(choices=StudentDetails.STATUS_CHOICES, default=StudentDetails.WAITING)


class Students(models.Model):
    full_name = models.CharField(max_length=30)
    student_user = models.ForeignKey(CustomUser, on_delete=models.CASCADE,null =True)
    email = models.CharField(unique=True, max_length=30)
    phone = models.CharField(unique=True, max_length=125)
    otp = models.CharField(max_length=150, blank=True, null=True)
    USER_TYPE_CHOICES = [
        (0, 'Student'),
        (1, 'Guardian'),
    ]
    GENDER_CHOICES = [
        (0, 'Male'),
        (1, 'Female'),
    ]
    STATUS_CHOICE = [
        (0, 'Inactive'),
        (1, 'Acive')
    ]
    user_type = models.IntegerField(choices=USER_TYPE_CHOICES)
    gender = models.CharField(choices=GENDER_CHOICES, max_length=10, null=True, blank=True)
    dets_status = models.IntegerField(default=0)
    student_name = models.CharField(max_length=255, blank=True, null=True)
    relation = models.CharField(max_length=255, blank=True, null=True)
    district = models.ForeignKey(District, on_delete=models.SET_NULL, blank=True, null=True)
    thana = models.ForeignKey(Thana, on_delete=models.SET_NULL, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    country_id = models.CharField(max_length=150, blank=True, null=True)
    countries = models.ManyToManyField(Countries, blank=True, null=True, related_name='countries')
    raw_password = models.CharField(max_length=60)
    password = models.CharField(max_length=255)
    status = models.IntegerField(choices=STATUS_CHOICE, default=0)
    created_at = models.DateTimeField(blank=True, null=True)
    updated_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        db_table = 'students'
        managed= True



class UserSession(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()

    def __str__(self):
        return f"{self.user.username} - {self.start_time} to {self.end_time}"

    class Meta:
        verbose_name_plural = "User Sessions"
    




class Users(models.Model):
    full_name = models.CharField(max_length=30)
    consultant_user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, null =True)
    user_name = models.CharField(max_length=150,  blank=True, null=True)
    email = models.CharField(unique=True, max_length=30)
    phone = models.CharField(unique=True, max_length=125)
    gender = models.CharField(max_length=50, blank=True, null=True)
    otp = models.CharField(max_length=150, blank=True, null=True)
    pin = models.CharField(max_length=50, blank=True, null=True)
    change_phone_otp = models.CharField(max_length=150, blank=True, null=True)
    about = models.TextField(blank=True, null=True)
    consultant_img = models.ImageField(upload_to='consultant_img/', blank=True, null=True)
    rating = models.FloatField(default=0.0, validators=[MinValueValidator(0.0), MinValueValidator(5.0)], null=True, blank=True)
    no_of_ratings = models.IntegerField(default=0, null=True, blank=True)
   
    land_phone = models.CharField(max_length=20, blank=True, null=True)
    fax_no = models.CharField(max_length=20, blank=True, null=True)
    company_name = models.CharField(max_length=60, blank=True, null=True)
    est_date = models.DateField(blank=True, null=True)
    district = models.ForeignKey(District, on_delete=models.CASCADE, blank=True, null=True)
    thana = models.ForeignKey(Thana, on_delete=models.CASCADE, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    website = models.CharField(max_length=40, blank=True, null=True)
    raw_password = models.CharField(max_length=60)
    password = models.CharField(max_length=255)
    user_role = models.IntegerField(blank=True, null=True)

    active_status = models.IntegerField(blank=True, null=True)
    suspension_time = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(blank=True, null=True)
    updated_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        db_table = 'users'
        managed=True


# class StudentViewLog(models.Model):
#     consultant_id =models.CharField(max_length=20, blank=True, null=True)
#     student_id = models.CharField(max_length=20, blank=True, null=True)
#     lead_level = models.IntegerField()  # Lead level clicked (0 for "My Lead", 1-5 for other leads)
#     viewed_at = models.DateTimeField(auto_now_add=True)

#     class Meta:
#         db_table = 'student_view_log'
#         managed = True