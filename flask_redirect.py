from flask import Flask, request, redirect
app = Flask(__name__)


@app.route('/')
def get_parameters():
    # Get the value of the 'code' parameter from the URL
    code = request.args.get('code')
    return redirect(f'https://t.me/nbnotesbot?start=code={code}')


if '__main__' == __name__:
    app.run(debug=False)
