from aip import AipSpeech
import os
from pydub import AudioSegment
file_name = "171125-210545.mp3"

abs_path = os.path.abspath(file_name)
#
# cmd = "ffmpeg -i \"{}\" -ar 16000 \"{}\"".format(abs_path, abs_path + '.wav')
# out = os.popen(cmd).read()
# print(out)
sound = AudioSegment.from_file(file_name)
sound.set_frame_rate(16000)
sound.export(file_name + '.wav', format="wav")
APP_ID = '10438301'
API_KEY = '6BNc10Gh9BiRdNSh7G5YXvSd'
SECRET_KEY = ' 6d7ab67d299b55aed465767c7c547a38'
aipSpeech = AipSpeech(APP_ID, API_KEY, SECRET_KEY)


def get_file_content(file_path):
    with open(file_path, 'rb') as fp:
        return fp.read()
print(aipSpeech.asr(get_file_content(file_name + '.wav'), 'wav', 16000, {
    'lan': 'zh',
}))