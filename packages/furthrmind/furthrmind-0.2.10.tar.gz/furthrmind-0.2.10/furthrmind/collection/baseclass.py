from functools import wraps

from furthrmind.utils import furthr_wrap, instance_overload
from typing_extensions import List, Self, Any, Dict, TYPE_CHECKING, Union
from inspect import isclass
import os
from urllib import parse

if TYPE_CHECKING:
    from furthrmind.collection import File, FieldData, Experiment, Sample, ResearchItem


class BaseClass:
    _data = {}
    _fetched = False
    _id = None
    fm = None

    _attr_definition = {}

    def __init__(self, id=None, data=None):
        if data:
            self._update_attributes(data)

        if id:
            self._id = id
        else:
            if "id" in self._data:
                self._id = self._data["id"]
        if not self._id:
            raise ValueError("No id provided")

        # create instance methods for certain class_methods
        instance_methods = [
            "get",
            "get_all",
            "get_many",
            "post",
            "delete",
            "_get",
            "_get_all",
            "_get_many",
            "_post",
            "_delete",
        ]
        instance_overload(self, instance_methods)

    def __getitem__(self, item):
        if hasattr(self, item):
            return getattr(self, item)
        else:
            raise ValueError("No such attribute")

    def __str__(self):
        class_name = type(self).__name__
        id = self._id
        name = ""
        if hasattr(self, "name"):
            name = self.name
        return f"{class_name} id: {id}, name: {name}"

    def _get_url_instance(self, project_id=None):
        return ""

    @classmethod
    def _get_url_class(cls, id, project_id=None):
        return ""

    @classmethod
    def _get_all_url(cls, project_id=None):
        return ""

    @classmethod
    def _post_url(cls, project_id=None):
        return ""

    @staticmethod
    def _update_instance_decorator(_fetched=False):
        def decorator(function):
            @wraps(function)
            def wrapper(*args, **kws):
                results = function(*args, **kws)
                results["_fetched"] = _fetched
                self = args[0]
                self._update_attributes(results)
                return self

            return wrapper

        return decorator

    @staticmethod
    def _create_instances_decorator(_fetched=False):
        def decorator(function):
            @wraps(function)
            def wrapper(*args, **kws):
                results = function(*args, **kws)
                if results is None:
                    return
                if isclass(args[0]):
                    cls = args[0]
                else:
                    self = args[0]
                    cls = self.__class__

                if isinstance(results, list):
                    item_list = []
                    for r in results:
                        r["_fetched"] = _fetched
                        item = cls(data=r)
                        item_list.append(item)
                    return item_list
                else:
                    results["_fetched"] = _fetched
                    item = cls(data=results)
                    return item

            return wrapper

        return decorator

    def _update_attributes(self, data):
        from furthrmind.collection import get_collection_class

        self._data = data

        def _create_instance(classname, _data):
            cls = get_collection_class(classname)
            if isinstance(_data, list):
                item_list = []
                for item in _data:
                    item = cls(self.fm, data=item)
                    item_list.append(item)
                item = item_list
            else:
                item = cls(self.fm, data=_data)
            return item

        for key in data:
            if hasattr(self, key):
                item = data[key]
                if key in self._attr_definition:
                    attr_definition = self._attr_definition[key]
                    if "class" in attr_definition:
                        if "nested_dict" in attr_definition:
                            item = {}
                            for item_key in data[key]:
                                item[item_key] = _create_instance(
                                    attr_definition["class"], data[key][item_key]
                                )
                        else:
                            if data[key]:
                                item = _create_instance(
                                    attr_definition["class"], data[key]
                                )
                            else:
                                pass

                setattr(self, key, item)
            else:
                for attr_definition in self._attr_definition.items():
                    definition_key = attr_definition[0]
                    definition_value = attr_definition[1]
                    if "data_key" in definition_value:
                        if definition_value["data_key"] == key:
                            item = data[key]
                            if "class" in definition_value:
                                item = _create_instance(
                                    definition_value["class"], data[key]
                                )
                            setattr(self, definition_key, item)
                            break

    @classmethod
    def _get(
        cls,
        id=None,
        shortid=None,
        name=None,
        category_name=None,
        category_id=None,
        parent_group_id=None,
        project_id=None,
    ):

        if isclass(cls):
            data = cls._get_class_method(
                id,
                shortid,
                name,
                category_name,
                category_id,
                parent_group_id,
                project_id,
            )
            return data
        else:
            self = cls
            data = self._get_instance_method()
            return data

    @_update_instance_decorator(_fetched=True)
    @furthr_wrap(force_list=False)
    def _get_instance_method(self):
        url = self._get_url_instance()
        data = self.fm.session.get(url)
        return data

    @classmethod
    @_create_instances_decorator(_fetched=True)
    @furthr_wrap(force_list=False)
    def _get_class_method(
        cls,
        id=None,
        shortid=None,
        name=None,
        category_name=None,
        category_id=None,
        parent_group_id=None,
        project_id=None,
    ):
        if id:
            if len(id) == 10:
                shortid = id
                id = None

        if shortid or name or category_name or category_id or parent_group_id:
            query = []
            if shortid:
                query.append(("shortid", shortid))
            if name:
                query.append(("name", name))
            if category_name:
                query.append(("category_name", category_name))
            if category_id:
                query.append(("category_id", category_id))
            if parent_group_id:
                query.append(("parent_group_id", parent_group_id))

            url_query = parse.urlencode(query)
            url = cls._get_all_url()
            url = f"{url}?{url_query}"
        else:
            url = cls._get_url_class(id, project_id=project_id)

        result = cls.fm.session.get(url)

        return result

    @classmethod
    def _get_many(
        cls,
        ids: List[str] = (),
        shortids: List[str] = (),
        names: List[str] = (),
        category_name=None,
        category_id=None,
        project_id=None,
    ) -> List[Self]:
        query = []
        if ids:
            for id in ids:
                query.append(("id", id))
        if shortids:
            for shortid in shortids:
                query.append(("shortid", shortid))
        if names:
            for name in names:
                query.append(("name", name))
        if category_name:
            query.append(("category_name", category_name))
        if category_id:
            query.append(("category_id", category_id))

        url_query = parse.urlencode(query)
        if isclass(cls):
            return cls._get_all_class_method(project_id, url_query)
        else:
            self = cls
            return self._get_all_instance_method(project_id, url_query)

    @classmethod
    def _get_all(cls, project_id=None) -> List[Self]:
        if isclass(cls):
            return cls._get_all_class_method(project_id)
        else:
            self = cls
            return self._get_all_instance_method(project_id)

    @_create_instances_decorator(_fetched=True)
    @furthr_wrap(force_list=True)
    def _get_all_instance_method(self, project_id, url_query=""):
        from .project import Project

        if isinstance(self, Project):
            url = self.__class__._get_all_url()
        else:
            url = self.__class__._get_all_url(project_id)

        if url_query:
            url = f"{url}?{url_query}"
        return self.fm.session.get(url)

    @classmethod
    @_create_instances_decorator(_fetched=True)
    @furthr_wrap(force_list=True)
    def _get_all_class_method(cls, project_id, url_query=""):
        from .project import Project

        if cls in [Project]:
            url = cls._get_all_url()
        else:
            url = cls._get_all_url(project_id)

        if url_query:
            url = f"{url}?{url_query}"
        return BaseClass.fm.session.get(url)

    @classmethod
    def _post(cls, data, project_id=None, force_list=False, endpoint=None):
        if endpoint:
            if force_list:
                return cls._post_custom_url_force_list(data, endpoint)
            else:  
                return cls._post_custom_url(data, endpoint)
            
        if isclass(cls):
            if force_list:
                return cls._post_class_force_list_method(data, project_id)
            else:
                return cls._post_class_method(data, project_id)
        else:
            self = cls
            return self._post_instance_method(data, project_id)
    
    @classmethod
    @furthr_wrap(force_list=False)
    def _post_custom_url(cls, data, endpoint):
        if not endpoint.startswith("/") and not cls.fm.base_url.endswith("/"):
            endpoint = "/" + endpoint
        url = cls.fm.base_url + endpoint
        return cls.fm.session.post(url, json=data)
    
    @classmethod
    @furthr_wrap(force_list=True)
    def _post_custom_url_force_list(cls, data, endpoint):
        if not endpoint.startswith("/") and not cls.fm.base_url.endswith("/"):
            endpoint = "/" + endpoint
        url = cls.fm.base_url + endpoint
        return cls.fm.session.post(url, json=data)
    
    @furthr_wrap(force_list=False)
    def _post_instance_method(self, data, project_id=None):
        url = self.__class__._post_url(project_id)
        return self.fm.session.post(url, json=data)

    @classmethod
    @furthr_wrap(force_list=False)
    def _post_class_method(cls, data, project_id=None):
        url = cls._post_url(project_id)
        return cls.fm.session.post(url, json=data)

    @classmethod
    @furthr_wrap(force_list=True)
    def _post_class_force_list_method(cls, data, project_id=None):
        url = cls._post_url(project_id)
        return cls.fm.session.post(url, json=data)

    @classmethod
    def delete(cls, id: str = "", project_id: str = "") -> str:
        """
        Method to delete an item. Can be called as a classmethod with providing the id to be deleted or on the instance
        of a class

        Parameters
        ----------
        id : str
            The id of the resource to delete
        project_id : str, optional
            Optionally to delete an item in another project as the furthrmind sdk was initiated with

        Returns
        -------
        str
            The id of the item
        """

        if isclass(cls):
            return cls._delete_class_method(id, project_id)
        else:
            self = cls
            return self._delete_instance_method(project_id)

    @classmethod
    @furthr_wrap(force_list=False)
    def _delete_class_method(cls, id, project_id=None):
        url = cls._get_url_class(id, project_id)
        return cls.fm.session.delete(url)

    @furthr_wrap(force_list=False)
    def _delete_instance_method(self, project_id=None):
        url = self._get_url_instance(project_id)
        return self.fm.session.delete(url)

    def to_dict(self):
        """
        Converts the object's attributes to a dictionary representation.

        Returns
        -------
        dict
            Dictionary containing the object's attributes (excluding private attributes, callable attributes, and attributes of type Furthrmind).
        """

        from furthrmind import Furthrmind

        data = {}
        for attr in dir(self):
            if attr.startswith("_"):
                continue
            value = getattr(self, attr)
            if callable(value):
                continue
            if isinstance(value, Furthrmind):
                continue
            data[attr] = self._convert(value)
        return data

    def _convert(self, item):
        if isinstance(item, dict):
            new_item = {}
            for key, value in item.items():
                if isinstance(value, (dict, list)):
                    value = self._convert(value)
                    new_item[key] = value
                elif isinstance(value, BaseClass):
                    value = value.to_dict()
                    new_item[key] = value
                else:
                    new_item[key] = value
        elif isinstance(item, list):
            new_item = []
            for value in item:
                if isinstance(value, (dict, list)):
                    value = self._convert(value)
                    new_item.append(value)
                elif isinstance(value, BaseClass):
                    value = value.to_dict()
                    new_item.append(value)
                else:
                    new_item.append(value)
        elif isinstance(item, BaseClass):
            new_item = item.to_dict()

        else:
            new_item = item

        return new_item


