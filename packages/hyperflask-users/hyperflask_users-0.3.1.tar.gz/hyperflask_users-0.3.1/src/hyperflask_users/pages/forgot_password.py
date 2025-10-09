from hyperflask import page, current_app, flash, abort
from .. import UserModel
from ..flow import send_reset_password_email
from ..captcha import validate_captcha_when_configured


if "password" not in current_app.extensions['users'].allowed_flows and "password_reset" not in current_app.extensions['users'].allowed_flows:
    abort(404)


form = page.form()


@validate_captcha_when_configured
def post():
    if form.validate():
        user = UserModel.find_one_or_404(email=form.email.data)
        send_reset_password_email(user)
        flash_msg = current_app.extensions['users'].forgot_password_flash_message
        if flash_msg:
            flash(flash_msg)
