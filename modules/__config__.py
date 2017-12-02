"""
If you want to get better parallel performance (i.e. when many users are requesting simultaneously), 
set multi_process=True in \_\_config__.py, in folder "modules".
"""
multi_process = False
"""
0: open the QR code using system's default image viewer
1: show the QR code in terminal (use this one if your terminal's background color is black)
-1: show the QR code in terminal (use this one if your terminal's background color is white)
"""
terminal_QR = 1
