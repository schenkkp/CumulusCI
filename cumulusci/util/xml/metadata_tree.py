from typing import Union

from lxml import etree

from .salesforce_encoding import serialize_xml_for_salesforce

METADATA_NAMESPACE = "http://soap.sforce.com/2006/04/metadata"


def parse(source):
    """Parse a file by path or file object into a Metadata Tree

    The parse() function supports any of the following sources:

        * an open file object (make sure to open it in binary mode)
        * a file-like object that has a .read(byte_count) method returning a byte string on each call
        * a filename string or pathlib Path
        * an HTTP or FTP URL string

    Note that passing a filename or URL is usually faster than passing an open file or file-like object. However, the HTTP/FTP client in libxml2 is rather simple, so things like HTTP authentication require a dedicated URL request library, e.g. urllib2 or requests. These libraries usually provide a file-like object for the result that you can parse from while the response is streaming in.
    """
    if hasattr(source, "as_posix"):  # for pathlib.Path objects
        source = source.as_posix()
    doc = etree.parse(source)
    return MetadataElement(doc.getroot())


def fromstring(source):
    """Parse a Metadata Tree from a string"""
    return MetadataElement(etree.fromstring(source))


class MetadataElement:
    '''A class for representing Metadata in a Pythonic tree.

    After you parse into a MetadataElement tree, you can refer
    to child elements like this:

    >>> from cumulusci.util.xml import metadata_tree
    >>> Package.types.name.text
    'StandardValueSet'
    >>> Package = metadata_tree.fromstring(b"""<?xml version="1.0" encoding="UTF-8"?>
    ... <Package xmlns="http://soap.sforce.com/2006/04/metadata">
    ...     <types>
    ...         <members>CaseReason</members>
    ...         <members>CaseStatus</members>
    ...         <members>CaseType</members>
    ...         <name>StandardValueSet</name>
    ...     </types>
    ...     <version>46.0</version>
    ... </Package>""")
    >>> Package.types.name.text
    'StandardValueSet'

    Or you can refer to them like this:

    >>> Package["types"]["name"].text
    'StandardValueSet'

    That might be convenient if you had the key names in a variable or if you had to refer to an element name
    which would clash with a Python keyword (like `import`) or an instance method (like `text`).

    You can refer to members of lists by index:

    >>> Package["types"]["members"][1]
    <members>CaseStatus</members> element

    There are also methods for finding, appending, inserting and removing nodes, which have their own documentation.
    '''

    __slots__ = ["_element", "_parent", "_ns", "tag"]

    def __init__(
        self, element: etree._Element, parent: etree._Element = None,
    ):
        assert isinstance(element, etree._Element)
        assert len(element.nsmap) == 1, "Only one namespace allowed"
        self._element = element
        self._parent = parent
        self._ns = next(iter(element.nsmap.values()))
        self.tag = element.tag.split("}")[1]

    @property
    def text(self):
        if len(self._element):  # if self has any element children
            return self._get_child("text")
        return self._element.text

    @text.setter
    def text(self, text):
        self._element.text = text

    def _wrap_element(self, child: etree._Element):
        return MetadataElement(child, self._element)

    def _add_namespace(self, tag):
        return "{%s}%s" % (self._ns, tag)

    def _get_child(self, childname):
        child_element = self._element.find(self._add_namespace(childname))
        if child_element is None:
            raise AttributeError(f"{childname} not found in {self.tag}")
        return self._wrap_element(child_element)

    def _create_child(self, tag, text=None):
        element = etree.Element(self._add_namespace(tag))
        element.text = text
        return self._wrap_element(element)

    def __getattr__(self, childname):
        return self._get_child(childname)

    def __getitem__(self, item: Union[int, str]):
        if isinstance(item, int):
            children = self._parent.findall(self._element.tag)
            return self._wrap_element(children[item])
        elif isinstance(item, str):
            return self._get_child(item)

    def append(self, tag: str, text: str = None):
        '''Append a new element at the appropriate place.

        If the parent element (self) already one or more children that match,
        the new element follows the last one.

        Otherwise, the new element goes to the bottom of the parent (self).

        >>> Package = metadata_tree.fromstring(b"""<?xml version="1.0" encoding="UTF-8"?>
        ... <Package xmlns="http://soap.sforce.com/2006/04/metadata">
        ...     <types>
        ...         <members>CaseReason</members>
        ...         <members>CaseStatus</members>
        ...         <members>CaseType</members>
        ...         <name>StandardValueSet</name>
        ...     </types>
        ...     <version>46.0</version>
        ... </Package>""")
        >>> Package.types.append("members", "CaseOfBeer")
        <members>CaseOfBeer</members> element
        >>> print(Package.types.tostring())
        <types xmlns="http://soap.sforce.com/2006/04/metadata">
            <members>CaseReason</members>
            <members>CaseStatus</members>
            <members>CaseType</members>
            <members>CaseOfBeer</members>
            <name>StandardValueSet</name>
        </types>
        '''
        newchild = self._create_child(tag, text)
        same_elements = self._element.findall(self._add_namespace(tag))
        if same_elements:
            last = same_elements[-1]
            index = self._element.index(last)
            self._element.insert(index + 1, newchild._element)
        else:
            self._element.append(newchild._element)
        return newchild

    def insert(self, index: int, tag: str, text: str = None):
        """Insert at a particular index.

        Tag and text can be supplied. Return value is the new element."""
        newchild = self._create_child(tag, text)
        self._element.insert(index, newchild._element)
        return newchild

    def insertBefore(self, oldElement: "MetadataElement", tag: str, text: str = None):
        """Insert before some other element

        Tag and text can be supplied. Return value is the new element."""
        index = self._element.index(oldElement._element)
        return self.insert(index, tag, text)

    def insertAfter(self, oldElement: "MetadataElement", tag: str, text: str = None):
        """Insert after some other element

        Tag and text can be supplied. Return value is the new element."""

        index = self._element.index(oldElement._element)
        return self.insert(index + 1, tag, text)

    def remove(self, metadata_element: "MetadataElement") -> None:
        """Remove an element from its parent (self)"""
        self._element.remove(metadata_element._element)

    def find(self, tag, text=None):
        """Find a single direct child-elements with name `tag`"""
        return next(self._findall(tag, text), None)

    def findall(self, tag, text=None):
        """Find all direct child-elements with name `tag`"""
        return list(self._findall(tag, text))

    def _findall(self, type, text=None):
        def matches(e):
            if text:
                return e.text == text
            else:
                return True

        return (
            self._wrap_element(e)
            for e in self._element.findall(self._add_namespace(type))
            if matches(e)
        )

    def tostring(self, xml_declaration=False):
        """Serialize back to XML.

        The XML Declaration is optional and can be controlled by `xml_declaration`"""
        doc = etree.ElementTree(self._element)
        etree.indent(doc, space="    ")
        return serialize_xml_for_salesforce(doc, xml_declaration=xml_declaration)

    def __eq__(self, other: "MetadataElement"):
        return self._element == other._element

    def __repr__(self):
        children = self._element.getchildren()
        if children:
            contents = f"<!-- {len(children)} children -->"
        elif self.text:
            contents = f"{self.text.strip()}"
        else:
            contents = ""

        return f"<{self.tag}>{contents}</{self.tag}> element"
