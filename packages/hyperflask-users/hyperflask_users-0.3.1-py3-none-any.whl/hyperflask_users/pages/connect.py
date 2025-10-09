from hyperflask import page, request, redirect, url_for, session, current_app, abort
from hyperflask.security import is_safe_redirect_url
from .. import UserModel
from ..flow import signup, send_login_link
from ..captcha import validate_captcha_when_configured


if "connect" not in current_app.extensions['users'].allowed_flows:
    if "login" in current_app.extensions['users'].allowed_flows or "password" in current_app.extensions['users'].allowed_flows:
        page.redirect(url_for(".login", next=request.args.get("next")))
    abort(404)


form = page.form()
next = request.args.get("next")


@validate_captcha_when_configured
def post():
    if form.validate():
        user = UserModel.find_one(email=form.email.data)
        if user:
            session['login_user'] = user.get_id()
            session['login_code'] = send_login_link(user)
            return redirect(url_for(".login_link", next=next))
        else:
            signup(form.data)
            return redirect(next if next and is_safe_redirect_url(next) else current_app.extensions['users'].signup_default_redirect_url)
