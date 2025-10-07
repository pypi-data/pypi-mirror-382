from furthrmind.collection.baseclass import BaseClass
from typing_extensions import List, Self, Dict, TYPE_CHECKING
from inspect import isclass

if TYPE_CHECKING:
    from furthrmind.collection.comboboxentry import ComboBoxEntry


class Field(BaseClass):
    """
    Attributes
    ----------
    id : str
        id of the field
    name : str
        name of the field
    type : str
        Corresponding field type. One out of:

            - Numeric for numeric fields
            - NumericRange for numeric range fields
            - Date for date fields
            - SingleLine for text fields
            - ComboBox for list fields
            - MultiLine for notebook fields
            - Checkbox for checkbox fields
            - Calculation for calculation fields

    script : str
        In case of a calculation field, this attribute holds the script applied for the calculations
    comboboxentries : List[ComboBoxEntry]
        In case of a list field, this attribute holds all attached list options as [ComboBoxEntry](comboboxentry.md)
        objects. Otherwise it is an empty list.
    """

    id = ""
    name = ""
    type = ""
    script = ""
    comboboxentries: List["ComboBoxEntry"] = []

    _attr_definition = {
        "comboboxentries": {"class": "ComboBoxEntry"}
    }

    def __init__(self, id=None, data=None):
        super().__init__(id, data)

    def _get_url_instance(self, project_id=None):
        project_url = Field.fm.get_project_url(project_id)
        url = f"{project_url}/fields/{self.id}"
        return url

    @classmethod
    def _get_url_class(cls, id, project_id=None):
        project_url = cls.fm.get_project_url(project_id)
        url = f"{project_url}/fields/{id}"
        return url

    @classmethod
    def _get_all_url(cls, project_id=None):
        project_url = cls.fm.get_project_url(project_id)
        url = f"{project_url}/fields"
        return url

    @classmethod
    def _post_url(cls, project_id=None):
        project_url = cls.fm.get_project_url(project_id)
        url = f"{project_url}/fields"
        return url

    @classmethod
    def get(cls, id: str = "", name: str = "", project_id: str = "") -> Self:
        """
        Method to get all one field by its id or name
        If called on the instance of a class, the id of the instance is used

        Parameters
        ----------
        id : str
            id of the requested field
        name : str
            name of the requested field
        project_id : str, optional
            Optionally to get a field from another project as the furthrmind sdk was initiated with

        Returns
        -------
        Self
            Instance of the field class

        Raises
        ------
        AssertionError
            If called as class method and neither id nor name is specified
        """

        if isclass(cls):
            assert id or name, "Either id or name must be specified"
        return cls._get(id, name=name, project_id=project_id)

    @classmethod
    def get_many(cls, ids: List[str] = (), names: List[str] = (), project_id: str = "") -> List[Self]:
        """
        Method to get many fields belonging to one project

        Parameters
        ----------
        ids : list of str, optional
            List of ids to get fields for.

        names : list of str, optional
            List of names to get fields for.

        project_id : str, optional
            Optionally to get fields from another project as the furthrmind sdk was initiated with

        Returns
        -------
        list[Self]
            List of instances of the experiment class.

        Raises
        ------
        AssertionError
            If neither ids nor names are specified.

        """

        assert ids or names, "Either ids or names must be specified"
        return cls._get_many(ids, names=names, project_id=project_id)

    @classmethod
    def get_all(cls, project_id: str = "") -> List[Self]:
        """
        Method to get all fields belonging to one project

        Parameters
        ----------
        project_id : str, optional
            Optionally to get fields from another project as the furthrmind sdk was initiated with

        Returns
        -------
        List[Self]
            A list of instances of the field class, representing all the fields belonging to the specified project.
        """

        return cls._get_all(project_id=project_id)

    @classmethod
    @BaseClass._create_instances_decorator(_fetched=False)
    def create(cls, name: str, type: str, project_id: str = "") -> Self:

        """
        Method to create a new field

        Parameters
        ----------
        name : str
            The name of the field to be created.
        type : str
            The field type of the field. Must be one of the following. Lower or uppercase is not considered,
                i.e. Numeric or numeric is both valid:
                - Numeric fields: numeric, numeric-field, numeric_field
                - Numeric range fields: numericrange, numeric_range, numericrangefield, numeric-range-field, numeric_range_field
                - Date fields: date, date_field, date-field, datefield
                - Text fields: singleline, singlelinefield, text, text-field, text_field, textfield
                - List fields: combobox, comboboxfield, list, list-field, list_field, listfield
                - Notebook fields: multiline, notebook, notebookfield, notebook-field, notebook_field
                - Checkbox fields: checkbox, checkbox-field, checkbox_field, checkboxfield
                - Calculation fields: calculation, calculation-field, calculation_field, calculationfield
        project_id : str, optional
            Optionally, the ID of the project to create an item in. If not provided, the item will be created in the project associated with the furthrmind SDK.

        Returns
        -------
        instance of the sample class
            The created sample instance.

        Raises
        ------
        ValueError
            If name is empty or if type is not one of the allowed types.

        """

        if not name:
            raise ValueError("Name cannot be empty")

        type = cls._check_field_type(type)
        data = {"name": name, "type": type}
        id = cls._post(data, project_id)
        data["id"] = id
        return data

    @classmethod
    def _check_field_type(cls, field_type: str):
        field_type_mapping = {
            "Numeric": ["numeric", "numeric-field", "numeric_field", "numericfield"],
            "NumericRange": ["numericrange", "numeric_range", "numericrangefield", "numeric-range-field","numeric_range_field"],
            "Date": ["date", "date_field", "date-field", "datefield"],
            "SingleLine": ["singleline", "single-line", "single_line", "singlelinefield", "single-line-field",
                           "single_line_field", "text", "text-field", "text_field", "textfield"],
            "ComboBox": ["combobox", "comboboxfield", "combobox-field", "combobox_field", "comboboxentry",
                         "list", "listfield", "list-field", "list_field"],
            "MultiLine": ["multiline", "multi_line", "mulit-line", "multilinefield", "multi-line-field",
                          "multi_line_field", "notebook-field", "notebook_field", "notebookfield"],
            "CheckBox": ["checkbox", "checkbox-field", "checkbox_field", "checkboxfield"],
            "Calculation": ["calculation", "calculation-field", "calculation_field", "calculationfield"],
        }
        for field_type_server in field_type_mapping:
            if field_type.lower() in field_type_mapping[field_type_server]:
                return field_type_server

        raise ValueError("Wrong field type")

    @classmethod
    @BaseClass._create_instances_decorator(_fetched=False)
    def create_many(cls, data_list: List[Dict], project_id=None) -> List[Self]:
        """
        Method to create multiple fields

        Parameters
        ----------
        data_list : List[Dict]
            A list of dictionaries containing the data for creating multiple samples. Each dictionary should
            have the following keys:
            - name : str
                The name of the field to be created.
            - type : str
                The field type of the field. Must be one of the following. Lower or uppercase is not considered,
                i.e. Numeric or numeric is both valid:
                - Numeric fields: numeric, numeric-field, numeric_field
                - Numeric range fields: numericrange, numeric_range, numericrangefield, numeric-range-field, numeric_range_field
                - Date fields: date, date_field, date-field, datefield
                - Text fields: singleline, singlelinefield, text, text-field, text_field, textfield
                - List fields: combobox, comboboxfield, list, list-field, list_field, listfield
                - Notebook fields: multiline, notebook, notebookfield, notebook-field, notebook_field
                - Checkbox fields: checkbox, checkbox-field, checkbox_field, checkboxfield
                - Calculation fields: calculation, calculation-field, calculation_field, calculationfield
        project_id : int, optional
            Optionally to create fields in another project as the furthrmind sdk was initiated with

        Returns
        -------
        List[Self]
            A list of instance of the field class that have been created.

        Raises
        ------
        ValueError
            When the "name" key is missing or empty in any of the dictionaries in data_list.
        ValueError
            When the "type" value is not one of: Numeric, Date, SingleLine, ComboBox, MultiLine, CheckBox, Calculation.


        Examples
        --------
        data_list = [
            {"name": "Field 1", "type": "Numeric"},
            {"name": "Field 2", "type": "SingleLine"},
            {"name": "Field 3", "type": "Date"},
            {"name": "Field 4", "type": "ComboBox"},
        ]

        fields = ClassName.create_many(data_list)

        """

        for data in data_list:
            if not "name" in data:
                raise ValueError("Name cannot be empty")

            field_type = cls._check_field_type(data.get("type"))
            data["type"] = field_type

        id_list = cls._post(data_list, project_id, force_list=True)
        for data, id in zip(data_list, id_list):
            data["id"] = id
        return data_list
