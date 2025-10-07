from inspect import isclass

from pandas import DataFrame
from typing_extensions import Self, List, TYPE_CHECKING, Union, Dict

from furthrmind.collection.baseclass import BaseClass

if TYPE_CHECKING:
    from furthrmind.collection import Column


class DataTable(BaseClass):
    """
    Attributes
    ----------
    id : str
        id of the datatable
    name : str
        name of the datatable
    columns : List[Column]
        List of [Column](column.md) objects belonging to this datatable. For additional information, consult the
        [Column](column.md) documentation. Initially, the columns only present the id and name. To retrieve their
        values, utilize the get() method on the relevant column or invoke the get_columns() method of the datatable.
    _fetched : bool
        This is a Boolean attribute indicating whether all attributes have been retrieved from the server or only
        the name and ID are present.
    """

    id = ""
    name = ""
    columns: List["Column"] = []

    _attr_definition = {
        "columns": {"class": "Column"}
    }

    def __init__(self, id=None, data=None):
        super().__init__(id, data)

    def _get_url_instance(self, project_id=None):
        project_url = DataTable.fm.get_project_url(project_id)
        url = f"{project_url}/rawdata/{self.id}"
        return url

    @classmethod
    def _get_url_class(cls, id, project_id=None):
        project_url = cls.fm.get_project_url(project_id)
        url = f"{project_url}/rawdata/{id}"
        return url

    @classmethod
    def _get_all_url(cls, project_id=None):
        project_url = cls.fm.get_project_url(project_id)
        url = f"{project_url}/rawdata"
        return url

    @classmethod
    def _post_url(cls, project_id=None):
        project_url = cls.fm.get_project_url(project_id)
        url = f"{project_url}/rawdata"
        return url

    @classmethod
    def get(cls, id: str = "", project_id: str = "") -> Self:
        """
        This method retrieves a singular `datatable` using its ID. If this method is invoked on an instance of the class,
        the instance's ID is utilized. The retrieved `datatable` contains columns identified solely by their respective
        IDs and names. To obtain the corresponding data for these columns, you must either:
        1. Invoke the `get()` method on the specific column, or
        2. call the `get_columns()` method on the `datatable`.

        Parameters
        ----------
        id : str
            id of the requested datatable, if
        project_id : str, optional
            Optionally, to get experiments from another project as the furthrmind sdk was initiated with

        Returns
        -------
        Self
            Instance of the datatable class

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
        Method to get many datatables belonging to one project
        Columns are retrieved with id and column names only. To get the belonging data, the get method of the
        corresponding column must be called. Alternatively, the 'get_columns' method of the datatable must be
        called

        Parameters
        ----------
        ids : List[str]
            List of ids.
        project_id : str, optional
            Optionally to get datatables from another project as the furthrmind sdk was initiated with

        Returns
        -------
        List[Self]
            List of instances of the experiment class.

        Raises
        ------
        AssertionError
            If ids is not specified.
        """
        pass

        assert ids, "ids must be specified"
        return cls._get_many(ids, project_id=project_id)

    @classmethod
    def get_all(cls, project_id: str = "") -> List[Self]:

        """
        Method to get all datatables belonging to one project
        Columns are retrieved with id and column names only. To get the belonging data, the get method of the
        corresponding column must be called. Alternatively, the 'get_columns' method of the datatable must be
        called

        Parameters
        ----------
        project_id : str, optional
            Optionally to get datatables from another project as the furthrmind sdk was initiated with

        Returns
        -------
        List[Self]
            A list of instances of the DataTable class

        """
        return cls._get_all(project_id=project_id)

    def get_columns(self, column_id_list: List[str] = (), column_name_list: List[str] = ()) -> List["Column"]:
        """
        Method to get columns and their data belonging to this datatable
        If column_id_list and column_name_list are not provided, the method will retrieve all columns belonging
        to the datatable
        Updates the columns attribute of the datatable for the retrieved columns that belong to this datatable

        Parameters
        ----------
        column_id_list : List[str], optional
            A list of column IDs to retrieve. If not provided, all columns belonging to the datatable will be retrieved.
        column_name_list : List[str], optional
            A list of column names to retrieve.

        Returns
        -------
        List["Column"]
            A list of column objects.

        """

        columns = self._get_columns(column_id_list, column_name_list)
        new_column_mapping = {c.id: c for c in columns}
        new_column_list = []
        for column in self.columns:
            if column.id in new_column_mapping:
                new_column_list.append(new_column_mapping[column.id])
            else:
                new_column_list.append(column)
        self.columns = new_column_list
        return columns

    def get_pandas_dataframe(self, column_id_list: List[str] = (), column_name_list: List[str] = ()) -> DataFrame:
        """
        Method to get columns and their data as a pandas dataframe
        If column_id_list and column_name_list are not provided, the method will retrieve all columns belonging
        to the datatable

        Parameters
        ----------
        column_id_list : List[str]
            List of column IDs to retrieve. If not provided, all columns belonging to the datatable will be retrieved.
        column_name_list : List[str]
            List of column names to retrieve. If not provided, all columns belonging to the datatable will be retrieved.

        Returns
        -------
        pandas.core.frame.DataFrame
            Pandas dataframe containing the columns and their data.

        """

        columns = self._get_columns(column_id_list, column_name_list)
        new_column_mapping = {c.id: c for c in columns}
        new_column_list = []
        for column in self.columns:
            if column.id in new_column_mapping:
                new_column_list.append(new_column_mapping[column.id])
            else:
                new_column_list.append(column)
        self.columns = new_column_list
        
        data_dict = {}
        max_length = 0
        for c in columns:
            data_dict[c.name] = c.values
            if len(c.values) > max_length:
                max_length = len(c.values)
        for key in data_dict:
            if len(data_dict[key]) < max_length:
                data_dict[key] = data_dict[key] + [None] * (max_length - len(data_dict[key]))
        df = DataFrame.from_dict(data_dict, orient="columns")
        return df

    def _get_columns(self, column_id_list: List[str] = None, column_name_list: List[str] = None) -> List["Column"]:
        from furthrmind.collection import Column
        if column_id_list:
            column_id_list_new = []
            current_column_ids = [c.id for c in self.columns]
            for column_id in column_id_list:
                if column_id in current_column_ids:
                    column_id_list_new.append(column_id)
            column_id_list = column_id_list_new
        elif column_name_list:
            column_id_list = []
            for column in self.columns:
                if column.name in column_name_list:
                    column_id_list.append(column.id)
        else:
            column_id_list = [c.id for c in self.columns]
        columns = Column.get_many(ids=column_id_list)
        return columns

    @classmethod
    @BaseClass._create_instances_decorator(_fetched=False)
    def create(cls, name: str = "Data table", experiment_id: str = "", sample_id: str = "", researchitem_id: str = "",
               columns: List[dict] = (), project_id: str = "") -> Self:
        """
        Parameters
        ----------
        name: str
            Name of the datatable.
        experiment_id: str
            ID of the experiment where the datatable belongs to.
        sample_id: str
            ID of the sample where the datatable belongs to.
        researchitem_id: str
            ID of the researchitem where the datatable belongs to.
        columns: List[dict]
            A list of columns that should be added to the datatable. List with dicts with the following keys:
            - name: name of the column
            - type: Type of the column, Either "Text" or "Numeric". Data must fit to type, for Text all data will be converted
              to string and for Numeric all data is converted to float (if possible)
            - data: List of column values, must fit to column_type, can also be a pandas data series
            - unit: dict with id or name, or name as string, or id as string
        project_id: str
            Optionally to create an item in another project as the furthrmind sdk was initiated with

        Returns
        -------
        Self
            Instance of datatable class.

        Raises
        ------
        AssertionError
            If name is not provided.
            If experiment_id nor sample_id nor researchitem_id is not provided.
        """

        from furthrmind.collection import Column

        assert name, "Name must be specified"
        assert experiment_id or sample_id or researchitem_id, "Either experiment_id or sample_id or researchitem_id must be specified"

        column_id_list = []
        if columns:
            columns = Column.create_many(columns)
            column_id_list = [c.id for c in columns]

        data = {"name": name}
        if column_id_list:
            data["columns"] = [{"id": column_id} for column_id in column_id_list]

        if experiment_id:
            data["experiment"] = {"id": experiment_id}

        if sample_id:
            data["sample"] = {"id": sample_id}

        if researchitem_id:
            data["researchitem"] = {"id": researchitem_id}

        id = cls._post(data, project_id)
        data["id"] = id
        return data

    def add_column(self, name: str, type: str, data: List, unit: Union[Dict, str] = None, 
                   pos: int = None, project_id: str = "") -> "DataTable":
        """
        Parameters
        ----------
        name: str
            Name of the column.
        type: str
            Type of the column, Either "Text" or "Numeric". Data must fit to type, for Text all data will be converted
            to string and for Numeric all data is converted to float (if possible)
        data: List
            List of column values, must fit to column_type, can also be a pandas data series
        unit: Union[Dict, str] 
            Dict with id or name, or name as string, or id as string
        project_id: str
            Optionally to create an item in another project as the furthrmind sdk was initiated with

        Returns
        -------
        Self
            Instance of datatable class.

        Raises
        ------
        AssertionError
            If name is not provided.
            If experiment_id nor sample_id nor researchitem_id is not provided.
        """
        
        column = self.fm.Column.create(name, type, data, unit, project_id=project_id)
        new_column_list = [{"id": c.id} for c in self.columns]
        if pos:
            new_column_list.insert(pos, {"id": column.id})
        else:
            new_column_list.append({"id": column.id})
            
        data = {"id": self.id, "columns": new_column_list}
        self._post(data, project_id)
        
        if pos:
            self.columns.insert(pos, column)
        else:
            self.columns.append(column)
        return self