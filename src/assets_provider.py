import os
from flask import send_from_directory, abort, current_app
from typing import cast

def provide_assets(path):
    app = current_app
    static_path = os.path.join(cast(str, app.static_folder), path)
    if os.path.isfile(static_path):
        return send_from_directory(cast(str, app.static_folder), path)
    else:
        # Optional: redirect to 404 page or return 404
        return abort(404)