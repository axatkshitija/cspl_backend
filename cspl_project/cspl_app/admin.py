from django.contrib import admin, messages
from django.utils import timezone
from .models import *
from .utils import send_approval_email, send_rejection_email
from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model
from django.contrib.admin.forms import AdminAuthenticationForm
from django import forms


def get_college_user_contacts(college):
    return CollegeContactPerson.objects.filter(
        college=college,
        contact_type__in=['coach', 'management_person']
    )

def generate_next_registration_no():
    year = timezone.now().year
    prefix = f"CSPL{year}"

    last_record = CollegeRegistration.objects.filter(
        generated_registration_no__startswith=prefix
    ).exclude(
        generated_registration_no__isnull=True
    ).exclude(
        generated_registration_no=""
    ).order_by('-generated_registration_no').first()

    if last_record and last_record.generated_registration_no:
        last_number = int(last_record.generated_registration_no[-5:])
        next_number = last_number + 1
    else:
        next_number = 1

    return f"{prefix}{str(next_number).zfill(5)}"




@admin.register(CollegeRegistration)
class CollegeRegistrationAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'full_name',
        'registration_number',
        'generated_registration_no',
        'team_name',
        'city',
        'state',
        'status',
        'created_at',
    )
    list_filter = ('status', 'state', 'country', 'filled_by', 'created_at')
    search_fields = ('full_name', 'registration_number', 'generated_registration_no', 'team_name')
    readonly_fields = ('created_at', 'updated_at', 'generated_registration_no')
    ordering = ('-created_at',)
    actions = ['approve_colleges', 'reject_colleges']

    def save_model(self, request, obj, form, change):
        previous_status = None
        if change and obj.pk:
            previous_obj = CollegeRegistration.objects.filter(pk=obj.pk).first()
            if previous_obj:
                previous_status = previous_obj.status

        if obj.status == 'approved' and not obj.generated_registration_no:
            obj.generated_registration_no = generate_next_registration_no()

        super().save_model(request, obj, form, change)

        if change and previous_status != obj.status:
            contacts = get_college_user_contacts(obj)

            if obj.status == 'approved':
                for contact in contacts:
                    if contact.email:
                        send_approval_email(contact.email, contact.name, obj)

                self.message_user(
                    request,
                    "Approval mail sent successfully.",
                    level=messages.SUCCESS
                )

            elif obj.status == 'rejected':
                for contact in contacts:
                    if contact.email:
                        send_rejection_email(contact.email, contact.name, obj)

                self.message_user(
                    request,
                    "Rejection mail sent successfully.",
                    level=messages.WARNING
                )

    @admin.action(description="Approve selected colleges")
    def approve_colleges(self, request, queryset):
        count = 0

        for college in queryset:
            previous_status = college.status

            if college.status != 'approved':
                if not college.generated_registration_no:
                    college.generated_registration_no = generate_next_registration_no()

                college.status = 'approved'
                college.save()

                contacts = get_college_user_contacts(college)
                for contact in contacts:
                    if contact.email:
                        send_approval_email(contact.email, contact.name, college)

                count += 1

        self.message_user(
            request,
            f"{count} college(s) approved and mail sent successfully.",
            level=messages.SUCCESS
        )

    @admin.action(description="Reject selected colleges")
    def reject_colleges(self, request, queryset):
        count = 0

        for college in queryset:
            if college.status != 'rejected':
                college.status = 'rejected'
                college.save()

                contacts = get_college_user_contacts(college)
                for contact in contacts:
                    if contact.email:
                        send_rejection_email(contact.email, contact.name, college)

                count += 1

        self.message_user(
            request,
            f"{count} college(s) rejected and mail sent successfully.",
            level=messages.WARNING
        )

@admin.register(CollegeContactPerson)
class CollegeContactPersonAdmin(admin.ModelAdmin):
    list_display = ('id', 'college', 'contact_type', 'name', 'phone', 'email')
    list_filter = ('contact_type',)
    search_fields = ('college__full_name', 'name', 'phone', 'email')

@admin.register(CollegeTeamMember)
class CollegeTeamMemberAdmin(admin.ModelAdmin):
    list_display = ('id', 'member_code', 'name', 'role', 'college', 'mobile_no')
    list_filter = ('role', 'college')
    search_fields = ('name', 'member_code', 'mobile_no', 'college__team_name')

    

