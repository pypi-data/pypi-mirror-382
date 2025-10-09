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


class ActiveScanConfig(
    _constructs_77d1e7e8.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="zap-cdk.ActiveScanConfig",
):
    '''Class representing the active scan configuration.

    :class: ActiveScanConfig
    :extends: Construct
    '''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        props: "IActiveScanConfigProps",
    ) -> None:
        '''Creates an instance of ActiveScanConfig.

        :param scope: - The scope in which this construct is defined.
        :param id: - The ID of the construct.
        :param props: - The properties of the active scan configuration.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ca23190d78d2919234c733f19bc05216a18406399e366571582fc581ddd3a04d)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
            check_type(argname="argument props", value=props, expected_type=type_hints["props"])
        jsii.create(self.__class__, self, [scope, id, props])

    @jsii.member(jsii_name="toYaml")
    def to_yaml(self) -> "IActiveScanConfig":
        '''Converts the active scan configuration to YAML format.

        :return: The active scan configuration in YAML format.
        '''
        return typing.cast("IActiveScanConfig", jsii.invoke(self, "toYaml", []))

    @builtins.property
    @jsii.member(jsii_name="config")
    def config(self) -> "IActiveScanConfig":
        '''The active scan configuration properties.'''
        return typing.cast("IActiveScanConfig", jsii.get(self, "config"))

    @config.setter
    def config(self, value: "IActiveScanConfig") -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8b0ddb7eb853d9c049ca8348df0137f1a23ad23b50e811df2bcaff3e9c4b14b9)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "config", value) # pyright: ignore[reportArgumentType]


class ActiveScanJob(
    _constructs_77d1e7e8.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="zap-cdk.ActiveScanJob",
):
    '''Class representing an active scan job.

    :class: ActiveScanJob
    :extends: Construct
    '''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        props: "IActiveScanJob",
    ) -> None:
        '''Creates an instance of ActiveScanJob.

        :param scope: - The scope in which this construct is defined.
        :param id: - The ID of the construct.
        :param props: - The properties of the active scan job.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a2085f7ef0b4920076c5afcbcde68feba9d61419b758eea5adcb3e987f983c2e)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
            check_type(argname="argument props", value=props, expected_type=type_hints["props"])
        jsii.create(self.__class__, self, [scope, id, props])

    @jsii.member(jsii_name="toYaml")
    def to_yaml(self) -> "IActiveScanJob":
        '''Converts the active scan job to YAML format.

        :return: The active scan job in YAML format.
        '''
        return typing.cast("IActiveScanJob", jsii.invoke(self, "toYaml", []))

    @builtins.property
    @jsii.member(jsii_name="job")
    def job(self) -> "IActiveScanJob":
        '''The active scan job properties.'''
        return typing.cast("IActiveScanJob", jsii.get(self, "job"))

    @job.setter
    def job(self, value: "IActiveScanJob") -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__86d1d4b9c76f03b522305295eeab25e3ea258092276c6d3372313ee7b559d438)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "job", value) # pyright: ignore[reportArgumentType]


class ActiveScanPolicyConfig(
    _constructs_77d1e7e8.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="zap-cdk.ActiveScanPolicyConfig",
):
    '''Class representing the active scan policy configuration.

    :class: ActiveScanPolicyConfig
    :extends: Construct
    '''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        props: "IActiveScanPolicyProps",
    ) -> None:
        '''Creates an instance of ActiveScanPolicyConfig.

        :param scope: - The scope in which this construct is defined.
        :param id: - The ID of the construct.
        :param props: - The properties of the active scan policy configuration.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__084e96fc35d1b7dbc9517ca12daa47f386f20e22c63943d6e4d015175436d854)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
            check_type(argname="argument props", value=props, expected_type=type_hints["props"])
        jsii.create(self.__class__, self, [scope, id, props])

    @jsii.member(jsii_name="toYaml")
    def to_yaml(self) -> "IActiveScanPolicy":
        '''Converts the active scan policy configuration to YAML format.

        :return: The active scan policy configuration in YAML format.
        '''
        return typing.cast("IActiveScanPolicy", jsii.invoke(self, "toYaml", []))

    @builtins.property
    @jsii.member(jsii_name="config")
    def config(self) -> "IActiveScanPolicy":
        return typing.cast("IActiveScanPolicy", jsii.get(self, "config"))

    @config.setter
    def config(self, value: "IActiveScanPolicy") -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6534e2afae36b77e40210a17de82410447fcc2457c8a1a43851fe2de50c3232a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "config", value) # pyright: ignore[reportArgumentType]


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


class DelayConfig(
    _constructs_77d1e7e8.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="zap-cdk.DelayConfig",
):
    '''Class representing the delay configuration.

    :class: DelayConfig
    :extends: Construct
    '''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        props: "IDelayProps",
    ) -> None:
        '''Creates an instance of DelayConfig.

        :param scope: - The scope in which this construct is defined.
        :param id: - The ID of the construct.
        :param props: - The properties of the delay configuration.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ad662c09c49cf027d20555f383009c853b03d18c2bd1743d5d72a3a30cb16a2b)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
            check_type(argname="argument props", value=props, expected_type=type_hints["props"])
        jsii.create(self.__class__, self, [scope, id, props])

    @jsii.member(jsii_name="toYaml")
    def to_yaml(self) -> "IDelay":
        '''Converts the delay configuration to YAML format.

        :return: The delay configuration in YAML format.
        '''
        return typing.cast("IDelay", jsii.invoke(self, "toYaml", []))

    @builtins.property
    @jsii.member(jsii_name="config")
    def config(self) -> "IDelay":
        return typing.cast("IDelay", jsii.get(self, "config"))

    @config.setter
    def config(self, value: "IDelay") -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1f010482d7efc9dd5289ea9cf8e12a22938f603166172abd5c53ba454fc3fa02)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "config", value) # pyright: ignore[reportArgumentType]


class EnvironmentConfig(
    _constructs_77d1e7e8.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="zap-cdk.EnvironmentConfig",
):
    '''Class representing the environment configuration.

    :class: EnvironmentConfig
    :extends: Construct
    '''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        props: "IEnvironmentProps",
    ) -> None:
        '''Creates an instance of EnvironmentConfig.

        :param scope: - The scope in which this construct is defined.
        :param id: - The ID of the construct.
        :param props: - The properties of the environment configuration.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4ec4069b55c551c9ec1c740b290092b04b969a1fb7df628e695c20e6d29300cf)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
            check_type(argname="argument props", value=props, expected_type=type_hints["props"])
        jsii.create(self.__class__, self, [scope, id, props])

    @jsii.member(jsii_name="toYaml")
    def to_yaml(self) -> "IEnvironment":
        '''Converts the environment configuration to YAML format.

        :return: The environment configuration in YAML format.
        '''
        return typing.cast("IEnvironment", jsii.invoke(self, "toYaml", []))

    @builtins.property
    @jsii.member(jsii_name="config")
    def config(self) -> "IEnvironment":
        return typing.cast("IEnvironment", jsii.get(self, "config"))

    @config.setter
    def config(self, value: "IEnvironment") -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f334f1cc55832e44ee7730d1527b668c98c2c6f940f41152ee2bd5559a7654bc)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "config", value) # pyright: ignore[reportArgumentType]


class ExitStatusConfig(
    _constructs_77d1e7e8.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="zap-cdk.ExitStatusConfig",
):
    '''Class representing the exit status configuration.

    :class: ExitStatusConfig
    :extends: Construct
    '''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        props: "IExitStatusProps",
    ) -> None:
        '''Creates an instance of ExitStatusConfig.

        :param scope: - The scope in which this construct is defined.
        :param id: - The ID of the construct.
        :param props: - The properties of the exit status configuration.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b1955ace043e11fd285dea3a9a4f27efa745bc54732188e249d2b9c62b8f884b)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
            check_type(argname="argument props", value=props, expected_type=type_hints["props"])
        jsii.create(self.__class__, self, [scope, id, props])

    @jsii.member(jsii_name="toYaml")
    def to_yaml(self) -> "IExitStatus":
        '''Converts the exit status configuration to YAML format.

        :return: The exit status configuration in YAML format.
        '''
        return typing.cast("IExitStatus", jsii.invoke(self, "toYaml", []))

    @builtins.property
    @jsii.member(jsii_name="config")
    def config(self) -> "IExitStatus":
        return typing.cast("IExitStatus", jsii.get(self, "config"))

    @config.setter
    def config(self, value: "IExitStatus") -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__289286215f39bb84bedf9cb35a0ff36ab346da8b4ca243aa51e23e1303536447)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "config", value) # pyright: ignore[reportArgumentType]


class ExportConfig(
    _constructs_77d1e7e8.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="zap-cdk.ExportConfig",
):
    '''Class representing the export configuration.

    :class: ExportConfig
    :extends: Construct
    '''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        props: "IExportProps",
    ) -> None:
        '''Creates an instance of ExportConfig.

        :param scope: - The scope in which this construct is defined.
        :param id: - The ID of the construct.
        :param props: - The properties of the export configuration.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4037c2c6d5e527d3c1b388ce5b3e6d225fcc975e37f6355310e1f858b46e8208)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
            check_type(argname="argument props", value=props, expected_type=type_hints["props"])
        jsii.create(self.__class__, self, [scope, id, props])

    @jsii.member(jsii_name="toYaml")
    def to_yaml(self) -> "IExport":
        '''Converts the export configuration to YAML format.

        :return: The export configuration in YAML format.
        '''
        return typing.cast("IExport", jsii.invoke(self, "toYaml", []))

    @builtins.property
    @jsii.member(jsii_name="config")
    def config(self) -> "IExport":
        return typing.cast("IExport", jsii.get(self, "config"))

    @config.setter
    def config(self, value: "IExport") -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7aa75e755f38fe6a850589f12376c85273dca7d059072033f1d401b2fde3263b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "config", value) # pyright: ignore[reportArgumentType]


class GraphQLConfig(
    _constructs_77d1e7e8.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="zap-cdk.GraphQLConfig",
):
    '''Class representing the GraphQL configuration.

    :class: GraphQLConfig
    :extends: Construct
    '''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        props: "IGraphQLProps",
    ) -> None:
        '''Creates an instance of GraphQLConfig.

        :param scope: - The scope in which this construct is defined.
        :param id: - The ID of the construct.
        :param props: - The properties of the GraphQL configuration.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8a6b9b787a6cc20c237882afd6f3d053908c0ec60393409ee1fe68d4f463ca21)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
            check_type(argname="argument props", value=props, expected_type=type_hints["props"])
        jsii.create(self.__class__, self, [scope, id, props])

    @jsii.member(jsii_name="toYaml")
    def to_yaml(self) -> "IGraphQL":
        return typing.cast("IGraphQL", jsii.invoke(self, "toYaml", []))

    @builtins.property
    @jsii.member(jsii_name="config")
    def config(self) -> "IGraphQL":
        return typing.cast("IGraphQL", jsii.get(self, "config"))

    @config.setter
    def config(self, value: "IGraphQL") -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8a017182eca10655d919e00f96289d33b3cc9b9cd5e73c811fca6255c667e97a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "config", value) # pyright: ignore[reportArgumentType]


@jsii.interface(jsii_type="zap-cdk.IActiveScan")
class IActiveScan(typing_extensions.Protocol):
    '''
    :interface:

    IActiveScan
    Represents an active scan configuration.
    :property: {boolean} [alwaysRun] - If set and the job is enabled, then it will run even if the plan exits early, default: false.
    '''

    @builtins.property
    @jsii.member(jsii_name="parameters")
    def parameters(self) -> "IActiveScanParameters":
        ...

    @parameters.setter
    def parameters(self, value: "IActiveScanParameters") -> None:
        ...

    @builtins.property
    @jsii.member(jsii_name="type")
    def type(self) -> builtins.str:
        ...

    @type.setter
    def type(self, value: builtins.str) -> None:
        ...

    @builtins.property
    @jsii.member(jsii_name="alwaysRun")
    def always_run(self) -> typing.Optional[builtins.bool]:
        ...

    @always_run.setter
    def always_run(self, value: typing.Optional[builtins.bool]) -> None:
        ...

    @builtins.property
    @jsii.member(jsii_name="enabled")
    def enabled(self) -> typing.Optional[builtins.bool]:
        ...

    @enabled.setter
    def enabled(self, value: typing.Optional[builtins.bool]) -> None:
        ...

    @builtins.property
    @jsii.member(jsii_name="policyDefinition")
    def policy_definition(self) -> typing.Optional["IPolicyDefinition"]:
        ...

    @policy_definition.setter
    def policy_definition(self, value: typing.Optional["IPolicyDefinition"]) -> None:
        ...


class _IActiveScanProxy:
    '''
    :interface:

    IActiveScan
    Represents an active scan configuration.
    :property: {boolean} [alwaysRun] - If set and the job is enabled, then it will run even if the plan exits early, default: false.
    '''

    __jsii_type__: typing.ClassVar[str] = "zap-cdk.IActiveScan"

    @builtins.property
    @jsii.member(jsii_name="parameters")
    def parameters(self) -> "IActiveScanParameters":
        return typing.cast("IActiveScanParameters", jsii.get(self, "parameters"))

    @parameters.setter
    def parameters(self, value: "IActiveScanParameters") -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__39ba182886f05e983ee5ba17ac6171a5e7e1fe447080de2760994b3f5326d4be)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "parameters", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="type")
    def type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "type"))

    @type.setter
    def type(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7b0bd039fd8636869ef24803522658fc1e68d212c7fecbd1c149915758f3bdc5)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "type", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="alwaysRun")
    def always_run(self) -> typing.Optional[builtins.bool]:
        return typing.cast(typing.Optional[builtins.bool], jsii.get(self, "alwaysRun"))

    @always_run.setter
    def always_run(self, value: typing.Optional[builtins.bool]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__004435ee8a412d4b14b073dc20f147901f1b1cccd8e834cab7bbfd502eda6165)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "alwaysRun", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="enabled")
    def enabled(self) -> typing.Optional[builtins.bool]:
        return typing.cast(typing.Optional[builtins.bool], jsii.get(self, "enabled"))

    @enabled.setter
    def enabled(self, value: typing.Optional[builtins.bool]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__104fb8bf3aefd428754fed2d01a73dfe8aa4d38d50907b2b71078badb849a4a5)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "enabled", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="policyDefinition")
    def policy_definition(self) -> typing.Optional["IPolicyDefinition"]:
        return typing.cast(typing.Optional["IPolicyDefinition"], jsii.get(self, "policyDefinition"))

    @policy_definition.setter
    def policy_definition(self, value: typing.Optional["IPolicyDefinition"]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__fa1e8f5dea3906034fd168f7578e951d822d07b22b2e00eb2a615af8da88e31b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "policyDefinition", value) # pyright: ignore[reportArgumentType]

# Adding a "__jsii_proxy_class__(): typing.Type" function to the interface
typing.cast(typing.Any, IActiveScan).__jsii_proxy_class__ = lambda : _IActiveScanProxy


@jsii.interface(jsii_type="zap-cdk.IActiveScanConfig")
class IActiveScanConfig(typing_extensions.Protocol):
    '''
    :interface:

    IActiveScanConfig
    Represents the configuration for an active scan.
    :property: {boolean} [alwaysRun] - If set and the job is enabled, then it will run even if the plan exits early, default: false.
    '''

    @builtins.property
    @jsii.member(jsii_name="parameters")
    def parameters(self) -> "IActiveScanConfigParameters":
        ...

    @parameters.setter
    def parameters(self, value: "IActiveScanConfigParameters") -> None:
        ...

    @builtins.property
    @jsii.member(jsii_name="type")
    def type(self) -> builtins.str:
        ...

    @type.setter
    def type(self, value: builtins.str) -> None:
        ...

    @builtins.property
    @jsii.member(jsii_name="alwaysRun")
    def always_run(self) -> typing.Optional[builtins.bool]:
        ...

    @always_run.setter
    def always_run(self, value: typing.Optional[builtins.bool]) -> None:
        ...

    @builtins.property
    @jsii.member(jsii_name="enabled")
    def enabled(self) -> typing.Optional[builtins.bool]:
        ...

    @enabled.setter
    def enabled(self, value: typing.Optional[builtins.bool]) -> None:
        ...

    @builtins.property
    @jsii.member(jsii_name="excludePaths")
    def exclude_paths(self) -> typing.Optional[typing.List[builtins.str]]:
        ...

    @exclude_paths.setter
    def exclude_paths(self, value: typing.Optional[typing.List[builtins.str]]) -> None:
        ...


class _IActiveScanConfigProxy:
    '''
    :interface:

    IActiveScanConfig
    Represents the configuration for an active scan.
    :property: {boolean} [alwaysRun] - If set and the job is enabled, then it will run even if the plan exits early, default: false.
    '''

    __jsii_type__: typing.ClassVar[str] = "zap-cdk.IActiveScanConfig"

    @builtins.property
    @jsii.member(jsii_name="parameters")
    def parameters(self) -> "IActiveScanConfigParameters":
        return typing.cast("IActiveScanConfigParameters", jsii.get(self, "parameters"))

    @parameters.setter
    def parameters(self, value: "IActiveScanConfigParameters") -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3a075a4adb319226a1fef8d3ee23b97da0450591a4f1041b979ffb434e6971b9)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "parameters", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="type")
    def type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "type"))

    @type.setter
    def type(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f9d6b390fdf9ae292ef9c534c03cd0a93631b7d556fa0ec4c2338fd3863b0fd6)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "type", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="alwaysRun")
    def always_run(self) -> typing.Optional[builtins.bool]:
        return typing.cast(typing.Optional[builtins.bool], jsii.get(self, "alwaysRun"))

    @always_run.setter
    def always_run(self, value: typing.Optional[builtins.bool]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a1a67ac88b2e807e0eafad36d3b0c62e47ac65fa21c59724ebcdff4f589fd8b4)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "alwaysRun", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="enabled")
    def enabled(self) -> typing.Optional[builtins.bool]:
        return typing.cast(typing.Optional[builtins.bool], jsii.get(self, "enabled"))

    @enabled.setter
    def enabled(self, value: typing.Optional[builtins.bool]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__58e83aa4d79baab3880246fb63a5771df60728fa4e9c39bfb32090951c81413d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "enabled", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="excludePaths")
    def exclude_paths(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "excludePaths"))

    @exclude_paths.setter
    def exclude_paths(self, value: typing.Optional[typing.List[builtins.str]]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4d4af7ae1fb657b91515fb482073ea8c575aaa3bfed3c202c18010947de8b902)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "excludePaths", value) # pyright: ignore[reportArgumentType]

# Adding a "__jsii_proxy_class__(): typing.Type" function to the interface
typing.cast(typing.Any, IActiveScanConfig).__jsii_proxy_class__ = lambda : _IActiveScanConfigProxy


@jsii.interface(jsii_type="zap-cdk.IActiveScanConfigParameters")
class IActiveScanConfigParameters(typing_extensions.Protocol):
    '''
    :interface:

    IActiveScanConfigParameters
    Represents the parameters for configuring an active scan.
    :property: {IInputVectors} inputVectors - The input vectors used during the active scan.
    '''

    @builtins.property
    @jsii.member(jsii_name="inputVectors")
    def input_vectors(self) -> "IInputVectors":
        ...

    @input_vectors.setter
    def input_vectors(self, value: "IInputVectors") -> None:
        ...

    @builtins.property
    @jsii.member(jsii_name="defaultPolicy")
    def default_policy(self) -> typing.Optional[builtins.str]:
        ...

    @default_policy.setter
    def default_policy(self, value: typing.Optional[builtins.str]) -> None:
        ...

    @builtins.property
    @jsii.member(jsii_name="handleAntiCSRFTokens")
    def handle_anti_csrf_tokens(self) -> typing.Optional[builtins.bool]:
        ...

    @handle_anti_csrf_tokens.setter
    def handle_anti_csrf_tokens(self, value: typing.Optional[builtins.bool]) -> None:
        ...

    @builtins.property
    @jsii.member(jsii_name="injectPluginIdInHeader")
    def inject_plugin_id_in_header(self) -> typing.Optional[builtins.bool]:
        ...

    @inject_plugin_id_in_header.setter
    def inject_plugin_id_in_header(self, value: typing.Optional[builtins.bool]) -> None:
        ...

    @builtins.property
    @jsii.member(jsii_name="maxAlertsPerRule")
    def max_alerts_per_rule(self) -> typing.Optional[jsii.Number]:
        ...

    @max_alerts_per_rule.setter
    def max_alerts_per_rule(self, value: typing.Optional[jsii.Number]) -> None:
        ...

    @builtins.property
    @jsii.member(jsii_name="maxRuleDurationInMins")
    def max_rule_duration_in_mins(self) -> typing.Optional[jsii.Number]:
        ...

    @max_rule_duration_in_mins.setter
    def max_rule_duration_in_mins(self, value: typing.Optional[jsii.Number]) -> None:
        ...

    @builtins.property
    @jsii.member(jsii_name="maxScanDurationInMins")
    def max_scan_duration_in_mins(self) -> typing.Optional[jsii.Number]:
        ...

    @max_scan_duration_in_mins.setter
    def max_scan_duration_in_mins(self, value: typing.Optional[jsii.Number]) -> None:
        ...

    @builtins.property
    @jsii.member(jsii_name="threadPerHost")
    def thread_per_host(self) -> typing.Optional[jsii.Number]:
        ...

    @thread_per_host.setter
    def thread_per_host(self, value: typing.Optional[jsii.Number]) -> None:
        ...


class _IActiveScanConfigParametersProxy:
    '''
    :interface:

    IActiveScanConfigParameters
    Represents the parameters for configuring an active scan.
    :property: {IInputVectors} inputVectors - The input vectors used during the active scan.
    '''

    __jsii_type__: typing.ClassVar[str] = "zap-cdk.IActiveScanConfigParameters"

    @builtins.property
    @jsii.member(jsii_name="inputVectors")
    def input_vectors(self) -> "IInputVectors":
        return typing.cast("IInputVectors", jsii.get(self, "inputVectors"))

    @input_vectors.setter
    def input_vectors(self, value: "IInputVectors") -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b504fefd5672cfcbe39306e21918ab5381b4eaec7f3f761ef7c4447625eb6557)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "inputVectors", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="defaultPolicy")
    def default_policy(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "defaultPolicy"))

    @default_policy.setter
    def default_policy(self, value: typing.Optional[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8a6b7b10c17cf59237cb48861597a4dc8fcff0f23d4d3bc404bca53cfba52b5b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "defaultPolicy", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="handleAntiCSRFTokens")
    def handle_anti_csrf_tokens(self) -> typing.Optional[builtins.bool]:
        return typing.cast(typing.Optional[builtins.bool], jsii.get(self, "handleAntiCSRFTokens"))

    @handle_anti_csrf_tokens.setter
    def handle_anti_csrf_tokens(self, value: typing.Optional[builtins.bool]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__188d3374fb5d88ecba26fdaa6cd996db8365289ea3efcc4cf2eaf3331576fcee)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "handleAntiCSRFTokens", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="injectPluginIdInHeader")
    def inject_plugin_id_in_header(self) -> typing.Optional[builtins.bool]:
        return typing.cast(typing.Optional[builtins.bool], jsii.get(self, "injectPluginIdInHeader"))

    @inject_plugin_id_in_header.setter
    def inject_plugin_id_in_header(self, value: typing.Optional[builtins.bool]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f3c666b269b07d71a7d81432403d0216b225cbb6e4c188b82159daa9e25eb8f1)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "injectPluginIdInHeader", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="maxAlertsPerRule")
    def max_alerts_per_rule(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "maxAlertsPerRule"))

    @max_alerts_per_rule.setter
    def max_alerts_per_rule(self, value: typing.Optional[jsii.Number]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__69183eaa0cf577d63814c3f264a6c499e6f0786015071376d7130b8c2eb9f31a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "maxAlertsPerRule", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="maxRuleDurationInMins")
    def max_rule_duration_in_mins(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "maxRuleDurationInMins"))

    @max_rule_duration_in_mins.setter
    def max_rule_duration_in_mins(self, value: typing.Optional[jsii.Number]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5c61df97e2f02b213285e769aecb93dfb5e8601dcf5a6ad7f2655fbf3175780a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "maxRuleDurationInMins", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="maxScanDurationInMins")
    def max_scan_duration_in_mins(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "maxScanDurationInMins"))

    @max_scan_duration_in_mins.setter
    def max_scan_duration_in_mins(self, value: typing.Optional[jsii.Number]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__66723e19545dbce6449385d557525fcef88a30cd54b737af430bacd13ed37ba7)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "maxScanDurationInMins", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="threadPerHost")
    def thread_per_host(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "threadPerHost"))

    @thread_per_host.setter
    def thread_per_host(self, value: typing.Optional[jsii.Number]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f17890a7f68c9ab7f3872c9c300cbe6490a4d9ff14e0aaedacad5d862f90e76f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "threadPerHost", value) # pyright: ignore[reportArgumentType]

# Adding a "__jsii_proxy_class__(): typing.Type" function to the interface
typing.cast(typing.Any, IActiveScanConfigParameters).__jsii_proxy_class__ = lambda : _IActiveScanConfigParametersProxy


@jsii.interface(jsii_type="zap-cdk.IActiveScanConfigProps")
class IActiveScanConfigProps(typing_extensions.Protocol):
    '''Properties for the ActiveScanConfig construct.

    :interface: IActiveScanConfigProps
    :property: {IActiveScanConfig} activeScanConfig - The active scan configuration.
    '''

    @builtins.property
    @jsii.member(jsii_name="activeScanConfig")
    def active_scan_config(self) -> IActiveScanConfig:
        ...

    @active_scan_config.setter
    def active_scan_config(self, value: IActiveScanConfig) -> None:
        ...


class _IActiveScanConfigPropsProxy:
    '''Properties for the ActiveScanConfig construct.

    :interface: IActiveScanConfigProps
    :property: {IActiveScanConfig} activeScanConfig - The active scan configuration.
    '''

    __jsii_type__: typing.ClassVar[str] = "zap-cdk.IActiveScanConfigProps"

    @builtins.property
    @jsii.member(jsii_name="activeScanConfig")
    def active_scan_config(self) -> IActiveScanConfig:
        return typing.cast(IActiveScanConfig, jsii.get(self, "activeScanConfig"))

    @active_scan_config.setter
    def active_scan_config(self, value: IActiveScanConfig) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__fdf7075df4fdf325b279c35c6411108f836770d9e1348b31b8e521221f02c527)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "activeScanConfig", value) # pyright: ignore[reportArgumentType]

# Adding a "__jsii_proxy_class__(): typing.Type" function to the interface
typing.cast(typing.Any, IActiveScanConfigProps).__jsii_proxy_class__ = lambda : _IActiveScanConfigPropsProxy


@jsii.interface(jsii_type="zap-cdk.IActiveScanJob")
class IActiveScanJob(typing_extensions.Protocol):
    '''
    :interface:

    IActiveScanJob
    Represents an active scan job.
    :property: {IActiveScan} activeScan - The active scan configuration.
    '''

    @builtins.property
    @jsii.member(jsii_name="activeScan")
    def active_scan(self) -> IActiveScan:
        ...

    @active_scan.setter
    def active_scan(self, value: IActiveScan) -> None:
        ...


class _IActiveScanJobProxy:
    '''
    :interface:

    IActiveScanJob
    Represents an active scan job.
    :property: {IActiveScan} activeScan - The active scan configuration.
    '''

    __jsii_type__: typing.ClassVar[str] = "zap-cdk.IActiveScanJob"

    @builtins.property
    @jsii.member(jsii_name="activeScan")
    def active_scan(self) -> IActiveScan:
        return typing.cast(IActiveScan, jsii.get(self, "activeScan"))

    @active_scan.setter
    def active_scan(self, value: IActiveScan) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b3ddc3fce98847c341bb07c7b507c0bf58f73e9468bfa12600b190bc8bdef8f7)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "activeScan", value) # pyright: ignore[reportArgumentType]

# Adding a "__jsii_proxy_class__(): typing.Type" function to the interface
typing.cast(typing.Any, IActiveScanJob).__jsii_proxy_class__ = lambda : _IActiveScanJobProxy


@jsii.interface(jsii_type="zap-cdk.IActiveScanParameters")
class IActiveScanParameters(typing_extensions.Protocol):
    '''
    :interface:

    IActiveScanParameters
    Represents the parameters for an active scan.
    :property: {ITest[]} [tests] - List of tests to perform.
    '''

    @builtins.property
    @jsii.member(jsii_name="addQueryParam")
    def add_query_param(self) -> typing.Optional[builtins.bool]:
        ...

    @add_query_param.setter
    def add_query_param(self, value: typing.Optional[builtins.bool]) -> None:
        ...

    @builtins.property
    @jsii.member(jsii_name="context")
    def context(self) -> typing.Optional[builtins.str]:
        ...

    @context.setter
    def context(self, value: typing.Optional[builtins.str]) -> None:
        ...

    @builtins.property
    @jsii.member(jsii_name="defaultPolicy")
    def default_policy(self) -> typing.Optional[builtins.str]:
        ...

    @default_policy.setter
    def default_policy(self, value: typing.Optional[builtins.str]) -> None:
        ...

    @builtins.property
    @jsii.member(jsii_name="delayInMs")
    def delay_in_ms(self) -> typing.Optional[jsii.Number]:
        ...

    @delay_in_ms.setter
    def delay_in_ms(self, value: typing.Optional[jsii.Number]) -> None:
        ...

    @builtins.property
    @jsii.member(jsii_name="handleAntiCSRFTokens")
    def handle_anti_csrf_tokens(self) -> typing.Optional[builtins.bool]:
        ...

    @handle_anti_csrf_tokens.setter
    def handle_anti_csrf_tokens(self, value: typing.Optional[builtins.bool]) -> None:
        ...

    @builtins.property
    @jsii.member(jsii_name="injectPluginIdInHeader")
    def inject_plugin_id_in_header(self) -> typing.Optional[builtins.bool]:
        ...

    @inject_plugin_id_in_header.setter
    def inject_plugin_id_in_header(self, value: typing.Optional[builtins.bool]) -> None:
        ...

    @builtins.property
    @jsii.member(jsii_name="maxAlertsPerRule")
    def max_alerts_per_rule(self) -> typing.Optional[jsii.Number]:
        ...

    @max_alerts_per_rule.setter
    def max_alerts_per_rule(self, value: typing.Optional[jsii.Number]) -> None:
        ...

    @builtins.property
    @jsii.member(jsii_name="maxRuleDurationInMins")
    def max_rule_duration_in_mins(self) -> typing.Optional[jsii.Number]:
        ...

    @max_rule_duration_in_mins.setter
    def max_rule_duration_in_mins(self, value: typing.Optional[jsii.Number]) -> None:
        ...

    @builtins.property
    @jsii.member(jsii_name="maxScanDurationInMins")
    def max_scan_duration_in_mins(self) -> typing.Optional[jsii.Number]:
        ...

    @max_scan_duration_in_mins.setter
    def max_scan_duration_in_mins(self, value: typing.Optional[jsii.Number]) -> None:
        ...

    @builtins.property
    @jsii.member(jsii_name="policy")
    def policy(self) -> typing.Optional[builtins.str]:
        ...

    @policy.setter
    def policy(self, value: typing.Optional[builtins.str]) -> None:
        ...

    @builtins.property
    @jsii.member(jsii_name="scanHeadersAllRequests")
    def scan_headers_all_requests(self) -> typing.Optional[builtins.bool]:
        ...

    @scan_headers_all_requests.setter
    def scan_headers_all_requests(self, value: typing.Optional[builtins.bool]) -> None:
        ...

    @builtins.property
    @jsii.member(jsii_name="tests")
    def tests(
        self,
    ) -> typing.Optional[typing.List[typing.Union["IAlertTest", "IMonitorTest", "IStatisticsTest", "IUrlTest"]]]:
        ...

    @tests.setter
    def tests(
        self,
        value: typing.Optional[typing.List[typing.Union["IAlertTest", "IMonitorTest", "IStatisticsTest", "IUrlTest"]]],
    ) -> None:
        ...

    @builtins.property
    @jsii.member(jsii_name="threadPerHost")
    def thread_per_host(self) -> typing.Optional[jsii.Number]:
        ...

    @thread_per_host.setter
    def thread_per_host(self, value: typing.Optional[jsii.Number]) -> None:
        ...

    @builtins.property
    @jsii.member(jsii_name="url")
    def url(self) -> typing.Optional[builtins.str]:
        ...

    @url.setter
    def url(self, value: typing.Optional[builtins.str]) -> None:
        ...

    @builtins.property
    @jsii.member(jsii_name="user")
    def user(self) -> typing.Optional[builtins.str]:
        ...

    @user.setter
    def user(self, value: typing.Optional[builtins.str]) -> None:
        ...


class _IActiveScanParametersProxy:
    '''
    :interface:

    IActiveScanParameters
    Represents the parameters for an active scan.
    :property: {ITest[]} [tests] - List of tests to perform.
    '''

    __jsii_type__: typing.ClassVar[str] = "zap-cdk.IActiveScanParameters"

    @builtins.property
    @jsii.member(jsii_name="addQueryParam")
    def add_query_param(self) -> typing.Optional[builtins.bool]:
        return typing.cast(typing.Optional[builtins.bool], jsii.get(self, "addQueryParam"))

    @add_query_param.setter
    def add_query_param(self, value: typing.Optional[builtins.bool]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d5957dc8a6ee13abaa8bb8e7312a4335c1f1e8fe37abfb4cc67bf1067e8680f4)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "addQueryParam", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="context")
    def context(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "context"))

    @context.setter
    def context(self, value: typing.Optional[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3a5be83aa8204f38dd29d36f0b646b42dcba6cf2020bcefb469da55b9f46d731)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "context", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="defaultPolicy")
    def default_policy(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "defaultPolicy"))

    @default_policy.setter
    def default_policy(self, value: typing.Optional[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8cc7ab0e0f7c1c36fb0a6de441dd09d8ebe74d105879654f40c4bb6fd277b821)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "defaultPolicy", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="delayInMs")
    def delay_in_ms(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "delayInMs"))

    @delay_in_ms.setter
    def delay_in_ms(self, value: typing.Optional[jsii.Number]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__df1e2bb7ca9cf381aece04cd960257c5a4dd76a2e98f2a82b24c1ace3f636994)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "delayInMs", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="handleAntiCSRFTokens")
    def handle_anti_csrf_tokens(self) -> typing.Optional[builtins.bool]:
        return typing.cast(typing.Optional[builtins.bool], jsii.get(self, "handleAntiCSRFTokens"))

    @handle_anti_csrf_tokens.setter
    def handle_anti_csrf_tokens(self, value: typing.Optional[builtins.bool]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8f061745aee1f7f160ed3e581047d3911ede6d299fccb7cda6c5d18d3e336b4a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "handleAntiCSRFTokens", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="injectPluginIdInHeader")
    def inject_plugin_id_in_header(self) -> typing.Optional[builtins.bool]:
        return typing.cast(typing.Optional[builtins.bool], jsii.get(self, "injectPluginIdInHeader"))

    @inject_plugin_id_in_header.setter
    def inject_plugin_id_in_header(self, value: typing.Optional[builtins.bool]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__efb7b527af79e9fe79fc49a68ce70d2b33deba4b1667e65b63b034ca93cbfc9b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "injectPluginIdInHeader", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="maxAlertsPerRule")
    def max_alerts_per_rule(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "maxAlertsPerRule"))

    @max_alerts_per_rule.setter
    def max_alerts_per_rule(self, value: typing.Optional[jsii.Number]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e2ed4d2485991c4a048c2c506044cc3b0ff9ed523956f0915776d2067e3169b9)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "maxAlertsPerRule", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="maxRuleDurationInMins")
    def max_rule_duration_in_mins(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "maxRuleDurationInMins"))

    @max_rule_duration_in_mins.setter
    def max_rule_duration_in_mins(self, value: typing.Optional[jsii.Number]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f7a1dc16dcc47c4a382488abdad3c855b0590e7484bb77cdc067e75641cd9121)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "maxRuleDurationInMins", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="maxScanDurationInMins")
    def max_scan_duration_in_mins(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "maxScanDurationInMins"))

    @max_scan_duration_in_mins.setter
    def max_scan_duration_in_mins(self, value: typing.Optional[jsii.Number]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e5f746695cea7a5525e31418a9f93f006743940b758bf0ed8c0f22b10ca8a583)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "maxScanDurationInMins", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="policy")
    def policy(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "policy"))

    @policy.setter
    def policy(self, value: typing.Optional[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__361b9e2ffd4d58ea3a0fe64582fdcbb8a49dc85c7ac694da65a06a359fa80bda)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "policy", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="scanHeadersAllRequests")
    def scan_headers_all_requests(self) -> typing.Optional[builtins.bool]:
        return typing.cast(typing.Optional[builtins.bool], jsii.get(self, "scanHeadersAllRequests"))

    @scan_headers_all_requests.setter
    def scan_headers_all_requests(self, value: typing.Optional[builtins.bool]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e702469e60539272a298dfda765cd11468106f13366bb350ceb4244c0c862986)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "scanHeadersAllRequests", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="tests")
    def tests(
        self,
    ) -> typing.Optional[typing.List[typing.Union["IAlertTest", "IMonitorTest", "IStatisticsTest", "IUrlTest"]]]:
        return typing.cast(typing.Optional[typing.List[typing.Union["IAlertTest", "IMonitorTest", "IStatisticsTest", "IUrlTest"]]], jsii.get(self, "tests"))

    @tests.setter
    def tests(
        self,
        value: typing.Optional[typing.List[typing.Union["IAlertTest", "IMonitorTest", "IStatisticsTest", "IUrlTest"]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c381784af7dd1e01585590e0becf64587c41f50c50d790865fbffeedaa4051cd)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "tests", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="threadPerHost")
    def thread_per_host(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "threadPerHost"))

    @thread_per_host.setter
    def thread_per_host(self, value: typing.Optional[jsii.Number]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4d3ac6644ee72cee5277961d3955892e069079b2af8acb0182cfe159d6544343)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "threadPerHost", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="url")
    def url(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "url"))

    @url.setter
    def url(self, value: typing.Optional[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6e70a801b6228ab68251897527d6ed306e3714168487f35f12f01efe37ebb8f9)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "url", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="user")
    def user(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "user"))

    @user.setter
    def user(self, value: typing.Optional[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4d9eb57731587721cb207ffcd878c4acbc05ebe2aa3dc5db83b99eaca1ea0559)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "user", value) # pyright: ignore[reportArgumentType]

# Adding a "__jsii_proxy_class__(): typing.Type" function to the interface
typing.cast(typing.Any, IActiveScanParameters).__jsii_proxy_class__ = lambda : _IActiveScanParametersProxy


@jsii.interface(jsii_type="zap-cdk.IActiveScanPolicy")
class IActiveScanPolicy(typing_extensions.Protocol):
    '''
    :interface:

    IActiveScanPolicy
    Represents an active scan policy configuration.
    :property: {boolean} [alwaysRun] - If set and the job is enabled then it will run even if the plan exits early, default: false.
    '''

    @builtins.property
    @jsii.member(jsii_name="parameters")
    def parameters(self) -> "IActiveScanPolicyParameters":
        ...

    @parameters.setter
    def parameters(self, value: "IActiveScanPolicyParameters") -> None:
        ...

    @builtins.property
    @jsii.member(jsii_name="type")
    def type(self) -> builtins.str:
        ...

    @type.setter
    def type(self, value: builtins.str) -> None:
        ...

    @builtins.property
    @jsii.member(jsii_name="alwaysRun")
    def always_run(self) -> typing.Optional[builtins.bool]:
        ...

    @always_run.setter
    def always_run(self, value: typing.Optional[builtins.bool]) -> None:
        ...

    @builtins.property
    @jsii.member(jsii_name="enabled")
    def enabled(self) -> typing.Optional[builtins.bool]:
        ...

    @enabled.setter
    def enabled(self, value: typing.Optional[builtins.bool]) -> None:
        ...


class _IActiveScanPolicyProxy:
    '''
    :interface:

    IActiveScanPolicy
    Represents an active scan policy configuration.
    :property: {boolean} [alwaysRun] - If set and the job is enabled then it will run even if the plan exits early, default: false.
    '''

    __jsii_type__: typing.ClassVar[str] = "zap-cdk.IActiveScanPolicy"

    @builtins.property
    @jsii.member(jsii_name="parameters")
    def parameters(self) -> "IActiveScanPolicyParameters":
        return typing.cast("IActiveScanPolicyParameters", jsii.get(self, "parameters"))

    @parameters.setter
    def parameters(self, value: "IActiveScanPolicyParameters") -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__acb2689e505797bb0987411298a02b53a5f2d8e6174de52cedba46d9cb6b103c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "parameters", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="type")
    def type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "type"))

    @type.setter
    def type(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a9d8df74f220ea0bca1ed7c224dee9df10ba2b9936ebc20af0def4a18f29a2a0)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "type", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="alwaysRun")
    def always_run(self) -> typing.Optional[builtins.bool]:
        return typing.cast(typing.Optional[builtins.bool], jsii.get(self, "alwaysRun"))

    @always_run.setter
    def always_run(self, value: typing.Optional[builtins.bool]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__350074fcacc17f040555e59f88c2452863bf4e16a681e5aa06cdcae12b762c89)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "alwaysRun", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="enabled")
    def enabled(self) -> typing.Optional[builtins.bool]:
        return typing.cast(typing.Optional[builtins.bool], jsii.get(self, "enabled"))

    @enabled.setter
    def enabled(self, value: typing.Optional[builtins.bool]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2834b449438f57536dca74690060eb075e627dcb29bc59c202ece887cbd4898e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "enabled", value) # pyright: ignore[reportArgumentType]

# Adding a "__jsii_proxy_class__(): typing.Type" function to the interface
typing.cast(typing.Any, IActiveScanPolicy).__jsii_proxy_class__ = lambda : _IActiveScanPolicyProxy


@jsii.interface(jsii_type="zap-cdk.IActiveScanPolicyDefinition")
class IActiveScanPolicyDefinition(typing_extensions.Protocol):
    '''
    :interface:

    IActiveScanPolicyDefinition
    Represents the policy definition for an active scan.
    :property: {Date} updatedAt - Last updated date of the policy.
    '''

    @builtins.property
    @jsii.member(jsii_name="createdAt")
    def created_at(self) -> datetime.datetime:
        ...

    @created_at.setter
    def created_at(self, value: datetime.datetime) -> None:
        ...

    @builtins.property
    @jsii.member(jsii_name="id")
    def id(self) -> jsii.Number:
        ...

    @id.setter
    def id(self, value: jsii.Number) -> None:
        ...

    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        ...

    @name.setter
    def name(self, value: builtins.str) -> None:
        ...

    @builtins.property
    @jsii.member(jsii_name="updatedAt")
    def updated_at(self) -> datetime.datetime:
        ...

    @updated_at.setter
    def updated_at(self, value: datetime.datetime) -> None:
        ...

    @builtins.property
    @jsii.member(jsii_name="description")
    def description(self) -> typing.Optional[builtins.str]:
        ...

    @description.setter
    def description(self, value: typing.Optional[builtins.str]) -> None:
        ...


class _IActiveScanPolicyDefinitionProxy:
    '''
    :interface:

    IActiveScanPolicyDefinition
    Represents the policy definition for an active scan.
    :property: {Date} updatedAt - Last updated date of the policy.
    '''

    __jsii_type__: typing.ClassVar[str] = "zap-cdk.IActiveScanPolicyDefinition"

    @builtins.property
    @jsii.member(jsii_name="createdAt")
    def created_at(self) -> datetime.datetime:
        return typing.cast(datetime.datetime, jsii.get(self, "createdAt"))

    @created_at.setter
    def created_at(self, value: datetime.datetime) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6f5b32b83e568f5fc4d6a4fae3b130eff8c106c93b8aaa70c48020abdb9ce963)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "createdAt", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="id")
    def id(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "id"))

    @id.setter
    def id(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3656005fb67617eed1dd0da51dafffcbd3a02cc01adcd26adb7d4dc1988c9a86)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "id", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b9b23cbe8cb5907509dd26c54383b2c71e043fe9fbe3d9b5bf7826a8a63d7c46)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "name", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="updatedAt")
    def updated_at(self) -> datetime.datetime:
        return typing.cast(datetime.datetime, jsii.get(self, "updatedAt"))

    @updated_at.setter
    def updated_at(self, value: datetime.datetime) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a7d22b2124d452c178e5f9c64b7e61f3360ae6a337ecdb70ac714a0c16d7439a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "updatedAt", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="description")
    def description(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "description"))

    @description.setter
    def description(self, value: typing.Optional[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f04d683a1b58ee7079e22fde8a080605cdb636e2a827bc5cb0e4c9b23ff1f5c1)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "description", value) # pyright: ignore[reportArgumentType]

# Adding a "__jsii_proxy_class__(): typing.Type" function to the interface
typing.cast(typing.Any, IActiveScanPolicyDefinition).__jsii_proxy_class__ = lambda : _IActiveScanPolicyDefinitionProxy


@jsii.interface(jsii_type="zap-cdk.IActiveScanPolicyParameters")
class IActiveScanPolicyParameters(typing_extensions.Protocol):
    '''
    :interface:

    IActiveScanPolicyParameters
    Represents the parameters for an active scan policy.
    :property: {IRule[]} [policyDefinition.rules] - A list of one or more active scan rules.
    '''

    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        ...

    @name.setter
    def name(self, value: builtins.str) -> None:
        ...

    @builtins.property
    @jsii.member(jsii_name="policyDefinition")
    def policy_definition(self) -> IActiveScanPolicyDefinition:
        ...

    @policy_definition.setter
    def policy_definition(self, value: IActiveScanPolicyDefinition) -> None:
        ...


class _IActiveScanPolicyParametersProxy:
    '''
    :interface:

    IActiveScanPolicyParameters
    Represents the parameters for an active scan policy.
    :property: {IRule[]} [policyDefinition.rules] - A list of one or more active scan rules.
    '''

    __jsii_type__: typing.ClassVar[str] = "zap-cdk.IActiveScanPolicyParameters"

    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__87eb15d37dfd45eba4718637f8a1a84ba628cb6b8b6771562e3ac9443dca6532)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "name", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="policyDefinition")
    def policy_definition(self) -> IActiveScanPolicyDefinition:
        return typing.cast(IActiveScanPolicyDefinition, jsii.get(self, "policyDefinition"))

    @policy_definition.setter
    def policy_definition(self, value: IActiveScanPolicyDefinition) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9fdb05ebf98873ec8af1710f5fae352824b7644ca727add404aca11a9714e80e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "policyDefinition", value) # pyright: ignore[reportArgumentType]

# Adding a "__jsii_proxy_class__(): typing.Type" function to the interface
typing.cast(typing.Any, IActiveScanPolicyParameters).__jsii_proxy_class__ = lambda : _IActiveScanPolicyParametersProxy


@jsii.interface(jsii_type="zap-cdk.IActiveScanPolicyProps")
class IActiveScanPolicyProps(typing_extensions.Protocol):
    '''Properties for the ActiveScanPolicyConfig construct.

    :interface: IActiveScanPolicyProps
    :property: {IActiveScanPolicy} activeScanPolicy - The active scan policy configuration.
    '''

    @builtins.property
    @jsii.member(jsii_name="activeScanPolicy")
    def active_scan_policy(self) -> IActiveScanPolicy:
        ...

    @active_scan_policy.setter
    def active_scan_policy(self, value: IActiveScanPolicy) -> None:
        ...


class _IActiveScanPolicyPropsProxy:
    '''Properties for the ActiveScanPolicyConfig construct.

    :interface: IActiveScanPolicyProps
    :property: {IActiveScanPolicy} activeScanPolicy - The active scan policy configuration.
    '''

    __jsii_type__: typing.ClassVar[str] = "zap-cdk.IActiveScanPolicyProps"

    @builtins.property
    @jsii.member(jsii_name="activeScanPolicy")
    def active_scan_policy(self) -> IActiveScanPolicy:
        return typing.cast(IActiveScanPolicy, jsii.get(self, "activeScanPolicy"))

    @active_scan_policy.setter
    def active_scan_policy(self, value: IActiveScanPolicy) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__afa0c2f038935b5bc77460447c8c8b7fdce253ce059aabf23c25ba00a7d745bc)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "activeScanPolicy", value) # pyright: ignore[reportArgumentType]

# Adding a "__jsii_proxy_class__(): typing.Type" function to the interface
typing.cast(typing.Any, IActiveScanPolicyProps).__jsii_proxy_class__ = lambda : _IActiveScanPolicyPropsProxy


@jsii.interface(jsii_type="zap-cdk.IAjaxTest")
class IAjaxTest(typing_extensions.Protocol):
    '''Interface representing a test configuration.

    :interface: IAjaxTest
    :property: {'warn' | 'error' | 'info'} [onFail] - Action to take on failure.
    '''

    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        ...

    @name.setter
    def name(self, value: builtins.str) -> None:
        ...

    @builtins.property
    @jsii.member(jsii_name="operator")
    def operator(self) -> builtins.str:
        ...

    @operator.setter
    def operator(self, value: builtins.str) -> None:
        ...

    @builtins.property
    @jsii.member(jsii_name="statistic")
    def statistic(self) -> builtins.str:
        ...

    @statistic.setter
    def statistic(self, value: builtins.str) -> None:
        ...

    @builtins.property
    @jsii.member(jsii_name="type")
    def type(self) -> builtins.str:
        ...

    @type.setter
    def type(self, value: builtins.str) -> None:
        ...

    @builtins.property
    @jsii.member(jsii_name="value")
    def value(self) -> jsii.Number:
        ...

    @value.setter
    def value(self, value: jsii.Number) -> None:
        ...

    @builtins.property
    @jsii.member(jsii_name="onFail")
    def on_fail(self) -> typing.Optional[builtins.str]:
        ...

    @on_fail.setter
    def on_fail(self, value: typing.Optional[builtins.str]) -> None:
        ...


class _IAjaxTestProxy:
    '''Interface representing a test configuration.

    :interface: IAjaxTest
    :property: {'warn' | 'error' | 'info'} [onFail] - Action to take on failure.
    '''

    __jsii_type__: typing.ClassVar[str] = "zap-cdk.IAjaxTest"

    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__21e8629528cdf90796e876d40bee85e20fec3c919a6c670d8bd0f3d94c91bb09)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "name", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="operator")
    def operator(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "operator"))

    @operator.setter
    def operator(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b93b53ea2a163c2d9bba32f7e444f1cdd4f19d7708ae698560f91d3c7ca36424)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "operator", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="statistic")
    def statistic(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "statistic"))

    @statistic.setter
    def statistic(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__df494d7a5b94fdff24cfeb5a852e49e59a262f318727f6061aa1c651d963a39e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "statistic", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="type")
    def type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "type"))

    @type.setter
    def type(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b3a67814a62470abff2a59ab59399dfba922db543fdfaedb466f07fe067988d7)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "type", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="value")
    def value(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "value"))

    @value.setter
    def value(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__edfd8b81e3c0dd19739e541e37ba53115dc3b31b19c815aa1799f2dcdfe9f790)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "value", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="onFail")
    def on_fail(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "onFail"))

    @on_fail.setter
    def on_fail(self, value: typing.Optional[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2959aebde08b09a9328e8f97aeea7d37f927d3f724bff0a8e12f5e7309710a09)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "onFail", value) # pyright: ignore[reportArgumentType]

# Adding a "__jsii_proxy_class__(): typing.Type" function to the interface
typing.cast(typing.Any, IAjaxTest).__jsii_proxy_class__ = lambda : _IAjaxTestProxy


@jsii.interface(jsii_type="zap-cdk.IAlertFilter")
class IAlertFilter(typing_extensions.Protocol):
    '''
    :interface:

    IAlertFilter
    Represents a filter for alerts in the scanning process.
    :property: {boolean} [evidenceRegex] - Optional; if true, then the evidence is treated as a regex.
    '''

    @builtins.property
    @jsii.member(jsii_name="newRisk")
    def new_risk(self) -> builtins.str:
        ...

    @new_risk.setter
    def new_risk(self, value: builtins.str) -> None:
        ...

    @builtins.property
    @jsii.member(jsii_name="ruleId")
    def rule_id(self) -> jsii.Number:
        ...

    @rule_id.setter
    def rule_id(self, value: jsii.Number) -> None:
        ...

    @builtins.property
    @jsii.member(jsii_name="attack")
    def attack(self) -> typing.Optional[builtins.str]:
        ...

    @attack.setter
    def attack(self, value: typing.Optional[builtins.str]) -> None:
        ...

    @builtins.property
    @jsii.member(jsii_name="attackRegex")
    def attack_regex(self) -> typing.Optional[builtins.bool]:
        ...

    @attack_regex.setter
    def attack_regex(self, value: typing.Optional[builtins.bool]) -> None:
        ...

    @builtins.property
    @jsii.member(jsii_name="context")
    def context(self) -> typing.Optional[builtins.str]:
        ...

    @context.setter
    def context(self, value: typing.Optional[builtins.str]) -> None:
        ...

    @builtins.property
    @jsii.member(jsii_name="evidence")
    def evidence(self) -> typing.Optional[builtins.str]:
        ...

    @evidence.setter
    def evidence(self, value: typing.Optional[builtins.str]) -> None:
        ...

    @builtins.property
    @jsii.member(jsii_name="evidenceRegex")
    def evidence_regex(self) -> typing.Optional[builtins.bool]:
        ...

    @evidence_regex.setter
    def evidence_regex(self, value: typing.Optional[builtins.bool]) -> None:
        ...

    @builtins.property
    @jsii.member(jsii_name="parameter")
    def parameter(self) -> typing.Optional[builtins.str]:
        ...

    @parameter.setter
    def parameter(self, value: typing.Optional[builtins.str]) -> None:
        ...

    @builtins.property
    @jsii.member(jsii_name="parameterRegex")
    def parameter_regex(self) -> typing.Optional[builtins.bool]:
        ...

    @parameter_regex.setter
    def parameter_regex(self, value: typing.Optional[builtins.bool]) -> None:
        ...

    @builtins.property
    @jsii.member(jsii_name="url")
    def url(self) -> typing.Optional[builtins.str]:
        ...

    @url.setter
    def url(self, value: typing.Optional[builtins.str]) -> None:
        ...

    @builtins.property
    @jsii.member(jsii_name="urlRegex")
    def url_regex(self) -> typing.Optional[builtins.bool]:
        ...

    @url_regex.setter
    def url_regex(self, value: typing.Optional[builtins.bool]) -> None:
        ...


class _IAlertFilterProxy:
    '''
    :interface:

    IAlertFilter
    Represents a filter for alerts in the scanning process.
    :property: {boolean} [evidenceRegex] - Optional; if true, then the evidence is treated as a regex.
    '''

    __jsii_type__: typing.ClassVar[str] = "zap-cdk.IAlertFilter"

    @builtins.property
    @jsii.member(jsii_name="newRisk")
    def new_risk(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "newRisk"))

    @new_risk.setter
    def new_risk(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__def45010adcc6315620a80e6a606a0d8d531ee0d2a268eaf8492ea3f1694124f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "newRisk", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="ruleId")
    def rule_id(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "ruleId"))

    @rule_id.setter
    def rule_id(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__88c98929537b3c33b406e8587b98f8aba9523c81436b62038b44de3ee391c607)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "ruleId", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="attack")
    def attack(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "attack"))

    @attack.setter
    def attack(self, value: typing.Optional[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__384ef7816fe69412f49d2dae6178e59d2156762d8257bf271a25404c9b75b57c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "attack", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="attackRegex")
    def attack_regex(self) -> typing.Optional[builtins.bool]:
        return typing.cast(typing.Optional[builtins.bool], jsii.get(self, "attackRegex"))

    @attack_regex.setter
    def attack_regex(self, value: typing.Optional[builtins.bool]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e46a32350578f67a3b6837c39f1c58235ae8a0570cf3b2b77b54c3bb14484ec9)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "attackRegex", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="context")
    def context(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "context"))

    @context.setter
    def context(self, value: typing.Optional[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ca377f59f51fa2ee7dc79ef8dbff4f553c5553b5e23c71e1e81ba89b7513fb9f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "context", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="evidence")
    def evidence(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "evidence"))

    @evidence.setter
    def evidence(self, value: typing.Optional[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__42aff3f8eaef5337dbd8e8f8b3787931a7fc9b18d8f61c7822ff72ad304efdb0)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "evidence", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="evidenceRegex")
    def evidence_regex(self) -> typing.Optional[builtins.bool]:
        return typing.cast(typing.Optional[builtins.bool], jsii.get(self, "evidenceRegex"))

    @evidence_regex.setter
    def evidence_regex(self, value: typing.Optional[builtins.bool]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__cb37b5aa6bd4d1ea95eba7c95012c2335aabbb9c7ce3e77796b3d96cccd426ef)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "evidenceRegex", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="parameter")
    def parameter(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "parameter"))

    @parameter.setter
    def parameter(self, value: typing.Optional[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__65124f21bb792970688a081933341bd26df3c6cffc1c00a649268ef8650d7658)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "parameter", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="parameterRegex")
    def parameter_regex(self) -> typing.Optional[builtins.bool]:
        return typing.cast(typing.Optional[builtins.bool], jsii.get(self, "parameterRegex"))

    @parameter_regex.setter
    def parameter_regex(self, value: typing.Optional[builtins.bool]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__504af35abe5a1284f1c1c118444237d03e300b3644f240e0ecc55be99bc3c808)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "parameterRegex", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="url")
    def url(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "url"))

    @url.setter
    def url(self, value: typing.Optional[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3db000522ca6305e8ecf33827473233db2f4cea2d1e226400a596f4b092df3d9)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "url", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="urlRegex")
    def url_regex(self) -> typing.Optional[builtins.bool]:
        return typing.cast(typing.Optional[builtins.bool], jsii.get(self, "urlRegex"))

    @url_regex.setter
    def url_regex(self, value: typing.Optional[builtins.bool]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3734f6fc222c3600dbbba8c09ca87c33a89034c7ad2c1279a1cb37b24a263bd4)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "urlRegex", value) # pyright: ignore[reportArgumentType]

# Adding a "__jsii_proxy_class__(): typing.Type" function to the interface
typing.cast(typing.Any, IAlertFilter).__jsii_proxy_class__ = lambda : _IAlertFilterProxy


@jsii.interface(jsii_type="zap-cdk.IAlertFilterParameters")
class IAlertFilterParameters(typing_extensions.Protocol):
    '''
    :interface:

    IAlertFilterParameters
    Represents the parameters for applying alert filters.
    :property: {IAlertFilter[]} alertFilters - A list of alertFilters to be applied.
    '''

    @builtins.property
    @jsii.member(jsii_name="alertFilters")
    def alert_filters(self) -> typing.List[IAlertFilter]:
        ...

    @alert_filters.setter
    def alert_filters(self, value: typing.List[IAlertFilter]) -> None:
        ...

    @builtins.property
    @jsii.member(jsii_name="deleteGlobalAlerts")
    def delete_global_alerts(self) -> typing.Optional[builtins.bool]:
        ...

    @delete_global_alerts.setter
    def delete_global_alerts(self, value: typing.Optional[builtins.bool]) -> None:
        ...


class _IAlertFilterParametersProxy:
    '''
    :interface:

    IAlertFilterParameters
    Represents the parameters for applying alert filters.
    :property: {IAlertFilter[]} alertFilters - A list of alertFilters to be applied.
    '''

    __jsii_type__: typing.ClassVar[str] = "zap-cdk.IAlertFilterParameters"

    @builtins.property
    @jsii.member(jsii_name="alertFilters")
    def alert_filters(self) -> typing.List[IAlertFilter]:
        return typing.cast(typing.List[IAlertFilter], jsii.get(self, "alertFilters"))

    @alert_filters.setter
    def alert_filters(self, value: typing.List[IAlertFilter]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4be56ee0f993319959d37e3c10efd1f6ea20de159778eed11c19d0bb61df0b47)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "alertFilters", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="deleteGlobalAlerts")
    def delete_global_alerts(self) -> typing.Optional[builtins.bool]:
        return typing.cast(typing.Optional[builtins.bool], jsii.get(self, "deleteGlobalAlerts"))

    @delete_global_alerts.setter
    def delete_global_alerts(self, value: typing.Optional[builtins.bool]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__67ee7d195a6e6fca958c3000d10f0be87c3dd608b5d726adb804446b9d54aa44)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "deleteGlobalAlerts", value) # pyright: ignore[reportArgumentType]

# Adding a "__jsii_proxy_class__(): typing.Type" function to the interface
typing.cast(typing.Any, IAlertFilterParameters).__jsii_proxy_class__ = lambda : _IAlertFilterParametersProxy


@jsii.interface(jsii_type="zap-cdk.IAlertTag")
class IAlertTag(typing_extensions.Protocol):
    '''
    :interface:

    IAlertTag
    Represents the configuration for alert tags.
    :property: {threshold} [threshold] - The Alert Threshold for this set of rules, default: Medium.
    '''

    @builtins.property
    @jsii.member(jsii_name="exclude")
    def exclude(self) -> typing.Optional[typing.List[builtins.str]]:
        ...

    @exclude.setter
    def exclude(self, value: typing.Optional[typing.List[builtins.str]]) -> None:
        ...

    @builtins.property
    @jsii.member(jsii_name="include")
    def include(self) -> typing.Optional[typing.List[builtins.str]]:
        ...

    @include.setter
    def include(self, value: typing.Optional[typing.List[builtins.str]]) -> None:
        ...

    @builtins.property
    @jsii.member(jsii_name="strength")
    def strength(self) -> typing.Optional[builtins.str]:
        ...

    @strength.setter
    def strength(self, value: typing.Optional[builtins.str]) -> None:
        ...

    @builtins.property
    @jsii.member(jsii_name="threshold")
    def threshold(self) -> typing.Optional[builtins.str]:
        ...

    @threshold.setter
    def threshold(self, value: typing.Optional[builtins.str]) -> None:
        ...


class _IAlertTagProxy:
    '''
    :interface:

    IAlertTag
    Represents the configuration for alert tags.
    :property: {threshold} [threshold] - The Alert Threshold for this set of rules, default: Medium.
    '''

    __jsii_type__: typing.ClassVar[str] = "zap-cdk.IAlertTag"

    @builtins.property
    @jsii.member(jsii_name="exclude")
    def exclude(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "exclude"))

    @exclude.setter
    def exclude(self, value: typing.Optional[typing.List[builtins.str]]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__db06983cb9c5dad8d2968994f74f39b5a4f05d9499702740eabc458616612db6)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "exclude", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="include")
    def include(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "include"))

    @include.setter
    def include(self, value: typing.Optional[typing.List[builtins.str]]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8c7ce4753f533815fce74b5bab23a58ab8663b43d3c1c426bb046247f95f3b35)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "include", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="strength")
    def strength(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "strength"))

    @strength.setter
    def strength(self, value: typing.Optional[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__bc26225f919da4776b588e62d9a87762f46307f2ce3c9d8eec690fd9a0ec239d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "strength", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="threshold")
    def threshold(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "threshold"))

    @threshold.setter
    def threshold(self, value: typing.Optional[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d95287e23bddd3dc313a1f08e792d8e035180f13bb4587565fddc905f4536c2c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "threshold", value) # pyright: ignore[reportArgumentType]

# Adding a "__jsii_proxy_class__(): typing.Type" function to the interface
typing.cast(typing.Any, IAlertTag).__jsii_proxy_class__ = lambda : _IAlertTagProxy


@jsii.interface(jsii_type="zap-cdk.IAlertTags")
class IAlertTags(typing_extensions.Protocol):
    '''
    :interface:

    IAlertTags
    Represents the configuration for alert tags.
    :property: {string} [threshold] - The Alert Threshold for this set of rules, one of Off, Low, Medium, High, default: Medium.
    '''

    @builtins.property
    @jsii.member(jsii_name="exclude")
    def exclude(self) -> typing.List[builtins.str]:
        ...

    @exclude.setter
    def exclude(self, value: typing.List[builtins.str]) -> None:
        ...

    @builtins.property
    @jsii.member(jsii_name="include")
    def include(self) -> typing.List[builtins.str]:
        ...

    @include.setter
    def include(self, value: typing.List[builtins.str]) -> None:
        ...

    @builtins.property
    @jsii.member(jsii_name="strength")
    def strength(self) -> typing.Optional[builtins.str]:
        ...

    @strength.setter
    def strength(self, value: typing.Optional[builtins.str]) -> None:
        ...

    @builtins.property
    @jsii.member(jsii_name="threshold")
    def threshold(self) -> typing.Optional[builtins.str]:
        ...

    @threshold.setter
    def threshold(self, value: typing.Optional[builtins.str]) -> None:
        ...


class _IAlertTagsProxy:
    '''
    :interface:

    IAlertTags
    Represents the configuration for alert tags.
    :property: {string} [threshold] - The Alert Threshold for this set of rules, one of Off, Low, Medium, High, default: Medium.
    '''

    __jsii_type__: typing.ClassVar[str] = "zap-cdk.IAlertTags"

    @builtins.property
    @jsii.member(jsii_name="exclude")
    def exclude(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "exclude"))

    @exclude.setter
    def exclude(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__80c9234b343377f12bc267046f6bbc0952d1adb141106d80ef53f8c365dab31f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "exclude", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="include")
    def include(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "include"))

    @include.setter
    def include(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__84b456293ad17dfc92426a47742d54b6633fe0dd205e08a5c2862cb307a389c6)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "include", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="strength")
    def strength(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "strength"))

    @strength.setter
    def strength(self, value: typing.Optional[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2e37aa8e1ac031be95b04b3c5f72cde5bfe3e24ae371b689a5eb70c3cd1a5fdb)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "strength", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="threshold")
    def threshold(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "threshold"))

    @threshold.setter
    def threshold(self, value: typing.Optional[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3f2f364553b125537df77964e0dde93db347dbcdb663cce61bbd17552ad0119b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "threshold", value) # pyright: ignore[reportArgumentType]

# Adding a "__jsii_proxy_class__(): typing.Type" function to the interface
typing.cast(typing.Any, IAlertTags).__jsii_proxy_class__ = lambda : _IAlertTagsProxy


@jsii.interface(jsii_type="zap-cdk.IAlertTest")
class IAlertTest(typing_extensions.Protocol):
    '''Interface for alert tests.

    Example YAML representation::

       - name: 'test one'                       # Name of the test, optional
         type: alert                            # Specifies that the test is of type 'alert'
         action: passIfPresent                  # String: The condition (presence/absence) of the alert, default: passIfAbsent
         scanRuleId: 123                        # Integer: The id of the scanRule which generates the alert, mandatory
         alertName: 'SQL Injection'              # String: The name of the alert generated, optional
         url: http://www.example.com/path       # String: The url of the request corresponding to the alert generated, optional
         method: GET                            # String: The method of the request corresponding to the alert generated, optional
         attack: 'SQL Injection Attack'         # String: The actual attack which generated the alert, optional
         param: 'username'                      # String: The parameter which was modified to generate the alert, optional
         evidence: 'Evidence of SQL injection'  # String: The evidence corresponding to the alert generated, optional
         confidence: High                       # String: The confidence of the alert, one of 'False Positive', 'Low', 'Medium', 'High', 'Confirmed', optional
         risk: High                             # String: The risk of the alert, one of 'Informational', 'Low', 'Medium', 'High', optional
         otherInfo: 'Additional context here'   # String: Additional information corresponding to the alert, optional
         onFail: 'info'                        # String: One of 'warn', 'error', 'info', mandatory

    :interface: IAlertTest
    :property: {OnFailType} onFail - Action to take on failure, mandatory.
    '''

    @builtins.property
    @jsii.member(jsii_name="onFail")
    def on_fail(self) -> builtins.str:
        ...

    @on_fail.setter
    def on_fail(self, value: builtins.str) -> None:
        ...

    @builtins.property
    @jsii.member(jsii_name="scanRuleId")
    def scan_rule_id(self) -> jsii.Number:
        ...

    @scan_rule_id.setter
    def scan_rule_id(self, value: jsii.Number) -> None:
        ...

    @builtins.property
    @jsii.member(jsii_name="type")
    def type(self) -> builtins.str:
        ...

    @type.setter
    def type(self, value: builtins.str) -> None:
        ...

    @builtins.property
    @jsii.member(jsii_name="action")
    def action(self) -> typing.Optional[builtins.str]:
        ...

    @action.setter
    def action(self, value: typing.Optional[builtins.str]) -> None:
        ...

    @builtins.property
    @jsii.member(jsii_name="alertName")
    def alert_name(self) -> typing.Optional[builtins.str]:
        ...

    @alert_name.setter
    def alert_name(self, value: typing.Optional[builtins.str]) -> None:
        ...

    @builtins.property
    @jsii.member(jsii_name="attack")
    def attack(self) -> typing.Optional[builtins.str]:
        ...

    @attack.setter
    def attack(self, value: typing.Optional[builtins.str]) -> None:
        ...

    @builtins.property
    @jsii.member(jsii_name="confidence")
    def confidence(self) -> typing.Optional[builtins.str]:
        ...

    @confidence.setter
    def confidence(self, value: typing.Optional[builtins.str]) -> None:
        ...

    @builtins.property
    @jsii.member(jsii_name="evidence")
    def evidence(self) -> typing.Optional[builtins.str]:
        ...

    @evidence.setter
    def evidence(self, value: typing.Optional[builtins.str]) -> None:
        ...

    @builtins.property
    @jsii.member(jsii_name="method")
    def method(self) -> typing.Optional[builtins.str]:
        ...

    @method.setter
    def method(self, value: typing.Optional[builtins.str]) -> None:
        ...

    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> typing.Optional[builtins.str]:
        ...

    @name.setter
    def name(self, value: typing.Optional[builtins.str]) -> None:
        ...

    @builtins.property
    @jsii.member(jsii_name="param")
    def param(self) -> typing.Optional[builtins.str]:
        ...

    @param.setter
    def param(self, value: typing.Optional[builtins.str]) -> None:
        ...

    @builtins.property
    @jsii.member(jsii_name="risk")
    def risk(self) -> typing.Optional[builtins.str]:
        ...

    @risk.setter
    def risk(self, value: typing.Optional[builtins.str]) -> None:
        ...

    @builtins.property
    @jsii.member(jsii_name="url")
    def url(self) -> typing.Optional[builtins.str]:
        ...

    @url.setter
    def url(self, value: typing.Optional[builtins.str]) -> None:
        ...


class _IAlertTestProxy:
    '''Interface for alert tests.

    Example YAML representation::

       - name: 'test one'                       # Name of the test, optional
         type: alert                            # Specifies that the test is of type 'alert'
         action: passIfPresent                  # String: The condition (presence/absence) of the alert, default: passIfAbsent
         scanRuleId: 123                        # Integer: The id of the scanRule which generates the alert, mandatory
         alertName: 'SQL Injection'              # String: The name of the alert generated, optional
         url: http://www.example.com/path       # String: The url of the request corresponding to the alert generated, optional
         method: GET                            # String: The method of the request corresponding to the alert generated, optional
         attack: 'SQL Injection Attack'         # String: The actual attack which generated the alert, optional
         param: 'username'                      # String: The parameter which was modified to generate the alert, optional
         evidence: 'Evidence of SQL injection'  # String: The evidence corresponding to the alert generated, optional
         confidence: High                       # String: The confidence of the alert, one of 'False Positive', 'Low', 'Medium', 'High', 'Confirmed', optional
         risk: High                             # String: The risk of the alert, one of 'Informational', 'Low', 'Medium', 'High', optional
         otherInfo: 'Additional context here'   # String: Additional information corresponding to the alert, optional
         onFail: 'info'                        # String: One of 'warn', 'error', 'info', mandatory

    :interface: IAlertTest
    :property: {OnFailType} onFail - Action to take on failure, mandatory.
    '''

    __jsii_type__: typing.ClassVar[str] = "zap-cdk.IAlertTest"

    @builtins.property
    @jsii.member(jsii_name="onFail")
    def on_fail(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "onFail"))

    @on_fail.setter
    def on_fail(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8f25f07770658386c8a3138ca975338d2afeaa80a3fba964aaf12c194c7fe9a9)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "onFail", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="scanRuleId")
    def scan_rule_id(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "scanRuleId"))

    @scan_rule_id.setter
    def scan_rule_id(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__eeb27c9a7758e3d006a6caa0569a57afc3ee847a97492db256a23fe498ee7115)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "scanRuleId", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="type")
    def type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "type"))

    @type.setter
    def type(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__aad51ee87979c9e57cfa38ad3d6567d4e7c23f081707c63134dfff85687e0041)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "type", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="action")
    def action(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "action"))

    @action.setter
    def action(self, value: typing.Optional[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d88e59a759583f259c9ca330f9e64e4456e73cdbecf493e4c0574672918631f9)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "action", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="alertName")
    def alert_name(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "alertName"))

    @alert_name.setter
    def alert_name(self, value: typing.Optional[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4d27bcdb326f07cadb24a2c57f7df108cba630d4c0202ac3d6a07669885cf57f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "alertName", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="attack")
    def attack(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "attack"))

    @attack.setter
    def attack(self, value: typing.Optional[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__90a2d5cd71e1ff75e969133be060630620b624114627de01dd5bbc27acf9c9cf)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "attack", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="confidence")
    def confidence(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "confidence"))

    @confidence.setter
    def confidence(self, value: typing.Optional[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__600f781777fc184ad1e334194eb5d72d1fc35ed8e4454bc9e34ff3d8f65c090d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "confidence", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="evidence")
    def evidence(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "evidence"))

    @evidence.setter
    def evidence(self, value: typing.Optional[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d23499f7ce966fe187be72e71d5d86ed5fc16465510d71c0964f343f692bdd1f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "evidence", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="method")
    def method(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "method"))

    @method.setter
    def method(self, value: typing.Optional[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__144b6545ace08dc2f9df1ef3db95981430c84f4b2b122ad170c330d600c85350)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "method", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "name"))

    @name.setter
    def name(self, value: typing.Optional[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d66a501872d2ce82650d382b2a51b60b25d4ac118d9fe816844f85ca7cbf1ad5)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "name", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="param")
    def param(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "param"))

    @param.setter
    def param(self, value: typing.Optional[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__96e34f45ba1a59f943edab0c886c35574ad5bc0ad02c03c4789f31651c912f6d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "param", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="risk")
    def risk(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "risk"))

    @risk.setter
    def risk(self, value: typing.Optional[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6f195e39e3a6944b9c420e9fdfaeebaa54ac1d75418972acff67f64ef2c1ecef)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "risk", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="url")
    def url(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "url"))

    @url.setter
    def url(self, value: typing.Optional[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__fd72b42aa985c2fce6982fcc142c94b515f0ac7b1a8768bb78640288dabaf5d2)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "url", value) # pyright: ignore[reportArgumentType]

# Adding a "__jsii_proxy_class__(): typing.Type" function to the interface
typing.cast(typing.Any, IAlertTest).__jsii_proxy_class__ = lambda : _IAlertTestProxy


@jsii.interface(jsii_type="zap-cdk.IAuthenticationParameters")
class IAuthenticationParameters(typing_extensions.Protocol):
    '''
    :interface:

    IAuthenticationParameters
    Represents the parameters for authentication in the scanning process.
    :property: {string} verification.pollAdditionalHeaders[].value - The header value.
    '''

    @builtins.property
    @jsii.member(jsii_name="method")
    def method(self) -> builtins.str:
        ...

    @method.setter
    def method(self, value: builtins.str) -> None:
        ...

    @builtins.property
    @jsii.member(jsii_name="parameters")
    def parameters(self) -> "IAuthenticationParametersParameters":
        ...

    @parameters.setter
    def parameters(self, value: "IAuthenticationParametersParameters") -> None:
        ...

    @builtins.property
    @jsii.member(jsii_name="verification")
    def verification(self) -> "IAuthenticationParametersVerification":
        ...

    @verification.setter
    def verification(self, value: "IAuthenticationParametersVerification") -> None:
        ...


class _IAuthenticationParametersProxy:
    '''
    :interface:

    IAuthenticationParameters
    Represents the parameters for authentication in the scanning process.
    :property: {string} verification.pollAdditionalHeaders[].value - The header value.
    '''

    __jsii_type__: typing.ClassVar[str] = "zap-cdk.IAuthenticationParameters"

    @builtins.property
    @jsii.member(jsii_name="method")
    def method(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "method"))

    @method.setter
    def method(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__52ca62c23f711572246801957a50a2a2260cf999465c91ccf8f7018aa515b05a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "method", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="parameters")
    def parameters(self) -> "IAuthenticationParametersParameters":
        return typing.cast("IAuthenticationParametersParameters", jsii.get(self, "parameters"))

    @parameters.setter
    def parameters(self, value: "IAuthenticationParametersParameters") -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5f83e38f0a7ca5c3fc135063d93dccc27958dbe244363b93ee727ab611ca99b7)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "parameters", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="verification")
    def verification(self) -> "IAuthenticationParametersVerification":
        return typing.cast("IAuthenticationParametersVerification", jsii.get(self, "verification"))

    @verification.setter
    def verification(self, value: "IAuthenticationParametersVerification") -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b09f53eb485e80307509d122da05148a6d820bbb25159544884b5f592c2c272e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "verification", value) # pyright: ignore[reportArgumentType]

# Adding a "__jsii_proxy_class__(): typing.Type" function to the interface
typing.cast(typing.Any, IAuthenticationParameters).__jsii_proxy_class__ = lambda : _IAuthenticationParametersProxy


@jsii.interface(jsii_type="zap-cdk.IAuthenticationParametersParameters")
class IAuthenticationParametersParameters(typing_extensions.Protocol):
    '''
    :interface:

    IAuthenticationParametersParameters
    Represents the parameters for authentication in the scanning process.
    :property: {string} [scriptEngine] - Name of the script engine to use, only for 'script' authentication.
    '''

    @builtins.property
    @jsii.member(jsii_name="hostname")
    def hostname(self) -> typing.Optional[builtins.str]:
        ...

    @hostname.setter
    def hostname(self, value: typing.Optional[builtins.str]) -> None:
        ...

    @builtins.property
    @jsii.member(jsii_name="loginPageUrl")
    def login_page_url(self) -> typing.Optional[builtins.str]:
        ...

    @login_page_url.setter
    def login_page_url(self, value: typing.Optional[builtins.str]) -> None:
        ...

    @builtins.property
    @jsii.member(jsii_name="loginRequestBody")
    def login_request_body(self) -> typing.Optional[builtins.str]:
        ...

    @login_request_body.setter
    def login_request_body(self, value: typing.Optional[builtins.str]) -> None:
        ...

    @builtins.property
    @jsii.member(jsii_name="loginRequestUrl")
    def login_request_url(self) -> typing.Optional[builtins.str]:
        ...

    @login_request_url.setter
    def login_request_url(self, value: typing.Optional[builtins.str]) -> None:
        ...

    @builtins.property
    @jsii.member(jsii_name="port")
    def port(self) -> typing.Optional[jsii.Number]:
        ...

    @port.setter
    def port(self, value: typing.Optional[jsii.Number]) -> None:
        ...

    @builtins.property
    @jsii.member(jsii_name="realm")
    def realm(self) -> typing.Optional[builtins.str]:
        ...

    @realm.setter
    def realm(self, value: typing.Optional[builtins.str]) -> None:
        ...

    @builtins.property
    @jsii.member(jsii_name="script")
    def script(self) -> typing.Optional[builtins.str]:
        ...

    @script.setter
    def script(self, value: typing.Optional[builtins.str]) -> None:
        ...

    @builtins.property
    @jsii.member(jsii_name="scriptEngine")
    def script_engine(self) -> typing.Optional[builtins.str]:
        ...

    @script_engine.setter
    def script_engine(self, value: typing.Optional[builtins.str]) -> None:
        ...

    @builtins.property
    @jsii.member(jsii_name="scriptInline")
    def script_inline(self) -> typing.Optional[builtins.str]:
        ...

    @script_inline.setter
    def script_inline(self, value: typing.Optional[builtins.str]) -> None:
        ...


class _IAuthenticationParametersParametersProxy:
    '''
    :interface:

    IAuthenticationParametersParameters
    Represents the parameters for authentication in the scanning process.
    :property: {string} [scriptEngine] - Name of the script engine to use, only for 'script' authentication.
    '''

    __jsii_type__: typing.ClassVar[str] = "zap-cdk.IAuthenticationParametersParameters"

    @builtins.property
    @jsii.member(jsii_name="hostname")
    def hostname(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "hostname"))

    @hostname.setter
    def hostname(self, value: typing.Optional[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d7722de6da3f23b9bee929872cf1c42240abf16e71459625896965234450b29a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "hostname", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="loginPageUrl")
    def login_page_url(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "loginPageUrl"))

    @login_page_url.setter
    def login_page_url(self, value: typing.Optional[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__cc05d141dca7d154cfb390b1ef633f68a905d4dee0df08320b9ca25e839ed5bf)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "loginPageUrl", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="loginRequestBody")
    def login_request_body(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "loginRequestBody"))

    @login_request_body.setter
    def login_request_body(self, value: typing.Optional[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__af735d99ca9cd05f16721cfb7ffc462f4c651689235beb6b25ca30d6b7de746a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "loginRequestBody", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="loginRequestUrl")
    def login_request_url(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "loginRequestUrl"))

    @login_request_url.setter
    def login_request_url(self, value: typing.Optional[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__057387cabc540c339eea571e07f3c41f439b089e44183c3bbb2d0263d9cc062c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "loginRequestUrl", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="port")
    def port(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "port"))

    @port.setter
    def port(self, value: typing.Optional[jsii.Number]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6a410c51610a2503684646ecc72748ec4585aba60377b941b8e7578e774665e5)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "port", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="realm")
    def realm(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "realm"))

    @realm.setter
    def realm(self, value: typing.Optional[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9601df8316ae67794e7549bf77b9c3fb5eda8d849f909d70b77a69039178f039)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "realm", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="script")
    def script(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "script"))

    @script.setter
    def script(self, value: typing.Optional[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__eca06960314e389be33991fc2e375a4384aeb214e2eb55eec0c9421cbd40ec44)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "script", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="scriptEngine")
    def script_engine(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "scriptEngine"))

    @script_engine.setter
    def script_engine(self, value: typing.Optional[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9cbbe943d2fad64468c336d3aadc97861dfb1a9ab3521140692b94a7b289ac63)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "scriptEngine", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="scriptInline")
    def script_inline(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "scriptInline"))

    @script_inline.setter
    def script_inline(self, value: typing.Optional[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d50db271d9e3e333b41961042aea8ee28ad5533a30eb48b6dc2d032e315b188c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "scriptInline", value) # pyright: ignore[reportArgumentType]

# Adding a "__jsii_proxy_class__(): typing.Type" function to the interface
typing.cast(typing.Any, IAuthenticationParametersParameters).__jsii_proxy_class__ = lambda : _IAuthenticationParametersParametersProxy


@jsii.interface(jsii_type="zap-cdk.IAuthenticationParametersVerification")
class IAuthenticationParametersVerification(typing_extensions.Protocol):
    '''
    :interface:

    IAuthenticationParametersVerification
    Represents the verification details for authentication in the scanning process.
    :property: {string} pollAdditionalHeaders[].value - The header value.
    '''

    @builtins.property
    @jsii.member(jsii_name="method")
    def method(self) -> builtins.str:
        ...

    @method.setter
    def method(self, value: builtins.str) -> None:
        ...

    @builtins.property
    @jsii.member(jsii_name="loggedInRegex")
    def logged_in_regex(self) -> typing.Optional[builtins.str]:
        ...

    @logged_in_regex.setter
    def logged_in_regex(self, value: typing.Optional[builtins.str]) -> None:
        ...

    @builtins.property
    @jsii.member(jsii_name="loggedOutRegex")
    def logged_out_regex(self) -> typing.Optional[builtins.str]:
        ...

    @logged_out_regex.setter
    def logged_out_regex(self, value: typing.Optional[builtins.str]) -> None:
        ...

    @builtins.property
    @jsii.member(jsii_name="pollAdditionalHeaders")
    def poll_additional_headers(
        self,
    ) -> typing.Optional[typing.List["IPollAdditionalHeaders"]]:
        ...

    @poll_additional_headers.setter
    def poll_additional_headers(
        self,
        value: typing.Optional[typing.List["IPollAdditionalHeaders"]],
    ) -> None:
        ...

    @builtins.property
    @jsii.member(jsii_name="pollFrequency")
    def poll_frequency(self) -> typing.Optional[jsii.Number]:
        ...

    @poll_frequency.setter
    def poll_frequency(self, value: typing.Optional[jsii.Number]) -> None:
        ...

    @builtins.property
    @jsii.member(jsii_name="pollPostData")
    def poll_post_data(self) -> typing.Optional[builtins.str]:
        ...

    @poll_post_data.setter
    def poll_post_data(self, value: typing.Optional[builtins.str]) -> None:
        ...

    @builtins.property
    @jsii.member(jsii_name="pollUnits")
    def poll_units(self) -> typing.Optional[builtins.str]:
        ...

    @poll_units.setter
    def poll_units(self, value: typing.Optional[builtins.str]) -> None:
        ...

    @builtins.property
    @jsii.member(jsii_name="pollUrl")
    def poll_url(self) -> typing.Optional[builtins.str]:
        ...

    @poll_url.setter
    def poll_url(self, value: typing.Optional[builtins.str]) -> None:
        ...


class _IAuthenticationParametersVerificationProxy:
    '''
    :interface:

    IAuthenticationParametersVerification
    Represents the verification details for authentication in the scanning process.
    :property: {string} pollAdditionalHeaders[].value - The header value.
    '''

    __jsii_type__: typing.ClassVar[str] = "zap-cdk.IAuthenticationParametersVerification"

    @builtins.property
    @jsii.member(jsii_name="method")
    def method(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "method"))

    @method.setter
    def method(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f98568443479f6e4b822117f1faf317c1ab2b6da60be36bc215c2666ceb0b360)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "method", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="loggedInRegex")
    def logged_in_regex(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "loggedInRegex"))

    @logged_in_regex.setter
    def logged_in_regex(self, value: typing.Optional[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__118ea4c4c3c355359d986242f4ede515e91c9ff7298a92d41d339046a8261770)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "loggedInRegex", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="loggedOutRegex")
    def logged_out_regex(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "loggedOutRegex"))

    @logged_out_regex.setter
    def logged_out_regex(self, value: typing.Optional[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ada7966e20dc36ceecbd4ddd9f3a1ab2d4d46f605bde6e705c0c5f1f95c576e9)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "loggedOutRegex", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="pollAdditionalHeaders")
    def poll_additional_headers(
        self,
    ) -> typing.Optional[typing.List["IPollAdditionalHeaders"]]:
        return typing.cast(typing.Optional[typing.List["IPollAdditionalHeaders"]], jsii.get(self, "pollAdditionalHeaders"))

    @poll_additional_headers.setter
    def poll_additional_headers(
        self,
        value: typing.Optional[typing.List["IPollAdditionalHeaders"]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ccce2a650b964a71adac5bbba632cf65daf5c3c138768eb8e9be1a4950684faf)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "pollAdditionalHeaders", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="pollFrequency")
    def poll_frequency(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "pollFrequency"))

    @poll_frequency.setter
    def poll_frequency(self, value: typing.Optional[jsii.Number]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ae0c1e4140f4419e50c482a646dea15e36406221ab262e0c1f9230d82c6b9de2)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "pollFrequency", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="pollPostData")
    def poll_post_data(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "pollPostData"))

    @poll_post_data.setter
    def poll_post_data(self, value: typing.Optional[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__97fea499561aaeeceac009bbd051fb9c8a1388ca74a6648fe9d8fd5ecac3ac02)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "pollPostData", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="pollUnits")
    def poll_units(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "pollUnits"))

    @poll_units.setter
    def poll_units(self, value: typing.Optional[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5c3a8d01f94ce3f84bc1bff5149f4ed9b3db9f1c3fe72824fa44f37cd135c9e3)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "pollUnits", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="pollUrl")
    def poll_url(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "pollUrl"))

    @poll_url.setter
    def poll_url(self, value: typing.Optional[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__aac8f6c5d303c9f1b02fb7d5814dd71668177ae7f08cf794b7334c11b2a434f3)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "pollUrl", value) # pyright: ignore[reportArgumentType]

# Adding a "__jsii_proxy_class__(): typing.Type" function to the interface
typing.cast(typing.Any, IAuthenticationParametersVerification).__jsii_proxy_class__ = lambda : _IAuthenticationParametersVerificationProxy


@jsii.interface(jsii_type="zap-cdk.IContext")
class IContext(typing_extensions.Protocol):
    '''
    :interface:

    IContext
    Represents a scanning context with its configuration.
    :property: {string} [users[].credentials[].totp.algorithm] - Algorithm, default: SHA1.
    '''

    @builtins.property
    @jsii.member(jsii_name="authentication")
    def authentication(self) -> IAuthenticationParameters:
        ...

    @authentication.setter
    def authentication(self, value: IAuthenticationParameters) -> None:
        ...

    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        ...

    @name.setter
    def name(self, value: builtins.str) -> None:
        ...

    @builtins.property
    @jsii.member(jsii_name="sessionManagement")
    def session_management(self) -> "ISessionManagementParameters":
        ...

    @session_management.setter
    def session_management(self, value: "ISessionManagementParameters") -> None:
        ...

    @builtins.property
    @jsii.member(jsii_name="structure")
    def structure(self) -> "IContextStructure":
        ...

    @structure.setter
    def structure(self, value: "IContextStructure") -> None:
        ...

    @builtins.property
    @jsii.member(jsii_name="technology")
    def technology(self) -> "ITechnology":
        ...

    @technology.setter
    def technology(self, value: "ITechnology") -> None:
        ...

    @builtins.property
    @jsii.member(jsii_name="urls")
    def urls(self) -> typing.List[builtins.str]:
        ...

    @urls.setter
    def urls(self, value: typing.List[builtins.str]) -> None:
        ...

    @builtins.property
    @jsii.member(jsii_name="users")
    def users(self) -> typing.List["IContextUser"]:
        ...

    @users.setter
    def users(self, value: typing.List["IContextUser"]) -> None:
        ...

    @builtins.property
    @jsii.member(jsii_name="excludePaths")
    def exclude_paths(self) -> typing.Optional[typing.List[builtins.str]]:
        ...

    @exclude_paths.setter
    def exclude_paths(self, value: typing.Optional[typing.List[builtins.str]]) -> None:
        ...

    @builtins.property
    @jsii.member(jsii_name="includePaths")
    def include_paths(self) -> typing.Optional[typing.List[builtins.str]]:
        ...

    @include_paths.setter
    def include_paths(self, value: typing.Optional[typing.List[builtins.str]]) -> None:
        ...


class _IContextProxy:
    '''
    :interface:

    IContext
    Represents a scanning context with its configuration.
    :property: {string} [users[].credentials[].totp.algorithm] - Algorithm, default: SHA1.
    '''

    __jsii_type__: typing.ClassVar[str] = "zap-cdk.IContext"

    @builtins.property
    @jsii.member(jsii_name="authentication")
    def authentication(self) -> IAuthenticationParameters:
        return typing.cast(IAuthenticationParameters, jsii.get(self, "authentication"))

    @authentication.setter
    def authentication(self, value: IAuthenticationParameters) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8c862f64c3e233c811f69417491907f84a9db5f5e836d0981f53f2a13bd8e22a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "authentication", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c8e1c18039e856bc81d0326d612323226e95b51b592f64fb578e0800ec17b02d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "name", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="sessionManagement")
    def session_management(self) -> "ISessionManagementParameters":
        return typing.cast("ISessionManagementParameters", jsii.get(self, "sessionManagement"))

    @session_management.setter
    def session_management(self, value: "ISessionManagementParameters") -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9c6f1336a5d8e4baaab4f3257b7b569268fbeb7b328d7ff0070c3c274117d806)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "sessionManagement", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="structure")
    def structure(self) -> "IContextStructure":
        return typing.cast("IContextStructure", jsii.get(self, "structure"))

    @structure.setter
    def structure(self, value: "IContextStructure") -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d679875cf018302a684da54609a79b6ed28a8b22499640e405aff291c2c9ddd4)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "structure", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="technology")
    def technology(self) -> "ITechnology":
        return typing.cast("ITechnology", jsii.get(self, "technology"))

    @technology.setter
    def technology(self, value: "ITechnology") -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__023611b082ef91815328e9c33e92b29fa4d8dae6a5c9026d4e262840b2745c37)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "technology", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="urls")
    def urls(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "urls"))

    @urls.setter
    def urls(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__fc069919a92a2a50127dacd4e153b0119693b0c8667fc4ff72aac97cf869bef1)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "urls", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="users")
    def users(self) -> typing.List["IContextUser"]:
        return typing.cast(typing.List["IContextUser"], jsii.get(self, "users"))

    @users.setter
    def users(self, value: typing.List["IContextUser"]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1800e8c445df948fd81324601df77c79e5a2fb72132c9813751b6b5abca6f16e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "users", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="excludePaths")
    def exclude_paths(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "excludePaths"))

    @exclude_paths.setter
    def exclude_paths(self, value: typing.Optional[typing.List[builtins.str]]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__cc812fadac413f546f2f25dd634eb020cce042011da3d1edb13ee573e5ed1260)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "excludePaths", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="includePaths")
    def include_paths(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "includePaths"))

    @include_paths.setter
    def include_paths(self, value: typing.Optional[typing.List[builtins.str]]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__388e1d152cd4efd76cdf203a3126b01c7970d6c8279a157560903198b168b941)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "includePaths", value) # pyright: ignore[reportArgumentType]

# Adding a "__jsii_proxy_class__(): typing.Type" function to the interface
typing.cast(typing.Any, IContext).__jsii_proxy_class__ = lambda : _IContextProxy


@jsii.interface(jsii_type="zap-cdk.IContextStructure")
class IContextStructure(typing_extensions.Protocol):
    '''
    :interface:

    IContextStructure
    Represents the structure details of the context.
    :property: {IDataDrivenNode[]} [dataDrivenNodes] - List of data driven nodes.
    '''

    @builtins.property
    @jsii.member(jsii_name="dataDrivenNodes")
    def data_driven_nodes(self) -> typing.Optional[typing.List["IDataDrivenNode"]]:
        ...

    @data_driven_nodes.setter
    def data_driven_nodes(
        self,
        value: typing.Optional[typing.List["IDataDrivenNode"]],
    ) -> None:
        ...

    @builtins.property
    @jsii.member(jsii_name="structuralParameters")
    def structural_parameters(self) -> typing.Optional[typing.List[builtins.str]]:
        ...

    @structural_parameters.setter
    def structural_parameters(
        self,
        value: typing.Optional[typing.List[builtins.str]],
    ) -> None:
        ...


class _IContextStructureProxy:
    '''
    :interface:

    IContextStructure
    Represents the structure details of the context.
    :property: {IDataDrivenNode[]} [dataDrivenNodes] - List of data driven nodes.
    '''

    __jsii_type__: typing.ClassVar[str] = "zap-cdk.IContextStructure"

    @builtins.property
    @jsii.member(jsii_name="dataDrivenNodes")
    def data_driven_nodes(self) -> typing.Optional[typing.List["IDataDrivenNode"]]:
        return typing.cast(typing.Optional[typing.List["IDataDrivenNode"]], jsii.get(self, "dataDrivenNodes"))

    @data_driven_nodes.setter
    def data_driven_nodes(
        self,
        value: typing.Optional[typing.List["IDataDrivenNode"]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0fd6b5b3089372632a8a643008f1bbd3e3615251dd187c0d8ccf5cc967d9a153)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "dataDrivenNodes", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="structuralParameters")
    def structural_parameters(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "structuralParameters"))

    @structural_parameters.setter
    def structural_parameters(
        self,
        value: typing.Optional[typing.List[builtins.str]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__75352072ad66a000838b8928aab3d33d1a2a70122e7df2552c524051a7c9109a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "structuralParameters", value) # pyright: ignore[reportArgumentType]

# Adding a "__jsii_proxy_class__(): typing.Type" function to the interface
typing.cast(typing.Any, IContextStructure).__jsii_proxy_class__ = lambda : _IContextStructureProxy


@jsii.interface(jsii_type="zap-cdk.IContextUser")
class IContextUser(typing_extensions.Protocol):
    '''
    :interface:

    IContextUser
    Represents a user in the context.
    :property: {IUserCredentials[]} credentials - User credentials for authentication.
    '''

    @builtins.property
    @jsii.member(jsii_name="credentials")
    def credentials(self) -> typing.List["IUserCredentials"]:
        ...

    @credentials.setter
    def credentials(self, value: typing.List["IUserCredentials"]) -> None:
        ...

    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        ...

    @name.setter
    def name(self, value: builtins.str) -> None:
        ...


class _IContextUserProxy:
    '''
    :interface:

    IContextUser
    Represents a user in the context.
    :property: {IUserCredentials[]} credentials - User credentials for authentication.
    '''

    __jsii_type__: typing.ClassVar[str] = "zap-cdk.IContextUser"

    @builtins.property
    @jsii.member(jsii_name="credentials")
    def credentials(self) -> typing.List["IUserCredentials"]:
        return typing.cast(typing.List["IUserCredentials"], jsii.get(self, "credentials"))

    @credentials.setter
    def credentials(self, value: typing.List["IUserCredentials"]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__097a558df1763bf58907c54142e2470e06076adf69050640ce5f173fafdb0a29)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "credentials", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__872d5f242b5f813327d0fc8f8cb147042d6b51983fc6235fb63373739768f5a2)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "name", value) # pyright: ignore[reportArgumentType]

# Adding a "__jsii_proxy_class__(): typing.Type" function to the interface
typing.cast(typing.Any, IContextUser).__jsii_proxy_class__ = lambda : _IContextUserProxy


@jsii.interface(jsii_type="zap-cdk.ICookieData")
class ICookieData(typing_extensions.Protocol):
    '''Configuration for cookie data scanning.

    :interface: ICookieData
    :property: {boolean} [encodeCookieValues] - If cookie values should be encoded. Default: false.
    '''

    @builtins.property
    @jsii.member(jsii_name="enabled")
    def enabled(self) -> typing.Optional[builtins.bool]:
        '''If cookie scanning is enabled.

        Default: false
        '''
        ...

    @enabled.setter
    def enabled(self, value: typing.Optional[builtins.bool]) -> None:
        ...

    @builtins.property
    @jsii.member(jsii_name="encodeCookieValues")
    def encode_cookie_values(self) -> typing.Optional[builtins.bool]:
        '''If cookie values should be encoded.

        Default: false
        '''
        ...

    @encode_cookie_values.setter
    def encode_cookie_values(self, value: typing.Optional[builtins.bool]) -> None:
        ...


class _ICookieDataProxy:
    '''Configuration for cookie data scanning.

    :interface: ICookieData
    :property: {boolean} [encodeCookieValues] - If cookie values should be encoded. Default: false.
    '''

    __jsii_type__: typing.ClassVar[str] = "zap-cdk.ICookieData"

    @builtins.property
    @jsii.member(jsii_name="enabled")
    def enabled(self) -> typing.Optional[builtins.bool]:
        '''If cookie scanning is enabled.

        Default: false
        '''
        return typing.cast(typing.Optional[builtins.bool], jsii.get(self, "enabled"))

    @enabled.setter
    def enabled(self, value: typing.Optional[builtins.bool]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__dc8e8f04c54e6123c4810a13a5e2a39fe2762635293d3adf3479d80d5899f8e0)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "enabled", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="encodeCookieValues")
    def encode_cookie_values(self) -> typing.Optional[builtins.bool]:
        '''If cookie values should be encoded.

        Default: false
        '''
        return typing.cast(typing.Optional[builtins.bool], jsii.get(self, "encodeCookieValues"))

    @encode_cookie_values.setter
    def encode_cookie_values(self, value: typing.Optional[builtins.bool]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__bd97dcb5c08f30fa5b052c1f0419d13e1878c049aaec66ec8d16db2bfed03935)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "encodeCookieValues", value) # pyright: ignore[reportArgumentType]

# Adding a "__jsii_proxy_class__(): typing.Type" function to the interface
typing.cast(typing.Any, ICookieData).__jsii_proxy_class__ = lambda : _ICookieDataProxy


@jsii.interface(jsii_type="zap-cdk.IDataDrivenNode")
class IDataDrivenNode(typing_extensions.Protocol):
    '''
    :interface:

    IDataDrivenNode
    Represents a data-driven node in the scanning process.
    :property: {string} regex - Regex of the data driven node, must contain 2 or 3 regex groups.
    '''

    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        ...

    @name.setter
    def name(self, value: builtins.str) -> None:
        ...

    @builtins.property
    @jsii.member(jsii_name="regex")
    def regex(self) -> builtins.str:
        ...

    @regex.setter
    def regex(self, value: builtins.str) -> None:
        ...


class _IDataDrivenNodeProxy:
    '''
    :interface:

    IDataDrivenNode
    Represents a data-driven node in the scanning process.
    :property: {string} regex - Regex of the data driven node, must contain 2 or 3 regex groups.
    '''

    __jsii_type__: typing.ClassVar[str] = "zap-cdk.IDataDrivenNode"

    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__66fb3a3e8df2ef347cd78ccb33369c7bc87588ae33ce53e106d767109075d75b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "name", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="regex")
    def regex(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "regex"))

    @regex.setter
    def regex(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f6394c43ee982be11016df20892c72fe0cb0aa5dcb92274e86c96b19b9fbeb88)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "regex", value) # pyright: ignore[reportArgumentType]

# Adding a "__jsii_proxy_class__(): typing.Type" function to the interface
typing.cast(typing.Any, IDataDrivenNode).__jsii_proxy_class__ = lambda : _IDataDrivenNodeProxy


@jsii.interface(jsii_type="zap-cdk.IDelay")
class IDelay(typing_extensions.Protocol):
    '''
    :interface:

    IDelay
    Represents a delay configuration in the execution plan.
    :property: {boolean} [alwaysRun] - If set and the job is enabled, then it will run even if the plan exits early, default: false.
    '''

    @builtins.property
    @jsii.member(jsii_name="parameters")
    def parameters(self) -> "IDelayParameters":
        ...

    @parameters.setter
    def parameters(self, value: "IDelayParameters") -> None:
        ...

    @builtins.property
    @jsii.member(jsii_name="type")
    def type(self) -> builtins.str:
        ...

    @type.setter
    def type(self, value: builtins.str) -> None:
        ...

    @builtins.property
    @jsii.member(jsii_name="alwaysRun")
    def always_run(self) -> typing.Optional[builtins.bool]:
        ...

    @always_run.setter
    def always_run(self, value: typing.Optional[builtins.bool]) -> None:
        ...

    @builtins.property
    @jsii.member(jsii_name="enabled")
    def enabled(self) -> typing.Optional[builtins.bool]:
        ...

    @enabled.setter
    def enabled(self, value: typing.Optional[builtins.bool]) -> None:
        ...


class _IDelayProxy:
    '''
    :interface:

    IDelay
    Represents a delay configuration in the execution plan.
    :property: {boolean} [alwaysRun] - If set and the job is enabled, then it will run even if the plan exits early, default: false.
    '''

    __jsii_type__: typing.ClassVar[str] = "zap-cdk.IDelay"

    @builtins.property
    @jsii.member(jsii_name="parameters")
    def parameters(self) -> "IDelayParameters":
        return typing.cast("IDelayParameters", jsii.get(self, "parameters"))

    @parameters.setter
    def parameters(self, value: "IDelayParameters") -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b730c719e133b1c7ce7773831132cab46aef67c413180f1c300b9ea933aac436)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "parameters", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="type")
    def type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "type"))

    @type.setter
    def type(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__94e589c03ad6ada9445ec74ce69bbb1c05b100249ee2c30743b06b33e651d627)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "type", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="alwaysRun")
    def always_run(self) -> typing.Optional[builtins.bool]:
        return typing.cast(typing.Optional[builtins.bool], jsii.get(self, "alwaysRun"))

    @always_run.setter
    def always_run(self, value: typing.Optional[builtins.bool]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1f1f4dff092de5c04dbe769cad8b66478b37f0d43fcfaeea056c777e73ab8c96)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "alwaysRun", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="enabled")
    def enabled(self) -> typing.Optional[builtins.bool]:
        return typing.cast(typing.Optional[builtins.bool], jsii.get(self, "enabled"))

    @enabled.setter
    def enabled(self, value: typing.Optional[builtins.bool]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c43d355833a5c01c5d21405def976685d91fa5f49c97bb22144d891d7d0ea9e2)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "enabled", value) # pyright: ignore[reportArgumentType]

# Adding a "__jsii_proxy_class__(): typing.Type" function to the interface
typing.cast(typing.Any, IDelay).__jsii_proxy_class__ = lambda : _IDelayProxy


@jsii.interface(jsii_type="zap-cdk.IDelayParameters")
class IDelayParameters(typing_extensions.Protocol):
    '''
    :interface:

    IDelayParameters
    Represents the parameters for configuring a delay in the execution plan.
    :property: {string} [fileName] - Name of a file which will cause the job to end early if created, default: empty.
    '''

    @builtins.property
    @jsii.member(jsii_name="fileName")
    def file_name(self) -> typing.Optional[builtins.str]:
        ...

    @file_name.setter
    def file_name(self, value: typing.Optional[builtins.str]) -> None:
        ...

    @builtins.property
    @jsii.member(jsii_name="time")
    def time(self) -> typing.Optional[builtins.str]:
        ...

    @time.setter
    def time(self, value: typing.Optional[builtins.str]) -> None:
        ...


class _IDelayParametersProxy:
    '''
    :interface:

    IDelayParameters
    Represents the parameters for configuring a delay in the execution plan.
    :property: {string} [fileName] - Name of a file which will cause the job to end early if created, default: empty.
    '''

    __jsii_type__: typing.ClassVar[str] = "zap-cdk.IDelayParameters"

    @builtins.property
    @jsii.member(jsii_name="fileName")
    def file_name(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "fileName"))

    @file_name.setter
    def file_name(self, value: typing.Optional[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2636f4bf0c4cc2b854bbc568fd2d2f0483851290fc6233d405a0fbb0eda22857)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "fileName", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="time")
    def time(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "time"))

    @time.setter
    def time(self, value: typing.Optional[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__07472401d586b743c20da73bfb17a88b7e6d23a59fba5bfbf1552ee4026b76b5)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "time", value) # pyright: ignore[reportArgumentType]

# Adding a "__jsii_proxy_class__(): typing.Type" function to the interface
typing.cast(typing.Any, IDelayParameters).__jsii_proxy_class__ = lambda : _IDelayParametersProxy


@jsii.interface(jsii_type="zap-cdk.IDelayProps")
class IDelayProps(typing_extensions.Protocol):
    '''Properties for the DelayConfig construct.

    :interface: IDelayProps
    :property: {IDelay} delay - The delay configuration.
    '''

    @builtins.property
    @jsii.member(jsii_name="delay")
    def delay(self) -> IDelay:
        ...

    @delay.setter
    def delay(self, value: IDelay) -> None:
        ...


class _IDelayPropsProxy:
    '''Properties for the DelayConfig construct.

    :interface: IDelayProps
    :property: {IDelay} delay - The delay configuration.
    '''

    __jsii_type__: typing.ClassVar[str] = "zap-cdk.IDelayProps"

    @builtins.property
    @jsii.member(jsii_name="delay")
    def delay(self) -> IDelay:
        return typing.cast(IDelay, jsii.get(self, "delay"))

    @delay.setter
    def delay(self, value: IDelay) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__715bd77d7edb3c9f890ea64fe61c86906b10c71a509965c9e97818e75f224dc0)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "delay", value) # pyright: ignore[reportArgumentType]

# Adding a "__jsii_proxy_class__(): typing.Type" function to the interface
typing.cast(typing.Any, IDelayProps).__jsii_proxy_class__ = lambda : _IDelayPropsProxy


@jsii.interface(jsii_type="zap-cdk.IEnvironment")
class IEnvironment(typing_extensions.Protocol):
    '''
    :interface:

    IEnvironment
    Represents the environment configuration for the scanning process.
    :property: {string} [proxy.password] - Proxy password.
    '''

    @builtins.property
    @jsii.member(jsii_name="contexts")
    def contexts(self) -> typing.List[IContext]:
        ...

    @contexts.setter
    def contexts(self, value: typing.List[IContext]) -> None:
        ...

    @builtins.property
    @jsii.member(jsii_name="parameters")
    def parameters(self) -> "IEnvironmentParameters":
        ...

    @parameters.setter
    def parameters(self, value: "IEnvironmentParameters") -> None:
        ...

    @builtins.property
    @jsii.member(jsii_name="proxy")
    def proxy(self) -> typing.Optional["IEnvironmentProxy"]:
        ...

    @proxy.setter
    def proxy(self, value: typing.Optional["IEnvironmentProxy"]) -> None:
        ...

    @builtins.property
    @jsii.member(jsii_name="vars")
    def vars(self) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        ...

    @vars.setter
    def vars(
        self,
        value: typing.Optional[typing.Mapping[builtins.str, builtins.str]],
    ) -> None:
        ...


class _IEnvironmentProxy:
    '''
    :interface:

    IEnvironment
    Represents the environment configuration for the scanning process.
    :property: {string} [proxy.password] - Proxy password.
    '''

    __jsii_type__: typing.ClassVar[str] = "zap-cdk.IEnvironment"

    @builtins.property
    @jsii.member(jsii_name="contexts")
    def contexts(self) -> typing.List[IContext]:
        return typing.cast(typing.List[IContext], jsii.get(self, "contexts"))

    @contexts.setter
    def contexts(self, value: typing.List[IContext]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__40141bbad17e31af6d4a8668fd75c5cca81f33a1d81e0600751ac227748465f2)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "contexts", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="parameters")
    def parameters(self) -> "IEnvironmentParameters":
        return typing.cast("IEnvironmentParameters", jsii.get(self, "parameters"))

    @parameters.setter
    def parameters(self, value: "IEnvironmentParameters") -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b8829711d0d415de7fb1e41b5d999f3aa6cd8f4c8f5b3de9facd6470aeca60ee)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "parameters", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="proxy")
    def proxy(self) -> typing.Optional["IEnvironmentProxy"]:
        return typing.cast(typing.Optional["IEnvironmentProxy"], jsii.get(self, "proxy"))

    @proxy.setter
    def proxy(self, value: typing.Optional["IEnvironmentProxy"]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__064cd1a824ea925cf83951d5e66badc65046b479ed41782d705c156caae2aa43)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "proxy", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="vars")
    def vars(self) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], jsii.get(self, "vars"))

    @vars.setter
    def vars(
        self,
        value: typing.Optional[typing.Mapping[builtins.str, builtins.str]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__51ba43f89bbdfd1c12dc49b3c60fe94227125886518830a8aeed92410e55ee0b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "vars", value) # pyright: ignore[reportArgumentType]

# Adding a "__jsii_proxy_class__(): typing.Type" function to the interface
typing.cast(typing.Any, IEnvironment).__jsii_proxy_class__ = lambda : _IEnvironmentProxy


@jsii.interface(jsii_type="zap-cdk.IEnvironmentParameters")
class IEnvironmentParameters(typing_extensions.Protocol):
    '''
    :interface:

    IEnvironmentParameters
    Represents the parameters for the environment configuration in the scanning process.
    :property: {boolean} [progressToStdout] - If true, write job progress to stdout.
    '''

    @builtins.property
    @jsii.member(jsii_name="continueOnFailure")
    def continue_on_failure(self) -> typing.Optional[builtins.bool]:
        ...

    @continue_on_failure.setter
    def continue_on_failure(self, value: typing.Optional[builtins.bool]) -> None:
        ...

    @builtins.property
    @jsii.member(jsii_name="failOnError")
    def fail_on_error(self) -> typing.Optional[builtins.bool]:
        ...

    @fail_on_error.setter
    def fail_on_error(self, value: typing.Optional[builtins.bool]) -> None:
        ...

    @builtins.property
    @jsii.member(jsii_name="failOnWarning")
    def fail_on_warning(self) -> typing.Optional[builtins.bool]:
        ...

    @fail_on_warning.setter
    def fail_on_warning(self, value: typing.Optional[builtins.bool]) -> None:
        ...

    @builtins.property
    @jsii.member(jsii_name="progressToStdout")
    def progress_to_stdout(self) -> typing.Optional[builtins.bool]:
        ...

    @progress_to_stdout.setter
    def progress_to_stdout(self, value: typing.Optional[builtins.bool]) -> None:
        ...


class _IEnvironmentParametersProxy:
    '''
    :interface:

    IEnvironmentParameters
    Represents the parameters for the environment configuration in the scanning process.
    :property: {boolean} [progressToStdout] - If true, write job progress to stdout.
    '''

    __jsii_type__: typing.ClassVar[str] = "zap-cdk.IEnvironmentParameters"

    @builtins.property
    @jsii.member(jsii_name="continueOnFailure")
    def continue_on_failure(self) -> typing.Optional[builtins.bool]:
        return typing.cast(typing.Optional[builtins.bool], jsii.get(self, "continueOnFailure"))

    @continue_on_failure.setter
    def continue_on_failure(self, value: typing.Optional[builtins.bool]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c1911f3aedbaba8a64fa0a00c8925f460a2388bd5f49350bfd699d8eaf3697ce)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "continueOnFailure", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="failOnError")
    def fail_on_error(self) -> typing.Optional[builtins.bool]:
        return typing.cast(typing.Optional[builtins.bool], jsii.get(self, "failOnError"))

    @fail_on_error.setter
    def fail_on_error(self, value: typing.Optional[builtins.bool]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e416f80420e701db0588e752474c5aaeaae2bb74ef370c5f3fdbcc63b5c7c55b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "failOnError", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="failOnWarning")
    def fail_on_warning(self) -> typing.Optional[builtins.bool]:
        return typing.cast(typing.Optional[builtins.bool], jsii.get(self, "failOnWarning"))

    @fail_on_warning.setter
    def fail_on_warning(self, value: typing.Optional[builtins.bool]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4932a64a79d7479c667ce3b9f1e8246da8baa11ed5aa91197937f3edd885f878)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "failOnWarning", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="progressToStdout")
    def progress_to_stdout(self) -> typing.Optional[builtins.bool]:
        return typing.cast(typing.Optional[builtins.bool], jsii.get(self, "progressToStdout"))

    @progress_to_stdout.setter
    def progress_to_stdout(self, value: typing.Optional[builtins.bool]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e29f17b433b9a7098d5d3b7ab3681cd1ad70ff572c184a101455eba9c2a30488)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "progressToStdout", value) # pyright: ignore[reportArgumentType]

# Adding a "__jsii_proxy_class__(): typing.Type" function to the interface
typing.cast(typing.Any, IEnvironmentParameters).__jsii_proxy_class__ = lambda : _IEnvironmentParametersProxy


@jsii.interface(jsii_type="zap-cdk.IEnvironmentProps")
class IEnvironmentProps(typing_extensions.Protocol):
    '''Properties for the EnvironmentConfig construct.

    :interface: IEnvironmentProps
    :property: {IEnvironment} environment - The environment configuration.
    '''

    @builtins.property
    @jsii.member(jsii_name="environment")
    def environment(self) -> IEnvironment:
        ...

    @environment.setter
    def environment(self, value: IEnvironment) -> None:
        ...


class _IEnvironmentPropsProxy:
    '''Properties for the EnvironmentConfig construct.

    :interface: IEnvironmentProps
    :property: {IEnvironment} environment - The environment configuration.
    '''

    __jsii_type__: typing.ClassVar[str] = "zap-cdk.IEnvironmentProps"

    @builtins.property
    @jsii.member(jsii_name="environment")
    def environment(self) -> IEnvironment:
        return typing.cast(IEnvironment, jsii.get(self, "environment"))

    @environment.setter
    def environment(self, value: IEnvironment) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__41a50bae66665638fdbf22cfa84315d58fcb3b295b646b721da8dd6e01190d5d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "environment", value) # pyright: ignore[reportArgumentType]

# Adding a "__jsii_proxy_class__(): typing.Type" function to the interface
typing.cast(typing.Any, IEnvironmentProps).__jsii_proxy_class__ = lambda : _IEnvironmentPropsProxy


@jsii.interface(jsii_type="zap-cdk.IEnvironmentProxy")
class IEnvironmentProxy(typing_extensions.Protocol):
    '''
    :interface:

    IEnvironmentProxy
    Represents the proxy configuration for the environment.
    :property: {string} [password] - Proxy password.
    '''

    @builtins.property
    @jsii.member(jsii_name="hostname")
    def hostname(self) -> typing.Optional[builtins.str]:
        ...

    @hostname.setter
    def hostname(self, value: typing.Optional[builtins.str]) -> None:
        ...

    @builtins.property
    @jsii.member(jsii_name="password")
    def password(self) -> typing.Optional[builtins.str]:
        ...

    @password.setter
    def password(self, value: typing.Optional[builtins.str]) -> None:
        ...

    @builtins.property
    @jsii.member(jsii_name="port")
    def port(self) -> typing.Optional[jsii.Number]:
        ...

    @port.setter
    def port(self, value: typing.Optional[jsii.Number]) -> None:
        ...

    @builtins.property
    @jsii.member(jsii_name="realm")
    def realm(self) -> typing.Optional[builtins.str]:
        ...

    @realm.setter
    def realm(self, value: typing.Optional[builtins.str]) -> None:
        ...

    @builtins.property
    @jsii.member(jsii_name="username")
    def username(self) -> typing.Optional[builtins.str]:
        ...

    @username.setter
    def username(self, value: typing.Optional[builtins.str]) -> None:
        ...


class _IEnvironmentProxyProxy:
    '''
    :interface:

    IEnvironmentProxy
    Represents the proxy configuration for the environment.
    :property: {string} [password] - Proxy password.
    '''

    __jsii_type__: typing.ClassVar[str] = "zap-cdk.IEnvironmentProxy"

    @builtins.property
    @jsii.member(jsii_name="hostname")
    def hostname(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "hostname"))

    @hostname.setter
    def hostname(self, value: typing.Optional[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7713df78eae5f387b5798289c84ae6024e9fdb69d060749d5ba2c8d9373be5d5)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "hostname", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="password")
    def password(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "password"))

    @password.setter
    def password(self, value: typing.Optional[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__147a45346a859b5371d8f9732fc2c5b6a7890676fdbb0963220786f358631e19)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "password", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="port")
    def port(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "port"))

    @port.setter
    def port(self, value: typing.Optional[jsii.Number]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4af490888e2dacf3862779f4ec5ced51237fc8bf392cfcb503c863ce48854a0b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "port", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="realm")
    def realm(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "realm"))

    @realm.setter
    def realm(self, value: typing.Optional[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c5cdb753c9882807617616b88099398ce129cb2116d9289588e2bb8c19aa21c8)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "realm", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="username")
    def username(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "username"))

    @username.setter
    def username(self, value: typing.Optional[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3c784287998c66234a46b216b81c1d3350f8302edca0472f6ad0e32d9e441f80)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "username", value) # pyright: ignore[reportArgumentType]

# Adding a "__jsii_proxy_class__(): typing.Type" function to the interface
typing.cast(typing.Any, IEnvironmentProxy).__jsii_proxy_class__ = lambda : _IEnvironmentProxyProxy


@jsii.interface(jsii_type="zap-cdk.IExcludedElement")
class IExcludedElement(typing_extensions.Protocol):
    '''Interface representing an excluded HTML element configuration.

    :interface: IExcludedElement
    :property: {string} [attributeValue] - Optional value of the attribute.
    '''

    @builtins.property
    @jsii.member(jsii_name="description")
    def description(self) -> builtins.str:
        ...

    @description.setter
    def description(self, value: builtins.str) -> None:
        ...

    @builtins.property
    @jsii.member(jsii_name="element")
    def element(self) -> builtins.str:
        ...

    @element.setter
    def element(self, value: builtins.str) -> None:
        ...

    @builtins.property
    @jsii.member(jsii_name="attributeName")
    def attribute_name(self) -> typing.Optional[builtins.str]:
        ...

    @attribute_name.setter
    def attribute_name(self, value: typing.Optional[builtins.str]) -> None:
        ...

    @builtins.property
    @jsii.member(jsii_name="attributeValue")
    def attribute_value(self) -> typing.Optional[builtins.str]:
        ...

    @attribute_value.setter
    def attribute_value(self, value: typing.Optional[builtins.str]) -> None:
        ...

    @builtins.property
    @jsii.member(jsii_name="text")
    def text(self) -> typing.Optional[builtins.str]:
        ...

    @text.setter
    def text(self, value: typing.Optional[builtins.str]) -> None:
        ...

    @builtins.property
    @jsii.member(jsii_name="xpath")
    def xpath(self) -> typing.Optional[builtins.str]:
        ...

    @xpath.setter
    def xpath(self, value: typing.Optional[builtins.str]) -> None:
        ...


class _IExcludedElementProxy:
    '''Interface representing an excluded HTML element configuration.

    :interface: IExcludedElement
    :property: {string} [attributeValue] - Optional value of the attribute.
    '''

    __jsii_type__: typing.ClassVar[str] = "zap-cdk.IExcludedElement"

    @builtins.property
    @jsii.member(jsii_name="description")
    def description(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "description"))

    @description.setter
    def description(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__63cbeb29c0c82088b41593e4bfcbc51e635ec403c9860b3b4f943c389f260af6)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "description", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="element")
    def element(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "element"))

    @element.setter
    def element(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__85c822cf69dd3ea149233158bfc19e56b9faf0c3e3906276fbc7f76624b7d049)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "element", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="attributeName")
    def attribute_name(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "attributeName"))

    @attribute_name.setter
    def attribute_name(self, value: typing.Optional[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__614d320a0ebd99163b7b84ca474307b37324e4886c38d698172b3ddacb12611f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "attributeName", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="attributeValue")
    def attribute_value(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "attributeValue"))

    @attribute_value.setter
    def attribute_value(self, value: typing.Optional[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8cd3f4e45797ad6bc894cdcea290c5eab6b334129fb37f045f6941d4ba258ad2)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "attributeValue", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="text")
    def text(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "text"))

    @text.setter
    def text(self, value: typing.Optional[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4a10db7eaf990d2991fb4d1db9f5302f3171cbfa02800cfcb6789bba66e5d638)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "text", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="xpath")
    def xpath(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "xpath"))

    @xpath.setter
    def xpath(self, value: typing.Optional[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__07083a02c313a32da683b59677a12b0c5818b98744433dd9c134f3c768712c5b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "xpath", value) # pyright: ignore[reportArgumentType]

# Adding a "__jsii_proxy_class__(): typing.Type" function to the interface
typing.cast(typing.Any, IExcludedElement).__jsii_proxy_class__ = lambda : _IExcludedElementProxy


@jsii.interface(jsii_type="zap-cdk.IExitStatus")
class IExitStatus(typing_extensions.Protocol):
    '''
    :interface:

    IExitStatus
    Represents the exit status configuration for the scanning process.
    :property: {boolean} [alwaysRun] - If set and the job is enabled, then it will run even if the plan exits early, default: false.
    '''

    @builtins.property
    @jsii.member(jsii_name="parameters")
    def parameters(self) -> "IExitStatusParameters":
        ...

    @parameters.setter
    def parameters(self, value: "IExitStatusParameters") -> None:
        ...

    @builtins.property
    @jsii.member(jsii_name="type")
    def type(self) -> builtins.str:
        ...

    @type.setter
    def type(self, value: builtins.str) -> None:
        ...

    @builtins.property
    @jsii.member(jsii_name="alwaysRun")
    def always_run(self) -> typing.Optional[builtins.bool]:
        ...

    @always_run.setter
    def always_run(self, value: typing.Optional[builtins.bool]) -> None:
        ...

    @builtins.property
    @jsii.member(jsii_name="enabled")
    def enabled(self) -> typing.Optional[builtins.bool]:
        ...

    @enabled.setter
    def enabled(self, value: typing.Optional[builtins.bool]) -> None:
        ...


class _IExitStatusProxy:
    '''
    :interface:

    IExitStatus
    Represents the exit status configuration for the scanning process.
    :property: {boolean} [alwaysRun] - If set and the job is enabled, then it will run even if the plan exits early, default: false.
    '''

    __jsii_type__: typing.ClassVar[str] = "zap-cdk.IExitStatus"

    @builtins.property
    @jsii.member(jsii_name="parameters")
    def parameters(self) -> "IExitStatusParameters":
        return typing.cast("IExitStatusParameters", jsii.get(self, "parameters"))

    @parameters.setter
    def parameters(self, value: "IExitStatusParameters") -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1fe777f75a19706efa755d94879858e18e51f710330c0e4bbb52076e51e409bc)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "parameters", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="type")
    def type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "type"))

    @type.setter
    def type(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a812a7aa1a6253a95d6c152f0bc5415e6d7da0fa3adafd385507d478a284991a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "type", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="alwaysRun")
    def always_run(self) -> typing.Optional[builtins.bool]:
        return typing.cast(typing.Optional[builtins.bool], jsii.get(self, "alwaysRun"))

    @always_run.setter
    def always_run(self, value: typing.Optional[builtins.bool]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c733167546ce73456e4d11d355335bb5400f23c37e14c4b19854fc7d4132f8fd)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "alwaysRun", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="enabled")
    def enabled(self) -> typing.Optional[builtins.bool]:
        return typing.cast(typing.Optional[builtins.bool], jsii.get(self, "enabled"))

    @enabled.setter
    def enabled(self, value: typing.Optional[builtins.bool]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f34cf95c2ef8c657e2cad1284a9ac27cb7a3d0d2c27087ef935ad4a325b246b9)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "enabled", value) # pyright: ignore[reportArgumentType]

# Adding a "__jsii_proxy_class__(): typing.Type" function to the interface
typing.cast(typing.Any, IExitStatus).__jsii_proxy_class__ = lambda : _IExitStatusProxy


@jsii.interface(jsii_type="zap-cdk.IExitStatusParameters")
class IExitStatusParameters(typing_extensions.Protocol):
    '''
    :interface:

    IExitStatusParameters
    Represents the parameters for configuring exit status in the scanning process.
    :property: {number} [warnExitValue] - Exit value if there are warnings, default: 2.
    '''

    @builtins.property
    @jsii.member(jsii_name="errorExitValue")
    def error_exit_value(self) -> typing.Optional[jsii.Number]:
        ...

    @error_exit_value.setter
    def error_exit_value(self, value: typing.Optional[jsii.Number]) -> None:
        ...

    @builtins.property
    @jsii.member(jsii_name="errorLevel")
    def error_level(self) -> typing.Optional[builtins.str]:
        ...

    @error_level.setter
    def error_level(self, value: typing.Optional[builtins.str]) -> None:
        ...

    @builtins.property
    @jsii.member(jsii_name="okExitValue")
    def ok_exit_value(self) -> typing.Optional[jsii.Number]:
        ...

    @ok_exit_value.setter
    def ok_exit_value(self, value: typing.Optional[jsii.Number]) -> None:
        ...

    @builtins.property
    @jsii.member(jsii_name="warnExitValue")
    def warn_exit_value(self) -> typing.Optional[jsii.Number]:
        ...

    @warn_exit_value.setter
    def warn_exit_value(self, value: typing.Optional[jsii.Number]) -> None:
        ...

    @builtins.property
    @jsii.member(jsii_name="warnLevel")
    def warn_level(self) -> typing.Optional[builtins.str]:
        ...

    @warn_level.setter
    def warn_level(self, value: typing.Optional[builtins.str]) -> None:
        ...


class _IExitStatusParametersProxy:
    '''
    :interface:

    IExitStatusParameters
    Represents the parameters for configuring exit status in the scanning process.
    :property: {number} [warnExitValue] - Exit value if there are warnings, default: 2.
    '''

    __jsii_type__: typing.ClassVar[str] = "zap-cdk.IExitStatusParameters"

    @builtins.property
    @jsii.member(jsii_name="errorExitValue")
    def error_exit_value(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "errorExitValue"))

    @error_exit_value.setter
    def error_exit_value(self, value: typing.Optional[jsii.Number]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2e2095af8e7b4ed3f1ea122c8adfd2fe86b7d6a3c984970074a87e3e01f94952)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "errorExitValue", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="errorLevel")
    def error_level(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "errorLevel"))

    @error_level.setter
    def error_level(self, value: typing.Optional[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__eb0547814e74540fb26f19399a3d8826bd34d43a99158596c483973237541148)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "errorLevel", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="okExitValue")
    def ok_exit_value(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "okExitValue"))

    @ok_exit_value.setter
    def ok_exit_value(self, value: typing.Optional[jsii.Number]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f3d5683c2349dbe83186858abc96a6c157467d396c3184aba29e78806569dd5f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "okExitValue", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="warnExitValue")
    def warn_exit_value(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "warnExitValue"))

    @warn_exit_value.setter
    def warn_exit_value(self, value: typing.Optional[jsii.Number]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1c4fdbb71342dbaaa095625e69c12bf61e2c9018c4ec9be93738670b750c4ee5)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "warnExitValue", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="warnLevel")
    def warn_level(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "warnLevel"))

    @warn_level.setter
    def warn_level(self, value: typing.Optional[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__120feea8219b4068dcacd4e406e6491d64d60c8d8fcdbf9e20c7e6f6edb3949a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "warnLevel", value) # pyright: ignore[reportArgumentType]

# Adding a "__jsii_proxy_class__(): typing.Type" function to the interface
typing.cast(typing.Any, IExitStatusParameters).__jsii_proxy_class__ = lambda : _IExitStatusParametersProxy


@jsii.interface(jsii_type="zap-cdk.IExitStatusProps")
class IExitStatusProps(typing_extensions.Protocol):
    '''Properties for the ExitStatusConfig construct.

    :interface: IExitStatusProps
    :property: {IExitStatus} exitStatus - The exit status configuration.
    '''

    @builtins.property
    @jsii.member(jsii_name="exitStatus")
    def exit_status(self) -> IExitStatus:
        ...

    @exit_status.setter
    def exit_status(self, value: IExitStatus) -> None:
        ...


class _IExitStatusPropsProxy:
    '''Properties for the ExitStatusConfig construct.

    :interface: IExitStatusProps
    :property: {IExitStatus} exitStatus - The exit status configuration.
    '''

    __jsii_type__: typing.ClassVar[str] = "zap-cdk.IExitStatusProps"

    @builtins.property
    @jsii.member(jsii_name="exitStatus")
    def exit_status(self) -> IExitStatus:
        return typing.cast(IExitStatus, jsii.get(self, "exitStatus"))

    @exit_status.setter
    def exit_status(self, value: IExitStatus) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__92e2b1b44083fb4f2c92559e503a753a060d4ca6893cedb9280f6062fa0ce6f8)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "exitStatus", value) # pyright: ignore[reportArgumentType]

# Adding a "__jsii_proxy_class__(): typing.Type" function to the interface
typing.cast(typing.Any, IExitStatusProps).__jsii_proxy_class__ = lambda : _IExitStatusPropsProxy


@jsii.interface(jsii_type="zap-cdk.IExport")
class IExport(typing_extensions.Protocol):
    '''
    :interface:

    IExport
    Represents the configuration for an export operation.
    :property: {string} fileName - Name/path to the file.
    '''

    @builtins.property
    @jsii.member(jsii_name="fileName")
    def file_name(self) -> builtins.str:
        ...

    @file_name.setter
    def file_name(self, value: builtins.str) -> None:
        ...

    @builtins.property
    @jsii.member(jsii_name="context")
    def context(self) -> typing.Optional[builtins.str]:
        ...

    @context.setter
    def context(self, value: typing.Optional[builtins.str]) -> None:
        ...

    @builtins.property
    @jsii.member(jsii_name="source")
    def source(self) -> typing.Optional[builtins.str]:
        ...

    @source.setter
    def source(self, value: typing.Optional[builtins.str]) -> None:
        ...

    @builtins.property
    @jsii.member(jsii_name="type")
    def type(self) -> typing.Optional[builtins.str]:
        ...

    @type.setter
    def type(self, value: typing.Optional[builtins.str]) -> None:
        ...


class _IExportProxy:
    '''
    :interface:

    IExport
    Represents the configuration for an export operation.
    :property: {string} fileName - Name/path to the file.
    '''

    __jsii_type__: typing.ClassVar[str] = "zap-cdk.IExport"

    @builtins.property
    @jsii.member(jsii_name="fileName")
    def file_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "fileName"))

    @file_name.setter
    def file_name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e1ba0bd9790eb1b1123f62c4e4684c85cdcf5b946aadf0fe3fb91b561663af8b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "fileName", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="context")
    def context(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "context"))

    @context.setter
    def context(self, value: typing.Optional[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d56305663b998d35c90046c04a605ea814cfb0ce93e463aecd8092eece82fc1e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "context", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="source")
    def source(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "source"))

    @source.setter
    def source(self, value: typing.Optional[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__389d98055c374eb4e752f7da5bb13d0f24e0a2c92e8251345a488b2ec6473203)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "source", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="type")
    def type(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "type"))

    @type.setter
    def type(self, value: typing.Optional[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ea261aec475e2fcbd99d53bb462d7d06fc27e977715193cbb8e7cf98a471650e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "type", value) # pyright: ignore[reportArgumentType]

# Adding a "__jsii_proxy_class__(): typing.Type" function to the interface
typing.cast(typing.Any, IExport).__jsii_proxy_class__ = lambda : _IExportProxy


@jsii.interface(jsii_type="zap-cdk.IExportProps")
class IExportProps(typing_extensions.Protocol):
    '''Properties for the ExportConfig construct.

    :interface: IExportProps
    :property: {IExport} export - The export configuration.
    '''

    @builtins.property
    @jsii.member(jsii_name="export")
    def export(self) -> IExport:
        ...

    @export.setter
    def export(self, value: IExport) -> None:
        ...


class _IExportPropsProxy:
    '''Properties for the ExportConfig construct.

    :interface: IExportProps
    :property: {IExport} export - The export configuration.
    '''

    __jsii_type__: typing.ClassVar[str] = "zap-cdk.IExportProps"

    @builtins.property
    @jsii.member(jsii_name="export")
    def export(self) -> IExport:
        return typing.cast(IExport, jsii.get(self, "export"))

    @export.setter
    def export(self, value: IExport) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c3313ff41c4c13212c9596a19ca33e2c68edb3e8ffb6015bf1f569c0d59100bd)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "export", value) # pyright: ignore[reportArgumentType]

# Adding a "__jsii_proxy_class__(): typing.Type" function to the interface
typing.cast(typing.Any, IExportProps).__jsii_proxy_class__ = lambda : _IExportPropsProxy


@jsii.interface(jsii_type="zap-cdk.IGraphQL")
class IGraphQL(typing_extensions.Protocol):
    '''
    :interface:

    IGraphQL
    Represents the configuration for a GraphQL operation.
    :property: {RequestMethod} [requestMethod] - The request method, default: post_json.
    '''

    @builtins.property
    @jsii.member(jsii_name="argsType")
    def args_type(self) -> typing.Optional[builtins.str]:
        ...

    @args_type.setter
    def args_type(self, value: typing.Optional[builtins.str]) -> None:
        ...

    @builtins.property
    @jsii.member(jsii_name="endpoint")
    def endpoint(self) -> typing.Optional[builtins.str]:
        ...

    @endpoint.setter
    def endpoint(self, value: typing.Optional[builtins.str]) -> None:
        ...

    @builtins.property
    @jsii.member(jsii_name="lenientMaxQueryDepthEnabled")
    def lenient_max_query_depth_enabled(self) -> typing.Optional[builtins.bool]:
        ...

    @lenient_max_query_depth_enabled.setter
    def lenient_max_query_depth_enabled(
        self,
        value: typing.Optional[builtins.bool],
    ) -> None:
        ...

    @builtins.property
    @jsii.member(jsii_name="maxAdditionalQueryDepth")
    def max_additional_query_depth(self) -> typing.Optional[jsii.Number]:
        ...

    @max_additional_query_depth.setter
    def max_additional_query_depth(self, value: typing.Optional[jsii.Number]) -> None:
        ...

    @builtins.property
    @jsii.member(jsii_name="maxArgsDepth")
    def max_args_depth(self) -> typing.Optional[jsii.Number]:
        ...

    @max_args_depth.setter
    def max_args_depth(self, value: typing.Optional[jsii.Number]) -> None:
        ...

    @builtins.property
    @jsii.member(jsii_name="maxQueryDepth")
    def max_query_depth(self) -> typing.Optional[jsii.Number]:
        ...

    @max_query_depth.setter
    def max_query_depth(self, value: typing.Optional[jsii.Number]) -> None:
        ...

    @builtins.property
    @jsii.member(jsii_name="optionalArgsEnabled")
    def optional_args_enabled(self) -> typing.Optional[builtins.bool]:
        ...

    @optional_args_enabled.setter
    def optional_args_enabled(self, value: typing.Optional[builtins.bool]) -> None:
        ...

    @builtins.property
    @jsii.member(jsii_name="queryGenEnabled")
    def query_gen_enabled(self) -> typing.Optional[builtins.bool]:
        ...

    @query_gen_enabled.setter
    def query_gen_enabled(self, value: typing.Optional[builtins.bool]) -> None:
        ...

    @builtins.property
    @jsii.member(jsii_name="querySplitType")
    def query_split_type(self) -> typing.Optional[builtins.str]:
        ...

    @query_split_type.setter
    def query_split_type(self, value: typing.Optional[builtins.str]) -> None:
        ...

    @builtins.property
    @jsii.member(jsii_name="requestMethod")
    def request_method(self) -> typing.Optional[builtins.str]:
        ...

    @request_method.setter
    def request_method(self, value: typing.Optional[builtins.str]) -> None:
        ...

    @builtins.property
    @jsii.member(jsii_name="schemaFile")
    def schema_file(self) -> typing.Optional[builtins.str]:
        ...

    @schema_file.setter
    def schema_file(self, value: typing.Optional[builtins.str]) -> None:
        ...

    @builtins.property
    @jsii.member(jsii_name="schemaUrl")
    def schema_url(self) -> typing.Optional[builtins.str]:
        ...

    @schema_url.setter
    def schema_url(self, value: typing.Optional[builtins.str]) -> None:
        ...


class _IGraphQLProxy:
    '''
    :interface:

    IGraphQL
    Represents the configuration for a GraphQL operation.
    :property: {RequestMethod} [requestMethod] - The request method, default: post_json.
    '''

    __jsii_type__: typing.ClassVar[str] = "zap-cdk.IGraphQL"

    @builtins.property
    @jsii.member(jsii_name="argsType")
    def args_type(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "argsType"))

    @args_type.setter
    def args_type(self, value: typing.Optional[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f546703e5f999e599c11077e5604392fcc7630a9cc29ed3c7ee8b25a00321401)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "argsType", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="endpoint")
    def endpoint(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "endpoint"))

    @endpoint.setter
    def endpoint(self, value: typing.Optional[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5b2996d4ddccdd31f600e3e1d466a167e30ef94f65a318320fe12ab9b70ea522)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "endpoint", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="lenientMaxQueryDepthEnabled")
    def lenient_max_query_depth_enabled(self) -> typing.Optional[builtins.bool]:
        return typing.cast(typing.Optional[builtins.bool], jsii.get(self, "lenientMaxQueryDepthEnabled"))

    @lenient_max_query_depth_enabled.setter
    def lenient_max_query_depth_enabled(
        self,
        value: typing.Optional[builtins.bool],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6051882e6343d3b88e73b7069132bb64bb0d9f43e063ee6e5776bbf44a3cdafb)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "lenientMaxQueryDepthEnabled", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="maxAdditionalQueryDepth")
    def max_additional_query_depth(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "maxAdditionalQueryDepth"))

    @max_additional_query_depth.setter
    def max_additional_query_depth(self, value: typing.Optional[jsii.Number]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__097cb58176803755d10c159391b49526f8cee6e5b03efd69058d6e8dd0a60ef9)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "maxAdditionalQueryDepth", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="maxArgsDepth")
    def max_args_depth(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "maxArgsDepth"))

    @max_args_depth.setter
    def max_args_depth(self, value: typing.Optional[jsii.Number]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2af74b2b502c05a23e62ee22433aab1a3e0638bc8168fb721b11701dba367f31)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "maxArgsDepth", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="maxQueryDepth")
    def max_query_depth(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "maxQueryDepth"))

    @max_query_depth.setter
    def max_query_depth(self, value: typing.Optional[jsii.Number]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__10884ac90963c74694a1bd8df72cb97ebea47922d020ddccc034758439325e94)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "maxQueryDepth", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="optionalArgsEnabled")
    def optional_args_enabled(self) -> typing.Optional[builtins.bool]:
        return typing.cast(typing.Optional[builtins.bool], jsii.get(self, "optionalArgsEnabled"))

    @optional_args_enabled.setter
    def optional_args_enabled(self, value: typing.Optional[builtins.bool]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b82cb9b1a14b8e1e544d3ded43a23c031039999545d956908dd1308a3bc7f1dd)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "optionalArgsEnabled", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="queryGenEnabled")
    def query_gen_enabled(self) -> typing.Optional[builtins.bool]:
        return typing.cast(typing.Optional[builtins.bool], jsii.get(self, "queryGenEnabled"))

    @query_gen_enabled.setter
    def query_gen_enabled(self, value: typing.Optional[builtins.bool]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1a138ee19fbff7313e7e4b96824a803d62cee0864a2abaf1356fdfb5aee99858)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "queryGenEnabled", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="querySplitType")
    def query_split_type(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "querySplitType"))

    @query_split_type.setter
    def query_split_type(self, value: typing.Optional[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__bfdcd83e404c6329f7e6bd5fa3639d2c9561575224f51d72c92b079e17f078a2)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "querySplitType", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="requestMethod")
    def request_method(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "requestMethod"))

    @request_method.setter
    def request_method(self, value: typing.Optional[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__00e26e50d2e00ee16dd4154d736b9621ae92eb413357dd36b9466ef6c5018253)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "requestMethod", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="schemaFile")
    def schema_file(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "schemaFile"))

    @schema_file.setter
    def schema_file(self, value: typing.Optional[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f4a7ee15489a88afc9a810f46452a46865fc4fe74bd744ec34e36cdfbb9da336)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "schemaFile", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="schemaUrl")
    def schema_url(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "schemaUrl"))

    @schema_url.setter
    def schema_url(self, value: typing.Optional[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0b88d8e49dc0009ead5ff29775778ac3fe73f2402fefbafae1493a781dd54656)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "schemaUrl", value) # pyright: ignore[reportArgumentType]

# Adding a "__jsii_proxy_class__(): typing.Type" function to the interface
typing.cast(typing.Any, IGraphQL).__jsii_proxy_class__ = lambda : _IGraphQLProxy


@jsii.interface(jsii_type="zap-cdk.IGraphQLProps")
class IGraphQLProps(typing_extensions.Protocol):
    '''Properties for the GraphQLConfig construct.

    :interface: IGraphQLProps
    :property: {IGraphQL} graphql - The GraphQL configuration.
    '''

    @builtins.property
    @jsii.member(jsii_name="graphql")
    def graphql(self) -> IGraphQL:
        ...

    @graphql.setter
    def graphql(self, value: IGraphQL) -> None:
        ...


class _IGraphQLPropsProxy:
    '''Properties for the GraphQLConfig construct.

    :interface: IGraphQLProps
    :property: {IGraphQL} graphql - The GraphQL configuration.
    '''

    __jsii_type__: typing.ClassVar[str] = "zap-cdk.IGraphQLProps"

    @builtins.property
    @jsii.member(jsii_name="graphql")
    def graphql(self) -> IGraphQL:
        return typing.cast(IGraphQL, jsii.get(self, "graphql"))

    @graphql.setter
    def graphql(self, value: IGraphQL) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7ab732d41a4014a4ebf2b3536b8fde50ea26b4eda8efd4f576435923e4d416d9)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "graphql", value) # pyright: ignore[reportArgumentType]

# Adding a "__jsii_proxy_class__(): typing.Type" function to the interface
typing.cast(typing.Any, IGraphQLProps).__jsii_proxy_class__ = lambda : _IGraphQLPropsProxy


@jsii.interface(jsii_type="zap-cdk.IHttpHeaders")
class IHttpHeaders(typing_extensions.Protocol):
    '''Configuration for HTTP header scanning.

    :interface: IHttpHeaders
    :property: {boolean} [allRequests] - If set, then the headers of requests that do not include any parameters will be scanned. Default: false.
    '''

    @builtins.property
    @jsii.member(jsii_name="allRequests")
    def all_requests(self) -> typing.Optional[builtins.bool]:
        '''If headers of requests without parameters should be scanned.

        Default: false
        '''
        ...

    @all_requests.setter
    def all_requests(self, value: typing.Optional[builtins.bool]) -> None:
        ...

    @builtins.property
    @jsii.member(jsii_name="enabled")
    def enabled(self) -> typing.Optional[builtins.bool]:
        '''If HTTP header scanning should be enabled.

        Default: false
        '''
        ...

    @enabled.setter
    def enabled(self, value: typing.Optional[builtins.bool]) -> None:
        ...


class _IHttpHeadersProxy:
    '''Configuration for HTTP header scanning.

    :interface: IHttpHeaders
    :property: {boolean} [allRequests] - If set, then the headers of requests that do not include any parameters will be scanned. Default: false.
    '''

    __jsii_type__: typing.ClassVar[str] = "zap-cdk.IHttpHeaders"

    @builtins.property
    @jsii.member(jsii_name="allRequests")
    def all_requests(self) -> typing.Optional[builtins.bool]:
        '''If headers of requests without parameters should be scanned.

        Default: false
        '''
        return typing.cast(typing.Optional[builtins.bool], jsii.get(self, "allRequests"))

    @all_requests.setter
    def all_requests(self, value: typing.Optional[builtins.bool]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7fca46aafc15c700d7acbb4326547575847dfc4bb2c1b5778430c8fe92273082)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "allRequests", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="enabled")
    def enabled(self) -> typing.Optional[builtins.bool]:
        '''If HTTP header scanning should be enabled.

        Default: false
        '''
        return typing.cast(typing.Optional[builtins.bool], jsii.get(self, "enabled"))

    @enabled.setter
    def enabled(self, value: typing.Optional[builtins.bool]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d8530865f32c15fdece4cc15153feed530efab483cfea09fc68d8f29d961b482)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "enabled", value) # pyright: ignore[reportArgumentType]

# Adding a "__jsii_proxy_class__(): typing.Type" function to the interface
typing.cast(typing.Any, IHttpHeaders).__jsii_proxy_class__ = lambda : _IHttpHeadersProxy


@jsii.interface(jsii_type="zap-cdk.IImport")
class IImport(typing_extensions.Protocol):
    '''
    :interface:

    IImport
    Represents the configuration for an import operation.
    :property: {string} fileName - Name of the file containing the data.
    '''

    @builtins.property
    @jsii.member(jsii_name="fileName")
    def file_name(self) -> builtins.str:
        ...

    @file_name.setter
    def file_name(self, value: builtins.str) -> None:
        ...

    @builtins.property
    @jsii.member(jsii_name="type")
    def type(self) -> builtins.str:
        ...

    @type.setter
    def type(self, value: builtins.str) -> None:
        ...


class _IImportProxy:
    '''
    :interface:

    IImport
    Represents the configuration for an import operation.
    :property: {string} fileName - Name of the file containing the data.
    '''

    __jsii_type__: typing.ClassVar[str] = "zap-cdk.IImport"

    @builtins.property
    @jsii.member(jsii_name="fileName")
    def file_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "fileName"))

    @file_name.setter
    def file_name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__41d8c525484070a21172df6d02d0d77487978007ceac6caee46423bbdaabe225)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "fileName", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="type")
    def type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "type"))

    @type.setter
    def type(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c862b6963f762b19a6fe3bc890d7c0c9a27e5d7dd00e4ffa9261728025b11503)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "type", value) # pyright: ignore[reportArgumentType]

# Adding a "__jsii_proxy_class__(): typing.Type" function to the interface
typing.cast(typing.Any, IImport).__jsii_proxy_class__ = lambda : _IImportProxy


@jsii.interface(jsii_type="zap-cdk.IImportProps")
class IImportProps(typing_extensions.Protocol):
    '''Properties for the ImportConfig construct.

    :interface: IImportProps
    :property: {IImport} import - The import configuration.
    '''

    @builtins.property
    @jsii.member(jsii_name="import")
    def import_(self) -> IImport:
        ...

    @import_.setter
    def import_(self, value: IImport) -> None:
        ...


class _IImportPropsProxy:
    '''Properties for the ImportConfig construct.

    :interface: IImportProps
    :property: {IImport} import - The import configuration.
    '''

    __jsii_type__: typing.ClassVar[str] = "zap-cdk.IImportProps"

    @builtins.property
    @jsii.member(jsii_name="import")
    def import_(self) -> IImport:
        return typing.cast(IImport, jsii.get(self, "import"))

    @import_.setter
    def import_(self, value: IImport) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__723e53c1b29783e36b3dfaa392426555f05abcdfa1a597fba4975959681abca1)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "import", value) # pyright: ignore[reportArgumentType]

# Adding a "__jsii_proxy_class__(): typing.Type" function to the interface
typing.cast(typing.Any, IImportProps).__jsii_proxy_class__ = lambda : _IImportPropsProxy


@jsii.interface(jsii_type="zap-cdk.IInputVectors")
class IInputVectors(typing_extensions.Protocol):
    '''Represents the configuration for input vectors used in an active scan.

    :interface:

    IInputVectors
    Represents the configuration for input vectors used in an active scan.
    :property: {boolean} [scripts] - If Input Vector scripts should be used. Default: true.
    '''

    @builtins.property
    @jsii.member(jsii_name="cookieData")
    def cookie_data(self) -> ICookieData:
        '''Configuration for cookie data scanning.'''
        ...

    @cookie_data.setter
    def cookie_data(self, value: ICookieData) -> None:
        ...

    @builtins.property
    @jsii.member(jsii_name="httpHeaders")
    def http_headers(self) -> IHttpHeaders:
        '''Configuration for HTTP header scanning.'''
        ...

    @http_headers.setter
    def http_headers(self, value: IHttpHeaders) -> None:
        ...

    @builtins.property
    @jsii.member(jsii_name="postData")
    def post_data(self) -> "IPostData":
        '''Configuration for POST data scanning.'''
        ...

    @post_data.setter
    def post_data(self, value: "IPostData") -> None:
        ...

    @builtins.property
    @jsii.member(jsii_name="urlQueryStringAndDataDrivenNodes")
    def url_query_string_and_data_driven_nodes(
        self,
    ) -> "IUrlQueryStringAndDataDrivenNodes":
        '''Configuration for query parameters and data-driven nodes.'''
        ...

    @url_query_string_and_data_driven_nodes.setter
    def url_query_string_and_data_driven_nodes(
        self,
        value: "IUrlQueryStringAndDataDrivenNodes",
    ) -> None:
        ...

    @builtins.property
    @jsii.member(jsii_name="scripts")
    def scripts(self) -> typing.Optional[builtins.bool]:
        '''If Input Vector scripts should be used.

        Default: true
        '''
        ...

    @scripts.setter
    def scripts(self, value: typing.Optional[builtins.bool]) -> None:
        ...

    @builtins.property
    @jsii.member(jsii_name="urlPath")
    def url_path(self) -> typing.Optional[builtins.bool]:
        '''If URL path segments should be scanned.

        Default: false
        '''
        ...

    @url_path.setter
    def url_path(self, value: typing.Optional[builtins.bool]) -> None:
        ...


class _IInputVectorsProxy:
    '''Represents the configuration for input vectors used in an active scan.

    :interface:

    IInputVectors
    Represents the configuration for input vectors used in an active scan.
    :property: {boolean} [scripts] - If Input Vector scripts should be used. Default: true.
    '''

    __jsii_type__: typing.ClassVar[str] = "zap-cdk.IInputVectors"

    @builtins.property
    @jsii.member(jsii_name="cookieData")
    def cookie_data(self) -> ICookieData:
        '''Configuration for cookie data scanning.'''
        return typing.cast(ICookieData, jsii.get(self, "cookieData"))

    @cookie_data.setter
    def cookie_data(self, value: ICookieData) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__17418a764680da2e48bc5b313118b2d5839651224141b6739e3593f0c51190f8)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "cookieData", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="httpHeaders")
    def http_headers(self) -> IHttpHeaders:
        '''Configuration for HTTP header scanning.'''
        return typing.cast(IHttpHeaders, jsii.get(self, "httpHeaders"))

    @http_headers.setter
    def http_headers(self, value: IHttpHeaders) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__bc69d886995785733af7845e54d6cb04ae20349126a576af8b77d7d1a8728484)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "httpHeaders", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="postData")
    def post_data(self) -> "IPostData":
        '''Configuration for POST data scanning.'''
        return typing.cast("IPostData", jsii.get(self, "postData"))

    @post_data.setter
    def post_data(self, value: "IPostData") -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ab5fcc033eb8e0327ccf88a87b022bff1f81f9fa75ccf2f3fcdab085b0e6f107)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "postData", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="urlQueryStringAndDataDrivenNodes")
    def url_query_string_and_data_driven_nodes(
        self,
    ) -> "IUrlQueryStringAndDataDrivenNodes":
        '''Configuration for query parameters and data-driven nodes.'''
        return typing.cast("IUrlQueryStringAndDataDrivenNodes", jsii.get(self, "urlQueryStringAndDataDrivenNodes"))

    @url_query_string_and_data_driven_nodes.setter
    def url_query_string_and_data_driven_nodes(
        self,
        value: "IUrlQueryStringAndDataDrivenNodes",
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c750167ffad4db33321d6da9fef8037c35a6b4e6b6c1a9a568cad910e5a3c85e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "urlQueryStringAndDataDrivenNodes", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="scripts")
    def scripts(self) -> typing.Optional[builtins.bool]:
        '''If Input Vector scripts should be used.

        Default: true
        '''
        return typing.cast(typing.Optional[builtins.bool], jsii.get(self, "scripts"))

    @scripts.setter
    def scripts(self, value: typing.Optional[builtins.bool]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4be0d68083a100641013e58581bad97f36e1461b08c604a297132a28b071cd6c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "scripts", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="urlPath")
    def url_path(self) -> typing.Optional[builtins.bool]:
        '''If URL path segments should be scanned.

        Default: false
        '''
        return typing.cast(typing.Optional[builtins.bool], jsii.get(self, "urlPath"))

    @url_path.setter
    def url_path(self, value: typing.Optional[builtins.bool]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__26f700cae4b9db1932b58696fb4cc0ed82f3324ef912a086539b6d682ca92d76)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "urlPath", value) # pyright: ignore[reportArgumentType]

# Adding a "__jsii_proxy_class__(): typing.Type" function to the interface
typing.cast(typing.Any, IInputVectors).__jsii_proxy_class__ = lambda : _IInputVectorsProxy


@jsii.interface(jsii_type="zap-cdk.IJsonPostData")
class IJsonPostData(typing_extensions.Protocol):
    '''Configuration for JSON body scanning in POST data.

    :interface: IJsonPostData
    :property: {boolean} [scanNullValues] - If null values should be scanned. Default: false.
    '''

    @builtins.property
    @jsii.member(jsii_name="enabled")
    def enabled(self) -> typing.Optional[builtins.bool]:
        '''If JSON scanning should be enabled.

        Default: true
        '''
        ...

    @enabled.setter
    def enabled(self, value: typing.Optional[builtins.bool]) -> None:
        ...

    @builtins.property
    @jsii.member(jsii_name="scanNullValues")
    def scan_null_values(self) -> typing.Optional[builtins.bool]:
        '''If null values should be scanned.

        Default: false
        '''
        ...

    @scan_null_values.setter
    def scan_null_values(self, value: typing.Optional[builtins.bool]) -> None:
        ...


class _IJsonPostDataProxy:
    '''Configuration for JSON body scanning in POST data.

    :interface: IJsonPostData
    :property: {boolean} [scanNullValues] - If null values should be scanned. Default: false.
    '''

    __jsii_type__: typing.ClassVar[str] = "zap-cdk.IJsonPostData"

    @builtins.property
    @jsii.member(jsii_name="enabled")
    def enabled(self) -> typing.Optional[builtins.bool]:
        '''If JSON scanning should be enabled.

        Default: true
        '''
        return typing.cast(typing.Optional[builtins.bool], jsii.get(self, "enabled"))

    @enabled.setter
    def enabled(self, value: typing.Optional[builtins.bool]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6885c313783edbf0b62223765b028da7ba92b131f910243bcb19884876a694ee)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "enabled", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="scanNullValues")
    def scan_null_values(self) -> typing.Optional[builtins.bool]:
        '''If null values should be scanned.

        Default: false
        '''
        return typing.cast(typing.Optional[builtins.bool], jsii.get(self, "scanNullValues"))

    @scan_null_values.setter
    def scan_null_values(self, value: typing.Optional[builtins.bool]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__74b922f739033736b68687a9d06b72b1fb5333f7dc132f826477398a72253578)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "scanNullValues", value) # pyright: ignore[reportArgumentType]

# Adding a "__jsii_proxy_class__(): typing.Type" function to the interface
typing.cast(typing.Any, IJsonPostData).__jsii_proxy_class__ = lambda : _IJsonPostDataProxy


@jsii.interface(jsii_type="zap-cdk.IMonitorTest")
class IMonitorTest(typing_extensions.Protocol):
    '''Interface for monitor tests.

    Example YAML representation::

       - name: 'test one'                      # Name of the test, optional
         type: monitor                         # Specifies that the test is of type 'monitor'
         statistic: 'stats.addon.something'    # Name of an integer / long statistic
         site:                                 # Name of the site for site specific tests, supports vars
         threshold: 10                         # The threshold at which a statistic fails
         onFail: 'info'                        # String: One of 'warn', 'error', 'info', mandatory

    :interface: IMonitorTest
    :property: {OnFailType} onFail - Action to take on failure, mandatory.
    '''

    @builtins.property
    @jsii.member(jsii_name="onFail")
    def on_fail(self) -> builtins.str:
        ...

    @on_fail.setter
    def on_fail(self, value: builtins.str) -> None:
        ...

    @builtins.property
    @jsii.member(jsii_name="statistic")
    def statistic(self) -> builtins.str:
        ...

    @statistic.setter
    def statistic(self, value: builtins.str) -> None:
        ...

    @builtins.property
    @jsii.member(jsii_name="type")
    def type(self) -> builtins.str:
        ...

    @type.setter
    def type(self, value: builtins.str) -> None:
        ...

    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> typing.Optional[builtins.str]:
        ...

    @name.setter
    def name(self, value: typing.Optional[builtins.str]) -> None:
        ...

    @builtins.property
    @jsii.member(jsii_name="site")
    def site(self) -> typing.Optional[builtins.str]:
        ...

    @site.setter
    def site(self, value: typing.Optional[builtins.str]) -> None:
        ...


class _IMonitorTestProxy:
    '''Interface for monitor tests.

    Example YAML representation::

       - name: 'test one'                      # Name of the test, optional
         type: monitor                         # Specifies that the test is of type 'monitor'
         statistic: 'stats.addon.something'    # Name of an integer / long statistic
         site:                                 # Name of the site for site specific tests, supports vars
         threshold: 10                         # The threshold at which a statistic fails
         onFail: 'info'                        # String: One of 'warn', 'error', 'info', mandatory

    :interface: IMonitorTest
    :property: {OnFailType} onFail - Action to take on failure, mandatory.
    '''

    __jsii_type__: typing.ClassVar[str] = "zap-cdk.IMonitorTest"

    @builtins.property
    @jsii.member(jsii_name="onFail")
    def on_fail(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "onFail"))

    @on_fail.setter
    def on_fail(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1e90dcd0013d5588f99ac520954e039471348003e11cb9c2a4e06eee55307e19)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "onFail", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="statistic")
    def statistic(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "statistic"))

    @statistic.setter
    def statistic(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__81e9fa0641c722e9148d58a4106da62a0ef57ceac5925de5968829ef1c581230)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "statistic", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="type")
    def type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "type"))

    @type.setter
    def type(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e98da75077d9f5679c779ef4c5335f80c80a42de1bb7b4aa4ee024621f3f958a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "type", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "name"))

    @name.setter
    def name(self, value: typing.Optional[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e8059a972b5c2f7322c2e810a7d18fb3d381d17b5da78c962807506a9bf55a50)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "name", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="site")
    def site(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "site"))

    @site.setter
    def site(self, value: typing.Optional[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__929b587697cb66c5b2685f5644deb8f6eaf2c9dae992dfc2c812fa2dadfa3035)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "site", value) # pyright: ignore[reportArgumentType]

# Adding a "__jsii_proxy_class__(): typing.Type" function to the interface
typing.cast(typing.Any, IMonitorTest).__jsii_proxy_class__ = lambda : _IMonitorTestProxy


@jsii.interface(jsii_type="zap-cdk.INewType")
class INewType(typing_extensions.Protocol):
    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        ...

    @name.setter
    def name(self, value: builtins.str) -> None:
        ...

    @builtins.property
    @jsii.member(jsii_name="parameters")
    def parameters(self) -> typing.Optional[typing.Mapping[builtins.str, typing.Any]]:
        ...

    @parameters.setter
    def parameters(
        self,
        value: typing.Optional[typing.Mapping[builtins.str, typing.Any]],
    ) -> None:
        ...


class _INewTypeProxy:
    __jsii_type__: typing.ClassVar[str] = "zap-cdk.INewType"

    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4995495535ec29d36664942cd573d24eeb8b3206acba02f42de57ce1a67b277a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "name", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="parameters")
    def parameters(self) -> typing.Optional[typing.Mapping[builtins.str, typing.Any]]:
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, typing.Any]], jsii.get(self, "parameters"))

    @parameters.setter
    def parameters(
        self,
        value: typing.Optional[typing.Mapping[builtins.str, typing.Any]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0851b1bee43e5de21b90c69ee46cb5f0e011739bf509e537874792f7a699dfa1)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "parameters", value) # pyright: ignore[reportArgumentType]

# Adding a "__jsii_proxy_class__(): typing.Type" function to the interface
typing.cast(typing.Any, INewType).__jsii_proxy_class__ = lambda : _INewTypeProxy


@jsii.interface(jsii_type="zap-cdk.IOpenAPI")
class IOpenAPI(typing_extensions.Protocol):
    '''
    :interface:

    IOpenAPI
    Represents the configuration for importing an OpenAPI definition.
    :property: {string} [targetUrl] - URL which overrides the target defined in the definition, default: null.
    '''

    @builtins.property
    @jsii.member(jsii_name="apiFile")
    def api_file(self) -> typing.Optional[builtins.str]:
        ...

    @api_file.setter
    def api_file(self, value: typing.Optional[builtins.str]) -> None:
        ...

    @builtins.property
    @jsii.member(jsii_name="apiUrl")
    def api_url(self) -> typing.Optional[builtins.str]:
        ...

    @api_url.setter
    def api_url(self, value: typing.Optional[builtins.str]) -> None:
        ...

    @builtins.property
    @jsii.member(jsii_name="context")
    def context(self) -> typing.Optional[builtins.str]:
        ...

    @context.setter
    def context(self, value: typing.Optional[builtins.str]) -> None:
        ...

    @builtins.property
    @jsii.member(jsii_name="targetUrl")
    def target_url(self) -> typing.Optional[builtins.str]:
        ...

    @target_url.setter
    def target_url(self, value: typing.Optional[builtins.str]) -> None:
        ...

    @builtins.property
    @jsii.member(jsii_name="user")
    def user(self) -> typing.Optional[builtins.str]:
        ...

    @user.setter
    def user(self, value: typing.Optional[builtins.str]) -> None:
        ...


class _IOpenAPIProxy:
    '''
    :interface:

    IOpenAPI
    Represents the configuration for importing an OpenAPI definition.
    :property: {string} [targetUrl] - URL which overrides the target defined in the definition, default: null.
    '''

    __jsii_type__: typing.ClassVar[str] = "zap-cdk.IOpenAPI"

    @builtins.property
    @jsii.member(jsii_name="apiFile")
    def api_file(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "apiFile"))

    @api_file.setter
    def api_file(self, value: typing.Optional[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__172ea9eebee1d8c71c05ecc46518f4a4bdcb58db599bfa3f2b7ac3306f5fd63e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "apiFile", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="apiUrl")
    def api_url(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "apiUrl"))

    @api_url.setter
    def api_url(self, value: typing.Optional[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__286e3b452507280491527c16822e633980d5bb627a13e6496e147dc517efd14a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "apiUrl", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="context")
    def context(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "context"))

    @context.setter
    def context(self, value: typing.Optional[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8a3a9c00b6614c10509322afdf05008324a07c670276714f934c54a3601134f3)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "context", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="targetUrl")
    def target_url(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "targetUrl"))

    @target_url.setter
    def target_url(self, value: typing.Optional[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f2e129f6faa7ce72ee73b6c7d7e8456c9b16bd88dbf41989b01714efa7b6ef17)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "targetUrl", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="user")
    def user(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "user"))

    @user.setter
    def user(self, value: typing.Optional[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1bd8f749a7d7a8f794270c8082aa6bd0e6b24b5be171b80637aba6f6314fd1f9)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "user", value) # pyright: ignore[reportArgumentType]

# Adding a "__jsii_proxy_class__(): typing.Type" function to the interface
typing.cast(typing.Any, IOpenAPI).__jsii_proxy_class__ = lambda : _IOpenAPIProxy


@jsii.interface(jsii_type="zap-cdk.IOpenAPIProps")
class IOpenAPIProps(typing_extensions.Protocol):
    '''Properties for the OpenAPIConfig construct.

    :interface: IOpenAPIProps
    :property: {IOpenAPI} openapi - The OpenAPI configuration.
    '''

    @builtins.property
    @jsii.member(jsii_name="openapi")
    def openapi(self) -> IOpenAPI:
        ...

    @openapi.setter
    def openapi(self, value: IOpenAPI) -> None:
        ...


class _IOpenAPIPropsProxy:
    '''Properties for the OpenAPIConfig construct.

    :interface: IOpenAPIProps
    :property: {IOpenAPI} openapi - The OpenAPI configuration.
    '''

    __jsii_type__: typing.ClassVar[str] = "zap-cdk.IOpenAPIProps"

    @builtins.property
    @jsii.member(jsii_name="openapi")
    def openapi(self) -> IOpenAPI:
        return typing.cast(IOpenAPI, jsii.get(self, "openapi"))

    @openapi.setter
    def openapi(self, value: IOpenAPI) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a54769c95e29c3a9c61e5313b66ec57df9a9c6d46531cbd4b8be211b5f85aa53)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "openapi", value) # pyright: ignore[reportArgumentType]

# Adding a "__jsii_proxy_class__(): typing.Type" function to the interface
typing.cast(typing.Any, IOpenAPIProps).__jsii_proxy_class__ = lambda : _IOpenAPIPropsProxy


@jsii.interface(jsii_type="zap-cdk.IPassiveScanConfig")
class IPassiveScanConfig(typing_extensions.Protocol):
    '''
    :interface:

    IPassiveScanConfig
    Represents the configuration for a passive scan.
    :property: {boolean} [alwaysRun] - If set and the job is enabled, then it will run even if the plan exits early, default: false.
    '''

    @builtins.property
    @jsii.member(jsii_name="parameters")
    def parameters(self) -> "IPassiveScanParameters":
        ...

    @parameters.setter
    def parameters(self, value: "IPassiveScanParameters") -> None:
        ...

    @builtins.property
    @jsii.member(jsii_name="type")
    def type(self) -> builtins.str:
        ...

    @type.setter
    def type(self, value: builtins.str) -> None:
        ...

    @builtins.property
    @jsii.member(jsii_name="alwaysRun")
    def always_run(self) -> typing.Optional[builtins.bool]:
        ...

    @always_run.setter
    def always_run(self, value: typing.Optional[builtins.bool]) -> None:
        ...

    @builtins.property
    @jsii.member(jsii_name="enabled")
    def enabled(self) -> typing.Optional[builtins.bool]:
        ...

    @enabled.setter
    def enabled(self, value: typing.Optional[builtins.bool]) -> None:
        ...

    @builtins.property
    @jsii.member(jsii_name="rules")
    def rules(self) -> typing.Optional[typing.List["IPassiveScanRule"]]:
        ...

    @rules.setter
    def rules(self, value: typing.Optional[typing.List["IPassiveScanRule"]]) -> None:
        ...


class _IPassiveScanConfigProxy:
    '''
    :interface:

    IPassiveScanConfig
    Represents the configuration for a passive scan.
    :property: {boolean} [alwaysRun] - If set and the job is enabled, then it will run even if the plan exits early, default: false.
    '''

    __jsii_type__: typing.ClassVar[str] = "zap-cdk.IPassiveScanConfig"

    @builtins.property
    @jsii.member(jsii_name="parameters")
    def parameters(self) -> "IPassiveScanParameters":
        return typing.cast("IPassiveScanParameters", jsii.get(self, "parameters"))

    @parameters.setter
    def parameters(self, value: "IPassiveScanParameters") -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d2c5fe4c6d3f23d1ebde8fabebbccbfc1df11f4928621a9cf08c4d5c449d1110)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "parameters", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="type")
    def type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "type"))

    @type.setter
    def type(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__17b579768803db320e03e01bc18e2c4ad34a1532d3e641552db168585785612a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "type", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="alwaysRun")
    def always_run(self) -> typing.Optional[builtins.bool]:
        return typing.cast(typing.Optional[builtins.bool], jsii.get(self, "alwaysRun"))

    @always_run.setter
    def always_run(self, value: typing.Optional[builtins.bool]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__97552be6abc066d01b668b4c4598987490db97a3d808763545ad7e22401a52a0)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "alwaysRun", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="enabled")
    def enabled(self) -> typing.Optional[builtins.bool]:
        return typing.cast(typing.Optional[builtins.bool], jsii.get(self, "enabled"))

    @enabled.setter
    def enabled(self, value: typing.Optional[builtins.bool]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4167f23e223f81c02e1d4a212cb73f3a8ced92e14df99448d7e9642c67c15ee7)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "enabled", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="rules")
    def rules(self) -> typing.Optional[typing.List["IPassiveScanRule"]]:
        return typing.cast(typing.Optional[typing.List["IPassiveScanRule"]], jsii.get(self, "rules"))

    @rules.setter
    def rules(self, value: typing.Optional[typing.List["IPassiveScanRule"]]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1f02a4e62510304f69676ef1c97e2730e99c5a139ef8624e60bc0ef458aeec26)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "rules", value) # pyright: ignore[reportArgumentType]

# Adding a "__jsii_proxy_class__(): typing.Type" function to the interface
typing.cast(typing.Any, IPassiveScanConfig).__jsii_proxy_class__ = lambda : _IPassiveScanConfigProxy


@jsii.interface(jsii_type="zap-cdk.IPassiveScanConfigProps")
class IPassiveScanConfigProps(typing_extensions.Protocol):
    '''Properties for the PassiveScanConfig construct.

    :interface: IPassiveScanConfigProps
    :property: {IPassiveScanConfig} passiveScanConfig - The passive scan configuration.
    '''

    @builtins.property
    @jsii.member(jsii_name="passiveScanConfig")
    def passive_scan_config(self) -> IPassiveScanConfig:
        ...

    @passive_scan_config.setter
    def passive_scan_config(self, value: IPassiveScanConfig) -> None:
        ...


class _IPassiveScanConfigPropsProxy:
    '''Properties for the PassiveScanConfig construct.

    :interface: IPassiveScanConfigProps
    :property: {IPassiveScanConfig} passiveScanConfig - The passive scan configuration.
    '''

    __jsii_type__: typing.ClassVar[str] = "zap-cdk.IPassiveScanConfigProps"

    @builtins.property
    @jsii.member(jsii_name="passiveScanConfig")
    def passive_scan_config(self) -> IPassiveScanConfig:
        return typing.cast(IPassiveScanConfig, jsii.get(self, "passiveScanConfig"))

    @passive_scan_config.setter
    def passive_scan_config(self, value: IPassiveScanConfig) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2b75ad96c8853d34087cb3b1e56cf471ef1bdb38fad3d133648c7264d11936e2)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "passiveScanConfig", value) # pyright: ignore[reportArgumentType]

# Adding a "__jsii_proxy_class__(): typing.Type" function to the interface
typing.cast(typing.Any, IPassiveScanConfigProps).__jsii_proxy_class__ = lambda : _IPassiveScanConfigPropsProxy


@jsii.interface(jsii_type="zap-cdk.IPassiveScanParameters")
class IPassiveScanParameters(typing_extensions.Protocol):
    '''
    :interface:

    IPassiveScanParameters
    Represents the parameters for configuring a passive scan.
    :property: {boolean} [disableAllRules] - If true, then will disable all rules before applying the settings in the rules section.
    '''

    @builtins.property
    @jsii.member(jsii_name="disableAllRules")
    def disable_all_rules(self) -> typing.Optional[builtins.bool]:
        ...

    @disable_all_rules.setter
    def disable_all_rules(self, value: typing.Optional[builtins.bool]) -> None:
        ...

    @builtins.property
    @jsii.member(jsii_name="enableTags")
    def enable_tags(self) -> typing.Optional[builtins.bool]:
        ...

    @enable_tags.setter
    def enable_tags(self, value: typing.Optional[builtins.bool]) -> None:
        ...

    @builtins.property
    @jsii.member(jsii_name="maxAlertsPerRule")
    def max_alerts_per_rule(self) -> typing.Optional[jsii.Number]:
        ...

    @max_alerts_per_rule.setter
    def max_alerts_per_rule(self, value: typing.Optional[jsii.Number]) -> None:
        ...

    @builtins.property
    @jsii.member(jsii_name="maxBodySizeInBytesToScan")
    def max_body_size_in_bytes_to_scan(self) -> typing.Optional[jsii.Number]:
        ...

    @max_body_size_in_bytes_to_scan.setter
    def max_body_size_in_bytes_to_scan(
        self,
        value: typing.Optional[jsii.Number],
    ) -> None:
        ...

    @builtins.property
    @jsii.member(jsii_name="scanOnlyInScope")
    def scan_only_in_scope(self) -> typing.Optional[builtins.bool]:
        ...

    @scan_only_in_scope.setter
    def scan_only_in_scope(self, value: typing.Optional[builtins.bool]) -> None:
        ...


class _IPassiveScanParametersProxy:
    '''
    :interface:

    IPassiveScanParameters
    Represents the parameters for configuring a passive scan.
    :property: {boolean} [disableAllRules] - If true, then will disable all rules before applying the settings in the rules section.
    '''

    __jsii_type__: typing.ClassVar[str] = "zap-cdk.IPassiveScanParameters"

    @builtins.property
    @jsii.member(jsii_name="disableAllRules")
    def disable_all_rules(self) -> typing.Optional[builtins.bool]:
        return typing.cast(typing.Optional[builtins.bool], jsii.get(self, "disableAllRules"))

    @disable_all_rules.setter
    def disable_all_rules(self, value: typing.Optional[builtins.bool]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9818f1d080f3bf36dd6c9da0390e848cbda2ce35dea91b93f79191b7f772f8cd)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "disableAllRules", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="enableTags")
    def enable_tags(self) -> typing.Optional[builtins.bool]:
        return typing.cast(typing.Optional[builtins.bool], jsii.get(self, "enableTags"))

    @enable_tags.setter
    def enable_tags(self, value: typing.Optional[builtins.bool]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7e45325ba5af1d8f63e296012c7de90cf87f92c87a4579b723e22206338201a3)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "enableTags", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="maxAlertsPerRule")
    def max_alerts_per_rule(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "maxAlertsPerRule"))

    @max_alerts_per_rule.setter
    def max_alerts_per_rule(self, value: typing.Optional[jsii.Number]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__32adf47e9e22f49fe484b5ab70f25fa7047721b3d8c0df80e1a85128a85443f8)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "maxAlertsPerRule", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="maxBodySizeInBytesToScan")
    def max_body_size_in_bytes_to_scan(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "maxBodySizeInBytesToScan"))

    @max_body_size_in_bytes_to_scan.setter
    def max_body_size_in_bytes_to_scan(
        self,
        value: typing.Optional[jsii.Number],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6299f9004bee5f3d42514827672affc2efd826435d2ff46f888618bc16fe4ef8)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "maxBodySizeInBytesToScan", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="scanOnlyInScope")
    def scan_only_in_scope(self) -> typing.Optional[builtins.bool]:
        return typing.cast(typing.Optional[builtins.bool], jsii.get(self, "scanOnlyInScope"))

    @scan_only_in_scope.setter
    def scan_only_in_scope(self, value: typing.Optional[builtins.bool]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__04913a0c0bc89dc90e59f8dfb850a64a7ff28daefc267e66dabcee448a35d2d2)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "scanOnlyInScope", value) # pyright: ignore[reportArgumentType]

# Adding a "__jsii_proxy_class__(): typing.Type" function to the interface
typing.cast(typing.Any, IPassiveScanParameters).__jsii_proxy_class__ = lambda : _IPassiveScanParametersProxy


@jsii.interface(jsii_type="zap-cdk.IPassiveScanRule")
class IPassiveScanRule(typing_extensions.Protocol):
    '''
    :interface:

    IPassiveScanRule
    Represents a passive scan rule configuration.
    :property: {'Off' | 'Low' | 'Medium' | 'High'} [threshold] - The Alert Threshold for this rule, default: Medium.
    '''

    @builtins.property
    @jsii.member(jsii_name="id")
    def id(self) -> jsii.Number:
        ...

    @id.setter
    def id(self, value: jsii.Number) -> None:
        ...

    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> typing.Optional[builtins.str]:
        ...

    @name.setter
    def name(self, value: typing.Optional[builtins.str]) -> None:
        ...

    @builtins.property
    @jsii.member(jsii_name="threshold")
    def threshold(self) -> typing.Optional[builtins.str]:
        ...

    @threshold.setter
    def threshold(self, value: typing.Optional[builtins.str]) -> None:
        ...


class _IPassiveScanRuleProxy:
    '''
    :interface:

    IPassiveScanRule
    Represents a passive scan rule configuration.
    :property: {'Off' | 'Low' | 'Medium' | 'High'} [threshold] - The Alert Threshold for this rule, default: Medium.
    '''

    __jsii_type__: typing.ClassVar[str] = "zap-cdk.IPassiveScanRule"

    @builtins.property
    @jsii.member(jsii_name="id")
    def id(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "id"))

    @id.setter
    def id(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a764c2b1afe9b2476224b5a116a38f9f4bbfa4defca5a604869edcd705917a23)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "id", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "name"))

    @name.setter
    def name(self, value: typing.Optional[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8064c5fa05af72a6bbc131f9bf0477afeb2f664d34ffdd4d36db44e660e38e39)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "name", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="threshold")
    def threshold(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "threshold"))

    @threshold.setter
    def threshold(self, value: typing.Optional[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ddeea77215033ca4f5ed48b73a5207e06ec04b4318db3c1027172574534c4ce4)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "threshold", value) # pyright: ignore[reportArgumentType]

# Adding a "__jsii_proxy_class__(): typing.Type" function to the interface
typing.cast(typing.Any, IPassiveScanRule).__jsii_proxy_class__ = lambda : _IPassiveScanRuleProxy


@jsii.interface(jsii_type="zap-cdk.IPassiveScanWait")
class IPassiveScanWait(typing_extensions.Protocol):
    '''
    :interface:

    IPassiveScanWait
    Represents the configuration for waiting during a passive scan.
    :property: {number} [maxDuration] - The max time to wait for the passive scanner, default: 0 (unlimited).
    '''

    @builtins.property
    @jsii.member(jsii_name="maxDuration")
    def max_duration(self) -> typing.Optional[jsii.Number]:
        ...

    @max_duration.setter
    def max_duration(self, value: typing.Optional[jsii.Number]) -> None:
        ...


class _IPassiveScanWaitProxy:
    '''
    :interface:

    IPassiveScanWait
    Represents the configuration for waiting during a passive scan.
    :property: {number} [maxDuration] - The max time to wait for the passive scanner, default: 0 (unlimited).
    '''

    __jsii_type__: typing.ClassVar[str] = "zap-cdk.IPassiveScanWait"

    @builtins.property
    @jsii.member(jsii_name="maxDuration")
    def max_duration(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "maxDuration"))

    @max_duration.setter
    def max_duration(self, value: typing.Optional[jsii.Number]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9155e050a5451ca42bddbd8ceb0389ab4e7f43dfe5a147ec3ac05dbf0725cf8b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "maxDuration", value) # pyright: ignore[reportArgumentType]

# Adding a "__jsii_proxy_class__(): typing.Type" function to the interface
typing.cast(typing.Any, IPassiveScanWait).__jsii_proxy_class__ = lambda : _IPassiveScanWaitProxy


@jsii.interface(jsii_type="zap-cdk.IPassiveScanWaitProps")
class IPassiveScanWaitProps(typing_extensions.Protocol):
    '''Properties for the PassiveScanWaitConfig construct.

    :interface: IPassiveScanWaitProps
    :property: {IPassiveScanWait} passiveScanWait - The passive scan wait configuration.
    '''

    @builtins.property
    @jsii.member(jsii_name="passiveScanWait")
    def passive_scan_wait(self) -> IPassiveScanWait:
        ...

    @passive_scan_wait.setter
    def passive_scan_wait(self, value: IPassiveScanWait) -> None:
        ...


class _IPassiveScanWaitPropsProxy:
    '''Properties for the PassiveScanWaitConfig construct.

    :interface: IPassiveScanWaitProps
    :property: {IPassiveScanWait} passiveScanWait - The passive scan wait configuration.
    '''

    __jsii_type__: typing.ClassVar[str] = "zap-cdk.IPassiveScanWaitProps"

    @builtins.property
    @jsii.member(jsii_name="passiveScanWait")
    def passive_scan_wait(self) -> IPassiveScanWait:
        return typing.cast(IPassiveScanWait, jsii.get(self, "passiveScanWait"))

    @passive_scan_wait.setter
    def passive_scan_wait(self, value: IPassiveScanWait) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d134ef685bc8c8e0b785db134bca2abcfe2c2bad3fd72a07cea4116bc2da6e84)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "passiveScanWait", value) # pyright: ignore[reportArgumentType]

# Adding a "__jsii_proxy_class__(): typing.Type" function to the interface
typing.cast(typing.Any, IPassiveScanWaitProps).__jsii_proxy_class__ = lambda : _IPassiveScanWaitPropsProxy


@jsii.interface(jsii_type="zap-cdk.IPolicyDefinition")
class IPolicyDefinition(typing_extensions.Protocol):
    '''
    :interface:

    IPolicyDefinition
    Represents the policy definition for an active scan.
    :property: {string} [rules[].threshold] - The Alert Threshold for this rule, one of Off, Low, Medium, High, default: Medium.
    '''

    @builtins.property
    @jsii.member(jsii_name="alertTags")
    def alert_tags(self) -> typing.Optional[IAlertTags]:
        ...

    @alert_tags.setter
    def alert_tags(self, value: typing.Optional[IAlertTags]) -> None:
        ...

    @builtins.property
    @jsii.member(jsii_name="defaultStrength")
    def default_strength(self) -> typing.Optional[builtins.str]:
        ...

    @default_strength.setter
    def default_strength(self, value: typing.Optional[builtins.str]) -> None:
        ...

    @builtins.property
    @jsii.member(jsii_name="defaultThreshold")
    def default_threshold(self) -> typing.Optional[builtins.str]:
        ...

    @default_threshold.setter
    def default_threshold(self, value: typing.Optional[builtins.str]) -> None:
        ...

    @builtins.property
    @jsii.member(jsii_name="rules")
    def rules(self) -> typing.Optional[typing.List["IRules"]]:
        ...

    @rules.setter
    def rules(self, value: typing.Optional[typing.List["IRules"]]) -> None:
        ...


class _IPolicyDefinitionProxy:
    '''
    :interface:

    IPolicyDefinition
    Represents the policy definition for an active scan.
    :property: {string} [rules[].threshold] - The Alert Threshold for this rule, one of Off, Low, Medium, High, default: Medium.
    '''

    __jsii_type__: typing.ClassVar[str] = "zap-cdk.IPolicyDefinition"

    @builtins.property
    @jsii.member(jsii_name="alertTags")
    def alert_tags(self) -> typing.Optional[IAlertTags]:
        return typing.cast(typing.Optional[IAlertTags], jsii.get(self, "alertTags"))

    @alert_tags.setter
    def alert_tags(self, value: typing.Optional[IAlertTags]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9be25baff0adeb1b67aad6876177e6f01de44e44f7127d22bef9a59b33146314)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "alertTags", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="defaultStrength")
    def default_strength(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "defaultStrength"))

    @default_strength.setter
    def default_strength(self, value: typing.Optional[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6c44c27220373563d767f53fd9b2231fcfe516d54608e30089f8ece92695e6a9)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "defaultStrength", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="defaultThreshold")
    def default_threshold(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "defaultThreshold"))

    @default_threshold.setter
    def default_threshold(self, value: typing.Optional[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1d2ff09966ffa883fbab1bca76b2735f54aa226f9ea0d1396f56344e117a338a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "defaultThreshold", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="rules")
    def rules(self) -> typing.Optional[typing.List["IRules"]]:
        return typing.cast(typing.Optional[typing.List["IRules"]], jsii.get(self, "rules"))

    @rules.setter
    def rules(self, value: typing.Optional[typing.List["IRules"]]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9ad5035940e2b31f298134690caa59759a357b8d177b621877e4c1a1f0f01370)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "rules", value) # pyright: ignore[reportArgumentType]

# Adding a "__jsii_proxy_class__(): typing.Type" function to the interface
typing.cast(typing.Any, IPolicyDefinition).__jsii_proxy_class__ = lambda : _IPolicyDefinitionProxy


@jsii.interface(jsii_type="zap-cdk.IPollAdditionalHeaders")
class IPollAdditionalHeaders(typing_extensions.Protocol):
    '''
    :interface:

    IPollAdditionalHeaders
    Represents additional headers for poll request in authentication verification.
    :property: {string} value - The header value.
    '''

    @builtins.property
    @jsii.member(jsii_name="header")
    def header(self) -> builtins.str:
        ...

    @header.setter
    def header(self, value: builtins.str) -> None:
        ...

    @builtins.property
    @jsii.member(jsii_name="value")
    def value(self) -> builtins.str:
        ...

    @value.setter
    def value(self, value: builtins.str) -> None:
        ...


class _IPollAdditionalHeadersProxy:
    '''
    :interface:

    IPollAdditionalHeaders
    Represents additional headers for poll request in authentication verification.
    :property: {string} value - The header value.
    '''

    __jsii_type__: typing.ClassVar[str] = "zap-cdk.IPollAdditionalHeaders"

    @builtins.property
    @jsii.member(jsii_name="header")
    def header(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "header"))

    @header.setter
    def header(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__cfd1785421830c4609a3b89beb607465134a17609e82d6f47d053e90375fe66a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "header", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="value")
    def value(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "value"))

    @value.setter
    def value(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__57c9fde0b011c330b808f8d6f2c8d57afd59acb97e6ecb2fccec32c0afa5508c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "value", value) # pyright: ignore[reportArgumentType]

# Adding a "__jsii_proxy_class__(): typing.Type" function to the interface
typing.cast(typing.Any, IPollAdditionalHeaders).__jsii_proxy_class__ = lambda : _IPollAdditionalHeadersProxy


@jsii.interface(jsii_type="zap-cdk.IPostData")
class IPostData(typing_extensions.Protocol):
    '''Configuration for POST data scanning.

    :interface: IPostData
    :property: {boolean} [directWebRemoting] - If DWR scanning should be enabled. Default: false.
    '''

    @builtins.property
    @jsii.member(jsii_name="json")
    def json(self) -> IJsonPostData:
        '''Configuration for JSON bodies.'''
        ...

    @json.setter
    def json(self, value: IJsonPostData) -> None:
        ...

    @builtins.property
    @jsii.member(jsii_name="directWebRemoting")
    def direct_web_remoting(self) -> typing.Optional[builtins.bool]:
        '''If DWR scanning should be enabled.

        Default: false
        '''
        ...

    @direct_web_remoting.setter
    def direct_web_remoting(self, value: typing.Optional[builtins.bool]) -> None:
        ...

    @builtins.property
    @jsii.member(jsii_name="enabled")
    def enabled(self) -> typing.Optional[builtins.bool]:
        '''If POST data scanning is enabled.

        Default: true
        '''
        ...

    @enabled.setter
    def enabled(self, value: typing.Optional[builtins.bool]) -> None:
        ...

    @builtins.property
    @jsii.member(jsii_name="googleWebToolkit")
    def google_web_toolkit(self) -> typing.Optional[builtins.bool]:
        '''If GWT scanning should be enabled.

        Default: false
        '''
        ...

    @google_web_toolkit.setter
    def google_web_toolkit(self, value: typing.Optional[builtins.bool]) -> None:
        ...

    @builtins.property
    @jsii.member(jsii_name="multiPartFormData")
    def multi_part_form_data(self) -> typing.Optional[builtins.bool]:
        '''If multipart form data bodies should be scanned.

        Default: true
        '''
        ...

    @multi_part_form_data.setter
    def multi_part_form_data(self, value: typing.Optional[builtins.bool]) -> None:
        ...

    @builtins.property
    @jsii.member(jsii_name="xml")
    def xml(self) -> typing.Optional[builtins.bool]:
        '''If XML bodies should be scanned.

        Default: true
        '''
        ...

    @xml.setter
    def xml(self, value: typing.Optional[builtins.bool]) -> None:
        ...


class _IPostDataProxy:
    '''Configuration for POST data scanning.

    :interface: IPostData
    :property: {boolean} [directWebRemoting] - If DWR scanning should be enabled. Default: false.
    '''

    __jsii_type__: typing.ClassVar[str] = "zap-cdk.IPostData"

    @builtins.property
    @jsii.member(jsii_name="json")
    def json(self) -> IJsonPostData:
        '''Configuration for JSON bodies.'''
        return typing.cast(IJsonPostData, jsii.get(self, "json"))

    @json.setter
    def json(self, value: IJsonPostData) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__cfc22f260113ac1b2e2524dc6761d4c3b359f818f0bd3e2002e2db7e8e7a5223)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "json", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="directWebRemoting")
    def direct_web_remoting(self) -> typing.Optional[builtins.bool]:
        '''If DWR scanning should be enabled.

        Default: false
        '''
        return typing.cast(typing.Optional[builtins.bool], jsii.get(self, "directWebRemoting"))

    @direct_web_remoting.setter
    def direct_web_remoting(self, value: typing.Optional[builtins.bool]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5c21eb339dd59edfc6f5329c10723c340b039c74cf175692e030ef59f6000cf2)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "directWebRemoting", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="enabled")
    def enabled(self) -> typing.Optional[builtins.bool]:
        '''If POST data scanning is enabled.

        Default: true
        '''
        return typing.cast(typing.Optional[builtins.bool], jsii.get(self, "enabled"))

    @enabled.setter
    def enabled(self, value: typing.Optional[builtins.bool]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4e1a2b091db13101db37b4c2bc869a956a4816f125faf789109ef951e36bdce8)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "enabled", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="googleWebToolkit")
    def google_web_toolkit(self) -> typing.Optional[builtins.bool]:
        '''If GWT scanning should be enabled.

        Default: false
        '''
        return typing.cast(typing.Optional[builtins.bool], jsii.get(self, "googleWebToolkit"))

    @google_web_toolkit.setter
    def google_web_toolkit(self, value: typing.Optional[builtins.bool]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c6b6de21903ce4fdb06173f9105428419140df6af47c5d19f37bd84bbf266e95)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "googleWebToolkit", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="multiPartFormData")
    def multi_part_form_data(self) -> typing.Optional[builtins.bool]:
        '''If multipart form data bodies should be scanned.

        Default: true
        '''
        return typing.cast(typing.Optional[builtins.bool], jsii.get(self, "multiPartFormData"))

    @multi_part_form_data.setter
    def multi_part_form_data(self, value: typing.Optional[builtins.bool]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ca382115e3a56016bcafed728bd8dbd36718d6b7f7a005ac727f601f2c7b347d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "multiPartFormData", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="xml")
    def xml(self) -> typing.Optional[builtins.bool]:
        '''If XML bodies should be scanned.

        Default: true
        '''
        return typing.cast(typing.Optional[builtins.bool], jsii.get(self, "xml"))

    @xml.setter
    def xml(self, value: typing.Optional[builtins.bool]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5c739455c509a3c4f6f5e8a775bc6d97c6da12389d46b722c599a5700dcb9898)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "xml", value) # pyright: ignore[reportArgumentType]

# Adding a "__jsii_proxy_class__(): typing.Type" function to the interface
typing.cast(typing.Any, IPostData).__jsii_proxy_class__ = lambda : _IPostDataProxy


@jsii.interface(jsii_type="zap-cdk.IPostman")
class IPostman(typing_extensions.Protocol):
    '''
    :interface:

    IPostman
    Represents the configuration for importing a Postman collection.
    :property: {string} [variables] - Comma-separated list of variables as key-value pairs.
    '''

    @builtins.property
    @jsii.member(jsii_name="collectionFile")
    def collection_file(self) -> typing.Optional[builtins.str]:
        ...

    @collection_file.setter
    def collection_file(self, value: typing.Optional[builtins.str]) -> None:
        ...

    @builtins.property
    @jsii.member(jsii_name="collectionUrl")
    def collection_url(self) -> typing.Optional[builtins.str]:
        ...

    @collection_url.setter
    def collection_url(self, value: typing.Optional[builtins.str]) -> None:
        ...

    @builtins.property
    @jsii.member(jsii_name="variables")
    def variables(self) -> typing.Optional[builtins.str]:
        ...

    @variables.setter
    def variables(self, value: typing.Optional[builtins.str]) -> None:
        ...


class _IPostmanProxy:
    '''
    :interface:

    IPostman
    Represents the configuration for importing a Postman collection.
    :property: {string} [variables] - Comma-separated list of variables as key-value pairs.
    '''

    __jsii_type__: typing.ClassVar[str] = "zap-cdk.IPostman"

    @builtins.property
    @jsii.member(jsii_name="collectionFile")
    def collection_file(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "collectionFile"))

    @collection_file.setter
    def collection_file(self, value: typing.Optional[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9fdfbfbd7596b4dc94dfe0bcb963c273e85edf164a9f6fd98fe98647da5f2eba)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "collectionFile", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="collectionUrl")
    def collection_url(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "collectionUrl"))

    @collection_url.setter
    def collection_url(self, value: typing.Optional[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__73e976a4559b8208d91009ca3f37b85c847a314d89588a3b5045510eaf38edd3)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "collectionUrl", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="variables")
    def variables(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "variables"))

    @variables.setter
    def variables(self, value: typing.Optional[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0315dac30fddb8c612b3b09f3ef392c2e6718c7b5a30095354570a535ec8c078)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "variables", value) # pyright: ignore[reportArgumentType]

# Adding a "__jsii_proxy_class__(): typing.Type" function to the interface
typing.cast(typing.Any, IPostman).__jsii_proxy_class__ = lambda : _IPostmanProxy


@jsii.interface(jsii_type="zap-cdk.IPostmanProps")
class IPostmanProps(typing_extensions.Protocol):
    '''Properties for the PostmanConfig construct.

    :interface: IPostmanProps
    :property: {IPostman} postman - The Postman configuration.
    '''

    @builtins.property
    @jsii.member(jsii_name="postman")
    def postman(self) -> IPostman:
        ...

    @postman.setter
    def postman(self, value: IPostman) -> None:
        ...


class _IPostmanPropsProxy:
    '''Properties for the PostmanConfig construct.

    :interface: IPostmanProps
    :property: {IPostman} postman - The Postman configuration.
    '''

    __jsii_type__: typing.ClassVar[str] = "zap-cdk.IPostmanProps"

    @builtins.property
    @jsii.member(jsii_name="postman")
    def postman(self) -> IPostman:
        return typing.cast(IPostman, jsii.get(self, "postman"))

    @postman.setter
    def postman(self, value: IPostman) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6237eede9b1dc1c76dcf05b8e79da0c26de73271a307e39dc79259430cabf4cd)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "postman", value) # pyright: ignore[reportArgumentType]

# Adding a "__jsii_proxy_class__(): typing.Type" function to the interface
typing.cast(typing.Any, IPostmanProps).__jsii_proxy_class__ = lambda : _IPostmanPropsProxy


@jsii.interface(jsii_type="zap-cdk.IReplacer")
class IReplacer(typing_extensions.Protocol):
    '''
    :interface:

    IReplacer
    Represents the configuration for string replacement rules.
    :property: {IReplacerRule[]} rules - A list of replacer rules.
    '''

    @builtins.property
    @jsii.member(jsii_name="rules")
    def rules(self) -> typing.List["IReplacerRule"]:
        ...

    @rules.setter
    def rules(self, value: typing.List["IReplacerRule"]) -> None:
        ...

    @builtins.property
    @jsii.member(jsii_name="deleteAllRules")
    def delete_all_rules(self) -> typing.Optional[builtins.bool]:
        ...

    @delete_all_rules.setter
    def delete_all_rules(self, value: typing.Optional[builtins.bool]) -> None:
        ...


class _IReplacerProxy:
    '''
    :interface:

    IReplacer
    Represents the configuration for string replacement rules.
    :property: {IReplacerRule[]} rules - A list of replacer rules.
    '''

    __jsii_type__: typing.ClassVar[str] = "zap-cdk.IReplacer"

    @builtins.property
    @jsii.member(jsii_name="rules")
    def rules(self) -> typing.List["IReplacerRule"]:
        return typing.cast(typing.List["IReplacerRule"], jsii.get(self, "rules"))

    @rules.setter
    def rules(self, value: typing.List["IReplacerRule"]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__673c33ebe86433cd4726ca9855632a23e78a2ef9b94cc538544327911ab18b0e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "rules", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="deleteAllRules")
    def delete_all_rules(self) -> typing.Optional[builtins.bool]:
        return typing.cast(typing.Optional[builtins.bool], jsii.get(self, "deleteAllRules"))

    @delete_all_rules.setter
    def delete_all_rules(self, value: typing.Optional[builtins.bool]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d9a0555934b9f177bf43e7f14a1f23eed295a6f33863aadd3d7a3bd119beb835)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "deleteAllRules", value) # pyright: ignore[reportArgumentType]

# Adding a "__jsii_proxy_class__(): typing.Type" function to the interface
typing.cast(typing.Any, IReplacer).__jsii_proxy_class__ = lambda : _IReplacerProxy


@jsii.interface(jsii_type="zap-cdk.IReplacerProps")
class IReplacerProps(typing_extensions.Protocol):
    '''Properties for the ReplacerConfig construct.

    :interface: IReplacerProps
    :property: {IReplacer} replacer - The replacer configuration.
    '''

    @builtins.property
    @jsii.member(jsii_name="replacer")
    def replacer(self) -> IReplacer:
        ...

    @replacer.setter
    def replacer(self, value: IReplacer) -> None:
        ...


class _IReplacerPropsProxy:
    '''Properties for the ReplacerConfig construct.

    :interface: IReplacerProps
    :property: {IReplacer} replacer - The replacer configuration.
    '''

    __jsii_type__: typing.ClassVar[str] = "zap-cdk.IReplacerProps"

    @builtins.property
    @jsii.member(jsii_name="replacer")
    def replacer(self) -> IReplacer:
        return typing.cast(IReplacer, jsii.get(self, "replacer"))

    @replacer.setter
    def replacer(self, value: IReplacer) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4f6157cbe93ab011a2727f0b5fc3013491698d949497ed0385f0b540e9749529)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "replacer", value) # pyright: ignore[reportArgumentType]

# Adding a "__jsii_proxy_class__(): typing.Type" function to the interface
typing.cast(typing.Any, IReplacerProps).__jsii_proxy_class__ = lambda : _IReplacerPropsProxy


@jsii.interface(jsii_type="zap-cdk.IReplacerRule")
class IReplacerRule(typing_extensions.Protocol):
    '''
    :interface:

    IReplacerRule
    Represents a rule for replacing strings in requests or responses.
    :property: {number[]} [initiators] - A list of integers representing the initiators.
    '''

    @builtins.property
    @jsii.member(jsii_name="description")
    def description(self) -> builtins.str:
        ...

    @description.setter
    def description(self, value: builtins.str) -> None:
        ...

    @builtins.property
    @jsii.member(jsii_name="matchString")
    def match_string(self) -> builtins.str:
        ...

    @match_string.setter
    def match_string(self, value: builtins.str) -> None:
        ...

    @builtins.property
    @jsii.member(jsii_name="matchType")
    def match_type(self) -> builtins.str:
        ...

    @match_type.setter
    def match_type(self, value: builtins.str) -> None:
        ...

    @builtins.property
    @jsii.member(jsii_name="replacementString")
    def replacement_string(self) -> builtins.str:
        ...

    @replacement_string.setter
    def replacement_string(self, value: builtins.str) -> None:
        ...

    @builtins.property
    @jsii.member(jsii_name="initiators")
    def initiators(self) -> typing.Optional[typing.List[jsii.Number]]:
        ...

    @initiators.setter
    def initiators(self, value: typing.Optional[typing.List[jsii.Number]]) -> None:
        ...

    @builtins.property
    @jsii.member(jsii_name="matchRegex")
    def match_regex(self) -> typing.Optional[builtins.bool]:
        ...

    @match_regex.setter
    def match_regex(self, value: typing.Optional[builtins.bool]) -> None:
        ...

    @builtins.property
    @jsii.member(jsii_name="tokenProcessing")
    def token_processing(self) -> typing.Optional[builtins.bool]:
        ...

    @token_processing.setter
    def token_processing(self, value: typing.Optional[builtins.bool]) -> None:
        ...

    @builtins.property
    @jsii.member(jsii_name="url")
    def url(self) -> typing.Optional[builtins.str]:
        ...

    @url.setter
    def url(self, value: typing.Optional[builtins.str]) -> None:
        ...


class _IReplacerRuleProxy:
    '''
    :interface:

    IReplacerRule
    Represents a rule for replacing strings in requests or responses.
    :property: {number[]} [initiators] - A list of integers representing the initiators.
    '''

    __jsii_type__: typing.ClassVar[str] = "zap-cdk.IReplacerRule"

    @builtins.property
    @jsii.member(jsii_name="description")
    def description(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "description"))

    @description.setter
    def description(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d08e6909f1522f8d50d1a8f8ca731c02d83a9f5ddc2c12e0048accecfe4259ae)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "description", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="matchString")
    def match_string(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "matchString"))

    @match_string.setter
    def match_string(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5a302facc95f04c01ebe37e25f8ff147d9b8fd574c1fe24a064ddb6ca72432e6)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "matchString", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="matchType")
    def match_type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "matchType"))

    @match_type.setter
    def match_type(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f82714d9a26249677af3cac484ff848ab3f798855db0076dfaf1c9ad70ef9d00)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "matchType", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="replacementString")
    def replacement_string(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "replacementString"))

    @replacement_string.setter
    def replacement_string(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__eaccf2daece190d93150f14c94805e93d3f0bb8f52852c867cc947234723459c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "replacementString", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="initiators")
    def initiators(self) -> typing.Optional[typing.List[jsii.Number]]:
        return typing.cast(typing.Optional[typing.List[jsii.Number]], jsii.get(self, "initiators"))

    @initiators.setter
    def initiators(self, value: typing.Optional[typing.List[jsii.Number]]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8d9c83aec98eaa2a03df879fdce4ed924f7a6320e5cca9711a94c655413148d3)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "initiators", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="matchRegex")
    def match_regex(self) -> typing.Optional[builtins.bool]:
        return typing.cast(typing.Optional[builtins.bool], jsii.get(self, "matchRegex"))

    @match_regex.setter
    def match_regex(self, value: typing.Optional[builtins.bool]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f271698dd8e4f23a5ca52ecb6907cc5b53c5d9175a839457d98fb3631230281b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "matchRegex", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="tokenProcessing")
    def token_processing(self) -> typing.Optional[builtins.bool]:
        return typing.cast(typing.Optional[builtins.bool], jsii.get(self, "tokenProcessing"))

    @token_processing.setter
    def token_processing(self, value: typing.Optional[builtins.bool]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a9900737a0778ba696d84519e19ee177bf88ff6de672175b7062540abeceb7e5)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "tokenProcessing", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="url")
    def url(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "url"))

    @url.setter
    def url(self, value: typing.Optional[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__18d1f5a1ff0650ab21b137e0d3555626b26fbedf676a02b1575d067e78535129)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "url", value) # pyright: ignore[reportArgumentType]

# Adding a "__jsii_proxy_class__(): typing.Type" function to the interface
typing.cast(typing.Any, IReplacerRule).__jsii_proxy_class__ = lambda : _IReplacerRuleProxy


@jsii.interface(jsii_type="zap-cdk.IReport")
class IReport(typing_extensions.Protocol):
    '''Interface representing a report configuration.

    :interface: IReport
    :property: {string[]} [sites] - The sites to include in this report, default all.
    '''

    @builtins.property
    @jsii.member(jsii_name="confidences")
    def confidences(self) -> typing.Optional[typing.List[builtins.str]]:
        ...

    @confidences.setter
    def confidences(self, value: typing.Optional[typing.List[builtins.str]]) -> None:
        ...

    @builtins.property
    @jsii.member(jsii_name="displayReport")
    def display_report(self) -> typing.Optional[builtins.bool]:
        ...

    @display_report.setter
    def display_report(self, value: typing.Optional[builtins.bool]) -> None:
        ...

    @builtins.property
    @jsii.member(jsii_name="reportDescription")
    def report_description(self) -> typing.Optional[builtins.str]:
        ...

    @report_description.setter
    def report_description(self, value: typing.Optional[builtins.str]) -> None:
        ...

    @builtins.property
    @jsii.member(jsii_name="reportDir")
    def report_dir(self) -> typing.Optional[builtins.str]:
        ...

    @report_dir.setter
    def report_dir(self, value: typing.Optional[builtins.str]) -> None:
        ...

    @builtins.property
    @jsii.member(jsii_name="reportFile")
    def report_file(self) -> typing.Optional[builtins.str]:
        ...

    @report_file.setter
    def report_file(self, value: typing.Optional[builtins.str]) -> None:
        ...

    @builtins.property
    @jsii.member(jsii_name="reportTitle")
    def report_title(self) -> typing.Optional[builtins.str]:
        ...

    @report_title.setter
    def report_title(self, value: typing.Optional[builtins.str]) -> None:
        ...

    @builtins.property
    @jsii.member(jsii_name="risks")
    def risks(self) -> typing.Optional[typing.List[builtins.str]]:
        ...

    @risks.setter
    def risks(self, value: typing.Optional[typing.List[builtins.str]]) -> None:
        ...

    @builtins.property
    @jsii.member(jsii_name="sections")
    def sections(self) -> typing.Optional[typing.List[builtins.str]]:
        ...

    @sections.setter
    def sections(self, value: typing.Optional[typing.List[builtins.str]]) -> None:
        ...

    @builtins.property
    @jsii.member(jsii_name="sites")
    def sites(self) -> typing.Optional[typing.List[builtins.str]]:
        ...

    @sites.setter
    def sites(self, value: typing.Optional[typing.List[builtins.str]]) -> None:
        ...

    @builtins.property
    @jsii.member(jsii_name="template")
    def template(self) -> typing.Optional[builtins.str]:
        ...

    @template.setter
    def template(self, value: typing.Optional[builtins.str]) -> None:
        ...

    @builtins.property
    @jsii.member(jsii_name="theme")
    def theme(self) -> typing.Optional[builtins.str]:
        ...

    @theme.setter
    def theme(self, value: typing.Optional[builtins.str]) -> None:
        ...


class _IReportProxy:
    '''Interface representing a report configuration.

    :interface: IReport
    :property: {string[]} [sites] - The sites to include in this report, default all.
    '''

    __jsii_type__: typing.ClassVar[str] = "zap-cdk.IReport"

    @builtins.property
    @jsii.member(jsii_name="confidences")
    def confidences(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "confidences"))

    @confidences.setter
    def confidences(self, value: typing.Optional[typing.List[builtins.str]]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__698bcdb9077f2327a8dd3374c3c9d7f55065efa482b7b46ad3c258954f79803e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "confidences", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="displayReport")
    def display_report(self) -> typing.Optional[builtins.bool]:
        return typing.cast(typing.Optional[builtins.bool], jsii.get(self, "displayReport"))

    @display_report.setter
    def display_report(self, value: typing.Optional[builtins.bool]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__511de7483cd9d4b5f9df4ae1bc8610742d10082c91a01a7ed61998ffda3f2928)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "displayReport", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="reportDescription")
    def report_description(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "reportDescription"))

    @report_description.setter
    def report_description(self, value: typing.Optional[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__28d57f0d2c179634d83e52b3865ea5b1a1b88ccaf0f98f00fe5f98ac1b890e58)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "reportDescription", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="reportDir")
    def report_dir(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "reportDir"))

    @report_dir.setter
    def report_dir(self, value: typing.Optional[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__15fed95dd6d8e31340894199b4c50c0a943f5660a240fe372cd29e61cc3f2700)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "reportDir", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="reportFile")
    def report_file(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "reportFile"))

    @report_file.setter
    def report_file(self, value: typing.Optional[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6fe4ca7cc6d6a70e99a8174dd28ebee90b4ae2b3f59defff8f8b055ba957affe)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "reportFile", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="reportTitle")
    def report_title(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "reportTitle"))

    @report_title.setter
    def report_title(self, value: typing.Optional[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__53bc7569a263eebb2b9ca54d06d3e1f5f89994e0d0b65aa113d853ad943f9b99)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "reportTitle", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="risks")
    def risks(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "risks"))

    @risks.setter
    def risks(self, value: typing.Optional[typing.List[builtins.str]]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__361db7eb7ca9ea8a0ad3c755a7dec8a7bc8665b236d825963804924de861f3a3)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "risks", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="sections")
    def sections(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "sections"))

    @sections.setter
    def sections(self, value: typing.Optional[typing.List[builtins.str]]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b3b1ee79bc9f1ac6eb86da315daf25326935c2d55c0a1673fb253b0191960631)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "sections", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="sites")
    def sites(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "sites"))

    @sites.setter
    def sites(self, value: typing.Optional[typing.List[builtins.str]]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__76186d0bc45c8c94b15cee6e66fede86e73b83ea4b12176ef0509028d15aef89)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "sites", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="template")
    def template(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "template"))

    @template.setter
    def template(self, value: typing.Optional[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__64f433871ebf42cb9f513a562185a640f36524ebeeb98f5149cf7acab78ac0e4)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "template", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="theme")
    def theme(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "theme"))

    @theme.setter
    def theme(self, value: typing.Optional[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b5a7fa980af165bc095a9f9605c0960a9e0d7615175617aa1163a98d031b7919)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "theme", value) # pyright: ignore[reportArgumentType]

# Adding a "__jsii_proxy_class__(): typing.Type" function to the interface
typing.cast(typing.Any, IReport).__jsii_proxy_class__ = lambda : _IReportProxy


@jsii.interface(jsii_type="zap-cdk.IReportProps")
class IReportProps(typing_extensions.Protocol):
    '''Properties for the ReportConfig construct.

    :interface: IReportProps
    :property: {IReport} report - The report configuration.
    '''

    @builtins.property
    @jsii.member(jsii_name="report")
    def report(self) -> IReport:
        ...

    @report.setter
    def report(self, value: IReport) -> None:
        ...


class _IReportPropsProxy:
    '''Properties for the ReportConfig construct.

    :interface: IReportProps
    :property: {IReport} report - The report configuration.
    '''

    __jsii_type__: typing.ClassVar[str] = "zap-cdk.IReportProps"

    @builtins.property
    @jsii.member(jsii_name="report")
    def report(self) -> IReport:
        return typing.cast(IReport, jsii.get(self, "report"))

    @report.setter
    def report(self, value: IReport) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a7795fd91eaf5fd466e97f352df81afa4109b164c53b06865b840bb33f7a5d0a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "report", value) # pyright: ignore[reportArgumentType]

# Adding a "__jsii_proxy_class__(): typing.Type" function to the interface
typing.cast(typing.Any, IReportProps).__jsii_proxy_class__ = lambda : _IReportPropsProxy


@jsii.interface(jsii_type="zap-cdk.IRequest")
class IRequest(typing_extensions.Protocol):
    '''Interface representing a single request configuration.

    :interface: IRequest
    :property: {number} [responseCode] - Optional expected response code.
    '''

    @builtins.property
    @jsii.member(jsii_name="url")
    def url(self) -> builtins.str:
        ...

    @url.setter
    def url(self, value: builtins.str) -> None:
        ...

    @builtins.property
    @jsii.member(jsii_name="data")
    def data(self) -> typing.Optional[builtins.str]:
        ...

    @data.setter
    def data(self, value: typing.Optional[builtins.str]) -> None:
        ...

    @builtins.property
    @jsii.member(jsii_name="headers")
    def headers(self) -> typing.Optional[typing.List[builtins.str]]:
        ...

    @headers.setter
    def headers(self, value: typing.Optional[typing.List[builtins.str]]) -> None:
        ...

    @builtins.property
    @jsii.member(jsii_name="httpVersion")
    def http_version(self) -> typing.Optional[builtins.str]:
        ...

    @http_version.setter
    def http_version(self, value: typing.Optional[builtins.str]) -> None:
        ...

    @builtins.property
    @jsii.member(jsii_name="method")
    def method(self) -> typing.Optional[builtins.str]:
        ...

    @method.setter
    def method(self, value: typing.Optional[builtins.str]) -> None:
        ...

    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> typing.Optional[builtins.str]:
        ...

    @name.setter
    def name(self, value: typing.Optional[builtins.str]) -> None:
        ...

    @builtins.property
    @jsii.member(jsii_name="responseCode")
    def response_code(self) -> typing.Optional[jsii.Number]:
        ...

    @response_code.setter
    def response_code(self, value: typing.Optional[jsii.Number]) -> None:
        ...


class _IRequestProxy:
    '''Interface representing a single request configuration.

    :interface: IRequest
    :property: {number} [responseCode] - Optional expected response code.
    '''

    __jsii_type__: typing.ClassVar[str] = "zap-cdk.IRequest"

    @builtins.property
    @jsii.member(jsii_name="url")
    def url(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "url"))

    @url.setter
    def url(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8e73508d4b934645f8fcc50b5e8ff2150099fc593e6032dfd32fb6badddd9631)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "url", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="data")
    def data(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "data"))

    @data.setter
    def data(self, value: typing.Optional[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__af7921b1cf43c5088afe86e9f0e0e1007726d47d61de3c93fdc132ddc28f7e27)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "data", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="headers")
    def headers(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "headers"))

    @headers.setter
    def headers(self, value: typing.Optional[typing.List[builtins.str]]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b56da701f5c1a6bf20aba998f54ad579e8402dfe03215207f92b65cb3a5a845b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "headers", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="httpVersion")
    def http_version(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "httpVersion"))

    @http_version.setter
    def http_version(self, value: typing.Optional[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__98a3b1b859b51c72f16a012829f1719ca40941cd7f37f270606dfc003967d4db)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "httpVersion", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="method")
    def method(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "method"))

    @method.setter
    def method(self, value: typing.Optional[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e4e4b5cd9c245a96cff7c770bdb1c17a579e61f206c5d7c166b96c535a414569)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "method", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "name"))

    @name.setter
    def name(self, value: typing.Optional[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d80534e42894c9e3e2b9ae606047f59bb6c1e032ccdf6d4e944dab3afca7142e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "name", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="responseCode")
    def response_code(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "responseCode"))

    @response_code.setter
    def response_code(self, value: typing.Optional[jsii.Number]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__33d8dace7bf48a596720324800bd29152d8783de1cc678187c3c01b286905863)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "responseCode", value) # pyright: ignore[reportArgumentType]

# Adding a "__jsii_proxy_class__(): typing.Type" function to the interface
typing.cast(typing.Any, IRequest).__jsii_proxy_class__ = lambda : _IRequestProxy


@jsii.interface(jsii_type="zap-cdk.IRequestorParameters")
class IRequestorParameters(typing_extensions.Protocol):
    '''Interface representing the parameters for making requests.

    :interface: IRequestorParameters
    :property: {boolean} [alwaysRun] - If set and the job is enabled, it will run even if the plan exits early, default: false.
    '''

    @builtins.property
    @jsii.member(jsii_name="requests")
    def requests(self) -> typing.List[IRequest]:
        ...

    @requests.setter
    def requests(self, value: typing.List[IRequest]) -> None:
        ...

    @builtins.property
    @jsii.member(jsii_name="alwaysRun")
    def always_run(self) -> typing.Optional[builtins.bool]:
        ...

    @always_run.setter
    def always_run(self, value: typing.Optional[builtins.bool]) -> None:
        ...

    @builtins.property
    @jsii.member(jsii_name="enabled")
    def enabled(self) -> typing.Optional[builtins.bool]:
        ...

    @enabled.setter
    def enabled(self, value: typing.Optional[builtins.bool]) -> None:
        ...

    @builtins.property
    @jsii.member(jsii_name="user")
    def user(self) -> typing.Optional[builtins.str]:
        ...

    @user.setter
    def user(self, value: typing.Optional[builtins.str]) -> None:
        ...


class _IRequestorParametersProxy:
    '''Interface representing the parameters for making requests.

    :interface: IRequestorParameters
    :property: {boolean} [alwaysRun] - If set and the job is enabled, it will run even if the plan exits early, default: false.
    '''

    __jsii_type__: typing.ClassVar[str] = "zap-cdk.IRequestorParameters"

    @builtins.property
    @jsii.member(jsii_name="requests")
    def requests(self) -> typing.List[IRequest]:
        return typing.cast(typing.List[IRequest], jsii.get(self, "requests"))

    @requests.setter
    def requests(self, value: typing.List[IRequest]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__148087ecbea2ea18f730a4a84b59b284b326d225b6f3dd50df6218e11fd45d13)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "requests", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="alwaysRun")
    def always_run(self) -> typing.Optional[builtins.bool]:
        return typing.cast(typing.Optional[builtins.bool], jsii.get(self, "alwaysRun"))

    @always_run.setter
    def always_run(self, value: typing.Optional[builtins.bool]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1165fa7cedb1858f2e1de9f2d6dab2b04940e9cfecf886fdc906ec8400942dbd)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "alwaysRun", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="enabled")
    def enabled(self) -> typing.Optional[builtins.bool]:
        return typing.cast(typing.Optional[builtins.bool], jsii.get(self, "enabled"))

    @enabled.setter
    def enabled(self, value: typing.Optional[builtins.bool]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__fdaf41c31fd17b3a6a1cfa6e383615d720e6f07a3531ec73be98caa96538e26a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "enabled", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="user")
    def user(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "user"))

    @user.setter
    def user(self, value: typing.Optional[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e7fcae784ea4084f96c26f343170547d6a10824d11a4bc81dfa26617310b7874)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "user", value) # pyright: ignore[reportArgumentType]

# Adding a "__jsii_proxy_class__(): typing.Type" function to the interface
typing.cast(typing.Any, IRequestorParameters).__jsii_proxy_class__ = lambda : _IRequestorParametersProxy


@jsii.interface(jsii_type="zap-cdk.IRequestorProps")
class IRequestorProps(typing_extensions.Protocol):
    '''Properties for the RequestorConfig construct.

    :interface: IRequestorProps
    :property: {IRequestorParameters} requestor - The requestor configuration.
    '''

    @builtins.property
    @jsii.member(jsii_name="requestor")
    def requestor(self) -> IRequestorParameters:
        ...

    @requestor.setter
    def requestor(self, value: IRequestorParameters) -> None:
        ...


class _IRequestorPropsProxy:
    '''Properties for the RequestorConfig construct.

    :interface: IRequestorProps
    :property: {IRequestorParameters} requestor - The requestor configuration.
    '''

    __jsii_type__: typing.ClassVar[str] = "zap-cdk.IRequestorProps"

    @builtins.property
    @jsii.member(jsii_name="requestor")
    def requestor(self) -> IRequestorParameters:
        return typing.cast(IRequestorParameters, jsii.get(self, "requestor"))

    @requestor.setter
    def requestor(self, value: IRequestorParameters) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__506cde699f33879e333b15f7997a53c8403e9923c42ab9317b2c65e2f75e5269)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "requestor", value) # pyright: ignore[reportArgumentType]

# Adding a "__jsii_proxy_class__(): typing.Type" function to the interface
typing.cast(typing.Any, IRequestorProps).__jsii_proxy_class__ = lambda : _IRequestorPropsProxy


@jsii.interface(jsii_type="zap-cdk.IRule")
class IRule(typing_extensions.Protocol):
    '''
    :interface:

    IRule
    Represents an individual rule in the active scan policy.
    :property: {threshold} [threshold] - The Alert Threshold for this rule, default: Medium.
    '''

    @builtins.property
    @jsii.member(jsii_name="id")
    def id(self) -> jsii.Number:
        ...

    @id.setter
    def id(self, value: jsii.Number) -> None:
        ...

    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> typing.Optional[builtins.str]:
        ...

    @name.setter
    def name(self, value: typing.Optional[builtins.str]) -> None:
        ...

    @builtins.property
    @jsii.member(jsii_name="strength")
    def strength(self) -> typing.Optional[builtins.str]:
        ...

    @strength.setter
    def strength(self, value: typing.Optional[builtins.str]) -> None:
        ...

    @builtins.property
    @jsii.member(jsii_name="threshold")
    def threshold(self) -> typing.Optional[builtins.str]:
        ...

    @threshold.setter
    def threshold(self, value: typing.Optional[builtins.str]) -> None:
        ...


class _IRuleProxy:
    '''
    :interface:

    IRule
    Represents an individual rule in the active scan policy.
    :property: {threshold} [threshold] - The Alert Threshold for this rule, default: Medium.
    '''

    __jsii_type__: typing.ClassVar[str] = "zap-cdk.IRule"

    @builtins.property
    @jsii.member(jsii_name="id")
    def id(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "id"))

    @id.setter
    def id(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ceabab1a10e77f8052974586e966e8c88beae6f8a22b5bd52642db7cc35ee7f5)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "id", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "name"))

    @name.setter
    def name(self, value: typing.Optional[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9a1fbc09418cf2050d3f09ddcf6f2495c40bf70cc03ad0f79fd912800ed22c1c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "name", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="strength")
    def strength(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "strength"))

    @strength.setter
    def strength(self, value: typing.Optional[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f52aeaf33b4c902045ec3942d9be12f4adab1f9e7cd5d498bed8abd2dce6bc53)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "strength", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="threshold")
    def threshold(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "threshold"))

    @threshold.setter
    def threshold(self, value: typing.Optional[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c0952c8cea99cd79a9873148c74b277f158c0d513d41a903ad3095e458f0e42a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "threshold", value) # pyright: ignore[reportArgumentType]

# Adding a "__jsii_proxy_class__(): typing.Type" function to the interface
typing.cast(typing.Any, IRule).__jsii_proxy_class__ = lambda : _IRuleProxy


@jsii.interface(jsii_type="zap-cdk.IRules")
class IRules(typing_extensions.Protocol):
    '''
    :interface:

    IRules
    Represents a rule for the active scan.
    :property: {string} [threshold] - The Alert Threshold for this rule, one of Off, Low, Medium, High, default: Medium.
    '''

    @builtins.property
    @jsii.member(jsii_name="id")
    def id(self) -> jsii.Number:
        ...

    @id.setter
    def id(self, value: jsii.Number) -> None:
        ...

    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> typing.Optional[builtins.str]:
        ...

    @name.setter
    def name(self, value: typing.Optional[builtins.str]) -> None:
        ...

    @builtins.property
    @jsii.member(jsii_name="strength")
    def strength(self) -> typing.Optional[builtins.str]:
        ...

    @strength.setter
    def strength(self, value: typing.Optional[builtins.str]) -> None:
        ...

    @builtins.property
    @jsii.member(jsii_name="threshold")
    def threshold(self) -> typing.Optional[builtins.str]:
        ...

    @threshold.setter
    def threshold(self, value: typing.Optional[builtins.str]) -> None:
        ...


class _IRulesProxy:
    '''
    :interface:

    IRules
    Represents a rule for the active scan.
    :property: {string} [threshold] - The Alert Threshold for this rule, one of Off, Low, Medium, High, default: Medium.
    '''

    __jsii_type__: typing.ClassVar[str] = "zap-cdk.IRules"

    @builtins.property
    @jsii.member(jsii_name="id")
    def id(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "id"))

    @id.setter
    def id(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e0c7d70f32d9b5147f3aa6ede8de027e8d4852417cf8bb1ea76d765954203928)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "id", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "name"))

    @name.setter
    def name(self, value: typing.Optional[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f27a4f53464657e4774d607918b430ed720d26d3f9d547f17ef624593e0cfe43)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "name", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="strength")
    def strength(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "strength"))

    @strength.setter
    def strength(self, value: typing.Optional[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6b6fa341c307f4a3aae6d02dc95b43f2a3f7bcc0727cc4dca63f72f2ffe5d84d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "strength", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="threshold")
    def threshold(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "threshold"))

    @threshold.setter
    def threshold(self, value: typing.Optional[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__30694de5e3c1eb85caf48dd146554aed64ec2a5f2986efcd128a2b40fde753ce)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "threshold", value) # pyright: ignore[reportArgumentType]

# Adding a "__jsii_proxy_class__(): typing.Type" function to the interface
typing.cast(typing.Any, IRules).__jsii_proxy_class__ = lambda : _IRulesProxy


@jsii.interface(jsii_type="zap-cdk.ISessionManagementParameters")
class ISessionManagementParameters(typing_extensions.Protocol):
    '''
    :interface:

    ISessionManagementParameters
    Represents the parameters for session management in the scanning process.
    :property: {string} [parameters.scriptEngine] - Name of the script engine to use, only for 'script' session management.
    '''

    @builtins.property
    @jsii.member(jsii_name="method")
    def method(self) -> builtins.str:
        ...

    @method.setter
    def method(self, value: builtins.str) -> None:
        ...

    @builtins.property
    @jsii.member(jsii_name="parameters")
    def parameters(self) -> "ISessionManagementParametersParameters":
        ...

    @parameters.setter
    def parameters(self, value: "ISessionManagementParametersParameters") -> None:
        ...


class _ISessionManagementParametersProxy:
    '''
    :interface:

    ISessionManagementParameters
    Represents the parameters for session management in the scanning process.
    :property: {string} [parameters.scriptEngine] - Name of the script engine to use, only for 'script' session management.
    '''

    __jsii_type__: typing.ClassVar[str] = "zap-cdk.ISessionManagementParameters"

    @builtins.property
    @jsii.member(jsii_name="method")
    def method(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "method"))

    @method.setter
    def method(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5cdbb9d0b54cc5eb2600fe7e248d48bd80bed699b1e26d7e719d7e883edbfc0a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "method", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="parameters")
    def parameters(self) -> "ISessionManagementParametersParameters":
        return typing.cast("ISessionManagementParametersParameters", jsii.get(self, "parameters"))

    @parameters.setter
    def parameters(self, value: "ISessionManagementParametersParameters") -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__652e501aa40928dec6500a7e56376f92ecba8898406b96dce387be74992d787e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "parameters", value) # pyright: ignore[reportArgumentType]

# Adding a "__jsii_proxy_class__(): typing.Type" function to the interface
typing.cast(typing.Any, ISessionManagementParameters).__jsii_proxy_class__ = lambda : _ISessionManagementParametersProxy


@jsii.interface(jsii_type="zap-cdk.ISessionManagementParametersParameters")
class ISessionManagementParametersParameters(typing_extensions.Protocol):
    @builtins.property
    @jsii.member(jsii_name="script")
    def script(self) -> typing.Optional[builtins.str]:
        ...

    @script.setter
    def script(self, value: typing.Optional[builtins.str]) -> None:
        ...

    @builtins.property
    @jsii.member(jsii_name="scriptEngine")
    def script_engine(self) -> typing.Optional[builtins.str]:
        ...

    @script_engine.setter
    def script_engine(self, value: typing.Optional[builtins.str]) -> None:
        ...


class _ISessionManagementParametersParametersProxy:
    __jsii_type__: typing.ClassVar[str] = "zap-cdk.ISessionManagementParametersParameters"

    @builtins.property
    @jsii.member(jsii_name="script")
    def script(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "script"))

    @script.setter
    def script(self, value: typing.Optional[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a4dc9de78053a677f66b21dc0abbd7d0f302e0a15dedc372057236bd4e49f614)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "script", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="scriptEngine")
    def script_engine(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "scriptEngine"))

    @script_engine.setter
    def script_engine(self, value: typing.Optional[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__65ed25b2bfabe433177b33e025aaccd65a45318c8ff56329f49322cf2d5c3401)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "scriptEngine", value) # pyright: ignore[reportArgumentType]

# Adding a "__jsii_proxy_class__(): typing.Type" function to the interface
typing.cast(typing.Any, ISessionManagementParametersParameters).__jsii_proxy_class__ = lambda : _ISessionManagementParametersParametersProxy


@jsii.interface(jsii_type="zap-cdk.ISoap")
class ISoap(typing_extensions.Protocol):
    '''Interface representing the configuration for a SOAP service.

    :interface: ISoap
    :property: {string} [wsdlUrl] - URL pointing to the WSDL, default: null.
    '''

    @builtins.property
    @jsii.member(jsii_name="wsdlFile")
    def wsdl_file(self) -> typing.Optional[builtins.str]:
        ...

    @wsdl_file.setter
    def wsdl_file(self, value: typing.Optional[builtins.str]) -> None:
        ...

    @builtins.property
    @jsii.member(jsii_name="wsdlUrl")
    def wsdl_url(self) -> typing.Optional[builtins.str]:
        ...

    @wsdl_url.setter
    def wsdl_url(self, value: typing.Optional[builtins.str]) -> None:
        ...


class _ISoapProxy:
    '''Interface representing the configuration for a SOAP service.

    :interface: ISoap
    :property: {string} [wsdlUrl] - URL pointing to the WSDL, default: null.
    '''

    __jsii_type__: typing.ClassVar[str] = "zap-cdk.ISoap"

    @builtins.property
    @jsii.member(jsii_name="wsdlFile")
    def wsdl_file(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "wsdlFile"))

    @wsdl_file.setter
    def wsdl_file(self, value: typing.Optional[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__fe7b748ecea4764af8b8f375c53d3bf021e202493bec4e14faa99366466fdf90)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wsdlFile", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="wsdlUrl")
    def wsdl_url(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "wsdlUrl"))

    @wsdl_url.setter
    def wsdl_url(self, value: typing.Optional[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0496cf76ba0dc52bbf55b429abef37988820ecdfb14b9407056e21ef1eb23bb8)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wsdlUrl", value) # pyright: ignore[reportArgumentType]

# Adding a "__jsii_proxy_class__(): typing.Type" function to the interface
typing.cast(typing.Any, ISoap).__jsii_proxy_class__ = lambda : _ISoapProxy


@jsii.interface(jsii_type="zap-cdk.ISoapProps")
class ISoapProps(typing_extensions.Protocol):
    '''Properties for the SOAPConfig construct.

    :interface: ISoapProps
    :property: {ISoap} soap - The SOAP configuration.
    '''

    @builtins.property
    @jsii.member(jsii_name="soap")
    def soap(self) -> ISoap:
        ...

    @soap.setter
    def soap(self, value: ISoap) -> None:
        ...


class _ISoapPropsProxy:
    '''Properties for the SOAPConfig construct.

    :interface: ISoapProps
    :property: {ISoap} soap - The SOAP configuration.
    '''

    __jsii_type__: typing.ClassVar[str] = "zap-cdk.ISoapProps"

    @builtins.property
    @jsii.member(jsii_name="soap")
    def soap(self) -> ISoap:
        return typing.cast(ISoap, jsii.get(self, "soap"))

    @soap.setter
    def soap(self, value: ISoap) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2202001b2062af3db7e70662bd39b2098c16a77c8092ba5e8b65577ffef1dedd)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "soap", value) # pyright: ignore[reportArgumentType]

# Adding a "__jsii_proxy_class__(): typing.Type" function to the interface
typing.cast(typing.Any, ISoapProps).__jsii_proxy_class__ = lambda : _ISoapPropsProxy


@jsii.interface(jsii_type="zap-cdk.ISpider")
class ISpider(typing_extensions.Protocol):
    '''Interface representing a spider configuration.

    :interface: ISpider
    :property: {boolean} [alwaysRun] - If set and the job is enabled, it will run even if the plan exits early, default: false.
    '''

    @builtins.property
    @jsii.member(jsii_name="parameters")
    def parameters(self) -> "ISpiderParameters":
        ...

    @parameters.setter
    def parameters(self, value: "ISpiderParameters") -> None:
        ...

    @builtins.property
    @jsii.member(jsii_name="type")
    def type(self) -> builtins.str:
        ...

    @type.setter
    def type(self, value: builtins.str) -> None:
        ...

    @builtins.property
    @jsii.member(jsii_name="alwaysRun")
    def always_run(self) -> typing.Optional[builtins.bool]:
        ...

    @always_run.setter
    def always_run(self, value: typing.Optional[builtins.bool]) -> None:
        ...

    @builtins.property
    @jsii.member(jsii_name="enabled")
    def enabled(self) -> typing.Optional[builtins.bool]:
        ...

    @enabled.setter
    def enabled(self, value: typing.Optional[builtins.bool]) -> None:
        ...

    @builtins.property
    @jsii.member(jsii_name="tests")
    def tests(self) -> typing.Optional[typing.List["ISpiderTest"]]:
        ...

    @tests.setter
    def tests(self, value: typing.Optional[typing.List["ISpiderTest"]]) -> None:
        ...


class _ISpiderProxy:
    '''Interface representing a spider configuration.

    :interface: ISpider
    :property: {boolean} [alwaysRun] - If set and the job is enabled, it will run even if the plan exits early, default: false.
    '''

    __jsii_type__: typing.ClassVar[str] = "zap-cdk.ISpider"

    @builtins.property
    @jsii.member(jsii_name="parameters")
    def parameters(self) -> "ISpiderParameters":
        return typing.cast("ISpiderParameters", jsii.get(self, "parameters"))

    @parameters.setter
    def parameters(self, value: "ISpiderParameters") -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ae6937b9f7c771b5f0740e894724b0229698639c51c1aefefc6df67f3ebd3ca4)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "parameters", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="type")
    def type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "type"))

    @type.setter
    def type(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6788c399f83f7ade85c26f1a40bf395b1410e695e638f30ca5b46f38117bdd8c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "type", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="alwaysRun")
    def always_run(self) -> typing.Optional[builtins.bool]:
        return typing.cast(typing.Optional[builtins.bool], jsii.get(self, "alwaysRun"))

    @always_run.setter
    def always_run(self, value: typing.Optional[builtins.bool]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7f44ba43f4c5205184c0ebd8f9897a411eaaca1559da7e0cc64d4b985ede107c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "alwaysRun", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="enabled")
    def enabled(self) -> typing.Optional[builtins.bool]:
        return typing.cast(typing.Optional[builtins.bool], jsii.get(self, "enabled"))

    @enabled.setter
    def enabled(self, value: typing.Optional[builtins.bool]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__dc18e1b0268f314549ba928ea71c41886eded224b912c555bc575de4a1abc553)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "enabled", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="tests")
    def tests(self) -> typing.Optional[typing.List["ISpiderTest"]]:
        return typing.cast(typing.Optional[typing.List["ISpiderTest"]], jsii.get(self, "tests"))

    @tests.setter
    def tests(self, value: typing.Optional[typing.List["ISpiderTest"]]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__57ff4f8d13451124e5373efdf967935c1f67bf3c660bc7ac8e7443f68929ffb1)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "tests", value) # pyright: ignore[reportArgumentType]

# Adding a "__jsii_proxy_class__(): typing.Type" function to the interface
typing.cast(typing.Any, ISpider).__jsii_proxy_class__ = lambda : _ISpiderProxy


@jsii.interface(jsii_type="zap-cdk.ISpiderAjax")
class ISpiderAjax(typing_extensions.Protocol):
    '''Interface representing the parameters for an AJAX spider configuration.

    :interface: ISpiderAjax
    :property: {ITest[]} [tests] - List of tests to perform.
    '''

    @builtins.property
    @jsii.member(jsii_name="browserId")
    def browser_id(self) -> typing.Optional[builtins.str]:
        ...

    @browser_id.setter
    def browser_id(self, value: typing.Optional[builtins.str]) -> None:
        ...

    @builtins.property
    @jsii.member(jsii_name="clickDefaultElems")
    def click_default_elems(self) -> typing.Optional[builtins.bool]:
        ...

    @click_default_elems.setter
    def click_default_elems(self, value: typing.Optional[builtins.bool]) -> None:
        ...

    @builtins.property
    @jsii.member(jsii_name="clickElemsOnce")
    def click_elems_once(self) -> typing.Optional[builtins.bool]:
        ...

    @click_elems_once.setter
    def click_elems_once(self, value: typing.Optional[builtins.bool]) -> None:
        ...

    @builtins.property
    @jsii.member(jsii_name="context")
    def context(self) -> typing.Optional[builtins.str]:
        ...

    @context.setter
    def context(self, value: typing.Optional[builtins.str]) -> None:
        ...

    @builtins.property
    @jsii.member(jsii_name="elements")
    def elements(self) -> typing.Optional[typing.List[builtins.str]]:
        ...

    @elements.setter
    def elements(self, value: typing.Optional[typing.List[builtins.str]]) -> None:
        ...

    @builtins.property
    @jsii.member(jsii_name="eventWait")
    def event_wait(self) -> typing.Optional[jsii.Number]:
        ...

    @event_wait.setter
    def event_wait(self, value: typing.Optional[jsii.Number]) -> None:
        ...

    @builtins.property
    @jsii.member(jsii_name="excludedElements")
    def excluded_elements(self) -> typing.Optional[typing.List[IExcludedElement]]:
        ...

    @excluded_elements.setter
    def excluded_elements(
        self,
        value: typing.Optional[typing.List[IExcludedElement]],
    ) -> None:
        ...

    @builtins.property
    @jsii.member(jsii_name="inScopeOnly")
    def in_scope_only(self) -> typing.Optional[builtins.bool]:
        ...

    @in_scope_only.setter
    def in_scope_only(self, value: typing.Optional[builtins.bool]) -> None:
        ...

    @builtins.property
    @jsii.member(jsii_name="maxCrawlDepth")
    def max_crawl_depth(self) -> typing.Optional[jsii.Number]:
        ...

    @max_crawl_depth.setter
    def max_crawl_depth(self, value: typing.Optional[jsii.Number]) -> None:
        ...

    @builtins.property
    @jsii.member(jsii_name="maxCrawlStates")
    def max_crawl_states(self) -> typing.Optional[jsii.Number]:
        ...

    @max_crawl_states.setter
    def max_crawl_states(self, value: typing.Optional[jsii.Number]) -> None:
        ...

    @builtins.property
    @jsii.member(jsii_name="maxDuration")
    def max_duration(self) -> typing.Optional[jsii.Number]:
        ...

    @max_duration.setter
    def max_duration(self, value: typing.Optional[jsii.Number]) -> None:
        ...

    @builtins.property
    @jsii.member(jsii_name="numberOfBrowsers")
    def number_of_browsers(self) -> typing.Optional[jsii.Number]:
        ...

    @number_of_browsers.setter
    def number_of_browsers(self, value: typing.Optional[jsii.Number]) -> None:
        ...

    @builtins.property
    @jsii.member(jsii_name="randomInputs")
    def random_inputs(self) -> typing.Optional[builtins.bool]:
        ...

    @random_inputs.setter
    def random_inputs(self, value: typing.Optional[builtins.bool]) -> None:
        ...

    @builtins.property
    @jsii.member(jsii_name="reloadWait")
    def reload_wait(self) -> typing.Optional[jsii.Number]:
        ...

    @reload_wait.setter
    def reload_wait(self, value: typing.Optional[jsii.Number]) -> None:
        ...

    @builtins.property
    @jsii.member(jsii_name="runOnlyIfModern")
    def run_only_if_modern(self) -> typing.Optional[builtins.bool]:
        ...

    @run_only_if_modern.setter
    def run_only_if_modern(self, value: typing.Optional[builtins.bool]) -> None:
        ...

    @builtins.property
    @jsii.member(jsii_name="scopeCheck")
    def scope_check(self) -> typing.Optional[builtins.str]:
        ...

    @scope_check.setter
    def scope_check(self, value: typing.Optional[builtins.str]) -> None:
        ...

    @builtins.property
    @jsii.member(jsii_name="tests")
    def tests(self) -> typing.Optional[typing.List[IAjaxTest]]:
        ...

    @tests.setter
    def tests(self, value: typing.Optional[typing.List[IAjaxTest]]) -> None:
        ...

    @builtins.property
    @jsii.member(jsii_name="url")
    def url(self) -> typing.Optional[builtins.str]:
        ...

    @url.setter
    def url(self, value: typing.Optional[builtins.str]) -> None:
        ...

    @builtins.property
    @jsii.member(jsii_name="user")
    def user(self) -> typing.Optional[builtins.str]:
        ...

    @user.setter
    def user(self, value: typing.Optional[builtins.str]) -> None:
        ...


class _ISpiderAjaxProxy:
    '''Interface representing the parameters for an AJAX spider configuration.

    :interface: ISpiderAjax
    :property: {ITest[]} [tests] - List of tests to perform.
    '''

    __jsii_type__: typing.ClassVar[str] = "zap-cdk.ISpiderAjax"

    @builtins.property
    @jsii.member(jsii_name="browserId")
    def browser_id(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "browserId"))

    @browser_id.setter
    def browser_id(self, value: typing.Optional[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1d2007dcd277966bae33fa5ed9dbb703c860c91152a3f7e806b2221d37a710da)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "browserId", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="clickDefaultElems")
    def click_default_elems(self) -> typing.Optional[builtins.bool]:
        return typing.cast(typing.Optional[builtins.bool], jsii.get(self, "clickDefaultElems"))

    @click_default_elems.setter
    def click_default_elems(self, value: typing.Optional[builtins.bool]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__cacb5eaed6ba69eaffb239c02fd1508192410a8d4b1088061908e72924481e21)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "clickDefaultElems", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="clickElemsOnce")
    def click_elems_once(self) -> typing.Optional[builtins.bool]:
        return typing.cast(typing.Optional[builtins.bool], jsii.get(self, "clickElemsOnce"))

    @click_elems_once.setter
    def click_elems_once(self, value: typing.Optional[builtins.bool]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__101d32aee3989a2d07c5dbc5414868543f86ff4bf64c702a55a779025874ee64)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "clickElemsOnce", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="context")
    def context(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "context"))

    @context.setter
    def context(self, value: typing.Optional[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6e598134d5f75379642ec1ea5d6aea76382855f6fd2e119018196f0a025a2f2c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "context", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="elements")
    def elements(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "elements"))

    @elements.setter
    def elements(self, value: typing.Optional[typing.List[builtins.str]]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__149d74588971ae8b20a12f45203c63d4b48d6b905fa5c4de64162c547a1a80b4)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "elements", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="eventWait")
    def event_wait(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "eventWait"))

    @event_wait.setter
    def event_wait(self, value: typing.Optional[jsii.Number]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__442b6f0a28b2a5a653cbec409a9d8371dd19a18242f125ef6a489cf0ec3ce6ac)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "eventWait", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="excludedElements")
    def excluded_elements(self) -> typing.Optional[typing.List[IExcludedElement]]:
        return typing.cast(typing.Optional[typing.List[IExcludedElement]], jsii.get(self, "excludedElements"))

    @excluded_elements.setter
    def excluded_elements(
        self,
        value: typing.Optional[typing.List[IExcludedElement]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9ca2004d04041d231bb56f095b26326a03b4c63200db6cd16b83e81638d9acb6)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "excludedElements", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="inScopeOnly")
    def in_scope_only(self) -> typing.Optional[builtins.bool]:
        return typing.cast(typing.Optional[builtins.bool], jsii.get(self, "inScopeOnly"))

    @in_scope_only.setter
    def in_scope_only(self, value: typing.Optional[builtins.bool]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6f9dbbadaf03f13d8318a81559cc6eee13bde731f7a01cba228ea58836387f6d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "inScopeOnly", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="maxCrawlDepth")
    def max_crawl_depth(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "maxCrawlDepth"))

    @max_crawl_depth.setter
    def max_crawl_depth(self, value: typing.Optional[jsii.Number]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__48d686721c7ba0fccd265525629e433b289daaa447ce35e8aed30443fc9e73dc)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "maxCrawlDepth", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="maxCrawlStates")
    def max_crawl_states(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "maxCrawlStates"))

    @max_crawl_states.setter
    def max_crawl_states(self, value: typing.Optional[jsii.Number]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d73a2741067e81260ec336a9d6347383063ffea2a700d5763a6902d950f86ad4)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "maxCrawlStates", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="maxDuration")
    def max_duration(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "maxDuration"))

    @max_duration.setter
    def max_duration(self, value: typing.Optional[jsii.Number]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e349fdfd3951db3d2917f2ac0507b6131a0a8fa91dee80137e30e872cb84cd50)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "maxDuration", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="numberOfBrowsers")
    def number_of_browsers(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "numberOfBrowsers"))

    @number_of_browsers.setter
    def number_of_browsers(self, value: typing.Optional[jsii.Number]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4e2808eed40580f45f3d20fff3985302b33f15b4e994898d25150ced3eaa1d9b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "numberOfBrowsers", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="randomInputs")
    def random_inputs(self) -> typing.Optional[builtins.bool]:
        return typing.cast(typing.Optional[builtins.bool], jsii.get(self, "randomInputs"))

    @random_inputs.setter
    def random_inputs(self, value: typing.Optional[builtins.bool]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6dadfe8a90f2a8a3ec52187a53dee158bd5f46643bedde886d828eefe7768c93)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "randomInputs", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="reloadWait")
    def reload_wait(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "reloadWait"))

    @reload_wait.setter
    def reload_wait(self, value: typing.Optional[jsii.Number]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c791e32cacc66b004677e3953197d165955a5b6b9fbc7b3eeb5bcbd6944d6722)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "reloadWait", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="runOnlyIfModern")
    def run_only_if_modern(self) -> typing.Optional[builtins.bool]:
        return typing.cast(typing.Optional[builtins.bool], jsii.get(self, "runOnlyIfModern"))

    @run_only_if_modern.setter
    def run_only_if_modern(self, value: typing.Optional[builtins.bool]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ae82776afd340eba02656a5c93f83ee1419ca5e859df05f249416afe4803b263)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "runOnlyIfModern", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="scopeCheck")
    def scope_check(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "scopeCheck"))

    @scope_check.setter
    def scope_check(self, value: typing.Optional[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__dea14a9b61c42d6cc55fab55f9b4dc6b25b78cdbf88daae11b55a3d9fc77748c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "scopeCheck", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="tests")
    def tests(self) -> typing.Optional[typing.List[IAjaxTest]]:
        return typing.cast(typing.Optional[typing.List[IAjaxTest]], jsii.get(self, "tests"))

    @tests.setter
    def tests(self, value: typing.Optional[typing.List[IAjaxTest]]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__65a89f14353ba072d6daa7d54bbc1944c97be475fd48980cca8b4da9dde6eadb)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "tests", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="url")
    def url(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "url"))

    @url.setter
    def url(self, value: typing.Optional[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6ae12a1a311134713762e55b65ad52d92ab122bb3daa1639acefd8faa39a40c9)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "url", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="user")
    def user(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "user"))

    @user.setter
    def user(self, value: typing.Optional[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6a1111b193cda28fa8db9fbee7710ff77642c81dbdd19433eb60ce65b6848902)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "user", value) # pyright: ignore[reportArgumentType]

# Adding a "__jsii_proxy_class__(): typing.Type" function to the interface
typing.cast(typing.Any, ISpiderAjax).__jsii_proxy_class__ = lambda : _ISpiderAjaxProxy


@jsii.interface(jsii_type="zap-cdk.ISpiderAjaxProps")
class ISpiderAjaxProps(typing_extensions.Protocol):
    '''Properties for the SpiderAjaxConfig construct.

    :interface: ISpiderAjaxProps
    :property: {ISpiderAjax} spiderAjax - The SpiderAjax configuration.
    '''

    @builtins.property
    @jsii.member(jsii_name="spiderAjax")
    def spider_ajax(self) -> ISpiderAjax:
        ...

    @spider_ajax.setter
    def spider_ajax(self, value: ISpiderAjax) -> None:
        ...


class _ISpiderAjaxPropsProxy:
    '''Properties for the SpiderAjaxConfig construct.

    :interface: ISpiderAjaxProps
    :property: {ISpiderAjax} spiderAjax - The SpiderAjax configuration.
    '''

    __jsii_type__: typing.ClassVar[str] = "zap-cdk.ISpiderAjaxProps"

    @builtins.property
    @jsii.member(jsii_name="spiderAjax")
    def spider_ajax(self) -> ISpiderAjax:
        return typing.cast(ISpiderAjax, jsii.get(self, "spiderAjax"))

    @spider_ajax.setter
    def spider_ajax(self, value: ISpiderAjax) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0024047e6697fa406fa4609cd4d1b657da835ea74b47f4b622cd3207896da026)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "spiderAjax", value) # pyright: ignore[reportArgumentType]

# Adding a "__jsii_proxy_class__(): typing.Type" function to the interface
typing.cast(typing.Any, ISpiderAjaxProps).__jsii_proxy_class__ = lambda : _ISpiderAjaxPropsProxy


@jsii.interface(jsii_type="zap-cdk.ISpiderParameters")
class ISpiderParameters(typing_extensions.Protocol):
    '''Interface representing the parameters for a spider configuration.

    :interface: ISpiderParameters
    :property: {string} [userAgent] - The user agent to use in requests, default: '' (use the default ZAP one).
    '''

    @builtins.property
    @jsii.member(jsii_name="acceptCookies")
    def accept_cookies(self) -> typing.Optional[builtins.bool]:
        ...

    @accept_cookies.setter
    def accept_cookies(self, value: typing.Optional[builtins.bool]) -> None:
        ...

    @builtins.property
    @jsii.member(jsii_name="context")
    def context(self) -> typing.Optional[builtins.str]:
        ...

    @context.setter
    def context(self, value: typing.Optional[builtins.str]) -> None:
        ...

    @builtins.property
    @jsii.member(jsii_name="handleODataParametersVisited")
    def handle_o_data_parameters_visited(self) -> typing.Optional[builtins.bool]:
        ...

    @handle_o_data_parameters_visited.setter
    def handle_o_data_parameters_visited(
        self,
        value: typing.Optional[builtins.bool],
    ) -> None:
        ...

    @builtins.property
    @jsii.member(jsii_name="handleParameters")
    def handle_parameters(self) -> typing.Optional[builtins.str]:
        ...

    @handle_parameters.setter
    def handle_parameters(self, value: typing.Optional[builtins.str]) -> None:
        ...

    @builtins.property
    @jsii.member(jsii_name="logoutAvoidance")
    def logout_avoidance(self) -> typing.Optional[builtins.bool]:
        ...

    @logout_avoidance.setter
    def logout_avoidance(self, value: typing.Optional[builtins.bool]) -> None:
        ...

    @builtins.property
    @jsii.member(jsii_name="maxChildren")
    def max_children(self) -> typing.Optional[jsii.Number]:
        ...

    @max_children.setter
    def max_children(self, value: typing.Optional[jsii.Number]) -> None:
        ...

    @builtins.property
    @jsii.member(jsii_name="maxDepth")
    def max_depth(self) -> typing.Optional[jsii.Number]:
        ...

    @max_depth.setter
    def max_depth(self, value: typing.Optional[jsii.Number]) -> None:
        ...

    @builtins.property
    @jsii.member(jsii_name="maxDuration")
    def max_duration(self) -> typing.Optional[jsii.Number]:
        ...

    @max_duration.setter
    def max_duration(self, value: typing.Optional[jsii.Number]) -> None:
        ...

    @builtins.property
    @jsii.member(jsii_name="maxParseSizeBytes")
    def max_parse_size_bytes(self) -> typing.Optional[jsii.Number]:
        ...

    @max_parse_size_bytes.setter
    def max_parse_size_bytes(self, value: typing.Optional[jsii.Number]) -> None:
        ...

    @builtins.property
    @jsii.member(jsii_name="parseComments")
    def parse_comments(self) -> typing.Optional[builtins.bool]:
        ...

    @parse_comments.setter
    def parse_comments(self, value: typing.Optional[builtins.bool]) -> None:
        ...

    @builtins.property
    @jsii.member(jsii_name="parseDsStore")
    def parse_ds_store(self) -> typing.Optional[builtins.bool]:
        ...

    @parse_ds_store.setter
    def parse_ds_store(self, value: typing.Optional[builtins.bool]) -> None:
        ...

    @builtins.property
    @jsii.member(jsii_name="parseGit")
    def parse_git(self) -> typing.Optional[builtins.bool]:
        ...

    @parse_git.setter
    def parse_git(self, value: typing.Optional[builtins.bool]) -> None:
        ...

    @builtins.property
    @jsii.member(jsii_name="parseRobotsTxt")
    def parse_robots_txt(self) -> typing.Optional[builtins.bool]:
        ...

    @parse_robots_txt.setter
    def parse_robots_txt(self, value: typing.Optional[builtins.bool]) -> None:
        ...

    @builtins.property
    @jsii.member(jsii_name="parseSitemapXml")
    def parse_sitemap_xml(self) -> typing.Optional[builtins.bool]:
        ...

    @parse_sitemap_xml.setter
    def parse_sitemap_xml(self, value: typing.Optional[builtins.bool]) -> None:
        ...

    @builtins.property
    @jsii.member(jsii_name="parseSVNEntries")
    def parse_svn_entries(self) -> typing.Optional[builtins.bool]:
        ...

    @parse_svn_entries.setter
    def parse_svn_entries(self, value: typing.Optional[builtins.bool]) -> None:
        ...

    @builtins.property
    @jsii.member(jsii_name="postForm")
    def post_form(self) -> typing.Optional[builtins.bool]:
        ...

    @post_form.setter
    def post_form(self, value: typing.Optional[builtins.bool]) -> None:
        ...

    @builtins.property
    @jsii.member(jsii_name="processForm")
    def process_form(self) -> typing.Optional[builtins.bool]:
        ...

    @process_form.setter
    def process_form(self, value: typing.Optional[builtins.bool]) -> None:
        ...

    @builtins.property
    @jsii.member(jsii_name="sendRefererHeader")
    def send_referer_header(self) -> typing.Optional[builtins.bool]:
        ...

    @send_referer_header.setter
    def send_referer_header(self, value: typing.Optional[builtins.bool]) -> None:
        ...

    @builtins.property
    @jsii.member(jsii_name="threadCount")
    def thread_count(self) -> typing.Optional[jsii.Number]:
        ...

    @thread_count.setter
    def thread_count(self, value: typing.Optional[jsii.Number]) -> None:
        ...

    @builtins.property
    @jsii.member(jsii_name="url")
    def url(self) -> typing.Optional[builtins.str]:
        ...

    @url.setter
    def url(self, value: typing.Optional[builtins.str]) -> None:
        ...

    @builtins.property
    @jsii.member(jsii_name="user")
    def user(self) -> typing.Optional[builtins.str]:
        ...

    @user.setter
    def user(self, value: typing.Optional[builtins.str]) -> None:
        ...

    @builtins.property
    @jsii.member(jsii_name="userAgent")
    def user_agent(self) -> typing.Optional[builtins.str]:
        ...

    @user_agent.setter
    def user_agent(self, value: typing.Optional[builtins.str]) -> None:
        ...


class _ISpiderParametersProxy:
    '''Interface representing the parameters for a spider configuration.

    :interface: ISpiderParameters
    :property: {string} [userAgent] - The user agent to use in requests, default: '' (use the default ZAP one).
    '''

    __jsii_type__: typing.ClassVar[str] = "zap-cdk.ISpiderParameters"

    @builtins.property
    @jsii.member(jsii_name="acceptCookies")
    def accept_cookies(self) -> typing.Optional[builtins.bool]:
        return typing.cast(typing.Optional[builtins.bool], jsii.get(self, "acceptCookies"))

    @accept_cookies.setter
    def accept_cookies(self, value: typing.Optional[builtins.bool]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9d896a0fbb35213dd1fe92cccdb086b33d38daf93225de4166d2c995bb77563a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "acceptCookies", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="context")
    def context(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "context"))

    @context.setter
    def context(self, value: typing.Optional[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f6363c51ad61a91cc91d8a158451082356f1ddae6326ef26e31ecc6227366dec)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "context", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="handleODataParametersVisited")
    def handle_o_data_parameters_visited(self) -> typing.Optional[builtins.bool]:
        return typing.cast(typing.Optional[builtins.bool], jsii.get(self, "handleODataParametersVisited"))

    @handle_o_data_parameters_visited.setter
    def handle_o_data_parameters_visited(
        self,
        value: typing.Optional[builtins.bool],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__cf63f4af3bafd8b71e7dd8e2c5ed38a2dc519ef5514a1e974b838dff47c04200)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "handleODataParametersVisited", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="handleParameters")
    def handle_parameters(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "handleParameters"))

    @handle_parameters.setter
    def handle_parameters(self, value: typing.Optional[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__70b78b942b6e5d2e7f6da1451c201b0a5dde56bc984565ff1983c82bebc4f625)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "handleParameters", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="logoutAvoidance")
    def logout_avoidance(self) -> typing.Optional[builtins.bool]:
        return typing.cast(typing.Optional[builtins.bool], jsii.get(self, "logoutAvoidance"))

    @logout_avoidance.setter
    def logout_avoidance(self, value: typing.Optional[builtins.bool]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c6f18da91f77425099fd1f322a76c47c6a7388faba96a4c16f30e715cab32cf4)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "logoutAvoidance", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="maxChildren")
    def max_children(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "maxChildren"))

    @max_children.setter
    def max_children(self, value: typing.Optional[jsii.Number]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3f4800b768bc52283a0e8eb4e77c0d6873d8ed02623a2a76360748bdab59ae06)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "maxChildren", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="maxDepth")
    def max_depth(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "maxDepth"))

    @max_depth.setter
    def max_depth(self, value: typing.Optional[jsii.Number]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__cb67cbc65ff4e7bfdff73e82273417699ebce41e4c7f03c46107625b99d065b9)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "maxDepth", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="maxDuration")
    def max_duration(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "maxDuration"))

    @max_duration.setter
    def max_duration(self, value: typing.Optional[jsii.Number]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__66d354412e708b08df7248e3aa56c75efcdbf033935c1324f7aed48f24d223b1)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "maxDuration", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="maxParseSizeBytes")
    def max_parse_size_bytes(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "maxParseSizeBytes"))

    @max_parse_size_bytes.setter
    def max_parse_size_bytes(self, value: typing.Optional[jsii.Number]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e340c30337eb67e7e1f1dc49e7d7d289a6aff6191e38fb8fbc527e64c17edee4)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "maxParseSizeBytes", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="parseComments")
    def parse_comments(self) -> typing.Optional[builtins.bool]:
        return typing.cast(typing.Optional[builtins.bool], jsii.get(self, "parseComments"))

    @parse_comments.setter
    def parse_comments(self, value: typing.Optional[builtins.bool]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__caa9194666ff47908e4fabe8292dba81f92e26eb4cc670140e2ff855f24b76b3)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "parseComments", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="parseDsStore")
    def parse_ds_store(self) -> typing.Optional[builtins.bool]:
        return typing.cast(typing.Optional[builtins.bool], jsii.get(self, "parseDsStore"))

    @parse_ds_store.setter
    def parse_ds_store(self, value: typing.Optional[builtins.bool]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2bed6e2edebf08d5aa92b8be051ad4741521d89692fefe8f59e0836373667a0f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "parseDsStore", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="parseGit")
    def parse_git(self) -> typing.Optional[builtins.bool]:
        return typing.cast(typing.Optional[builtins.bool], jsii.get(self, "parseGit"))

    @parse_git.setter
    def parse_git(self, value: typing.Optional[builtins.bool]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__96a8864200042aea37a91e614da4348ce5bcaa9e8b7f986a6542764009091f09)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "parseGit", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="parseRobotsTxt")
    def parse_robots_txt(self) -> typing.Optional[builtins.bool]:
        return typing.cast(typing.Optional[builtins.bool], jsii.get(self, "parseRobotsTxt"))

    @parse_robots_txt.setter
    def parse_robots_txt(self, value: typing.Optional[builtins.bool]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__dd165a4b46f09d1c9792a6f0db3db1cdf2684066419855abc6e4379d7f9b465f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "parseRobotsTxt", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="parseSitemapXml")
    def parse_sitemap_xml(self) -> typing.Optional[builtins.bool]:
        return typing.cast(typing.Optional[builtins.bool], jsii.get(self, "parseSitemapXml"))

    @parse_sitemap_xml.setter
    def parse_sitemap_xml(self, value: typing.Optional[builtins.bool]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ecbdeed364e1622a7f03a7d0ffdaa0ad4eb7e7ce331d9c187f0689f2bca2e341)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "parseSitemapXml", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="parseSVNEntries")
    def parse_svn_entries(self) -> typing.Optional[builtins.bool]:
        return typing.cast(typing.Optional[builtins.bool], jsii.get(self, "parseSVNEntries"))

    @parse_svn_entries.setter
    def parse_svn_entries(self, value: typing.Optional[builtins.bool]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__141bc718b2a14f9522ec6a416a03d698f427926094ee23fb14bddf4b7ea81976)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "parseSVNEntries", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="postForm")
    def post_form(self) -> typing.Optional[builtins.bool]:
        return typing.cast(typing.Optional[builtins.bool], jsii.get(self, "postForm"))

    @post_form.setter
    def post_form(self, value: typing.Optional[builtins.bool]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5423b002d3bfb1fd4923568d66ba567ecd16dd53a224fd8f0ca48446fab592dc)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "postForm", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="processForm")
    def process_form(self) -> typing.Optional[builtins.bool]:
        return typing.cast(typing.Optional[builtins.bool], jsii.get(self, "processForm"))

    @process_form.setter
    def process_form(self, value: typing.Optional[builtins.bool]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f357ab70612af39c4d161473008b1bb615aee0e1ee3585cd4d6eaa3b32589334)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "processForm", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="sendRefererHeader")
    def send_referer_header(self) -> typing.Optional[builtins.bool]:
        return typing.cast(typing.Optional[builtins.bool], jsii.get(self, "sendRefererHeader"))

    @send_referer_header.setter
    def send_referer_header(self, value: typing.Optional[builtins.bool]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b9e23cbfd125236628a888f0dfb1382a28f07b40bf1bd33fe3237fcadb28c9e7)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "sendRefererHeader", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="threadCount")
    def thread_count(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "threadCount"))

    @thread_count.setter
    def thread_count(self, value: typing.Optional[jsii.Number]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c09658779f26e58dfa2345745172068799715d9bc7218cc1b322f1959365702d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "threadCount", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="url")
    def url(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "url"))

    @url.setter
    def url(self, value: typing.Optional[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5e13209ba0d55738de3bdc7581f0fca274a978b95ac6de3f5e14caa33166b3a5)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "url", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="user")
    def user(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "user"))

    @user.setter
    def user(self, value: typing.Optional[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__14ffe2eab23a29e74fc48b60522ec75725b744e0f3ab720ea835a5d3c09b3286)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "user", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="userAgent")
    def user_agent(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "userAgent"))

    @user_agent.setter
    def user_agent(self, value: typing.Optional[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__34954a033ee2c76bbfa74a8e8bed751693c8c46897837a80c59f329527d743b1)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "userAgent", value) # pyright: ignore[reportArgumentType]

# Adding a "__jsii_proxy_class__(): typing.Type" function to the interface
typing.cast(typing.Any, ISpiderParameters).__jsii_proxy_class__ = lambda : _ISpiderParametersProxy


@jsii.interface(jsii_type="zap-cdk.ISpiderTest")
class ISpiderTest(typing_extensions.Protocol):
    '''Interface representing a test configuration for the spider.

    :interface: ISpiderTest
    :property: {'warn' | 'error' | 'info'} onFail - One of 'warn', 'error', 'info', mandatory.
    '''

    @builtins.property
    @jsii.member(jsii_name="onFail")
    def on_fail(self) -> builtins.str:
        ...

    @on_fail.setter
    def on_fail(self, value: builtins.str) -> None:
        ...

    @builtins.property
    @jsii.member(jsii_name="operator")
    def operator(self) -> builtins.str:
        ...

    @operator.setter
    def operator(self, value: builtins.str) -> None:
        ...

    @builtins.property
    @jsii.member(jsii_name="statistic")
    def statistic(self) -> builtins.str:
        ...

    @statistic.setter
    def statistic(self, value: builtins.str) -> None:
        ...

    @builtins.property
    @jsii.member(jsii_name="type")
    def type(self) -> builtins.str:
        ...

    @type.setter
    def type(self, value: builtins.str) -> None:
        ...

    @builtins.property
    @jsii.member(jsii_name="value")
    def value(self) -> jsii.Number:
        ...

    @value.setter
    def value(self, value: jsii.Number) -> None:
        ...

    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> typing.Optional[builtins.str]:
        ...

    @name.setter
    def name(self, value: typing.Optional[builtins.str]) -> None:
        ...


class _ISpiderTestProxy:
    '''Interface representing a test configuration for the spider.

    :interface: ISpiderTest
    :property: {'warn' | 'error' | 'info'} onFail - One of 'warn', 'error', 'info', mandatory.
    '''

    __jsii_type__: typing.ClassVar[str] = "zap-cdk.ISpiderTest"

    @builtins.property
    @jsii.member(jsii_name="onFail")
    def on_fail(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "onFail"))

    @on_fail.setter
    def on_fail(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__fa26ee714a2dc275fe5fe234a7104a7d2543897c5fa98244477b144871060391)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "onFail", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="operator")
    def operator(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "operator"))

    @operator.setter
    def operator(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__00a2b5c3836f46d5cd6f0e2355f62148d475f9bacc707d74af97873541d070ff)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "operator", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="statistic")
    def statistic(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "statistic"))

    @statistic.setter
    def statistic(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a5295b60c0514207b992db5ce7e3fd11bded69a4db8978db9789e6cc95d5d423)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "statistic", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="type")
    def type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "type"))

    @type.setter
    def type(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d396d8df17926319338f7dae070391766858004ead1878c9f1a7a372f0ea978a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "type", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="value")
    def value(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "value"))

    @value.setter
    def value(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a0c6df805e70f9a0eb782705ac45ecb2d195b63d98661c5c29e3aedcd530cc77)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "value", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "name"))

    @name.setter
    def name(self, value: typing.Optional[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b07630a03143c54f19776bc480a088410376badb88d0c9342ff0c3891773f590)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "name", value) # pyright: ignore[reportArgumentType]

# Adding a "__jsii_proxy_class__(): typing.Type" function to the interface
typing.cast(typing.Any, ISpiderTest).__jsii_proxy_class__ = lambda : _ISpiderTestProxy


@jsii.interface(jsii_type="zap-cdk.IStatisticsTest")
class IStatisticsTest(typing_extensions.Protocol):
    '''Interface for statistics tests.

    Example YAML representation::

       - name: 'test one'                      # Name of the test, optional
         type: stats                           # Specifies that the test is of type 'stats'
         statistic: 'stats.addon.something'    # Name of an integer / long statistic
         site:                                 # Name of the site for site specific tests, supports vars
         operator: '>='                        # One of '==', '!=', '>=', '>', '<', '<='
         value: 10                             # Value to compare statistic against
         onFail: 'info'                        # String: One of 'warn', 'error', 'info', mandatory

    :interface: IStatisticsTest
    :property: {OnFailType} onFail - Action to take on failure, mandatory.
    '''

    @builtins.property
    @jsii.member(jsii_name="onFail")
    def on_fail(self) -> builtins.str:
        ...

    @on_fail.setter
    def on_fail(self, value: builtins.str) -> None:
        ...

    @builtins.property
    @jsii.member(jsii_name="operator")
    def operator(self) -> builtins.str:
        ...

    @operator.setter
    def operator(self, value: builtins.str) -> None:
        ...

    @builtins.property
    @jsii.member(jsii_name="statistic")
    def statistic(self) -> builtins.str:
        ...

    @statistic.setter
    def statistic(self, value: builtins.str) -> None:
        ...

    @builtins.property
    @jsii.member(jsii_name="type")
    def type(self) -> builtins.str:
        ...

    @type.setter
    def type(self, value: builtins.str) -> None:
        ...

    @builtins.property
    @jsii.member(jsii_name="value")
    def value(self) -> jsii.Number:
        ...

    @value.setter
    def value(self, value: jsii.Number) -> None:
        ...

    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> typing.Optional[builtins.str]:
        ...

    @name.setter
    def name(self, value: typing.Optional[builtins.str]) -> None:
        ...

    @builtins.property
    @jsii.member(jsii_name="site")
    def site(self) -> typing.Optional[builtins.str]:
        ...

    @site.setter
    def site(self, value: typing.Optional[builtins.str]) -> None:
        ...


class _IStatisticsTestProxy:
    '''Interface for statistics tests.

    Example YAML representation::

       - name: 'test one'                      # Name of the test, optional
         type: stats                           # Specifies that the test is of type 'stats'
         statistic: 'stats.addon.something'    # Name of an integer / long statistic
         site:                                 # Name of the site for site specific tests, supports vars
         operator: '>='                        # One of '==', '!=', '>=', '>', '<', '<='
         value: 10                             # Value to compare statistic against
         onFail: 'info'                        # String: One of 'warn', 'error', 'info', mandatory

    :interface: IStatisticsTest
    :property: {OnFailType} onFail - Action to take on failure, mandatory.
    '''

    __jsii_type__: typing.ClassVar[str] = "zap-cdk.IStatisticsTest"

    @builtins.property
    @jsii.member(jsii_name="onFail")
    def on_fail(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "onFail"))

    @on_fail.setter
    def on_fail(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f82f19abaeccbd97592b1366602f8f025f4bf49beafef96f2897293841ab1db5)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "onFail", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="operator")
    def operator(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "operator"))

    @operator.setter
    def operator(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8048954b297fa497689adf2dae43ecb43932498847bebe1fcc854ce08ead9881)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "operator", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="statistic")
    def statistic(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "statistic"))

    @statistic.setter
    def statistic(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__502addf944962ff1c9124f01738d68d6f8dea0508b240f64d49d54eea3dc5d8c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "statistic", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="type")
    def type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "type"))

    @type.setter
    def type(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8334f725128893232a022f1e9f8907a0f259c852e049b693692b58e372552cb0)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "type", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="value")
    def value(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "value"))

    @value.setter
    def value(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e599163506538036cafb75c3c5f2e7eb204a1f2addcfca92393aca1e18b00e0a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "value", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "name"))

    @name.setter
    def name(self, value: typing.Optional[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__532aaaa9d93caa5627ce5f4cc2f1053926ea5cf6b750313553f98aafc71fdad6)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "name", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="site")
    def site(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "site"))

    @site.setter
    def site(self, value: typing.Optional[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__555268c139ca00096816460e0258e02213f0dc8bcfef6e93fff953d1600eb309)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "site", value) # pyright: ignore[reportArgumentType]

# Adding a "__jsii_proxy_class__(): typing.Type" function to the interface
typing.cast(typing.Any, IStatisticsTest).__jsii_proxy_class__ = lambda : _IStatisticsTestProxy


@jsii.interface(jsii_type="zap-cdk.ITechnology")
class ITechnology(typing_extensions.Protocol):
    '''
    :interface:

    ITechnology
    Represents the technology details for the scanning context.
    :property: {string[]} [include] - List of tech to include.
    '''

    @builtins.property
    @jsii.member(jsii_name="exclude")
    def exclude(self) -> typing.Optional[typing.List[builtins.str]]:
        ...

    @exclude.setter
    def exclude(self, value: typing.Optional[typing.List[builtins.str]]) -> None:
        ...

    @builtins.property
    @jsii.member(jsii_name="include")
    def include(self) -> typing.Optional[typing.List[builtins.str]]:
        ...

    @include.setter
    def include(self, value: typing.Optional[typing.List[builtins.str]]) -> None:
        ...


class _ITechnologyProxy:
    '''
    :interface:

    ITechnology
    Represents the technology details for the scanning context.
    :property: {string[]} [include] - List of tech to include.
    '''

    __jsii_type__: typing.ClassVar[str] = "zap-cdk.ITechnology"

    @builtins.property
    @jsii.member(jsii_name="exclude")
    def exclude(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "exclude"))

    @exclude.setter
    def exclude(self, value: typing.Optional[typing.List[builtins.str]]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__dd782cc74977e26423b6f3c158dffba5e46614c0291d02cde8a3ca723eac35e1)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "exclude", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="include")
    def include(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "include"))

    @include.setter
    def include(self, value: typing.Optional[typing.List[builtins.str]]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a9d3e723be6606f42ef7e006227f411dad3774ca535315a7babc2d872cf00dec)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "include", value) # pyright: ignore[reportArgumentType]

# Adding a "__jsii_proxy_class__(): typing.Type" function to the interface
typing.cast(typing.Any, ITechnology).__jsii_proxy_class__ = lambda : _ITechnologyProxy


@jsii.interface(jsii_type="zap-cdk.ITotpConfig")
class ITotpConfig(typing_extensions.Protocol):
    '''
    :interface:

    ITotpConfig
    Represents the TOTP (Time-based One-Time Password) configuration for a user.
    :property: {string} [algorithm] - Algorithm, default: SHA1.
    '''

    @builtins.property
    @jsii.member(jsii_name="secret")
    def secret(self) -> builtins.str:
        ...

    @secret.setter
    def secret(self, value: builtins.str) -> None:
        ...

    @builtins.property
    @jsii.member(jsii_name="algorithm")
    def algorithm(self) -> typing.Optional[builtins.str]:
        ...

    @algorithm.setter
    def algorithm(self, value: typing.Optional[builtins.str]) -> None:
        ...

    @builtins.property
    @jsii.member(jsii_name="digits")
    def digits(self) -> typing.Optional[jsii.Number]:
        ...

    @digits.setter
    def digits(self, value: typing.Optional[jsii.Number]) -> None:
        ...

    @builtins.property
    @jsii.member(jsii_name="period")
    def period(self) -> typing.Optional[jsii.Number]:
        ...

    @period.setter
    def period(self, value: typing.Optional[jsii.Number]) -> None:
        ...


class _ITotpConfigProxy:
    '''
    :interface:

    ITotpConfig
    Represents the TOTP (Time-based One-Time Password) configuration for a user.
    :property: {string} [algorithm] - Algorithm, default: SHA1.
    '''

    __jsii_type__: typing.ClassVar[str] = "zap-cdk.ITotpConfig"

    @builtins.property
    @jsii.member(jsii_name="secret")
    def secret(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "secret"))

    @secret.setter
    def secret(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__caa84775fd057b8023dd4808b0de88dc83889852e6a33b1b355765f250ab4433)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "secret", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="algorithm")
    def algorithm(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "algorithm"))

    @algorithm.setter
    def algorithm(self, value: typing.Optional[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5ff2645a048e06f8fb1c38ea9538dc0d52d55993a3c6cbd720b5f89dc9cc5d58)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "algorithm", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="digits")
    def digits(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "digits"))

    @digits.setter
    def digits(self, value: typing.Optional[jsii.Number]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c3fc4b6095a92521b7c5566f4c533997c8e5a8e40f46cb167315f4f1f1b3e657)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "digits", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="period")
    def period(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "period"))

    @period.setter
    def period(self, value: typing.Optional[jsii.Number]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8781a59cfd1f582546f670b6d7160c042c87d189750aadf4049629531a20ee2d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "period", value) # pyright: ignore[reportArgumentType]

# Adding a "__jsii_proxy_class__(): typing.Type" function to the interface
typing.cast(typing.Any, ITotpConfig).__jsii_proxy_class__ = lambda : _ITotpConfigProxy


@jsii.interface(jsii_type="zap-cdk.IUrlQueryStringAndDataDrivenNodes")
class IUrlQueryStringAndDataDrivenNodes(typing_extensions.Protocol):
    '''Configuration options for scanning URL query strings and Data Driven Nodes (DDNs).

    :interface: IUrlQueryStringAndDataDrivenNodes
    :property: {boolean} [odata] - If OData query filters should be scanned. Default: true
    '''

    @builtins.property
    @jsii.member(jsii_name="addParam")
    def add_param(self) -> typing.Optional[builtins.bool]:
        '''If a query parameter should be added if none present.

        Default: false
        '''
        ...

    @add_param.setter
    def add_param(self, value: typing.Optional[builtins.bool]) -> None:
        ...

    @builtins.property
    @jsii.member(jsii_name="enabled")
    def enabled(self) -> typing.Optional[builtins.bool]:
        '''If query parameters and DDNs scanning should be enabled.

        Default: true
        '''
        ...

    @enabled.setter
    def enabled(self, value: typing.Optional[builtins.bool]) -> None:
        ...

    @builtins.property
    @jsii.member(jsii_name="odata")
    def odata(self) -> typing.Optional[builtins.bool]:
        '''If OData query filters should be scanned.

        Default: true
        '''
        ...

    @odata.setter
    def odata(self, value: typing.Optional[builtins.bool]) -> None:
        ...


class _IUrlQueryStringAndDataDrivenNodesProxy:
    '''Configuration options for scanning URL query strings and Data Driven Nodes (DDNs).

    :interface: IUrlQueryStringAndDataDrivenNodes
    :property: {boolean} [odata] - If OData query filters should be scanned. Default: true
    '''

    __jsii_type__: typing.ClassVar[str] = "zap-cdk.IUrlQueryStringAndDataDrivenNodes"

    @builtins.property
    @jsii.member(jsii_name="addParam")
    def add_param(self) -> typing.Optional[builtins.bool]:
        '''If a query parameter should be added if none present.

        Default: false
        '''
        return typing.cast(typing.Optional[builtins.bool], jsii.get(self, "addParam"))

    @add_param.setter
    def add_param(self, value: typing.Optional[builtins.bool]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__aab6b3320c8b5ed180393e3c8ec006f176de4327b6a5b590518821d90402ce62)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "addParam", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="enabled")
    def enabled(self) -> typing.Optional[builtins.bool]:
        '''If query parameters and DDNs scanning should be enabled.

        Default: true
        '''
        return typing.cast(typing.Optional[builtins.bool], jsii.get(self, "enabled"))

    @enabled.setter
    def enabled(self, value: typing.Optional[builtins.bool]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6c9513a7ba0dde9719e51014f59729062305e49ba15efc3c6b984a2b9a3d7afa)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "enabled", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="odata")
    def odata(self) -> typing.Optional[builtins.bool]:
        '''If OData query filters should be scanned.

        Default: true
        '''
        return typing.cast(typing.Optional[builtins.bool], jsii.get(self, "odata"))

    @odata.setter
    def odata(self, value: typing.Optional[builtins.bool]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9cc7e596f4e2e98b431d1d318feacf1d54de3f07128a7915e5f490682a616c38)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "odata", value) # pyright: ignore[reportArgumentType]

# Adding a "__jsii_proxy_class__(): typing.Type" function to the interface
typing.cast(typing.Any, IUrlQueryStringAndDataDrivenNodes).__jsii_proxy_class__ = lambda : _IUrlQueryStringAndDataDrivenNodesProxy


@jsii.interface(jsii_type="zap-cdk.IUrlTest")
class IUrlTest(typing_extensions.Protocol):
    '''Interface for URL tests.

    Example YAML representation::

       - name: 'test one'                      # Name of the test, optional
         type: url                             # Specifies that the test is of type 'url'
         url: http://www.example.com/path      # String: The URL to be tested.
         operator: 'and'                       # One of 'and', 'or', default is 'or'
         requestHeaderRegex:                   # String: The regular expression to be matched in the request header, optional
         requestBodyRegex:                     # String: The regular expression to be matched in the request body, optional
         responseHeaderRegex:                  # String: The regular expression to be matched in the response header, optional
         responseBodyRegex:                    # String: The regular expression to be matched in the response body, optional
         onFail: 'info'                        # String: One of 'warn', 'error', 'info', mandatory

    :interface: IUrlTest
    :property: {OnFailType} onFail - Action to take on failure, mandatory.
    '''

    @builtins.property
    @jsii.member(jsii_name="onFail")
    def on_fail(self) -> builtins.str:
        ...

    @on_fail.setter
    def on_fail(self, value: builtins.str) -> None:
        ...

    @builtins.property
    @jsii.member(jsii_name="operator")
    def operator(self) -> builtins.str:
        ...

    @operator.setter
    def operator(self, value: builtins.str) -> None:
        ...

    @builtins.property
    @jsii.member(jsii_name="type")
    def type(self) -> builtins.str:
        ...

    @type.setter
    def type(self, value: builtins.str) -> None:
        ...

    @builtins.property
    @jsii.member(jsii_name="url")
    def url(self) -> builtins.str:
        ...

    @url.setter
    def url(self, value: builtins.str) -> None:
        ...

    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> typing.Optional[builtins.str]:
        ...

    @name.setter
    def name(self, value: typing.Optional[builtins.str]) -> None:
        ...

    @builtins.property
    @jsii.member(jsii_name="requestBodyRegex")
    def request_body_regex(self) -> typing.Optional[builtins.str]:
        ...

    @request_body_regex.setter
    def request_body_regex(self, value: typing.Optional[builtins.str]) -> None:
        ...

    @builtins.property
    @jsii.member(jsii_name="requestHeaderRegex")
    def request_header_regex(self) -> typing.Optional[builtins.str]:
        ...

    @request_header_regex.setter
    def request_header_regex(self, value: typing.Optional[builtins.str]) -> None:
        ...

    @builtins.property
    @jsii.member(jsii_name="responseBodyRegex")
    def response_body_regex(self) -> typing.Optional[builtins.str]:
        ...

    @response_body_regex.setter
    def response_body_regex(self, value: typing.Optional[builtins.str]) -> None:
        ...

    @builtins.property
    @jsii.member(jsii_name="responseHeaderRegex")
    def response_header_regex(self) -> typing.Optional[builtins.str]:
        ...

    @response_header_regex.setter
    def response_header_regex(self, value: typing.Optional[builtins.str]) -> None:
        ...


class _IUrlTestProxy:
    '''Interface for URL tests.

    Example YAML representation::

       - name: 'test one'                      # Name of the test, optional
         type: url                             # Specifies that the test is of type 'url'
         url: http://www.example.com/path      # String: The URL to be tested.
         operator: 'and'                       # One of 'and', 'or', default is 'or'
         requestHeaderRegex:                   # String: The regular expression to be matched in the request header, optional
         requestBodyRegex:                     # String: The regular expression to be matched in the request body, optional
         responseHeaderRegex:                  # String: The regular expression to be matched in the response header, optional
         responseBodyRegex:                    # String: The regular expression to be matched in the response body, optional
         onFail: 'info'                        # String: One of 'warn', 'error', 'info', mandatory

    :interface: IUrlTest
    :property: {OnFailType} onFail - Action to take on failure, mandatory.
    '''

    __jsii_type__: typing.ClassVar[str] = "zap-cdk.IUrlTest"

    @builtins.property
    @jsii.member(jsii_name="onFail")
    def on_fail(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "onFail"))

    @on_fail.setter
    def on_fail(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e83f530d6fd4975a5e9d833601a1ba0da602461338158552839c08cc7c68ad2a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "onFail", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="operator")
    def operator(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "operator"))

    @operator.setter
    def operator(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__803d555a4687b09617efeca6555c9a0c547d208cce4b3fcba260e656293b0431)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "operator", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="type")
    def type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "type"))

    @type.setter
    def type(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__bf82256371e8af18d733cf6e3576565fb3fee322e1407ba32d4a58936e43706a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "type", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="url")
    def url(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "url"))

    @url.setter
    def url(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b6391c87993381eb2a1cfbce502581139547eeb293036255195358364394c1a2)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "url", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "name"))

    @name.setter
    def name(self, value: typing.Optional[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f6713b2f9883a94ac79a38204e71ea4ae51126ab1edd725ba4a3212febdbe452)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "name", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="requestBodyRegex")
    def request_body_regex(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "requestBodyRegex"))

    @request_body_regex.setter
    def request_body_regex(self, value: typing.Optional[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__19e0f22afb0ccb009b081a3a2dde585905ec7100821d6fe298055b70203de58b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "requestBodyRegex", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="requestHeaderRegex")
    def request_header_regex(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "requestHeaderRegex"))

    @request_header_regex.setter
    def request_header_regex(self, value: typing.Optional[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__137fca5161fc7e4ca23828405348297e920b18f1756c88fe540ddc51cb6236a6)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "requestHeaderRegex", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="responseBodyRegex")
    def response_body_regex(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "responseBodyRegex"))

    @response_body_regex.setter
    def response_body_regex(self, value: typing.Optional[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__40cb0d93da14f245fdd64661d854a8ff7a48ca8ae17e8422d6d7abb3f1b84729)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "responseBodyRegex", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="responseHeaderRegex")
    def response_header_regex(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "responseHeaderRegex"))

    @response_header_regex.setter
    def response_header_regex(self, value: typing.Optional[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__01266709283dc90708ae25e398a73b2fefe17d335fdedf6e00e53105c9042b98)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "responseHeaderRegex", value) # pyright: ignore[reportArgumentType]

# Adding a "__jsii_proxy_class__(): typing.Type" function to the interface
typing.cast(typing.Any, IUrlTest).__jsii_proxy_class__ = lambda : _IUrlTestProxy


@jsii.interface(jsii_type="zap-cdk.IUserCredentials")
class IUserCredentials(typing_extensions.Protocol):
    '''
    :interface:

    IUserCredentials
    Represents the credentials for a user.
    :property: {ITotpConfig} [totp] - Optional TOTP configuration.
    '''

    @builtins.property
    @jsii.member(jsii_name="password")
    def password(self) -> builtins.str:
        ...

    @password.setter
    def password(self, value: builtins.str) -> None:
        ...

    @builtins.property
    @jsii.member(jsii_name="username")
    def username(self) -> builtins.str:
        ...

    @username.setter
    def username(self, value: builtins.str) -> None:
        ...

    @builtins.property
    @jsii.member(jsii_name="totp")
    def totp(self) -> typing.Optional[ITotpConfig]:
        ...

    @totp.setter
    def totp(self, value: typing.Optional[ITotpConfig]) -> None:
        ...


class _IUserCredentialsProxy:
    '''
    :interface:

    IUserCredentials
    Represents the credentials for a user.
    :property: {ITotpConfig} [totp] - Optional TOTP configuration.
    '''

    __jsii_type__: typing.ClassVar[str] = "zap-cdk.IUserCredentials"

    @builtins.property
    @jsii.member(jsii_name="password")
    def password(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "password"))

    @password.setter
    def password(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6b7987528ff7f20ab7c9b57c03cb4200d426cfc4f42e4d087d1087d2e010bc2e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "password", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="username")
    def username(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "username"))

    @username.setter
    def username(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5cd6caa9ce412a3d7dbf5f4803c5781f7ad18ad5af3dd94d6eb44fb8022a7208)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "username", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="totp")
    def totp(self) -> typing.Optional[ITotpConfig]:
        return typing.cast(typing.Optional[ITotpConfig], jsii.get(self, "totp"))

    @totp.setter
    def totp(self, value: typing.Optional[ITotpConfig]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e75f8983aceb72f5d0a898866d8ef93bd886a0571063067b93fb841b37ea8bf1)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "totp", value) # pyright: ignore[reportArgumentType]

# Adding a "__jsii_proxy_class__(): typing.Type" function to the interface
typing.cast(typing.Any, IUserCredentials).__jsii_proxy_class__ = lambda : _IUserCredentialsProxy


@jsii.interface(jsii_type="zap-cdk.IZap")
class IZap(typing_extensions.Protocol):
    '''Interface representing the ZAP (Zed Attack Proxy) configuration.

    :interface: IZap
    :property: {IJob[]} jobs - The list of jobs to be executed.
    '''

    @builtins.property
    @jsii.member(jsii_name="env")
    def env(self) -> IEnvironment:
        ...

    @env.setter
    def env(self, value: IEnvironment) -> None:
        ...

    @builtins.property
    @jsii.member(jsii_name="jobs")
    def jobs(
        self,
    ) -> typing.List[typing.Union[IActiveScan, IActiveScanPolicy, IActiveScanConfig, ISpider, IDelay, IExitStatus, IExport, IGraphQL, IImport, IOpenAPI, IPassiveScanConfig, IPassiveScanWait, IPostman, IReplacer, IReport, IRequest, ISoap, ISpiderAjax, INewType]]:
        ...

    @jobs.setter
    def jobs(
        self,
        value: typing.List[typing.Union[IActiveScan, IActiveScanPolicy, IActiveScanConfig, ISpider, IDelay, IExitStatus, IExport, IGraphQL, IImport, IOpenAPI, IPassiveScanConfig, IPassiveScanWait, IPostman, IReplacer, IReport, IRequest, ISoap, ISpiderAjax, INewType]],
    ) -> None:
        ...


class _IZapProxy:
    '''Interface representing the ZAP (Zed Attack Proxy) configuration.

    :interface: IZap
    :property: {IJob[]} jobs - The list of jobs to be executed.
    '''

    __jsii_type__: typing.ClassVar[str] = "zap-cdk.IZap"

    @builtins.property
    @jsii.member(jsii_name="env")
    def env(self) -> IEnvironment:
        return typing.cast(IEnvironment, jsii.get(self, "env"))

    @env.setter
    def env(self, value: IEnvironment) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1c3d1768c8b547fb8817bdfa19adf45fd71dd0c16f8bec762030bcb045600f3a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "env", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="jobs")
    def jobs(
        self,
    ) -> typing.List[typing.Union[IActiveScan, IActiveScanPolicy, IActiveScanConfig, ISpider, IDelay, IExitStatus, IExport, IGraphQL, IImport, IOpenAPI, IPassiveScanConfig, IPassiveScanWait, IPostman, IReplacer, IReport, IRequest, ISoap, ISpiderAjax, INewType]]:
        return typing.cast(typing.List[typing.Union[IActiveScan, IActiveScanPolicy, IActiveScanConfig, ISpider, IDelay, IExitStatus, IExport, IGraphQL, IImport, IOpenAPI, IPassiveScanConfig, IPassiveScanWait, IPostman, IReplacer, IReport, IRequest, ISoap, ISpiderAjax, INewType]], jsii.get(self, "jobs"))

    @jobs.setter
    def jobs(
        self,
        value: typing.List[typing.Union[IActiveScan, IActiveScanPolicy, IActiveScanConfig, ISpider, IDelay, IExitStatus, IExport, IGraphQL, IImport, IOpenAPI, IPassiveScanConfig, IPassiveScanWait, IPostman, IReplacer, IReport, IRequest, ISoap, ISpiderAjax, INewType]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e10343c0aaa52fc59631fd2790032d49abc24601a170075c2307c3b55ab18e74)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "jobs", value) # pyright: ignore[reportArgumentType]

# Adding a "__jsii_proxy_class__(): typing.Type" function to the interface
typing.cast(typing.Any, IZap).__jsii_proxy_class__ = lambda : _IZapProxy


class ImportConfig(
    _constructs_77d1e7e8.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="zap-cdk.ImportConfig",
):
    '''Class representing the import configuration.

    :class: ImportConfig
    :extends: Construct
    '''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        props: IImportProps,
    ) -> None:
        '''Creates an instance of ImportConfig.

        :param scope: - The scope in which this construct is defined.
        :param id: - The ID of the construct.
        :param props: - The properties of the import configuration.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__26d928c212bff21972591897dd0fa374d6662598c7dd3a7d33a2229d5c555748)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
            check_type(argname="argument props", value=props, expected_type=type_hints["props"])
        jsii.create(self.__class__, self, [scope, id, props])

    @jsii.member(jsii_name="toYaml")
    def to_yaml(self) -> IImport:
        '''Converts the import configuration to YAML format.

        :return: The import configuration in YAML format.
        '''
        return typing.cast(IImport, jsii.invoke(self, "toYaml", []))

    @builtins.property
    @jsii.member(jsii_name="config")
    def config(self) -> IImport:
        return typing.cast(IImport, jsii.get(self, "config"))

    @config.setter
    def config(self, value: IImport) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__91f4aa3c97d70788796568533de68f0826274de23c38775784854ae1dd0e1d6d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "config", value) # pyright: ignore[reportArgumentType]


class OpenAPIConfig(
    _constructs_77d1e7e8.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="zap-cdk.OpenAPIConfig",
):
    '''Class representing the OpenAPI configuration.

    :class: OpenAPIConfig
    :extends: Construct
    '''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        props: IOpenAPIProps,
    ) -> None:
        '''Creates an instance of OpenAPIConfig.

        :param scope: - The scope in which this construct is defined.
        :param id: - The ID of the construct.
        :param props: - The properties of the OpenAPI configuration.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e84fd801092de50427019c50b1916f2044d763eb6faf4474e9e439fe613097df)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
            check_type(argname="argument props", value=props, expected_type=type_hints["props"])
        jsii.create(self.__class__, self, [scope, id, props])

    @jsii.member(jsii_name="toYaml")
    def to_yaml(self) -> IOpenAPI:
        return typing.cast(IOpenAPI, jsii.invoke(self, "toYaml", []))

    @builtins.property
    @jsii.member(jsii_name="config")
    def config(self) -> IOpenAPI:
        return typing.cast(IOpenAPI, jsii.get(self, "config"))

    @config.setter
    def config(self, value: IOpenAPI) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__862e0d1b2fabc46f6f0ec2ff29cd9ab00ce2e6d42ea979e19f3afcd195c45b49)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "config", value) # pyright: ignore[reportArgumentType]


class PassiveScanConfig(
    _constructs_77d1e7e8.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="zap-cdk.PassiveScanConfig",
):
    '''Class representing the passive scan configuration.

    :class: PassiveScanConfig
    :extends: Construct
    '''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        props: IPassiveScanConfigProps,
    ) -> None:
        '''Creates an instance of PassiveScanConfig.

        :param scope: - The scope in which this construct is defined.
        :param id: - The ID of the construct.
        :param props: - The properties of the passive scan configuration.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d7bda6e25a77f58d3d499466dc1cb176f766470ba980fd72caba067bc6b93160)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
            check_type(argname="argument props", value=props, expected_type=type_hints["props"])
        jsii.create(self.__class__, self, [scope, id, props])

    @jsii.member(jsii_name="toYaml")
    def to_yaml(self) -> IPassiveScanConfig:
        '''Converts the passive scan configuration to YAML format.

        :return: The passive scan configuration in YAML format.
        '''
        return typing.cast(IPassiveScanConfig, jsii.invoke(self, "toYaml", []))

    @builtins.property
    @jsii.member(jsii_name="config")
    def config(self) -> IPassiveScanConfig:
        return typing.cast(IPassiveScanConfig, jsii.get(self, "config"))

    @config.setter
    def config(self, value: IPassiveScanConfig) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__03175aafaf9dadbb01efc59110074f8f5abbd460ce318c55ff6120fc8f98f2a7)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "config", value) # pyright: ignore[reportArgumentType]


class PassiveScanWaitConfig(
    _constructs_77d1e7e8.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="zap-cdk.PassiveScanWaitConfig",
):
    '''Class representing the passive scan wait configuration.

    :class: PassiveScanWaitConfig
    :extends: Construct
    '''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        props: IPassiveScanWaitProps,
    ) -> None:
        '''Creates an instance of PassiveScanWaitConfig.

        :param scope: - The scope in which this construct is defined.
        :param id: - The ID of the construct.
        :param props: - The properties of the passive scan wait configuration.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__889cfef0a8742ab06135a0a1b35c8c51a892501a22c65438c53da4f42e0656e4)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
            check_type(argname="argument props", value=props, expected_type=type_hints["props"])
        jsii.create(self.__class__, self, [scope, id, props])

    @jsii.member(jsii_name="toYaml")
    def to_yaml(self) -> IPassiveScanWait:
        '''Converts the passive scan wait configuration to YAML format.

        :return: The passive scan wait configuration in YAML format.
        '''
        return typing.cast(IPassiveScanWait, jsii.invoke(self, "toYaml", []))

    @builtins.property
    @jsii.member(jsii_name="config")
    def config(self) -> IPassiveScanWait:
        return typing.cast(IPassiveScanWait, jsii.get(self, "config"))

    @config.setter
    def config(self, value: IPassiveScanWait) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f66e44b5e04a1d2c38c7d56ce6dc6e1687e41aec4899821d4efc493255a81af5)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "config", value) # pyright: ignore[reportArgumentType]


class PostmanConfig(
    _constructs_77d1e7e8.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="zap-cdk.PostmanConfig",
):
    '''Class representing the Postman configuration.

    :class: PostmanConfig
    :extends: Construct
    '''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        props: IPostmanProps,
    ) -> None:
        '''Creates an instance of PostmanConfig.

        :param scope: - The scope in which this construct is defined.
        :param id: - The ID of the construct.
        :param props: - The properties of the Postman configuration.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__47bbc432f94ea291f2ebb484f7405595ee72a015361643fa2ffc8e88e7174ef5)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
            check_type(argname="argument props", value=props, expected_type=type_hints["props"])
        jsii.create(self.__class__, self, [scope, id, props])

    @jsii.member(jsii_name="toYaml")
    def to_yaml(self) -> IPostman:
        '''Converts the Postman configuration to YAML format.

        :return: The Postman configuration in YAML format.
        '''
        return typing.cast(IPostman, jsii.invoke(self, "toYaml", []))

    @builtins.property
    @jsii.member(jsii_name="config")
    def config(self) -> IPostman:
        return typing.cast(IPostman, jsii.get(self, "config"))

    @config.setter
    def config(self, value: IPostman) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0448eb80f786ce36d7cab2fcd3d96fddddefcb6b87c9d69a9d799c74fb9e2779)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "config", value) # pyright: ignore[reportArgumentType]


class ReplacerConfig(
    _constructs_77d1e7e8.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="zap-cdk.ReplacerConfig",
):
    '''Class representing the replacer configuration.

    :class: ReplacerConfig
    :extends: Construct
    '''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        props: IReplacerProps,
    ) -> None:
        '''Creates an instance of ReplacerConfig.

        :param scope: - The scope in which this construct is defined.
        :param id: - The ID of the construct.
        :param props: - The properties of the replacer configuration.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ed55f033666d619960eecfd5017d594575a38d3d70f804468b091583137c4c87)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
            check_type(argname="argument props", value=props, expected_type=type_hints["props"])
        jsii.create(self.__class__, self, [scope, id, props])

    @jsii.member(jsii_name="toYaml")
    def to_yaml(self) -> IReplacer:
        '''Converts the replacer configuration to YAML format.

        :return: The replacer configuration in YAML format.
        '''
        return typing.cast(IReplacer, jsii.invoke(self, "toYaml", []))

    @builtins.property
    @jsii.member(jsii_name="config")
    def config(self) -> IReplacer:
        return typing.cast(IReplacer, jsii.get(self, "config"))

    @config.setter
    def config(self, value: IReplacer) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8a13461a6145882e5b81273307a882a17a6d5627bc4a8de7180e5e3980b31e33)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "config", value) # pyright: ignore[reportArgumentType]


class ReportConfig(
    _constructs_77d1e7e8.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="zap-cdk.ReportConfig",
):
    '''Class representing the report configuration.

    :class: ReportConfig
    :extends: Construct
    '''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        props: IReportProps,
    ) -> None:
        '''Creates an instance of ReportConfig.

        :param scope: - The scope in which this construct is defined.
        :param id: - The ID of the construct.
        :param props: - The properties of the report configuration.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a3ebd374b9fc34e3882e5172f8bfc9b920322575de2dd6cd25b1204061c419f6)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
            check_type(argname="argument props", value=props, expected_type=type_hints["props"])
        jsii.create(self.__class__, self, [scope, id, props])

    @jsii.member(jsii_name="toYaml")
    def to_yaml(self) -> IReport:
        '''Converts the report configuration to YAML format.

        :return: The report configuration in YAML format.
        '''
        return typing.cast(IReport, jsii.invoke(self, "toYaml", []))

    @builtins.property
    @jsii.member(jsii_name="config")
    def config(self) -> IReport:
        return typing.cast(IReport, jsii.get(self, "config"))

    @config.setter
    def config(self, value: IReport) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8af3e2b0e8298faf714c686c34f9f3d4277a993a57fc90c95da847f2da4cea68)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "config", value) # pyright: ignore[reportArgumentType]


class RequestorConfig(
    _constructs_77d1e7e8.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="zap-cdk.RequestorConfig",
):
    '''Class representing the requestor configuration.

    :class: RequestorConfig
    :extends: Construct
    '''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        props: IRequestorProps,
    ) -> None:
        '''Creates an instance of RequestorConfig.

        :param scope: - The scope in which this construct is defined.
        :param id: - The ID of the construct.
        :param props: - The properties of the requestor configuration.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__db36fdf220e388e6b7b448971359c7b60d3f85894ad5b7d3c2035e4e3779ca63)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
            check_type(argname="argument props", value=props, expected_type=type_hints["props"])
        jsii.create(self.__class__, self, [scope, id, props])

    @jsii.member(jsii_name="toYaml")
    def to_yaml(self) -> IRequestorParameters:
        '''Converts the requestor configuration to YAML format.

        :return: The requestor configuration in YAML format.
        '''
        return typing.cast(IRequestorParameters, jsii.invoke(self, "toYaml", []))

    @builtins.property
    @jsii.member(jsii_name="config")
    def config(self) -> IRequestorParameters:
        return typing.cast(IRequestorParameters, jsii.get(self, "config"))

    @config.setter
    def config(self, value: IRequestorParameters) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1ea9f7c48a0630bbaa4320e90d21bfbea21b36d81f66defda4911592a25f7cf8)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "config", value) # pyright: ignore[reportArgumentType]


class SOAPConfig(
    _constructs_77d1e7e8.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="zap-cdk.SOAPConfig",
):
    '''Class representing the SOAP configuration.

    :class: SOAPConfig
    :extends: Construct
    '''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        props: ISoapProps,
    ) -> None:
        '''Creates an instance of SOAPConfig.

        :param scope: - The scope in which this construct is defined.
        :param id: - The ID of the construct.
        :param props: - The properties of the SOAP configuration.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4843416f8cb2d6ddc2d95dee76d16aaa16d7b665896b761099b63fcd3c9d7f61)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
            check_type(argname="argument props", value=props, expected_type=type_hints["props"])
        jsii.create(self.__class__, self, [scope, id, props])

    @jsii.member(jsii_name="toYaml")
    def to_yaml(self) -> ISoap:
        '''Converts the SOAP configuration to YAML format.

        :return: The SOAP configuration in YAML format.
        '''
        return typing.cast(ISoap, jsii.invoke(self, "toYaml", []))

    @builtins.property
    @jsii.member(jsii_name="config")
    def config(self) -> ISoap:
        return typing.cast(ISoap, jsii.get(self, "config"))

    @config.setter
    def config(self, value: ISoap) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1583ccdd341a52f969ba35edf51f555f20581f1b5ed51f10001c954882d252bb)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "config", value) # pyright: ignore[reportArgumentType]


class SpiderAjaxConfig(
    _constructs_77d1e7e8.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="zap-cdk.SpiderAjaxConfig",
):
    '''Class representing the SpiderAjax configuration.

    :class: SpiderAjaxConfig
    :extends: Construct *
    '''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        props: ISpiderAjaxProps,
    ) -> None:
        '''Creates an instance of SpiderAjaxConfig.

        :param scope: - The scope in which this construct is defined.
        :param id: - The ID of the construct.
        :param props: - The properties of the SpiderAjax configuration.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b4d659140e7795f6d597b0ba238bda72c634a517c6e6023d60e03c9c1739564d)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
            check_type(argname="argument props", value=props, expected_type=type_hints["props"])
        jsii.create(self.__class__, self, [scope, id, props])

    @jsii.member(jsii_name="toYaml")
    def to_yaml(self) -> ISpiderAjax:
        '''Converts the SpiderAjax configuration to YAML format.

        :return: The SpiderAjax configuration in YAML format.
        '''
        return typing.cast(ISpiderAjax, jsii.invoke(self, "toYaml", []))

    @builtins.property
    @jsii.member(jsii_name="config")
    def config(self) -> ISpiderAjax:
        return typing.cast(ISpiderAjax, jsii.get(self, "config"))

    @config.setter
    def config(self, value: ISpiderAjax) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f72bf58a00298427f0770fbf482a2c76944db226c349c3bbdbdcd7799632b2b5)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "config", value) # pyright: ignore[reportArgumentType]


class SpiderConfig(
    _constructs_77d1e7e8.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="zap-cdk.SpiderConfig",
):
    '''Class representing the Spider configuration.

    :class: SpiderConfig
    :extends: Construct
    '''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        spider: ISpider,
    ) -> None:
        '''Creates an instance of SpiderConfig.

        :param scope: - The scope in which this construct is defined.
        :param id: - The ID of the construct.
        :param spider: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e0a5b68bfaae70f3bf1d2e6a569e34a8de569dd40a8dfa68ed210b730f07211a)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = SpiderProps(spider=spider)

        jsii.create(self.__class__, self, [scope, id, props])

    @jsii.member(jsii_name="toYaml")
    def to_yaml(self) -> ISpider:
        '''Converts the spider configuration to YAML format.

        :return: The spider configuration in YAML format.
        '''
        return typing.cast(ISpider, jsii.invoke(self, "toYaml", []))

    @builtins.property
    @jsii.member(jsii_name="config")
    def config(self) -> ISpider:
        return typing.cast(ISpider, jsii.get(self, "config"))

    @config.setter
    def config(self, value: ISpider) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0583628a54d2e412fc72ea49e04114b8341fcbf24a5b80c3a000a99fadc461fa)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "config", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="zap-cdk.SpiderProps",
    jsii_struct_bases=[],
    name_mapping={"spider": "spider"},
)
class SpiderProps:
    def __init__(self, *, spider: ISpider) -> None:
        '''Properties for the SpiderConfig construct.

        :param spider: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__576c170c601ea46aa887ed94f5e04f3bf674a900b0d860cd9e126ae278b7586d)
            check_type(argname="argument spider", value=spider, expected_type=type_hints["spider"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "spider": spider,
        }

    @builtins.property
    def spider(self) -> ISpider:
        result = self._values.get("spider")
        assert result is not None, "Required property 'spider' is missing"
        return typing.cast(ISpider, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "SpiderProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ZapConfig(
    _constructs_77d1e7e8.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="zap-cdk.ZapConfig",
):
    '''Class representing the Zap configuration.

    :class: ZapConfig
    :extends: Construct
    '''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        props: IZap,
    ) -> None:
        '''Creates an instance of Zap.

        :param scope: - The scope in which this construct is defined.
        :param id: - The ID of the construct.
        :param props: - The properties of the Zap configuration.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3bd22a287a9c38de36d24543303284350f18de74cea65506c787999ec1bb8c92)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
            check_type(argname="argument props", value=props, expected_type=type_hints["props"])
        jsii.create(self.__class__, self, [scope, id, props])

    @jsii.member(jsii_name="synth")
    def synth(self) -> builtins.str:
        '''Synthesizes the Zap configuration to a YAML string.

        :return: The Zap configuration as a YAML string.
        '''
        return typing.cast(builtins.str, jsii.invoke(self, "synth", []))

    @jsii.member(jsii_name="toYaml")
    def to_yaml(self) -> IZap:
        '''Converts the Zap configuration to YAML format.

        :return: The Zap configuration in YAML format.
        '''
        return typing.cast(IZap, jsii.invoke(self, "toYaml", []))

    @builtins.property
    @jsii.member(jsii_name="config")
    def config(self) -> IZap:
        return typing.cast(IZap, jsii.get(self, "config"))

    @config.setter
    def config(self, value: IZap) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8f2016062e53ac595f4d1ec7fa18bc6a252c46924db45efa324aa4b2bc65bd98)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "config", value) # pyright: ignore[reportArgumentType]


__all__ = [
    "ActiveScanConfig",
    "ActiveScanJob",
    "ActiveScanPolicyConfig",
    "App",
    "DelayConfig",
    "EnvironmentConfig",
    "ExitStatusConfig",
    "ExportConfig",
    "GraphQLConfig",
    "IActiveScan",
    "IActiveScanConfig",
    "IActiveScanConfigParameters",
    "IActiveScanConfigProps",
    "IActiveScanJob",
    "IActiveScanParameters",
    "IActiveScanPolicy",
    "IActiveScanPolicyDefinition",
    "IActiveScanPolicyParameters",
    "IActiveScanPolicyProps",
    "IAjaxTest",
    "IAlertFilter",
    "IAlertFilterParameters",
    "IAlertTag",
    "IAlertTags",
    "IAlertTest",
    "IAuthenticationParameters",
    "IAuthenticationParametersParameters",
    "IAuthenticationParametersVerification",
    "IContext",
    "IContextStructure",
    "IContextUser",
    "ICookieData",
    "IDataDrivenNode",
    "IDelay",
    "IDelayParameters",
    "IDelayProps",
    "IEnvironment",
    "IEnvironmentParameters",
    "IEnvironmentProps",
    "IEnvironmentProxy",
    "IExcludedElement",
    "IExitStatus",
    "IExitStatusParameters",
    "IExitStatusProps",
    "IExport",
    "IExportProps",
    "IGraphQL",
    "IGraphQLProps",
    "IHttpHeaders",
    "IImport",
    "IImportProps",
    "IInputVectors",
    "IJsonPostData",
    "IMonitorTest",
    "INewType",
    "IOpenAPI",
    "IOpenAPIProps",
    "IPassiveScanConfig",
    "IPassiveScanConfigProps",
    "IPassiveScanParameters",
    "IPassiveScanRule",
    "IPassiveScanWait",
    "IPassiveScanWaitProps",
    "IPolicyDefinition",
    "IPollAdditionalHeaders",
    "IPostData",
    "IPostman",
    "IPostmanProps",
    "IReplacer",
    "IReplacerProps",
    "IReplacerRule",
    "IReport",
    "IReportProps",
    "IRequest",
    "IRequestorParameters",
    "IRequestorProps",
    "IRule",
    "IRules",
    "ISessionManagementParameters",
    "ISessionManagementParametersParameters",
    "ISoap",
    "ISoapProps",
    "ISpider",
    "ISpiderAjax",
    "ISpiderAjaxProps",
    "ISpiderParameters",
    "ISpiderTest",
    "IStatisticsTest",
    "ITechnology",
    "ITotpConfig",
    "IUrlQueryStringAndDataDrivenNodes",
    "IUrlTest",
    "IUserCredentials",
    "IZap",
    "ImportConfig",
    "OpenAPIConfig",
    "PassiveScanConfig",
    "PassiveScanWaitConfig",
    "PostmanConfig",
    "ReplacerConfig",
    "ReportConfig",
    "RequestorConfig",
    "SOAPConfig",
    "SpiderAjaxConfig",
    "SpiderConfig",
    "SpiderProps",
    "ZapConfig",
]

publication.publish()

def _typecheckingstub__ca23190d78d2919234c733f19bc05216a18406399e366571582fc581ddd3a04d(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    props: IActiveScanConfigProps,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8b0ddb7eb853d9c049ca8348df0137f1a23ad23b50e811df2bcaff3e9c4b14b9(
    value: IActiveScanConfig,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a2085f7ef0b4920076c5afcbcde68feba9d61419b758eea5adcb3e987f983c2e(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    props: IActiveScanJob,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__86d1d4b9c76f03b522305295eeab25e3ea258092276c6d3372313ee7b559d438(
    value: IActiveScanJob,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__084e96fc35d1b7dbc9517ca12daa47f386f20e22c63943d6e4d015175436d854(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    props: IActiveScanPolicyProps,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6534e2afae36b77e40210a17de82410447fcc2457c8a1a43851fe2de50c3232a(
    value: IActiveScanPolicy,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e95ef3650f7e32fe23b005b05fb2bb67ac82df46e6326e92f4f960e7622e4fcf(
    output_dir: typing.Optional[builtins.str] = None,
    file_name: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ad662c09c49cf027d20555f383009c853b03d18c2bd1743d5d72a3a30cb16a2b(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    props: IDelayProps,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1f010482d7efc9dd5289ea9cf8e12a22938f603166172abd5c53ba454fc3fa02(
    value: IDelay,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4ec4069b55c551c9ec1c740b290092b04b969a1fb7df628e695c20e6d29300cf(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    props: IEnvironmentProps,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f334f1cc55832e44ee7730d1527b668c98c2c6f940f41152ee2bd5559a7654bc(
    value: IEnvironment,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b1955ace043e11fd285dea3a9a4f27efa745bc54732188e249d2b9c62b8f884b(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    props: IExitStatusProps,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__289286215f39bb84bedf9cb35a0ff36ab346da8b4ca243aa51e23e1303536447(
    value: IExitStatus,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4037c2c6d5e527d3c1b388ce5b3e6d225fcc975e37f6355310e1f858b46e8208(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    props: IExportProps,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7aa75e755f38fe6a850589f12376c85273dca7d059072033f1d401b2fde3263b(
    value: IExport,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8a6b9b787a6cc20c237882afd6f3d053908c0ec60393409ee1fe68d4f463ca21(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    props: IGraphQLProps,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8a017182eca10655d919e00f96289d33b3cc9b9cd5e73c811fca6255c667e97a(
    value: IGraphQL,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__39ba182886f05e983ee5ba17ac6171a5e7e1fe447080de2760994b3f5326d4be(
    value: IActiveScanParameters,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7b0bd039fd8636869ef24803522658fc1e68d212c7fecbd1c149915758f3bdc5(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__004435ee8a412d4b14b073dc20f147901f1b1cccd8e834cab7bbfd502eda6165(
    value: typing.Optional[builtins.bool],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__104fb8bf3aefd428754fed2d01a73dfe8aa4d38d50907b2b71078badb849a4a5(
    value: typing.Optional[builtins.bool],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__fa1e8f5dea3906034fd168f7578e951d822d07b22b2e00eb2a615af8da88e31b(
    value: typing.Optional[IPolicyDefinition],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3a075a4adb319226a1fef8d3ee23b97da0450591a4f1041b979ffb434e6971b9(
    value: IActiveScanConfigParameters,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f9d6b390fdf9ae292ef9c534c03cd0a93631b7d556fa0ec4c2338fd3863b0fd6(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a1a67ac88b2e807e0eafad36d3b0c62e47ac65fa21c59724ebcdff4f589fd8b4(
    value: typing.Optional[builtins.bool],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__58e83aa4d79baab3880246fb63a5771df60728fa4e9c39bfb32090951c81413d(
    value: typing.Optional[builtins.bool],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4d4af7ae1fb657b91515fb482073ea8c575aaa3bfed3c202c18010947de8b902(
    value: typing.Optional[typing.List[builtins.str]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b504fefd5672cfcbe39306e21918ab5381b4eaec7f3f761ef7c4447625eb6557(
    value: IInputVectors,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8a6b7b10c17cf59237cb48861597a4dc8fcff0f23d4d3bc404bca53cfba52b5b(
    value: typing.Optional[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__188d3374fb5d88ecba26fdaa6cd996db8365289ea3efcc4cf2eaf3331576fcee(
    value: typing.Optional[builtins.bool],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f3c666b269b07d71a7d81432403d0216b225cbb6e4c188b82159daa9e25eb8f1(
    value: typing.Optional[builtins.bool],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__69183eaa0cf577d63814c3f264a6c499e6f0786015071376d7130b8c2eb9f31a(
    value: typing.Optional[jsii.Number],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5c61df97e2f02b213285e769aecb93dfb5e8601dcf5a6ad7f2655fbf3175780a(
    value: typing.Optional[jsii.Number],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__66723e19545dbce6449385d557525fcef88a30cd54b737af430bacd13ed37ba7(
    value: typing.Optional[jsii.Number],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f17890a7f68c9ab7f3872c9c300cbe6490a4d9ff14e0aaedacad5d862f90e76f(
    value: typing.Optional[jsii.Number],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__fdf7075df4fdf325b279c35c6411108f836770d9e1348b31b8e521221f02c527(
    value: IActiveScanConfig,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b3ddc3fce98847c341bb07c7b507c0bf58f73e9468bfa12600b190bc8bdef8f7(
    value: IActiveScan,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d5957dc8a6ee13abaa8bb8e7312a4335c1f1e8fe37abfb4cc67bf1067e8680f4(
    value: typing.Optional[builtins.bool],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3a5be83aa8204f38dd29d36f0b646b42dcba6cf2020bcefb469da55b9f46d731(
    value: typing.Optional[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8cc7ab0e0f7c1c36fb0a6de441dd09d8ebe74d105879654f40c4bb6fd277b821(
    value: typing.Optional[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__df1e2bb7ca9cf381aece04cd960257c5a4dd76a2e98f2a82b24c1ace3f636994(
    value: typing.Optional[jsii.Number],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8f061745aee1f7f160ed3e581047d3911ede6d299fccb7cda6c5d18d3e336b4a(
    value: typing.Optional[builtins.bool],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__efb7b527af79e9fe79fc49a68ce70d2b33deba4b1667e65b63b034ca93cbfc9b(
    value: typing.Optional[builtins.bool],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e2ed4d2485991c4a048c2c506044cc3b0ff9ed523956f0915776d2067e3169b9(
    value: typing.Optional[jsii.Number],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f7a1dc16dcc47c4a382488abdad3c855b0590e7484bb77cdc067e75641cd9121(
    value: typing.Optional[jsii.Number],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e5f746695cea7a5525e31418a9f93f006743940b758bf0ed8c0f22b10ca8a583(
    value: typing.Optional[jsii.Number],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__361b9e2ffd4d58ea3a0fe64582fdcbb8a49dc85c7ac694da65a06a359fa80bda(
    value: typing.Optional[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e702469e60539272a298dfda765cd11468106f13366bb350ceb4244c0c862986(
    value: typing.Optional[builtins.bool],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c381784af7dd1e01585590e0becf64587c41f50c50d790865fbffeedaa4051cd(
    value: typing.Optional[typing.List[typing.Union[IAlertTest, IMonitorTest, IStatisticsTest, IUrlTest]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4d3ac6644ee72cee5277961d3955892e069079b2af8acb0182cfe159d6544343(
    value: typing.Optional[jsii.Number],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6e70a801b6228ab68251897527d6ed306e3714168487f35f12f01efe37ebb8f9(
    value: typing.Optional[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4d9eb57731587721cb207ffcd878c4acbc05ebe2aa3dc5db83b99eaca1ea0559(
    value: typing.Optional[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__acb2689e505797bb0987411298a02b53a5f2d8e6174de52cedba46d9cb6b103c(
    value: IActiveScanPolicyParameters,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a9d8df74f220ea0bca1ed7c224dee9df10ba2b9936ebc20af0def4a18f29a2a0(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__350074fcacc17f040555e59f88c2452863bf4e16a681e5aa06cdcae12b762c89(
    value: typing.Optional[builtins.bool],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2834b449438f57536dca74690060eb075e627dcb29bc59c202ece887cbd4898e(
    value: typing.Optional[builtins.bool],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6f5b32b83e568f5fc4d6a4fae3b130eff8c106c93b8aaa70c48020abdb9ce963(
    value: datetime.datetime,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3656005fb67617eed1dd0da51dafffcbd3a02cc01adcd26adb7d4dc1988c9a86(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b9b23cbe8cb5907509dd26c54383b2c71e043fe9fbe3d9b5bf7826a8a63d7c46(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a7d22b2124d452c178e5f9c64b7e61f3360ae6a337ecdb70ac714a0c16d7439a(
    value: datetime.datetime,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f04d683a1b58ee7079e22fde8a080605cdb636e2a827bc5cb0e4c9b23ff1f5c1(
    value: typing.Optional[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__87eb15d37dfd45eba4718637f8a1a84ba628cb6b8b6771562e3ac9443dca6532(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9fdb05ebf98873ec8af1710f5fae352824b7644ca727add404aca11a9714e80e(
    value: IActiveScanPolicyDefinition,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__afa0c2f038935b5bc77460447c8c8b7fdce253ce059aabf23c25ba00a7d745bc(
    value: IActiveScanPolicy,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__21e8629528cdf90796e876d40bee85e20fec3c919a6c670d8bd0f3d94c91bb09(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b93b53ea2a163c2d9bba32f7e444f1cdd4f19d7708ae698560f91d3c7ca36424(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__df494d7a5b94fdff24cfeb5a852e49e59a262f318727f6061aa1c651d963a39e(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b3a67814a62470abff2a59ab59399dfba922db543fdfaedb466f07fe067988d7(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__edfd8b81e3c0dd19739e541e37ba53115dc3b31b19c815aa1799f2dcdfe9f790(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2959aebde08b09a9328e8f97aeea7d37f927d3f724bff0a8e12f5e7309710a09(
    value: typing.Optional[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__def45010adcc6315620a80e6a606a0d8d531ee0d2a268eaf8492ea3f1694124f(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__88c98929537b3c33b406e8587b98f8aba9523c81436b62038b44de3ee391c607(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__384ef7816fe69412f49d2dae6178e59d2156762d8257bf271a25404c9b75b57c(
    value: typing.Optional[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e46a32350578f67a3b6837c39f1c58235ae8a0570cf3b2b77b54c3bb14484ec9(
    value: typing.Optional[builtins.bool],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ca377f59f51fa2ee7dc79ef8dbff4f553c5553b5e23c71e1e81ba89b7513fb9f(
    value: typing.Optional[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__42aff3f8eaef5337dbd8e8f8b3787931a7fc9b18d8f61c7822ff72ad304efdb0(
    value: typing.Optional[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__cb37b5aa6bd4d1ea95eba7c95012c2335aabbb9c7ce3e77796b3d96cccd426ef(
    value: typing.Optional[builtins.bool],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__65124f21bb792970688a081933341bd26df3c6cffc1c00a649268ef8650d7658(
    value: typing.Optional[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__504af35abe5a1284f1c1c118444237d03e300b3644f240e0ecc55be99bc3c808(
    value: typing.Optional[builtins.bool],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3db000522ca6305e8ecf33827473233db2f4cea2d1e226400a596f4b092df3d9(
    value: typing.Optional[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3734f6fc222c3600dbbba8c09ca87c33a89034c7ad2c1279a1cb37b24a263bd4(
    value: typing.Optional[builtins.bool],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4be56ee0f993319959d37e3c10efd1f6ea20de159778eed11c19d0bb61df0b47(
    value: typing.List[IAlertFilter],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__67ee7d195a6e6fca958c3000d10f0be87c3dd608b5d726adb804446b9d54aa44(
    value: typing.Optional[builtins.bool],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__db06983cb9c5dad8d2968994f74f39b5a4f05d9499702740eabc458616612db6(
    value: typing.Optional[typing.List[builtins.str]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8c7ce4753f533815fce74b5bab23a58ab8663b43d3c1c426bb046247f95f3b35(
    value: typing.Optional[typing.List[builtins.str]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__bc26225f919da4776b588e62d9a87762f46307f2ce3c9d8eec690fd9a0ec239d(
    value: typing.Optional[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d95287e23bddd3dc313a1f08e792d8e035180f13bb4587565fddc905f4536c2c(
    value: typing.Optional[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__80c9234b343377f12bc267046f6bbc0952d1adb141106d80ef53f8c365dab31f(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__84b456293ad17dfc92426a47742d54b6633fe0dd205e08a5c2862cb307a389c6(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2e37aa8e1ac031be95b04b3c5f72cde5bfe3e24ae371b689a5eb70c3cd1a5fdb(
    value: typing.Optional[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3f2f364553b125537df77964e0dde93db347dbcdb663cce61bbd17552ad0119b(
    value: typing.Optional[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8f25f07770658386c8a3138ca975338d2afeaa80a3fba964aaf12c194c7fe9a9(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__eeb27c9a7758e3d006a6caa0569a57afc3ee847a97492db256a23fe498ee7115(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__aad51ee87979c9e57cfa38ad3d6567d4e7c23f081707c63134dfff85687e0041(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d88e59a759583f259c9ca330f9e64e4456e73cdbecf493e4c0574672918631f9(
    value: typing.Optional[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4d27bcdb326f07cadb24a2c57f7df108cba630d4c0202ac3d6a07669885cf57f(
    value: typing.Optional[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__90a2d5cd71e1ff75e969133be060630620b624114627de01dd5bbc27acf9c9cf(
    value: typing.Optional[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__600f781777fc184ad1e334194eb5d72d1fc35ed8e4454bc9e34ff3d8f65c090d(
    value: typing.Optional[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d23499f7ce966fe187be72e71d5d86ed5fc16465510d71c0964f343f692bdd1f(
    value: typing.Optional[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__144b6545ace08dc2f9df1ef3db95981430c84f4b2b122ad170c330d600c85350(
    value: typing.Optional[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d66a501872d2ce82650d382b2a51b60b25d4ac118d9fe816844f85ca7cbf1ad5(
    value: typing.Optional[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__96e34f45ba1a59f943edab0c886c35574ad5bc0ad02c03c4789f31651c912f6d(
    value: typing.Optional[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6f195e39e3a6944b9c420e9fdfaeebaa54ac1d75418972acff67f64ef2c1ecef(
    value: typing.Optional[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__fd72b42aa985c2fce6982fcc142c94b515f0ac7b1a8768bb78640288dabaf5d2(
    value: typing.Optional[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__52ca62c23f711572246801957a50a2a2260cf999465c91ccf8f7018aa515b05a(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5f83e38f0a7ca5c3fc135063d93dccc27958dbe244363b93ee727ab611ca99b7(
    value: IAuthenticationParametersParameters,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b09f53eb485e80307509d122da05148a6d820bbb25159544884b5f592c2c272e(
    value: IAuthenticationParametersVerification,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d7722de6da3f23b9bee929872cf1c42240abf16e71459625896965234450b29a(
    value: typing.Optional[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__cc05d141dca7d154cfb390b1ef633f68a905d4dee0df08320b9ca25e839ed5bf(
    value: typing.Optional[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__af735d99ca9cd05f16721cfb7ffc462f4c651689235beb6b25ca30d6b7de746a(
    value: typing.Optional[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__057387cabc540c339eea571e07f3c41f439b089e44183c3bbb2d0263d9cc062c(
    value: typing.Optional[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6a410c51610a2503684646ecc72748ec4585aba60377b941b8e7578e774665e5(
    value: typing.Optional[jsii.Number],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9601df8316ae67794e7549bf77b9c3fb5eda8d849f909d70b77a69039178f039(
    value: typing.Optional[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__eca06960314e389be33991fc2e375a4384aeb214e2eb55eec0c9421cbd40ec44(
    value: typing.Optional[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9cbbe943d2fad64468c336d3aadc97861dfb1a9ab3521140692b94a7b289ac63(
    value: typing.Optional[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d50db271d9e3e333b41961042aea8ee28ad5533a30eb48b6dc2d032e315b188c(
    value: typing.Optional[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f98568443479f6e4b822117f1faf317c1ab2b6da60be36bc215c2666ceb0b360(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__118ea4c4c3c355359d986242f4ede515e91c9ff7298a92d41d339046a8261770(
    value: typing.Optional[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ada7966e20dc36ceecbd4ddd9f3a1ab2d4d46f605bde6e705c0c5f1f95c576e9(
    value: typing.Optional[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ccce2a650b964a71adac5bbba632cf65daf5c3c138768eb8e9be1a4950684faf(
    value: typing.Optional[typing.List[IPollAdditionalHeaders]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ae0c1e4140f4419e50c482a646dea15e36406221ab262e0c1f9230d82c6b9de2(
    value: typing.Optional[jsii.Number],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__97fea499561aaeeceac009bbd051fb9c8a1388ca74a6648fe9d8fd5ecac3ac02(
    value: typing.Optional[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5c3a8d01f94ce3f84bc1bff5149f4ed9b3db9f1c3fe72824fa44f37cd135c9e3(
    value: typing.Optional[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__aac8f6c5d303c9f1b02fb7d5814dd71668177ae7f08cf794b7334c11b2a434f3(
    value: typing.Optional[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8c862f64c3e233c811f69417491907f84a9db5f5e836d0981f53f2a13bd8e22a(
    value: IAuthenticationParameters,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c8e1c18039e856bc81d0326d612323226e95b51b592f64fb578e0800ec17b02d(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9c6f1336a5d8e4baaab4f3257b7b569268fbeb7b328d7ff0070c3c274117d806(
    value: ISessionManagementParameters,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d679875cf018302a684da54609a79b6ed28a8b22499640e405aff291c2c9ddd4(
    value: IContextStructure,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__023611b082ef91815328e9c33e92b29fa4d8dae6a5c9026d4e262840b2745c37(
    value: ITechnology,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__fc069919a92a2a50127dacd4e153b0119693b0c8667fc4ff72aac97cf869bef1(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1800e8c445df948fd81324601df77c79e5a2fb72132c9813751b6b5abca6f16e(
    value: typing.List[IContextUser],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__cc812fadac413f546f2f25dd634eb020cce042011da3d1edb13ee573e5ed1260(
    value: typing.Optional[typing.List[builtins.str]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__388e1d152cd4efd76cdf203a3126b01c7970d6c8279a157560903198b168b941(
    value: typing.Optional[typing.List[builtins.str]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0fd6b5b3089372632a8a643008f1bbd3e3615251dd187c0d8ccf5cc967d9a153(
    value: typing.Optional[typing.List[IDataDrivenNode]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__75352072ad66a000838b8928aab3d33d1a2a70122e7df2552c524051a7c9109a(
    value: typing.Optional[typing.List[builtins.str]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__097a558df1763bf58907c54142e2470e06076adf69050640ce5f173fafdb0a29(
    value: typing.List[IUserCredentials],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__872d5f242b5f813327d0fc8f8cb147042d6b51983fc6235fb63373739768f5a2(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__dc8e8f04c54e6123c4810a13a5e2a39fe2762635293d3adf3479d80d5899f8e0(
    value: typing.Optional[builtins.bool],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__bd97dcb5c08f30fa5b052c1f0419d13e1878c049aaec66ec8d16db2bfed03935(
    value: typing.Optional[builtins.bool],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__66fb3a3e8df2ef347cd78ccb33369c7bc87588ae33ce53e106d767109075d75b(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f6394c43ee982be11016df20892c72fe0cb0aa5dcb92274e86c96b19b9fbeb88(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b730c719e133b1c7ce7773831132cab46aef67c413180f1c300b9ea933aac436(
    value: IDelayParameters,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__94e589c03ad6ada9445ec74ce69bbb1c05b100249ee2c30743b06b33e651d627(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1f1f4dff092de5c04dbe769cad8b66478b37f0d43fcfaeea056c777e73ab8c96(
    value: typing.Optional[builtins.bool],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c43d355833a5c01c5d21405def976685d91fa5f49c97bb22144d891d7d0ea9e2(
    value: typing.Optional[builtins.bool],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2636f4bf0c4cc2b854bbc568fd2d2f0483851290fc6233d405a0fbb0eda22857(
    value: typing.Optional[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__07472401d586b743c20da73bfb17a88b7e6d23a59fba5bfbf1552ee4026b76b5(
    value: typing.Optional[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__715bd77d7edb3c9f890ea64fe61c86906b10c71a509965c9e97818e75f224dc0(
    value: IDelay,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__40141bbad17e31af6d4a8668fd75c5cca81f33a1d81e0600751ac227748465f2(
    value: typing.List[IContext],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b8829711d0d415de7fb1e41b5d999f3aa6cd8f4c8f5b3de9facd6470aeca60ee(
    value: IEnvironmentParameters,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__064cd1a824ea925cf83951d5e66badc65046b479ed41782d705c156caae2aa43(
    value: typing.Optional[IEnvironmentProxy],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__51ba43f89bbdfd1c12dc49b3c60fe94227125886518830a8aeed92410e55ee0b(
    value: typing.Optional[typing.Mapping[builtins.str, builtins.str]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c1911f3aedbaba8a64fa0a00c8925f460a2388bd5f49350bfd699d8eaf3697ce(
    value: typing.Optional[builtins.bool],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e416f80420e701db0588e752474c5aaeaae2bb74ef370c5f3fdbcc63b5c7c55b(
    value: typing.Optional[builtins.bool],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4932a64a79d7479c667ce3b9f1e8246da8baa11ed5aa91197937f3edd885f878(
    value: typing.Optional[builtins.bool],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e29f17b433b9a7098d5d3b7ab3681cd1ad70ff572c184a101455eba9c2a30488(
    value: typing.Optional[builtins.bool],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__41a50bae66665638fdbf22cfa84315d58fcb3b295b646b721da8dd6e01190d5d(
    value: IEnvironment,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7713df78eae5f387b5798289c84ae6024e9fdb69d060749d5ba2c8d9373be5d5(
    value: typing.Optional[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__147a45346a859b5371d8f9732fc2c5b6a7890676fdbb0963220786f358631e19(
    value: typing.Optional[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4af490888e2dacf3862779f4ec5ced51237fc8bf392cfcb503c863ce48854a0b(
    value: typing.Optional[jsii.Number],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c5cdb753c9882807617616b88099398ce129cb2116d9289588e2bb8c19aa21c8(
    value: typing.Optional[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3c784287998c66234a46b216b81c1d3350f8302edca0472f6ad0e32d9e441f80(
    value: typing.Optional[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__63cbeb29c0c82088b41593e4bfcbc51e635ec403c9860b3b4f943c389f260af6(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__85c822cf69dd3ea149233158bfc19e56b9faf0c3e3906276fbc7f76624b7d049(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__614d320a0ebd99163b7b84ca474307b37324e4886c38d698172b3ddacb12611f(
    value: typing.Optional[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8cd3f4e45797ad6bc894cdcea290c5eab6b334129fb37f045f6941d4ba258ad2(
    value: typing.Optional[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4a10db7eaf990d2991fb4d1db9f5302f3171cbfa02800cfcb6789bba66e5d638(
    value: typing.Optional[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__07083a02c313a32da683b59677a12b0c5818b98744433dd9c134f3c768712c5b(
    value: typing.Optional[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1fe777f75a19706efa755d94879858e18e51f710330c0e4bbb52076e51e409bc(
    value: IExitStatusParameters,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a812a7aa1a6253a95d6c152f0bc5415e6d7da0fa3adafd385507d478a284991a(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c733167546ce73456e4d11d355335bb5400f23c37e14c4b19854fc7d4132f8fd(
    value: typing.Optional[builtins.bool],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f34cf95c2ef8c657e2cad1284a9ac27cb7a3d0d2c27087ef935ad4a325b246b9(
    value: typing.Optional[builtins.bool],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2e2095af8e7b4ed3f1ea122c8adfd2fe86b7d6a3c984970074a87e3e01f94952(
    value: typing.Optional[jsii.Number],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__eb0547814e74540fb26f19399a3d8826bd34d43a99158596c483973237541148(
    value: typing.Optional[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f3d5683c2349dbe83186858abc96a6c157467d396c3184aba29e78806569dd5f(
    value: typing.Optional[jsii.Number],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1c4fdbb71342dbaaa095625e69c12bf61e2c9018c4ec9be93738670b750c4ee5(
    value: typing.Optional[jsii.Number],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__120feea8219b4068dcacd4e406e6491d64d60c8d8fcdbf9e20c7e6f6edb3949a(
    value: typing.Optional[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__92e2b1b44083fb4f2c92559e503a753a060d4ca6893cedb9280f6062fa0ce6f8(
    value: IExitStatus,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e1ba0bd9790eb1b1123f62c4e4684c85cdcf5b946aadf0fe3fb91b561663af8b(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d56305663b998d35c90046c04a605ea814cfb0ce93e463aecd8092eece82fc1e(
    value: typing.Optional[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__389d98055c374eb4e752f7da5bb13d0f24e0a2c92e8251345a488b2ec6473203(
    value: typing.Optional[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ea261aec475e2fcbd99d53bb462d7d06fc27e977715193cbb8e7cf98a471650e(
    value: typing.Optional[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c3313ff41c4c13212c9596a19ca33e2c68edb3e8ffb6015bf1f569c0d59100bd(
    value: IExport,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f546703e5f999e599c11077e5604392fcc7630a9cc29ed3c7ee8b25a00321401(
    value: typing.Optional[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5b2996d4ddccdd31f600e3e1d466a167e30ef94f65a318320fe12ab9b70ea522(
    value: typing.Optional[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6051882e6343d3b88e73b7069132bb64bb0d9f43e063ee6e5776bbf44a3cdafb(
    value: typing.Optional[builtins.bool],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__097cb58176803755d10c159391b49526f8cee6e5b03efd69058d6e8dd0a60ef9(
    value: typing.Optional[jsii.Number],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2af74b2b502c05a23e62ee22433aab1a3e0638bc8168fb721b11701dba367f31(
    value: typing.Optional[jsii.Number],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__10884ac90963c74694a1bd8df72cb97ebea47922d020ddccc034758439325e94(
    value: typing.Optional[jsii.Number],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b82cb9b1a14b8e1e544d3ded43a23c031039999545d956908dd1308a3bc7f1dd(
    value: typing.Optional[builtins.bool],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1a138ee19fbff7313e7e4b96824a803d62cee0864a2abaf1356fdfb5aee99858(
    value: typing.Optional[builtins.bool],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__bfdcd83e404c6329f7e6bd5fa3639d2c9561575224f51d72c92b079e17f078a2(
    value: typing.Optional[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__00e26e50d2e00ee16dd4154d736b9621ae92eb413357dd36b9466ef6c5018253(
    value: typing.Optional[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f4a7ee15489a88afc9a810f46452a46865fc4fe74bd744ec34e36cdfbb9da336(
    value: typing.Optional[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0b88d8e49dc0009ead5ff29775778ac3fe73f2402fefbafae1493a781dd54656(
    value: typing.Optional[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7ab732d41a4014a4ebf2b3536b8fde50ea26b4eda8efd4f576435923e4d416d9(
    value: IGraphQL,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7fca46aafc15c700d7acbb4326547575847dfc4bb2c1b5778430c8fe92273082(
    value: typing.Optional[builtins.bool],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d8530865f32c15fdece4cc15153feed530efab483cfea09fc68d8f29d961b482(
    value: typing.Optional[builtins.bool],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__41d8c525484070a21172df6d02d0d77487978007ceac6caee46423bbdaabe225(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c862b6963f762b19a6fe3bc890d7c0c9a27e5d7dd00e4ffa9261728025b11503(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__723e53c1b29783e36b3dfaa392426555f05abcdfa1a597fba4975959681abca1(
    value: IImport,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__17418a764680da2e48bc5b313118b2d5839651224141b6739e3593f0c51190f8(
    value: ICookieData,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__bc69d886995785733af7845e54d6cb04ae20349126a576af8b77d7d1a8728484(
    value: IHttpHeaders,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ab5fcc033eb8e0327ccf88a87b022bff1f81f9fa75ccf2f3fcdab085b0e6f107(
    value: IPostData,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c750167ffad4db33321d6da9fef8037c35a6b4e6b6c1a9a568cad910e5a3c85e(
    value: IUrlQueryStringAndDataDrivenNodes,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4be0d68083a100641013e58581bad97f36e1461b08c604a297132a28b071cd6c(
    value: typing.Optional[builtins.bool],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__26f700cae4b9db1932b58696fb4cc0ed82f3324ef912a086539b6d682ca92d76(
    value: typing.Optional[builtins.bool],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6885c313783edbf0b62223765b028da7ba92b131f910243bcb19884876a694ee(
    value: typing.Optional[builtins.bool],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__74b922f739033736b68687a9d06b72b1fb5333f7dc132f826477398a72253578(
    value: typing.Optional[builtins.bool],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1e90dcd0013d5588f99ac520954e039471348003e11cb9c2a4e06eee55307e19(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__81e9fa0641c722e9148d58a4106da62a0ef57ceac5925de5968829ef1c581230(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e98da75077d9f5679c779ef4c5335f80c80a42de1bb7b4aa4ee024621f3f958a(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e8059a972b5c2f7322c2e810a7d18fb3d381d17b5da78c962807506a9bf55a50(
    value: typing.Optional[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__929b587697cb66c5b2685f5644deb8f6eaf2c9dae992dfc2c812fa2dadfa3035(
    value: typing.Optional[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4995495535ec29d36664942cd573d24eeb8b3206acba02f42de57ce1a67b277a(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0851b1bee43e5de21b90c69ee46cb5f0e011739bf509e537874792f7a699dfa1(
    value: typing.Optional[typing.Mapping[builtins.str, typing.Any]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__172ea9eebee1d8c71c05ecc46518f4a4bdcb58db599bfa3f2b7ac3306f5fd63e(
    value: typing.Optional[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__286e3b452507280491527c16822e633980d5bb627a13e6496e147dc517efd14a(
    value: typing.Optional[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8a3a9c00b6614c10509322afdf05008324a07c670276714f934c54a3601134f3(
    value: typing.Optional[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f2e129f6faa7ce72ee73b6c7d7e8456c9b16bd88dbf41989b01714efa7b6ef17(
    value: typing.Optional[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1bd8f749a7d7a8f794270c8082aa6bd0e6b24b5be171b80637aba6f6314fd1f9(
    value: typing.Optional[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a54769c95e29c3a9c61e5313b66ec57df9a9c6d46531cbd4b8be211b5f85aa53(
    value: IOpenAPI,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d2c5fe4c6d3f23d1ebde8fabebbccbfc1df11f4928621a9cf08c4d5c449d1110(
    value: IPassiveScanParameters,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__17b579768803db320e03e01bc18e2c4ad34a1532d3e641552db168585785612a(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__97552be6abc066d01b668b4c4598987490db97a3d808763545ad7e22401a52a0(
    value: typing.Optional[builtins.bool],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4167f23e223f81c02e1d4a212cb73f3a8ced92e14df99448d7e9642c67c15ee7(
    value: typing.Optional[builtins.bool],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1f02a4e62510304f69676ef1c97e2730e99c5a139ef8624e60bc0ef458aeec26(
    value: typing.Optional[typing.List[IPassiveScanRule]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2b75ad96c8853d34087cb3b1e56cf471ef1bdb38fad3d133648c7264d11936e2(
    value: IPassiveScanConfig,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9818f1d080f3bf36dd6c9da0390e848cbda2ce35dea91b93f79191b7f772f8cd(
    value: typing.Optional[builtins.bool],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7e45325ba5af1d8f63e296012c7de90cf87f92c87a4579b723e22206338201a3(
    value: typing.Optional[builtins.bool],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__32adf47e9e22f49fe484b5ab70f25fa7047721b3d8c0df80e1a85128a85443f8(
    value: typing.Optional[jsii.Number],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6299f9004bee5f3d42514827672affc2efd826435d2ff46f888618bc16fe4ef8(
    value: typing.Optional[jsii.Number],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__04913a0c0bc89dc90e59f8dfb850a64a7ff28daefc267e66dabcee448a35d2d2(
    value: typing.Optional[builtins.bool],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a764c2b1afe9b2476224b5a116a38f9f4bbfa4defca5a604869edcd705917a23(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8064c5fa05af72a6bbc131f9bf0477afeb2f664d34ffdd4d36db44e660e38e39(
    value: typing.Optional[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ddeea77215033ca4f5ed48b73a5207e06ec04b4318db3c1027172574534c4ce4(
    value: typing.Optional[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9155e050a5451ca42bddbd8ceb0389ab4e7f43dfe5a147ec3ac05dbf0725cf8b(
    value: typing.Optional[jsii.Number],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d134ef685bc8c8e0b785db134bca2abcfe2c2bad3fd72a07cea4116bc2da6e84(
    value: IPassiveScanWait,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9be25baff0adeb1b67aad6876177e6f01de44e44f7127d22bef9a59b33146314(
    value: typing.Optional[IAlertTags],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6c44c27220373563d767f53fd9b2231fcfe516d54608e30089f8ece92695e6a9(
    value: typing.Optional[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1d2ff09966ffa883fbab1bca76b2735f54aa226f9ea0d1396f56344e117a338a(
    value: typing.Optional[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9ad5035940e2b31f298134690caa59759a357b8d177b621877e4c1a1f0f01370(
    value: typing.Optional[typing.List[IRules]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__cfd1785421830c4609a3b89beb607465134a17609e82d6f47d053e90375fe66a(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__57c9fde0b011c330b808f8d6f2c8d57afd59acb97e6ecb2fccec32c0afa5508c(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__cfc22f260113ac1b2e2524dc6761d4c3b359f818f0bd3e2002e2db7e8e7a5223(
    value: IJsonPostData,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5c21eb339dd59edfc6f5329c10723c340b039c74cf175692e030ef59f6000cf2(
    value: typing.Optional[builtins.bool],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4e1a2b091db13101db37b4c2bc869a956a4816f125faf789109ef951e36bdce8(
    value: typing.Optional[builtins.bool],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c6b6de21903ce4fdb06173f9105428419140df6af47c5d19f37bd84bbf266e95(
    value: typing.Optional[builtins.bool],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ca382115e3a56016bcafed728bd8dbd36718d6b7f7a005ac727f601f2c7b347d(
    value: typing.Optional[builtins.bool],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5c739455c509a3c4f6f5e8a775bc6d97c6da12389d46b722c599a5700dcb9898(
    value: typing.Optional[builtins.bool],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9fdfbfbd7596b4dc94dfe0bcb963c273e85edf164a9f6fd98fe98647da5f2eba(
    value: typing.Optional[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__73e976a4559b8208d91009ca3f37b85c847a314d89588a3b5045510eaf38edd3(
    value: typing.Optional[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0315dac30fddb8c612b3b09f3ef392c2e6718c7b5a30095354570a535ec8c078(
    value: typing.Optional[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6237eede9b1dc1c76dcf05b8e79da0c26de73271a307e39dc79259430cabf4cd(
    value: IPostman,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__673c33ebe86433cd4726ca9855632a23e78a2ef9b94cc538544327911ab18b0e(
    value: typing.List[IReplacerRule],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d9a0555934b9f177bf43e7f14a1f23eed295a6f33863aadd3d7a3bd119beb835(
    value: typing.Optional[builtins.bool],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4f6157cbe93ab011a2727f0b5fc3013491698d949497ed0385f0b540e9749529(
    value: IReplacer,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d08e6909f1522f8d50d1a8f8ca731c02d83a9f5ddc2c12e0048accecfe4259ae(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5a302facc95f04c01ebe37e25f8ff147d9b8fd574c1fe24a064ddb6ca72432e6(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f82714d9a26249677af3cac484ff848ab3f798855db0076dfaf1c9ad70ef9d00(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__eaccf2daece190d93150f14c94805e93d3f0bb8f52852c867cc947234723459c(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8d9c83aec98eaa2a03df879fdce4ed924f7a6320e5cca9711a94c655413148d3(
    value: typing.Optional[typing.List[jsii.Number]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f271698dd8e4f23a5ca52ecb6907cc5b53c5d9175a839457d98fb3631230281b(
    value: typing.Optional[builtins.bool],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a9900737a0778ba696d84519e19ee177bf88ff6de672175b7062540abeceb7e5(
    value: typing.Optional[builtins.bool],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__18d1f5a1ff0650ab21b137e0d3555626b26fbedf676a02b1575d067e78535129(
    value: typing.Optional[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__698bcdb9077f2327a8dd3374c3c9d7f55065efa482b7b46ad3c258954f79803e(
    value: typing.Optional[typing.List[builtins.str]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__511de7483cd9d4b5f9df4ae1bc8610742d10082c91a01a7ed61998ffda3f2928(
    value: typing.Optional[builtins.bool],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__28d57f0d2c179634d83e52b3865ea5b1a1b88ccaf0f98f00fe5f98ac1b890e58(
    value: typing.Optional[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__15fed95dd6d8e31340894199b4c50c0a943f5660a240fe372cd29e61cc3f2700(
    value: typing.Optional[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6fe4ca7cc6d6a70e99a8174dd28ebee90b4ae2b3f59defff8f8b055ba957affe(
    value: typing.Optional[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__53bc7569a263eebb2b9ca54d06d3e1f5f89994e0d0b65aa113d853ad943f9b99(
    value: typing.Optional[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__361db7eb7ca9ea8a0ad3c755a7dec8a7bc8665b236d825963804924de861f3a3(
    value: typing.Optional[typing.List[builtins.str]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b3b1ee79bc9f1ac6eb86da315daf25326935c2d55c0a1673fb253b0191960631(
    value: typing.Optional[typing.List[builtins.str]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__76186d0bc45c8c94b15cee6e66fede86e73b83ea4b12176ef0509028d15aef89(
    value: typing.Optional[typing.List[builtins.str]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__64f433871ebf42cb9f513a562185a640f36524ebeeb98f5149cf7acab78ac0e4(
    value: typing.Optional[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b5a7fa980af165bc095a9f9605c0960a9e0d7615175617aa1163a98d031b7919(
    value: typing.Optional[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a7795fd91eaf5fd466e97f352df81afa4109b164c53b06865b840bb33f7a5d0a(
    value: IReport,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8e73508d4b934645f8fcc50b5e8ff2150099fc593e6032dfd32fb6badddd9631(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__af7921b1cf43c5088afe86e9f0e0e1007726d47d61de3c93fdc132ddc28f7e27(
    value: typing.Optional[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b56da701f5c1a6bf20aba998f54ad579e8402dfe03215207f92b65cb3a5a845b(
    value: typing.Optional[typing.List[builtins.str]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__98a3b1b859b51c72f16a012829f1719ca40941cd7f37f270606dfc003967d4db(
    value: typing.Optional[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e4e4b5cd9c245a96cff7c770bdb1c17a579e61f206c5d7c166b96c535a414569(
    value: typing.Optional[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d80534e42894c9e3e2b9ae606047f59bb6c1e032ccdf6d4e944dab3afca7142e(
    value: typing.Optional[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__33d8dace7bf48a596720324800bd29152d8783de1cc678187c3c01b286905863(
    value: typing.Optional[jsii.Number],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__148087ecbea2ea18f730a4a84b59b284b326d225b6f3dd50df6218e11fd45d13(
    value: typing.List[IRequest],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1165fa7cedb1858f2e1de9f2d6dab2b04940e9cfecf886fdc906ec8400942dbd(
    value: typing.Optional[builtins.bool],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__fdaf41c31fd17b3a6a1cfa6e383615d720e6f07a3531ec73be98caa96538e26a(
    value: typing.Optional[builtins.bool],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e7fcae784ea4084f96c26f343170547d6a10824d11a4bc81dfa26617310b7874(
    value: typing.Optional[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__506cde699f33879e333b15f7997a53c8403e9923c42ab9317b2c65e2f75e5269(
    value: IRequestorParameters,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ceabab1a10e77f8052974586e966e8c88beae6f8a22b5bd52642db7cc35ee7f5(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9a1fbc09418cf2050d3f09ddcf6f2495c40bf70cc03ad0f79fd912800ed22c1c(
    value: typing.Optional[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f52aeaf33b4c902045ec3942d9be12f4adab1f9e7cd5d498bed8abd2dce6bc53(
    value: typing.Optional[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c0952c8cea99cd79a9873148c74b277f158c0d513d41a903ad3095e458f0e42a(
    value: typing.Optional[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e0c7d70f32d9b5147f3aa6ede8de027e8d4852417cf8bb1ea76d765954203928(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f27a4f53464657e4774d607918b430ed720d26d3f9d547f17ef624593e0cfe43(
    value: typing.Optional[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6b6fa341c307f4a3aae6d02dc95b43f2a3f7bcc0727cc4dca63f72f2ffe5d84d(
    value: typing.Optional[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__30694de5e3c1eb85caf48dd146554aed64ec2a5f2986efcd128a2b40fde753ce(
    value: typing.Optional[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5cdbb9d0b54cc5eb2600fe7e248d48bd80bed699b1e26d7e719d7e883edbfc0a(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__652e501aa40928dec6500a7e56376f92ecba8898406b96dce387be74992d787e(
    value: ISessionManagementParametersParameters,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a4dc9de78053a677f66b21dc0abbd7d0f302e0a15dedc372057236bd4e49f614(
    value: typing.Optional[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__65ed25b2bfabe433177b33e025aaccd65a45318c8ff56329f49322cf2d5c3401(
    value: typing.Optional[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__fe7b748ecea4764af8b8f375c53d3bf021e202493bec4e14faa99366466fdf90(
    value: typing.Optional[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0496cf76ba0dc52bbf55b429abef37988820ecdfb14b9407056e21ef1eb23bb8(
    value: typing.Optional[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2202001b2062af3db7e70662bd39b2098c16a77c8092ba5e8b65577ffef1dedd(
    value: ISoap,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ae6937b9f7c771b5f0740e894724b0229698639c51c1aefefc6df67f3ebd3ca4(
    value: ISpiderParameters,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6788c399f83f7ade85c26f1a40bf395b1410e695e638f30ca5b46f38117bdd8c(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7f44ba43f4c5205184c0ebd8f9897a411eaaca1559da7e0cc64d4b985ede107c(
    value: typing.Optional[builtins.bool],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__dc18e1b0268f314549ba928ea71c41886eded224b912c555bc575de4a1abc553(
    value: typing.Optional[builtins.bool],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__57ff4f8d13451124e5373efdf967935c1f67bf3c660bc7ac8e7443f68929ffb1(
    value: typing.Optional[typing.List[ISpiderTest]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1d2007dcd277966bae33fa5ed9dbb703c860c91152a3f7e806b2221d37a710da(
    value: typing.Optional[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__cacb5eaed6ba69eaffb239c02fd1508192410a8d4b1088061908e72924481e21(
    value: typing.Optional[builtins.bool],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__101d32aee3989a2d07c5dbc5414868543f86ff4bf64c702a55a779025874ee64(
    value: typing.Optional[builtins.bool],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6e598134d5f75379642ec1ea5d6aea76382855f6fd2e119018196f0a025a2f2c(
    value: typing.Optional[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__149d74588971ae8b20a12f45203c63d4b48d6b905fa5c4de64162c547a1a80b4(
    value: typing.Optional[typing.List[builtins.str]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__442b6f0a28b2a5a653cbec409a9d8371dd19a18242f125ef6a489cf0ec3ce6ac(
    value: typing.Optional[jsii.Number],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9ca2004d04041d231bb56f095b26326a03b4c63200db6cd16b83e81638d9acb6(
    value: typing.Optional[typing.List[IExcludedElement]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6f9dbbadaf03f13d8318a81559cc6eee13bde731f7a01cba228ea58836387f6d(
    value: typing.Optional[builtins.bool],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__48d686721c7ba0fccd265525629e433b289daaa447ce35e8aed30443fc9e73dc(
    value: typing.Optional[jsii.Number],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d73a2741067e81260ec336a9d6347383063ffea2a700d5763a6902d950f86ad4(
    value: typing.Optional[jsii.Number],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e349fdfd3951db3d2917f2ac0507b6131a0a8fa91dee80137e30e872cb84cd50(
    value: typing.Optional[jsii.Number],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4e2808eed40580f45f3d20fff3985302b33f15b4e994898d25150ced3eaa1d9b(
    value: typing.Optional[jsii.Number],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6dadfe8a90f2a8a3ec52187a53dee158bd5f46643bedde886d828eefe7768c93(
    value: typing.Optional[builtins.bool],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c791e32cacc66b004677e3953197d165955a5b6b9fbc7b3eeb5bcbd6944d6722(
    value: typing.Optional[jsii.Number],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ae82776afd340eba02656a5c93f83ee1419ca5e859df05f249416afe4803b263(
    value: typing.Optional[builtins.bool],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__dea14a9b61c42d6cc55fab55f9b4dc6b25b78cdbf88daae11b55a3d9fc77748c(
    value: typing.Optional[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__65a89f14353ba072d6daa7d54bbc1944c97be475fd48980cca8b4da9dde6eadb(
    value: typing.Optional[typing.List[IAjaxTest]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6ae12a1a311134713762e55b65ad52d92ab122bb3daa1639acefd8faa39a40c9(
    value: typing.Optional[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6a1111b193cda28fa8db9fbee7710ff77642c81dbdd19433eb60ce65b6848902(
    value: typing.Optional[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0024047e6697fa406fa4609cd4d1b657da835ea74b47f4b622cd3207896da026(
    value: ISpiderAjax,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9d896a0fbb35213dd1fe92cccdb086b33d38daf93225de4166d2c995bb77563a(
    value: typing.Optional[builtins.bool],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f6363c51ad61a91cc91d8a158451082356f1ddae6326ef26e31ecc6227366dec(
    value: typing.Optional[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__cf63f4af3bafd8b71e7dd8e2c5ed38a2dc519ef5514a1e974b838dff47c04200(
    value: typing.Optional[builtins.bool],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__70b78b942b6e5d2e7f6da1451c201b0a5dde56bc984565ff1983c82bebc4f625(
    value: typing.Optional[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c6f18da91f77425099fd1f322a76c47c6a7388faba96a4c16f30e715cab32cf4(
    value: typing.Optional[builtins.bool],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3f4800b768bc52283a0e8eb4e77c0d6873d8ed02623a2a76360748bdab59ae06(
    value: typing.Optional[jsii.Number],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__cb67cbc65ff4e7bfdff73e82273417699ebce41e4c7f03c46107625b99d065b9(
    value: typing.Optional[jsii.Number],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__66d354412e708b08df7248e3aa56c75efcdbf033935c1324f7aed48f24d223b1(
    value: typing.Optional[jsii.Number],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e340c30337eb67e7e1f1dc49e7d7d289a6aff6191e38fb8fbc527e64c17edee4(
    value: typing.Optional[jsii.Number],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__caa9194666ff47908e4fabe8292dba81f92e26eb4cc670140e2ff855f24b76b3(
    value: typing.Optional[builtins.bool],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2bed6e2edebf08d5aa92b8be051ad4741521d89692fefe8f59e0836373667a0f(
    value: typing.Optional[builtins.bool],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__96a8864200042aea37a91e614da4348ce5bcaa9e8b7f986a6542764009091f09(
    value: typing.Optional[builtins.bool],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__dd165a4b46f09d1c9792a6f0db3db1cdf2684066419855abc6e4379d7f9b465f(
    value: typing.Optional[builtins.bool],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ecbdeed364e1622a7f03a7d0ffdaa0ad4eb7e7ce331d9c187f0689f2bca2e341(
    value: typing.Optional[builtins.bool],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__141bc718b2a14f9522ec6a416a03d698f427926094ee23fb14bddf4b7ea81976(
    value: typing.Optional[builtins.bool],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5423b002d3bfb1fd4923568d66ba567ecd16dd53a224fd8f0ca48446fab592dc(
    value: typing.Optional[builtins.bool],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f357ab70612af39c4d161473008b1bb615aee0e1ee3585cd4d6eaa3b32589334(
    value: typing.Optional[builtins.bool],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b9e23cbfd125236628a888f0dfb1382a28f07b40bf1bd33fe3237fcadb28c9e7(
    value: typing.Optional[builtins.bool],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c09658779f26e58dfa2345745172068799715d9bc7218cc1b322f1959365702d(
    value: typing.Optional[jsii.Number],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5e13209ba0d55738de3bdc7581f0fca274a978b95ac6de3f5e14caa33166b3a5(
    value: typing.Optional[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__14ffe2eab23a29e74fc48b60522ec75725b744e0f3ab720ea835a5d3c09b3286(
    value: typing.Optional[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__34954a033ee2c76bbfa74a8e8bed751693c8c46897837a80c59f329527d743b1(
    value: typing.Optional[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__fa26ee714a2dc275fe5fe234a7104a7d2543897c5fa98244477b144871060391(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__00a2b5c3836f46d5cd6f0e2355f62148d475f9bacc707d74af97873541d070ff(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a5295b60c0514207b992db5ce7e3fd11bded69a4db8978db9789e6cc95d5d423(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d396d8df17926319338f7dae070391766858004ead1878c9f1a7a372f0ea978a(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a0c6df805e70f9a0eb782705ac45ecb2d195b63d98661c5c29e3aedcd530cc77(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b07630a03143c54f19776bc480a088410376badb88d0c9342ff0c3891773f590(
    value: typing.Optional[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f82f19abaeccbd97592b1366602f8f025f4bf49beafef96f2897293841ab1db5(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8048954b297fa497689adf2dae43ecb43932498847bebe1fcc854ce08ead9881(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__502addf944962ff1c9124f01738d68d6f8dea0508b240f64d49d54eea3dc5d8c(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8334f725128893232a022f1e9f8907a0f259c852e049b693692b58e372552cb0(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e599163506538036cafb75c3c5f2e7eb204a1f2addcfca92393aca1e18b00e0a(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__532aaaa9d93caa5627ce5f4cc2f1053926ea5cf6b750313553f98aafc71fdad6(
    value: typing.Optional[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__555268c139ca00096816460e0258e02213f0dc8bcfef6e93fff953d1600eb309(
    value: typing.Optional[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__dd782cc74977e26423b6f3c158dffba5e46614c0291d02cde8a3ca723eac35e1(
    value: typing.Optional[typing.List[builtins.str]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a9d3e723be6606f42ef7e006227f411dad3774ca535315a7babc2d872cf00dec(
    value: typing.Optional[typing.List[builtins.str]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__caa84775fd057b8023dd4808b0de88dc83889852e6a33b1b355765f250ab4433(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5ff2645a048e06f8fb1c38ea9538dc0d52d55993a3c6cbd720b5f89dc9cc5d58(
    value: typing.Optional[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c3fc4b6095a92521b7c5566f4c533997c8e5a8e40f46cb167315f4f1f1b3e657(
    value: typing.Optional[jsii.Number],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8781a59cfd1f582546f670b6d7160c042c87d189750aadf4049629531a20ee2d(
    value: typing.Optional[jsii.Number],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__aab6b3320c8b5ed180393e3c8ec006f176de4327b6a5b590518821d90402ce62(
    value: typing.Optional[builtins.bool],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6c9513a7ba0dde9719e51014f59729062305e49ba15efc3c6b984a2b9a3d7afa(
    value: typing.Optional[builtins.bool],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9cc7e596f4e2e98b431d1d318feacf1d54de3f07128a7915e5f490682a616c38(
    value: typing.Optional[builtins.bool],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e83f530d6fd4975a5e9d833601a1ba0da602461338158552839c08cc7c68ad2a(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__803d555a4687b09617efeca6555c9a0c547d208cce4b3fcba260e656293b0431(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__bf82256371e8af18d733cf6e3576565fb3fee322e1407ba32d4a58936e43706a(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b6391c87993381eb2a1cfbce502581139547eeb293036255195358364394c1a2(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f6713b2f9883a94ac79a38204e71ea4ae51126ab1edd725ba4a3212febdbe452(
    value: typing.Optional[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__19e0f22afb0ccb009b081a3a2dde585905ec7100821d6fe298055b70203de58b(
    value: typing.Optional[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__137fca5161fc7e4ca23828405348297e920b18f1756c88fe540ddc51cb6236a6(
    value: typing.Optional[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__40cb0d93da14f245fdd64661d854a8ff7a48ca8ae17e8422d6d7abb3f1b84729(
    value: typing.Optional[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__01266709283dc90708ae25e398a73b2fefe17d335fdedf6e00e53105c9042b98(
    value: typing.Optional[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6b7987528ff7f20ab7c9b57c03cb4200d426cfc4f42e4d087d1087d2e010bc2e(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5cd6caa9ce412a3d7dbf5f4803c5781f7ad18ad5af3dd94d6eb44fb8022a7208(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e75f8983aceb72f5d0a898866d8ef93bd886a0571063067b93fb841b37ea8bf1(
    value: typing.Optional[ITotpConfig],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1c3d1768c8b547fb8817bdfa19adf45fd71dd0c16f8bec762030bcb045600f3a(
    value: IEnvironment,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e10343c0aaa52fc59631fd2790032d49abc24601a170075c2307c3b55ab18e74(
    value: typing.List[typing.Union[IActiveScan, IActiveScanPolicy, IActiveScanConfig, ISpider, IDelay, IExitStatus, IExport, IGraphQL, IImport, IOpenAPI, IPassiveScanConfig, IPassiveScanWait, IPostman, IReplacer, IReport, IRequest, ISoap, ISpiderAjax, INewType]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__26d928c212bff21972591897dd0fa374d6662598c7dd3a7d33a2229d5c555748(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    props: IImportProps,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__91f4aa3c97d70788796568533de68f0826274de23c38775784854ae1dd0e1d6d(
    value: IImport,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e84fd801092de50427019c50b1916f2044d763eb6faf4474e9e439fe613097df(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    props: IOpenAPIProps,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__862e0d1b2fabc46f6f0ec2ff29cd9ab00ce2e6d42ea979e19f3afcd195c45b49(
    value: IOpenAPI,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d7bda6e25a77f58d3d499466dc1cb176f766470ba980fd72caba067bc6b93160(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    props: IPassiveScanConfigProps,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__03175aafaf9dadbb01efc59110074f8f5abbd460ce318c55ff6120fc8f98f2a7(
    value: IPassiveScanConfig,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__889cfef0a8742ab06135a0a1b35c8c51a892501a22c65438c53da4f42e0656e4(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    props: IPassiveScanWaitProps,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f66e44b5e04a1d2c38c7d56ce6dc6e1687e41aec4899821d4efc493255a81af5(
    value: IPassiveScanWait,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__47bbc432f94ea291f2ebb484f7405595ee72a015361643fa2ffc8e88e7174ef5(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    props: IPostmanProps,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0448eb80f786ce36d7cab2fcd3d96fddddefcb6b87c9d69a9d799c74fb9e2779(
    value: IPostman,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ed55f033666d619960eecfd5017d594575a38d3d70f804468b091583137c4c87(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    props: IReplacerProps,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8a13461a6145882e5b81273307a882a17a6d5627bc4a8de7180e5e3980b31e33(
    value: IReplacer,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a3ebd374b9fc34e3882e5172f8bfc9b920322575de2dd6cd25b1204061c419f6(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    props: IReportProps,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8af3e2b0e8298faf714c686c34f9f3d4277a993a57fc90c95da847f2da4cea68(
    value: IReport,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__db36fdf220e388e6b7b448971359c7b60d3f85894ad5b7d3c2035e4e3779ca63(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    props: IRequestorProps,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1ea9f7c48a0630bbaa4320e90d21bfbea21b36d81f66defda4911592a25f7cf8(
    value: IRequestorParameters,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4843416f8cb2d6ddc2d95dee76d16aaa16d7b665896b761099b63fcd3c9d7f61(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    props: ISoapProps,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1583ccdd341a52f969ba35edf51f555f20581f1b5ed51f10001c954882d252bb(
    value: ISoap,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b4d659140e7795f6d597b0ba238bda72c634a517c6e6023d60e03c9c1739564d(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    props: ISpiderAjaxProps,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f72bf58a00298427f0770fbf482a2c76944db226c349c3bbdbdcd7799632b2b5(
    value: ISpiderAjax,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e0a5b68bfaae70f3bf1d2e6a569e34a8de569dd40a8dfa68ed210b730f07211a(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    spider: ISpider,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0583628a54d2e412fc72ea49e04114b8341fcbf24a5b80c3a000a99fadc461fa(
    value: ISpider,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__576c170c601ea46aa887ed94f5e04f3bf674a900b0d860cd9e126ae278b7586d(
    *,
    spider: ISpider,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3bd22a287a9c38de36d24543303284350f18de74cea65506c787999ec1bb8c92(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    props: IZap,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8f2016062e53ac595f4d1ec7fa18bc6a252c46924db45efa324aa4b2bc65bd98(
    value: IZap,
) -> None:
    """Type checking stubs"""
    pass
