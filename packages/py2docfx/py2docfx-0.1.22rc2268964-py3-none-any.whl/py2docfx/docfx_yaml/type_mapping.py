# -*- coding: utf-8 -*-
#
# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""
Type mapping utilities for converting various documentation types to standardized forms.
"""

# Standard types
PACKAGE = 'package'
METHOD = 'method'
FUNCTION = 'function'
DATA = 'data'
MODULE = 'module'
CLASS = 'class'
EXCEPTION = 'exception'
ATTRIBUTE = 'attribute'
PROPERTY = 'property'

# Pydantic specific types
PYDANTIC_MODEL = 'pydantic_model'
PYDANTIC_FIELD = 'pydantic_field'
PYDANTIC_SETTINGS = 'pydantic_settings'
PYDANTIC_VALIDATOR = 'pydantic_validator'
PYDANTIC_CONFIG = 'pydantic_config'

# Translator-style constants (for compatibility)
CLASS_TYPE = 'class'
EXCEPTION_TYPE = 'exception'
ATTRIBUTE_TYPE = 'attribute'
PYDANTIC_MODEL_TYPE = "pydantic_model"
PYDANTIC_SETTINGS_TYPE = "pydantic_settings"
PYDANTIC_FIELD_TYPE = "pydantic_field"
PYDANTIC_CONFIG_TYPE = "pydantic_config"

# Type groupings for translator functionality
types_contain_constructor = {
    CLASS_TYPE,
    PYDANTIC_MODEL_TYPE,
    PYDANTIC_SETTINGS_TYPE,
    EXCEPTION_TYPE,
    PYDANTIC_CONFIG_TYPE,
}

types_contain_attributes = {
    CLASS_TYPE,
    PYDANTIC_MODEL_TYPE,
    PYDANTIC_SETTINGS_TYPE,
    EXCEPTION_TYPE,
    PYDANTIC_CONFIG_TYPE,
}

attribute_types = {PYDANTIC_FIELD_TYPE, ATTRIBUTE_TYPE}


def map_type_transformations(type_name):
    """
    Apply type transformations to convert various documentation types to standardized forms.
    Used by process_doctree.py for initial type processing.
    
    Args:
        type_name (str): The original type name
        
    Returns:
        str: The transformed type name
    """
    # Type transformations
    if type_name == EXCEPTION or type_name in {PYDANTIC_MODEL, PYDANTIC_SETTINGS, PYDANTIC_CONFIG}:
        return CLASS
    elif type_name == PROPERTY or type_name == PYDANTIC_FIELD:
        return ATTRIBUTE
    elif type_name == PYDANTIC_VALIDATOR:
        return METHOD
    
    # Return original type if no transformation needed
    return type_name


def translator_type_mapping(type_name):
    """
    Apply type mapping transformations for translator processing.
    Used by translator.py for docstring processing.
    Includes both original translator mappings and process_doctree transformations.
    
    Args:
        type_name (str): The original type name
        
    Returns:
        str: The mapped type name
    """
    # First apply the process_doctree style transformations
    transformed_type = map_type_transformations(type_name)
    
    # Then apply the original translator mappings
    mapping = {
        "staticmethod": "method",
        "classmethod": "method",
    }

    return mapping[transformed_type] if transformed_type in mapping else transformed_type