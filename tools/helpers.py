def PrintAtributes(obj):
    attribute_list = [attribute for attribute in dir(obj) if
                      not callable(getattr(obj, attribute)) and attribute.startswith(
                          '__') is False and attribute.startswith('_') is False]
    for item in attribute_list:
        print(f"{item} : {getattr(obj, item)}")


def PoundForceToNewtons(val):
    return val * 4.448


def NewtonsToPoundForce(val):
    return val / 4.448


def InchToMillimetre(var):
    return var * 25.4


def MillimetreToInch(val):
    return val / 25.4
