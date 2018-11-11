from .__templates__ import Interactive
from .__config__ import multi_process, terminal_QR
import numpy as np
import time
import itchat
import io
from cmath import *
from PIL import Image
if multi_process:
    from multiprocessing import Process
else:
    from .__stoppable__ import Process


class ImgTrans(Interactive):
    alias = "imgtf"
    __author__ = "Hanzhi Zhou"
    title = "Image Transformation"
    description = "\n".join(["Perform arbitrary image transformation by complex mapping"])
    parameters = "[function] [kernel size]"
    example = "\n".join(["Example: /imgtf c:c**1.2 5\n",
                         "This will perform a complex mapping f(c)=c^1.2 on the image you sent then smooth it with convolution kernel of size 5*5"])

    # convert the sparse matrix dictionary (mapping (x, y) to (b, g, r)) to a numpy three dimensional array
    @staticmethod
    def toMatrix(newDict):
        global const
        arrs = newDict.keys()
        xRange = max(arrs, key=lambda x: x[0])[0] - min(arrs, key=lambda x: x[0])[0]
        yRange = max(arrs, key=lambda x: x[1])[1] - min(arrs, key=lambda x: x[1])[1]
        shiftX = xRange // 2
        shiftY = yRange // 2
        imgArr = np.zeros((yRange, xRange, 3), np.uint8)
        for x in range(xRange):
            for y in range(yRange):
                imgArr[y, x, :] = np.array(newDict.get((x - shiftX, y - shiftY), [255, 255, 255]), np.uint8)
        return imgArr

    # interpolate the pixels with a matrix of size (size*size)
    @staticmethod
    def avPixels(newImg, m, n, bgr, size, c):
        a = round(m)
        b = round(n)
        for i in range(-c, size - c):
            for j in range(-c, size - c):
                (x, y) = (a + i, b + j)
                if newImg.get((x, y)) is None:
                    newImg[(x, y)] = bgr

    @staticmethod
    def transform(x, y, orgX, orgY, f):
        c = complex(x - orgX, y - orgY)
        return f(c)

    @classmethod
    def parse_args(cls, from_user, args):
        assert len(args) >= 2, "Two parameters are required: [function] and [kernel size]"
        f = eval("lambda " + args[0])
        assert type(f(complex(0, 0))) == complex, "Illegal Complex Function!"
        assert args[1].isdigit(), "A positive integer is required for specifying the kernel size"
        return args[0], int(args[1])

    def __init__(self, from_user, args):
        super(self.__class__, self).__init__(from_user, args)
        self.f, self.kernel = args
        self.process = None
        self.send_separator(from_user)
        itchat.send_msg("Please send an image", from_user)

    def msg_handler(self, msg):
        if msg['Text'] == '/q':
            if self.process is not None:
                self.process.terminate()
            self.finished = True
            itchat.send_msg('Command interrupted', msg['FromUserName'])
            self.send_separator(msg['FromUserName'])
            return True
        else:
            itchat.send_msg("If you want to switch command, please type /q to quit current session first", msg['FromUserName'])
            return False

    def file_handler(self, file):
        if not self.finished:
            itchat.send_msg("Image Received.\nProcessing...", file['FromUserName'])
            file_b = io.BytesIO(file['Text']())
            self.process = Process(target=self.exec_task,
                                   args=(file.fileName.split('.')[1], file_b, file['FromUserName'], self.f,))
            self.process.start()
        else:
            itchat.send_msg("Processing...\nPlease be patient...", file['FromUserName'])

    def exec_task(self, pic_type, file_b, from_user, f):
        if multi_process:
            itchat.auto_login(hotReload=True, enableCmdQR=terminal_QR)
        func = eval("lambda " + f)
        t = time.clock()

        img = np.asarray(Image.open(file_b))
        height, width = img.shape[0:2]
        orgX, orgY = (width // 2, height // 2)
        c = self.kernel // 2
        newImg = {}
        for x in range(width):
            for y in range(height):
                xy = ImgTrans.transform(x, y, orgX, orgY, func)
                ImgTrans.avPixels(newImg, xy.real, xy.imag, img[y, x, :], self.kernel, c)
        imgArr = ImgTrans.toMatrix(newImg)

        buf = io.BytesIO()
        Image.fromarray(imgArr).save(buf, format=pic_type, quality=75, compression_level=5)
        buf.seek(0)

        itchat.send_image(None, from_user, None, buf)
        itchat.send_msg("Time spent = {}s".format(round(time.clock() - t, 2)), from_user)
        self.send_separator(from_user)
        self.finished = True
        file_b.close()
        buf.close()