@admin.register(SponsorRegistration)
class SponsorRegistrationAdmin(admin.ModelAdmin):
    list_display = ('id', 'full_name', 'email', 'phone_number', 'company_name', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('full_name', 'email', 'company_name')    


class EmailAuthBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        UserModel = get_user_model()
        try:
            # Username dabba me jo text aaya hai, use database ke email field me dhoondo
            user = UserModel.objects.get(email=username)
        except UserModel.DoesNotExist:
            return None
        if user.check_password(password) and self.user_can_authenticate(user):
            return user
        return None

# 2. Login dabba ke validation ko sahi karne ke liye custom form
class EmailAdminAuthenticationForm(AdminAuthenticationForm):
    username = forms.EmailField(label="Email Address", widget=forms.EmailInput(attrs={'autofocus': True}))

# 3. Django Admin ko naye form par set karein
admin.site.login_form = EmailAdminAuthenticationForm

admin.site.site_header = "Welcome CSPL Admin"
admin.site.site_title = "CSPL Admin Portal"
admin.site.index_title = "Welcome to CSPL Administration"



@admin.register(VendorRegistration)
class VendorRegistrationAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "legal_business_name",
        "trade_name",
        "entity_type",
        "core_category_of_service",
        "primary_contact_person_name",
        "designation",
        "mobile_number",
        "email",
        "pan",
        "gstin",
        "years_of_active_operation",
        "email_verified",
        "phone_verified",
        "created_at",
    )

    list_filter = (
        "entity_type",
        "core_category_of_service",
        "handled_large_scale_sports_tournaments",
        "email_verified",
        "phone_verified",
        "created_at",
        "updated_at",
    )

    search_fields = (
        "legal_business_name",
        "trade_name",
        "primary_contact_person_name",
        "designation",
        "mobile_number",
        "email",
        "pan",
        "gstin",
        "msme_registration_number",
        "bank_name",
        "account_holder_name",
        "ifsc_code",
    )

    readonly_fields = (
        "email_verified",
        "phone_verified",
        "created_at",
        "updated_at",
    )

    fieldsets = (
        ("Company Overview", {
            "fields": (
                "legal_business_name",
                "trade_name",
                "entity_type",
                "other_entity_type",
                "registered_office_address",
                "cin",
            )
        }),
        ("Core Category of Service/Supply", {
            "fields": ("core_category_of_service",)
        }),
        ("Contact Information", {
            "fields": (
                "primary_contact_person_name",
                "designation",
                "mobile_number",
                "email",
                "escalation_contact",
            )
        }),
        ("Statutory & Financial Details", {
            "fields": (
                "pan",
                "gstin",
                "msme_registration_number",
                "bank_name",
                "account_holder_name",
                "account_number",
                "ifsc_code",
            )
        }),
        ("Experience & Past Portfolio", {
            "fields": (
                "years_of_active_operation",
                "handled_large_scale_sports_tournaments",
                "prominent_events_or_projects",
            )
        }),
        ("Documents to Attach", {
            "fields": (
                "pan_card_copy",
                "gst_registration_certificate",
                "cancelled_cheque_or_passbook",
                "company_profile_or_pitch_deck",
            )
        }),
        ("Declaration", {
            "fields": (
                "declaration_name",
                "declaration_designation",
                "signature_and_company_seal",
                "declaration_date",
            )
        }),
        ("Verification & Meta", {
            "fields": (
                "email_verified",
                "phone_verified",
                "created_at",
                "updated_at",
            )
        }),
    )

    ordering = ("-created_at",)

# ==============================================================================
# TOURNAMENT, LIVE SCORING & HOMEPAGE CMS ADMIN CONFIGURATION
# ==============================================================================

class MatchPlayingXIInline(admin.TabularInline):
    model = MatchPlayingXI
    extra = 0
    autocomplete_fields = ['player', 'team']


class InningsInline(admin.TabularInline):
    model = Innings
    extra = 0
    readonly_fields = ['total_runs', 'total_wickets', 'total_overs', 'is_completed']


