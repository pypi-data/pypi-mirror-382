import os
from ..scripts import Smbo
from ..scripts import Flite
from ..scripts import Scripted
from .collections import SMessage
from Oxgram.functions import Flinks
#=====================================================================================================================

class Extractors:

    async def extract03(texted, length, clean):
        texted = Scripted.DATA01.join(clean.get(chao, chao) for chao in texted)
        return texted[:length] if length else texted

#=====================================================================================================================
    
    async def extract01(update, incoming):
        poxwers = incoming.split(Smbo.DATA04)
        if len(poxwers) == 2 and Smbo.DATA04 in incoming:
             Username = None
             Password = None
             Flielink = poxwers[0] # INCOMING URL
             Filename = poxwers[1] # INCOMING FILENAME
        elif len(poxwers) == 3 and Smbo.DATA04 in incoming:
             Filename = None
             Flielink = poxwers[0] # INCOMING URL
             Username = poxwers[1] # INCOMING USERNAME
             Password = poxwers[2] # INCOMING PASSWORD
        elif len(poxwers) == 4 and Smbo.DATA04 in incoming:
             Flielink = poxwers[0] # INCOMING URL
             Filename = poxwers[1] # INCOMING FILENAME
             Username = poxwers[2] # INCOMING USERNAME
             Password = poxwers[3] # INCOMING PASSWORD
        else:
             Filename = None # INCOMING FILENAME
             Username = None # INCOMING USERNAME
             Password = None # INCOMING PASSWORD
             Flielink = await Flinks.get01(update, incoming)

        moon01 = Flielink.strip() if Flielink else None
        moon02 = Filename.strip() if Filename else None
        moon03 = Username.strip() if Username else None
        moon04 = Password.strip() if Password else None
        return SMessage(filelink=moon01, filename=moon02, username=moon03, password=moon04)

#=====================================================================================================================
    
    async def extract02(onames, cnames, length=60, clean=Flite.DATA01):
        filenamen = os.path.splitext(cnames)[0] if cnames else os.path.splitext(onames)[0]
        extensios = os.path.splitext(cnames)[1] if cnames else os.path.splitext(onames)[1]
        extension = extensios if extensios else os.path.splitext(onames)[1]
        filenames = await Extractors.extract03(filenamen, length, clean)
        return SMessage(filename=filenames, extenson=extension)

#=====================================================================================================================
