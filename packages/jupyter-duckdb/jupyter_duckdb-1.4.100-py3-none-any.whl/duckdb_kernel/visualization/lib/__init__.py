import os

__CSS_INITIALIZED = False
__RA_INITIALIZED = False
__PLOTLY_INITIALIZED = False

__location = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))


def init_css() -> str:
    global __CSS_INITIALIZED

    if not __CSS_INITIALIZED:
        with open(os.path.join(__location, 'ra.css')) as ra_file:
            css = ra_file.read()
    else:
        css = ''

    __CSS_INITIALIZED = True
    return css


def init_ra() -> str:
    global __RA_INITIALIZED

    if not __RA_INITIALIZED:
        with open(os.path.join(__location, 'ra.js')) as ra_file:
            ra = ra_file.read()
    else:
        ra = ''

    __RA_INITIALIZED = True
    return ra


def init_plotly() -> str:
    global __PLOTLY_INITIALIZED

    if not __PLOTLY_INITIALIZED:
        with open(os.path.join(__location, 'plotly-3.0.1.min.js')) as plotly_file:
            plotly = plotly_file.read()
    else:
        plotly = ''

    __PLOTLY_INITIALIZED = True
    return plotly


__all__ = [
    'init_css',
    'init_ra',
    'init_plotly',
]
