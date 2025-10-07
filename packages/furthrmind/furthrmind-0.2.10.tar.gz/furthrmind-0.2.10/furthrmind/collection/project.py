from furthrmind.collection.baseclass import BaseClass
from typing_extensions import List, Dict, Self, TYPE_CHECKING
from inspect import isclass
if TYPE_CHECKING:
    from furthrmind.collection import Sample, Experiment, Group, Unit, ResearchItem, Field

class Project(BaseClass):
    """
    Attributes
    ----------
    id : str
        id of the project
    name : str
        name of the project
    shortid : str
        shortid of the project
    info : str
        Detailed information about the project
    samples : List[Sample]
        This list contains 'sample' objects belonging to this project. These objects are partially fetched,
        providing only the name and ID. To retrieve the entire object, invoke the 'get()' method on the 'sample'.
        Refer to nested objects in [Getting Started](index.md) for further details. For a comprehensive understanding of
        'sample' objects, see the provided [Sample](sample.md).
    experiments : List[Experiment]
        This list contains 'experiment' objects belonging to this project. These objects are partially fetched,
        providing only the name and ID. To retrieve the entire object, invoke the 'get()' method on the 'experiment'.
        Refer to nested objects in [Getting Started](index.md) for further details. For a comprehensive understanding of
        'experiment' objects, see the provided [Experiment](experiment.md).
    researchitems : Dict[str, List[ResearchItem]]
        This is a dictionary with category name as keys and lists with the corresponding `researchitem` objects belonging
        to this project as values. The `researchitem` objects are partially fetched,
        providing only the name and ID. To retrieve the entire object, invoke the 'get()' method on the 'researchitem'.
        Refer to nested objects in [Getting Started](index.md) for further details. For a comprehensive understanding of
        'researchitem' objects, see the provided [ResearchItem](researchitem.md).
    groups : List[Group]
        This list contains 'group' objects that belong to this project. These objects are partially fetched,
        providing only the name and ID. To retrieve the entire object, invoke the 'get()' method on the 'group'.
        Refer to nested objects in [Getting Started](index.md) for further details. For a comprehensive understanding of
        'group' objects, see the provided [Group](group.md).
    units : List[Unit]
        This list contains all unit objects that belong to this project. For more information about the unit object, please
        refer to [Unit](unit.md).
    fields : List[Field]
        This list contains all fields that belong to this project. Each entry is a [Field](field.md) object.
    permissions : Dict
        This is a dictionary containing various keys. The `owner` key represents the owner of the project.
        The `users` key refers to a list of users granted access to this project, including their respective access levels.
        Lastly, the `usergroups` key relates to a list of usergroups with access privileges to this project, also presenting
        their respective access levels.
    _fetched : bool
        This is a Boolean attribute indicating whether all attributes have been retrieved from the server or only
        the name and ID are present.
    """

    id = ""
    name = ""
    info = ""
    shortid = ""
    samples: List["Sample"] = []
    experiments: List["Experiment"] = []
    groups: List["Group"] = []
    units: List["Unit"] = []
    researchitems: Dict[str, List["ResearchItem"]] = {}
    permissions: Dict[str, List] = {}
    fields: List["Field"] = []

    _attr_definition = {
        "samples": {"class": "Sample"},
        "experiments": {"class": "Experiment"},
        "groups": {"class": "Group"},
        "units": {"class": "Unit"},
        "researchitems": {"class": "ResearchItem", "nested_dict": True},
        "fields": {"class": "Field"}
    }

    def __init__(self, id=None, data=None):
        super().__init__(id, data)

    def _get_url_instance(self):
        project_url = self.fm.get_project_url(self.id)
        return project_url

    @classmethod
    def _get_url_class(cls, id, project_id=None):
        project_url = cls.fm.get_project_url(id)
        return project_url

    @classmethod
    def _get_all_url(cls, project_id=None):
        return f"{cls.fm.base_url}/projects"

    @classmethod
    def _post_url(cls):
        return f"{cls.fm.base_url}/projects"
    
    @classmethod
    def get(cls, id: str = "", name: str = "") -> Self:
        """
        This method is used to get one project by its id or name.
        If called on an instance of the class, the id of the class is used.
        Either id or name must be specified.

        Parameters
        ----------
        id : str, optional
            id or short_id of the requested project.
            Default value is an empty string.
        name : str, optional
            name of the requested project.
            Default value is an empty string.

        Returns
        -------
        Self
            Instance of the project class.

        """

        if isclass(cls):
            assert id or name, "Either id or name must be specified"

        return cls._get(id=id, name=name)


    @classmethod
    def get_many(cls, ids: List[str] = (), names: List[str] = ()) -> List[Self]:
        """
        Method to get many projects

        Parameters
        ----------
        ids : List[str]
            List of ids.

        names : List[str]
            List of names.

        Returns
        -------
        List[Self]
            List of instances of the class.

        Raises
        ------
        AssertionError
            If neither ids nor names are specified.
        """
        pass

        assert ids or names, "Either ids or names must be specified"
        return cls._get_many(ids, names)

    @classmethod
    def get_all(cls) -> List[Self]:
        """
        Method to get all projects

        Returns
        -------
        List[Self]
            List of instances of the class.

        """

        return super()._get_all()

    @classmethod
    @BaseClass._create_instances_decorator(_fetched=False)
    def create(cls, name: str) -> Self:
        """
        Method to create a new project

        Parameters
        ----------
        name : str
            Name of the new project

        Returns
        -------
        Self
            Instance of the project class

        Raises
        ------
        ValueError
            If name is empty or None

        """

        if not name:
            raise ValueError("Name is required")
        data = {"name": name}
        id = cls._post(data)
        data["id"] = id
        return data




