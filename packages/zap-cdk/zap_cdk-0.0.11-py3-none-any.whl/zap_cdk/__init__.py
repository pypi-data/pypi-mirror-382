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


class ActiveScanConfigConstruct(
    _constructs_77d1e7e8.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="zap-cdk.ActiveScanConfigConstruct",
):
    '''Class representing the active scan configuration.

    :class: ActiveScanConfigConstruct
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
            type_hints = typing.get_type_hints(_typecheckingstub__723dfe17ccb2865059396c64422ebee3fe43fb92717124023c900be16aa09fa6)
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
            type_hints = typing.get_type_hints(_typecheckingstub__23fe837004c918d019ad1d9ff46e4fc05e1d4d707c26b227ec48fff9ca49fb37)
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

    :class: Request
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

    :class: Request
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

    :class: RequestorParameters
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

    :class: RequestorParameters
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


@jsii.implements(IImport)
class Import(metaclass=jsii.JSIIMeta, jsii_type="zap-cdk.Import"):
    def __init__(self, options: IImport) -> None:
        '''Creates an instance of Import.

        :param options: -

        :throws: Will throw an error if the fileName is not provided.

        Example::

            const importConfig = new Import({
              type: 'har',
              fileName: 'import.har'
            });
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ae9262485b3495d63b5010496abea9960dd3d43070751056147f1f81d280a07a)
            check_type(argname="argument options", value=options, expected_type=type_hints["options"])
        jsii.create(self.__class__, self, [options])

    @builtins.property
    @jsii.member(jsii_name="fileName")
    def file_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "fileName"))

    @file_name.setter
    def file_name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b50ba4456d4b7757435923c5400cef22f2ae1e95ec3c24bd597e412b0d0b4fd6)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "fileName", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="type")
    def type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "type"))

    @type.setter
    def type(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__eb3999b9021490cbcfd55533aeb28c322c6ab7849480982f15963b9e8034d66e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "type", value) # pyright: ignore[reportArgumentType]


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


@jsii.implements(IInputVectors)
class InputVectors(metaclass=jsii.JSIIMeta, jsii_type="zap-cdk.InputVectors"):
    '''Class representing the configuration for input vectors used in an active scan.

    :implements: IInputVectors *
    :property: {boolean} [scripts] - If Input Vector scripts should be used. Default: true.

    Example::

        const inputVectorsConfig = new InputVectors({
          urlQueryStringAndDataDrivenNodes: new UrlQueryStringAndDataDrivenNodes(),
          postData: new PostData(),
    '''

    def __init__(self, options: typing.Optional[IInputVectors] = None) -> None:
        '''Creates an instance of InputVectors.

        :param options: - The configuration options for input vectors.

        :memberof: InputVectors

        Example::

            const inputVectorsConfig = new InputVectors({
              urlQueryStringAndDataDrivenNodes: new UrlQueryStringAndDataDrivenNodes(),
              postData: new PostData(),
              urlPath: false,
              httpHeaders: new HttpHeaders(),
              cookieData: new CookieData(),
              scripts: true
            });
            console.log(inputVectorsConfig.postData.enabled); // true
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8cd02eaa881493a20e9c51c5aa93e03d17b6c9ccbb71a6dac952671317d0a0db)
            check_type(argname="argument options", value=options, expected_type=type_hints["options"])
        jsii.create(self.__class__, self, [options])

    @builtins.property
    @jsii.member(jsii_name="cookieData")
    def cookie_data(self) -> ICookieData:
        '''Configuration for cookie data scanning.'''
        return typing.cast(ICookieData, jsii.get(self, "cookieData"))

    @cookie_data.setter
    def cookie_data(self, value: ICookieData) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__51c10c9fb6ab81e903674e4f34ee3ef18f8180f08c9aa847b3a993e5f69a3d0b)
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
            type_hints = typing.get_type_hints(_typecheckingstub__6e97ec86572c44846c9f6994d334e0664a150f2ab2e2472a6f3c139ebcef283d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "httpHeaders", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="postData")
    def post_data(self) -> IPostData:
        '''Configuration for POST data scanning.'''
        return typing.cast(IPostData, jsii.get(self, "postData"))

    @post_data.setter
    def post_data(self, value: IPostData) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__da3a58d64f8f1df5b146ba07acef8bf1a2d1f67572a50ac60db33a9939e298f8)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "postData", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="urlQueryStringAndDataDrivenNodes")
    def url_query_string_and_data_driven_nodes(
        self,
    ) -> IUrlQueryStringAndDataDrivenNodes:
        '''Configuration for query parameters and data-driven nodes.'''
        return typing.cast(IUrlQueryStringAndDataDrivenNodes, jsii.get(self, "urlQueryStringAndDataDrivenNodes"))

    @url_query_string_and_data_driven_nodes.setter
    def url_query_string_and_data_driven_nodes(
        self,
        value: IUrlQueryStringAndDataDrivenNodes,
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__407c276df3ba7322af40923893a56b6750078fe6ad3ef61bb531ec2046f1b403)
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
            type_hints = typing.get_type_hints(_typecheckingstub__3ea3b6c8ba22594772036db26a1d90b958f0ec8353865bd36a14b5d755e1807c)
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
            type_hints = typing.get_type_hints(_typecheckingstub__2710a4c1ff157460d3d51fed9f190aa29ee4fec96a8ed6aff3b71ea4b1a45f8e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "urlPath", value) # pyright: ignore[reportArgumentType]


@jsii.implements(IJsonPostData)
class JsonPostData(metaclass=jsii.JSIIMeta, jsii_type="zap-cdk.JsonPostData"):
    '''Class representing the configuration for JSON body scanning in POST data.

    :implements: IJsonPostData *
    :property: {boolean} [scanNullValues] - If null values should be scanned. Default: false.

    Example::

        const jsonConfig = new JsonPostData({ enabled: true, scanNullValues: false });
        console.log(jsonConfig.enabled); // true
    '''

    def __init__(self, options: typing.Optional[IJsonPostData] = None) -> None:
        '''Creates an instance of JsonPostData.

        :param options: - The configuration options for JSON scanning.

        :memberof: JsonPostData

        Example::

            const jsonConfig = new JsonPostData({ enabled: true, scanNullValues: false });
            console.log(jsonConfig.enabled); // true
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f7bd714d4062469ab3a01a61e4b0d072cd911a74eee184ff27d0d070380a4d9d)
            check_type(argname="argument options", value=options, expected_type=type_hints["options"])
        jsii.create(self.__class__, self, [options])

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
            type_hints = typing.get_type_hints(_typecheckingstub__9f10fea9424c61881badd4c03e00d0cde227d8f05926f19fcc47400e3b31de36)
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
            type_hints = typing.get_type_hints(_typecheckingstub__3ecdbdb392b5d3039240a2a5c088ba1de75eaf96a20889235c87722f0efc0b94)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "scanNullValues", value) # pyright: ignore[reportArgumentType]


@jsii.implements(IMonitorTest)
class MonitorTest(metaclass=jsii.JSIIMeta, jsii_type="zap-cdk.MonitorTest"):
    '''Class representing a monitor test.

    :class: MonitorTest
    :implements: IMonitorTest *
    :property: {OnFailType} onFail - Action to take on failure, mandatory.

    Example::

        const monitorTest = new MonitorTest({
          name: 'test one',
          statistic: 'stats.addon.something',
          site: 'MySite',
          onFail: 'info'
        });
    '''

    def __init__(self, options: IMonitorTest) -> None:
        '''Creates an instance of MonitorTest.

        :param options: - The configuration options for the monitor test.

        :property: {OnFailType} options.onFail - Action to take on failure, mandatory.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__60c6528d04afe806304eab67b59fcbd27013f766e7b55dc577bf7659cf98a5b8)
            check_type(argname="argument options", value=options, expected_type=type_hints["options"])
        jsii.create(self.__class__, self, [options])

    @builtins.property
    @jsii.member(jsii_name="onFail")
    def on_fail(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "onFail"))

    @on_fail.setter
    def on_fail(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4ec2bf7be2e1a6a400c0050d18a031d35e29d4685db736908fb682f50d1611d3)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "onFail", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="statistic")
    def statistic(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "statistic"))

    @statistic.setter
    def statistic(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0232c40c34a1a08a528559bb28c4392cb66edd3af1a1337f5cf909471f9ef7ef)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "statistic", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="type")
    def type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "type"))

    @type.setter
    def type(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d316662cb1e3d3c02ecfa775ed3c1a7086fe851b8cc75f37530a19e775f64565)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "type", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "name"))

    @name.setter
    def name(self, value: typing.Optional[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__002197728fb3715405e8d942ed84a0e94cb86527c61cbf8abc4e8d3999b32751)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "name", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="site")
    def site(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "site"))

    @site.setter
    def site(self, value: typing.Optional[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__860f1b4f94e6162f6de6c6d8211b1d23c0c95ed7f6a0aecd37679af815eb1e9f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "site", value) # pyright: ignore[reportArgumentType]


@jsii.implements(IOpenAPI)
class OpenAPI(metaclass=jsii.JSIIMeta, jsii_type="zap-cdk.OpenAPI"):
    '''Class representing the OpenAPI import configuration.

    :class: OpenAPI
    :implements: IOpenAPI *
    :property: {string} [targetUrl] - URL which overrides the target defined in the definition, default: null.

    Example::

        const openApiConfig = new OpenAPI({
          apiFile: 'api-definition.yaml',
          context: 'MyContext',
          user: 'apiUser',
          targetUrl: 'https://api.example.com'
        });
    '''

    def __init__(self, options: IOpenAPI) -> None:
        '''Creates an instance of OpenAPI.

        :param options: - The options to initialize the OpenAPI configuration.

        :property: {string} [options.targetUrl] - URL which overrides the target defined in the definition, default: null.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__99287435a763381828ba2c0438ad1898177718304311bfa17424468a33b583e8)
            check_type(argname="argument options", value=options, expected_type=type_hints["options"])
        jsii.create(self.__class__, self, [options])

    @builtins.property
    @jsii.member(jsii_name="apiFile")
    def api_file(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "apiFile"))

    @api_file.setter
    def api_file(self, value: typing.Optional[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f16f5f25e9bb2409ddc4d89b08af25300d67081cdaf738a5853564352a54f29b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "apiFile", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="apiUrl")
    def api_url(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "apiUrl"))

    @api_url.setter
    def api_url(self, value: typing.Optional[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2988a6260dfcdc1177c6e94ad655c41b15fc2ba932a34abc5f845eb3001388de)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "apiUrl", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="context")
    def context(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "context"))

    @context.setter
    def context(self, value: typing.Optional[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__629b5cd81900c1bd79c3f757622ac3dc37dcf96a34eb42b1cb8f7c8acd5bfc78)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "context", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="targetUrl")
    def target_url(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "targetUrl"))

    @target_url.setter
    def target_url(self, value: typing.Optional[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e51e4398843496092d69a604c0f102154fb3ffd36e42812c77fd00e269465139)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "targetUrl", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="user")
    def user(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "user"))

    @user.setter
    def user(self, value: typing.Optional[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3ac8ec5b156603d835c2bb00fa4bdf7abdc68b9fff4be6024db36785c7f69968)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "user", value) # pyright: ignore[reportArgumentType]


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


@jsii.implements(IPassiveScanConfig)
class PassiveScanConfig(metaclass=jsii.JSIIMeta, jsii_type="zap-cdk.PassiveScanConfig"):
    '''Class representing the passive scan configuration.

    :class: PassiveScanConfig
    :implements: IPassiveScanConfig *

    Example::

        const passiveScanConfig = new PassiveScanConfig({
          parameters: {
            maxAlertsPerRule: 5,
            scanOnlyInScope: true,
            maxBodySizeInBytesToScan: 0,
            enableTags: false,
            disableAllRules: true
          },
          rules: [
            { id: 10010, name: 'Cross-Domain Misconfiguration', threshold: 'Medium' },
            { id: 10011, name: 'CSP Header Not Set', threshold: 'High' }
          ],
          enabled: true,
          alwaysRun: false
        });
    '''

    def __init__(self, options: IPassiveScanConfig) -> None:
        '''Creates an instance of PassiveScanConfig.

        :param options: - The options to initialize the passive scan configuration.

        :property: {boolean} [options.alwaysRun=false] - If set and the job is enabled, then it will run even if the plan exits early, default: false.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d7bda6e25a77f58d3d499466dc1cb176f766470ba980fd72caba067bc6b93160)
            check_type(argname="argument options", value=options, expected_type=type_hints["options"])
        jsii.create(self.__class__, self, [options])

    @builtins.property
    @jsii.member(jsii_name="parameters")
    def parameters(self) -> IPassiveScanParameters:
        return typing.cast(IPassiveScanParameters, jsii.get(self, "parameters"))

    @parameters.setter
    def parameters(self, value: IPassiveScanParameters) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__98d408c2c5062051f60e28bff492d16546367c406232e99ef3c0c1601aabb0f2)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "parameters", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="type")
    def type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "type"))

    @type.setter
    def type(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c18b570068429b31a72fb9932007cd3929adf86bf8e414761911815af2d30f42)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "type", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="alwaysRun")
    def always_run(self) -> typing.Optional[builtins.bool]:
        return typing.cast(typing.Optional[builtins.bool], jsii.get(self, "alwaysRun"))

    @always_run.setter
    def always_run(self, value: typing.Optional[builtins.bool]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__311730f720b5388c124c5d09045f0fc6bb7437256c588bd617d6b518905effe6)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "alwaysRun", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="enabled")
    def enabled(self) -> typing.Optional[builtins.bool]:
        return typing.cast(typing.Optional[builtins.bool], jsii.get(self, "enabled"))

    @enabled.setter
    def enabled(self, value: typing.Optional[builtins.bool]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0110420decb8f9c3946e99a1b826ecc7c5a2864550c1f54c099ba8ed36e94d7b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "enabled", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="rules")
    def rules(self) -> typing.Optional[typing.List[IPassiveScanRule]]:
        return typing.cast(typing.Optional[typing.List[IPassiveScanRule]], jsii.get(self, "rules"))

    @rules.setter
    def rules(self, value: typing.Optional[typing.List[IPassiveScanRule]]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__364eb3b49d38aa1278ae3b3bd97edf2bd0fdf11cd0ce92ead1cbb5ba3a775b17)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "rules", value) # pyright: ignore[reportArgumentType]


class PassiveScanConfigConstruct(
    _constructs_77d1e7e8.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="zap-cdk.PassiveScanConfigConstruct",
):
    '''Class representing the passive scan configuration.

    :class: PassiveScanConfigConstruct
    :extends: Construct
    '''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        props: IPassiveScanConfigProps,
    ) -> None:
        '''Creates an instance of PassiveScanConfigConstruct.

        :param scope: - The scope in which this construct is defined.
        :param id: - The ID of the construct.
        :param props: - The properties of the passive scan configuration.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__41a310fa8ccd2b8a3839d98abb7586268af7c21df91fb133706f0992959dd295)
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
            type_hints = typing.get_type_hints(_typecheckingstub__e067afd320b53600be7f0c4ac781a9b0ff0bdadc83b2af89793699205cd532b3)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "config", value) # pyright: ignore[reportArgumentType]


@jsii.implements(IPassiveScanParameters)
class PassiveScanParameters(
    metaclass=jsii.JSIIMeta,
    jsii_type="zap-cdk.PassiveScanParameters",
):
    '''Class representing the parameters for configuring a passive scan.

    :class: PassiveScanParameters
    :implements: IPassiveScanParameters *

    Example::

        const passiveScanParams = new PassiveScanParameters({
          maxAlertsPerRule: 5,
          scanOnlyInScope: true,
          maxBodySizeInBytesToScan: 0,
          enableTags: false,
          disableAllRules: true
        });
    '''

    def __init__(self, options: IPassiveScanParameters) -> None:
        '''Creates an instance of PassiveScanParameters.

        :param options: - The options to initialize the passive scan parameters.

        :property: {boolean} [options.disableAllRules] - If true, then will disable all rules before applying the settings in the rules section.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a369d413b10f47648c36d198ae533607faede10ab301ea81fa93d124259720f8)
            check_type(argname="argument options", value=options, expected_type=type_hints["options"])
        jsii.create(self.__class__, self, [options])

    @builtins.property
    @jsii.member(jsii_name="disableAllRules")
    def disable_all_rules(self) -> typing.Optional[builtins.bool]:
        return typing.cast(typing.Optional[builtins.bool], jsii.get(self, "disableAllRules"))

    @disable_all_rules.setter
    def disable_all_rules(self, value: typing.Optional[builtins.bool]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7d7bdecc91f90ccf8054e24484b8c9a6fd2b1f40b5f7b31317bd8fbcafeba9d5)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "disableAllRules", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="enableTags")
    def enable_tags(self) -> typing.Optional[builtins.bool]:
        return typing.cast(typing.Optional[builtins.bool], jsii.get(self, "enableTags"))

    @enable_tags.setter
    def enable_tags(self, value: typing.Optional[builtins.bool]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e45b7b332bfc26a5522670c1b2b354214100826bd28023e138167dd2cf85efd9)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "enableTags", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="maxAlertsPerRule")
    def max_alerts_per_rule(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "maxAlertsPerRule"))

    @max_alerts_per_rule.setter
    def max_alerts_per_rule(self, value: typing.Optional[jsii.Number]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__846c438f7445432740e7111d7aee94ba6486ae123ae9ee657ef95fbcc6f7497f)
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
            type_hints = typing.get_type_hints(_typecheckingstub__68c42454bb94e6819bdae7999ea18797a10e953ea486eef6bfda75ce91c3e2e4)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "maxBodySizeInBytesToScan", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="scanOnlyInScope")
    def scan_only_in_scope(self) -> typing.Optional[builtins.bool]:
        return typing.cast(typing.Optional[builtins.bool], jsii.get(self, "scanOnlyInScope"))

    @scan_only_in_scope.setter
    def scan_only_in_scope(self, value: typing.Optional[builtins.bool]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__10f96ddcbf046a47d09ad7e3dc49cad8ec05db74d0fd64b30bb387642a81d8e3)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "scanOnlyInScope", value) # pyright: ignore[reportArgumentType]


@jsii.implements(IPassiveScanRule)
class PassiveScanRule(metaclass=jsii.JSIIMeta, jsii_type="zap-cdk.PassiveScanRule"):
    '''Class representing a passive scan rule configuration.

    :class: PassiveScanRule
    :implements: IPassiveScanRule *

    Example::

        const passiveScanRule = new PassiveScanRule({
          id: 10010,
          name: 'Cross-Domain Misconfiguration',
          threshold: 'Medium'
        });
    '''

    def __init__(self, options: IPassiveScanRule) -> None:
        '''Creates an instance of PassiveScanRule.

        :param options: - The options to initialize the passive scan rule.

        :property: {'Off' | 'Low' | 'Medium' | 'High'} [options.threshold='Medium'] - The Alert Threshold for this rule, default: Medium.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__93ac98e339102cd68a776f9fe4819d8c93b697c1b6e7e9316948979ad49041d8)
            check_type(argname="argument options", value=options, expected_type=type_hints["options"])
        jsii.create(self.__class__, self, [options])

    @builtins.property
    @jsii.member(jsii_name="id")
    def id(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "id"))

    @id.setter
    def id(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__afdc8855188221ace931a532c1f5489ae269494c65190e5062dadb39356cdb87)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "id", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "name"))

    @name.setter
    def name(self, value: typing.Optional[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__05be68b0347a6a5a19d98baa7a9398e27247acd7d4dff10e35155cda1fdebfea)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "name", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="threshold")
    def threshold(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "threshold"))

    @threshold.setter
    def threshold(self, value: typing.Optional[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f8da2b6c3807e7aabe29cfcc10cba4c3b395bae3b810824bd1873ddfb699ad61)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "threshold", value) # pyright: ignore[reportArgumentType]


@jsii.implements(IPassiveScanWait)
class PassiveScanWait(metaclass=jsii.JSIIMeta, jsii_type="zap-cdk.PassiveScanWait"):
    '''Class representing the configuration for waiting during a passive scan.

    :class: PassiveScanWait
    :implements: IPassiveScanWait *

    Example::

        const passiveScanWaitConfig = new PassiveScanWait({
          maxDuration: 300
        });
    '''

    def __init__(self, max_duration: typing.Optional[jsii.Number] = None) -> None:
        '''Creates an instance of PassiveScanWait.

        :param max_duration: - The max time to wait for the passive scanner, default: 0 (unlimited).
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__fd1027f82784b7836e3420252e40b7817c41ea2adb0cc30c8b726012909507cb)
            check_type(argname="argument max_duration", value=max_duration, expected_type=type_hints["max_duration"])
        jsii.create(self.__class__, self, [max_duration])

    @builtins.property
    @jsii.member(jsii_name="maxDuration")
    def max_duration(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "maxDuration"))

    @max_duration.setter
    def max_duration(self, value: typing.Optional[jsii.Number]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__de49989d8e7e1331f2b355ac905b276332c5f3d19c0302389191a4bb1bf1ac92)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "maxDuration", value) # pyright: ignore[reportArgumentType]


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


@jsii.implements(IPolicyDefinition)
class PolicyDefinition(metaclass=jsii.JSIIMeta, jsii_type="zap-cdk.PolicyDefinition"):
    '''Class representing the policy definition for an active scan.

    :implements: IPolicyDefinition *
    :property: {string} [rules[].threshold] - The Alert Threshold for this rule, one of Off, Low, Medium, High, default: Medium.
    '''

    def __init__(self, options: typing.Optional[IPolicyDefinition] = None) -> None:
        '''Creates an instance of PolicyDefinition.

        :param options: - The policy definition details.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__bf38b1864c290187f86b9b468047ef42da4404f07c325c7fdedb111fe13c2715)
            check_type(argname="argument options", value=options, expected_type=type_hints["options"])
        jsii.create(self.__class__, self, [options])

    @builtins.property
    @jsii.member(jsii_name="alertTags")
    def alert_tags(self) -> typing.Optional[IAlertTags]:
        return typing.cast(typing.Optional[IAlertTags], jsii.get(self, "alertTags"))

    @alert_tags.setter
    def alert_tags(self, value: typing.Optional[IAlertTags]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d758ef6acd3f0901f9095eb3037e6ef9df3a52a62d500d733b880cfd95fb0373)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "alertTags", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="defaultStrength")
    def default_strength(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "defaultStrength"))

    @default_strength.setter
    def default_strength(self, value: typing.Optional[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6d12470d0b422824c9b58864e9f0e9a8a2bc11e8f80060c8b6e5e35aa3afa6b2)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "defaultStrength", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="defaultThreshold")
    def default_threshold(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "defaultThreshold"))

    @default_threshold.setter
    def default_threshold(self, value: typing.Optional[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1588a75d23e4a613b56e8877b7ff67b51143416bb33b38b4b967f309094329da)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "defaultThreshold", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="rules")
    def rules(self) -> typing.Optional[typing.List[IRules]]:
        return typing.cast(typing.Optional[typing.List[IRules]], jsii.get(self, "rules"))

    @rules.setter
    def rules(self, value: typing.Optional[typing.List[IRules]]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__18476c8b564c999623ea81a028f2a12f56c991afe8e306aa2b9583b938326ff7)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "rules", value) # pyright: ignore[reportArgumentType]


@jsii.implements(IPollAdditionalHeaders)
class PollAdditionalHeaders(
    metaclass=jsii.JSIIMeta,
    jsii_type="zap-cdk.PollAdditionalHeaders",
):
    '''Represents additional headers for poll request in authentication verification.

    :class: PollAdditionalHeaders
    :implements: IPollAdditionalHeaders *
    :property: {string} value - The header value.
    '''

    def __init__(self, options: IPollAdditionalHeaders) -> None:
        '''Creates an instance of PollAdditionalHeaders.

        :param options: - The options to initialize the headers.

        :property: {string} [options.value] - The header value.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0b7caa40c2f337f6483bc12147498eb13ff3e34a573d21e8778bc54c6dc1c3ed)
            check_type(argname="argument options", value=options, expected_type=type_hints["options"])
        jsii.create(self.__class__, self, [options])

    @builtins.property
    @jsii.member(jsii_name="header")
    def header(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "header"))

    @header.setter
    def header(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e9816da747828200e0cd469e343ab2772744e2b27a036bd7cf3cdd370467eba5)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "header", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="value")
    def value(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "value"))

    @value.setter
    def value(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1a7a431b085e4a138f998fa836a2696b0572a34a7b6b11a00b226fe9b2513286)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "value", value) # pyright: ignore[reportArgumentType]


@jsii.implements(IPostData)
class PostData(metaclass=jsii.JSIIMeta, jsii_type="zap-cdk.PostData"):
    '''Class representing the configuration for POST data scanning.

    :implements: IPostData *
    :property: {boolean} [directWebRemoting] - If DWR scanning should be enabled. Default: false.

    Example::

        const postDataConfig = new PostData({ enabled: true, multiPartFormData: true, xml: true, json: new JsonPostData(), googleWebToolkit: false, directWebRemoting: false });
        console.log(postDataConfig.enabled); // true
    '''

    def __init__(self, options: typing.Optional[IPostData] = None) -> None:
        '''Creates an instance of PostData.

        :param options: - The configuration options for POST data scanning.

        :memberof: PostData

        Example::

            const postDataConfig = new PostData({ enabled: true, multiPartFormData: true, xml: true, json: new JsonPostData(), googleWebToolkit: false, directWebRemoting: false });
            console.log(postDataConfig.enabled); // true
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c4babefe72d93be8beb83f01e5585488024e3a19694d6b3dcbd481d31b628727)
            check_type(argname="argument options", value=options, expected_type=type_hints["options"])
        jsii.create(self.__class__, self, [options])

    @builtins.property
    @jsii.member(jsii_name="json")
    def json(self) -> IJsonPostData:
        '''Configuration for JSON bodies.'''
        return typing.cast(IJsonPostData, jsii.get(self, "json"))

    @json.setter
    def json(self, value: IJsonPostData) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f28a29365dc2f7cb147977280b59876cc30285949a8f8ddcc995a87a388a3948)
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
            type_hints = typing.get_type_hints(_typecheckingstub__8ac87b25d7a9a276871f1e44bbca15b7bedd02ab258913d61864ccbcffee3632)
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
            type_hints = typing.get_type_hints(_typecheckingstub__6b9a46ad010de4f08d938001f7afbb934a3e88d283a24d3ea25aeb0396e12bab)
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
            type_hints = typing.get_type_hints(_typecheckingstub__df99e80072bca3065152cc071cfd6e6318d6d5df37537a88bcab4f544fde90ec)
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
            type_hints = typing.get_type_hints(_typecheckingstub__06e443d723c93647ce20a9d35014c3b4e3728b19789d9b8abcf5e0390e4cd97f)
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
            type_hints = typing.get_type_hints(_typecheckingstub__729f7dcd5684d809dd04f4ce0788e25bd36cf29d5d73485d5b33bc54fe9f5853)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "xml", value) # pyright: ignore[reportArgumentType]


