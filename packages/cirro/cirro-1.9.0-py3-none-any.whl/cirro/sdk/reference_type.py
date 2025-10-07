from cirro_api_client.v1.models import ReferenceType

from cirro.sdk.asset import DataPortalAssets, DataPortalAsset


class DataPortalReferenceType(DataPortalAsset):
    """
    Reference data is organized by project, categorized by type.
    """

    def __init__(self, ref_type: ReferenceType):
        self._data = ref_type

    @property
    def name(self):
        """Name of reference type"""
        return self._data.name

    @property
    def description(self):
        """Description of reference type"""
        return self._data.description

    @property
    def directory(self):
        return self._data.directory

    @property
    def validation(self):
        return self._data.validation

    def __str__(self):
        return '\n'.join([
            f"{i.title()}: {self.__getattribute__(i)}"
            for i in ['name', 'description']
        ])


class DataPortalReferenceTypes(DataPortalAssets[DataPortalReferenceType]):
    """Collection of DataPortalReferenceType objects."""
    asset_name = "reference type"

    def get_by_id(self, _id: str) -> DataPortalReferenceType:
        raise NotImplementedError("Filtering by ID is not supported, use get_by_name")
