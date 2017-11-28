from modules.__templates__ import Interactive
from modules.__secrets__ import facepp_keys, facepp_secrets
import itchat
import requests
from json import JSONDecoder
import multiprocessing, os, cv2
import traceback
import random


class FaceAnalysis(Interactive):
    __author__ = "Hanzhi Zhou"
    alias = "face"
    title = "Face++ Face Analysis Integration"
    parameters = "[attr1] [attr2] [...]"
    attributes = ['gender', 'age', 'smiling', 'headpose', 'eyestatus', 'emotion', 'ethnicity',
                  'beauty', 'mouthstatus', 'eyegaze', 'skinstatus']
    description = "Let the machine evaluate your face\nChoose one or more of the following attributes\n\t" + ", ".join(
        ['gender', 'age', 'smiling', 'headpose', 'eyestatus', 'emotion', 'ethnicity',
         'beauty', 'mouthstatus', 'eyegaze', 'skinstatus'])

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
            itchat.send_msg("Please send an image with face(s) in it", from_user)

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
            for file_name in self.file_name:
                FaceAnalysis.remove_garbage(file_name)
                FaceAnalysis.remove_garbage("result-{}.png".format(file_name))
            self.finished = True
            self.send_separator(from_user)
            return True

    def file_handler(self, file):
        file_name = "{}-{}".format(len(self.file_name), file.fileName)
        self.file_name.append(file_name)
        file.download(file_name)
        itchat.send_msg("Processing image...", file['FromUserName'])
        self.proc.append(multiprocessing.Process(target=self.exec_task, args=(file_name, file['FromUserName'],)))
        self.proc[len(self.proc) - 1].start()

    def exec_task(self, file_name, from_user):
        itchat.auto_login(hotReload=True)
        http_url = "https://api-cn.faceplusplus.com/facepp/v3/detect"

        rng_idx = random.randint(0, 2)
        data = {"api_key": facepp_keys[rng_idx],
                "api_secret": facepp_secrets[rng_idx],
                "return_landmark": "0",
                "return_attributes": ",".join(self.attr)
                }
        f = open(file_name, "rb")
        files = {"image_file": f}

        response = requests.post(http_url, data=data, files=files)
        req_con = response.content.decode('utf-8')
        req_dict = JSONDecoder().decode(req_con)
        print(req_dict)
        try:
            if req_dict.get('faces', None) is None:
                itchat.send_msg("Too many requests. Please try again later.", from_user)
            else:
                if len(req_dict['faces']) > 0:
                    faces = req_dict['faces']
                    pic = cv2.imread(file_name)
                    msgs = []
                    for i in range(len(faces)):
                        face = faces[i]
                        print(i, face)
                        rect = face['face_rectangle']
                        cv2.rectangle(pic, (rect['left'], rect['top']), (rect['left'] + rect['width'],
                                                                         rect['top'] + rect['height']), (0, 255, 0), 5)
                        cv2.putText(pic, "Face {}".format(i + 1), (rect['left'], rect['top'] + rect['height'] + 30),
                                    cv2.FONT_HERSHEY_COMPLEX, 1, (255, 255, 255), 2)
                        if face.get('attributes', None) is not None:
                            msgs.append("Face {}: \n".format(i + 1) + str(
                                "\n".join([attr + ": " + str(face['attributes'][attr]) for attr in self.attr])))

                    cv2.imwrite("result-{}".format(file_name), pic, (cv2.IMWRITE_PNG_COMPRESSION, 9))
                    itchat.send_image("result-{}".format(file_name), from_user)
                    for msg in msgs:
                        itchat.send_msg(msg, from_user)
                else:
                    itchat.send_msg("No face detected!", from_user)
        except:
            print(traceback.format_exc())
            itchat.send_msg("Error!", from_user)
        finally:
            f.close()
            FaceAnalysis.remove_garbage(file_name)
            FaceAnalysis.remove_garbage("result-{}".format(file_name))

    @staticmethod
    def remove_garbage(file_name):
        try:
            os.remove(file_name)
        except:
            pass
