# riffusionDJ
Multichannel Looper/Feedback System for Riffusion (with Automatic1111) made for live performance
- Record or load audio
- Resize loaded files (great for drum loops) or randomly crop loaded files
- Any # of prompts, any # of channels
- Max MSP looper patch included for playing back generated samples

![2924553387_Photo of a Robot DJ at a rave Face, human_xl-beta-v2-2-2](https://user-images.githubusercontent.com/29033313/228206617-fb12c9cc-9f37-41f5-af92-b3c62273778e.png)

https://user-images.githubusercontent.com/29033313/229276109-077edfc5-1d2a-47b6-9972-65374b12bb1f.mp4

https://user-images.githubusercontent.com/29033313/228204558-729204e7-7582-4ed7-9b58-8b1cd17262d6.mp4

https://user-images.githubusercontent.com/29033313/228205138-db122bfd-11b9-4176-b25b-c9402cd9d86d.mp4

# Dependencies
1. Install the Riffusion Github if you haven't: https://github.com/riffusion/riffusion
2. ```pip install scipy PIL sounddevice```
3. (IF NOT USING GOOGLE COLAB) Install Automatic1111: https://github.com/AUTOMATIC1111/stable-diffusion-webui

# Usage
Some examples:

```python dj.py -p "violin" "opera singer" "funky"``` in a loop, record the user, uses prompts in order, saves to 3 channels (1.wav through 3.wav)

```python dj.py -p "violin solo" -c 5``` in a loop, record the user, uses "violin solo" as prompt, saves to 5 channels (1.wav through 5.wav)

```python dj.py -p "EDM techno house" -S 0.4 -c 2 -n 2 -l ~/Desktop/break.wav --resize``` uses loaded file, uses "EDM techno house" as prompt, sets denoising strength to 0.4, saves to 2 channels (1.wav through 2.wav),  quits after 2 iterations, resize the spectrogram instead of cropping.

```python dj.py -p "opera singer" "orchestra" -c 4 -l ~/Desktop/raga.wav``` in a loop, uses loaded file, uses prompts in order, saves to 4 channels (1.wav through 4.wav), randomly crops input spectrogram each iteration

All options:
```optional arguments:
  -h, --help            show this help message and exit
  -p PROMPTS [PROMPTS ...], --prompts PROMPTS [PROMPTS ...]
                        specify prompts to use in quotes seperated by spaces
  -s, --shuffle         shuffle prompt order
  -r, --reverse         reverse samples pre-riffusion
  -C, --clear           delete previously generated files
  -S STRENGTH, --strength STRENGTH
                        denoising strength (default: 0.5)
  -cfg CFG, --cfg CFG   CFG scale (default: 7.5)
  -st STEPS, --steps STEPS
                        steps count (default: 50)
  -H HOST, --host HOST  specify Automatic1111 web host (default:
                        http://127.0.0.1:7860)
  -a AUTH, --auth AUTH  specify "username:password" if using basic http
                        authentication
  -l LOAD, --load LOAD  load an audio file instead of recording (specify path
                        in quotes if there's spaces in it)
  -rs, --resize         resize spectrogram instead of randomly cropping it
                        (only applies to loaded files)
  -rl, --reload         use previously generated spectrogram (ignores loaded
                        file/record mode)
  -c CHANNELS, --channels CHANNELS
                        number of wavs to generate, ex: 3 would cycle from
                        1.wav to 3.wav (default: length of prompt list)
  -i INDEX, --index INDEX
                        set starting index, ex: -i 3 -c 2 would cycle from
                        3.wav to 4.wav (default: 1)
  -t THREAD, --thread THREAD
                        thread # identifier, meant for running multiple
                        instances of this script (default: 0)
  -n NUM, --num NUM     number of iterations before quitting (default:
                        infinite)
