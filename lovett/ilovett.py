"""Functions for use in the IPython notebook interface."""

from IPython.display import display, HTML
import pkg_resources


def ilovett():
    return display(HTML("""<script>$("head").append($("<style type='text/css' />").text('%s'));</script>""" %
                        open(pkg_resources.resource_filename("lovett", "css/ipython.css")).read().replace("\n","\\n")))


# TODO: a widget that allows the editing of a single tree annotald-style in
# the ipython window.  (Or pops up another window to do it?).  Will allow
# R-like fix() function
