""" opentrons_shared_data.labware.types: types for labware defs

types in this file by and large require the use of typing_extensions.
this module shouldn't be imported unless typing.TYPE_CHECKING is true.
"""
from typing import NewType
from typing_extensions import Literal, TypedDict, NotRequired
from .constants import (
    CircularType,
    RectangularType,
)

LabwareUri = NewType("LabwareUri", str)

LabwareDisplayCategory = Literal[
    "tipRack",
    "tubeRack",
    "reservoir",
    "trash",
    "wellPlate",
    "aluminumBlock",
    "adapter",
    "other",
    "lid",
    "system",
]

LabwareFormat = Literal[
    "96Standard",
    "384Standard",
    "trough",
    "irregular",
    "trash",
]

LabwareRoles = Literal[
    "labware",
    "fixture",
    "adapter",
    "maintenance",
    "lid",
    "system",
]

SpringDirectionalForce = Literal["backLeftBottom"]


class Vector2D(TypedDict):
    x: float
    y: float


class Vector3D(TypedDict):
    x: float
    y: float
    z: float


class AxisAlignedBoundingBox2D(TypedDict):
    backLeft: Vector2D
    frontRight: Vector2D


class AxisAlignedBoundingBox3D(TypedDict):
    backLeftBottom: Vector3D
    frontRightTop: Vector3D


class GripperOffsets(TypedDict):
    pickUpOffset: Vector3D
    dropOffset: Vector3D


class LabwareParameters2(TypedDict):
    format: LabwareFormat
    isTiprack: bool
    loadName: str
    isMagneticModuleCompatible: bool
    isDeckSlotCompatible: NotRequired[bool]
    quirks: NotRequired[list[str]]
    tipLength: NotRequired[float]
    tipOverlap: NotRequired[float]
    magneticModuleEngageHeight: NotRequired[float]


class LabwareParameters3(LabwareParameters2, TypedDict):
    pass  # Currently equivalent to LabwareParameters2.


class LabwareBrandData(TypedDict):
    brand: str
    brandId: NotRequired[list[str]]
    links: NotRequired[list[str]]


class LabwareMetadata(TypedDict):
    displayName: str
    displayCategory: LabwareDisplayCategory
    displayVolumeUnits: Literal["µL", "mL", "L"]
    tags: NotRequired[list[str]]


class LabwareDimensions(TypedDict):
    yDimension: float
    zDimension: float
    xDimension: float


class _WellCommon2(TypedDict):
    depth: float
    totalLiquidVolume: float
    x: float
    y: float
    z: float
    geometryDefinitionId: NotRequired[str | None]


class CircularWellDefinition2(_WellCommon2, TypedDict):
    shape: CircularType
    diameter: float


class RectangularWellDefinition2(_WellCommon2, TypedDict):
    shape: RectangularType
    xDimension: float
    yDimension: float


WellDefinition2 = CircularWellDefinition2 | RectangularWellDefinition2


class CircularWellDefinition3(CircularWellDefinition2, TypedDict):
    # Currently equivalent to CircularWellDefinition2.
    pass


class RectangularWellDefinition3(RectangularWellDefinition2, TypedDict):
    # Currently equivalent to RectangularWellDefinition2.
    pass


WellDefinition3 = CircularWellDefinition3 | RectangularWellDefinition3


class WellGroupMetadata(TypedDict):
    displayName: NotRequired[str]
    displayCategory: NotRequired[LabwareDisplayCategory]
    wellBottomShape: NotRequired[Literal["flat", "u", "v"]]


class WellGroup(TypedDict):
    wells: list[str]
    metadata: WellGroupMetadata
    brand: NotRequired[LabwareBrandData]


class Extents(TypedDict):
    total: AxisAlignedBoundingBox3D


class SlotFootprintAsChildFeature(TypedDict):
    z: float
    backLeft: Vector2D
    frontRight: Vector2D
    springDirectionalForce: NotRequired[SpringDirectionalForce]


class SlotFootprintAsParentFeature(TypedDict):
    z: float
    backLeft: Vector2D
    frontRight: Vector2D
    springDirectionalForce: NotRequired[SpringDirectionalForce]


class OpentronsFlexTipRackLidAsParentFeature(TypedDict):
    matingZ: float


class OpentronsFlexTipRackLidAsChildFeature(TypedDict):
    matingZ: float


class LocatingFeatures(TypedDict):
    """A dictionary of locating features."""

    slotFootprintAsChild: NotRequired[SlotFootprintAsChildFeature]
    slotFootprintAsParent: NotRequired[SlotFootprintAsParentFeature]
    springDirectionalForceAsParent: NotRequired[SpringDirectionalForce]
    opentronsFlexTipRackLidAsParent: NotRequired[OpentronsFlexTipRackLidAsParentFeature]
    opentronsFlexTipRackLidAsChild: NotRequired[OpentronsFlexTipRackLidAsChildFeature]


class LabwareDefinition2(TypedDict):
    schemaVersion: Literal[2]
    version: int
    namespace: str
    metadata: LabwareMetadata
    brand: LabwareBrandData
    parameters: LabwareParameters2
    cornerOffsetFromSlot: Vector3D
    ordering: list[list[str]]
    dimensions: LabwareDimensions
    wells: dict[str, WellDefinition2]
    groups: list[WellGroup]
    stackingOffsetWithLabware: NotRequired[dict[str, Vector3D]]
    stackingOffsetWithModule: NotRequired[dict[str, Vector3D]]
    allowedRoles: NotRequired[list[LabwareRoles]]
    gripperOffsets: NotRequired[dict[str, GripperOffsets]]
    gripForce: NotRequired[float]
    gripHeightFromLabwareBottom: NotRequired[float]
    stackLimit: NotRequired[int]
    compatibleParentLabware: NotRequired[list[str]]
    # The innerLabwareGeometry dict values are not currently modeled in these
    # TypedDict-based bindings. The only code that cares about them
    # currentlyuses our Pydantic-based bindings instead.
    innerLabwareGeometry: NotRequired[dict[str, object] | None]


# Class to mix in the "$otSharedSchema" key. This cannot be defined with the normal
# TypedDict class syntax because it contains a dollar sign.
_OTSharedSchemaMixin = TypedDict(
    "_OTSharedSchemaMixin", {"$otSharedSchema": Literal["#/labware/schemas/3"]}
)


class LabwareDefinition3(_OTSharedSchemaMixin, TypedDict):
    schemaVersion: Literal[3]
    # $otSharedSchema mixed in via subclassing
    version: int
    namespace: str
    metadata: LabwareMetadata
    brand: LabwareBrandData
    parameters: LabwareParameters3
    ordering: list[list[str]]
    features: LocatingFeatures
    extents: Extents
    wells: dict[str, WellDefinition3]
    groups: list[WellGroup]
    stackingOffsetWithLabware: NotRequired[dict[str, Vector3D]]
    stackingOffsetWithModule: NotRequired[dict[str, Vector3D]]
    allowedRoles: NotRequired[list[LabwareRoles]]
    gripperOffsets: NotRequired[dict[str, GripperOffsets]]
    gripForce: NotRequired[float]
    gripHeightFromLabwareOrigin: NotRequired[float]
    stackLimit: NotRequired[int]
    compatibleParentLabware: NotRequired[list[str]]
    # The innerLabwareGeometry dict values are not currently modeled in these
    # TypedDict-based bindings. The only code that cares about them
    # currentlyuses our Pydantic-based bindings instead.
    innerLabwareGeometry: NotRequired[dict[str, object] | None]


LabwareDefinition = LabwareDefinition2 | LabwareDefinition3
