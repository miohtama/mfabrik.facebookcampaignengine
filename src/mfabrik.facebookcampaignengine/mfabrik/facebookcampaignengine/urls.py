from django.conf.urls.defaults import *

handler500 = 'djangotoolbox.errorviews.server_error'

urlpatterns = patterns('',
    ('^_ah/warmup$', 'djangoappengine.views.warmup'),
    
    # These are required by Facebook application permission dialog
    ('^privacy-policy$', 'django.views.generic.simple.direct_to_template', {'template': 'privacy-policy.html'}),
    ('^terms-of-service$', 'django.views.generic.simple.direct_to_template', {'template': 'terms-of-service.html'}),
    
    # Facebook 
    (r'^facebook/callback(.*)$', "mfabrik.facebookcampaignengine.views.fbook.auth_complete"),
    (r'^facebook/send_love_letter/', "mfabrik.facebookcampaignengine.views.campaign.send_love_letter"),    
    (r'^facebook/select_friend/', "mfabrik.facebookcampaignengine.views.campaign.select_friend"),    
    (r'^facebook/canvas/', "mfabrik.facebookcampaignengine.views.campaign.canvas"),
    (r'^facebook/pagetab', "mfabrik.facebookcampaignengine.views.campaign.page_tab"),
    (r'^facebook/ping/(.*)$', "mfabrik.facebookcampaignengine.views.campaign.ping"),
    (r'^facebook/competition/(.*)$', "mfabrik.facebookcampaignengine.views.campaign.competition"),
        
    # Not sure with this...
    (r'^facebook/(.*)$', "mfabrik.facebookcampaignengine.views.campaign.canvas"),
    
    ('^$', 'django.views.generic.simple.direct_to_template', {'template': 'home.html'}),
)