class BaseClassWithFieldData(BaseClass):
    id = None
    fielddata: List["FieldData"] = []

    def __init__(self, id=None, data=None):
        super().__init__(id, data)

    def update_field_value(self, value, field_name: str = "", field_id: str = ""):
        """
        Parameters
        ----------
        value : various data types
            The value to be updated in the field.

            - Numeric fields: float or int, or a string convertible to a float
            - Date fields: datetime, date object, unix timestamp, or string with iso format
            - Text fields: string
            - List fields: dictionary with id or name as key, or string with name, or string with id
            - Notebook fields: dictionary with content as key, or string
            - Checkbox fields: boolean
        field_name : str, optional
            Name of the field that should be updated. Either `field_name` or `field_id` must be specified.
        field_id : str, optional
            ID of the field that should be updated. Either `field_name` or `field_id` must be specified.

        Returns
        -------
        int
            The ID of the field that was updated.

        Raises
        ------
        ValueError
            If no field is found with the given `field_id` or `field_name`.
        """

        if not self._fetched:
            self._get()

        fielddata = None
        for item in self.fielddata:
            if fielddata:
                break
            if field_id:
                if item.field_id == field_id:
                    fielddata = item
            elif field_name:
                if item.field_name.lower() == field_name.lower():
                    fielddata = item

        if not fielddata:
            raise ValueError("No field found with the given field_id or field_name")

        return fielddata.update_value(value)

    def update_field_unit(
        self, unit: Union[Dict, str], field_name: str = "", field_id: str = ""
    ):
        """
        Method to update the unit of a field.

        Parameters
        ----------
        unit : Union[Dict, str]
            Dictionary with id or name, or string representing the name, or string representing the id.
        field_name : str, optional
            The name of the field that should be updated. Either `field_name` or `field_id` must be specified.
        field_id : str, optional
            The ID of the field that should be updated. Either `field_name` or `field_id` must be specified.

        Returns
        -------
        id
            The ID of the updated field.

        Raises
        ------
        ValueError
            If no field is found with the given `field_id` or `field_name`.

        """

        if not self._fetched:
            self._get()

        fielddata = None
        for item in self.fielddata:
            if fielddata is not None:
                break
            if field_id:
                if item.field_id == field_id:
                    fielddata = item
            elif field_name:
                if item.field_name.lower() == field_name.lower():
                    fielddata = item

        if not fielddata:
            raise ValueError("No field found with the given field_id or field_name")

        return fielddata.update_unit(unit)

    def set_calculation_result(
        self,
        value: dict,
        field_name: str = "",
        field_id: str = "",
        fielddata_id: str = "",
    ):
        """
        Method to update a calculation result

        Parameters
        ----------
        value : dict
            Dictionary containing the calculation result to be set for the field.
        field_name : str, optional
            Name of the field that should be updated. Either `field_name`, `field_id`, or `fielddata_id` must be specified.
        field_id : str, optional
            ID of the field that should be updated. Either `field_name`, `field_id`, or `fielddata_id` must be specified.
        fielddata_id : str, optional
            ID of the fielddata that should be updated. Either `field_name`, `field_id`, or `fielddata_id` must be specified.

        Returns
        -------
        id
            The ID of the fielddata that was updated.

        Raises
        ------
        ValueError
            If no field is found with the given `field_id` or `field_name`.
        """

        if not self._fetched:
            self._get()

        fielddata = None
        for item in self.fielddata:
            if fielddata:
                break
            if fielddata_id:
                if item.id == fielddata_id:
                    fielddata = item
            if field_id:
                if item.field_id == field_id:
                    fielddata = item
            elif field_name:
                if item.field_name.lower() == field_name.lower():
                    fielddata = item

        if not fielddata:
            raise ValueError("No field found with the given field_id or field_name")

        return fielddata.set_calculation_result(value)

    def add_field(
        self,
        field_name: str = "",
        field_type: str = "",
        field_id: str = "",
        value: Any = None,
        unit: Union[Dict, str] = None,
        position: int = None,
    ) -> "FieldData":
        """
        Method to add a field to the current item

        Parameters
        ----------
        field_name : str
            Name of field that should be added. If fieldname provided, also fieldtype must be specified.
            Either fieldname and fieldtype or field_id must be specified.
        field_type : str
            Type of field. Must be one of:

            - Numeric fields: numeric, numeric-field, numeric_field
            - Date fields: date, date_field, date-field, datefield
            - Text fields: singleline, singlelinefield, text, text-field, text_field, textfield
            - List fields: combobox, comboboxfield, list, list-field, list_field, listfield
            - Notebook fields: multiline, notebook, notebookfield, notebook-field, notebook_field
            - Checkbox fields: checkbox, checkbox-field, checkbox_field, checkboxfield
            - Calculation fields: calculation, calculation-field, calculation_field, calculationfield
        field_id : str
            Id of field that should be added.
        value : Any
            Value of the field. The data type of the value depends on the field_type:

            - Numeric fields: float or int, or a string convertible to a float
            - Date fields: datetime, date object, unix timestamp, or string with iso format
            - Text fields: string
            - List fields: dictionary with id or name as key, or string with name, or string with id
            - Notebook fields: dictionary with content as key, or string
            - Checkbox fields: boolean

        unit : Union[Dict, str]
            Dictionary with id or name, or string representing the name, or string representing the id.

        position: int
            The position where the field should be added in the card. Starting at "0". Optionally.

        Returns
        -------
        FieldData
            The new FieldData object that was created.

        """

        from .fielddata import FieldData

        if not self._fetched:
            self._get()

        fielddata = FieldData.create(field_name, field_type, field_id, value, unit)

        new_field_data_list = list(self.fielddata)
        if position is not None:
            assert type(position) is int, "Position must be an integer"
            new_field_data_list.insert(position, fielddata)
        else:
            new_field_data_list.append(fielddata)

        self.fielddata = new_field_data_list

        data = {"id": self.id, "fielddata": [{"id": f.id} for f in self.fielddata]}
        self._post(data)
        return fielddata

    def add_many_fields(self, data_list: List[Dict]) -> List["FieldData"]:
        """
        Method to add many fields to the current item

        Parameters
        ----------
        data_list: List[Dict]
            List of dictionaries containing the information about the fields to be added. Each dictionary should have the following keys:

            - field_name: Name of the field to be added. Either field_name and field_type or field_id must be specified.
            - field_type:
                Type of the field. Must be one of the following:

                - Numeric fields: numeric, numeric-field, numeric_field
                - Date fields: date, date_field, date-field, datefield
                - Text fields: singleline, singlelinefield, text, text-field, text_field, textfield
                - List fields: combobox, comboboxfield, list, list-field, list_field, listfield
                - Notebook fields: multiline, notebook, notebookfield, notebook-field, notebook_field
                - Checkbox fields: checkbox, checkbox-field, checkbox_field, checkboxfield
                - Calculation fields: calculation, calculation-field, calculation_field, calculationfield

            - field_id: ID of the field to be added.
            - value: Value of the field. The required format depends on the field_type:

                - Numeric: float or int, or a string convertible to a float.
                - Date: datetime, date object, Unix timestamp, or string in ISO format.
                - SingleLine: string.
                - ComboBoxEntry: Dictionary with ID or name as key, or string with name, or string with ID.
                - MultiLine: Dictionary with content as key, or string.
                - CheckBox: Boolean.

            - unit: Dictionary with ID or name as key, or string with name, or string with ID.
            - position: int, The position where the field should be added in the card. Starting at "0". Optionally.

        Returns
        -------
        List["FieldData"]
            List of FieldData objects representing the added fields.

        """

        from .fielddata import FieldData

        if not self._fetched:
            self._get()

        fielddata_list = FieldData.create_many(data_list)

        new_field_data_list = list(self.fielddata)
        for fielddata, data in zip(fielddata_list, data_list):
            if "position" in data:
                assert type(data["position"]) is int, "Position must be an integer"
                new_field_data_list.insert(data["position"], fielddata)
            else:
                new_field_data_list.append(fielddata)

        self.fielddata = new_field_data_list

        data = {"id": self.id, "fielddata": [{"id": f.id} for f in self.fielddata]}
        self._post(data)
        return fielddata_list

    def remove_field(self, field_name: str = "", field_id: str = ""):
        """
        Removes a field from the current item.

        Parameters
        ----------
        field_name : str, optional
            Name of the field that should be removed. Either the `field_name` or `field_id` must be specified.
        field_id : str, optional
            ID of the field that should be removed.Either the `field_name` or `field_id` must be specified.

        Returns
        -------
        str
            ID of the item after the field is removed.

        Raises
        ------
        ValueError
            If no field is found with the given `field_name` or `field_id`.
        """

        if not self._fetched:
            self._get()

        new_fielddata_list = []
        fielddata_to_be_removed = None
        for fielddata in self.fielddata:
            found = False
            if field_id:
                if fielddata.field_id == field_id:
                    fielddata_to_be_removed = fielddata
                    found = True
            elif field_name:
                if fielddata.field_name == field_name:
                    fielddata_to_be_removed = fielddata
                    found = True
            if not found:
                new_fielddata_list.append(fielddata)

        if not fielddata_to_be_removed:
            raise ValueError("No field found with the given fieldid or fieldname")

        self.fielddata = new_fielddata_list
        fielddata_list = [{"id": fd.id} for fd in new_fielddata_list]
        post_data = {"id": self.id, "fielddata": fielddata_list}
        id = self._post(post_data)
        return id


