from inspect import isclass

from typing_extensions import Self, List, Dict, TYPE_CHECKING

from furthrmind.collection.baseclass import (BaseClassWithFieldData,
                                             BaseClassWithFiles,
                                             BaseClassWithGroup,
                                             BaseClassWithLinking,
                                             BaseClass, BaseClassWithNameUpdate, BaseClassWithProtected
                                             )

if TYPE_CHECKING:
    from furthrmind.collection import FieldData, Sample, Group, ResearchItem, DataTable, File


class Experiment(BaseClassWithFieldData, BaseClassWithFiles,
                 BaseClassWithGroup, BaseClassWithLinking, BaseClassWithNameUpdate, BaseClassWithProtected):
    """
    Attributes
    ----------
    id : str
        id of the experiment
    name : str
        name of the experiment
    shortid : str
        shortid of the experiment
    protected: bool
        Indicates, if the experiment is protected in frontend. Does not protect the item for changes made by the api
    files : List[File]
        List of files belonging to this experiment. See [File](file.md) for more information.
    fielddata : List[FieldData]
        List of field data belonging to this experiment. See [FieldData](fielddata.md) for more information.
    linked_samples : List[Sample]
        This list contains 'sample' objects linked to the current experiment. These objects are partially fetched,
        providing only the name and ID. To retrieve the entire object, invoke the 'get()' method on the 'sample'.
        Refer to nested objects in [Getting Started](index.md) for further details. For a comprehensive understanding of
        'sample' objects, see the provided [Sample](sample.md).
    linked_experiments : List[Experiment]
        This list contains 'experiment' objects linked to the current experiment. These objects are partially fetched,
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
        This list contains 'group' objects the experiment belongs to. These objects are partially fetched,
        providing only the name and ID. To retrieve the entire object, invoke the 'get()' method on the 'group'.
        Refer to nested objects in [Getting Started](index.md) for further details. For a comprehensive understanding of
        'group' objects, see the provided [Group](group.md).
    datatables : List[DataTable]
        This list contains 'datatable' objects that belong to this experiment. These objects are partially fetched,
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
    linked_samples: List["Sample"] = []
    linked_experiments: List[Self] = []
    groups: List["Group"] = []
    linked_researchitems: Dict[str, List["ResearchItem"]] = []
    datatables: List["DataTable"] = []

    _attr_definition = {
        "files": {"class": "File"},
        "fielddata": {"class": "FieldData"},
        "linked_samples": {"class": "Sample"},
        "linked_experiments": {"class": "Experiment"},
        "groups": {"class": "Group"},
        "linked_researchitems": {"class": "ResearchItem", "nested_dict": True},
        "datatables": {"class": "DataTable"}
    }

    def __init__(self, id=None, data=None):
        super().__init__(id, data)

    def _get_url_instance(self, project_id=None):
        project_url = Experiment.fm.get_project_url(project_id)
        url = f"{project_url}/experiments/{self.id}"
        return url

    @classmethod
    def _get_url_class(cls, id, project_id=None):
        project_url = cls.fm.get_project_url(project_id)
        url = f"{project_url}/experiments/{id}"
        return url

    @classmethod
    def _get_all_url(cls, project_id: str = None) -> str:
        project_url = cls.fm.get_project_url(project_id)
        url = f"{project_url}/experiments"
        return url

    @classmethod
    def _post_url(cls, project_id=None):
        project_url = cls.fm.get_project_url(project_id)
        url = f"{project_url}/experiments"
        return url

    @classmethod
    def get(cls, id: str = None, name: str = None, shortid: str = "", project_id: str = "") -> Self:
        """
        Method to get one experiment by its id, name, or short_id
        If called on an instance of the class, the id of the class is used

        Parameters
        ----------
        id : str, optional
            The ID of the experiment to retrieve. If not provided, the ID of the calling instance will be used.
        name : str, optional
            The name of the experiment to retrieve.
        shortid : str, optional
            The short ID of the experiment to retrieve.
        project_id : str, optional
            Optionally to get an experiment from another project as the furthrmind sdk was initiated with

        Returns
        -------
        Self
            An instance of the experiment class.

        Raises
        ------
        AssertionError
            If neither ID nor name nor shortid is specified.

        Example usage:
            experiment = Experiment.get(id='ex123')
        """

        if isclass(cls):
            assert id or name or shortid, "Either id, name, or shortid must be specified"

        return cls._get(id, shortid, name, project_id=project_id)

    @classmethod
    def get_many(cls, ids: List[str] = (), shortids: List[str] = (), names: List[str] = (), project_id: str = "") -> \
            List[Self]:
        """
        Method to get all experiment belonging to one project

        Parameters
        ----------
        ids : List[str]
            List of experiment ids.
        shortids : List[str]
            List of experiment short ids.
        names : List[str]
            List of experiment names.
        project_id : str, optional
            Optionally to get experiments from another project as the furthrmind sdk was initiated with

        Returns
        -------
        List[Self]
            List of instances of the experiment class.

        Raises
        ------
        AssertionError
            If none of the ids, shortids, or names are specified.

        """

        assert ids or names or shortids, "Either ids, shortids, or names must be specified"
        return cls._get_many(ids, shortids, names, project_id=project_id)

    @classmethod
    def get_all(cls, project_id: str = "") -> List[Self]:
        """
        Method to get all experiment belonging to one project

        Parameters
        ----------
        project_id : str, optional
            Optionally to get experiments from another project as the furthrmind sdk was initiated with

        Returns
        -------
        List[Self]
            A list containing instances of the experiment class.
        """

        return cls._get_all(project_id=project_id)

    @classmethod
    @BaseClass._create_instances_decorator(_fetched=False)
    def create(cls, name: str, group_name: str = "", group_id: str = "", project_id: str = "") -> Self:
        """
        Method to create a new experiment

        Parameters
        ----------
        name : str
            The name of the item to be created
        group_name : str, optional
            The name of the group where the new item will belong to. Group name can be only considered for groups that
            are not subgroups. Either group_name or group_id must be specified.
        group_id : str, optional
            The id of the group where the new item will belong to. Either group_name or group_id must be specified.
        project_id : str, optional
            Optionally, to create an item in another project as the furthrmind sdk was initiated with.

        Returns
        -------
        Experiment instance
            The instance of the experiment class created.

        """

        return cls._create(name, group_name, group_id, project_id)

    @classmethod
    @BaseClass._create_instances_decorator(_fetched=False)
    def create_many(cls, data_list: List[Dict], project_id: str = "") -> List[Self]:
        """
        Parameters
        ----------
        data_list : List[Dict]
            List of dictionaries containing information about the experiments to be created.
            Each dictionary should have the following keys:

            - name: str
                The name of the experiment.
            - group_name : str
                The name of the group where the experiment will belong to.
                Only applicable for groups that are not subgroups. Either group_name or group_id must be specified.
            - group_id : str
                The ID of the group where the experiment will belong to. Either group_name or group_id must be specified.

        project_id : str, optional
            Optionally to create an item in another project as the furthrmind sdk was initiated with

        Returns
        -------
        List[Self]
            List of instances of the experiment class.

        """

        return cls._create_many(data_list, project_id)

    def add_datatable(self, name: str, columns: List[Dict], project_id: str = "") -> "DataTable":
        """
        Method to create a new datatable within this experiment. Add the created datatable to the datatables attribute

        Parameters
        ----------
        name : str
            Name of the datatable.
        columns : List[Dict]
            A list of columns that should be added to the datatable. Each column is represented as a dictionary with the
            following keys:

            - name : str
                Name of the column.</br>
            - type : str
                Type of the column. Either "Text" or "Numeric". Data must fit the specified type.
            - data : Union[List[Union[str, float]], pandas.Series]
                List of column values. Data must fit the specified type of the column.
                For Text columns, the items must be convertable to strings
                For Numeric columns, the items must be convertable to floats.
                Can be a list or a pandas.Series.
            - unit : dict or str
                Unit of the column. It can be represented as either a dictionary with 'id' or 'name', or a string
                representing the name or id of the unit.
        project_id : str, optional
            Optionally, specify the id of another project to create the datatable in.

        Returns
        -------
        DataTable
            An instance of the DataTable class representing the created datatable.

        """

        from furthrmind.collection import DataTable
        datatable = DataTable.create(name, experiment_id=self.id, columns=columns, project_id=project_id)

        new_datatables = list(self.datatables)
        new_datatables.append(datatable)
        self.datatables = new_datatables

        return datatable
