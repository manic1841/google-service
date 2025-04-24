import os


class PhotoFile:
    def __init__(self):
        self.filename = ""
        self.filepath = ""
        self.exif_path = ""
        self.need_exif = True
        self.album = ""


class TakeoutLoader:
    def __init__(self, root: str): ...

    def load(self, path): ...