class BaseClassWithFiles(BaseClass):
    id = None
    files = []

    def __init__(self, id=None, data=None):
        super().__init__(id, data)

    def add_file(
        self, file_path: str = "", file_name: str = "", file_id: str = ""
    ) -> "File":
        """
        Parameters
        ----------
        file_path : str, optional
            File path of the file that should be uploaded.
        file_name : str, optional
            Optionally specify the file name if not the original file name should be used.
        file_id : str, optional
            ID of the file.

        Returns
        -------
        File
            The file object that has been added.

        Raises
        ------
        AssertationError
            If neither file path nor file_id is specified.
        ValueError
            If the file path specified does not exist.
        """

        from furthrmind.file_loader import FileLoader
        from .file import File

        assert file_path or file_id, "File_path or file_id must be specified"

        if not self._fetched:
            self._get()

        if not file_id:
            assert file_path, "File path must be specified"
            if not os.path.isfile(file_path):
                raise ValueError("File does not exist")

            fl = FileLoader(self.fm.host, self.fm.api_key)
            file_id, file_name = fl.uploadFile(file_path, file_name)
            if not file_name:
                file_path = file_path.replace("\\", "/")
                file_name = os.path.basename(file_path)
            file_data = {"id": file_id, "name": file_name}
        else:
            file_data = {"id": file_id}

        file_list = [{"id": f.id} for f in self.files]
        file_list.append(file_data)
        post_data = {"id": self.id, "files": file_list}

        id = self._post(post_data)
        file = File(data=file_data)
        new_file_list = list(self.files)
        new_file_list.append(file)
        self.files = new_file_list
        return file

    def remove_file(self, file_id: str = "", file_name: str = ""):
        """
        Method to remove a file from the current item

        Parameters
        ----------
        file_id: str, optional
            ID of the file that should be removed. Either `file_id` or `file_name` must be specified.
        file_name: str, optional
            Name of the file to be removed.

        Returns
        -------
        file_object: dict
            Object representing the removed file.

        Raises
        ------
        ValueError
            If no file is found with the given `file_id` or `file_name`.

        """

        if not self._fetched:
            self._get()

        new_file_list = []
        file_to_be_removed = None
        for file in self.files:
            found = False
            if file_id:
                if file.id == file_id:
                    found = True
                    file_to_be_removed = file
            elif file_name:
                if file.name == file_name:
                    found = True
                    file_to_be_removed = file
            if not found:
                new_file_list.append(file)

        if not file_to_be_removed:
            raise ValueError("No file found with the given file_id or file_name")

        self.files = new_file_list
        file_list = [{"id": f.id} for f in new_file_list]
        post_data = {"id": self.id, "files": file_list}
        id = self._post(post_data)
        return id


