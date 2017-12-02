from modules.__templates__ import Interactive
import numpy as np
import time
import itchat
import io
from PIL import Image
from modules.__config__ import multi_process
if multi_process:
    from multiprocessing import Process
else:
    from modules.__stoppable__ import Process


class ImgTrans(Interactive):
    alias = "imgtf"
    __author__ = "Hanzhi Zhou"
    title = "Image Transformation"
    description = "\n".join(["Perform arbitrary image transformation by complex mapping",
                             "which will perform a complex mapping f(c)->c^1.2 on the image you sent then smooth it with convolution kernel of size 5*5"])
    parameters = "[function] [kernel size]"
    example = "Example: /imgtf c:c**1.2 5,"

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

    def __init__(self, from_user, args):
        Interactive.__init__(self, from_user, args)
        try:
            f = eval("lambda " + args[0])
            if type(f(complex(0, 0))) != complex:
                itchat.send_msg("Illegal Complex Function!", from_user)
                raise AssertionError
            self.f = args[0]
            self.kernel = int(args[1])
            self.proc = None
        except AssertionError:
            raise Exception
        except:
            itchat.send_msg("Illegal Arguments!", from_user)
            raise Exception

        self.send_separator(from_user)
        itchat.send_msg("Please send an image", from_user)

    def msg_handler(self, msg):
        if msg['Text'] == '/q':
            self.proc.terminate()
            self.finished = True
            itchat.send_msg('Command interrupted', msg['FromUserName'])
            self.send_separator(msg['FromUserName'])
            return True
        else:
            return False

    def file_handler(self, file):
        if not self.finished:
            itchat.send_msg("Image Received.\nProcessing...", file['FromUserName'])
            file_b = io.BytesIO(file['Text']())
            self.proc = Process(target=self.exec_task,
                                                args=(file.fileName.split('.')[1], file_b, file['FromUserName'], self.f,))
            self.proc.start()
        else:
            itchat.send_msg("Processing...\nPlease be patient...", file['FromUserName'])

    def exec_task(self, pic_type, file_b, from_user, f):
        if multi_process:
            itchat.auto_login(hotReload=True)
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
        Image.fromarray(imgArr).save(buf, format=pic_type, quality=75, compression_leve=5)
        buf.seek(0)

        itchat.send_image(None, from_user, None, buf)
        itchat.send_msg("Time spent = {}s".format(round(time.clock() - t, 2)), from_user)
        self.send_separator(from_user)
        self.finished = True
        file_b.close()
        buf.close()
