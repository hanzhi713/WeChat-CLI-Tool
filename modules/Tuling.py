from modules.__templates__ import Interactive
from modules.__secrets__ import tuling_keys
import itchat
import requests


class Tuling(Interactive):
    alias = "tu"
    __author__ = "Hanzhi Zhou"
    title = "Invoke Tuling Robot"
    num_of_reqs = 0

    def __init__(self, from_user, args):
        Interactive.__init__(self, from_user, args)
        self.user = from_user
        self.send_separator(self.user)

    def msg_handler(self, msg):
        txt = msg['Text']
        if txt == '/q':
            itchat.send_msg("Quitting...", self.user)
            self.send_separator(self.user)
            self.finished = True
            return True

        response = self.post_data(txt)
        code = response["code"]
        if code == 100000:
            itchat.send_msg(response["text"], self.user)
        elif code == 200000:
            itchat.send_msg("\n".join([response["text"], response["url"]]), self.user)
        else:
            itchat.send_msg(response["text"], self.user)

    def post_data(self, txt):
        num_of_keys = len(tuling_keys)
        key_idx = Tuling.num_of_reqs % num_of_keys
        data = {
            "key" : tuling_keys[key_idx],
            "info" : txt,
            "userid" : self.user
        }
        return requests.post("http://www.tuling123.com/openapi/api", data).json()
