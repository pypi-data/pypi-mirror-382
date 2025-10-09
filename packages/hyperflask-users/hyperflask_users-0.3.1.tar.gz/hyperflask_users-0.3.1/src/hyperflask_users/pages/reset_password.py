from hyperflask import redirect, request, page, current_app, abort
from hyperflask.security import is_safe_redirect_url
from .. import UserModel
from ..flow import reset_password
from ..captcha import validate_captcha_when_configured


if "password" not in current_app.extensions['users'].allowed_flows and "password_reset" not in current_app.extensions['users'].allowed_flows:
    abort(404)


form = page.form()
user = UserModel.from_token_or_404(request.args["token"], max_age=current_app.extensions['users'].token_max_age)


@validate_captcha_when_configured
def post():
    if form.validate():
        try:
            reset_password(user, form.password.data)
            next = request.args.get("next", current_app.extensions['users'].reset_password_redirect_url)
            if next and is_safe_redirect_url(next):
                return redirect(next)
        except:
            pass
