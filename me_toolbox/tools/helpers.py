"""module containing misc functions"""
import numpy as np


def print_atributes(obj):
    """prints all the attributes of an object
    excluding the dunder attributes and attributes
    with single leading underscore

    :param obj: any object
    """
    # attribute_list = [attribute for attribute in dir(obj) if
    #                   not callable(getattr(obj, attribute)) and attribute.startswith(
    #                       '__') is False and attribute.startswith('_') is False]

    attribute_list = []

    for attribute in dir(obj):
        try:
            if (not callable(getattr(obj, attribute)) and attribute.startswith('__') is False and
                    attribute.startswith('_') is False):
                attribute_list.append(attribute)
        except Exception:
            continue

    for item in attribute_list:
        print(f"{item} : {getattr(obj, item)}")


def parse_input(obj, fields, kwargs):
    """adds attributes specified in kwargs to obj only if they are specified in
    fields contain dictionary of the anticipated attributes and their default value
    if one exists, if not use the '' as placeholder.

    :param obj: An object to which add the attributes
    :param dict fields: A dictionary containing the desired attributes with default values
    :param dict kwargs: dictionary containing the keywords to check

    .. code-block:: python

        from tools import parse_input
        from tools import print_atributes
        class P:
            def __init__(self,**kwargs):
                fields = {'name':'', 'age':'30', 'fav_color':'', 'hobby':'sky'}
                parse_input(self, fields, kwargs)

        p=P(name='Omri', fav_color='blue')
        print_atributes(p)
    """
    for key, val in kwargs.items():
        if key in fields:
            setattr(obj, key, val)
        else:
            raise TypeError(f"__init__() got an unexpected keyword argument '{key}'")

    # check if all attributes were assigned

    error_list = []
    for field in fields:
        if field not in kwargs:  # check if a field was not filled
            if fields[field] != '':  # check if a default value exists
                setattr(obj, field, fields[field])
            else:
                error_list.append(field)

    # raise error if a field is not satisfied
    if len(error_list) == 1:
        raise TypeError(f"__init__() missing 1 required keyword argument: '{error_list[0]}'")
    elif len(error_list) > 1:
        msg = f"__init__() missing {len(error_list)} required keyword arguments: "
        raise TypeError(msg + f"{str(error_list[:-1]).strip('[]')} and {str(error_list[-1])}")


# unit conversions
def lbs_per_in_to_newtons_per_mm(val):
    """converts lbs/in to N/mm

    :param float or list val: value to convert

    :returns: converted value
    :rtype: float or list
    """
    if not isinstance(val, float) and not isinstance(val, list):
        raise ValueError(f"{type(val)} is not valid input type for this function")
    if not isinstance(val, list):
        return val * 0.175
    else:
        return [x * 0.175 for x in val]


def newtons_per_mm_to_lbs_per_in(val):
    """convert newtons to pound max_force

    :param float or list val: value to convert

    :returns: converted value
    :rtype: float or tuple
    """
    if not isinstance(val, float) and not isinstance(val, list):
        raise ValueError(f"{type(val)} is not valid input type for this function")
    if not isinstance(val, list):
        return val * 5.71
    else:
        return [x * 5.71 for x in val]


def inch_to_millimetre(val):
    """converts inches to millimeters

    :param float or list val: value to convert

    :returns: converted value
    :rtype: float or list
    """
    if not isinstance(val, float) and not isinstance(val, list):
        raise ValueError(f"{type(val)} is not valid input type for this function")
    if not isinstance(val, list):
        return val * 25.4
    else:
        return [x * 25.4 for x in val]


def millimetre_to_inch(val):
    """converts millimetres to inches

    :param float or list val: value to convert

    :returns: converted value
    :rtype: float or tuple
    """
    if not isinstance(val, float) and not isinstance(val, list):
        raise ValueError(f"{type(val)} is not valid input type for this function")
    if not isinstance(val, list):
        return val / 25.4
    else:
        return [x /25.4 for x in val]


def percent_to_decimal(var):
    """if input in percent (>=1) convert to decimal"""
    if not isinstance(var, list) and not isinstance(var, tuple):
        dec = var / 100 if var >= 1 else var
    else:
        dec = []
        for val in var:
            if val >= 1:
                # if var is in percentage form divide by 100
                dec.append(val / 100)
            else:
                # if var is in decimal form no correction needed
                dec.append(val)
    return dec


def pol2cart(rho, phi):
    x = rho * np.cos(np.deg2rad(phi))
    y = rho * np.sin(np.deg2rad(phi))
    return x, y
