"""
    Facebook logic related HTTP views.

    This code uses contributions from:
        
        - http://www.lethain.com/entry/2007/nov/30/using-pyfacebook-without-facebook-middleware/
        
        
    Process:
    
        - Create Facebook account
        
        - Add Developer Facebook application
        
        - Request new application id
        
        - Fill in application info, with "Can your application be added on Facebook?" toggled
        
            - Maps URLS to Django views exported by your server
        
        - Add application to your profile
        
        - Test, test, code, test, code
        
        - Re-edit application information, submit it

"""
__author__ = "Mikko Ohtamaa <mikko@mfabrik.com>"
__docformat__ = 'epytext'
__copyright__ = "Copyright 2008-2010 mFabrik Research Oy"

import time
import logging
import os

# Django imports
from django import template
from django.shortcuts import render_to_response
from django.template.loader import render_to_string
from django.template import RequestContext
from django import forms
from django.http import HttpResponse, HttpResponseForbidden, HttpResponseServerError, HttpResponseRedirect

# Django-nonrel

from djangoappengine.utils import on_production_server 

# Local imports
from django.conf import settings

# Facebook Python API
from facebook.djangofb import Facebook
from facebook import FacebookError

from mfabrik.facebookcampaignengine.models import User

# Python logging package logger object for our server
logger = logging.getLogger("Facebook helpers")




def get_user(id):
    """ Return Facebook user object. """
    return User.objects.get(network = User.NETWORK_FACEBOOK, network_id = id)
    
def cache_facebook_instance(request):
    """ Adds request.facebook object. 
    
    @param request: HTTP request object acting as cache storage
    
    @return: Facebook object    
    """

    # if request already has a facebook instance attached, immediately return
    if getattr(request, 'facebook', None) is not None:
        return request
        
    # auth_token is other important possible param
    api_key = settings.FACEBOOK_API_KEY
    secret_key = settings.FACEBOOK_SECRET_KEY
    app_name = getattr(settings, 'FACEBOOK_APP_NAME', None)
    callback_path = getattr(settings, 'FACEBOOK_CALLBACK_PATH', None)
    internal = getattr(settings, 'FACEBOOK_INTERNAL', True)
    
    request.facebook = Facebook(
        api_key=api_key,
        secret_key=secret_key,
        app_name=app_name,
        callback_path=callback_path,
        internal=internal
        )
    
    return request.facebook

def get_permission_url():
    """
    http://www.facebook.com/connect/prompt_permissions.php?api_key=de33669a10a4219daecf0436ce829a2e&v=1.0&next=http://apps.facebook.com/myappname/granted/%3fxxRESULTTOKENxx&display=popup&ext_perm=read_stream,publish_stream,offline_access&enable_profile_selector=1
    """
    
    
    

def add_instance_outband_form(request):
    """ Create Facebook object for forms not submitted to the application canvas.
    
    Namely, file upload forms.
    
    http://wiki.developers.facebook.com/index.php/UsageNotes/Forms    
    """
    # if request already has a facebook instance attached, immediately return
    if getattr(request, 'facebook', None) is not None:
        return request
    
    # auth_token is other important possible param
    api_key = settings.FACEBOOK_API_KEY
    secret_key = settings.FACEBOOK_SECRET_KEY
    app_name = getattr(settings, 'FACEBOOK_APP_NAME', None)
    callback_path = getattr(settings, 'FACEBOOK_CALLBACK_PATH', None)
    internal = getattr(settings, 'FACEBOOK_INTERNAL', True)
        
    request.facebook = Facebook(
        api_key=api_key,
        secret_key=secret_key,
        app_name=app_name,
        callback_path=callback_path,
        internal=internal
        )
    
    return request.facebook

def login():
    """ Function decorator to require Facebook session and logged in user for the request handler. """

    def decorator(view):
        def require_login(request, *args, **kwargs):
            """ Make sure that the user is logged in to Facebook.
            
            If the user is not logged in to the Facebook, go to the 
            Facebook login page which will redirect to the application canvas page.    
            """
            if getattr(request, 'facebook', None) is None:
                add_instance(request)
            fb = request.facebook
            if not fb.check_session(request):
                return fb.redirect(fb.get_login_url(next=fb.get_app_url()))
            
            return view(request, *args, **kwargs)
                
        return require_login
            
    return decorator

@login()
def post_add(request):
    """ Post made by Facebook when the user adds this application to his/her profile.
    """    
                        
    # return to the canvas main page
    return request.facebook.redirect(settings.FACEBOOK_EXTERNAL_URL)

@login()
def post_remove(request):
    """ Called by Facebook when user removes the application from his/her profile.
    """
    remove_confirmation = request.POST["fb_sig_uninstall"]
    
    if remove_confirmation == "1":
        facebook_id = int(request.POST["fb_sig_user"])
        
        # Clean Facebook specific data from our servers
        try:
            entry = get_user(facebook_id)
        except User.DoesNotExist:
            return HttpResponseServerError("There was no Facebook binding for the facebook user id " + str(facebook_id))
        
        entry.delete()
        
    else:
        return HttpResponseServerError("Does not understand Facebook request")

