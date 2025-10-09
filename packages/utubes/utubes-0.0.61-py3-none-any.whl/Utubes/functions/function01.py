import os, asyncio
from ..scripts import Okeys
from ..scripts import Flite
from ..scripts import Scripted
from ..exception import Cancelled
from .collections import THREAD, SMessage
from yt_dlp import YoutubeDL, DownloadError
#===============================================================================================

class DownloadER:

    async def download(link, command, progress=None):
        with YoutubeDL(command) as ydl:
            try:
                filelink = [link]
                loop = asyncio.get_event_loop()
                ydl.add_progress_hook(progress) if progress else progress
                await loop.run_in_executor(THREAD, ydl.download, filelink)
            except DownloadError as errors:
                raise Exception(errors)
            except Cancelled as errors:
                raise Cancelled(errors)
            except Exception as errors:
                raise Exception(errors)

#===============================================================================================
    
    async def metadata(link, command):
        with YoutubeDL(command) as ydl:
            try:
                loop = asyncio.get_event_loop()
                moonus = await loop.run_in_executor(THREAD, ydl.extract_info, link, False)
                return SMessage(result=moonus)
            except Exception as errors:
                return SMessage(errors=errors)

#===============================================================================================

    async def extracts(link, command):
        with YoutubeDL(command) as ydl:
            try:
                loop = asyncio.get_event_loop()
                moonus = await loop.run_in_executor(THREAD, ydl.extract_info, link, False)
                return SMessage(result=moonus)
            except Exception as errors:
                return SMessage(errors=errors)

#===============================================================================================

    async def filename(link, command, names=Okeys.DATA01):
        with YoutubeDL(command) as ydl:
            try:
                loop = asyncio.get_event_loop()
                meawes = await loop.run_in_executor(THREAD, ydl.extract_info, link, False)
                moonus = ydl.prepare_filename(meawes, outtmpl=names)
                return SMessage(result=moonus)
            except DownloadError as errors:
                raise Exception(errors)

#===============================================================================================
