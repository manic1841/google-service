import os
import shutil
import json
import glob

from .agent.models import AlbumModel, MediaItemModel
from .shortcut import ShortCut

class Photo:
    def __init__(self,
                 id: str,
                 filename: str,
                 filepath: str,
                 metadata_path: str,
                 metadata: dict=None):
        self.id = id
        self.filename = filename
        self.filepath = filepath
        self.metadata_path = metadata_path

        if not metadata:
            with open(self.metadata_path, 'r') as f:
                self.metadata = json.load(f)
        else:
            self.metadata = metadata

    @classmethod
    def from_filepath(cls, filepath: str):
        """
        Create photo object from filepath
        """
        metadata_path = cls._get_metadata_path(filepath)
        with open(metadata_path, 'r') as f:
            metadata = json.load(f)

        id = metadata['id']
        filename = metadata['filename']

        return cls(id=id,
                   filename=filename,
                   filepath=filepath,
                   metadata_path=metadata_path,
                   metadata=metadata)

    @classmethod
    def from_metadata_path(cls, metadata_path: str):
        """
        Create photo object from photo metadata path
        """
        # Get photo real path
        ext = metadata_path.split('.')[-1]
        pattern = f'{metadata_path[:-len(ext)]}*'
        filepath = ''
        for file in glob.glob(pattern):
            if file.endswith('.json'):
                continue
            filepath = file
            break
        if len(filepath) == 0:
            raise RuntimeError(f"Photo not found according {metadata_path}")

        return cls.from_filepath(filepath)

    @classmethod
    def from_mediaitem(cls, model: MediaItemModel, src: str, album_path: str):
        """
        Create photo object from mediaitem and copy file to album.
        The filename supposed to be f'{date}_{filename}'
        """
        filename = model.filename
        id = model.id

        filepath = os.path.join(album_path, filename)
        if os.path.exists(filepath):
            raise RuntimeError(f'Photo {id} has already existed on {filepath}')

        # Copy file
        shutil.copyfile(src, filepath)

        # Save metadata
        metadata_filepath = cls._get_metadata_path(filepath)
        metadata = model.dict()
        with open(metadata_filepath, 'w') as f:
            json.dump(metadata, f, indent=2)

        return cls(id=id,
                   filename=filename,
                   filepath=filepath,
                   metadata_path=metadata,
                   metadata=metadata)

    @staticmethod
    def _get_metadata_path(filepath: str):
        ext = filepath.split('.')[-1]
        return filepath[:-len(ext)] + 'json'

class Album:

    def __init__(self,
                 id: str,
                 title: str,
                 filepath: str,
                 metadata_path: str,
                 metadata: dict=None):
        self.id = id
        self.title = title
        self.filepath = filepath
        self.metadata_path = metadata_path

        # windows shortcut shell
        self.shortcut_tool = ShortCut()

        if not metadata:
            # Load metadata
            with open(self.metadata_path, 'r') as f:
                self.metadata = json.load(f)
        else:
            self.metadata = metadata

        # Load all photos in the album folder
        self.photo_by_id = {}
        for dir in os.listdir(self.filepath):
            # Skip album metadata
            if dir.endswith('.json'):
                continue
            abspath = os.path.join(self.filepath, dir)
            # Get real path
            real_path = self.shortcut_tool.get_target_path(abspath)
            photo = Photo.from_filepath(real_path)
            self.photo_by_id[photo.id] = photo

    @classmethod
    def from_filepath(cls, filepath: str):
        """
        Create album object from filepath. The path supposed to be a folder
        """
        title = os.path.basename(filepath)
        metadata_path = cls._get_metadata_path(filepath, title)
        with open(metadata_path, 'r') as f:
            metadata = json.load(f)

        return cls(id=metadata['id'],
                   title=title,
                   filepath=filepath,
                   metadata_path=metadata_path,
                   metadata=metadata)

    @classmethod
    def from_album(cls, model: AlbumModel, root: str):
        """
        Create album object from album, and create the folder on the root path
        """
        title = model.title
        filepath = os.path.join(root, title)
        metadata_path = cls._get_metadata_path(filepath, title)

        # Create local folder
        if not os.path.exists(filepath):
            os.makedirs(filepath)

            # Save metadata
            metadata = model.dict()
            with open(metadata_path, 'w', encoding='utf-8') as f:
                json.dump(metadata, f, ensure_ascii=False, indent=2)

        return cls(id=model.id,
                   title=title,
                   filepath=filepath,
                   metadata_path=metadata_path,
                   metadata=metadata)

    @staticmethod
    def _get_metadata_path(root: str, title: str):
        return os.path.join(root, f'{title}_album.json')

    def add_photo(self, photo: Photo):
        """
        Add photo into album. Create a shortcut to link real file
        """
        if photo.id in self.photo_by_id:
            return

        basename = os.path.basename(photo.filepath)
        dst = os.path.join(self.filepath, f'{basename}.lnk')
        self.shortcut_tool.create_shortcut(photo.filepath, dst)

        self.photo_by_id[photo.id] = photo


