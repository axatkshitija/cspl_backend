from django.db import transaction, IntegrityError
from rest_framework import serializers
from .models import CollegeRegistration, CollegeContactPerson
from django.db import IntegrityError, transaction
from rest_framework import serializers
from .models import CollegeRegistration, CollegeContactPerson
from .utils import (
    send_registration_thank_you_email,
    send_admin_registration_notification,
)


from rest_framework import serializers
from .models import CollegeContactPerson

from rest_framework import serializers


class SendCollegeContactOTPSerializer(serializers.Serializer):
    contact_type = serializers.ChoiceField(choices=[
        'coach',
        'sports_teacher',
        'management_person',
    ])
    target = serializers.CharField()
    type = serializers.ChoiceField(choices=['sms', 'email'])

    def validate(self, attrs):
        verify_type = attrs.get("type")
        target = str(attrs.get("target", "")).strip()

        if verify_type == "sms":
            cleaned = target.replace(" ", "").replace("+", "")

            if cleaned.startswith("91") and len(cleaned) == 12:
                cleaned = cleaned[2:]

            if not cleaned.isdigit() or len(cleaned) != 10:
                raise serializers.ValidationError({
                    "target": "Enter a valid 10 digit phone number."
                })

            attrs["target"] = cleaned
            attrs["e164_target"] = f"+91{cleaned}"

        elif verify_type == "email":
            email = serializers.EmailField().run_validation(target)
            attrs["target"] = email.lower()

        return attrs

class VerifyCollegeContactOTPSerializer(serializers.Serializer):
    contact_type = serializers.ChoiceField(choices=[
        'coach',
        'sports_teacher',
        'management_person',
    ])
    target = serializers.CharField()
    type = serializers.ChoiceField(choices=['sms', 'email'])
    otp = serializers.CharField(max_length=6, min_length=4)

    def validate(self, attrs):
        verify_type = attrs.get("type")
        target = str(attrs.get("target", "")).strip()

        if verify_type == "sms":
            cleaned = target.replace(" ", "").replace("+", "")

            if cleaned.startswith("91") and len(cleaned) == 12:
                cleaned = cleaned[2:]

            if not cleaned.isdigit() or len(cleaned) != 10:
                raise serializers.ValidationError({
                    "target": "Enter a valid 10 digit phone number."
                })

            attrs["target"] = cleaned
            attrs["e164_target"] = f"+91{cleaned}"


        elif verify_type == "email":
            email = serializers.EmailField().run_validation(target)
            attrs["target"] = email.lower()

        otp = str(attrs.get("otp", "")).strip()
        if not otp.isdigit():
            raise serializers.ValidationError({
                "otp": "OTP must contain only digits."
            })

        attrs["otp"] = otp
        return attrs

# class SendCollegeContactOTPSerializer(serializers.Serializer):
#     contact_type = serializers.ChoiceField(choices=[
#         'coach',
#         'sports_teacher',
#         'management_person',
#     ])
#     target = serializers.CharField()
#     type = serializers.ChoiceField(choices=['sms', 'email'])

#     def validate(self, attrs):
#         verify_type = attrs.get("type")
#         target = str(attrs.get("target", "")).strip()

#         if verify_type == "sms":
#             cleaned = target.replace(" ", "").replace("+", "")
#             if cleaned.startswith("91") and len(cleaned) == 12:
#                 cleaned = cleaned[2:]
#             if not cleaned.isdigit() or len(cleaned) != 10:
#                 raise serializers.ValidationError({
#                     "target": "Enter a valid 10 digit phone number."
#                 })
#             attrs["target"] = cleaned

#         elif verify_type == "email":
#             serializers.EmailField().run_validation(target)
#             attrs["target"] = target.lower()

#         return attrs


# class VerifyCollegeContactOTPSerializer(serializers.Serializer):
#     contact_type = serializers.ChoiceField(choices=[
#         'coach',
#         'sports_teacher',
#         'management_person',
#     ])
#     target = serializers.CharField()
#     type = serializers.ChoiceField(choices=['sms', 'email'])
#     otp = serializers.CharField(max_length=6, min_length=4)

#     def validate(self, attrs):
#         verify_type = attrs.get("type")
#         target = str(attrs.get("target", "")).strip()

#         if verify_type == "sms":
#             cleaned = target.replace(" ", "").replace("+", "")
#             if cleaned.startswith("91") and len(cleaned) == 12:
#                 cleaned = cleaned[2:]
#             if not cleaned.isdigit() or len(cleaned) != 10:
#                 raise serializers.ValidationError({
#                     "target": "Enter a valid 10 digit phone number."
#                 })
#             attrs["target"] = cleaned

#         elif verify_type == "email":
#             serializers.EmailField().run_validation(target)
#             attrs["target"] = target.lower()

#         return attrs


        
class CollegeContactPersonInputSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=255)
    phone = serializers.CharField(max_length=20)
    email = serializers.EmailField()

