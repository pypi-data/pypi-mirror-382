import re
import asyncio
from ..scripts import Rttps
from ..scripts import Flite
from .collections import THREAD
from .collections import SMessage
from instaloader import Post, Profile
from instaloader import Instaloader, NodeIterator
#========================================================================================================
# FUNCTION --> 16

class Instagram:

    async def get01(incoming):
        matchs = re.search(Rttps.DATA03, incoming)
        moonus = True if matchs else False
        return SMessage(result=matchs, status=moonus)

    async def get02(incoming):
        mainse = Flite.DATA02
        conmom = mainse.get(incoming.group(2))
        moonus = True if conmom else False
        return SMessage(result=conmom, status=moonus)

    async def get03(bot, shortcode):
        moonus = Post.from_shortcode(bot.context, shortcode)
        return moonus

    async def get04(bot, username):
        moonus = Profile.from_username(bot.context, username)
        return moonus

    async def get05(bot: Profile) -> NodeIterator[Post]:
        moonus = bot.get_posts()
        return moonus

    async def get06(incoming):
        for index, pattern in enumerate(Rttps.DATA04):
            moons = re.search(pattern, incoming)
            if moons:
                return incoming if index == 0 else moons.group(1)
        return None
    
    async def download(bot: Instaloader, update: Post):
        loomed = asyncio.get_event_loop()
        moonus = await loomed.run_in_executor(THREAD, bot.download_post, update, update.owner_username)
        return moonus

#========================================================================================================