class BackupManager:
    _all_photo_folder_ = '0_all'

    def __init__(self, root: str):
        """
        Load all albums and photos on the root path
        """
        root = os.path.abspath(root)
        self.root = root
        self.all_photo_folder = os.path.join(root, self._all_photo_folder_)
        # Create all photo folder
        if not os.path.exists(self.all_photo_folder):
            os.makedirs(self.all_photo_folder)

        self.albums_by_id = {}
        self.photo_by_id = {}
        # Load all album
        for dir in os.listdir(root):
            abspath = os.path.join(root, dir)
            # Skip all photo folder
            if abspath == self.all_photo_folder:
                continue
            # Get album
            if os.path.isdir(abspath):
                album = Album.from_filepath(abspath)
                self.albums_by_id[album.id] = album

                for id, photo in album.photo_by_id.items():
                    self.photo_by_id[id] = photo

        # Load all photo
        for dir in os.listdir(self.all_photo_folder):
            if dir.endswith('.json'):
                abspath = os.path.join(self.all_photo_folder, dir)
                photo = Photo.from_metadata_path(abspath)

                # Avoid loading photo again
                if photo.id not in self.photo_by_id:
                    self.photo_by_id[photo.id] = photo

    def check_album_existed(self, id: str):
        return id in self.albums_by_id

    def check_photo_existed(self, id: str):
        return id in self.photo_by_id

    def backup_album(self, model: AlbumModel, photo_list: list):
        """
        Backup album

        Args:
            - model:
            - photo_list: a list of tuple '(MediaItemModel, src)'
        Return:
            Album
        """
        if not self.check_album_existed(model.id):
            # Create album
            album = Album.from_album(model, self.root)

            self.albums_by_id[album.id] = album
        else:
            album = self.albums_by_id[model.id]

        for photo_model, src in photo_list:
            photo = self.backup_photo(photo_model, src)
            album.add_photo(photo)

        return album

    def backup_photo(self, model: MediaItemModel, src: str):
        """
        Backup photo

        Args:
            - model:
            - src: path to photo file
        Return:
            Photo
        """
        if self.check_photo_existed(model.id):
            return self.photo_by_id[model.id]

        photo = Photo.from_mediaitem(model, src, self.all_photo_folder)
        self.photo_by_id[photo.id] = photo

        return photo

    def overview(self):
        """
        Show overview of all albums
        """

        print('-'*50)
        print(f'album: (total: {len(self.albums_by_id)})')
        for id, album in self.albums_by_id.items():
            print(f'  {album.title}:\t{len(album.photo_by_id)}')
        print(f'  {self._all_photo_folder_}:\t{len(self.photo_by_id)}')
        print('-'*50)