class CollegeBasicInfoCreateSerializer(serializers.ModelSerializer):
    coach_details = CollegeContactPersonInputSerializer(write_only=True)
    sports_teacher_details = CollegeContactPersonInputSerializer(write_only=True)
    management_person_details = CollegeContactPersonInputSerializer(write_only=True)

    # password = serializers.CharField(write_only=True, min_length=6)
    # confirm_password = serializers.CharField(write_only=True, min_length=6)

    class Meta:
        model = CollegeRegistration
        fields = [
            'id',
            'full_name',
            'ngo_or_trust',
            'registration_number',
            'team_name',
            'address_line_1',
            'address_line_2',
            'city',
            'state',
            'country',
            'pin_code',
            'filled_by',
            'coach_details',
            'sports_teacher_details',
            'management_person_details',
            # 'password',
            # 'confirm_password',
            'created_at',
        ]
        read_only_fields = ['id', 'created_at']

    def validate_registration_number(self, value):
        value = value.strip()
        if CollegeRegistration.objects.filter(registration_number__iexact=value).exists():
            raise serializers.ValidationError("Registration number already exists.")
        return value
    def validate(self, attrs):
        errors = {}

        full_name = attrs.get("full_name", "").strip()
        pin_code = attrs.get("pin_code", "").strip()

        if full_name and pin_code:
            if CollegeRegistration.objects.filter(
                full_name__iexact=full_name,
                pin_code=pin_code
            ).exists():
                errors["full_name"] = ["A college with this name and pin code already exists."]
                errors["pin_code"] = ["A college with this name and pin code already exists."]

        if errors:
            raise serializers.ValidationError(errors)

        return attrs
    # def validate(self, attrs):
    #     if attrs['password'] != attrs['confirm_password']:
    #         raise serializers.ValidationError({
    #             "confirm_password": ["Password and confirm password do not match."]
    #         })
        # return attrs
    @transaction.atomic
    def create(self, validated_data):
        coach_data = validated_data.pop('coach_details')
        sports_teacher_data = validated_data.pop('sports_teacher_details')
        management_person_data = validated_data.pop('management_person_details')
        # password = validated_data.pop('password')
        # validated_data.pop('confirm_password')
    
        try:
            college = CollegeRegistration(**validated_data)
            college.status = 'submitted'
            # college.set_password(password)
            college.save()
    
            coach = CollegeContactPerson.objects.create(
                college=college,
                contact_type='coach',
                **coach_data
            )
    
            sports_teacher = CollegeContactPerson.objects.create(
                college=college,
                contact_type='sports_teacher',
                **sports_teacher_data
            )
    
            management_person = CollegeContactPerson.objects.create(
                college=college,
                contact_type='management_person',
                **management_person_data
            )
    
            if coach.email:
                send_registration_thank_you_email(
                    user_email=coach.email,
                    user_name=coach.name,
                    college=college
                )
    
            if management_person.email:
                send_registration_thank_you_email(
                    user_email=management_person.email,
                    user_name=management_person.name,
                    college=college
                )
    
            send_admin_registration_notification(
                college=college,
                coach=coach,
                sports_teacher=sports_teacher,
                management_person=management_person
            )
    
            return college
    
        except IntegrityError as e:
            print("INTEGRITY ERROR =>", str(e))
            raise serializers.ValidationError({
                "non_field_errors": [str(e)]
            })
    # @transaction.atomic
    # def create(self, validated_data):
    #     coach_data = validated_data.pop('coach_details')
    #     sports_teacher_data = validated_data.pop('sports_teacher_details')
    #     management_person_data = validated_data.pop('management_person_details')
    #     password = validated_data.pop('password')
    #     validated_data.pop('confirm_password')

    #     try:
    #         college = CollegeRegistration(**validated_data)
    #         college.status = 'submitted'

    #         college.set_password(password)
    #         college.save()

    #         CollegeContactPerson.objects.create(
    #             college=college,
    #             contact_type='coach',
    #             **coach_data
    #         )
    #         CollegeContactPerson.objects.create(
    #             college=college,
    #             contact_type='sports_teacher',
    #             **sports_teacher_data
    #         )
    #         CollegeContactPerson.objects.create(
    #             college=college,
    #             contact_type='management_person',
    #             **management_person_data
    #         )

    #         return college

    #     except IntegrityError:
    #         raise serializers.ValidationError({
    #             "registration_number": ["Registration number already exists."]
    #         })
        

class SendLoginOTPSerializer(serializers.Serializer):
    generated_registration_no = serializers.CharField()
    email = serializers.EmailField()

    def validate_generated_registration_no(self, value):
        value = value.strip()
        if not value:
            raise serializers.ValidationError("Generated registration number is required.")
        return value

    def validate_email(self, value):
        value = value.strip().lower()
        if not value:
            raise serializers.ValidationError("Email is required.")
        return value


class VerifyLoginOTPSerializer(serializers.Serializer):
    generated_registration_no = serializers.CharField()
    email = serializers.EmailField()
    otp = serializers.CharField(max_length=6, min_length=4)

    def validate_generated_registration_no(self, value):
        value = value.strip()
        if not value:
            raise serializers.ValidationError("Generated registration number is required.")
        return value

    def validate_email(self, value):
        value = value.strip().lower()
        if not value:
            raise serializers.ValidationError("Email is required.")
        return value

    def validate_otp(self, value):
        value = value.strip()
        if not value.isdigit():
            raise serializers.ValidationError("OTP must contain only digits.")
        return value

        
# class SendOTPSerializer(serializers.Serializer):
#     registration_number = serializers.CharField(required=True, allow_blank=False)
#     password = serializers.CharField(required=True, allow_blank=False)
#     mobile_no = serializers.CharField(required=True, allow_blank=False)

#     def validate_mobile_no(self, value):
#         value = value.strip()
#         if not value.isdigit():
#             raise serializers.ValidationError("Mobile number must contain only digits.")
#         if len(value) != 10:
#             raise serializers.ValidationError("Mobile number must be 10 digits.")
#         return value

#     # contact_type = serializers.ChoiceField(
#     #     choices=['coach', 'sports_teacher', 'management_person']
#     # )
# class VerifyOTPSerializer(serializers.Serializer):
#     mobile_no = serializers.CharField(required=True, max_length=15)
#     otp = serializers.CharField(required=True, min_length=6, max_length=6)

#     def validate_mobile_no(self, value):
#         value = value.strip()
#         if not value.isdigit():
#             raise serializers.ValidationError("Mobile number must contain only digits.")
#         return value

#     def validate_otp(self, value):
#         value = value.strip()
#         if not value.isdigit():
#             raise serializers.ValidationError("OTP must contain only digits.")
#         return value

# class SendOTPSerializer(serializers.Serializer):
#     mobile_number = serializers.CharField(max_length=15)

#     def validate_mobile_number(self, value):
#         value = value.strip()
#         if not value.isdigit():
#             raise serializers.ValidationError("Mobile number must contain only digits.")
#         if len(value) != 10:
#             raise serializers.ValidationError("Mobile number must be 10 digits.")
#         return value


