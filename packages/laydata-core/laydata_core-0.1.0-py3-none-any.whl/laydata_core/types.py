from typing_extensions import TypedDict


class HealthResponse(TypedDict):
    status: str
    teable: str
    spaces: int


class VersionResponse(TypedDict):
    server: str
    protocol: str


class SpaceData(TypedDict):
    id: str
    name: str
    role: str | None
    organization: str | None


class CreateSpaceRequest(TypedDict):
    name: str


class BaseData(TypedDict):
    id: str
    name: str
    spaceId: str


class CreateBaseRequest(TypedDict):
    name: str
    spaceId: str


class TableData(TypedDict):
    id: str
    name: str
    baseId: str
    dbTableName: str | None
    description: str | None
    icon: str | None
    order: int | None
    lastModifiedTime: str | None
    defaultViewId: str | None


class CreateTableRequest(TypedDict):
    name: str
    baseId: str

