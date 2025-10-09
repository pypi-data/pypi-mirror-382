from pydantic import BaseModel, Field
from typing import Annotated, Generic, Literal, Optional, TypeVar, Union
from maleo.enums.environment import Environment
from maleo.enums.service import Key, Name


KeyT = TypeVar("KeyT", bound=Key)
NameT = TypeVar("NameT", bound=Name)


class MaleoClientConfig(BaseModel, Generic[KeyT, NameT]):
    environment: Environment = Field(..., description="Client's environment")
    key: KeyT = Field(..., description="Client's key")
    name: NameT = Field(..., description="Client's name")
    url: str = Field(..., description="Client's URL")


class MaleoTelemetryClientConfig(
    MaleoClientConfig[Literal[Key.TELEMETRY], Literal[Name.TELEMETRY]]
):
    key: Annotated[
        Literal[Key.TELEMETRY], Field(Key.TELEMETRY, description="Client's key")
    ] = Key.TELEMETRY
    name: Annotated[
        Literal[Name.TELEMETRY], Field(Name.TELEMETRY, description="Client's name")
    ] = Name.TELEMETRY


class MaleoTelemetryClientConfigMixin(BaseModel):
    telemetry: MaleoTelemetryClientConfig = Field(
        ..., description="MaleoTelemetry client's configuration"
    )


class MaleoMetadataClientConfig(
    MaleoClientConfig[Literal[Key.METADATA], Literal[Name.METADATA]]
):
    key: Annotated[
        Literal[Key.METADATA], Field(Key.METADATA, description="Client's key")
    ] = Key.METADATA
    name: Annotated[
        Literal[Name.METADATA], Field(Name.METADATA, description="Client's name")
    ] = Name.METADATA


class MaleoMetadataClientConfigMixin(BaseModel):
    metadata: MaleoMetadataClientConfig = Field(
        ..., description="MaleoMetadata client's configuration"
    )


class MaleoIdentityClientConfig(
    MaleoClientConfig[Literal[Key.IDENTITY], Literal[Name.IDENTITY]]
):
    key: Annotated[
        Literal[Key.IDENTITY], Field(Key.IDENTITY, description="Client's key")
    ] = Key.IDENTITY
    name: Annotated[
        Literal[Name.IDENTITY], Field(Name.IDENTITY, description="Client's name")
    ] = Name.IDENTITY


class MaleoIdentityClientConfigMixin(BaseModel):
    identity: MaleoIdentityClientConfig = Field(
        ..., description="MaleoIdentity client's configuration"
    )


class MaleoAccessClientConfig(
    MaleoClientConfig[Literal[Key.ACCESS], Literal[Name.ACCESS]]
):
    key: Annotated[
        Literal[Key.ACCESS], Field(Key.ACCESS, description="Client's key")
    ] = Key.ACCESS
    name: Annotated[
        Literal[Name.ACCESS], Field(Name.ACCESS, description="Client's name")
    ] = Name.ACCESS


class MaleoAccessClientConfigMixin(BaseModel):
    access: MaleoAccessClientConfig = Field(
        ..., description="MaleoAccess client's configuration"
    )


class MaleoWorkshopClientConfig(
    MaleoClientConfig[Literal[Key.WORKSHOP], Literal[Name.WORKSHOP]]
):
    key: Annotated[
        Literal[Key.WORKSHOP], Field(Key.WORKSHOP, description="Client's key")
    ] = Key.WORKSHOP
    name: Annotated[
        Literal[Name.WORKSHOP], Field(Name.WORKSHOP, description="Client's name")
    ] = Name.WORKSHOP


class MaleoWorkshopClientConfigMixin(BaseModel):
    workshop: MaleoWorkshopClientConfig = Field(
        ..., description="MaleoWorkshop client's configuration"
    )


class MaleoResearchClientConfig(
    MaleoClientConfig[Literal[Key.RESEARCH], Literal[Name.RESEARCH]]
):
    key: Annotated[
        Literal[Key.RESEARCH], Field(Key.RESEARCH, description="Client's key")
    ] = Key.RESEARCH
    name: Annotated[
        Literal[Name.RESEARCH], Field(Name.RESEARCH, description="Client's name")
    ] = Name.RESEARCH


class MaleoResearchClientConfigMixin(BaseModel):
    research: MaleoResearchClientConfig = Field(
        ..., description="MaleoResearch client's configuration"
    )


class MaleoRegistryClientConfig(
    MaleoClientConfig[Literal[Key.REGISTRY], Literal[Name.REGISTRY]]
):
    key: Annotated[
        Literal[Key.REGISTRY], Field(Key.REGISTRY, description="Client's key")
    ] = Key.REGISTRY
    name: Annotated[
        Literal[Name.REGISTRY], Field(Name.REGISTRY, description="Client's name")
    ] = Name.REGISTRY


class MaleoRegistryClientConfigMixin(BaseModel):
    registry: MaleoRegistryClientConfig = Field(
        ..., description="MaleoRegistry client's configuration"
    )


