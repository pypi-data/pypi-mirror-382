from pathlib import Path
#=========================================================================

class Finders:

    async def get00(location):
        if location:
            return location
        else:
            raise Exception("FILE CORRUPTED")

#=========================================================================

    async def get01(location):
        try:
            moones = Path(location)
            moonus = moones.stat()
            return moonus.st_size
        except Exception as errors:
            raise Exception("FILE CORRUPTED")

#=========================================================================

    async def get05(filename, directory, location=None):
        for item in Path(directory).rglob('*'):
            if item.is_file() and item.name.startswith(filename):
                location = str(item)
                break

        return location

#=========================================================================
