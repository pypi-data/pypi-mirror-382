import datetime
from datetime import timezone
import math

import iteration_utilities
import pandas
from typing_extensions import Self, List, Dict, Any, TYPE_CHECKING
from inspect import isclass
from furthrmind.collection.baseclass import BaseClass
from furthrmind.collection.fielddata import FieldData
if TYPE_CHECKING:
    from furthrmind.collection import Unit


class Column(BaseClass):
    """
    Attributes
    ----------
    id : str
        id of the column
    name : str
        name of the column
    type : str
        Type of the column. Either "Text" or "Numeric"
    values : List[Any]
        "These represent the values held within the column. If the column type is 'Text',
        the values are characterized as strings. Conversely, for 'Numeric' type columns,
        the values are expressed as floating-point numbers."
    _fetched : bool
        This is a Boolean attribute indicating whether all attributes have been retrieved from the server or only
        the name and ID are present.
    """

    id: str = ""
    name: str = ""
    type: str = ""
    unit: "Unit" = None
    values: List[Any] = []

    _attr_definition = {"unit": {"class": "Unit"}}

    def __init__(self, id=None, data=None):
        super().__init__(id, data)

    def _update_attributes(self, data):
        super()._update_attributes(data)

        def convert_date(value):
            if not value:
                return value
            if isinstance(value, (int, float)):
                value = datetime.datetime.fromtimestamp(value)
            if isinstance(value, str):
                value = datetime.datetime.fromisoformat(value)
            return value

        if self.type == "Date":
            if self.values:
                self.values = list(map(convert_date, self.values))

    @classmethod
    def get(cls, id: str = "", project_id: str = "") -> Self:

        """
        Method to get one column by its id
        If called on an instance of the class, the id of the instance is used

        Parameters
        ----------
        id : str
            id of requested column
        project_id : str, optional
            Optionally to get a column from another project as the furthrmind sdk was initiated with, defaults to ""

        Returns
        -------
        Self
            Instance of column class

        Raises
        ------
        AssertionError
            If used as a class method and id is not specified.
        """

        if isclass(cls):
            assert id, "id must be specified"

        return cls._get(id, project_id=project_id)

    # noinspection PyMethodOverriding
    @classmethod
    def get_many(cls, ids: List[str] = (), project_id: str = "") -> List[Self]:
        """
        Method to get many columns belonging to one project

        Parameters
        ----------
        ids : List[str]
            List with ids.

        project_id : str
            Optionally, the id of the project from which to get the experiments. Defaults to an empty string.

        Returns
        -------
        List[Self]
            List with instances of the experiment class.

        Raises
        ------
        AssertionError
            If `ids` is not specified.
        """

        assert ids, "ids must be specified"
        return cls._get_many(ids, project_id=project_id)

    @classmethod
    def _get_all(cls, project_id=None) -> List[Self]:
        raise ValueError("Not implemented for columns")

    def _get_url_instance(self, project_id=None):
        project_url = Column.fm.get_project_url(project_id)
        url = f"{project_url}/column/{self.id}"
        return url

    @classmethod
    def _get_url_class(cls, id, project_id=None):
        project_url = cls.fm.get_project_url(project_id)
        url = f"{project_url}/column/{id}"
        return url

    @classmethod
    def _post_url(cls, project_id=None):
        project_url = cls.fm.get_project_url(project_id)
        url = f"{project_url}/column"
        return url

    @classmethod
    def _get_all_url(cls, project_id=None):
        project_url = cls.fm.get_project_url(project_id)
        url = f"{project_url}/column"
        return url

    @classmethod
    def _type_check(cls, column_type, data):
        column_type = column_type.capitalize()
        if not column_type in ["Text", "Numeric", "Date", "Bool"]:
            raise ValueError("Column type must be Text/Numeric/Date/Bool.")
        if isinstance(data, pandas.Series):
            data = data.tolist()

        data = list(map(Column._convert_nan, data))

        if column_type == "Text":
            if iteration_utilities.all_isinstance(data, (str, type(None))):
                return data
            return [str(d) for d in data]

        elif column_type == "Numeric":
            if iteration_utilities.all_isinstance(data, (int, float, type(None))):
                return data
            data = list(map(Column._convert_float, data))
            return data
        
        elif column_type == "Date":
            if iteration_utilities.all_isinstance(data, (int, float, type(None))):
                return data
            data = list(map(Column._convert_date, data))
            return data

    @staticmethod
    def _convert_nan(value):
        if value is None:
            return None
        try:
            if math.isnan(value):
                return None
            else:
                return value
        except:
            return value

    @staticmethod
    def _convert_float(value):
        if value is None:
            return value
        try:
            value = float(value)
            return value
        except:
            raise ValueError(
                "All column values must be a float, int or a string that can be converted to a float")

    @staticmethod
    def _convert_date(value):
        if value is None:
            return value
        if isinstance(value, datetime.datetime):
            if isinstance(value, pandas.Timestamp):
                value = value.to_pydatetime()
            if value.tzinfo is None:
                return value.isoformat()
            return int(value.timestamp())
        elif isinstance(value, datetime.date):
            value = datetime.datetime.combine(value, datetime.datetime.min.time())
            if value.tzinfo is None:
                return value.isoformat()
            return int(value.timestamp())
        elif isinstance(value, str):
            try:
                datetime.datetime.fromisoformat(value)
                return value
            except ValueError:
                raise TypeError("No iso time format")
        elif isinstance(value, (int, float)):
            return value
        raise ValueError("All column values must be a date, datetime, string, or int")

    @classmethod
    @BaseClass._create_instances_decorator(_fetched=False)
    def create(cls, name: str, type: str, data: list, unit=None, project_id=None) -> Self:
        """
        Method to create a new column

        Parameters
        ----------
        name : str
            Name of the column
        type : str
            The column type is categorized as either "Text" or "Numeric". For the "Text" type, all data
            will be transformed into strings. Conversely, for the "Numeric" type, data will be converted
            into floats, provided such a conversion is feasible. Please ensure that your data corresponds
            to the assigned column type.
        data : Union[list, pandas.Series]
            This should be either a list or a pandas series. Its values need to comply with the specified column type
            and will undergo conversion based on the rules described above.
        unit : Optional[Union[str, Dict]]
            Dict with id or name, or name as string, or id as string
        project_id : Optional[str]
            Optionally to create an item in another project as the furthrmind sdk was initiated with

        Returns
        -------
        Self
            Instance of column class

        """
        type = type.capitalize()
        data = cls._type_check(type, data)
        unit = FieldData._check_unit(unit)
        data_dict = {"name": name, "type": type, "values": data, "unit": unit}
        id = cls._post(data_dict, project_id)
        data_dict["id"] = id
        return data_dict

    @classmethod
    @BaseClass._create_instances_decorator(_fetched=False)
    def create_many(cls, data_list: List[Dict], project_id: str = "") -> List[Self]:
        """
        Method to create many new columns

        Parameters
        ----------
        data_list : List[Dict]
            A list of dictionaries containing information about the data columns to be created. Each dictionary should
             have the following keys:

                - name: Name of the column
                - type: Type of the column. Allowed values are "Text" or "Numeric".
                - data: List of column values. The values must match the column type. Can also be a pandas data series.
                - unit: Optional. Dictionary with id or name, or name as a string, or id as a string.

        project_id : str, optional
            Optionally to create columns in another project as the furthrmind sdk was initiated with

        Returns
        -------
        List[Self]
            A list of instances of the column class.

        """

        new_data_list = []
        for item in data_list:
            type:str = item.get("type", "")
            type = type.capitalize()
            unit = item.get("unit")
            name = item.get("name")
            data = item.get("value")
            if data is None:
                data = item.get("data")
            data = cls._type_check(type, data)
            unit = FieldData._check_unit(unit)
            data_dict = {"name": name, "type": type, "values": data, "unit": unit}
            new_data_list.append(data_dict)

        id_list = cls._post(new_data_list, project_id, force_list=True)
        for item, id in zip(new_data_list, id_list):
            item["id"] = id

        return new_data_list
