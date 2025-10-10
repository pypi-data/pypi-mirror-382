from __future__ import annotations

from typing import Any, List, Optional, Union

from pydantic import BaseModel, ConfigDict, Field


class PublicRegisterModel(BaseModel):
    """Base model with common configuration for Public Register data."""

    model_config = ConfigDict(populate_by_name=True, extra="allow")


class Metadata(PublicRegisterModel):
    publisher: str
    licence: str
    documentation: str
    has_format: Optional[List[str]] = Field(None, alias="hasFormat")
    version: Optional[str] = None
    comment: Optional[str] = None
    limit: Optional[int] = None
    offset: Optional[int] = None


class Register(PublicRegisterModel):
    id: str = Field(..., alias="@id")
    label: Optional[str] = None
    type: Optional[dict[str, Any]] = None


class Holder(PublicRegisterModel):
    id: str = Field(..., alias="@id")
    name: Union[str, List[str]]
    trading_name: Optional[str] = Field(None, alias="tradingName")


class HolderSummary(Holder):
    type: Optional[Union[str, List[str]]] = None


class HolderTypeReference(PublicRegisterModel):
    id: str = Field(..., alias="@id")


class HolderDetail(Holder):
    type: Optional[Union[HolderTypeReference, List[HolderTypeReference]]] = None


class PostcodeReference(PublicRegisterModel):
    id: str = Field(..., alias="@id")


class Address(PublicRegisterModel):
    address: Union[str, List[str]]
    postcode: Optional[Union[str, int]] = None
    organization_name: Optional[str] = Field(None, alias="organization_name")
    street_address: Optional[Union[str, int, List[str]]] = Field(None, alias="street_address")
    locality: Optional[str] = None


class AddressSummary(Address):
    postcode_uri: Optional[Union[str, PostcodeReference]] = Field(
        None, alias="postcodeURI"
    )


class AddressDetail(Address):
    postcode_uri: Optional[Union[str, PostcodeReference]] = Field(
        None, alias="postcodeURI"
    )


class Site(PublicRegisterModel):
    id: str = Field(..., alias="@id")
    site_address: Optional[Union[AddressSummary, AddressDetail]] = Field(
        None, alias="siteAddress"
    )


class SiteLocation(PublicRegisterModel):
    easting: float
    northing: float
    grid_reference: Optional[str] = Field(None, alias="gridReference")


class SiteDetail(Site):
    location: Optional[SiteLocation] = None
    premises: Optional[str] = None
    site_type: Optional[dict[str, Any]] = Field(None, alias="siteType")


class RegistrationType(PublicRegisterModel):
    id: str = Field(..., alias="@id")
    notation: Optional[str] = None
    label: Optional[str] = None
    pref_label: Optional[str] = Field(None, alias="prefLabel")
    see_also: Optional[Union[str, dict[str, str]]] = Field(None, alias="seeAlso")


class LocalAuthority(PublicRegisterModel):
    id: str = Field(..., alias="@id")
    label: str


class Tier(PublicRegisterModel):
    id: Optional[str] = Field(None, alias="@id")
    label: Optional[str] = None


class RDFType(PublicRegisterModel):
    id: str = Field(..., alias="@id")


class GenericRegistration(PublicRegisterModel):
    id: str = Field(..., alias="@id")
    register_: Register = Field(..., alias="register")
    registration_number: Union[str, int] = Field(..., alias="registrationNumber")

    @property
    def register(self) -> Register:
        """Expose the register field without shadowing BaseModel.register."""
        return self.register_


class GenericRegistrationSummary(GenericRegistration):
    type: Optional[List[str]] = None
    holder: Optional[Union[HolderSummary, List[HolderSummary]]] = None


class GenericRegistrationDetail(GenericRegistration):
    type: List[RDFType] = Field(default_factory=list)
    holder: Optional[Union[HolderDetail, List[HolderDetail]]] = None


class RegistrationSummary(GenericRegistrationSummary):
    expiry_date: Optional[str] = Field(None, alias="expiryDate")
    registration_date: Optional[str] = Field(None, alias="registrationDate")
    local_authority: Optional[LocalAuthority] = Field(None, alias="localAuthority")
    registration_type: Optional[RegistrationType] = Field(
        None, alias="registrationType"
    )
    site: Optional[Union[Site, List[Site]]] = None
    tier: Optional[Tier] = None
    distance: Optional[float] = None


class RegistrationDetail(GenericRegistrationDetail):
    label: Optional[str] = None
    notation: Optional[str] = None
    expiry_date: Optional[str] = Field(None, alias="expiryDate")
    registration_date: Optional[str] = Field(None, alias="registrationDate")
    registration_type: Optional[RegistrationType] = Field(
        None, alias="registrationType"
    )
    site: Optional[Union[Site, SiteDetail]] = None
    tier: Optional[Tier] = None
    local_authority: Optional[LocalAuthority] = Field(None, alias="localAuthority")


class RegistrationSearchResponse(PublicRegisterModel):
    meta: Metadata
    items: List[RegistrationSummary] = Field(default_factory=list)