# class VerifyOTPSerializer(serializers.Serializer):
#     mobile_number = serializers.CharField(max_length=15)
#     otp = serializers.CharField(max_length=6)

#     def validate_mobile_number(self, value):
#         value = value.strip()
#         if not value.isdigit():
#             raise serializers.ValidationError("Mobile number must contain only digits.")
#         return value

#     def validate_otp(self, value):
#         value = value.strip()
#         if not value.isdigit() or len(value) != 6:
#             raise serializers.ValidationError("OTP must be 6 digits.")
#         return value



class InstitutionInformationSerializer(serializers.ModelSerializer):
    future_sports = serializers.ListField(
        child=serializers.ChoiceField(choices=[c[0] for c in CollegeRegistration.SPORT_CHOICES]),
        allow_empty=True,
        required=False
    )

    class Meta:
        model = CollegeRegistration
        fields = [
            'total_students',
            'teaching_staff',
            'non_teaching_staff',
            'current_sport',
            'future_sports',
            'has_ground',
            'ground_dimension_sq_m',
        ]

    def validate(self, attrs):
        has_ground = attrs.get('has_ground', getattr(self.instance, 'has_ground', False))
        ground_dimension = attrs.get('ground_dimension_sq_m', getattr(self.instance, 'ground_dimension_sq_m', None))

        if has_ground and not ground_dimension:
            raise serializers.ValidationError({
                "ground_dimension_sq_m": "Ground dimension is required when ground is available."
            })

        if not has_ground:
            attrs['ground_dimension_sq_m'] = None

        return attrs
    

# # serializers.py
# from rest_framework import serializers
# from .models import CollegeTeamMember


# class CollegeTeamMemberSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = CollegeTeamMember
#         fields = [
#             'id',
#             'role',
#             'name',
#             'age',
#             'dob',
#             'mobile_no',
#             'alternate_no',
#             'relation',
#             'email',
#             'current_address',
#             'permanent_address',
#             'photo',
#             'no_photo',
#             'created_at',
#         ]
#         read_only_fields = ['id', 'created_at']

#     def validate_mobile_no(self, value):
#         value = value.strip()
#         if not value.isdigit():
#             raise serializers.ValidationError("Mobile number must contain only digits.")
#         if len(value) != 10:
#             raise serializers.ValidationError("Mobile number must be 10 digits.")
#         return value

#     def validate_alternate_no(self, value):
#         if value:
#             value = value.strip()
#             if not value.isdigit():
#                 raise serializers.ValidationError("Alternate number must contain only digits.")
#             if len(value) != 10:
#                 raise serializers.ValidationError("Alternate number must be 10 digits.")
#         return value

#     def validate(self, attrs):
#         no_photo = attrs.get("no_photo", False)
#         photo = attrs.get("photo")

#         if not no_photo and not photo:
#             raise serializers.ValidationError({
#                 "photo": "Photo is required when 'No Photo' is not selected."
#             })

#         if no_photo:
#             attrs["photo"] = None

#         return attrs
    
from rest_framework import serializers
from .models import CollegeTeamMember

class SiblingDetailSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=255)
    age = serializers.IntegerField(min_value=0)


class EducationDetailSerializer(serializers.Serializer):
    degree_name = serializers.ChoiceField(choices=[
        'HSC',
        'SSC',
        'Graduation',
        'Post Graduation',
        'Doctor',
        'PHD',
    ])
    studying_year = serializers.CharField(max_length=50)


class CollegeTeamMemberSerializer(serializers.ModelSerializer):
    sibling_details = SiblingDetailSerializer(many=True, required=False)
    education_details = EducationDetailSerializer(many=True, required=False)
    member_code = serializers.CharField(read_only=True)

    class Meta:
        model = CollegeTeamMember
        fields = [
            'id',
            'member_code',
            'role',
            'name',
            'age',
            'dob',
            'mobile_no',
            'alternate_no',
            'relation',
            'email',
            'current_address',
            'permanent_address',
            'photo',
            'no_photo',
            'father_name',
            'mother_name',
            'sibling_details',
            'education_details',
            'created_at',
        ]
        read_only_fields = ['id', 'member_code', 'created_at']

    def validate_mobile_no(self, value):
        value = value.strip()
        if not value.isdigit():
            raise serializers.ValidationError("Mobile number must contain only digits.")
        if len(value) != 10:
            raise serializers.ValidationError("Mobile number must be 10 digits.")
        return value

    def validate_alternate_no(self, value):
        if value:
            value = value.strip()
            if not value.isdigit():
                raise serializers.ValidationError("Alternate number must contain only digits.")
            if len(value) != 10:
                raise serializers.ValidationError("Alternate number must be 10 digits.")
        return value

    def validate(self, attrs):
        no_photo = attrs.get("no_photo", False)
        photo = attrs.get("photo")

        if not no_photo and not photo:
            raise serializers.ValidationError({
                "photo": "Photo is required when 'No Photo' is not selected."
            })

        if no_photo:
            attrs["photo"] = None

        return attrs
# class CollegeTeamMemberSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = CollegeTeamMember
#         fields = [
#             'id',
#             'role',
#             'name',
#             'age',
#             'dob',
#             'mobile_no',
#             'alternate_no',
#             'relation',
#             'email',
#             'current_address',
#             'permanent_address',
#             'photo',
#             'no_photo',
#             'created_at',
#         ]
#         read_only_fields = ['id', 'created_at']

#     def validate_mobile_no(self, value):
#         value = value.strip()
#         if not value.isdigit():
#             raise serializers.ValidationError("Mobile number must contain only digits.")
#         if len(value) != 10:
#             raise serializers.ValidationError("Mobile number must be 10 digits.")
#         return value

