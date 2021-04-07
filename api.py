import flask
from flask import make_response, request
import subprocess
import uuid
import os

app = flask.Flask(__name__)
app.config['DEBUG'] = False

@app.route('/')
def home():
    return '<h1>DECTALK API</h1><p>example command line usage:</p><pre>curl {}/say?text=hi+my+name+is+steven --output out.wav</pre>'.format(request.host)

@app.route('/say')
def say():
    if not 'text' in request.args.keys():
        return ''
    text = '"' + request.args['text'] + '"'
    fn = str(uuid.uuid1()) + '.wav'
    path = os.path.join(dectalk,fn)
    try:
        subprocess.check_output(['wine', 'say.exe', '-w', fn, text],cwd = dectalk)
        with open(path,'rb') as f:
            response = make_response(f.read())
            response.headers.set('Content-Type', 'audio/wav')
            os.remove(path)
            return response
        
    except subprocess.CalledProcessError as sayexc:                                                                   return('say error:', sayexc.output)

dir = os.path.dirname(os.path.realpath(__file__))
dectalk = os.path.join(dir,'dectalk')
app.run(host='0.0.0.0')
