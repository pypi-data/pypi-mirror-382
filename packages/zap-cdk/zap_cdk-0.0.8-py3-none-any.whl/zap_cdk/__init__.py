r'''
# zap-cdk

Create zap automation yaml using the awscdk constructs

# Introduction

This is in {{draft}} mode as there is plenty things to fix but i wanted to get the ball rolling.

# WATCH-THIS-SPACE

Now added nuget
'''
from pkgutil import extend_path
__path__ = extend_path(__path__, __name__)

import abc
import builtins
import datetime
import enum
import typing

import jsii
import publication
import typing_extensions

import typeguard
from importlib.metadata import version as _metadata_package_version
TYPEGUARD_MAJOR_VERSION = int(_metadata_package_version('typeguard').split('.')[0])

def check_type(argname: str, value: object, expected_type: typing.Any) -> typing.Any:
    if TYPEGUARD_MAJOR_VERSION <= 2:
        return typeguard.check_type(argname=argname, value=value, expected_type=expected_type) # type:ignore
    else:
        if isinstance(value, jsii._reference_map.InterfaceDynamicProxy): # pyright: ignore [reportAttributeAccessIssue]
           pass
        else:
            if TYPEGUARD_MAJOR_VERSION == 3:
                typeguard.config.collection_check_strategy = typeguard.CollectionCheckStrategy.ALL_ITEMS # type:ignore
                typeguard.check_type(value=value, expected_type=expected_type) # type:ignore
            else:
                typeguard.check_type(value=value, expected_type=expected_type, collection_check_strategy=typeguard.CollectionCheckStrategy.ALL_ITEMS) # type:ignore

from ._jsii import *

import constructs as _constructs_77d1e7e8


class App(
    _constructs_77d1e7e8.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="zap-cdk.App",
):
    '''The main application construct that aggregates all child constructs and synthesizes them into a single YAML file.'''

    def __init__(self) -> None:
        '''Initializes the App construct.'''
        jsii.create(self.__class__, self, [])

    @jsii.member(jsii_name="synth")
    def synth(
        self,
        output_dir: typing.Optional[builtins.str] = None,
        file_name: typing.Optional[builtins.str] = None,
    ) -> None:
        '''Synthesizes all child constructs into a single YAML file.

        Each construct must implement a ``synth()`` method.

        :param output_dir: -
        :param file_name: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e95ef3650f7e32fe23b005b05fb2bb67ac82df46e6326e92f4f960e7622e4fcf)
            check_type(argname="argument output_dir", value=output_dir, expected_type=type_hints["output_dir"])
            check_type(argname="argument file_name", value=file_name, expected_type=type_hints["file_name"])
        return typing.cast(None, jsii.invoke(self, "synth", [output_dir, file_name]))


__all__ = [
    "App",
]

publication.publish()

def _typecheckingstub__e95ef3650f7e32fe23b005b05fb2bb67ac82df46e6326e92f4f960e7622e4fcf(
    output_dir: typing.Optional[builtins.str] = None,
    file_name: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass
