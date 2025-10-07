from enum import Enum


class DbtSubType(str, Enum):
    """
    Enum for dbt-specific subtypes that map to ItemType categories.

    These subtypes represent specific dbt concepts and their behaviors.
    """

    # DATABASE subtypes
    DATABASE = "database"

    # SCHEMA subtypes
    SCHEMA = "schema"

    # TABLE subtypes
    MODEL = "model"
    SNAPSHOT = "snapshot"
    SEED = "seed"

    # COLUMN subtypes
    COLUMN = "column"

    # DOC subtypes
    DOC_BLOCK = "doc_block"
    DOCUMENTATION = "documentation"

    # TEST subtypes
    TEST = "test"
    UNIT_TEST = "unit_test"

    # LOGIC subtypes
    MACRO = "macro"
    ANALYSIS = "analysis"
    OPERATION = "operation"

    # CONFIG subtypes
    PROJECT = "project"
    PROFILE = "profile"
    PACKAGE = "package"
    SOURCE = "source"
    EXPOSURE = "exposure"
    METRIC = "metric"
    SEMANTIC_MODEL = "semantic_model"
    SAVED_QUERY = "saved_query"
