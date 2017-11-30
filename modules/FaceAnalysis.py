from modules.__templates__ import Interactive
from modules.__secrets__ import facepp_keys, facepp_secrets
import itchat
import requests
import multiprocessing
import traceback
import io, os, cv2, time
import numpy as np
from PIL import Image


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
            for file_name in self.file_name:
                FaceAnalysis.remove_garbage("result-{}.png".format(file_name))
            self.finished = True
            self.send_separator(from_user)
            return True
        else:
            itchat.send_msg("If you want to switch command, please type /q to quit current session first", from_user)
            return False

    def file_handler(self, file):
        file_name = "{}-{}".format(len(self.file_name), file.fileName)
        self.file_name.append(file_name)

        file_b = io.BytesIO(file['Text']())
        itchat.send_msg("Processing image...", file['FromUserName'])

        FaceAnalysis.num_of_reqs += 1
        self.proc.append(multiprocessing.Process(target=self.exec_task, args=(file_name, file_b, file['FromUserName'],)))
        self.proc[len(self.proc) - 1].start()

    def exec_task(self, file_name, file_b, from_user):
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
                    raw_pic = np.asarray(Image.open(file_b))
                    pic = np.zeros(raw_pic.shape, raw_pic.dtype)
                    pic[:, :, 0] = raw_pic[:, :, 2]
                    pic[:, :, 1] = raw_pic[:, :, 1]
                    pic[:, :, 2] = raw_pic[:, :, 0]

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
                                "\n".join(
                                    [attr + ": " + str(face['attributes'][FaceAnalysis.attributes_map[attr]]) for attr
                                     in self.attr])))

                    cv2.imwrite("result-{}".format(file_name), pic, (cv2.IMWRITE_PNG_COMPRESSION, 9))

                    print(time.clock() - t1)

                    itchat.send_image("result-{}".format(file_name), from_user)
                    for msg in msgs:
                        itchat.send_msg(msg, from_user)
                    itchat.send_msg("Time taken: {}s".format(round(time.clock() - t, 2)), from_user)
                else:
                    itchat.send_msg("No face detected!", from_user)
        except:
            print(traceback.format_exc())
            itchat.send_msg("Error! Maybe your image is too big (>2MB)", from_user)
        finally:
            file_b.close()
            FaceAnalysis.remove_garbage("result-{}".format(file_name))

    @staticmethod
    def remove_garbage(file_name):
        try:
            os.remove(file_name)
        except:
            pass
