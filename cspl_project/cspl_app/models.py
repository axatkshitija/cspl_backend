# from django.db import models
from django.db import models
from django.utils import timezone
from datetime import timedelta
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password, check_password
from django.db.models import Q
import random

# Create your models here.
# from django.db import models


from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import send_mail
from django.conf import settings


class CollegeRegistration(models.Model):
    STATE_CHOICES = [
        ("Andhra Pradesh", "Andhra Pradesh"),
    ("Arunachal Pradesh", "Arunachal Pradesh"),
    ("Assam", "Assam"),
    ("Bihar", "Bihar"),
    ("Chhattisgarh", "Chhattisgarh"),
    ("Goa", "Goa"),
    ("Gujarat", "Gujarat"),
    ("Haryana", "Haryana"),
    ("Himachal Pradesh", "Himachal Pradesh"),
    ("Jharkhand", "Jharkhand"),
    ("Karnataka", "Karnataka"),
    ("Kerala", "Kerala"),
    ("Madhya Pradesh", "Madhya Pradesh"),
    ("Maharashtra", "Maharashtra"),
    ("Manipur", "Manipur"),
    ("Meghalaya", "Meghalaya"),
    ("Mizoram", "Mizoram"),
    ("Nagaland", "Nagaland"),
    ("Odisha", "Odisha"),
    ("Punjab", "Punjab"),
    ("Rajasthan", "Rajasthan"),
    ("Sikkim", "Sikkim"),
    ("Tamil Nadu", "Tamil Nadu"),
    ("Telangana", "Telangana"),
    ("Tripura", "Tripura"),
    ("Uttar Pradesh", "Uttar Pradesh"),
    ("Uttarakhand", "Uttarakhand"),
    ("West Bengal", "West Bengal"),
]

    COUNTRY_CHOICES = [
        ("Afghanistan", "Afghanistan"),
    ("Albania", "Albania"),
    ("Algeria", "Algeria"),
    ("Andorra", "Andorra"),
    ("Angola", "Angola"),
    ("Argentina", "Argentina"),
    ("Armenia", "Armenia"),
    ("Australia", "Australia"),
    ("Austria", "Austria"),
    ("Azerbaijan", "Azerbaijan"),
    ("Bahrain", "Bahrain"),
    ("Bangladesh", "Bangladesh"),
    ("Belarus", "Belarus"),
    ("Belgium", "Belgium"),
    ("Bhutan", "Bhutan"),
    ("Bolivia", "Bolivia"),
    ("Bosnia and Herzegovina", "Bosnia and Herzegovina"),
    ("Botswana", "Botswana"),
    ("Brazil", "Brazil"),
    ("Brunei", "Brunei"),
    ("Bulgaria", "Bulgaria"),
    ("Cambodia", "Cambodia"),
    ("Cameroon", "Cameroon"),
    ("Canada", "Canada"),
    ("Chile", "Chile"),
    ("China", "China"),
    ("Colombia", "Colombia"),
    ("Costa Rica", "Costa Rica"),
    ("Croatia", "Croatia"),
    ("Cuba", "Cuba"),
    ("Cyprus", "Cyprus"),
    ("Czech Republic", "Czech Republic"),
    ("Denmark", "Denmark"),
    ("Dominican Republic", "Dominican Republic"),
    ("Ecuador", "Ecuador"),
    ("Egypt", "Egypt"),
    ("El Salvador", "El Salvador"),
    ("Estonia", "Estonia"),
    ("Ethiopia", "Ethiopia"),
    ("Finland", "Finland"),
    ("France", "France"),
    ("Georgia", "Georgia"),
    ("Germany", "Germany"),
    ("Ghana", "Ghana"),
    ("Greece", "Greece"),
    ("Guatemala", "Guatemala"),
    ("Hong Kong", "Hong Kong"),
    ("Hungary", "Hungary"),
    ("Iceland", "Iceland"),
    ("India", "India"),
    ("Indonesia", "Indonesia"),
    ("Iran", "Iran"),
    ("Iraq", "Iraq"),
    ("Ireland", "Ireland"),
    ("Israel", "Israel"),
    ("Italy", "Italy"),
    ("Jamaica", "Jamaica"),
    ("Japan", "Japan"),
    ("Jordan", "Jordan"),
    ("Kazakhstan", "Kazakhstan"),
    ("Kenya", "Kenya"),
    ("Kuwait", "Kuwait"),
    ("Kyrgyzstan", "Kyrgyzstan"),
    ("Laos", "Laos"),
    ("Latvia", "Latvia"),
    ("Lebanon", "Lebanon"),
    ("Libya", "Libya"),
    ("Lithuania", "Lithuania"),
    ("Luxembourg", "Luxembourg"),
    ("Malaysia", "Malaysia"),
    ("Maldives", "Maldives"),
    ("Malta", "Malta"),
    ("Mauritius", "Mauritius"),
    ("Mexico", "Mexico"),
    ("Moldova", "Moldova"),
    ("Mongolia", "Mongolia"),
    ("Morocco", "Morocco"),
    ("Myanmar", "Myanmar"),
    ("Nepal", "Nepal"),
    ("Netherlands", "Netherlands"),
    ("New Zealand", "New Zealand"),
    ("Nigeria", "Nigeria"),
    ("North Korea", "North Korea"),
    ("Norway", "Norway"),
    ("Oman", "Oman"),
    ("Pakistan", "Pakistan"),
    ("Panama", "Panama"),
    ("Paraguay", "Paraguay"),
    ("Peru", "Peru"),
    ("Philippines", "Philippines"),
    ("Poland", "Poland"),
    ("Portugal", "Portugal"),
    ("Qatar", "Qatar"),
    ("Romania", "Romania"),
    ("Russia", "Russia"),
    ("Saudi Arabia", "Saudi Arabia"),
    ("Serbia", "Serbia"),
    ("Singapore", "Singapore"),
    ("Slovakia", "Slovakia"),
    ("Slovenia", "Slovenia"),
    ("South Africa", "South Africa"),
    ("South Korea", "South Korea"),
    ("Spain", "Spain"),
    ("Sri Lanka", "Sri Lanka"),
    ("Sweden", "Sweden"),
    ("Switzerland", "Switzerland"),
    ("Syria", "Syria"),
    ("Taiwan", "Taiwan"),
    ("Tajikistan", "Tajikistan"),
    ("Tanzania", "Tanzania"),
    ("Thailand", "Thailand"),
    ("Tunisia", "Tunisia"),
    ("Turkey", "Turkey"),
    ("Turkmenistan", "Turkmenistan"),
    ("Uganda", "Uganda"),
    ("Ukraine", "Ukraine"),
    ("United Arab Emirates", "United Arab Emirates"),
    ("United Kingdom", "United Kingdom"),
    ("United States", "United States"),
    ("Uruguay", "Uruguay"),
    ("Uzbekistan", "Uzbekistan"),
    ("Venezuela", "Venezuela"),
    ("Vietnam", "Vietnam"),
    ("Yemen", "Yemen"),
    ("Zambia", "Zambia"),
    ("Zimbabwe", "Zimbabwe"),
]

    FILLED_BY_CHOICES = [
        ('Admin', 'Admin'),
        ('Coach', 'Coach'),
        ('Sports Teacher', 'Sports Teacher'),
        ('Management Person', 'Management Person'),
    ]

    SPORT_CHOICES = [
        ('Cricket', 'Cricket'),
        ('Football', 'Football'),
        ('Hockey', 'Hockey'),
        ('Badminton', 'Badminton'),
    ]

    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('submitted', 'Submitted'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]

    full_name = models.CharField(max_length=255)
    college_logo= models.ImageField(upload_to='college_logos/', null=True, blank=True)
    ngo_or_trust = models.CharField(max_length=255)
    registration_number = models.CharField(max_length=100, unique=True)
    # team_name = models.CharField(max_length=150)
    generated_registration_no = models.CharField(
        max_length=20,
        unique=True,
        null=True,
        blank=True
    )  # CSPL202600001
    team_name = models.CharField(max_length=150)
    team_logo = models.ImageField(upload_to='team_logos/', null=True, blank=True)
    address_line_1 = models.CharField(max_length=255)
    address_line_2 = models.CharField(max_length=255, blank=True, null=True)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100, choices=STATE_CHOICES)
    country = models.CharField(max_length=100, choices=COUNTRY_CHOICES, default='India')
    pin_code = models.CharField(max_length=10)

    total_students = models.PositiveIntegerField(null=True, blank=True)
    teaching_staff = models.PositiveIntegerField(null=True, blank=True)
    non_teaching_staff = models.PositiveIntegerField(null=True, blank=True)

    current_sport = models.CharField(
        max_length=50,
        choices=SPORT_CHOICES,
        null=True,
        blank=True
    )
    future_sports = models.JSONField(default=list, blank=True)

    has_ground = models.BooleanField(default=False)
    ground_dimension_sq_m = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True
    )

    filled_by = models.CharField(max_length=50, choices=FILLED_BY_CHOICES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='submitted')
    # password = models.CharField(max_length=255)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # def set_password(self, raw_password):
    #     self.password = make_password(raw_password)

    # def check_password(self, raw_password):
    #     return check_password(raw_password, self.password)
    
    @property
    def is_authenticated(self):
        return True
    
    def __str__(self):
        return self.full_name


