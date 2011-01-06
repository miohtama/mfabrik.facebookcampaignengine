from django.conf.urls.defaults import *

handler500 = 'djangotoolbox.errorviews.server_error'

urlpatterns = patterns('',
    ('^_ah/warmup$', 'djangoappengine.views.warmup'),
    
    # These are required by Facebook application permission dialog
    ('^privacy-policy$', 'django.views.generic.simple.direct_to_template', {'template': 'privacy-policy.html'}),
    ('^terms-of-service$', 'django.views.generic.simple.direct_to_template', {'template': 'terms-of-service.html'}),
    
    # Facebook 
    (r'^facebook/callback(.*)$', "mfabrik.facebookcampaignengine.views.fbook.auth_complete"),    
    (r'^facebook/canvas/', "mfabrik.facebookcampaignengine.views.campaign.canvas"),
    (r'^facebook/ping/(.*)$', "mfabrik.facebookcampaignengine.views.campaign.ping"),
    
    # Not sure with this...
    (r'^facebook/(.*)$', "mfabrik.facebookcampaignengine.views.campaign.canvas"),
    
    ('^$', 'django.views.generic.simple.direct_to_template', {'template': 'home.html'}),
)
