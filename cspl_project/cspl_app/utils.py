import requests
from twilio.rest import Client
from django.conf import settings

import random
# from twilio.rest import Client
from django.conf import settings
from django.core.mail import send_mail
from django.utils import timezone


def send_login_otp_email(email, otp_code):
    subject = "Your Login OTP"
    message = f"Your OTP for login is {otp_code}. It is valid for 10 minutes."
    send_mail(
        subject,
        message,
        settings.DEFAULT_FROM_EMAIL,
        [email],
        fail_silently=False
    )
import requests
from django.conf import settings

import requests
from django.conf import settings


def send_sms_quick_fast2sms(phone, otp):
    url = "https://www.fast2sms.com/dev/bulkV2"

    params = {
        "authorization": settings.FAST2SMS_API_KEY.strip(),
        "route": "dlt",
        "sender_id": settings.FAST2SMS_SENDER_ID.strip(),
        # yahan DLT template ID jayegi, message text nahi
        "message": settings.FAST2SMS_TEMPLATE_ID_OTP.strip(),
        # template me jitne {#var#} honge, utne values '|' se separated
        "variables_values": str(otp).strip(),
        "numbers": str(phone).strip(),
    }

    response = requests.get(url, params=params, timeout=20)

    print("FAST2SMS URL:", response.url)
    print("FAST2SMS STATUS:", response.status_code)
    print("FAST2SMS TEXT:", repr(response.text))

    if response.status_code != 200:
        return {
            "return": False,
            "status_code": response.status_code,
            "message": "HTTP error from SMS provider",
            "raw_response": response.text,
        }

    if not response.text.strip():
        return {
            "return": False,
            "status_code": 200,
            "message": "Empty response from SMS provider",
            "raw_response": response.text,
        }

    try:
        return response.json()
    except Exception:
        return {
            "return": False,
            "status_code": 200,
            "message": "Non-JSON response from SMS provider",
            "raw_response": response.text,
        }


def generate_email_otp():
    return str(random.randint(100000, 999999))


def send_email_otp(email, otp):
    send_mail(
        subject="Email Verification OTP",
        message=f"Your OTP for email verification is {otp}. It is valid for 10 minutes.",
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[email],
        fail_silently=False
    )

def format_indian_phone(phone):
    phone = str(phone).strip().replace(" ", "")
    if phone.startswith("+"):
        return phone
    return f"+91{phone}"


def send_otp_sms(phone):
    client = Client(
        settings.TWILIO_ACCOUNT_SID,
        settings.TWILIO_AUTH_TOKEN
    )

    verification = client.verify.v2.services(
        settings.TWILIO_VERIFY_SERVICE_SID
    ).verifications.create(
        to=format_indian_phone(phone),
        channel="sms"
    )

    return verification


def verify_otp_sms(phone, otp):
    client = Client(
        settings.TWILIO_ACCOUNT_SID,
        settings.TWILIO_AUTH_TOKEN
    )

    result = client.verify.v2.services(
        settings.TWILIO_VERIFY_SERVICE_SID
    ).verification_checks.create(
        to=format_indian_phone(phone),
        code=otp
    )

    return result


from django.conf import settings
from django.core.mail import EmailMultiAlternatives


def send_html_email(subject, text_content, html_content, recipient_list):
    msg = EmailMultiAlternatives(
        subject=subject,
        body=text_content,
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=recipient_list
    )
    msg.attach_alternative(html_content, "text/html")
    msg.send(fail_silently=False)



def send_approval_email(user_email, user_name, college):
    subject = "College Registration Approved"

    text_content = (
        f"Dear {user_name},\n\n"
        f"Congratulations. Your college registration has been approved.\n"
        f"You can now login using your registration number, password, and OTP.\n\n"
        f"College Name: {college.full_name}\n"
        # f"Registration Number: {college.registration_number}\n"
        f"CSPL Code ID: {college.generated_registration_no}\n\n"
        f"Regards,\n"
        f"CSPL Team"
    )

    html_content = f"""
        <p>Dear {user_name},</p>
        <p>Congratulations. Your college registration has been <strong>approved</strong>.</p>
        <p>You can now login using your registration number, email, and OTP.</p>
        <p><strong>College Name:</strong> {college.full_name}</p>
        <p><strong>CSPL Code ID:</strong> {college.generated_registration_no}</p>
        <p>Regards,<br>CSPL Team</p>
    """
        # <p><strong>Registration Number:</strong> {college.registration_number}</p>

    send_html_email(subject, text_content, html_content, [user_email])