@jsii.implements(IPostman)
class Postman(metaclass=jsii.JSIIMeta, jsii_type="zap-cdk.Postman"):
    '''Class representing the Postman import configuration.

    :class: Postman
    :implements: IPostman *
    :property: {string} [variables] - Comma-separated list of variables as key-value pairs.

    Example::

        const postmanConfig = new Postman({
          collectionFile: 'postman-collection.json',
          variables: 'baseUrl=https://api.example.com,apiKey=12345'
        });
    '''

    def __init__(self, options: IPostman) -> None:
        '''Creates an instance of Postman.

        :param options: - The options to initialize the Postman configuration.

        :property: {string} [options.variables] - Comma-separated list of variables as key-value pairs.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c3d81267406fb2aa6ccf20039eabfd98427283dec51869b07fa444047ce34482)
            check_type(argname="argument options", value=options, expected_type=type_hints["options"])
        jsii.create(self.__class__, self, [options])

    @builtins.property
    @jsii.member(jsii_name="collectionFile")
    def collection_file(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "collectionFile"))

    @collection_file.setter
    def collection_file(self, value: typing.Optional[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8d1aed4ff6ddece407e1977f31d9ef5a45a3463e9bd4005ba050487866896573)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "collectionFile", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="collectionUrl")
    def collection_url(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "collectionUrl"))

    @collection_url.setter
    def collection_url(self, value: typing.Optional[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c1b200c1ceeffffc1dc49d39f270599fbb63b89e4de83a853215f0f78f855b28)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "collectionUrl", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="variables")
    def variables(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "variables"))

    @variables.setter
    def variables(self, value: typing.Optional[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b8cf1950596db474221c1e0f10c6b1fd4892f3f5356091e6f3dd12b150e41c96)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "variables", value) # pyright: ignore[reportArgumentType]


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


@jsii.implements(IReplacer)
class Replacer(metaclass=jsii.JSIIMeta, jsii_type="zap-cdk.Replacer"):
    '''Class representing the configuration for string replacement rules.

    :class: Replacer
    :implements: IReplacer *

    Example::

        const replacerConfig = new Replacer({
          deleteAllRules: true,
          rules: [
            new ReplacerRule({
              description: 'Replace API Key',
              url: '.*example.*',
              matchType: 'req_header_str',
              matchString: 'API-Key: .*',
              matchRegex: true,
              replacementString: 'API-Key: 12345',
              tokenProcessing: false,
              initiators: [1, 2, 3]
            })
          ]
        });
    '''

    def __init__(self, options: IReplacer) -> None:
        '''Creates an instance of Replacer.

        :param options: - The options to initialize the replacer configuration.

        :property: {IReplacerRule[]} options.rules - A list of replacer rules.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e006c9ca2f0b1a84fa007ccc42e191b223fad827745e93ce401aa8353953ba9e)
            check_type(argname="argument options", value=options, expected_type=type_hints["options"])
        jsii.create(self.__class__, self, [options])

    @builtins.property
    @jsii.member(jsii_name="rules")
    def rules(self) -> typing.List[IReplacerRule]:
        return typing.cast(typing.List[IReplacerRule], jsii.get(self, "rules"))

    @rules.setter
    def rules(self, value: typing.List[IReplacerRule]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__597cfbd7b08edde963d3f7e2e2fbc20642ecc8d0200710a88a1f611d3f3b21b1)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "rules", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="deleteAllRules")
    def delete_all_rules(self) -> typing.Optional[builtins.bool]:
        return typing.cast(typing.Optional[builtins.bool], jsii.get(self, "deleteAllRules"))

    @delete_all_rules.setter
    def delete_all_rules(self, value: typing.Optional[builtins.bool]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__25b36626eabaf1ac3470d5cd48b3908075fbff37ee33189e282291d817f2ec4c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "deleteAllRules", value) # pyright: ignore[reportArgumentType]


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


@jsii.implements(IReplacerRule)
class ReplacerRule(metaclass=jsii.JSIIMeta, jsii_type="zap-cdk.ReplacerRule"):
    '''Class representing a rule for replacing strings in requests or responses.

    :class: ReplacerRule
    :implements: IReplacerRule *

    Example::

        const replacerRule = new ReplacerRule({
          description: 'Replace API Key',
          url: '.*example.*',
          matchType: 'req_header_str',
          matchString: 'API-Key: .*',
          matchRegex: true,
          replacementString: 'API-Key: 12345',
          tokenProcessing: false,
          initiators: [1, 2, 3]
        });
    '''

    def __init__(self, options: IReplacerRule) -> None:
        '''Creates an instance of ReplacerRule.

        :param options: - The configuration options for the replacer rule.

        :property: {number[]} [options.initiators] - A list of integers representing the initiators.

        Example::

            const replacerRule = new ReplacerRule({
              description: 'Replace API Key',
              url: '.*example.*',
              matchType: 'req_header_str',
              matchString: 'API-Key: .*',
              matchRegex: true,
              replacementString: 'API-Key: 12345',
              tokenProcessing: false,
              initiators: [1, 2, 3]
            });
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__da41296778627d8ea25869142c9a5af37814c92a2ceeebd044b9ab5541c220b2)
            check_type(argname="argument options", value=options, expected_type=type_hints["options"])
        jsii.create(self.__class__, self, [options])

    @builtins.property
    @jsii.member(jsii_name="description")
    def description(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "description"))

    @description.setter
    def description(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4bd1fd4da74e3aa0ac009cf2ee0c37a81168bbf9599fe0bace546d4f2cc79c6c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "description", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="matchString")
    def match_string(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "matchString"))

    @match_string.setter
    def match_string(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e39dfcd3351df507d625671675608fd43fff13bcc5b4c7af2d25858f770f0969)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "matchString", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="matchType")
    def match_type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "matchType"))

    @match_type.setter
    def match_type(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f5d1f61da2ed6c5abab1b903a7e4fa5bd1acdee2829034c7b2dc952eac312071)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "matchType", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="replacementString")
    def replacement_string(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "replacementString"))

    @replacement_string.setter
    def replacement_string(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__18063198eed2467aa5b678b9356389bd3e9f2eb47c18896aaa03281d93e47c61)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "replacementString", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="initiators")
    def initiators(self) -> typing.Optional[typing.List[jsii.Number]]:
        return typing.cast(typing.Optional[typing.List[jsii.Number]], jsii.get(self, "initiators"))

    @initiators.setter
    def initiators(self, value: typing.Optional[typing.List[jsii.Number]]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__42d21c224b3ba5746669c5c6d54313613f4c90ac59cd40eb83152adb0df55d54)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "initiators", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="matchRegex")
    def match_regex(self) -> typing.Optional[builtins.bool]:
        return typing.cast(typing.Optional[builtins.bool], jsii.get(self, "matchRegex"))

    @match_regex.setter
    def match_regex(self, value: typing.Optional[builtins.bool]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4aa72921e49acb27554030d6502efa33b8277a9f6a10e46a71a02c6ceb5ba4f7)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "matchRegex", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="tokenProcessing")
    def token_processing(self) -> typing.Optional[builtins.bool]:
        return typing.cast(typing.Optional[builtins.bool], jsii.get(self, "tokenProcessing"))

    @token_processing.setter
    def token_processing(self, value: typing.Optional[builtins.bool]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__57f606a1a0ef083c2c9b249e33073c1188c1df3108048b86946af0888e451bfc)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "tokenProcessing", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="url")
    def url(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "url"))

    @url.setter
    def url(self, value: typing.Optional[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__198f2faaeebc7b6477b0f1e298d2b66c08ab2ec561fc977540e6f7b6b1ade2b7)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "url", value) # pyright: ignore[reportArgumentType]


@jsii.implements(IReport)
class Report(metaclass=jsii.JSIIMeta, jsii_type="zap-cdk.Report"):
    '''Class representing a report configuration.

    :implements: IReport *

    Example::

        const reportConfig = new Report({
          template: 'traditional-html',
          theme: 'corporate',
          reportDir: '/reports',
          reportFile: '{{yyyy-MM-dd}}-ZAP-Report-[[site]]',
          reportTitle: 'Weekly Security Report',
          reportDescription: 'This is the weekly security report generated by ZAP.',
          displayReport: true,
          risks: ['high', 'medium'],
          confidences: ['high', 'medium', 'low'],
          sections: ['alertSummary', 'siteSummary', 'alertsByRisk'],
          sites: ['https://example.com', 'https://another-example.com']
        });
    '''

    def __init__(self, options: IReport) -> None:
        '''Creates an instance of Report.

        :param options: - The options to initialize the report configuration.

        :property: {string[]} [options.sites] - The sites to include in this report, default all.

        Example::

            const reportConfig = new Report({
              template: 'traditional-html',
              theme: 'corporate',
              reportDir: '/reports',
              reportFile: '{{yyyy-MM-dd}}-ZAP-Report-[[site]]',
              reportTitle: 'Weekly Security Report',
              reportDescription: 'This is the weekly security report generated by ZAP.',
              displayReport: true,
              risks: ['high', 'medium'],
              confidences: ['high', 'medium', 'low'],
              sections: ['alertSummary', 'siteSummary', 'alertsByRisk'],
              sites: ['https://example.com', 'https://another-example.com']
            });
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__91225ae8d98ede25cf4d9aa8c4a8ddc3847eb3efcae23308f2a1a90b1181c046)
            check_type(argname="argument options", value=options, expected_type=type_hints["options"])
        jsii.create(self.__class__, self, [options])

    @builtins.property
    @jsii.member(jsii_name="confidences")
    def confidences(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "confidences"))

    @confidences.setter
    def confidences(self, value: typing.Optional[typing.List[builtins.str]]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8dc4a062c616bb609e6702501e06b5afeb68080e0666a8bc1128db0c10ff6e2b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "confidences", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="displayReport")
    def display_report(self) -> typing.Optional[builtins.bool]:
        return typing.cast(typing.Optional[builtins.bool], jsii.get(self, "displayReport"))

    @display_report.setter
    def display_report(self, value: typing.Optional[builtins.bool]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__30ff975397f8106db0da742319373da1d38b9bbad0926820f4bd200ccacbf5e3)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "displayReport", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="reportDescription")
    def report_description(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "reportDescription"))

    @report_description.setter
    def report_description(self, value: typing.Optional[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5fb200b691d9cc5e4ab2ecb6a8c73bfe036ba438fc712ea570667219f8a911a0)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "reportDescription", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="reportDir")
    def report_dir(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "reportDir"))

    @report_dir.setter
    def report_dir(self, value: typing.Optional[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d8817e70dfd59854b3a125bb5e4e7ed7fcd70b73a391d7ccd52c8704d120af41)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "reportDir", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="reportFile")
    def report_file(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "reportFile"))

    @report_file.setter
    def report_file(self, value: typing.Optional[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__fca3ced659d95beb5e8a64d99c2cd8a4d512c193470097cf3f1d8d6616788532)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "reportFile", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="reportTitle")
    def report_title(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "reportTitle"))

    @report_title.setter
    def report_title(self, value: typing.Optional[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__70f7476ca9462dd3127da48bde5a81810e8222709b3d9ddb5166db0a08cdc555)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "reportTitle", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="risks")
    def risks(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "risks"))

    @risks.setter
    def risks(self, value: typing.Optional[typing.List[builtins.str]]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3d1b5465d8673aed3d035d5a7fff5f77c2a0e178f731324395ecefdf37e69737)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "risks", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="sections")
    def sections(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "sections"))

    @sections.setter
    def sections(self, value: typing.Optional[typing.List[builtins.str]]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__06f2fd29a141b80145d1851a7417011f95fe4e72470865215fd6f9cde77f4ae6)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "sections", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="sites")
    def sites(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "sites"))

    @sites.setter
    def sites(self, value: typing.Optional[typing.List[builtins.str]]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__eaaa75394d9e2dadb4fd192bfd19d59f1a2f1b05955ad36a4ce263d265686197)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "sites", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="template")
    def template(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "template"))

    @template.setter
    def template(self, value: typing.Optional[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8dffb7c8f803f0e5107d50917fdcb4855624ee11387cb8088f1ade70a06bbc14)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "template", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="theme")
    def theme(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "theme"))

    @theme.setter
    def theme(self, value: typing.Optional[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2657cd3f94bce7e2206bae621f50b72b0e91734f5b3f214aebe25bb0bed67e7b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "theme", value) # pyright: ignore[reportArgumentType]


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


@jsii.implements(IRequest)
class Request(metaclass=jsii.JSIIMeta, jsii_type="zap-cdk.Request"):
    def __init__(self, options: IRequest) -> None:
        '''Creates an instance of Request.

        :param options: - The configuration options for the request.

        :property: {number} [options.responseCode] - Optional expected response code.

        Example::

            const request = new Request({
              url: 'https://example.com/api',
              method: 'POST',
              headers: ['Content-Type: application/json'],
              data: '{"key":"value"}',
              responseCode: 200
            });
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8c49b6f6a5b3d68fb766ea82d7b12e8e245995bf862fe5b4dc2d5c0cd5fb43fb)
            check_type(argname="argument options", value=options, expected_type=type_hints["options"])
        jsii.create(self.__class__, self, [options])

    @builtins.property
    @jsii.member(jsii_name="url")
    def url(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "url"))

    @url.setter
    def url(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__97a247fcf1d0d3178db895a6b620654d91235a488957458909bcf0653d3215b7)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "url", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="data")
    def data(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "data"))

    @data.setter
    def data(self, value: typing.Optional[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4f30543fd3a57b8a81924dad72dee21ee16cd915122b8f0a22a7e339d69fb6eb)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "data", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="headers")
    def headers(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "headers"))

    @headers.setter
    def headers(self, value: typing.Optional[typing.List[builtins.str]]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__16b128e45486b8eb9a94c94d5bddba113d0da381508ba969267300ec9643f228)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "headers", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="httpVersion")
    def http_version(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "httpVersion"))

    @http_version.setter
    def http_version(self, value: typing.Optional[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__efc63cf92f6143bb916fb0b3d33c1b6ac38bb191552705afc07ba3a2873df2d7)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "httpVersion", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="method")
    def method(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "method"))

    @method.setter
    def method(self, value: typing.Optional[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f00de859401602980d07158f8b734d689e7c563fd1d69cec3d373740c634b339)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "method", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "name"))

    @name.setter
    def name(self, value: typing.Optional[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__283fd6b407d89faaabb4ee0262624b5844ff7d02a45ce174a34ea1705ba819b6)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "name", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="responseCode")
    def response_code(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "responseCode"))

    @response_code.setter
    def response_code(self, value: typing.Optional[jsii.Number]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a848ee2973ccd6fc7f9cc6fc90cbe7928683adc6898a6cd4182c1a00af22a75e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "responseCode", value) # pyright: ignore[reportArgumentType]


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


@jsii.implements(IRequestorParameters)
class RequestorParameters(
    metaclass=jsii.JSIIMeta,
    jsii_type="zap-cdk.RequestorParameters",
):
    def __init__(self, options: IRequestorParameters) -> None:
        '''Creates an instance of RequestorParameters.

        :param options: - The configuration options for the requestor parameters.

        :property: {boolean} [options.alwaysRun] - If set and the job is enabled, it will run even if the plan exits early, default: false.

        Example::

            const requestorParams = new RequestorParameters({
              user: 'admin',
              requests: [
                new Request({ url: 'https://example.com/api1' }),
                new Request({ url: 'https://example.com/api2', method: 'POST' })
              ],
              enabled: true,
              alwaysRun: false
            });
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1a4aadd701722f907fdac037f2c2d67d0ab3a966f5a3d8daa396a56b69ddd89a)
            check_type(argname="argument options", value=options, expected_type=type_hints["options"])
        jsii.create(self.__class__, self, [options])

    @builtins.property
    @jsii.member(jsii_name="requests")
    def requests(self) -> typing.List[IRequest]:
        return typing.cast(typing.List[IRequest], jsii.get(self, "requests"))

    @requests.setter
    def requests(self, value: typing.List[IRequest]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__31721d47a8986ad6be735e8ebf5eedb82abf50f83eabdcbabc923f3ad0bc2835)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "requests", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="alwaysRun")
    def always_run(self) -> typing.Optional[builtins.bool]:
        return typing.cast(typing.Optional[builtins.bool], jsii.get(self, "alwaysRun"))

    @always_run.setter
    def always_run(self, value: typing.Optional[builtins.bool]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ad6c6e3908562f8989474133dd17ef3ef64fb51a875607f29abf64383e3cd158)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "alwaysRun", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="enabled")
    def enabled(self) -> typing.Optional[builtins.bool]:
        return typing.cast(typing.Optional[builtins.bool], jsii.get(self, "enabled"))

    @enabled.setter
    def enabled(self, value: typing.Optional[builtins.bool]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ffa61cadcffc518269d9b91a2bb57eb55acc662b22c11631cbc48393a7486aee)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "enabled", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="user")
    def user(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "user"))

    @user.setter
    def user(self, value: typing.Optional[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__10b96736257b6840d28d3fb98a5522865703fbdc1e1bdc6f7995d1d717507050)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "user", value) # pyright: ignore[reportArgumentType]


@jsii.implements(IRule)
class Rule(metaclass=jsii.JSIIMeta, jsii_type="zap-cdk.Rule"):
    '''Class representing an individual rule in the active scan policy.

    :class: Rule
    :implements: IRule *
    :property: {threshold} [threshold] - The Alert Threshold for this rule, default: Medium.
    '''

    def __init__(self, options: IRule) -> None:
        '''Creates an instance of Rule.

        :param options: - The configuration options for the rule.

        :property: {threshold} [options.threshold] - The Alert Threshold for this rule, default: Medium.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f9f847168b277cd1f4a14e8576f40abc4a27395e9514c666872915db8515b1f9)
            check_type(argname="argument options", value=options, expected_type=type_hints["options"])
        jsii.create(self.__class__, self, [options])

    @builtins.property
    @jsii.member(jsii_name="id")
    def id(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "id"))

    @id.setter
    def id(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__17e82a53e07f2e144ccbf3bc6a5aac30c57378b1c1c36691bb6b103d907a1fc8)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "id", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "name"))

    @name.setter
    def name(self, value: typing.Optional[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__953d96b3dca961a2983f76efd2849b57430fae57317ba0e17220e3907314e04a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "name", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="strength")
    def strength(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "strength"))

    @strength.setter
    def strength(self, value: typing.Optional[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2fee20f04cd336978abec955aa412d274a02f661c39f2bc96a794b418054a1f8)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "strength", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="threshold")
    def threshold(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "threshold"))

    @threshold.setter
    def threshold(self, value: typing.Optional[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__181f3f560fb6c8998c012bb9ae665fdda8fef0dbea7cc4c57494deeeeb5d8fbf)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "threshold", value) # pyright: ignore[reportArgumentType]


@jsii.implements(IRules)
class Rules(metaclass=jsii.JSIIMeta, jsii_type="zap-cdk.Rules"):
    '''Class representing a rule for the active scan.

    :implements: IRules *
    :property: {string} [threshold] - The Alert Threshold for this rule, one of Off, Low, Medium, High, default: Medium.
    '''

    def __init__(self, options: IRules) -> None:
        '''Creates an instance of Rules.

        :param options: - The rule details.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a56797b9c4452b42f38fac488a031d1d08450a0b960b3d1e8bf6541e4c772380)
            check_type(argname="argument options", value=options, expected_type=type_hints["options"])
        jsii.create(self.__class__, self, [options])

    @builtins.property
    @jsii.member(jsii_name="id")
    def id(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "id"))

    @id.setter
    def id(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__de5f3e28a821aca1e586a889c56d58913dbb100768683ea1872e70ee4dcc861d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "id", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "name"))

    @name.setter
    def name(self, value: typing.Optional[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ae47ba16b69a561fd681f5206820318e72dd5759a9f1a45f1b81de86aa92b6a5)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "name", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="strength")
    def strength(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "strength"))

    @strength.setter
    def strength(self, value: typing.Optional[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a47d9c5de1f7bc72009d8d63b0205c6195f393240f2461b3bf5fb72dcca38026)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "strength", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="threshold")
    def threshold(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "threshold"))

    @threshold.setter
    def threshold(self, value: typing.Optional[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7bcc737dcd77f280e1f39f8467725523ab030a14599888cb37c5905d247f0ff5)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "threshold", value) # pyright: ignore[reportArgumentType]


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


@jsii.implements(ISessionManagementParameters)
class SessionManagementParameters(
    metaclass=jsii.JSIIMeta,
    jsii_type="zap-cdk.SessionManagementParameters",
):
    '''Represents the parameters for session management in the scanning process.

    :class: SessionManagementParameters
    :implements: ISessionManagementParameters *
    :property: {string} [parameters.scriptEngine] - Name of the script engine to use, only for 'script' session management.
    '''

    def __init__(self, options: ISessionManagementParameters) -> None:
        '''Creates an instance of SessionManagementParameters.

        :param options: -

        :property: {string} [parameters.scriptEngine] - Name of the script engine to use, only for 'script' session management.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ed8687282b7c108721e28e88f2ec05ac393bc8bab90d92ccfe631c73338e4468)
            check_type(argname="argument options", value=options, expected_type=type_hints["options"])
        jsii.create(self.__class__, self, [options])

    @builtins.property
    @jsii.member(jsii_name="method")
    def method(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "method"))

    @method.setter
    def method(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a39a17a72b570dbf63b91b11954898391f5cf8276318aeea03723d57f415de63)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "method", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="parameters")
    def parameters(self) -> ISessionManagementParametersParameters:
        return typing.cast(ISessionManagementParametersParameters, jsii.get(self, "parameters"))

    @parameters.setter
    def parameters(self, value: ISessionManagementParametersParameters) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1e6d3d93ea8a8101f61e7d6ad433f5b0f8aed3fd4bab4f153b5bc55f0fbd5661)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "parameters", value) # pyright: ignore[reportArgumentType]


@jsii.implements(ISessionManagementParametersParameters)
class SessionManagementParametersParameters(
    metaclass=jsii.JSIIMeta,
    jsii_type="zap-cdk.SessionManagementParametersParameters",
):
    '''Represents the parameters for session management in the scanning process.

    :class: SessionManagementParametersParameters
    :implements: ISessionManagementParametersParameters *
    :property: {string} [scriptEngine] - Name of the script engine to use, only for 'script' session management.
    '''

    def __init__(
        self,
        options: typing.Optional[ISessionManagementParametersParameters] = None,
    ) -> None:
        '''Creates an instance of SessionManagementParametersParameters.

        :param options: - The options to initialize the session management parameters.

        :property: {string} [options.scriptEngine] - Name of the script engine to use, only for 'script' session management.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e94b1681bb2bdc1d7db7bceee2d0ed30dbe2b19327b2e45abd1557991c655cfe)
            check_type(argname="argument options", value=options, expected_type=type_hints["options"])
        jsii.create(self.__class__, self, [options])

    @builtins.property
    @jsii.member(jsii_name="script")
    def script(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "script"))

    @script.setter
    def script(self, value: typing.Optional[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d273e2582e07d2196080f8e12c8b4d79c8abe02d0912cb648a57bee4cc5b55d1)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "script", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="scriptEngine")
    def script_engine(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "scriptEngine"))

    @script_engine.setter
    def script_engine(self, value: typing.Optional[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__12665fa5b1f2e7f3260fa384731b424f47a27c1846ed40f812f4d99f810e14ce)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "scriptEngine", value) # pyright: ignore[reportArgumentType]


@jsii.implements(ISoap)
class Soap(metaclass=jsii.JSIIMeta, jsii_type="zap-cdk.Soap"):
    '''Class representing the SOAP service configuration.

    :class: Soap
    :implements: ISoap *
    :property: {string} [wsdlUrl] - URL pointing to the WSDL, default: null.

    Example::

        const soapConfig = new Soap({
          wsdlFile: 'service.wsdl',
          wsdlUrl: 'https://example.com/service?wsdl'
        });
    '''

    def __init__(self, options: ISoap) -> None:
        '''Creates an instance of Soap.

        :param options: - The options to initialize the SOAP configuration.

        :property: {string} [options.wsdlUrl] - URL pointing to the WSDL, default: null.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b33b110d3eb11300ec66d8b62b6e41993825eb12a3865137793eacfa5ad90129)
            check_type(argname="argument options", value=options, expected_type=type_hints["options"])
        jsii.create(self.__class__, self, [options])

    @builtins.property
    @jsii.member(jsii_name="wsdlFile")
    def wsdl_file(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "wsdlFile"))

    @wsdl_file.setter
    def wsdl_file(self, value: typing.Optional[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5b383cfbfb5883b5d0c0beb59c9bac2f0f807f8211b962f328bc7a170ad6d937)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wsdlFile", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="wsdlUrl")
    def wsdl_url(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "wsdlUrl"))

    @wsdl_url.setter
    def wsdl_url(self, value: typing.Optional[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__633b2721deab084ce34469d69d353eb71f0b6a194f1101ddc90cce089c480b81)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wsdlUrl", value) # pyright: ignore[reportArgumentType]


@jsii.implements(ISpider)
class Spider(metaclass=jsii.JSIIMeta, jsii_type="zap-cdk.Spider"):
    '''Class representing a spider configuration.

    :class: Spider
    :implements: ISpider *

    Example::

        const spiderParams = new SpiderParameters({
          context: 'MyContext',
          maxDuration: 10,
          parseComments: false
        });
        const spiderTest = new SpiderTest({
          statistic: 'urls',
          operator: '>=',
          value: 10,
          onFail: 'error'
        });
        const spider = new Spider(spiderParams, [spiderTest], true, false);
    '''

    def __init__(
        self,
        parameters: ISpiderParameters,
        tests: typing.Optional[typing.Sequence[ISpiderTest]] = None,
        enabled: typing.Optional[builtins.bool] = None,
        always_run: typing.Optional[builtins.bool] = None,
    ) -> None:
        '''Creates an instance of Spider.

        :param parameters: - The parameters for the spider configuration.
        :param tests: - List of tests to perform.
        :param enabled: - If set to false the job will not be run, default: true.
        :param always_run: - If set and the job is enabled then it will run even if the plan exits early, default: false.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3e0e85161b0d0dfde77bd5e0c78792625f522d463f7d52db49cf180290f94da1)
            check_type(argname="argument parameters", value=parameters, expected_type=type_hints["parameters"])
            check_type(argname="argument tests", value=tests, expected_type=type_hints["tests"])
            check_type(argname="argument enabled", value=enabled, expected_type=type_hints["enabled"])
            check_type(argname="argument always_run", value=always_run, expected_type=type_hints["always_run"])
        jsii.create(self.__class__, self, [parameters, tests, enabled, always_run])

    @builtins.property
    @jsii.member(jsii_name="parameters")
    def parameters(self) -> ISpiderParameters:
        return typing.cast(ISpiderParameters, jsii.get(self, "parameters"))

    @parameters.setter
    def parameters(self, value: ISpiderParameters) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0a61235ac80db5bedc24e18c1b8eb0ee187d10abce8a3757f620166d7c025481)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "parameters", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="type")
    def type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "type"))

    @type.setter
    def type(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4324b73ebb7665ab6bbfb839407285976a8cd3627b444d0ca378cc564782a102)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "type", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="alwaysRun")
    def always_run(self) -> typing.Optional[builtins.bool]:
        return typing.cast(typing.Optional[builtins.bool], jsii.get(self, "alwaysRun"))

    @always_run.setter
    def always_run(self, value: typing.Optional[builtins.bool]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__cb59fb2d16adb2ffff72b6822a238d4aa67c426b849ecd7e58054593b1187fba)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "alwaysRun", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="enabled")
    def enabled(self) -> typing.Optional[builtins.bool]:
        return typing.cast(typing.Optional[builtins.bool], jsii.get(self, "enabled"))

    @enabled.setter
    def enabled(self, value: typing.Optional[builtins.bool]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c2f9d7414697e1125d72d483a96a0890e2b2252288924489418fe846a0e1513d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "enabled", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="tests")
    def tests(self) -> typing.Optional[typing.List[ISpiderTest]]:
        return typing.cast(typing.Optional[typing.List[ISpiderTest]], jsii.get(self, "tests"))

    @tests.setter
    def tests(self, value: typing.Optional[typing.List[ISpiderTest]]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0f9dde29c84c2346b8648f6e9f95008056249873a4a4f900aea1ccd8263e5298)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "tests", value) # pyright: ignore[reportArgumentType]