@admin.register(Tournament)
class TournamentAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'season', 'start_date', 'end_date', 'is_active', 'created_at')
    list_filter = ('is_active', 'season')
    search_fields = ('name', 'season')


@admin.register(Venue)
class VenueAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'city')
    search_fields = ('name', 'city')


@admin.register(Match)
class MatchAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'tournament', 'team_a', 'team_b', 'match_datetime',
        'format', 'total_overs', 'status', 'winner'
    )
    list_filter = ('status', 'format', 'tournament')
    search_fields = ('team_a__team_name', 'team_b__team_name', 'result_description')
    inlines = [MatchPlayingXIInline, InningsInline]
    ordering = ('-match_datetime',)


@admin.register(Innings)
class InningsAdmin(admin.ModelAdmin):
    list_display = ('id', 'match', 'innings_number', 'batting_team', 'bowling_team', 'total_runs', 'total_wickets', 'total_overs', 'is_completed')
    list_filter = ('innings_number', 'is_completed')
    search_fields = ('match__team_a__team_name', 'match__team_b__team_name')


# @admin.register(BallByBall)
# class BallByBallAdmin(admin.ModelAdmin):
#     list_display = ('id', 'innings', 'over_number', 'ball_number', 'bowler', 'striker', 'runs_scored', 'extra_type', 'is_wicket', 'timestamp')
#     list_filter = ('extra_type', 'is_wicket', 'is_four', 'is_six')
#     search_fields = ('striker__name', 'bowler__name')

from decimal import Decimal
from django import forms
from django.contrib import admin
from django.db.models import Sum
from django.core.exceptions import ValidationError
from .models import (
    CollegeRegistration, CollegeTeamMember, CollegeContactPerson,
    Tournament, Venue, Match, Innings, BallByBall, 
    PointsTable, HomepageBanner, LiveStreamConfig, Announcement, SponsorRegistration
)

class CustomPlayerChoiceField(forms.ModelChoiceField):
    """
    Renders visual status tags (🏏 STRIKER, 🏃 NON-STRIKER, ❌ OUT, ⏳ YET TO BAT) in dropdowns.
    """
    def label_from_instance(self, obj):
        status_tag = getattr(obj, '_status_tag', '')
        if status_tag:
            return f"{obj.name} ({obj.college.team_name}) — {status_tag}"
        return f"{obj.name} ({obj.college.team_name})"


