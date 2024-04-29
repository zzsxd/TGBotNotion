import os
import platform
from flask import Flask, request, redirect
from config_parser import ConfigParser
app = Flask(__name__)

config_name = 'secrets.json'

@app.route('/')
def get_parameters():
    # Get the value of the 'code' parameter from the URL
    code = request.args.get('code')
    return redirect(f'{config.get_config()["tg_link"]}?start=code={code}')


if '__main__' == __name__:
    os_type = platform.system()
    work_dir = os.path.dirname(os.path.realpath(__file__))
    config = ConfigParser(f'{work_dir}/{config_name}', os_type)
    app.run(debug=False)