@jsii.implements(ISpiderAjax)
class SpiderAjax(metaclass=jsii.JSIIMeta, jsii_type="zap-cdk.SpiderAjax"):
    '''Class representing the configuration for an AJAX spider.

    :class: SpiderAjax
    :implements: ISpiderAjax *
    :property: {IAjaxTest[]} [tests] - List of tests to perform, default: empty list.

    Example::

        const spiderAjax = new SpiderAjax({
          context: 'MyContext',
          url: 'https://example.com',
          maxDuration: 10,
          inScopeOnly: true,
          elements: ['a', 'button'],
          excludedElements: [
            new ExcludedElement({
              description: 'Exclude login button',
              element: 'button',
              text: 'Login'
            })
          ],
          tests: [
            new AjaxTest({
              name: 'Check AJAX requests',
              type: 'stats',
              statistic: 'ajax.requests',
              operator: '>',
              value: 10,
              onFail: 'warn'
            })
          ]
        });
    '''

    def __init__(self, options: ISpiderAjax) -> None:
        '''Creates an instance of SpiderAjax.

        :param options: - The options to initialize the AJAX spider configuration.

        :property: {IAjaxTest[]} [options.tests] - List of tests to perform, default: empty list.

        Example::

            const spiderAjax = new SpiderAjax({
              context: 'MyContext',
              url: 'https://example.com',
              maxDuration: 10,
              inScopeOnly: true,
              elements: ['a', 'button'],
              excludedElements: [
                new ExcludedElement({
                  description: 'Exclude login button',
                  element: 'button',
                  text: 'Login'
                })
              ],
              tests: [
                new AjaxTest({
                  name: 'Check AJAX requests',
                  type: 'stats',
                  statistic: 'ajax.requests',
                  operator: '>',
                  value: 10,
                  onFail: 'warn'
                })
              ]
            });
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6506c074278e8773057878ca0fc589cbc6136d12acec5c6f0f44373a26d94713)
            check_type(argname="argument options", value=options, expected_type=type_hints["options"])
        jsii.create(self.__class__, self, [options])

    @builtins.property
    @jsii.member(jsii_name="browserId")
    def browser_id(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "browserId"))

    @browser_id.setter
    def browser_id(self, value: typing.Optional[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__90735e36532ec21e5bdc711740b4606a93a3f4a796d18b6e5674fae41ca4642a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "browserId", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="clickDefaultElems")
    def click_default_elems(self) -> typing.Optional[builtins.bool]:
        return typing.cast(typing.Optional[builtins.bool], jsii.get(self, "clickDefaultElems"))

    @click_default_elems.setter
    def click_default_elems(self, value: typing.Optional[builtins.bool]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__cd4997eb4e569ccbbf93f8da7c4a2763f010248ef2f08588c7ff8852cc5d1d11)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "clickDefaultElems", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="clickElemsOnce")
    def click_elems_once(self) -> typing.Optional[builtins.bool]:
        return typing.cast(typing.Optional[builtins.bool], jsii.get(self, "clickElemsOnce"))

    @click_elems_once.setter
    def click_elems_once(self, value: typing.Optional[builtins.bool]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f950d60e70b9ceeb26a4843ab8172d3e6bfd9396de8f7d393de1f8903799d640)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "clickElemsOnce", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="context")
    def context(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "context"))

    @context.setter
    def context(self, value: typing.Optional[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__05f8179260f82e5327f9bbe38f0eca7a45a60da3e18dd1cd7311588b9ce1529c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "context", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="elements")
    def elements(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "elements"))

    @elements.setter
    def elements(self, value: typing.Optional[typing.List[builtins.str]]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8b1ff7dcc6cee09402188a4ac4edd1855cf07482c91500176eae42f8f458083e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "elements", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="eventWait")
    def event_wait(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "eventWait"))

    @event_wait.setter
    def event_wait(self, value: typing.Optional[jsii.Number]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__01303ea5ef448901c27f7310b2f0b90431f8c7c172c741cd795b80e9741cf24d)
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
            type_hints = typing.get_type_hints(_typecheckingstub__83b49a7296b832e33376dde67d4ee363ac0614ebc3d354e8e853d6e11a02abe7)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "excludedElements", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="inScopeOnly")
    def in_scope_only(self) -> typing.Optional[builtins.bool]:
        return typing.cast(typing.Optional[builtins.bool], jsii.get(self, "inScopeOnly"))

    @in_scope_only.setter
    def in_scope_only(self, value: typing.Optional[builtins.bool]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b0a211170a67af76f770912bdbebdd9417ca9794f4975984046fc56de074ee6d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "inScopeOnly", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="maxCrawlDepth")
    def max_crawl_depth(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "maxCrawlDepth"))

    @max_crawl_depth.setter
    def max_crawl_depth(self, value: typing.Optional[jsii.Number]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ca665436d4dcc4edeb8c89376b9a3d94a798641eeefb3fd974728c68af15e4d0)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "maxCrawlDepth", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="maxCrawlStates")
    def max_crawl_states(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "maxCrawlStates"))

    @max_crawl_states.setter
    def max_crawl_states(self, value: typing.Optional[jsii.Number]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__795b40d0b3524a50cda3e4bfc2c4a9e09c7d290355687339874410c807219250)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "maxCrawlStates", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="maxDuration")
    def max_duration(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "maxDuration"))

    @max_duration.setter
    def max_duration(self, value: typing.Optional[jsii.Number]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a49f64a0f6db8382bc1f849ac8341a200a29791705d9157bd73531804155b94a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "maxDuration", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="numberOfBrowsers")
    def number_of_browsers(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "numberOfBrowsers"))

    @number_of_browsers.setter
    def number_of_browsers(self, value: typing.Optional[jsii.Number]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__30317e766ee20c3a87eb674d7078eb979ca9a7096939cc76d8b28dbe7b901a01)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "numberOfBrowsers", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="randomInputs")
    def random_inputs(self) -> typing.Optional[builtins.bool]:
        return typing.cast(typing.Optional[builtins.bool], jsii.get(self, "randomInputs"))

    @random_inputs.setter
    def random_inputs(self, value: typing.Optional[builtins.bool]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ac2bc68565b46bdbc86ed786150dc9cc71c31ef5774dda3e90eef94e9785e742)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "randomInputs", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="reloadWait")
    def reload_wait(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "reloadWait"))

    @reload_wait.setter
    def reload_wait(self, value: typing.Optional[jsii.Number]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__74ddb8c7350876e6a5eedc3a3b03244b010a244092d6c1dde00a16fb6385969e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "reloadWait", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="runOnlyIfModern")
    def run_only_if_modern(self) -> typing.Optional[builtins.bool]:
        return typing.cast(typing.Optional[builtins.bool], jsii.get(self, "runOnlyIfModern"))

    @run_only_if_modern.setter
    def run_only_if_modern(self, value: typing.Optional[builtins.bool]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f2fcf65e9963939456089d8c6007dfcc5af10d3680d107f1be30534a0105764f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "runOnlyIfModern", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="scopeCheck")
    def scope_check(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "scopeCheck"))

    @scope_check.setter
    def scope_check(self, value: typing.Optional[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__852ea5dab0f0e8e8e9b5e08fc330a9579e285c9d2335d8db5dc501d21dd07476)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "scopeCheck", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="tests")
    def tests(self) -> typing.Optional[typing.List[IAjaxTest]]:
        return typing.cast(typing.Optional[typing.List[IAjaxTest]], jsii.get(self, "tests"))

    @tests.setter
    def tests(self, value: typing.Optional[typing.List[IAjaxTest]]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3edc6d479fa80659ef9c68fb7b7ef48e62661290058671a36bfef64d21e5b412)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "tests", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="url")
    def url(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "url"))

    @url.setter
    def url(self, value: typing.Optional[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5a99d4fb49af8269eabcd126a9e1d57fd154ce65d9128b3c05a81b4df3690674)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "url", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="user")
    def user(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "user"))

    @user.setter
    def user(self, value: typing.Optional[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3041e7e253db69b234cf9e6d55c48bd41e28ba56b00db1089d642c283968853f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "user", value) # pyright: ignore[reportArgumentType]


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


@jsii.implements(ISpiderParameters)
class SpiderParameters(metaclass=jsii.JSIIMeta, jsii_type="zap-cdk.SpiderParameters"):
    def __init__(self, options: ISpiderParameters) -> None:
        '''Creates an instance of SpiderParameters.

        :param options: - The options to initialize the spider parameters.

        :property: {string} [options.userAgent] - The user agent to use in requests, default: '' (use the default ZAP one).
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4391b68e7bb86217de43b834689fd90d8aad7f8f1287b3a539ca6cc736adfb4e)
            check_type(argname="argument options", value=options, expected_type=type_hints["options"])
        jsii.create(self.__class__, self, [options])

    @builtins.property
    @jsii.member(jsii_name="acceptCookies")
    def accept_cookies(self) -> typing.Optional[builtins.bool]:
        return typing.cast(typing.Optional[builtins.bool], jsii.get(self, "acceptCookies"))

    @accept_cookies.setter
    def accept_cookies(self, value: typing.Optional[builtins.bool]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0fd869a9a5038cc18e3f8a2fe1e3a70fc2d8870ffc7f3a4ef6eb6619eb9cade2)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "acceptCookies", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="context")
    def context(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "context"))

    @context.setter
    def context(self, value: typing.Optional[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__dae6c8142a31d205a9ca4d09ec5ed0019e739a42b14874ea18094338429fc7d6)
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
            type_hints = typing.get_type_hints(_typecheckingstub__85073f4761fc0e93f0192aa82a6b11a417186633a915cc53f95556a8c558d205)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "handleODataParametersVisited", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="handleParameters")
    def handle_parameters(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "handleParameters"))

    @handle_parameters.setter
    def handle_parameters(self, value: typing.Optional[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__41a43f827f0b9aea3a11c2599bed7c0e95f276aac7d3c2ba2223e39b548cada3)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "handleParameters", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="logoutAvoidance")
    def logout_avoidance(self) -> typing.Optional[builtins.bool]:
        return typing.cast(typing.Optional[builtins.bool], jsii.get(self, "logoutAvoidance"))

    @logout_avoidance.setter
    def logout_avoidance(self, value: typing.Optional[builtins.bool]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__25367df58f86766c418a1d835a6068d943082c190ff36e386c9abbc34a406e7c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "logoutAvoidance", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="maxChildren")
    def max_children(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "maxChildren"))

    @max_children.setter
    def max_children(self, value: typing.Optional[jsii.Number]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e771cf3bc25e06f7a906b0167a820e7169888eb714d416649f33c993b3b8fba2)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "maxChildren", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="maxDepth")
    def max_depth(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "maxDepth"))

    @max_depth.setter
    def max_depth(self, value: typing.Optional[jsii.Number]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c5aed289cddd7d3601a0d183370eb86131b1ab5285ea5b0478750d5e68450292)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "maxDepth", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="maxDuration")
    def max_duration(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "maxDuration"))

    @max_duration.setter
    def max_duration(self, value: typing.Optional[jsii.Number]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ca47d0002343427f3d99ed8c5c2f2432456bb699372325bf6bd01cf057c2a032)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "maxDuration", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="maxParseSizeBytes")
    def max_parse_size_bytes(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "maxParseSizeBytes"))

    @max_parse_size_bytes.setter
    def max_parse_size_bytes(self, value: typing.Optional[jsii.Number]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d7b92e118b2870bfe05cfa936f9545a692c09cf08f9f67cbd800fe3e319c0516)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "maxParseSizeBytes", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="parseComments")
    def parse_comments(self) -> typing.Optional[builtins.bool]:
        return typing.cast(typing.Optional[builtins.bool], jsii.get(self, "parseComments"))

    @parse_comments.setter
    def parse_comments(self, value: typing.Optional[builtins.bool]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9d8b7eabee808ad29eff99f5b5244ce159d59c9533c6ea46d64d7fb2b874da74)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "parseComments", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="parseDsStore")
    def parse_ds_store(self) -> typing.Optional[builtins.bool]:
        return typing.cast(typing.Optional[builtins.bool], jsii.get(self, "parseDsStore"))

    @parse_ds_store.setter
    def parse_ds_store(self, value: typing.Optional[builtins.bool]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1432d4771f67269f498f0a7ced00eac2d7d1c7a55b24bdcea6d9724ff3e734a6)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "parseDsStore", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="parseGit")
    def parse_git(self) -> typing.Optional[builtins.bool]:
        return typing.cast(typing.Optional[builtins.bool], jsii.get(self, "parseGit"))

    @parse_git.setter
    def parse_git(self, value: typing.Optional[builtins.bool]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__60c8a95732b077642e216e00a18242a7be38b2cc7c14d28766cd03425e341d0b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "parseGit", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="parseRobotsTxt")
    def parse_robots_txt(self) -> typing.Optional[builtins.bool]:
        return typing.cast(typing.Optional[builtins.bool], jsii.get(self, "parseRobotsTxt"))

    @parse_robots_txt.setter
    def parse_robots_txt(self, value: typing.Optional[builtins.bool]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c6efb3e309ff91b0fbbdcee93097f3bcee117c640ff2f67a1ac32a5ac444142c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "parseRobotsTxt", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="parseSitemapXml")
    def parse_sitemap_xml(self) -> typing.Optional[builtins.bool]:
        return typing.cast(typing.Optional[builtins.bool], jsii.get(self, "parseSitemapXml"))

    @parse_sitemap_xml.setter
    def parse_sitemap_xml(self, value: typing.Optional[builtins.bool]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4537342edf36ad481b5204f98a8316d599f14056a9802b11c16a17dc5f96ea15)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "parseSitemapXml", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="parseSVNEntries")
    def parse_svn_entries(self) -> typing.Optional[builtins.bool]:
        return typing.cast(typing.Optional[builtins.bool], jsii.get(self, "parseSVNEntries"))

    @parse_svn_entries.setter
    def parse_svn_entries(self, value: typing.Optional[builtins.bool]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4f296fbd7e9fafa7f9a0cb3c7297e4b40c30face29664cb1e2f4065f7e3cf571)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "parseSVNEntries", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="postForm")
    def post_form(self) -> typing.Optional[builtins.bool]:
        return typing.cast(typing.Optional[builtins.bool], jsii.get(self, "postForm"))

    @post_form.setter
    def post_form(self, value: typing.Optional[builtins.bool]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__976d99258dc9506fa0c0519ba120f1a25263b27082bc40eb4196d58cc6066b09)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "postForm", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="processForm")
    def process_form(self) -> typing.Optional[builtins.bool]:
        return typing.cast(typing.Optional[builtins.bool], jsii.get(self, "processForm"))

    @process_form.setter
    def process_form(self, value: typing.Optional[builtins.bool]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__86d755d7662363ba7e447aae709a5c84c7ec9c1eadbb1de97d4d233d30eb32d7)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "processForm", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="sendRefererHeader")
    def send_referer_header(self) -> typing.Optional[builtins.bool]:
        return typing.cast(typing.Optional[builtins.bool], jsii.get(self, "sendRefererHeader"))

    @send_referer_header.setter
    def send_referer_header(self, value: typing.Optional[builtins.bool]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__17d507b62359ef4c23a7cbd07fa8493e744ee1b944cb80dd93c6ee5a000d1078)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "sendRefererHeader", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="threadCount")
    def thread_count(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "threadCount"))

    @thread_count.setter
    def thread_count(self, value: typing.Optional[jsii.Number]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6c3816a71032eada18d0a8b5992af324e72e030e1f99aff7dfc4a18deab66eb0)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "threadCount", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="url")
    def url(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "url"))

    @url.setter
    def url(self, value: typing.Optional[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1a652c3000c21192999c0364fe03fe1b7ed98117703be9d4b3a2a84905c17fd2)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "url", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="user")
    def user(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "user"))

    @user.setter
    def user(self, value: typing.Optional[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ffbf9b64500b4dbcff62cc4d02eaef2b9e8d9b7775e69a10795d677e628e4c12)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "user", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="userAgent")
    def user_agent(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "userAgent"))

    @user_agent.setter
    def user_agent(self, value: typing.Optional[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__fa1ac54b486b899737c1b979292cbbc115ba35f27220038c8d39895e4fd07a05)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "userAgent", value) # pyright: ignore[reportArgumentType]


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


@jsii.implements(ISpiderTest)
class SpiderTest(metaclass=jsii.JSIIMeta, jsii_type="zap-cdk.SpiderTest"):
    '''Class representing a test configuration for the spider.

    :class: SpiderTest
    :implements: ISpiderTest *

    Example::

        const spiderTest = new SpiderTest({
          statistic: 'urls',
          operator: '>=',
          value: 10,
          onFail: 'error'
        });
    '''

    def __init__(self, options: ISpiderTest) -> None:
        '''Creates an instance of SpiderTest.

        :param options: - The options to initialize the spider test.

        :property: {'warn' | 'error' | 'info'} options.onFail - One of 'warn', 'error', 'info', mandatory.

        Example::

            const spiderTest = new SpiderTest({
              statistic: 'urls',
              operator: '>=',
              value: 10,
              onFail: 'error'
            });
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3a1f2eae44471c9abdd1124b9b6806f6c2b78e3db066b041392e80ce33870cf8)
            check_type(argname="argument options", value=options, expected_type=type_hints["options"])
        jsii.create(self.__class__, self, [options])

    @builtins.property
    @jsii.member(jsii_name="onFail")
    def on_fail(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "onFail"))

    @on_fail.setter
    def on_fail(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d9586b08db0cb2f8f3a7e184f0fe4d1a033f8f5fdb673856574c38759783d39b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "onFail", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="operator")
    def operator(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "operator"))

    @operator.setter
    def operator(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__061ce35b2194e36d968c55160fe284d7e83ee3c0a0c505dd61f2a012f11a220c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "operator", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="statistic")
    def statistic(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "statistic"))

    @statistic.setter
    def statistic(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f5510386857c87c1e37a24c8962737682ea94b966d600dbfaae2d3f07ecb958d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "statistic", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="type")
    def type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "type"))

    @type.setter
    def type(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7186f4c6d434c2ed02979b2af703a783ece6f332013f8214f8abb10969a5dbb0)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "type", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="value")
    def value(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "value"))

    @value.setter
    def value(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3cafb9afed7e19f9ce009b9b0130eefad7cd030469430d327ecf904181205990)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "value", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "name"))

    @name.setter
    def name(self, value: typing.Optional[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e987bbcbfa5d38f9d8fa94e5aaada6b60e9aa59545b03027368f7a5bd0dbcf1c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "name", value) # pyright: ignore[reportArgumentType]


@jsii.implements(IStatisticsTest)
class StatisticsTest(metaclass=jsii.JSIIMeta, jsii_type="zap-cdk.StatisticsTest"):
    def __init__(self, options: IStatisticsTest) -> None:
        '''Creates an instance of StatisticsTest.

        :param options: - The configuration options for the statistics test.

        :property: {OnFailType} options.onFail - Action to take on failure, mandatory.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e589527410d2357500bfcbb7f277942e8f5f02222bfadf865c5c4001ed511d53)
            check_type(argname="argument options", value=options, expected_type=type_hints["options"])
        jsii.create(self.__class__, self, [options])

    @builtins.property
    @jsii.member(jsii_name="onFail")
    def on_fail(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "onFail"))

    @on_fail.setter
    def on_fail(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__58958cf7c96b758cdd2f74cec7ce583801c7f816709979b47616a3f299c0e9d7)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "onFail", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="operator")
    def operator(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "operator"))

    @operator.setter
    def operator(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__278f706e3198da5e4775f967987fab712de1a7b3b21c37f798b9b4d42ddd34dc)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "operator", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="statistic")
    def statistic(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "statistic"))

    @statistic.setter
    def statistic(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__87ef38e699436b7b524c614e60c018d63bd7dee2dee26072f698b922fdb4c709)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "statistic", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="type")
    def type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "type"))

    @type.setter
    def type(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4507281eb4f27e710a2d232473e255e1b001ed8473dd7adf065586073f4dbc01)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "type", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="value")
    def value(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "value"))

    @value.setter
    def value(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__49bde5877a0212dff5bcaf581230c46ed026f584ba5c38f9f3b5ee2fb1c98f11)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "value", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "name"))

    @name.setter
    def name(self, value: typing.Optional[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7bf447a6c70fd114b5cbd7113e33f78b640e209ab31e293b91d3e80191c65797)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "name", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="site")
    def site(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "site"))

    @site.setter
    def site(self, value: typing.Optional[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ad028245822ce269ceb3dc78639e47a019760d4bc69d15706b41685ac58b64aa)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "site", value) # pyright: ignore[reportArgumentType]


@jsii.implements(ITechnology)
class Technology(metaclass=jsii.JSIIMeta, jsii_type="zap-cdk.Technology"):
    '''Represents the technology details for the scanning context.

    :class: Technology
    :implements: ITechnology *
    :property: {string[]} [include] - List of tech to include.
    '''

    def __init__(self, options: ITechnology) -> None:
        '''Creates an instance of Technology.

        :param options: - The options to initialize the technology details.

        :property: {string[]} [options.include] - List of tech to include.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5494039db6148e623ad24e6adc6169ef08d2797b2a3acac346c78c6ec27ad689)
            check_type(argname="argument options", value=options, expected_type=type_hints["options"])
        jsii.create(self.__class__, self, [options])

    @builtins.property
    @jsii.member(jsii_name="exclude")
    def exclude(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "exclude"))

    @exclude.setter
    def exclude(self, value: typing.Optional[typing.List[builtins.str]]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4ebebc66d4836f0ee5854f9245c982527ea77f1a08c362219ffd75549a2e2cd4)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "exclude", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="include")
    def include(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "include"))

    @include.setter
    def include(self, value: typing.Optional[typing.List[builtins.str]]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__bfa64ef4dac0b731f07ffecc3a6c3da24adb146bcd2d3102d34c657dd676adfd)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "include", value) # pyright: ignore[reportArgumentType]


@jsii.implements(ITotpConfig)
class TotpConfig(metaclass=jsii.JSIIMeta, jsii_type="zap-cdk.TotpConfig"):
    '''Represents the TOTP (Time-based One-Time Password) configuration for a user.

    :class: TotpConfig
    :implements: ITotpConfig *
    :property: {string} [algorithm] - Algorithm, default: SHA1.
    '''

    def __init__(self, options: ITotpConfig) -> None:
        '''Creates an instance of TotpConfig.

        :param options: - The options to initialize the TOTP configuration.

        :property: {string} [options.algorithm] - Algorithm, default: SHA1.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e6700e17530c3abecbcdaa6641d4d979f1ce7ce263fb101a9e569de9ffc0df91)
            check_type(argname="argument options", value=options, expected_type=type_hints["options"])
        jsii.create(self.__class__, self, [options])

    @builtins.property
    @jsii.member(jsii_name="secret")
    def secret(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "secret"))

    @secret.setter
    def secret(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1d74fd06e313fc89902f4bc4189f3e43d0b03894a5d6e8a5c32b0bf8103efa35)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "secret", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="algorithm")
    def algorithm(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "algorithm"))

    @algorithm.setter
    def algorithm(self, value: typing.Optional[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7e7d7e7367b960774a9a5aeb50d7517e9042bd9a21f7bf9407dea944fdde209e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "algorithm", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="digits")
    def digits(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "digits"))

    @digits.setter
    def digits(self, value: typing.Optional[jsii.Number]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c657d3d1a403c3a1eb438a32aeca1e3eb3b7bfa208a124b8fcc43c33631cda59)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "digits", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="period")
    def period(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "period"))

    @period.setter
    def period(self, value: typing.Optional[jsii.Number]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__96ef8c9ea378c63c2483450d231d56d59b1aa01c4f7f6c66d910c173bb14351c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "period", value) # pyright: ignore[reportArgumentType]


