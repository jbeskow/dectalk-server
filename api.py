import flask
from flask import make_response, request
import subprocess
import uuid
import os
import wave
import audioop

app = flask.Flask(__name__)
app.config['DEBUG'] = False

def to16khz(wavfile):
    outfile = wavfile.replace('.wav','_16.wav')
    with wave.open(wavfile,'rb') as wf1:
        p1 = wf1.getparams()
        if p1.framerate != 16000:
            data1 = wf1.readframes(p1.nframes)
            data2,state = audioop.ratecv(data1,p1.sampwidth,p1.nchannels,p1.framerate,16000,None)
            with wave.open(outfile,'wb') as wf2:
                wf2.setsampwidth(p1.sampwidth)
                wf2.setnchannels(p1.nchannels)
                wf2.setframerate(16000)
                wf2.writeframes(data2)
                return outfile
    return None

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
        os.environ['DISPLAY']=':0.0'
        subprocess.check_output(['wine', 'say.exe', '-w', fn, text],cwd = dectalk)
        path2 = to16khz(path)
        
        with open(path2,'rb') as f:
            response = make_response(f.read())
            response.headers.set('Content-Type', 'audio/wav')
            os.remove(path)
            os.remove(path2)
            return response
        
    except subprocess.CalledProcessError as sayexc:
        return('say error:', sayexc.output)

dir = os.path.dirname(os.path.realpath(__file__))
dectalk = os.path.join(dir,'dectalk')
app.run(host='0.0.0.0')
