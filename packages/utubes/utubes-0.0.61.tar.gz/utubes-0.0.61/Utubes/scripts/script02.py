class Rttps(object):

    DATA01 = r"^((?:https?:)?\/\/)"
    DATA05 = r"https://www\.instagram\.com/[^ ]+"
    DATA02 = r"(?:(?:https?|ftp):\/\/)?[\w/\-?=%.]+\.[\w/\-?=%.]+"
    DATA03 = r"^https://www\.instagram\.com/([A-Za-z0-9._]+/)?(p|tv|reel)/([A-Za-z0-9\-_]*)"

    DATA04 = [
        r"/p/([a-zA-Z0-9_-]+)/",
        r"/tv/([a-zA-Z0-9_-]+)/",
        r"/reel/([a-zA-Z0-9_-]+)/",
        r"/stories/highlights/([a-zA-Z0-9_-]+)/",
        r"(?:https?://)?(?:www\.)?(?:threads\.net)(?:/[@\w.]+)?(?:/post)?/([\w-]+)(?:/?\?.*)?$"]
