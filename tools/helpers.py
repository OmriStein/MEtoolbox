def print_atributes(obj):
    attribute_list = [attribute for attribute in dir(obj) if
                      not callable(getattr(obj, attribute)) and attribute.startswith(
                          '__') is False and attribute.startswith('_') is False]
    for item in attribute_list:
        print(f"{item} : {getattr(obj, item)}")


def parse_input(obj, fields, kwargs):
    """adds attributes specified in kwargs to obj only if they are specified in fields
    fields contain a dictionary of the anticipated attributes and their default value
    if one exists, if not use the '' as a place holder

    :param obj: An object to which add the attributes
    :param dict fields: A dictionary containing the desired attributes with default values
    :param dict kwargs: a dictionary containing the keywords to check

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
def pound_force_to_newtons(val):
    return val * 4.448


def newtons_to_pound_force(val):
    return val / 4.448


def inch_to_millimetre(var):
    return var * 25.4


def millimetre_to_inch(val):
    return val / 25.4
