from hyperflask import redirect, url_for, current_app
from ..flow import logout


def get():
    logout()
    return redirect(current_app.extensions['users'].logout_redirect_url)
