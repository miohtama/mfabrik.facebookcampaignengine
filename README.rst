=================================================
 Facebook campaign Engine for Google App Engine 
=================================================

.. contents ::

Introduction
============

Create Facebook campaigns for questionaries, competitions and others easily.

Development process
===================

- Create Facebook account

- Add Developer Facebook application

- Request new application id

- Fill in application info, with "Can your application be added on Facebook?" toggled

    - Maps URLS to Django views exported by your server

- Add application to your profile

- Test, test, code, test, code

- Re-edit application information, submit it

Settings
========

There are three different Django settings files

* base_settings.py - settings used on every computer

* dev_settings.py - settings used when developing locally with dev server

* production_settings.py - settings used when running on Google App Engine

base_settings.py contains various Facebook related settings. You
get them when you register your application with Facebook (see below).

Develop and debug
=================

You need to register your application with Facebook (see below).

Use SSH port-forward from a public server to test the Facebook application running on a development 
server on your local computer.

This will command will build tunnel from outfacing port 3334 to your local Google App Engine port 8000:: 

    ssh -gNR 3334:localhost:8000 youruser@yourserver.com
    
Make sure dev server is on. Test your SSH tunnel by pointing your browser to URL::

    http://yourserver.com:3334/facebook/canvas/
    
Here is an example how to set Facebook app settings for testing::

* Canvas Page: http://apps.facebook.com/mikkotestcampaign You can access your FB app in this address)

* Canvas URL: http://mansikki.twinapex.fi:3334/facebook/ 

* Canvas type: FBML

* OAuth 2.0 for Canvas: Disabled (Pyfacebook does not support this... this is signed_request payload in HTTP POST request)


Canvas URL is a HTTP address for server-to-server traffic. Facebook connects this URL, reads FBML pages, converts them to HTML
and servers the user. Publicly canvas URL can be reached from Canvas page address. 
In our Django application, we simply map all these urls to /facebook/ URI space.

E.g.

    apps.facebook.com/yourapp/ping
    
Becomes internally

    http://localhost:8000/facebook/ping

For development, it is a best practice to SSH tunnel Canvas URL to your local computer.

.. note ::

    The benefit of using SSH tunnel over your dynamic public IP is that you don't need to fiddle with Facebook 
    app settings every time your dynamic IP changes.

Errors
++++++

Facebook canvas will serve a blank page in the case App Engine gives you an error response
You need to catch errors from the dev_server terminal output. This will be also the case if your
SSH tunnel stops responding.

Deploy
======

Deploy the application on Google App Engine.

Registering with Facebook
-------------------------

Create a test Facebook account. Register yourself to Facebook *Developer* application (just type Developer in Facebook search box).
The Facebook account must be verified with a credit card or a mobile phone number.

Facebook assets
---------------

Facebook app needs 

* Language

* Icon: Appears next to your app name throughout Facebook (16x16)

* Logo: Appears in authorization dialogs, search results, and the app directory (75x75)

* Privacy Policy URL

* Terms of Service URL

Notes
=====

Workflow
--------

* If the user is accessing the web site directly, and not through public apps.facebook.com URL, the user is directed to the public URL

* If the user has not logged into Facebook, Facebook will prompt for it

* Facebook gives "Add application dialog"

* Extented permissions are prompted for the application

* Questionnaire page is shown

* 

Author
======

* Contact mikko at mfabrik dot com

* `Follow in Twitter <http://twitter.com/moo9000>`_