@jsii.implements(IUrlQueryStringAndDataDrivenNodes)
class UrlQueryStringAndDataDrivenNodes(
    metaclass=jsii.JSIIMeta,
    jsii_type="zap-cdk.UrlQueryStringAndDataDrivenNodes",
):
    '''Class representing the configuration options for scanning URL query strings and Data Driven Nodes (DDNs).

    :implements: IUrlQueryStringAndDataDrivenNodes *
    :property: {boolean} [odata] - If OData query filters should be scanned. Default: true

    Example::

        const config = new UrlQueryStringAndDataDrivenNodes({ enabled: true, addParam: false, odata: true });
        console.log(config.enabled); // true
    '''

    def __init__(
        self,
        options: typing.Optional[IUrlQueryStringAndDataDrivenNodes] = None,
    ) -> None:
        '''Creates an instance of UrlQueryStringAndDataDrivenNodes.

        :param options: - The configuration options.

        :memberof: UrlQueryStringAndDataDrivenNodes

        Example::

            const config = new UrlQueryStringAndDataDrivenNodes({ enabled: true, addParam: false, odata: true });
            console.log(config.enabled); // true
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__042343489372ee0fd16a66fd50d885080b6de2b9cbc402dd061e7c609b70114e)
            check_type(argname="argument options", value=options, expected_type=type_hints["options"])
        jsii.create(self.__class__, self, [options])

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
            type_hints = typing.get_type_hints(_typecheckingstub__18be073c4e552a81e292ace44da8bc644d8140ce1719ca95a8ade4efb8faecfe)
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
            type_hints = typing.get_type_hints(_typecheckingstub__ecdf0e877818988de2a5128e8596ee8cc5536ce64ee3105527780730d23e32ef)
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
            type_hints = typing.get_type_hints(_typecheckingstub__bab6d3429fbd401c852f614b582393df397bd0147a5652e03456a34fbe3ad9f7)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "odata", value) # pyright: ignore[reportArgumentType]


@jsii.implements(IUrlTest)
class UrlTest(metaclass=jsii.JSIIMeta, jsii_type="zap-cdk.UrlTest"):
    '''Class representing a URL test.

    :class: UrlTest
    :implements: IUrlTest *
    :property: {OnFailType} onFail - Action to take on failure, mandatory.

    Example::

        const urlTest = new UrlTest({
          name: 'test one',
          url: 'http://www.example.com/path',
          operator: 'and',
          requestHeaderRegex: 'some-regex',
          requestBodyRegex: 'some-regex',
          responseHeaderRegex: 'some-regex',
          responseBodyRegex: 'some-regex',
          onFail: 'error',
        });
    '''

    def __init__(self, options: IUrlTest) -> None:
        '''Creates an instance of UrlTest.

        :param options: - The configuration options for the URL test.

        :property: {OnFailType} options.onFail - Action to take on failure, mandatory.

        Example::

            const urlTest = new UrlTest({
              name: 'test one',
              url: 'http://www.example.com/path',
              operator: 'and',
              requestHeaderRegex: 'some-regex',
              requestBodyRegex: 'some-regex',
              responseHeaderRegex: 'some-regex',
              responseBodyRegex: 'some-regex',
              onFail: 'error',
            });
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c26cf331e9db56a247e2d822a8e1cdb74dfee18125ecbe885ef6b0e0c0b31e50)
            check_type(argname="argument options", value=options, expected_type=type_hints["options"])
        jsii.create(self.__class__, self, [options])

    @builtins.property
    @jsii.member(jsii_name="onFail")
    def on_fail(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "onFail"))

    @on_fail.setter
    def on_fail(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__891a1056d9000fd5477a227d9e099b4f2773b5f4de7c19e01a344247a7fb7b14)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "onFail", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="operator")
    def operator(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "operator"))

    @operator.setter
    def operator(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c1269ccde197633f1a58095008d92acab8c4caa3064f1bbf1ba981711bde44fd)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "operator", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="type")
    def type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "type"))

    @type.setter
    def type(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__530ccae163083c6ffac50351f23a8a1888f1addd8d7d0029793a12e74e54caa8)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "type", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="url")
    def url(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "url"))

    @url.setter
    def url(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3c66e3d7f0c3d28465d757996e8daed3878cdc216c58225d620d72f39bcf105e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "url", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "name"))

    @name.setter
    def name(self, value: typing.Optional[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a1b01cb76aedacc62fdff562481308c183a867343e9db739e41a6be34c915a35)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "name", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="requestBodyRegex")
    def request_body_regex(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "requestBodyRegex"))

    @request_body_regex.setter
    def request_body_regex(self, value: typing.Optional[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b97ff50575922661f23465f4090c5154bb1bff373df806f0697a64cd132c1aec)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "requestBodyRegex", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="requestHeaderRegex")
    def request_header_regex(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "requestHeaderRegex"))

    @request_header_regex.setter
    def request_header_regex(self, value: typing.Optional[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b323cad760e16dd2cef6d8ed41bb6bf97115eb58264f3c66d951f8ff9c64c2b0)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "requestHeaderRegex", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="responseBodyRegex")
    def response_body_regex(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "responseBodyRegex"))

    @response_body_regex.setter
    def response_body_regex(self, value: typing.Optional[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4463f02bfb65887a0d6e5282abfd67450bc93c6e07bb328ab734c34956d49c3d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "responseBodyRegex", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="responseHeaderRegex")
    def response_header_regex(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "responseHeaderRegex"))

    @response_header_regex.setter
    def response_header_regex(self, value: typing.Optional[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ab198d371591181d1c6ea4ba65601ec2f71f9eeac2d8a8b64aedb7f51a140e55)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "responseHeaderRegex", value) # pyright: ignore[reportArgumentType]


