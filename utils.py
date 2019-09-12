import sys
from os import path

def RM_path(pathStr):

    if getattr(sys, 'frozen', False):

        wd = sys._MEIPASS

    else:

        wd = ''

    return path.join(wd, pathStr)
