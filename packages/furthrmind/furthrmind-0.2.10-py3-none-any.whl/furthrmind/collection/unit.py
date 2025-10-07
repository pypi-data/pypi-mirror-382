from furthrmind.collection.baseclass import BaseClass
from typing_extensions import Self, List, Dict
from inspect import isclass

class Unit(BaseClass):
    """
    Attributes
    ----------
    id : str
        id of the unit
    name : str
        name of the unit
    longname : str
        Long name of the unit. In case of "cm" this would be centimeter
    definition : str
        In case of self defined units, this attributes gives the definition of the unit in si units
    """

    id = ""
    name = ""
    longname = ""
    definition = ""

    _attr_definition = {
    }

    def __init__(self, id=None, data=None):
        super().__init__(id, data)

    def _get_url_instance(self, project_id=None):
        project_url = Unit.fm.get_project_url(project_id)
        url = f"{project_url}/units/{self.id}"
        return url

    @classmethod
    def _get_url_class(cls, id, project_id=None):
        project_url = cls.fm.get_project_url(project_id)
        url = f"{project_url}/units/{id}"
        return url

    @classmethod
    def _get_all_url(cls, project_id=None):
        project_url = cls.fm.get_project_url(project_id)
        url = f"{project_url}/units"
        return url

    @classmethod
    def _post_url(cls, project_id=None):
        project_url = cls.fm.get_project_url(project_id)
        url = f"{project_url}/units"
        return url
    
    @classmethod
    def get(cls, id: str = None) -> Self:
        """
        Method to get one unit.
        If called on an instance of the class, the id of the instance is used

        Parameters
        ----------
        id : str, optional
            The id of the unit to be retrieved. If not specified, the id of the instance is used.

        Returns
        -------
        Self
            An instance of the unit class.

        """

        if isclass(cls):
            assert id, "id must be specified"
            return cls._get_class_method(id)
        else:
            self = cls
            data = self._get_instance_method()
            return data

    @classmethod
    def get_many(cls, ids: List[str] = (), project_id=None) -> List[Self]:
        """
        This method is used to retrieve many units belonging to one project.

        Parameters
        ----------
        ids : List[str]
            List of ids.
        project_id : str, optional
            The project id. Defaults to None.

        Returns
        -------
        List[Self]
            List of instances of the experiment class.

        Raises
        ------
        TypeError
            If ids is not a list.
        """

        return super()._get_many(ids, project_id=project_id)

    @classmethod
    def get_all(cls, project_id=None) -> List[Self]:
        """
        Method to get all units belonging to one project

        Parameters
        ----------
        project_id : str
            Optionally specify the project ID to get units from. Defaults to None.

        Returns
        -------
        List[Self]
            A list containing instances of the unit class.
        """

        return super()._get_all(project_id)

    @classmethod
    @BaseClass._create_instances_decorator(_fetched=False)
    def create(cls, name: str, definition: str = None, project_id: str = None) -> Self:
        """
        Method to create a new unit.

        Parameters
        ----------
        name : str
            Name of the new unit
        definition : str, optional
            Unit definition in SI units to convert the new unit to an SI value. E.g. for unit cm², the definition would be 'cm*cm'.
            For valid units, please check the web app and open the unit editor. You will find a list of valid units. A definition may also contain scalar values.
        project_id : any, optional
            Project ID to create an item in another project

        Returns
        -------
        Self
            Instance of the unit class

        Raises
        ------
        AssertationError
            If name is not provided
        """

        assert name, "Name must be provided"

        data = {"name": name, "definition": definition}
        id = cls._post(data, project_id)
        data["id"] = id
        return data

    @classmethod
    @BaseClass._create_instances_decorator(_fetched=False)
    def create_many(cls, data_list: List[Dict], project_id: str = None) -> Self:
        """
        Parameters
        ----------
        data_list : List[Dict]
            A list of dictionaries containing the information for creating new units.
            Each dictionary should have the following keys:
            - name : str
                Name of the new unit.
            - definition : str
                Unit definition in SI units to convert the new unit to an SI Value.
                For example, for unit cm², the definition would be 'cm * cm'.
                For valid units, please check the web app unit editor.
                A definition can also contain scalar values.

        project_id : str, optional
            Optionally to create an item in another project as the furthrmind sdk was initiated with

        Returns
        -------
        List[Self]
            A list with instances of the unit class

        Raises
        ------
        AssertationError
            If the name parameter is missing for any unit in the data_list.
        """

        new_data_list = []
        for data in data_list:
            name = data.get("name")
            definition = data.get("definition")

            assert name, "Name is required"

            data = {"name": name, "definition": definition}
            new_data_list.append(data)

        id_list = cls._post(new_data_list, project_id, force_list=True)
        for data, id in zip(new_data_list, id_list):
            data["id"] = id

        return new_data_list
