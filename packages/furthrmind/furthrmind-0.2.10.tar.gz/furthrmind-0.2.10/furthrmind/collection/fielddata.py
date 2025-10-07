from datetime import datetime, date, timezone
from inspect import isclass
from bson import ObjectId
from typing_extensions import List, TYPE_CHECKING, Dict, Tuple, Union, Self

from furthrmind.collection.baseclass import BaseClass
from furthrmind.utils import instance_overload

if TYPE_CHECKING:
    from furthrmind.collection.unit import Unit


class FieldData(BaseClass):
    """
    Attributes
    ----------
    id : str
        id of the fielddata
    field_name : str
        field name of the corresponding field
    field_id : List[File]
        field id of the corresponding field
    field_type : str
        field type of the corresponding field
    value : Any
        value of the fielddata. Type depends on the field type:

            - Numeric fields: float or None
            - Numeric range fields: list of two floats or None
            - Date fields: python datetime object or None
            - Text field: string or None
            - List field: The value will be a dictionary with the name and the id to the selected option (comboboxentry).
                If no option is selected, the value will be None
            - Notebook field: The value will be a dictionary with the id and content of the notebook.
            - Checkbox field: boolean
    si_value : Union[float, None]
        In case of numeric fields, the attribute represents the corresponding si-value considering the selected unit
    unit : [Unit](unit.md)
        The selected unit for numeric fields. Otherwise None
    author: Dict[str, str]
        The author of the fielddata with id and email address

    """
    id = ""
    field_name = ""
    field_id = ""
    field_type = ""
    si_value = None
    unit: "Unit" = None
    author = None
    value = None

    _attr_definition = {
        "unit": {"class": "Unit"},
        "field_name": {"data_key": "fieldname"},
        "field_type": {"data_key": "fieldtype"},
        "field_id": {"data_key": "fieldid"},
    }

    def __init__(self, id=None, data=None):
        super().__init__(id, data)

        # create instance methods for certain class_methods
        instance_methods = ["_check_value_type"]
        instance_overload(self, instance_methods)

    def _update_attributes(self, data):
        super()._update_attributes(data)
        if self.field_type == "Date":
            if self.value:
                if isinstance(self.value, (int, float)):
                    self.value = datetime.fromtimestamp(self.value)
                if isinstance(self.value, str):
                    self.value = datetime.fromisoformat(self.value)

    @classmethod
    def _post_url(cls, project_id=None):
        project_url = cls.fm.get_project_url(project_id)
        url = f"{project_url}/fielddata"
        return url

    @classmethod
    def get(cls, id=None, project_id: str = ""):
        if isclass(cls):
            assert id, "id must be specified"

        return cls._get(id, project_id=project_id)

    @classmethod
    def get_all(cls, project_id=None):
        return cls._get_all(project_id=project_id)
    
    def _get_url_instance(self, project_id=None):
        project_url = FieldData.fm.get_project_url(project_id)
        url = f"{project_url}/fielddata/{self.id}"
        return url

    @classmethod
    def _get_url_class(cls, id, project_id=None):
        project_url = cls.fm.get_project_url(project_id)
        url = f"{project_url}/fielddata/{id}"
        return url
    
    @classmethod
    def _get_all_url(cls, project_id: str = None) -> str:
        project_url = cls.fm.get_project_url(project_id)
        url = f"{project_url}/fielddata"
        return url

    def update_value(self, value) -> str:
        """
        Parameters
        ----------
        value :
            The value to update the fielddata. The valid types for each field type are as follows:

            - numeric, numeric-field, numeric_field: float or int, or a string convertable to a float
            - numeric range, numeric-range-field, numeric_range_field: List with two floats, ints, or strings convertable to a float
            - date, date_field, date-field, datefield: datetime, or date object, or unix timestamp or string with
                iso format
            - singleline, singlelinefield, text, text-field, text_field, textfield: string
            - combobox, comboboxfield, list, list-field, list_field, listfield: dict with id or name as key, or string
                with name, or string with id
            - multiline, notebook, notebookfield, notebook-field, notebook_field: dict with content as key, or string
            - checkbox, checkbox-field, checkbox_field, checkboxfield: boolean

        Returns
        -------
        id : str
            The id of the updated fielddata.
        """

        value, field_type = self.__class__._check_value_type(value, self.field_type)
        data = {"id": self.id,
                "value": value}
        if self.field_type == "Date":
            if isinstance(value, str):
                value = datetime.fromisoformat(value)
            elif isinstance(value, (int, float)):
                value = datetime.fromtimestamp(value)
        id = self._post(data)
        self.value = value
        return id

    def set_calculation_result(self, value: Dict) -> str:
        """
        Parameters
        ----------
        value: dict
            A dictionary representing the calculation result.

        Raises
        ------
        TypeError
            If the field type is not a calculation

        Returns
        -------
        id: str
            The ID of the calculation field.
        """

        if not self.field_type.lower() in ["calculation", "rawdatacalc"]:
            raise TypeError("Only applicable for calculation field")

        url = f"{self.fm.base_url}/set-result/{self.id}"
        response = self.fm.session.post(url, json=value)
        if response.status_code != 200:
            raise ValueError("Setting calculation result failed")
        return self.id

    @classmethod
    def _check_value_type(cls, value, field_type=None) -> Tuple:
        from furthrmind.collection import Field

        if issubclass(cls, BaseClass):
            # classmethod
            if field_type is None:
                raise ValueError("fieldtype must not be None")
        else:
            # instance method
            self = cls
            field_type = self.field_type

        # raises an error or returns: "Numeric", "Date", "SingleLine",
        # "ComboBox", "MultiLine", "CheckBox", "Calculation"
        field_type = Field._check_field_type(field_type)

        if value is None:
            return value, field_type

        if field_type == "Numeric":
            try:
                value = float(value)
            except:
                raise TypeError("Not numeric")
            return value, field_type
        elif field_type == "NumericRange":
            if not isinstance(value, list):
                raise TypeError("Not a list")
            if not len(value) == 2:
                raise TypeError("Not a list with two elements")
            for pos, element in enumerate(value):
                if element is None:
                    continue
                try:
                    element = float(element)
                    value[pos] = element
                except:
                    raise TypeError("Element is not convertible to float")
            return value, field_type

        elif field_type == "Date":
            if isinstance(value, datetime):
                if value.tzinfo is None:
                    return value.isoformat(), field_type
                return int(value.timestamp()), field_type
            if isinstance(value, date):
                value = datetime.combine(value, datetime.min.time())
                if value.tzinfo is None:
                    return value.isoformat(), field_type
                return int(value.timestamp()), field_type
            if isinstance(value, str):
                try:
                    value = datetime.fromisoformat(value)
                    return value, field_type
                except ValueError:
                    raise TypeError("No iso time format")
            if isinstance(value, (int, float)):
                return value, field_type
        elif field_type == "SingleLine":
            if isinstance(value, str):
                return value, field_type
            if isinstance(value, (float, int)):
                return str(value), field_type
            raise TypeError("Type must be string")

        elif field_type == "ComboBox":
            if isinstance(value, dict):
                if "id" in value:
                    return value, field_type
                if "name" in value:
                    return value, field_type
                raise TypeError("The dict must have either id or name key")
            if isinstance(value, str):
                try:
                    value = ObjectId(value)
                    value = {"id": value}
                except:
                    value = {"name": value}
                return value, field_type
            raise TypeError("Only string and dict supported")

        elif field_type == "MultiLine":
            if isinstance(value, dict):
                if "content" not in value:
                    raise TypeError("Key 'content' is required")
                return value, field_type
            if isinstance(value, str):
                value = {"content": value}
                return value, field_type
            raise TypeError("Only string and dict supported")

        elif field_type == "CheckBox":
            if not isinstance(value, bool):
                raise TypeError("value must be a bool")
            return value, field_type
        elif field_type == "Calculation":
            return None, field_type

    def update_unit(self, unit: Union[Dict, str]) -> str:
        """
        Parameters
        ----------
        unit : Union[Dict, str]
            Dictionary with id or name, or string representing the name, or string representing the id.

        Returns
        -------
        id: str
            The id of the updated unit.

        Raises
        ------
        None

        """

        unit = self._check_unit(unit)
        data = {"id": self.id,
                "unit": unit}
        id = self._post(data)
        self.unit = unit
        return id

    @classmethod
    def _check_unit(cls, unit):
        if not unit:
            return unit
        if isinstance(unit, dict):
            if "id" in unit:
                return unit
            if "name" in unit:
                return unit
            raise TypeError("The dict must have either id or name key")

        elif isinstance(unit, str):
            try:
                unit = ObjectId(unit)
                unit = {"id": str(unit)}
            except:
                unit = {"name": unit}
            return unit
        raise TypeError("Only string and dict supported")

    @classmethod
    @BaseClass._create_instances_decorator(_fetched=False)
    def create(cls, field_name: str = "", field_type: str = "", field_id: str = "", value=None, unit=None,
               project_id: str = "") -> Self:
        """
        Parameters
        ----------
        field_name : str, optional
            Name of the field. Either field name and field_type must be specified, or field_id must be specified.
        field_type : str, optional
            Type of the field. Must be one of the following:

                - Numeric fields: numeric, numeric-field, numeric_field
                - Numeric range fields: numericrange, numeric_range, numericrangefield, numeric-range-field, numeric_range_field
                - Date fields: date, date_field, date-field, datefield
                - Text fields: singleline, singlelinefield, text, text-field, text_field, textfield
                - List fields: combobox, comboboxfield, list, list-field, list_field, listfield
                - Notebook fields: multiline, notebook, notebookfield, notebook-field, notebook_field
                - Checkbox fields: checkbox, checkbox-field, checkbox_field, checkboxfield
                - Calculation fields: calculation, calculation-field, calculation_field, calculationfield

        field_id : str, optional
            ID of the field.
        value : None, float, int, str, datetime, date, optional
            Value of the field. The data type depends on the field_type parameter:

                - Numeric fields: float or int, or a string convertible to a float
                - Numeric range fields: List with two floats, ints, or strings convertable to a float
                - Date fields: datetime, date object, unix timestamp, or string with iso format
                - Text fields: string
                - List fields: dictionary with id or name as key, or string with name, or string with id
                - Notebook fields: dictionary with content as key, or string
                - Checkbox fields:  boolean

        unit : dict, str, optional
            Unit of the field. Can be either a dictionary with id or name, or a string with the name.
        project_id : str, optional
            Optionally to create fielddata in another project as the furthrmind sdk was initiated with

        Returns
        -------
        dict
            Instance of the `fielddata` class.

        Raises
        ------
        ValueError
            If field_id not specified, fieldname and fieldtype must be specified.

        """

        from furthrmind.collection import Field
        data = {}
        if field_id:
            data.update({"fieldid": field_id})
            field: Field = Field.get(id=field_id)
            field_type = field.type

        value, field_type = FieldData._check_value_type(value, field_type)
        data["value"] = value

        if not field_id:
            if not field_name or not field_type:
                raise ValueError("fieldname and fieldtype must be specified")
            data.update(
                {"fieldname": field_name, "fieldtype": field_type})

        if unit:
            unit = FieldData._check_unit(unit)
            data["unit"] = unit

        id = FieldData._post(data, project_id)
        data["id"] = id
        return data

    @classmethod
    @BaseClass._create_instances_decorator(_fetched=False)
    def create_many(cls, data_list: List[Dict], project_id: str = "") -> List[Self]:
        """
        Parameters
        ----------
        data_list: List[Dict]
            List with dictionaries containing the following keys:
            - field_name: name of the field. Either field name and field_type must be specified, or field_id must be specified
            - field_type: type of the field. Must be one of the following:

                - Numeric fields: numeric, numeric-field, numeric_field
                - Numeric range fields: numericrange, numeric_range, numericrangefield, numeric-range-field, numeric_range_field
                - Date fields: date, date_field, date-field, datefield
                - Text fields: singleline, singlelinefield, text, text-field, text_field, textfield
                - List fields: combobox, comboboxfield, list, list-field, list_field, listfield
                - Notebook fields: multiline, notebook, notebookfield, notebook-field, notebook_field
                - Checkbox fields: checkbox, checkbox-field, checkbox_field, checkboxfield
                - Calculation fields: calculation, calculation-field, calculation_field, calculationfield

            - field_id: id of the field
            - value:

                - Numeric fields: float or int, or a string convertible to a float
                - Numeric range fields: List with two floats, ints, or strings convertable to a float
                - Date fields: datetime, date object, unix timestamp, or string with iso format
                - Text fields: string
                - List fields: dictionary with id or name as key, or string with name, or string with id
                - Notebook fields: dictionary with content as key, or string
                - Checkbox fields:  boolean

            - unit: dictionary with id or name, or name as string, or id as string

        project_id: str, optional
            Optionally to create an item in another project as the furthrmind sdk was initiated with

        Returns
        -------
        List[Dict]
            List with dictionaries of instances of the fielddata class

        """

        from furthrmind.collection import Field

        post_data_list = []
        for data in data_list:
            field_id = data.get("field_id")
            field_name = data.get("field_name")
            field_type = data.get("field_type")
            value = data.get("value")
            unit = data.get("unit")

            _data = {}
            if field_id:
                _data.update({"fieldid": field_id})
                if not field_type:
                    field: Field = Field.get(id=field_id)
                    field_type = field.type

            value, field_type = FieldData._check_value_type(value, field_type)
            _data["value"] = value

            if not field_id:
                if not field_name or not field_type:
                    raise ValueError("field_name and field_type must be specified")
                _data.update(
                    {"fieldname": field_name,
                     "fieldtype": field_type})

            if unit:
                unit = FieldData._check_unit(unit)
                _data["unit"] = unit
            post_data_list.append(_data)

        id_list = FieldData._post(post_data_list, project_id, force_list=True)
        for data, id in zip(post_data_list, id_list):
            data["id"] = id
        return post_data_list