class MaleoSOAPIEClientConfig(
    MaleoClientConfig[Literal[Key.SOAPIE], Literal[Name.SOAPIE]]
):
    key: Annotated[
        Literal[Key.SOAPIE], Field(Key.SOAPIE, description="Client's key")
    ] = Key.SOAPIE
    name: Annotated[
        Literal[Name.SOAPIE], Field(Name.SOAPIE, description="Client's name")
    ] = Name.SOAPIE


class MaleoSOAPIEClientConfigMixin(BaseModel):
    soapie: MaleoSOAPIEClientConfig = Field(
        ..., description="MaleoSOAPIE client's configuration"
    )


class MaleoMedixClientConfig(
    MaleoClientConfig[Literal[Key.MEDIX], Literal[Name.MEDIX]]
):
    key: Annotated[Literal[Key.MEDIX], Field(Key.MEDIX, description="Client's key")] = (
        Key.MEDIX
    )
    name: Annotated[
        Literal[Name.MEDIX], Field(Name.MEDIX, description="Client's name")
    ] = Name.MEDIX


class MaleoMedixClientConfigMixin(BaseModel):
    medix: MaleoMedixClientConfig = Field(
        ..., description="MaleoMedix client's configuration"
    )


class MaleoDICOMClientConfig(
    MaleoClientConfig[Literal[Key.DICOM], Literal[Name.DICOM]]
):
    key: Annotated[Literal[Key.DICOM], Field(Key.DICOM, description="Client's key")] = (
        Key.DICOM
    )
    name: Annotated[
        Literal[Name.DICOM], Field(Name.DICOM, description="Client's name")
    ] = Name.DICOM


class MaleoDICOMClientConfigMixin(BaseModel):
    dicom: MaleoDICOMClientConfig = Field(
        ..., description="MaleoDICOM client's configuration"
    )


class MaleoScribeClientConfig(
    MaleoClientConfig[Literal[Key.SCRIBE], Literal[Name.SCRIBE]]
):
    key: Annotated[
        Literal[Key.SCRIBE], Field(Key.SCRIBE, description="Client's key")
    ] = Key.SCRIBE
    name: Annotated[
        Literal[Name.SCRIBE], Field(Name.SCRIBE, description="Client's name")
    ] = Name.SCRIBE


class MaleoScribeClientConfigMixin(BaseModel):
    scribe: MaleoScribeClientConfig = Field(
        ..., description="MaleoScribe client's configuration"
    )


class MaleoCDSClientConfig(MaleoClientConfig[Literal[Key.CDS], Literal[Name.CDS]]):
    key: Annotated[Literal[Key.CDS], Field(Key.CDS, description="Client's key")] = (
        Key.CDS
    )
    name: Annotated[Literal[Name.CDS], Field(Name.CDS, description="Client's name")] = (
        Name.CDS
    )


class MaleoCDSClientConfigMixin(BaseModel):
    cds: MaleoCDSClientConfig = Field(
        ..., description="MaleoCDS client's configuration"
    )


class MaleoImagingClientConfig(
    MaleoClientConfig[Literal[Key.IMAGING], Literal[Name.IMAGING]]
):
    key: Annotated[
        Literal[Key.IMAGING], Field(Key.IMAGING, description="Client's key")
    ] = Key.IMAGING
    name: Annotated[
        Literal[Name.IMAGING], Field(Name.IMAGING, description="Client's name")
    ] = Name.IMAGING


class MaleoImagingClientConfigMixin(BaseModel):
    imaging: MaleoImagingClientConfig = Field(
        ..., description="MaleoImaging client's configuration"
    )


class MaleoMCUClientConfig(MaleoClientConfig[Literal[Key.MCU], Literal[Name.MCU]]):
    key: Annotated[Literal[Key.MCU], Field(Key.MCU, description="Client's key")] = (
        Key.MCU
    )
    name: Annotated[Literal[Name.MCU], Field(Name.MCU, description="Client's name")] = (
        Name.MCU
    )


class MaleoMCUClientConfigMixin(BaseModel):
    mcu: MaleoMCUClientConfig = Field(
        ..., description="MaleoMCU client's configuration"
    )


AnyMaleoClientConfig = Union[
    MaleoTelemetryClientConfig,
    MaleoMetadataClientConfig,
    MaleoIdentityClientConfig,
    MaleoAccessClientConfig,
    MaleoWorkshopClientConfig,
    MaleoResearchClientConfig,
    MaleoRegistryClientConfig,
    MaleoSOAPIEClientConfig,
    MaleoMedixClientConfig,
    MaleoDICOMClientConfig,
    MaleoScribeClientConfig,
    MaleoCDSClientConfig,
    MaleoImagingClientConfig,
    MaleoMCUClientConfig,
]
AnyMaleoClientConfigT = TypeVar("AnyMaleoClientConfigT", bound=AnyMaleoClientConfig)


class MaleoClientsConfig(BaseModel):
    pass


MaleoClientsConfigT = TypeVar("MaleoClientsConfigT", bound=Optional[MaleoClientsConfig])
