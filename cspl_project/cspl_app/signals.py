from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import send_mail
from django.conf import settings
from .models import *
@receiver(post_save, sender=Match)
def notify_subscribers_on_new_match(sender, instance, created, **kwargs):
    """
    Jaise hi naya match add hoga, yeh signal sabhi active newsletter subscribers ko email bhej dega.
    """
    if created:
        # Sabhi active subscribers ki email list nikalna
        subscribers = NewsletterSubscription.objects.filter(is_active=True).values_list('email', flat=True)
        
        if subscribers:
            team_a_name = instance.team_a.team_name if instance.team_a else "Team A"
            team_b_name = instance.team_b.team_name if instance.team_b else "Team B"
            venue_name = instance.venue.name if instance.venue else "TBD"
            match_time = instance.match_datetime.strftime("%d %B %Y, %I:%M %p") if instance.match_datetime else "Soon"

            subject = f"🏏 New Match Scheduled: {team_a_name} vs {team_b_name} - CSPL"
            message = (
                f"Hello from College Sports Premier League (CSPL)!\n\n"
                f"A new match has just been scheduled:\n\n"
                f"⚔️ Match: {team_a_name} vs {team_b_name}\n"
                f"📅 Date & Time: {match_time}\n"
                f"🏟️ Venue: {venue_name}\n\n"
                f"Get ready for high-voltage action! Stay tuned for live updates.\n\n"
                f"Regards,\nCSPL Team"
            )
            
            # Email send karna (background ya direct)
            send_mail(
                subject=subject,
                message=message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=list(subscribers),
                fail_silently=True,
            )

@receiver(post_save, sender=LiveStreamConfig)
def notify_subscribers_on_live_stream(sender, instance, created, **kwargs):
    """
    LiveStreamConfig create ya update hone par agar is_live True hai, toh mail bhejega.
    """
    # Debugger (Terminal par rokne ke liye)
    breakpoint()
    
    # Check karein ki stream live hai aur URL available hai
    if instance.is_live and instance.youtube_stream_url:
        subscribers = list(NewsletterSubscription.objects.filter(is_active=True).values_list('email', flat=True))
        
        print(f"DEBUG: Active subscribers found -> {len(subscribers)}") # Terminal par count dikhega
        
        if subscribers:
            match = instance.match
            team_a_name = match.team_a.team_name if (match and match.team_a) else "Team A"
            team_b_name = match.team_b.team_name if (match and match.team_b) else "Team B"
            stream_url = instance.youtube_stream_url

            subject = f"🔴 LIVE NOW: {team_a_name} vs {team_b_name} - CSPL Match Streaming"
            message = (
                f"Hello from College Sports Premier League (CSPL)!\n\n"
                f"The match is LIVE right now! Catch all the action live:\n\n"
                f"⚔️ Match: {team_a_name} vs {team_b_name}\n"
                f"📺 Watch Live Here: {stream_url}\n\n"
                f"Grab your snacks and join the stream now!\n\n"
                f"Regards,\nCSPL Team"
            )
            
            # fail_silently=False karke dekhein taaki agar koi error ho toh terminal par dikhe
            try:
                send_mail(
                    subject=subject,
                    message=message,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=subscribers,
                    fail_silently=False, 
                )
                print("DEBUG: Live stream email sent successfully!")
            except Exception as e:
                print(f"DEBUG ERROR: Failed to send email -> {e}")


@receiver(post_save, sender=NewsArticle)
def notify_subscribers_on_new_news(sender, instance, created, **kwargs):
    """
    Jaise hi koi naya News Article create hoga, yeh signal sabhi active 
    newsletter subscribers ko breaking news / latest update email bhej dega.
    """
    if created:
        subscribers = list(NewsletterSubscription.objects.filter(is_active=True).values_list('email', flat=True))
        
        if subscribers:
            title = instance.title
            category = instance.get_category_display() if hasattr(instance, 'get_category_display') else "Latest News"
            summary = instance.summary or "Read the full story on the official CSPL portal."

            subject = f"📰 Latest Update: {title} - CSPL"
            message = (
                f"Hello from College Sports Premier League (CSPL)!\n\n"
                f"We have just published a new update under [{category}]:\n\n"
                f"📌 {title}\n\n"
                f"Summary:\n{summary}\n\n"
                f"Visit the website to read the full article.\n\n"
                f"Regards,\nCSPL Team"
            )
            
            send_mail(
                subject=subject,
                message=message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=subscribers,
                fail_silently=True,
            )