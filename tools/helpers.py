def PrintAtributes(obj):
    attribute_list = [attribute for attribute in dir(obj) if
                      not callable(getattr(obj, attribute)) and attribute.startswith('__') is False]
    for item in attribute_list:
        print(f"{item} : {getattr(obj, item)}")