class BallByBallAdminForm(forms.ModelForm):
    striker = CustomPlayerChoiceField(queryset=CollegeTeamMember.objects.all(), required=True)
    non_striker = CustomPlayerChoiceField(queryset=CollegeTeamMember.objects.all(), required=True)
    bowler = CustomPlayerChoiceField(queryset=CollegeTeamMember.objects.all(), required=True)
    player_dismissed = CustomPlayerChoiceField(queryset=CollegeTeamMember.objects.all(), required=False)
    fielder_involved = CustomPlayerChoiceField(queryset=CollegeTeamMember.objects.all(), required=False)

    class Meta:
        model = BallByBall
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # 1. Identify active innings
        innings = None
        if self.instance and hasattr(self.instance, 'innings_id') and self.instance.innings_id:
            innings = self.instance.innings
        elif 'innings' in self.initial and self.initial['innings']:
            innings = Innings.objects.filter(pk=self.initial['innings']).first()
        elif self.data and self.data.get('innings'):
            innings = Innings.objects.filter(pk=self.data.get('innings')).first()
        else:
            innings = Innings.objects.filter(is_completed=False).last() or Innings.objects.last()

        if innings:
            # 2. Fetch all previous deliveries to identify dismissed players and crease status
            previous_deliveries = innings.balls.all()
            if self.instance and self.instance.pk:
                previous_deliveries = previous_deliveries.exclude(pk=self.instance.pk)

            # Map dismissed players
            dismissed_events = previous_deliveries.filter(is_wicket=True).exclude(wicket_type='retired_hurt')
            dismissed_dict = {
                b.player_dismissed_id: (b.wicket_type or 'Out')
                for b in dismissed_events if b.player_dismissed_id
            }

            # Identify batsmen currently on the crease
            last_ball = previous_deliveries.order_by('-id').first()
            current_striker_id = last_ball.striker_id if last_ball else None
            current_non_striker_id = last_ball.non_striker_id if last_ball else None

            # 3. Label Batting Team Players
            batting_players = list(CollegeTeamMember.objects.filter(college=innings.batting_team))
            for p in batting_players:
                if p.id in dismissed_dict:
                    p._status_tag = f"❌ [OUT - {dismissed_dict[p.id].upper()}]"
                elif p.id == current_striker_id:
                    p._status_tag = "🏏 [ON CREASE - STRIKER]"
                elif p.id == current_non_striker_id:
                    p._status_tag = "🏃 [ON CREASE - NON-STRIKER]"
                else:
                    p._status_tag = "⏳ [YET TO BAT]"

            batting_qs = CollegeTeamMember.objects.filter(id__in=[p.id for p in batting_players])
            self.fields['striker'].queryset = batting_qs
            self.fields['non_striker'].queryset = batting_qs
            self.fields['player_dismissed'].queryset = batting_qs

            # 4. Label Bowling Team Players
            bowling_players = list(CollegeTeamMember.objects.filter(college=innings.bowling_team))
            for p in bowling_players:
                p._status_tag = "🎯 [BOWLER / FIELDER]"

            bowling_qs = CollegeTeamMember.objects.filter(id__in=[p.id for p in bowling_players])
            self.fields['bowler'].queryset = bowling_qs
            self.fields['fielder_involved'].queryset = bowling_qs

    def clean(self):
        cleaned_data = super().clean()
        innings = cleaned_data.get('innings')
        over_number = cleaned_data.get('over_number')
        ball_number = cleaned_data.get('ball_number')
        striker = cleaned_data.get('striker')
        non_striker = cleaned_data.get('non_striker')
        bowler = cleaned_data.get('bowler')
        extra_type = cleaned_data.get('extra_type')
        runs_scored = cleaned_data.get('runs_scored')
        is_wicket = cleaned_data.get('is_wicket')
        wicket_type = cleaned_data.get('wicket_type')
        player_dismissed = cleaned_data.get('player_dismissed')

        if not innings:
            return cleaned_data

        # Rule 1: Striker and Non-Striker must be distinct
        if striker and non_striker and striker.id == non_striker.id:
            raise ValidationError({
                'non_striker': "Striker and Non-Striker cannot be the same player."
            })

        # Rule 2: Restrict bat runs between 0 and 6
        if runs_scored is not None and runs_scored not in [0, 1, 2, 3, 4, 5, 6]:
            raise ValidationError({
                'runs_scored': "Runs scored off the bat on a single delivery must be between 0 and 6."
            })

        # Rule 3: Duplicate Legal Ball Validation (Prevent repeating Over/Ball)
        if over_number is not None and ball_number is not None:
            existing_deliveries = BallByBall.objects.filter(
                innings=innings,
                over_number=over_number,
                ball_number=ball_number
            )
            if self.instance and self.instance.pk:
                existing_deliveries = existing_deliveries.exclude(pk=self.instance.pk)

            has_legal_ball = existing_deliveries.filter(extra_type__in=['none', 'bye', 'leg_bye']).exists()
            if has_legal_ball and extra_type in ['none', 'bye', 'leg_bye']:
                raise ValidationError({
                    'ball_number': f"Over {over_number}, Ball {ball_number} has already been recorded with a legal delivery! Please increment the ball number for the next delivery."
                })

        # Rule 4: Hard Block Already Dismissed (OUT) Batsmen
        previous_balls = innings.balls.all()
        if self.instance and self.instance.pk:
            previous_balls = previous_balls.exclude(pk=self.instance.pk)

        dismissed_ids = set(
            previous_balls.filter(is_wicket=True)
            .exclude(wicket_type='retired_hurt')
            .values_list('player_dismissed_id', flat=True)
        )

        if striker and striker.id in dismissed_ids:
            raise ValidationError({
                'striker': f"Invalid Entry: {striker.name} has already been dismissed (OUT) in this innings! They cannot be selected as striker."
            })

        if non_striker and non_striker.id in dismissed_ids:
            raise ValidationError({
                'non_striker': f"Invalid Entry: {non_striker.name} has already been dismissed (OUT) in this innings! They cannot be selected as non-striker."
            })

        # Rule 5: Wicket Consistency
        if is_wicket:
            if not wicket_type:
                raise ValidationError({'wicket_type': "Please select a Wicket Type when a wicket occurs."})
            if not player_dismissed:
                cleaned_data['player_dismissed'] = striker
            elif player_dismissed.id in dismissed_ids:
                raise ValidationError({
                    'player_dismissed': f"{player_dismissed.name} is already dismissed (OUT)."
                })
        else:
            if wicket_type or player_dismissed:
                raise ValidationError({'is_wicket': "Please check 'Is Wicket' if a batsman is being dismissed."})

        # Rule 6: Bowler must belong to the bowling team
        if bowler and bowler.college_id != innings.bowling_team_id:
            raise ValidationError({
                'bowler': f"Bowler ({bowler.name}) must belong to the bowling team ({innings.bowling_team.team_name})."
            })

        return cleaned_data