import secrets

class CollegeAuthToken(models.Model):
    college = models.OneToOneField(
        CollegeRegistration,
        on_delete=models.CASCADE,
        related_name='auth_token'
    )
    key = models.CharField(max_length=64, unique=True, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.key:
            self.key = secrets.token_hex(32)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.college.registration_number} - {self.key}"


class CollegeContactPerson(models.Model):
    CONTACT_TYPE_CHOICES = [
        ('coach', 'Coach'),
        ('sports_teacher', 'Sports Teacher'),
        ('management_person', 'Management Person'),
    ]

    college = models.ForeignKey(CollegeRegistration, on_delete=models.CASCADE, related_name='contacts')
    contact_type = models.CharField(max_length=30, choices=CONTACT_TYPE_CHOICES)
    name = models.CharField(max_length=255)
    phone = models.CharField(max_length=20)
    email = models.EmailField(unique=True)
    email_verified = models.BooleanField(default=False)
    phone_verified = models.BooleanField(default=False)

    email_otp = models.CharField(max_length=6, null=True, blank=True)
    email_otp_created_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = ('college', 'contact_type')

    def __str__(self):
        return f"{self.college.full_name} - {self.contact_type}"

    # class Meta:
    #     unique_together = ('college', 'contact_type')

    # def __str__(self):
    #     return f"{self.college.full_name} - {self.contact_type}"

class CollegeContactOTP(models.Model):
    OTP_TYPE_CHOICES = [
        ('email', 'Email'),
        ('sms', 'SMS'),
    ]

    college = models.ForeignKey(
        CollegeRegistration,
        on_delete=models.CASCADE,
        related_name='contact_otps',
        null=True,
        blank=True
    )
    contact = models.ForeignKey(
        CollegeContactPerson,
        on_delete=models.CASCADE,
        related_name='otps',
        null=True,
        blank=True
    )
    otp_type = models.CharField(max_length=10, choices=OTP_TYPE_CHOICES)
    target = models.CharField(max_length=255)
    otp = models.CharField(max_length=6)
    is_used = models.BooleanField(default=False)
    expires_at = models.DateTimeField()
    verified_at = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    @staticmethod
    def generate_otp():
        return str(random.randint(100000, 999999))

    def is_expired(self):
        return timezone.now() > self.expires_at

    def __str__(self):
        return f"{self.contact.contact_type} - {self.otp_type} - {self.target}"