class BaseClassWithGroup(BaseClass):
    id = None
    groups = []

    def __init__(self, id=None, data=None):
        super().__init__(id, data)

    @classmethod
    def _create(
        cls, name, group_name: str = "", group_id: str = "", project_id: str = ""
    ):
        """
        Internal method to create items that belong to a group: exp, sample, researchitem

        Parameters
        ----------
        name : str
            The name of the item to be created.

        group_name : str, optional
            The name of the group where the new item will belong to. Note that group name can only be considered for groups that
            are not subgroups. Either `group_name` or `group_id` must be specified.

        group_id : str, optional
            The id of the group where the new item will belong to. Either `group_name` or `group_id` must be specified.

        project_id : str, optional
            Optionally, create an item in another project as the `furthrmind sdk` was initiated with.

        Returns
        -------
        dict
            Dictionary representing the data including the generated id of the new item
        """

        data = cls._prepare_data_for_create(name, group_name, group_id, project_id)
        id = cls._post(data, project_id)
        data["id"] = id
        return data

    @classmethod
    def _create_many(cls, data_list: List[Dict], project_id: str = "") -> List[Dict]:
        """
        Parameters
        ----------
        data_list : List[Dict]
            A list of dictionaries representing the data for creating multiple items (samples or experiments).
            Each dictionary should contain the following keys:

                - name : str
                    The name of the item to be created.
                - group_name : str
                    The name of the group where the new item will belong to.
                    The group name can be only considered for groups that are not subgroups.
                    Either group_name or group_id must be specified.
                - group_id : str
                    The ID of the group where the new item will belong to.
                    Either group_name or group_id must be specified.

        project_id : str, optional
            Optionally, create an item in another project as the `furthrmind sdk` was initiated with.

        Returns
        -------
        list
            A list with Dictionaries representing the data including the generated id of the new item



        """

        new_list = []
        for data in data_list:
            new_list.append(
                cls._prepare_data_for_create(
                    name=data.get("name"),
                    group_name=data.get("group_name"),
                    group_id=data.get("group_id"),
                    project_id=project_id,
                )
            )

        id_list = cls._post(new_list, project_id, force_list=True)
        for data, id in zip(new_list, id_list):
            data["id"] = id
        return new_list

    @classmethod
    def _prepare_data_for_create(
        cls, name, group_name=None, group_id=None, project_id=None
    ):
        from furthrmind.collection import Group

        assert name, "Name must be specified"
        assert group_name or group_id, "Either group_name or group_id must be specified"

        if group_name:
            group = Group.get(name=group_name, project_id=project_id)
            if group:
                group_id = group.id

            if not group_id:
                raise ValueError("No group with Name was found")

        data = {"name": name, "groups": [{"id": group_id}]}

        return data
    
    @classmethod
    def copy(
        cls,
        item_to_be_copied_id: str,
        name: str,
        group_id: str = None,
        group_name: str = None,
        fielddata: bool = True,
        files: bool = True,
        datatables: bool = True,
        project_id: str = None,
    ) -> Self:
        """_summary_

        Parameters
        ----------
        item_to_be_copied_id : str, optional
            the id of the item that should be copied
        name : str, optional
            the name of the new item
        group_id : str, optional
            id of the group, where the new item should be created, Either `group_id` or `group_name` must be specified, by default None
        group_name : str, optional
            the name of the group, where the new item should be created, Either group_name or group_id must be specified, by default None
        fielddata : bool, optional
            whether the fielddata should be copied or not, by default True
        files : bool, optional
            whether the files of the item should be copied or not, by default True
        datatables : bool, optional
            whether the datatables of the item should be copied or not, by default True
        project_id : str, optional
            if the item should be created in another project. If None, the project is used the furthrmind sdk was initiated with, by default None

        Returns
        -------
        Self
            A new instance of the class

        Raises
        ------
        AssertionError
            if name is not set or not a string
        AssertionError
            if group_id and group_name are not set
        """

        assert name and isinstance(name, str), "Name must be a string"
        assert group_id or group_name, "Either group_id or group_name must be specified"
        
        item_to_be_copied = cls.get(item_to_be_copied_id)
        if not item_to_be_copied:
            raise ValueError("Item to be copied not found")
        
        if not project_id:
            project_id = cls.fm.project_id
            
        if not group_id and group_name:
            group = cls.fm.Group.get(name=group_name, project_id=project_id)
            group_id = group.id
 
        data = {
            "targetProject": project_id,
            "targetGroup": group_id,
            "sourceId": item_to_be_copied_id,
            "collection": cls.__name__,
            # includeExps: true,
            # includeSamples: true,
            # includeResearchItems: true,
            # includeSubgroups: true,
            "includeFields": fielddata,
            "includeRawData": datatables,
            "includeFiles": files}
        
        result = cls._post(data, endpoint="/copy-item")
        new_id = result.get("id")
        new_item = cls.get(new_id)
        
        update_id = new_item.update_name(name)
        if not update_id == new_id:
            new_item.delete()
            raise ValueError("Error updating the name, most likely name conflict")
        return new_item

