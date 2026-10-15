from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from cspl_app.views import (
    CollegeBasicInfoCreateAPIView,
    SendOTPView,
    VerifyOTPView,
    InstitutionInformationUpdateAPIView,
    AddTeamMembersAPIView,
    CollegeDocumentUploadAPIView,
    SponsorRegistrationAPIView,
    SendCollegeContactOTPAPIView,
    VerifyCollegeContactOTPAPIView,
    CollegeMasterDataAPIView,
    VendorRegistrationCreateAPIView,
    SendVendorContactOTPAPIView,
    VerifyVendorContactOTPAPIView,
    VendorRegistrationListAPIView,
    VendorRegistrationDetailAPIView,
    MatchSetupAPIView,
    RecordTossAPI,
    StartInningsAPIView,
    RecordBallAPIView,
    UndoBallAPIView,
    LiveMatchScorecardAPIView,
    TournamentLeaderboardAPIView,
    HomepageMasterAPIView,
    FullMatchScorecardAPIView,
    PlayerProfileStatsAPIView,
    MatchAnalyticsAPIView,
    ScorerMatchContextAPIView,
    NewsletterSubscribeAPIView,
    # Admin ViewSets
    AdminTournamentViewSet,
    AdminVenueViewSet,
    AdminMatchViewSet,
    AdminVideoHighlightViewSet,
    AdminNewsArticleViewSet,
    AdminGalleryMediaViewSet,
    AdminTournamentFAQViewSet,
    AdminHomepageBannerViewSet,
    AdminAnnouncementViewSet,
    AdminPointsTableViewSet,
    AdminSponsorViewSet,
    AdminLoginAPIView,
    CleanHomepageAPIView,
    FullPointsTableAPIView,
    get_categorized_matches,
    subscribe_newsletter,
    testimonial_api,
    get_latest_news_api,
    get_photo_gallery_api,
    get_all_sponsors_api,
    contact_us_api,
    video_highlights_api,
    get_video_gallery_api,
    get_tournaments_list,
    get_tournament_detail,
    rewards_and_awards_api,
    tournament_statistics_api
)