# models.py
class CollegeTeamMember(models.Model):
    ROLE_CHOICES = [
        ('Batsman', 'Batsman'),
        ('Bowler', 'Bowler'),
        ('Wicketkeeper', 'Wicketkeeper'),
        ('All Rounder', 'All Rounder'),
        ('Coach','Coach'),
        ('Team Manager','Team Manager'),
        ('Physiotherapist','Physiotherapist'),
        ('Admin','Admin'),
    ]

    RELATION_CHOICES = [
        ('Father', 'Father'),
        ('Mother', 'Mother'),
        ('Guardian', 'Guardian'),
    ]
    ROLE_PREFIX_MAP = {
        'Batsman': 'BT',
        'Bowler': 'BL',
        'Wicketkeeper': 'WK',
        'All Rounder': 'AR',
        'Physiotherapist': 'DR',
        'Coach': 'CO',
        'Admin': 'AD',
        'Team Manager': 'TM',
    }

    college = models.ForeignKey(
        CollegeRegistration,
        on_delete=models.CASCADE,
        related_name='team_members'
    )
    member_code = models.CharField(max_length=20, unique=True, blank=True, null=True)

    role = models.CharField(max_length=50, choices=ROLE_CHOICES)
    name = models.CharField(max_length=255)
    age = models.PositiveIntegerField()
    dob = models.DateField()
    mobile_no = models.CharField(max_length=20)
    alternate_no = models.CharField(max_length=20, blank=True, null=True)
    relation = models.CharField(max_length=20, choices=RELATION_CHOICES, blank=True, null=True)
    email = models.EmailField()
    current_address = models.TextField()
    permanent_address = models.TextField()
    photo = models.ImageField(upload_to='team_members/', blank=True, null=True)
    no_photo = models.BooleanField(default=False)

    father_name = models.CharField(max_length=255, blank=True, null=True)
    mother_name = models.CharField(max_length=255, blank=True, null=True)
    sibling_details = models.JSONField(default=list, blank=True)
    education_details = models.JSONField(default=list, blank=True)

    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)

    class Meta:
        ordering = ['id']

    def __str__(self):
        return f"{self.name} - {self.college.team_name}"

    def generate_member_code(self):
        prefix = self.ROLE_PREFIX_MAP.get(self.role, 'TM')
        name_part = (self.name or '').replace(' ', '').upper()[:4].ljust(4, 'X')

        last_member = CollegeTeamMember.objects.filter(
            member_code__startswith=f"{prefix}{name_part}"
        ).exclude(
            Q(member_code__isnull=True) | Q(member_code="")
        ).order_by('-member_code').first()

        if last_member and last_member.member_code:
            last_number = int(last_member.member_code[-5:])
            next_number = last_number + 1
        else:
            next_number = 1

        return f"{prefix}{name_part}{str(next_number).zfill(5)}"

    def save(self, *args, **kwargs):
        if not self.member_code:
            self.member_code = self.generate_member_code()
        super().save(*args, **kwargs)



