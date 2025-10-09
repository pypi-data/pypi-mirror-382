from hyperflask import page, request, redirect, url_for, current_app, session, abort
from hyperflask.security import is_safe_redirect_url
from .. import UserModel
from ..flow import login, send_login_link
from ..captcha import validate_captcha_when_configured


if "login" not in current_app.extensions['users'].allowed_flows and "password" not in current_app.extensions['users'].allowed_flows:
    if "connect" in current_app.extensions['users'].allowed_flows:
        page.redirect(url_for(".connect", next=request.args.get("next")))
    abort(404)


form = page.form()


@validate_captcha_when_configured
def post():
    if form.validate():
        if "username_or_email" in form:
            q = UserModel.c.username == form.username_or_email.data | UserModel.c.email == form.username_or_email.data
        elif "username" in form:
            q = UserModel.c.username == form.username.data
        else:
            q = UserModel.c.email == form.email.data
        user = UserModel.find_one(q)
        remember = request.form.get("remember") == "1"
        if user:
            if "password" not in form:
                session['login_user'] = user.get_id()
                session['login_code'] = send_login_link(user)
                return redirect(url_for(".login_link", next=request.args.get("next")))
            try:
                login(user, form.password.data, remember=remember)
                next = request.args.get("next")
                return redirect(next if next and is_safe_redirect_url(next) else current_app.extensions['users'].login_redirect_url)
            except:
                pass
