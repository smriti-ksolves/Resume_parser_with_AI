from app.app import flask_app
import os
from app.api.routes import api_routes
from flask_cors import CORS

flask_app.register_blueprint(api_routes)
CORS(flask_app, supports_credentials=False)
host_ip, port_ip = os.environ.get("HOST_NAME", '0.0.0.0'), os.environ.get("PORT", 6543)

if __name__ == '__main__':
    flask_app.run(host='0.0.0.0', port=int(port_ip))