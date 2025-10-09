import os, random
from yt_dlp import YoutubeDL
from urllib.parse import unquote
from urllib.parse import urlparse
from .collections import SMessage
from ..scripts import Okeys, Scripted
#=================================================================================

class Filename:

    async def get01(extension=None):
        mainos = str(random.randint(10000, 100000000000000))
        moonus = mainos + extension if extension else mainos
        return moonus

#=================================================================================

    async def get02(filelink):
        try:
            findoutne = urlparse(filelink)
            filenameo = os.path.basename(findoutne.path)
            filenames = unquote(filenameo)
            return SMessage(result=filenames)
        except Exception as errors:
            return SMessage(result="Unknown.tmp", errors=errors)

#=================================================================================

    async def get03(filelink, command):
        with YoutubeDL(command) as ydl:
            try:
                mainos = Okeys.DATA01
                meawes = ydl.extract_info(filelink, download=False)
                moonus = ydl.prepare_filename(meawes, outtmpl=mainos)
                return SMessage(result=moonus)
            except Exception as errors:
                return SMessage(result="Unknown.tmp", errors=errors)

#=================================================================================
