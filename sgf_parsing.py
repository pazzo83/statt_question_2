import re

class SgfTree:
    def __init__(self, properties=None, children=None):
        self.properties = properties or {}
        self.children = children or []

    def __eq__(self, other):
        if not isinstance(other, SgfTree):
            return False
        for k, v in self.properties.items():
            if k not in other.properties:
                return False
            if other.properties[k] != v:
                return False
        for k in other.properties.keys():
            if k not in self.properties:
                return False
        if len(self.children) != len(other.children):
            return False
        for a, b in zip(self.children, other.children):
            if a != b:
                return False
        return True

    def __ne__(self, other):
        return not self == other


def _is_boundary(char: str):
    if char == "(" or char == ")" or char == ";":
        return True
    
    return False


def _parse_property_key(property_string: str):
    i = 0
    # we will loop through the property string until we hit a bracket, indicating the value
    while i < len(property_string):
        char = property_string[i]
        if char == "[":
            # we are in the value part of the string
            break
        elif char < "A" or char > "Z":
            # here we check to make sure the key is only upper case letters
            raise ValueError(f"Character {char} is invalid.  Only upper case letters are permitted for keys")
        i += 1
    
    # what we've iterated over thus far represents the key, and we also return the rest of the string to
    # later parse the value
    return property_string[:i], property_string[i:]


def _extract_property_value(property_string: str):
    property_string = re.sub(r"\t|\\\n|\\\r", " ", property_string)
    return re.sub(r"\\(?!\\)", "", property_string)


def _parse_property_values(property_string: str):
    values = []
    escaped = False
    in_property = False
    i = 0
    value_idx = 0

    while i < len(property_string):
        if escaped:
            escaped = False
        else:
            char = property_string[i]
            if char == "[":
                # we are in the property
                # we set the part of the string with the value to start at the next index
                value_idx = i + 1
                in_property = True
            elif char == "]":
                # we are exiting the property value
                # now we can extract the value itself
                values.append(_extract_property_value(property_string[value_idx:i]))
                in_property=False
            elif char == "\\":
                escaped = True
            elif in_property == False:
                break
        i += 1
    
    if len(values) == 0:
        raise ValueError("This is not a valid SGF string - no values present")
    
    return values, property_string[i:]
        

def _parse_property(property_string: str):
    key, property_string = _parse_property_key(property_string)
    values, property_string = _parse_property_values(property_string)

    return {key: values}, property_string


def _parse_properties(properties_string: str):
    properties = {}
    while properties_string != "":
        new_property, properties_string = _parse_property(properties_string)
        # update dictionary
        properties = {**properties, **new_property}
    
    return properties


def _parse_inner_node(node_string: str):
    # nothing is inside this node, something is wrong
    if node_string == "" or node_string[0] != ";":
        raise ValueError("The node string is not well-formed - missing semi-colon!")
    
    escaped = False

    # similarly here, we start at 1 because we've already processed the boundary character
    i = 1
    while i < len(node_string):
        if escaped:
            escaped = False
        else:
            char = node_string[i]
            if _is_boundary(char):
                # we've reached a boundary signifying the end of properties in this node string
                # we exit the loop
                break
            elif char == "\\":
                escaped = True
        i += 1
    
    # our properties are now one past the initial index (so one past the boundary) to the end boundary we
    # reached by iterating
    properties_string = node_string[1:i]
    
    # the rest of our node is now left for processing
    node_string = node_string[i:]

    # first, extract the properites from our properties string
    properties = _parse_properties(properties_string)

    # then, loop through the rest of our node string to see if we find any child nodes
    children = []

    # we loop while there is still a string left to process
    while len(node_string) > 0:
        # recursive call here - we parse a node if we find it and add it to this node's children
        child, node_string = _parse_node(node_string)
        if child is None:
            # that parsing didn't give us anything, let's try to parse the inner node
            if len(children) == 0:
                child, node_string = _parse_inner_node(node_string)
            else:
                raise ValueError("The SGF string is not valid.")
        children.append(child)
    
    # finally we return the SgfTree object and what is left of the string to process
    return SgfTree(properties, children), node_string


def _parse_node(input_string: str):
    # To help with recursive nature, if we hit a node that is just an empty string
    # or does not begin with the proper boundary, we just return None and continue.
    if input_string == "" or input_string[0] != "(":
        return None, input_string

    # initialize node level so we know when to break out of the while loop
    node_level = 1
    escaped = False

    # we start at 1 because we've already processed the boundary character
    i = 1

    while i < len(input_string):
        if escaped:
            escaped = False
        else:
            char = input_string[i]
            if char == ")":
                # at the end of this node, let's move up a level
                node_level -= 1
                if node_level == 0:
                    # if we have moved back to the base node, we are done
                    break
            elif char == "(":
                # starting a new node
                node_level += 1
            elif char == "\\":
                # escape sign
                escaped = True
        i += 1

    # restrict our node string to being from index 1 (so all but the first character, which is a boundary) to the index we've
    # iterated through (which is the other boundary).
    node_string = input_string[1:i]
    # parse this node
    node, _ = _parse_inner_node(node_string)

    # now that we've processed this node, we move one beyond the boundary and return that string,
    # as well as the SgfTree we created
    return node, input_string[i+1:]


def parse(input_string: str ) -> SgfTree:
    """Parse an SGF String."""
    sgfTree, input_string = _parse_node(input_string)
    if sgfTree is None or len(input_string) > 0:
        raise ValueError("Error parsing SGF string.")
    return sgfTree