class CollegeDocument(models.Model):
    college = models.OneToOneField(
        CollegeRegistration,
        on_delete=models.CASCADE,
        related_name='documents'
    )
    registration_certificate = models.FileField(upload_to='college_documents/registration_certificates/')
    pan_card = models.FileField(upload_to='college_documents/pan_cards/')
    additional_document = models.FileField(
        upload_to='college_documents/additional_documents/',
        blank=True,
        null=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Documents - {self.college.registration_number}"
    

from django.utils.crypto import get_random_string

User = get_user_model()
class LoginOTP(models.Model):
    LOGIN_TYPE_CHOICES = [
        ("email", "Email"),
        ("sms", "SMS"),
    ]

    college = models.ForeignKey(CollegeRegistration, on_delete=models.CASCADE)
    login_type = models.CharField(max_length=10, choices=LOGIN_TYPE_CHOICES, default="email")
    target = models.CharField(max_length=255)
    otp_code = models.CharField(max_length=6)
    is_used = models.BooleanField(default=False)
    attempts = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()

    def is_expired(self):
        return timezone.now() > self.expires_at

    @classmethod
    def generate_otp(cls):
        return get_random_string(6, allowed_chars="0123456789")

    @classmethod
    def create_otp(cls, college, target, login_type="email"):
        otp_code = cls.generate_otp()
        return cls.objects.create(
            college=college,
            login_type=login_type,
            target=target,
            otp_code=otp_code,
            expires_at=timezone.now() + timedelta(minutes=10)
        )

# class LoginOTP(models.Model):
#     college = models.ForeignKey(CollegeRegistration, on_delete=models.CASCADE)
#     mobile_no = models.CharField(max_length=15)
#     otp_code = models.CharField(max_length=6)
#     is_used = models.BooleanField(default=False)
#     attempts = models.IntegerField(default=0)
#     created_at = models.DateTimeField(auto_now_add=True)
#     expires_at = models.DateTimeField()
#     def is_expired(self):
#         return timezone.now() > self.expires_at

#     @classmethod
#     def create_otp(cls, user, mobile_no, otp_code):
#         return cls.objects.create(
#             user=user,
#             mobile_no=mobile_no,
#             otp_code=otp_code,
#             expires_at=timezone.now() + timedelta(minutes=5)
#         )




from django.db import models


class SponsorRegistration(models.Model):
    class IndustryChoices(models.TextChoices):
        IT = "IT", "IT"
        TEST = "Test", "Test"

    class JobTitleChoices(models.TextChoices):
        FRONTEND_DEVELOPER = "FrontEnd Developer", "FrontEnd Developer"
        TEST_ENGINEER = "Test Engineer", "Test Engineer"

    class SponsorTierChoices(models.TextChoices):
        TITLE_SPONSOR = "Title Sponsor", "Title Sponsor"
        POWERED_BY = "Powered By / Co-Sponsor", "Powered By / Co-Sponsor"
        ASSOCIATE_SPONSOR = "Associate Sponsor", "Associate Sponsor"
        CATEGORY_PARTNER = "Category Partner", "Category Partner"

    class PrimaryGoalChoices(models.TextChoices):
        BRAND_AWARENESS = "Brand Awareness / Reach", "Brand Awareness / Reach"
        PRODUCT_LAUNCH = "Product Launch / Direct Sales", "Product Launch / Direct Sales"
        CSR = "CSR (Corporate Social Responsibility)", "CSR (Corporate Social Responsibility)"
        RECRUITMENT = "Recruitment / Campus Connection", "Recruitment / Campus Connection"

    class BudgetRangeChoices(models.TextChoices):
        RANGE_10K_50K = "₹10,000 - ₹50,000", "₹10,000 - ₹50,000"
        RANGE_50K_100K = "₹50,000 - ₹100,000", "₹50,000 - ₹100,000"
        RANGE_100K_500K = "₹100,000 - ₹500,000", "₹100,000 - ₹500,000"
        RANGE_500K_PLUS = "₹500,000+", "₹500,000+"

    class PartnershipDurationChoices(models.TextChoices):
        ONE_TIME = "One-time Event", "One-time Event"
        ANNUAL = "Annual", "Annual"
        MULTI_YEAR = "Multi-year", "Multi-year"

    company_name = models.CharField(max_length=255)
    industry_sector = models.CharField(max_length=100, choices=IndustryChoices.choices)
    company_website = models.URLField()
    headquarters_address = models.TextField()

    full_name = models.CharField(max_length=255)
    job_title = models.CharField(max_length=100, choices=JobTitleChoices.choices)
    email = models.EmailField()
    phone_number = models.CharField(max_length=20)

    sponsor_tier = models.CharField(max_length=100, choices=SponsorTierChoices.choices)
    preferred_engagement_zones = models.JSONField(default=list, blank=True)
    primary_goal = models.CharField(max_length=100, choices=PrimaryGoalChoices.choices)
    target_demographic = models.JSONField(default=list, blank=True)

    require_stall_booth = models.BooleanField(default=False)
    instagram = models.URLField(blank=True, null=True)
    linkedin = models.URLField(blank=True, null=True)
    x_twitter = models.URLField(blank=True, null=True)
    facebook = models.URLField(blank=True, null=True)

    estimated_budget_range = models.CharField(
        max_length=100,
        choices=BudgetRangeChoices.choices,
        blank=True,
        null=True
    )
    partnership_duration = models.CharField(
        max_length=50,
        choices=PartnershipDurationChoices.choices
    )

    company_logo = models.FileField(upload_to="sponsor_documents/company_logos/")
    gst_details = models.FileField(upload_to="sponsor_documents/gst_details/")

    additional_notes = models.TextField(blank=True, null=True)
    agreed_to_terms = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.company_name 

from django.db import models


class VendorRegistration(models.Model):
    ENTITY_TYPE_CHOICES = [
        ("sole_proprietorship", "Sole Proprietorship"),
        ("partnership_llp", "Partnership / LLP"),
        ("private_limited_company", "Private Limited Company"),
        ("other", "Other"),
    ]

    SERVICE_CATEGORY_CHOICES = [
        ("it_digital_services", "IT & Digital Services"),
        ("sports_infrastructure_venue", "Sports Infrastructure & Venue"),
        ("apparel_merchandise", "Apparel & Merchandise"),
        ("event_management_operations", "Event Management & Operations"),
        ("media_marketing", "Media & Marketing"),
        ("logistics_hospitality", "Logistics & Hospitality"),
    ]

    legal_business_name = models.CharField(max_length=255)
    trade_name = models.CharField(max_length=255, blank=True, null=True)
    entity_type = models.CharField(max_length=50, choices=ENTITY_TYPE_CHOICES)
    other_entity_type = models.CharField(max_length=255, blank=True, null=True)
    registered_office_address = models.TextField()
    cin = models.CharField(max_length=50, blank=True, null=True)

    core_category_of_service = models.CharField(max_length=100, choices=SERVICE_CATEGORY_CHOICES)

    primary_contact_person_name = models.CharField(max_length=255)
    designation = models.CharField(max_length=255)
    mobile_number = models.CharField(max_length=15)
    email = models.EmailField()
    escalation_contact = models.CharField(max_length=255, blank=True, null=True)

    pan = models.CharField(max_length=20)
    gstin = models.CharField(max_length=20, blank=True, null=True)
    msme_registration_number = models.CharField(max_length=50, blank=True, null=True)

    bank_name = models.CharField(max_length=255)
    account_holder_name = models.CharField(max_length=255)
    account_number = models.CharField(max_length=50)
    ifsc_code = models.CharField(max_length=20)

    years_of_active_operation = models.PositiveIntegerField(default=0)
    handled_large_scale_sports_tournaments = models.BooleanField(default=False)
    prominent_events_or_projects = models.TextField(blank=True, null=True)

    pan_card_copy = models.FileField(upload_to="vendor_documents/pan/", blank=True, null=True)
    gst_registration_certificate = models.FileField(upload_to="vendor_documents/gst/", blank=True, null=True)
    cancelled_cheque_or_passbook = models.FileField(upload_to="vendor_documents/bank/", blank=True, null=True)
    company_profile_or_pitch_deck = models.FileField(upload_to="vendor_documents/profile/", blank=True, null=True)

    declaration_name = models.CharField(max_length=255)
    declaration_designation = models.CharField(max_length=255)
    signature_and_company_seal = models.FileField(upload_to="vendor_documents/signature/", blank=True, null=True)
    declaration_date = models.DateField()

    email_verified = models.BooleanField(default=False)
    phone_verified = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.legal_business_name

import random
from django.db import models
from django.utils import timezone


class VendorContactOTP(models.Model):
    CONTACT_TYPE_CHOICES = [
        ("primary", "Primary"),
        ("escalation", "Escalation"),
    ]

    OTP_TYPE_CHOICES = [
        ("email", "Email"),
        ("sms", "SMS"),
    ]

    contact_type = models.CharField(max_length=20, choices=CONTACT_TYPE_CHOICES)
    otp_type = models.CharField(max_length=10, choices=OTP_TYPE_CHOICES)
    target = models.CharField(max_length=255)
    otp = models.CharField(max_length=10)
    is_used = models.BooleanField(default=False)
    is_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    verified_at = models.DateTimeField(blank=True, null=True)

    @staticmethod
    def generate_otp():
        return str(random.randint(100000, 999999))

    def is_expired(self):
        return timezone.now() > self.expires_at

    def __str__(self):
        return f"{self.otp_type} - {self.target}"


# TOURNAMENT, LIVE SCORING & HOMEPAGE CMS MODELS (NEW MODULES)


class Tournament(models.Model):
    name = models.CharField(max_length=250)
    season = models.CharField(max_length=100)
    image = models.ImageField(upload_to='tournaments/', null=True, blank=True)
    start_date = models.DateField()
    end_date = models.DateField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} - {self.season}"


