from furthrmind.collection.baseclass import BaseClassWithFieldData, BaseClass
from typing_extensions import List, Dict, Self, TYPE_CHECKING
from inspect import isclass
if TYPE_CHECKING:
    from furthrmind.collection import File, FieldData, Experiment, Sample, ResearchItem


class Group(BaseClassWithFieldData):
    """
    Attributes
    ----------
    id : str
        id of the group
    name : str
        name of the group
    shortid : str
        shortid of the group
    files : List[File]
        List of files belonging to this group. See [File](file.md) for more information.
    fielddata : List[FieldData]
        List of field data belonging to this group. See [FieldData](fielddata.md) for more information.
    samples : List[Sample]
        This list contains 'sample' objects belonging to this group. These objects are partially fetched,
        providing only the name and ID. To retrieve the entire object, invoke the 'get()' method on the 'sample'.
        Refer to nested objects in [Getting Started](index.md) for further details. For a comprehensive understanding of
        'sample' objects, see the provided [Sample](sample.md).
    experiments : List[Experiment]
        This list contains 'experiment' objects belonging to this group. These objects are partially fetched,
        providing only the name and ID. To retrieve the entire object, invoke the 'get()' method on the 'experiment'.
        Refer to nested objects in [Getting Started](index.md) for further details. For a comprehensive understanding of
        'experiment' objects, see the provided [Experiment](experiment.md).
    researchitems : Dict[str, List[ResearchItem]]
        This is a dictionary with category name as keys and lists with the corresponding `researchitem` objects belonging
         to this group as values. The `researchitem` objects are partially fetched,
        providing only the name and ID. To retrieve the entire object, invoke the 'get()' method on the 'researchitem'.
        Refer to nested objects in [Getting Started](index.md) for further details. For a comprehensive understanding of
        'researchitem' objects, see the provided [ResearchItem](researchitem.md).
    sub_groups : List[Group]
        This list contains 'group' objects that are subgroups of this group. These objects are partially fetched,
        providing only the name and ID. To retrieve the entire object, invoke the 'get()' method on the 'group'.
        Refer to nested objects in [Getting Started](index.md) for further details. For a comprehensive understanding of
        'group' objects, see the provided [Group](group.md).
    parent_group : Group
        If the group is a subgroup, the attribute holds its parent group. This object is partially fetched,
        providing only the name and ID. To retrieve the entire object, invoke the 'get()' method on the 'group'.
        Refer to nested objects in [Getting Started](index.md) for further details. For a comprehensive understanding of
        'group' objects, see the provided [Group](group.md).
    _fetched : bool
        This is a Boolean attribute indicating whether all attributes have been retrieved from the server or only
        the name and ID are present.
    """

    id = ""
    name = ""
    neglect = False
    shortid = ""
    files: List["File"] = []
    fielddata: List["FieldData"] = []
    experiments: List["Experiment"] = []
    samples: List["Sample"] = []
    researchitems: Dict[str, List["ResearchItem"]] = {}
    sub_groups: List[Self] = []
    parent_group: Self = None

    _attr_definition = {
        "files": {"class": "File"},
        "fielddata": {"class": "FieldData"},
        "samples": {"class": "Sample"},
        "experiments": {"class": "Experiment"},
        "researchitems": {"class": "ResearchItem", "nested_dict": True},
        "sub_groups": {"class": "Group"},
        "parent_group": {"class": "Group"}
    }

    def __init__(self, id=None, data=None):
        super().__init__(id, data)

    def _get_url_instance(self, project_id=None):
        project_url = Group.fm.get_project_url(project_id)
        url = f"{project_url}/groups/{self.id}"
        return url

    @classmethod
    def _get_url_class(cls, id, project_id=None):
        project_url = cls.fm.get_project_url(project_id)
        url = f"{project_url}/groups/{id}"
        return url

    @classmethod
    def _get_all_url(cls, project_id=None):
        project_url = cls.fm.get_project_url(project_id)
        url = f"{project_url}/groups"
        return url

    @classmethod
    def _post_url(cls, project_id=None):
        project_url = cls.fm.get_project_url(project_id)
        url = f"{project_url}/groups"
        return url

    @classmethod
    def get(cls, id: str = "", name: str = "", shortid: str = "", parent_group_id: str = "", project_id: str = "") -> Self:
        """
        Method to get one group by its id, name, or shortid.
        If called on an instance of the class, the id of the class is used.

        Parameters
        ----------
        id : str
            id or short_id of requested group
        name : str
            name of requested group. For subgroups, see parent_group_id parameter
        shortid : str
            shortid of requested group
        parent_group_id : str
            id of parent group.
            If a subgroup is requested, the name and the parent_group_id is required
        project_id : str, optional
            Optionally to get a group from another project as the furthrmind sdk was initiated with.
            Defaults to None

        Returns
        -------
        Self
            Instance of group class

        Raises
        ------
        AssertionError
            When used as a class method, id, name, or shortid must be specified.

        """

        if isclass(cls):
            assert id or name or shortid, "Either id or name must be specified"

        return cls._get(id, shortid, name, parent_group_id=parent_group_id, project_id=project_id)

    @classmethod
    def get_many(cls, ids: List[str] = (), shortids: List[str] = (), names: List[str] = (),
                 project_id: str = "") -> List[Self]:
        """
        Method to get many groups

        Parameters
        ----------
        ids : List[str]
            List of ids to filter the groups.
        shortids : List[str]
            List of short_ids to filter the groups.
        names : List[str]
            List of names to filter the groups.
        project_id : str, optional
            Optionally to get groups from another project as the furthrmind sdk was initiated with

        Returns
        -------
        List[Self]
            List of instances of the Group class.

        Raises
        ------
        AssertionError
            If none of the parameters (ids, shortids, or names) are specified.

        """

        assert ids or names or shortids, "Either ids, shortids, or names must be specified"
        return cls._get_many(ids, shortids, names, project_id=project_id)

    @classmethod
    def get_all(cls, project_id: str = "") -> List[Self]:
        """
        Method to get all groups belonging to one project

        Parameters
        ----------
        project_id : str, optional
            Optionally to get groups from another project as the furthrmind sdk was initiated with

        Returns
        -------
        List[Self]
            A list of instances of the group class.

        """

        return super()._get_all(project_id)
    
    @classmethod
    @BaseClass._create_instances_decorator(_fetched=False)
    def create(cls, name: str, parent_group_id: str = "", project_id: str = "") -> Self:
        """
        Method to create a new group.

        Parameters
        ----------
        name: str
            The name of the item to be created.
        parent_group_id: str, optional
            The ID of the parent group where the new group should belong to. Defaults to an empty string.
        project_id: str, optional
            Optionally, create a group in another project as the furthrmind SDK was initiated with

        Returns
        -------
        instance of the group class
        """

        data = {"name": name}
        if parent_group_id:
            data["parent_group"] = {"id": parent_group_id}
        id = cls._post(data, project_id)
        data["id"] = id
        return data

    @classmethod
    @BaseClass._create_instances_decorator(_fetched=False)
    def create_many(cls, name_list: List[str], project_id: str = "") -> List[Self]:
        """
        Method to create multiple groups

        Parameters
        ----------
        name_list: List[str]
            A list containing names of the groups to be created.
        project_id: str, optional
            Optionally to create groups in another project as the furthrmind sdk was initiated with

        Returns
        -------
        List[Self]
            A list containing instances of the group class corresponding to the groups created.

        """

        data_list = [{"name": name} for name in name_list]

        id_list = cls._post(data_list, project_id, force_list=True)

        for data, id in zip(data_list, id_list):
            data["id"] = id

        return data_list
