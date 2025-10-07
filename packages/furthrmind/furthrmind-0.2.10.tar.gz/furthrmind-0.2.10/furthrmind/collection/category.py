from inspect import isclass
from furthrmind.collection.baseclass import BaseClass
from typing_extensions import List, Self


class Category(BaseClass):
    """
    Attributes
    ----------
    id : str
        id of the category
    name : str
        name of the category
    description : str
        Description of the category
    _fetched : bool
        This is a Boolean attribute indicating whether all attributes have been retrieved from the server or only
        the name and ID are present.
    """

    id = ""
    name = ""
    description = ""

    def __init__(self, id=None, data=None):
        super().__init__(id, data)

    def _get_url_instance(self, project_id=None):
        project_url = Category.fm.get_project_url(project_id)
        url = f"{project_url}/researchcategory/{self.id}"
        return url

    @classmethod
    def _get_url_class(cls, id, project_id=None):
        project_url = cls.fm.get_project_url(project_id)
        url = f"{project_url}/researchcategory/{id}"
        return url

    @classmethod
    def _get_all_url(cls, project_id=None):
        project_url = cls.fm.get_project_url(project_id)
        url = f"{project_url}/researchcategory"
        return url

    @classmethod
    def _post_url(cls, project_id=None):
        project_url = cls.fm.get_project_url(project_id)
        url = f"{project_url}/researchcategory"
        return url

    @classmethod
    def get(cls, id: str = "", project_id: str = "") -> Self:
        """
        Method to get a category by its id.

        Parameters
        ----------
        id : str
            The id of the requested category. Only needed if used on as a class method
        project_id : str
            The project_id parameter is optional and can be used to retrieve categories
            from another project as the furthrmind sdk was initiated with.

        Returns
        -------
        Self
            An instance of the category class.

        Raises
        ------
        AssertionError
            If used as a class method and id is not specified.
        """

        if isclass(cls):
            assert id, "id must be specified"
        return super()._get(id=id, project_id=project_id)


    # noinspection PyMethodOverriding
    @classmethod
    def get_many(cls, ids: List[str] = (), project_id: str = "") -> List[Self]:
        """
        Method to get a category by its ids.

        Parameters
        ----------
        ids : List[str]
            List with ids.
        project_id : str, optional
            Optionally, to get experiments from another project as the furthrmind sdk was initiated with. Defaults to None.

        Returns
        -------
        List[Self]
            List with instances of the category class.

        Raises
        ------
        AssertionError
            If ids or names are not specified.
        """

        assert ids, "ids must be specified"
        return cls._get_many(ids, project_id=project_id)

    @classmethod
    def get_all(cls, project_id: str = "") -> List[Self]:
        """
        Method to get all categories.

        Parameters
        ----------
        project_id : str (optional)
            Optionally to get categories from another project as the furthrmind sdk was initiated with, defaults to None

        Returns
        -------
        List[Self]
            List with instances of category class
        """

        return cls._get_all(project_id=project_id)
    
    @classmethod
    @BaseClass._create_instances_decorator(_fetched=False)
    def create(cls, name: str, project_id: str = "") -> Self:
        """
        Method to create a new category

        Parameters
        ----------
        name : str
            Name of the new category

        project_id : str, optional
            Identifier of another project where the category should be created,
            defaults to an empty string

        Returns
        -------
        Self
            The newly created category object
        """
        data = {
            "name": name
        }
        
        cat_id = cls._post(data)
        data = {
            "id": cat_id,
            "name": name
        }
        return data




