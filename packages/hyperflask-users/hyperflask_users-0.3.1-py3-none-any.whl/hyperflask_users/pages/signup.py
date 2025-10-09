from hyperflask import page, request, redirect, url_for, current_app, abort
from hyperflask.security import is_safe_redirect_url
from ..flow import signup
from ..captcha import validate_captcha_when_configured


if "signup" not in current_app.extensions['users'].allowed_flows and "password" not in current_app.extensions['users'].allowed_flows:
    if "connect" in current_app.extensions['users'].allowed_flows:
        page.redirect(url_for(".connect", next=request.args.get("next")))
    abort(404)


form = page.form()


@validate_captcha_when_configured
def post():
    if form.validate():
        try:
            signup(form.data)
            next = request.args.get("next")
            return redirect(next if next and is_safe_redirect_url(next) else current_app.extensions['users'].signup_default_redirect_url)
        except Exception as e:
            pass
