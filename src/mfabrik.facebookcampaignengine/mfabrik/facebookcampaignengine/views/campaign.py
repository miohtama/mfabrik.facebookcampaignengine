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


# Python logging package logger object for our server

logger = logging.getLogger("Campaign Engine")


def need_user():
    """ Function decorator to require Facebook session and logged in user for the request handler. """

    def decorator(view):
        def need_user(request, *args, **kwargs):
            """ Make sure that the user is logged in to Facebook and we have a persistent User object.
            """
            if getattr(request, 'facebook', None) is None:
                fbook.add_instance(request)
            
            fb = request.facebook
            if not fb.check_session(request):
                return fb.redirect(fb.get_login_url(next=fb.get_app_url()))
            
            # Store the current internal user object in the request,
            # so it is easily accessible everywhere
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
                fbook.add_instance(request)
                
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
      
    params = {}     
    
    if hasattr(request, "pets_user"):
        params.update({
            "user" : request.pets_user,
            "own_pets" : resolve_pets(request, request.pets_user.pets.all()),
            # Add wizard status variable
            "wizard_step" : request.GET.get("step", None)
        })
    
    params.update(fbook.get_context_parameters())
    #logger.debug("Params:" + str(params))
    return params

@need_user()  
def canvas(request):
    """ Canvas is the page which is rendered when the user clicks your application in Facebook.

    This page is not the page displayed in the Facebook profile!
    
    We use the page to change the Facebook integration settings of the user and 
    display a preview of his/her profile block.    
    """
    
    logger.info("On Facebook canvas")
    
    
    
    request.facebook_user = get_or_create_user(request)
    
    params = get_context_parameters(request)
                   
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

