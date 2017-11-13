import numpy as np
import cv2, time
import itchat
import os
import multiprocessing


class ImgTrans:
    alias = "imgtf"
    interactive = True
    __author__ = "Hanzhi Zhou"
    title = "Image Transformation"
    description = "\n".join(["Perform arbitrary image transformation by complex mapping",
                             "Example: /imgtf c:c**1.2 5,",
                             "which will perform a complex mapping f(c)->c^1.2 on the image you sent then smooth it with convolution kernel of size 5*5"])
    parameters = "[function] [kernel size]"

    @staticmethod
    def help(from_user):
        my_class = ImgTrans
        itchat.send_msg("\n\t".join(["/{} {}".format(my_class.alias, my_class.parameters),
                                     "{} by {}".format(my_class.title, my_class.__author__),
                                     my_class.description]), from_user)

    # convert the sparse matrix dictionary (mapping (x, y) to (b, g, r)) to a numpy three dimensional array
    @staticmethod
    def toMatrix(newDict):
        global const
        arrs = newDict.keys()
        xRange = max(arrs, key=lambda x: x[0])[0] - min(arrs, key=lambda x: x[0])[0]
        yRange = max(arrs, key=lambda x: x[1])[1] - min(arrs, key=lambda x: x[1])[1]
        shiftX = xRange // 2
        shiftY = yRange // 2
        imgArr = np.zeros((yRange, xRange, 3), np.int16)
        for x in range(xRange):
            for y in range(yRange):
                imgArr[y, x, :] = np.array(newDict.get((x - shiftX, y - shiftY), [255, 255, 255]), np.int16)
        return imgArr

    @staticmethod
    def bgrTorgb(img):
        img_rgb = np.zeros(img.shape, img.dtype)
        img_rgb[:, :, 0] = img[:, :, 2]
        img_rgb[:, :, 1] = img[:, :, 1]
        img_rgb[:, :, 2] = img[:, :, 0]
        return img_rgb

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
        try:
            f = eval("lambda " + args[0])
            if type(f(complex(0, 0))) != complex:
                itchat.send_msg("Illegal Complex Function!", from_user)
                raise AssertionError
            self.f = args[0]
            self.kernel = int(args[1])
            self.proc = None
            self.finished = False
        except AssertionError:
            raise Exception
        except:
            itchat.send_msg("Illegal Arguments!", from_user)
            raise Exception

        self.send_separator(from_user)
        itchat.send_msg("Please send an image", from_user)

    def send_separator(self, dst):
        itchat.send_msg("-" * 30, dst)

    def msg_handler(self, msg):
        if msg['Text'] == '/q':
            self.proc.terminate()
            self.finished = True
            itchat.send_msg('Command interrupted', msg['FromUserName'])
            self.send_separator(msg['FromUserName'])
            ImgTrans.remove_garbage(self.file_name)
            return True
        else:
            return False

    def file_handler(self, file):
        if not self.finished:
            file.download(file.fileName)
            itchat.send_msg("Image Received.\nProcessing...", file['FromUserName'])
            self.file_name = file.fileName
            self.proc = multiprocessing.Process(target=self.exec_task,
                                                args=(file.fileName, file['FromUserName'], self.f,))
            self.proc.start()
        else:
            itchat.send_msg("Processing...\nPlease be patient...", file['FromUserName'])

    def exec_task(self, file_name, from_user, f):
        itchat.auto_login(hotReload=True)
        func = eval("lambda " + f)
        t = time.clock()
        img = cv2.imread(file_name)
        height, width = img.shape[0:2]
        orgX, orgY = (width // 2, height // 2)
        c = self.kernel // 2
        newImg = {}
        for x in range(width):
            for y in range(height):
                xy = ImgTrans.transform(x, y, orgX, orgY, func)
                ImgTrans.avPixels(newImg, xy.real, xy.imag, img[y, x, :], self.kernel, c)
        imgArr = ImgTrans.toMatrix(newImg)
        cv2.imwrite("result.png", imgArr)

        itchat.send_image("result.png", from_user)
        itchat.send_msg("Time spent = {}s".format(round(time.clock() - t, 2)), from_user)
        self.send_separator(from_user)
        self.finished = True
        ImgTrans.remove_garbage(file_name)

    @staticmethod
    def remove_garbage(file_name):
        try:
            os.remove(file_name)
            os.remove("result.png")
        except:
            pass