class Venue(models.Model):
    name = models.CharField(max_length=200)
    city = models.CharField(max_length=100)
    address = models.TextField(blank=True,null=True)

    def __str__(self):
        return f"{self.name} - {self.city}"


class Match(models.Model):
    FORMAT_CHOICES = [
        ("T10", "T10 (10 overs)"),
        ("T20", "T20 (20 overs)"),
        ("ODI", "ODI (50 overs)"),
        ('CUSTOM', 'Custom')
    ]
    STATUS_CHOICES = [
        ('upcoming', 'Upcoming'),
        ('live', 'live'),
        ('innings_break', 'Innings Break'),
        ('completed', 'Completed'),
        ('abandoned', 'Abandoned'),
        ('postponed', 'Postponed'),
        ('cancelled', 'Cancelled'),
        ('no_result', 'No Result'),
    ]

    TOSS_DECISION_CHOICES = [
        ('bat', 'Bat'),
        ('bowl', 'Bowl'), 
    ]

    tournament = models.ForeignKey(Tournament, on_delete=models.CASCADE, related_name='matches')
    team_a = models.ForeignKey(CollegeRegistration, on_delete=models.CASCADE, related_name='home_matches')
    team_b = models.ForeignKey(CollegeRegistration, on_delete=models.CASCADE, related_name='away_matches')
    venue = models.ForeignKey(Venue, on_delete=models.SET_NULL, null=True, blank=True)
    match_datetime = models.DateTimeField()
    format = models.CharField(max_length=20, choices=FORMAT_CHOICES, default='T20')
    total_overs = models.PositiveIntegerField(default=20)
    thumbnail_image = models.ImageField(
        upload_to='matches/thumbnails/', 
        null=True, 
        blank=True, 
        help_text="Match Day poster or background thumbnail for UI card"
    )
    toss_winner = models.ForeignKey(CollegeRegistration, on_delete=models.SET_NULL, null=True, blank=True, related_name='toss_won_matches')
    toss_decision = models.CharField(max_length=10, choices=TOSS_DECISION_CHOICES, null=True, blank=True)
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='upcoming')
    winner = models.ForeignKey(CollegeRegistration, on_delete=models.SET_NULL, null=True, blank=True, related_name='matches_won')
    result_description = models.CharField(max_length=255, blank=True, null=True)
    player_of_match = models.ForeignKey(CollegeTeamMember, on_delete=models.SET_NULL, null=True, blank=True, related_name='pom_matches')

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-match_datetime']

    def __str__(self):
        return f"{self.team_a.team_name} vs {self.team_b.team_name} - {self.match_datetime.strftime('%d %b %Y')}"

    def save(self, *args, **kwargs):
        is_now_live = False
        
        # Check karenge ki kya yeh update ho raha hai aur status 'live' ho gaya hai
        if self.pk:
            old_instance = Match.objects.filter(pk=self.pk).first()
            if old_instance and old_instance.status != 'live' and self.status == 'live':
                is_now_live = True
        else:
            if self.status == 'live':
                is_now_live = True

        super().save(*args, **kwargs)

        # Agar match live ho gaya hai, toh sabhi active subscribers ko email bhej do
        if is_now_live:
            subscribers = list(NewsletterSubscription.objects.filter(is_active=True).values_list('email', flat=True))
            
            if subscribers:
                team_a_name = self.team_a.team_name if self.team_a else "Team A"
                team_b_name = self.team_b.team_name if self.team_b else "Team B"
                
                # Agar LiveStreamConfig linked hai toh uska URL lenge, warna default message
                stream_url = "https://cspl.com/live" # Aap apna frontend/streaming link de sakte hain
                if hasattr(self, 'live_stream') and self.live_stream and self.live_stream.youtube_stream_url:
                    stream_url = self.live_stream.youtube_stream_url

                subject = f"🔴 LIVE NOW: {team_a_name} vs {team_b_name} - CSPL Match Streaming"
                message = (
                    f"Hello from College Sports Premier League (CSPL)!\n\n"
                    f"The match has just started and is LIVE right now! Catch all the action live:\n\n"
                    f"⚔️ Match: {team_a_name} vs {team_b_name}\n"
                    # f"📺 Watch Live Here: {stream_url}\n\n"
                    f"Grab your snacks and join the stream now!\n\n"
                    f"Regards,\nCSPL Team"
                )
                
                send_mail(
                    subject=subject,
                    message=message,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=subscribers,
                    fail_silently=True,
                )

class MatchPlayingXI(models.Model):
    match = models.ForeignKey(Match, on_delete=models.CASCADE, related_name='squads')
    team = models.ForeignKey(CollegeRegistration, on_delete=models.CASCADE)
    player = models.ForeignKey(CollegeTeamMember, on_delete=models.CASCADE)
    is_captain = models.BooleanField(default=False)
    is_wicketkeeper = models.BooleanField(default=False)
    is_substitute = models.BooleanField(default=False)

    class Meta:
        unique_together = ('match', 'player')

    def __str__(self):
        role_tag = " (C)" if self.is_captain else (" (WK)" if self.is_wicketkeeper else "")
        return f"{self.player.name}{role_tag} - {self.team.team_name}"