class BaseClassWithLinking(BaseClass):
    id: str = ""
    linked_samples: List["Sample"] = []
    linked_experiments: List["Experiment"] = []
    linked_researchitems: Dict[str, List["ResearchItem"]] = []

    def __init__(self, id=None, data=None):
        super().__init__(id, data)

    def add_linked_experiment(self, experiment_id: str = "", experiment_name: str = ""):
        """
        This method is used to link an experiment to the current item. If the experiment is already linked to the item,
        no action is taken.

        Parameters
        ----------
        experiment_id : str, optional
            The ID of the experiment to link. Either `experiment_id` or `experiment_name` must be provided.
        experiment_name : str, optional
            The name of the experiment to link. Either `experiment_id` or `experiment_name` must be provided.

        Returns
        -------
        str
            The ID of the item.

        Raises
        ------
        ValueError
            If no experiment is found with the given name.

        """

        from furthrmind.collection import Experiment

        assert (
            experiment_id or experiment_name
        ), "Either experiment_id or experiment_name must be specified"

        if not self._fetched:
            self._get()

        if experiment_name:
            exp = Experiment.get(name=experiment_name)
            if not exp:
                raise ValueError("No exp found with the given name")
            experiment_id = exp.id
        else:
            exp = Experiment.get(experiment_id)

        experiment_id_list = [item.id for item in self.linked_experiments]
        if experiment_id in experiment_id_list:
            return self.id

        experiment_id_list.append(experiment_id)

        linked_experiment = [{"id": exp_id} for exp_id in experiment_id_list]
        data = {"id": self.id, "experiments": linked_experiment}

        self._post(data=data)
        new_linked_experiments = list(self.linked_experiments)
        new_linked_experiments.append(exp)
        self.linked_experiments = new_linked_experiments
        return self.id

    def remove_linked_experiment(
        self, experiment_id: str = "", experiment_name: str = ""
    ):
        """
        Method to remove a linked experiment from the current item.

        Parameters
        ----------
        experiment_id : str, optional
            The ID of the experiment you want to unlink. Either `experiment_id` or `experiment_name` must be given.
        experiment_name : str, optional
            The name of the experiment you want to unlink. Either `experiment_id` or `experiment_name` must be given.

        Returns
        -------
        str
            The ID of the item after removing the linkage.

        Raises
        ------
        ValueError
            If no experiment is found with the given name.
        AssertionError
            If neither `experiment_id` nor `experiment_name` is specified.

        """

        from furthrmind.collection import Experiment

        assert (
            experiment_id or experiment_name
        ), "Either experiment_id or experiment_name must be specified"

        if not self._fetched:
            self._get()

        if experiment_name:
            exp = Experiment.get(name=experiment_name)
            if not exp:
                raise ValueError("No exp found with the given name")
            experiment_id = exp.id

        experiment_id_list = []
        new_linked_items = []
        for item in self.linked_experiments:
            if item.id == experiment_id:
                continue
            new_linked_items.append(item)
            experiment_id_list.append(item.id)

        linked_experiment = [{"id": exp_id} for exp_id in experiment_id_list]
        data = {"id": self.id, "experiments": linked_experiment}

        self._post(data=data)
        self.linked_experiments = new_linked_items
        return self.id

    def add_linked_sample(self, sample_id: str = "", sample_name: str = ""):
        """
        Method is to link a sample to the current item

        Parameters
        ----------
        sample_id : str, optional
            id to the sample you want to link, either id or name must be given
        sample_name : str, optional
            name of the sample you want to link, either name or id must be given

        Returns
        -------
        str
            the id of the item

        Raises
        ------
        ValueError
            If no sample found with the given name

        """

        from furthrmind.collection import Sample

        assert (
            sample_id or sample_name
        ), "Either sample_id or sample_name must be specified"

        if not self._fetched:
            self._get()

        if sample_name:
            s = Sample.get(name=sample_name)
            if not s:
                raise ValueError("No sample found with the given name")
            sample_id = s.id
        else:
            s = Sample.get(sample_id)

        sample_id_list = [item.id for item in self.linked_samples]
        if sample_id in sample_id_list:
            return self.id

        sample_id_list.append(sample_id)

        linked_samples = [{"id": s_id} for s_id in sample_id_list]

        data = {"id": self.id, "samples": linked_samples}

        self._post(data=data)
        new_linked_samples = list(self.linked_samples)
        new_linked_samples.append(s)
        self.linked_samples = new_linked_samples
        return self.id

    def remove_linked_sample(self, sample_id: str = "", sample_name: str = ""):
        """
        Method is to remove a linked sample from the current item

        Parameters
        ----------
        sample_id : str, optional
            The id of the sample you want to unlink. Either `sample_id` or `sample_name` must be provided.
        sample_name : str, optional
            The name of the sample you want to unlink. Either `sample_id` or `sample_name` must be provided.

        Returns
        -------
        str
            The id of the item.

        Raises
        ------
        ValueError
            If no sample is found with the given name.

        Notes
        -----
        This method is used to remove a linked sample from the current item. It updates the list of linked samples for the item and saves the changes.

        """

        from furthrmind.collection import Sample

        assert (
            sample_id or sample_name
        ), "Either sample_id or sample_name must be specified"

        if not self._fetched:
            self._get()

        if sample_name:
            s = Sample.get(name=sample_name)
            if not s:
                raise ValueError("No sample found with the given name")
            sample_id = s.id

        sample_id_list = []
        new_linked_items = []
        for item in self.linked_samples:
            if item.id == sample_id:
                continue
            new_linked_items.append(item)
            sample_id_list.append(item.id)

        linked_samples = [{"id": s_id} for s_id in sample_id_list]

        data = {"id": self.id, "samples": linked_samples}
        self._post(data=data)
        self.linked_samples = new_linked_items
        return self.id

    def add_linked_researchitem(self, researchitem_id: str):
        """
        Method is to link a research item to the current item

        Parameters
        ----------
        researchitem_id : str
            The id of the research item to be linked. If not specified, the method will raise an assertion error.

        Returns
        -------
        str
            The id of the current research item.

        Raises
        ------
        AssertionError
            If researchitem_id is not specified.

        """

        from furthrmind.collection import ResearchItem

        assert researchitem_id, "researchitem_id must be specified"

        if not self._fetched:
            self._get()

        researchitem_id_list = []
        for cat in self.linked_researchitems:
            researchitem_id_list.extend(
                [ri_id.id for ri_id in self.linked_researchitems[cat]]
            )

        if researchitem_id in researchitem_id_list:
            return self.id

        researchitem_id_list.append(researchitem_id)

        linked_researchitems = [{"id": ri_id} for ri_id in researchitem_id_list]

        data = {"id": self.id, "researchitems": linked_researchitems}

        self._post(data=data)
        ri = ResearchItem.get(id=researchitem_id)
        research_item_dict = dict(self.linked_researchitems)
        if ri.category.name in self.linked_researchitems:
            new_linked_researchitems = list(self.linked_researchitems[ri.category.name])
        else:
            new_linked_researchitems = []

        new_linked_researchitems.append(ri)
        research_item_dict[ri.category.name] = new_linked_researchitems
        self.linked_researchitems = research_item_dict

        return self.id

    def remove_linked_researchitem(self, researchitem_id: str):
        """
        Method to remove a linked researchitem from the current item

        Parameters
        ----------
        researchitem_id : str
            The ID of the research item you want to unlink

        Returns
        -------
        str
            The ID of the item after removing the linkage.
        """

        assert researchitem_id, "Either experiment_id must be specified"

        if not self._fetched:
            self._get()

        researchitem_id_list = []
        new_linked_items = {}
        for cat in self.linked_researchitems:
            for item in self.linked_researchitems[cat]:
                if item.id == researchitem_id:
                    continue
                if cat not in new_linked_items:
                    new_linked_items[cat] = []
                new_linked_items[cat].append(item)
                researchitem_id_list.append(item.id)

        if researchitem_id in researchitem_id_list:
            researchitem_id_list.remove(researchitem_id)

        linked_researchitems = [{"id": ri_id} for ri_id in researchitem_id_list]

        data = {"id": self.id, "researchitems": linked_researchitems}

        self._post(data=data)
        self.linked_researchitems = new_linked_items
        return self.id