@jsii.implements(IUserCredentials)
class UserCredentials(metaclass=jsii.JSIIMeta, jsii_type="zap-cdk.UserCredentials"):
    '''Represents the credentials for a user.

    :class: UserCredentials
    :implements: IUserCredentials *
    :property: {ITotpConfig} [totp] - Optional TOTP configuration.
    '''

    def __init__(self, options: IUserCredentials) -> None:
        '''Creates an instance of UserCredentials.

        :param options: - The options to initialize the user credentials.

        :property: {ITotpConfig} [options.totp] - Optional TOTP configuration.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0bae0be71d8af1cc4a753a149c58079a33d6db14df7e51d5a6ef5ac6d6d70d7d)
            check_type(argname="argument options", value=options, expected_type=type_hints["options"])
        jsii.create(self.__class__, self, [options])

    @builtins.property
    @jsii.member(jsii_name="password")
    def password(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "password"))

    @password.setter
    def password(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5cbd0c7670a7374e8f835ecedeaab78244e883a15293b439945da2b93439ab77)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "password", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="username")
    def username(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "username"))

    @username.setter
    def username(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2068ffb83ce0004dc765e7f18a21ee90aaedd8208b18d346add2d3085d4596e1)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "username", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="totp")
    def totp(self) -> typing.Optional[ITotpConfig]:
        return typing.cast(typing.Optional[ITotpConfig], jsii.get(self, "totp"))

    @totp.setter
    def totp(self, value: typing.Optional[ITotpConfig]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0c04ddadb5f51c764fd86d16dc70d039e8b5f4a57f778dfcb8b79526aba843ed)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "totp", value) # pyright: ignore[reportArgumentType]


@jsii.implements(IZap)
class Zap(metaclass=jsii.JSIIMeta, jsii_type="zap-cdk.Zap"):
    '''Class representing the ZAP configuration.

    :class: Zap
    :implements: IZap *

    Example::

        const zapConfig = new Zap({
          env: new Environment({ /* environment config options *\/ }),
          jobs: [
            new Job({ /* job config options *\/ }),
            new Job({ /* another job config options *\/ })
          ]
        });
    '''

    def __init__(self, options: IZap) -> None:
        '''Creates an instance of Zap.

        :param options: - The ZAP configuration options.

        :property: {IJob[]} options.jobs - The list of jobs to be executed.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e8988d1177722ca3b6f00f51e9031d89ab9f6cd69685393453bbed7e814b9aa8)
            check_type(argname="argument options", value=options, expected_type=type_hints["options"])
        jsii.create(self.__class__, self, [options])

    @builtins.property
    @jsii.member(jsii_name="env")
    def env(self) -> IEnvironment:
        return typing.cast(IEnvironment, jsii.get(self, "env"))

    @env.setter
    def env(self, value: IEnvironment) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f4d7049f9370e6aed7a28e6f59caaa91b8c20ec5f18bdc7d07c91fb09d25d810)
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
            type_hints = typing.get_type_hints(_typecheckingstub__6a77f47f4f857b419ed4729dbbe1186a06f8280e56830c7c6185168cd9931854)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "jobs", value) # pyright: ignore[reportArgumentType]


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


@jsii.implements(IActiveScan)
class ActiveScan(metaclass=jsii.JSIIMeta, jsii_type="zap-cdk.ActiveScan"):
    '''Class representing an active scan configuration.

    :implements: IActiveScan *
    :property: {boolean} [alwaysRun] - If set and the job is enabled, it will run even if the plan exits early, default: false.
    '''

    def __init__(self, options: IActiveScan) -> None:
        '''Creates an instance of ActiveScan.

        :param options: - The active scan configuration details.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e4d0720d8d86c42c59c0e1e3253e2918128a5cf003a2f3e5c0d2c44588d29d83)
            check_type(argname="argument options", value=options, expected_type=type_hints["options"])
        jsii.create(self.__class__, self, [options])

    @builtins.property
    @jsii.member(jsii_name="parameters")
    def parameters(self) -> IActiveScanParameters:
        return typing.cast(IActiveScanParameters, jsii.get(self, "parameters"))

    @parameters.setter
    def parameters(self, value: IActiveScanParameters) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__14fd47c6f7d3371930d23da4375ed97989c1839f55f24e1b7f78e096e41582e2)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "parameters", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="type")
    def type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "type"))

    @type.setter
    def type(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7d2c602860a79d8299eee78d01eebd781c7cc86cea4988791faa4ceca76566d3)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "type", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="alwaysRun")
    def always_run(self) -> typing.Optional[builtins.bool]:
        return typing.cast(typing.Optional[builtins.bool], jsii.get(self, "alwaysRun"))

    @always_run.setter
    def always_run(self, value: typing.Optional[builtins.bool]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2c68503f194092162b95ac79b1b5d0654ee1d632e393c209e92d72245a9e5b3e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "alwaysRun", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="enabled")
    def enabled(self) -> typing.Optional[builtins.bool]:
        return typing.cast(typing.Optional[builtins.bool], jsii.get(self, "enabled"))

    @enabled.setter
    def enabled(self, value: typing.Optional[builtins.bool]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__614f60eb367c0c2a239630d0c38ac7a0bded354b5e25fe58dce7f50648186a63)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "enabled", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="policyDefinition")
    def policy_definition(self) -> typing.Optional[IPolicyDefinition]:
        return typing.cast(typing.Optional[IPolicyDefinition], jsii.get(self, "policyDefinition"))

    @policy_definition.setter
    def policy_definition(self, value: typing.Optional[IPolicyDefinition]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9dc169b39f6653fea9b10bb336bb93678b0acb50e6336415febb266baa88edc7)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "policyDefinition", value) # pyright: ignore[reportArgumentType]


@jsii.implements(IActiveScanConfig)
class ActiveScanConfig(metaclass=jsii.JSIIMeta, jsii_type="zap-cdk.ActiveScanConfig"):
    '''Class representing the configuration for an active scan.

    :implements: IActiveScanConfig *
    :property: {boolean} [alwaysRun] - If set and the job is enabled, then it will run even if the plan exits early, default: false.

    Example::

        const activeScanConfig = new ActiveScanConfig({
          parameters: new ActiveScanConfigParameters(),
          excludePaths: ['^/api/health$', '^/static/.*$'],
          enabled: true,
          alwaysRun: false
        });
        console.log(activeScanConfig.type); // 'activeScan-config'
    '''

    def __init__(self, options: IActiveScanConfig) -> None:
        '''Creates an instance of ActiveScanConfig.

        :param options: - The configuration options for the active scan.

        :memberof: ActiveScanConfig

        Example::

            const activeScanConfig = new ActiveScanConfig({
              parameters: new ActiveScanConfigParameters(),
              excludePaths: ['^/api/health$', '^/static/.*$'],
              enabled: true,
              alwaysRun: false
            });
            console.log(activeScanConfig.type); // 'activeScan-config'
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ca23190d78d2919234c733f19bc05216a18406399e366571582fc581ddd3a04d)
            check_type(argname="argument options", value=options, expected_type=type_hints["options"])
        jsii.create(self.__class__, self, [options])

    @builtins.property
    @jsii.member(jsii_name="parameters")
    def parameters(self) -> IActiveScanConfigParameters:
        return typing.cast(IActiveScanConfigParameters, jsii.get(self, "parameters"))

    @parameters.setter
    def parameters(self, value: IActiveScanConfigParameters) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__aeb5adaf84febceae2fe2bc5119099b6f07430e1dbbe133eb441179ea458dc24)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "parameters", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="type")
    def type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "type"))

    @type.setter
    def type(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1c5a5d8977784df7424847063e18e470351b7d1dfdaa97f698325d15750f1c0a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "type", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="alwaysRun")
    def always_run(self) -> typing.Optional[builtins.bool]:
        return typing.cast(typing.Optional[builtins.bool], jsii.get(self, "alwaysRun"))

    @always_run.setter
    def always_run(self, value: typing.Optional[builtins.bool]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b1984e2cda7e3561d8bebf4d718f1df3f33b47779ed4d9474c6b40564caf5128)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "alwaysRun", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="enabled")
    def enabled(self) -> typing.Optional[builtins.bool]:
        return typing.cast(typing.Optional[builtins.bool], jsii.get(self, "enabled"))

    @enabled.setter
    def enabled(self, value: typing.Optional[builtins.bool]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b1908729c1443f0d204f0b57ad5113d421b2a431edb6e45012035f4f7fa74edb)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "enabled", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="excludePaths")
    def exclude_paths(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "excludePaths"))

    @exclude_paths.setter
    def exclude_paths(self, value: typing.Optional[typing.List[builtins.str]]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__412bb64daf3c0159397bf84993712b4d8e9aa0005303cb1a0b196e48e9a6e5b4)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "excludePaths", value) # pyright: ignore[reportArgumentType]


@jsii.implements(IActiveScanConfigParameters)
class ActiveScanConfigParameters(
    metaclass=jsii.JSIIMeta,
    jsii_type="zap-cdk.ActiveScanConfigParameters",
):
    '''Class representing the parameters for configuring an active scan.

    :implements: IActiveScanConfigParameters *
    :property: {IInputVectors} inputVectors - The input vectors used during the active scan.

    Example::

        const activeScanConfig = new ActiveScanConfigParameters({
          maxRuleDurationInMins: 0,
          maxScanDurationInMins: 0,
          maxAlertsPerRule: 0,
          defaultPolicy: 'Default Policy',
          handleAntiCSRFTokens: false,
          injectPluginIdInHeader: false,
          threadPerHost: 4,
          inputVectors: new InputVectors()
        });
        console.log(activeScanConfig.defaultPolicy); // 'Default Policy'
    '''

    def __init__(
        self,
        options: typing.Optional[IActiveScanConfigParameters] = None,
    ) -> None:
        '''Creates an instance of ActiveScanConfigParameters.

        :param options: - The configuration options for the active scan.

        :memberof: ActiveScanConfigParameters

        Example::

            const activeScanConfig = new ActiveScanConfigParameters({
              maxRuleDurationInMins: 0,
              maxScanDurationInMins: 0,
              maxAlertsPerRule: 0,
              defaultPolicy: 'Default Policy',
              handleAntiCSRFTokens: false,
              injectPluginIdInHeader: false,
              threadPerHost: 4,
              inputVectors: new InputVectors()
            });
            console.log(activeScanConfig.defaultPolicy); // 'Default Policy'
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ecafbad3fd2176b7a57e35033fa35f3b2017f81f963253c90de8f10524c1f7db)
            check_type(argname="argument options", value=options, expected_type=type_hints["options"])
        jsii.create(self.__class__, self, [options])

    @builtins.property
    @jsii.member(jsii_name="inputVectors")
    def input_vectors(self) -> IInputVectors:
        return typing.cast(IInputVectors, jsii.get(self, "inputVectors"))

    @input_vectors.setter
    def input_vectors(self, value: IInputVectors) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4d6b3b971d10a756119e0023ceb28d9b655089b11e47db67658c1436a207b21c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "inputVectors", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="defaultPolicy")
    def default_policy(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "defaultPolicy"))

    @default_policy.setter
    def default_policy(self, value: typing.Optional[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ea35170cf4215bbf83faf7bb216f92240d508e48ec6d133b0695738f4059990e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "defaultPolicy", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="handleAntiCSRFTokens")
    def handle_anti_csrf_tokens(self) -> typing.Optional[builtins.bool]:
        return typing.cast(typing.Optional[builtins.bool], jsii.get(self, "handleAntiCSRFTokens"))

    @handle_anti_csrf_tokens.setter
    def handle_anti_csrf_tokens(self, value: typing.Optional[builtins.bool]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__160db386ae533c04decec7f288fb1a386694ecd9227ae3cf1e0f550ad0312168)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "handleAntiCSRFTokens", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="injectPluginIdInHeader")
    def inject_plugin_id_in_header(self) -> typing.Optional[builtins.bool]:
        return typing.cast(typing.Optional[builtins.bool], jsii.get(self, "injectPluginIdInHeader"))

    @inject_plugin_id_in_header.setter
    def inject_plugin_id_in_header(self, value: typing.Optional[builtins.bool]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__00eca7528fd3f90a90c5d98399c4214db1fb0a5f4246344b5aeb50d9fbfe9b91)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "injectPluginIdInHeader", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="maxAlertsPerRule")
    def max_alerts_per_rule(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "maxAlertsPerRule"))

    @max_alerts_per_rule.setter
    def max_alerts_per_rule(self, value: typing.Optional[jsii.Number]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5a08c984fb96ab5780e33f9fe46ae51da68bd4f9eddd325c7efa508e0e18b1b3)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "maxAlertsPerRule", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="maxRuleDurationInMins")
    def max_rule_duration_in_mins(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "maxRuleDurationInMins"))

    @max_rule_duration_in_mins.setter
    def max_rule_duration_in_mins(self, value: typing.Optional[jsii.Number]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__57462400a5137f9a8bd8c897512b220e8c8a775a5709be647ad331484da08324)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "maxRuleDurationInMins", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="maxScanDurationInMins")
    def max_scan_duration_in_mins(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "maxScanDurationInMins"))

    @max_scan_duration_in_mins.setter
    def max_scan_duration_in_mins(self, value: typing.Optional[jsii.Number]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__64fe248bf70bd14398d898d7ac2f469be2116e8b0e3b9e069d8e7cc6d988b564)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "maxScanDurationInMins", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="threadPerHost")
    def thread_per_host(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "threadPerHost"))

    @thread_per_host.setter
    def thread_per_host(self, value: typing.Optional[jsii.Number]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c97831594f25a0ba0d3b7a332b320c00006c0204eb90d8b24432909123b98eae)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "threadPerHost", value) # pyright: ignore[reportArgumentType]


@jsii.implements(IActiveScanParameters)
class ActiveScanParameters(
    metaclass=jsii.JSIIMeta,
    jsii_type="zap-cdk.ActiveScanParameters",
):
    '''Class representing parameters for an active scan.

    :implements: IActiveScanParameters *
    :property: {ITest[]} [tests] - List of tests to perform.
    '''

    def __init__(self, options: typing.Optional[IActiveScanParameters] = None) -> None:
        '''Creates an instance of ActiveScanParameters.

        :param options: - The parameters for the active scan.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d39727b3e8ac31f020cd3342d1416dadc9e045a358440a26a764313431e8a0b0)
            check_type(argname="argument options", value=options, expected_type=type_hints["options"])
        jsii.create(self.__class__, self, [options])

    @builtins.property
    @jsii.member(jsii_name="addQueryParam")
    def add_query_param(self) -> typing.Optional[builtins.bool]:
        return typing.cast(typing.Optional[builtins.bool], jsii.get(self, "addQueryParam"))

    @add_query_param.setter
    def add_query_param(self, value: typing.Optional[builtins.bool]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__fe5eae05347518eda844f48f3125d5f2a835431d28d06348ed614c4fdcb69dd9)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "addQueryParam", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="context")
    def context(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "context"))

    @context.setter
    def context(self, value: typing.Optional[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__dff11e6128126cca346efa60642819902ddcd957df1082b95c33d14df28d591e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "context", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="defaultPolicy")
    def default_policy(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "defaultPolicy"))

    @default_policy.setter
    def default_policy(self, value: typing.Optional[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a01b2c61e6a4558dc6cea511736d1c7763795c5e02db842d7c5e68e0e8ea068b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "defaultPolicy", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="delayInMs")
    def delay_in_ms(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "delayInMs"))

    @delay_in_ms.setter
    def delay_in_ms(self, value: typing.Optional[jsii.Number]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__cd68262e93a5b3502d24f0429c0710d638dd7af80b162691770404dbecee7b0d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "delayInMs", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="handleAntiCSRFTokens")
    def handle_anti_csrf_tokens(self) -> typing.Optional[builtins.bool]:
        return typing.cast(typing.Optional[builtins.bool], jsii.get(self, "handleAntiCSRFTokens"))

    @handle_anti_csrf_tokens.setter
    def handle_anti_csrf_tokens(self, value: typing.Optional[builtins.bool]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__fa44794f6d7b2c85fba14dba4a745d154f81cf54c2e3018ef172e7d2896018ef)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "handleAntiCSRFTokens", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="injectPluginIdInHeader")
    def inject_plugin_id_in_header(self) -> typing.Optional[builtins.bool]:
        return typing.cast(typing.Optional[builtins.bool], jsii.get(self, "injectPluginIdInHeader"))

    @inject_plugin_id_in_header.setter
    def inject_plugin_id_in_header(self, value: typing.Optional[builtins.bool]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__92ba2f6b88abd8f77e9cc9d3c04228940df79ee9d889c4020cd992a097e5998c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "injectPluginIdInHeader", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="maxAlertsPerRule")
    def max_alerts_per_rule(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "maxAlertsPerRule"))

    @max_alerts_per_rule.setter
    def max_alerts_per_rule(self, value: typing.Optional[jsii.Number]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7843a26fe3b03bd28235b1ebc021309e24ee3901d80c0b569bef58d5ca20ae50)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "maxAlertsPerRule", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="maxRuleDurationInMins")
    def max_rule_duration_in_mins(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "maxRuleDurationInMins"))

    @max_rule_duration_in_mins.setter
    def max_rule_duration_in_mins(self, value: typing.Optional[jsii.Number]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__dc6b7df0214c0ec38aa3c55ca538716d217766ae7f6e7dd3d55057e6cd3ad89a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "maxRuleDurationInMins", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="maxScanDurationInMins")
    def max_scan_duration_in_mins(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "maxScanDurationInMins"))

    @max_scan_duration_in_mins.setter
    def max_scan_duration_in_mins(self, value: typing.Optional[jsii.Number]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__91f3bb0b2bf8ace80e0066f9984f181768eb0496465be138d26fe140798ed527)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "maxScanDurationInMins", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="policy")
    def policy(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "policy"))

    @policy.setter
    def policy(self, value: typing.Optional[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a8ebd573eb4b5ea885e8afedfd67f67e2a97b94e900cbb5f34229d70f2f91fcf)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "policy", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="scanHeadersAllRequests")
    def scan_headers_all_requests(self) -> typing.Optional[builtins.bool]:
        return typing.cast(typing.Optional[builtins.bool], jsii.get(self, "scanHeadersAllRequests"))

    @scan_headers_all_requests.setter
    def scan_headers_all_requests(self, value: typing.Optional[builtins.bool]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ff6815f4d66c724de6d394dbfed78abcb8b29680c85c3a49b27f902ced6223d1)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "scanHeadersAllRequests", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="tests")
    def tests(
        self,
    ) -> typing.Optional[typing.List[typing.Union[IAlertTest, IMonitorTest, IStatisticsTest, IUrlTest]]]:
        return typing.cast(typing.Optional[typing.List[typing.Union[IAlertTest, IMonitorTest, IStatisticsTest, IUrlTest]]], jsii.get(self, "tests"))

    @tests.setter
    def tests(
        self,
        value: typing.Optional[typing.List[typing.Union[IAlertTest, IMonitorTest, IStatisticsTest, IUrlTest]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__cc18abb2a154ad644ec55859205b4b60ef60bc3d4afcd433dd160ef97ee1ed7f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "tests", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="threadPerHost")
    def thread_per_host(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "threadPerHost"))

    @thread_per_host.setter
    def thread_per_host(self, value: typing.Optional[jsii.Number]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__aafdf0cb385f3824e2e2994f55af4e713d66827ac9e7d32ab46d6cefc10ea258)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "threadPerHost", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="url")
    def url(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "url"))

    @url.setter
    def url(self, value: typing.Optional[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__49cc78e5507a1a40c571b97e518bcbd1f435077f22fc2cd18d7dde324456b77a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "url", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="user")
    def user(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "user"))

    @user.setter
    def user(self, value: typing.Optional[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5ef8a49b103ceb6cca0cee614ef20f7539459cf23d3f311f4e0258d2631d9f78)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "user", value) # pyright: ignore[reportArgumentType]


@jsii.implements(IActiveScanPolicy)
class ActiveScanPolicy(metaclass=jsii.JSIIMeta, jsii_type="zap-cdk.ActiveScanPolicy"):
    '''Class representing an active scan policy configuration.

    :class: ActiveScanPolicy
    :implements: IActiveScanPolicy *
    :property: {boolean} [alwaysRun] - If set and the job is enabled then it will run even if the plan exits early, default: false.
    '''

    def __init__(self, options: IActiveScanPolicy) -> None:
        '''Creates an instance of ActiveScanPolicy.

        :param options: - The configuration options for the active scan policy.

        :property: {boolean} [options.alwaysRun] - If set and the job is enabled then it will run even if the plan exits early, default: false.
        :throws: {Error} If the parameters property is not provided.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a80af27aa5eea08ca6e95581160a422fd9a3709af156272a86c7409df7aa8740)
            check_type(argname="argument options", value=options, expected_type=type_hints["options"])
        jsii.create(self.__class__, self, [options])

    @builtins.property
    @jsii.member(jsii_name="parameters")
    def parameters(self) -> IActiveScanPolicyParameters:
        return typing.cast(IActiveScanPolicyParameters, jsii.get(self, "parameters"))

    @parameters.setter
    def parameters(self, value: IActiveScanPolicyParameters) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__594a955ffe1c41d834041f98154c328824be38ab69b6eaecb5b0c785d3d34fd0)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "parameters", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="type")
    def type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "type"))

    @type.setter
    def type(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__28415b318e2fd90ea1b1c240526adfea64ef34b7046408555978fbe90c774958)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "type", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="alwaysRun")
    def always_run(self) -> typing.Optional[builtins.bool]:
        return typing.cast(typing.Optional[builtins.bool], jsii.get(self, "alwaysRun"))

    @always_run.setter
    def always_run(self, value: typing.Optional[builtins.bool]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a450984d1535a0445fedd3525ca5d483fb59cdd49fcce581786180c007cf1b55)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "alwaysRun", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="enabled")
    def enabled(self) -> typing.Optional[builtins.bool]:
        return typing.cast(typing.Optional[builtins.bool], jsii.get(self, "enabled"))

    @enabled.setter
    def enabled(self, value: typing.Optional[builtins.bool]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__12938ef5f26097b25cab621a708d4ac8db768d16c71bc372520242172527a67c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "enabled", value) # pyright: ignore[reportArgumentType]


@jsii.implements(IActiveScanPolicyDefinition)
class ActiveScanPolicyDefinition(
    metaclass=jsii.JSIIMeta,
    jsii_type="zap-cdk.ActiveScanPolicyDefinition",
):
    '''Class representing the policy definition for an active scan.

    :class: ActiveScanPolicyDefinition
    :implements: IActiveScanPolicyDefinition *
    :property: {Date} updatedAt - Last updated date of the policy.
    '''

    def __init__(self, options: IActiveScanPolicyDefinition) -> None:
        '''Creates an instance of ActiveScanPolicyDefinition.

        :param options: - The configuration options for the policy definition.

        :property: {Date} options.updatedAt - Last updated date of the policy.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__70c8371a279367b4433448a0352d077e581f0fc600442e3aa028683ce992f6f9)
            check_type(argname="argument options", value=options, expected_type=type_hints["options"])
        jsii.create(self.__class__, self, [options])

    @builtins.property
    @jsii.member(jsii_name="createdAt")
    def created_at(self) -> datetime.datetime:
        return typing.cast(datetime.datetime, jsii.get(self, "createdAt"))

    @created_at.setter
    def created_at(self, value: datetime.datetime) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f807d237d2f2aa67b01d927c020eee461bf10ab6348839e95cb5259d7f21878a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "createdAt", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="id")
    def id(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "id"))

    @id.setter
    def id(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f590a204c82e8ce44064a8965133173b5529e15bfb0e0395b6de019ef902f0a8)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "id", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c82cf1b96694a497b30d69002d0b5db5b395a678709c41f0d05c07a435d29db2)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "name", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="updatedAt")
    def updated_at(self) -> datetime.datetime:
        return typing.cast(datetime.datetime, jsii.get(self, "updatedAt"))

    @updated_at.setter
    def updated_at(self, value: datetime.datetime) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ef3c2ce9e5b63cd4c6ee0651c486d98419ad952804034792c0144bf09348c166)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "updatedAt", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="description")
    def description(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "description"))

    @description.setter
    def description(self, value: typing.Optional[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5528f46763f2305d0d4ead5168e7b76b0cb0b6e5d49df615d6fb3849e603cb88)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "description", value) # pyright: ignore[reportArgumentType]


@jsii.implements(IActiveScanPolicyParameters)
class ActiveScanPolicyParameters(
    metaclass=jsii.JSIIMeta,
    jsii_type="zap-cdk.ActiveScanPolicyParameters",
):
    '''Class representing the parameters for an active scan policy.

    :class: ActiveScanPolicyParameters
    :implements: IActiveScanPolicyParameters *
    :property: {ActiveScanPolicyDefinition} policyDefinition - The definition of the policy.
    '''

    def __init__(self, options: IActiveScanPolicyParameters) -> None:
        '''Creates an instance of ActiveScanPolicyParameters.

        :param options: - The configuration options for the active scan policy parameters.

        :property: {IActiveScanPolicyDefinition} options.policyDefinition - The definition of the policy.
        :throws: {Error} If the name property is not provided.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ebf4a01e118d83c76b7176071f5a3e7d887dc48c6eaf81c147e57e06a4d5cc2e)
            check_type(argname="argument options", value=options, expected_type=type_hints["options"])
        jsii.create(self.__class__, self, [options])

    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__62d765d84c17fe61d71ebf8e21494a2c1178cfd9d768a8b5973eed26b7842f07)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "name", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="policyDefinition")
    def policy_definition(self) -> IActiveScanPolicyDefinition:
        return typing.cast(IActiveScanPolicyDefinition, jsii.get(self, "policyDefinition"))

    @policy_definition.setter
    def policy_definition(self, value: IActiveScanPolicyDefinition) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ef93fc4562f155c738fa4d6c1aa91513a8a2480b529c29aacc0f0c4977f8d1a9)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "policyDefinition", value) # pyright: ignore[reportArgumentType]


@jsii.implements(IAjaxTest)
class AjaxTest(metaclass=jsii.JSIIMeta, jsii_type="zap-cdk.AjaxTest"):
    def __init__(self, options: IAjaxTest) -> None:
        '''Creates an instance of AjaxTest.

        :param options: - The options to initialize the AJAX test.

        :property: {'warn' | 'error' | 'info'} [options.onFail] - Action to take on failure.

        Example::

            const ajaxTest = new AjaxTest({
              name: 'Check AJAX requests',
              type: 'stats',
              statistic: 'ajax.requests',
              operator: '>',
              value: 10,
              onFail: 'warn'
            });
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c6ef9ab1b115cd009f22eb685140974a7f97fc6dc0e50f0df96bf4cc8cd6891b)
            check_type(argname="argument options", value=options, expected_type=type_hints["options"])
        jsii.create(self.__class__, self, [options])

    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e9516d2a49f5b1c3f7a6537b906b2a2edf310620c723cbc5aec78357a91b0c6d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "name", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="operator")
    def operator(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "operator"))

    @operator.setter
    def operator(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__dc850a8121706931fb16b6dd9e97c84fef6ec56f9220889d9a8068e75d0ecc29)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "operator", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="statistic")
    def statistic(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "statistic"))

    @statistic.setter
    def statistic(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f66d3a9fb76ed62982365d2b8580a6e9c417f4f5da1a70aba5213a40ba90cf04)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "statistic", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="type")
    def type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "type"))

    @type.setter
    def type(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__cc97b3eb313afaf6a6323abe3e477fa366c2d552bc17547a64473c93ee71bcaa)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "type", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="value")
    def value(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "value"))

    @value.setter
    def value(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5f0dfcf86651c1d90ef4752a5e1592413bfa3200761027a5a62e4123715a5427)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "value", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="onFail")
    def on_fail(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "onFail"))

    @on_fail.setter
    def on_fail(self, value: typing.Optional[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8c7609fb668ad10cc15cc469fc2d5ca54dba8a7fc1dc57e40b3b0e6d6757bc1b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "onFail", value) # pyright: ignore[reportArgumentType]


@jsii.implements(IAlertFilter)
class AlertFilter(metaclass=jsii.JSIIMeta, jsii_type="zap-cdk.AlertFilter"):
    '''Class representing a filter for alerts in the scanning process.

    :implements: IAlertFilter *

    Example::

        const alertFilter = new AlertFilter({
          ruleId: 10010,
          newRisk: 'Low',
          context: 'MyContext',
          url: '.*example.*',
          urlRegex: true,
          parameter: 'sessionid',
          parameterRegex: false,
          attack: 'SQL Injection',
          attackRegex: false,
          evidence: 'SELECT',
          evidenceRegex: true
        });
    '''

    def __init__(self, options: IAlertFilter) -> None:
        '''Creates an instance of AlertFilter.

        :param options: - The configuration options for the alert filter.

        Example::

            const alertFilter = new AlertFilter({
              ruleId: 10010,
              newRisk: 'Low',
              context: 'MyContext',
              url: '.*example.*',
              urlRegex: true,
              parameter: 'sessionid',
              parameterRegex: false,
              attack: 'SQL Injection',
              attackRegex: false,
              evidence: 'SELECT',
              evidenceRegex: true
            });
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2fb23318a5c05e0201f11704a3048ade67dc076741280a9081033dfc46febb76)
            check_type(argname="argument options", value=options, expected_type=type_hints["options"])
        jsii.create(self.__class__, self, [options])

    @builtins.property
    @jsii.member(jsii_name="newRisk")
    def new_risk(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "newRisk"))

    @new_risk.setter
    def new_risk(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9379d76457ebd34954e12578150052add41db521bd75820248995f66c5341dc5)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "newRisk", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="ruleId")
    def rule_id(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "ruleId"))

    @rule_id.setter
    def rule_id(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__134a4d4cab7fe123ab02010f0e38548765c86ab45504eb66dba033a81803c4b8)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "ruleId", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="attack")
    def attack(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "attack"))

    @attack.setter
    def attack(self, value: typing.Optional[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__14241304945c9b667f6add030d3ff79906606d7d2a1bf3be3fb1c96bafe6cd9b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "attack", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="attackRegex")
    def attack_regex(self) -> typing.Optional[builtins.bool]:
        return typing.cast(typing.Optional[builtins.bool], jsii.get(self, "attackRegex"))

    @attack_regex.setter
    def attack_regex(self, value: typing.Optional[builtins.bool]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4b081445f35fab2b9572d1f49ff01ca45f6be8f34af6fd571cef023b8c7c26c3)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "attackRegex", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="context")
    def context(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "context"))

    @context.setter
    def context(self, value: typing.Optional[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a1981c6a02b74cf993ed0f77fce68f0b08ece07e8e963220da3872089cec8ce0)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "context", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="evidence")
    def evidence(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "evidence"))

    @evidence.setter
    def evidence(self, value: typing.Optional[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3cab09ed7d5eb1ddf5a1c66bd2cfa6c561b9b43f4e8f8a6a94f998565f97d80c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "evidence", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="evidenceRegex")
    def evidence_regex(self) -> typing.Optional[builtins.bool]:
        return typing.cast(typing.Optional[builtins.bool], jsii.get(self, "evidenceRegex"))

    @evidence_regex.setter
    def evidence_regex(self, value: typing.Optional[builtins.bool]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1de266faf7a847086a6fbfcc9e40f9cde40560d633ce6c0e43c6dba91bde5ce9)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "evidenceRegex", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="parameter")
    def parameter(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "parameter"))

    @parameter.setter
    def parameter(self, value: typing.Optional[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1d654a80de82e2e0f8ffeb537719880ad1dca06365dae01cace70af48a6f2238)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "parameter", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="parameterRegex")
    def parameter_regex(self) -> typing.Optional[builtins.bool]:
        return typing.cast(typing.Optional[builtins.bool], jsii.get(self, "parameterRegex"))

    @parameter_regex.setter
    def parameter_regex(self, value: typing.Optional[builtins.bool]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__fb6a2df026a5b62af10fcca71dcc77827d4d5f54d48d0342ebc16cf8da901b7e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "parameterRegex", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="url")
    def url(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "url"))

    @url.setter
    def url(self, value: typing.Optional[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a695a6a45022afb056ba9af145e8fbb5c95683eaf9f3e495745d2d81af330b43)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "url", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="urlRegex")
    def url_regex(self) -> typing.Optional[builtins.bool]:
        return typing.cast(typing.Optional[builtins.bool], jsii.get(self, "urlRegex"))

    @url_regex.setter
    def url_regex(self, value: typing.Optional[builtins.bool]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0c7ae79b646680d85b0a43f8673fada25fad2de89a89556cb2268900f127007d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "urlRegex", value) # pyright: ignore[reportArgumentType]


@jsii.implements(IAlertFilterParameters)
class AlertFilterParameters(
    metaclass=jsii.JSIIMeta,
    jsii_type="zap-cdk.AlertFilterParameters",
):
    def __init__(self, options: IAlertFilterParameters) -> None:
        '''Creates an instance of AlertFilterParameters.

        :param options: - The configuration options for the alert filter parameters.

        Example::

            const alertFilterParams = new AlertFilterParameters({
              deleteGlobalAlerts: true,
              alertFilters: [
                new AlertFilter({
                  ruleId: 10010,
                  newRisk: 'Low',
                  context: 'MyContext',
                  url: '.*example.*',
                  urlRegex: true,
                  parameter: 'sessionid',
                  parameterRegex: false,
                  attack: 'SQL Injection',
                  attackRegex: false,
                  evidence: 'SELECT',
                  evidenceRegex: true
                })
              ]
            });
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6e29e19af954a95bf4959b058d0f5fc55e5ce8c00c52b91cc87d417d5671193e)
            check_type(argname="argument options", value=options, expected_type=type_hints["options"])
        jsii.create(self.__class__, self, [options])

    @builtins.property
    @jsii.member(jsii_name="alertFilters")
    def alert_filters(self) -> typing.List[IAlertFilter]:
        return typing.cast(typing.List[IAlertFilter], jsii.get(self, "alertFilters"))

    @alert_filters.setter
    def alert_filters(self, value: typing.List[IAlertFilter]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d048d7c034ddb3eff66f305e8301338734d8e569cf38f2b6a35fd07ee5ea8d57)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "alertFilters", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="deleteGlobalAlerts")
    def delete_global_alerts(self) -> typing.Optional[builtins.bool]:
        return typing.cast(typing.Optional[builtins.bool], jsii.get(self, "deleteGlobalAlerts"))

    @delete_global_alerts.setter
    def delete_global_alerts(self, value: typing.Optional[builtins.bool]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3de99f28c0ce43a37b1b11f46cd79b6ac9db465e905884e1ba1616db3ade1b34)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "deleteGlobalAlerts", value) # pyright: ignore[reportArgumentType]


@jsii.implements(IAlertTag)
class AlertTag(metaclass=jsii.JSIIMeta, jsii_type="zap-cdk.AlertTag"):
    '''Class representing the configuration for alert tags.

    :class: AlertTag
    :implements: IAlertTag *
    :property: {threshold} [threshold] - The Alert Threshold for this set of rules, default: Medium.
    '''

    def __init__(self, options: typing.Optional[IAlertTag] = None) -> None:
        '''Creates an instance of AlertTag.

        :param options: - The configuration options for alert tags.

        :property: {threshold} [options.threshold] - The Alert Threshold for this set of rules, default: Medium.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__09d54d0bdde2e854061990c81bbec5f00f106fc50748b1c10aebe5e708ea8257)
            check_type(argname="argument options", value=options, expected_type=type_hints["options"])
        jsii.create(self.__class__, self, [options])

    @builtins.property
    @jsii.member(jsii_name="exclude")
    def exclude(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "exclude"))

    @exclude.setter
    def exclude(self, value: typing.Optional[typing.List[builtins.str]]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9e86415242d7589ea703d9b0faf348ab54d8b1ea46dcc02f9b9dba45c8503c90)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "exclude", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="include")
    def include(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "include"))

    @include.setter
    def include(self, value: typing.Optional[typing.List[builtins.str]]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__583c04532b41febfbde1de15b973d2093b1ac3e49cbc9d5685eaf6ac50c0b5a4)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "include", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="strength")
    def strength(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "strength"))

    @strength.setter
    def strength(self, value: typing.Optional[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e747ad2981d36642d317ac6b53c0042d8e0147be53f23b1221728f96c4bb867e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "strength", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="threshold")
    def threshold(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "threshold"))

    @threshold.setter
    def threshold(self, value: typing.Optional[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1edf6bfb32200e381492349baa817335994f538ae6754054bbe6afeeb2fc4824)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "threshold", value) # pyright: ignore[reportArgumentType]


@jsii.implements(IAlertTags)
class AlertTags(metaclass=jsii.JSIIMeta, jsii_type="zap-cdk.AlertTags"):
    '''Class representing the configuration for alert tags.

    :implements: IAlertTags *
    :property: {string} [threshold] - The Alert Threshold for this set of rules, one of Off, Low, Medium, High, default: Medium.
    '''

    def __init__(self, options: IAlertTags) -> None:
        '''Creates an instance of AlertTags.

        :param options: - The configuration for alert tags.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__012a77be1911ea01e692411edd3f710b38c65804574bfb20dd997e462cc2fa7e)
            check_type(argname="argument options", value=options, expected_type=type_hints["options"])
        jsii.create(self.__class__, self, [options])

    @builtins.property
    @jsii.member(jsii_name="exclude")
    def exclude(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "exclude"))

    @exclude.setter
    def exclude(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8bf6f0d1fb4cb5423d52a70e5db91aa05a85dc25ba68edaea29d6e02c517bccd)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "exclude", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="include")
    def include(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "include"))

    @include.setter
    def include(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__96004500518890dc200392d1f8e64595da4616bfa4d8333fac9eef9f4a6dd12f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "include", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="strength")
    def strength(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "strength"))

    @strength.setter
    def strength(self, value: typing.Optional[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3955be8c8fc82f2d142a19f39ac0daa2482f645fe882dc9d910fcc567bba30b0)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "strength", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="threshold")
    def threshold(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "threshold"))

    @threshold.setter
    def threshold(self, value: typing.Optional[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__35f5199af5e98aa1ec4f109ec97c81b93aefe195379f93d3bc1b873b1b61c21b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "threshold", value) # pyright: ignore[reportArgumentType]


@jsii.implements(IAlertTest)
class AlertTest(metaclass=jsii.JSIIMeta, jsii_type="zap-cdk.AlertTest"):
    def __init__(self, options: IAlertTest) -> None:
        '''Creates an instance of AlertTest.

        :param options: - The configuration options for the alert test.

        :property: {OnFailType} options.onFail - Action to take on failure, mandatory.

        Example::

            const alertTest = new AlertTest({
              name: 'test one',
              action: 'passIfPresent',
              scanRuleId: 123,
              alertName: 'SQL Injection',
              url: 'http://www.example.com/path',
              method: 'GET',
              attack: 'SQL Injection Attack',
              param: 'username',
              evidence: 'Evidence of SQL injection',
              confidence: 'High',
              risk: 'High',
              onFail: 'info'
            });
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0a1eeee781bae8d8ebc926a0a555ff1c4a9090dcf227a719869a7ef6fa1345c8)
            check_type(argname="argument options", value=options, expected_type=type_hints["options"])
        jsii.create(self.__class__, self, [options])

    @builtins.property
    @jsii.member(jsii_name="onFail")
    def on_fail(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "onFail"))

    @on_fail.setter
    def on_fail(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4be3d48b847f5073f6f869064e4b8f899ac6b75da737c3b9cc979cf78b3cc3c2)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "onFail", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="scanRuleId")
    def scan_rule_id(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "scanRuleId"))

    @scan_rule_id.setter
    def scan_rule_id(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ce93bedb98f55c44ff18751009ecb87cf63e58d879a29787eb34a0db4506f549)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "scanRuleId", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="type")
    def type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "type"))

    @type.setter
    def type(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__77dffb9ce57ae71b9eb1c56b4cb824297c7f4644fa48251388975933032ae3a3)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "type", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="action")
    def action(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "action"))

    @action.setter
    def action(self, value: typing.Optional[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b2b4152c08989ee0e811ea1c6553d4e1bd77e89c78fd4fb0d2724a2923e43599)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "action", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="alertName")
    def alert_name(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "alertName"))

    @alert_name.setter
    def alert_name(self, value: typing.Optional[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f310c064785080dd019f1709b5db5cd1e02b67dd8adad0c4bce11ba75d57ed8d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "alertName", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="attack")
    def attack(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "attack"))

    @attack.setter
    def attack(self, value: typing.Optional[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2ecb64911b6561c0e290006d6fc29add7d3207eea92a052e32f73d82f1661124)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "attack", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="confidence")
    def confidence(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "confidence"))

    @confidence.setter
    def confidence(self, value: typing.Optional[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a4d98037e282bce55dc4043ea9803f40d96f714e64619b5448f0d32ae88d2c94)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "confidence", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="evidence")
    def evidence(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "evidence"))

    @evidence.setter
    def evidence(self, value: typing.Optional[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ee9c31d12de60675c2cc1a60fd129660444a782abe527a2748ce1efbaa3e75be)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "evidence", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="method")
    def method(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "method"))

    @method.setter
    def method(self, value: typing.Optional[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c1ba61dfd78788d03c0f7976f8e43a94f8699ec6e181193239ef5674787cad43)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "method", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "name"))

    @name.setter
    def name(self, value: typing.Optional[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__dbe8013c7f946a1bb6f2033fc4a9409d61817d82aeac08affef0929b0b42af56)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "name", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="param")
    def param(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "param"))

    @param.setter
    def param(self, value: typing.Optional[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2349e34dfa71825d4c30b930ef0fdb9a06bb4a0a60b6a6a75e636500d866c133)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "param", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="risk")
    def risk(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "risk"))

    @risk.setter
    def risk(self, value: typing.Optional[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__fe8362b544297c08bcbaa0d298e2c418c1b5e13a66129cb319029e72a175ed43)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "risk", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="url")
    def url(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "url"))

    @url.setter
    def url(self, value: typing.Optional[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d46e5cc6be2ffd00ca7b9cfee8cdeb7717418b468405cce7dd1b618020274259)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "url", value) # pyright: ignore[reportArgumentType]


@jsii.implements(IAuthenticationParameters)
class AuthenticationParameters(
    metaclass=jsii.JSIIMeta,
    jsii_type="zap-cdk.AuthenticationParameters",
):
    '''Represents the parameters for authentication in the scanning process.

    :class: AuthenticationParameters
    :implements: IAuthenticationParameters *
    :property: {string} verification.pollAdditionalHeaders[].value - The header value.
    '''

    def __init__(self, options: IAuthenticationParameters) -> None:
        '''Creates an instance of AuthenticationParameters.

        :param options: - The options to initialize the authentication parameters.

        :property: {string} options.verification.pollAdditionalHeaders[].value - The header value.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7d5051de2cf23a10abe9405eddb4c76ea938d4645c31f214e5db739deb0ff2bc)
            check_type(argname="argument options", value=options, expected_type=type_hints["options"])
        jsii.create(self.__class__, self, [options])

    @builtins.property
    @jsii.member(jsii_name="method")
    def method(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "method"))

    @method.setter
    def method(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7d284f5c1079bee6a8ba4724bdbab2a7ce009375ab9a5a450f97696be7677cf7)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "method", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="parameters")
    def parameters(self) -> IAuthenticationParametersParameters:
        return typing.cast(IAuthenticationParametersParameters, jsii.get(self, "parameters"))

    @parameters.setter
    def parameters(self, value: IAuthenticationParametersParameters) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9a517c037186b642234018061e2de7f341f7c16a0516e2e4bad6a97d9ff26a23)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "parameters", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="verification")
    def verification(self) -> IAuthenticationParametersVerification:
        return typing.cast(IAuthenticationParametersVerification, jsii.get(self, "verification"))

    @verification.setter
    def verification(self, value: IAuthenticationParametersVerification) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d59bbb0e600a0254c50b5b1ed1440acde1b39226c363f394566f267d8dcf81c9)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "verification", value) # pyright: ignore[reportArgumentType]


@jsii.implements(IAuthenticationParametersParameters)
class AuthenticationParametersParameters(
    metaclass=jsii.JSIIMeta,
    jsii_type="zap-cdk.AuthenticationParametersParameters",
):
    '''Represents the parameters for authentication in the scanning process.

    :class: AuthenticationParametersParameters
    :implements: IAuthenticationParametersParameters *
    :property: {string} [scriptEngine] - Name of the script engine to use, only for 'script' authentication.
    '''

    def __init__(
        self,
        options: typing.Optional[IAuthenticationParametersParameters] = None,
    ) -> None:
        '''Creates an instance of AuthenticationParametersParameters.

        :param options: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1329013a27a80fdbf8dc450922289913970047c12730babb0902dfd019eef346)
            check_type(argname="argument options", value=options, expected_type=type_hints["options"])
        jsii.create(self.__class__, self, [options])

    @builtins.property
    @jsii.member(jsii_name="hostname")
    def hostname(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "hostname"))

    @hostname.setter
    def hostname(self, value: typing.Optional[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4cff7db9e6ff1590f96c938c410e2d61dc745d12d9f62e18bc350005a8a3f4b9)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "hostname", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="loginPageUrl")
    def login_page_url(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "loginPageUrl"))

    @login_page_url.setter
    def login_page_url(self, value: typing.Optional[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__efb1245b1009f2d8b2623cd809e3e940ec18c6b36a57c032e79d168daba07d52)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "loginPageUrl", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="loginRequestBody")
    def login_request_body(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "loginRequestBody"))

    @login_request_body.setter
    def login_request_body(self, value: typing.Optional[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a68756cdf33a5b291896b57d83687667b38f5735c29d1cac4091a317c394f51a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "loginRequestBody", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="loginRequestUrl")
    def login_request_url(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "loginRequestUrl"))

    @login_request_url.setter
    def login_request_url(self, value: typing.Optional[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3df07182ef641018e49cd4ec4130fd5dce2fa4dfce14c1290b01037fb070ceea)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "loginRequestUrl", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="port")
    def port(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "port"))

    @port.setter
    def port(self, value: typing.Optional[jsii.Number]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9e966666d098a9b5b13a058b9d60b1880ed3eab6e5270b678086a1879d331820)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "port", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="realm")
    def realm(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "realm"))

    @realm.setter
    def realm(self, value: typing.Optional[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__486380ca0ede2e15539c5dc85e3431c883a6f515b1c16f293074e057c3a3c903)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "realm", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="script")
    def script(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "script"))

    @script.setter
    def script(self, value: typing.Optional[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ac61435363b7cfec8adb42841d50786a829f2ad3ad2fff1577fb8084762364f0)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "script", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="scriptEngine")
    def script_engine(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "scriptEngine"))

    @script_engine.setter
    def script_engine(self, value: typing.Optional[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__972aad6e7bc25c329b2e48bdfad7d5ff8adace87bf5ab2e3b5461d1e229c3320)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "scriptEngine", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="scriptInline")
    def script_inline(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "scriptInline"))

    @script_inline.setter
    def script_inline(self, value: typing.Optional[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1e38456f623c4a1f27f5188f882898c801f9c87a2862461a203ebfd7a842532b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "scriptInline", value) # pyright: ignore[reportArgumentType]


@jsii.implements(IAuthenticationParametersVerification)
class AuthenticationParametersVerification(
    metaclass=jsii.JSIIMeta,
    jsii_type="zap-cdk.AuthenticationParametersVerification",
):
    '''Represents the verification details for authentication in the scanning process.

    :class: AuthenticationParametersVerification
    :implements: IAuthenticationParametersVerification *
    :property: {string} pollAdditionalHeaders[].value - The header value.
    '''

    def __init__(self, options: IAuthenticationParametersVerification) -> None:
        '''Creates an instance of AuthenticationParametersVerification.

        :param options: - The options to initialize the verification details.

        :property: {string} options.pollAdditionalHeaders[].value - The header value.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__78a9626ee3cc0a454b4ab39695b03419001265fe4f7a890ae2bfc74d9a38556d)
            check_type(argname="argument options", value=options, expected_type=type_hints["options"])
        jsii.create(self.__class__, self, [options])

    @builtins.property
    @jsii.member(jsii_name="method")
    def method(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "method"))

    @method.setter
    def method(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2cd3a437dd46c186f07054ffbb1b9168ec83c9dca2f5e8cb0f67442f8c425c63)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "method", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="loggedInRegex")
    def logged_in_regex(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "loggedInRegex"))

    @logged_in_regex.setter
    def logged_in_regex(self, value: typing.Optional[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1d5edd1c38fe34db8179d9706c65abaefbc47f4d7fafce4d55c24c41a51ebc90)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "loggedInRegex", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="loggedOutRegex")
    def logged_out_regex(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "loggedOutRegex"))

    @logged_out_regex.setter
    def logged_out_regex(self, value: typing.Optional[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__cbbd34e680286d24b1a3b58bf878296162546817485fe838b692aebf03f79e3a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "loggedOutRegex", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="pollAdditionalHeaders")
    def poll_additional_headers(
        self,
    ) -> typing.Optional[typing.List[IPollAdditionalHeaders]]:
        return typing.cast(typing.Optional[typing.List[IPollAdditionalHeaders]], jsii.get(self, "pollAdditionalHeaders"))

    @poll_additional_headers.setter
    def poll_additional_headers(
        self,
        value: typing.Optional[typing.List[IPollAdditionalHeaders]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__de06133bc37f5f00cdf4684f99ccc783c5bb3ae4a30a8d89faa09fa0a4747f08)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "pollAdditionalHeaders", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="pollFrequency")
    def poll_frequency(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "pollFrequency"))

    @poll_frequency.setter
    def poll_frequency(self, value: typing.Optional[jsii.Number]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f15a2849a755a31839f457a582c1e34f7e1220ac987ce302065a8dbe8f5e77ea)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "pollFrequency", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="pollPostData")
    def poll_post_data(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "pollPostData"))

    @poll_post_data.setter
    def poll_post_data(self, value: typing.Optional[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d5a3d7148fee54a04ba884c326be849de398c22f6ed0bebf1444a9adca9b9792)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "pollPostData", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="pollUnits")
    def poll_units(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "pollUnits"))

    @poll_units.setter
    def poll_units(self, value: typing.Optional[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__13e202c31a9b86659259ad91c593fdf9724bd156dec73bde1eb7c06ec5849c4d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "pollUnits", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="pollUrl")
    def poll_url(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "pollUrl"))

    @poll_url.setter
    def poll_url(self, value: typing.Optional[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9efd98dc9926dc87cf409f9145679c8fa21f85867d5f5b3f9e33998084f0cb1c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "pollUrl", value) # pyright: ignore[reportArgumentType]


@jsii.implements(IContextStructure)
class ContextStructure(metaclass=jsii.JSIIMeta, jsii_type="zap-cdk.ContextStructure"):
    '''Represents the structure details of the context.

    :class: ContextStructure
    :implements: IContextStructure *
    :property: {IDataDrivenNode[]} [dataDrivenNodes] - List of data driven nodes.
    '''

    def __init__(self, options: IContextStructure) -> None:
        '''Creates an instance of ContextStructure.

        :param options: - The options to initialize the context structure.

        :property: {IDataDrivenNode[]} [options.dataDrivenNodes] - List of data driven nodes.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1d5809817c8b283f3d2b9e6def3e5982ded3e1c6371f4c366ef28ba790581161)
            check_type(argname="argument options", value=options, expected_type=type_hints["options"])
        jsii.create(self.__class__, self, [options])

    @builtins.property
    @jsii.member(jsii_name="dataDrivenNodes")
    def data_driven_nodes(self) -> typing.Optional[typing.List[IDataDrivenNode]]:
        return typing.cast(typing.Optional[typing.List[IDataDrivenNode]], jsii.get(self, "dataDrivenNodes"))

    @data_driven_nodes.setter
    def data_driven_nodes(
        self,
        value: typing.Optional[typing.List[IDataDrivenNode]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__737294269ace93aab91086394ccd2936c1478415ef00eea71b56315d6b46e240)
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
            type_hints = typing.get_type_hints(_typecheckingstub__f245e60b36bf0087db3bd3dba2312eb8a9ebf8d154f4dcafbc7de1f2286d585f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "structuralParameters", value) # pyright: ignore[reportArgumentType]


@jsii.implements(IContextUser)
class ContextUser(metaclass=jsii.JSIIMeta, jsii_type="zap-cdk.ContextUser"):
    '''Represents a user in the context.

    :class: ContextUser
    :implements: IContextUser *
    :property: {IUserCredentials[]} credentials - User credentials for authentication.
    '''

    def __init__(self, options: IContextUser) -> None:
        '''Creates an instance of ContextUser.

        :param options: - The options to initialize the context user.

        :property: {IUserCredentials[]} options.credentials - User credentials for authentication.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__cf097ec1b59c6d6305e9d45e894285013f6bf2d08206715e86d85dcbbe31fffd)
            check_type(argname="argument options", value=options, expected_type=type_hints["options"])
        jsii.create(self.__class__, self, [options])

    @builtins.property
    @jsii.member(jsii_name="credentials")
    def credentials(self) -> typing.List[IUserCredentials]:
        return typing.cast(typing.List[IUserCredentials], jsii.get(self, "credentials"))

    @credentials.setter
    def credentials(self, value: typing.List[IUserCredentials]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__dec059b7c453dae8078bf6f80f76f095b11b6b2f2e566ce64d7e6dcbed26a293)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "credentials", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__28fe30eb403dfefee7590b8887610be270bcf1c7368d92022b798320d45842fa)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "name", value) # pyright: ignore[reportArgumentType]


@jsii.implements(ICookieData)
class CookieData(metaclass=jsii.JSIIMeta, jsii_type="zap-cdk.CookieData"):
    '''Class representing the configuration for cookie data scanning.

    :implements: ICookieData *
    :property: {boolean} [encodeCookieValues] - If cookie values should be encoded. Default: false.

    Example::

        const cookieConfig = new CookieData({ enabled: false, encodeCookieValues: false });
        console.log(cookieConfig.enabled); // false
    '''

    def __init__(self, options: typing.Optional[ICookieData] = None) -> None:
        '''Creates an instance of CookieData.

        :param options: - The configuration options for cookie data scanning.

        :memberof: CookieData

        Example::

            const cookieConfig = new CookieData({ enabled: false, encodeCookieValues: false });
            console.log(cookieConfig.enabled); // false
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8794d236188a85c4bc7f0ce3352c13c921d0fde1b9698bc77c3d8273c5f34daf)
            check_type(argname="argument options", value=options, expected_type=type_hints["options"])
        jsii.create(self.__class__, self, [options])

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
            type_hints = typing.get_type_hints(_typecheckingstub__1fe3ab94daa513978836677c7a8f4b7086044de841d3e8a5c4a8c97e4668971e)
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
            type_hints = typing.get_type_hints(_typecheckingstub__a31f4fd01751421e887e4a1582261994b16e27810dbc19953c7be9ea41a4c4c8)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "encodeCookieValues", value) # pyright: ignore[reportArgumentType]


@jsii.implements(IDataDrivenNode)
class DataDrivenNode(metaclass=jsii.JSIIMeta, jsii_type="zap-cdk.DataDrivenNode"):
    '''Represents a data-driven node in the scanning process.

    :class: DataDrivenNode
    :implements: IDataDrivenNode *
    :property: {string} regex - Regex of the data driven node, must contain 2 or 3 regex groups.
    '''

    def __init__(self, options: IDataDrivenNode) -> None:
        '''Creates an instance of DataDrivenNode.

        :param options: - The options to initialize the data-driven node.

        :property: {string} options.regex - Regex of the data-driven node, must contain 2 or 3 regex groups.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f4acb1d9764609ae7ee038ccd9d42ce1c89f3a100f2418a8a59afef323e50ebc)
            check_type(argname="argument options", value=options, expected_type=type_hints["options"])
        jsii.create(self.__class__, self, [options])

    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5620b63226ab7448ee63f17886daf5233f5e02fb6df253d92a17b495af930a41)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "name", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="regex")
    def regex(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "regex"))

    @regex.setter
    def regex(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__24ebd6d4c5b0e4e95b132d4a109977789bb7300a4b32156af4127dfedbc47643)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "regex", value) # pyright: ignore[reportArgumentType]


@jsii.implements(IDelay)
class Delay(metaclass=jsii.JSIIMeta, jsii_type="zap-cdk.Delay"):
    def __init__(
        self,
        parameters: IDelayParameters,
        enabled: typing.Optional[builtins.bool] = None,
        always_run: typing.Optional[builtins.bool] = None,
    ) -> None:
        '''Creates an instance of Delay.

        :param parameters: - The parameters for the delay configuration.
        :param enabled: - If set to false the job will not be run, default: true.
        :param always_run: - If set and the job is enabled then it will run even if the plan exits early, default: false.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2780a37bffa1d9d2d30e73ea731a4526e213c8a4b2abd041fc452c9d4e9ece38)
            check_type(argname="argument parameters", value=parameters, expected_type=type_hints["parameters"])
            check_type(argname="argument enabled", value=enabled, expected_type=type_hints["enabled"])
            check_type(argname="argument always_run", value=always_run, expected_type=type_hints["always_run"])
        jsii.create(self.__class__, self, [parameters, enabled, always_run])

    @builtins.property
    @jsii.member(jsii_name="parameters")
    def parameters(self) -> IDelayParameters:
        return typing.cast(IDelayParameters, jsii.get(self, "parameters"))

    @parameters.setter
    def parameters(self, value: IDelayParameters) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6a6ab60a1e6442bf9deb7aaf8f3094a23050929ac95611e42e834ffe33c765f3)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "parameters", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="type")
    def type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "type"))

    @type.setter
    def type(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e37b6069dbe3969d7c6befc8d3fe6eb27b6a9dda08199df93596557406f9ff86)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "type", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="alwaysRun")
    def always_run(self) -> typing.Optional[builtins.bool]:
        return typing.cast(typing.Optional[builtins.bool], jsii.get(self, "alwaysRun"))

    @always_run.setter
    def always_run(self, value: typing.Optional[builtins.bool]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__76d116649c51e592f54735851281a84a860ed11b2cb2a5577cad79ad9fac2c6e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "alwaysRun", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="enabled")
    def enabled(self) -> typing.Optional[builtins.bool]:
        return typing.cast(typing.Optional[builtins.bool], jsii.get(self, "enabled"))

    @enabled.setter
    def enabled(self, value: typing.Optional[builtins.bool]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8dc6a4b56e86d0ec225279218c8556d462b8d071dc6dba85142324dd5e48922d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "enabled", value) # pyright: ignore[reportArgumentType]


@jsii.implements(IDelayParameters)
class DelayParameters(metaclass=jsii.JSIIMeta, jsii_type="zap-cdk.DelayParameters"):
    def __init__(
        self,
        time: typing.Optional[builtins.str] = None,
        file_name: typing.Optional[builtins.str] = None,
    ) -> None:
        '''Creates an instance of DelayParameters.

        :param time: - The time to wait, format any of ['hh:mm:ss', 'mm:ss', 'ss'], default: 0.
        :param file_name: - Name of a file which will cause the job to end early if created, default: empty.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0cd44bbcd4f268acf5c20a21d1b7f1c005f607826b14c51c3c2270796fdfa706)
            check_type(argname="argument time", value=time, expected_type=type_hints["time"])
            check_type(argname="argument file_name", value=file_name, expected_type=type_hints["file_name"])
        jsii.create(self.__class__, self, [time, file_name])

    @builtins.property
    @jsii.member(jsii_name="fileName")
    def file_name(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "fileName"))

    @file_name.setter
    def file_name(self, value: typing.Optional[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__14acebdb3d15fcf3560f470f2e10d14cf040f0278a4671c308f62d35394f9ec7)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "fileName", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="time")
    def time(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "time"))

    @time.setter
    def time(self, value: typing.Optional[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f1c259dde8eb3267fb0a349d1d77917bda5a6b9865a2aafdbc5e1961517f78a5)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "time", value) # pyright: ignore[reportArgumentType]


@jsii.implements(IExcludedElement)
class ExcludedElement(metaclass=jsii.JSIIMeta, jsii_type="zap-cdk.ExcludedElement"):
    '''Class representing an excluded HTML element configuration.

    :class: ExcludedElement
    :implements: IExcludedElement *

    Example::

        const excludedElement = new ExcludedElement({
          description: 'Exclude login button',
          element: 'button',
          text: 'Login'
        });
    '''

    def __init__(self, options: IExcludedElement) -> None:
        '''Creates an instance of ExcludedElement.

        :param options: - The options to initialize the excluded element.

        :property: {string} [options.attributeValue] - Optional value of the attribute.

        Example::

            const excludedElement = new ExcludedElement({
              description: 'Exclude login button',
              element: 'button',
              text: 'Login'
            });
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f56dcf0632d6a6d4523337e4a9909e1c879007047e95a24e709e93b07adf9139)
            check_type(argname="argument options", value=options, expected_type=type_hints["options"])
        jsii.create(self.__class__, self, [options])

    @builtins.property
    @jsii.member(jsii_name="description")
    def description(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "description"))

    @description.setter
    def description(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ea14f607b601781b70715f3ce34891cad569baf33a4c1462c17137564343a03d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "description", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="element")
    def element(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "element"))

    @element.setter
    def element(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c86f29d0b3e08ddae791e45dafe96a41a53f3bd0af8da372817588faa4ecc11b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "element", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="attributeName")
    def attribute_name(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "attributeName"))

    @attribute_name.setter
    def attribute_name(self, value: typing.Optional[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__53a85c348d4e2b397b03077283bfb8a98679b1ce894162a6f018541f20bea7a2)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "attributeName", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="attributeValue")
    def attribute_value(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "attributeValue"))

    @attribute_value.setter
    def attribute_value(self, value: typing.Optional[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b05cdc983b6613cc828db56497b43fd0200b6745729dae03f989d14e6e6e671a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "attributeValue", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="text")
    def text(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "text"))

    @text.setter
    def text(self, value: typing.Optional[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__56c1a2a8ad8301594d8d327672d1a517203986cbeb46529c44d19020a687319d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "text", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="xpath")
    def xpath(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "xpath"))

    @xpath.setter
    def xpath(self, value: typing.Optional[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__bbbe78e999f173cd67d253fc797661aaeed67df12ce691112c7871cdbf154f13)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "xpath", value) # pyright: ignore[reportArgumentType]


@jsii.implements(IExitStatus)
class ExitStatus(metaclass=jsii.JSIIMeta, jsii_type="zap-cdk.ExitStatus"):
    '''Represents the exit status configuration for the scanning process.'''

    def __init__(self, options: IExitStatus) -> None:
        '''Creates an instance of ExitStatus.

        :param options: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__48fdc6d0b23cf2198a171947ed6eef7fdd40285f6717c689b55a66f564fbe97e)
            check_type(argname="argument options", value=options, expected_type=type_hints["options"])
        jsii.create(self.__class__, self, [options])

    @builtins.property
    @jsii.member(jsii_name="parameters")
    def parameters(self) -> IExitStatusParameters:
        return typing.cast(IExitStatusParameters, jsii.get(self, "parameters"))

    @parameters.setter
    def parameters(self, value: IExitStatusParameters) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__dd550c6c36f5b08e7ee97974258059bb198eebda7a7a9b5cee1ab2c711117713)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "parameters", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="type")
    def type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "type"))

    @type.setter
    def type(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ab7d26d5469b5b6c0e29a363f1df400cb54444d7c1410e5ff9f75040b8d016a5)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "type", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="alwaysRun")
    def always_run(self) -> typing.Optional[builtins.bool]:
        return typing.cast(typing.Optional[builtins.bool], jsii.get(self, "alwaysRun"))

    @always_run.setter
    def always_run(self, value: typing.Optional[builtins.bool]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9aa80e9da29b815c2216de3e59544d411c5ae7ccb91a9aa5862ec208bcc359e0)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "alwaysRun", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="enabled")
    def enabled(self) -> typing.Optional[builtins.bool]:
        return typing.cast(typing.Optional[builtins.bool], jsii.get(self, "enabled"))

    @enabled.setter
    def enabled(self, value: typing.Optional[builtins.bool]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__40451e9eb2383fabfc2f6167dd2fcf338905db7adab8c75235e7190fdb177b68)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "enabled", value) # pyright: ignore[reportArgumentType]


@jsii.implements(IExitStatusParameters)
class ExitStatusParameters(
    metaclass=jsii.JSIIMeta,
    jsii_type="zap-cdk.ExitStatusParameters",
):
    '''Represents the parameters for configuring exit status in the scanning process.

    :implements: IExitStatusParameters *

    Example::

        const exitStatusParams = new ExitStatusParameters({
          errorLevel: 'High',
          warnLevel: 'Medium',
          okExitValue: 0,
          errorExitValue: 1,
          warnExitValue: 2
        });
    '''

    def __init__(self, options: IExitStatusParameters) -> None:
        '''Creates an instance of ExitStatusParameters.

        :param options: - The options to initialize the exit status parameters.

        :property: {number} [options.warnExitValue] - Exit value if there are warnings, default: 2.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__737ec7840e8dfa9d9cd5cf32a5984c31ca00e6ad76655f07f1d726f854375cd6)
            check_type(argname="argument options", value=options, expected_type=type_hints["options"])
        jsii.create(self.__class__, self, [options])

    @builtins.property
    @jsii.member(jsii_name="errorExitValue")
    def error_exit_value(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "errorExitValue"))

    @error_exit_value.setter
    def error_exit_value(self, value: typing.Optional[jsii.Number]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a33531853ca010cd8882c5714e9a2ad6beee006846d2e57cb93190ad05124b18)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "errorExitValue", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="errorLevel")
    def error_level(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "errorLevel"))

    @error_level.setter
    def error_level(self, value: typing.Optional[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4ce1b0fe452141f52dadedaec25ac1e425828335ed0ff4b7200c567492d6a9b5)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "errorLevel", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="okExitValue")
    def ok_exit_value(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "okExitValue"))

    @ok_exit_value.setter
    def ok_exit_value(self, value: typing.Optional[jsii.Number]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__39a62fb1c3c72626b222baedfd34426037042b43639e755e64fcc23e8faa619b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "okExitValue", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="warnExitValue")
    def warn_exit_value(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "warnExitValue"))

    @warn_exit_value.setter
    def warn_exit_value(self, value: typing.Optional[jsii.Number]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__432d3c94a37792d993d81a4a6725eadd7a8b2d968dadbf01c54ff8d7dc47f3ea)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "warnExitValue", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="warnLevel")
    def warn_level(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "warnLevel"))

    @warn_level.setter
    def warn_level(self, value: typing.Optional[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1fa427b17c981c14d342fb14befcdc3df096414a5ff731207ee27c782a723585)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "warnLevel", value) # pyright: ignore[reportArgumentType]


@jsii.implements(IExport)
class Export(metaclass=jsii.JSIIMeta, jsii_type="zap-cdk.Export"):
    '''Class representing an export operation.

    :class: Export
    :implements: IExport *

    Example::

        const exportConfig = new Export({
          fileName: 'export.har',
          type: 'har',
          source: 'history',
          context: 'MyContext'
        });
    '''

    def __init__(self, options: IExport) -> None:
        '''Creates an instance of Export.

        :param options: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a77d55a66ee913d0287ddb7b65dacc0e9e2d24afe229da0f45f50f4276cd9ccf)
            check_type(argname="argument options", value=options, expected_type=type_hints["options"])
        jsii.create(self.__class__, self, [options])

    @builtins.property
    @jsii.member(jsii_name="fileName")
    def file_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "fileName"))

    @file_name.setter
    def file_name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__dbeee402395196520cb0c5ef3ee261e41aeb050f715e088d7fcb7ef8222a1890)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "fileName", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="context")
    def context(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "context"))

    @context.setter
    def context(self, value: typing.Optional[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__112fb7b2bcbb690a9d185f92f3e7b9d93cd123e2f25b4483ca3e5709bca9ac99)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "context", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="source")
    def source(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "source"))

    @source.setter
    def source(self, value: typing.Optional[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1bf4f8a646cddadc97de3bda8981a50d3a8e3e2bc223d8db9b54de1440429309)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "source", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="type")
    def type(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "type"))

    @type.setter
    def type(self, value: typing.Optional[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d05c02ccd544ed30bdf5ccc79d345903ebaafe812310e9387bfa36532737c027)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "type", value) # pyright: ignore[reportArgumentType]


@jsii.implements(IGraphQL)
class GraphQL(metaclass=jsii.JSIIMeta, jsii_type="zap-cdk.GraphQL"):
    def __init__(self, options: IGraphQL) -> None:
        '''Creates an instance of GraphQL.

        :param options: - The options to initialize the GraphQL configuration.

        :property: {RequestMethod} [options.requestMethod='post_json'] - The request method, default: post_json.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d0744234256114728d0e2ba4a8c3e24b83f89d6f2800b6fc74f76d3c5c23efcb)
            check_type(argname="argument options", value=options, expected_type=type_hints["options"])
        jsii.create(self.__class__, self, [options])

    @builtins.property
    @jsii.member(jsii_name="argsType")
    def args_type(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "argsType"))

    @args_type.setter
    def args_type(self, value: typing.Optional[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7f6a5592eb5de32e44b135d23989807949590e257274420bc2cbc32a481b4b20)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "argsType", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="endpoint")
    def endpoint(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "endpoint"))

    @endpoint.setter
    def endpoint(self, value: typing.Optional[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7e184b80f2fd3510f698ff522aa2bb934bd04dab50cef1f0504dddca03cf4eb8)
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
            type_hints = typing.get_type_hints(_typecheckingstub__419879280b8f202a98c9a8b9c83a7ffdcf869962595952b4356c0df16ae443c2)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "lenientMaxQueryDepthEnabled", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="maxAdditionalQueryDepth")
    def max_additional_query_depth(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "maxAdditionalQueryDepth"))

    @max_additional_query_depth.setter
    def max_additional_query_depth(self, value: typing.Optional[jsii.Number]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__73348b7c04a3fff47333e243af255ae9832a51ce03fe3994a1803e3b27b95f22)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "maxAdditionalQueryDepth", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="maxArgsDepth")
    def max_args_depth(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "maxArgsDepth"))

    @max_args_depth.setter
    def max_args_depth(self, value: typing.Optional[jsii.Number]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5bfc5febe57d1b3446892e0e9283dfab6a7c6562ccc9e8301b7e7ce49e12522d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "maxArgsDepth", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="maxQueryDepth")
    def max_query_depth(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "maxQueryDepth"))

    @max_query_depth.setter
    def max_query_depth(self, value: typing.Optional[jsii.Number]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0082db5525ec4009a3aefe13efe88c96ccbe1026aceea14fa95026e03937cbc1)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "maxQueryDepth", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="optionalArgsEnabled")
    def optional_args_enabled(self) -> typing.Optional[builtins.bool]:
        return typing.cast(typing.Optional[builtins.bool], jsii.get(self, "optionalArgsEnabled"))

    @optional_args_enabled.setter
    def optional_args_enabled(self, value: typing.Optional[builtins.bool]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__98127d7e597d46492b3d6cf4261a6ce76a5b840e74fe0514cdd7d2625e101b58)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "optionalArgsEnabled", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="queryGenEnabled")
    def query_gen_enabled(self) -> typing.Optional[builtins.bool]:
        return typing.cast(typing.Optional[builtins.bool], jsii.get(self, "queryGenEnabled"))

    @query_gen_enabled.setter
    def query_gen_enabled(self, value: typing.Optional[builtins.bool]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3002fcc84c354156c13eae3c661634a1d3f729b04d362760c87839e9aa035cec)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "queryGenEnabled", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="querySplitType")
    def query_split_type(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "querySplitType"))

    @query_split_type.setter
    def query_split_type(self, value: typing.Optional[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ae1b6fa0fcb676d3c99a4901944aef555c9d685ed8a8cdcb6c0ad2f78ca6c094)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "querySplitType", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="requestMethod")
    def request_method(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "requestMethod"))

    @request_method.setter
    def request_method(self, value: typing.Optional[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__07e6997b69df8a2b0dff975a71a706001be6d0d6438708249e2f122ee7cf3381)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "requestMethod", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="schemaFile")
    def schema_file(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "schemaFile"))

    @schema_file.setter
    def schema_file(self, value: typing.Optional[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3b499a58a0003c8b742b267a6395612387ccd2d9b9cf55c15efff538e7181b06)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "schemaFile", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="schemaUrl")
    def schema_url(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "schemaUrl"))

    @schema_url.setter
    def schema_url(self, value: typing.Optional[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a48d44c10fd2b74902041a559a616edb43600ab1709037aad45f33aa6cface55)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "schemaUrl", value) # pyright: ignore[reportArgumentType]


@jsii.implements(IHttpHeaders)
class HttpHeaders(metaclass=jsii.JSIIMeta, jsii_type="zap-cdk.HttpHeaders"):
    '''Class representing the configuration for HTTP header scanning.

    :implements: IHttpHeaders *
    :property: {boolean} [allRequests] - If set, then the headers of requests that do not include any parameters will be scanned. Default: false.

    Example::

        const headerConfig = new HttpHeaders({ enabled: false, allRequests: false });
        console.log(headerConfig.enabled); // false
    '''

    def __init__(self, options: typing.Optional[IHttpHeaders] = None) -> None:
        '''Creates an instance of HttpHeaders.

        :param options: - The configuration options for HTTP header scanning.

        :memberof: HttpHeaders

        Example::

            const headerConfig = new HttpHeaders({ enabled: false, allRequests: false });
            console.log(headerConfig.enabled); // false
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__93d2dd3d4c5b9123a1a76a0555cb93ecd98e4cd4a5e37d3debcfacf3eeda39c4)
            check_type(argname="argument options", value=options, expected_type=type_hints["options"])
        jsii.create(self.__class__, self, [options])

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
            type_hints = typing.get_type_hints(_typecheckingstub__0a33b265388fdea1bf371cf3d31e2d813b550da405fc1d47cb058d0db2de8e51)
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
            type_hints = typing.get_type_hints(_typecheckingstub__31d37e54c10474c7fa28382aaed4eaf79d4c95a7d544e3ed5ec4419fcc29666a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "enabled", value) # pyright: ignore[reportArgumentType]


__all__ = [
    "ActiveScan",
    "ActiveScanConfig",
    "ActiveScanConfigConstruct",
    "ActiveScanConfigParameters",
    "ActiveScanJob",
    "ActiveScanParameters",
    "ActiveScanPolicy",
    "ActiveScanPolicyConfig",
    "ActiveScanPolicyDefinition",
    "ActiveScanPolicyParameters",
    "AjaxTest",
    "AlertFilter",
    "AlertFilterParameters",
    "AlertTag",
    "AlertTags",
    "AlertTest",
    "App",
    "AuthenticationParameters",
    "AuthenticationParametersParameters",
    "AuthenticationParametersVerification",
    "ContextStructure",
    "ContextUser",
    "CookieData",
    "DataDrivenNode",
    "Delay",
    "DelayConfig",
    "DelayParameters",
    "EnvironmentConfig",
    "ExcludedElement",
    "ExitStatus",
    "ExitStatusConfig",
    "ExitStatusParameters",
    "Export",
    "ExportConfig",
    "GraphQL",
    "GraphQLConfig",
    "HttpHeaders",
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
    "Import",
    "ImportConfig",
    "InputVectors",
    "JsonPostData",
    "MonitorTest",
    "OpenAPI",
    "OpenAPIConfig",
    "PassiveScanConfig",
    "PassiveScanConfigConstruct",
    "PassiveScanParameters",
    "PassiveScanRule",
    "PassiveScanWait",
    "PassiveScanWaitConfig",
    "PolicyDefinition",
    "PollAdditionalHeaders",
    "PostData",
    "Postman",
    "PostmanConfig",
    "Replacer",
    "ReplacerConfig",
    "ReplacerRule",
    "Report",
    "ReportConfig",
    "Request",
    "RequestorConfig",
    "RequestorParameters",
    "Rule",
    "Rules",
    "SOAPConfig",
    "SessionManagementParameters",
    "SessionManagementParametersParameters",
    "Soap",
    "Spider",
    "SpiderAjax",
    "SpiderAjaxConfig",
    "SpiderConfig",
    "SpiderParameters",
    "SpiderProps",
    "SpiderTest",
    "StatisticsTest",
    "Technology",
    "TotpConfig",
    "UrlQueryStringAndDataDrivenNodes",
    "UrlTest",
    "UserCredentials",
    "Zap",
    "ZapConfig",
]

publication.publish()

def _typecheckingstub__723dfe17ccb2865059396c64422ebee3fe43fb92717124023c900be16aa09fa6(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    props: IActiveScanConfigProps,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__23fe837004c918d019ad1d9ff46e4fc05e1d4d707c26b227ec48fff9ca49fb37(
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

def _typecheckingstub__ae9262485b3495d63b5010496abea9960dd3d43070751056147f1f81d280a07a(
    options: IImport,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b50ba4456d4b7757435923c5400cef22f2ae1e95ec3c24bd597e412b0d0b4fd6(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__eb3999b9021490cbcfd55533aeb28c322c6ab7849480982f15963b9e8034d66e(
    value: builtins.str,
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

def _typecheckingstub__8cd02eaa881493a20e9c51c5aa93e03d17b6c9ccbb71a6dac952671317d0a0db(
    options: typing.Optional[IInputVectors] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__51c10c9fb6ab81e903674e4f34ee3ef18f8180f08c9aa847b3a993e5f69a3d0b(
    value: ICookieData,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6e97ec86572c44846c9f6994d334e0664a150f2ab2e2472a6f3c139ebcef283d(
    value: IHttpHeaders,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__da3a58d64f8f1df5b146ba07acef8bf1a2d1f67572a50ac60db33a9939e298f8(
    value: IPostData,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__407c276df3ba7322af40923893a56b6750078fe6ad3ef61bb531ec2046f1b403(
    value: IUrlQueryStringAndDataDrivenNodes,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3ea3b6c8ba22594772036db26a1d90b958f0ec8353865bd36a14b5d755e1807c(
    value: typing.Optional[builtins.bool],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2710a4c1ff157460d3d51fed9f190aa29ee4fec96a8ed6aff3b71ea4b1a45f8e(
    value: typing.Optional[builtins.bool],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f7bd714d4062469ab3a01a61e4b0d072cd911a74eee184ff27d0d070380a4d9d(
    options: typing.Optional[IJsonPostData] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9f10fea9424c61881badd4c03e00d0cde227d8f05926f19fcc47400e3b31de36(
    value: typing.Optional[builtins.bool],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3ecdbdb392b5d3039240a2a5c088ba1de75eaf96a20889235c87722f0efc0b94(
    value: typing.Optional[builtins.bool],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__60c6528d04afe806304eab67b59fcbd27013f766e7b55dc577bf7659cf98a5b8(
    options: IMonitorTest,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4ec2bf7be2e1a6a400c0050d18a031d35e29d4685db736908fb682f50d1611d3(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0232c40c34a1a08a528559bb28c4392cb66edd3af1a1337f5cf909471f9ef7ef(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d316662cb1e3d3c02ecfa775ed3c1a7086fe851b8cc75f37530a19e775f64565(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__002197728fb3715405e8d942ed84a0e94cb86527c61cbf8abc4e8d3999b32751(
    value: typing.Optional[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__860f1b4f94e6162f6de6c6d8211b1d23c0c95ed7f6a0aecd37679af815eb1e9f(
    value: typing.Optional[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__99287435a763381828ba2c0438ad1898177718304311bfa17424468a33b583e8(
    options: IOpenAPI,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f16f5f25e9bb2409ddc4d89b08af25300d67081cdaf738a5853564352a54f29b(
    value: typing.Optional[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2988a6260dfcdc1177c6e94ad655c41b15fc2ba932a34abc5f845eb3001388de(
    value: typing.Optional[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__629b5cd81900c1bd79c3f757622ac3dc37dcf96a34eb42b1cb8f7c8acd5bfc78(
    value: typing.Optional[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e51e4398843496092d69a604c0f102154fb3ffd36e42812c77fd00e269465139(
    value: typing.Optional[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3ac8ec5b156603d835c2bb00fa4bdf7abdc68b9fff4be6024db36785c7f69968(
    value: typing.Optional[builtins.str],
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
    options: IPassiveScanConfig,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__98d408c2c5062051f60e28bff492d16546367c406232e99ef3c0c1601aabb0f2(
    value: IPassiveScanParameters,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c18b570068429b31a72fb9932007cd3929adf86bf8e414761911815af2d30f42(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__311730f720b5388c124c5d09045f0fc6bb7437256c588bd617d6b518905effe6(
    value: typing.Optional[builtins.bool],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0110420decb8f9c3946e99a1b826ecc7c5a2864550c1f54c099ba8ed36e94d7b(
    value: typing.Optional[builtins.bool],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__364eb3b49d38aa1278ae3b3bd97edf2bd0fdf11cd0ce92ead1cbb5ba3a775b17(
    value: typing.Optional[typing.List[IPassiveScanRule]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__41a310fa8ccd2b8a3839d98abb7586268af7c21df91fb133706f0992959dd295(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    props: IPassiveScanConfigProps,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e067afd320b53600be7f0c4ac781a9b0ff0bdadc83b2af89793699205cd532b3(
    value: IPassiveScanConfig,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a369d413b10f47648c36d198ae533607faede10ab301ea81fa93d124259720f8(
    options: IPassiveScanParameters,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7d7bdecc91f90ccf8054e24484b8c9a6fd2b1f40b5f7b31317bd8fbcafeba9d5(
    value: typing.Optional[builtins.bool],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e45b7b332bfc26a5522670c1b2b354214100826bd28023e138167dd2cf85efd9(
    value: typing.Optional[builtins.bool],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__846c438f7445432740e7111d7aee94ba6486ae123ae9ee657ef95fbcc6f7497f(
    value: typing.Optional[jsii.Number],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__68c42454bb94e6819bdae7999ea18797a10e953ea486eef6bfda75ce91c3e2e4(
    value: typing.Optional[jsii.Number],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__10f96ddcbf046a47d09ad7e3dc49cad8ec05db74d0fd64b30bb387642a81d8e3(
    value: typing.Optional[builtins.bool],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__93ac98e339102cd68a776f9fe4819d8c93b697c1b6e7e9316948979ad49041d8(
    options: IPassiveScanRule,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__afdc8855188221ace931a532c1f5489ae269494c65190e5062dadb39356cdb87(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__05be68b0347a6a5a19d98baa7a9398e27247acd7d4dff10e35155cda1fdebfea(
    value: typing.Optional[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f8da2b6c3807e7aabe29cfcc10cba4c3b395bae3b810824bd1873ddfb699ad61(
    value: typing.Optional[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__fd1027f82784b7836e3420252e40b7817c41ea2adb0cc30c8b726012909507cb(
    max_duration: typing.Optional[jsii.Number] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__de49989d8e7e1331f2b355ac905b276332c5f3d19c0302389191a4bb1bf1ac92(
    value: typing.Optional[jsii.Number],
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

def _typecheckingstub__bf38b1864c290187f86b9b468047ef42da4404f07c325c7fdedb111fe13c2715(
    options: typing.Optional[IPolicyDefinition] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d758ef6acd3f0901f9095eb3037e6ef9df3a52a62d500d733b880cfd95fb0373(
    value: typing.Optional[IAlertTags],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6d12470d0b422824c9b58864e9f0e9a8a2bc11e8f80060c8b6e5e35aa3afa6b2(
    value: typing.Optional[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1588a75d23e4a613b56e8877b7ff67b51143416bb33b38b4b967f309094329da(
    value: typing.Optional[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__18476c8b564c999623ea81a028f2a12f56c991afe8e306aa2b9583b938326ff7(
    value: typing.Optional[typing.List[IRules]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0b7caa40c2f337f6483bc12147498eb13ff3e34a573d21e8778bc54c6dc1c3ed(
    options: IPollAdditionalHeaders,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e9816da747828200e0cd469e343ab2772744e2b27a036bd7cf3cdd370467eba5(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1a7a431b085e4a138f998fa836a2696b0572a34a7b6b11a00b226fe9b2513286(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c4babefe72d93be8beb83f01e5585488024e3a19694d6b3dcbd481d31b628727(
    options: typing.Optional[IPostData] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f28a29365dc2f7cb147977280b59876cc30285949a8f8ddcc995a87a388a3948(
    value: IJsonPostData,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8ac87b25d7a9a276871f1e44bbca15b7bedd02ab258913d61864ccbcffee3632(
    value: typing.Optional[builtins.bool],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6b9a46ad010de4f08d938001f7afbb934a3e88d283a24d3ea25aeb0396e12bab(
    value: typing.Optional[builtins.bool],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__df99e80072bca3065152cc071cfd6e6318d6d5df37537a88bcab4f544fde90ec(
    value: typing.Optional[builtins.bool],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__06e443d723c93647ce20a9d35014c3b4e3728b19789d9b8abcf5e0390e4cd97f(
    value: typing.Optional[builtins.bool],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__729f7dcd5684d809dd04f4ce0788e25bd36cf29d5d73485d5b33bc54fe9f5853(
    value: typing.Optional[builtins.bool],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c3d81267406fb2aa6ccf20039eabfd98427283dec51869b07fa444047ce34482(
    options: IPostman,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8d1aed4ff6ddece407e1977f31d9ef5a45a3463e9bd4005ba050487866896573(
    value: typing.Optional[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c1b200c1ceeffffc1dc49d39f270599fbb63b89e4de83a853215f0f78f855b28(
    value: typing.Optional[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b8cf1950596db474221c1e0f10c6b1fd4892f3f5356091e6f3dd12b150e41c96(
    value: typing.Optional[builtins.str],
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

def _typecheckingstub__e006c9ca2f0b1a84fa007ccc42e191b223fad827745e93ce401aa8353953ba9e(
    options: IReplacer,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__597cfbd7b08edde963d3f7e2e2fbc20642ecc8d0200710a88a1f611d3f3b21b1(
    value: typing.List[IReplacerRule],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__25b36626eabaf1ac3470d5cd48b3908075fbff37ee33189e282291d817f2ec4c(
    value: typing.Optional[builtins.bool],
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

def _typecheckingstub__da41296778627d8ea25869142c9a5af37814c92a2ceeebd044b9ab5541c220b2(
    options: IReplacerRule,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4bd1fd4da74e3aa0ac009cf2ee0c37a81168bbf9599fe0bace546d4f2cc79c6c(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e39dfcd3351df507d625671675608fd43fff13bcc5b4c7af2d25858f770f0969(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f5d1f61da2ed6c5abab1b903a7e4fa5bd1acdee2829034c7b2dc952eac312071(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__18063198eed2467aa5b678b9356389bd3e9f2eb47c18896aaa03281d93e47c61(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__42d21c224b3ba5746669c5c6d54313613f4c90ac59cd40eb83152adb0df55d54(
    value: typing.Optional[typing.List[jsii.Number]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4aa72921e49acb27554030d6502efa33b8277a9f6a10e46a71a02c6ceb5ba4f7(
    value: typing.Optional[builtins.bool],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__57f606a1a0ef083c2c9b249e33073c1188c1df3108048b86946af0888e451bfc(
    value: typing.Optional[builtins.bool],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__198f2faaeebc7b6477b0f1e298d2b66c08ab2ec561fc977540e6f7b6b1ade2b7(
    value: typing.Optional[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__91225ae8d98ede25cf4d9aa8c4a8ddc3847eb3efcae23308f2a1a90b1181c046(
    options: IReport,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8dc4a062c616bb609e6702501e06b5afeb68080e0666a8bc1128db0c10ff6e2b(
    value: typing.Optional[typing.List[builtins.str]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__30ff975397f8106db0da742319373da1d38b9bbad0926820f4bd200ccacbf5e3(
    value: typing.Optional[builtins.bool],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5fb200b691d9cc5e4ab2ecb6a8c73bfe036ba438fc712ea570667219f8a911a0(
    value: typing.Optional[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d8817e70dfd59854b3a125bb5e4e7ed7fcd70b73a391d7ccd52c8704d120af41(
    value: typing.Optional[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__fca3ced659d95beb5e8a64d99c2cd8a4d512c193470097cf3f1d8d6616788532(
    value: typing.Optional[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__70f7476ca9462dd3127da48bde5a81810e8222709b3d9ddb5166db0a08cdc555(
    value: typing.Optional[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3d1b5465d8673aed3d035d5a7fff5f77c2a0e178f731324395ecefdf37e69737(
    value: typing.Optional[typing.List[builtins.str]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__06f2fd29a141b80145d1851a7417011f95fe4e72470865215fd6f9cde77f4ae6(
    value: typing.Optional[typing.List[builtins.str]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__eaaa75394d9e2dadb4fd192bfd19d59f1a2f1b05955ad36a4ce263d265686197(
    value: typing.Optional[typing.List[builtins.str]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8dffb7c8f803f0e5107d50917fdcb4855624ee11387cb8088f1ade70a06bbc14(
    value: typing.Optional[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2657cd3f94bce7e2206bae621f50b72b0e91734f5b3f214aebe25bb0bed67e7b(
    value: typing.Optional[builtins.str],
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

def _typecheckingstub__8c49b6f6a5b3d68fb766ea82d7b12e8e245995bf862fe5b4dc2d5c0cd5fb43fb(
    options: IRequest,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__97a247fcf1d0d3178db895a6b620654d91235a488957458909bcf0653d3215b7(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4f30543fd3a57b8a81924dad72dee21ee16cd915122b8f0a22a7e339d69fb6eb(
    value: typing.Optional[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__16b128e45486b8eb9a94c94d5bddba113d0da381508ba969267300ec9643f228(
    value: typing.Optional[typing.List[builtins.str]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__efc63cf92f6143bb916fb0b3d33c1b6ac38bb191552705afc07ba3a2873df2d7(
    value: typing.Optional[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f00de859401602980d07158f8b734d689e7c563fd1d69cec3d373740c634b339(
    value: typing.Optional[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__283fd6b407d89faaabb4ee0262624b5844ff7d02a45ce174a34ea1705ba819b6(
    value: typing.Optional[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a848ee2973ccd6fc7f9cc6fc90cbe7928683adc6898a6cd4182c1a00af22a75e(
    value: typing.Optional[jsii.Number],
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

def _typecheckingstub__1a4aadd701722f907fdac037f2c2d67d0ab3a966f5a3d8daa396a56b69ddd89a(
    options: IRequestorParameters,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__31721d47a8986ad6be735e8ebf5eedb82abf50f83eabdcbabc923f3ad0bc2835(
    value: typing.List[IRequest],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ad6c6e3908562f8989474133dd17ef3ef64fb51a875607f29abf64383e3cd158(
    value: typing.Optional[builtins.bool],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ffa61cadcffc518269d9b91a2bb57eb55acc662b22c11631cbc48393a7486aee(
    value: typing.Optional[builtins.bool],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__10b96736257b6840d28d3fb98a5522865703fbdc1e1bdc6f7995d1d717507050(
    value: typing.Optional[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f9f847168b277cd1f4a14e8576f40abc4a27395e9514c666872915db8515b1f9(
    options: IRule,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__17e82a53e07f2e144ccbf3bc6a5aac30c57378b1c1c36691bb6b103d907a1fc8(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__953d96b3dca961a2983f76efd2849b57430fae57317ba0e17220e3907314e04a(
    value: typing.Optional[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2fee20f04cd336978abec955aa412d274a02f661c39f2bc96a794b418054a1f8(
    value: typing.Optional[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__181f3f560fb6c8998c012bb9ae665fdda8fef0dbea7cc4c57494deeeeb5d8fbf(
    value: typing.Optional[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a56797b9c4452b42f38fac488a031d1d08450a0b960b3d1e8bf6541e4c772380(
    options: IRules,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__de5f3e28a821aca1e586a889c56d58913dbb100768683ea1872e70ee4dcc861d(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ae47ba16b69a561fd681f5206820318e72dd5759a9f1a45f1b81de86aa92b6a5(
    value: typing.Optional[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a47d9c5de1f7bc72009d8d63b0205c6195f393240f2461b3bf5fb72dcca38026(
    value: typing.Optional[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7bcc737dcd77f280e1f39f8467725523ab030a14599888cb37c5905d247f0ff5(
    value: typing.Optional[builtins.str],
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

def _typecheckingstub__ed8687282b7c108721e28e88f2ec05ac393bc8bab90d92ccfe631c73338e4468(
    options: ISessionManagementParameters,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a39a17a72b570dbf63b91b11954898391f5cf8276318aeea03723d57f415de63(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1e6d3d93ea8a8101f61e7d6ad433f5b0f8aed3fd4bab4f153b5bc55f0fbd5661(
    value: ISessionManagementParametersParameters,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e94b1681bb2bdc1d7db7bceee2d0ed30dbe2b19327b2e45abd1557991c655cfe(
    options: typing.Optional[ISessionManagementParametersParameters] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d273e2582e07d2196080f8e12c8b4d79c8abe02d0912cb648a57bee4cc5b55d1(
    value: typing.Optional[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__12665fa5b1f2e7f3260fa384731b424f47a27c1846ed40f812f4d99f810e14ce(
    value: typing.Optional[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b33b110d3eb11300ec66d8b62b6e41993825eb12a3865137793eacfa5ad90129(
    options: ISoap,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5b383cfbfb5883b5d0c0beb59c9bac2f0f807f8211b962f328bc7a170ad6d937(
    value: typing.Optional[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__633b2721deab084ce34469d69d353eb71f0b6a194f1101ddc90cce089c480b81(
    value: typing.Optional[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3e0e85161b0d0dfde77bd5e0c78792625f522d463f7d52db49cf180290f94da1(
    parameters: ISpiderParameters,
    tests: typing.Optional[typing.Sequence[ISpiderTest]] = None,
    enabled: typing.Optional[builtins.bool] = None,
    always_run: typing.Optional[builtins.bool] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0a61235ac80db5bedc24e18c1b8eb0ee187d10abce8a3757f620166d7c025481(
    value: ISpiderParameters,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4324b73ebb7665ab6bbfb839407285976a8cd3627b444d0ca378cc564782a102(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__cb59fb2d16adb2ffff72b6822a238d4aa67c426b849ecd7e58054593b1187fba(
    value: typing.Optional[builtins.bool],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c2f9d7414697e1125d72d483a96a0890e2b2252288924489418fe846a0e1513d(
    value: typing.Optional[builtins.bool],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0f9dde29c84c2346b8648f6e9f95008056249873a4a4f900aea1ccd8263e5298(
    value: typing.Optional[typing.List[ISpiderTest]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6506c074278e8773057878ca0fc589cbc6136d12acec5c6f0f44373a26d94713(
    options: ISpiderAjax,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__90735e36532ec21e5bdc711740b4606a93a3f4a796d18b6e5674fae41ca4642a(
    value: typing.Optional[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__cd4997eb4e569ccbbf93f8da7c4a2763f010248ef2f08588c7ff8852cc5d1d11(
    value: typing.Optional[builtins.bool],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f950d60e70b9ceeb26a4843ab8172d3e6bfd9396de8f7d393de1f8903799d640(
    value: typing.Optional[builtins.bool],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__05f8179260f82e5327f9bbe38f0eca7a45a60da3e18dd1cd7311588b9ce1529c(
    value: typing.Optional[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8b1ff7dcc6cee09402188a4ac4edd1855cf07482c91500176eae42f8f458083e(
    value: typing.Optional[typing.List[builtins.str]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__01303ea5ef448901c27f7310b2f0b90431f8c7c172c741cd795b80e9741cf24d(
    value: typing.Optional[jsii.Number],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__83b49a7296b832e33376dde67d4ee363ac0614ebc3d354e8e853d6e11a02abe7(
    value: typing.Optional[typing.List[IExcludedElement]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b0a211170a67af76f770912bdbebdd9417ca9794f4975984046fc56de074ee6d(
    value: typing.Optional[builtins.bool],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ca665436d4dcc4edeb8c89376b9a3d94a798641eeefb3fd974728c68af15e4d0(
    value: typing.Optional[jsii.Number],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__795b40d0b3524a50cda3e4bfc2c4a9e09c7d290355687339874410c807219250(
    value: typing.Optional[jsii.Number],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a49f64a0f6db8382bc1f849ac8341a200a29791705d9157bd73531804155b94a(
    value: typing.Optional[jsii.Number],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__30317e766ee20c3a87eb674d7078eb979ca9a7096939cc76d8b28dbe7b901a01(
    value: typing.Optional[jsii.Number],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ac2bc68565b46bdbc86ed786150dc9cc71c31ef5774dda3e90eef94e9785e742(
    value: typing.Optional[builtins.bool],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__74ddb8c7350876e6a5eedc3a3b03244b010a244092d6c1dde00a16fb6385969e(
    value: typing.Optional[jsii.Number],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f2fcf65e9963939456089d8c6007dfcc5af10d3680d107f1be30534a0105764f(
    value: typing.Optional[builtins.bool],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__852ea5dab0f0e8e8e9b5e08fc330a9579e285c9d2335d8db5dc501d21dd07476(
    value: typing.Optional[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3edc6d479fa80659ef9c68fb7b7ef48e62661290058671a36bfef64d21e5b412(
    value: typing.Optional[typing.List[IAjaxTest]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5a99d4fb49af8269eabcd126a9e1d57fd154ce65d9128b3c05a81b4df3690674(
    value: typing.Optional[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3041e7e253db69b234cf9e6d55c48bd41e28ba56b00db1089d642c283968853f(
    value: typing.Optional[builtins.str],
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

def _typecheckingstub__4391b68e7bb86217de43b834689fd90d8aad7f8f1287b3a539ca6cc736adfb4e(
    options: ISpiderParameters,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0fd869a9a5038cc18e3f8a2fe1e3a70fc2d8870ffc7f3a4ef6eb6619eb9cade2(
    value: typing.Optional[builtins.bool],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__dae6c8142a31d205a9ca4d09ec5ed0019e739a42b14874ea18094338429fc7d6(
    value: typing.Optional[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__85073f4761fc0e93f0192aa82a6b11a417186633a915cc53f95556a8c558d205(
    value: typing.Optional[builtins.bool],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__41a43f827f0b9aea3a11c2599bed7c0e95f276aac7d3c2ba2223e39b548cada3(
    value: typing.Optional[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__25367df58f86766c418a1d835a6068d943082c190ff36e386c9abbc34a406e7c(
    value: typing.Optional[builtins.bool],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e771cf3bc25e06f7a906b0167a820e7169888eb714d416649f33c993b3b8fba2(
    value: typing.Optional[jsii.Number],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c5aed289cddd7d3601a0d183370eb86131b1ab5285ea5b0478750d5e68450292(
    value: typing.Optional[jsii.Number],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ca47d0002343427f3d99ed8c5c2f2432456bb699372325bf6bd01cf057c2a032(
    value: typing.Optional[jsii.Number],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d7b92e118b2870bfe05cfa936f9545a692c09cf08f9f67cbd800fe3e319c0516(
    value: typing.Optional[jsii.Number],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9d8b7eabee808ad29eff99f5b5244ce159d59c9533c6ea46d64d7fb2b874da74(
    value: typing.Optional[builtins.bool],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1432d4771f67269f498f0a7ced00eac2d7d1c7a55b24bdcea6d9724ff3e734a6(
    value: typing.Optional[builtins.bool],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__60c8a95732b077642e216e00a18242a7be38b2cc7c14d28766cd03425e341d0b(
    value: typing.Optional[builtins.bool],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c6efb3e309ff91b0fbbdcee93097f3bcee117c640ff2f67a1ac32a5ac444142c(
    value: typing.Optional[builtins.bool],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4537342edf36ad481b5204f98a8316d599f14056a9802b11c16a17dc5f96ea15(
    value: typing.Optional[builtins.bool],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4f296fbd7e9fafa7f9a0cb3c7297e4b40c30face29664cb1e2f4065f7e3cf571(
    value: typing.Optional[builtins.bool],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__976d99258dc9506fa0c0519ba120f1a25263b27082bc40eb4196d58cc6066b09(
    value: typing.Optional[builtins.bool],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__86d755d7662363ba7e447aae709a5c84c7ec9c1eadbb1de97d4d233d30eb32d7(
    value: typing.Optional[builtins.bool],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__17d507b62359ef4c23a7cbd07fa8493e744ee1b944cb80dd93c6ee5a000d1078(
    value: typing.Optional[builtins.bool],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6c3816a71032eada18d0a8b5992af324e72e030e1f99aff7dfc4a18deab66eb0(
    value: typing.Optional[jsii.Number],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1a652c3000c21192999c0364fe03fe1b7ed98117703be9d4b3a2a84905c17fd2(
    value: typing.Optional[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ffbf9b64500b4dbcff62cc4d02eaef2b9e8d9b7775e69a10795d677e628e4c12(
    value: typing.Optional[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__fa1ac54b486b899737c1b979292cbbc115ba35f27220038c8d39895e4fd07a05(
    value: typing.Optional[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__576c170c601ea46aa887ed94f5e04f3bf674a900b0d860cd9e126ae278b7586d(
    *,
    spider: ISpider,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3a1f2eae44471c9abdd1124b9b6806f6c2b78e3db066b041392e80ce33870cf8(
    options: ISpiderTest,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d9586b08db0cb2f8f3a7e184f0fe4d1a033f8f5fdb673856574c38759783d39b(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__061ce35b2194e36d968c55160fe284d7e83ee3c0a0c505dd61f2a012f11a220c(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f5510386857c87c1e37a24c8962737682ea94b966d600dbfaae2d3f07ecb958d(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7186f4c6d434c2ed02979b2af703a783ece6f332013f8214f8abb10969a5dbb0(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3cafb9afed7e19f9ce009b9b0130eefad7cd030469430d327ecf904181205990(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e987bbcbfa5d38f9d8fa94e5aaada6b60e9aa59545b03027368f7a5bd0dbcf1c(
    value: typing.Optional[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e589527410d2357500bfcbb7f277942e8f5f02222bfadf865c5c4001ed511d53(
    options: IStatisticsTest,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__58958cf7c96b758cdd2f74cec7ce583801c7f816709979b47616a3f299c0e9d7(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__278f706e3198da5e4775f967987fab712de1a7b3b21c37f798b9b4d42ddd34dc(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__87ef38e699436b7b524c614e60c018d63bd7dee2dee26072f698b922fdb4c709(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4507281eb4f27e710a2d232473e255e1b001ed8473dd7adf065586073f4dbc01(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__49bde5877a0212dff5bcaf581230c46ed026f584ba5c38f9f3b5ee2fb1c98f11(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7bf447a6c70fd114b5cbd7113e33f78b640e209ab31e293b91d3e80191c65797(
    value: typing.Optional[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ad028245822ce269ceb3dc78639e47a019760d4bc69d15706b41685ac58b64aa(
    value: typing.Optional[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5494039db6148e623ad24e6adc6169ef08d2797b2a3acac346c78c6ec27ad689(
    options: ITechnology,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4ebebc66d4836f0ee5854f9245c982527ea77f1a08c362219ffd75549a2e2cd4(
    value: typing.Optional[typing.List[builtins.str]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__bfa64ef4dac0b731f07ffecc3a6c3da24adb146bcd2d3102d34c657dd676adfd(
    value: typing.Optional[typing.List[builtins.str]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e6700e17530c3abecbcdaa6641d4d979f1ce7ce263fb101a9e569de9ffc0df91(
    options: ITotpConfig,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1d74fd06e313fc89902f4bc4189f3e43d0b03894a5d6e8a5c32b0bf8103efa35(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7e7d7e7367b960774a9a5aeb50d7517e9042bd9a21f7bf9407dea944fdde209e(
    value: typing.Optional[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c657d3d1a403c3a1eb438a32aeca1e3eb3b7bfa208a124b8fcc43c33631cda59(
    value: typing.Optional[jsii.Number],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__96ef8c9ea378c63c2483450d231d56d59b1aa01c4f7f6c66d910c173bb14351c(
    value: typing.Optional[jsii.Number],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__042343489372ee0fd16a66fd50d885080b6de2b9cbc402dd061e7c609b70114e(
    options: typing.Optional[IUrlQueryStringAndDataDrivenNodes] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__18be073c4e552a81e292ace44da8bc644d8140ce1719ca95a8ade4efb8faecfe(
    value: typing.Optional[builtins.bool],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ecdf0e877818988de2a5128e8596ee8cc5536ce64ee3105527780730d23e32ef(
    value: typing.Optional[builtins.bool],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__bab6d3429fbd401c852f614b582393df397bd0147a5652e03456a34fbe3ad9f7(
    value: typing.Optional[builtins.bool],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c26cf331e9db56a247e2d822a8e1cdb74dfee18125ecbe885ef6b0e0c0b31e50(
    options: IUrlTest,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__891a1056d9000fd5477a227d9e099b4f2773b5f4de7c19e01a344247a7fb7b14(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c1269ccde197633f1a58095008d92acab8c4caa3064f1bbf1ba981711bde44fd(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__530ccae163083c6ffac50351f23a8a1888f1addd8d7d0029793a12e74e54caa8(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3c66e3d7f0c3d28465d757996e8daed3878cdc216c58225d620d72f39bcf105e(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a1b01cb76aedacc62fdff562481308c183a867343e9db739e41a6be34c915a35(
    value: typing.Optional[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b97ff50575922661f23465f4090c5154bb1bff373df806f0697a64cd132c1aec(
    value: typing.Optional[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b323cad760e16dd2cef6d8ed41bb6bf97115eb58264f3c66d951f8ff9c64c2b0(
    value: typing.Optional[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4463f02bfb65887a0d6e5282abfd67450bc93c6e07bb328ab734c34956d49c3d(
    value: typing.Optional[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ab198d371591181d1c6ea4ba65601ec2f71f9eeac2d8a8b64aedb7f51a140e55(
    value: typing.Optional[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0bae0be71d8af1cc4a753a149c58079a33d6db14df7e51d5a6ef5ac6d6d70d7d(
    options: IUserCredentials,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5cbd0c7670a7374e8f835ecedeaab78244e883a15293b439945da2b93439ab77(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2068ffb83ce0004dc765e7f18a21ee90aaedd8208b18d346add2d3085d4596e1(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0c04ddadb5f51c764fd86d16dc70d039e8b5f4a57f778dfcb8b79526aba843ed(
    value: typing.Optional[ITotpConfig],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e8988d1177722ca3b6f00f51e9031d89ab9f6cd69685393453bbed7e814b9aa8(
    options: IZap,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f4d7049f9370e6aed7a28e6f59caaa91b8c20ec5f18bdc7d07c91fb09d25d810(
    value: IEnvironment,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6a77f47f4f857b419ed4729dbbe1186a06f8280e56830c7c6185168cd9931854(
    value: typing.List[typing.Union[IActiveScan, IActiveScanPolicy, IActiveScanConfig, ISpider, IDelay, IExitStatus, IExport, IGraphQL, IImport, IOpenAPI, IPassiveScanConfig, IPassiveScanWait, IPostman, IReplacer, IReport, IRequest, ISoap, ISpiderAjax, INewType]],
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

def _typecheckingstub__e4d0720d8d86c42c59c0e1e3253e2918128a5cf003a2f3e5c0d2c44588d29d83(
    options: IActiveScan,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__14fd47c6f7d3371930d23da4375ed97989c1839f55f24e1b7f78e096e41582e2(
    value: IActiveScanParameters,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7d2c602860a79d8299eee78d01eebd781c7cc86cea4988791faa4ceca76566d3(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2c68503f194092162b95ac79b1b5d0654ee1d632e393c209e92d72245a9e5b3e(
    value: typing.Optional[builtins.bool],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__614f60eb367c0c2a239630d0c38ac7a0bded354b5e25fe58dce7f50648186a63(
    value: typing.Optional[builtins.bool],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9dc169b39f6653fea9b10bb336bb93678b0acb50e6336415febb266baa88edc7(
    value: typing.Optional[IPolicyDefinition],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ca23190d78d2919234c733f19bc05216a18406399e366571582fc581ddd3a04d(
    options: IActiveScanConfig,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__aeb5adaf84febceae2fe2bc5119099b6f07430e1dbbe133eb441179ea458dc24(
    value: IActiveScanConfigParameters,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1c5a5d8977784df7424847063e18e470351b7d1dfdaa97f698325d15750f1c0a(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b1984e2cda7e3561d8bebf4d718f1df3f33b47779ed4d9474c6b40564caf5128(
    value: typing.Optional[builtins.bool],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b1908729c1443f0d204f0b57ad5113d421b2a431edb6e45012035f4f7fa74edb(
    value: typing.Optional[builtins.bool],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__412bb64daf3c0159397bf84993712b4d8e9aa0005303cb1a0b196e48e9a6e5b4(
    value: typing.Optional[typing.List[builtins.str]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ecafbad3fd2176b7a57e35033fa35f3b2017f81f963253c90de8f10524c1f7db(
    options: typing.Optional[IActiveScanConfigParameters] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4d6b3b971d10a756119e0023ceb28d9b655089b11e47db67658c1436a207b21c(
    value: IInputVectors,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ea35170cf4215bbf83faf7bb216f92240d508e48ec6d133b0695738f4059990e(
    value: typing.Optional[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__160db386ae533c04decec7f288fb1a386694ecd9227ae3cf1e0f550ad0312168(
    value: typing.Optional[builtins.bool],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__00eca7528fd3f90a90c5d98399c4214db1fb0a5f4246344b5aeb50d9fbfe9b91(
    value: typing.Optional[builtins.bool],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5a08c984fb96ab5780e33f9fe46ae51da68bd4f9eddd325c7efa508e0e18b1b3(
    value: typing.Optional[jsii.Number],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__57462400a5137f9a8bd8c897512b220e8c8a775a5709be647ad331484da08324(
    value: typing.Optional[jsii.Number],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__64fe248bf70bd14398d898d7ac2f469be2116e8b0e3b9e069d8e7cc6d988b564(
    value: typing.Optional[jsii.Number],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c97831594f25a0ba0d3b7a332b320c00006c0204eb90d8b24432909123b98eae(
    value: typing.Optional[jsii.Number],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d39727b3e8ac31f020cd3342d1416dadc9e045a358440a26a764313431e8a0b0(
    options: typing.Optional[IActiveScanParameters] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__fe5eae05347518eda844f48f3125d5f2a835431d28d06348ed614c4fdcb69dd9(
    value: typing.Optional[builtins.bool],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__dff11e6128126cca346efa60642819902ddcd957df1082b95c33d14df28d591e(
    value: typing.Optional[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a01b2c61e6a4558dc6cea511736d1c7763795c5e02db842d7c5e68e0e8ea068b(
    value: typing.Optional[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__cd68262e93a5b3502d24f0429c0710d638dd7af80b162691770404dbecee7b0d(
    value: typing.Optional[jsii.Number],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__fa44794f6d7b2c85fba14dba4a745d154f81cf54c2e3018ef172e7d2896018ef(
    value: typing.Optional[builtins.bool],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__92ba2f6b88abd8f77e9cc9d3c04228940df79ee9d889c4020cd992a097e5998c(
    value: typing.Optional[builtins.bool],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7843a26fe3b03bd28235b1ebc021309e24ee3901d80c0b569bef58d5ca20ae50(
    value: typing.Optional[jsii.Number],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__dc6b7df0214c0ec38aa3c55ca538716d217766ae7f6e7dd3d55057e6cd3ad89a(
    value: typing.Optional[jsii.Number],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__91f3bb0b2bf8ace80e0066f9984f181768eb0496465be138d26fe140798ed527(
    value: typing.Optional[jsii.Number],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a8ebd573eb4b5ea885e8afedfd67f67e2a97b94e900cbb5f34229d70f2f91fcf(
    value: typing.Optional[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ff6815f4d66c724de6d394dbfed78abcb8b29680c85c3a49b27f902ced6223d1(
    value: typing.Optional[builtins.bool],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__cc18abb2a154ad644ec55859205b4b60ef60bc3d4afcd433dd160ef97ee1ed7f(
    value: typing.Optional[typing.List[typing.Union[IAlertTest, IMonitorTest, IStatisticsTest, IUrlTest]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__aafdf0cb385f3824e2e2994f55af4e713d66827ac9e7d32ab46d6cefc10ea258(
    value: typing.Optional[jsii.Number],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__49cc78e5507a1a40c571b97e518bcbd1f435077f22fc2cd18d7dde324456b77a(
    value: typing.Optional[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5ef8a49b103ceb6cca0cee614ef20f7539459cf23d3f311f4e0258d2631d9f78(
    value: typing.Optional[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a80af27aa5eea08ca6e95581160a422fd9a3709af156272a86c7409df7aa8740(
    options: IActiveScanPolicy,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__594a955ffe1c41d834041f98154c328824be38ab69b6eaecb5b0c785d3d34fd0(
    value: IActiveScanPolicyParameters,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__28415b318e2fd90ea1b1c240526adfea64ef34b7046408555978fbe90c774958(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a450984d1535a0445fedd3525ca5d483fb59cdd49fcce581786180c007cf1b55(
    value: typing.Optional[builtins.bool],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__12938ef5f26097b25cab621a708d4ac8db768d16c71bc372520242172527a67c(
    value: typing.Optional[builtins.bool],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__70c8371a279367b4433448a0352d077e581f0fc600442e3aa028683ce992f6f9(
    options: IActiveScanPolicyDefinition,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f807d237d2f2aa67b01d927c020eee461bf10ab6348839e95cb5259d7f21878a(
    value: datetime.datetime,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f590a204c82e8ce44064a8965133173b5529e15bfb0e0395b6de019ef902f0a8(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c82cf1b96694a497b30d69002d0b5db5b395a678709c41f0d05c07a435d29db2(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ef3c2ce9e5b63cd4c6ee0651c486d98419ad952804034792c0144bf09348c166(
    value: datetime.datetime,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5528f46763f2305d0d4ead5168e7b76b0cb0b6e5d49df615d6fb3849e603cb88(
    value: typing.Optional[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ebf4a01e118d83c76b7176071f5a3e7d887dc48c6eaf81c147e57e06a4d5cc2e(
    options: IActiveScanPolicyParameters,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__62d765d84c17fe61d71ebf8e21494a2c1178cfd9d768a8b5973eed26b7842f07(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ef93fc4562f155c738fa4d6c1aa91513a8a2480b529c29aacc0f0c4977f8d1a9(
    value: IActiveScanPolicyDefinition,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c6ef9ab1b115cd009f22eb685140974a7f97fc6dc0e50f0df96bf4cc8cd6891b(
    options: IAjaxTest,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e9516d2a49f5b1c3f7a6537b906b2a2edf310620c723cbc5aec78357a91b0c6d(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__dc850a8121706931fb16b6dd9e97c84fef6ec56f9220889d9a8068e75d0ecc29(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f66d3a9fb76ed62982365d2b8580a6e9c417f4f5da1a70aba5213a40ba90cf04(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__cc97b3eb313afaf6a6323abe3e477fa366c2d552bc17547a64473c93ee71bcaa(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5f0dfcf86651c1d90ef4752a5e1592413bfa3200761027a5a62e4123715a5427(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8c7609fb668ad10cc15cc469fc2d5ca54dba8a7fc1dc57e40b3b0e6d6757bc1b(
    value: typing.Optional[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2fb23318a5c05e0201f11704a3048ade67dc076741280a9081033dfc46febb76(
    options: IAlertFilter,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9379d76457ebd34954e12578150052add41db521bd75820248995f66c5341dc5(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__134a4d4cab7fe123ab02010f0e38548765c86ab45504eb66dba033a81803c4b8(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__14241304945c9b667f6add030d3ff79906606d7d2a1bf3be3fb1c96bafe6cd9b(
    value: typing.Optional[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4b081445f35fab2b9572d1f49ff01ca45f6be8f34af6fd571cef023b8c7c26c3(
    value: typing.Optional[builtins.bool],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a1981c6a02b74cf993ed0f77fce68f0b08ece07e8e963220da3872089cec8ce0(
    value: typing.Optional[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3cab09ed7d5eb1ddf5a1c66bd2cfa6c561b9b43f4e8f8a6a94f998565f97d80c(
    value: typing.Optional[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1de266faf7a847086a6fbfcc9e40f9cde40560d633ce6c0e43c6dba91bde5ce9(
    value: typing.Optional[builtins.bool],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1d654a80de82e2e0f8ffeb537719880ad1dca06365dae01cace70af48a6f2238(
    value: typing.Optional[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__fb6a2df026a5b62af10fcca71dcc77827d4d5f54d48d0342ebc16cf8da901b7e(
    value: typing.Optional[builtins.bool],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a695a6a45022afb056ba9af145e8fbb5c95683eaf9f3e495745d2d81af330b43(
    value: typing.Optional[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0c7ae79b646680d85b0a43f8673fada25fad2de89a89556cb2268900f127007d(
    value: typing.Optional[builtins.bool],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6e29e19af954a95bf4959b058d0f5fc55e5ce8c00c52b91cc87d417d5671193e(
    options: IAlertFilterParameters,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d048d7c034ddb3eff66f305e8301338734d8e569cf38f2b6a35fd07ee5ea8d57(
    value: typing.List[IAlertFilter],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3de99f28c0ce43a37b1b11f46cd79b6ac9db465e905884e1ba1616db3ade1b34(
    value: typing.Optional[builtins.bool],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__09d54d0bdde2e854061990c81bbec5f00f106fc50748b1c10aebe5e708ea8257(
    options: typing.Optional[IAlertTag] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9e86415242d7589ea703d9b0faf348ab54d8b1ea46dcc02f9b9dba45c8503c90(
    value: typing.Optional[typing.List[builtins.str]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__583c04532b41febfbde1de15b973d2093b1ac3e49cbc9d5685eaf6ac50c0b5a4(
    value: typing.Optional[typing.List[builtins.str]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e747ad2981d36642d317ac6b53c0042d8e0147be53f23b1221728f96c4bb867e(
    value: typing.Optional[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1edf6bfb32200e381492349baa817335994f538ae6754054bbe6afeeb2fc4824(
    value: typing.Optional[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__012a77be1911ea01e692411edd3f710b38c65804574bfb20dd997e462cc2fa7e(
    options: IAlertTags,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8bf6f0d1fb4cb5423d52a70e5db91aa05a85dc25ba68edaea29d6e02c517bccd(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__96004500518890dc200392d1f8e64595da4616bfa4d8333fac9eef9f4a6dd12f(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3955be8c8fc82f2d142a19f39ac0daa2482f645fe882dc9d910fcc567bba30b0(
    value: typing.Optional[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__35f5199af5e98aa1ec4f109ec97c81b93aefe195379f93d3bc1b873b1b61c21b(
    value: typing.Optional[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0a1eeee781bae8d8ebc926a0a555ff1c4a9090dcf227a719869a7ef6fa1345c8(
    options: IAlertTest,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4be3d48b847f5073f6f869064e4b8f899ac6b75da737c3b9cc979cf78b3cc3c2(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ce93bedb98f55c44ff18751009ecb87cf63e58d879a29787eb34a0db4506f549(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__77dffb9ce57ae71b9eb1c56b4cb824297c7f4644fa48251388975933032ae3a3(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b2b4152c08989ee0e811ea1c6553d4e1bd77e89c78fd4fb0d2724a2923e43599(
    value: typing.Optional[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f310c064785080dd019f1709b5db5cd1e02b67dd8adad0c4bce11ba75d57ed8d(
    value: typing.Optional[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2ecb64911b6561c0e290006d6fc29add7d3207eea92a052e32f73d82f1661124(
    value: typing.Optional[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a4d98037e282bce55dc4043ea9803f40d96f714e64619b5448f0d32ae88d2c94(
    value: typing.Optional[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ee9c31d12de60675c2cc1a60fd129660444a782abe527a2748ce1efbaa3e75be(
    value: typing.Optional[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c1ba61dfd78788d03c0f7976f8e43a94f8699ec6e181193239ef5674787cad43(
    value: typing.Optional[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__dbe8013c7f946a1bb6f2033fc4a9409d61817d82aeac08affef0929b0b42af56(
    value: typing.Optional[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2349e34dfa71825d4c30b930ef0fdb9a06bb4a0a60b6a6a75e636500d866c133(
    value: typing.Optional[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__fe8362b544297c08bcbaa0d298e2c418c1b5e13a66129cb319029e72a175ed43(
    value: typing.Optional[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d46e5cc6be2ffd00ca7b9cfee8cdeb7717418b468405cce7dd1b618020274259(
    value: typing.Optional[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7d5051de2cf23a10abe9405eddb4c76ea938d4645c31f214e5db739deb0ff2bc(
    options: IAuthenticationParameters,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7d284f5c1079bee6a8ba4724bdbab2a7ce009375ab9a5a450f97696be7677cf7(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9a517c037186b642234018061e2de7f341f7c16a0516e2e4bad6a97d9ff26a23(
    value: IAuthenticationParametersParameters,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d59bbb0e600a0254c50b5b1ed1440acde1b39226c363f394566f267d8dcf81c9(
    value: IAuthenticationParametersVerification,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1329013a27a80fdbf8dc450922289913970047c12730babb0902dfd019eef346(
    options: typing.Optional[IAuthenticationParametersParameters] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4cff7db9e6ff1590f96c938c410e2d61dc745d12d9f62e18bc350005a8a3f4b9(
    value: typing.Optional[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__efb1245b1009f2d8b2623cd809e3e940ec18c6b36a57c032e79d168daba07d52(
    value: typing.Optional[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a68756cdf33a5b291896b57d83687667b38f5735c29d1cac4091a317c394f51a(
    value: typing.Optional[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3df07182ef641018e49cd4ec4130fd5dce2fa4dfce14c1290b01037fb070ceea(
    value: typing.Optional[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9e966666d098a9b5b13a058b9d60b1880ed3eab6e5270b678086a1879d331820(
    value: typing.Optional[jsii.Number],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__486380ca0ede2e15539c5dc85e3431c883a6f515b1c16f293074e057c3a3c903(
    value: typing.Optional[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ac61435363b7cfec8adb42841d50786a829f2ad3ad2fff1577fb8084762364f0(
    value: typing.Optional[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__972aad6e7bc25c329b2e48bdfad7d5ff8adace87bf5ab2e3b5461d1e229c3320(
    value: typing.Optional[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1e38456f623c4a1f27f5188f882898c801f9c87a2862461a203ebfd7a842532b(
    value: typing.Optional[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__78a9626ee3cc0a454b4ab39695b03419001265fe4f7a890ae2bfc74d9a38556d(
    options: IAuthenticationParametersVerification,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2cd3a437dd46c186f07054ffbb1b9168ec83c9dca2f5e8cb0f67442f8c425c63(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1d5edd1c38fe34db8179d9706c65abaefbc47f4d7fafce4d55c24c41a51ebc90(
    value: typing.Optional[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__cbbd34e680286d24b1a3b58bf878296162546817485fe838b692aebf03f79e3a(
    value: typing.Optional[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__de06133bc37f5f00cdf4684f99ccc783c5bb3ae4a30a8d89faa09fa0a4747f08(
    value: typing.Optional[typing.List[IPollAdditionalHeaders]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f15a2849a755a31839f457a582c1e34f7e1220ac987ce302065a8dbe8f5e77ea(
    value: typing.Optional[jsii.Number],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d5a3d7148fee54a04ba884c326be849de398c22f6ed0bebf1444a9adca9b9792(
    value: typing.Optional[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__13e202c31a9b86659259ad91c593fdf9724bd156dec73bde1eb7c06ec5849c4d(
    value: typing.Optional[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9efd98dc9926dc87cf409f9145679c8fa21f85867d5f5b3f9e33998084f0cb1c(
    value: typing.Optional[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1d5809817c8b283f3d2b9e6def3e5982ded3e1c6371f4c366ef28ba790581161(
    options: IContextStructure,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__737294269ace93aab91086394ccd2936c1478415ef00eea71b56315d6b46e240(
    value: typing.Optional[typing.List[IDataDrivenNode]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f245e60b36bf0087db3bd3dba2312eb8a9ebf8d154f4dcafbc7de1f2286d585f(
    value: typing.Optional[typing.List[builtins.str]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__cf097ec1b59c6d6305e9d45e894285013f6bf2d08206715e86d85dcbbe31fffd(
    options: IContextUser,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__dec059b7c453dae8078bf6f80f76f095b11b6b2f2e566ce64d7e6dcbed26a293(
    value: typing.List[IUserCredentials],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__28fe30eb403dfefee7590b8887610be270bcf1c7368d92022b798320d45842fa(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8794d236188a85c4bc7f0ce3352c13c921d0fde1b9698bc77c3d8273c5f34daf(
    options: typing.Optional[ICookieData] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1fe3ab94daa513978836677c7a8f4b7086044de841d3e8a5c4a8c97e4668971e(
    value: typing.Optional[builtins.bool],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a31f4fd01751421e887e4a1582261994b16e27810dbc19953c7be9ea41a4c4c8(
    value: typing.Optional[builtins.bool],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f4acb1d9764609ae7ee038ccd9d42ce1c89f3a100f2418a8a59afef323e50ebc(
    options: IDataDrivenNode,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5620b63226ab7448ee63f17886daf5233f5e02fb6df253d92a17b495af930a41(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__24ebd6d4c5b0e4e95b132d4a109977789bb7300a4b32156af4127dfedbc47643(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2780a37bffa1d9d2d30e73ea731a4526e213c8a4b2abd041fc452c9d4e9ece38(
    parameters: IDelayParameters,
    enabled: typing.Optional[builtins.bool] = None,
    always_run: typing.Optional[builtins.bool] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6a6ab60a1e6442bf9deb7aaf8f3094a23050929ac95611e42e834ffe33c765f3(
    value: IDelayParameters,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e37b6069dbe3969d7c6befc8d3fe6eb27b6a9dda08199df93596557406f9ff86(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__76d116649c51e592f54735851281a84a860ed11b2cb2a5577cad79ad9fac2c6e(
    value: typing.Optional[builtins.bool],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8dc6a4b56e86d0ec225279218c8556d462b8d071dc6dba85142324dd5e48922d(
    value: typing.Optional[builtins.bool],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0cd44bbcd4f268acf5c20a21d1b7f1c005f607826b14c51c3c2270796fdfa706(
    time: typing.Optional[builtins.str] = None,
    file_name: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__14acebdb3d15fcf3560f470f2e10d14cf040f0278a4671c308f62d35394f9ec7(
    value: typing.Optional[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f1c259dde8eb3267fb0a349d1d77917bda5a6b9865a2aafdbc5e1961517f78a5(
    value: typing.Optional[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f56dcf0632d6a6d4523337e4a9909e1c879007047e95a24e709e93b07adf9139(
    options: IExcludedElement,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ea14f607b601781b70715f3ce34891cad569baf33a4c1462c17137564343a03d(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c86f29d0b3e08ddae791e45dafe96a41a53f3bd0af8da372817588faa4ecc11b(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__53a85c348d4e2b397b03077283bfb8a98679b1ce894162a6f018541f20bea7a2(
    value: typing.Optional[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b05cdc983b6613cc828db56497b43fd0200b6745729dae03f989d14e6e6e671a(
    value: typing.Optional[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__56c1a2a8ad8301594d8d327672d1a517203986cbeb46529c44d19020a687319d(
    value: typing.Optional[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__bbbe78e999f173cd67d253fc797661aaeed67df12ce691112c7871cdbf154f13(
    value: typing.Optional[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__48fdc6d0b23cf2198a171947ed6eef7fdd40285f6717c689b55a66f564fbe97e(
    options: IExitStatus,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__dd550c6c36f5b08e7ee97974258059bb198eebda7a7a9b5cee1ab2c711117713(
    value: IExitStatusParameters,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ab7d26d5469b5b6c0e29a363f1df400cb54444d7c1410e5ff9f75040b8d016a5(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9aa80e9da29b815c2216de3e59544d411c5ae7ccb91a9aa5862ec208bcc359e0(
    value: typing.Optional[builtins.bool],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__40451e9eb2383fabfc2f6167dd2fcf338905db7adab8c75235e7190fdb177b68(
    value: typing.Optional[builtins.bool],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__737ec7840e8dfa9d9cd5cf32a5984c31ca00e6ad76655f07f1d726f854375cd6(
    options: IExitStatusParameters,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a33531853ca010cd8882c5714e9a2ad6beee006846d2e57cb93190ad05124b18(
    value: typing.Optional[jsii.Number],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4ce1b0fe452141f52dadedaec25ac1e425828335ed0ff4b7200c567492d6a9b5(
    value: typing.Optional[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__39a62fb1c3c72626b222baedfd34426037042b43639e755e64fcc23e8faa619b(
    value: typing.Optional[jsii.Number],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__432d3c94a37792d993d81a4a6725eadd7a8b2d968dadbf01c54ff8d7dc47f3ea(
    value: typing.Optional[jsii.Number],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1fa427b17c981c14d342fb14befcdc3df096414a5ff731207ee27c782a723585(
    value: typing.Optional[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a77d55a66ee913d0287ddb7b65dacc0e9e2d24afe229da0f45f50f4276cd9ccf(
    options: IExport,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__dbeee402395196520cb0c5ef3ee261e41aeb050f715e088d7fcb7ef8222a1890(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__112fb7b2bcbb690a9d185f92f3e7b9d93cd123e2f25b4483ca3e5709bca9ac99(
    value: typing.Optional[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1bf4f8a646cddadc97de3bda8981a50d3a8e3e2bc223d8db9b54de1440429309(
    value: typing.Optional[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d05c02ccd544ed30bdf5ccc79d345903ebaafe812310e9387bfa36532737c027(
    value: typing.Optional[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d0744234256114728d0e2ba4a8c3e24b83f89d6f2800b6fc74f76d3c5c23efcb(
    options: IGraphQL,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7f6a5592eb5de32e44b135d23989807949590e257274420bc2cbc32a481b4b20(
    value: typing.Optional[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7e184b80f2fd3510f698ff522aa2bb934bd04dab50cef1f0504dddca03cf4eb8(
    value: typing.Optional[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__419879280b8f202a98c9a8b9c83a7ffdcf869962595952b4356c0df16ae443c2(
    value: typing.Optional[builtins.bool],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__73348b7c04a3fff47333e243af255ae9832a51ce03fe3994a1803e3b27b95f22(
    value: typing.Optional[jsii.Number],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5bfc5febe57d1b3446892e0e9283dfab6a7c6562ccc9e8301b7e7ce49e12522d(
    value: typing.Optional[jsii.Number],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0082db5525ec4009a3aefe13efe88c96ccbe1026aceea14fa95026e03937cbc1(
    value: typing.Optional[jsii.Number],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__98127d7e597d46492b3d6cf4261a6ce76a5b840e74fe0514cdd7d2625e101b58(
    value: typing.Optional[builtins.bool],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3002fcc84c354156c13eae3c661634a1d3f729b04d362760c87839e9aa035cec(
    value: typing.Optional[builtins.bool],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ae1b6fa0fcb676d3c99a4901944aef555c9d685ed8a8cdcb6c0ad2f78ca6c094(
    value: typing.Optional[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__07e6997b69df8a2b0dff975a71a706001be6d0d6438708249e2f122ee7cf3381(
    value: typing.Optional[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3b499a58a0003c8b742b267a6395612387ccd2d9b9cf55c15efff538e7181b06(
    value: typing.Optional[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a48d44c10fd2b74902041a559a616edb43600ab1709037aad45f33aa6cface55(
    value: typing.Optional[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__93d2dd3d4c5b9123a1a76a0555cb93ecd98e4cd4a5e37d3debcfacf3eeda39c4(
    options: typing.Optional[IHttpHeaders] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0a33b265388fdea1bf371cf3d31e2d813b550da405fc1d47cb058d0db2de8e51(
    value: typing.Optional[builtins.bool],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__31d37e54c10474c7fa28382aaed4eaf79d4c95a7d544e3ed5ec4419fcc29666a(
    value: typing.Optional[builtins.bool],
) -> None:
    """Type checking stubs"""
    pass
