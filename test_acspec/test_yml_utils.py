import os
import pytest

import schematics

from acspec import package_root
from acspec.yml_utils import load_with_node_infos


def test_load_with_node_infos():
    yml = r"""
    some:
      nested_string: String
      nested_number: 1
    """

    result = load_with_node_infos(yml)

    assert hasattr(result, 'node_info')
    assert result == {
        u'some': {u'nested_string': u'String', u'nested_number': 1}
    }
    assert result.node_info.start_mark.line == 1

    assert hasattr(result['some'], 'node_info')
    assert result['some'] == {u'nested_string': u'String', u'nested_number': 1}
    assert result['some'].node_info.start_mark.line == 2

    assert hasattr(result['some']['nested_string'], 'node_info')
    assert result['some']['nested_string'] == 'String'
    assert result['some']['nested_string'].node_info.start_mark.line == 2
