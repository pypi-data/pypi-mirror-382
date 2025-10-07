from inspect import isclass

from typing_extensions import Self, Dict, List, TYPE_CHECKING

from furthrmind.collection.baseclass import (BaseClassWithFieldData, BaseClassWithFiles,
                                             BaseClassWithGroup, BaseClass,
                                             BaseClassWithLinking, BaseClassWithNameUpdate, BaseClassWithProtected)
from furthrmind.utils import instance_overload

if TYPE_CHECKING:
    from furthrmind.collection import FieldData, Experiment, ResearchItem, Group, DataTable, File


class Sample(BaseClassWithFieldData,
             BaseClassWithFiles, BaseClassWithGroup,
             BaseClassWithLinking, BaseClassWithNameUpdate, BaseClassWithProtected, BaseClass):
    """
    Attributes
    ----------
    id : str
        id of the sample
    name : str
        name of the sample
    shortid : str
        shortid of the sample
    protected: bool
        Indicates, if the sample is protected in frontend. Does not protect the item for changes made by the api
    files : List[File]
        List of files belonging to this sample. See [File](file.md) for more information.
    fielddata : List[FieldData]
        List of field data belonging to this sample. See [FieldData](fielddata.md) for more information.
    linked_samples : List[Sample]
        This list contains 'sample' objects linked to the current sample. These objects are partially fetched,
        providing only the name and ID. To retrieve the entire object, invoke the 'get()' method on the 'sample'.
        Refer to nested objects in [Getting Started](index.md) for further details. For a comprehensive understanding of
        'sample' objects, see the provided [Sample](sample.md).
    linked_experiments : List[Experiment]
        This list contains 'experiment' objects linked to the current sample. These objects are partially fetched,
        providing only the name and ID. To retrieve the entire object, invoke the 'get()' method on the 'experiment'.
        Refer to nested objects in [Getting Started](index.md) for further details. For a comprehensive understanding of
        'experiment' objects, see the provided [Experiment](experiment.md).
    linked_researchitems : Dict[str, List[ResearchItem]]
        This is a dictionary with category name as keys and lists with the corresponding `researchitem` objects as values.
        The `researchitem` objects are partially fetched,
        providing only the name and ID. To retrieve the entire object, invoke the 'get()' method on the 'researchitem'.
        Refer to nested objects in [Getting Started](index.md) for further details. For a comprehensive understanding of
        'researchitem' objects, see the provided [ResearchItem](researchitem.md).
    groups : List[Group]
        This list contains 'group' objects the sample belongs to. These objects are partially fetched,
        providing only the name and ID. To retrieve the entire object, invoke the 'get()' method on the 'group'.
        Refer to nested objects in [Getting Started](index.md) for further details. For a comprehensive understanding of
        'group' objects, see the provided [Group](group.md).
    datatables : List[DataTable]
        This list contains 'datatable' objects that belong to this sample. These objects are partially fetched,
        providing only the name and ID. To retrieve the entire object, invoke the 'get()' method on the 'datatable'.
        Refer to nested objects in [Getting Started](index.md) for further details. For a comprehensive understanding of
        'datatable' objects, see the provided [DataTable](datatable.md).
    _fetched : bool
        This is a Boolean attribute indicating whether all attributes have been retrieved from the server or only
        the name and ID are present.
    """

    id = ""
    name = ""
    neglect = False
    protected = False
    shortid = ""
    files: List["File"] = []
    fielddata: List["FieldData"] = []
    linked_experiments: List["Experiment"] = []
    linked_samples: List[Self] = []
    linked_researchitems: Dict[str, List["ResearchItem"]] = {}
    groups: List["Group"] = []
    datatables: List["DataTable"] = []

    _attr_definition = {
        "files": {"class": "File"},
        "fielddata": {"class": "FieldData"},
        "groups": {"class": "Group"},
        "linked_samples": {"class": "Sample"},
        "linked_experiments": {"class": "Experiment"},
        "linked_researchitems": {"class": "ResearchItem", "nested_dict": True},
        "datatables": {"class": "DataTable"}
    }

    def __init__(self, id=None, data=None):
        super().__init__(id, data)
        # create instance methods for certain class_methods
        instance_methods = ["get"]
        instance_overload(self, instance_methods)

    def _get_url_instance(self, project_id=None):
        project_url = Sample.fm.get_project_url(project_id)
        url = f"{project_url}/samples/{self.id}"
        return url

    @classmethod
    def _get_url_class(cls, id, project_id=None):
        project_url = cls.fm.get_project_url(project_id)
        url = f"{project_url}/samples/{id}"
        return url

    @classmethod
    def _get_all_url(cls, project_id=None):
        project_url = cls.fm.get_project_url(project_id)
        url = f"{project_url}/samples"
        return url

    @classmethod
    def _post_url(cls, project_id=None):
        project_url = cls.fm.get_project_url(project_id)
        url = f"{project_url}/samples"
        return url

    @classmethod
    def get(cls, id: str = "", name: str = "", shortid: str = "", project_id: str = "") -> Self:
        """
        Method to get one sample by its id, short_id, or name.
        If called on an instance of the class, the id of the instance is used

        Parameters
        ----------
        id : str
            The id or short_id of the requested sample.
        name : str
            The name of the requested sample.
        shortid : str
            The shortid of the requested sample.
        project_id : str, optional
            Optionally to get the sample from another project as the furthrmind sdk was initiated with

        Returns
        -------
        Self
            An instance of the sample class.

        Raises
        ------
        AssertionError
            If called as a class method and no id, shortid, or name is specified.

        """

        if isclass(cls):
            assert id or name or shortid, "Either id, shortid, or name must be specified"

        return cls._get(id, shortid, name, project_id=project_id)

    @classmethod
    def get_many(cls, ids: List[str] = (), shortids: List[str] = (), names: List[str] = (),
                 project_id: str = None) -> List[Self]:
        """
        Method to get many samples by its ids, short_ids, or names.

        Parameters
        ----------
        ids : List[str]
            List of sample ids to filter samples by.
        shortids : List[str]
            List of short ids to filter samples by.
        names : List[str]
            List of names to filter samples by.
        project_id : str, optional
            Optionally to get samples from another project as the furthrmind sdk was initiated with

        Returns
        -------
        List[Self]
            List of instances of the sample class.

        Raises
        ------
        AssertionError
            If neither ids, shortids, nor names are specified.

        """

        assert ids or names or shortids, "Either ids, shortids, or names must be specified"
        return cls._get_many(ids, shortids, names, project_id=project_id)

    @classmethod
    def get_all(cls, project_id: str = "") -> List[Self]:
        """
        Method to get all samples belonging to one project

        Parameters
        ----------
        project_id : str, optional
            Optionally to get samples from another project as the furthrmind sdk was initiated with

        Returns
        -------
        List[Self]
            List of instances of the `Sample` class representing the fetched samples.
        """

        return cls._get_all(project_id)

    @classmethod
    @BaseClass._create_instances_decorator(_fetched=False)
    def create(cls, name: str, group_name: str = None, group_id: str = None, project_id: str = None) -> Self:
        """
        Method to create a new sample.

        Parameters
        ----------
        name : str
            The name of the sample to be created.

        group_name : str, optional
            The name of the group where the new item will belong to. Group name can only be considered for groups that are not subgroups.
            Either group_name or group_id must be specified.

        group_id : int, optional
            The ID of the group where the new item will belong to.
            Either group_name or group_id must be specified.
        project_id : str, optional
            Optionally to get samples from another project as the furthrmind sdk was initiated with

        Returns
        -------
        Self
            An instance of the sample class.

        Raises
        ------
        AssertionError
            If neither group_name nor group_id is specified.

        """

        return Sample._create(name, group_name, group_id, project_id)

    @classmethod
    @BaseClass._create_instances_decorator(_fetched=False)
    def create_many(cls, data_list: List[Dict], project_id: str = None) -> Self:
        """
        Method to create many samples.

        Parameters
        ----------
        data_list : List[Dict]
            A list of dictionaries representing the data for creating multiple samples. Each dictionary should have the following keys:
            - 'name': The name of the sample to be created.
            - 'group_name': The name of the group where the new item will belong to. The 'group_name' can only be considered for groups
                            that are not subgroups. Either 'group_name' or 'group_id' must be specified.
            - 'group_id': The id of the group where the new item will belong to. Either 'group_name' or 'group_id' must be specified.

        project_id : str, optional
            Optionally to get samples from another project as the furthrmind sdk was initiated with

        Returns
        -------
        List[Sample]
            A list of instances of the 'Sample' class, representing the created samples.

        Raises
        ------
        AssertionError
            If neither group_name nor group_id is specified.

        """

        return Sample._create_many(data_list, project_id)

    def add_datatable(self, name: str, columns: List[Dict] = None, project_id: str = None) -> "DataTable":
        """
        Method to create a new datatable and add within a sample.

        Parameters
        ----------
        name: str
            Name of the datatable
        columns: List[Dict], optional
            A list of columns that should be added to the datatable. Each column is represented by a dictionary with the following keys:
            - name: str
                Name of the column
            - type: str
                Type of the column. Either "Text" or "Numeric". Data must fit the specified type. For Text, all data
                will be converted to a string and for Numeric, all data will be converted to a float (if possible)
            - data: List
                List of column values. Values must fit the specified column type
            - unit: Union[Dict, str], optional
                Dictionary with an id or name, or a name as a string, or an id as a string representing the unit
        project_id: str, optional
            Optionally create the datatable in another project as the furthrmind sdk was initiated with

        Returns
        -------
        DataTable
            Instance of the datatable class
        """

        from furthrmind.collection import DataTable
        datatable = DataTable.create(name, sample_id=self.id, columns=columns, project_id=project_id)

        new_datatable = list(self.datatables)
        new_datatable.append(datatable)
        self.datatables = new_datatable

        return datatable
