import datetime, platform
import site_secrets

ABSOLUTE_PATH = "" # Absolute path to append during dev.
if platform.system() != 'Windows':
    ABSOLUTE_PATH = "/home/apiteamsplus/mysite/" # Absolute path to append during production
JWT_SECRET_KEY = site_secrets.JWT_SECRET # Secret key for JWT
CAPTCHA_SECRET = site_secrets.CAPTCHA_SECRET # Secret key for hCaptcha
TOKEN_EXPIRY_TIME = datetime.timedelta(days=7) # JWT Token expire time
TOKEN_EXPIRY_INT = (60 * 60 * 24) * 7 # JWT Cookie Expire time integer in seconds
DOWNLOAD_URL = '/static/assets/teamsplus_versions/' # Download URL for TeamsPlus versions