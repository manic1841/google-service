import typing as t

from pydantic import BaseModel
import pydantic


class AllOptional(pydantic.main.ModelMetaclass):
    def __new__(cls, name, bases, namespaces, **kwargs):
        annotations = namespaces.get("__annotations__", {})
        for base in bases:
            annotations.update(base.__annotations__)
        for field in annotations:
            if not field.startswith("__"):
                annotations[field] = t.Optional[annotations[field]]
        namespaces["__annotations__"] = annotations
        return super().__new__(cls, name, bases, namespaces, **kwargs)


class AlbumBaseModel(BaseModel):
    id: str
    title: str
    productUrl: str
    isWriteable: bool
    shareInfo: dict
    mediaItemsCount: str
    coverPhotoBaseUrl: str
    coverPhotoMediaItemId: str


class AlbumModel(AlbumBaseModel, metaclass=AllOptional):
    pass


class MediaMetadataBaseModel(BaseModel):
    createTime: str
    width: str
    height: str
    video: dict
    photo: dict


class MediaMetadataModel(MediaMetadataBaseModel, metaclass=AllOptional):
    pass


class MediaItemBaseModel(BaseModel):
    id: str
    description: str
    productUrl: str
    baseUrl: str
    mimeType: str
    mediaMetadata: MediaMetadataModel
    contributorInfo: dict
    filename: str


class MediaItemModel(MediaItemBaseModel, metaclass=AllOptional):
    pass
