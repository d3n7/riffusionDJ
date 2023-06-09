#!/usr/bin/env python
import io, os, base64, requests, json, random, argparse, shutil
import sounddevice as sd
from scipy.io import wavfile
from PIL import Image, ImageOps

#environment variables
path = os.path.realpath(os.path.dirname(__file__))
inPath = os.path.join(path,"input")
outPath = os.path.join(path,"output")
audioPath = os.path.join(inPath,"input.wav")
cropPath = os.path.join(inPath,"cropped.png")
specIn = os.path.join(inPath,"input.png")
specOut = os.path.join(outPath,"output.png")

#parse arguments
parser = argparse.ArgumentParser()
parser.add_argument("-p", "--prompts", help="specify prompts to use in quotes seperated by spaces", nargs="+", default=["opera singer","piano","violin","electronic drums","synthesizer"])
parser.add_argument("-s", "--shuffle", help="shuffle prompt order", action="store_true")
parser.add_argument("-r", "--reverse", help="reverse samples pre-riffusion", action="store_true")
parser.add_argument("-C", "--clear", help="delete previously generated files", action="store_true")
parser.add_argument("-S", "--strength", help="denoising strength (default: 0.5)", type=float, default=0.5)
parser.add_argument("-cfg", "--cfg", help="CFG scale (default: 7.5)", type=float, default=7.5)
parser.add_argument("-st", "--steps", help="steps count (default: 50)", type=int, default=50)
parser.add_argument("-H", "--host", help="specify Automatic1111 web host (default: http://127.0.0.1:7860)", default="http://127.0.0.1:7860")
parser.add_argument("-a", "--auth", help="specify \"username:password\" if using basic http authentication")
parser.add_argument("-l", "--load", help="load an audio file instead of recording (specify path in quotes if there's spaces in it)")
parser.add_argument("-rs", "--resize", help="resize spectrogram instead of randomly cropping it (only applies to loaded files)", action="store_true")
parser.add_argument("-rl", "--reload", help="use previously generated spectrogram (ignores loaded file/record mode)", action="store_true")
parser.add_argument("-c", "--channels", help="number of wavs to generate, ex: 3 would cycle from 1.wav to 3.wav (default: length of prompt list)", type=int)
parser.add_argument("-i", "--index", help="set starting index, ex: -i 3 -c 2 would cycle from 3.wav to 4.wav (default: 1)", type=int, default=1)
parser.add_argument("-t", "--thread", help="thread # identifier, meant for running multiple instances of this script (default: 0)", type=int, default=0)
parser.add_argument("-n", "--num", help="number of iterations before quitting (default: infinite)", type=int, default=0)
args = parser.parse_args()

#store args, setup vars
reverse = args.reverse
prompts = args.prompts
strength = args.strength
cfg = args.cfg
steps = args.steps
resize = args.resize
channels = args.channels if args.channels else len(prompts)
index = args.index
num = args.num
url = args.host+"sdapi/v1/img2img" if args.host.endswith("/") else args.host+"/sdapi/v1/img2img"
creds = args.auth.split(":") if args.auth else "  "
if args.clear:
    for i in [inPath, outPath]:
        for j in os.listdir(i):
            if j.endswith(".wav") or j.endswith(".png"):
                os.remove(os.path.join(i, j))
thread = args.thread
if thread != 0:
    audioPath = audioPath[:-4]+str(thread)+audioPath[-4:]
    cropPath = cropPath[:-4]+str(thread)+cropPath[-4:]
    specIn = specIn[:-4]+str(thread)+specIn[-4:]
    specOut = specOut[:-4]+str(thread)+specOut[-4:]
reload = args.reload if os.path.isfile(specIn) else False
loadFile = None if reload else args.load
if loadFile:
    shutil.copy(loadFile, audioPath)
if args.shuffle:
    random.shuffle(prompts) #randomize the prompt order

#main loop
counter = channels
while 1:
    for p in prompts:
        #record input audio (if it's not a loadFile or reload)
        if not (loadFile or reload):
            freq = 44100
            duration = 5.119
            print("\n[*] Recording audio...\n")
            recording = sd.rec(int(duration * freq),samplerate=freq, channels=1)
            sd.wait()
            wavfile.write(audioPath, freq, recording)

        #convert audio to input spectrogram (if it's a loaded file only do it on the first run, or never if reload, otherwise everytime)
        if (counter==channels or (not loadFile)) and (not reload):
            print("\n[*] Making input spectrogram\n")
            os.system("python -m riffusion.cli audio-to-image -a \"{}\" -i \"{}\" >/dev/null 2>&1".format(audioPath, specIn))

        #random crop (only if it's a reload or loaded file, and not if resize)
        imgPath = specIn
        if (loadFile or reload) and (not resize):
            cropped = Image.open(specIn)
            width, height = cropped.size
            if width>512:
                randX = random.randint(0,width-512)
                cropped = cropped.crop((randX, 0, randX+512, height))
                cropped.save(cropPath, "PNG")
                imgPath = cropPath

        #reverse it (if it's a loaded file or reload and its being resized, only on reverse spec once, otherwise every time)
        if reverse:
            if counter==channels or (not ((loadFile or reload) and resize)):
                reversed = ImageOps.mirror(Image.open(imgPath))
                reversed.save(imgPath,"PNG")

        #make post request to Automatic1111 API
        encodedI = base64.b64encode(open(imgPath, "rb").read())
        payload = {
            "init_images": ["data:image/png;base64,"+encodedI.decode('utf-8')+"="],
            "denoising_strength": strength,
            "cfg_scale": cfg,
            "resize_mode": 0,
            "prompt": p,
            "steps": steps
        }
        print("\n[*] Sending to Automatic1111 with prompt: {}\n".format(p))
        r = requests.post(url, json=payload, auth=(creds[0], creds[1])) if args.auth else requests.post(url, json=payload)
        r = r.json()
        for i in r['images']:
            image = Image.open(io.BytesIO(base64.b64decode(i.split(",",1)[0])))
            image.save(specOut,"PNG")
        print("\n[*] Received spectrogram\n")

        #turn output spectrogram into audio
        wavcount = str(counter%channels+index)
        os.system("python -m riffusion.cli image-to-audio  -i \"{}\" -a \"{}\" >/dev/null 2>&1".format(specOut, os.path.join(outPath,wavcount+".wav")))
        print("\n[*] Saved audio as {}\n".format(wavcount+".wav"))

        counter += 1
        if num:
            if counter >= channels+num:
                print("\n[*] Quitting after {} iters\n".format(num))
                exit()
