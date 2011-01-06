"""

    Development settings for running FB app on local app engine dev server

"""

from mfabrik.facebookcampaignengine.base_settings import * 

# Our server HTTP endpoint

FACEBOOK_REAL_URL="http://mansikki.twinapex.fi:3334"

#: Facebook will render the result of this HTTP GET as an application canvas 
FACEBOOK_CALLBACK_PATH=FACEBOOK_REAL_URL + "/facebook/canvas/"