@admin.register(BallByBall)
class BallByBallAdmin(admin.ModelAdmin):
    form = BallByBallAdminForm
    list_display = (
        'id', 'innings', 'over_number', 'ball_number', 
        'striker', 'bowler', 'runs_scored', 'extra_type', 
        'extra_runs', 'is_wicket'
    )
    list_filter = ('innings', 'is_wicket', 'extra_type')
    readonly_fields = ('is_dot_ball', 'is_four', 'is_six')

    def get_changeform_initial_data(self, request):
        """
        Auto-calculates next Over and Ball number dynamically when adding a new ball.
        """
        initial = super().get_changeform_initial_data(request)
        active_innings = Innings.objects.filter(is_completed=False).last() or Innings.objects.last()
        
        if active_innings:
            last_ball = active_innings.balls.order_by('-id').first()
            if last_ball:
                if last_ball.extra_type in ['wide', 'no_ball']:
                    initial['over_number'] = last_ball.over_number
                    initial['ball_number'] = last_ball.ball_number
                elif last_ball.ball_number >= 6:
                    initial['over_number'] = last_ball.over_number + 1
                    initial['ball_number'] = 1
                else:
                    initial['over_number'] = last_ball.over_number
                    initial['ball_number'] = last_ball.ball_number + 1
                
                initial['innings'] = active_innings.id
                initial['striker'] = last_ball.striker_id
                initial['non_striker'] = last_ball.non_striker_id
                initial['bowler'] = last_ball.bowler_id

        return initial

    def save_model(self, request, obj, form, change):
        if obj.extra_type in ['wide', 'no_ball']:
            obj.is_dot_ball = False
        else:
            obj.is_dot_ball = (obj.runs_scored == 0 and not obj.is_wicket)

        obj.is_four = (obj.runs_scored == 4)
        obj.is_six = (obj.runs_scored == 6)

        super().save_model(request, obj, form, change)
        self.recalculate_innings(obj.innings)

    def delete_model(self, request, obj):
        innings = obj.innings
        super().delete_model(request, obj)
        self.recalculate_innings(innings)

    def recalculate_innings(self, innings):
        balls = innings.balls.all()
        bat_runs = balls.aggregate(total=Sum('runs_scored'))['total'] or 0
        extra_runs = balls.aggregate(total=Sum('extra_runs'))['total'] or 0
        total_runs = bat_runs + extra_runs

        total_wickets = balls.filter(is_wicket=True).exclude(wicket_type='retired_hurt').count()

        legal_balls_count = balls.exclude(extra_type__in=['wide', 'no_ball']).count()
        completed_overs = legal_balls_count // 6
        remaining_balls = legal_balls_count % 6
        total_overs = Decimal(f"{completed_overs}.{remaining_balls}")

        innings.total_runs = total_runs
        innings.total_wickets = total_wickets
        innings.total_overs = total_overs
        innings.save(update_fields=['total_runs', 'total_wickets', 'total_overs'])
        


@admin.register(PointsTable)
class PointsTableAdmin(admin.ModelAdmin):
    list_display = ('id', 'tournament', 'team', 'matches_played', 'won', 'lost', 'tied', 'points', 'net_run_rate')
    list_filter = ('tournament',)
    search_fields = ('team__team_name',)
    ordering = ('tournament', '-points', '-net_run_rate')