class BaseClassWithNameUpdate(BaseClass):
    id = None
    name = ""

    def __init__(self, id=None, data=None):
        super().__init__(id, data)

    def update_name(self, name: str) -> str:
        """
        The method updates the name of the current item.

        Parameters
        ----------
        name : str
            New name


        Returns
        -------
        str
            The id of the item.
        """

        data = {"id": self.id, "name": name}
        id = self._post(data)
        self.name = name
        return id

    @classmethod
    def update_many_names(cls, data_list: List[Dict[str, str]]) -> List[str]:
        """
        Method to update the name of many items.

        Parameters
        ----------
        data_list : List[Dict[str, str]]
            A list of dictionaries representing the data to update the name of many items.
            Each dictionary should contain the following keys:

                - id : str
                    The id of the item that should be updated.
                - name : str
                    The new name of the item.


        Returns
        -------
        Self
            The updated object.
        """

        assert isinstance(data_list, (tuple, list)), "data_list must be a list or tuple"

        new_data_list = []
        for data in data_list:
            assert isinstance(
                data, dict
            ), "Each entry in the data list must be a dictionary"
            assert (
                "name" in data and "id" in data
            ), "Each entry must have a key 'name' and a key 'id'"
            new_data_list.append({"id": data["id"], "name": data["name"]})

        id_list = cls._post(new_data_list, force_list=True)

        return id_list