#     def validate_alternate_no(self, value):
#         if value:
#             value = value.strip()
#             if not value.isdigit():
#                 raise serializers.ValidationError("Alternate number must contain only digits.")
#             if len(value) != 10:
#                 raise serializers.ValidationError("Alternate number must be 10 digits.")
#         return value

#     def validate(self, attrs):
#         no_photo = attrs.get("no_photo", False)
#         photo = attrs.get("photo")

#         if not no_photo and not photo:
#             raise serializers.ValidationError({
#                 "photo": "Photo is required when 'No Photo' is not selected."
#             })

#         if no_photo:
#             attrs["photo"] = None

#         return attrs

from rest_framework import serializers
from .models import CollegeDocument


class CollegeDocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = CollegeDocument
        fields = [
            'registration_certificate',
            'pan_card',
            'additional_document',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['created_at', 'updated_at']

    def validate_file(self, file, field_name):
        allowed_extensions = ['pdf', 'jpg', 'jpeg', 'png']
        max_size = 5 * 1024 * 1024

        ext = file.name.split('.')[-1].lower()

        if ext not in allowed_extensions:
            raise serializers.ValidationError(
                f"{field_name} must be PDF, JPG, JPEG, or PNG."
            )

        if file.size > max_size:
            raise serializers.ValidationError(
                f"{field_name} size must not exceed 5 MB."
            )

        return file

    def validate_registration_certificate(self, value):
        return self.validate_file(value, "Registration certificate")

    def validate_pan_card(self, value):
        return self.validate_file(value, "PAN card")

    def validate_additional_document(self, value):
        if value:
            return self.validate_file(value, "Additional document")
        return value
    



from rest_framework import serializers
from .models import SponsorRegistration


class SponsorRegistrationSerializer(serializers.ModelSerializer):
    class Meta:
        model = SponsorRegistration
        fields = "__all__"
        read_only_fields = ["id", "created_at"]

    def validate_phone_number(self, value):
        value = value.strip()
        if not value.isdigit():
            raise serializers.ValidationError("Phone number must contain only digits.")
        if len(value) < 10 or len(value) > 15:
            raise serializers.ValidationError("Phone number must be between 10 and 15 digits.")
        return value

    def validate_preferred_engagement_zones(self, value):
        allowed = [
            "On-Ground Branding",
            "Digital Branding",
            "Direct Engagement",
        ]
        if not isinstance(value, list):
            raise serializers.ValidationError("Preferred engagement zones must be a list.")
        invalid = [item for item in value if item not in allowed]
        if invalid:
            raise serializers.ValidationError(f"Invalid engagement zones: {invalid}")
        return value

    def validate_target_demographic(self, value):
        allowed = [
            "Students aged 18-24",
            "Faculty",
            "Sports Enthusiasts",
            "Others",
        ]
        if not isinstance(value, list):
            raise serializers.ValidationError("Target demographic must be a list.")
        invalid = [item for item in value if item not in allowed]
        if invalid:
            raise serializers.ValidationError(f"Invalid target demographic values: {invalid}")
        return value

    def validate_company_logo(self, value):
        allowed_extensions = ["png", "ai"]
        max_size = 5 * 1024 * 1024

        ext = value.name.split(".")[-1].lower()
        if ext not in allowed_extensions:
            raise serializers.ValidationError("Company logo must be PNG or AI file.")
        if value.size > max_size:
            raise serializers.ValidationError("Company logo size must not exceed 5 MB.")
        return value

    def validate_gst_details(self, value):
        allowed_extensions = ["pdf", "jpg", "jpeg", "png"]
        max_size = 5 * 1024 * 1024

        ext = value.name.split(".")[-1].lower()
        if ext not in allowed_extensions:
            raise serializers.ValidationError("GST details must be PDF, JPG, JPEG, or PNG.")
        if value.size > max_size:
            raise serializers.ValidationError("GST details size must not exceed 5 MB.")
        return value

    def validate_agreed_to_terms(self, value):
        if value is not True:
            raise serializers.ValidationError("You must agree to the Terms and Conditions.")
        return value
    

from rest_framework import serializers
from .models import VendorRegistration, VendorContactOTP

class VendorRegistrationSerializer(serializers.ModelSerializer):
    entity_type = serializers.CharField()
    core_category_of_service = serializers.CharField()

    class Meta:
        model = VendorRegistration
        fields = [
            "id",
            "legal_business_name",
            "trade_name",
            "entity_type",
            "other_entity_type",
            "registered_office_address",
            "cin",
            "core_category_of_service",
            "primary_contact_person_name",
            "designation",
            "mobile_number",
            "email",
            "escalation_contact",
            "pan",
            "gstin",
            "msme_registration_number",
            "bank_name",
            "account_holder_name",
            "account_number",
            "ifsc_code",
            "years_of_active_operation",
            "handled_large_scale_sports_tournaments",
            "prominent_events_or_projects",
            "pan_card_copy",
            "gst_registration_certificate",
            "cancelled_cheque_or_passbook",
            "company_profile_or_pitch_deck",
            "declaration_name",
            "declaration_designation",
            "signature_and_company_seal",
            "declaration_date",
            "email_verified",
            "phone_verified",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "email_verified",
            "phone_verified",
            "created_at",
            "updated_at",
        ]

    def _map_choice_value(self, value, choices, field_label):
        value = str(value).strip()
        if not value:
            raise serializers.ValidationError(f"{field_label} is required.")

        choice_dict = dict(choices)

        if value in choice_dict:
            return value

        reverse_choice_dict = {
            str(label).strip().lower(): key
            for key, label in choices
        }

        mapped_value = reverse_choice_dict.get(value.lower())
        if mapped_value:
            return mapped_value

        raise serializers.ValidationError(f"Invalid {field_label.lower()} selected.")

    def validate_legal_business_name(self, value):
        value = str(value).strip()
        if not value:
            raise serializers.ValidationError("Legal business name is required.")
        return value

    def validate_trade_name(self, value):
        return str(value).strip() if value else ""

    def validate_entity_type(self, value):
        return self._map_choice_value(
            value,
            VendorRegistration.ENTITY_TYPE_CHOICES,
            "Entity type"
        )

    def validate_other_entity_type(self, value):
        return str(value).strip() if value else ""

    def validate_registered_office_address(self, value):
        value = str(value).strip()
        if not value:
            raise serializers.ValidationError("Registered office address is required.")
        return value

    def validate_cin(self, value):
        return str(value).strip().upper() if value else ""

    def validate_core_category_of_service(self, value):
        return self._map_choice_value(
            value,
            VendorRegistration.SERVICE_CATEGORY_CHOICES,
            "Core category of service"
        )

    def validate_primary_contact_person_name(self, value):
        value = str(value).strip()
        if not value:
            raise serializers.ValidationError("Primary contact person name is required.")
        return value

    def validate_designation(self, value):
        value = str(value).strip()
        if not value:
            raise serializers.ValidationError("Designation is required.")
        return value

    def validate_mobile_number(self, value):
        value = str(value).strip().replace(" ", "").replace("-", "")
        if value.startswith("+91"):
            value = value[3:]
        if not value.isdigit():
            raise serializers.ValidationError("Mobile number must contain only digits.")
        if len(value) != 10:
            raise serializers.ValidationError("Mobile number must be 10 digits.")
        return value

    def validate_email(self, value):
        value = str(value).strip().lower()
        if not value:
            raise serializers.ValidationError("Email is required.")
        return value

    def validate_escalation_contact(self, value):
        return str(value).strip() if value else ""

    def validate_pan(self, value):
        value = str(value).strip().upper()
        if not value:
            raise serializers.ValidationError("PAN is required.")
        if len(value) != 10:
            raise serializers.ValidationError("PAN must be 10 characters.")
        return value

    def validate_gstin(self, value):
        value = str(value).strip().upper() if value else ""
        if value and len(value) != 15:
            raise serializers.ValidationError("GSTIN must be 15 characters.")
        return value

    def validate_msme_registration_number(self, value):
        return str(value).strip().upper() if value else ""

    def validate_bank_name(self, value):
        value = str(value).strip()
        if not value:
            raise serializers.ValidationError("Bank name is required.")
        return value

    def validate_account_holder_name(self, value):
        value = str(value).strip()
        if not value:
            raise serializers.ValidationError("Account holder name is required.")
        return value

    def validate_account_number(self, value):
        value = str(value).strip().replace(" ", "")
        if not value:
            raise serializers.ValidationError("Account number is required.")
        return value

    def validate_ifsc_code(self, value):
        value = str(value).strip().upper()
        if not value:
            raise serializers.ValidationError("IFSC code is required.")
        if len(value) != 11:
            raise serializers.ValidationError("IFSC code must be 11 characters.")
        return value

    def validate_years_of_active_operation(self, value):
        if value is None:
            raise serializers.ValidationError("Years of active operation is required.")
        if value < 0:
            raise serializers.ValidationError("Years of active operation cannot be negative.")
        return value

    def validate_prominent_events_or_projects(self, value):
        return str(value).strip() if value else ""

    def validate_declaration_name(self, value):
        value = str(value).strip()
        if not value:
            raise serializers.ValidationError("Declaration name is required.")
        return value

    def validate_declaration_designation(self, value):
        value = str(value).strip()
        if not value:
            raise serializers.ValidationError("Declaration designation is required.")
        return value

    def validate(self, attrs):
        entity_type = attrs.get("entity_type")
        other_entity_type = str(attrs.get("other_entity_type", "")).strip()

        if entity_type == "other" and not other_entity_type:
            raise serializers.ValidationError(
                {"other_entity_type": "Please specify other entity type."}
            )

        email = attrs.get("email")
        mobile_number = attrs.get("mobile_number")
        pan = attrs.get("pan")

        instance = getattr(self, "instance", None)

        email_qs = VendorRegistration.objects.filter(email__iexact=email)
        mobile_qs = VendorRegistration.objects.filter(mobile_number=mobile_number)
        pan_qs = VendorRegistration.objects.filter(pan__iexact=pan)

        if instance:
            email_qs = email_qs.exclude(pk=instance.pk)
            mobile_qs = mobile_qs.exclude(pk=instance.pk)
            pan_qs = pan_qs.exclude(pk=instance.pk)

        if email_qs.exists():
            raise serializers.ValidationError({"email": "This email is already registered."})

        if mobile_qs.exists():
            raise serializers.ValidationError({"mobile_number": "This mobile number is already registered."})

        if pan_qs.exists():
            raise serializers.ValidationError({"pan": "This PAN is already registered."})

        email_verified = VendorContactOTP.objects.filter(
            contact_type="primary",
            otp_type="email",
            target__iexact=email,
            is_verified=True
        ).exists()

        phone_verified = VendorContactOTP.objects.filter(
            contact_type="primary",
            otp_type="sms",
            target=mobile_number,
            is_verified=True
        ).exists()

        if not email_verified:
            raise serializers.ValidationError({"email": "Please verify email before submitting the form."})

        if not phone_verified:
            raise serializers.ValidationError({"mobile_number": "Please verify mobile number before submitting the form."})

        attrs["email_verified"] = True
        attrs["phone_verified"] = True

        return attrs

# from rest_framework import serializers
# from .models import VendorRegistration, VendorContactOTP


# class VendorRegistrationSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = VendorRegistration
#         fields = [
#             "id",

#             # Company Overview
#             "legal_business_name",
#             "trade_name",
#             "entity_type",
#             "other_entity_type",
#             "registered_office_address",
#             "cin",

#             # Core Category of Service/Supply
#             "core_category_of_service",

#             # Contact Information
#             "primary_contact_person_name",
#             "designation",
#             "mobile_number",
#             "email",
#             "escalation_contact",

#             # Statutory & Financial Details
#             "pan",
#             "gstin",
#             "msme_registration_number",
#             "bank_name",
#             "account_holder_name",
#             "account_number",
#             "ifsc_code",

#             # Experience & Past Portfolio
#             "years_of_active_operation",
#             "handled_large_scale_sports_tournaments",
#             "prominent_events_or_projects",

#             # Documents to Attach
#             "pan_card_copy",
#             "gst_registration_certificate",
#             "cancelled_cheque_or_passbook",
#             "company_profile_or_pitch_deck",

#             # Declaration
#             "declaration_name",
#             "declaration_designation",
#             "signature_and_company_seal",
#             "declaration_date",

#             # Verification
#             "email_verified",
#             "phone_verified",

#             "created_at",
#             "updated_at",
#         ]
#         read_only_fields = [
#             "id",
#             "email_verified",
#             "phone_verified",
#             "created_at",
#             "updated_at",
#         ]

#     def validate_legal_business_name(self, value):
#         value = str(value).strip()
#         if not value:
#             raise serializers.ValidationError("Legal business name is required.")
#         return value

#     def validate_trade_name(self, value):
#         return str(value).strip() if value else ""

#     def validate_entity_type(self, value):
#         value = str(value).strip()
#         if not value:
#             raise serializers.ValidationError("Type of entity is required.")
#         return value

#     def validate_other_entity_type(self, value):
#         return str(value).strip() if value else ""

#     def validate_registered_office_address(self, value):
#         value = str(value).strip()
#         if not value:
#             raise serializers.ValidationError("Registered office address is required.")
#         return value

#     def validate_cin(self, value):
#         return str(value).strip().upper() if value else ""

#     def validate_core_category_of_service(self, value):
#         value = str(value).strip()
#         if not value:
#             raise serializers.ValidationError("Core category of service is required.")
#         return value

#     def validate_primary_contact_person_name(self, value):
#         value = str(value).strip()
#         if not value:
#             raise serializers.ValidationError("Primary contact person name is required.")
#         return value

#     def validate_designation(self, value):
#         value = str(value).strip()
#         if not value:
#             raise serializers.ValidationError("Designation is required.")
#         return value

#     def validate_mobile_number(self, value):
#         value = str(value).strip().replace(" ", "").replace("-", "")
#         if value.startswith("+91"):
#             value = value[3:]
#         if not value.isdigit():
#             raise serializers.ValidationError("Mobile number must contain only digits.")
#         if len(value) != 10:
#             raise serializers.ValidationError("Mobile number must be 10 digits.")
#         return value

#     def validate_email(self, value):
#         value = str(value).strip().lower()
#         if not value:
#             raise serializers.ValidationError("Email is required.")
#         return value

#     def validate_escalation_contact(self, value):
#         return str(value).strip() if value else ""

#     def validate_pan(self, value):
#         value = str(value).strip().upper()
#         if not value:
#             raise serializers.ValidationError("PAN is required.")
#         if len(value) != 10:
#             raise serializers.ValidationError("PAN must be 10 characters.")
#         return value

#     def validate_gstin(self, value):
#         value = str(value).strip().upper() if value else ""
#         if value and len(value) != 15:
#             raise serializers.ValidationError("GSTIN must be 15 characters.")
#         return value

#     def validate_msme_registration_number(self, value):
#         return str(value).strip().upper() if value else ""

#     def validate_bank_name(self, value):
#         value = str(value).strip()
#         if not value:
#             raise serializers.ValidationError("Bank name is required.")
#         return value

#     def validate_account_holder_name(self, value):
#         value = str(value).strip()
#         if not value:
#             raise serializers.ValidationError("Account holder name is required.")
#         return value

#     def validate_account_number(self, value):
#         value = str(value).strip().replace(" ", "")
#         if not value:
#             raise serializers.ValidationError("Account number is required.")
#         return value

#     def validate_ifsc_code(self, value):
#         value = str(value).strip().upper()
#         if not value:
#             raise serializers.ValidationError("IFSC code is required.")
#         if len(value) != 11:
#             raise serializers.ValidationError("IFSC code must be 11 characters.")
#         return value

#     def validate_years_of_active_operation(self, value):
#         if value is None:
#             raise serializers.ValidationError("Years of active operation is required.")
#         if value < 0:
#             raise serializers.ValidationError("Years of active operation cannot be negative.")
#         return value

#     def validate_prominent_events_or_projects(self, value):
#         return str(value).strip() if value else ""

#     def validate_declaration_name(self, value):
#         value = str(value).strip()
#         if not value:
#             raise serializers.ValidationError("Declaration name is required.")
#         return value

#     def validate_declaration_designation(self, value):
#         value = str(value).strip()
#         if not value:
#             raise serializers.ValidationError("Declaration designation is required.")
#         return value

#     def validate(self, attrs):
#         entity_type = attrs.get("entity_type")
#         other_entity_type = str(attrs.get("other_entity_type", "")).strip()

#         if entity_type == "other" and not other_entity_type:
#             raise serializers.ValidationError(
#                 {"other_entity_type": "Please specify other entity type."}
#             )

#         email = attrs.get("email")
#         mobile_number = attrs.get("mobile_number")
#         pan = attrs.get("pan")

#         instance = getattr(self, "instance", None)

#         email_qs = VendorRegistration.objects.filter(email__iexact=email)
#         mobile_qs = VendorRegistration.objects.filter(mobile_number=mobile_number)
#         pan_qs = VendorRegistration.objects.filter(pan__iexact=pan)

#         if instance:
#             email_qs = email_qs.exclude(pk=instance.pk)
#             mobile_qs = mobile_qs.exclude(pk=instance.pk)
#             pan_qs = pan_qs.exclude(pk=instance.pk)

#         if email_qs.exists():
#             raise serializers.ValidationError({"email": "This email is already registered."})

#         if mobile_qs.exists():
#             raise serializers.ValidationError({"mobile_number": "This mobile number is already registered."})

#         if pan_qs.exists():
#             raise serializers.ValidationError({"pan": "This PAN is already registered."})

#         email_verified = VendorContactOTP.objects.filter(
#             contact_type="primary",
#             otp_type="email",
#             target__iexact=email,
#             is_verified=True
#         ).exists()

#         phone_verified = VendorContactOTP.objects.filter(
#             contact_type="primary",
#             otp_type="sms",
#             target=mobile_number,
#             is_verified=True
#         ).exists()

#         if not email_verified:
#             raise serializers.ValidationError({"email": "Please verify email before submitting the form."})

#         if not phone_verified:
#             raise serializers.ValidationError({"mobile_number": "Please verify mobile number before submitting the form."})

#         attrs["email_verified"] = True
#         attrs["phone_verified"] = True

#         return attrs

class SendVendorContactOTPSerializer(serializers.Serializer):
    CONTACT_TYPE_CHOICES = [
        ("primary", "Primary"),
        ("escalation", "Escalation"),
    ]

    VERIFY_TYPE_CHOICES = [
        ("sms", "SMS"),
        ("email", "Email"),
    ]

    contact_type = serializers.ChoiceField(choices=CONTACT_TYPE_CHOICES)
    target = serializers.CharField()
    type = serializers.ChoiceField(choices=VERIFY_TYPE_CHOICES)

    def validate_contact_type(self, value):
        return str(value).strip().lower()

    def validate_type(self, value):
        return str(value).strip().lower()

    def validate_target(self, value):
        value = str(value).strip()
        verify_type = str(self.initial_data.get("type", "")).strip().lower()

        if verify_type == "email":
            value = value.lower()
            if "@" not in value:
                raise serializers.ValidationError("Enter a valid email address.")

            existing_vendor = VendorRegistration.objects.filter(email__iexact=value).exists()
            if existing_vendor:
                raise serializers.ValidationError("This email is already registered.")
            return value

        if verify_type == "sms":
            value = value.replace(" ", "").replace("-", "")
            if value.startswith("+91"):
                value = value[3:]
            if not value.isdigit():
                raise serializers.ValidationError("Mobile number must contain only digits.")
            if len(value) != 10:
                raise serializers.ValidationError("Mobile number must be 10 digits.")

            existing_vendor = VendorRegistration.objects.filter(mobile_number=value).exists()
            if existing_vendor:
                raise serializers.ValidationError("This mobile number is already registered.")
            return value

        return value


class VerifyVendorContactOTPSerializer(serializers.Serializer):
    CONTACT_TYPE_CHOICES = [
        ("primary", "Primary"),
        ("escalation", "Escalation"),
    ]

    VERIFY_TYPE_CHOICES = [
        ("sms", "SMS"),
        ("email", "Email"),
    ]

    contact_type = serializers.ChoiceField(choices=CONTACT_TYPE_CHOICES)
    target = serializers.CharField()
    type = serializers.ChoiceField(choices=VERIFY_TYPE_CHOICES)
    otp = serializers.CharField(max_length=10)

    def validate_contact_type(self, value):
        return str(value).strip().lower()

    def validate_type(self, value):
        return str(value).strip().lower()

    def validate_target(self, value):
        value = str(value).strip()
        verify_type = str(self.initial_data.get("type", "")).strip().lower()

        if verify_type == "email":
            value = value.lower()
            if "@" not in value:
                raise serializers.ValidationError("Enter a valid email address.")
            return value

        if verify_type == "sms":
            value = value.replace(" ", "").replace("-", "")
            if value.startswith("+91"):
                value = value[3:]
            if not value.isdigit():
                raise serializers.ValidationError("Mobile number must contain only digits.")
            if len(value) != 10:
                raise serializers.ValidationError("Mobile number must be 10 digits.")
            return value

        return value

    def validate_otp(self, value):
        value = str(value).strip()
        if not value.isdigit():
            raise serializers.ValidationError("OTP must contain only digits.")
        if len(value) < 4 or len(value) > 10:
            raise serializers.ValidationError("OTP length is invalid.")
        return value

    def validate(self, attrs):
        contact_type = attrs.get("contact_type")
        target = attrs.get("target")
        verify_type = attrs.get("type")

        otp_exists = VendorContactOTP.objects.filter(
            contact_type=contact_type,
            otp_type=verify_type,
            target__iexact=target if verify_type == "email" else target,
            is_used=False
        ).exists()

        if not otp_exists:
            raise serializers.ValidationError({"otp": "No active OTP request found for this target."})

        return attrs


# ==============================================================================
# TOURNAMENT & LIVE SCORING SERIALIZERS
# ==============================================================================
from .models import (
    Tournament, Venue, Match, MatchPlayingXI, Innings,
    BallByBall, PointsTable, HomepageBanner, LiveStreamConfig, Announcement
)


class VenueSerializer(serializers.ModelSerializer):
    class Meta:
        model = Venue
        fields = '__all__'


class TournamentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tournament
        fields = '__all__'


class MatchPlayingXISerializer(serializers.ModelSerializer):
    player_name = serializers.CharField(source='player.name', read_only=True)
    player_code = serializers.CharField(source='player.member_code', read_only=True)

    class Meta:
        model = MatchPlayingXI
        fields = [
            'id', 'player', 'player_name', 'player_code',
            'is_captain', 'is_wicketkeeper', 'is_substitute'
        ]


class MatchSetupSerializer(serializers.ModelSerializer):
    squad_team_a = MatchPlayingXISerializer(many=True, write_only=True)
    squad_team_b = MatchPlayingXISerializer(many=True, write_only=True)

    class Meta:
        model = Match
        fields = [
            'id', 'tournament', 'team_a', 'team_b', 'venue',
            'match_datetime', 'format', 'total_overs',
            'squad_team_a', 'squad_team_b'
        ]

    @transaction.atomic
    def create(self, validated_data):
        squad_a_data = validated_data.pop('squad_team_a')
        squad_b_data = validated_data.pop('squad_team_b')

        match = Match.objects.create(**validated_data)

        # Create Squad for Team A
        for item in squad_a_data:
            MatchPlayingXI.objects.create(match=match, team=match.team_a, **item)

        # Create Squad for Team B
        for item in squad_b_data:
            MatchPlayingXI.objects.create(match=match, team=match.team_b, **item)

        return match


class TossRecordSerializer(serializers.Serializer):
    toss_winner = serializers.PrimaryKeyRelatedField(queryset=CollegeRegistration.objects.all())
    toss_decision = serializers.ChoiceField(choices=['bat', 'bowl'])


class StartInningsSerializer(serializers.Serializer):
    innings_number = serializers.ChoiceField(choices=[1, 2])
    batting_team = serializers.PrimaryKeyRelatedField(queryset=CollegeRegistration.objects.all())
    bowling_team = serializers.PrimaryKeyRelatedField(queryset=CollegeRegistration.objects.all())
    striker = serializers.PrimaryKeyRelatedField(queryset=CollegeTeamMember.objects.all())
    non_striker = serializers.PrimaryKeyRelatedField(queryset=CollegeTeamMember.objects.all())
    bowler = serializers.PrimaryKeyRelatedField(queryset=CollegeTeamMember.objects.all())


class RecordBallSerializer(serializers.Serializer):
    striker = serializers.PrimaryKeyRelatedField(queryset=CollegeTeamMember.objects.all())
    non_striker = serializers.PrimaryKeyRelatedField(queryset=CollegeTeamMember.objects.all())
    bowler = serializers.PrimaryKeyRelatedField(queryset=CollegeTeamMember.objects.all())
    runs_scored = serializers.IntegerField(min_value=0, max_value=6, default=0)
    extra_type = serializers.ChoiceField(choices=BallByBall.EXTRA_CHOICES, default='none')
    extra_runs = serializers.IntegerField(min_value=0, default=0)
    is_wicket = serializers.BooleanField(default=False)
    wicket_type = serializers.ChoiceField(choices=BallByBall.WICKET_CHOICES, required=False, allow_null=True)
    player_dismissed = serializers.PrimaryKeyRelatedField(queryset=CollegeTeamMember.objects.all(), required=False, allow_null=True)
    fielder_involved = serializers.PrimaryKeyRelatedField(queryset=CollegeTeamMember.objects.all(), required=False, allow_null=True)
    commentary_text = serializers.CharField(max_length=255, required=False, allow_blank=True)


class PointsTableSerializer(serializers.ModelSerializer):
    team_name = serializers.CharField(source='team.team_name', read_only=True)

    class Meta:
        model = PointsTable
        fields = [
            'id', 'team', 'team_name', 'matches_played',
            'won', 'lost', 'tied', 'no_result', 'points', 'net_run_rate'
        ]


class AnnouncementSerializer(serializers.ModelSerializer):
    class Meta:
        model = Announcement
        fields = '__all__'


class HomepageBannerSerializer(serializers.ModelSerializer):
    class Meta:
        model = HomepageBanner
        fields = '__all__'


from .models import VideoHighlight, NewsArticle, GalleryMedia, TournamentFAQ, NewsletterSubscription

class VideoHighlightSerializer(serializers.ModelSerializer):
    class Meta:
        model = VideoHighlight
        fields = ['id', 'title', 'duration', 'thumbnail', 'youtube_url', 'is_featured', 'created_at']

class NewsArticleSerializer(serializers.ModelSerializer):
    category_display = serializers.CharField(source='get_category_display', read_only=True)

    class Meta:
        model = NewsArticle
        fields = ['id', 'title', 'category', 'category_display', 'summary', 'content', 'cover_image', 'is_featured', 'created_at']

class GalleryMediaSerializer(serializers.ModelSerializer):
    class Meta:
        model = GalleryMedia
        fields = ['id', 'title', 'image', 'created_at']

class TournamentFAQSerializer(serializers.ModelSerializer):
    class Meta:
        model = TournamentFAQ
        fields = ['id', 'question', 'answer', 'order']

class NewsletterSubscriptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = NewsletterSubscription
        fields = ['id', 'email', 'subscribed_at']





from rest_framework import serializers
from .models import (
    Tournament, Venue, Match, VideoHighlight, NewsArticle, 
    GalleryMedia, TournamentFAQ, HomepageBanner, Announcement,
    PointsTable, CollegeRegistration, CollegeTeamMember, SponsorRegistration
)

class AdminTournamentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tournament
        fields = '__all__'

class AdminVenueSerializer(serializers.ModelSerializer):
    class Meta:
        model = Venue
        fields = '__all__'

class AdminMatchSerializer(serializers.ModelSerializer):
    team_a_name = serializers.CharField(source='team_a.team_name', read_only=True)
    team_b_name = serializers.CharField(source='team_b.team_name', read_only=True)

    class Meta:
        model = Match
        fields = '__all__'

class AdminVideoHighlightSerializer(serializers.ModelSerializer):
    class Meta:
        model = VideoHighlight
        fields = '__all__'

class AdminNewsArticleSerializer(serializers.ModelSerializer):
    class Meta:
        model = NewsArticle
        fields = '__all__'

class AdminGalleryMediaSerializer(serializers.ModelSerializer):
    class Meta:
        model = GalleryMedia
        fields = '__all__'

class AdminTournamentFAQSerializer(serializers.ModelSerializer):
    class Meta:
        model = TournamentFAQ
        fields = '__all__'

class AdminHomepageBannerSerializer(serializers.ModelSerializer):
    class Meta:
        model = HomepageBanner
        fields = '__all__'

class AdminAnnouncementSerializer(serializers.ModelSerializer):
    class Meta:
        model = Announcement
        fields = '__all__'

class AdminPointsTableSerializer(serializers.ModelSerializer):
    team_name = serializers.CharField(source='team.team_name', read_only=True)

    class Meta:
        model = PointsTable
        fields = '__all__'

class AdminSponsorSerializer(serializers.ModelSerializer):
    class Meta:
        model = SponsorRegistration
        fields = '__all__'