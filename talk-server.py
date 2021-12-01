import flask
from flask import make_response, request
import urllib
import subprocess
import uuid
import os
import platform
import wave
import audioop
import argparse


parser = argparse.ArgumentParser('basic tts server')
parser.add_argument('-e','--engine',type=str,default='mimic',dest='engine')
args=parser.parse_args()

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
            os.rename(outfile,wavfile)
        return wavfile
    return None


def say_dectalk(text):
    fn = str(uuid.uuid1()) + '.wav'
    path = os.path.join(dectalkdir,fn)
    cmd = dectalkcmd + ['-w', fn, text]
    print(cmd)

    #os.environ['DISPLAY']=':0.0'   
    output = subprocess.check_output(cmd,stderr=subprocess.STDOUT,cwd = dectalk)
    print(output)
    return to16khz(path)


def say_mimic(text):
    fn = str(uuid.uuid1()) + '.wav'
    path = os.path.join(dir,fn)
    cmd = mimiccmd + ['-t', text, '-o', path,'-psdur']
    #cmd = ['mimic', '-t', text, '-o', path]

    print('cmd=',cmd)
    output = subprocess.check_output(cmd,stderr=subprocess.STDOUT)
    print(output)
    return to16khz(path)


@app.route('/')
def home():
    return '<h1>TTS API</h1><p>example command line usage:</p><pre>curl \"{}/say?text=hi+my+name+is+steven\" --output out.wav</pre>'.format(request.host)



@app.route('/say')
def say():
    requrl = request.full_path
    if requrl.endswith('.wav'):
        req = requrl[:-4]
        res = urllib.parse.urlparse(req)
        pq = urllib.parse.parse_qs(res.query)
        text = pq['text'][0]
        # engine = pq['engine']
        
    else:
        text = '"{}"'.format(request.args['text'])

    try:
        path = say_mimic(text)
        #path = say_dectalk(text)
    except Exception as e:
        print(str(e))
        return make_response('say error:' + str(e),418)

    
    with open(path,'rb') as f:
        response = make_response(f.read())
        response.headers.set('Content-Type', 'audio/wav')
        os.remove(path)
        return response

    
dir = os.path.dirname(os.path.realpath(__file__))
'''
ttsengine = {
    'mimic':{
        'cmd': {
            'Linux': [os.path.join(dir,'bin','mimic','linux','mimic')],
            'Darwin': [os.path.join(dir,'bin','mimic','macos','mimic')]
        }
    },
    'dectalk':{
        'dir': os.path.join(dir,'dectalk')
        'cmd': {
            'Linux': ['wine','say.exe'],
            'Windows': ['say.exe']
        }
    }
}    
'''
if platform.system()=='Linux':
    dectalkdir = os.path.join(dir,'dectalk')
    dectalkcmd = ['wine','say.exe']
    mimiccmd = [os.path.join(dir,'bin','mimic','linux','mimic')]
elif platform.system()=='Darwin':
    dectalkdir = ''
    dectalkcmd = ''
    mimiccmd = [os.path.join(dir,'bin','mimic','macos','mimic')]

else:
    dectalkdir = os.path.join(dir,'dectalk')
    dectalkcmd = ['say.exe']
    mimiccmd = ''

app.run(host='0.0.0.0')
