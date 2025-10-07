from inspect import isclass

from typing_extensions import List, Self, Dict, TYPE_CHECKING

from furthrmind.collection.baseclass import BaseClassWithFieldData, BaseClass

if TYPE_CHECKING:
    from furthrmind.collection import File, FieldData


class ComboBoxEntry(BaseClassWithFieldData):
    """
    ComboBoxEntries represent the available options in a list field

    Attributes
    ----------
    id : str
        id of the column
    name : str
        name of the column
    files : List[File]
        List of files belonging to this comboboxentry. See [File](file.md) for more information.
    fielddata : List[FieldData]
        List of field data belonging to this comboboxentry. See [FieldData](fielddata.md) for more information.
    _fetched : bool
        This is a Boolean attribute indicating whether all attributes have been retrieved from the server or only
        the name and ID are present.
    """

    id = ""
    name = ""
    files: List["File"] = []
    fielddata: List["FieldData"] = []

    _attr_definition = {
        "files": {"class": "File"},
        "fielddata": {"class": "FieldData"}
    }

    def __init__(self, id=None, data=None):
        super().__init__(id, data)

    def _get_url_instance(self, project_id=None):
        project_url = ComboBoxEntry.fm.get_project_url(project_id)
        url = f"{project_url}/comboboxentry/{self.id}"
        return url

    @classmethod
    def _get_url_class(cls, id, project_id=None):
        project_url = cls.fm.get_project_url(project_id)
        url = f"{project_url}/comboboxentry/{id}"
        return url

    @classmethod
    def _get_all_url(cls, project_id=None):
        project_url = cls.fm.get_project_url(project_id)
        url = f"{project_url}/comboboxentry"
        return url

    @classmethod
    def _post_url(cls, project_id=None):
        project_url = cls.fm.get_project_url(project_id)
        url = f"{project_url}/comboboxentry"
        return url

    @classmethod
    def get(cls, id: str = "", project_id: str = "") -> Self:
        """
        Method to get one combobox entry
        If called on an instance of the class, the id of the instance is used

        Parameters
        ----------
        id : str
            id of the requested comboboxentry
        project_id : str
            Optionally, to get a comboboxentry from another project as the furthrmind sdk was initiated with

        Returns
        -------
        Self
            Instance of the ComboBoxEntry class

        Raises
        ------
        AssertionError
            If used as class method and id not specified

        """

        if isclass(cls):
            assert id, "id must be specified"

        return cls._get(id, project_id=project_id)

    # noinspection PyMethodOverriding
    @classmethod
    def get_many(cls, ids: List[str] = (), project_id: str = "") -> List[Self]:
        """
        This method is a class method that retrieves multiple comboboxentries belonging to one project.

        Parameters
        ----------
        ids : List[str]
            List with ids.

        project_id : str, optional
            Optionally to get comboboxentries from another project as the furthrmind sdk was initiated with,
            defaults to an empty string.

        Returns
        -------
        List[Self]
            List with instances of experiment class.

        Raises
        ------
        AssertError
            If `ids` list is empty.

        """

        assert ids, "ids must be specified"
        return cls._get_many(ids, project_id=project_id)

    @classmethod
    def get_all(cls, project_id: str = "") -> List[Self]:
        """
        Method to get all comboboxentries belonging to one project.

        Parameters
        ----------
        project_id : str, optional
            Optionally to get comboboxentries from another project as the furthrmind sdk was initiated with

        Returns
        -------
        List[Self]
            A list containing instances of the comboboxentry class.
        """

        return cls._get_all(project_id=project_id)

    @classmethod
    @BaseClass._create_instances_decorator(_fetched=False)
    def create(cls, name: str, field_name: str = "", field_id: str = "", project_id: str = "") -> Self:
        """
        Method to create a new combobox entry

        Parameters
        ----------
        name: str
            Name of the combobox entry.
        field_name: str, optional
            Name of the field where the combobox entry should belong to. Either the field name or id must be provided.
        field_id: str, optional
            Id of the field where the combobox entry should belong to. Either the field name or id must be provided.
        project_id: str, optional
            Id of the project where the combobox entry should be created. This is only required if the combobox entry needs to
            be created in a different project than the one the SDK was initiated with.

        Returns
        -------
        Self
            Instance of the column comboboxentry class.

        Raises
        ------
        ValueError
            If the name is not specified.
        ValueError
            If neither field_name nor field_id is provided.
        ValueError
            If the field with the given name is not found.
        """

        from furthrmind.collection.field import Field

        if not name:
            raise ValueError("Name must be specified")
        if not field_name and not field_id:
            raise ValueError("Either field_name or field_id must be provided")

        if field_name:
            fields = Field._get_all(project_id)
            for field in fields:
                if field.name.lower() == field_name.lower():
                    field_id = field.id
                    break

            if not field_id:
                raise ValueError("Field with given name not found")

        data = {"name": name, "field": {"id": field_id}}
        id = cls._post(data, project_id)
        data["id"] = id
        return data

    @classmethod
    @BaseClass._create_instances_decorator(_fetched=False)
    def create_many(cls, data_list: List[Dict], project_id: str = "") -> List[Self]:
        """
        Method to create many new combobox entries

        Parameters
        ----------
        data_list : List[Dict]
            List of dictionaries containing the data for creating instances of comboboxentry class. Each dictionary
            should have the following keys:

            - "name" (str): Name of the combobox entry.
            - "field_name" (str, optional): Name of the field where the combobox entry should belong to. Either
                "field_name" or "field_id" must be provided.
            - "field_id" (str, optional): ID of the field where the combobox entry should belong to. Either "field_name"
                or "field_id" must be provided.

        project_id : str, optional
            ID of the project where the combobox entries should be created. If not provided, the items will be created
            in the current project.

        Returns
        -------
        List[Self]
            List of instances of comboboxentry class that were created.

        Raises
        ------
        ValueError
            If any of the following conditions are met:

            - "name" is missing in any of the dictionaries in "data_list".
            - Both "field_name" and "field_id" are missing in any of the dictionaries in "data_list".
            - The provided "field_name" does not match any existing field in the project.

        """

        from furthrmind.collection.field import Field

        look_for_field_ids = False
        for data in data_list:
            if not data.get("name"):
                raise ValueError("Name must be specified")

            if data.get("field_name"):
                look_for_field_ids = True
                break

        if look_for_field_ids:
            fields = Field._get_all(project_id)
            for data in data_list:
                field_name = data.get("field_name")
                field_id = data.get("field_id")
                if not field_name and not field_id:
                    raise ValueError("Either field_name or field_id must be provided")
                if field_name:
                    for field in fields:
                        if field.name.lower() == field_name.lower():
                            field_id = field.id
                            data["field_id"] = field_id
                            break
                    if not data.get("field_id"):
                        raise ValueError(f"Field with given name '{field_name}' not found")

        new_data_list = []
        for data in data_list:
            new_data_list.append({
                "name": data.get("name"),
                "field": {"id": data.get("field_id")}
            })

        id_list = cls._post(new_data_list, project_id, force_list=True)
        for data, id in zip(new_data_list, id_list):
            data["id"] = id

        return new_data_list
