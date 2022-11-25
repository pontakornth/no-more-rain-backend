import sys
import connexion

sys.path.append('stub')
from stub.swagger_server import encoder
from flask_cors import CORS

def main():
    app = connexion.App(__name__, specification_dir='./openapi')

    # All domain, all routes.
    # Please don't use this on production.
    # This is a temporary solution so it's fine.
    CORS(app.app)
    app.app.json_encoder = encoder.JSONEncoder
    app.add_api('no-more-rain.yaml',
                arguments={'title': 'No more rain API'},
                pythonic_params=True)

    app.run(port=8080, debug=True)

if __name__ == '__main__':
    main()
