from modules.__templates__ import Interactive
from modules.__secrets__ import facepp_keys, facepp_secrets
import itchat
import requests
import multiprocessing
import traceback
import io, time
from PIL import Image, ImageDraw, ImageFont


class FaceAnalysis(Interactive):
    __author__ = "Hanzhi Zhou"
    alias = "face"
    title = "Face++ Face Analysis Integration"
    parameters = "[attr1] [attr2] [...]"
    attributes = ['gender', 'age', 'smiling', 'headpose', 'eyestatus', 'emotion', 'ethnicity',
                  'beauty', 'mouthstatus', 'eyegaze', 'skinstatus']
    attributes_map = {
        'gender': 'gender', 'age': 'age', 'smiling': 'smile', 'headpose': 'headpose',
        'eyestatus': 'eyestatus', 'emotion': 'emotion', 'ethnicity': 'ethnicity',
        'beauty': 'beauty', 'mouthstatus': 'mouthstatus', 'eyegaze': 'eyegaze', 'skinstatus': 'skinstatus'
    }
    description = "Let the machine evaluate your face\nChoose one or more of the following attributes\n\t" + ", ".join(
        ['gender', 'age', 'smiling', 'headpose', 'eyestatus', 'emotion', 'ethnicity',
         'beauty', 'mouthstatus', 'eyegaze',
         'skinstatus']) + "\nNote that your request might not succeed if the image you sent contains more than 5 faces"

    example = "Example: /face age beauty"

    num_of_reqs = 0

    def __init__(self, from_user, args):
        Interactive.__init__(self, from_user, args)
        try:
            if len(args) == 0:
                itchat.send_msg("You must enter one attribute!", from_user)
                raise AssertionError
            for attr in args:
                if attr not in FaceAnalysis.attributes:
                    itchat.send_msg("Non-existent attribute {}\nAllowed attributes are {}".format(attr, ", ".join(
                        FaceAnalysis.attributes)), from_user)
                    raise AssertionError
            self.attr = args.copy()
            self.send_separator(from_user)
            self.file_name = []
            self.proc = []
            itchat.send_msg("Please send an image with face(s) in it. You can send multiple images.", from_user)

        except AssertionError:
            raise Exception
        except:
            itchat.send_msg("Illegal Argument!", from_user)
            raise Exception

    def msg_handler(self, msg):
        from_user = msg['FromUserName']
        if msg['Text'] == '/q':
            for proc in self.proc:
                if proc.is_alive():
                    itchat.send_msg("Interrupted", from_user)
                    proc.terminate()
            self.finished = True
            self.send_separator(from_user)
            return True
        else:
            itchat.send_msg("If you want to switch command, please type /q to quit current session first", from_user)
            return False

    def file_handler(self, file):
        file_b = io.BytesIO(file['Text']())
        itchat.send_msg("Processing image...", file['FromUserName'])

        FaceAnalysis.num_of_reqs += 1
        self.proc.append(
            multiprocessing.Process(target=self.exec_task,
                                    args=(file.fileName.split('.')[1], file_b, file['FromUserName'],)))
        self.proc[len(self.proc) - 1].start()

    def exec_task(self, pic_type, file_b, from_user):
        itchat.auto_login(hotReload=True)

        t = time.clock()
        http_url = "https://api-cn.faceplusplus.com/facepp/v3/detect"

        num_of_keys = len(facepp_keys)
        key_idx = FaceAnalysis.num_of_reqs % num_of_keys
        data = {"api_key": facepp_keys[key_idx],
                "api_secret": facepp_secrets[key_idx],
                "return_landmark": "0",
                "return_attributes": ",".join(self.attr)
                }
        files = {"image_file": file_b}

        req_dict = requests.post(http_url, data=data, files=files).json()
        print(req_dict)

        try:
            if req_dict.get('faces', None) is None:
                itchat.send_msg("Too many requests. Please try again later.", from_user)
            else:
                if len(req_dict['faces']) > 0:
                    faces = req_dict['faces']

                    t1 = time.clock()
                    pic = Image.open(file_b)
                    draw = ImageDraw.Draw(pic)
                    msgs = []

                    for i in range(len(faces)):
                        face = faces[i]
                        print(i, face)
                        rect = face['face_rectangle']
                        FaceAnalysis.draw_rectangle(draw, (rect['left'], rect['top'], rect['left'] + rect['width'],
                                                           rect['top'] + rect['height']), (0, 255, 0), 5)
                        draw.text((rect['left'], rect['top'] + rect['height'] + 10), "Face {}".format(i + 1),
                                  (255, 255, 255), ImageFont.truetype("modules/calibri.ttf", rect['height'] // 3))
                        if face.get('attributes', None) is not None:
                            msgs.append("Face {}: \n".format(i + 1) + str("\n".join(
                                [attr + ": " + str(face['attributes'][FaceAnalysis.attributes_map[attr]])
                                 for attr in self.attr])))

                    buf = io.BytesIO()
                    pic.save(buf, format=pic_type, compression_level=5, quality=75)
                    buf.seek(0)

                    print(time.clock() - t1)
                    itchat.send_image(None, from_user, None, buf)
                    for msg in msgs:
                        itchat.send_msg(msg, from_user)
                    itchat.send_msg("Time taken: {}s".format(round(time.clock() - t, 2)), from_user)
                    buf.close()
                else:
                    itchat.send_msg("No face detected!", from_user)
        except:
            print(traceback.format_exc())
            itchat.send_msg("Error! Maybe your image is too big (>2MB)", from_user)
        finally:
            file_b.close()

    @staticmethod
    def draw_rectangle(draw, coor, color, width):
        draw.rectangle((coor[0], coor[1], coor[0] + width, coor[3]), fill=color)
        draw.rectangle((coor[0], coor[1], coor[2], coor[1] + width), fill=color)
        draw.rectangle((coor[0], coor[3], coor[2] + width, coor[3] + width), fill=color)
        draw.rectangle((coor[2], coor[1], coor[2] + width, coor[3] + width), fill=color)