class Innings(models.Model):
    match = models.ForeignKey(Match, on_delete=models.CASCADE, related_name='innings')
    innings_number = models.PositiveSmallIntegerField(choices=[(1, '1st Innings'), (2, '2nd Innings')])
    batting_team = models.ForeignKey(CollegeRegistration, on_delete=models.CASCADE, related_name='batting_innings')
    bowling_team = models.ForeignKey(CollegeRegistration, on_delete=models.CASCADE, related_name='bowling_innings')
    
    total_runs = models.PositiveIntegerField(default=0)
    total_wickets = models.PositiveSmallIntegerField(default=0)
    total_overs = models.DecimalField(max_digits=4, decimal_places=1, default=0.0)  # e.g., 19.4
    is_completed = models.BooleanField(default=False)
    is_declared = models.BooleanField(default=False)

    class Meta:
        unique_together = ('match', 'innings_number')

    def __str__(self):
        return f"Match {self.match.id} - Innings {self.innings_number} ({self.batting_team.team_name})"


# class BallByBall(models.Model):
#     EXTRA_CHOICES = [
#         ('none', 'None'),
#         ('wide', 'Wide'),
#         ('no_ball', 'No Ball'),
#         ('bye', 'Bye'),
#         ('leg_bye', 'Leg Bye'),
#         ('penalty', 'Penalty'),
#     ]
#     WICKET_CHOICES = [
#         ('bowled', 'Bowled'),
#         ('caught', 'Caught'),
#         ('lbw', 'LBW'),
#         ('run_out', 'Run Out'),
#         ('stumped', 'Stumped'),
#         ('hit_wicket', 'Hit Wicket'),
#         ('retired_hurt', 'Retired Hurt'),
#         ('retired_out', 'Retired Out'),
#         ('obstructing_field', 'Obstructing Field'),
#     ]

#     innings = models.ForeignKey(Innings, on_delete=models.CASCADE, related_name='balls')
#     over_number = models.PositiveIntegerField()   # 0 to 49
#     ball_number = models.PositiveIntegerField()   # 1 to 6 (legal delivery sequence)
    
#     bowler = models.ForeignKey(CollegeTeamMember, on_delete=models.CASCADE, related_name='bowled_balls')
#     striker = models.ForeignKey(CollegeTeamMember, on_delete=models.CASCADE, related_name='striker_balls')
#     non_striker = models.ForeignKey(CollegeTeamMember, on_delete=models.CASCADE, related_name='non_striker_balls')
    
#     runs_scored = models.PositiveSmallIntegerField(default=0)  # 0, 1, 2, 3, 4, 6
#     is_dot_ball = models.BooleanField(default=False)
#     is_four = models.BooleanField(default=False)
#     is_six = models.BooleanField(default=False)

#     extra_type = models.CharField(max_length=20, choices=EXTRA_CHOICES, default='none')
#     extra_runs = models.PositiveSmallIntegerField(default=0)
    
#     is_wicket = models.BooleanField(default=False)
#     wicket_type = models.CharField(max_length=30, choices=WICKET_CHOICES, null=True, blank=True)
#     player_dismissed = models.ForeignKey(CollegeTeamMember, on_delete=models.SET_NULL, null=True, blank=True, related_name='dismissals')
#     fielder_involved = models.ForeignKey(CollegeTeamMember, on_delete=models.SET_NULL, null=True, blank=True, related_name='fielding_actions')

#     commentary_text = models.CharField(max_length=255, blank=True, null=True)
#     timestamp = models.DateTimeField(auto_now_add=True)

#     class Meta:
#         ordering = ['innings', 'over_number', 'ball_number', 'timestamp']


from django.db import models
from django.core.exceptions import ValidationError

