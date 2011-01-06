"""

    This is an entry to point to your Google App Engine + django-nonrel + buildout based application.
    It exposes Python eggs properly for App Engine to see.

"""

__author__ = "Mikko Ohtamaa <mikko@mfabrik.com>"
__copyright__ = "2010 mFabrik Research Oy"
__license__ = "BSD"

import os
import sys
import logging

logger = logging.getLogger("bootstrap")

# This path will be filled in by "flatten-eggs" part of buikdout
sys.path = [ os.path.join(os.path.dirname(__file__), "flattened-eggs") ] + sys.path

# Then we need this special trick because of bad packaging of djangoappengine
sys.path = [ os.path.join(os.path.dirname(__file__), "flattened-eggs", "djangoappengine") ] + sys.path

def enable_pdb():
    """
    Make import pdb ; pdb.set_trace() debugging possible
    """
    for attr in ('stdin', 'stdout', 'stderr'):
        setattr(sys, attr, getattr(sys, '__%s__' % attr))
 
def main():
    """
    After we have set up PYTHONPATH we can let djangoappengine to take over the request
    
    We need this irritating hooky wooky because Google App Engine does not properly support
    Python packaging and expects a flat directory structure only. 
    """
    
    logger.info("Starting with PYTHONPATH:" + str(sys.path))
    
    import django
    
    from djangoappengine.main.main import main as djangoappengine_main
    djangoappengine_main()
    
if __name__ == '__main__':
    main()
    
