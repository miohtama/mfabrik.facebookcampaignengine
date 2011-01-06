from django.conf.urls.defaults import *

handler500 = 'djangotoolbox.errorviews.server_error'

urlpatterns = patterns('',
    ('^_ah/warmup$', 'djangoappengine.views.warmup'),
    
    (r'^facebook/callback(.*)$', "mfabrik.facebookcampaignengine.views.fbook.auth_complete"),    
    (r'^facebook/canvas/', "mfabrik.facebookcampaignengine.views.campaignengine.canvas"),
    (r'^facebook/ping/(.*)$', "mfabrik.facebookcampaignengine.views.campaignengine.ping"),
    ('^$', 'django.views.generic.simple.direct_to_template', {'template': 'home.html'}),
)