@admin.register(HomepageBanner)
class HomepageBannerAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'season_tag', 'cta_title', 'is_active', 'created_at')
    list_filter = ('is_active',)
    search_fields = ('title', 'season_tag')


@admin.register(LiveStreamConfig)
class LiveStreamConfigAdmin(admin.ModelAdmin):
    list_display = ('id', 'match', 'youtube_stream_url', 'is_live', 'created_at')
    list_filter = ('is_live',)
    search_fields = ('match__team_a__team_name', 'match__team_b__team_name')


@admin.register(Announcement)
class AnnouncementAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'is_pinned', 'is_active', 'created_at')
    list_filter = ('is_pinned', 'is_active')
    search_fields = ('title', 'details')

@admin.register(VideoHighlight)
class HighlightAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'duration', 'is_featured', 'created_at')
    list_filter = ('is_featured',)

@admin.register(NewsArticle)
class NewsArticleAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'category', 'is_featured', 'created_at')
    list_filter = ('category', 'is_featured')

class GalleryMediaInline(admin.TabularInline):
    model = GalleryMedia
    extra = 1 
    fields = ('title', 'subtitle', 'image', 'match', 'is_featured')
    autocomplete_fields = ['match']


@admin.register(GalleryAlbum)
class GalleryAlbumAdmin(admin.ModelAdmin):
    # Yahan se 'subtitle' aur 'is_featured' hata diye gaye hain
    list_display = ('id', 'title', 'total_photos_count', 'created_at')
    search_fields = ('title',)
    inlines = [GalleryMediaInline]
    ordering = ('-created_at',)

    def total_photos_count(self, obj):
        return f"{obj.photos.count()} Photos"
    total_photos_count.short_description = "Total Photos"


@admin.register(GalleryMedia)
class GalleryMediaAdmin(admin.ModelAdmin):
    # Single photos ke panel mein fields properly set hain
    list_display = ('id', 'title', 'subtitle', 'album', 'is_featured', 'created_at')
    list_filter = ('is_featured', 'created_at', 'album')
    list_editable = ('is_featured',)
    search_fields = ('title', 'subtitle')
    autocomplete_fields = ['album', 'match']

@admin.register(TournamentFAQ)
class TournamentFAQAdmin(admin.ModelAdmin):
    list_display = ('id', 'question', 'order', 'is_active')
    list_editable = ('order', 'is_active')

@admin.register(NewsletterSubscription)
class NewsletterSubscriptionAdmin(admin.ModelAdmin):
    list_display = ('id', 'email', 'subscribed_at', 'is_active')
    search_fields = ('email',)

@admin.register(BroadcastPartner)
class BroadcastPartnerAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'partner_type', 'is_active', 'display_order')
    list_filter = ('is_active', 'partner_type')
    list_editable = ('display_order', 'is_active')
    search_fields = ('name', 'partner_type')

@admin.register(AssociateSponsor)
class AssociateSponsorAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'sponsor_tier', 'is_active', 'display_order', 'created_at')
    list_filter = ('is_active', 'sponsor_tier')
    list_editable = ('display_order', 'is_active')
    search_fields = ('name', 'sponsor_tier')

@admin.register(Testimonial)
class TestimonialAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'designation', 'rating', 'is_active', 'display_order')
    list_filter = ('is_active', 'rating')
    list_editable = ('display_order', 'is_active')
    search_fields = ('name', 'designation', 'quote')


@admin.register(VideoMatchHighlight)
class VideoMatchHighlightAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'event_name', 'team_name', 'created_at')
    # list_filter = ('event_name', 'team_name', 'created_at')
    search_fields = ('title', 'event_name', 'team_name')

@admin.register(VideoGallery)
class VideoGalleryAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'is_featured', 'created_at')
    list_filter = ('is_featured', 'created_at')
    search_fields = ('title', 'subtitle')


@admin.register(RewardAndAward)
class RewardAndAwardAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'category', 'prize_amount', 'tournament', 'is_active', 'created_at')
    list_filter = ('category', 'is_active', 'created_at')
    search_fields = ('title', 'description')