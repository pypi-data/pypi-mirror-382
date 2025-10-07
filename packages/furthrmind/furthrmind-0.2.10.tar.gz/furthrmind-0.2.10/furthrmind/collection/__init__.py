def get_collection_class(collection_name):
    return eval(collection_name)

from .file import File
from .fielddata import FieldData
from .researchitem import ResearchItem
from .sample import Sample
from .unit import Unit
from .comboboxentry import ComboBoxEntry
from .field import Field
from .datatable import DataTable
from .group import Group
from .experiment import Experiment
from .column import Column
from .project import Project
from .category import Category