class BaseClassWithProtected(BaseClass):
    id = None
    protected = False

    def __init__(self, id=None, data=None):
        super().__init__(id, data)

    def update_protected(self, protected: bool) -> str:
        """
        This method updates the protection state of the current item.

        Parameters
        ----------
        protected : bool
            True or False, whether the item should be protected or not.

        Returns
        -------
        str
            The id of the item.
        """
        if not self._fetched:
            self._get()

        assert isinstance(protected, bool), "protected must be a boolean"

        if self.protected == protected:
            return self.id

        data = {"id": self.id, "protected": protected}
        id = self._post(data)
        self.protected = protected
        return id

    @classmethod
    def update_many_protected(cls, data_list: List[Dict[str, str]]) -> List[str]:
        """
        With this method the protection state of many items are updated.

        Parameters
        ----------
        data_list : List[Dict[str, str]]
            A list of dictionaries representing the data for updating the items.
            Each dictionary should contain the following keys:

                - id : str
                    The id of the item that should be updated.
                - protected : bool
                    True or False, whether the item should be protected or not.


        Returns
        -------
        Self
            The updated object.
        """

        assert isinstance(data_list, (tuple, list)), "data_list must be a list or tuple"

        new_data_list = []
        for data in data_list:
            assert isinstance(
                data, dict
            ), "Each entry in the data list must be a dictionary"
            assert (
                "protected" in data and "id" in data
            ), "Each entry must have a key 'name' and a key 'id'"
            assert isinstance(data["protected"], bool), "protected must be a boolean"
            new_data_list.append({"id": data["id"], "protected": data["protected"]})

        id_list = cls._post(new_data_list, force_list=True)

        return id_list

