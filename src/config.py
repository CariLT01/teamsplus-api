import datetime, platform

ABSOLUTE_PATH = "" # Absolute path to append during dev.
if platform.system() != 'Windows':
    ABSOLUTE_PATH = "/home/apiteamsplus/mysite/" # Absolute path to append during production
JWT_SECRET_KEY = "this key is very secret!hjahahadshsifhsdfhoidfhishoidpghiodsfhgipofoisdhboofgviofdhohdspisd" # Secret key for JWT
CAPTCHA_SECRET = 'ES_b1beac59470648df91ae9baf55bd58f3' # Secret key for hCaptcha
TOKEN_EXPIRY_TIME = datetime.timedelta(days=7) # JWT Token expire time
TOKEN_EXPIRY_INT = (60 * 60 * 24) * 7 # JWT Cookie Expire time integer in seconds
DOWNLOAD_URL = '/static/assets/teamsplus_versions/' # Download URL for TeamsPlus versions