import abc


class NodeBase(metaclass=abc.ABCMeta):
    """
    https://developer.mozilla.org/en-US/docs/Web/API/Node
    """
    def appendChild(self, el):
        raise NotImplementedError

    def prependChild(self, el):
        raise NotImplementedError


class ElementBase(NodeBase, metaclass=abc.ABCMeta):
    """
    https://developer.mozilla.org/en-US/docs/Web/API/Element
    """
    def append(self, *els):
        raise NotImplementedError

    def prepend(self, *els):
        raise NotImplementedError

    def replace_children(self, *els):
        raise NotImplementedError


class DocumentBase(NodeBase, metaclass=abc.ABCMeta):
    """
    https://developer.mozilla.org/en-US/docs/Web/API/Document
    """

    def __init__(self, *args, **kwargs):
        self.body: ElementBase = None
