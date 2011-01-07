import time
import datetime

from django.db import models
from django.contrib import admin
from django.conf import settings

class User(models.Model):    
    """ Social network user.
    
    Store the data of a social network user accessing the site, 
    including tokens needed to do push requests to the social network.
    
    This model also serves as a key to our internally stored data e.g.
    answers given by a user.
    """
    
    class Meta:        
        unique_together = (('network','network_id'),)
        app_label = 'facebookcampaignengine'
    
    NETWORK_FACEBOOK=0
    
    #: Social network id hosting this user
    network = models.IntegerField()
    
    #: User id in the social network
    network_id = models.CharField(max_length=256)

    #: Active Facebook auth token we can use to update the user's profile - needed only for outside browser sessions
    auth_token = models.CharField(max_length=256, null=True)
    
    #: Active Facebook session id which we can use to update the user's profile  - needed only for outside browser sessions
    session_key = models.CharField(max_length=256, null=True)
        
#admin.site.register(User)
