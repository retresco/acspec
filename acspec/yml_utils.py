from builtins import str

import yaml

from yaml.composer import Composer
from yaml.reader import Reader
from yaml.scanner import Scanner
from yaml.resolver import Resolver
from yaml.parser import Parser
from yaml.constructor import SafeConstructor

# load with filename and line numbers


def NodeFactory(base_class):
    class NodeBase(base_class):

        def __init__(self, *args, **kwargs):
            if "node_info" in kwargs:
                self.node_info = kwargs.pop("node_info")

            # Python3 compatibility: str#__init__ does not accept arguments
            if base_class != str:
                super(NodeBase, self).__init__(*args, **kwargs)

        def __new__(cls, x, *args, **kwargs):
            if "node_info" in kwargs:
                del kwargs["node_info"]
            return base_class.__new__(cls, x, *args, **kwargs)

    name = '{}_node'.format(base_class.__name__)
    node_class = type(name, (NodeBase,), {})

    return node_class


dict_node = NodeFactory(dict)
list_node = NodeFactory(list)
str_node = NodeFactory(str)


class NodeConstructor(SafeConstructor):
    def construct_yaml_map(self, node):
        obj, = SafeConstructor.construct_yaml_map(self, node)
        return dict_node(obj, node_info=node)

    def construct_yaml_seq(self, node):
        obj, = SafeConstructor.construct_yaml_seq(self, node)
        return list_node(obj, node_info=node)

    def construct_yaml_str(self, node):
        # always return unicode objects
        obj = SafeConstructor.construct_scalar(self, node)
        return str_node(obj, node_info=node)


NodeConstructor.add_constructor(
    u'tag:yaml.org,2002:map',
    NodeConstructor.construct_yaml_map
)

NodeConstructor.add_constructor(
    u'tag:yaml.org,2002:seq',
    NodeConstructor.construct_yaml_seq
)

NodeConstructor.add_constructor(
    u'tag:yaml.org,2002:str',
    NodeConstructor.construct_yaml_str
)


class NodeLoader(Reader, Scanner, Parser, Composer, NodeConstructor, Resolver):
    def __init__(self, stream):
        Reader.__init__(self, stream)
        Scanner.__init__(self)
        Parser.__init__(self)
        Composer.__init__(self)
        SafeConstructor.__init__(self)
        Resolver.__init__(self)


def load_with_node_infos(stream):
    return NodeLoader(stream).get_single_data()


# pretty print


class PrettyDumper(yaml.dumper.Dumper):

    def ignore_aliases(self, _data):
        return True


def str_node_representer(dumper, str_node):
    node = yaml.ScalarNode(tag=u'tag:yaml.org,2002:str', value=str(str_node))
    return node


def dict_node_representer(dumper, dict_node):
    items = dict_node.items()
    items = sorted(items, key=lambda x: x[0])
    return dumper.represent_mapping('tag:yaml.org,2002:map', items)


def list_node_representer(dumper, list_node):
    items = sorted(list_node)
    return dumper.represent_mapping('tag:yaml.org,2002:seq', items)


PrettyDumper.add_representer(str_node, str_node_representer)
PrettyDumper.add_representer(list_node, list_node_representer)
PrettyDumper.add_representer(list, list_node_representer)
PrettyDumper.add_representer(dict_node, dict_node_representer)
PrettyDumper.add_representer(dict, dict_node_representer)


def pretty_print_with_node_infos(data):
    return yaml.dump(
        data, Dumper=PrettyDumper, default_flow_style=False
    )
