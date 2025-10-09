from ..scripts import Ulinks
from ..exception import Audiomode
from ..exception import Videomode
from ..exception import Filesmode
#====================================================================

class Manage:

    async def get01(mode, link, extension):
        if extension == "mp3":
            raise Audiomode()
        elif mode == True:
            raise Videomode()
        elif link.startswith(Ulinks.DATA02):
            raise Videomode()
        else:
            raise Filesmode()

#====================================================================