class BallByBall(models.Model):
    EXTRA_CHOICES = [
        ('none', 'None'),
        ('wide', 'Wide'),
        ('no_ball', 'No Ball'),
        ('bye', 'Bye'),
        ('leg_bye', 'Leg Bye'),
        ('penalty', 'Penalty'),
    ]
    WICKET_CHOICES = [
        ('bowled', 'Bowled'),
        ('caught', 'Caught'),
        ('lbw', 'LBW'),
        ('run_out', 'Run Out'),
        ('stumped', 'Stumped'),
        ('hit_wicket', 'Hit Wicket'),
        ('retired_hurt', 'Retired Hurt'),
        ('retired_out', 'Retired Out'),
        ('obstructing_field', 'Obstructing Field'),
    ]

    innings = models.ForeignKey('Innings', on_delete=models.CASCADE, related_name='balls')
    over_number = models.PositiveIntegerField()   # 0 to 49
    ball_number = models.PositiveIntegerField()   # 1 to 6
    
    bowler = models.ForeignKey('CollegeTeamMember', on_delete=models.CASCADE, related_name='bowled_balls')
    striker = models.ForeignKey('CollegeTeamMember', on_delete=models.CASCADE, related_name='striker_balls')
    non_striker = models.ForeignKey('CollegeTeamMember', on_delete=models.CASCADE, related_name='non_striker_balls')
    
    runs_scored = models.PositiveSmallIntegerField(default=0)
    is_dot_ball = models.BooleanField(default=False)
    is_four = models.BooleanField(default=False)
    is_six = models.BooleanField(default=False)

    extra_type = models.CharField(max_length=20, choices=EXTRA_CHOICES, default='none')
    extra_runs = models.PositiveSmallIntegerField(default=0)
    
    is_wicket = models.BooleanField(default=False)
    wicket_type = models.CharField(max_length=30, choices=WICKET_CHOICES, null=True, blank=True)
    player_dismissed = models.ForeignKey(
        'CollegeTeamMember', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='dismissals'
    )
    fielder_involved = models.ForeignKey(
        'CollegeTeamMember', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='fielding_actions'
    )

    commentary_text = models.CharField(max_length=255, blank=True, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['innings', 'over_number', 'ball_number', 'timestamp']

    def clean(self):
        super().clean()

        # 1. Duplicate Ball Number Validation (Cricket Legal vs Extra Delivery Check)
        if hasattr(self, 'innings') and self.innings:
            existing_deliveries = BallByBall.objects.filter(
                innings=self.innings,
                over_number=self.over_number,
                ball_number=self.ball_number
            )
            if self.pk:
                existing_deliveries = existing_deliveries.exclude(pk=self.pk)

            # Check if a legal delivery (None/Bye/Leg Bye) already exists for this over and ball number
            has_completed_legal_ball = existing_deliveries.filter(
                extra_type__in=['none', 'bye', 'leg_bye']
            ).exists()

            if has_completed_legal_ball:
                raise ValidationError({
                    'ball_number': f"Over {self.over_number}, Ball {self.ball_number} has already been recorded! Please increment the ball number for the next delivery."
                })

            # Check if current ball is legal and another legal delivery is being attempted under the same ball number
            if self.extra_type in ['none', 'bye', 'leg_bye'] and existing_deliveries.filter(extra_type__in=['none', 'bye', 'leg_bye']).exists():
                raise ValidationError({
                    'ball_number': f"Cannot save two legal deliveries for Over {self.over_number}, Ball {self.ball_number}."
                })

        # 2. Striker and Non-Striker cannot be the same player
        if self.striker_id and self.non_striker_id and self.striker_id == self.non_striker_id:
            raise ValidationError("Striker and Non-Striker cannot be the same player.")

        # 3. Dismissed Batsman Check
        if hasattr(self, 'innings') and self.innings:
            previous_balls = BallByBall.objects.filter(
                innings=self.innings, 
                is_wicket=True
            ).exclude(wicket_type='retired_hurt')
            if self.pk:
                previous_balls = previous_balls.exclude(pk=self.pk)

            dismissed_player_ids = set()
            for b in previous_balls:
                if b.player_dismissed_id:
                    dismissed_player_ids.add(b.player_dismissed_id)
                elif b.striker_id:
                    dismissed_player_ids.add(b.striker_id)

            if self.striker_id in dismissed_player_ids:
                raise ValidationError({
                    'striker': f"Invalid: {self.striker.name} has already been dismissed (OUT) in this innings!"
                })

            if self.non_striker_id in dismissed_player_ids:
                raise ValidationError({
                    'non_striker': f"Invalid: {self.non_striker.name} has already been dismissed (OUT) in this innings!"
                })

        # 4. Runs Boundary (0 to 6)
        if self.runs_scored not in [0, 1, 2, 3, 4, 5, 6]:
            raise ValidationError({
                'runs_scored': 'Runs scored must be between 0 and 6 only.'
            })

    def save(self, *args, **kwargs):
        # Execute validation before saving
        self.full_clean()

        # Auto-compute boolean markers
        if self.extra_type in ['wide', 'no_ball']:
            self.is_dot_ball = False
        else:
            self.is_dot_ball = (self.runs_scored == 0 and not self.is_wicket)

        self.is_four = (self.runs_scored == 4)
        self.is_six = (self.runs_scored == 6)

        super().save(*args, **kwargs)



class PointsTable(models.Model):
    tournament = models.ForeignKey(Tournament, on_delete=models.CASCADE, related_name='points_table')
    team = models.ForeignKey(CollegeRegistration, on_delete=models.CASCADE)
    matches_played = models.PositiveIntegerField(default=0)
    won = models.PositiveIntegerField(default=0)
    lost = models.PositiveIntegerField(default=0)
    tied = models.PositiveIntegerField(default=0)
    no_result = models.PositiveIntegerField(default=0)
    points = models.PositiveIntegerField(default=0)
    net_run_rate = models.DecimalField(max_digits=6, decimal_places=3, default=0.000)

    class Meta:
        unique_together = ('tournament', 'team')
        ordering = ['-points', '-net_run_rate']

    def __str__(self):
        return f"{self.team.team_name} - Pts: {self.points} (NRR: {self.net_run_rate})"


class HomepageBanner(models.Model):
    title = models.CharField(max_length=255)
    subtitle = models.CharField(max_length=255, blank=True, null=True)
    season_tag = models.CharField(max_length=50, default="Season 2026")
    banner_image = models.ImageField(upload_to='homepage/banners/')
    cta_title = models.CharField(max_length=100, default="Register Now")
    cta_url = models.CharField(max_length=255, default="/register")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


class LiveStreamConfig(models.Model):
    match = models.OneToOneField(Match, on_delete=models.CASCADE, related_name='live_stream')
    youtube_stream_url = models.URLField(help_text="YouTube Live Embed URL (e.g., https://www.youtube.com/embed/...)")
    is_live = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Stream for Match {self.match.id}"


class Announcement(models.Model):
    title = models.CharField(max_length=255)
    details = models.TextField()
    is_pinned = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-is_pinned', '-created_at']

    def __str__(self):
        return self.title




class VideoHighlight(models.Model):
    title=models.CharField(max_length=255)
    match=models.ForeignKey(Match,on_delete=models.SET_NULL,null=True,blank=True,related_name='highlights')
    duration=models.CharField(max_length=30,default="03:45",help_text="e.g. 05.20")
    thumbnail=models.ImageField(upload_to='highlights/thumbnails/')
    youtube_url=models.URLField(help_text="YouTube Video URL (e.g., https://www.youtube.com/watch?v=...)")
    is_featured=models.BooleanField(default=False)
    created_at=models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Match Hightlight"
        ordering = ['-is_featured', '-created_at']

    def __str__(self):
        return self.title


class NewsArticle(models.Model):
    CATEGORY_CHOICES = [
        ('match_report','Match Report'),
        ('announcement','Announcement'),
        ('interview','Interview'),
        ('press_release','Press Release'),
        ('other','Other'),  ]

    title=models.CharField(max_length=255)
    slug=models.SlugField(unique=True,blank=True,null=True)
    category=models.CharField(max_length=50,choices=CATEGORY_CHOICES,default='other')
    summary=models.TextField(help_text="Short summary of the article")
    content=models.TextField(help_text="Full content of the article")
    cover_image=models.ImageField(upload_to='news/cover_images/')
    is_featured = models.BooleanField(default=False,help_text="Set as main big featured news on homepage")
    created_at=models.DateTimeField(auto_now_add=True)  

    class Meta:
        ordering = ['-is_featured', '-created_at']

    def __str__(self):
        return f"{self.title} - {self.get_category_display()}"



class GalleryAlbum(models.Model):
    title = models.CharField(max_length=150)
    cover_image = models.ImageField(upload_to='gallery/covers/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


class GalleryMedia(models.Model):
    album = models.ForeignKey(GalleryAlbum, on_delete=models.CASCADE, related_name='photos', null=True, blank=True)
    title = models.CharField(max_length=150)
    subtitle = models.CharField(max_length=255, blank=True, null=True)  # <-- Single photo ke liye subtitle
    image = models.ImageField(upload_to='gallery/images/', blank=True, null=True)
    match = models.ForeignKey(Match, on_delete=models.SET_NULL, null=True, blank=True, related_name='gallery_media')
    is_featured = models.BooleanField(default=False)  # <-- Single photo ko feature karne ke liye
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title

# class GalleryMedia(models.Model):
#     title=models.CharField(max_length=150)
#     image=models.ImageField(upload_to='gallery/images/',blank=True,null=True)
#     match= models.ForeignKey(Match,on_delete=models.SET_NULL,null=True,blank=True,related_name='gallery_media')
#     created_at=models.DateTimeField(auto_now_add=True)


#     class Meta:
#         ordering=['-created_at']
    
#     def  __str__(self):
#         return self.title


class TournamentFAQ(models.Model):
    question=models.CharField(max_length=255)
    answer=models.TextField()
    order=models.PositiveIntegerField(default=1,help_text="Order of appearance in FAQ section")
    is_active=models.BooleanField(default=True)

    class Meta:
        ordering=['order','id']

    def __str__(self):
        return self.question


class NewsletterSubscription(models.Model):
    email=models.EmailField(unique=True)
    subscribed_at=models.DateTimeField(auto_now_add=True)
    is_active=models.BooleanField(default=True) 

    def __str__(self):
        return self.email

class BroadcastPartner(models.Model):
    name = models.CharField(max_length=150)
    logo = models.ImageField(upload_to='partners/broadcast/', blank=True, null=True)
    partner_type = models.CharField(max_length=100, default="Official Broadcast Partner") # e.g., Streaming Partner, TV Partner
    website_url = models.URLField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    display_order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['display_order', '-created_at']

    def __str__(self):
        return self.name


class AssociateSponsor(models.Model):
    name = models.CharField(max_length=150)
    logo = models.ImageField(upload_to='partners/sponsors/', blank=True, null=True)
    sponsor_tier = models.CharField(max_length=100, default="Associate Sponsor") # e.g., Title Sponsor, Co-Sponsor, Associate
    # country = models.CharField(max_length=100, blank=True, null=True)
    website_url = models.URLField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    display_order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['display_order', '-created_at']

    def __str__(self):
        return self.name



class Testimonial(models.Model):
    name = models.CharField(max_length=150)
    designation = models.CharField(max_length=200, help_text="e.g. College Director, Oakwood University")
    avatar = models.ImageField(upload_to='testimonials/avatars/', blank=True, null=True)
    rating = models.PositiveIntegerField(default=5, help_text="Rating out of 5")
    quote = models.TextField(help_text="Testimonial message/experience")
    is_active = models.BooleanField(default=True)
    display_order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['display_order', '-created_at']

    def __str__(self):
        return f"{self.name} - {self.designation}"
    

class ContactMessage(models.Model):
    name = models.CharField(max_length=150)
    email = models.EmailField()
    subject = models.CharField(max_length=255)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name} - {self.subject}"


class VideoMatchHighlight(models.Model):
    title = models.CharField(max_length=255)
    video_file=models.FileField(upload_to='highlights/videos/')
    thumbnail=models.ImageField(upload_to='highlights/thumbnails/')
    team_name=models.CharField(max_length=100,blank=True,null=True)
    event_name=models.CharField(max_length=100,blank=True,null=True)
    created_at=models.DateTimeField(auto_now_add=True)  

    class Meta: 
        verbose_name = "Video Highlight"
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.title} - {self.event_name} - {self.team_name}"


