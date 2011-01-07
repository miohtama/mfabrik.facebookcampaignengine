"""

    Facebook campaign engine related HTTP views in Facebook.
 
"""


__author__ = "Mikko Ohtamaa <mikko@mfabrik.com>"
__docformat__ = 'epytext'
__copyright__ = "Copyright 2008-2010 mFabrik Research Oy"

import logging
import urllib

# Django imports
from django import template
from django.shortcuts import render_to_response
from django.template.loader import render_to_string
from django.template import RequestContext
from django.http import HttpResponse, HttpResponseForbidden, HttpResponseServerError, HttpResponseRedirect
from django.utils import simplejson

# Local imports
from django.conf import settings

# Facebook Python API
from facebook.djangofb import Facebook
from facebook import FacebookError

import fbook
from models import User

# Python logging package logger object for our server

logger = logging.getLogger("Campaign Engine")

def get_or_create_user(request):
    """ Create a persistent user entry of this Facebook user to our database """
    
    # Check if we have cached FB user available
    user = getattr(request, "facebook_user", None)
    if user:
        return user
    
    facebook = request.facebook
    uid = facebook.uid
    
    # User account is already binded with the Facebook account
    try:
        entry = fbook.get_user(uid)
        return entry
    except User.DoesNotExist:
        pass
    
    # Lazily create the user object
    uid = facebook.users.getLoggedInUser()
    logger.info("Adding application for uid:" + str(uid))    
    request.pets_user = User.objects.create(network=User.NETWORK_FACEBOOK, network_id=uid)
    
    return user

def need_user():
    """ Function decorator to require Facebook session and logged in user for the request handler. 
    
    Facebook apps can contain pages for anonymous and logged in users.
    This decorator forces the pages we serve to be for logged in users only.
    """

    def decorator(view):
        def need_user(request, *args, **kwargs):
            """ Make sure that the user is logged in to Facebook and we have a persistent User object.
            """
            if getattr(request, 'facebook', None) is None:
                fbook.cache_facebook_instance(request)
            
            fb = request.facebook
            
            # Checking if the user has logged into faecbook
            if not fb.check_session(request):
                logger.info("User was not logged into facebook")
                return fb.redirect(fb.get_login_url(next=fb.get_app_url()))
            
            # Store the current internal user object in the request,
            # so it is easily accessible everywhere
            logger.debug("Creating local user object")
            request.facebook_user = get_or_create_user(request)
            
            return view(request, *args, **kwargs)
                
        return need_user
            
    return decorator


def need_user_outband_form_post():
    """ Set-up Facebook object when the HTTP request comes to our servers directly as HTTP POST. """

    def decorator(view):
        def need_user(request, *args, **kwargs):
            """ Make sure that the user is logged in to Facebook and we have a persistent User object.
            """
            
            if getattr(request, 'facebook', None) is None:
                fbook.cache_facebook_instance(request)
                
            fb = request.facebook
            if not fb.check_session(request):
                return fb.redirect(fb.get_login_url(next=fb.get_app_url()))
            
            # Store the current internal user object in the request,
            # so it is easily accessible everywhere
            request.pets_user = get_or_create_user(request)
            
            return view(request, *args, **kwargs)
                
        return need_user
            
    return decorator


def get_context_parameters(request):
    """
    Our helper function for filling in template vars.
    """  
    params = {}     
    
    if hasattr(request, "pets_user"):
        params.update({
            "user" : request.facebook_user,
        })
    

    params.update(fbook.get_context_parameters())
    
    return params

@need_user()  
def canvas(request, *args, **kwargs):
    """ Canvas is the page which is rendered when the user clicks your application in Facebook
    (enters apps.facebook.com URL)=
    
    We use the page to change the Facebook integration settings of the user and 
    display a preview of his/her profile block.    
    """
    
    logger.info("On Facebook canvas " + str(args) + " " + str(kwargs))
    
    request.facebook_user = get_or_create_user(request)
    
    params = get_context_parameters(request)
    
    # Check whether required extened permissions are in place
    # This is little bit expensive, as two remote calls ensures
    # http://developers.facebook.com/docs/reference/rest/users.hasAppPermission
    logger.debug("Got:" + str(request.facebook.users.hasAppPermission("email")))
    params["has_required_permissions"] =  (request.facebook.users.hasAppPermission("email") == 1 and 
                                           request.facebook.users.hasAppPermission("publish_stream") == 1)
    
    logger.debug("Rendering canvas:" + str(params))
    
    return render_to_response('canvas.fbml', 
                              params,
                              context_instance=RequestContext(request)
                              )

  
@need_user()
def publish_facebook_story(request, one_line_story_templates, template_data):
  """ Publish action in user's feed. Only has adding new pet for now. 
  
  @param one_line_story_templates: List of different tempaltes
  
  @param template_data: dict
  
  """
  facebook = request.facebook

  one_line_story_templates = [
      '{*actor*} added a new pet {*category*} called {*name*}',
      '{*actor*} has a new pet called {*name*}',
      '{*actor*} has a new pet!'
    ]
  
  template_bundle_id = facebook.feed.registerTemplateBundle(simplejson.dumps(one_line_story_templates))
  
  try:
      facebook.feed.publishUserAction(template_bundle_id=template_bundle_id, template_data=template_data)
  except FacebookError, e:
      # There's no need to tell the user.
      logger.debug("Could not publish news item:%r" % e)

@need_user()
def ping(request, *args, **kwargs):    
    """ Ping the application """
    logger.info("Responding to a ping request")
    facebook = request.facebook
    logger.info(facebook.photos.getAlbums())
    return HttpResponse("OK")


def callback(request, *args, **kwargs):
    """ Handle the application callback url.
    
    Since this URL is referred both
    
        - Facebook default canvas viewer
        
        - Target as a external web site login 
        
    We need to have some magic here.
    """
        
    return canvas(request)