def send_rejection_email(user_email, user_name, college):
    subject = "College Registration Rejected"

    text_content = (
        f"Dear {user_name},\n\n"
        f"We are sorry to inform you that your college registration has been rejected.\n\n"
        f"College Name: {college.full_name}\n"
        f"Registration Number: {college.registration_number}\n\n"
        f"For further assistance, please contact the support team.\n\n"
        f"Regards,\n"
        f"CSPL Team"
    )

    html_content = f"""
        <p>Dear {user_name},</p>
        <p>We are sorry to inform you that your college registration has been <strong>rejected</strong>.</p>
        <p><strong>College Name:</strong> {college.full_name}</p>
        <p><strong>Registration Number:</strong> {college.registration_number}</p>
        <p>For further assistance, please contact the support team.</p>
        <p>Regards,<br>CSPL Team</p>
    """

    send_html_email(subject, text_content, html_content, [user_email])


def send_registration_thank_you_email(user_email, user_name, college):
    subject = "Thank you for your registration"

    text_content = (
        f"Dear {user_name},\n\n"
        f"Thank you for your registration for {college.full_name}.\n"
        f"Your application has been received successfully and is under review.\n\n"
        f"Registration Number: {college.registration_number}\n"
        f"Team Name: {college.team_name}\n\n"
        f"Regards,\n"
        f"CSPL Team"
    )

    html_content = f"""
        <p>Dear {user_name},</p>
        <p>Thank you for your registration for <strong>{college.full_name}</strong>.</p>
        <p>Your application has been received successfully and is under review.</p>
        <p><strong>Registration Number:</strong> {college.registration_number}</p>
        <p><strong>Team Name:</strong> {college.team_name}</p>
        <p>Regards,<br>CSPL Team</p>
    """

    send_html_email(subject, text_content, html_content, [user_email])


def send_admin_registration_notification(college, coach, sports_teacher, management_person):
    subject = f"New College Registration Received - {college.full_name}"

    text_content = (
        f"A new college registration has been submitted and is waiting for approval.\n\n"
        f"College Details:\n"
        f"Full Name: {college.full_name}\n"
        f"NGO/Trust: {college.ngo_or_trust}\n"
        f"Registration Number: {college.registration_number}\n"
        f"Team Name: {college.team_name}\n"
        f"Address Line 1: {college.address_line_1}\n"
        f"Address Line 2: {college.address_line_2}\n"
        f"City: {college.city}\n"
        f"State: {college.state}\n"
        f"Country: {college.country}\n"
        f"Pin Code: {college.pin_code}\n"
        f"Filled By: {college.filled_by}\n"
        f"Status: {college.status}\n\n"
        f"Coach Details:\n"
        f"Name: {coach.name}\n"
        f"Phone: {coach.phone}\n"
        f"Email: {coach.email}\n\n"
        f"Sports Teacher Details:\n"
        f"Name: {sports_teacher.name}\n"
        f"Phone: {sports_teacher.phone}\n"
        f"Email: {sports_teacher.email}\n\n"
        f"Management Person Details:\n"
        f"Name: {management_person.name}\n"
        f"Phone: {management_person.phone}\n"
        f"Email: {management_person.email}\n\n"
        f"Admin Panel: {settings.ADMIN_PANEL_URL}"
    )

    html_content = f"""
        <p>A new college registration has been submitted and is waiting for approval.</p>

        <h3>College Details</h3>
        <p><strong>Full Name:</strong> {college.full_name}</p>
        <p><strong>NGO/Trust:</strong> {college.ngo_or_trust}</p>
        <p><strong>Registration Number:</strong> {college.registration_number}</p>
        <p><strong>Team Name:</strong> {college.team_name}</p>
        <p><strong>Address Line 1:</strong> {college.address_line_1}</p>
        <p><strong>Address Line 2:</strong> {college.address_line_2}</p>
        <p><strong>City:</strong> {college.city}</p>
        <p><strong>State:</strong> {college.state}</p>
        <p><strong>Country:</strong> {college.country}</p>
        <p><strong>Pin Code:</strong> {college.pin_code}</p>
        <p><strong>Filled By:</strong> {college.filled_by}</p>
        <p><strong>Status:</strong> {college.status}</p>

        <h3>Coach Details</h3>
        <p><strong>Name:</strong> {coach.name}</p>
        <p><strong>Phone:</strong> {coach.phone}</p>
        <p><strong>Email:</strong> {coach.email}</p>

        <h3>Sports Teacher Details</h3>
        <p><strong>Name:</strong> {sports_teacher.name}</p>
        <p><strong>Phone:</strong> {sports_teacher.phone}</p>
        <p><strong>Email:</strong> {sports_teacher.email}</p>

        <h3>Management Person Details</h3>
        <p><strong>Name:</strong> {management_person.name}</p>
        <p><strong>Phone:</strong> {management_person.phone}</p>
        <p><strong>Email:</strong> {management_person.email}</p>

        <p>
            <a href="{settings.ADMIN_PANEL_URL}" target="_blank" rel="noopener noreferrer">
                Open Admin Panel
            </a>
        </p>
    """

    send_html_email(
        subject,
        text_content,
        html_content,
        [settings.ADMIN_NOTIFICATION_EMAIL]
    )