def get_api(user=None):
    """ Return Facebook API object which can be used externally.
    
    The page does not need to be serverd in Facebook UI context.
    We store a session which never expires.
    
    @param user: Network User object.
    
    @return: Facebook instance
    """
    
    if "auth_token" in request.GET:
        
        # Try to establish a session with this auth_token
        # and if it fails, prompt user to login again
        facebook = Facebook(
            api_key=settings.FACEBOOK_API_KEY,
            secret_key=settings.FACEBOOK_SECRET_KEY,
            app_name=settings.FACEBOOK_APP_NAME,
            auth_token = request.GET["auth_token"],
            internal=False
        )
        
        # TODO: How we fail?
        
    else:
        
        facebook = Facebook(
            api_key=settings.FACEBOOK_API_KEY,
            secret_key=settings.FACEBOOK_SECRET_KEY,
            app_name=settings.FACEBOOK_APP_NAME,
            internal=False
        )
            
    return facebook

def has_valid_session(user):
    """ Return Facebook instance if we have a valid session. """

    facebook = get_api(user)        
        
    if facebook == None:
        return None
    
    try:
        result = facebook.users.getLoggedInUser()
    except FacebookError, e:
        logger.exception(e)
        return None
    
    #if facebook.session_key_expires != 0:
    #    logger.warn("Has expiring session key:" + str(facebook.session_key_expires))
        # We want permanent session and unfortunately
        # the user was too stopid to follow instructions
        # and check "Save session" checkbox
    #    return False
    
    return facebook
    

def get_user_from_request(request):
    """ Get/create persistent User object associated with the Facebook user.
    
    - Try look-up by Facebook UID. This will work even if our cookie is expired,
      but user is still logged in to facebook.
    
    @return: User object
    """
    
    facebook = request.facebook
    uid = facebook.uid
    
    # User account is already binded with the Facebook account
    try:
        entry = get_user(uid)
        return entry
    except User.DoesNotExist:
        return None

def refresh_user(request):        
    """ Always keep our auth_token up to date - user might have relogged.
    
    This information must be persistent so that we can post profile
    updates outside the web browser session.
    """
    fb_settings.auth_token = facebook.auth_token
    fb_settings.session_key = facebook.session_key    
    fb_settings.save()
    

def logout(request):
    """ Terminate user's Facebook session """
    
    user = request.user
    
    facebook = get_api(user)
    facebook.auth.createToken() # Invalidates the old session
    
    return HttpResponseRedirect("/" + user.username + "/facebook_info/")
            
    
def auth_complete(request, *args, **kwargs):
    """ Page on our site which gets redirect after Facebook completes the authorization.
    
    This is same as Facebook callback URL in the developer settings.
    """
    
    # Facebook redirected us back to this page after succesful authentication.
    auth_token = request.GET["auth_token"]
    
    logger.info("Authorizing Facebook session for token %s" % (auth_token))
    
    facebook = Facebook(
            api_key=settings.FACEBOOK_API_KEY,
            secret_key=settings.FACEBOOK_SECRET_KEY,
            auth_token = auth_token,       
            internal=False
        )
    
    # users.getLoggedInUser() requires a session key
    facebook.auth.getSession()
    

def generate_latest_static_media_timestamp():
    """ 
    Query all files in static and get the latest timestamp. 
    """
    static_path = os.path.join(os.path.dirname(__file__), "..", "static")
    
    latest_time = 0
    
    files = os.listdir(static_path)
    for f in files:
        t = os.path.getmtime(os.path.join(static_path, f))
        if t > latest_time:
            latest_time = t
            
    return latest_time

_latest_media_timestamp = None

def get_static_media_suffix():
    """
    Since Facebook never expires static content, we
    need to have a way to identify when static content has changed.
    
    We do this by suffixing all media URLs with a HTTP GET query parameter.
    there.
    """
    global _latest_media_timestamp
    
    # Look up for the timestamp only on the server start
    if not _latest_media_timestamp:
        _latest_media_timestamp = generate_latest_static_media_timestamp()
        
    return _latest_media_timestamp

def get_context_parameters():
    """
    Fill in parameters for Fae
    
    @return: Template context parameters for Facebook applications 
    
    @rtype: dict
    """
    return {
        "fb_application_id" : settings.FACEBOOK_APPLICATION_ID,
        "fb_external_url" : settings.FACEBOOK_EXTERNAL_URL,
        "fb_media_url_suffix" : get_static_media_suffix(),
        "fb_real_url" : settings.FACEBOOK_REAL_URL
    }
    
def redirect(url):
    """ Facebook canvas compatible redirect. """
    return HttpResponse('<fb:redirect url="%s" />' % (url, ))


class FacebookView(object):
    """
    Base class for Facebook canvas views.
    """
    
    
    def prepare_template_params(self):
        params = dict(current_user=self.current_user,
                    facebook_app_id=settings.FACEBOOK_APP_ID)
    
    @property
    def current_user(self):
        
        if not hasattr(self, "_current_user"):
            self._current_user = None
            cookie = facebook.get_user_from_cookie(
                self.request.cookies, FACEBOOK_APP_ID, FACEBOOK_APP_SECRET)
            if cookie:
                # Store a local instance of the user data so we don't need
                # a round-trip to Facebook on every request
                user = User.get_by_key_name(cookie["uid"])
                if not user:
                    graph = facebook.GraphAPI(cookie["access_token"])
                    profile = graph.get_object("me")
                    user = User(key_name=str(profile["id"]),
                                id=str(profile["id"]),
                                name=profile["name"],
                                profile_url=profile["link"],
                                access_token=cookie["access_token"])
                    user.put()
                elif user.access_token != cookie["access_token"]:
                    user.access_token = cookie["access_token"]
                    user.put()
                self._current_user = user
        return self._current_user

    