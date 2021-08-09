

def soup_attribute_exists(soup_element, tag, attribute=None, attribute_type=None):
    if attribute is None:
        return False if soup_element.find(tag) is None else True
        
    if soup_element.find(tag, {attribute_type: attribute}) is None:
        return False
    else:
        return True