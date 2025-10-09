from blinker import signal
from flask_login import user_logged_in, user_logged_out


user_before_signup = signal("user-before-signup")
user_signed_up = signal("user-signup")
user_email_validated = signal("user-email-validated")
