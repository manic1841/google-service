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

# Directions API
class GeocodedWaypointBaseModel(BaseModel):
    geocoder_status: str
    place_id: str
    types: t.List[str]

class GeocodedWaypointModel(GeocodedWaypointBaseModel, metaclass=AllOptional):
    pass

class PolylineBaseModel(BaseModel):
    points: str

class PolylineModel(PolylineBaseModel, metaclass=AllOptional):
    pass

class LegBaseModel(BaseModel):
    distance: dict
    duration: dict
    end_address: str
    end_location: dict
    start_address: str
    start_location: dict
    steps: t.List[dict]
    traffic_speed_entry: list
    via_waypoint: list

class LegModel(LegBaseModel, metaclass=AllOptional):
    pass

class RoutesBaseModel(BaseModel):
    bounds: dict
    copyrights: str
    legs: t.List[LegModel]
    overview_polyline: PolylineModel
    summary: str
    warnings: list
    waypoint_order: t.List[int]

class RoutesModel(RoutesBaseModel, metaclass=AllOptional):
    pass

class DirectionsBaseModel(BaseModel):
    geocoded_waypoints: t.List[GeocodedWaypointModel]
    routes: t.List[RoutesModel]
    status: str

class DirectionsModel(DirectionsBaseModel, metaclass=AllOptional):
    pass