class VideoGallery(models.Model):
    Choices = [
        ('match_highlight', 'Match Highlight'), 
        ('interview', 'Interview'),
        ('behind_the_scenes', 'Behind the Scenes'),
        ('promo', 'Promotional Video'),
        ('other', 'Other'),
    ]
    title = models.CharField(max_length=200)
    category = models.CharField(max_length=100, blank=True, null=True, choices=Choices)
    subtitle = models.CharField(max_length=250, blank=True, null=True)
    video_file = models.FileField(upload_to='video_gallery/videos/', blank=True, null=True)
    video_url = models.URLField(blank=True, null=True, help_text="YouTube or external video URL")
    duration=models.CharField(max_length=20, blank=True, null=True, help_text="Duration in format HH:MM:SS or MM:SS")   
    cover_image = models.ImageField(upload_to='video_gallery/covers/', blank=True, null=True, help_text="Thumbnail or Album cover image")
    match = models.ForeignKey('Match', on_delete=models.SET_NULL, blank=True, null=True)
    is_featured = models.BooleanField(default=False, help_text="Check if this should appear in featured videos")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title



class RewardAndAward(models.Model):
    AWARD_CATEGORY_CHOICES = [
        ('trophy', 'Trophy & Cup'),
        ('medal', 'Medal'),
        ('cash_prize', 'Cash Prize'),
        ('certificate', 'Certificate'),
        ('other', 'Other'),
    ]

    title = models.CharField(max_length=200, help_text="e.g. Man of the Tournament, Fair Play Award")
    category = models.CharField(max_length=50, choices=AWARD_CATEGORY_CHOICES, default='trophy')
    description = models.TextField(blank=True, null=True, help_text="Details about the award or criteria")
    image = models.ImageField(upload_to='rewards/images/', blank=True, null=True, help_text="Award image or trophy photo")
    prize_amount = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True, help_text="Cash prize amount if applicable")
    tournament = models.ForeignKey('Tournament', on_delete=models.SET_NULL, null=True, blank=True, related_name='awards')
    winner_team = models.ForeignKey('CollegeRegistration', on_delete=models.SET_NULL, null=True, blank=True, related_name='won_awards')
    winner_player = models.ForeignKey('CollegeTeamMember', on_delete=models.SET_NULL, null=True, blank=True, related_name='player_awards')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title