# Custom Admin REST Router
admin_router = DefaultRouter()
admin_router.register(r'admin/tournaments', AdminTournamentViewSet, basename='admin-tournaments')
admin_router.register(r'admin/venues', AdminVenueViewSet, basename='admin-venues')
admin_router.register(r'admin/matches', AdminMatchViewSet, basename='admin-matches')
admin_router.register(r'admin/videos', AdminVideoHighlightViewSet, basename='admin-videos')
admin_router.register(r'admin/news', AdminNewsArticleViewSet, basename='admin-news')
admin_router.register(r'admin/gallery', AdminGalleryMediaViewSet, basename='admin-gallery')
admin_router.register(r'admin/faqs', AdminTournamentFAQViewSet, basename='admin-faqs')
admin_router.register(r'admin/banners', AdminHomepageBannerViewSet, basename='admin-banners')
admin_router.register(r'admin/announcements', AdminAnnouncementViewSet, basename='admin-announcements')
admin_router.register(r'admin/points-table', AdminPointsTableViewSet, basename='admin-points-table')
admin_router.register(r'admin/sponsors', AdminSponsorViewSet, basename='admin-sponsors')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/college/basic-info/', CollegeBasicInfoCreateAPIView.as_view(), name='college-basic-info-create'),
    path("api/college/login/", SendOTPView.as_view(), name="send-otp"),
    path("api/college/verify-otp/", VerifyOTPView.as_view(), name="verify-otp"),
    path("api/college/institution-information/", InstitutionInformationUpdateAPIView.as_view(), name="institution-information-update"),
    path('api/college/add-team-members/', AddTeamMembersAPIView.as_view(), name='add-team-members'),
    path('api/college/upload-documents/', CollegeDocumentUploadAPIView.as_view(), name='college-upload-documents'),
    path("api/college/sponsor-registration/", SponsorRegistrationAPIView.as_view(), name="sponsor-registration"),
    path('send-contact-otp/', SendCollegeContactOTPAPIView.as_view(), name='send-contact-otp'),
    path('verify-contact-otp/', VerifyCollegeContactOTPAPIView.as_view(), name='verify-contact-otp'),
    path("api/college/master-data/", CollegeMasterDataAPIView.as_view(), name="college-master-data"),
    path("vender-register/", VendorRegistrationCreateAPIView.as_view(), name="vendor-register"),
    path("vender-send-contact-otp/", SendVendorContactOTPAPIView.as_view(), name="vendor-send-contact-otp"),
    path("vender-verify-contact-otp/", VerifyVendorContactOTPAPIView.as_view(), name="vendor-verify-contact-otp"),
    path("vender-list/", VendorRegistrationListAPIView.as_view(), name="vendor-registration-list"),
    path("vender-detail/<int:pk>/", VendorRegistrationDetailAPIView.as_view(), name="vendor-registration-detail"),

    # Tournament & Live Scoring API Routes
    path('scoring/match-setup/', MatchSetupAPIView.as_view(), name='scoring-match-setup'),
    path('scoring/match/<int:match_id>/toss/', RecordTossAPI.as_view(), name='scoring-record-toss'),
    path('scoring/match/<int:match_id>/start-innings/', StartInningsAPIView.as_view(), name='scoring-start-innings'),
    path('scoring/innings/<int:innings_id>/record-ball/', RecordBallAPIView.as_view(), name='scoring-record-ball'),
    path('scoring/innings/<int:innings_id>/undo-ball/', UndoBallAPIView.as_view(), name='scoring-undo-ball'),

    # Public & Fan Endpoints
    path('matches/<int:match_id>/scorecard/', LiveMatchScorecardAPIView.as_view(), name='match-scorecard'),
    path('tournament/<int:tournament_id>/leaderboard/', TournamentLeaderboardAPIView.as_view(), name='tournament-leaderboard'),
    # path('homepage/master/', HomepageMasterAPIView.as_view(), name='homepage-master-data'),   
    path('matches/<int:match_id>/full-scorecard/', FullMatchScorecardAPIView.as_view(), name='full-match-scorecard'),  
    path('players/<int:player_id>/profile/', PlayerProfileStatsAPIView.as_view(), name='player-profile-stats'),
    path('matches/<int:match_id>/analytics/', MatchAnalyticsAPIView.as_view(), name='match-analytics'),
    path('matches/<int:match_id>/scorer-context/', ScorerMatchContextAPIView.as_view(), name='scorer-match-context'),
    path('newsletter/subscribe/', NewsletterSubscribeAPIView.as_view(), name='newsletter-subscribe'),

    # Custom Admin API Endpoints (CRUD)
    path('api/', include(admin_router.urls)),
    path('api/admin/login/', AdminLoginAPIView.as_view(), name='admin-login'),
    path('api/subscribe/', subscribe_newsletter, name='subscribe_newsletter'),
    path('api/points-table/', FullPointsTableAPIView.as_view(), name='full-points-table'),
    path('api/testimonials/', testimonial_api, name='testimonial_api'),
    path('homepage/master/',CleanHomepageAPIView.as_view(), name='homepage-master-data'),
    path('matches/categorized/', get_categorized_matches, name='get_categorized_matches'),
    path('news/latest/', get_latest_news_api, name='get_latest_news_api'),
    path('api/gallery/', get_photo_gallery_api, name='get_photo_gallery_api'),
    path('api/sponsors/all/', get_all_sponsors_api, name='get_all_sponsors_api'),
    path('api/contact/', contact_us_api, name='contact_us_api'),
    path('api/highlights/', video_highlights_api, name='video_highlights_api'),
    path('api/video-gallery/', get_video_gallery_api, name='get_video_gallery_api'),
    path('api/tournaments/', get_tournaments_list, name='get_tournaments_list'),
    path('api/tournaments/<int:pk>/', get_tournament_detail, name='get_tournament_detail'),
    path('api/rewards/', rewards_and_awards_api, name='rewards_and_awards_api'),  # get / post
    path('api/tournament-statistics/', tournament_statistics_api, name='tournament_statistics_api'),

]