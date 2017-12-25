"""
If you want to get better parallel performance (i.e. when many users are requesting simultaneously), 
set this to True
I found some problems associated with itchat hotReload on ARM64 platform, and therefore I designed an alternative solution -- using threading to avoid hotReload.
"""
multi_process = False
"""
0: open the QR code using system's default image viewer
1: show the QR code in terminal (use this one if your terminal's background color is black)
-1: show the QR code in terminal (use this one if your terminal's background color is white)
"""
terminal_QR = 0