from django.conf import settings
from django.core.mail import send_mail


def send_sponsor_admin_notification(sponsor):
    subject = f"New Sponsor Registration: {sponsor.company_name}"
    message = (
        f"New sponsor registration details:\n\n"
        f"Company Name: {sponsor.company_name}\n"
        f"Industry Sector: {sponsor.industry_sector}\n"
        f"Contact Person: {sponsor.full_name}\n"
        f"Email: {sponsor.email}\n"
        f"Phone Number: {sponsor.phone_number}\n"
        f"Sponsor Tier: {sponsor.sponsor_tier}\n"
        f"Preferred Engagement Zones: {', '.join(sponsor.preferred_engagement_zones or [])}\n"
        f"Primary Goal: {sponsor.primary_goal}\n"
        f"Target Demographic: {', '.join(sponsor.target_demographic or [])}\n"
        f"Require Stall Booth: {'Yes' if sponsor.require_stall_booth else 'No'}\n"
        f"Estimated Budget Range: {sponsor.estimated_budget_range}\n"
        f"Partnership Duration: {sponsor.partnership_duration}\n"
    )

    admin_email = getattr(settings, "SPONSOR_ADMIN_EMAIL", settings.DEFAULT_FROM_EMAIL)

    send_mail(
        subject=subject,
        message=message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[admin_email],
        fail_silently=False,
    )


def send_sponsor_thank_you_email(sponsor):
    subject = "Thank you for registering as a Sponsor"
    message = (
        f"Dear {sponsor.full_name},\n\n"
        f"Thank you for registering {sponsor.company_name} as a sponsor.\n"
        f"Our team will review your details and get back to you shortly.\n\n"
        f"Summary of your submission:\n"
        f"- Sponsor Tier: {sponsor.sponsor_tier}\n"
        f"- Primary Goal: {sponsor.primary_goal}\n"
        f"- Estimated Budget Range: {sponsor.estimated_budget_range}\n"
        f"- Partnership Duration: {sponsor.partnership_duration}\n\n"
        f"Regards,\n"
        f"Organizing Team"
    )

    send_mail(
        subject=subject,
        message=message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[sponsor.email],
        fail_silently=False,
    )




def send_vendor_submission_mail_to_admin(vendor):
    subject = "New Vendor Registration Submitted"
    message = (
        f"A new vendor registration has been submitted.\n\n"
        f"Legal Business Name: {vendor.legal_business_name}\n"
        f"Trade Name: {vendor.trade_name}\n"
        f"Entity Type: {vendor.get_entity_type_display()}\n"
        f"Registered Office Address: {vendor.registered_office_address}\n"
        f"CIN: {vendor.cin}\n"
        f"Core Service Category: {vendor.get_core_category_of_service_display()}\n\n"
        f"Primary Contact Person: {vendor.primary_contact_person_name}\n"
        f"Designation: {vendor.designation}\n"
        f"Mobile Number: {vendor.mobile_number}\n"
        f"Email: {vendor.email}\n"
        f"Escalation Contact: {vendor.escalation_contact}\n\n"
        f"PAN: {vendor.pan}\n"
        f"GSTIN: {vendor.gstin}\n"
        f"MSME Registration Number: {vendor.msme_registration_number}\n"
        f"Bank Name: {vendor.bank_name}\n"
        f"Account Holder Name: {vendor.account_holder_name}\n"
        f"Account Number: {vendor.account_number}\n"
        f"IFSC Code: {vendor.ifsc_code}\n\n"
        f"Years of Active Operation: {vendor.years_of_active_operation}\n"
        f"Handled Large Scale Sports Tournaments: {'Yes' if vendor.handled_large_scale_sports_tournaments else 'No'}\n"
        f"Prominent Events / Projects: {vendor.prominent_events_or_projects}\n\n"
        f"Declaration Name: {vendor.declaration_name}\n"
        f"Declaration Designation: {vendor.declaration_designation}\n"
        f"Declaration Date: {vendor.declaration_date}\n"
        f"Created At: {vendor.created_at}\n"
    )

    admin_emails = [email for _, email in settings.ADMINS] if getattr(settings, "ADMINS", None) else [settings.DEFAULT_FROM_EMAIL]

    send_mail(
        subject=subject,
        message=message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=admin_emails,
        fail_silently=False
    )


def send_vendor_submission_mail_to_vendor(vendor):
    subject = "Vendor Registration Submitted Successfully"
    message = (
        f"Dear {vendor.primary_contact_person_name},\n\n"
        f"Your vendor registration form has been submitted successfully.\n"
        f"Our team will review the details submitted by you.\n"
        f"Regards,\n"
        f"Team"
    )

    send_mail(
        subject=subject,
        message=message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[vendor.email],
        fail_silently=False
    )
