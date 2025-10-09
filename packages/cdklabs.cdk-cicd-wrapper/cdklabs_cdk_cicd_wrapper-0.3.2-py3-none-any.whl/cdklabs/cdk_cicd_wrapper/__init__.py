r'''
## CDK CI/CD Wrapper

[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)

The [CDK CI/CD Wrapper](https://cdklabs.github.io/cdk-cicd-wrapper/) is a comprehensive solution that streamlines the delivery of your AWS Cloud Development Kit (CDK) applications. It provides a robust and standardized multi-stage CI/CD pipeline, ensuring high quality and confidence throughout the development and deployment process.

## Table of Contents

* [Introduction](#introduction)
* [Features](#features)
* [Getting Started](#getting-started)

  * [Prerequisites](#prerequisites)
  * [Installation](#installation)
* [Usage](#usage)

  * [Defining Stages](#defining-stages)
  * [Configuring Stacks](#configuring-stacks)
  * [Customizing CI/CD Steps](#customizing-cicd-steps)
* [Contributing](#contributing)
* [License](#license)

## Introduction

The CDK CI/CD Wrapper builds upon the success of the [aws-cdk-cicd-boot-sample](https://github.com/aws-samples/aws-cdk-cicd-boot-sample) and takes it a step further by providing additional tools and features to simplify and standardize the multi-stage CI/CD process for your Infrastructure as Code (IaC) projects.

## Features

* **Multi-staged CI/CD Pipeline**: Seamlessly deploy your CDK applications across multiple stages (e.g., DEV, INT, PROD) and AWS accounts.
* **Security Scanning**: Perform security scanning on dependencies and codebase, blocking the pipeline in case of CVE findings.
* **License Management**: Manage licenses for NPM and Python dependencies, ensuring compliance with your organization's policies.
* **Private NPM Registry**: Securely store and utilize private NPM libraries.
* **Customizable Pipeline**: Tailor the CI/CD pipeline to your project's specific needs with built-in dependency injection.
* **Workbench Deployment**: Develop and experiment with your solutions in isolation before introducing them to the delivery pipeline.
* **Pre/Post Deploy Hooks**: Execute custom scripts before and after deployments in each stage (e.g., unit tests, functional tests, load testing).
* **Centralized Compliance Logs**: Store compliance logs in pre-configured S3 buckets on a per-stage/environment basis.
* **Lambda Layer Support**: Build and scan dependencies for Python Lambda Layers.

## Getting Started

### Prerequisites

Before you begin, ensure that you have the following dependencies installed:

* AWS Account (RES/DEV/INT/PROD)
* macOS or Cloud9 with Ubuntu Server 22.04 LTS Platform in the RES Account
* Bash/ZSH terminal
* Docker version >= 24.0.x
* AWS CLI v2 ([installation guide](https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html))
* AWS credentials and profiles for each environment in `~/.aws/config` ([configuration guide](https://docs.aws.amazon.com/cli/latest/userguide/cli-configure-files.html))
* Node.js >= v18.17._ && NPM >= v10.2._
* jq command-line JSON processor (jq-1.7)

For developing Python Lambdas, you'll also need:

* Python >= 3.11
* Pipenv 2023.* ([installation guide](https://pipenv.pypa.io/en/latest/))

### Installation

1. Clone the CDK CI/CD Wrapper repository:

   ```bash
   git clone https://github.com/your-repo/cdk-cicd-wrapper.git
   cd cdk-cicd-wrapper
   ```
2. Install the required dependencies:

   ```bash
   npm install
   ```

## Usage

### Defining Stages

The CDK CI/CD Wrapper comes with a default set of stages (DEV, INT, PROD), but you can easily extend or modify these stages to suit your project's needs. Follow the step-by-step guide in the documentation to define your desired stages.

### Configuring Stacks

Configure the CDK stacks you want to deploy in each stage. The CDK CI/CD Wrapper allows you to specify which stacks should be deployed in each stage, giving you granular control over your deployment process.

### Customizing CI/CD Steps

Tailor the CI/CD pipeline to meet your project's specific requirements. The CDK CI/CD Wrapper provides built-in dependency injection, allowing you to customize the CI/CD steps seamlessly.

## Contributing

Contributions to the CDK CI/CD Wrapper are welcome! If you'd like to contribute, please follow the guidelines outlined in the [CONTRIBUTING.md](CONTRIBUTING.md) file.

## License

This project is licensed under the [Apache 2.0 License](LICENSE).
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

import aws_cdk as _aws_cdk_ceddda9d
import aws_cdk.aws_codebuild as _aws_cdk_aws_codebuild_ceddda9d
import aws_cdk.aws_codepipeline as _aws_cdk_aws_codepipeline_ceddda9d
import aws_cdk.aws_ec2 as _aws_cdk_aws_ec2_ceddda9d
import aws_cdk.aws_iam as _aws_cdk_aws_iam_ceddda9d
import aws_cdk.aws_kms as _aws_cdk_aws_kms_ceddda9d
import aws_cdk.aws_ssm as _aws_cdk_aws_ssm_ceddda9d
import aws_cdk.cx_api as _aws_cdk_cx_api_ceddda9d
import aws_cdk.pipelines as _aws_cdk_pipelines_ceddda9d
import cdk_pipelines_github as _cdk_pipelines_github_fc0d05f7
import constructs as _constructs_77d1e7e8


@jsii.data_type(
    jsii_type="@cdklabs/cdk-cicd-wrapper.AddStageOpts",
    jsii_struct_bases=[_aws_cdk_pipelines_ceddda9d.AddStageOpts],
    name_mapping={
        "post": "post",
        "pre": "pre",
        "stack_steps": "stackSteps",
        "before_entry": "beforeEntry",
        "on_failure": "onFailure",
        "on_success": "onSuccess",
        "transition_disabled_reason": "transitionDisabledReason",
        "transition_to_enabled": "transitionToEnabled",
    },
)
class AddStageOpts(_aws_cdk_pipelines_ceddda9d.AddStageOpts):
    def __init__(
        self,
        *,
        post: typing.Optional[typing.Sequence[_aws_cdk_pipelines_ceddda9d.Step]] = None,
        pre: typing.Optional[typing.Sequence[_aws_cdk_pipelines_ceddda9d.Step]] = None,
        stack_steps: typing.Optional[typing.Sequence[typing.Union[_aws_cdk_pipelines_ceddda9d.StackSteps, typing.Dict[builtins.str, typing.Any]]]] = None,
        before_entry: typing.Optional[typing.Union[_aws_cdk_aws_codepipeline_ceddda9d.Conditions, typing.Dict[builtins.str, typing.Any]]] = None,
        on_failure: typing.Optional[typing.Union[_aws_cdk_aws_codepipeline_ceddda9d.FailureConditions, typing.Dict[builtins.str, typing.Any]]] = None,
        on_success: typing.Optional[typing.Union[_aws_cdk_aws_codepipeline_ceddda9d.Conditions, typing.Dict[builtins.str, typing.Any]]] = None,
        transition_disabled_reason: typing.Optional[builtins.str] = None,
        transition_to_enabled: typing.Optional[builtins.bool] = None,
    ) -> None:
        '''
        :param post: Additional steps to run after all of the stacks in the stage. Default: - No additional steps
        :param pre: Additional steps to run before any of the stacks in the stage. Default: - No additional steps
        :param stack_steps: Instructions for stack level steps. Default: - No additional instructions
        :param before_entry: The method to use when a stage allows entry. Default: - No conditions are applied before stage entry
        :param on_failure: The method to use when a stage has not completed successfully. Default: - No failure conditions are applied
        :param on_success: The method to use when a stage has succeeded. Default: - No success conditions are applied
        :param transition_disabled_reason: The reason for disabling transition to this stage. Only applicable if ``transitionToEnabled`` is set to ``false``. Default: 'Transition disabled'
        :param transition_to_enabled: Whether to enable transition to this stage. Default: true
        '''
        if isinstance(before_entry, dict):
            before_entry = _aws_cdk_aws_codepipeline_ceddda9d.Conditions(**before_entry)
        if isinstance(on_failure, dict):
            on_failure = _aws_cdk_aws_codepipeline_ceddda9d.FailureConditions(**on_failure)
        if isinstance(on_success, dict):
            on_success = _aws_cdk_aws_codepipeline_ceddda9d.Conditions(**on_success)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__fcc51638b65f56e1cec2fe849b835e401809055e38ebabeda2276f1ed766fe16)
            check_type(argname="argument post", value=post, expected_type=type_hints["post"])
            check_type(argname="argument pre", value=pre, expected_type=type_hints["pre"])
            check_type(argname="argument stack_steps", value=stack_steps, expected_type=type_hints["stack_steps"])
            check_type(argname="argument before_entry", value=before_entry, expected_type=type_hints["before_entry"])
            check_type(argname="argument on_failure", value=on_failure, expected_type=type_hints["on_failure"])
            check_type(argname="argument on_success", value=on_success, expected_type=type_hints["on_success"])
            check_type(argname="argument transition_disabled_reason", value=transition_disabled_reason, expected_type=type_hints["transition_disabled_reason"])
            check_type(argname="argument transition_to_enabled", value=transition_to_enabled, expected_type=type_hints["transition_to_enabled"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if post is not None:
            self._values["post"] = post
        if pre is not None:
            self._values["pre"] = pre
        if stack_steps is not None:
            self._values["stack_steps"] = stack_steps
        if before_entry is not None:
            self._values["before_entry"] = before_entry
        if on_failure is not None:
            self._values["on_failure"] = on_failure
        if on_success is not None:
            self._values["on_success"] = on_success
        if transition_disabled_reason is not None:
            self._values["transition_disabled_reason"] = transition_disabled_reason
        if transition_to_enabled is not None:
            self._values["transition_to_enabled"] = transition_to_enabled

    @builtins.property
    def post(self) -> typing.Optional[typing.List[_aws_cdk_pipelines_ceddda9d.Step]]:
        '''Additional steps to run after all of the stacks in the stage.

        :default: - No additional steps
        '''
        result = self._values.get("post")
        return typing.cast(typing.Optional[typing.List[_aws_cdk_pipelines_ceddda9d.Step]], result)

    @builtins.property
    def pre(self) -> typing.Optional[typing.List[_aws_cdk_pipelines_ceddda9d.Step]]:
        '''Additional steps to run before any of the stacks in the stage.

        :default: - No additional steps
        '''
        result = self._values.get("pre")
        return typing.cast(typing.Optional[typing.List[_aws_cdk_pipelines_ceddda9d.Step]], result)

    @builtins.property
    def stack_steps(
        self,
    ) -> typing.Optional[typing.List[_aws_cdk_pipelines_ceddda9d.StackSteps]]:
        '''Instructions for stack level steps.

        :default: - No additional instructions
        '''
        result = self._values.get("stack_steps")
        return typing.cast(typing.Optional[typing.List[_aws_cdk_pipelines_ceddda9d.StackSteps]], result)

    @builtins.property
    def before_entry(
        self,
    ) -> typing.Optional[_aws_cdk_aws_codepipeline_ceddda9d.Conditions]:
        '''The method to use when a stage allows entry.

        :default: - No conditions are applied before stage entry
        '''
        result = self._values.get("before_entry")
        return typing.cast(typing.Optional[_aws_cdk_aws_codepipeline_ceddda9d.Conditions], result)

    @builtins.property
    def on_failure(
        self,
    ) -> typing.Optional[_aws_cdk_aws_codepipeline_ceddda9d.FailureConditions]:
        '''The method to use when a stage has not completed successfully.

        :default: - No failure conditions are applied
        '''
        result = self._values.get("on_failure")
        return typing.cast(typing.Optional[_aws_cdk_aws_codepipeline_ceddda9d.FailureConditions], result)

    @builtins.property
    def on_success(
        self,
    ) -> typing.Optional[_aws_cdk_aws_codepipeline_ceddda9d.Conditions]:
        '''The method to use when a stage has succeeded.

        :default: - No success conditions are applied
        '''
        result = self._values.get("on_success")
        return typing.cast(typing.Optional[_aws_cdk_aws_codepipeline_ceddda9d.Conditions], result)

    @builtins.property
    def transition_disabled_reason(self) -> typing.Optional[builtins.str]:
        '''The reason for disabling transition to this stage.

        Only applicable
        if ``transitionToEnabled`` is set to ``false``.

        :default: 'Transition disabled'
        '''
        result = self._values.get("transition_disabled_reason")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def transition_to_enabled(self) -> typing.Optional[builtins.bool]:
        '''Whether to enable transition to this stage.

        :default: true
        '''
        result = self._values.get("transition_to_enabled")
        return typing.cast(typing.Optional[builtins.bool], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "AddStageOpts(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class AppStage(
    _aws_cdk_ceddda9d.Stage,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdklabs/cdk-cicd-wrapper.AppStage",
):
    '''Represents a stage in the application deployment process.

    This class encapsulates the logic for creating and configuring a deployment stage in an application.

    :class: AppStage
    :extends: cdk.Stage - Inherits functionality from the cdk.Stage class.
    '''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        env: typing.Optional[typing.Union[_aws_cdk_ceddda9d.Environment, typing.Dict[builtins.str, typing.Any]]] = None,
        outdir: typing.Optional[builtins.str] = None,
        permissions_boundary: typing.Optional[_aws_cdk_ceddda9d.PermissionsBoundary] = None,
        policy_validation_beta1: typing.Optional[typing.Sequence[_aws_cdk_ceddda9d.IPolicyValidationPluginBeta1]] = None,
        stage_name: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param env: Default AWS environment (account/region) for ``Stack``s in this ``Stage``. Stacks defined inside this ``Stage`` with either ``region`` or ``account`` missing from its env will use the corresponding field given here. If either ``region`` or ``account``is is not configured for ``Stack`` (either on the ``Stack`` itself or on the containing ``Stage``), the Stack will be *environment-agnostic*. Environment-agnostic stacks can be deployed to any environment, may not be able to take advantage of all features of the CDK. For example, they will not be able to use environmental context lookups, will not automatically translate Service Principals to the right format based on the environment's AWS partition, and other such enhancements. Default: - The environments should be configured on the ``Stack``s.
        :param outdir: The output directory into which to emit synthesized artifacts. Can only be specified if this stage is the root stage (the app). If this is specified and this stage is nested within another stage, an error will be thrown. Default: - for nested stages, outdir will be determined as a relative directory to the outdir of the app. For apps, if outdir is not specified, a temporary directory will be created.
        :param permissions_boundary: Options for applying a permissions boundary to all IAM Roles and Users created within this Stage. Be aware that this feature uses Aspects, and the Aspects are applied at the Stack level with a priority of ``MUTATING`` (if the feature flag ``@aws-cdk/core:aspectPrioritiesMutating`` is set) or ``DEFAULT`` (if the flag is not set). This is relevant if you are both using your own Aspects to assign Permissions Boundaries, as well as specifying this property. The Aspect added by this property will overwrite the Permissions Boundary assigned by your own Aspect if both: (a) your Aspect has a lower or equal priority to the automatic Aspect, and (b) your Aspect is applied *above* the Stack level. If either of those conditions are not true, your own Aspect will win. We recommend assigning Permissions Boundaries only using the provided APIs, and not using custom Aspects. Default: - no permissions boundary is applied
        :param policy_validation_beta1: Validation plugins to run during synthesis. If any plugin reports any violation, synthesis will be interrupted and the report displayed to the user. Default: - no validation plugins are used
        :param stage_name: Name of this stage. Default: - Derived from the id.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__77654defeaf3698a9aadb8849bbb10f6cdf215c08f96e4208e74f268a4647f53)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = _aws_cdk_ceddda9d.StageProps(
            env=env,
            outdir=outdir,
            permissions_boundary=permissions_boundary,
            policy_validation_beta1=policy_validation_beta1,
            stage_name=stage_name,
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @jsii.member(jsii_name="addBeforeEntryCondition")
    def add_before_entry_condition(
        self,
        *,
        conditions: typing.Optional[typing.Sequence[typing.Union[_aws_cdk_aws_codepipeline_ceddda9d.Condition, typing.Dict[builtins.str, typing.Any]]]] = None,
    ) -> None:
        '''Sets the conditions to be applied before the stage entry.

        :param conditions: The conditions that are configured as entry conditions, making check to succeed the stage, or fail the stage. Default: - No conditions are configured
        '''
        conditions_ = _aws_cdk_aws_codepipeline_ceddda9d.Conditions(
            conditions=conditions
        )

        return typing.cast(None, jsii.invoke(self, "addBeforeEntryCondition", [conditions_]))

    @jsii.member(jsii_name="disableTransition")
    def disable_transition(self, reason: builtins.str) -> None:
        '''Sets the reason for disabling the transition.

        :param reason: - The reason for disabling the transition.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8cf96545be51eec6264fb0287e08c9badf0113db4c6d6cb6b85879bba5bfac78)
            check_type(argname="argument reason", value=reason, expected_type=type_hints["reason"])
        return typing.cast(None, jsii.invoke(self, "disableTransition", [reason]))

    @jsii.member(jsii_name="onFailure")
    def on_failure(
        self,
        *,
        result: typing.Optional[_aws_cdk_aws_codepipeline_ceddda9d.Result] = None,
        retry_mode: typing.Optional[_aws_cdk_aws_codepipeline_ceddda9d.RetryMode] = None,
        conditions: typing.Optional[typing.Sequence[typing.Union[_aws_cdk_aws_codepipeline_ceddda9d.Condition, typing.Dict[builtins.str, typing.Any]]]] = None,
    ) -> None:
        '''Sets the conditions to be applied when the stage has not completed successfully.

        :param result: The specified result for when the failure conditions are met, such as rolling back the stage. Default: FAIL
        :param retry_mode: The method that you want to configure for automatic stage retry on stage failure. Default: ALL_ACTIONS
        :param conditions: The conditions that are configured as entry conditions, making check to succeed the stage, or fail the stage. Default: - No conditions are configured
        '''
        conditions = _aws_cdk_aws_codepipeline_ceddda9d.FailureConditions(
            result=result, retry_mode=retry_mode, conditions=conditions
        )

        return typing.cast(None, jsii.invoke(self, "onFailure", [conditions]))

    @jsii.member(jsii_name="onSuccess")
    def on_success(
        self,
        *,
        conditions: typing.Optional[typing.Sequence[typing.Union[_aws_cdk_aws_codepipeline_ceddda9d.Condition, typing.Dict[builtins.str, typing.Any]]]] = None,
    ) -> None:
        '''Sets the conditions to be applied when the stage has succeeded.

        :param conditions: The conditions that are configured as entry conditions, making check to succeed the stage, or fail the stage. Default: - No conditions are configured
        '''
        conditions_ = _aws_cdk_aws_codepipeline_ceddda9d.Conditions(
            conditions=conditions
        )

        return typing.cast(None, jsii.invoke(self, "onSuccess", [conditions_]))

    @jsii.member(jsii_name="synth")
    def synth(
        self,
        *,
        aspect_stabilization: typing.Optional[builtins.bool] = None,
        error_on_duplicate_synth: typing.Optional[builtins.bool] = None,
        force: typing.Optional[builtins.bool] = None,
        skip_validation: typing.Optional[builtins.bool] = None,
        validate_on_synthesis: typing.Optional[builtins.bool] = None,
    ) -> _aws_cdk_cx_api_ceddda9d.CloudAssembly:
        '''Synthesize this stage into a cloud assembly.

        Once an assembly has been synthesized, it cannot be modified. Subsequent
        calls will return the same assembly.

        :param aspect_stabilization: Whether or not run the stabilization loop while invoking Aspects. The stabilization loop runs multiple passes of the construct tree when invoking Aspects. Without the stabilization loop, Aspects that are created by other Aspects are not run and new nodes that are created at higher points on the construct tree by an Aspect will not inherit their parent aspects. Default: false
        :param error_on_duplicate_synth: Whether or not to throw a warning instead of an error if the construct tree has been mutated since the last synth. Default: true
        :param force: Force a re-synth, even if the stage has already been synthesized. This is used by tests to allow for incremental verification of the output. Do not use in production. Default: false
        :param skip_validation: Should we skip construct validation. Default: - false
        :param validate_on_synthesis: Whether the stack should be validated after synthesis to check for error metadata. Default: - false
        '''
        options = _aws_cdk_ceddda9d.StageSynthesisOptions(
            aspect_stabilization=aspect_stabilization,
            error_on_duplicate_synth=error_on_duplicate_synth,
            force=force,
            skip_validation=skip_validation,
            validate_on_synthesis=validate_on_synthesis,
        )

        return typing.cast(_aws_cdk_cx_api_ceddda9d.CloudAssembly, jsii.invoke(self, "synth", [options]))

    @builtins.property
    @jsii.member(jsii_name="config")
    def config(self) -> "IStageConfig":
        '''Returns the stage configuration.

        :return: The stage configuration.
        '''
        return typing.cast("IStageConfig", jsii.get(self, "config"))


@jsii.data_type(
    jsii_type="@cdklabs/cdk-cicd-wrapper.AppStageProps",
    jsii_struct_bases=[_aws_cdk_ceddda9d.StageProps],
    name_mapping={
        "env": "env",
        "outdir": "outdir",
        "permissions_boundary": "permissionsBoundary",
        "policy_validation_beta1": "policyValidationBeta1",
        "stage_name": "stageName",
        "context": "context",
    },
)
class AppStageProps(_aws_cdk_ceddda9d.StageProps):
    def __init__(
        self,
        *,
        env: typing.Optional[typing.Union[_aws_cdk_ceddda9d.Environment, typing.Dict[builtins.str, typing.Any]]] = None,
        outdir: typing.Optional[builtins.str] = None,
        permissions_boundary: typing.Optional[_aws_cdk_ceddda9d.PermissionsBoundary] = None,
        policy_validation_beta1: typing.Optional[typing.Sequence[_aws_cdk_ceddda9d.IPolicyValidationPluginBeta1]] = None,
        stage_name: typing.Optional[builtins.str] = None,
        context: "ResourceContext",
    ) -> None:
        '''Interface for the properties required to create an AppStage.

        This interface represents the configuration properties needed to create a stage in the application deployment process.

        :param env: Default AWS environment (account/region) for ``Stack``s in this ``Stage``. Stacks defined inside this ``Stage`` with either ``region`` or ``account`` missing from its env will use the corresponding field given here. If either ``region`` or ``account``is is not configured for ``Stack`` (either on the ``Stack`` itself or on the containing ``Stage``), the Stack will be *environment-agnostic*. Environment-agnostic stacks can be deployed to any environment, may not be able to take advantage of all features of the CDK. For example, they will not be able to use environmental context lookups, will not automatically translate Service Principals to the right format based on the environment's AWS partition, and other such enhancements. Default: - The environments should be configured on the ``Stack``s.
        :param outdir: The output directory into which to emit synthesized artifacts. Can only be specified if this stage is the root stage (the app). If this is specified and this stage is nested within another stage, an error will be thrown. Default: - for nested stages, outdir will be determined as a relative directory to the outdir of the app. For apps, if outdir is not specified, a temporary directory will be created.
        :param permissions_boundary: Options for applying a permissions boundary to all IAM Roles and Users created within this Stage. Be aware that this feature uses Aspects, and the Aspects are applied at the Stack level with a priority of ``MUTATING`` (if the feature flag ``@aws-cdk/core:aspectPrioritiesMutating`` is set) or ``DEFAULT`` (if the flag is not set). This is relevant if you are both using your own Aspects to assign Permissions Boundaries, as well as specifying this property. The Aspect added by this property will overwrite the Permissions Boundary assigned by your own Aspect if both: (a) your Aspect has a lower or equal priority to the automatic Aspect, and (b) your Aspect is applied *above* the Stack level. If either of those conditions are not true, your own Aspect will win. We recommend assigning Permissions Boundaries only using the provided APIs, and not using custom Aspects. Default: - no permissions boundary is applied
        :param policy_validation_beta1: Validation plugins to run during synthesis. If any plugin reports any violation, synthesis will be interrupted and the report displayed to the user. Default: - no validation plugins are used
        :param stage_name: Name of this stage. Default: - Derived from the id.
        :param context: 

        :extends: cdk.StageProps - Inherits properties from the cdk.StageProps interface.
        :interface: AppStageProps
        :property: {ResourceContext} context - The resource context object containing deployment-related information.
        '''
        if isinstance(env, dict):
            env = _aws_cdk_ceddda9d.Environment(**env)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__268d48de282b6f8137f8c004fc74599cd87b57ce07891625172bb54fd640c1b4)
            check_type(argname="argument env", value=env, expected_type=type_hints["env"])
            check_type(argname="argument outdir", value=outdir, expected_type=type_hints["outdir"])
            check_type(argname="argument permissions_boundary", value=permissions_boundary, expected_type=type_hints["permissions_boundary"])
            check_type(argname="argument policy_validation_beta1", value=policy_validation_beta1, expected_type=type_hints["policy_validation_beta1"])
            check_type(argname="argument stage_name", value=stage_name, expected_type=type_hints["stage_name"])
            check_type(argname="argument context", value=context, expected_type=type_hints["context"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "context": context,
        }
        if env is not None:
            self._values["env"] = env
        if outdir is not None:
            self._values["outdir"] = outdir
        if permissions_boundary is not None:
            self._values["permissions_boundary"] = permissions_boundary
        if policy_validation_beta1 is not None:
            self._values["policy_validation_beta1"] = policy_validation_beta1
        if stage_name is not None:
            self._values["stage_name"] = stage_name

    @builtins.property
    def env(self) -> typing.Optional[_aws_cdk_ceddda9d.Environment]:
        '''Default AWS environment (account/region) for ``Stack``s in this ``Stage``.

        Stacks defined inside this ``Stage`` with either ``region`` or ``account`` missing
        from its env will use the corresponding field given here.

        If either ``region`` or ``account``is is not configured for ``Stack`` (either on
        the ``Stack`` itself or on the containing ``Stage``), the Stack will be
        *environment-agnostic*.

        Environment-agnostic stacks can be deployed to any environment, may not be
        able to take advantage of all features of the CDK. For example, they will
        not be able to use environmental context lookups, will not automatically
        translate Service Principals to the right format based on the environment's
        AWS partition, and other such enhancements.

        :default: - The environments should be configured on the ``Stack``s.

        Example::

            // Use a concrete account and region to deploy this Stage to
            new Stage(app, 'Stage1', {
              env: { account: '123456789012', region: 'us-east-1' },
            });
            
            // Use the CLI's current credentials to determine the target environment
            new Stage(app, 'Stage2', {
              env: { account: process.env.CDK_DEFAULT_ACCOUNT, region: process.env.CDK_DEFAULT_REGION },
            });
        '''
        result = self._values.get("env")
        return typing.cast(typing.Optional[_aws_cdk_ceddda9d.Environment], result)

    @builtins.property
    def outdir(self) -> typing.Optional[builtins.str]:
        '''The output directory into which to emit synthesized artifacts.

        Can only be specified if this stage is the root stage (the app). If this is
        specified and this stage is nested within another stage, an error will be
        thrown.

        :default:

        - for nested stages, outdir will be determined as a relative
        directory to the outdir of the app. For apps, if outdir is not specified, a
        temporary directory will be created.
        '''
        result = self._values.get("outdir")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def permissions_boundary(
        self,
    ) -> typing.Optional[_aws_cdk_ceddda9d.PermissionsBoundary]:
        '''Options for applying a permissions boundary to all IAM Roles and Users created within this Stage.

        Be aware that this feature uses Aspects, and the Aspects are applied at the
        Stack level with a priority of ``MUTATING`` (if the feature flag
        ``@aws-cdk/core:aspectPrioritiesMutating`` is set) or ``DEFAULT`` (if the flag
        is not set). This is relevant if you are both using your own Aspects to
        assign Permissions Boundaries, as well as specifying this property.  The
        Aspect added by this property will overwrite the Permissions Boundary
        assigned by your own Aspect if both: (a) your Aspect has a lower or equal
        priority to the automatic Aspect, and (b) your Aspect is applied *above*
        the Stack level.  If either of those conditions are not true, your own
        Aspect will win.

        We recommend assigning Permissions Boundaries only using the provided APIs,
        and not using custom Aspects.

        :default: - no permissions boundary is applied
        '''
        result = self._values.get("permissions_boundary")
        return typing.cast(typing.Optional[_aws_cdk_ceddda9d.PermissionsBoundary], result)

    @builtins.property
    def policy_validation_beta1(
        self,
    ) -> typing.Optional[typing.List[_aws_cdk_ceddda9d.IPolicyValidationPluginBeta1]]:
        '''Validation plugins to run during synthesis.

        If any plugin reports any violation,
        synthesis will be interrupted and the report displayed to the user.

        :default: - no validation plugins are used
        '''
        result = self._values.get("policy_validation_beta1")
        return typing.cast(typing.Optional[typing.List[_aws_cdk_ceddda9d.IPolicyValidationPluginBeta1]], result)

    @builtins.property
    def stage_name(self) -> typing.Optional[builtins.str]:
        '''Name of this stage.

        :default: - Derived from the id.
        '''
        result = self._values.get("stage_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def context(self) -> "ResourceContext":
        result = self._values.get("context")
        assert result is not None, "Required property 'context' is missing"
        return typing.cast("ResourceContext", result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "AppStageProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdklabs/cdk-cicd-wrapper.BuildOptions",
    jsii_struct_bases=[],
    name_mapping={
        "code_build_defaults": "codeBuildDefaults",
        "run_time_versions": "runTimeVersions",
    },
)
class BuildOptions:
    def __init__(
        self,
        *,
        code_build_defaults: typing.Optional[typing.Union[_aws_cdk_pipelines_ceddda9d.CodeBuildOptions, typing.Dict[builtins.str, typing.Any]]] = None,
        run_time_versions: typing.Optional[typing.Union["RuntimeVersionOptions", typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''
        :param code_build_defaults: 
        :param run_time_versions: 
        '''
        if isinstance(code_build_defaults, dict):
            code_build_defaults = _aws_cdk_pipelines_ceddda9d.CodeBuildOptions(**code_build_defaults)
        if isinstance(run_time_versions, dict):
            run_time_versions = RuntimeVersionOptions(**run_time_versions)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__feab7d5c7f161a2021e30e139c542a8cd7ed813103cd0ffc4280adedcb2ce429)
            check_type(argname="argument code_build_defaults", value=code_build_defaults, expected_type=type_hints["code_build_defaults"])
            check_type(argname="argument run_time_versions", value=run_time_versions, expected_type=type_hints["run_time_versions"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if code_build_defaults is not None:
            self._values["code_build_defaults"] = code_build_defaults
        if run_time_versions is not None:
            self._values["run_time_versions"] = run_time_versions

    @builtins.property
    def code_build_defaults(
        self,
    ) -> typing.Optional[_aws_cdk_pipelines_ceddda9d.CodeBuildOptions]:
        result = self._values.get("code_build_defaults")
        return typing.cast(typing.Optional[_aws_cdk_pipelines_ceddda9d.CodeBuildOptions], result)

    @builtins.property
    def run_time_versions(self) -> typing.Optional["RuntimeVersionOptions"]:
        result = self._values.get("run_time_versions")
        return typing.cast(typing.Optional["RuntimeVersionOptions"], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "BuildOptions(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class CDKPipeline(
    _aws_cdk_pipelines_ceddda9d.CodePipeline,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdklabs/cdk-cicd-wrapper.CDKPipeline",
):
    '''A construct for creating a CDK pipeline.'''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        application_qualifier: builtins.str,
        pipeline_name: builtins.str,
        role_policies: typing.Optional[typing.Sequence[_aws_cdk_aws_iam_ceddda9d.PolicyStatement]] = None,
        branch: builtins.str,
        ci_build_spec: _aws_cdk_aws_codebuild_ceddda9d.BuildSpec,
        code_build_defaults: typing.Union[_aws_cdk_pipelines_ceddda9d.CodeBuildOptions, typing.Dict[builtins.str, typing.Any]],
        primary_output_directory: builtins.str,
        repository_input: _aws_cdk_pipelines_ceddda9d.IFileSetProducer,
        build_image: typing.Optional[_aws_cdk_aws_codebuild_ceddda9d.IBuildImage] = None,
        code_guru_scan_threshold: typing.Optional["CodeGuruSeverityThreshold"] = None,
        install_commands: typing.Optional[typing.Sequence[builtins.str]] = None,
        is_docker_enabled_for_synth: typing.Optional[builtins.bool] = None,
        options: typing.Optional[typing.Union["PipelineOptions", typing.Dict[builtins.str, typing.Any]]] = None,
        pipeline_variables: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        synth_code_build_defaults: typing.Optional[typing.Union[_aws_cdk_pipelines_ceddda9d.CodeBuildOptions, typing.Dict[builtins.str, typing.Any]]] = None,
        vpc_props: typing.Optional[typing.Union["VpcProps", typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''Creates a new instance of the CDKPipeline construct.

        :param scope: The parent construct.
        :param id: The ID of the construct.
        :param application_qualifier: The qualifier for the application.
        :param pipeline_name: The name of the pipeline.
        :param role_policies: Additional IAM policies to be attached to the pipeline role.
        :param branch: The branch to be used from the source repository.
        :param ci_build_spec: The CI commands to be executed as part of the Synth step.
        :param code_build_defaults: Default options for CodeBuild projects in the pipeline.
        :param primary_output_directory: The primary output directory for the synth step.
        :param repository_input: The source repository for the pipeline.
        :param build_image: The Docker image to be used for the build project.
        :param code_guru_scan_threshold: The severity threshold for CodeGuru security scans.
        :param install_commands: Additional install commands to be executed before the synth step.
        :param is_docker_enabled_for_synth: Whether Docker should be enabled for synth. Default: false
        :param options: Additional Pipeline options.
        :param pipeline_variables: Pipeline variables to be passed as environment variables.
        :param synth_code_build_defaults: Default options for the synth CodeBuild project.
        :param vpc_props: VPC configuration for the pipeline.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__99bfefc0b03a54a957572378463c1ece234bab54b79ba7eaa99c7f9d7034a4e5)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = CDKPipelineProps(
            application_qualifier=application_qualifier,
            pipeline_name=pipeline_name,
            role_policies=role_policies,
            branch=branch,
            ci_build_spec=ci_build_spec,
            code_build_defaults=code_build_defaults,
            primary_output_directory=primary_output_directory,
            repository_input=repository_input,
            build_image=build_image,
            code_guru_scan_threshold=code_guru_scan_threshold,
            install_commands=install_commands,
            is_docker_enabled_for_synth=is_docker_enabled_for_synth,
            options=options,
            pipeline_variables=pipeline_variables,
            synth_code_build_defaults=synth_code_build_defaults,
            vpc_props=vpc_props,
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @jsii.member(jsii_name="addStageWithV2Options")
    def add_stage_with_v2_options(
        self,
        stage: _aws_cdk_ceddda9d.Stage,
        *,
        before_entry: typing.Optional[typing.Union[_aws_cdk_aws_codepipeline_ceddda9d.Conditions, typing.Dict[builtins.str, typing.Any]]] = None,
        on_failure: typing.Optional[typing.Union[_aws_cdk_aws_codepipeline_ceddda9d.FailureConditions, typing.Dict[builtins.str, typing.Any]]] = None,
        on_success: typing.Optional[typing.Union[_aws_cdk_aws_codepipeline_ceddda9d.Conditions, typing.Dict[builtins.str, typing.Any]]] = None,
        transition_disabled_reason: typing.Optional[builtins.str] = None,
        transition_to_enabled: typing.Optional[builtins.bool] = None,
        post: typing.Optional[typing.Sequence[_aws_cdk_pipelines_ceddda9d.Step]] = None,
        pre: typing.Optional[typing.Sequence[_aws_cdk_pipelines_ceddda9d.Step]] = None,
        stack_steps: typing.Optional[typing.Sequence[typing.Union[_aws_cdk_pipelines_ceddda9d.StackSteps, typing.Dict[builtins.str, typing.Any]]]] = None,
    ) -> _aws_cdk_pipelines_ceddda9d.StageDeployment:
        '''
        :param stage: -
        :param before_entry: The method to use when a stage allows entry. Default: - No conditions are applied before stage entry
        :param on_failure: The method to use when a stage has not completed successfully. Default: - No failure conditions are applied
        :param on_success: The method to use when a stage has succeeded. Default: - No success conditions are applied
        :param transition_disabled_reason: The reason for disabling transition to this stage. Only applicable if ``transitionToEnabled`` is set to ``false``. Default: 'Transition disabled'
        :param transition_to_enabled: Whether to enable transition to this stage. Default: true
        :param post: Additional steps to run after all of the stacks in the stage. Default: - No additional steps
        :param pre: Additional steps to run before any of the stacks in the stage. Default: - No additional steps
        :param stack_steps: Instructions for stack level steps. Default: - No additional instructions
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e306cc57ea84dcf20fb796679fd0a84b1178f92467322896b08f88a7962453dd)
            check_type(argname="argument stage", value=stage, expected_type=type_hints["stage"])
        options = AddStageOpts(
            before_entry=before_entry,
            on_failure=on_failure,
            on_success=on_success,
            transition_disabled_reason=transition_disabled_reason,
            transition_to_enabled=transition_to_enabled,
            post=post,
            pre=pre,
            stack_steps=stack_steps,
        )

        return typing.cast(_aws_cdk_pipelines_ceddda9d.StageDeployment, jsii.invoke(self, "addStageWithV2Options", [stage, options]))

    @jsii.member(jsii_name="buildPipeline")
    def build_pipeline(self) -> None:
        '''Builds the pipeline by applying necessary configurations and suppressing certain CDK Nag rules.'''
        return typing.cast(None, jsii.invoke(self, "buildPipeline", []))

    @jsii.python.classproperty
    @jsii.member(jsii_name="installCommands")
    def INSTALL_COMMANDS(cls) -> typing.List[builtins.str]:
        '''Default install commands for the pipeline.'''
        return typing.cast(typing.List[builtins.str], jsii.sget(cls, "installCommands"))

    @builtins.property
    @jsii.member(jsii_name="pipeline")
    def pipeline(self) -> _aws_cdk_aws_codepipeline_ceddda9d.Pipeline:
        '''The CodePipeline pipeline that deploys the CDK app.

        Only available after the pipeline has been built.
        '''
        return typing.cast(_aws_cdk_aws_codepipeline_ceddda9d.Pipeline, jsii.get(self, "pipeline"))

    @builtins.property
    @jsii.member(jsii_name="stages")
    def stages(
        self,
    ) -> typing.Mapping[builtins.str, _aws_cdk_pipelines_ceddda9d.AddStageOpts]:
        return typing.cast(typing.Mapping[builtins.str, _aws_cdk_pipelines_ceddda9d.AddStageOpts], jsii.get(self, "stages"))


@jsii.data_type(
    jsii_type="@cdklabs/cdk-cicd-wrapper.CodeArtifactPluginProps",
    jsii_struct_bases=[],
    name_mapping={
        "domain": "domain",
        "repository_name": "repositoryName",
        "account": "account",
        "npm_scope": "npmScope",
        "region": "region",
        "repository_types": "repositoryTypes",
    },
)
class CodeArtifactPluginProps:
    def __init__(
        self,
        *,
        domain: builtins.str,
        repository_name: builtins.str,
        account: typing.Optional[builtins.str] = None,
        npm_scope: typing.Optional[builtins.str] = None,
        region: typing.Optional[builtins.str] = None,
        repository_types: typing.Optional[typing.Sequence["CodeArtifactRepositoryTypes"]] = None,
    ) -> None:
        '''
        :param domain: 
        :param repository_name: 
        :param account: 
        :param npm_scope: 
        :param region: 
        :param repository_types: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4d291da8d58e12fa244bd82f53b17eeb5979e60f82bd74fd6b25150552161ae0)
            check_type(argname="argument domain", value=domain, expected_type=type_hints["domain"])
            check_type(argname="argument repository_name", value=repository_name, expected_type=type_hints["repository_name"])
            check_type(argname="argument account", value=account, expected_type=type_hints["account"])
            check_type(argname="argument npm_scope", value=npm_scope, expected_type=type_hints["npm_scope"])
            check_type(argname="argument region", value=region, expected_type=type_hints["region"])
            check_type(argname="argument repository_types", value=repository_types, expected_type=type_hints["repository_types"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "domain": domain,
            "repository_name": repository_name,
        }
        if account is not None:
            self._values["account"] = account
        if npm_scope is not None:
            self._values["npm_scope"] = npm_scope
        if region is not None:
            self._values["region"] = region
        if repository_types is not None:
            self._values["repository_types"] = repository_types

    @builtins.property
    def domain(self) -> builtins.str:
        result = self._values.get("domain")
        assert result is not None, "Required property 'domain' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def repository_name(self) -> builtins.str:
        result = self._values.get("repository_name")
        assert result is not None, "Required property 'repository_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def account(self) -> typing.Optional[builtins.str]:
        result = self._values.get("account")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def npm_scope(self) -> typing.Optional[builtins.str]:
        result = self._values.get("npm_scope")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def region(self) -> typing.Optional[builtins.str]:
        result = self._values.get("region")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def repository_types(
        self,
    ) -> typing.Optional[typing.List["CodeArtifactRepositoryTypes"]]:
        result = self._values.get("repository_types")
        return typing.cast(typing.Optional[typing.List["CodeArtifactRepositoryTypes"]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CodeArtifactPluginProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.enum(jsii_type="@cdklabs/cdk-cicd-wrapper.CodeArtifactRepositoryTypes")
class CodeArtifactRepositoryTypes(enum.Enum):
    NPM = "NPM"
    PIP = "PIP"
    NUGET = "NUGET"
    SWIFT = "SWIFT"
    DOTNET = "DOTNET"
    TWINE = "TWINE"


class CodeCommitRepositoryConstruct(
    _constructs_77d1e7e8.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdklabs/cdk-cicd-wrapper.CodeCommitRepositoryConstruct",
):
    '''A construct for creating a new AWS CodeCommit repository with optional pull request checks.'''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        application_name: builtins.str,
        application_qualifier: builtins.str,
        pr: typing.Optional[typing.Union["PRCheckConfig", typing.Dict[builtins.str, typing.Any]]] = None,
        branch: builtins.str,
        name: builtins.str,
        repository_type: builtins.str,
        code_build_clone_output: typing.Optional[builtins.bool] = None,
        description: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param application_name: The name of the application.
        :param application_qualifier: A qualifier for the application name.
        :param pr: Optional configuration for enabling pull request checks.
        :param branch: The branch for the repository.
        :param name: The name of the repository.
        :param repository_type: The type of the repository.
        :param code_build_clone_output: Enforce full clone for the repository.
        :param description: The description of the repository (optional).
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ee6b85606ca87dcdfd0961983691019b43620792a1e43f832a4f4be34e01ced8)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = CodeCommitRepositoryConstructProps(
            application_name=application_name,
            application_qualifier=application_qualifier,
            pr=pr,
            branch=branch,
            name=name,
            repository_type=repository_type,
            code_build_clone_output=code_build_clone_output,
            description=description,
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @builtins.property
    @jsii.member(jsii_name="pipelineInput")
    def pipeline_input(self) -> _aws_cdk_pipelines_ceddda9d.IFileSetProducer:
        '''The pipeline input for the repository.'''
        return typing.cast(_aws_cdk_pipelines_ceddda9d.IFileSetProducer, jsii.get(self, "pipelineInput"))


@jsii.enum(jsii_type="@cdklabs/cdk-cicd-wrapper.CodeGuruSeverityThreshold")
class CodeGuruSeverityThreshold(enum.Enum):
    '''Represents the severity thresholds for CodeGuru.'''

    INFO = "INFO"
    '''Information severity threshold.'''
    LOW = "LOW"
    '''Low severity threshold.'''
    MEDIUM = "MEDIUM"
    '''Medium severity threshold.'''
    HIGH = "HIGH"
    '''High severity threshold.'''
    CRITICAL = "CRITICAL"
    '''Critical severity threshold.'''


class CodeStarConnectionConstruct(
    _constructs_77d1e7e8.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdklabs/cdk-cicd-wrapper.CodeStarConnectionConstruct",
):
    '''Constructs an AWS CodeStar connection for use in a CodePipeline.'''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        code_star_connection_arn: builtins.str,
        branch: builtins.str,
        name: builtins.str,
        repository_type: builtins.str,
        code_build_clone_output: typing.Optional[builtins.bool] = None,
        description: typing.Optional[builtins.str] = None,
    ) -> None:
        '''Constructs a new instance of the CodeStarConnectionConstruct class.

        :param scope: - The scope in which to define this construct.
        :param id: - The unique identifier for this construct.
        :param code_star_connection_arn: The Amazon Resource Name (ARN) of the CodeStar connection.
        :param branch: The branch for the repository.
        :param name: The name of the repository.
        :param repository_type: The type of the repository.
        :param code_build_clone_output: Enforce full clone for the repository.
        :param description: The description of the repository (optional).
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3bdb055e914f501dcd1f46d960aba1897f20cabc108a50ab9c44dca3b5d8e445)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = CodeStarConfig(
            code_star_connection_arn=code_star_connection_arn,
            branch=branch,
            name=name,
            repository_type=repository_type,
            code_build_clone_output=code_build_clone_output,
            description=description,
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @builtins.property
    @jsii.member(jsii_name="codeStarConnectionArn")
    def code_star_connection_arn(self) -> builtins.str:
        '''The Amazon Resource Name (ARN) of the CodeStar connection.'''
        return typing.cast(builtins.str, jsii.get(self, "codeStarConnectionArn"))

    @builtins.property
    @jsii.member(jsii_name="pipelineInput")
    def pipeline_input(self) -> _aws_cdk_pipelines_ceddda9d.IFileSetProducer:
        '''The input source for the CodePipeline.'''
        return typing.cast(_aws_cdk_pipelines_ceddda9d.IFileSetProducer, jsii.get(self, "pipelineInput"))


@jsii.data_type(
    jsii_type="@cdklabs/cdk-cicd-wrapper.ComplianceBucketProviderOptions",
    jsii_struct_bases=[],
    name_mapping={"run_on_vpc": "runOnVpc"},
)
class ComplianceBucketProviderOptions:
    def __init__(self, *, run_on_vpc: typing.Optional[builtins.bool] = None) -> None:
        '''Compliance bucket provider options.

        :param run_on_vpc: Run the Custom resource on the VPC. Default: false
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6e76287addf40fe1e284454aa367bd1be88653807a3626bb749d72809b390b85)
            check_type(argname="argument run_on_vpc", value=run_on_vpc, expected_type=type_hints["run_on_vpc"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if run_on_vpc is not None:
            self._values["run_on_vpc"] = run_on_vpc

    @builtins.property
    def run_on_vpc(self) -> typing.Optional[builtins.bool]:
        '''Run the Custom resource on the VPC.

        :default: false
        '''
        result = self._values.get("run_on_vpc")
        return typing.cast(typing.Optional[builtins.bool], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ComplianceBucketProviderOptions(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdklabs/cdk-cicd-wrapper.ComplianceLogBucketStackProps",
    jsii_struct_bases=[_aws_cdk_ceddda9d.StackProps],
    name_mapping={
        "analytics_reporting": "analyticsReporting",
        "cross_region_references": "crossRegionReferences",
        "description": "description",
        "env": "env",
        "notification_arns": "notificationArns",
        "permissions_boundary": "permissionsBoundary",
        "stack_name": "stackName",
        "suppress_template_indentation": "suppressTemplateIndentation",
        "synthesizer": "synthesizer",
        "tags": "tags",
        "termination_protection": "terminationProtection",
        "compliance_log_bucket_name": "complianceLogBucketName",
        "security_group": "securityGroup",
        "subnet_selection": "subnetSelection",
        "vpc": "vpc",
    },
)
class ComplianceLogBucketStackProps(_aws_cdk_ceddda9d.StackProps):
    def __init__(
        self,
        *,
        analytics_reporting: typing.Optional[builtins.bool] = None,
        cross_region_references: typing.Optional[builtins.bool] = None,
        description: typing.Optional[builtins.str] = None,
        env: typing.Optional[typing.Union[_aws_cdk_ceddda9d.Environment, typing.Dict[builtins.str, typing.Any]]] = None,
        notification_arns: typing.Optional[typing.Sequence[builtins.str]] = None,
        permissions_boundary: typing.Optional[_aws_cdk_ceddda9d.PermissionsBoundary] = None,
        stack_name: typing.Optional[builtins.str] = None,
        suppress_template_indentation: typing.Optional[builtins.bool] = None,
        synthesizer: typing.Optional[_aws_cdk_ceddda9d.IStackSynthesizer] = None,
        tags: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        termination_protection: typing.Optional[builtins.bool] = None,
        compliance_log_bucket_name: builtins.str,
        security_group: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.ISecurityGroup] = None,
        subnet_selection: typing.Optional[typing.Union[_aws_cdk_aws_ec2_ceddda9d.SubnetSelection, typing.Dict[builtins.str, typing.Any]]] = None,
        vpc: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.IVpc] = None,
    ) -> None:
        '''Properties for the ComplianceLogBucketStack.

        :param analytics_reporting: Include runtime versioning information in this Stack. Default: ``analyticsReporting`` setting of containing ``App``, or value of 'aws:cdk:version-reporting' context key
        :param cross_region_references: Enable this flag to allow native cross region stack references. Enabling this will create a CloudFormation custom resource in both the producing stack and consuming stack in order to perform the export/import This feature is currently experimental Default: false
        :param description: A description of the stack. Default: - No description.
        :param env: The AWS environment (account/region) where this stack will be deployed. Set the ``region``/``account`` fields of ``env`` to either a concrete value to select the indicated environment (recommended for production stacks), or to the values of environment variables ``CDK_DEFAULT_REGION``/``CDK_DEFAULT_ACCOUNT`` to let the target environment depend on the AWS credentials/configuration that the CDK CLI is executed under (recommended for development stacks). If the ``Stack`` is instantiated inside a ``Stage``, any undefined ``region``/``account`` fields from ``env`` will default to the same field on the encompassing ``Stage``, if configured there. If either ``region`` or ``account`` are not set nor inherited from ``Stage``, the Stack will be considered "*environment-agnostic*"". Environment-agnostic stacks can be deployed to any environment but may not be able to take advantage of all features of the CDK. For example, they will not be able to use environmental context lookups such as ``ec2.Vpc.fromLookup`` and will not automatically translate Service Principals to the right format based on the environment's AWS partition, and other such enhancements. Default: - The environment of the containing ``Stage`` if available, otherwise create the stack will be environment-agnostic.
        :param notification_arns: SNS Topic ARNs that will receive stack events. Default: - no notfication arns.
        :param permissions_boundary: Options for applying a permissions boundary to all IAM Roles and Users created within this Stage. Default: - no permissions boundary is applied
        :param stack_name: Name to deploy the stack with. Default: - Derived from construct path.
        :param suppress_template_indentation: Enable this flag to suppress indentation in generated CloudFormation templates. If not specified, the value of the ``@aws-cdk/core:suppressTemplateIndentation`` context key will be used. If that is not specified, then the default value ``false`` will be used. Default: - the value of ``@aws-cdk/core:suppressTemplateIndentation``, or ``false`` if that is not set.
        :param synthesizer: Synthesis method to use while deploying this stack. The Stack Synthesizer controls aspects of synthesis and deployment, like how assets are referenced and what IAM roles to use. For more information, see the README of the main CDK package. If not specified, the ``defaultStackSynthesizer`` from ``App`` will be used. If that is not specified, ``DefaultStackSynthesizer`` is used if ``@aws-cdk/core:newStyleStackSynthesis`` is set to ``true`` or the CDK major version is v2. In CDK v1 ``LegacyStackSynthesizer`` is the default if no other synthesizer is specified. Default: - The synthesizer specified on ``App``, or ``DefaultStackSynthesizer`` otherwise.
        :param tags: Stack tags that will be applied to all the taggable resources and the stack itself. Default: {}
        :param termination_protection: Whether to enable termination protection for this stack. Default: false
        :param compliance_log_bucket_name: The name of the compliance log bucket to be created.
        :param security_group: The security group of the vpc.
        :param subnet_selection: The subnet selection of the vpc.
        :param vpc: The vpc where the ComplianceLogBucket CR Lambda must be attached to.
        '''
        if isinstance(env, dict):
            env = _aws_cdk_ceddda9d.Environment(**env)
        if isinstance(subnet_selection, dict):
            subnet_selection = _aws_cdk_aws_ec2_ceddda9d.SubnetSelection(**subnet_selection)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9d486671678cc2237ca4931916d6e48bdaa0ac31591dcbe5f31ac3d5b64a7e4a)
            check_type(argname="argument analytics_reporting", value=analytics_reporting, expected_type=type_hints["analytics_reporting"])
            check_type(argname="argument cross_region_references", value=cross_region_references, expected_type=type_hints["cross_region_references"])
            check_type(argname="argument description", value=description, expected_type=type_hints["description"])
            check_type(argname="argument env", value=env, expected_type=type_hints["env"])
            check_type(argname="argument notification_arns", value=notification_arns, expected_type=type_hints["notification_arns"])
            check_type(argname="argument permissions_boundary", value=permissions_boundary, expected_type=type_hints["permissions_boundary"])
            check_type(argname="argument stack_name", value=stack_name, expected_type=type_hints["stack_name"])
            check_type(argname="argument suppress_template_indentation", value=suppress_template_indentation, expected_type=type_hints["suppress_template_indentation"])
            check_type(argname="argument synthesizer", value=synthesizer, expected_type=type_hints["synthesizer"])
            check_type(argname="argument tags", value=tags, expected_type=type_hints["tags"])
            check_type(argname="argument termination_protection", value=termination_protection, expected_type=type_hints["termination_protection"])
            check_type(argname="argument compliance_log_bucket_name", value=compliance_log_bucket_name, expected_type=type_hints["compliance_log_bucket_name"])
            check_type(argname="argument security_group", value=security_group, expected_type=type_hints["security_group"])
            check_type(argname="argument subnet_selection", value=subnet_selection, expected_type=type_hints["subnet_selection"])
            check_type(argname="argument vpc", value=vpc, expected_type=type_hints["vpc"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "compliance_log_bucket_name": compliance_log_bucket_name,
        }
        if analytics_reporting is not None:
            self._values["analytics_reporting"] = analytics_reporting
        if cross_region_references is not None:
            self._values["cross_region_references"] = cross_region_references
        if description is not None:
            self._values["description"] = description
        if env is not None:
            self._values["env"] = env
        if notification_arns is not None:
            self._values["notification_arns"] = notification_arns
        if permissions_boundary is not None:
            self._values["permissions_boundary"] = permissions_boundary
        if stack_name is not None:
            self._values["stack_name"] = stack_name
        if suppress_template_indentation is not None:
            self._values["suppress_template_indentation"] = suppress_template_indentation
        if synthesizer is not None:
            self._values["synthesizer"] = synthesizer
        if tags is not None:
            self._values["tags"] = tags
        if termination_protection is not None:
            self._values["termination_protection"] = termination_protection
        if security_group is not None:
            self._values["security_group"] = security_group
        if subnet_selection is not None:
            self._values["subnet_selection"] = subnet_selection
        if vpc is not None:
            self._values["vpc"] = vpc

    @builtins.property
    def analytics_reporting(self) -> typing.Optional[builtins.bool]:
        '''Include runtime versioning information in this Stack.

        :default:

        ``analyticsReporting`` setting of containing ``App``, or value of
        'aws:cdk:version-reporting' context key
        '''
        result = self._values.get("analytics_reporting")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def cross_region_references(self) -> typing.Optional[builtins.bool]:
        '''Enable this flag to allow native cross region stack references.

        Enabling this will create a CloudFormation custom resource
        in both the producing stack and consuming stack in order to perform the export/import

        This feature is currently experimental

        :default: false
        '''
        result = self._values.get("cross_region_references")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def description(self) -> typing.Optional[builtins.str]:
        '''A description of the stack.

        :default: - No description.
        '''
        result = self._values.get("description")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def env(self) -> typing.Optional[_aws_cdk_ceddda9d.Environment]:
        '''The AWS environment (account/region) where this stack will be deployed.

        Set the ``region``/``account`` fields of ``env`` to either a concrete value to
        select the indicated environment (recommended for production stacks), or to
        the values of environment variables
        ``CDK_DEFAULT_REGION``/``CDK_DEFAULT_ACCOUNT`` to let the target environment
        depend on the AWS credentials/configuration that the CDK CLI is executed
        under (recommended for development stacks).

        If the ``Stack`` is instantiated inside a ``Stage``, any undefined
        ``region``/``account`` fields from ``env`` will default to the same field on the
        encompassing ``Stage``, if configured there.

        If either ``region`` or ``account`` are not set nor inherited from ``Stage``, the
        Stack will be considered "*environment-agnostic*"". Environment-agnostic
        stacks can be deployed to any environment but may not be able to take
        advantage of all features of the CDK. For example, they will not be able to
        use environmental context lookups such as ``ec2.Vpc.fromLookup`` and will not
        automatically translate Service Principals to the right format based on the
        environment's AWS partition, and other such enhancements.

        :default:

        - The environment of the containing ``Stage`` if available,
        otherwise create the stack will be environment-agnostic.

        Example::

            // Use a concrete account and region to deploy this stack to:
            // `.account` and `.region` will simply return these values.
            new Stack(app, 'Stack1', {
              env: {
                account: '123456789012',
                region: 'us-east-1'
              },
            });
            
            // Use the CLI's current credentials to determine the target environment:
            // `.account` and `.region` will reflect the account+region the CLI
            // is configured to use (based on the user CLI credentials)
            new Stack(app, 'Stack2', {
              env: {
                account: process.env.CDK_DEFAULT_ACCOUNT,
                region: process.env.CDK_DEFAULT_REGION
              },
            });
            
            // Define multiple stacks stage associated with an environment
            const myStage = new Stage(app, 'MyStage', {
              env: {
                account: '123456789012',
                region: 'us-east-1'
              }
            });
            
            // both of these stacks will use the stage's account/region:
            // `.account` and `.region` will resolve to the concrete values as above
            new MyStack(myStage, 'Stack1');
            new YourStack(myStage, 'Stack2');
            
            // Define an environment-agnostic stack:
            // `.account` and `.region` will resolve to `{ "Ref": "AWS::AccountId" }` and `{ "Ref": "AWS::Region" }` respectively.
            // which will only resolve to actual values by CloudFormation during deployment.
            new MyStack(app, 'Stack1');
        '''
        result = self._values.get("env")
        return typing.cast(typing.Optional[_aws_cdk_ceddda9d.Environment], result)

    @builtins.property
    def notification_arns(self) -> typing.Optional[typing.List[builtins.str]]:
        '''SNS Topic ARNs that will receive stack events.

        :default: - no notfication arns.
        '''
        result = self._values.get("notification_arns")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def permissions_boundary(
        self,
    ) -> typing.Optional[_aws_cdk_ceddda9d.PermissionsBoundary]:
        '''Options for applying a permissions boundary to all IAM Roles and Users created within this Stage.

        :default: - no permissions boundary is applied
        '''
        result = self._values.get("permissions_boundary")
        return typing.cast(typing.Optional[_aws_cdk_ceddda9d.PermissionsBoundary], result)

    @builtins.property
    def stack_name(self) -> typing.Optional[builtins.str]:
        '''Name to deploy the stack with.

        :default: - Derived from construct path.
        '''
        result = self._values.get("stack_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def suppress_template_indentation(self) -> typing.Optional[builtins.bool]:
        '''Enable this flag to suppress indentation in generated CloudFormation templates.

        If not specified, the value of the ``@aws-cdk/core:suppressTemplateIndentation``
        context key will be used. If that is not specified, then the
        default value ``false`` will be used.

        :default: - the value of ``@aws-cdk/core:suppressTemplateIndentation``, or ``false`` if that is not set.
        '''
        result = self._values.get("suppress_template_indentation")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def synthesizer(self) -> typing.Optional[_aws_cdk_ceddda9d.IStackSynthesizer]:
        '''Synthesis method to use while deploying this stack.

        The Stack Synthesizer controls aspects of synthesis and deployment,
        like how assets are referenced and what IAM roles to use. For more
        information, see the README of the main CDK package.

        If not specified, the ``defaultStackSynthesizer`` from ``App`` will be used.
        If that is not specified, ``DefaultStackSynthesizer`` is used if
        ``@aws-cdk/core:newStyleStackSynthesis`` is set to ``true`` or the CDK major
        version is v2. In CDK v1 ``LegacyStackSynthesizer`` is the default if no
        other synthesizer is specified.

        :default: - The synthesizer specified on ``App``, or ``DefaultStackSynthesizer`` otherwise.
        '''
        result = self._values.get("synthesizer")
        return typing.cast(typing.Optional[_aws_cdk_ceddda9d.IStackSynthesizer], result)

    @builtins.property
    def tags(self) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        '''Stack tags that will be applied to all the taggable resources and the stack itself.

        :default: {}
        '''
        result = self._values.get("tags")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], result)

    @builtins.property
    def termination_protection(self) -> typing.Optional[builtins.bool]:
        '''Whether to enable termination protection for this stack.

        :default: false
        '''
        result = self._values.get("termination_protection")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def compliance_log_bucket_name(self) -> builtins.str:
        '''The name of the compliance log bucket to be created.'''
        result = self._values.get("compliance_log_bucket_name")
        assert result is not None, "Required property 'compliance_log_bucket_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def security_group(
        self,
    ) -> typing.Optional[_aws_cdk_aws_ec2_ceddda9d.ISecurityGroup]:
        '''The security group of the vpc.'''
        result = self._values.get("security_group")
        return typing.cast(typing.Optional[_aws_cdk_aws_ec2_ceddda9d.ISecurityGroup], result)

    @builtins.property
    def subnet_selection(
        self,
    ) -> typing.Optional[_aws_cdk_aws_ec2_ceddda9d.SubnetSelection]:
        '''The subnet selection of the vpc.'''
        result = self._values.get("subnet_selection")
        return typing.cast(typing.Optional[_aws_cdk_aws_ec2_ceddda9d.SubnetSelection], result)

    @builtins.property
    def vpc(self) -> typing.Optional[_aws_cdk_aws_ec2_ceddda9d.IVpc]:
        '''The vpc where the ComplianceLogBucket CR Lambda must be attached to.'''
        result = self._values.get("vpc")
        return typing.cast(typing.Optional[_aws_cdk_aws_ec2_ceddda9d.IVpc], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ComplianceLogBucketStackProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdklabs/cdk-cicd-wrapper.DefaultCodeBuildFactoryProps",
    jsii_struct_bases=[],
    name_mapping={
        "application_qualifier": "applicationQualifier",
        "parameter_provider": "parameterProvider",
        "region": "region",
        "res_account": "resAccount",
        "additional_role_policies": "additionalRolePolicies",
        "code_build_env_settings": "codeBuildEnvSettings",
        "install_commands": "installCommands",
        "npm_registry": "npmRegistry",
        "proxy_config": "proxyConfig",
        "vpc": "vpc",
    },
)
class DefaultCodeBuildFactoryProps:
    def __init__(
        self,
        *,
        application_qualifier: builtins.str,
        parameter_provider: "IParameterConstruct",
        region: builtins.str,
        res_account: builtins.str,
        additional_role_policies: typing.Optional[typing.Sequence[_aws_cdk_aws_iam_ceddda9d.PolicyStatement]] = None,
        code_build_env_settings: typing.Optional[typing.Union[_aws_cdk_aws_codebuild_ceddda9d.BuildEnvironment, typing.Dict[builtins.str, typing.Any]]] = None,
        install_commands: typing.Optional[typing.Sequence[builtins.str]] = None,
        npm_registry: typing.Optional[typing.Union["NPMRegistryConfig", typing.Dict[builtins.str, typing.Any]]] = None,
        proxy_config: typing.Optional["IProxyConfig"] = None,
        vpc: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.IVpc] = None,
    ) -> None:
        '''
        :param application_qualifier: The applicationQualifier used for the pipeline.
        :param parameter_provider: Provider for Parameter Store parameters.
        :param region: The AWS region to set.
        :param res_account: The account ID of the RES stage.
        :param additional_role_policies: Additional IAM policy statements to be added to the CodeBuild project role Default value is undefined.
        :param code_build_env_settings: Environment settings for the CodeBuild project Default value is undefined.
        :param install_commands: The install commands to run before the build phase.
        :param npm_registry: Configuration for an NPM registry Default value is undefined.
        :param proxy_config: Configuration for an HTTP proxy Default value is undefined.
        :param vpc: The VPC to use for the CodeBuild project Default value is undefined (no VPC).
        '''
        if isinstance(code_build_env_settings, dict):
            code_build_env_settings = _aws_cdk_aws_codebuild_ceddda9d.BuildEnvironment(**code_build_env_settings)
        if isinstance(npm_registry, dict):
            npm_registry = NPMRegistryConfig(**npm_registry)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__bff0f10e7606a0a87c519b6fcae1d08c136a64f8d8e54d9f80b5e2a05af96b56)
            check_type(argname="argument application_qualifier", value=application_qualifier, expected_type=type_hints["application_qualifier"])
            check_type(argname="argument parameter_provider", value=parameter_provider, expected_type=type_hints["parameter_provider"])
            check_type(argname="argument region", value=region, expected_type=type_hints["region"])
            check_type(argname="argument res_account", value=res_account, expected_type=type_hints["res_account"])
            check_type(argname="argument additional_role_policies", value=additional_role_policies, expected_type=type_hints["additional_role_policies"])
            check_type(argname="argument code_build_env_settings", value=code_build_env_settings, expected_type=type_hints["code_build_env_settings"])
            check_type(argname="argument install_commands", value=install_commands, expected_type=type_hints["install_commands"])
            check_type(argname="argument npm_registry", value=npm_registry, expected_type=type_hints["npm_registry"])
            check_type(argname="argument proxy_config", value=proxy_config, expected_type=type_hints["proxy_config"])
            check_type(argname="argument vpc", value=vpc, expected_type=type_hints["vpc"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "application_qualifier": application_qualifier,
            "parameter_provider": parameter_provider,
            "region": region,
            "res_account": res_account,
        }
        if additional_role_policies is not None:
            self._values["additional_role_policies"] = additional_role_policies
        if code_build_env_settings is not None:
            self._values["code_build_env_settings"] = code_build_env_settings
        if install_commands is not None:
            self._values["install_commands"] = install_commands
        if npm_registry is not None:
            self._values["npm_registry"] = npm_registry
        if proxy_config is not None:
            self._values["proxy_config"] = proxy_config
        if vpc is not None:
            self._values["vpc"] = vpc

    @builtins.property
    def application_qualifier(self) -> builtins.str:
        '''The applicationQualifier used for the pipeline.'''
        result = self._values.get("application_qualifier")
        assert result is not None, "Required property 'application_qualifier' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def parameter_provider(self) -> "IParameterConstruct":
        '''Provider for Parameter Store parameters.'''
        result = self._values.get("parameter_provider")
        assert result is not None, "Required property 'parameter_provider' is missing"
        return typing.cast("IParameterConstruct", result)

    @builtins.property
    def region(self) -> builtins.str:
        '''The AWS region to set.'''
        result = self._values.get("region")
        assert result is not None, "Required property 'region' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def res_account(self) -> builtins.str:
        '''The account ID of the RES stage.'''
        result = self._values.get("res_account")
        assert result is not None, "Required property 'res_account' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def additional_role_policies(
        self,
    ) -> typing.Optional[typing.List[_aws_cdk_aws_iam_ceddda9d.PolicyStatement]]:
        '''Additional IAM policy statements to be added to the CodeBuild project role Default value is undefined.'''
        result = self._values.get("additional_role_policies")
        return typing.cast(typing.Optional[typing.List[_aws_cdk_aws_iam_ceddda9d.PolicyStatement]], result)

    @builtins.property
    def code_build_env_settings(
        self,
    ) -> typing.Optional[_aws_cdk_aws_codebuild_ceddda9d.BuildEnvironment]:
        '''Environment settings for the CodeBuild project Default value is undefined.'''
        result = self._values.get("code_build_env_settings")
        return typing.cast(typing.Optional[_aws_cdk_aws_codebuild_ceddda9d.BuildEnvironment], result)

    @builtins.property
    def install_commands(self) -> typing.Optional[typing.List[builtins.str]]:
        '''The install commands to run before the build phase.'''
        result = self._values.get("install_commands")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def npm_registry(self) -> typing.Optional["NPMRegistryConfig"]:
        '''Configuration for an NPM registry Default value is undefined.'''
        result = self._values.get("npm_registry")
        return typing.cast(typing.Optional["NPMRegistryConfig"], result)

    @builtins.property
    def proxy_config(self) -> typing.Optional["IProxyConfig"]:
        '''Configuration for an HTTP proxy Default value is undefined.'''
        result = self._values.get("proxy_config")
        return typing.cast(typing.Optional["IProxyConfig"], result)

    @builtins.property
    def vpc(self) -> typing.Optional[_aws_cdk_aws_ec2_ceddda9d.IVpc]:
        '''The VPC to use for the CodeBuild project Default value is undefined (no VPC).'''
        result = self._values.get("vpc")
        return typing.cast(typing.Optional[_aws_cdk_aws_ec2_ceddda9d.IVpc], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DefaultCodeBuildFactoryProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdklabs/cdk-cicd-wrapper.DefaultStackProviderOptions",
    jsii_struct_bases=[],
    name_mapping={
        "normalize_stack_names": "normalizeStackNames",
        "provider_name": "providerName",
        "use_application_name": "useApplicationName",
    },
)
class DefaultStackProviderOptions:
    def __init__(
        self,
        *,
        normalize_stack_names: typing.Optional[builtins.bool] = None,
        provider_name: typing.Optional[builtins.str] = None,
        use_application_name: typing.Optional[builtins.bool] = None,
    ) -> None:
        '''Options for the DefaultStackProvider class.

        :param normalize_stack_names: Enable stack name normalization to replace hyphens and forward slashes. Default: false
        :param provider_name: The name of the provider.
        :param use_application_name: Indicates whether to use the application name or not. Default: false
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__879d91301c994b130bf98b102f5dbef2d7de3db448d53f91e484a57446966c75)
            check_type(argname="argument normalize_stack_names", value=normalize_stack_names, expected_type=type_hints["normalize_stack_names"])
            check_type(argname="argument provider_name", value=provider_name, expected_type=type_hints["provider_name"])
            check_type(argname="argument use_application_name", value=use_application_name, expected_type=type_hints["use_application_name"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if normalize_stack_names is not None:
            self._values["normalize_stack_names"] = normalize_stack_names
        if provider_name is not None:
            self._values["provider_name"] = provider_name
        if use_application_name is not None:
            self._values["use_application_name"] = use_application_name

    @builtins.property
    def normalize_stack_names(self) -> typing.Optional[builtins.bool]:
        '''Enable stack name normalization to replace hyphens and forward slashes.

        :default: false
        '''
        result = self._values.get("normalize_stack_names")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def provider_name(self) -> typing.Optional[builtins.str]:
        '''The name of the provider.'''
        result = self._values.get("provider_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def use_application_name(self) -> typing.Optional[builtins.bool]:
        '''Indicates whether to use the application name or not.

        :default: false
        '''
        result = self._values.get("use_application_name")
        return typing.cast(typing.Optional[builtins.bool], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DefaultStackProviderOptions(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdklabs/cdk-cicd-wrapper.DeploymentDefinition",
    jsii_struct_bases=[],
    name_mapping={
        "env": "env",
        "manual_approval_required": "manualApprovalRequired",
        "stacks_providers": "stacksProviders",
        "compliance_log_bucket_name": "complianceLogBucketName",
        "vpc": "vpc",
    },
)
class DeploymentDefinition:
    def __init__(
        self,
        *,
        env: typing.Union["Environment", typing.Dict[builtins.str, typing.Any]],
        manual_approval_required: builtins.bool,
        stacks_providers: typing.Sequence["IStackProvider"],
        compliance_log_bucket_name: typing.Optional[builtins.str] = None,
        vpc: typing.Optional["IVpcConfig"] = None,
    ) -> None:
        '''Represents a deployment definition.

        :param env: The environment for the deployment.
        :param manual_approval_required: Manual approval is required or not. Default: for DEV stage it is false otherwise true
        :param stacks_providers: The stack providers for the deployment.
        :param compliance_log_bucket_name: The complianceLogBucketName Name.
        :param vpc: The VPC configuration for the deployment.
        '''
        if isinstance(env, dict):
            env = Environment(**env)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__999876a0c3379f5aa69e4245b2f46b1895daf317efa1aeff5757edbdc3e84312)
            check_type(argname="argument env", value=env, expected_type=type_hints["env"])
            check_type(argname="argument manual_approval_required", value=manual_approval_required, expected_type=type_hints["manual_approval_required"])
            check_type(argname="argument stacks_providers", value=stacks_providers, expected_type=type_hints["stacks_providers"])
            check_type(argname="argument compliance_log_bucket_name", value=compliance_log_bucket_name, expected_type=type_hints["compliance_log_bucket_name"])
            check_type(argname="argument vpc", value=vpc, expected_type=type_hints["vpc"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "env": env,
            "manual_approval_required": manual_approval_required,
            "stacks_providers": stacks_providers,
        }
        if compliance_log_bucket_name is not None:
            self._values["compliance_log_bucket_name"] = compliance_log_bucket_name
        if vpc is not None:
            self._values["vpc"] = vpc

    @builtins.property
    def env(self) -> "Environment":
        '''The environment for the deployment.'''
        result = self._values.get("env")
        assert result is not None, "Required property 'env' is missing"
        return typing.cast("Environment", result)

    @builtins.property
    def manual_approval_required(self) -> builtins.bool:
        '''Manual approval is required or not.

        :default: for DEV stage it is false otherwise true
        '''
        result = self._values.get("manual_approval_required")
        assert result is not None, "Required property 'manual_approval_required' is missing"
        return typing.cast(builtins.bool, result)

    @builtins.property
    def stacks_providers(self) -> typing.List["IStackProvider"]:
        '''The stack providers for the deployment.'''
        result = self._values.get("stacks_providers")
        assert result is not None, "Required property 'stacks_providers' is missing"
        return typing.cast(typing.List["IStackProvider"], result)

    @builtins.property
    def compliance_log_bucket_name(self) -> typing.Optional[builtins.str]:
        '''The complianceLogBucketName Name.'''
        result = self._values.get("compliance_log_bucket_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def vpc(self) -> typing.Optional["IVpcConfig"]:
        '''The VPC configuration for the deployment.'''
        result = self._values.get("vpc")
        return typing.cast(typing.Optional["IVpcConfig"], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DeploymentDefinition(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdklabs/cdk-cicd-wrapper.DeploymentHookConfig",
    jsii_struct_bases=[],
    name_mapping={"post": "post", "pre": "pre"},
)
class DeploymentHookConfig:
    def __init__(
        self,
        *,
        post: typing.Optional[typing.Sequence[_aws_cdk_pipelines_ceddda9d.Step]] = None,
        pre: typing.Optional[typing.Sequence[_aws_cdk_pipelines_ceddda9d.Step]] = None,
    ) -> None:
        '''Represents the configuration for deployment hooks.

        :param post: The post-deployment steps (optional).
        :param pre: The pre-deployment steps (optional).
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__aac68b76c52f782b91345396d1418c376cefb2aa1f8cb3220a139f1350630c8d)
            check_type(argname="argument post", value=post, expected_type=type_hints["post"])
            check_type(argname="argument pre", value=pre, expected_type=type_hints["pre"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if post is not None:
            self._values["post"] = post
        if pre is not None:
            self._values["pre"] = pre

    @builtins.property
    def post(self) -> typing.Optional[typing.List[_aws_cdk_pipelines_ceddda9d.Step]]:
        '''The post-deployment steps (optional).'''
        result = self._values.get("post")
        return typing.cast(typing.Optional[typing.List[_aws_cdk_pipelines_ceddda9d.Step]], result)

    @builtins.property
    def pre(self) -> typing.Optional[typing.List[_aws_cdk_pipelines_ceddda9d.Step]]:
        '''The pre-deployment steps (optional).'''
        result = self._values.get("pre")
        return typing.cast(typing.Optional[typing.List[_aws_cdk_pipelines_ceddda9d.Step]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DeploymentHookConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class EncryptionStack(
    _aws_cdk_ceddda9d.Stack,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdklabs/cdk-cicd-wrapper.EncryptionStack",
):
    '''A stack that creates a KMS key for encryption and grants the necessary permissions.'''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        application_name: builtins.str,
        stage_name: builtins.str,
        analytics_reporting: typing.Optional[builtins.bool] = None,
        cross_region_references: typing.Optional[builtins.bool] = None,
        description: typing.Optional[builtins.str] = None,
        env: typing.Optional[typing.Union[_aws_cdk_ceddda9d.Environment, typing.Dict[builtins.str, typing.Any]]] = None,
        notification_arns: typing.Optional[typing.Sequence[builtins.str]] = None,
        permissions_boundary: typing.Optional[_aws_cdk_ceddda9d.PermissionsBoundary] = None,
        stack_name: typing.Optional[builtins.str] = None,
        suppress_template_indentation: typing.Optional[builtins.bool] = None,
        synthesizer: typing.Optional[_aws_cdk_ceddda9d.IStackSynthesizer] = None,
        tags: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        termination_protection: typing.Optional[builtins.bool] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param application_name: The name of the application.
        :param stage_name: The name of the stage.
        :param analytics_reporting: Include runtime versioning information in this Stack. Default: ``analyticsReporting`` setting of containing ``App``, or value of 'aws:cdk:version-reporting' context key
        :param cross_region_references: Enable this flag to allow native cross region stack references. Enabling this will create a CloudFormation custom resource in both the producing stack and consuming stack in order to perform the export/import This feature is currently experimental Default: false
        :param description: A description of the stack. Default: - No description.
        :param env: The AWS environment (account/region) where this stack will be deployed. Set the ``region``/``account`` fields of ``env`` to either a concrete value to select the indicated environment (recommended for production stacks), or to the values of environment variables ``CDK_DEFAULT_REGION``/``CDK_DEFAULT_ACCOUNT`` to let the target environment depend on the AWS credentials/configuration that the CDK CLI is executed under (recommended for development stacks). If the ``Stack`` is instantiated inside a ``Stage``, any undefined ``region``/``account`` fields from ``env`` will default to the same field on the encompassing ``Stage``, if configured there. If either ``region`` or ``account`` are not set nor inherited from ``Stage``, the Stack will be considered "*environment-agnostic*"". Environment-agnostic stacks can be deployed to any environment but may not be able to take advantage of all features of the CDK. For example, they will not be able to use environmental context lookups such as ``ec2.Vpc.fromLookup`` and will not automatically translate Service Principals to the right format based on the environment's AWS partition, and other such enhancements. Default: - The environment of the containing ``Stage`` if available, otherwise create the stack will be environment-agnostic.
        :param notification_arns: SNS Topic ARNs that will receive stack events. Default: - no notfication arns.
        :param permissions_boundary: Options for applying a permissions boundary to all IAM Roles and Users created within this Stage. Default: - no permissions boundary is applied
        :param stack_name: Name to deploy the stack with. Default: - Derived from construct path.
        :param suppress_template_indentation: Enable this flag to suppress indentation in generated CloudFormation templates. If not specified, the value of the ``@aws-cdk/core:suppressTemplateIndentation`` context key will be used. If that is not specified, then the default value ``false`` will be used. Default: - the value of ``@aws-cdk/core:suppressTemplateIndentation``, or ``false`` if that is not set.
        :param synthesizer: Synthesis method to use while deploying this stack. The Stack Synthesizer controls aspects of synthesis and deployment, like how assets are referenced and what IAM roles to use. For more information, see the README of the main CDK package. If not specified, the ``defaultStackSynthesizer`` from ``App`` will be used. If that is not specified, ``DefaultStackSynthesizer`` is used if ``@aws-cdk/core:newStyleStackSynthesis`` is set to ``true`` or the CDK major version is v2. In CDK v1 ``LegacyStackSynthesizer`` is the default if no other synthesizer is specified. Default: - The synthesizer specified on ``App``, or ``DefaultStackSynthesizer`` otherwise.
        :param tags: Stack tags that will be applied to all the taggable resources and the stack itself. Default: {}
        :param termination_protection: Whether to enable termination protection for this stack. Default: false
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__38c7f4fd3ab929f5ee80acccce8dc16c2fd2df647519d109ca1eabfae51e8751)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = EncryptionStackProps(
            application_name=application_name,
            stage_name=stage_name,
            analytics_reporting=analytics_reporting,
            cross_region_references=cross_region_references,
            description=description,
            env=env,
            notification_arns=notification_arns,
            permissions_boundary=permissions_boundary,
            stack_name=stack_name,
            suppress_template_indentation=suppress_template_indentation,
            synthesizer=synthesizer,
            tags=tags,
            termination_protection=termination_protection,
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @builtins.property
    @jsii.member(jsii_name="kmsKey")
    def kms_key(self) -> _aws_cdk_aws_kms_ceddda9d.Key:
        '''The KMS key created by this stack.'''
        return typing.cast(_aws_cdk_aws_kms_ceddda9d.Key, jsii.get(self, "kmsKey"))


@jsii.data_type(
    jsii_type="@cdklabs/cdk-cicd-wrapper.EncryptionStackProps",
    jsii_struct_bases=[_aws_cdk_ceddda9d.StackProps],
    name_mapping={
        "analytics_reporting": "analyticsReporting",
        "cross_region_references": "crossRegionReferences",
        "description": "description",
        "env": "env",
        "notification_arns": "notificationArns",
        "permissions_boundary": "permissionsBoundary",
        "stack_name": "stackName",
        "suppress_template_indentation": "suppressTemplateIndentation",
        "synthesizer": "synthesizer",
        "tags": "tags",
        "termination_protection": "terminationProtection",
        "application_name": "applicationName",
        "stage_name": "stageName",
    },
)
class EncryptionStackProps(_aws_cdk_ceddda9d.StackProps):
    def __init__(
        self,
        *,
        analytics_reporting: typing.Optional[builtins.bool] = None,
        cross_region_references: typing.Optional[builtins.bool] = None,
        description: typing.Optional[builtins.str] = None,
        env: typing.Optional[typing.Union[_aws_cdk_ceddda9d.Environment, typing.Dict[builtins.str, typing.Any]]] = None,
        notification_arns: typing.Optional[typing.Sequence[builtins.str]] = None,
        permissions_boundary: typing.Optional[_aws_cdk_ceddda9d.PermissionsBoundary] = None,
        stack_name: typing.Optional[builtins.str] = None,
        suppress_template_indentation: typing.Optional[builtins.bool] = None,
        synthesizer: typing.Optional[_aws_cdk_ceddda9d.IStackSynthesizer] = None,
        tags: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        termination_protection: typing.Optional[builtins.bool] = None,
        application_name: builtins.str,
        stage_name: builtins.str,
    ) -> None:
        '''Properties for the EncryptionStack.

        Defines the configuration options required to create an instance of the EncryptionStack.

        :param analytics_reporting: Include runtime versioning information in this Stack. Default: ``analyticsReporting`` setting of containing ``App``, or value of 'aws:cdk:version-reporting' context key
        :param cross_region_references: Enable this flag to allow native cross region stack references. Enabling this will create a CloudFormation custom resource in both the producing stack and consuming stack in order to perform the export/import This feature is currently experimental Default: false
        :param description: A description of the stack. Default: - No description.
        :param env: The AWS environment (account/region) where this stack will be deployed. Set the ``region``/``account`` fields of ``env`` to either a concrete value to select the indicated environment (recommended for production stacks), or to the values of environment variables ``CDK_DEFAULT_REGION``/``CDK_DEFAULT_ACCOUNT`` to let the target environment depend on the AWS credentials/configuration that the CDK CLI is executed under (recommended for development stacks). If the ``Stack`` is instantiated inside a ``Stage``, any undefined ``region``/``account`` fields from ``env`` will default to the same field on the encompassing ``Stage``, if configured there. If either ``region`` or ``account`` are not set nor inherited from ``Stage``, the Stack will be considered "*environment-agnostic*"". Environment-agnostic stacks can be deployed to any environment but may not be able to take advantage of all features of the CDK. For example, they will not be able to use environmental context lookups such as ``ec2.Vpc.fromLookup`` and will not automatically translate Service Principals to the right format based on the environment's AWS partition, and other such enhancements. Default: - The environment of the containing ``Stage`` if available, otherwise create the stack will be environment-agnostic.
        :param notification_arns: SNS Topic ARNs that will receive stack events. Default: - no notfication arns.
        :param permissions_boundary: Options for applying a permissions boundary to all IAM Roles and Users created within this Stage. Default: - no permissions boundary is applied
        :param stack_name: Name to deploy the stack with. Default: - Derived from construct path.
        :param suppress_template_indentation: Enable this flag to suppress indentation in generated CloudFormation templates. If not specified, the value of the ``@aws-cdk/core:suppressTemplateIndentation`` context key will be used. If that is not specified, then the default value ``false`` will be used. Default: - the value of ``@aws-cdk/core:suppressTemplateIndentation``, or ``false`` if that is not set.
        :param synthesizer: Synthesis method to use while deploying this stack. The Stack Synthesizer controls aspects of synthesis and deployment, like how assets are referenced and what IAM roles to use. For more information, see the README of the main CDK package. If not specified, the ``defaultStackSynthesizer`` from ``App`` will be used. If that is not specified, ``DefaultStackSynthesizer`` is used if ``@aws-cdk/core:newStyleStackSynthesis`` is set to ``true`` or the CDK major version is v2. In CDK v1 ``LegacyStackSynthesizer`` is the default if no other synthesizer is specified. Default: - The synthesizer specified on ``App``, or ``DefaultStackSynthesizer`` otherwise.
        :param tags: Stack tags that will be applied to all the taggable resources and the stack itself. Default: {}
        :param termination_protection: Whether to enable termination protection for this stack. Default: false
        :param application_name: The name of the application.
        :param stage_name: The name of the stage.
        '''
        if isinstance(env, dict):
            env = _aws_cdk_ceddda9d.Environment(**env)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__bf3596ec2168345e555b782e9234fda57f79681275af693c143827db9f54dcce)
            check_type(argname="argument analytics_reporting", value=analytics_reporting, expected_type=type_hints["analytics_reporting"])
            check_type(argname="argument cross_region_references", value=cross_region_references, expected_type=type_hints["cross_region_references"])
            check_type(argname="argument description", value=description, expected_type=type_hints["description"])
            check_type(argname="argument env", value=env, expected_type=type_hints["env"])
            check_type(argname="argument notification_arns", value=notification_arns, expected_type=type_hints["notification_arns"])
            check_type(argname="argument permissions_boundary", value=permissions_boundary, expected_type=type_hints["permissions_boundary"])
            check_type(argname="argument stack_name", value=stack_name, expected_type=type_hints["stack_name"])
            check_type(argname="argument suppress_template_indentation", value=suppress_template_indentation, expected_type=type_hints["suppress_template_indentation"])
            check_type(argname="argument synthesizer", value=synthesizer, expected_type=type_hints["synthesizer"])
            check_type(argname="argument tags", value=tags, expected_type=type_hints["tags"])
            check_type(argname="argument termination_protection", value=termination_protection, expected_type=type_hints["termination_protection"])
            check_type(argname="argument application_name", value=application_name, expected_type=type_hints["application_name"])
            check_type(argname="argument stage_name", value=stage_name, expected_type=type_hints["stage_name"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "application_name": application_name,
            "stage_name": stage_name,
        }
        if analytics_reporting is not None:
            self._values["analytics_reporting"] = analytics_reporting
        if cross_region_references is not None:
            self._values["cross_region_references"] = cross_region_references
        if description is not None:
            self._values["description"] = description
        if env is not None:
            self._values["env"] = env
        if notification_arns is not None:
            self._values["notification_arns"] = notification_arns
        if permissions_boundary is not None:
            self._values["permissions_boundary"] = permissions_boundary
        if stack_name is not None:
            self._values["stack_name"] = stack_name
        if suppress_template_indentation is not None:
            self._values["suppress_template_indentation"] = suppress_template_indentation
        if synthesizer is not None:
            self._values["synthesizer"] = synthesizer
        if tags is not None:
            self._values["tags"] = tags
        if termination_protection is not None:
            self._values["termination_protection"] = termination_protection

    @builtins.property
    def analytics_reporting(self) -> typing.Optional[builtins.bool]:
        '''Include runtime versioning information in this Stack.

        :default:

        ``analyticsReporting`` setting of containing ``App``, or value of
        'aws:cdk:version-reporting' context key
        '''
        result = self._values.get("analytics_reporting")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def cross_region_references(self) -> typing.Optional[builtins.bool]:
        '''Enable this flag to allow native cross region stack references.

        Enabling this will create a CloudFormation custom resource
        in both the producing stack and consuming stack in order to perform the export/import

        This feature is currently experimental

        :default: false
        '''
        result = self._values.get("cross_region_references")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def description(self) -> typing.Optional[builtins.str]:
        '''A description of the stack.

        :default: - No description.
        '''
        result = self._values.get("description")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def env(self) -> typing.Optional[_aws_cdk_ceddda9d.Environment]:
        '''The AWS environment (account/region) where this stack will be deployed.

        Set the ``region``/``account`` fields of ``env`` to either a concrete value to
        select the indicated environment (recommended for production stacks), or to
        the values of environment variables
        ``CDK_DEFAULT_REGION``/``CDK_DEFAULT_ACCOUNT`` to let the target environment
        depend on the AWS credentials/configuration that the CDK CLI is executed
        under (recommended for development stacks).

        If the ``Stack`` is instantiated inside a ``Stage``, any undefined
        ``region``/``account`` fields from ``env`` will default to the same field on the
        encompassing ``Stage``, if configured there.

        If either ``region`` or ``account`` are not set nor inherited from ``Stage``, the
        Stack will be considered "*environment-agnostic*"". Environment-agnostic
        stacks can be deployed to any environment but may not be able to take
        advantage of all features of the CDK. For example, they will not be able to
        use environmental context lookups such as ``ec2.Vpc.fromLookup`` and will not
        automatically translate Service Principals to the right format based on the
        environment's AWS partition, and other such enhancements.

        :default:

        - The environment of the containing ``Stage`` if available,
        otherwise create the stack will be environment-agnostic.

        Example::

            // Use a concrete account and region to deploy this stack to:
            // `.account` and `.region` will simply return these values.
            new Stack(app, 'Stack1', {
              env: {
                account: '123456789012',
                region: 'us-east-1'
              },
            });
            
            // Use the CLI's current credentials to determine the target environment:
            // `.account` and `.region` will reflect the account+region the CLI
            // is configured to use (based on the user CLI credentials)
            new Stack(app, 'Stack2', {
              env: {
                account: process.env.CDK_DEFAULT_ACCOUNT,
                region: process.env.CDK_DEFAULT_REGION
              },
            });
            
            // Define multiple stacks stage associated with an environment
            const myStage = new Stage(app, 'MyStage', {
              env: {
                account: '123456789012',
                region: 'us-east-1'
              }
            });
            
            // both of these stacks will use the stage's account/region:
            // `.account` and `.region` will resolve to the concrete values as above
            new MyStack(myStage, 'Stack1');
            new YourStack(myStage, 'Stack2');
            
            // Define an environment-agnostic stack:
            // `.account` and `.region` will resolve to `{ "Ref": "AWS::AccountId" }` and `{ "Ref": "AWS::Region" }` respectively.
            // which will only resolve to actual values by CloudFormation during deployment.
            new MyStack(app, 'Stack1');
        '''
        result = self._values.get("env")
        return typing.cast(typing.Optional[_aws_cdk_ceddda9d.Environment], result)

    @builtins.property
    def notification_arns(self) -> typing.Optional[typing.List[builtins.str]]:
        '''SNS Topic ARNs that will receive stack events.

        :default: - no notfication arns.
        '''
        result = self._values.get("notification_arns")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def permissions_boundary(
        self,
    ) -> typing.Optional[_aws_cdk_ceddda9d.PermissionsBoundary]:
        '''Options for applying a permissions boundary to all IAM Roles and Users created within this Stage.

        :default: - no permissions boundary is applied
        '''
        result = self._values.get("permissions_boundary")
        return typing.cast(typing.Optional[_aws_cdk_ceddda9d.PermissionsBoundary], result)

    @builtins.property
    def stack_name(self) -> typing.Optional[builtins.str]:
        '''Name to deploy the stack with.

        :default: - Derived from construct path.
        '''
        result = self._values.get("stack_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def suppress_template_indentation(self) -> typing.Optional[builtins.bool]:
        '''Enable this flag to suppress indentation in generated CloudFormation templates.

        If not specified, the value of the ``@aws-cdk/core:suppressTemplateIndentation``
        context key will be used. If that is not specified, then the
        default value ``false`` will be used.

        :default: - the value of ``@aws-cdk/core:suppressTemplateIndentation``, or ``false`` if that is not set.
        '''
        result = self._values.get("suppress_template_indentation")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def synthesizer(self) -> typing.Optional[_aws_cdk_ceddda9d.IStackSynthesizer]:
        '''Synthesis method to use while deploying this stack.

        The Stack Synthesizer controls aspects of synthesis and deployment,
        like how assets are referenced and what IAM roles to use. For more
        information, see the README of the main CDK package.

        If not specified, the ``defaultStackSynthesizer`` from ``App`` will be used.
        If that is not specified, ``DefaultStackSynthesizer`` is used if
        ``@aws-cdk/core:newStyleStackSynthesis`` is set to ``true`` or the CDK major
        version is v2. In CDK v1 ``LegacyStackSynthesizer`` is the default if no
        other synthesizer is specified.

        :default: - The synthesizer specified on ``App``, or ``DefaultStackSynthesizer`` otherwise.
        '''
        result = self._values.get("synthesizer")
        return typing.cast(typing.Optional[_aws_cdk_ceddda9d.IStackSynthesizer], result)

    @builtins.property
    def tags(self) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        '''Stack tags that will be applied to all the taggable resources and the stack itself.

        :default: {}
        '''
        result = self._values.get("tags")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], result)

    @builtins.property
    def termination_protection(self) -> typing.Optional[builtins.bool]:
        '''Whether to enable termination protection for this stack.

        :default: false
        '''
        result = self._values.get("termination_protection")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def application_name(self) -> builtins.str:
        '''The name of the application.'''
        result = self._values.get("application_name")
        assert result is not None, "Required property 'application_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def stage_name(self) -> builtins.str:
        '''The name of the stage.'''
        result = self._values.get("stage_name")
        assert result is not None, "Required property 'stage_name' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "EncryptionStackProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdklabs/cdk-cicd-wrapper.Environment",
    jsii_struct_bases=[],
    name_mapping={"account": "account", "region": "region"},
)
class Environment:
    def __init__(self, *, account: builtins.str, region: builtins.str) -> None:
        '''Represents an environment with an account and region.

        :param account: The account ID.
        :param region: The region.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__16ab79c02fa419c536c6e7e716bb6a0e3c1e64d99da80fae59f90884f09827a1)
            check_type(argname="argument account", value=account, expected_type=type_hints["account"])
            check_type(argname="argument region", value=region, expected_type=type_hints["region"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "account": account,
            "region": region,
        }

    @builtins.property
    def account(self) -> builtins.str:
        '''The account ID.'''
        result = self._values.get("account")
        assert result is not None, "Required property 'account' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def region(self) -> builtins.str:
        '''The region.'''
        result = self._values.get("region")
        assert result is not None, "Required property 'region' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "Environment(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdklabs/cdk-cicd-wrapper.GitHubPipelinePluginOptions",
    jsii_struct_bases=[],
    name_mapping={
        "build_container": "buildContainer",
        "cdk_cli_version": "cdkCliVersion",
        "concurrency": "concurrency",
        "docker_asset_job_settings": "dockerAssetJobSettings",
        "docker_credentials": "dockerCredentials",
        "job_settings": "jobSettings",
        "open_id_connect_provider_arn": "openIdConnectProviderArn",
        "post_build_steps": "postBuildSteps",
        "pre_build_steps": "preBuildSteps",
        "pre_synthed": "preSynthed",
        "publish_assets_auth_region": "publishAssetsAuthRegion",
        "repository_name": "repositoryName",
        "role_name": "roleName",
        "runner": "runner",
        "subject_claims": "subjectClaims",
        "thumbprints": "thumbprints",
        "workflow_name": "workflowName",
        "workflow_path": "workflowPath",
        "workflow_triggers": "workflowTriggers",
    },
)
class GitHubPipelinePluginOptions:
    def __init__(
        self,
        *,
        build_container: typing.Optional[typing.Union[_cdk_pipelines_github_fc0d05f7.ContainerOptions, typing.Dict[builtins.str, typing.Any]]] = None,
        cdk_cli_version: typing.Optional[builtins.str] = None,
        concurrency: typing.Optional[typing.Union[_cdk_pipelines_github_fc0d05f7.ConcurrencyOptions, typing.Dict[builtins.str, typing.Any]]] = None,
        docker_asset_job_settings: typing.Optional[typing.Union[_cdk_pipelines_github_fc0d05f7.DockerAssetJobSettings, typing.Dict[builtins.str, typing.Any]]] = None,
        docker_credentials: typing.Optional[typing.Sequence[_cdk_pipelines_github_fc0d05f7.DockerCredential]] = None,
        job_settings: typing.Optional[typing.Union[_cdk_pipelines_github_fc0d05f7.JobSettings, typing.Dict[builtins.str, typing.Any]]] = None,
        open_id_connect_provider_arn: typing.Optional[builtins.str] = None,
        post_build_steps: typing.Optional[typing.Sequence[typing.Union[_cdk_pipelines_github_fc0d05f7.JobStep, typing.Dict[builtins.str, typing.Any]]]] = None,
        pre_build_steps: typing.Optional[typing.Sequence[typing.Union[_cdk_pipelines_github_fc0d05f7.JobStep, typing.Dict[builtins.str, typing.Any]]]] = None,
        pre_synthed: typing.Optional[builtins.bool] = None,
        publish_assets_auth_region: typing.Optional[builtins.str] = None,
        repository_name: typing.Optional[builtins.str] = None,
        role_name: typing.Optional[builtins.str] = None,
        runner: typing.Optional[_cdk_pipelines_github_fc0d05f7.Runner] = None,
        subject_claims: typing.Optional[typing.Sequence[builtins.str]] = None,
        thumbprints: typing.Optional[typing.Sequence[builtins.str]] = None,
        workflow_name: typing.Optional[builtins.str] = None,
        workflow_path: typing.Optional[builtins.str] = None,
        workflow_triggers: typing.Optional[typing.Union[_cdk_pipelines_github_fc0d05f7.WorkflowTriggers, typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''
        :param build_container: Build container options. Default: - GitHub defaults
        :param cdk_cli_version: Version of the CDK CLI to use. Default: - automatic
        :param concurrency: GitHub workflow concurrency. Default: - no concurrency settings
        :param docker_asset_job_settings: Job level settings applied to all docker asset publishing jobs in the workflow. Default: - no additional settings
        :param docker_credentials: The Docker Credentials to use to login. If you set this variable, you will be logged in to docker when you upload Docker Assets.
        :param job_settings: Job level settings that will be applied to all jobs in the workflow, including synth and asset deploy jobs. Currently the only valid setting is 'if'. You can use this to run jobs only in specific repositories.
        :param open_id_connect_provider_arn: 
        :param post_build_steps: GitHub workflow steps to execute after build. Default: []
        :param pre_build_steps: GitHub workflow steps to execute before build. Default: []
        :param pre_synthed: Indicates if the repository already contains a synthesized ``cdk.out`` directory, in which case we will simply checkout the repo in jobs that require ``cdk.out``. Default: false
        :param publish_assets_auth_region: Will assume the GitHubActionRole in this region when publishing assets. This is NOT the region in which the assets are published. In most cases, you do not have to worry about this property, and can safely ignore it. Default: "us-west-2"
        :param repository_name: 
        :param role_name: 
        :param runner: The type of runner to run the job on. The runner can be either a GitHub-hosted runner or a self-hosted runner. Default: Runner.UBUNTU_LATEST
        :param subject_claims: A list of subject claims allowed to access the IAM role. See https://docs.github.com/en/actions/deployment/security-hardening-your-deployments/about-security-hardening-with-openid-connect A subject claim can include ``*`` and ``?`` wildcards according to the ``StringLike`` condition operator. For example, ``['repo:owner/repo1:ref:refs/heads/branch1', 'repo:owner/repo1:environment:prod']``
        :param thumbprints: Thumbprints of GitHub's certificates. Every time GitHub rotates their certificates, this value will need to be updated. Default value is up-to-date to June 27, 2023 as per https://github.blog/changelog/2023-06-27-github-actions-update-on-oidc-integration-with-aws/ Default: - Use built-in keys
        :param workflow_name: Name of the workflow. Default: "deploy"
        :param workflow_path: File path for the GitHub workflow. Default: ".github/workflows/deploy.yml"
        :param workflow_triggers: GitHub workflow triggers. Default: - By default, workflow is triggered on push to the ``main`` branch and can also be triggered manually (``workflow_dispatch``).
        '''
        if isinstance(build_container, dict):
            build_container = _cdk_pipelines_github_fc0d05f7.ContainerOptions(**build_container)
        if isinstance(concurrency, dict):
            concurrency = _cdk_pipelines_github_fc0d05f7.ConcurrencyOptions(**concurrency)
        if isinstance(docker_asset_job_settings, dict):
            docker_asset_job_settings = _cdk_pipelines_github_fc0d05f7.DockerAssetJobSettings(**docker_asset_job_settings)
        if isinstance(job_settings, dict):
            job_settings = _cdk_pipelines_github_fc0d05f7.JobSettings(**job_settings)
        if isinstance(workflow_triggers, dict):
            workflow_triggers = _cdk_pipelines_github_fc0d05f7.WorkflowTriggers(**workflow_triggers)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a6ec7da65576fb7c11b896d62212c5d7433b3776f713753d7800049328a9fb62)
            check_type(argname="argument build_container", value=build_container, expected_type=type_hints["build_container"])
            check_type(argname="argument cdk_cli_version", value=cdk_cli_version, expected_type=type_hints["cdk_cli_version"])
            check_type(argname="argument concurrency", value=concurrency, expected_type=type_hints["concurrency"])
            check_type(argname="argument docker_asset_job_settings", value=docker_asset_job_settings, expected_type=type_hints["docker_asset_job_settings"])
            check_type(argname="argument docker_credentials", value=docker_credentials, expected_type=type_hints["docker_credentials"])
            check_type(argname="argument job_settings", value=job_settings, expected_type=type_hints["job_settings"])
            check_type(argname="argument open_id_connect_provider_arn", value=open_id_connect_provider_arn, expected_type=type_hints["open_id_connect_provider_arn"])
            check_type(argname="argument post_build_steps", value=post_build_steps, expected_type=type_hints["post_build_steps"])
            check_type(argname="argument pre_build_steps", value=pre_build_steps, expected_type=type_hints["pre_build_steps"])
            check_type(argname="argument pre_synthed", value=pre_synthed, expected_type=type_hints["pre_synthed"])
            check_type(argname="argument publish_assets_auth_region", value=publish_assets_auth_region, expected_type=type_hints["publish_assets_auth_region"])
            check_type(argname="argument repository_name", value=repository_name, expected_type=type_hints["repository_name"])
            check_type(argname="argument role_name", value=role_name, expected_type=type_hints["role_name"])
            check_type(argname="argument runner", value=runner, expected_type=type_hints["runner"])
            check_type(argname="argument subject_claims", value=subject_claims, expected_type=type_hints["subject_claims"])
            check_type(argname="argument thumbprints", value=thumbprints, expected_type=type_hints["thumbprints"])
            check_type(argname="argument workflow_name", value=workflow_name, expected_type=type_hints["workflow_name"])
            check_type(argname="argument workflow_path", value=workflow_path, expected_type=type_hints["workflow_path"])
            check_type(argname="argument workflow_triggers", value=workflow_triggers, expected_type=type_hints["workflow_triggers"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if build_container is not None:
            self._values["build_container"] = build_container
        if cdk_cli_version is not None:
            self._values["cdk_cli_version"] = cdk_cli_version
        if concurrency is not None:
            self._values["concurrency"] = concurrency
        if docker_asset_job_settings is not None:
            self._values["docker_asset_job_settings"] = docker_asset_job_settings
        if docker_credentials is not None:
            self._values["docker_credentials"] = docker_credentials
        if job_settings is not None:
            self._values["job_settings"] = job_settings
        if open_id_connect_provider_arn is not None:
            self._values["open_id_connect_provider_arn"] = open_id_connect_provider_arn
        if post_build_steps is not None:
            self._values["post_build_steps"] = post_build_steps
        if pre_build_steps is not None:
            self._values["pre_build_steps"] = pre_build_steps
        if pre_synthed is not None:
            self._values["pre_synthed"] = pre_synthed
        if publish_assets_auth_region is not None:
            self._values["publish_assets_auth_region"] = publish_assets_auth_region
        if repository_name is not None:
            self._values["repository_name"] = repository_name
        if role_name is not None:
            self._values["role_name"] = role_name
        if runner is not None:
            self._values["runner"] = runner
        if subject_claims is not None:
            self._values["subject_claims"] = subject_claims
        if thumbprints is not None:
            self._values["thumbprints"] = thumbprints
        if workflow_name is not None:
            self._values["workflow_name"] = workflow_name
        if workflow_path is not None:
            self._values["workflow_path"] = workflow_path
        if workflow_triggers is not None:
            self._values["workflow_triggers"] = workflow_triggers

    @builtins.property
    def build_container(
        self,
    ) -> typing.Optional[_cdk_pipelines_github_fc0d05f7.ContainerOptions]:
        '''Build container options.

        :default: - GitHub defaults
        '''
        result = self._values.get("build_container")
        return typing.cast(typing.Optional[_cdk_pipelines_github_fc0d05f7.ContainerOptions], result)

    @builtins.property
    def cdk_cli_version(self) -> typing.Optional[builtins.str]:
        '''Version of the CDK CLI to use.

        :default: - automatic
        '''
        result = self._values.get("cdk_cli_version")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def concurrency(
        self,
    ) -> typing.Optional[_cdk_pipelines_github_fc0d05f7.ConcurrencyOptions]:
        '''GitHub workflow concurrency.

        :default: - no concurrency settings
        '''
        result = self._values.get("concurrency")
        return typing.cast(typing.Optional[_cdk_pipelines_github_fc0d05f7.ConcurrencyOptions], result)

    @builtins.property
    def docker_asset_job_settings(
        self,
    ) -> typing.Optional[_cdk_pipelines_github_fc0d05f7.DockerAssetJobSettings]:
        '''Job level settings applied to all docker asset publishing jobs in the workflow.

        :default: - no additional settings
        '''
        result = self._values.get("docker_asset_job_settings")
        return typing.cast(typing.Optional[_cdk_pipelines_github_fc0d05f7.DockerAssetJobSettings], result)

    @builtins.property
    def docker_credentials(
        self,
    ) -> typing.Optional[typing.List[_cdk_pipelines_github_fc0d05f7.DockerCredential]]:
        '''The Docker Credentials to use to login.

        If you set this variable,
        you will be logged in to docker when you upload Docker Assets.
        '''
        result = self._values.get("docker_credentials")
        return typing.cast(typing.Optional[typing.List[_cdk_pipelines_github_fc0d05f7.DockerCredential]], result)

    @builtins.property
    def job_settings(
        self,
    ) -> typing.Optional[_cdk_pipelines_github_fc0d05f7.JobSettings]:
        '''Job level settings that will be applied to all jobs in the workflow, including synth and asset deploy jobs.

        Currently the only valid setting
        is 'if'. You can use this to run jobs only in specific repositories.

        :see: https://docs.github.com/en/actions/using-workflows/workflow-syntax-for-github-actions#example-only-run-job-for-specific-repository
        '''
        result = self._values.get("job_settings")
        return typing.cast(typing.Optional[_cdk_pipelines_github_fc0d05f7.JobSettings], result)

    @builtins.property
    def open_id_connect_provider_arn(self) -> typing.Optional[builtins.str]:
        result = self._values.get("open_id_connect_provider_arn")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def post_build_steps(
        self,
    ) -> typing.Optional[typing.List[_cdk_pipelines_github_fc0d05f7.JobStep]]:
        '''GitHub workflow steps to execute after build.

        :default: []
        '''
        result = self._values.get("post_build_steps")
        return typing.cast(typing.Optional[typing.List[_cdk_pipelines_github_fc0d05f7.JobStep]], result)

    @builtins.property
    def pre_build_steps(
        self,
    ) -> typing.Optional[typing.List[_cdk_pipelines_github_fc0d05f7.JobStep]]:
        '''GitHub workflow steps to execute before build.

        :default: []
        '''
        result = self._values.get("pre_build_steps")
        return typing.cast(typing.Optional[typing.List[_cdk_pipelines_github_fc0d05f7.JobStep]], result)

    @builtins.property
    def pre_synthed(self) -> typing.Optional[builtins.bool]:
        '''Indicates if the repository already contains a synthesized ``cdk.out`` directory, in which case we will simply checkout the repo in jobs that require ``cdk.out``.

        :default: false
        '''
        result = self._values.get("pre_synthed")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def publish_assets_auth_region(self) -> typing.Optional[builtins.str]:
        '''Will assume the GitHubActionRole in this region when publishing assets.

        This is NOT the region in which the assets are published.

        In most cases, you do not have to worry about this property, and can safely
        ignore it.

        :default: "us-west-2"
        '''
        result = self._values.get("publish_assets_auth_region")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def repository_name(self) -> typing.Optional[builtins.str]:
        result = self._values.get("repository_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def role_name(self) -> typing.Optional[builtins.str]:
        result = self._values.get("role_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def runner(self) -> typing.Optional[_cdk_pipelines_github_fc0d05f7.Runner]:
        '''The type of runner to run the job on.

        The runner can be either a
        GitHub-hosted runner or a self-hosted runner.

        :default: Runner.UBUNTU_LATEST
        '''
        result = self._values.get("runner")
        return typing.cast(typing.Optional[_cdk_pipelines_github_fc0d05f7.Runner], result)

    @builtins.property
    def subject_claims(self) -> typing.Optional[typing.List[builtins.str]]:
        '''A list of subject claims allowed to access the IAM role.

        See https://docs.github.com/en/actions/deployment/security-hardening-your-deployments/about-security-hardening-with-openid-connect
        A subject claim can include ``*`` and ``?`` wildcards according to the ``StringLike``
        condition operator.

        For example, ``['repo:owner/repo1:ref:refs/heads/branch1', 'repo:owner/repo1:environment:prod']``
        '''
        result = self._values.get("subject_claims")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def thumbprints(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Thumbprints of GitHub's certificates.

        Every time GitHub rotates their certificates, this value will need to be updated.

        Default value is up-to-date to June 27, 2023 as per
        https://github.blog/changelog/2023-06-27-github-actions-update-on-oidc-integration-with-aws/

        :default: - Use built-in keys
        '''
        result = self._values.get("thumbprints")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def workflow_name(self) -> typing.Optional[builtins.str]:
        '''Name of the workflow.

        :default: "deploy"
        '''
        result = self._values.get("workflow_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def workflow_path(self) -> typing.Optional[builtins.str]:
        '''File path for the GitHub workflow.

        :default: ".github/workflows/deploy.yml"
        '''
        result = self._values.get("workflow_path")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def workflow_triggers(
        self,
    ) -> typing.Optional[_cdk_pipelines_github_fc0d05f7.WorkflowTriggers]:
        '''GitHub workflow triggers.

        :default:

        - By default, workflow is triggered on push to the ``main`` branch
        and can also be triggered manually (``workflow_dispatch``).
        '''
        result = self._values.get("workflow_triggers")
        return typing.cast(typing.Optional[_cdk_pipelines_github_fc0d05f7.WorkflowTriggers], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "GitHubPipelinePluginOptions(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.enum(jsii_type="@cdklabs/cdk-cicd-wrapper.GlobalResources")
class GlobalResources(enum.Enum):
    '''Enum representing global resources.'''

    REPOSITORY = "REPOSITORY"
    VPC = "VPC"
    PROXY = "PROXY"
    ENCRYPTION = "ENCRYPTION"
    PARAMETER_STORE = "PARAMETER_STORE"
    STAGE_PROVIDER = "STAGE_PROVIDER"
    CODEBUILD_FACTORY = "CODEBUILD_FACTORY"
    COMPLIANCE_BUCKET = "COMPLIANCE_BUCKET"
    PIPELINE = "PIPELINE"
    PHASE = "PHASE"
    HOOK = "HOOK"
    ADDON_STORE = "ADDON_STORE"
    CI_DEFINITION = "CI_DEFINITION"
    LOGGING = "LOGGING"


class Hook(metaclass=jsii.JSIIMeta, jsii_type="@cdklabs/cdk-cicd-wrapper.Hook"):
    def __init__(self) -> None:
        jsii.create(self.__class__, self, [])

    @jsii.member(jsii_name="addPostHook")
    @builtins.classmethod
    def add_post_hook(cls, hook: _aws_cdk_pipelines_ceddda9d.Step) -> None:
        '''
        :param hook: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5e2b9bc3c52f053417c3721aa8305630c0720cf192c9323d73d9be0bc289fbfd)
            check_type(argname="argument hook", value=hook, expected_type=type_hints["hook"])
        return typing.cast(None, jsii.sinvoke(cls, "addPostHook", [hook]))

    @jsii.member(jsii_name="addPreHook")
    @builtins.classmethod
    def add_pre_hook(cls, hook: _aws_cdk_pipelines_ceddda9d.Step) -> None:
        '''
        :param hook: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f73a1ba7c6489e87fc48407aba8b61e9c0e5a5f93e4092cc322069e7f2c5dd66)
            check_type(argname="argument hook", value=hook, expected_type=type_hints["hook"])
        return typing.cast(None, jsii.sinvoke(cls, "addPreHook", [hook]))


@jsii.interface(jsii_type="@cdklabs/cdk-cicd-wrapper.ICIDefinition")
class ICIDefinition(typing_extensions.Protocol):
    @jsii.member(jsii_name="additionalPolicyStatements")
    def additional_policy_statements(
        self,
        policy_statements: typing.Sequence[_aws_cdk_aws_iam_ceddda9d.PolicyStatement],
    ) -> None:
        '''
        :param policy_statements: -
        '''
        ...

    @jsii.member(jsii_name="append")
    def append(
        self,
        partial_build_spec: _aws_cdk_aws_codebuild_ceddda9d.BuildSpec,
    ) -> None:
        '''
        :param partial_build_spec: -
        '''
        ...

    @jsii.member(jsii_name="provideBuildSpec")
    def provide_build_spec(self) -> _aws_cdk_aws_codebuild_ceddda9d.BuildSpec:
        ...

    @jsii.member(jsii_name="provideCodeBuildDefaults")
    def provide_code_build_defaults(
        self,
    ) -> _aws_cdk_pipelines_ceddda9d.CodeBuildOptions:
        ...


class _ICIDefinitionProxy:
    __jsii_type__: typing.ClassVar[str] = "@cdklabs/cdk-cicd-wrapper.ICIDefinition"

    @jsii.member(jsii_name="additionalPolicyStatements")
    def additional_policy_statements(
        self,
        policy_statements: typing.Sequence[_aws_cdk_aws_iam_ceddda9d.PolicyStatement],
    ) -> None:
        '''
        :param policy_statements: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8ca7176508a22cb3577a93b4645cf33b04614c2dc3248b61d34b176dac90562c)
            check_type(argname="argument policy_statements", value=policy_statements, expected_type=type_hints["policy_statements"])
        return typing.cast(None, jsii.invoke(self, "additionalPolicyStatements", [policy_statements]))

    @jsii.member(jsii_name="append")
    def append(
        self,
        partial_build_spec: _aws_cdk_aws_codebuild_ceddda9d.BuildSpec,
    ) -> None:
        '''
        :param partial_build_spec: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3a34c635ac1e3f9a8abe9d73266c9e37b01209f16085b0e3b8175b8ef1b549e9)
            check_type(argname="argument partial_build_spec", value=partial_build_spec, expected_type=type_hints["partial_build_spec"])
        return typing.cast(None, jsii.invoke(self, "append", [partial_build_spec]))

    @jsii.member(jsii_name="provideBuildSpec")
    def provide_build_spec(self) -> _aws_cdk_aws_codebuild_ceddda9d.BuildSpec:
        return typing.cast(_aws_cdk_aws_codebuild_ceddda9d.BuildSpec, jsii.invoke(self, "provideBuildSpec", []))

    @jsii.member(jsii_name="provideCodeBuildDefaults")
    def provide_code_build_defaults(
        self,
    ) -> _aws_cdk_pipelines_ceddda9d.CodeBuildOptions:
        return typing.cast(_aws_cdk_pipelines_ceddda9d.CodeBuildOptions, jsii.invoke(self, "provideCodeBuildDefaults", []))

# Adding a "__jsii_proxy_class__(): typing.Type" function to the interface
typing.cast(typing.Any, ICIDefinition).__jsii_proxy_class__ = lambda : _ICIDefinitionProxy


@jsii.interface(jsii_type="@cdklabs/cdk-cicd-wrapper.ICodeBuildFactory")
class ICodeBuildFactory(typing_extensions.Protocol):
    '''Interface for a factory that provides CodeBuild options for the pipeline.'''

    @jsii.member(jsii_name="provideCodeBuildOptions")
    def provide_code_build_options(
        self,
    ) -> _aws_cdk_pipelines_ceddda9d.CodeBuildOptions:
        '''Provides the CodeBuild options for the pipeline.

        :return: The CodeBuildOptions object containing options for the CodeBuild project
        '''
        ...


class _ICodeBuildFactoryProxy:
    '''Interface for a factory that provides CodeBuild options for the pipeline.'''

    __jsii_type__: typing.ClassVar[str] = "@cdklabs/cdk-cicd-wrapper.ICodeBuildFactory"

    @jsii.member(jsii_name="provideCodeBuildOptions")
    def provide_code_build_options(
        self,
    ) -> _aws_cdk_pipelines_ceddda9d.CodeBuildOptions:
        '''Provides the CodeBuild options for the pipeline.

        :return: The CodeBuildOptions object containing options for the CodeBuild project
        '''
        return typing.cast(_aws_cdk_pipelines_ceddda9d.CodeBuildOptions, jsii.invoke(self, "provideCodeBuildOptions", []))

# Adding a "__jsii_proxy_class__(): typing.Type" function to the interface
typing.cast(typing.Any, ICodeBuildFactory).__jsii_proxy_class__ = lambda : _ICodeBuildFactoryProxy


@jsii.interface(jsii_type="@cdklabs/cdk-cicd-wrapper.IComplianceBucket")
class IComplianceBucket(typing_extensions.Protocol):
    '''Compliance Bucket configuration interface.

    This interface defines the configuration properties for a compliance bucket.
    '''

    @builtins.property
    @jsii.member(jsii_name="bucketName")
    def bucket_name(self) -> builtins.str:
        '''The name of the compliance bucket.'''
        ...


class _IComplianceBucketProxy:
    '''Compliance Bucket configuration interface.

    This interface defines the configuration properties for a compliance bucket.
    '''

    __jsii_type__: typing.ClassVar[str] = "@cdklabs/cdk-cicd-wrapper.IComplianceBucket"

    @builtins.property
    @jsii.member(jsii_name="bucketName")
    def bucket_name(self) -> builtins.str:
        '''The name of the compliance bucket.'''
        return typing.cast(builtins.str, jsii.get(self, "bucketName"))

# Adding a "__jsii_proxy_class__(): typing.Type" function to the interface
typing.cast(typing.Any, IComplianceBucket).__jsii_proxy_class__ = lambda : _IComplianceBucketProxy


@jsii.interface(jsii_type="@cdklabs/cdk-cicd-wrapper.IDeploymentHookConfigProvider")
class IDeploymentHookConfigProvider(typing_extensions.Protocol):
    @builtins.property
    @jsii.member(jsii_name="config")
    def config(self) -> DeploymentHookConfig:
        ...

    @jsii.member(jsii_name="addPostHook")
    def add_post_hook(self, hook: _aws_cdk_pipelines_ceddda9d.Step) -> None:
        '''
        :param hook: -
        '''
        ...

    @jsii.member(jsii_name="addPreHook")
    def add_pre_hook(self, hook: _aws_cdk_pipelines_ceddda9d.Step) -> None:
        '''
        :param hook: -
        '''
        ...


class _IDeploymentHookConfigProviderProxy:
    __jsii_type__: typing.ClassVar[str] = "@cdklabs/cdk-cicd-wrapper.IDeploymentHookConfigProvider"

    @builtins.property
    @jsii.member(jsii_name="config")
    def config(self) -> DeploymentHookConfig:
        return typing.cast(DeploymentHookConfig, jsii.get(self, "config"))

    @jsii.member(jsii_name="addPostHook")
    def add_post_hook(self, hook: _aws_cdk_pipelines_ceddda9d.Step) -> None:
        '''
        :param hook: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4e38b5a9769ad5e10befcdb5f024343ce008d3d7cf81d6fed1986e7f4b9e9ba2)
            check_type(argname="argument hook", value=hook, expected_type=type_hints["hook"])
        return typing.cast(None, jsii.invoke(self, "addPostHook", [hook]))

    @jsii.member(jsii_name="addPreHook")
    def add_pre_hook(self, hook: _aws_cdk_pipelines_ceddda9d.Step) -> None:
        '''
        :param hook: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0a60bb57fecf6818ab286e39d1a1d3e6f4aff613aa3ff7fc917a9fbebc54a7c2)
            check_type(argname="argument hook", value=hook, expected_type=type_hints["hook"])
        return typing.cast(None, jsii.invoke(self, "addPreHook", [hook]))

# Adding a "__jsii_proxy_class__(): typing.Type" function to the interface
typing.cast(typing.Any, IDeploymentHookConfigProvider).__jsii_proxy_class__ = lambda : _IDeploymentHookConfigProviderProxy


@jsii.interface(jsii_type="@cdklabs/cdk-cicd-wrapper.IEncryptionKey")
class IEncryptionKey(_constructs_77d1e7e8.IConstruct, typing_extensions.Protocol):
    '''Interface representing a construct for supplying an encryption key.'''

    @builtins.property
    @jsii.member(jsii_name="kmsKey")
    def kms_key(self) -> _aws_cdk_aws_kms_ceddda9d.Key:
        '''The KMS Key used for encryption.'''
        ...


class _IEncryptionKeyProxy(
    jsii.proxy_for(_constructs_77d1e7e8.IConstruct), # type: ignore[misc]
):
    '''Interface representing a construct for supplying an encryption key.'''

    __jsii_type__: typing.ClassVar[str] = "@cdklabs/cdk-cicd-wrapper.IEncryptionKey"

    @builtins.property
    @jsii.member(jsii_name="kmsKey")
    def kms_key(self) -> _aws_cdk_aws_kms_ceddda9d.Key:
        '''The KMS Key used for encryption.'''
        return typing.cast(_aws_cdk_aws_kms_ceddda9d.Key, jsii.get(self, "kmsKey"))

# Adding a "__jsii_proxy_class__(): typing.Type" function to the interface
typing.cast(typing.Any, IEncryptionKey).__jsii_proxy_class__ = lambda : _IEncryptionKeyProxy


@jsii.interface(jsii_type="@cdklabs/cdk-cicd-wrapper.ILambdaDLQPluginProps")
class ILambdaDLQPluginProps(typing_extensions.Protocol):
    @builtins.property
    @jsii.member(jsii_name="retentionPeriod")
    def retention_period(self) -> typing.Optional[_aws_cdk_ceddda9d.Duration]:
        '''The retentionPeriod for the DLQ.'''
        ...

    @retention_period.setter
    def retention_period(
        self,
        value: typing.Optional[_aws_cdk_ceddda9d.Duration],
    ) -> None:
        ...


class _ILambdaDLQPluginPropsProxy:
    __jsii_type__: typing.ClassVar[str] = "@cdklabs/cdk-cicd-wrapper.ILambdaDLQPluginProps"

    @builtins.property
    @jsii.member(jsii_name="retentionPeriod")
    def retention_period(self) -> typing.Optional[_aws_cdk_ceddda9d.Duration]:
        '''The retentionPeriod for the DLQ.'''
        return typing.cast(typing.Optional[_aws_cdk_ceddda9d.Duration], jsii.get(self, "retentionPeriod"))

    @retention_period.setter
    def retention_period(
        self,
        value: typing.Optional[_aws_cdk_ceddda9d.Duration],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__77be351f74bdc1d9aa8d3b24592f69235ed8c7b3b241a48df933f1a0b25f3d9a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "retentionPeriod", value) # pyright: ignore[reportArgumentType]

# Adding a "__jsii_proxy_class__(): typing.Type" function to the interface
typing.cast(typing.Any, ILambdaDLQPluginProps).__jsii_proxy_class__ = lambda : _ILambdaDLQPluginPropsProxy


@jsii.interface(jsii_type="@cdklabs/cdk-cicd-wrapper.ILogger")
class ILogger(typing_extensions.Protocol):
    @jsii.member(jsii_name="error")
    def error(
        self,
        message: builtins.str,
        on: typing.Optional[_constructs_77d1e7e8.IConstruct] = None,
    ) -> None:
        '''
        :param message: -
        :param on: -
        '''
        ...

    @jsii.member(jsii_name="info")
    def info(
        self,
        message: builtins.str,
        on: typing.Optional[_constructs_77d1e7e8.IConstruct] = None,
    ) -> None:
        '''
        :param message: -
        :param on: -
        '''
        ...

    @jsii.member(jsii_name="warning")
    def warning(
        self,
        message: builtins.str,
        on: typing.Optional[_constructs_77d1e7e8.IConstruct] = None,
    ) -> None:
        '''
        :param message: -
        :param on: -
        '''
        ...


class _ILoggerProxy:
    __jsii_type__: typing.ClassVar[str] = "@cdklabs/cdk-cicd-wrapper.ILogger"

    @jsii.member(jsii_name="error")
    def error(
        self,
        message: builtins.str,
        on: typing.Optional[_constructs_77d1e7e8.IConstruct] = None,
    ) -> None:
        '''
        :param message: -
        :param on: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__542e1655521dfb9d0015022e610e443ae7a3cab28a1954b773273bc7f4c802e7)
            check_type(argname="argument message", value=message, expected_type=type_hints["message"])
            check_type(argname="argument on", value=on, expected_type=type_hints["on"])
        return typing.cast(None, jsii.invoke(self, "error", [message, on]))

    @jsii.member(jsii_name="info")
    def info(
        self,
        message: builtins.str,
        on: typing.Optional[_constructs_77d1e7e8.IConstruct] = None,
    ) -> None:
        '''
        :param message: -
        :param on: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3318d9da2949330eb99da5d1d63de125d49cb94b4d896faae8cedc4fa560becf)
            check_type(argname="argument message", value=message, expected_type=type_hints["message"])
            check_type(argname="argument on", value=on, expected_type=type_hints["on"])
        return typing.cast(None, jsii.invoke(self, "info", [message, on]))

    @jsii.member(jsii_name="warning")
    def warning(
        self,
        message: builtins.str,
        on: typing.Optional[_constructs_77d1e7e8.IConstruct] = None,
    ) -> None:
        '''
        :param message: -
        :param on: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e17d7ae556b313f3fd1389a85e577e38787f8cd2d7f76d0adedc932d0c838443)
            check_type(argname="argument message", value=message, expected_type=type_hints["message"])
            check_type(argname="argument on", value=on, expected_type=type_hints["on"])
        return typing.cast(None, jsii.invoke(self, "warning", [message, on]))

# Adding a "__jsii_proxy_class__(): typing.Type" function to the interface
typing.cast(typing.Any, ILogger).__jsii_proxy_class__ = lambda : _ILoggerProxy


@jsii.interface(jsii_type="@cdklabs/cdk-cicd-wrapper.IManagedVpcConfig")
class IManagedVpcConfig(typing_extensions.Protocol):
    '''VPC Configuration for new VPC.'''

    @builtins.property
    @jsii.member(jsii_name="cidrBlock")
    def cidr_block(self) -> builtins.str:
        '''CIDR block for the VPC.

        default is: 172.31.0.0/20
        '''
        ...

    @cidr_block.setter
    def cidr_block(self, value: builtins.str) -> None:
        ...

    @builtins.property
    @jsii.member(jsii_name="maxAzs")
    def max_azs(self) -> jsii.Number:
        '''Max AZs.

        default is: 2
        '''
        ...

    @max_azs.setter
    def max_azs(self, value: jsii.Number) -> None:
        ...

    @builtins.property
    @jsii.member(jsii_name="subnetCidrMask")
    def subnet_cidr_mask(self) -> jsii.Number:
        '''Subnets CIDR masks.

        default is: 24
        '''
        ...

    @subnet_cidr_mask.setter
    def subnet_cidr_mask(self, value: jsii.Number) -> None:
        ...


class _IManagedVpcConfigProxy:
    '''VPC Configuration for new VPC.'''

    __jsii_type__: typing.ClassVar[str] = "@cdklabs/cdk-cicd-wrapper.IManagedVpcConfig"

    @builtins.property
    @jsii.member(jsii_name="cidrBlock")
    def cidr_block(self) -> builtins.str:
        '''CIDR block for the VPC.

        default is: 172.31.0.0/20
        '''
        return typing.cast(builtins.str, jsii.get(self, "cidrBlock"))

    @cidr_block.setter
    def cidr_block(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__50a2cc20300c757258682193b62ea04043ea0368b9031fa5eccb8b785ffd73fc)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "cidrBlock", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="maxAzs")
    def max_azs(self) -> jsii.Number:
        '''Max AZs.

        default is: 2
        '''
        return typing.cast(jsii.Number, jsii.get(self, "maxAzs"))

    @max_azs.setter
    def max_azs(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2cb3175d7f2fc722b6ad91b7a384bd93f61754432ba397bb1b90b464f20fe1fa)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "maxAzs", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="subnetCidrMask")
    def subnet_cidr_mask(self) -> jsii.Number:
        '''Subnets CIDR masks.

        default is: 24
        '''
        return typing.cast(jsii.Number, jsii.get(self, "subnetCidrMask"))

    @subnet_cidr_mask.setter
    def subnet_cidr_mask(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__17da2a9a1c9b7838abc12539c72e276d381f752d01c5ca6d3326ce372ab8c70b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "subnetCidrMask", value) # pyright: ignore[reportArgumentType]

# Adding a "__jsii_proxy_class__(): typing.Type" function to the interface
typing.cast(typing.Any, IManagedVpcConfig).__jsii_proxy_class__ = lambda : _IManagedVpcConfigProxy


@jsii.interface(jsii_type="@cdklabs/cdk-cicd-wrapper.IParameterConstruct")
class IParameterConstruct(_constructs_77d1e7e8.IConstruct, typing_extensions.Protocol):
    '''Construct to supply persistent parameters for IaaC code.'''

    @jsii.member(jsii_name="createParameter")
    def create_parameter(
        self,
        parameter_name: builtins.str,
        parameter_value: builtins.str,
    ) -> _aws_cdk_aws_ssm_ceddda9d.IStringParameter:
        '''Create a parameter that is accessible through the pipeline.

        :param parameter_name: - name of the parameter.
        :param parameter_value: - value of the parameter.
        '''
        ...

    @jsii.member(jsii_name="provideParameterPolicyStatement")
    def provide_parameter_policy_statement(
        self,
    ) -> _aws_cdk_aws_iam_ceddda9d.PolicyStatement:
        '''Returns with a policy that allows access to the parameters.'''
        ...


class _IParameterConstructProxy(
    jsii.proxy_for(_constructs_77d1e7e8.IConstruct), # type: ignore[misc]
):
    '''Construct to supply persistent parameters for IaaC code.'''

    __jsii_type__: typing.ClassVar[str] = "@cdklabs/cdk-cicd-wrapper.IParameterConstruct"

    @jsii.member(jsii_name="createParameter")
    def create_parameter(
        self,
        parameter_name: builtins.str,
        parameter_value: builtins.str,
    ) -> _aws_cdk_aws_ssm_ceddda9d.IStringParameter:
        '''Create a parameter that is accessible through the pipeline.

        :param parameter_name: - name of the parameter.
        :param parameter_value: - value of the parameter.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5fee80111a77172c533d99c1978fc9affa7ad9185f9969ba4c8a2c0624a9abdc)
            check_type(argname="argument parameter_name", value=parameter_name, expected_type=type_hints["parameter_name"])
            check_type(argname="argument parameter_value", value=parameter_value, expected_type=type_hints["parameter_value"])
        return typing.cast(_aws_cdk_aws_ssm_ceddda9d.IStringParameter, jsii.invoke(self, "createParameter", [parameter_name, parameter_value]))

    @jsii.member(jsii_name="provideParameterPolicyStatement")
    def provide_parameter_policy_statement(
        self,
    ) -> _aws_cdk_aws_iam_ceddda9d.PolicyStatement:
        '''Returns with a policy that allows access to the parameters.'''
        return typing.cast(_aws_cdk_aws_iam_ceddda9d.PolicyStatement, jsii.invoke(self, "provideParameterPolicyStatement", []))

# Adding a "__jsii_proxy_class__(): typing.Type" function to the interface
typing.cast(typing.Any, IParameterConstruct).__jsii_proxy_class__ = lambda : _IParameterConstructProxy


@jsii.interface(jsii_type="@cdklabs/cdk-cicd-wrapper.IPhaseCommand")
class IPhaseCommand(typing_extensions.Protocol):
    '''Represents a phase command.'''

    @builtins.property
    @jsii.member(jsii_name="command")
    def command(self) -> builtins.str:
        '''The command to run during the phase.'''
        ...


class _IPhaseCommandProxy:
    '''Represents a phase command.'''

    __jsii_type__: typing.ClassVar[str] = "@cdklabs/cdk-cicd-wrapper.IPhaseCommand"

    @builtins.property
    @jsii.member(jsii_name="command")
    def command(self) -> builtins.str:
        '''The command to run during the phase.'''
        return typing.cast(builtins.str, jsii.get(self, "command"))

# Adding a "__jsii_proxy_class__(): typing.Type" function to the interface
typing.cast(typing.Any, IPhaseCommand).__jsii_proxy_class__ = lambda : _IPhaseCommandProxy


@jsii.interface(jsii_type="@cdklabs/cdk-cicd-wrapper.IPhaseCommandSettings")
class IPhaseCommandSettings(typing_extensions.Protocol):
    '''Setting the list of commands for the phases.'''

    @jsii.member(jsii_name="getCommands")
    def get_commands(self, *phases: "PipelinePhases") -> typing.List[builtins.str]:
        '''Returns the list of commands for the specified phases.

        :param phases: The phases for which commands are needed.

        :return: The list of commands for the specified phases.
        '''
        ...


class _IPhaseCommandSettingsProxy:
    '''Setting the list of commands for the phases.'''

    __jsii_type__: typing.ClassVar[str] = "@cdklabs/cdk-cicd-wrapper.IPhaseCommandSettings"

    @jsii.member(jsii_name="getCommands")
    def get_commands(self, *phases: "PipelinePhases") -> typing.List[builtins.str]:
        '''Returns the list of commands for the specified phases.

        :param phases: The phases for which commands are needed.

        :return: The list of commands for the specified phases.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9827465564253a29afb24e4bd204809318dd1f35375199c9e6b05f3fb9ef64b0)
            check_type(argname="argument phases", value=phases, expected_type=typing.Tuple[type_hints["phases"], ...]) # pyright: ignore [reportGeneralTypeIssues]
        return typing.cast(typing.List[builtins.str], jsii.invoke(self, "getCommands", [*phases]))

# Adding a "__jsii_proxy_class__(): typing.Type" function to the interface
typing.cast(typing.Any, IPhaseCommandSettings).__jsii_proxy_class__ = lambda : _IPhaseCommandSettingsProxy


@jsii.interface(jsii_type="@cdklabs/cdk-cicd-wrapper.IPipelineConfig")
class IPipelineConfig(typing_extensions.Protocol):
    '''Represents the configuration for a vanilla pipeline.'''

    @builtins.property
    @jsii.member(jsii_name="applicationName")
    def application_name(self) -> builtins.str:
        '''The name of the application.'''
        ...

    @application_name.setter
    def application_name(self, value: builtins.str) -> None:
        ...

    @builtins.property
    @jsii.member(jsii_name="applicationQualifier")
    def application_qualifier(self) -> builtins.str:
        '''The qualifier for the application.'''
        ...

    @application_qualifier.setter
    def application_qualifier(self, value: builtins.str) -> None:
        ...

    @builtins.property
    @jsii.member(jsii_name="codeBuildEnvSettings")
    def code_build_env_settings(
        self,
    ) -> _aws_cdk_aws_codebuild_ceddda9d.BuildEnvironment:
        '''The environment settings for CodeBuild.'''
        ...

    @code_build_env_settings.setter
    def code_build_env_settings(
        self,
        value: _aws_cdk_aws_codebuild_ceddda9d.BuildEnvironment,
    ) -> None:
        ...

    @builtins.property
    @jsii.member(jsii_name="deploymentDefinition")
    def deployment_definition(
        self,
    ) -> typing.Mapping[builtins.str, DeploymentDefinition]:
        '''The deployment definition for each stage.'''
        ...

    @deployment_definition.setter
    def deployment_definition(
        self,
        value: typing.Mapping[builtins.str, DeploymentDefinition],
    ) -> None:
        ...

    @builtins.property
    @jsii.member(jsii_name="logRetentionInDays")
    def log_retention_in_days(self) -> builtins.str:
        '''The number of days to retain logs.'''
        ...

    @log_retention_in_days.setter
    def log_retention_in_days(self, value: builtins.str) -> None:
        ...

    @builtins.property
    @jsii.member(jsii_name="phases")
    def phases(self) -> "IPipelinePhases":
        '''The phases in the pipeline.'''
        ...

    @phases.setter
    def phases(self, value: "IPipelinePhases") -> None:
        ...

    @builtins.property
    @jsii.member(jsii_name="primaryOutputDirectory")
    def primary_output_directory(self) -> builtins.str:
        '''The primary output directory for the pipeline.'''
        ...

    @primary_output_directory.setter
    def primary_output_directory(self, value: builtins.str) -> None:
        ...

    @builtins.property
    @jsii.member(jsii_name="buildOptions")
    def build_options(self) -> typing.Optional[BuildOptions]:
        '''Additional buildOptions.'''
        ...

    @build_options.setter
    def build_options(self, value: typing.Optional[BuildOptions]) -> None:
        ...

    @builtins.property
    @jsii.member(jsii_name="buildSpec")
    def build_spec(self) -> typing.Optional[_aws_cdk_aws_codebuild_ceddda9d.BuildSpec]:
        '''The build specification for the Synth phase.

        The buildSpec takes precedence over the phases.
        '''
        ...

    @build_spec.setter
    def build_spec(
        self,
        value: typing.Optional[_aws_cdk_aws_codebuild_ceddda9d.BuildSpec],
    ) -> None:
        ...

    @builtins.property
    @jsii.member(jsii_name="codeGuruScanThreshold")
    def code_guru_scan_threshold(self) -> typing.Optional[CodeGuruSeverityThreshold]:
        '''The severity threshold for CodeGuru scans (optional).'''
        ...

    @code_guru_scan_threshold.setter
    def code_guru_scan_threshold(
        self,
        value: typing.Optional[CodeGuruSeverityThreshold],
    ) -> None:
        ...

    @builtins.property
    @jsii.member(jsii_name="npmRegistry")
    def npm_registry(self) -> typing.Optional["NPMRegistryConfig"]:
        '''The configuration for the NPM registry (optional).'''
        ...

    @npm_registry.setter
    def npm_registry(self, value: typing.Optional["NPMRegistryConfig"]) -> None:
        ...

    @builtins.property
    @jsii.member(jsii_name="pipelineOptions")
    def pipeline_options(self) -> typing.Optional["PipelineOptions"]:
        '''Additional pipelineOptions.'''
        ...

    @pipeline_options.setter
    def pipeline_options(self, value: typing.Optional["PipelineOptions"]) -> None:
        ...

    @builtins.property
    @jsii.member(jsii_name="repositorySource")
    def repository_source(self) -> typing.Optional["RepositorySource"]:
        '''The repository source for the pipeline.'''
        ...

    @repository_source.setter
    def repository_source(self, value: typing.Optional["RepositorySource"]) -> None:
        ...

    @builtins.property
    @jsii.member(jsii_name="workbench")
    def workbench(self) -> typing.Optional["WorkbenchConfig"]:
        '''The configuration for the workbench (optional).'''
        ...

    @workbench.setter
    def workbench(self, value: typing.Optional["WorkbenchConfig"]) -> None:
        ...


class _IPipelineConfigProxy:
    '''Represents the configuration for a vanilla pipeline.'''

    __jsii_type__: typing.ClassVar[str] = "@cdklabs/cdk-cicd-wrapper.IPipelineConfig"

    @builtins.property
    @jsii.member(jsii_name="applicationName")
    def application_name(self) -> builtins.str:
        '''The name of the application.'''
        return typing.cast(builtins.str, jsii.get(self, "applicationName"))

    @application_name.setter
    def application_name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ac21a8ef1a621af75f9fab526106bbceb4aefa596dcfc4e0232123329d831c72)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "applicationName", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="applicationQualifier")
    def application_qualifier(self) -> builtins.str:
        '''The qualifier for the application.'''
        return typing.cast(builtins.str, jsii.get(self, "applicationQualifier"))

    @application_qualifier.setter
    def application_qualifier(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7fe8c9486db1a4fee462a7e9cd2567bb977e4a3d40b6693b74ecef1fec175938)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "applicationQualifier", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="codeBuildEnvSettings")
    def code_build_env_settings(
        self,
    ) -> _aws_cdk_aws_codebuild_ceddda9d.BuildEnvironment:
        '''The environment settings for CodeBuild.'''
        return typing.cast(_aws_cdk_aws_codebuild_ceddda9d.BuildEnvironment, jsii.get(self, "codeBuildEnvSettings"))

    @code_build_env_settings.setter
    def code_build_env_settings(
        self,
        value: _aws_cdk_aws_codebuild_ceddda9d.BuildEnvironment,
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__82c7ae901f54587ddb19d2d4a3daca6a3842def49e2e1da1d6edd8f9b954f9fd)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "codeBuildEnvSettings", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="deploymentDefinition")
    def deployment_definition(
        self,
    ) -> typing.Mapping[builtins.str, DeploymentDefinition]:
        '''The deployment definition for each stage.'''
        return typing.cast(typing.Mapping[builtins.str, DeploymentDefinition], jsii.get(self, "deploymentDefinition"))

    @deployment_definition.setter
    def deployment_definition(
        self,
        value: typing.Mapping[builtins.str, DeploymentDefinition],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8dc5710d462f0e42105a4b72c65820f51a4c9f0b668ac3e2eb01fb0081afa90a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "deploymentDefinition", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="logRetentionInDays")
    def log_retention_in_days(self) -> builtins.str:
        '''The number of days to retain logs.'''
        return typing.cast(builtins.str, jsii.get(self, "logRetentionInDays"))

    @log_retention_in_days.setter
    def log_retention_in_days(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d6be3e88255ba58405c48da5f4389446b865e3b5457e8f98dbea9c7b8c98167d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "logRetentionInDays", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="phases")
    def phases(self) -> "IPipelinePhases":
        '''The phases in the pipeline.'''
        return typing.cast("IPipelinePhases", jsii.get(self, "phases"))

    @phases.setter
    def phases(self, value: "IPipelinePhases") -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__30669fd3818c6b466c688d5608bfeb950055e0227f66dd176c5554c2ff065d87)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "phases", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="primaryOutputDirectory")
    def primary_output_directory(self) -> builtins.str:
        '''The primary output directory for the pipeline.'''
        return typing.cast(builtins.str, jsii.get(self, "primaryOutputDirectory"))

    @primary_output_directory.setter
    def primary_output_directory(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ec731bcac61bf306eb4427799ffc86a8f892b71d643afffa11bc02d90434d58b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "primaryOutputDirectory", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="buildOptions")
    def build_options(self) -> typing.Optional[BuildOptions]:
        '''Additional buildOptions.'''
        return typing.cast(typing.Optional[BuildOptions], jsii.get(self, "buildOptions"))

    @build_options.setter
    def build_options(self, value: typing.Optional[BuildOptions]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__526bfd98bbde27a6d1545002d8d91bb55a8f10596cf8df91996c097469154ebb)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "buildOptions", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="buildSpec")
    def build_spec(self) -> typing.Optional[_aws_cdk_aws_codebuild_ceddda9d.BuildSpec]:
        '''The build specification for the Synth phase.

        The buildSpec takes precedence over the phases.
        '''
        return typing.cast(typing.Optional[_aws_cdk_aws_codebuild_ceddda9d.BuildSpec], jsii.get(self, "buildSpec"))

    @build_spec.setter
    def build_spec(
        self,
        value: typing.Optional[_aws_cdk_aws_codebuild_ceddda9d.BuildSpec],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3c056af3b7aac401e23c5be3a1c6d9eea34bb543add73eef7c6d5d7afa32d6ba)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "buildSpec", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="codeGuruScanThreshold")
    def code_guru_scan_threshold(self) -> typing.Optional[CodeGuruSeverityThreshold]:
        '''The severity threshold for CodeGuru scans (optional).'''
        return typing.cast(typing.Optional[CodeGuruSeverityThreshold], jsii.get(self, "codeGuruScanThreshold"))

    @code_guru_scan_threshold.setter
    def code_guru_scan_threshold(
        self,
        value: typing.Optional[CodeGuruSeverityThreshold],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9bd62c07b36992dacbf46dcfedad6ad0d0cd1528ff4b2f31927e25d5537a2a02)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "codeGuruScanThreshold", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="npmRegistry")
    def npm_registry(self) -> typing.Optional["NPMRegistryConfig"]:
        '''The configuration for the NPM registry (optional).'''
        return typing.cast(typing.Optional["NPMRegistryConfig"], jsii.get(self, "npmRegistry"))

    @npm_registry.setter
    def npm_registry(self, value: typing.Optional["NPMRegistryConfig"]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3c082033088fdf175de944baef880cfbf7fca7751fa7a5a18dbb95b0b4ada9bb)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "npmRegistry", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="pipelineOptions")
    def pipeline_options(self) -> typing.Optional["PipelineOptions"]:
        '''Additional pipelineOptions.'''
        return typing.cast(typing.Optional["PipelineOptions"], jsii.get(self, "pipelineOptions"))

    @pipeline_options.setter
    def pipeline_options(self, value: typing.Optional["PipelineOptions"]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5ebc5edfa8c4cd954d295925b9c796bb6a5456ce28520c943bc3a389a777c112)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "pipelineOptions", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="repositorySource")
    def repository_source(self) -> typing.Optional["RepositorySource"]:
        '''The repository source for the pipeline.'''
        return typing.cast(typing.Optional["RepositorySource"], jsii.get(self, "repositorySource"))

    @repository_source.setter
    def repository_source(self, value: typing.Optional["RepositorySource"]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__20f19231b8487de7ecb479bd9371b34eb7ef6551bd840b1646bf463e07f3916b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "repositorySource", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="workbench")
    def workbench(self) -> typing.Optional["WorkbenchConfig"]:
        '''The configuration for the workbench (optional).'''
        return typing.cast(typing.Optional["WorkbenchConfig"], jsii.get(self, "workbench"))

    @workbench.setter
    def workbench(self, value: typing.Optional["WorkbenchConfig"]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e9574ab90d10366386281cc97183ea9a6f0a5443ec34916ceb7bc4ddb933f36d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "workbench", value) # pyright: ignore[reportArgumentType]

# Adding a "__jsii_proxy_class__(): typing.Type" function to the interface
typing.cast(typing.Any, IPipelineConfig).__jsii_proxy_class__ = lambda : _IPipelineConfigProxy


@jsii.interface(jsii_type="@cdklabs/cdk-cicd-wrapper.IPipelinePhases")
class IPipelinePhases(typing_extensions.Protocol):
    '''Represents the phases in a pipeline.'''

    @builtins.property
    @jsii.member(jsii_name="initialize")
    def initialize(self) -> typing.Optional[typing.List[IPhaseCommand]]:
        '''The commands to run during the initialize phase (optional).'''
        ...

    @initialize.setter
    def initialize(self, value: typing.Optional[typing.List[IPhaseCommand]]) -> None:
        ...

    @builtins.property
    @jsii.member(jsii_name="postDeploy")
    def post_deploy(self) -> typing.Optional[typing.List[IPhaseCommand]]:
        '''The commands to run during the post-deploy phase (optional).'''
        ...

    @post_deploy.setter
    def post_deploy(self, value: typing.Optional[typing.List[IPhaseCommand]]) -> None:
        ...

    @builtins.property
    @jsii.member(jsii_name="preBuild")
    def pre_build(self) -> typing.Optional[typing.List[IPhaseCommand]]:
        '''The commands to run during the pre-build phase (optional).'''
        ...

    @pre_build.setter
    def pre_build(self, value: typing.Optional[typing.List[IPhaseCommand]]) -> None:
        ...

    @builtins.property
    @jsii.member(jsii_name="preDeploy")
    def pre_deploy(self) -> typing.Optional[typing.List[IPhaseCommand]]:
        '''The commands to run during the pre-deploy phase (optional).'''
        ...

    @pre_deploy.setter
    def pre_deploy(self, value: typing.Optional[typing.List[IPhaseCommand]]) -> None:
        ...

    @builtins.property
    @jsii.member(jsii_name="runBuild")
    def run_build(self) -> typing.Optional[typing.List[IPhaseCommand]]:
        '''The commands to run during the run-build phase (optional).'''
        ...

    @run_build.setter
    def run_build(self, value: typing.Optional[typing.List[IPhaseCommand]]) -> None:
        ...

    @builtins.property
    @jsii.member(jsii_name="testing")
    def testing(self) -> typing.Optional[typing.List[IPhaseCommand]]:
        '''The commands to run during the testing phase (optional).'''
        ...

    @testing.setter
    def testing(self, value: typing.Optional[typing.List[IPhaseCommand]]) -> None:
        ...


class _IPipelinePhasesProxy:
    '''Represents the phases in a pipeline.'''

    __jsii_type__: typing.ClassVar[str] = "@cdklabs/cdk-cicd-wrapper.IPipelinePhases"

    @builtins.property
    @jsii.member(jsii_name="initialize")
    def initialize(self) -> typing.Optional[typing.List[IPhaseCommand]]:
        '''The commands to run during the initialize phase (optional).'''
        return typing.cast(typing.Optional[typing.List[IPhaseCommand]], jsii.get(self, "initialize"))

    @initialize.setter
    def initialize(self, value: typing.Optional[typing.List[IPhaseCommand]]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1452e71847823a6e2646dca9a540f47256b2312d6d4623405a93404e5e19c776)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "initialize", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="postDeploy")
    def post_deploy(self) -> typing.Optional[typing.List[IPhaseCommand]]:
        '''The commands to run during the post-deploy phase (optional).'''
        return typing.cast(typing.Optional[typing.List[IPhaseCommand]], jsii.get(self, "postDeploy"))

    @post_deploy.setter
    def post_deploy(self, value: typing.Optional[typing.List[IPhaseCommand]]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3900856b9fd1866808653d0e68254a2f33a82ce094368d16049583ba0692bf85)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "postDeploy", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="preBuild")
    def pre_build(self) -> typing.Optional[typing.List[IPhaseCommand]]:
        '''The commands to run during the pre-build phase (optional).'''
        return typing.cast(typing.Optional[typing.List[IPhaseCommand]], jsii.get(self, "preBuild"))

    @pre_build.setter
    def pre_build(self, value: typing.Optional[typing.List[IPhaseCommand]]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__795369e6a94c2a8ef896db52ec821e6100dc66a54fc858db52f22771f37bdc0b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "preBuild", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="preDeploy")
    def pre_deploy(self) -> typing.Optional[typing.List[IPhaseCommand]]:
        '''The commands to run during the pre-deploy phase (optional).'''
        return typing.cast(typing.Optional[typing.List[IPhaseCommand]], jsii.get(self, "preDeploy"))

    @pre_deploy.setter
    def pre_deploy(self, value: typing.Optional[typing.List[IPhaseCommand]]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__274d7cac8ee21a62e3c54506d377d90d81b683bfa5c6c598f4d22afa3488704f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "preDeploy", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="runBuild")
    def run_build(self) -> typing.Optional[typing.List[IPhaseCommand]]:
        '''The commands to run during the run-build phase (optional).'''
        return typing.cast(typing.Optional[typing.List[IPhaseCommand]], jsii.get(self, "runBuild"))

    @run_build.setter
    def run_build(self, value: typing.Optional[typing.List[IPhaseCommand]]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a025d8e732e84f8b766b536c39242e4d3fe88ba835679bff9beebce34ec7e478)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "runBuild", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="testing")
    def testing(self) -> typing.Optional[typing.List[IPhaseCommand]]:
        '''The commands to run during the testing phase (optional).'''
        return typing.cast(typing.Optional[typing.List[IPhaseCommand]], jsii.get(self, "testing"))

    @testing.setter
    def testing(self, value: typing.Optional[typing.List[IPhaseCommand]]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a0676eef9c1c4648a6480b76bd9b555e8d9355db5a8d8a21f9c7d82dabddf50f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "testing", value) # pyright: ignore[reportArgumentType]

# Adding a "__jsii_proxy_class__(): typing.Type" function to the interface
typing.cast(typing.Any, IPipelinePhases).__jsii_proxy_class__ = lambda : _IPipelinePhasesProxy


@jsii.interface(jsii_type="@cdklabs/cdk-cicd-wrapper.IPlugin")
class IPlugin(typing_extensions.Protocol):
    '''Represents a pipeline plugin.'''

    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        '''The name of the plugin.'''
        ...

    @builtins.property
    @jsii.member(jsii_name="version")
    def version(self) -> builtins.str:
        '''The version of the plugin.'''
        ...

    @jsii.member(jsii_name="afterStage")
    def after_stage(
        self,
        scope: _constructs_77d1e7e8.Construct,
        context: "ResourceContext",
    ) -> None:
        '''The method called after the stage is created.

        :param scope: -
        :param context: -
        '''
        ...

    @jsii.member(jsii_name="beforeStage")
    def before_stage(
        self,
        scope: _constructs_77d1e7e8.Construct,
        context: "ResourceContext",
    ) -> None:
        '''The method called before the stage is created.

        :param scope: -
        :param context: -
        '''
        ...

    @jsii.member(jsii_name="create")
    def create(self, context: "ResourceContext") -> None:
        '''The method called when the Pipeline configuration finalized.

        :param context: -
        '''
        ...


class _IPluginProxy:
    '''Represents a pipeline plugin.'''

    __jsii_type__: typing.ClassVar[str] = "@cdklabs/cdk-cicd-wrapper.IPlugin"

    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        '''The name of the plugin.'''
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @builtins.property
    @jsii.member(jsii_name="version")
    def version(self) -> builtins.str:
        '''The version of the plugin.'''
        return typing.cast(builtins.str, jsii.get(self, "version"))

    @jsii.member(jsii_name="afterStage")
    def after_stage(
        self,
        scope: _constructs_77d1e7e8.Construct,
        context: "ResourceContext",
    ) -> None:
        '''The method called after the stage is created.

        :param scope: -
        :param context: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b54c4e8eb6f3938b81207e513aa93d587c0e2aee5261debf5c4cede5b3385534)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument context", value=context, expected_type=type_hints["context"])
        return typing.cast(None, jsii.invoke(self, "afterStage", [scope, context]))

    @jsii.member(jsii_name="beforeStage")
    def before_stage(
        self,
        scope: _constructs_77d1e7e8.Construct,
        context: "ResourceContext",
    ) -> None:
        '''The method called before the stage is created.

        :param scope: -
        :param context: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__82244cc4dc2cff3aadc9fc4456862f35c41f0e4afe338270aa6892f6b7fdfe30)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument context", value=context, expected_type=type_hints["context"])
        return typing.cast(None, jsii.invoke(self, "beforeStage", [scope, context]))

    @jsii.member(jsii_name="create")
    def create(self, context: "ResourceContext") -> None:
        '''The method called when the Pipeline configuration finalized.

        :param context: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__68c5b356d31650cf6c7b3fd5811af6fe87e079f3e59edf5b48908c8fa08af0d8)
            check_type(argname="argument context", value=context, expected_type=type_hints["context"])
        return typing.cast(None, jsii.invoke(self, "create", [context]))

# Adding a "__jsii_proxy_class__(): typing.Type" function to the interface
typing.cast(typing.Any, IPlugin).__jsii_proxy_class__ = lambda : _IPluginProxy


@jsii.interface(jsii_type="@cdklabs/cdk-cicd-wrapper.IProxyConfig")
class IProxyConfig(typing_extensions.Protocol):
    '''HTTP(s) Proxy configuration.'''

    @builtins.property
    @jsii.member(jsii_name="noProxy")
    def no_proxy(self) -> typing.List[builtins.str]:
        '''A list of URLs or IP addresses that should bypass the proxy.'''
        ...

    @no_proxy.setter
    def no_proxy(self, value: typing.List[builtins.str]) -> None:
        ...

    @builtins.property
    @jsii.member(jsii_name="proxySecretArn")
    def proxy_secret_arn(self) -> builtins.str:
        '''The ARN of the Secrets Manager secret that contains the proxy credentials.'''
        ...

    @proxy_secret_arn.setter
    def proxy_secret_arn(self, value: builtins.str) -> None:
        ...

    @builtins.property
    @jsii.member(jsii_name="proxyTestUrl")
    def proxy_test_url(self) -> builtins.str:
        '''A URL to test the proxy configuration.'''
        ...

    @proxy_test_url.setter
    def proxy_test_url(self, value: builtins.str) -> None:
        ...


class _IProxyConfigProxy:
    '''HTTP(s) Proxy configuration.'''

    __jsii_type__: typing.ClassVar[str] = "@cdklabs/cdk-cicd-wrapper.IProxyConfig"

    @builtins.property
    @jsii.member(jsii_name="noProxy")
    def no_proxy(self) -> typing.List[builtins.str]:
        '''A list of URLs or IP addresses that should bypass the proxy.'''
        return typing.cast(typing.List[builtins.str], jsii.get(self, "noProxy"))

    @no_proxy.setter
    def no_proxy(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9a6b3845b744da23ba38e1b6281e204353917bb487cc52023ade063112f9f59f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "noProxy", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="proxySecretArn")
    def proxy_secret_arn(self) -> builtins.str:
        '''The ARN of the Secrets Manager secret that contains the proxy credentials.'''
        return typing.cast(builtins.str, jsii.get(self, "proxySecretArn"))

    @proxy_secret_arn.setter
    def proxy_secret_arn(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1131a520d2dc76a1bcfbaed53b1f95afaff9ac3a65961418dfdebc191897adb6)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "proxySecretArn", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="proxyTestUrl")
    def proxy_test_url(self) -> builtins.str:
        '''A URL to test the proxy configuration.'''
        return typing.cast(builtins.str, jsii.get(self, "proxyTestUrl"))

    @proxy_test_url.setter
    def proxy_test_url(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__64426f347056475ac5a95fc546ed489ca1146101a69b1a55bddf6f2324795ef5)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "proxyTestUrl", value) # pyright: ignore[reportArgumentType]

# Adding a "__jsii_proxy_class__(): typing.Type" function to the interface
typing.cast(typing.Any, IProxyConfig).__jsii_proxy_class__ = lambda : _IProxyConfigProxy


@jsii.interface(jsii_type="@cdklabs/cdk-cicd-wrapper.IRepositoryStack")
class IRepositoryStack(_constructs_77d1e7e8.IConstruct, typing_extensions.Protocol):
    '''Represents a repository stack in the pipeline.'''

    @builtins.property
    @jsii.member(jsii_name="pipelineEnvVars")
    def pipeline_env_vars(self) -> typing.Mapping[builtins.str, builtins.str]:
        ...

    @builtins.property
    @jsii.member(jsii_name="pipelineInput")
    def pipeline_input(self) -> _aws_cdk_pipelines_ceddda9d.IFileSetProducer:
        ...

    @builtins.property
    @jsii.member(jsii_name="repositoryBranch")
    def repository_branch(self) -> builtins.str:
        ...


class _IRepositoryStackProxy(
    jsii.proxy_for(_constructs_77d1e7e8.IConstruct), # type: ignore[misc]
):
    '''Represents a repository stack in the pipeline.'''

    __jsii_type__: typing.ClassVar[str] = "@cdklabs/cdk-cicd-wrapper.IRepositoryStack"

    @builtins.property
    @jsii.member(jsii_name="pipelineEnvVars")
    def pipeline_env_vars(self) -> typing.Mapping[builtins.str, builtins.str]:
        return typing.cast(typing.Mapping[builtins.str, builtins.str], jsii.get(self, "pipelineEnvVars"))

    @builtins.property
    @jsii.member(jsii_name="pipelineInput")
    def pipeline_input(self) -> _aws_cdk_pipelines_ceddda9d.IFileSetProducer:
        return typing.cast(_aws_cdk_pipelines_ceddda9d.IFileSetProducer, jsii.get(self, "pipelineInput"))

    @builtins.property
    @jsii.member(jsii_name="repositoryBranch")
    def repository_branch(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "repositoryBranch"))

# Adding a "__jsii_proxy_class__(): typing.Type" function to the interface
typing.cast(typing.Any, IRepositoryStack).__jsii_proxy_class__ = lambda : _IRepositoryStackProxy


@jsii.interface(jsii_type="@cdklabs/cdk-cicd-wrapper.IResourceProvider")
class IResourceProvider(typing_extensions.Protocol):
    '''Interface representing a generic resource provider.

    Provides resources through the ``provide`` method.
    '''

    @builtins.property
    @jsii.member(jsii_name="scope")
    def scope(self) -> typing.Optional["Scope"]:
        '''The scope in which the resource provider is available.

        Defaults to ``Scope.GLOBAL``.
        '''
        ...

    @scope.setter
    def scope(self, value: typing.Optional["Scope"]) -> None:
        ...

    @jsii.member(jsii_name="provide")
    def provide(self, context: "ResourceContext") -> typing.Any:
        '''Provides resources based on the given context.

        :param context: The context in which the resources are provided.

        :return: The provided resources.
        '''
        ...


class _IResourceProviderProxy:
    '''Interface representing a generic resource provider.

    Provides resources through the ``provide`` method.
    '''

    __jsii_type__: typing.ClassVar[str] = "@cdklabs/cdk-cicd-wrapper.IResourceProvider"

    @builtins.property
    @jsii.member(jsii_name="scope")
    def scope(self) -> typing.Optional["Scope"]:
        '''The scope in which the resource provider is available.

        Defaults to ``Scope.GLOBAL``.
        '''
        return typing.cast(typing.Optional["Scope"], jsii.get(self, "scope"))

    @scope.setter
    def scope(self, value: typing.Optional["Scope"]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c3cdeb8d8e912d222a6a0c078ddbd381679a36ef6e9af3d179d5b759d3e067a4)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "scope", value) # pyright: ignore[reportArgumentType]

    @jsii.member(jsii_name="provide")
    def provide(self, context: "ResourceContext") -> typing.Any:
        '''Provides resources based on the given context.

        :param context: The context in which the resources are provided.

        :return: The provided resources.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__022ec6359bf8623c4688f9a50b7ac61d91f90bf6874c5425473c5b2e8526d5e6)
            check_type(argname="argument context", value=context, expected_type=type_hints["context"])
        return typing.cast(typing.Any, jsii.invoke(self, "provide", [context]))

# Adding a "__jsii_proxy_class__(): typing.Type" function to the interface
typing.cast(typing.Any, IResourceProvider).__jsii_proxy_class__ = lambda : _IResourceProviderProxy


@jsii.interface(jsii_type="@cdklabs/cdk-cicd-wrapper.IStackProvider")
class IStackProvider(typing_extensions.Protocol):
    '''Represents a stack provider interface.'''

    @jsii.member(jsii_name="provide")
    def provide(self, context: "ResourceContext") -> None:
        '''Provides the deployment hook configuration or void.

        :param context: The resource context.
        '''
        ...


class _IStackProviderProxy:
    '''Represents a stack provider interface.'''

    __jsii_type__: typing.ClassVar[str] = "@cdklabs/cdk-cicd-wrapper.IStackProvider"

    @jsii.member(jsii_name="provide")
    def provide(self, context: "ResourceContext") -> None:
        '''Provides the deployment hook configuration or void.

        :param context: The resource context.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__aa2e2be5ef472df4931cbf5b7c7b1c429d3de6bc51a4f31d378667667b6b598b)
            check_type(argname="argument context", value=context, expected_type=type_hints["context"])
        return typing.cast(None, jsii.invoke(self, "provide", [context]))

# Adding a "__jsii_proxy_class__(): typing.Type" function to the interface
typing.cast(typing.Any, IStackProvider).__jsii_proxy_class__ = lambda : _IStackProviderProxy


@jsii.interface(jsii_type="@cdklabs/cdk-cicd-wrapper.IStageConfig")
class IStageConfig(typing_extensions.Protocol):
    @builtins.property
    @jsii.member(jsii_name="beforeEntry")
    def before_entry(
        self,
    ) -> typing.Optional[_aws_cdk_aws_codepipeline_ceddda9d.Conditions]:
        '''The method to use when a stage allows entry.

        :default: - No conditions are applied before stage entry
        '''
        ...

    @before_entry.setter
    def before_entry(
        self,
        value: typing.Optional[_aws_cdk_aws_codepipeline_ceddda9d.Conditions],
    ) -> None:
        ...

    @builtins.property
    @jsii.member(jsii_name="disableTransition")
    def disable_transition(self) -> typing.Optional[builtins.str]:
        '''The reason for disabling the transition.'''
        ...

    @disable_transition.setter
    def disable_transition(self, value: typing.Optional[builtins.str]) -> None:
        ...

    @builtins.property
    @jsii.member(jsii_name="onFailure")
    def on_failure(
        self,
    ) -> typing.Optional[_aws_cdk_aws_codepipeline_ceddda9d.FailureConditions]:
        '''The method to use when a stage has not completed successfully.

        :default: - No failure conditions are applied
        '''
        ...

    @on_failure.setter
    def on_failure(
        self,
        value: typing.Optional[_aws_cdk_aws_codepipeline_ceddda9d.FailureConditions],
    ) -> None:
        ...

    @builtins.property
    @jsii.member(jsii_name="onSuccess")
    def on_success(
        self,
    ) -> typing.Optional[_aws_cdk_aws_codepipeline_ceddda9d.Conditions]:
        '''The method to use when a stage has succeeded.

        :default: - No success conditions are applied
        '''
        ...

    @on_success.setter
    def on_success(
        self,
        value: typing.Optional[_aws_cdk_aws_codepipeline_ceddda9d.Conditions],
    ) -> None:
        ...


class _IStageConfigProxy:
    __jsii_type__: typing.ClassVar[str] = "@cdklabs/cdk-cicd-wrapper.IStageConfig"

    @builtins.property
    @jsii.member(jsii_name="beforeEntry")
    def before_entry(
        self,
    ) -> typing.Optional[_aws_cdk_aws_codepipeline_ceddda9d.Conditions]:
        '''The method to use when a stage allows entry.

        :default: - No conditions are applied before stage entry
        '''
        return typing.cast(typing.Optional[_aws_cdk_aws_codepipeline_ceddda9d.Conditions], jsii.get(self, "beforeEntry"))

    @before_entry.setter
    def before_entry(
        self,
        value: typing.Optional[_aws_cdk_aws_codepipeline_ceddda9d.Conditions],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__38774dcd02360477515624272bb81ed33fde51cf44e30ab3dab6ba31840e7d75)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "beforeEntry", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="disableTransition")
    def disable_transition(self) -> typing.Optional[builtins.str]:
        '''The reason for disabling the transition.'''
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "disableTransition"))

    @disable_transition.setter
    def disable_transition(self, value: typing.Optional[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__45fd062d2880c7d2f6a1339fd957b3bfc14fefdd7dc4212484f5704b7884509e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "disableTransition", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="onFailure")
    def on_failure(
        self,
    ) -> typing.Optional[_aws_cdk_aws_codepipeline_ceddda9d.FailureConditions]:
        '''The method to use when a stage has not completed successfully.

        :default: - No failure conditions are applied
        '''
        return typing.cast(typing.Optional[_aws_cdk_aws_codepipeline_ceddda9d.FailureConditions], jsii.get(self, "onFailure"))

    @on_failure.setter
    def on_failure(
        self,
        value: typing.Optional[_aws_cdk_aws_codepipeline_ceddda9d.FailureConditions],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5ea7872f6e9107d85d053109eb71cf88244ac183e0b4c7d0a4a79492013efba5)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "onFailure", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="onSuccess")
    def on_success(
        self,
    ) -> typing.Optional[_aws_cdk_aws_codepipeline_ceddda9d.Conditions]:
        '''The method to use when a stage has succeeded.

        :default: - No success conditions are applied
        '''
        return typing.cast(typing.Optional[_aws_cdk_aws_codepipeline_ceddda9d.Conditions], jsii.get(self, "onSuccess"))

    @on_success.setter
    def on_success(
        self,
        value: typing.Optional[_aws_cdk_aws_codepipeline_ceddda9d.Conditions],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ec27f4d1d4b5c451583b18ecdc4f7645813837553c1ed57a8b7786aa67b2387e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "onSuccess", value) # pyright: ignore[reportArgumentType]

# Adding a "__jsii_proxy_class__(): typing.Type" function to the interface
typing.cast(typing.Any, IStageConfig).__jsii_proxy_class__ = lambda : _IStageConfigProxy


@jsii.interface(jsii_type="@cdklabs/cdk-cicd-wrapper.IStageDefinition")
class IStageDefinition(typing_extensions.Protocol):
    '''Represents a stage definition.'''

    @builtins.property
    @jsii.member(jsii_name="stage")
    def stage(self) -> builtins.str:
        '''The name of the stage.'''
        ...

    @stage.setter
    def stage(self, value: builtins.str) -> None:
        ...

    @builtins.property
    @jsii.member(jsii_name="account")
    def account(self) -> typing.Optional[builtins.str]:
        '''The account for the stage (optional).'''
        ...

    @account.setter
    def account(self, value: typing.Optional[builtins.str]) -> None:
        ...

    @builtins.property
    @jsii.member(jsii_name="complianceLogBucketName")
    def compliance_log_bucket_name(self) -> typing.Optional[builtins.str]:
        '''The complianceBucket Name.'''
        ...

    @compliance_log_bucket_name.setter
    def compliance_log_bucket_name(self, value: typing.Optional[builtins.str]) -> None:
        ...

    @builtins.property
    @jsii.member(jsii_name="manualApprovalRequired")
    def manual_approval_required(self) -> typing.Optional[builtins.bool]:
        '''Manual approval is required or not.

        :default: for DEV stage it is false otherwise true
        '''
        ...

    @manual_approval_required.setter
    def manual_approval_required(self, value: typing.Optional[builtins.bool]) -> None:
        ...

    @builtins.property
    @jsii.member(jsii_name="region")
    def region(self) -> typing.Optional[builtins.str]:
        '''The region for the stage (optional).'''
        ...

    @region.setter
    def region(self, value: typing.Optional[builtins.str]) -> None:
        ...

    @builtins.property
    @jsii.member(jsii_name="vpc")
    def vpc(self) -> typing.Optional["IVpcConfig"]:
        '''The VPC configuration for the stage.'''
        ...

    @vpc.setter
    def vpc(self, value: typing.Optional["IVpcConfig"]) -> None:
        ...


class _IStageDefinitionProxy:
    '''Represents a stage definition.'''

    __jsii_type__: typing.ClassVar[str] = "@cdklabs/cdk-cicd-wrapper.IStageDefinition"

    @builtins.property
    @jsii.member(jsii_name="stage")
    def stage(self) -> builtins.str:
        '''The name of the stage.'''
        return typing.cast(builtins.str, jsii.get(self, "stage"))

    @stage.setter
    def stage(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__95ec8494f3439f66a2953a04cee921364792a9dc940a239466f2ef996bced85b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "stage", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="account")
    def account(self) -> typing.Optional[builtins.str]:
        '''The account for the stage (optional).'''
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "account"))

    @account.setter
    def account(self, value: typing.Optional[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3de0f4e2f3f3f2d0d4fe396ca29e13a0b1727e4721a10ba572b451ce4f2b2ac6)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "account", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="complianceLogBucketName")
    def compliance_log_bucket_name(self) -> typing.Optional[builtins.str]:
        '''The complianceBucket Name.'''
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "complianceLogBucketName"))

    @compliance_log_bucket_name.setter
    def compliance_log_bucket_name(self, value: typing.Optional[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e32989d7e98737acefdbff60d9cc3a0dae0380f19178903630855bb1c6cd6cc2)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "complianceLogBucketName", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="manualApprovalRequired")
    def manual_approval_required(self) -> typing.Optional[builtins.bool]:
        '''Manual approval is required or not.

        :default: for DEV stage it is false otherwise true
        '''
        return typing.cast(typing.Optional[builtins.bool], jsii.get(self, "manualApprovalRequired"))

    @manual_approval_required.setter
    def manual_approval_required(self, value: typing.Optional[builtins.bool]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__20898bda8dea3f7e774078abf74a8bd5cdd475e8e8d4998a22ece9a810e9b725)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "manualApprovalRequired", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="region")
    def region(self) -> typing.Optional[builtins.str]:
        '''The region for the stage (optional).'''
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "region"))

    @region.setter
    def region(self, value: typing.Optional[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__43102f4878e00fc0dd939f2392c826be08b7313d7caa5f66fbbb908dbd1c6464)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "region", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="vpc")
    def vpc(self) -> typing.Optional["IVpcConfig"]:
        '''The VPC configuration for the stage.'''
        return typing.cast(typing.Optional["IVpcConfig"], jsii.get(self, "vpc"))

    @vpc.setter
    def vpc(self, value: typing.Optional["IVpcConfig"]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__aeaa3fd6d391d0d5c2e15332c12810a36da3a2e6c30cd8264446e59e33564d7f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "vpc", value) # pyright: ignore[reportArgumentType]

# Adding a "__jsii_proxy_class__(): typing.Type" function to the interface
typing.cast(typing.Any, IStageDefinition).__jsii_proxy_class__ = lambda : _IStageDefinitionProxy


@jsii.interface(jsii_type="@cdklabs/cdk-cicd-wrapper.IVpcConfig")
class IVpcConfig(typing_extensions.Protocol):
    '''Interface representing VPC configuration.'''

    @builtins.property
    @jsii.member(jsii_name="managedVPC")
    def managed_vpc(self) -> typing.Optional[IManagedVpcConfig]:
        ...

    @managed_vpc.setter
    def managed_vpc(self, value: typing.Optional[IManagedVpcConfig]) -> None:
        ...

    @builtins.property
    @jsii.member(jsii_name="vpcFromLookUp")
    def vpc_from_look_up(self) -> typing.Optional[builtins.str]:
        ...

    @vpc_from_look_up.setter
    def vpc_from_look_up(self, value: typing.Optional[builtins.str]) -> None:
        ...


class _IVpcConfigProxy:
    '''Interface representing VPC configuration.'''

    __jsii_type__: typing.ClassVar[str] = "@cdklabs/cdk-cicd-wrapper.IVpcConfig"

    @builtins.property
    @jsii.member(jsii_name="managedVPC")
    def managed_vpc(self) -> typing.Optional[IManagedVpcConfig]:
        return typing.cast(typing.Optional[IManagedVpcConfig], jsii.get(self, "managedVPC"))

    @managed_vpc.setter
    def managed_vpc(self, value: typing.Optional[IManagedVpcConfig]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ab276d5122a044b23e9a26a526006e8a580af461cf59ea71bd212b6444ffa1ef)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "managedVPC", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="vpcFromLookUp")
    def vpc_from_look_up(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "vpcFromLookUp"))

    @vpc_from_look_up.setter
    def vpc_from_look_up(self, value: typing.Optional[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__cd4ef4e2430712868b0ef23708e30fbe0a8c75850d90e986240da922508be24c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "vpcFromLookUp", value) # pyright: ignore[reportArgumentType]

# Adding a "__jsii_proxy_class__(): typing.Type" function to the interface
typing.cast(typing.Any, IVpcConfig).__jsii_proxy_class__ = lambda : _IVpcConfigProxy


@jsii.interface(jsii_type="@cdklabs/cdk-cicd-wrapper.IVpcConfigFromLookUp")
class IVpcConfigFromLookUp(typing_extensions.Protocol):
    '''VPC Configuration for VPC id lookup.'''

    @builtins.property
    @jsii.member(jsii_name="vpcId")
    def vpc_id(self) -> builtins.str:
        '''VPC id to lookup.'''
        ...

    @vpc_id.setter
    def vpc_id(self, value: builtins.str) -> None:
        ...


class _IVpcConfigFromLookUpProxy:
    '''VPC Configuration for VPC id lookup.'''

    __jsii_type__: typing.ClassVar[str] = "@cdklabs/cdk-cicd-wrapper.IVpcConfigFromLookUp"

    @builtins.property
    @jsii.member(jsii_name="vpcId")
    def vpc_id(self) -> builtins.str:
        '''VPC id to lookup.'''
        return typing.cast(builtins.str, jsii.get(self, "vpcId"))

    @vpc_id.setter
    def vpc_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1e61264f328af5c22ce14b5c05013f702dacb0a3b71318edaec256b8018905df)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "vpcId", value) # pyright: ignore[reportArgumentType]

# Adding a "__jsii_proxy_class__(): typing.Type" function to the interface
typing.cast(typing.Any, IVpcConfigFromLookUp).__jsii_proxy_class__ = lambda : _IVpcConfigFromLookUpProxy


@jsii.interface(jsii_type="@cdklabs/cdk-cicd-wrapper.IVpcConstruct")
class IVpcConstruct(typing_extensions.Protocol):
    '''VPC construct that provides the VPC and HTTP proxy settings.'''

    @builtins.property
    @jsii.member(jsii_name="securityGroup")
    def security_group(
        self,
    ) -> typing.Optional[_aws_cdk_aws_ec2_ceddda9d.ISecurityGroup]:
        ...

    @builtins.property
    @jsii.member(jsii_name="subnetType")
    def subnet_type(self) -> typing.Optional[_aws_cdk_aws_ec2_ceddda9d.SubnetType]:
        ...

    @builtins.property
    @jsii.member(jsii_name="vpc")
    def vpc(self) -> typing.Optional[_aws_cdk_aws_ec2_ceddda9d.IVpc]:
        ...


class _IVpcConstructProxy:
    '''VPC construct that provides the VPC and HTTP proxy settings.'''

    __jsii_type__: typing.ClassVar[str] = "@cdklabs/cdk-cicd-wrapper.IVpcConstruct"

    @builtins.property
    @jsii.member(jsii_name="securityGroup")
    def security_group(
        self,
    ) -> typing.Optional[_aws_cdk_aws_ec2_ceddda9d.ISecurityGroup]:
        return typing.cast(typing.Optional[_aws_cdk_aws_ec2_ceddda9d.ISecurityGroup], jsii.get(self, "securityGroup"))

    @builtins.property
    @jsii.member(jsii_name="subnetType")
    def subnet_type(self) -> typing.Optional[_aws_cdk_aws_ec2_ceddda9d.SubnetType]:
        return typing.cast(typing.Optional[_aws_cdk_aws_ec2_ceddda9d.SubnetType], jsii.get(self, "subnetType"))

    @builtins.property
    @jsii.member(jsii_name="vpc")
    def vpc(self) -> typing.Optional[_aws_cdk_aws_ec2_ceddda9d.IVpc]:
        return typing.cast(typing.Optional[_aws_cdk_aws_ec2_ceddda9d.IVpc], jsii.get(self, "vpc"))

# Adding a "__jsii_proxy_class__(): typing.Type" function to the interface
typing.cast(typing.Any, IVpcConstruct).__jsii_proxy_class__ = lambda : _IVpcConstructProxy


@jsii.implements(IPhaseCommand)
class InlineShellPhaseCommand(
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdklabs/cdk-cicd-wrapper.InlineShellPhaseCommand",
):
    '''Phase Command that place the scripts code directly into the CodeBuild buildSpec definition.

    This is used to add scripts from this NPM library to the buildSpec that needs to run without internet access or ability to invoke npm ci.
    '''

    def __init__(
        self,
        script: builtins.str,
        export_environment: typing.Optional[builtins.bool] = None,
    ) -> None:
        '''
        :param script: -
        :param export_environment: Determines whether the script should export environment variables or not. Default: false
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__29e06bf649dc4df088c99ff0722bc663c408c8bca362dd5e0f006df462e3089d)
            check_type(argname="argument script", value=script, expected_type=type_hints["script"])
            check_type(argname="argument export_environment", value=export_environment, expected_type=type_hints["export_environment"])
        jsii.create(self.__class__, self, [script, export_environment])

    @builtins.property
    @jsii.member(jsii_name="command")
    def command(self) -> builtins.str:
        '''Returns the command to be executed for the given inline shell script.'''
        return typing.cast(builtins.str, jsii.get(self, "command"))

    @builtins.property
    @jsii.member(jsii_name="exportEnvironment")
    def export_environment(self) -> builtins.bool:
        '''Determines whether the script should export environment variables or not.

        :default: false
        '''
        return typing.cast(builtins.bool, jsii.get(self, "exportEnvironment"))

    @builtins.property
    @jsii.member(jsii_name="script")
    def script(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "script"))


@jsii.implements(IResourceProvider)
class LoggingProvider(
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdklabs/cdk-cicd-wrapper.LoggingProvider",
):
    def __init__(self) -> None:
        jsii.create(self.__class__, self, [])

    @jsii.member(jsii_name="provide")
    def provide(self, _: "ResourceContext") -> typing.Any:
        '''Provides resources based on the given context.

        :param _: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c3cbcac597367da9bcc590c7f19f8e3f7ec75f4e364dfd1590f44bd6da78ef45)
            check_type(argname="argument _", value=_, expected_type=type_hints["_"])
        return typing.cast(typing.Any, jsii.invoke(self, "provide", [_]))


class ManagedVPCStack(
    _aws_cdk_ceddda9d.Stack,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdklabs/cdk-cicd-wrapper.ManagedVPCStack",
):
    '''A stack that creates or looks up a VPC and configures its settings.'''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        cidr_block: builtins.str,
        max_azs: jsii.Number,
        subnet_cidr_mask: jsii.Number,
        use_proxy: builtins.bool,
        allow_all_outbound: typing.Optional[builtins.bool] = None,
        code_build_vpc_interfaces: typing.Optional[typing.Sequence[_aws_cdk_aws_ec2_ceddda9d.InterfaceVpcEndpointAwsService]] = None,
        flow_logs_bucket_name: typing.Optional[builtins.str] = None,
        restrict_default_security_group: typing.Optional[builtins.bool] = None,
        subnet_type: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.SubnetType] = None,
        analytics_reporting: typing.Optional[builtins.bool] = None,
        cross_region_references: typing.Optional[builtins.bool] = None,
        description: typing.Optional[builtins.str] = None,
        env: typing.Optional[typing.Union[_aws_cdk_ceddda9d.Environment, typing.Dict[builtins.str, typing.Any]]] = None,
        notification_arns: typing.Optional[typing.Sequence[builtins.str]] = None,
        permissions_boundary: typing.Optional[_aws_cdk_ceddda9d.PermissionsBoundary] = None,
        stack_name: typing.Optional[builtins.str] = None,
        suppress_template_indentation: typing.Optional[builtins.bool] = None,
        synthesizer: typing.Optional[_aws_cdk_ceddda9d.IStackSynthesizer] = None,
        tags: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        termination_protection: typing.Optional[builtins.bool] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param cidr_block: CIDR block for the VPC.
        :param max_azs: Max AZs.
        :param subnet_cidr_mask: Subnets CIDR masks.
        :param use_proxy: Whether to use a proxy for the VPC. Default value is false.
        :param allow_all_outbound: Whether to allow all outbound traffic by default. If this is set to true, there will only be a single egress rule which allows all outbound traffic. If this is set to false, no outbound traffic will be allowed by default and all egress traffic must be explicitly authorized. Default: true
        :param code_build_vpc_interfaces: The list of CodeBuild VPC InterfacesVpcEndpointAwsServices to extend the defaultCodeBuildVPCInterfaces.
        :param flow_logs_bucket_name: The name of the S3 bucket for VPC flow logs.
        :param restrict_default_security_group: If set to true then the default inbound & outbound rules will be removed from the default security group. Default: true
        :param subnet_type: The subnets attached to the VPC. Default: - Private Subnet only
        :param analytics_reporting: Include runtime versioning information in this Stack. Default: ``analyticsReporting`` setting of containing ``App``, or value of 'aws:cdk:version-reporting' context key
        :param cross_region_references: Enable this flag to allow native cross region stack references. Enabling this will create a CloudFormation custom resource in both the producing stack and consuming stack in order to perform the export/import This feature is currently experimental Default: false
        :param description: A description of the stack. Default: - No description.
        :param env: The AWS environment (account/region) where this stack will be deployed. Set the ``region``/``account`` fields of ``env`` to either a concrete value to select the indicated environment (recommended for production stacks), or to the values of environment variables ``CDK_DEFAULT_REGION``/``CDK_DEFAULT_ACCOUNT`` to let the target environment depend on the AWS credentials/configuration that the CDK CLI is executed under (recommended for development stacks). If the ``Stack`` is instantiated inside a ``Stage``, any undefined ``region``/``account`` fields from ``env`` will default to the same field on the encompassing ``Stage``, if configured there. If either ``region`` or ``account`` are not set nor inherited from ``Stage``, the Stack will be considered "*environment-agnostic*"". Environment-agnostic stacks can be deployed to any environment but may not be able to take advantage of all features of the CDK. For example, they will not be able to use environmental context lookups such as ``ec2.Vpc.fromLookup`` and will not automatically translate Service Principals to the right format based on the environment's AWS partition, and other such enhancements. Default: - The environment of the containing ``Stage`` if available, otherwise create the stack will be environment-agnostic.
        :param notification_arns: SNS Topic ARNs that will receive stack events. Default: - no notfication arns.
        :param permissions_boundary: Options for applying a permissions boundary to all IAM Roles and Users created within this Stage. Default: - no permissions boundary is applied
        :param stack_name: Name to deploy the stack with. Default: - Derived from construct path.
        :param suppress_template_indentation: Enable this flag to suppress indentation in generated CloudFormation templates. If not specified, the value of the ``@aws-cdk/core:suppressTemplateIndentation`` context key will be used. If that is not specified, then the default value ``false`` will be used. Default: - the value of ``@aws-cdk/core:suppressTemplateIndentation``, or ``false`` if that is not set.
        :param synthesizer: Synthesis method to use while deploying this stack. The Stack Synthesizer controls aspects of synthesis and deployment, like how assets are referenced and what IAM roles to use. For more information, see the README of the main CDK package. If not specified, the ``defaultStackSynthesizer`` from ``App`` will be used. If that is not specified, ``DefaultStackSynthesizer`` is used if ``@aws-cdk/core:newStyleStackSynthesis`` is set to ``true`` or the CDK major version is v2. In CDK v1 ``LegacyStackSynthesizer`` is the default if no other synthesizer is specified. Default: - The synthesizer specified on ``App``, or ``DefaultStackSynthesizer`` otherwise.
        :param tags: Stack tags that will be applied to all the taggable resources and the stack itself. Default: {}
        :param termination_protection: Whether to enable termination protection for this stack. Default: false
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__70b0ba31b33d549518a53cba5e179a3e44bdf4061c06fc504716cb5bc90cb540)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = ManagedVPCStackProps(
            cidr_block=cidr_block,
            max_azs=max_azs,
            subnet_cidr_mask=subnet_cidr_mask,
            use_proxy=use_proxy,
            allow_all_outbound=allow_all_outbound,
            code_build_vpc_interfaces=code_build_vpc_interfaces,
            flow_logs_bucket_name=flow_logs_bucket_name,
            restrict_default_security_group=restrict_default_security_group,
            subnet_type=subnet_type,
            analytics_reporting=analytics_reporting,
            cross_region_references=cross_region_references,
            description=description,
            env=env,
            notification_arns=notification_arns,
            permissions_boundary=permissions_boundary,
            stack_name=stack_name,
            suppress_template_indentation=suppress_template_indentation,
            synthesizer=synthesizer,
            tags=tags,
            termination_protection=termination_protection,
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @builtins.property
    @jsii.member(jsii_name="allowAllOutbound")
    def allow_all_outbound(self) -> builtins.bool:
        return typing.cast(builtins.bool, jsii.get(self, "allowAllOutbound"))

    @builtins.property
    @jsii.member(jsii_name="cidrBlock")
    def cidr_block(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "cidrBlock"))

    @builtins.property
    @jsii.member(jsii_name="codeBuildVPCInterfaces")
    def code_build_vpc_interfaces(
        self,
    ) -> typing.List[_aws_cdk_aws_ec2_ceddda9d.InterfaceVpcEndpointAwsService]:
        '''The list of CodeBuild VPC InterfacesVpcEndpointAwsServices.'''
        return typing.cast(typing.List[_aws_cdk_aws_ec2_ceddda9d.InterfaceVpcEndpointAwsService], jsii.get(self, "codeBuildVPCInterfaces"))

    @builtins.property
    @jsii.member(jsii_name="maxAzs")
    def max_azs(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "maxAzs"))

    @builtins.property
    @jsii.member(jsii_name="restrictDefaultSecurityGroup")
    def restrict_default_security_group(self) -> builtins.bool:
        return typing.cast(builtins.bool, jsii.get(self, "restrictDefaultSecurityGroup"))

    @builtins.property
    @jsii.member(jsii_name="subnetCidrMask")
    def subnet_cidr_mask(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "subnetCidrMask"))

    @builtins.property
    @jsii.member(jsii_name="vpc")
    def vpc(self) -> _aws_cdk_aws_ec2_ceddda9d.IVpc:
        '''The VPC created or looked up by this stack.'''
        return typing.cast(_aws_cdk_aws_ec2_ceddda9d.IVpc, jsii.get(self, "vpc"))

    @builtins.property
    @jsii.member(jsii_name="securityGroup")
    def security_group(
        self,
    ) -> typing.Optional[_aws_cdk_aws_ec2_ceddda9d.ISecurityGroup]:
        return typing.cast(typing.Optional[_aws_cdk_aws_ec2_ceddda9d.ISecurityGroup], jsii.get(self, "securityGroup"))

    @builtins.property
    @jsii.member(jsii_name="subnetType")
    def subnet_type(self) -> typing.Optional[_aws_cdk_aws_ec2_ceddda9d.SubnetType]:
        '''The subnets attached to the VPC.'''
        return typing.cast(typing.Optional[_aws_cdk_aws_ec2_ceddda9d.SubnetType], jsii.get(self, "subnetType"))


@jsii.data_type(
    jsii_type="@cdklabs/cdk-cicd-wrapper.ManagedVPCStackProps",
    jsii_struct_bases=[_aws_cdk_ceddda9d.StackProps],
    name_mapping={
        "analytics_reporting": "analyticsReporting",
        "cross_region_references": "crossRegionReferences",
        "description": "description",
        "env": "env",
        "notification_arns": "notificationArns",
        "permissions_boundary": "permissionsBoundary",
        "stack_name": "stackName",
        "suppress_template_indentation": "suppressTemplateIndentation",
        "synthesizer": "synthesizer",
        "tags": "tags",
        "termination_protection": "terminationProtection",
        "cidr_block": "cidrBlock",
        "max_azs": "maxAzs",
        "subnet_cidr_mask": "subnetCidrMask",
        "use_proxy": "useProxy",
        "allow_all_outbound": "allowAllOutbound",
        "code_build_vpc_interfaces": "codeBuildVPCInterfaces",
        "flow_logs_bucket_name": "flowLogsBucketName",
        "restrict_default_security_group": "restrictDefaultSecurityGroup",
        "subnet_type": "subnetType",
    },
)
class ManagedVPCStackProps(_aws_cdk_ceddda9d.StackProps):
    def __init__(
        self,
        *,
        analytics_reporting: typing.Optional[builtins.bool] = None,
        cross_region_references: typing.Optional[builtins.bool] = None,
        description: typing.Optional[builtins.str] = None,
        env: typing.Optional[typing.Union[_aws_cdk_ceddda9d.Environment, typing.Dict[builtins.str, typing.Any]]] = None,
        notification_arns: typing.Optional[typing.Sequence[builtins.str]] = None,
        permissions_boundary: typing.Optional[_aws_cdk_ceddda9d.PermissionsBoundary] = None,
        stack_name: typing.Optional[builtins.str] = None,
        suppress_template_indentation: typing.Optional[builtins.bool] = None,
        synthesizer: typing.Optional[_aws_cdk_ceddda9d.IStackSynthesizer] = None,
        tags: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        termination_protection: typing.Optional[builtins.bool] = None,
        cidr_block: builtins.str,
        max_azs: jsii.Number,
        subnet_cidr_mask: jsii.Number,
        use_proxy: builtins.bool,
        allow_all_outbound: typing.Optional[builtins.bool] = None,
        code_build_vpc_interfaces: typing.Optional[typing.Sequence[_aws_cdk_aws_ec2_ceddda9d.InterfaceVpcEndpointAwsService]] = None,
        flow_logs_bucket_name: typing.Optional[builtins.str] = None,
        restrict_default_security_group: typing.Optional[builtins.bool] = None,
        subnet_type: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.SubnetType] = None,
    ) -> None:
        '''Properties for the VPCStack.

        :param analytics_reporting: Include runtime versioning information in this Stack. Default: ``analyticsReporting`` setting of containing ``App``, or value of 'aws:cdk:version-reporting' context key
        :param cross_region_references: Enable this flag to allow native cross region stack references. Enabling this will create a CloudFormation custom resource in both the producing stack and consuming stack in order to perform the export/import This feature is currently experimental Default: false
        :param description: A description of the stack. Default: - No description.
        :param env: The AWS environment (account/region) where this stack will be deployed. Set the ``region``/``account`` fields of ``env`` to either a concrete value to select the indicated environment (recommended for production stacks), or to the values of environment variables ``CDK_DEFAULT_REGION``/``CDK_DEFAULT_ACCOUNT`` to let the target environment depend on the AWS credentials/configuration that the CDK CLI is executed under (recommended for development stacks). If the ``Stack`` is instantiated inside a ``Stage``, any undefined ``region``/``account`` fields from ``env`` will default to the same field on the encompassing ``Stage``, if configured there. If either ``region`` or ``account`` are not set nor inherited from ``Stage``, the Stack will be considered "*environment-agnostic*"". Environment-agnostic stacks can be deployed to any environment but may not be able to take advantage of all features of the CDK. For example, they will not be able to use environmental context lookups such as ``ec2.Vpc.fromLookup`` and will not automatically translate Service Principals to the right format based on the environment's AWS partition, and other such enhancements. Default: - The environment of the containing ``Stage`` if available, otherwise create the stack will be environment-agnostic.
        :param notification_arns: SNS Topic ARNs that will receive stack events. Default: - no notfication arns.
        :param permissions_boundary: Options for applying a permissions boundary to all IAM Roles and Users created within this Stage. Default: - no permissions boundary is applied
        :param stack_name: Name to deploy the stack with. Default: - Derived from construct path.
        :param suppress_template_indentation: Enable this flag to suppress indentation in generated CloudFormation templates. If not specified, the value of the ``@aws-cdk/core:suppressTemplateIndentation`` context key will be used. If that is not specified, then the default value ``false`` will be used. Default: - the value of ``@aws-cdk/core:suppressTemplateIndentation``, or ``false`` if that is not set.
        :param synthesizer: Synthesis method to use while deploying this stack. The Stack Synthesizer controls aspects of synthesis and deployment, like how assets are referenced and what IAM roles to use. For more information, see the README of the main CDK package. If not specified, the ``defaultStackSynthesizer`` from ``App`` will be used. If that is not specified, ``DefaultStackSynthesizer`` is used if ``@aws-cdk/core:newStyleStackSynthesis`` is set to ``true`` or the CDK major version is v2. In CDK v1 ``LegacyStackSynthesizer`` is the default if no other synthesizer is specified. Default: - The synthesizer specified on ``App``, or ``DefaultStackSynthesizer`` otherwise.
        :param tags: Stack tags that will be applied to all the taggable resources and the stack itself. Default: {}
        :param termination_protection: Whether to enable termination protection for this stack. Default: false
        :param cidr_block: CIDR block for the VPC.
        :param max_azs: Max AZs.
        :param subnet_cidr_mask: Subnets CIDR masks.
        :param use_proxy: Whether to use a proxy for the VPC. Default value is false.
        :param allow_all_outbound: Whether to allow all outbound traffic by default. If this is set to true, there will only be a single egress rule which allows all outbound traffic. If this is set to false, no outbound traffic will be allowed by default and all egress traffic must be explicitly authorized. Default: true
        :param code_build_vpc_interfaces: The list of CodeBuild VPC InterfacesVpcEndpointAwsServices to extend the defaultCodeBuildVPCInterfaces.
        :param flow_logs_bucket_name: The name of the S3 bucket for VPC flow logs.
        :param restrict_default_security_group: If set to true then the default inbound & outbound rules will be removed from the default security group. Default: true
        :param subnet_type: The subnets attached to the VPC. Default: - Private Subnet only
        '''
        if isinstance(env, dict):
            env = _aws_cdk_ceddda9d.Environment(**env)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__00467d891c9ffdaeb9151b3e4a44fcdfddb5230c8d6204f2f1b47147423de751)
            check_type(argname="argument analytics_reporting", value=analytics_reporting, expected_type=type_hints["analytics_reporting"])
            check_type(argname="argument cross_region_references", value=cross_region_references, expected_type=type_hints["cross_region_references"])
            check_type(argname="argument description", value=description, expected_type=type_hints["description"])
            check_type(argname="argument env", value=env, expected_type=type_hints["env"])
            check_type(argname="argument notification_arns", value=notification_arns, expected_type=type_hints["notification_arns"])
            check_type(argname="argument permissions_boundary", value=permissions_boundary, expected_type=type_hints["permissions_boundary"])
            check_type(argname="argument stack_name", value=stack_name, expected_type=type_hints["stack_name"])
            check_type(argname="argument suppress_template_indentation", value=suppress_template_indentation, expected_type=type_hints["suppress_template_indentation"])
            check_type(argname="argument synthesizer", value=synthesizer, expected_type=type_hints["synthesizer"])
            check_type(argname="argument tags", value=tags, expected_type=type_hints["tags"])
            check_type(argname="argument termination_protection", value=termination_protection, expected_type=type_hints["termination_protection"])
            check_type(argname="argument cidr_block", value=cidr_block, expected_type=type_hints["cidr_block"])
            check_type(argname="argument max_azs", value=max_azs, expected_type=type_hints["max_azs"])
            check_type(argname="argument subnet_cidr_mask", value=subnet_cidr_mask, expected_type=type_hints["subnet_cidr_mask"])
            check_type(argname="argument use_proxy", value=use_proxy, expected_type=type_hints["use_proxy"])
            check_type(argname="argument allow_all_outbound", value=allow_all_outbound, expected_type=type_hints["allow_all_outbound"])
            check_type(argname="argument code_build_vpc_interfaces", value=code_build_vpc_interfaces, expected_type=type_hints["code_build_vpc_interfaces"])
            check_type(argname="argument flow_logs_bucket_name", value=flow_logs_bucket_name, expected_type=type_hints["flow_logs_bucket_name"])
            check_type(argname="argument restrict_default_security_group", value=restrict_default_security_group, expected_type=type_hints["restrict_default_security_group"])
            check_type(argname="argument subnet_type", value=subnet_type, expected_type=type_hints["subnet_type"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "cidr_block": cidr_block,
            "max_azs": max_azs,
            "subnet_cidr_mask": subnet_cidr_mask,
            "use_proxy": use_proxy,
        }
        if analytics_reporting is not None:
            self._values["analytics_reporting"] = analytics_reporting
        if cross_region_references is not None:
            self._values["cross_region_references"] = cross_region_references
        if description is not None:
            self._values["description"] = description
        if env is not None:
            self._values["env"] = env
        if notification_arns is not None:
            self._values["notification_arns"] = notification_arns
        if permissions_boundary is not None:
            self._values["permissions_boundary"] = permissions_boundary
        if stack_name is not None:
            self._values["stack_name"] = stack_name
        if suppress_template_indentation is not None:
            self._values["suppress_template_indentation"] = suppress_template_indentation
        if synthesizer is not None:
            self._values["synthesizer"] = synthesizer
        if tags is not None:
            self._values["tags"] = tags
        if termination_protection is not None:
            self._values["termination_protection"] = termination_protection
        if allow_all_outbound is not None:
            self._values["allow_all_outbound"] = allow_all_outbound
        if code_build_vpc_interfaces is not None:
            self._values["code_build_vpc_interfaces"] = code_build_vpc_interfaces
        if flow_logs_bucket_name is not None:
            self._values["flow_logs_bucket_name"] = flow_logs_bucket_name
        if restrict_default_security_group is not None:
            self._values["restrict_default_security_group"] = restrict_default_security_group
        if subnet_type is not None:
            self._values["subnet_type"] = subnet_type

    @builtins.property
    def analytics_reporting(self) -> typing.Optional[builtins.bool]:
        '''Include runtime versioning information in this Stack.

        :default:

        ``analyticsReporting`` setting of containing ``App``, or value of
        'aws:cdk:version-reporting' context key
        '''
        result = self._values.get("analytics_reporting")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def cross_region_references(self) -> typing.Optional[builtins.bool]:
        '''Enable this flag to allow native cross region stack references.

        Enabling this will create a CloudFormation custom resource
        in both the producing stack and consuming stack in order to perform the export/import

        This feature is currently experimental

        :default: false
        '''
        result = self._values.get("cross_region_references")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def description(self) -> typing.Optional[builtins.str]:
        '''A description of the stack.

        :default: - No description.
        '''
        result = self._values.get("description")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def env(self) -> typing.Optional[_aws_cdk_ceddda9d.Environment]:
        '''The AWS environment (account/region) where this stack will be deployed.

        Set the ``region``/``account`` fields of ``env`` to either a concrete value to
        select the indicated environment (recommended for production stacks), or to
        the values of environment variables
        ``CDK_DEFAULT_REGION``/``CDK_DEFAULT_ACCOUNT`` to let the target environment
        depend on the AWS credentials/configuration that the CDK CLI is executed
        under (recommended for development stacks).

        If the ``Stack`` is instantiated inside a ``Stage``, any undefined
        ``region``/``account`` fields from ``env`` will default to the same field on the
        encompassing ``Stage``, if configured there.

        If either ``region`` or ``account`` are not set nor inherited from ``Stage``, the
        Stack will be considered "*environment-agnostic*"". Environment-agnostic
        stacks can be deployed to any environment but may not be able to take
        advantage of all features of the CDK. For example, they will not be able to
        use environmental context lookups such as ``ec2.Vpc.fromLookup`` and will not
        automatically translate Service Principals to the right format based on the
        environment's AWS partition, and other such enhancements.

        :default:

        - The environment of the containing ``Stage`` if available,
        otherwise create the stack will be environment-agnostic.

        Example::

            // Use a concrete account and region to deploy this stack to:
            // `.account` and `.region` will simply return these values.
            new Stack(app, 'Stack1', {
              env: {
                account: '123456789012',
                region: 'us-east-1'
              },
            });
            
            // Use the CLI's current credentials to determine the target environment:
            // `.account` and `.region` will reflect the account+region the CLI
            // is configured to use (based on the user CLI credentials)
            new Stack(app, 'Stack2', {
              env: {
                account: process.env.CDK_DEFAULT_ACCOUNT,
                region: process.env.CDK_DEFAULT_REGION
              },
            });
            
            // Define multiple stacks stage associated with an environment
            const myStage = new Stage(app, 'MyStage', {
              env: {
                account: '123456789012',
                region: 'us-east-1'
              }
            });
            
            // both of these stacks will use the stage's account/region:
            // `.account` and `.region` will resolve to the concrete values as above
            new MyStack(myStage, 'Stack1');
            new YourStack(myStage, 'Stack2');
            
            // Define an environment-agnostic stack:
            // `.account` and `.region` will resolve to `{ "Ref": "AWS::AccountId" }` and `{ "Ref": "AWS::Region" }` respectively.
            // which will only resolve to actual values by CloudFormation during deployment.
            new MyStack(app, 'Stack1');
        '''
        result = self._values.get("env")
        return typing.cast(typing.Optional[_aws_cdk_ceddda9d.Environment], result)

    @builtins.property
    def notification_arns(self) -> typing.Optional[typing.List[builtins.str]]:
        '''SNS Topic ARNs that will receive stack events.

        :default: - no notfication arns.
        '''
        result = self._values.get("notification_arns")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def permissions_boundary(
        self,
    ) -> typing.Optional[_aws_cdk_ceddda9d.PermissionsBoundary]:
        '''Options for applying a permissions boundary to all IAM Roles and Users created within this Stage.

        :default: - no permissions boundary is applied
        '''
        result = self._values.get("permissions_boundary")
        return typing.cast(typing.Optional[_aws_cdk_ceddda9d.PermissionsBoundary], result)

    @builtins.property
    def stack_name(self) -> typing.Optional[builtins.str]:
        '''Name to deploy the stack with.

        :default: - Derived from construct path.
        '''
        result = self._values.get("stack_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def suppress_template_indentation(self) -> typing.Optional[builtins.bool]:
        '''Enable this flag to suppress indentation in generated CloudFormation templates.

        If not specified, the value of the ``@aws-cdk/core:suppressTemplateIndentation``
        context key will be used. If that is not specified, then the
        default value ``false`` will be used.

        :default: - the value of ``@aws-cdk/core:suppressTemplateIndentation``, or ``false`` if that is not set.
        '''
        result = self._values.get("suppress_template_indentation")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def synthesizer(self) -> typing.Optional[_aws_cdk_ceddda9d.IStackSynthesizer]:
        '''Synthesis method to use while deploying this stack.

        The Stack Synthesizer controls aspects of synthesis and deployment,
        like how assets are referenced and what IAM roles to use. For more
        information, see the README of the main CDK package.

        If not specified, the ``defaultStackSynthesizer`` from ``App`` will be used.
        If that is not specified, ``DefaultStackSynthesizer`` is used if
        ``@aws-cdk/core:newStyleStackSynthesis`` is set to ``true`` or the CDK major
        version is v2. In CDK v1 ``LegacyStackSynthesizer`` is the default if no
        other synthesizer is specified.

        :default: - The synthesizer specified on ``App``, or ``DefaultStackSynthesizer`` otherwise.
        '''
        result = self._values.get("synthesizer")
        return typing.cast(typing.Optional[_aws_cdk_ceddda9d.IStackSynthesizer], result)

    @builtins.property
    def tags(self) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        '''Stack tags that will be applied to all the taggable resources and the stack itself.

        :default: {}
        '''
        result = self._values.get("tags")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], result)

    @builtins.property
    def termination_protection(self) -> typing.Optional[builtins.bool]:
        '''Whether to enable termination protection for this stack.

        :default: false
        '''
        result = self._values.get("termination_protection")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def cidr_block(self) -> builtins.str:
        '''CIDR block for the VPC.'''
        result = self._values.get("cidr_block")
        assert result is not None, "Required property 'cidr_block' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def max_azs(self) -> jsii.Number:
        '''Max AZs.'''
        result = self._values.get("max_azs")
        assert result is not None, "Required property 'max_azs' is missing"
        return typing.cast(jsii.Number, result)

    @builtins.property
    def subnet_cidr_mask(self) -> jsii.Number:
        '''Subnets CIDR masks.'''
        result = self._values.get("subnet_cidr_mask")
        assert result is not None, "Required property 'subnet_cidr_mask' is missing"
        return typing.cast(jsii.Number, result)

    @builtins.property
    def use_proxy(self) -> builtins.bool:
        '''Whether to use a proxy for the VPC.

        Default value is false.
        '''
        result = self._values.get("use_proxy")
        assert result is not None, "Required property 'use_proxy' is missing"
        return typing.cast(builtins.bool, result)

    @builtins.property
    def allow_all_outbound(self) -> typing.Optional[builtins.bool]:
        '''Whether to allow all outbound traffic by default.

        If this is set to true, there will only be a single egress rule which allows all
        outbound traffic. If this is set to false, no outbound traffic will be allowed by
        default and all egress traffic must be explicitly authorized.

        :default: true
        '''
        result = self._values.get("allow_all_outbound")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def code_build_vpc_interfaces(
        self,
    ) -> typing.Optional[typing.List[_aws_cdk_aws_ec2_ceddda9d.InterfaceVpcEndpointAwsService]]:
        '''The list of CodeBuild VPC InterfacesVpcEndpointAwsServices to extend the defaultCodeBuildVPCInterfaces.'''
        result = self._values.get("code_build_vpc_interfaces")
        return typing.cast(typing.Optional[typing.List[_aws_cdk_aws_ec2_ceddda9d.InterfaceVpcEndpointAwsService]], result)

    @builtins.property
    def flow_logs_bucket_name(self) -> typing.Optional[builtins.str]:
        '''The name of the S3 bucket for VPC flow logs.'''
        result = self._values.get("flow_logs_bucket_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def restrict_default_security_group(self) -> typing.Optional[builtins.bool]:
        '''If set to true then the default inbound & outbound rules will be removed from the default security group.

        :default: true
        '''
        result = self._values.get("restrict_default_security_group")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def subnet_type(self) -> typing.Optional[_aws_cdk_aws_ec2_ceddda9d.SubnetType]:
        '''The subnets attached to the VPC.

        :default: - Private Subnet only
        '''
        result = self._values.get("subnet_type")
        return typing.cast(typing.Optional[_aws_cdk_aws_ec2_ceddda9d.SubnetType], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ManagedVPCStackProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.implements(IPhaseCommand)
class NPMPhaseCommand(
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdklabs/cdk-cicd-wrapper.NPMPhaseCommand",
):
    '''Phase command that invokes NPM scripts from project package.json.'''

    def __init__(self, script: builtins.str) -> None:
        '''
        :param script: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__db1030ec2131c2e10ada4ffc3ffa92947ac2264b0db04034128174f579f8a1b4)
            check_type(argname="argument script", value=script, expected_type=type_hints["script"])
        jsii.create(self.__class__, self, [script])

    @builtins.property
    @jsii.member(jsii_name="command")
    def command(self) -> builtins.str:
        '''Returns the command to be executed for the given NPM script.'''
        return typing.cast(builtins.str, jsii.get(self, "command"))

    @builtins.property
    @jsii.member(jsii_name="script")
    def script(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "script"))


@jsii.data_type(
    jsii_type="@cdklabs/cdk-cicd-wrapper.NPMRegistryConfig",
    jsii_struct_bases=[],
    name_mapping={
        "basic_auth_secret_arn": "basicAuthSecretArn",
        "url": "url",
        "scope": "scope",
    },
)
class NPMRegistryConfig:
    def __init__(
        self,
        *,
        basic_auth_secret_arn: builtins.str,
        url: builtins.str,
        scope: typing.Optional[builtins.str] = None,
    ) -> None:
        '''Represents the configuration for an NPM registry.

        :param basic_auth_secret_arn: The ARN of the secret containing the basic auth credentials for the NPM registry.
        :param url: The URL of the NPM registry.
        :param scope: The scope for the NPM registry (optional).
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b332a03f5cb108af1680ca9f1bb11e08566078c9d97d3aaa9446b3d9b353d466)
            check_type(argname="argument basic_auth_secret_arn", value=basic_auth_secret_arn, expected_type=type_hints["basic_auth_secret_arn"])
            check_type(argname="argument url", value=url, expected_type=type_hints["url"])
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "basic_auth_secret_arn": basic_auth_secret_arn,
            "url": url,
        }
        if scope is not None:
            self._values["scope"] = scope

    @builtins.property
    def basic_auth_secret_arn(self) -> builtins.str:
        '''The ARN of the secret containing the basic auth credentials for the NPM registry.'''
        result = self._values.get("basic_auth_secret_arn")
        assert result is not None, "Required property 'basic_auth_secret_arn' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def url(self) -> builtins.str:
        '''The URL of the NPM registry.'''
        result = self._values.get("url")
        assert result is not None, "Required property 'url' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def scope(self) -> typing.Optional[builtins.str]:
        '''The scope for the NPM registry (optional).'''
        result = self._values.get("scope")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "NPMRegistryConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.implements(IVpcConstruct)
class NoVPCStack(
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdklabs/cdk-cicd-wrapper.NoVPCStack",
):
    '''A NoVPCStack that does not create a VPC.'''

    def __init__(self) -> None:
        '''Constructs a new instance of the NoVPCStack class.'''
        jsii.create(self.__class__, self, [])

    @builtins.property
    @jsii.member(jsii_name="codeBuildVPCInterfaces")
    def code_build_vpc_interfaces(
        self,
    ) -> typing.List[_aws_cdk_aws_ec2_ceddda9d.InterfaceVpcEndpointAwsService]:
        '''The list of CodeBuild VPC Interface VPC Endpoint AWS Services.'''
        return typing.cast(typing.List[_aws_cdk_aws_ec2_ceddda9d.InterfaceVpcEndpointAwsService], jsii.get(self, "codeBuildVPCInterfaces"))

    @builtins.property
    @jsii.member(jsii_name="securityGroup")
    def security_group(
        self,
    ) -> typing.Optional[_aws_cdk_aws_ec2_ceddda9d.ISecurityGroup]:
        '''The security group attached to the VPC.'''
        return typing.cast(typing.Optional[_aws_cdk_aws_ec2_ceddda9d.ISecurityGroup], jsii.get(self, "securityGroup"))

    @builtins.property
    @jsii.member(jsii_name="subnetType")
    def subnet_type(self) -> typing.Optional[_aws_cdk_aws_ec2_ceddda9d.SubnetType]:
        '''The subnet type attached to the VPC.'''
        return typing.cast(typing.Optional[_aws_cdk_aws_ec2_ceddda9d.SubnetType], jsii.get(self, "subnetType"))

    @builtins.property
    @jsii.member(jsii_name="vpc")
    def vpc(self) -> typing.Optional[_aws_cdk_aws_ec2_ceddda9d.IVpc]:
        '''The VPC created or looked up by this stack.'''
        return typing.cast(typing.Optional[_aws_cdk_aws_ec2_ceddda9d.IVpc], jsii.get(self, "vpc"))


@jsii.data_type(
    jsii_type="@cdklabs/cdk-cicd-wrapper.PRCheckConfig",
    jsii_struct_bases=[],
    name_mapping={
        "build_spec": "buildSpec",
        "code_build_options": "codeBuildOptions",
        "code_guru_reviewer": "codeGuruReviewer",
    },
)
class PRCheckConfig:
    def __init__(
        self,
        *,
        build_spec: _aws_cdk_aws_codebuild_ceddda9d.BuildSpec,
        code_build_options: typing.Union[_aws_cdk_pipelines_ceddda9d.CodeBuildOptions, typing.Dict[builtins.str, typing.Any]],
        code_guru_reviewer: builtins.bool,
    ) -> None:
        '''Configuration options for enabling pull request checks.

        :param build_spec: The AWS CodeBuild build spec to use for pull request checks.
        :param code_build_options: Additional options for the AWS CodeBuild project used for pull request checks.
        :param code_guru_reviewer: Whether to enable Amazon CodeGuru Reviewer for the repository. Default: false
        '''
        if isinstance(code_build_options, dict):
            code_build_options = _aws_cdk_pipelines_ceddda9d.CodeBuildOptions(**code_build_options)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c426a119773ac893377d5c58bb29ad5dff6d05abbe71ea3c6591cfd4e44e56a2)
            check_type(argname="argument build_spec", value=build_spec, expected_type=type_hints["build_spec"])
            check_type(argname="argument code_build_options", value=code_build_options, expected_type=type_hints["code_build_options"])
            check_type(argname="argument code_guru_reviewer", value=code_guru_reviewer, expected_type=type_hints["code_guru_reviewer"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "build_spec": build_spec,
            "code_build_options": code_build_options,
            "code_guru_reviewer": code_guru_reviewer,
        }

    @builtins.property
    def build_spec(self) -> _aws_cdk_aws_codebuild_ceddda9d.BuildSpec:
        '''The AWS CodeBuild build spec to use for pull request checks.'''
        result = self._values.get("build_spec")
        assert result is not None, "Required property 'build_spec' is missing"
        return typing.cast(_aws_cdk_aws_codebuild_ceddda9d.BuildSpec, result)

    @builtins.property
    def code_build_options(self) -> _aws_cdk_pipelines_ceddda9d.CodeBuildOptions:
        '''Additional options for the AWS CodeBuild project used for pull request checks.'''
        result = self._values.get("code_build_options")
        assert result is not None, "Required property 'code_build_options' is missing"
        return typing.cast(_aws_cdk_pipelines_ceddda9d.CodeBuildOptions, result)

    @builtins.property
    def code_guru_reviewer(self) -> builtins.bool:
        '''Whether to enable Amazon CodeGuru Reviewer for the repository.

        :default: false
        '''
        result = self._values.get("code_guru_reviewer")
        assert result is not None, "Required property 'code_guru_reviewer' is missing"
        return typing.cast(builtins.bool, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "PRCheckConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.implements(IResourceProvider)
class ParameterProvider(
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdklabs/cdk-cicd-wrapper.ParameterProvider",
):
    '''Resource provider that creates Parameters in AWS Systems Manager (SSM).'''

    def __init__(self) -> None:
        jsii.create(self.__class__, self, [])

    @jsii.member(jsii_name="provide")
    def provide(self, context: "ResourceContext") -> typing.Any:
        '''Provides the resources (SSM parameters) based on the given context.

        :param context: - The context that contains scope, blueprint properties, and environment.

        :return: The SSMParameterStack instance
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__58d1b1a41267fdc1330544a8fa0937f6e4a0846a56edb48b7b143e3522060932)
            check_type(argname="argument context", value=context, expected_type=type_hints["context"])
        return typing.cast(typing.Any, jsii.invoke(self, "provide", [context]))


class ParameterResolver(
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdklabs/cdk-cicd-wrapper.ParameterResolver",
):
    '''This class provides functionality to resolve parameter values from AWS Systems Manager Parameter Store or from provided string values.'''

    def __init__(self) -> None:
        jsii.create(self.__class__, self, [])

    @jsii.member(jsii_name="resolveValue")
    @builtins.classmethod
    def resolve_value(
        cls,
        scope: _constructs_77d1e7e8.Construct,
        param: builtins.str,
    ) -> builtins.str:
        '''Resolves the value of a parameter, either from an SSM parameter or using the provided string value.

        :param scope: The scope in which the parameter is resolved.
        :param param: The parameter value to resolve. If it starts with 'ssm:', it will be treated as an SSM parameter name.

        :return: The resolved parameter value.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__88247bee6ba65673ff953f8e7aa6ed1b590a24428384be6dc7c4f7be5a895cc0)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument param", value=param, expected_type=type_hints["param"])
        return typing.cast(builtins.str, jsii.sinvoke(cls, "resolveValue", [scope, param]))

    @jsii.python.classproperty
    @jsii.member(jsii_name="PREFIX")
    def PREFIX(cls) -> builtins.str:
        '''The prefix used to identify parameter resolution from AWS Systems Manager Parameter Store.

        :default: 'resolve'
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "PREFIX"))


@jsii.implements(IResourceProvider)
class PhaseCommandProvider(
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdklabs/cdk-cicd-wrapper.PhaseCommandProvider",
):
    '''Provides the phase commands.'''

    def __init__(self) -> None:
        jsii.create(self.__class__, self, [])

    @jsii.member(jsii_name="provide")
    def provide(self, context: "ResourceContext") -> typing.Any:
        '''Provides resources based on the given context.

        :param context: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2d23320659531364ab50aa4e68cbf0b2eaee552337a74166d327cf86e8c02a08)
            check_type(argname="argument context", value=context, expected_type=type_hints["context"])
        return typing.cast(typing.Any, jsii.invoke(self, "provide", [context]))


class PipelineBlueprint(
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdklabs/cdk-cicd-wrapper.PipelineBlueprint",
):
    '''Class for creating a Pipeline Blueprint.'''

    def __init__(self) -> None:
        jsii.create(self.__class__, self, [])

    @jsii.member(jsii_name="builder")
    @builtins.classmethod
    def builder(cls) -> "PipelineBlueprintBuilder":
        '''Creates a new PipelineBlueprintBuilder instance.

        :return: A PipelineBlueprintBuilder instance.
        '''
        return typing.cast("PipelineBlueprintBuilder", jsii.sinvoke(cls, "builder", []))


class PipelineBlueprintBuilder(
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdklabs/cdk-cicd-wrapper.PipelineBlueprintBuilder",
):
    '''Class for building a Pipeline Blueprint.'''

    def __init__(
        self,
        props: typing.Optional["IPipelineBlueprintProps"] = None,
    ) -> None:
        '''Constructor for the PipelineBlueprintBuilder class.

        :param props: The configuration properties for the Pipeline Blueprint. Defaults to the ``defaultConfigs`` object.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8d9fa55a35936fc5427ea6cb97e35399c50fe9d7c910859f9325155c91d04b3d)
            check_type(argname="argument props", value=props, expected_type=type_hints["props"])
        jsii.create(self.__class__, self, [props])

    @jsii.member(jsii_name="addStack")
    def add_stack(
        self,
        stack_provider: IStackProvider,
        *stages: builtins.str,
    ) -> "PipelineBlueprintBuilder":
        '''Adds a stack to the Pipeline Blueprint.

        :param stack_provider: The stack provider to add.
        :param stages: The stages to which the stack should be added.

        :return: This PipelineBlueprintBuilder instance.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e3932058d67c1f681d71d3c13f355b985131f752dc26b4907512e65c2359eba8)
            check_type(argname="argument stack_provider", value=stack_provider, expected_type=type_hints["stack_provider"])
            check_type(argname="argument stages", value=stages, expected_type=typing.Tuple[type_hints["stages"], ...]) # pyright: ignore [reportGeneralTypeIssues]
        return typing.cast("PipelineBlueprintBuilder", jsii.invoke(self, "addStack", [stack_provider, *stages]))

    @jsii.member(jsii_name="applicationName")
    def application_name(
        self,
        application_name: builtins.str,
    ) -> "PipelineBlueprintBuilder":
        '''Sets the application name for the Pipeline Blueprint.

        :param application_name: The application name to set.

        :return: This PipelineBlueprintBuilder instance.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0fbe70885993bed3b7e4d20588d3470d2821b2c4a1447d580bac812acd2543be)
            check_type(argname="argument application_name", value=application_name, expected_type=type_hints["application_name"])
        return typing.cast("PipelineBlueprintBuilder", jsii.invoke(self, "applicationName", [application_name]))

    @jsii.member(jsii_name="applicationQualifier")
    def application_qualifier(
        self,
        application_qualifier: builtins.str,
    ) -> "PipelineBlueprintBuilder":
        '''Sets the application qualifier for the Pipeline Blueprint.

        :param application_qualifier: The application qualifier to set.

        :return: This PipelineBlueprintBuilder instance.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__043e03cfcd8bedbdcdb5977d825377a84d25dbbb3d90b3447afbc51874ef4916)
            check_type(argname="argument application_qualifier", value=application_qualifier, expected_type=type_hints["application_qualifier"])
        return typing.cast("PipelineBlueprintBuilder", jsii.invoke(self, "applicationQualifier", [application_qualifier]))

    @jsii.member(jsii_name="buildOptions")
    def build_options(
        self,
        *,
        code_build_defaults: typing.Optional[typing.Union[_aws_cdk_pipelines_ceddda9d.CodeBuildOptions, typing.Dict[builtins.str, typing.Any]]] = None,
        run_time_versions: typing.Optional[typing.Union["RuntimeVersionOptions", typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> "PipelineBlueprintBuilder":
        '''Defines the build options for the Pipeline Blueprint.

        :param code_build_defaults: 
        :param run_time_versions: 
        '''
        options = BuildOptions(
            code_build_defaults=code_build_defaults,
            run_time_versions=run_time_versions,
        )

        return typing.cast("PipelineBlueprintBuilder", jsii.invoke(self, "buildOptions", [options]))

    @jsii.member(jsii_name="buildSpec")
    def build_spec(
        self,
        build_spec: _aws_cdk_aws_codebuild_ceddda9d.BuildSpec,
    ) -> "PipelineBlueprintBuilder":
        '''Defines the buildSpec for the Synth step.

        The buildSpec takes precedence over the definedPhases.

        Usage::

              PipelineBlueprint.builder().buildSpec(BuildSpec.fromObject({ phases: { build: { commands: ['npm run build'] } } }))

        :param build_spec: - BuildSpec for the Synth step.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f43a53c89998dc50496696797391217d7f77f7fb8cad74dd75af4ba8a8d18417)
            check_type(argname="argument build_spec", value=build_spec, expected_type=type_hints["build_spec"])
        return typing.cast("PipelineBlueprintBuilder", jsii.invoke(self, "buildSpec", [build_spec]))

    @jsii.member(jsii_name="buildSpecFromFile")
    def build_spec_from_file(
        self,
        file_path: builtins.str,
    ) -> "PipelineBlueprintBuilder":
        '''Defines the buildSpec for the Synth step from a file.

        The buildSpec takes precedence over the definedPhases.

        Usage::

              PipelineBlueprint.builder().buildSpecFromFile('buildspec.yml')

        :param file_path: - Path to the buildspec file.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e66bc7dbb5d232627bdc5724d0e458258fe989d96f52ce58d4544b808cafaf7b)
            check_type(argname="argument file_path", value=file_path, expected_type=type_hints["file_path"])
        return typing.cast("PipelineBlueprintBuilder", jsii.invoke(self, "buildSpecFromFile", [file_path]))

    @jsii.member(jsii_name="codeBuildEnvSettings")
    def code_build_env_settings(
        self,
        *,
        build_image: typing.Optional[_aws_cdk_aws_codebuild_ceddda9d.IBuildImage] = None,
        certificate: typing.Optional[typing.Union[_aws_cdk_aws_codebuild_ceddda9d.BuildEnvironmentCertificate, typing.Dict[builtins.str, typing.Any]]] = None,
        compute_type: typing.Optional[_aws_cdk_aws_codebuild_ceddda9d.ComputeType] = None,
        environment_variables: typing.Optional[typing.Mapping[builtins.str, typing.Union[_aws_cdk_aws_codebuild_ceddda9d.BuildEnvironmentVariable, typing.Dict[builtins.str, typing.Any]]]] = None,
        fleet: typing.Optional[_aws_cdk_aws_codebuild_ceddda9d.IFleet] = None,
        privileged: typing.Optional[builtins.bool] = None,
    ) -> "PipelineBlueprintBuilder":
        '''Sets the CodeBuild environment settings for the Pipeline Blueprint.

        :param build_image: The image used for the builds. Default: LinuxBuildImage.STANDARD_7_0
        :param certificate: The location of the PEM-encoded certificate for the build project. Default: - No external certificate is added to the project
        :param compute_type: The type of compute to use for this build. See the ``ComputeType`` enum for the possible values. Default: taken from ``#buildImage#defaultComputeType``
        :param environment_variables: The environment variables that your builds can use.
        :param fleet: Fleet resource for a reserved capacity CodeBuild project. Fleets allow for process builds or tests to run immediately and reduces build durations, by reserving compute resources for your projects. You will be charged for the resources in the fleet, even if they are idle. Default: - No fleet will be attached to the project, which will remain on-demand.
        :param privileged: Indicates how the project builds Docker images. Specify true to enable running the Docker daemon inside a Docker container. This value must be set to true only if this build project will be used to build Docker images, and the specified build environment image is not one provided by AWS CodeBuild with Docker support. Otherwise, all associated builds that attempt to interact with the Docker daemon will fail. Default: false

        :return: This PipelineBlueprintBuilder instance.
        '''
        code_build_env_settings = _aws_cdk_aws_codebuild_ceddda9d.BuildEnvironment(
            build_image=build_image,
            certificate=certificate,
            compute_type=compute_type,
            environment_variables=environment_variables,
            fleet=fleet,
            privileged=privileged,
        )

        return typing.cast("PipelineBlueprintBuilder", jsii.invoke(self, "codeBuildEnvSettings", [code_build_env_settings]))

    @jsii.member(jsii_name="codeGuruScanThreshold")
    def code_guru_scan_threshold(
        self,
        code_guru_scan_threshold: CodeGuruSeverityThreshold,
    ) -> "PipelineBlueprintBuilder":
        '''Sets the Amazon CodeGuru Reviewer severity threshold for the Pipeline Blueprint.

        :param code_guru_scan_threshold: The Amazon CodeGuru Reviewer severity threshold to set.

        :return: This PipelineBlueprintBuilder instance.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__dd06b480eec7ac0f096afa8e2f9d8ac3762d239ff97e71c7fcf51b8a4db15a75)
            check_type(argname="argument code_guru_scan_threshold", value=code_guru_scan_threshold, expected_type=type_hints["code_guru_scan_threshold"])
        return typing.cast("PipelineBlueprintBuilder", jsii.invoke(self, "codeGuruScanThreshold", [code_guru_scan_threshold]))

    @jsii.member(jsii_name="definePhase")
    def define_phase(
        self,
        phase: "PipelinePhases",
        commands_to_execute: typing.Sequence[IPhaseCommand],
    ) -> "PipelineBlueprintBuilder":
        '''Defines a phase for the Pipeline Blueprint.

        :param phase: The phase to define.
        :param commands_to_execute: The commands to execute during the phase.

        :return: This PipelineBlueprintBuilder instance.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__888c0a8d309e0cd70d56652ee163dc6eb42c31955347584a681d25195430b863)
            check_type(argname="argument phase", value=phase, expected_type=type_hints["phase"])
            check_type(argname="argument commands_to_execute", value=commands_to_execute, expected_type=type_hints["commands_to_execute"])
        return typing.cast("PipelineBlueprintBuilder", jsii.invoke(self, "definePhase", [phase, commands_to_execute]))

    @jsii.member(jsii_name="defineStages")
    def define_stages(
        self,
        stage_definition: typing.Sequence[typing.Union[builtins.str, IStageDefinition]],
    ) -> "PipelineBlueprintBuilder":
        '''Defines the stages for the Pipeline Blueprint.

        :param stage_definition: An array of stage definitions or stage names.

        :return: This PipelineBlueprintBuilder instance.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1a25e970e93c990b233ecb0651d590b18bae77cb11f5a164dd9dbf162940fe8a)
            check_type(argname="argument stage_definition", value=stage_definition, expected_type=type_hints["stage_definition"])
        return typing.cast("PipelineBlueprintBuilder", jsii.invoke(self, "defineStages", [stage_definition]))

    @jsii.member(jsii_name="disable")
    def disable(self, name: builtins.str) -> "PipelineBlueprintBuilder":
        '''
        :param name: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__83c9c30e5c910f8a42c91c2cdfe10b96838427cfad1df0dd0d1f79a25c689743)
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
        return typing.cast("PipelineBlueprintBuilder", jsii.invoke(self, "disable", [name]))

    @jsii.member(jsii_name="id")
    def id(self, id: builtins.str) -> "PipelineBlueprintBuilder":
        '''Sets the ID for the Pipeline Blueprint.

        :param id: The ID to set.

        :return: This PipelineBlueprintBuilder instance.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e6c3e7c1ab6370c7e9e1543431006bb4a8f0633c59a8905776483258a8d5e956)
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        return typing.cast("PipelineBlueprintBuilder", jsii.invoke(self, "id", [id]))

    @jsii.member(jsii_name="logRetentionInDays")
    def log_retention_in_days(
        self,
        log_retention_in_days: builtins.str,
    ) -> "PipelineBlueprintBuilder":
        '''Sets the log retention period in days for the Pipeline Blueprint.

        :param log_retention_in_days: The log retention period in days to set.

        :return: This PipelineBlueprintBuilder instance.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__069e90c1610d43cb2c6ef43b14042fc85fa26ed52ae992b62ad0cb0c44a3ffba)
            check_type(argname="argument log_retention_in_days", value=log_retention_in_days, expected_type=type_hints["log_retention_in_days"])
        return typing.cast("PipelineBlueprintBuilder", jsii.invoke(self, "logRetentionInDays", [log_retention_in_days]))

    @jsii.member(jsii_name="npmRegistry")
    def npm_registry(
        self,
        *,
        basic_auth_secret_arn: builtins.str,
        url: builtins.str,
        scope: typing.Optional[builtins.str] = None,
    ) -> "PipelineBlueprintBuilder":
        '''Sets the NPM registry configuration for the Pipeline Blueprint.

        :param basic_auth_secret_arn: The ARN of the secret containing the basic auth credentials for the NPM registry.
        :param url: The URL of the NPM registry.
        :param scope: The scope for the NPM registry (optional).

        :return: This PipelineBlueprintBuilder instance.
        '''
        npm_registry = NPMRegistryConfig(
            basic_auth_secret_arn=basic_auth_secret_arn, url=url, scope=scope
        )

        return typing.cast("PipelineBlueprintBuilder", jsii.invoke(self, "npmRegistry", [npm_registry]))

    @jsii.member(jsii_name="pipelineOptions")
    def pipeline_options(
        self,
        *,
        pipeline_type: _aws_cdk_aws_codepipeline_ceddda9d.PipelineType,
        docker_credentials: typing.Optional[typing.Sequence[_aws_cdk_pipelines_ceddda9d.DockerCredential]] = None,
        publish_assets_in_parallel: typing.Optional[builtins.bool] = None,
        self_mutation: typing.Optional[builtins.bool] = None,
        use_change_sets: typing.Optional[builtins.bool] = None,
    ) -> "PipelineBlueprintBuilder":
        '''Defines the pipeline options for the Pipeline Blueprint.

        :param pipeline_type: The pipeline type to use. Default: - The default pipeline type is V1.
        :param docker_credentials: A list of credentials used to authenticate to Docker registries. Specify any credentials necessary within the pipeline to build, synth, update, or publish assets. Default: []
        :param publish_assets_in_parallel: Publish assets in multiple CodeBuild projects. If set to false, use one Project per type to publish all assets. Publishing in parallel improves concurrency and may reduce publishing latency, but may also increase overall provisioning time of the CodeBuild projects. Experiment and see what value works best for you. Default: true
        :param self_mutation: Whether the pipeline should allow self-mutation.
        :param use_change_sets: Deploy every stack by creating a change set and executing it. When enabled, creates a "Prepare" and "Execute" action for each stack. Disable to deploy the stack in one pipeline action. Default: true
        '''
        options = PipelineOptions(
            pipeline_type=pipeline_type,
            docker_credentials=docker_credentials,
            publish_assets_in_parallel=publish_assets_in_parallel,
            self_mutation=self_mutation,
            use_change_sets=use_change_sets,
        )

        return typing.cast("PipelineBlueprintBuilder", jsii.invoke(self, "pipelineOptions", [options]))

    @jsii.member(jsii_name="plugin")
    def plugin(self, plugin: IPlugin) -> "PipelineBlueprintBuilder":
        '''Adds a plugin to the Pipeline Blueprint.

        :param plugin: The plugin to add.

        :return: This PipelineBlueprintBuilder instance.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8a3183666d8c9303b29fc55e929aae211c7873631be8e182ab032d34792ee111)
            check_type(argname="argument plugin", value=plugin, expected_type=type_hints["plugin"])
        return typing.cast("PipelineBlueprintBuilder", jsii.invoke(self, "plugin", [plugin]))

    @jsii.member(jsii_name="primaryOutputDirectory")
    def primary_output_directory(
        self,
        primary_output_directory: builtins.str,
    ) -> "PipelineBlueprintBuilder":
        '''Defines the primary output directory for the CDK Synth.

        :param primary_output_directory: Configures the primary output directory for the synth step.

        :default: './cdk.out'
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__de2cafae27b0a8b224592ddb7b3e0c866e606b476cc82a384f7e17b21e903b55)
            check_type(argname="argument primary_output_directory", value=primary_output_directory, expected_type=type_hints["primary_output_directory"])
        return typing.cast("PipelineBlueprintBuilder", jsii.invoke(self, "primaryOutputDirectory", [primary_output_directory]))

    @jsii.member(jsii_name="proxy")
    def proxy(
        self,
        proxy: typing.Optional[IProxyConfig] = None,
    ) -> "PipelineBlueprintBuilder":
        '''Sets the proxy configuration for the Pipeline Blueprint.

        :param proxy: The proxy configuration to set. If not provided, a default proxy configuration will be used.

        :return: This PipelineBlueprintBuilder instance.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__257f02515607ca7b2cbac870b9dc51acd5825eee3eea8b2541d187d31d8c6170)
            check_type(argname="argument proxy", value=proxy, expected_type=type_hints["proxy"])
        return typing.cast("PipelineBlueprintBuilder", jsii.invoke(self, "proxy", [proxy]))

    @jsii.member(jsii_name="region")
    def region(self, region: builtins.str) -> "PipelineBlueprintBuilder":
        '''Sets the AWS region for the Pipeline Blueprint.

        :param region: The AWS region to set.

        :return: This PipelineBlueprintBuilder instance.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c4fb5ed816611a8a70f08dd308e0bed206030900f86c7344c801f76c4702132d)
            check_type(argname="argument region", value=region, expected_type=type_hints["region"])
        return typing.cast("PipelineBlueprintBuilder", jsii.invoke(self, "region", [region]))

    @jsii.member(jsii_name="repository")
    def repository(
        self,
        repository_source: "RepositorySource",
    ) -> "PipelineBlueprintBuilder":
        '''
        :param repository_source: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f4420b671e8440f0a0480eb324d0348d3e070a960cb8c6a0079a8065f84add05)
            check_type(argname="argument repository_source", value=repository_source, expected_type=type_hints["repository_source"])
        return typing.cast("PipelineBlueprintBuilder", jsii.invoke(self, "repository", [repository_source]))

    @jsii.member(jsii_name="repositoryProvider")
    def repository_provider(
        self,
        repository_provider: IResourceProvider,
    ) -> "PipelineBlueprintBuilder":
        '''Sets the repository provider for the Pipeline Blueprint.

        :param repository_provider: The repository provider to set.

        :return: This PipelineBlueprintBuilder instance.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__669b5d7571521122e2a07e6927208f54a1970d3f1499f36240a119a80f76bb11)
            check_type(argname="argument repository_provider", value=repository_provider, expected_type=type_hints["repository_provider"])
        return typing.cast("PipelineBlueprintBuilder", jsii.invoke(self, "repositoryProvider", [repository_provider]))

    @jsii.member(jsii_name="resourceProvider")
    def resource_provider(
        self,
        name: builtins.str,
        provider: IResourceProvider,
    ) -> "PipelineBlueprintBuilder":
        '''Sets a resource provider for the Pipeline Blueprint.

        :param name: The name of the resource provider.
        :param provider: The resource provider to set.

        :return: This PipelineBlueprintBuilder instance.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__dc3b4580752fe4a8e1a1b1b27a59031558d39f1726d08d645f3ffb902f8bd8d0)
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
        return typing.cast("PipelineBlueprintBuilder", jsii.invoke(self, "resourceProvider", [name, provider]))

    @jsii.member(jsii_name="synth")
    def synth(self, app: _aws_cdk_ceddda9d.App) -> _aws_cdk_ceddda9d.Stack:
        '''Synthesizes the Pipeline Blueprint and creates the necessary stacks.

        :param app: The CDK app instance.

        :return: The created stack.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5b82264054c5081c0202d720cf235cc8363756098c9c30b6c77bda9b8563276d)
            check_type(argname="argument app", value=app, expected_type=type_hints["app"])
        return typing.cast(_aws_cdk_ceddda9d.Stack, jsii.invoke(self, "synth", [app]))

    @jsii.member(jsii_name="workbench")
    def workbench(
        self,
        stack_provider: IStackProvider,
        *,
        stage_to_use: typing.Optional[builtins.str] = None,
        workbench_prefix: typing.Optional[builtins.str] = None,
    ) -> "PipelineBlueprintBuilder":
        '''Sets up a workbench environment for the Pipeline Blueprint.

        :param stack_provider: The stack provider for the workbench environment.
        :param stage_to_use: The stage to use for the workbench (optional).
        :param workbench_prefix: The prefix for the workbench (optional).

        :return: This PipelineBlueprintBuilder instance.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7a227c2795585c5792f9af4e6d26cb1058d189a051941a517c1dca61b3340a59)
            check_type(argname="argument stack_provider", value=stack_provider, expected_type=type_hints["stack_provider"])
        option = WorkbenchOptions(
            stage_to_use=stage_to_use, workbench_prefix=workbench_prefix
        )

        return typing.cast("PipelineBlueprintBuilder", jsii.invoke(self, "workbench", [stack_provider, option]))


@jsii.data_type(
    jsii_type="@cdklabs/cdk-cicd-wrapper.PipelineOptions",
    jsii_struct_bases=[],
    name_mapping={
        "pipeline_type": "pipelineType",
        "docker_credentials": "dockerCredentials",
        "publish_assets_in_parallel": "publishAssetsInParallel",
        "self_mutation": "selfMutation",
        "use_change_sets": "useChangeSets",
    },
)
class PipelineOptions:
    def __init__(
        self,
        *,
        pipeline_type: _aws_cdk_aws_codepipeline_ceddda9d.PipelineType,
        docker_credentials: typing.Optional[typing.Sequence[_aws_cdk_pipelines_ceddda9d.DockerCredential]] = None,
        publish_assets_in_parallel: typing.Optional[builtins.bool] = None,
        self_mutation: typing.Optional[builtins.bool] = None,
        use_change_sets: typing.Optional[builtins.bool] = None,
    ) -> None:
        '''
        :param pipeline_type: The pipeline type to use. Default: - The default pipeline type is V1.
        :param docker_credentials: A list of credentials used to authenticate to Docker registries. Specify any credentials necessary within the pipeline to build, synth, update, or publish assets. Default: []
        :param publish_assets_in_parallel: Publish assets in multiple CodeBuild projects. If set to false, use one Project per type to publish all assets. Publishing in parallel improves concurrency and may reduce publishing latency, but may also increase overall provisioning time of the CodeBuild projects. Experiment and see what value works best for you. Default: true
        :param self_mutation: Whether the pipeline should allow self-mutation.
        :param use_change_sets: Deploy every stack by creating a change set and executing it. When enabled, creates a "Prepare" and "Execute" action for each stack. Disable to deploy the stack in one pipeline action. Default: true
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__52896c1bf00490014e35c3e554377df286a6dea674c0a39a8ba117796da24a32)
            check_type(argname="argument pipeline_type", value=pipeline_type, expected_type=type_hints["pipeline_type"])
            check_type(argname="argument docker_credentials", value=docker_credentials, expected_type=type_hints["docker_credentials"])
            check_type(argname="argument publish_assets_in_parallel", value=publish_assets_in_parallel, expected_type=type_hints["publish_assets_in_parallel"])
            check_type(argname="argument self_mutation", value=self_mutation, expected_type=type_hints["self_mutation"])
            check_type(argname="argument use_change_sets", value=use_change_sets, expected_type=type_hints["use_change_sets"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "pipeline_type": pipeline_type,
        }
        if docker_credentials is not None:
            self._values["docker_credentials"] = docker_credentials
        if publish_assets_in_parallel is not None:
            self._values["publish_assets_in_parallel"] = publish_assets_in_parallel
        if self_mutation is not None:
            self._values["self_mutation"] = self_mutation
        if use_change_sets is not None:
            self._values["use_change_sets"] = use_change_sets

    @builtins.property
    def pipeline_type(self) -> _aws_cdk_aws_codepipeline_ceddda9d.PipelineType:
        '''The pipeline type to use.

        :default: - The default pipeline type is V1.

        :see: https://docs.aws.amazon.com/cdk/api/latest/docs/aws-cdk-lib.pipelines-readme.html#pipeline-types
        '''
        result = self._values.get("pipeline_type")
        assert result is not None, "Required property 'pipeline_type' is missing"
        return typing.cast(_aws_cdk_aws_codepipeline_ceddda9d.PipelineType, result)

    @builtins.property
    def docker_credentials(
        self,
    ) -> typing.Optional[typing.List[_aws_cdk_pipelines_ceddda9d.DockerCredential]]:
        '''A list of credentials used to authenticate to Docker registries.

        Specify any credentials necessary within the pipeline to build, synth, update, or publish assets.

        :default: []
        '''
        result = self._values.get("docker_credentials")
        return typing.cast(typing.Optional[typing.List[_aws_cdk_pipelines_ceddda9d.DockerCredential]], result)

    @builtins.property
    def publish_assets_in_parallel(self) -> typing.Optional[builtins.bool]:
        '''Publish assets in multiple CodeBuild projects.

        If set to false, use one Project per type to publish all assets.

        Publishing in parallel improves concurrency and may reduce publishing
        latency, but may also increase overall provisioning time of the CodeBuild
        projects.

        Experiment and see what value works best for you.

        :default: true
        '''
        result = self._values.get("publish_assets_in_parallel")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def self_mutation(self) -> typing.Optional[builtins.bool]:
        '''Whether the pipeline should allow self-mutation.'''
        result = self._values.get("self_mutation")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def use_change_sets(self) -> typing.Optional[builtins.bool]:
        '''Deploy every stack by creating a change set and executing it.

        When enabled, creates a "Prepare" and "Execute" action for each stack. Disable
        to deploy the stack in one pipeline action.

        :default: true
        '''
        result = self._values.get("use_change_sets")
        return typing.cast(typing.Optional[builtins.bool], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "PipelineOptions(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.enum(jsii_type="@cdklabs/cdk-cicd-wrapper.PipelinePhases")
class PipelinePhases(enum.Enum):
    '''Represents the phases in a pipeline.'''

    INITIALIZE = "INITIALIZE"
    '''The initialize phase.'''
    PRE_BUILD = "PRE_BUILD"
    '''The pre-build phase.'''
    BUILD = "BUILD"
    '''The build phase.'''
    TESTING = "TESTING"
    '''The testing phase.'''
    PRE_DEPLOY = "PRE_DEPLOY"
    '''The pre-deploy phase.'''
    POST_DEPLOY = "POST_DEPLOY"
    '''The post-deploy phase.'''


@jsii.data_type(
    jsii_type="@cdklabs/cdk-cicd-wrapper.PipelineProps",
    jsii_struct_bases=[],
    name_mapping={
        "branch": "branch",
        "ci_build_spec": "ciBuildSpec",
        "code_build_defaults": "codeBuildDefaults",
        "primary_output_directory": "primaryOutputDirectory",
        "repository_input": "repositoryInput",
        "build_image": "buildImage",
        "code_guru_scan_threshold": "codeGuruScanThreshold",
        "install_commands": "installCommands",
        "is_docker_enabled_for_synth": "isDockerEnabledForSynth",
        "options": "options",
        "pipeline_variables": "pipelineVariables",
        "synth_code_build_defaults": "synthCodeBuildDefaults",
        "vpc_props": "vpcProps",
    },
)
class PipelineProps:
    def __init__(
        self,
        *,
        branch: builtins.str,
        ci_build_spec: _aws_cdk_aws_codebuild_ceddda9d.BuildSpec,
        code_build_defaults: typing.Union[_aws_cdk_pipelines_ceddda9d.CodeBuildOptions, typing.Dict[builtins.str, typing.Any]],
        primary_output_directory: builtins.str,
        repository_input: _aws_cdk_pipelines_ceddda9d.IFileSetProducer,
        build_image: typing.Optional[_aws_cdk_aws_codebuild_ceddda9d.IBuildImage] = None,
        code_guru_scan_threshold: typing.Optional[CodeGuruSeverityThreshold] = None,
        install_commands: typing.Optional[typing.Sequence[builtins.str]] = None,
        is_docker_enabled_for_synth: typing.Optional[builtins.bool] = None,
        options: typing.Optional[typing.Union[PipelineOptions, typing.Dict[builtins.str, typing.Any]]] = None,
        pipeline_variables: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        synth_code_build_defaults: typing.Optional[typing.Union[_aws_cdk_pipelines_ceddda9d.CodeBuildOptions, typing.Dict[builtins.str, typing.Any]]] = None,
        vpc_props: typing.Optional[typing.Union["VpcProps", typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''Props for configuring the pipeline.

        :param branch: The branch to be used from the source repository.
        :param ci_build_spec: The CI commands to be executed as part of the Synth step.
        :param code_build_defaults: Default options for CodeBuild projects in the pipeline.
        :param primary_output_directory: The primary output directory for the synth step.
        :param repository_input: The source repository for the pipeline.
        :param build_image: The Docker image to be used for the build project.
        :param code_guru_scan_threshold: The severity threshold for CodeGuru security scans.
        :param install_commands: Additional install commands to be executed before the synth step.
        :param is_docker_enabled_for_synth: Whether Docker should be enabled for synth. Default: false
        :param options: Additional Pipeline options.
        :param pipeline_variables: Pipeline variables to be passed as environment variables.
        :param synth_code_build_defaults: Default options for the synth CodeBuild project.
        :param vpc_props: VPC configuration for the pipeline.
        '''
        if isinstance(code_build_defaults, dict):
            code_build_defaults = _aws_cdk_pipelines_ceddda9d.CodeBuildOptions(**code_build_defaults)
        if isinstance(options, dict):
            options = PipelineOptions(**options)
        if isinstance(synth_code_build_defaults, dict):
            synth_code_build_defaults = _aws_cdk_pipelines_ceddda9d.CodeBuildOptions(**synth_code_build_defaults)
        if isinstance(vpc_props, dict):
            vpc_props = VpcProps(**vpc_props)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__eea3324e3b8fd85555f6fdf9982b07417cf8c57ec0fe84753017f088babfdd5f)
            check_type(argname="argument branch", value=branch, expected_type=type_hints["branch"])
            check_type(argname="argument ci_build_spec", value=ci_build_spec, expected_type=type_hints["ci_build_spec"])
            check_type(argname="argument code_build_defaults", value=code_build_defaults, expected_type=type_hints["code_build_defaults"])
            check_type(argname="argument primary_output_directory", value=primary_output_directory, expected_type=type_hints["primary_output_directory"])
            check_type(argname="argument repository_input", value=repository_input, expected_type=type_hints["repository_input"])
            check_type(argname="argument build_image", value=build_image, expected_type=type_hints["build_image"])
            check_type(argname="argument code_guru_scan_threshold", value=code_guru_scan_threshold, expected_type=type_hints["code_guru_scan_threshold"])
            check_type(argname="argument install_commands", value=install_commands, expected_type=type_hints["install_commands"])
            check_type(argname="argument is_docker_enabled_for_synth", value=is_docker_enabled_for_synth, expected_type=type_hints["is_docker_enabled_for_synth"])
            check_type(argname="argument options", value=options, expected_type=type_hints["options"])
            check_type(argname="argument pipeline_variables", value=pipeline_variables, expected_type=type_hints["pipeline_variables"])
            check_type(argname="argument synth_code_build_defaults", value=synth_code_build_defaults, expected_type=type_hints["synth_code_build_defaults"])
            check_type(argname="argument vpc_props", value=vpc_props, expected_type=type_hints["vpc_props"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "branch": branch,
            "ci_build_spec": ci_build_spec,
            "code_build_defaults": code_build_defaults,
            "primary_output_directory": primary_output_directory,
            "repository_input": repository_input,
        }
        if build_image is not None:
            self._values["build_image"] = build_image
        if code_guru_scan_threshold is not None:
            self._values["code_guru_scan_threshold"] = code_guru_scan_threshold
        if install_commands is not None:
            self._values["install_commands"] = install_commands
        if is_docker_enabled_for_synth is not None:
            self._values["is_docker_enabled_for_synth"] = is_docker_enabled_for_synth
        if options is not None:
            self._values["options"] = options
        if pipeline_variables is not None:
            self._values["pipeline_variables"] = pipeline_variables
        if synth_code_build_defaults is not None:
            self._values["synth_code_build_defaults"] = synth_code_build_defaults
        if vpc_props is not None:
            self._values["vpc_props"] = vpc_props

    @builtins.property
    def branch(self) -> builtins.str:
        '''The branch to be used from the source repository.'''
        result = self._values.get("branch")
        assert result is not None, "Required property 'branch' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def ci_build_spec(self) -> _aws_cdk_aws_codebuild_ceddda9d.BuildSpec:
        '''The CI commands to be executed as part of the Synth step.'''
        result = self._values.get("ci_build_spec")
        assert result is not None, "Required property 'ci_build_spec' is missing"
        return typing.cast(_aws_cdk_aws_codebuild_ceddda9d.BuildSpec, result)

    @builtins.property
    def code_build_defaults(self) -> _aws_cdk_pipelines_ceddda9d.CodeBuildOptions:
        '''Default options for CodeBuild projects in the pipeline.'''
        result = self._values.get("code_build_defaults")
        assert result is not None, "Required property 'code_build_defaults' is missing"
        return typing.cast(_aws_cdk_pipelines_ceddda9d.CodeBuildOptions, result)

    @builtins.property
    def primary_output_directory(self) -> builtins.str:
        '''The primary output directory for the synth step.'''
        result = self._values.get("primary_output_directory")
        assert result is not None, "Required property 'primary_output_directory' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def repository_input(self) -> _aws_cdk_pipelines_ceddda9d.IFileSetProducer:
        '''The source repository for the pipeline.'''
        result = self._values.get("repository_input")
        assert result is not None, "Required property 'repository_input' is missing"
        return typing.cast(_aws_cdk_pipelines_ceddda9d.IFileSetProducer, result)

    @builtins.property
    def build_image(
        self,
    ) -> typing.Optional[_aws_cdk_aws_codebuild_ceddda9d.IBuildImage]:
        '''The Docker image to be used for the build project.'''
        result = self._values.get("build_image")
        return typing.cast(typing.Optional[_aws_cdk_aws_codebuild_ceddda9d.IBuildImage], result)

    @builtins.property
    def code_guru_scan_threshold(self) -> typing.Optional[CodeGuruSeverityThreshold]:
        '''The severity threshold for CodeGuru security scans.'''
        result = self._values.get("code_guru_scan_threshold")
        return typing.cast(typing.Optional[CodeGuruSeverityThreshold], result)

    @builtins.property
    def install_commands(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Additional install commands to be executed before the synth step.'''
        result = self._values.get("install_commands")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def is_docker_enabled_for_synth(self) -> typing.Optional[builtins.bool]:
        '''Whether Docker should be enabled for synth.

        :default: false
        '''
        result = self._values.get("is_docker_enabled_for_synth")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def options(self) -> typing.Optional[PipelineOptions]:
        '''Additional Pipeline options.'''
        result = self._values.get("options")
        return typing.cast(typing.Optional[PipelineOptions], result)

    @builtins.property
    def pipeline_variables(
        self,
    ) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        '''Pipeline variables to be passed as environment variables.'''
        result = self._values.get("pipeline_variables")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], result)

    @builtins.property
    def synth_code_build_defaults(
        self,
    ) -> typing.Optional[_aws_cdk_pipelines_ceddda9d.CodeBuildOptions]:
        '''Default options for the synth CodeBuild project.'''
        result = self._values.get("synth_code_build_defaults")
        return typing.cast(typing.Optional[_aws_cdk_pipelines_ceddda9d.CodeBuildOptions], result)

    @builtins.property
    def vpc_props(self) -> typing.Optional["VpcProps"]:
        '''VPC configuration for the pipeline.'''
        result = self._values.get("vpc_props")
        return typing.cast(typing.Optional["VpcProps"], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "PipelineProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.implements(IPlugin)
class PluginBase(
    metaclass=jsii.JSIIAbstractClass,
    jsii_type="@cdklabs/cdk-cicd-wrapper.PluginBase",
):
    def __init__(self) -> None:
        jsii.create(self.__class__, self, [])

    @jsii.member(jsii_name="afterStage")
    def after_stage(
        self,
        scope: _constructs_77d1e7e8.Construct,
        context: "ResourceContext",
    ) -> None:
        '''The method called after the stage is created.

        :param scope: -
        :param context: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e719a4ad9cfdd62aa1cb38580c0026d384dfb7fea4f275a417b2bf25a3b5df16)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument context", value=context, expected_type=type_hints["context"])
        return typing.cast(None, jsii.invoke(self, "afterStage", [scope, context]))

    @jsii.member(jsii_name="beforeStage")
    def before_stage(
        self,
        scope: _constructs_77d1e7e8.Construct,
        context: "ResourceContext",
    ) -> None:
        '''The method called before the stage is created.

        :param scope: -
        :param context: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__49465724184f1e1b2dffd7e1bb267264b426f64fdae78a1e05655cb8ce8bf12b)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument context", value=context, expected_type=type_hints["context"])
        return typing.cast(None, jsii.invoke(self, "beforeStage", [scope, context]))

    @jsii.member(jsii_name="create")
    def create(self, context: "ResourceContext") -> None:
        '''The method called when the Pipeline configuration finalized.

        :param context: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__69e2889677167aaaee4e737eacef4ebd7a5a427e276383982069fab8bbaa0b81)
            check_type(argname="argument context", value=context, expected_type=type_hints["context"])
        return typing.cast(None, jsii.invoke(self, "create", [context]))

    @builtins.property
    @jsii.member(jsii_name="name")
    @abc.abstractmethod
    def name(self) -> builtins.str:
        '''The name of the plugin.'''
        ...

    @builtins.property
    @jsii.member(jsii_name="version")
    @abc.abstractmethod
    def version(self) -> builtins.str:
        '''The version of the plugin.'''
        ...


class _PluginBaseProxy(PluginBase):
    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        '''The name of the plugin.'''
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @builtins.property
    @jsii.member(jsii_name="version")
    def version(self) -> builtins.str:
        '''The version of the plugin.'''
        return typing.cast(builtins.str, jsii.get(self, "version"))

# Adding a "__jsii_proxy_class__(): typing.Type" function to the abstract class
typing.cast(typing.Any, PluginBase).__jsii_proxy_class__ = lambda : _PluginBaseProxy


class Plugins(metaclass=jsii.JSIIMeta, jsii_type="@cdklabs/cdk-cicd-wrapper.Plugins"):
    '''Class containing static instances of various security and optimization plugins.'''

    def __init__(self) -> None:
        jsii.create(self.__class__, self, [])

    @jsii.python.classproperty
    @jsii.member(jsii_name="AccessLogsForBucketPlugin")
    def ACCESS_LOGS_FOR_BUCKET_PLUGIN(cls) -> "AccessLogsForBucketPlugin":
        '''Static instance of the AccessLogsForBucketPlugin.'''
        return typing.cast("AccessLogsForBucketPlugin", jsii.sget(cls, "AccessLogsForBucketPlugin"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="DestroyEncryptionKeysOnDeletePlugin")
    def DESTROY_ENCRYPTION_KEYS_ON_DELETE_PLUGIN(
        cls,
    ) -> "DestroyEncryptionKeysOnDeletePlugin":
        '''Static instance of the DestroyEncryptionKeysOnDeletePlugin.'''
        return typing.cast("DestroyEncryptionKeysOnDeletePlugin", jsii.sget(cls, "DestroyEncryptionKeysOnDeletePlugin"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="DisablePublicIPAssignmentForEC2Plugin")
    def DISABLE_PUBLIC_IP_ASSIGNMENT_FOR_EC2_PLUGIN(
        cls,
    ) -> "DisablePublicIPAssignmentForEC2Plugin":
        '''Static instance of the DisablePublicIPAssignmentForEC2Plugin.'''
        return typing.cast("DisablePublicIPAssignmentForEC2Plugin", jsii.sget(cls, "DisablePublicIPAssignmentForEC2Plugin"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="EncryptBucketOnTransitPlugin")
    def ENCRYPT_BUCKET_ON_TRANSIT_PLUGIN(cls) -> "EncryptBucketOnTransitPlugin":
        '''Static instance of the EncryptBucketOnTransitPlugin.'''
        return typing.cast("EncryptBucketOnTransitPlugin", jsii.sget(cls, "EncryptBucketOnTransitPlugin"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="EncryptCloudWatchLogGroupsPlugin")
    def ENCRYPT_CLOUD_WATCH_LOG_GROUPS_PLUGIN(
        cls,
    ) -> "EncryptCloudWatchLogGroupsPlugin":
        '''Static instance of the EncryptCloudWatchLogGroupsPlugin.'''
        return typing.cast("EncryptCloudWatchLogGroupsPlugin", jsii.sget(cls, "EncryptCloudWatchLogGroupsPlugin"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="EncryptSNSTopicOnTransitPlugin")
    def ENCRYPT_SNS_TOPIC_ON_TRANSIT_PLUGIN(cls) -> "EncryptSNSTopicOnTransitPlugin":
        '''Static instance of the EncryptSNSTopicOnTransitPlugin.'''
        return typing.cast("EncryptSNSTopicOnTransitPlugin", jsii.sget(cls, "EncryptSNSTopicOnTransitPlugin"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="RotateEncryptionKeysPlugin")
    def ROTATE_ENCRYPTION_KEYS_PLUGIN(cls) -> "RotateEncryptionKeysPlugin":
        '''Static instance of the RotateEncryptionKeysPlugin.'''
        return typing.cast("RotateEncryptionKeysPlugin", jsii.sget(cls, "RotateEncryptionKeysPlugin"))


class PostDeployBuildStep(
    _aws_cdk_pipelines_ceddda9d.CodeBuildStep,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdklabs/cdk-cicd-wrapper.PostDeployBuildStep",
):
    '''A class that represents a post-deployment build step in a CDK pipeline.

    This step is responsible for running commands after a successful deployment.
    '''

    def __init__(
        self,
        stage: builtins.str,
        props: typing.Union[_aws_cdk_pipelines_ceddda9d.CodeBuildStepProps, typing.Dict[builtins.str, typing.Any]],
        application_name: builtins.str,
        role_arn: builtins.str,
    ) -> None:
        '''Constructs a new instance of the PostDeployBuildStep class.

        :param stage: The stage of the pipeline in which this step is executed.
        :param props: The properties for the CodeBuild step.
        :param application_name: The name of the application.
        :param role_arn: The ARN of the role used for post build step.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9f7afea493adedc2b081e5ea11b7fd108a0c91e0c862989ec3c81f8201106dcd)
            check_type(argname="argument stage", value=stage, expected_type=type_hints["stage"])
            check_type(argname="argument props", value=props, expected_type=type_hints["props"])
            check_type(argname="argument application_name", value=application_name, expected_type=type_hints["application_name"])
            check_type(argname="argument role_arn", value=role_arn, expected_type=type_hints["role_arn"])
        jsii.create(self.__class__, self, [stage, props, application_name, role_arn])


class PostDeployExecutorStack(
    _aws_cdk_ceddda9d.Stack,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdklabs/cdk-cicd-wrapper.PostDeployExecutorStack",
):
    '''Stack for creating an IAM role used for Post Deploy command executions.'''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        name: builtins.str,
        res_account: builtins.str,
        stage_name: builtins.str,
        inline_policies: typing.Optional[typing.Mapping[builtins.str, _aws_cdk_aws_iam_ceddda9d.PolicyDocument]] = None,
        prefix: typing.Optional[builtins.str] = None,
        analytics_reporting: typing.Optional[builtins.bool] = None,
        cross_region_references: typing.Optional[builtins.bool] = None,
        description: typing.Optional[builtins.str] = None,
        env: typing.Optional[typing.Union[_aws_cdk_ceddda9d.Environment, typing.Dict[builtins.str, typing.Any]]] = None,
        notification_arns: typing.Optional[typing.Sequence[builtins.str]] = None,
        permissions_boundary: typing.Optional[_aws_cdk_ceddda9d.PermissionsBoundary] = None,
        stack_name: typing.Optional[builtins.str] = None,
        suppress_template_indentation: typing.Optional[builtins.bool] = None,
        synthesizer: typing.Optional[_aws_cdk_ceddda9d.IStackSynthesizer] = None,
        tags: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        termination_protection: typing.Optional[builtins.bool] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param name: The name of the application.
        :param res_account: The AWS account ID where the resources will be deployed.
        :param stage_name: The name of the deployment stage (e.g., 'prod', 'test').
        :param inline_policies: A list of named policies to inline into this role. These policies will be created with the role, whereas those added by ``addToPolicy`` are added using a separate CloudFormation resource (allowing a way around circular dependencies that could otherwise be introduced). Default: - No policy is inlined in the Role resource.
        :param prefix: The prefix to use for resource names.
        :param analytics_reporting: Include runtime versioning information in this Stack. Default: ``analyticsReporting`` setting of containing ``App``, or value of 'aws:cdk:version-reporting' context key
        :param cross_region_references: Enable this flag to allow native cross region stack references. Enabling this will create a CloudFormation custom resource in both the producing stack and consuming stack in order to perform the export/import This feature is currently experimental Default: false
        :param description: A description of the stack. Default: - No description.
        :param env: The AWS environment (account/region) where this stack will be deployed. Set the ``region``/``account`` fields of ``env`` to either a concrete value to select the indicated environment (recommended for production stacks), or to the values of environment variables ``CDK_DEFAULT_REGION``/``CDK_DEFAULT_ACCOUNT`` to let the target environment depend on the AWS credentials/configuration that the CDK CLI is executed under (recommended for development stacks). If the ``Stack`` is instantiated inside a ``Stage``, any undefined ``region``/``account`` fields from ``env`` will default to the same field on the encompassing ``Stage``, if configured there. If either ``region`` or ``account`` are not set nor inherited from ``Stage``, the Stack will be considered "*environment-agnostic*"". Environment-agnostic stacks can be deployed to any environment but may not be able to take advantage of all features of the CDK. For example, they will not be able to use environmental context lookups such as ``ec2.Vpc.fromLookup`` and will not automatically translate Service Principals to the right format based on the environment's AWS partition, and other such enhancements. Default: - The environment of the containing ``Stage`` if available, otherwise create the stack will be environment-agnostic.
        :param notification_arns: SNS Topic ARNs that will receive stack events. Default: - no notfication arns.
        :param permissions_boundary: Options for applying a permissions boundary to all IAM Roles and Users created within this Stage. Default: - no permissions boundary is applied
        :param stack_name: Name to deploy the stack with. Default: - Derived from construct path.
        :param suppress_template_indentation: Enable this flag to suppress indentation in generated CloudFormation templates. If not specified, the value of the ``@aws-cdk/core:suppressTemplateIndentation`` context key will be used. If that is not specified, then the default value ``false`` will be used. Default: - the value of ``@aws-cdk/core:suppressTemplateIndentation``, or ``false`` if that is not set.
        :param synthesizer: Synthesis method to use while deploying this stack. The Stack Synthesizer controls aspects of synthesis and deployment, like how assets are referenced and what IAM roles to use. For more information, see the README of the main CDK package. If not specified, the ``defaultStackSynthesizer`` from ``App`` will be used. If that is not specified, ``DefaultStackSynthesizer`` is used if ``@aws-cdk/core:newStyleStackSynthesis`` is set to ``true`` or the CDK major version is v2. In CDK v1 ``LegacyStackSynthesizer`` is the default if no other synthesizer is specified. Default: - The synthesizer specified on ``App``, or ``DefaultStackSynthesizer`` otherwise.
        :param tags: Stack tags that will be applied to all the taggable resources and the stack itself. Default: {}
        :param termination_protection: Whether to enable termination protection for this stack. Default: false
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8164c597bc966401bc0fe92404de52ab14230c9c79587bc72ada8435efbedffa)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = PostDeployExecutorStackProps(
            name=name,
            res_account=res_account,
            stage_name=stage_name,
            inline_policies=inline_policies,
            prefix=prefix,
            analytics_reporting=analytics_reporting,
            cross_region_references=cross_region_references,
            description=description,
            env=env,
            notification_arns=notification_arns,
            permissions_boundary=permissions_boundary,
            stack_name=stack_name,
            suppress_template_indentation=suppress_template_indentation,
            synthesizer=synthesizer,
            tags=tags,
            termination_protection=termination_protection,
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @jsii.python.classproperty
    @jsii.member(jsii_name="POST_DEPLOY_ROLE_ARN")
    def POST_DEPLOY_ROLE_ARN(cls) -> builtins.str:
        return typing.cast(builtins.str, jsii.sget(cls, "POST_DEPLOY_ROLE_ARN"))

    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        '''The name of the application.'''
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @builtins.property
    @jsii.member(jsii_name="prefix")
    def prefix(self) -> builtins.str:
        '''The prefix to use for resource names.'''
        return typing.cast(builtins.str, jsii.get(self, "prefix"))

    @builtins.property
    @jsii.member(jsii_name="resAccount")
    def res_account(self) -> builtins.str:
        '''The AWS account ID where the resources will be deployed.'''
        return typing.cast(builtins.str, jsii.get(self, "resAccount"))

    @builtins.property
    @jsii.member(jsii_name="role")
    def role(self) -> _aws_cdk_aws_iam_ceddda9d.Role:
        '''The IAM role used for Post Deploy command executions.'''
        return typing.cast(_aws_cdk_aws_iam_ceddda9d.Role, jsii.get(self, "role"))

    @builtins.property
    @jsii.member(jsii_name="roleArn")
    def role_arn(self) -> builtins.str:
        '''The ARN of the created IAM role.'''
        return typing.cast(builtins.str, jsii.get(self, "roleArn"))

    @builtins.property
    @jsii.member(jsii_name="roleName")
    def role_name(self) -> builtins.str:
        '''The name of the created IAM role.'''
        return typing.cast(builtins.str, jsii.get(self, "roleName"))

    @builtins.property
    @jsii.member(jsii_name="stageName")
    def stage_name(self) -> builtins.str:
        '''The name of the deployment stage (e.g., 'prod', 'test').'''
        return typing.cast(builtins.str, jsii.get(self, "stageName"))


@jsii.data_type(
    jsii_type="@cdklabs/cdk-cicd-wrapper.PostDeployExecutorStackProps",
    jsii_struct_bases=[_aws_cdk_ceddda9d.StackProps],
    name_mapping={
        "analytics_reporting": "analyticsReporting",
        "cross_region_references": "crossRegionReferences",
        "description": "description",
        "env": "env",
        "notification_arns": "notificationArns",
        "permissions_boundary": "permissionsBoundary",
        "stack_name": "stackName",
        "suppress_template_indentation": "suppressTemplateIndentation",
        "synthesizer": "synthesizer",
        "tags": "tags",
        "termination_protection": "terminationProtection",
        "name": "name",
        "res_account": "resAccount",
        "stage_name": "stageName",
        "inline_policies": "inlinePolicies",
        "prefix": "prefix",
    },
)
class PostDeployExecutorStackProps(_aws_cdk_ceddda9d.StackProps):
    def __init__(
        self,
        *,
        analytics_reporting: typing.Optional[builtins.bool] = None,
        cross_region_references: typing.Optional[builtins.bool] = None,
        description: typing.Optional[builtins.str] = None,
        env: typing.Optional[typing.Union[_aws_cdk_ceddda9d.Environment, typing.Dict[builtins.str, typing.Any]]] = None,
        notification_arns: typing.Optional[typing.Sequence[builtins.str]] = None,
        permissions_boundary: typing.Optional[_aws_cdk_ceddda9d.PermissionsBoundary] = None,
        stack_name: typing.Optional[builtins.str] = None,
        suppress_template_indentation: typing.Optional[builtins.bool] = None,
        synthesizer: typing.Optional[_aws_cdk_ceddda9d.IStackSynthesizer] = None,
        tags: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        termination_protection: typing.Optional[builtins.bool] = None,
        name: builtins.str,
        res_account: builtins.str,
        stage_name: builtins.str,
        inline_policies: typing.Optional[typing.Mapping[builtins.str, _aws_cdk_aws_iam_ceddda9d.PolicyDocument]] = None,
        prefix: typing.Optional[builtins.str] = None,
    ) -> None:
        '''Properties for the PostDeployExecutorStack.

        :param analytics_reporting: Include runtime versioning information in this Stack. Default: ``analyticsReporting`` setting of containing ``App``, or value of 'aws:cdk:version-reporting' context key
        :param cross_region_references: Enable this flag to allow native cross region stack references. Enabling this will create a CloudFormation custom resource in both the producing stack and consuming stack in order to perform the export/import This feature is currently experimental Default: false
        :param description: A description of the stack. Default: - No description.
        :param env: The AWS environment (account/region) where this stack will be deployed. Set the ``region``/``account`` fields of ``env`` to either a concrete value to select the indicated environment (recommended for production stacks), or to the values of environment variables ``CDK_DEFAULT_REGION``/``CDK_DEFAULT_ACCOUNT`` to let the target environment depend on the AWS credentials/configuration that the CDK CLI is executed under (recommended for development stacks). If the ``Stack`` is instantiated inside a ``Stage``, any undefined ``region``/``account`` fields from ``env`` will default to the same field on the encompassing ``Stage``, if configured there. If either ``region`` or ``account`` are not set nor inherited from ``Stage``, the Stack will be considered "*environment-agnostic*"". Environment-agnostic stacks can be deployed to any environment but may not be able to take advantage of all features of the CDK. For example, they will not be able to use environmental context lookups such as ``ec2.Vpc.fromLookup`` and will not automatically translate Service Principals to the right format based on the environment's AWS partition, and other such enhancements. Default: - The environment of the containing ``Stage`` if available, otherwise create the stack will be environment-agnostic.
        :param notification_arns: SNS Topic ARNs that will receive stack events. Default: - no notfication arns.
        :param permissions_boundary: Options for applying a permissions boundary to all IAM Roles and Users created within this Stage. Default: - no permissions boundary is applied
        :param stack_name: Name to deploy the stack with. Default: - Derived from construct path.
        :param suppress_template_indentation: Enable this flag to suppress indentation in generated CloudFormation templates. If not specified, the value of the ``@aws-cdk/core:suppressTemplateIndentation`` context key will be used. If that is not specified, then the default value ``false`` will be used. Default: - the value of ``@aws-cdk/core:suppressTemplateIndentation``, or ``false`` if that is not set.
        :param synthesizer: Synthesis method to use while deploying this stack. The Stack Synthesizer controls aspects of synthesis and deployment, like how assets are referenced and what IAM roles to use. For more information, see the README of the main CDK package. If not specified, the ``defaultStackSynthesizer`` from ``App`` will be used. If that is not specified, ``DefaultStackSynthesizer`` is used if ``@aws-cdk/core:newStyleStackSynthesis`` is set to ``true`` or the CDK major version is v2. In CDK v1 ``LegacyStackSynthesizer`` is the default if no other synthesizer is specified. Default: - The synthesizer specified on ``App``, or ``DefaultStackSynthesizer`` otherwise.
        :param tags: Stack tags that will be applied to all the taggable resources and the stack itself. Default: {}
        :param termination_protection: Whether to enable termination protection for this stack. Default: false
        :param name: The name of the application.
        :param res_account: The AWS account ID where the resources will be deployed.
        :param stage_name: The name of the deployment stage (e.g., 'prod', 'test').
        :param inline_policies: A list of named policies to inline into this role. These policies will be created with the role, whereas those added by ``addToPolicy`` are added using a separate CloudFormation resource (allowing a way around circular dependencies that could otherwise be introduced). Default: - No policy is inlined in the Role resource.
        :param prefix: The prefix to use for resource names.
        '''
        if isinstance(env, dict):
            env = _aws_cdk_ceddda9d.Environment(**env)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f6647e09f88c64f99ee4bdc5407591bb186063dc43d2565eb8ce7bbf8b863356)
            check_type(argname="argument analytics_reporting", value=analytics_reporting, expected_type=type_hints["analytics_reporting"])
            check_type(argname="argument cross_region_references", value=cross_region_references, expected_type=type_hints["cross_region_references"])
            check_type(argname="argument description", value=description, expected_type=type_hints["description"])
            check_type(argname="argument env", value=env, expected_type=type_hints["env"])
            check_type(argname="argument notification_arns", value=notification_arns, expected_type=type_hints["notification_arns"])
            check_type(argname="argument permissions_boundary", value=permissions_boundary, expected_type=type_hints["permissions_boundary"])
            check_type(argname="argument stack_name", value=stack_name, expected_type=type_hints["stack_name"])
            check_type(argname="argument suppress_template_indentation", value=suppress_template_indentation, expected_type=type_hints["suppress_template_indentation"])
            check_type(argname="argument synthesizer", value=synthesizer, expected_type=type_hints["synthesizer"])
            check_type(argname="argument tags", value=tags, expected_type=type_hints["tags"])
            check_type(argname="argument termination_protection", value=termination_protection, expected_type=type_hints["termination_protection"])
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
            check_type(argname="argument res_account", value=res_account, expected_type=type_hints["res_account"])
            check_type(argname="argument stage_name", value=stage_name, expected_type=type_hints["stage_name"])
            check_type(argname="argument inline_policies", value=inline_policies, expected_type=type_hints["inline_policies"])
            check_type(argname="argument prefix", value=prefix, expected_type=type_hints["prefix"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "name": name,
            "res_account": res_account,
            "stage_name": stage_name,
        }
        if analytics_reporting is not None:
            self._values["analytics_reporting"] = analytics_reporting
        if cross_region_references is not None:
            self._values["cross_region_references"] = cross_region_references
        if description is not None:
            self._values["description"] = description
        if env is not None:
            self._values["env"] = env
        if notification_arns is not None:
            self._values["notification_arns"] = notification_arns
        if permissions_boundary is not None:
            self._values["permissions_boundary"] = permissions_boundary
        if stack_name is not None:
            self._values["stack_name"] = stack_name
        if suppress_template_indentation is not None:
            self._values["suppress_template_indentation"] = suppress_template_indentation
        if synthesizer is not None:
            self._values["synthesizer"] = synthesizer
        if tags is not None:
            self._values["tags"] = tags
        if termination_protection is not None:
            self._values["termination_protection"] = termination_protection
        if inline_policies is not None:
            self._values["inline_policies"] = inline_policies
        if prefix is not None:
            self._values["prefix"] = prefix

    @builtins.property
    def analytics_reporting(self) -> typing.Optional[builtins.bool]:
        '''Include runtime versioning information in this Stack.

        :default:

        ``analyticsReporting`` setting of containing ``App``, or value of
        'aws:cdk:version-reporting' context key
        '''
        result = self._values.get("analytics_reporting")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def cross_region_references(self) -> typing.Optional[builtins.bool]:
        '''Enable this flag to allow native cross region stack references.

        Enabling this will create a CloudFormation custom resource
        in both the producing stack and consuming stack in order to perform the export/import

        This feature is currently experimental

        :default: false
        '''
        result = self._values.get("cross_region_references")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def description(self) -> typing.Optional[builtins.str]:
        '''A description of the stack.

        :default: - No description.
        '''
        result = self._values.get("description")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def env(self) -> typing.Optional[_aws_cdk_ceddda9d.Environment]:
        '''The AWS environment (account/region) where this stack will be deployed.

        Set the ``region``/``account`` fields of ``env`` to either a concrete value to
        select the indicated environment (recommended for production stacks), or to
        the values of environment variables
        ``CDK_DEFAULT_REGION``/``CDK_DEFAULT_ACCOUNT`` to let the target environment
        depend on the AWS credentials/configuration that the CDK CLI is executed
        under (recommended for development stacks).

        If the ``Stack`` is instantiated inside a ``Stage``, any undefined
        ``region``/``account`` fields from ``env`` will default to the same field on the
        encompassing ``Stage``, if configured there.

        If either ``region`` or ``account`` are not set nor inherited from ``Stage``, the
        Stack will be considered "*environment-agnostic*"". Environment-agnostic
        stacks can be deployed to any environment but may not be able to take
        advantage of all features of the CDK. For example, they will not be able to
        use environmental context lookups such as ``ec2.Vpc.fromLookup`` and will not
        automatically translate Service Principals to the right format based on the
        environment's AWS partition, and other such enhancements.

        :default:

        - The environment of the containing ``Stage`` if available,
        otherwise create the stack will be environment-agnostic.

        Example::

            // Use a concrete account and region to deploy this stack to:
            // `.account` and `.region` will simply return these values.
            new Stack(app, 'Stack1', {
              env: {
                account: '123456789012',
                region: 'us-east-1'
              },
            });
            
            // Use the CLI's current credentials to determine the target environment:
            // `.account` and `.region` will reflect the account+region the CLI
            // is configured to use (based on the user CLI credentials)
            new Stack(app, 'Stack2', {
              env: {
                account: process.env.CDK_DEFAULT_ACCOUNT,
                region: process.env.CDK_DEFAULT_REGION
              },
            });
            
            // Define multiple stacks stage associated with an environment
            const myStage = new Stage(app, 'MyStage', {
              env: {
                account: '123456789012',
                region: 'us-east-1'
              }
            });
            
            // both of these stacks will use the stage's account/region:
            // `.account` and `.region` will resolve to the concrete values as above
            new MyStack(myStage, 'Stack1');
            new YourStack(myStage, 'Stack2');
            
            // Define an environment-agnostic stack:
            // `.account` and `.region` will resolve to `{ "Ref": "AWS::AccountId" }` and `{ "Ref": "AWS::Region" }` respectively.
            // which will only resolve to actual values by CloudFormation during deployment.
            new MyStack(app, 'Stack1');
        '''
        result = self._values.get("env")
        return typing.cast(typing.Optional[_aws_cdk_ceddda9d.Environment], result)

    @builtins.property
    def notification_arns(self) -> typing.Optional[typing.List[builtins.str]]:
        '''SNS Topic ARNs that will receive stack events.

        :default: - no notfication arns.
        '''
        result = self._values.get("notification_arns")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def permissions_boundary(
        self,
    ) -> typing.Optional[_aws_cdk_ceddda9d.PermissionsBoundary]:
        '''Options for applying a permissions boundary to all IAM Roles and Users created within this Stage.

        :default: - no permissions boundary is applied
        '''
        result = self._values.get("permissions_boundary")
        return typing.cast(typing.Optional[_aws_cdk_ceddda9d.PermissionsBoundary], result)

    @builtins.property
    def stack_name(self) -> typing.Optional[builtins.str]:
        '''Name to deploy the stack with.

        :default: - Derived from construct path.
        '''
        result = self._values.get("stack_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def suppress_template_indentation(self) -> typing.Optional[builtins.bool]:
        '''Enable this flag to suppress indentation in generated CloudFormation templates.

        If not specified, the value of the ``@aws-cdk/core:suppressTemplateIndentation``
        context key will be used. If that is not specified, then the
        default value ``false`` will be used.

        :default: - the value of ``@aws-cdk/core:suppressTemplateIndentation``, or ``false`` if that is not set.
        '''
        result = self._values.get("suppress_template_indentation")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def synthesizer(self) -> typing.Optional[_aws_cdk_ceddda9d.IStackSynthesizer]:
        '''Synthesis method to use while deploying this stack.

        The Stack Synthesizer controls aspects of synthesis and deployment,
        like how assets are referenced and what IAM roles to use. For more
        information, see the README of the main CDK package.

        If not specified, the ``defaultStackSynthesizer`` from ``App`` will be used.
        If that is not specified, ``DefaultStackSynthesizer`` is used if
        ``@aws-cdk/core:newStyleStackSynthesis`` is set to ``true`` or the CDK major
        version is v2. In CDK v1 ``LegacyStackSynthesizer`` is the default if no
        other synthesizer is specified.

        :default: - The synthesizer specified on ``App``, or ``DefaultStackSynthesizer`` otherwise.
        '''
        result = self._values.get("synthesizer")
        return typing.cast(typing.Optional[_aws_cdk_ceddda9d.IStackSynthesizer], result)

    @builtins.property
    def tags(self) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        '''Stack tags that will be applied to all the taggable resources and the stack itself.

        :default: {}
        '''
        result = self._values.get("tags")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], result)

    @builtins.property
    def termination_protection(self) -> typing.Optional[builtins.bool]:
        '''Whether to enable termination protection for this stack.

        :default: false
        '''
        result = self._values.get("termination_protection")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def name(self) -> builtins.str:
        '''The name of the application.'''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def res_account(self) -> builtins.str:
        '''The AWS account ID where the resources will be deployed.'''
        result = self._values.get("res_account")
        assert result is not None, "Required property 'res_account' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def stage_name(self) -> builtins.str:
        '''The name of the deployment stage (e.g., 'prod', 'test').'''
        result = self._values.get("stage_name")
        assert result is not None, "Required property 'stage_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def inline_policies(
        self,
    ) -> typing.Optional[typing.Mapping[builtins.str, _aws_cdk_aws_iam_ceddda9d.PolicyDocument]]:
        '''A list of named policies to inline into this role.

        These policies will be
        created with the role, whereas those added by ``addToPolicy`` are added
        using a separate CloudFormation resource (allowing a way around circular
        dependencies that could otherwise be introduced).

        :default: - No policy is inlined in the Role resource.
        '''
        result = self._values.get("inline_policies")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, _aws_cdk_aws_iam_ceddda9d.PolicyDocument]], result)

    @builtins.property
    def prefix(self) -> typing.Optional[builtins.str]:
        '''The prefix to use for resource names.'''
        result = self._values.get("prefix")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "PostDeployExecutorStackProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class PreDeployBuildStep(
    _aws_cdk_pipelines_ceddda9d.CodeBuildStep,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdklabs/cdk-cicd-wrapper.PreDeployBuildStep",
):
    '''A class that extends the CodeBuildStep class from the aws-cdk-lib/pipelines module.

    This class is used to create a pre-deployment build step for a specific stage in a pipeline.
    '''

    def __init__(
        self,
        stage: builtins.str,
        *,
        action_role: typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole] = None,
        build_environment: typing.Optional[typing.Union[_aws_cdk_aws_codebuild_ceddda9d.BuildEnvironment, typing.Dict[builtins.str, typing.Any]]] = None,
        cache: typing.Optional[_aws_cdk_aws_codebuild_ceddda9d.Cache] = None,
        file_system_locations: typing.Optional[typing.Sequence[_aws_cdk_aws_codebuild_ceddda9d.IFileSystemLocation]] = None,
        logging: typing.Optional[typing.Union[_aws_cdk_aws_codebuild_ceddda9d.LoggingOptions, typing.Dict[builtins.str, typing.Any]]] = None,
        partial_build_spec: typing.Optional[_aws_cdk_aws_codebuild_ceddda9d.BuildSpec] = None,
        project_name: typing.Optional[builtins.str] = None,
        role: typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole] = None,
        role_policy_statements: typing.Optional[typing.Sequence[_aws_cdk_aws_iam_ceddda9d.PolicyStatement]] = None,
        security_groups: typing.Optional[typing.Sequence[_aws_cdk_aws_ec2_ceddda9d.ISecurityGroup]] = None,
        subnet_selection: typing.Optional[typing.Union[_aws_cdk_aws_ec2_ceddda9d.SubnetSelection, typing.Dict[builtins.str, typing.Any]]] = None,
        timeout: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
        vpc: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.IVpc] = None,
        commands: typing.Sequence[builtins.str],
        additional_inputs: typing.Optional[typing.Mapping[builtins.str, _aws_cdk_pipelines_ceddda9d.IFileSetProducer]] = None,
        env: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        env_from_cfn_outputs: typing.Optional[typing.Mapping[builtins.str, _aws_cdk_ceddda9d.CfnOutput]] = None,
        input: typing.Optional[_aws_cdk_pipelines_ceddda9d.IFileSetProducer] = None,
        install_commands: typing.Optional[typing.Sequence[builtins.str]] = None,
        primary_output_directory: typing.Optional[builtins.str] = None,
    ) -> None:
        '''Creates a new instance of the PreDeployBuildStep class.

        :param stage: - The stage for which the pre-deployment build step is being created.
        :param action_role: Custom execution role to be used for the Code Build Action. Default: - A role is automatically created
        :param build_environment: Changes to environment. This environment will be combined with the pipeline's default environment. Default: - Use the pipeline's default build environment
        :param cache: Caching strategy to use. Default: - No cache
        :param file_system_locations: ProjectFileSystemLocation objects for CodeBuild build projects. A ProjectFileSystemLocation object specifies the identifier, location, mountOptions, mountPoint, and type of a file system created using Amazon Elastic File System. Default: - no file system locations
        :param logging: Information about logs for CodeBuild projects. A CodeBuild project can create logs in Amazon CloudWatch Logs, an S3 bucket, or both. Default: - no log configuration is set
        :param partial_build_spec: Additional configuration that can only be configured via BuildSpec. You should not use this to specify output artifacts; those should be supplied via the other properties of this class, otherwise CDK Pipelines won't be able to inspect the artifacts. Set the ``commands`` to an empty array if you want to fully specify the BuildSpec using this field. The BuildSpec must be available inline--it cannot reference a file on disk. Default: - BuildSpec completely derived from other properties
        :param project_name: Name for the generated CodeBuild project. Default: - Automatically generated
        :param role: Custom execution role to be used for the CodeBuild project. Default: - A role is automatically created
        :param role_policy_statements: Policy statements to add to role used during the synth. Can be used to add acces to a CodeArtifact repository etc. Default: - No policy statements added to CodeBuild Project Role
        :param security_groups: Which security group to associate with the script's project network interfaces. If no security group is identified, one will be created automatically. Only used if 'vpc' is supplied. Default: - Security group will be automatically created.
        :param subnet_selection: Which subnets to use. Only used if 'vpc' is supplied. Default: - All private subnets.
        :param timeout: The number of minutes after which AWS CodeBuild stops the build if it's not complete. For valid values, see the timeoutInMinutes field in the AWS CodeBuild User Guide. Default: Duration.hours(1)
        :param vpc: The VPC where to execute the SimpleSynth. Default: - No VPC
        :param commands: Commands to run.
        :param additional_inputs: Additional FileSets to put in other directories. Specifies a mapping from directory name to FileSets. During the script execution, the FileSets will be available in the directories indicated. The directory names may be relative. For example, you can put the main input and an additional input side-by-side with the following configuration:: const script = new pipelines.ShellStep('MainScript', { commands: ['npm ci','npm run build','npx cdk synth'], input: pipelines.CodePipelineSource.gitHub('org/source1', 'main'), additionalInputs: { '../siblingdir': pipelines.CodePipelineSource.gitHub('org/source2', 'main'), } }); Default: - No additional inputs
        :param env: Environment variables to set. Default: - No environment variables
        :param env_from_cfn_outputs: Set environment variables based on Stack Outputs. ``ShellStep``s following stack or stage deployments may access the ``CfnOutput``s of those stacks to get access to --for example--automatically generated resource names or endpoint URLs. Default: - No environment variables created from stack outputs
        :param input: FileSet to run these scripts on. The files in the FileSet will be placed in the working directory when the script is executed. Use ``additionalInputs`` to download file sets to other directories as well. Default: - No input specified
        :param install_commands: Installation commands to run before the regular commands. For deployment engines that support it, install commands will be classified differently in the job history from the regular ``commands``. Default: - No installation commands
        :param primary_output_directory: The directory that will contain the primary output fileset. After running the script, the contents of the given directory will be treated as the primary output of this Step. Default: - No primary output
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__cb31b97373db95cd416ca376c1e5eba687bcf3ab942d2569c57bcd982d7f8fd2)
            check_type(argname="argument stage", value=stage, expected_type=type_hints["stage"])
        props = _aws_cdk_pipelines_ceddda9d.CodeBuildStepProps(
            action_role=action_role,
            build_environment=build_environment,
            cache=cache,
            file_system_locations=file_system_locations,
            logging=logging,
            partial_build_spec=partial_build_spec,
            project_name=project_name,
            role=role,
            role_policy_statements=role_policy_statements,
            security_groups=security_groups,
            subnet_selection=subnet_selection,
            timeout=timeout,
            vpc=vpc,
            commands=commands,
            additional_inputs=additional_inputs,
            env=env,
            env_from_cfn_outputs=env_from_cfn_outputs,
            input=input,
            install_commands=install_commands,
            primary_output_directory=primary_output_directory,
        )

        jsii.create(self.__class__, self, [stage, props])


@jsii.data_type(
    jsii_type="@cdklabs/cdk-cicd-wrapper.ProxyProps",
    jsii_struct_bases=[],
    name_mapping={
        "no_proxy": "noProxy",
        "proxy_secret_arn": "proxySecretArn",
        "proxy_test_url": "proxyTestUrl",
    },
)
class ProxyProps:
    def __init__(
        self,
        *,
        no_proxy: typing.Sequence[builtins.str],
        proxy_secret_arn: builtins.str,
        proxy_test_url: builtins.str,
    ) -> None:
        '''Props for configuring a proxy.

        :param no_proxy: A list of URLs or IP addresses that should bypass the proxy.
        :param proxy_secret_arn: The ARN of the secret containing the proxy credentials.
        :param proxy_test_url: A URL to test the proxy configuration.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__089ff8ed46011c56913f9c41f507ec457aa745cdbd0b3a78ce5f0d0ffcf63620)
            check_type(argname="argument no_proxy", value=no_proxy, expected_type=type_hints["no_proxy"])
            check_type(argname="argument proxy_secret_arn", value=proxy_secret_arn, expected_type=type_hints["proxy_secret_arn"])
            check_type(argname="argument proxy_test_url", value=proxy_test_url, expected_type=type_hints["proxy_test_url"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "no_proxy": no_proxy,
            "proxy_secret_arn": proxy_secret_arn,
            "proxy_test_url": proxy_test_url,
        }

    @builtins.property
    def no_proxy(self) -> typing.List[builtins.str]:
        '''A list of URLs or IP addresses that should bypass the proxy.'''
        result = self._values.get("no_proxy")
        assert result is not None, "Required property 'no_proxy' is missing"
        return typing.cast(typing.List[builtins.str], result)

    @builtins.property
    def proxy_secret_arn(self) -> builtins.str:
        '''The ARN of the secret containing the proxy credentials.'''
        result = self._values.get("proxy_secret_arn")
        assert result is not None, "Required property 'proxy_secret_arn' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def proxy_test_url(self) -> builtins.str:
        '''A URL to test the proxy configuration.'''
        result = self._values.get("proxy_test_url")
        assert result is not None, "Required property 'proxy_test_url' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ProxyProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.implements(IPhaseCommand)
class PythonPhaseCommand(
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdklabs/cdk-cicd-wrapper.PythonPhaseCommand",
):
    '''Phase Command that invokes Python scripts from project folder.'''

    def __init__(self, script: builtins.str) -> None:
        '''
        :param script: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7d8f35a66618d2e7c7f39cff05c118af6defe9c791ae585ca95d4ab2db26e8f5)
            check_type(argname="argument script", value=script, expected_type=type_hints["script"])
        jsii.create(self.__class__, self, [script])

    @builtins.property
    @jsii.member(jsii_name="command")
    def command(self) -> builtins.str:
        '''Returns the command to be executed for the given Python script.'''
        return typing.cast(builtins.str, jsii.get(self, "command"))

    @builtins.property
    @jsii.member(jsii_name="script")
    def script(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "script"))


@jsii.data_type(
    jsii_type="@cdklabs/cdk-cicd-wrapper.RepositoryConfig",
    jsii_struct_bases=[],
    name_mapping={
        "branch": "branch",
        "name": "name",
        "repository_type": "repositoryType",
        "code_build_clone_output": "codeBuildCloneOutput",
        "description": "description",
    },
)
class RepositoryConfig:
    def __init__(
        self,
        *,
        branch: builtins.str,
        name: builtins.str,
        repository_type: builtins.str,
        code_build_clone_output: typing.Optional[builtins.bool] = None,
        description: typing.Optional[builtins.str] = None,
    ) -> None:
        '''Represents the configuration for a repository.

        :param branch: The branch for the repository.
        :param name: The name of the repository.
        :param repository_type: The type of the repository.
        :param code_build_clone_output: Enforce full clone for the repository.
        :param description: The description of the repository (optional).
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__cd7a11f613d342f1cdb5aecca9a3c81db0760271727f0901a73b8fe466e0463a)
            check_type(argname="argument branch", value=branch, expected_type=type_hints["branch"])
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
            check_type(argname="argument repository_type", value=repository_type, expected_type=type_hints["repository_type"])
            check_type(argname="argument code_build_clone_output", value=code_build_clone_output, expected_type=type_hints["code_build_clone_output"])
            check_type(argname="argument description", value=description, expected_type=type_hints["description"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "branch": branch,
            "name": name,
            "repository_type": repository_type,
        }
        if code_build_clone_output is not None:
            self._values["code_build_clone_output"] = code_build_clone_output
        if description is not None:
            self._values["description"] = description

    @builtins.property
    def branch(self) -> builtins.str:
        '''The branch for the repository.'''
        result = self._values.get("branch")
        assert result is not None, "Required property 'branch' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def name(self) -> builtins.str:
        '''The name of the repository.'''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def repository_type(self) -> builtins.str:
        '''The type of the repository.'''
        result = self._values.get("repository_type")
        assert result is not None, "Required property 'repository_type' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def code_build_clone_output(self) -> typing.Optional[builtins.bool]:
        '''Enforce full clone for the repository.'''
        result = self._values.get("code_build_clone_output")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def description(self) -> typing.Optional[builtins.str]:
        '''The description of the repository (optional).'''
        result = self._values.get("description")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "RepositoryConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class RepositorySource(
    metaclass=jsii.JSIIAbstractClass,
    jsii_type="@cdklabs/cdk-cicd-wrapper.RepositorySource",
):
    '''Represents a repository source.'''

    def __init__(self) -> None:
        jsii.create(self.__class__, self, [])

    @jsii.member(jsii_name="basedType")
    @builtins.classmethod
    def based_type(
        cls,
        type: builtins.str,
        *,
        code_guru_reviewer: typing.Optional[builtins.bool] = None,
        code_star_connection_arn: typing.Optional[builtins.str] = None,
        branch: builtins.str,
        name: builtins.str,
        repository_type: builtins.str,
        code_build_clone_output: typing.Optional[builtins.bool] = None,
        description: typing.Optional[builtins.str] = None,
    ) -> "RepositorySource":
        '''
        :param type: -
        :param code_guru_reviewer: 
        :param code_star_connection_arn: 
        :param branch: The branch for the repository.
        :param name: The name of the repository.
        :param repository_type: The type of the repository.
        :param code_build_clone_output: Enforce full clone for the repository.
        :param description: The description of the repository (optional).
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__21e3be4487767c5d4930911688171dde310cc674a0936577bc4b3cd866aab5e1)
            check_type(argname="argument type", value=type, expected_type=type_hints["type"])
        config = BaseRepositoryProviderProps(
            code_guru_reviewer=code_guru_reviewer,
            code_star_connection_arn=code_star_connection_arn,
            branch=branch,
            name=name,
            repository_type=repository_type,
            code_build_clone_output=code_build_clone_output,
            description=description,
        )

        return typing.cast("RepositorySource", jsii.sinvoke(cls, "basedType", [type, config]))

    @jsii.member(jsii_name="codecommit")
    @builtins.classmethod
    def codecommit(
        cls,
        *,
        enable_code_guru_reviewer: typing.Optional[builtins.bool] = None,
        enable_pull_request_checks: typing.Optional[builtins.bool] = None,
        branch: typing.Optional[builtins.str] = None,
        code_build_clone_output: typing.Optional[builtins.bool] = None,
        description: typing.Optional[builtins.str] = None,
        repository_name: typing.Optional[builtins.str] = None,
    ) -> "RepositorySource":
        '''Creates a new CodeCommit repository source.

        :param enable_code_guru_reviewer: Enable CodeGuru Reviewer. Default: - false
        :param enable_pull_request_checks: Enable pull request checks. Default: - true
        :param branch: The branch of the repository. Default: - 'main'
        :param code_build_clone_output: Enforce full clone for the repository. Tools like semgrep and pre-commit hooks require a full clone. Default: - false
        :param description: The description of the repository. Default: - No description.
        :param repository_name: The name of the repository. Default: - The name of the application. other options to configure: in package.json file "config": { "repositoryName": "my-repo", }
        '''
        options = CodeCommitRepositorySourceOptions(
            enable_code_guru_reviewer=enable_code_guru_reviewer,
            enable_pull_request_checks=enable_pull_request_checks,
            branch=branch,
            code_build_clone_output=code_build_clone_output,
            description=description,
            repository_name=repository_name,
        )

        return typing.cast("RepositorySource", jsii.sinvoke(cls, "codecommit", [options]))

    @jsii.member(jsii_name="codestarConnection")
    @builtins.classmethod
    def codestar_connection(
        cls,
        *,
        code_star_connection_arn: typing.Optional[builtins.str] = None,
        branch: typing.Optional[builtins.str] = None,
        code_build_clone_output: typing.Optional[builtins.bool] = None,
        description: typing.Optional[builtins.str] = None,
        repository_name: typing.Optional[builtins.str] = None,
    ) -> "RepositorySource":
        '''Creates a new CodeStar connection repository source.

        :param code_star_connection_arn: The ARN of the CodeStar connection. Default: - The value of the CODESTAR_CONNECTION_ARN environment variable.
        :param branch: The branch of the repository. Default: - 'main'
        :param code_build_clone_output: Enforce full clone for the repository. Tools like semgrep and pre-commit hooks require a full clone. Default: - false
        :param description: The description of the repository. Default: - No description.
        :param repository_name: The name of the repository. Default: - The name of the application. other options to configure: in package.json file "config": { "repositoryName": "my-repo", }
        '''
        options = CodeStarConnectionRepositorySourceOptions(
            code_star_connection_arn=code_star_connection_arn,
            branch=branch,
            code_build_clone_output=code_build_clone_output,
            description=description,
            repository_name=repository_name,
        )

        return typing.cast("RepositorySource", jsii.sinvoke(cls, "codestarConnection", [options]))

    @jsii.member(jsii_name="github")
    @builtins.classmethod
    def github(
        cls,
        *,
        code_star_connection_arn: typing.Optional[builtins.str] = None,
        branch: typing.Optional[builtins.str] = None,
        code_build_clone_output: typing.Optional[builtins.bool] = None,
        description: typing.Optional[builtins.str] = None,
        repository_name: typing.Optional[builtins.str] = None,
    ) -> "RepositorySource":
        '''Creates a new Github - CodeStar connection repository source.

        :param code_star_connection_arn: The ARN of the CodeStar connection. Default: - The value of the CODESTAR_CONNECTION_ARN environment variable.
        :param branch: The branch of the repository. Default: - 'main'
        :param code_build_clone_output: Enforce full clone for the repository. Tools like semgrep and pre-commit hooks require a full clone. Default: - false
        :param description: The description of the repository. Default: - No description.
        :param repository_name: The name of the repository. Default: - The name of the application. other options to configure: in package.json file "config": { "repositoryName": "my-repo", }
        '''
        options = CodeStarConnectionRepositorySourceOptions(
            code_star_connection_arn=code_star_connection_arn,
            branch=branch,
            code_build_clone_output=code_build_clone_output,
            description=description,
            repository_name=repository_name,
        )

        return typing.cast("RepositorySource", jsii.sinvoke(cls, "github", [options]))

    @jsii.member(jsii_name="s3")
    @builtins.classmethod
    def s3(
        cls,
        *,
        bucket_name: typing.Optional[builtins.str] = None,
        prefix: typing.Optional[builtins.str] = None,
        removal_policy: typing.Optional[_aws_cdk_ceddda9d.RemovalPolicy] = None,
        roles: typing.Optional[typing.Sequence[builtins.str]] = None,
        branch: typing.Optional[builtins.str] = None,
        code_build_clone_output: typing.Optional[builtins.bool] = None,
        description: typing.Optional[builtins.str] = None,
        repository_name: typing.Optional[builtins.str] = None,
    ) -> "RepositorySource":
        '''Creates a new S3 repository source.

        :param bucket_name: The name of the S3 bucket where the repository is stored. Default: - A bucket name is generated based on the application name, account, and region.
        :param prefix: An optional prefix to use within the S3 bucket. This can be used to specify a subdirectory within the bucket. Default: - No prefix is used.
        :param removal_policy: The removal policy for the S3 bucket.
        :param roles: An optional list of IAM roles that are allowed to access the repository.
        :param branch: The branch of the repository. Default: - 'main'
        :param code_build_clone_output: Enforce full clone for the repository. Tools like semgrep and pre-commit hooks require a full clone. Default: - false
        :param description: The description of the repository. Default: - No description.
        :param repository_name: The name of the repository. Default: - The name of the application. other options to configure: in package.json file "config": { "repositoryName": "my-repo", }
        '''
        options = S3RepositorySourceOptions(
            bucket_name=bucket_name,
            prefix=prefix,
            removal_policy=removal_policy,
            roles=roles,
            branch=branch,
            code_build_clone_output=code_build_clone_output,
            description=description,
            repository_name=repository_name,
        )

        return typing.cast("RepositorySource", jsii.sinvoke(cls, "s3", [options]))

    @jsii.member(jsii_name="produceSourceConfig")
    @abc.abstractmethod
    def produce_source_config(self, context: "ResourceContext") -> IRepositoryStack:
        '''
        :param context: -
        '''
        ...


class _RepositorySourceProxy(RepositorySource):
    @jsii.member(jsii_name="produceSourceConfig")
    def produce_source_config(self, context: "ResourceContext") -> IRepositoryStack:
        '''
        :param context: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__cc5eb055e68eeb38bf802b5bc0ba875fa4dc6a10c324f002a1d11c4bc578047b)
            check_type(argname="argument context", value=context, expected_type=type_hints["context"])
        return typing.cast(IRepositoryStack, jsii.invoke(self, "produceSourceConfig", [context]))

# Adding a "__jsii_proxy_class__(): typing.Type" function to the abstract class
typing.cast(typing.Any, RepositorySource).__jsii_proxy_class__ = lambda : _RepositorySourceProxy


@jsii.data_type(
    jsii_type="@cdklabs/cdk-cicd-wrapper.RepositorySourceOptions",
    jsii_struct_bases=[],
    name_mapping={
        "branch": "branch",
        "code_build_clone_output": "codeBuildCloneOutput",
        "description": "description",
        "repository_name": "repositoryName",
    },
)
class RepositorySourceOptions:
    def __init__(
        self,
        *,
        branch: typing.Optional[builtins.str] = None,
        code_build_clone_output: typing.Optional[builtins.bool] = None,
        description: typing.Optional[builtins.str] = None,
        repository_name: typing.Optional[builtins.str] = None,
    ) -> None:
        '''Represents the configuration for a repository source.

        :param branch: The branch of the repository. Default: - 'main'
        :param code_build_clone_output: Enforce full clone for the repository. Tools like semgrep and pre-commit hooks require a full clone. Default: - false
        :param description: The description of the repository. Default: - No description.
        :param repository_name: The name of the repository. Default: - The name of the application. other options to configure: in package.json file "config": { "repositoryName": "my-repo", }
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__05576ebde777c88feb630da30f74fd9172cf956c6ed229ee91767e043baa752a)
            check_type(argname="argument branch", value=branch, expected_type=type_hints["branch"])
            check_type(argname="argument code_build_clone_output", value=code_build_clone_output, expected_type=type_hints["code_build_clone_output"])
            check_type(argname="argument description", value=description, expected_type=type_hints["description"])
            check_type(argname="argument repository_name", value=repository_name, expected_type=type_hints["repository_name"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if branch is not None:
            self._values["branch"] = branch
        if code_build_clone_output is not None:
            self._values["code_build_clone_output"] = code_build_clone_output
        if description is not None:
            self._values["description"] = description
        if repository_name is not None:
            self._values["repository_name"] = repository_name

    @builtins.property
    def branch(self) -> typing.Optional[builtins.str]:
        '''The branch of the repository.

        :default: - 'main'
        '''
        result = self._values.get("branch")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def code_build_clone_output(self) -> typing.Optional[builtins.bool]:
        '''Enforce full clone for the repository.

        Tools like semgrep and pre-commit hooks require a full clone.

        :default: - false
        '''
        result = self._values.get("code_build_clone_output")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def description(self) -> typing.Optional[builtins.str]:
        '''The description of the repository.

        :default: - No description.
        '''
        result = self._values.get("description")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def repository_name(self) -> typing.Optional[builtins.str]:
        '''The name of the repository.

        :default:

        - The name of the application.

        other options to configure:
        in  package.json file

        "config": {
        "repositoryName": "my-repo",
        }
        '''
        result = self._values.get("repository_name")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "RepositorySourceOptions(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ResourceContext(
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdklabs/cdk-cicd-wrapper.ResourceContext",
):
    '''Provides an API to register resource providers and access the provided resources.'''

    def __init__(
        self,
        _scope: _constructs_77d1e7e8.Construct,
        pipeline_stack: _constructs_77d1e7e8.Construct,
        blueprint_props: "IPipelineBlueprintProps",
    ) -> None:
        '''Constructs a new instance of ResourceContext.

        :param _scope: The construct scope.
        :param pipeline_stack: The pipeline stack construct.
        :param blueprint_props: The pipeline blueprint properties.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6f34ce6664c6ad39a0e84b86392061f5c3ae5df3fb5ddb4a0af4669a6d308354)
            check_type(argname="argument _scope", value=_scope, expected_type=type_hints["_scope"])
            check_type(argname="argument pipeline_stack", value=pipeline_stack, expected_type=type_hints["pipeline_stack"])
            check_type(argname="argument blueprint_props", value=blueprint_props, expected_type=type_hints["blueprint_props"])
        jsii.create(self.__class__, self, [_scope, pipeline_stack, blueprint_props])

    @jsii.member(jsii_name="instance")
    @builtins.classmethod
    def instance(cls) -> "ResourceContext":
        '''Returns the singleton instance of ResourceContext.

        :return: The ResourceContext instance.
        '''
        return typing.cast("ResourceContext", jsii.sinvoke(cls, "instance", []))

    @jsii.member(jsii_name="add")
    def add(self, name: builtins.str, value: typing.Any) -> None:
        '''
        :param name: -
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__29aaf3e2aee7b9f9ace4d5a07be6ebd6f4fb0befea6f38ea6c643e820f8cb248)
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "add", [name, value]))

    @jsii.member(jsii_name="get")
    def get(self, name: builtins.str) -> typing.Any:
        '''Retrieves a resource by its name.

        :param name: The name of the resource.

        :return: The resource, or undefined if it doesn't exist.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__fcc5cf5762c3a9ef4fe5d457152ebb9460335dcd72643bf9aadbb56da7fe06cf)
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
        return typing.cast(typing.Any, jsii.invoke(self, "get", [name]))

    @jsii.member(jsii_name="has")
    def has(self, name: builtins.str) -> builtins.bool:
        '''Checks if a resource with the given name exists.

        :param name: The name of the resource.

        :return: True if the resource exists, false otherwise.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__90f8a7950f878afee504f6453182a4b979ba397aef2c71ee1e7deeed98bea3c7)
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
        return typing.cast(builtins.bool, jsii.invoke(self, "has", [name]))

    @jsii.member(jsii_name="initStage")
    def init_stage(self, stage: builtins.str) -> None:
        '''Initializes the current stage and its associated resource providers.

        :param stage: The current stage.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4f5471bc22ce257979e8d93c1416387b27683da69dfcac193d2e0d0443496eda)
            check_type(argname="argument stage", value=stage, expected_type=type_hints["stage"])
        return typing.cast(None, jsii.invoke(self, "initStage", [stage]))

    @builtins.property
    @jsii.member(jsii_name="blueprintProps")
    def blueprint_props(self) -> "IPipelineBlueprintProps":
        '''The pipeline blueprint properties.'''
        return typing.cast("IPipelineBlueprintProps", jsii.get(self, "blueprintProps"))

    @builtins.property
    @jsii.member(jsii_name="environment")
    def environment(self) -> Environment:
        '''Retrieves the current environment.

        :return: The current environment.
        '''
        return typing.cast(Environment, jsii.get(self, "environment"))

    @builtins.property
    @jsii.member(jsii_name="locked")
    def locked(self) -> builtins.bool:
        return typing.cast(builtins.bool, jsii.get(self, "locked"))

    @builtins.property
    @jsii.member(jsii_name="pipelineStack")
    def pipeline_stack(self) -> _constructs_77d1e7e8.Construct:
        '''The pipeline stack construct.'''
        return typing.cast(_constructs_77d1e7e8.Construct, jsii.get(self, "pipelineStack"))

    @builtins.property
    @jsii.member(jsii_name="scope")
    def scope(self) -> _constructs_77d1e7e8.Construct:
        '''Retrieves the current construct scope.

        :return: The current construct scope.
        '''
        return typing.cast(_constructs_77d1e7e8.Construct, jsii.get(self, "scope"))

    @builtins.property
    @jsii.member(jsii_name="stage")
    def stage(self) -> builtins.str:
        '''Retrieves the current stage.

        :return: The current stage.
        '''
        return typing.cast(builtins.str, jsii.get(self, "stage"))


class RotateEncryptionKeysPlugin(
    PluginBase,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdklabs/cdk-cicd-wrapper.RotateEncryptionKeysPlugin",
):
    '''Plugin to enable key rotation for KMS keys.'''

    def __init__(self) -> None:
        jsii.create(self.__class__, self, [])

    @jsii.member(jsii_name="afterStage")
    def after_stage(
        self,
        scope: _constructs_77d1e7e8.Construct,
        _: ResourceContext,
    ) -> None:
        '''The method called after the stage is created.

        :param scope: -
        :param _: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9913f45c0f7fd1459e64a81c3cbf4683133c5a8d2b0f926fc0b4969b16816fcf)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument _", value=_, expected_type=type_hints["_"])
        return typing.cast(None, jsii.invoke(self, "afterStage", [scope, _]))

    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        '''The name of the plugin.'''
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @builtins.property
    @jsii.member(jsii_name="version")
    def version(self) -> builtins.str:
        '''The version of the plugin.'''
        return typing.cast(builtins.str, jsii.get(self, "version"))


@jsii.data_type(
    jsii_type="@cdklabs/cdk-cicd-wrapper.RuntimeVersionOptions",
    jsii_struct_bases=[],
    name_mapping={
        "dotnet": "dotnet",
        "golang": "golang",
        "java": "java",
        "nodejs": "nodejs",
        "php": "php",
        "python": "python",
        "ruby": "ruby",
    },
)
class RuntimeVersionOptions:
    def __init__(
        self,
        *,
        dotnet: typing.Optional[builtins.str] = None,
        golang: typing.Optional[builtins.str] = None,
        java: typing.Optional[builtins.str] = None,
        nodejs: typing.Optional[builtins.str] = None,
        php: typing.Optional[builtins.str] = None,
        python: typing.Optional[builtins.str] = None,
        ruby: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param dotnet: 
        :param golang: 
        :param java: 
        :param nodejs: 
        :param php: 
        :param python: 
        :param ruby: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__20c4903b48e4b9702ed6f32f3af88151150aaa993ab2015f582d1238209c6bd9)
            check_type(argname="argument dotnet", value=dotnet, expected_type=type_hints["dotnet"])
            check_type(argname="argument golang", value=golang, expected_type=type_hints["golang"])
            check_type(argname="argument java", value=java, expected_type=type_hints["java"])
            check_type(argname="argument nodejs", value=nodejs, expected_type=type_hints["nodejs"])
            check_type(argname="argument php", value=php, expected_type=type_hints["php"])
            check_type(argname="argument python", value=python, expected_type=type_hints["python"])
            check_type(argname="argument ruby", value=ruby, expected_type=type_hints["ruby"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if dotnet is not None:
            self._values["dotnet"] = dotnet
        if golang is not None:
            self._values["golang"] = golang
        if java is not None:
            self._values["java"] = java
        if nodejs is not None:
            self._values["nodejs"] = nodejs
        if php is not None:
            self._values["php"] = php
        if python is not None:
            self._values["python"] = python
        if ruby is not None:
            self._values["ruby"] = ruby

    @builtins.property
    def dotnet(self) -> typing.Optional[builtins.str]:
        result = self._values.get("dotnet")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def golang(self) -> typing.Optional[builtins.str]:
        result = self._values.get("golang")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def java(self) -> typing.Optional[builtins.str]:
        result = self._values.get("java")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def nodejs(self) -> typing.Optional[builtins.str]:
        result = self._values.get("nodejs")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def php(self) -> typing.Optional[builtins.str]:
        result = self._values.get("php")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def python(self) -> typing.Optional[builtins.str]:
        result = self._values.get("python")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def ruby(self) -> typing.Optional[builtins.str]:
        result = self._values.get("ruby")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "RuntimeVersionOptions(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class S3RepositorySource(
    RepositorySource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdklabs/cdk-cicd-wrapper.S3RepositorySource",
):
    def __init__(
        self,
        *,
        bucket_name: typing.Optional[builtins.str] = None,
        prefix: typing.Optional[builtins.str] = None,
        removal_policy: typing.Optional[_aws_cdk_ceddda9d.RemovalPolicy] = None,
        roles: typing.Optional[typing.Sequence[builtins.str]] = None,
        branch: typing.Optional[builtins.str] = None,
        code_build_clone_output: typing.Optional[builtins.bool] = None,
        description: typing.Optional[builtins.str] = None,
        repository_name: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param bucket_name: The name of the S3 bucket where the repository is stored. Default: - A bucket name is generated based on the application name, account, and region.
        :param prefix: An optional prefix to use within the S3 bucket. This can be used to specify a subdirectory within the bucket. Default: - No prefix is used.
        :param removal_policy: The removal policy for the S3 bucket.
        :param roles: An optional list of IAM roles that are allowed to access the repository.
        :param branch: The branch of the repository. Default: - 'main'
        :param code_build_clone_output: Enforce full clone for the repository. Tools like semgrep and pre-commit hooks require a full clone. Default: - false
        :param description: The description of the repository. Default: - No description.
        :param repository_name: The name of the repository. Default: - The name of the application. other options to configure: in package.json file "config": { "repositoryName": "my-repo", }
        '''
        options = S3RepositorySourceOptions(
            bucket_name=bucket_name,
            prefix=prefix,
            removal_policy=removal_policy,
            roles=roles,
            branch=branch,
            code_build_clone_output=code_build_clone_output,
            description=description,
            repository_name=repository_name,
        )

        jsii.create(self.__class__, self, [options])

    @jsii.member(jsii_name="produceSourceConfig")
    def produce_source_config(self, context: ResourceContext) -> IRepositoryStack:
        '''
        :param context: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__836a73b666c09f791e0a9164cd93f9ddfe0ca30834a1bbb22342516c2b0be956)
            check_type(argname="argument context", value=context, expected_type=type_hints["context"])
        return typing.cast(IRepositoryStack, jsii.invoke(self, "produceSourceConfig", [context]))


@jsii.data_type(
    jsii_type="@cdklabs/cdk-cicd-wrapper.S3RepositorySourceOptions",
    jsii_struct_bases=[RepositorySourceOptions],
    name_mapping={
        "branch": "branch",
        "code_build_clone_output": "codeBuildCloneOutput",
        "description": "description",
        "repository_name": "repositoryName",
        "bucket_name": "bucketName",
        "prefix": "prefix",
        "removal_policy": "removalPolicy",
        "roles": "roles",
    },
)
class S3RepositorySourceOptions(RepositorySourceOptions):
    def __init__(
        self,
        *,
        branch: typing.Optional[builtins.str] = None,
        code_build_clone_output: typing.Optional[builtins.bool] = None,
        description: typing.Optional[builtins.str] = None,
        repository_name: typing.Optional[builtins.str] = None,
        bucket_name: typing.Optional[builtins.str] = None,
        prefix: typing.Optional[builtins.str] = None,
        removal_policy: typing.Optional[_aws_cdk_ceddda9d.RemovalPolicy] = None,
        roles: typing.Optional[typing.Sequence[builtins.str]] = None,
    ) -> None:
        '''Options for configuring an S3 repository source.

        :param branch: The branch of the repository. Default: - 'main'
        :param code_build_clone_output: Enforce full clone for the repository. Tools like semgrep and pre-commit hooks require a full clone. Default: - false
        :param description: The description of the repository. Default: - No description.
        :param repository_name: The name of the repository. Default: - The name of the application. other options to configure: in package.json file "config": { "repositoryName": "my-repo", }
        :param bucket_name: The name of the S3 bucket where the repository is stored. Default: - A bucket name is generated based on the application name, account, and region.
        :param prefix: An optional prefix to use within the S3 bucket. This can be used to specify a subdirectory within the bucket. Default: - No prefix is used.
        :param removal_policy: The removal policy for the S3 bucket.
        :param roles: An optional list of IAM roles that are allowed to access the repository.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4eb15330d57d57d2fa0906ecf502b8fcc38dfdc05caf6ab104490901b8840cc5)
            check_type(argname="argument branch", value=branch, expected_type=type_hints["branch"])
            check_type(argname="argument code_build_clone_output", value=code_build_clone_output, expected_type=type_hints["code_build_clone_output"])
            check_type(argname="argument description", value=description, expected_type=type_hints["description"])
            check_type(argname="argument repository_name", value=repository_name, expected_type=type_hints["repository_name"])
            check_type(argname="argument bucket_name", value=bucket_name, expected_type=type_hints["bucket_name"])
            check_type(argname="argument prefix", value=prefix, expected_type=type_hints["prefix"])
            check_type(argname="argument removal_policy", value=removal_policy, expected_type=type_hints["removal_policy"])
            check_type(argname="argument roles", value=roles, expected_type=type_hints["roles"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if branch is not None:
            self._values["branch"] = branch
        if code_build_clone_output is not None:
            self._values["code_build_clone_output"] = code_build_clone_output
        if description is not None:
            self._values["description"] = description
        if repository_name is not None:
            self._values["repository_name"] = repository_name
        if bucket_name is not None:
            self._values["bucket_name"] = bucket_name
        if prefix is not None:
            self._values["prefix"] = prefix
        if removal_policy is not None:
            self._values["removal_policy"] = removal_policy
        if roles is not None:
            self._values["roles"] = roles

    @builtins.property
    def branch(self) -> typing.Optional[builtins.str]:
        '''The branch of the repository.

        :default: - 'main'
        '''
        result = self._values.get("branch")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def code_build_clone_output(self) -> typing.Optional[builtins.bool]:
        '''Enforce full clone for the repository.

        Tools like semgrep and pre-commit hooks require a full clone.

        :default: - false
        '''
        result = self._values.get("code_build_clone_output")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def description(self) -> typing.Optional[builtins.str]:
        '''The description of the repository.

        :default: - No description.
        '''
        result = self._values.get("description")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def repository_name(self) -> typing.Optional[builtins.str]:
        '''The name of the repository.

        :default:

        - The name of the application.

        other options to configure:
        in  package.json file

        "config": {
        "repositoryName": "my-repo",
        }
        '''
        result = self._values.get("repository_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def bucket_name(self) -> typing.Optional[builtins.str]:
        '''The name of the S3 bucket where the repository is stored.

        :default: - A bucket name is generated based on the application name, account, and region.
        '''
        result = self._values.get("bucket_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def prefix(self) -> typing.Optional[builtins.str]:
        '''An optional prefix to use within the S3 bucket.

        This can be used to specify a subdirectory within the bucket.

        :default: - No prefix is used.
        '''
        result = self._values.get("prefix")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def removal_policy(self) -> typing.Optional[_aws_cdk_ceddda9d.RemovalPolicy]:
        '''The removal policy for the S3 bucket.'''
        result = self._values.get("removal_policy")
        return typing.cast(typing.Optional[_aws_cdk_ceddda9d.RemovalPolicy], result)

    @builtins.property
    def roles(self) -> typing.Optional[typing.List[builtins.str]]:
        '''An optional list of IAM roles that are allowed to access the repository.'''
        result = self._values.get("roles")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "S3RepositorySourceOptions(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class SSMParameterStack(
    _aws_cdk_ceddda9d.Stack,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdklabs/cdk-cicd-wrapper.SSMParameterStack",
):
    '''A stack for creating and managing AWS Systems Manager (SSM) Parameters.'''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        application_qualifier: builtins.str,
        parameter: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        analytics_reporting: typing.Optional[builtins.bool] = None,
        cross_region_references: typing.Optional[builtins.bool] = None,
        description: typing.Optional[builtins.str] = None,
        env: typing.Optional[typing.Union[_aws_cdk_ceddda9d.Environment, typing.Dict[builtins.str, typing.Any]]] = None,
        notification_arns: typing.Optional[typing.Sequence[builtins.str]] = None,
        permissions_boundary: typing.Optional[_aws_cdk_ceddda9d.PermissionsBoundary] = None,
        stack_name: typing.Optional[builtins.str] = None,
        suppress_template_indentation: typing.Optional[builtins.bool] = None,
        synthesizer: typing.Optional[_aws_cdk_ceddda9d.IStackSynthesizer] = None,
        tags: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        termination_protection: typing.Optional[builtins.bool] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param application_qualifier: The qualifier to use for the application.
        :param parameter: An optional object containing key-value pairs representing the parameters to create in the SSM Parameter Store. Default: - No parameters are created.
        :param analytics_reporting: Include runtime versioning information in this Stack. Default: ``analyticsReporting`` setting of containing ``App``, or value of 'aws:cdk:version-reporting' context key
        :param cross_region_references: Enable this flag to allow native cross region stack references. Enabling this will create a CloudFormation custom resource in both the producing stack and consuming stack in order to perform the export/import This feature is currently experimental Default: false
        :param description: A description of the stack. Default: - No description.
        :param env: The AWS environment (account/region) where this stack will be deployed. Set the ``region``/``account`` fields of ``env`` to either a concrete value to select the indicated environment (recommended for production stacks), or to the values of environment variables ``CDK_DEFAULT_REGION``/``CDK_DEFAULT_ACCOUNT`` to let the target environment depend on the AWS credentials/configuration that the CDK CLI is executed under (recommended for development stacks). If the ``Stack`` is instantiated inside a ``Stage``, any undefined ``region``/``account`` fields from ``env`` will default to the same field on the encompassing ``Stage``, if configured there. If either ``region`` or ``account`` are not set nor inherited from ``Stage``, the Stack will be considered "*environment-agnostic*"". Environment-agnostic stacks can be deployed to any environment but may not be able to take advantage of all features of the CDK. For example, they will not be able to use environmental context lookups such as ``ec2.Vpc.fromLookup`` and will not automatically translate Service Principals to the right format based on the environment's AWS partition, and other such enhancements. Default: - The environment of the containing ``Stage`` if available, otherwise create the stack will be environment-agnostic.
        :param notification_arns: SNS Topic ARNs that will receive stack events. Default: - no notfication arns.
        :param permissions_boundary: Options for applying a permissions boundary to all IAM Roles and Users created within this Stage. Default: - no permissions boundary is applied
        :param stack_name: Name to deploy the stack with. Default: - Derived from construct path.
        :param suppress_template_indentation: Enable this flag to suppress indentation in generated CloudFormation templates. If not specified, the value of the ``@aws-cdk/core:suppressTemplateIndentation`` context key will be used. If that is not specified, then the default value ``false`` will be used. Default: - the value of ``@aws-cdk/core:suppressTemplateIndentation``, or ``false`` if that is not set.
        :param synthesizer: Synthesis method to use while deploying this stack. The Stack Synthesizer controls aspects of synthesis and deployment, like how assets are referenced and what IAM roles to use. For more information, see the README of the main CDK package. If not specified, the ``defaultStackSynthesizer`` from ``App`` will be used. If that is not specified, ``DefaultStackSynthesizer`` is used if ``@aws-cdk/core:newStyleStackSynthesis`` is set to ``true`` or the CDK major version is v2. In CDK v1 ``LegacyStackSynthesizer`` is the default if no other synthesizer is specified. Default: - The synthesizer specified on ``App``, or ``DefaultStackSynthesizer`` otherwise.
        :param tags: Stack tags that will be applied to all the taggable resources and the stack itself. Default: {}
        :param termination_protection: Whether to enable termination protection for this stack. Default: false
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__79c18121b9902de42722598e43d8a1c359a96c61c2ed36a92b623a474f6282ad)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = SSMParameterStackProps(
            application_qualifier=application_qualifier,
            parameter=parameter,
            analytics_reporting=analytics_reporting,
            cross_region_references=cross_region_references,
            description=description,
            env=env,
            notification_arns=notification_arns,
            permissions_boundary=permissions_boundary,
            stack_name=stack_name,
            suppress_template_indentation=suppress_template_indentation,
            synthesizer=synthesizer,
            tags=tags,
            termination_protection=termination_protection,
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @jsii.member(jsii_name="createParameter")
    def create_parameter(
        self,
        scope: _constructs_77d1e7e8.Construct,
        parameter_name: builtins.str,
        parameter_value: builtins.str,
    ) -> _aws_cdk_aws_ssm_ceddda9d.StringParameter:
        '''Creates a new String Parameter in the SSM Parameter Store within the provided scope.

        :param scope: - The scope in which to create the parameter.
        :param parameter_name: - The name of the parameter.
        :param parameter_value: - The value of the parameter.

        :return: The created SSM String Parameter resource.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__686c34d5dc18b773af4369d624355d84ebf146e5e3b7ef1e349e08613c781ae4)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument parameter_name", value=parameter_name, expected_type=type_hints["parameter_name"])
            check_type(argname="argument parameter_value", value=parameter_value, expected_type=type_hints["parameter_value"])
        return typing.cast(_aws_cdk_aws_ssm_ceddda9d.StringParameter, jsii.invoke(self, "createParameter", [scope, parameter_name, parameter_value]))

    @jsii.member(jsii_name="createParameterInSSMParameterStack")
    def create_parameter_in_ssm_parameter_stack(
        self,
        parameter_name: builtins.str,
        parameter_value: builtins.str,
    ) -> _aws_cdk_aws_ssm_ceddda9d.StringParameter:
        '''Creates a new String Parameter in the SSM Parameter Store within this stack.

        :param parameter_name: - The name of the parameter.
        :param parameter_value: - The value of the parameter.

        :return: The created SSM String Parameter resource.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1e6df23de8cdb325667d069a22fc0f33c6721a76eb0e5b0fd929aea2f2e2d328)
            check_type(argname="argument parameter_name", value=parameter_name, expected_type=type_hints["parameter_name"])
            check_type(argname="argument parameter_value", value=parameter_value, expected_type=type_hints["parameter_value"])
        return typing.cast(_aws_cdk_aws_ssm_ceddda9d.StringParameter, jsii.invoke(self, "createParameterInSSMParameterStack", [parameter_name, parameter_value]))

    @jsii.member(jsii_name="provideParameterPolicyStatement")
    def provide_parameter_policy_statement(
        self,
    ) -> _aws_cdk_aws_iam_ceddda9d.PolicyStatement:
        '''Provides an IAM Policy Statement that grants permissions to retrieve parameters from the SSM Parameter Store.

        :return: The IAM Policy Statement granting access to the SSM Parameters.
        '''
        return typing.cast(_aws_cdk_aws_iam_ceddda9d.PolicyStatement, jsii.invoke(self, "provideParameterPolicyStatement", []))

    @builtins.property
    @jsii.member(jsii_name="applicationQualifier")
    def application_qualifier(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "applicationQualifier"))


@jsii.data_type(
    jsii_type="@cdklabs/cdk-cicd-wrapper.SSMParameterStackProps",
    jsii_struct_bases=[_aws_cdk_ceddda9d.StackProps],
    name_mapping={
        "analytics_reporting": "analyticsReporting",
        "cross_region_references": "crossRegionReferences",
        "description": "description",
        "env": "env",
        "notification_arns": "notificationArns",
        "permissions_boundary": "permissionsBoundary",
        "stack_name": "stackName",
        "suppress_template_indentation": "suppressTemplateIndentation",
        "synthesizer": "synthesizer",
        "tags": "tags",
        "termination_protection": "terminationProtection",
        "application_qualifier": "applicationQualifier",
        "parameter": "parameter",
    },
)
class SSMParameterStackProps(_aws_cdk_ceddda9d.StackProps):
    def __init__(
        self,
        *,
        analytics_reporting: typing.Optional[builtins.bool] = None,
        cross_region_references: typing.Optional[builtins.bool] = None,
        description: typing.Optional[builtins.str] = None,
        env: typing.Optional[typing.Union[_aws_cdk_ceddda9d.Environment, typing.Dict[builtins.str, typing.Any]]] = None,
        notification_arns: typing.Optional[typing.Sequence[builtins.str]] = None,
        permissions_boundary: typing.Optional[_aws_cdk_ceddda9d.PermissionsBoundary] = None,
        stack_name: typing.Optional[builtins.str] = None,
        suppress_template_indentation: typing.Optional[builtins.bool] = None,
        synthesizer: typing.Optional[_aws_cdk_ceddda9d.IStackSynthesizer] = None,
        tags: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        termination_protection: typing.Optional[builtins.bool] = None,
        application_qualifier: builtins.str,
        parameter: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
    ) -> None:
        '''Properties for the SSMParameterStack.

        :param analytics_reporting: Include runtime versioning information in this Stack. Default: ``analyticsReporting`` setting of containing ``App``, or value of 'aws:cdk:version-reporting' context key
        :param cross_region_references: Enable this flag to allow native cross region stack references. Enabling this will create a CloudFormation custom resource in both the producing stack and consuming stack in order to perform the export/import This feature is currently experimental Default: false
        :param description: A description of the stack. Default: - No description.
        :param env: The AWS environment (account/region) where this stack will be deployed. Set the ``region``/``account`` fields of ``env`` to either a concrete value to select the indicated environment (recommended for production stacks), or to the values of environment variables ``CDK_DEFAULT_REGION``/``CDK_DEFAULT_ACCOUNT`` to let the target environment depend on the AWS credentials/configuration that the CDK CLI is executed under (recommended for development stacks). If the ``Stack`` is instantiated inside a ``Stage``, any undefined ``region``/``account`` fields from ``env`` will default to the same field on the encompassing ``Stage``, if configured there. If either ``region`` or ``account`` are not set nor inherited from ``Stage``, the Stack will be considered "*environment-agnostic*"". Environment-agnostic stacks can be deployed to any environment but may not be able to take advantage of all features of the CDK. For example, they will not be able to use environmental context lookups such as ``ec2.Vpc.fromLookup`` and will not automatically translate Service Principals to the right format based on the environment's AWS partition, and other such enhancements. Default: - The environment of the containing ``Stage`` if available, otherwise create the stack will be environment-agnostic.
        :param notification_arns: SNS Topic ARNs that will receive stack events. Default: - no notfication arns.
        :param permissions_boundary: Options for applying a permissions boundary to all IAM Roles and Users created within this Stage. Default: - no permissions boundary is applied
        :param stack_name: Name to deploy the stack with. Default: - Derived from construct path.
        :param suppress_template_indentation: Enable this flag to suppress indentation in generated CloudFormation templates. If not specified, the value of the ``@aws-cdk/core:suppressTemplateIndentation`` context key will be used. If that is not specified, then the default value ``false`` will be used. Default: - the value of ``@aws-cdk/core:suppressTemplateIndentation``, or ``false`` if that is not set.
        :param synthesizer: Synthesis method to use while deploying this stack. The Stack Synthesizer controls aspects of synthesis and deployment, like how assets are referenced and what IAM roles to use. For more information, see the README of the main CDK package. If not specified, the ``defaultStackSynthesizer`` from ``App`` will be used. If that is not specified, ``DefaultStackSynthesizer`` is used if ``@aws-cdk/core:newStyleStackSynthesis`` is set to ``true`` or the CDK major version is v2. In CDK v1 ``LegacyStackSynthesizer`` is the default if no other synthesizer is specified. Default: - The synthesizer specified on ``App``, or ``DefaultStackSynthesizer`` otherwise.
        :param tags: Stack tags that will be applied to all the taggable resources and the stack itself. Default: {}
        :param termination_protection: Whether to enable termination protection for this stack. Default: false
        :param application_qualifier: The qualifier to use for the application.
        :param parameter: An optional object containing key-value pairs representing the parameters to create in the SSM Parameter Store. Default: - No parameters are created.
        '''
        if isinstance(env, dict):
            env = _aws_cdk_ceddda9d.Environment(**env)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__170535cb27d2b150d49bcbe83f3b1688950d0ecffcbf7d1dc5176a715b842332)
            check_type(argname="argument analytics_reporting", value=analytics_reporting, expected_type=type_hints["analytics_reporting"])
            check_type(argname="argument cross_region_references", value=cross_region_references, expected_type=type_hints["cross_region_references"])
            check_type(argname="argument description", value=description, expected_type=type_hints["description"])
            check_type(argname="argument env", value=env, expected_type=type_hints["env"])
            check_type(argname="argument notification_arns", value=notification_arns, expected_type=type_hints["notification_arns"])
            check_type(argname="argument permissions_boundary", value=permissions_boundary, expected_type=type_hints["permissions_boundary"])
            check_type(argname="argument stack_name", value=stack_name, expected_type=type_hints["stack_name"])
            check_type(argname="argument suppress_template_indentation", value=suppress_template_indentation, expected_type=type_hints["suppress_template_indentation"])
            check_type(argname="argument synthesizer", value=synthesizer, expected_type=type_hints["synthesizer"])
            check_type(argname="argument tags", value=tags, expected_type=type_hints["tags"])
            check_type(argname="argument termination_protection", value=termination_protection, expected_type=type_hints["termination_protection"])
            check_type(argname="argument application_qualifier", value=application_qualifier, expected_type=type_hints["application_qualifier"])
            check_type(argname="argument parameter", value=parameter, expected_type=type_hints["parameter"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "application_qualifier": application_qualifier,
        }
        if analytics_reporting is not None:
            self._values["analytics_reporting"] = analytics_reporting
        if cross_region_references is not None:
            self._values["cross_region_references"] = cross_region_references
        if description is not None:
            self._values["description"] = description
        if env is not None:
            self._values["env"] = env
        if notification_arns is not None:
            self._values["notification_arns"] = notification_arns
        if permissions_boundary is not None:
            self._values["permissions_boundary"] = permissions_boundary
        if stack_name is not None:
            self._values["stack_name"] = stack_name
        if suppress_template_indentation is not None:
            self._values["suppress_template_indentation"] = suppress_template_indentation
        if synthesizer is not None:
            self._values["synthesizer"] = synthesizer
        if tags is not None:
            self._values["tags"] = tags
        if termination_protection is not None:
            self._values["termination_protection"] = termination_protection
        if parameter is not None:
            self._values["parameter"] = parameter

    @builtins.property
    def analytics_reporting(self) -> typing.Optional[builtins.bool]:
        '''Include runtime versioning information in this Stack.

        :default:

        ``analyticsReporting`` setting of containing ``App``, or value of
        'aws:cdk:version-reporting' context key
        '''
        result = self._values.get("analytics_reporting")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def cross_region_references(self) -> typing.Optional[builtins.bool]:
        '''Enable this flag to allow native cross region stack references.

        Enabling this will create a CloudFormation custom resource
        in both the producing stack and consuming stack in order to perform the export/import

        This feature is currently experimental

        :default: false
        '''
        result = self._values.get("cross_region_references")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def description(self) -> typing.Optional[builtins.str]:
        '''A description of the stack.

        :default: - No description.
        '''
        result = self._values.get("description")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def env(self) -> typing.Optional[_aws_cdk_ceddda9d.Environment]:
        '''The AWS environment (account/region) where this stack will be deployed.

        Set the ``region``/``account`` fields of ``env`` to either a concrete value to
        select the indicated environment (recommended for production stacks), or to
        the values of environment variables
        ``CDK_DEFAULT_REGION``/``CDK_DEFAULT_ACCOUNT`` to let the target environment
        depend on the AWS credentials/configuration that the CDK CLI is executed
        under (recommended for development stacks).

        If the ``Stack`` is instantiated inside a ``Stage``, any undefined
        ``region``/``account`` fields from ``env`` will default to the same field on the
        encompassing ``Stage``, if configured there.

        If either ``region`` or ``account`` are not set nor inherited from ``Stage``, the
        Stack will be considered "*environment-agnostic*"". Environment-agnostic
        stacks can be deployed to any environment but may not be able to take
        advantage of all features of the CDK. For example, they will not be able to
        use environmental context lookups such as ``ec2.Vpc.fromLookup`` and will not
        automatically translate Service Principals to the right format based on the
        environment's AWS partition, and other such enhancements.

        :default:

        - The environment of the containing ``Stage`` if available,
        otherwise create the stack will be environment-agnostic.

        Example::

            // Use a concrete account and region to deploy this stack to:
            // `.account` and `.region` will simply return these values.
            new Stack(app, 'Stack1', {
              env: {
                account: '123456789012',
                region: 'us-east-1'
              },
            });
            
            // Use the CLI's current credentials to determine the target environment:
            // `.account` and `.region` will reflect the account+region the CLI
            // is configured to use (based on the user CLI credentials)
            new Stack(app, 'Stack2', {
              env: {
                account: process.env.CDK_DEFAULT_ACCOUNT,
                region: process.env.CDK_DEFAULT_REGION
              },
            });
            
            // Define multiple stacks stage associated with an environment
            const myStage = new Stage(app, 'MyStage', {
              env: {
                account: '123456789012',
                region: 'us-east-1'
              }
            });
            
            // both of these stacks will use the stage's account/region:
            // `.account` and `.region` will resolve to the concrete values as above
            new MyStack(myStage, 'Stack1');
            new YourStack(myStage, 'Stack2');
            
            // Define an environment-agnostic stack:
            // `.account` and `.region` will resolve to `{ "Ref": "AWS::AccountId" }` and `{ "Ref": "AWS::Region" }` respectively.
            // which will only resolve to actual values by CloudFormation during deployment.
            new MyStack(app, 'Stack1');
        '''
        result = self._values.get("env")
        return typing.cast(typing.Optional[_aws_cdk_ceddda9d.Environment], result)

    @builtins.property
    def notification_arns(self) -> typing.Optional[typing.List[builtins.str]]:
        '''SNS Topic ARNs that will receive stack events.

        :default: - no notfication arns.
        '''
        result = self._values.get("notification_arns")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def permissions_boundary(
        self,
    ) -> typing.Optional[_aws_cdk_ceddda9d.PermissionsBoundary]:
        '''Options for applying a permissions boundary to all IAM Roles and Users created within this Stage.

        :default: - no permissions boundary is applied
        '''
        result = self._values.get("permissions_boundary")
        return typing.cast(typing.Optional[_aws_cdk_ceddda9d.PermissionsBoundary], result)

    @builtins.property
    def stack_name(self) -> typing.Optional[builtins.str]:
        '''Name to deploy the stack with.

        :default: - Derived from construct path.
        '''
        result = self._values.get("stack_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def suppress_template_indentation(self) -> typing.Optional[builtins.bool]:
        '''Enable this flag to suppress indentation in generated CloudFormation templates.

        If not specified, the value of the ``@aws-cdk/core:suppressTemplateIndentation``
        context key will be used. If that is not specified, then the
        default value ``false`` will be used.

        :default: - the value of ``@aws-cdk/core:suppressTemplateIndentation``, or ``false`` if that is not set.
        '''
        result = self._values.get("suppress_template_indentation")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def synthesizer(self) -> typing.Optional[_aws_cdk_ceddda9d.IStackSynthesizer]:
        '''Synthesis method to use while deploying this stack.

        The Stack Synthesizer controls aspects of synthesis and deployment,
        like how assets are referenced and what IAM roles to use. For more
        information, see the README of the main CDK package.

        If not specified, the ``defaultStackSynthesizer`` from ``App`` will be used.
        If that is not specified, ``DefaultStackSynthesizer`` is used if
        ``@aws-cdk/core:newStyleStackSynthesis`` is set to ``true`` or the CDK major
        version is v2. In CDK v1 ``LegacyStackSynthesizer`` is the default if no
        other synthesizer is specified.

        :default: - The synthesizer specified on ``App``, or ``DefaultStackSynthesizer`` otherwise.
        '''
        result = self._values.get("synthesizer")
        return typing.cast(typing.Optional[_aws_cdk_ceddda9d.IStackSynthesizer], result)

    @builtins.property
    def tags(self) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        '''Stack tags that will be applied to all the taggable resources and the stack itself.

        :default: {}
        '''
        result = self._values.get("tags")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], result)

    @builtins.property
    def termination_protection(self) -> typing.Optional[builtins.bool]:
        '''Whether to enable termination protection for this stack.

        :default: false
        '''
        result = self._values.get("termination_protection")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def application_qualifier(self) -> builtins.str:
        '''The qualifier to use for the application.'''
        result = self._values.get("application_qualifier")
        assert result is not None, "Required property 'application_qualifier' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def parameter(self) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        '''An optional object containing key-value pairs representing the parameters to create in the SSM Parameter Store.

        :default: - No parameters are created.
        '''
        result = self._values.get("parameter")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "SSMParameterStackProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.enum(jsii_type="@cdklabs/cdk-cicd-wrapper.Scope")
class Scope(enum.Enum):
    '''Defines the scope of a resource provider.'''

    GLOBAL = "GLOBAL"
    '''The resource provider will be available globally across all stages.'''
    PER_STAGE = "PER_STAGE"
    '''The resource provider will be available only within the current stage.'''


@jsii.implements(IPhaseCommand)
class ShellCommandPhaseCommand(
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdklabs/cdk-cicd-wrapper.ShellCommandPhaseCommand",
):
    '''Phase Command that invokes a simple shell command.'''

    def __init__(self, command: builtins.str) -> None:
        '''
        :param command: The command to run during the phase.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__97d34fd84710d7e19754b401f9349c4ef78fc6ac154658f21e15f05229da479d)
            check_type(argname="argument command", value=command, expected_type=type_hints["command"])
        jsii.create(self.__class__, self, [command])

    @builtins.property
    @jsii.member(jsii_name="command")
    def command(self) -> builtins.str:
        '''The command to run during the phase.'''
        return typing.cast(builtins.str, jsii.get(self, "command"))


@jsii.implements(IPhaseCommand)
class ShellScriptPhaseCommand(
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdklabs/cdk-cicd-wrapper.ShellScriptPhaseCommand",
):
    '''Phase Command that invokes shell scripts from project folder.'''

    def __init__(self, script: builtins.str) -> None:
        '''
        :param script: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__cb3e9a52990b22235a8364f4211bde160966e495fa73cb3bc33fa7047bb09871)
            check_type(argname="argument script", value=script, expected_type=type_hints["script"])
        jsii.create(self.__class__, self, [script])

    @builtins.property
    @jsii.member(jsii_name="command")
    def command(self) -> builtins.str:
        '''Returns the command to be executed for the given shell script.'''
        return typing.cast(builtins.str, jsii.get(self, "command"))

    @builtins.property
    @jsii.member(jsii_name="script")
    def script(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "script"))


class Stage(metaclass=jsii.JSIIMeta, jsii_type="@cdklabs/cdk-cicd-wrapper.Stage"):
    '''Represents the stages in the pipeline.'''

    def __init__(self) -> None:
        jsii.create(self.__class__, self, [])

    @jsii.python.classproperty
    @jsii.member(jsii_name="DEV")
    def DEV(cls) -> builtins.str:
        '''The 'DEV' stage.'''
        return typing.cast(builtins.str, jsii.sget(cls, "DEV"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="INT")
    def INT(cls) -> builtins.str:
        '''The 'INT' stage.'''
        return typing.cast(builtins.str, jsii.sget(cls, "INT"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="PROD")
    def PROD(cls) -> builtins.str:
        '''The 'PROD' stage.'''
        return typing.cast(builtins.str, jsii.sget(cls, "PROD"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="RES")
    def RES(cls) -> builtins.str:
        '''The 'RES' stage.'''
        return typing.cast(builtins.str, jsii.sget(cls, "RES"))


@jsii.implements(IResourceProvider)
class StageProvider(
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdklabs/cdk-cicd-wrapper.StageProvider",
):
    '''Provides AppStage definitions.'''

    def __init__(self) -> None:
        jsii.create(self.__class__, self, [])

    @jsii.member(jsii_name="provide")
    def provide(self, context: ResourceContext) -> typing.Any:
        '''Provides an AppStage instance based on the given ResourceContext.

        :param context: - The ResourceContext containing information about the current scope, stage, and environment.

        :return: An instance of AppStage.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7220e6b836834a71afbd78df0aace7bd839469e961059ac52d5b7ce7b0236a2d)
            check_type(argname="argument context", value=context, expected_type=type_hints["context"])
        return typing.cast(typing.Any, jsii.invoke(self, "provide", [context]))

    @builtins.property
    @jsii.member(jsii_name="scope")
    def scope(self) -> typing.Optional[Scope]:
        '''Scope at which the provider operates.

        Defaults to Scope.PER_STAGE.
        '''
        return typing.cast(typing.Optional[Scope], jsii.get(self, "scope"))

    @scope.setter
    def scope(self, value: typing.Optional[Scope]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__32dfdf8b3797d6aa03fe8fe21749e5e347f05045ad36b7481f9686b3e7adfec9)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "scope", value) # pyright: ignore[reportArgumentType]


class VPCFromLookUpStack(
    _aws_cdk_ceddda9d.Stack,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdklabs/cdk-cicd-wrapper.VPCFromLookUpStack",
):
    '''A stack that creates or looks up a VPC and configures its settings.'''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        vpc_id: builtins.str,
        code_build_vpc_interfaces: typing.Optional[typing.Sequence[_aws_cdk_aws_ec2_ceddda9d.InterfaceVpcEndpointAwsService]] = None,
        analytics_reporting: typing.Optional[builtins.bool] = None,
        cross_region_references: typing.Optional[builtins.bool] = None,
        description: typing.Optional[builtins.str] = None,
        env: typing.Optional[typing.Union[_aws_cdk_ceddda9d.Environment, typing.Dict[builtins.str, typing.Any]]] = None,
        notification_arns: typing.Optional[typing.Sequence[builtins.str]] = None,
        permissions_boundary: typing.Optional[_aws_cdk_ceddda9d.PermissionsBoundary] = None,
        stack_name: typing.Optional[builtins.str] = None,
        suppress_template_indentation: typing.Optional[builtins.bool] = None,
        synthesizer: typing.Optional[_aws_cdk_ceddda9d.IStackSynthesizer] = None,
        tags: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        termination_protection: typing.Optional[builtins.bool] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param vpc_id: The configuration for the VPC to be created or looked up.
        :param code_build_vpc_interfaces: The list of CodeBuild VPC InterfacesVpcEndpointAwsServices to extend the defaultCodeBuildVPCInterfaces.
        :param analytics_reporting: Include runtime versioning information in this Stack. Default: ``analyticsReporting`` setting of containing ``App``, or value of 'aws:cdk:version-reporting' context key
        :param cross_region_references: Enable this flag to allow native cross region stack references. Enabling this will create a CloudFormation custom resource in both the producing stack and consuming stack in order to perform the export/import This feature is currently experimental Default: false
        :param description: A description of the stack. Default: - No description.
        :param env: The AWS environment (account/region) where this stack will be deployed. Set the ``region``/``account`` fields of ``env`` to either a concrete value to select the indicated environment (recommended for production stacks), or to the values of environment variables ``CDK_DEFAULT_REGION``/``CDK_DEFAULT_ACCOUNT`` to let the target environment depend on the AWS credentials/configuration that the CDK CLI is executed under (recommended for development stacks). If the ``Stack`` is instantiated inside a ``Stage``, any undefined ``region``/``account`` fields from ``env`` will default to the same field on the encompassing ``Stage``, if configured there. If either ``region`` or ``account`` are not set nor inherited from ``Stage``, the Stack will be considered "*environment-agnostic*"". Environment-agnostic stacks can be deployed to any environment but may not be able to take advantage of all features of the CDK. For example, they will not be able to use environmental context lookups such as ``ec2.Vpc.fromLookup`` and will not automatically translate Service Principals to the right format based on the environment's AWS partition, and other such enhancements. Default: - The environment of the containing ``Stage`` if available, otherwise create the stack will be environment-agnostic.
        :param notification_arns: SNS Topic ARNs that will receive stack events. Default: - no notfication arns.
        :param permissions_boundary: Options for applying a permissions boundary to all IAM Roles and Users created within this Stage. Default: - no permissions boundary is applied
        :param stack_name: Name to deploy the stack with. Default: - Derived from construct path.
        :param suppress_template_indentation: Enable this flag to suppress indentation in generated CloudFormation templates. If not specified, the value of the ``@aws-cdk/core:suppressTemplateIndentation`` context key will be used. If that is not specified, then the default value ``false`` will be used. Default: - the value of ``@aws-cdk/core:suppressTemplateIndentation``, or ``false`` if that is not set.
        :param synthesizer: Synthesis method to use while deploying this stack. The Stack Synthesizer controls aspects of synthesis and deployment, like how assets are referenced and what IAM roles to use. For more information, see the README of the main CDK package. If not specified, the ``defaultStackSynthesizer`` from ``App`` will be used. If that is not specified, ``DefaultStackSynthesizer`` is used if ``@aws-cdk/core:newStyleStackSynthesis`` is set to ``true`` or the CDK major version is v2. In CDK v1 ``LegacyStackSynthesizer`` is the default if no other synthesizer is specified. Default: - The synthesizer specified on ``App``, or ``DefaultStackSynthesizer`` otherwise.
        :param tags: Stack tags that will be applied to all the taggable resources and the stack itself. Default: {}
        :param termination_protection: Whether to enable termination protection for this stack. Default: false
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4d3d82188ff493924bd19bfd03d82068f7bdf03bc8245e19aea750d438e9afe2)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = VPCFromLookUpStackProps(
            vpc_id=vpc_id,
            code_build_vpc_interfaces=code_build_vpc_interfaces,
            analytics_reporting=analytics_reporting,
            cross_region_references=cross_region_references,
            description=description,
            env=env,
            notification_arns=notification_arns,
            permissions_boundary=permissions_boundary,
            stack_name=stack_name,
            suppress_template_indentation=suppress_template_indentation,
            synthesizer=synthesizer,
            tags=tags,
            termination_protection=termination_protection,
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @builtins.property
    @jsii.member(jsii_name="codeBuildVPCInterfaces")
    def code_build_vpc_interfaces(
        self,
    ) -> typing.List[_aws_cdk_aws_ec2_ceddda9d.InterfaceVpcEndpointAwsService]:
        '''The list of CodeBuild VPC InterfacesVpcEndpointAwsServices.'''
        return typing.cast(typing.List[_aws_cdk_aws_ec2_ceddda9d.InterfaceVpcEndpointAwsService], jsii.get(self, "codeBuildVPCInterfaces"))

    @builtins.property
    @jsii.member(jsii_name="vpc")
    def vpc(self) -> _aws_cdk_aws_ec2_ceddda9d.IVpc:
        '''The VPC created or looked up by this stack.'''
        return typing.cast(_aws_cdk_aws_ec2_ceddda9d.IVpc, jsii.get(self, "vpc"))

    @builtins.property
    @jsii.member(jsii_name="vpcId")
    def vpc_id(self) -> builtins.str:
        '''The ID of the VPC being created or looked up.'''
        return typing.cast(builtins.str, jsii.get(self, "vpcId"))

    @builtins.property
    @jsii.member(jsii_name="securityGroup")
    def security_group(
        self,
    ) -> typing.Optional[_aws_cdk_aws_ec2_ceddda9d.ISecurityGroup]:
        '''The security group attached to the VPC.'''
        return typing.cast(typing.Optional[_aws_cdk_aws_ec2_ceddda9d.ISecurityGroup], jsii.get(self, "securityGroup"))

    @builtins.property
    @jsii.member(jsii_name="subnetType")
    def subnet_type(self) -> typing.Optional[_aws_cdk_aws_ec2_ceddda9d.SubnetType]:
        '''The subnets attached to the VPC.'''
        return typing.cast(typing.Optional[_aws_cdk_aws_ec2_ceddda9d.SubnetType], jsii.get(self, "subnetType"))


@jsii.data_type(
    jsii_type="@cdklabs/cdk-cicd-wrapper.VPCFromLookUpStackProps",
    jsii_struct_bases=[_aws_cdk_ceddda9d.StackProps],
    name_mapping={
        "analytics_reporting": "analyticsReporting",
        "cross_region_references": "crossRegionReferences",
        "description": "description",
        "env": "env",
        "notification_arns": "notificationArns",
        "permissions_boundary": "permissionsBoundary",
        "stack_name": "stackName",
        "suppress_template_indentation": "suppressTemplateIndentation",
        "synthesizer": "synthesizer",
        "tags": "tags",
        "termination_protection": "terminationProtection",
        "vpc_id": "vpcId",
        "code_build_vpc_interfaces": "codeBuildVPCInterfaces",
    },
)
class VPCFromLookUpStackProps(_aws_cdk_ceddda9d.StackProps):
    def __init__(
        self,
        *,
        analytics_reporting: typing.Optional[builtins.bool] = None,
        cross_region_references: typing.Optional[builtins.bool] = None,
        description: typing.Optional[builtins.str] = None,
        env: typing.Optional[typing.Union[_aws_cdk_ceddda9d.Environment, typing.Dict[builtins.str, typing.Any]]] = None,
        notification_arns: typing.Optional[typing.Sequence[builtins.str]] = None,
        permissions_boundary: typing.Optional[_aws_cdk_ceddda9d.PermissionsBoundary] = None,
        stack_name: typing.Optional[builtins.str] = None,
        suppress_template_indentation: typing.Optional[builtins.bool] = None,
        synthesizer: typing.Optional[_aws_cdk_ceddda9d.IStackSynthesizer] = None,
        tags: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        termination_protection: typing.Optional[builtins.bool] = None,
        vpc_id: builtins.str,
        code_build_vpc_interfaces: typing.Optional[typing.Sequence[_aws_cdk_aws_ec2_ceddda9d.InterfaceVpcEndpointAwsService]] = None,
    ) -> None:
        '''Properties for the VPCStack.

        :param analytics_reporting: Include runtime versioning information in this Stack. Default: ``analyticsReporting`` setting of containing ``App``, or value of 'aws:cdk:version-reporting' context key
        :param cross_region_references: Enable this flag to allow native cross region stack references. Enabling this will create a CloudFormation custom resource in both the producing stack and consuming stack in order to perform the export/import This feature is currently experimental Default: false
        :param description: A description of the stack. Default: - No description.
        :param env: The AWS environment (account/region) where this stack will be deployed. Set the ``region``/``account`` fields of ``env`` to either a concrete value to select the indicated environment (recommended for production stacks), or to the values of environment variables ``CDK_DEFAULT_REGION``/``CDK_DEFAULT_ACCOUNT`` to let the target environment depend on the AWS credentials/configuration that the CDK CLI is executed under (recommended for development stacks). If the ``Stack`` is instantiated inside a ``Stage``, any undefined ``region``/``account`` fields from ``env`` will default to the same field on the encompassing ``Stage``, if configured there. If either ``region`` or ``account`` are not set nor inherited from ``Stage``, the Stack will be considered "*environment-agnostic*"". Environment-agnostic stacks can be deployed to any environment but may not be able to take advantage of all features of the CDK. For example, they will not be able to use environmental context lookups such as ``ec2.Vpc.fromLookup`` and will not automatically translate Service Principals to the right format based on the environment's AWS partition, and other such enhancements. Default: - The environment of the containing ``Stage`` if available, otherwise create the stack will be environment-agnostic.
        :param notification_arns: SNS Topic ARNs that will receive stack events. Default: - no notfication arns.
        :param permissions_boundary: Options for applying a permissions boundary to all IAM Roles and Users created within this Stage. Default: - no permissions boundary is applied
        :param stack_name: Name to deploy the stack with. Default: - Derived from construct path.
        :param suppress_template_indentation: Enable this flag to suppress indentation in generated CloudFormation templates. If not specified, the value of the ``@aws-cdk/core:suppressTemplateIndentation`` context key will be used. If that is not specified, then the default value ``false`` will be used. Default: - the value of ``@aws-cdk/core:suppressTemplateIndentation``, or ``false`` if that is not set.
        :param synthesizer: Synthesis method to use while deploying this stack. The Stack Synthesizer controls aspects of synthesis and deployment, like how assets are referenced and what IAM roles to use. For more information, see the README of the main CDK package. If not specified, the ``defaultStackSynthesizer`` from ``App`` will be used. If that is not specified, ``DefaultStackSynthesizer`` is used if ``@aws-cdk/core:newStyleStackSynthesis`` is set to ``true`` or the CDK major version is v2. In CDK v1 ``LegacyStackSynthesizer`` is the default if no other synthesizer is specified. Default: - The synthesizer specified on ``App``, or ``DefaultStackSynthesizer`` otherwise.
        :param tags: Stack tags that will be applied to all the taggable resources and the stack itself. Default: {}
        :param termination_protection: Whether to enable termination protection for this stack. Default: false
        :param vpc_id: The configuration for the VPC to be created or looked up.
        :param code_build_vpc_interfaces: The list of CodeBuild VPC InterfacesVpcEndpointAwsServices to extend the defaultCodeBuildVPCInterfaces.
        '''
        if isinstance(env, dict):
            env = _aws_cdk_ceddda9d.Environment(**env)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__568a5801eb6463e97dd95391b7a31bc0cf542050e26818e6fe0fdb7fa00898a6)
            check_type(argname="argument analytics_reporting", value=analytics_reporting, expected_type=type_hints["analytics_reporting"])
            check_type(argname="argument cross_region_references", value=cross_region_references, expected_type=type_hints["cross_region_references"])
            check_type(argname="argument description", value=description, expected_type=type_hints["description"])
            check_type(argname="argument env", value=env, expected_type=type_hints["env"])
            check_type(argname="argument notification_arns", value=notification_arns, expected_type=type_hints["notification_arns"])
            check_type(argname="argument permissions_boundary", value=permissions_boundary, expected_type=type_hints["permissions_boundary"])
            check_type(argname="argument stack_name", value=stack_name, expected_type=type_hints["stack_name"])
            check_type(argname="argument suppress_template_indentation", value=suppress_template_indentation, expected_type=type_hints["suppress_template_indentation"])
            check_type(argname="argument synthesizer", value=synthesizer, expected_type=type_hints["synthesizer"])
            check_type(argname="argument tags", value=tags, expected_type=type_hints["tags"])
            check_type(argname="argument termination_protection", value=termination_protection, expected_type=type_hints["termination_protection"])
            check_type(argname="argument vpc_id", value=vpc_id, expected_type=type_hints["vpc_id"])
            check_type(argname="argument code_build_vpc_interfaces", value=code_build_vpc_interfaces, expected_type=type_hints["code_build_vpc_interfaces"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "vpc_id": vpc_id,
        }
        if analytics_reporting is not None:
            self._values["analytics_reporting"] = analytics_reporting
        if cross_region_references is not None:
            self._values["cross_region_references"] = cross_region_references
        if description is not None:
            self._values["description"] = description
        if env is not None:
            self._values["env"] = env
        if notification_arns is not None:
            self._values["notification_arns"] = notification_arns
        if permissions_boundary is not None:
            self._values["permissions_boundary"] = permissions_boundary
        if stack_name is not None:
            self._values["stack_name"] = stack_name
        if suppress_template_indentation is not None:
            self._values["suppress_template_indentation"] = suppress_template_indentation
        if synthesizer is not None:
            self._values["synthesizer"] = synthesizer
        if tags is not None:
            self._values["tags"] = tags
        if termination_protection is not None:
            self._values["termination_protection"] = termination_protection
        if code_build_vpc_interfaces is not None:
            self._values["code_build_vpc_interfaces"] = code_build_vpc_interfaces

    @builtins.property
    def analytics_reporting(self) -> typing.Optional[builtins.bool]:
        '''Include runtime versioning information in this Stack.

        :default:

        ``analyticsReporting`` setting of containing ``App``, or value of
        'aws:cdk:version-reporting' context key
        '''
        result = self._values.get("analytics_reporting")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def cross_region_references(self) -> typing.Optional[builtins.bool]:
        '''Enable this flag to allow native cross region stack references.

        Enabling this will create a CloudFormation custom resource
        in both the producing stack and consuming stack in order to perform the export/import

        This feature is currently experimental

        :default: false
        '''
        result = self._values.get("cross_region_references")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def description(self) -> typing.Optional[builtins.str]:
        '''A description of the stack.

        :default: - No description.
        '''
        result = self._values.get("description")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def env(self) -> typing.Optional[_aws_cdk_ceddda9d.Environment]:
        '''The AWS environment (account/region) where this stack will be deployed.

        Set the ``region``/``account`` fields of ``env`` to either a concrete value to
        select the indicated environment (recommended for production stacks), or to
        the values of environment variables
        ``CDK_DEFAULT_REGION``/``CDK_DEFAULT_ACCOUNT`` to let the target environment
        depend on the AWS credentials/configuration that the CDK CLI is executed
        under (recommended for development stacks).

        If the ``Stack`` is instantiated inside a ``Stage``, any undefined
        ``region``/``account`` fields from ``env`` will default to the same field on the
        encompassing ``Stage``, if configured there.

        If either ``region`` or ``account`` are not set nor inherited from ``Stage``, the
        Stack will be considered "*environment-agnostic*"". Environment-agnostic
        stacks can be deployed to any environment but may not be able to take
        advantage of all features of the CDK. For example, they will not be able to
        use environmental context lookups such as ``ec2.Vpc.fromLookup`` and will not
        automatically translate Service Principals to the right format based on the
        environment's AWS partition, and other such enhancements.

        :default:

        - The environment of the containing ``Stage`` if available,
        otherwise create the stack will be environment-agnostic.

        Example::

            // Use a concrete account and region to deploy this stack to:
            // `.account` and `.region` will simply return these values.
            new Stack(app, 'Stack1', {
              env: {
                account: '123456789012',
                region: 'us-east-1'
              },
            });
            
            // Use the CLI's current credentials to determine the target environment:
            // `.account` and `.region` will reflect the account+region the CLI
            // is configured to use (based on the user CLI credentials)
            new Stack(app, 'Stack2', {
              env: {
                account: process.env.CDK_DEFAULT_ACCOUNT,
                region: process.env.CDK_DEFAULT_REGION
              },
            });
            
            // Define multiple stacks stage associated with an environment
            const myStage = new Stage(app, 'MyStage', {
              env: {
                account: '123456789012',
                region: 'us-east-1'
              }
            });
            
            // both of these stacks will use the stage's account/region:
            // `.account` and `.region` will resolve to the concrete values as above
            new MyStack(myStage, 'Stack1');
            new YourStack(myStage, 'Stack2');
            
            // Define an environment-agnostic stack:
            // `.account` and `.region` will resolve to `{ "Ref": "AWS::AccountId" }` and `{ "Ref": "AWS::Region" }` respectively.
            // which will only resolve to actual values by CloudFormation during deployment.
            new MyStack(app, 'Stack1');
        '''
        result = self._values.get("env")
        return typing.cast(typing.Optional[_aws_cdk_ceddda9d.Environment], result)

    @builtins.property
    def notification_arns(self) -> typing.Optional[typing.List[builtins.str]]:
        '''SNS Topic ARNs that will receive stack events.

        :default: - no notfication arns.
        '''
        result = self._values.get("notification_arns")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def permissions_boundary(
        self,
    ) -> typing.Optional[_aws_cdk_ceddda9d.PermissionsBoundary]:
        '''Options for applying a permissions boundary to all IAM Roles and Users created within this Stage.

        :default: - no permissions boundary is applied
        '''
        result = self._values.get("permissions_boundary")
        return typing.cast(typing.Optional[_aws_cdk_ceddda9d.PermissionsBoundary], result)

    @builtins.property
    def stack_name(self) -> typing.Optional[builtins.str]:
        '''Name to deploy the stack with.

        :default: - Derived from construct path.
        '''
        result = self._values.get("stack_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def suppress_template_indentation(self) -> typing.Optional[builtins.bool]:
        '''Enable this flag to suppress indentation in generated CloudFormation templates.

        If not specified, the value of the ``@aws-cdk/core:suppressTemplateIndentation``
        context key will be used. If that is not specified, then the
        default value ``false`` will be used.

        :default: - the value of ``@aws-cdk/core:suppressTemplateIndentation``, or ``false`` if that is not set.
        '''
        result = self._values.get("suppress_template_indentation")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def synthesizer(self) -> typing.Optional[_aws_cdk_ceddda9d.IStackSynthesizer]:
        '''Synthesis method to use while deploying this stack.

        The Stack Synthesizer controls aspects of synthesis and deployment,
        like how assets are referenced and what IAM roles to use. For more
        information, see the README of the main CDK package.

        If not specified, the ``defaultStackSynthesizer`` from ``App`` will be used.
        If that is not specified, ``DefaultStackSynthesizer`` is used if
        ``@aws-cdk/core:newStyleStackSynthesis`` is set to ``true`` or the CDK major
        version is v2. In CDK v1 ``LegacyStackSynthesizer`` is the default if no
        other synthesizer is specified.

        :default: - The synthesizer specified on ``App``, or ``DefaultStackSynthesizer`` otherwise.
        '''
        result = self._values.get("synthesizer")
        return typing.cast(typing.Optional[_aws_cdk_ceddda9d.IStackSynthesizer], result)

    @builtins.property
    def tags(self) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        '''Stack tags that will be applied to all the taggable resources and the stack itself.

        :default: {}
        '''
        result = self._values.get("tags")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], result)

    @builtins.property
    def termination_protection(self) -> typing.Optional[builtins.bool]:
        '''Whether to enable termination protection for this stack.

        :default: false
        '''
        result = self._values.get("termination_protection")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def vpc_id(self) -> builtins.str:
        '''The configuration for the VPC to be created or looked up.'''
        result = self._values.get("vpc_id")
        assert result is not None, "Required property 'vpc_id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def code_build_vpc_interfaces(
        self,
    ) -> typing.Optional[typing.List[_aws_cdk_aws_ec2_ceddda9d.InterfaceVpcEndpointAwsService]]:
        '''The list of CodeBuild VPC InterfacesVpcEndpointAwsServices to extend the defaultCodeBuildVPCInterfaces.'''
        result = self._values.get("code_build_vpc_interfaces")
        return typing.cast(typing.Optional[typing.List[_aws_cdk_aws_ec2_ceddda9d.InterfaceVpcEndpointAwsService]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "VPCFromLookUpStackProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.implements(IResourceProvider)
class VPCProvider(
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdklabs/cdk-cicd-wrapper.VPCProvider",
):
    '''Legacy VPC Provider that defines the VPC used by the CI/CD process.'''

    def __init__(self, legacy_config: typing.Optional[IVpcConfig] = None) -> None:
        '''
        :param legacy_config: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9cb678678c5149ad6421a902df2d3a623600a703dd7c5f18faad8ffa9f15978a)
            check_type(argname="argument legacy_config", value=legacy_config, expected_type=type_hints["legacy_config"])
        jsii.create(self.__class__, self, [legacy_config])

    @jsii.member(jsii_name="provide")
    def provide(self, context: ResourceContext) -> typing.Any:
        '''Provides the VPC resource.

        :param context: The resource context.

        :return: The VPC stack
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__fdd3c2dd80b7c984a453628a65861222abc4482d8381a85218fecd00f299f006)
            check_type(argname="argument context", value=context, expected_type=type_hints["context"])
        return typing.cast(typing.Any, jsii.invoke(self, "provide", [context]))

    @builtins.property
    @jsii.member(jsii_name="legacyConfig")
    def legacy_config(self) -> IVpcConfig:
        return typing.cast(IVpcConfig, jsii.get(self, "legacyConfig"))

    @builtins.property
    @jsii.member(jsii_name="scope")
    def scope(self) -> typing.Optional[Scope]:
        '''The scope in which the resource provider is available.

        Defaults to ``Scope.GLOBAL``.
        '''
        return typing.cast(typing.Optional[Scope], jsii.get(self, "scope"))

    @scope.setter
    def scope(self, value: typing.Optional[Scope]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__622fe918713ec74ba2c1e4ab2f7ed8ae0a4ec65a96fe0e8620746aab99e4a8d9)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "scope", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdklabs/cdk-cicd-wrapper.VpcProps",
    jsii_struct_bases=[],
    name_mapping={"vpc": "vpc", "proxy": "proxy"},
)
class VpcProps:
    def __init__(
        self,
        *,
        vpc: _aws_cdk_aws_ec2_ceddda9d.IVpc,
        proxy: typing.Optional[typing.Union[ProxyProps, typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''Props for configuring a VPC.

        :param vpc: The VPC to be used.
        :param proxy: Proxy configuration.
        '''
        if isinstance(proxy, dict):
            proxy = ProxyProps(**proxy)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__eaeae75044f602086394b1aa0bcd90ce0806f7528969b249d9b40078c36ddab4)
            check_type(argname="argument vpc", value=vpc, expected_type=type_hints["vpc"])
            check_type(argname="argument proxy", value=proxy, expected_type=type_hints["proxy"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "vpc": vpc,
        }
        if proxy is not None:
            self._values["proxy"] = proxy

    @builtins.property
    def vpc(self) -> _aws_cdk_aws_ec2_ceddda9d.IVpc:
        '''The VPC to be used.'''
        result = self._values.get("vpc")
        assert result is not None, "Required property 'vpc' is missing"
        return typing.cast(_aws_cdk_aws_ec2_ceddda9d.IVpc, result)

    @builtins.property
    def proxy(self) -> typing.Optional[ProxyProps]:
        '''Proxy configuration.'''
        result = self._values.get("proxy")
        return typing.cast(typing.Optional[ProxyProps], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "VpcProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdklabs/cdk-cicd-wrapper.WorkbenchConfig",
    jsii_struct_bases=[],
    name_mapping={"options": "options", "stack_provider": "stackProvider"},
)
class WorkbenchConfig:
    def __init__(
        self,
        *,
        options: typing.Union["WorkbenchOptions", typing.Dict[builtins.str, typing.Any]],
        stack_provider: IStackProvider,
    ) -> None:
        '''Represents the configuration for a workbench.

        :param options: The options for the workbench.
        :param stack_provider: The stack provider for the workbench.
        '''
        if isinstance(options, dict):
            options = WorkbenchOptions(**options)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__34abccea35b03904e80070603d8ca068e8fb7d437444a2dd7d242c1b2bd24fe1)
            check_type(argname="argument options", value=options, expected_type=type_hints["options"])
            check_type(argname="argument stack_provider", value=stack_provider, expected_type=type_hints["stack_provider"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "options": options,
            "stack_provider": stack_provider,
        }

    @builtins.property
    def options(self) -> "WorkbenchOptions":
        '''The options for the workbench.'''
        result = self._values.get("options")
        assert result is not None, "Required property 'options' is missing"
        return typing.cast("WorkbenchOptions", result)

    @builtins.property
    def stack_provider(self) -> IStackProvider:
        '''The stack provider for the workbench.'''
        result = self._values.get("stack_provider")
        assert result is not None, "Required property 'stack_provider' is missing"
        return typing.cast(IStackProvider, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "WorkbenchConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdklabs/cdk-cicd-wrapper.WorkbenchOptions",
    jsii_struct_bases=[],
    name_mapping={"stage_to_use": "stageToUse", "workbench_prefix": "workbenchPrefix"},
)
class WorkbenchOptions:
    def __init__(
        self,
        *,
        stage_to_use: typing.Optional[builtins.str] = None,
        workbench_prefix: typing.Optional[builtins.str] = None,
    ) -> None:
        '''Represents the options for a workbench.

        :param stage_to_use: The stage to use for the workbench (optional).
        :param workbench_prefix: The prefix for the workbench (optional).
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b019ff265121b74fa169874c60cca2bfa4c9422a7c81b457375d95b4e54eefd0)
            check_type(argname="argument stage_to_use", value=stage_to_use, expected_type=type_hints["stage_to_use"])
            check_type(argname="argument workbench_prefix", value=workbench_prefix, expected_type=type_hints["workbench_prefix"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if stage_to_use is not None:
            self._values["stage_to_use"] = stage_to_use
        if workbench_prefix is not None:
            self._values["workbench_prefix"] = workbench_prefix

    @builtins.property
    def stage_to_use(self) -> typing.Optional[builtins.str]:
        '''The stage to use for the workbench (optional).'''
        result = self._values.get("stage_to_use")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def workbench_prefix(self) -> typing.Optional[builtins.str]:
        '''The prefix for the workbench (optional).'''
        result = self._values.get("workbench_prefix")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "WorkbenchOptions(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class AccessLogsForBucketPlugin(
    PluginBase,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdklabs/cdk-cicd-wrapper.AccessLogsForBucketPlugin",
):
    '''Plugin to enable access logs for an S3 bucket.'''

    def __init__(self) -> None:
        jsii.create(self.__class__, self, [])

    @jsii.member(jsii_name="afterStage")
    def after_stage(
        self,
        scope: _constructs_77d1e7e8.Construct,
        context: ResourceContext,
    ) -> None:
        '''The method called after the stage is created.

        :param scope: -
        :param context: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6e20db3465b69cda662c15c86df02f716061cbc07b8720551fa2bc4bd4008966)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument context", value=context, expected_type=type_hints["context"])
        return typing.cast(None, jsii.invoke(self, "afterStage", [scope, context]))

    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        '''The name of the plugin.'''
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @builtins.property
    @jsii.member(jsii_name="version")
    def version(self) -> builtins.str:
        '''The version of the plugin.'''
        return typing.cast(builtins.str, jsii.get(self, "version"))


@jsii.implements(ICIDefinition)
class BaseCIDefinition(
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdklabs/cdk-cicd-wrapper.BaseCIDefinition",
):
    def __init__(
        self,
        build_spec: _aws_cdk_aws_codebuild_ceddda9d.BuildSpec,
        *,
        build_environment: typing.Optional[typing.Union[_aws_cdk_aws_codebuild_ceddda9d.BuildEnvironment, typing.Dict[builtins.str, typing.Any]]] = None,
        cache: typing.Optional[_aws_cdk_aws_codebuild_ceddda9d.Cache] = None,
        file_system_locations: typing.Optional[typing.Sequence[_aws_cdk_aws_codebuild_ceddda9d.IFileSystemLocation]] = None,
        logging: typing.Optional[typing.Union[_aws_cdk_aws_codebuild_ceddda9d.LoggingOptions, typing.Dict[builtins.str, typing.Any]]] = None,
        partial_build_spec: typing.Optional[_aws_cdk_aws_codebuild_ceddda9d.BuildSpec] = None,
        role_policy: typing.Optional[typing.Sequence[_aws_cdk_aws_iam_ceddda9d.PolicyStatement]] = None,
        security_groups: typing.Optional[typing.Sequence[_aws_cdk_aws_ec2_ceddda9d.ISecurityGroup]] = None,
        subnet_selection: typing.Optional[typing.Union[_aws_cdk_aws_ec2_ceddda9d.SubnetSelection, typing.Dict[builtins.str, typing.Any]]] = None,
        timeout: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
        vpc: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.IVpc] = None,
    ) -> None:
        '''
        :param build_spec: -
        :param build_environment: Partial build environment, will be combined with other build environments that apply. Default: - Non-privileged build, SMALL instance, LinuxBuildImage.STANDARD_7_0
        :param cache: Caching strategy to use. Default: - No cache
        :param file_system_locations: ProjectFileSystemLocation objects for CodeBuild build projects. A ProjectFileSystemLocation object specifies the identifier, location, mountOptions, mountPoint, and type of a file system created using Amazon Elastic File System. Requires a vpc to be set and privileged to be set to true. Default: - no file system locations
        :param logging: Information about logs for CodeBuild projects. A CodeBuild project can create logs in Amazon CloudWatch Logs, an S3 bucket, or both. Default: - no log configuration is set
        :param partial_build_spec: Partial buildspec, will be combined with other buildspecs that apply. The BuildSpec must be available inline--it cannot reference a file on disk. Default: - No initial BuildSpec
        :param role_policy: Policy statements to add to role. Default: - No policy statements added to CodeBuild Project Role
        :param security_groups: Which security group(s) to associate with the project network interfaces. Only used if 'vpc' is supplied. Default: - Security group will be automatically created.
        :param subnet_selection: Which subnets to use. Only used if 'vpc' is supplied. Default: - All private subnets.
        :param timeout: The number of minutes after which AWS CodeBuild stops the build if it's not complete. For valid values, see the timeoutInMinutes field in the AWS CodeBuild User Guide. Default: Duration.hours(1)
        :param vpc: The VPC where to create the CodeBuild network interfaces in. Default: - No VPC
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__147924c72866b4c27849d07a0553fb97d12e07a5c4b00c0cbc526dd4e32730e0)
            check_type(argname="argument build_spec", value=build_spec, expected_type=type_hints["build_spec"])
        build_options = _aws_cdk_pipelines_ceddda9d.CodeBuildOptions(
            build_environment=build_environment,
            cache=cache,
            file_system_locations=file_system_locations,
            logging=logging,
            partial_build_spec=partial_build_spec,
            role_policy=role_policy,
            security_groups=security_groups,
            subnet_selection=subnet_selection,
            timeout=timeout,
            vpc=vpc,
        )

        jsii.create(self.__class__, self, [build_spec, build_options])

    @jsii.member(jsii_name="additionalPolicyStatements")
    def additional_policy_statements(
        self,
        policy_statements: typing.Sequence[_aws_cdk_aws_iam_ceddda9d.PolicyStatement],
    ) -> None:
        '''
        :param policy_statements: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5c767dd217b4b30647a569278c238dfe91636e0a122f5bd957e8425fbffad50b)
            check_type(argname="argument policy_statements", value=policy_statements, expected_type=type_hints["policy_statements"])
        return typing.cast(None, jsii.invoke(self, "additionalPolicyStatements", [policy_statements]))

    @jsii.member(jsii_name="append")
    def append(
        self,
        partial_build_spec: _aws_cdk_aws_codebuild_ceddda9d.BuildSpec,
    ) -> None:
        '''
        :param partial_build_spec: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9c794c113fa8b23b1c4ed1fc05a45fa328039d7ce3dd09f941cf35ce65129096)
            check_type(argname="argument partial_build_spec", value=partial_build_spec, expected_type=type_hints["partial_build_spec"])
        return typing.cast(None, jsii.invoke(self, "append", [partial_build_spec]))

    @jsii.member(jsii_name="appendCodeBuildOptions")
    def append_code_build_options(
        self,
        *,
        build_environment: typing.Optional[typing.Union[_aws_cdk_aws_codebuild_ceddda9d.BuildEnvironment, typing.Dict[builtins.str, typing.Any]]] = None,
        cache: typing.Optional[_aws_cdk_aws_codebuild_ceddda9d.Cache] = None,
        file_system_locations: typing.Optional[typing.Sequence[_aws_cdk_aws_codebuild_ceddda9d.IFileSystemLocation]] = None,
        logging: typing.Optional[typing.Union[_aws_cdk_aws_codebuild_ceddda9d.LoggingOptions, typing.Dict[builtins.str, typing.Any]]] = None,
        partial_build_spec: typing.Optional[_aws_cdk_aws_codebuild_ceddda9d.BuildSpec] = None,
        role_policy: typing.Optional[typing.Sequence[_aws_cdk_aws_iam_ceddda9d.PolicyStatement]] = None,
        security_groups: typing.Optional[typing.Sequence[_aws_cdk_aws_ec2_ceddda9d.ISecurityGroup]] = None,
        subnet_selection: typing.Optional[typing.Union[_aws_cdk_aws_ec2_ceddda9d.SubnetSelection, typing.Dict[builtins.str, typing.Any]]] = None,
        timeout: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
        vpc: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.IVpc] = None,
    ) -> None:
        '''
        :param build_environment: Partial build environment, will be combined with other build environments that apply. Default: - Non-privileged build, SMALL instance, LinuxBuildImage.STANDARD_7_0
        :param cache: Caching strategy to use. Default: - No cache
        :param file_system_locations: ProjectFileSystemLocation objects for CodeBuild build projects. A ProjectFileSystemLocation object specifies the identifier, location, mountOptions, mountPoint, and type of a file system created using Amazon Elastic File System. Requires a vpc to be set and privileged to be set to true. Default: - no file system locations
        :param logging: Information about logs for CodeBuild projects. A CodeBuild project can create logs in Amazon CloudWatch Logs, an S3 bucket, or both. Default: - no log configuration is set
        :param partial_build_spec: Partial buildspec, will be combined with other buildspecs that apply. The BuildSpec must be available inline--it cannot reference a file on disk. Default: - No initial BuildSpec
        :param role_policy: Policy statements to add to role. Default: - No policy statements added to CodeBuild Project Role
        :param security_groups: Which security group(s) to associate with the project network interfaces. Only used if 'vpc' is supplied. Default: - Security group will be automatically created.
        :param subnet_selection: Which subnets to use. Only used if 'vpc' is supplied. Default: - All private subnets.
        :param timeout: The number of minutes after which AWS CodeBuild stops the build if it's not complete. For valid values, see the timeoutInMinutes field in the AWS CodeBuild User Guide. Default: Duration.hours(1)
        :param vpc: The VPC where to create the CodeBuild network interfaces in. Default: - No VPC
        '''
        code_build_options = _aws_cdk_pipelines_ceddda9d.CodeBuildOptions(
            build_environment=build_environment,
            cache=cache,
            file_system_locations=file_system_locations,
            logging=logging,
            partial_build_spec=partial_build_spec,
            role_policy=role_policy,
            security_groups=security_groups,
            subnet_selection=subnet_selection,
            timeout=timeout,
            vpc=vpc,
        )

        return typing.cast(None, jsii.invoke(self, "appendCodeBuildOptions", [code_build_options]))

    @jsii.member(jsii_name="provideBuildSpec")
    def provide_build_spec(self) -> _aws_cdk_aws_codebuild_ceddda9d.BuildSpec:
        return typing.cast(_aws_cdk_aws_codebuild_ceddda9d.BuildSpec, jsii.invoke(self, "provideBuildSpec", []))

    @jsii.member(jsii_name="provideCodeBuildDefaults")
    def provide_code_build_defaults(
        self,
    ) -> _aws_cdk_pipelines_ceddda9d.CodeBuildOptions:
        return typing.cast(_aws_cdk_pipelines_ceddda9d.CodeBuildOptions, jsii.invoke(self, "provideCodeBuildDefaults", []))


@jsii.data_type(
    jsii_type="@cdklabs/cdk-cicd-wrapper.BaseRepositoryProviderProps",
    jsii_struct_bases=[RepositoryConfig],
    name_mapping={
        "branch": "branch",
        "name": "name",
        "repository_type": "repositoryType",
        "code_build_clone_output": "codeBuildCloneOutput",
        "description": "description",
        "code_guru_reviewer": "codeGuruReviewer",
        "code_star_connection_arn": "codeStarConnectionArn",
    },
)
class BaseRepositoryProviderProps(RepositoryConfig):
    def __init__(
        self,
        *,
        branch: builtins.str,
        name: builtins.str,
        repository_type: builtins.str,
        code_build_clone_output: typing.Optional[builtins.bool] = None,
        description: typing.Optional[builtins.str] = None,
        code_guru_reviewer: typing.Optional[builtins.bool] = None,
        code_star_connection_arn: typing.Optional[builtins.str] = None,
    ) -> None:
        '''Base properties for repository provider.

        :param branch: The branch for the repository.
        :param name: The name of the repository.
        :param repository_type: The type of the repository.
        :param code_build_clone_output: Enforce full clone for the repository.
        :param description: The description of the repository (optional).
        :param code_guru_reviewer: 
        :param code_star_connection_arn: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0786935eb8047679ad4ae957c1c92688fa948e80e25c84108fb1f1921638620c)
            check_type(argname="argument branch", value=branch, expected_type=type_hints["branch"])
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
            check_type(argname="argument repository_type", value=repository_type, expected_type=type_hints["repository_type"])
            check_type(argname="argument code_build_clone_output", value=code_build_clone_output, expected_type=type_hints["code_build_clone_output"])
            check_type(argname="argument description", value=description, expected_type=type_hints["description"])
            check_type(argname="argument code_guru_reviewer", value=code_guru_reviewer, expected_type=type_hints["code_guru_reviewer"])
            check_type(argname="argument code_star_connection_arn", value=code_star_connection_arn, expected_type=type_hints["code_star_connection_arn"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "branch": branch,
            "name": name,
            "repository_type": repository_type,
        }
        if code_build_clone_output is not None:
            self._values["code_build_clone_output"] = code_build_clone_output
        if description is not None:
            self._values["description"] = description
        if code_guru_reviewer is not None:
            self._values["code_guru_reviewer"] = code_guru_reviewer
        if code_star_connection_arn is not None:
            self._values["code_star_connection_arn"] = code_star_connection_arn

    @builtins.property
    def branch(self) -> builtins.str:
        '''The branch for the repository.'''
        result = self._values.get("branch")
        assert result is not None, "Required property 'branch' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def name(self) -> builtins.str:
        '''The name of the repository.'''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def repository_type(self) -> builtins.str:
        '''The type of the repository.'''
        result = self._values.get("repository_type")
        assert result is not None, "Required property 'repository_type' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def code_build_clone_output(self) -> typing.Optional[builtins.bool]:
        '''Enforce full clone for the repository.'''
        result = self._values.get("code_build_clone_output")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def description(self) -> typing.Optional[builtins.str]:
        '''The description of the repository (optional).'''
        result = self._values.get("description")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def code_guru_reviewer(self) -> typing.Optional[builtins.bool]:
        result = self._values.get("code_guru_reviewer")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def code_star_connection_arn(self) -> typing.Optional[builtins.str]:
        result = self._values.get("code_star_connection_arn")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "BaseRepositoryProviderProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.implements(IStackProvider)
class BaseStackProvider(
    metaclass=jsii.JSIIAbstractClass,
    jsii_type="@cdklabs/cdk-cicd-wrapper.BaseStackProvider",
):
    '''Abstract base class for providing stacks to a deployment pipeline.

    This class implements the IStackProvider interface and provides default implementation
    for providing deployment hook configurations (pre and post hooks) and accessing context properties.
    '''

    def __init__(self) -> None:
        jsii.create(self.__class__, self, [])

    @jsii.member(jsii_name="beforeEntryCondition")
    def _before_entry_condition(
        self,
    ) -> typing.Optional[_aws_cdk_aws_codepipeline_ceddda9d.Conditions]:
        '''Returns the conditions to be applied before the entry of this stack provider.

        :return: The conditions to be applied before entry.
        '''
        return typing.cast(typing.Optional[_aws_cdk_aws_codepipeline_ceddda9d.Conditions], jsii.invoke(self, "beforeEntryCondition", []))

    @jsii.member(jsii_name="disableTransition")
    def disable_transition(self, reason: builtins.str) -> None:
        '''
        :param reason: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d21350111e8f0af91174db10afef8f55217eaad998fd3fa8f831b3ec48a4796c)
            check_type(argname="argument reason", value=reason, expected_type=type_hints["reason"])
        return typing.cast(None, jsii.invoke(self, "disableTransition", [reason]))

    @jsii.member(jsii_name="onFailureConditions")
    def _on_failure_conditions(
        self,
    ) -> typing.Optional[_aws_cdk_aws_codepipeline_ceddda9d.FailureConditions]:
        return typing.cast(typing.Optional[_aws_cdk_aws_codepipeline_ceddda9d.FailureConditions], jsii.invoke(self, "onFailureConditions", []))

    @jsii.member(jsii_name="onSuccessConditions")
    def _on_success_conditions(
        self,
    ) -> typing.Optional[_aws_cdk_aws_codepipeline_ceddda9d.Conditions]:
        return typing.cast(typing.Optional[_aws_cdk_aws_codepipeline_ceddda9d.Conditions], jsii.invoke(self, "onSuccessConditions", []))

    @jsii.member(jsii_name="postHooks")
    def _post_hooks(self) -> typing.List[_aws_cdk_pipelines_ceddda9d.Step]:
        '''Returns the post-deployment hook steps for this stack provider.

        :return: An array of post-deployment hook steps.
        '''
        return typing.cast(typing.List[_aws_cdk_pipelines_ceddda9d.Step], jsii.invoke(self, "postHooks", []))

    @jsii.member(jsii_name="preHooks")
    def _pre_hooks(self) -> typing.List[_aws_cdk_pipelines_ceddda9d.Step]:
        '''Returns the pre-deployment hook steps for this stack provider.

        :return: An array of pre-deployment hook steps.
        '''
        return typing.cast(typing.List[_aws_cdk_pipelines_ceddda9d.Step], jsii.invoke(self, "preHooks", []))

    @jsii.member(jsii_name="provide")
    def provide(self, context: ResourceContext) -> None:
        '''Provides the deployment hook configuration for this stack provider.

        :param context: The resource context containing the scope, stage, environment, and blueprint properties.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__93749efec26f6060dadfeee523230f2893d7b4f15df00660a895c33f6aaa036f)
            check_type(argname="argument context", value=context, expected_type=type_hints["context"])
        return typing.cast(None, jsii.invoke(self, "provide", [context]))

    @jsii.member(jsii_name="resolve")
    def resolve(self, ssm_parameter_name: builtins.str) -> builtins.str:
        '''Resolves the value of an SSM parameter.

        :param ssm_parameter_name: The name of the SSM parameter to resolve.

        :return: The resolved value of the SSM parameter.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d697cdcbe532f07d04b89722be4ec6911b4b2516ffc502aba9f3652ee94e8634)
            check_type(argname="argument ssm_parameter_name", value=ssm_parameter_name, expected_type=type_hints["ssm_parameter_name"])
        return typing.cast(builtins.str, jsii.invoke(self, "resolve", [ssm_parameter_name]))

    @jsii.member(jsii_name="stacks")
    @abc.abstractmethod
    def stacks(self, context: ResourceContext) -> None:
        '''Abstract method that must be implemented by subclasses to define the stacks to be deployed.

        :param context: The resource context containing the scope, stage, environment, and blueprint properties.
        '''
        ...

    @builtins.property
    @jsii.member(jsii_name="applicationName")
    def _application_name(self) -> builtins.str:
        '''Getter for the application name.

        :return: The name of the application being deployed.
        '''
        return typing.cast(builtins.str, jsii.get(self, "applicationName"))

    @builtins.property
    @jsii.member(jsii_name="applicationQualifier")
    def _application_qualifier(self) -> builtins.str:
        '''Getter for the application qualifier.

        :return: The qualifier for the application being deployed.
        '''
        return typing.cast(builtins.str, jsii.get(self, "applicationQualifier"))

    @builtins.property
    @jsii.member(jsii_name="context")
    def _context(self) -> ResourceContext:
        '''Getter for the resource context.

        :return: The resource context containing the scope, stage, environment, and blueprint properties.
        '''
        return typing.cast(ResourceContext, jsii.get(self, "context"))

    @builtins.property
    @jsii.member(jsii_name="encryptionKey")
    def _encryption_key(self) -> _aws_cdk_aws_kms_ceddda9d.Key:
        '''Getter for the encryption key.

        :return: The encryption key used in the deployment.
        '''
        return typing.cast(_aws_cdk_aws_kms_ceddda9d.Key, jsii.get(self, "encryptionKey"))

    @builtins.property
    @jsii.member(jsii_name="env")
    def _env(self) -> _aws_cdk_ceddda9d.Environment:
        '''Getter for the deployment environment.

        :return: The deployment environment.
        '''
        return typing.cast(_aws_cdk_ceddda9d.Environment, jsii.get(self, "env"))

    @builtins.property
    @jsii.member(jsii_name="properties")
    def _properties(self) -> IPipelineConfig:
        '''Getter for the pipeline configuration properties.

        :return: The pipeline configuration properties.
        '''
        return typing.cast(IPipelineConfig, jsii.get(self, "properties"))

    @builtins.property
    @jsii.member(jsii_name="scope")
    def _scope(self) -> _constructs_77d1e7e8.Construct:
        '''Getter for the deployment scope.

        :return: The deployment scope construct.
        '''
        return typing.cast(_constructs_77d1e7e8.Construct, jsii.get(self, "scope"))

    @builtins.property
    @jsii.member(jsii_name="stageName")
    def _stage_name(self) -> builtins.str:
        '''Getter for the stage name.

        :return: The name of the deployment stage.
        '''
        return typing.cast(builtins.str, jsii.get(self, "stageName"))


class _BaseStackProviderProxy(BaseStackProvider):
    @jsii.member(jsii_name="stacks")
    def stacks(self, context: ResourceContext) -> None:
        '''Abstract method that must be implemented by subclasses to define the stacks to be deployed.

        :param context: The resource context containing the scope, stage, environment, and blueprint properties.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3d05ec817f774252beefe21c47c48d57bef1a1630540a04f30467dbd7ae53d72)
            check_type(argname="argument context", value=context, expected_type=type_hints["context"])
        return typing.cast(None, jsii.invoke(self, "stacks", [context]))

# Adding a "__jsii_proxy_class__(): typing.Type" function to the abstract class
typing.cast(typing.Any, BaseStackProvider).__jsii_proxy_class__ = lambda : _BaseStackProviderProxy


@jsii.implements(IResourceProvider)
class BasicRepositoryProvider(
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdklabs/cdk-cicd-wrapper.BasicRepositoryProvider",
):
    '''Basic implementation of repository provider.'''

    def __init__(
        self,
        *,
        code_guru_reviewer: typing.Optional[builtins.bool] = None,
        code_star_connection_arn: typing.Optional[builtins.str] = None,
        branch: builtins.str,
        name: builtins.str,
        repository_type: builtins.str,
        code_build_clone_output: typing.Optional[builtins.bool] = None,
        description: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param code_guru_reviewer: 
        :param code_star_connection_arn: 
        :param branch: The branch for the repository.
        :param name: The name of the repository.
        :param repository_type: The type of the repository.
        :param code_build_clone_output: Enforce full clone for the repository.
        :param description: The description of the repository (optional).
        '''
        config = BaseRepositoryProviderProps(
            code_guru_reviewer=code_guru_reviewer,
            code_star_connection_arn=code_star_connection_arn,
            branch=branch,
            name=name,
            repository_type=repository_type,
            code_build_clone_output=code_build_clone_output,
            description=description,
        )

        jsii.create(self.__class__, self, [config])

    @jsii.member(jsii_name="provide")
    def provide(self, context: ResourceContext) -> typing.Any:
        '''Provides a repository stack based on the configuration.

        :param context: The resource context.

        :return: The repository stack.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d9f45aee57f132f39a3dbfeafc22b558e4ef6959ec5789e3fa2ec6c8692946af)
            check_type(argname="argument context", value=context, expected_type=type_hints["context"])
        return typing.cast(typing.Any, jsii.invoke(self, "provide", [context]))

    @builtins.property
    @jsii.member(jsii_name="config")
    def config(self) -> BaseRepositoryProviderProps:
        return typing.cast(BaseRepositoryProviderProps, jsii.get(self, "config"))


@jsii.data_type(
    jsii_type="@cdklabs/cdk-cicd-wrapper.CDKPipelineProps",
    jsii_struct_bases=[PipelineProps],
    name_mapping={
        "branch": "branch",
        "ci_build_spec": "ciBuildSpec",
        "code_build_defaults": "codeBuildDefaults",
        "primary_output_directory": "primaryOutputDirectory",
        "repository_input": "repositoryInput",
        "build_image": "buildImage",
        "code_guru_scan_threshold": "codeGuruScanThreshold",
        "install_commands": "installCommands",
        "is_docker_enabled_for_synth": "isDockerEnabledForSynth",
        "options": "options",
        "pipeline_variables": "pipelineVariables",
        "synth_code_build_defaults": "synthCodeBuildDefaults",
        "vpc_props": "vpcProps",
        "application_qualifier": "applicationQualifier",
        "pipeline_name": "pipelineName",
        "role_policies": "rolePolicies",
    },
)
class CDKPipelineProps(PipelineProps):
    def __init__(
        self,
        *,
        branch: builtins.str,
        ci_build_spec: _aws_cdk_aws_codebuild_ceddda9d.BuildSpec,
        code_build_defaults: typing.Union[_aws_cdk_pipelines_ceddda9d.CodeBuildOptions, typing.Dict[builtins.str, typing.Any]],
        primary_output_directory: builtins.str,
        repository_input: _aws_cdk_pipelines_ceddda9d.IFileSetProducer,
        build_image: typing.Optional[_aws_cdk_aws_codebuild_ceddda9d.IBuildImage] = None,
        code_guru_scan_threshold: typing.Optional[CodeGuruSeverityThreshold] = None,
        install_commands: typing.Optional[typing.Sequence[builtins.str]] = None,
        is_docker_enabled_for_synth: typing.Optional[builtins.bool] = None,
        options: typing.Optional[typing.Union[PipelineOptions, typing.Dict[builtins.str, typing.Any]]] = None,
        pipeline_variables: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        synth_code_build_defaults: typing.Optional[typing.Union[_aws_cdk_pipelines_ceddda9d.CodeBuildOptions, typing.Dict[builtins.str, typing.Any]]] = None,
        vpc_props: typing.Optional[typing.Union[VpcProps, typing.Dict[builtins.str, typing.Any]]] = None,
        application_qualifier: builtins.str,
        pipeline_name: builtins.str,
        role_policies: typing.Optional[typing.Sequence[_aws_cdk_aws_iam_ceddda9d.PolicyStatement]] = None,
    ) -> None:
        '''Props for the CDKPipeline construct.

        :param branch: The branch to be used from the source repository.
        :param ci_build_spec: The CI commands to be executed as part of the Synth step.
        :param code_build_defaults: Default options for CodeBuild projects in the pipeline.
        :param primary_output_directory: The primary output directory for the synth step.
        :param repository_input: The source repository for the pipeline.
        :param build_image: The Docker image to be used for the build project.
        :param code_guru_scan_threshold: The severity threshold for CodeGuru security scans.
        :param install_commands: Additional install commands to be executed before the synth step.
        :param is_docker_enabled_for_synth: Whether Docker should be enabled for synth. Default: false
        :param options: Additional Pipeline options.
        :param pipeline_variables: Pipeline variables to be passed as environment variables.
        :param synth_code_build_defaults: Default options for the synth CodeBuild project.
        :param vpc_props: VPC configuration for the pipeline.
        :param application_qualifier: The qualifier for the application.
        :param pipeline_name: The name of the pipeline.
        :param role_policies: Additional IAM policies to be attached to the pipeline role.
        '''
        if isinstance(code_build_defaults, dict):
            code_build_defaults = _aws_cdk_pipelines_ceddda9d.CodeBuildOptions(**code_build_defaults)
        if isinstance(options, dict):
            options = PipelineOptions(**options)
        if isinstance(synth_code_build_defaults, dict):
            synth_code_build_defaults = _aws_cdk_pipelines_ceddda9d.CodeBuildOptions(**synth_code_build_defaults)
        if isinstance(vpc_props, dict):
            vpc_props = VpcProps(**vpc_props)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d620e25e0a083b43dfb5f69b1260b2072f9c44c0a626d98289867d8408743048)
            check_type(argname="argument branch", value=branch, expected_type=type_hints["branch"])
            check_type(argname="argument ci_build_spec", value=ci_build_spec, expected_type=type_hints["ci_build_spec"])
            check_type(argname="argument code_build_defaults", value=code_build_defaults, expected_type=type_hints["code_build_defaults"])
            check_type(argname="argument primary_output_directory", value=primary_output_directory, expected_type=type_hints["primary_output_directory"])
            check_type(argname="argument repository_input", value=repository_input, expected_type=type_hints["repository_input"])
            check_type(argname="argument build_image", value=build_image, expected_type=type_hints["build_image"])
            check_type(argname="argument code_guru_scan_threshold", value=code_guru_scan_threshold, expected_type=type_hints["code_guru_scan_threshold"])
            check_type(argname="argument install_commands", value=install_commands, expected_type=type_hints["install_commands"])
            check_type(argname="argument is_docker_enabled_for_synth", value=is_docker_enabled_for_synth, expected_type=type_hints["is_docker_enabled_for_synth"])
            check_type(argname="argument options", value=options, expected_type=type_hints["options"])
            check_type(argname="argument pipeline_variables", value=pipeline_variables, expected_type=type_hints["pipeline_variables"])
            check_type(argname="argument synth_code_build_defaults", value=synth_code_build_defaults, expected_type=type_hints["synth_code_build_defaults"])
            check_type(argname="argument vpc_props", value=vpc_props, expected_type=type_hints["vpc_props"])
            check_type(argname="argument application_qualifier", value=application_qualifier, expected_type=type_hints["application_qualifier"])
            check_type(argname="argument pipeline_name", value=pipeline_name, expected_type=type_hints["pipeline_name"])
            check_type(argname="argument role_policies", value=role_policies, expected_type=type_hints["role_policies"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "branch": branch,
            "ci_build_spec": ci_build_spec,
            "code_build_defaults": code_build_defaults,
            "primary_output_directory": primary_output_directory,
            "repository_input": repository_input,
            "application_qualifier": application_qualifier,
            "pipeline_name": pipeline_name,
        }
        if build_image is not None:
            self._values["build_image"] = build_image
        if code_guru_scan_threshold is not None:
            self._values["code_guru_scan_threshold"] = code_guru_scan_threshold
        if install_commands is not None:
            self._values["install_commands"] = install_commands
        if is_docker_enabled_for_synth is not None:
            self._values["is_docker_enabled_for_synth"] = is_docker_enabled_for_synth
        if options is not None:
            self._values["options"] = options
        if pipeline_variables is not None:
            self._values["pipeline_variables"] = pipeline_variables
        if synth_code_build_defaults is not None:
            self._values["synth_code_build_defaults"] = synth_code_build_defaults
        if vpc_props is not None:
            self._values["vpc_props"] = vpc_props
        if role_policies is not None:
            self._values["role_policies"] = role_policies

    @builtins.property
    def branch(self) -> builtins.str:
        '''The branch to be used from the source repository.'''
        result = self._values.get("branch")
        assert result is not None, "Required property 'branch' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def ci_build_spec(self) -> _aws_cdk_aws_codebuild_ceddda9d.BuildSpec:
        '''The CI commands to be executed as part of the Synth step.'''
        result = self._values.get("ci_build_spec")
        assert result is not None, "Required property 'ci_build_spec' is missing"
        return typing.cast(_aws_cdk_aws_codebuild_ceddda9d.BuildSpec, result)

    @builtins.property
    def code_build_defaults(self) -> _aws_cdk_pipelines_ceddda9d.CodeBuildOptions:
        '''Default options for CodeBuild projects in the pipeline.'''
        result = self._values.get("code_build_defaults")
        assert result is not None, "Required property 'code_build_defaults' is missing"
        return typing.cast(_aws_cdk_pipelines_ceddda9d.CodeBuildOptions, result)

    @builtins.property
    def primary_output_directory(self) -> builtins.str:
        '''The primary output directory for the synth step.'''
        result = self._values.get("primary_output_directory")
        assert result is not None, "Required property 'primary_output_directory' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def repository_input(self) -> _aws_cdk_pipelines_ceddda9d.IFileSetProducer:
        '''The source repository for the pipeline.'''
        result = self._values.get("repository_input")
        assert result is not None, "Required property 'repository_input' is missing"
        return typing.cast(_aws_cdk_pipelines_ceddda9d.IFileSetProducer, result)

    @builtins.property
    def build_image(
        self,
    ) -> typing.Optional[_aws_cdk_aws_codebuild_ceddda9d.IBuildImage]:
        '''The Docker image to be used for the build project.'''
        result = self._values.get("build_image")
        return typing.cast(typing.Optional[_aws_cdk_aws_codebuild_ceddda9d.IBuildImage], result)

    @builtins.property
    def code_guru_scan_threshold(self) -> typing.Optional[CodeGuruSeverityThreshold]:
        '''The severity threshold for CodeGuru security scans.'''
        result = self._values.get("code_guru_scan_threshold")
        return typing.cast(typing.Optional[CodeGuruSeverityThreshold], result)

    @builtins.property
    def install_commands(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Additional install commands to be executed before the synth step.'''
        result = self._values.get("install_commands")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def is_docker_enabled_for_synth(self) -> typing.Optional[builtins.bool]:
        '''Whether Docker should be enabled for synth.

        :default: false
        '''
        result = self._values.get("is_docker_enabled_for_synth")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def options(self) -> typing.Optional[PipelineOptions]:
        '''Additional Pipeline options.'''
        result = self._values.get("options")
        return typing.cast(typing.Optional[PipelineOptions], result)

    @builtins.property
    def pipeline_variables(
        self,
    ) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        '''Pipeline variables to be passed as environment variables.'''
        result = self._values.get("pipeline_variables")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], result)

    @builtins.property
    def synth_code_build_defaults(
        self,
    ) -> typing.Optional[_aws_cdk_pipelines_ceddda9d.CodeBuildOptions]:
        '''Default options for the synth CodeBuild project.'''
        result = self._values.get("synth_code_build_defaults")
        return typing.cast(typing.Optional[_aws_cdk_pipelines_ceddda9d.CodeBuildOptions], result)

    @builtins.property
    def vpc_props(self) -> typing.Optional[VpcProps]:
        '''VPC configuration for the pipeline.'''
        result = self._values.get("vpc_props")
        return typing.cast(typing.Optional[VpcProps], result)

    @builtins.property
    def application_qualifier(self) -> builtins.str:
        '''The qualifier for the application.'''
        result = self._values.get("application_qualifier")
        assert result is not None, "Required property 'application_qualifier' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def pipeline_name(self) -> builtins.str:
        '''The name of the pipeline.'''
        result = self._values.get("pipeline_name")
        assert result is not None, "Required property 'pipeline_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def role_policies(
        self,
    ) -> typing.Optional[typing.List[_aws_cdk_aws_iam_ceddda9d.PolicyStatement]]:
        '''Additional IAM policies to be attached to the pipeline role.'''
        result = self._values.get("role_policies")
        return typing.cast(typing.Optional[typing.List[_aws_cdk_aws_iam_ceddda9d.PolicyStatement]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CDKPipelineProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.implements(IResourceProvider)
class CIDefinitionProvider(
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdklabs/cdk-cicd-wrapper.CIDefinitionProvider",
):
    '''Provides CodeBuild BuildSpec for the Synth Step.'''

    def __init__(self) -> None:
        jsii.create(self.__class__, self, [])

    @jsii.member(jsii_name="provide")
    def provide(self, context: ResourceContext) -> typing.Any:
        '''Provides resources based on the given context.

        :param context: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__40ae53f223487f82ec30681c3f884548ce3854177854807bcbb633fc589950d5)
            check_type(argname="argument context", value=context, expected_type=type_hints["context"])
        return typing.cast(typing.Any, jsii.invoke(self, "provide", [context]))


class CodeArtifactPlugin(
    PluginBase,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdklabs/cdk-cicd-wrapper.CodeArtifactPlugin",
):
    '''Plugin to enable key rotation for KMS keys.'''

    def __init__(
        self,
        *,
        domain: builtins.str,
        repository_name: builtins.str,
        account: typing.Optional[builtins.str] = None,
        npm_scope: typing.Optional[builtins.str] = None,
        region: typing.Optional[builtins.str] = None,
        repository_types: typing.Optional[typing.Sequence[CodeArtifactRepositoryTypes]] = None,
    ) -> None:
        '''
        :param domain: 
        :param repository_name: 
        :param account: 
        :param npm_scope: 
        :param region: 
        :param repository_types: 
        '''
        options = CodeArtifactPluginProps(
            domain=domain,
            repository_name=repository_name,
            account=account,
            npm_scope=npm_scope,
            region=region,
            repository_types=repository_types,
        )

        jsii.create(self.__class__, self, [options])

    @jsii.member(jsii_name="create")
    def create(self, context: ResourceContext) -> None:
        '''The method called when the Pipeline configuration finalized.

        :param context: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__bc46d45204f1c4a5420d1b824c76ced78e236d677d5566eba693ffb24bbbe500)
            check_type(argname="argument context", value=context, expected_type=type_hints["context"])
        return typing.cast(None, jsii.invoke(self, "create", [context]))

    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        '''The name of the plugin.'''
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @builtins.property
    @jsii.member(jsii_name="version")
    def version(self) -> builtins.str:
        '''The version of the plugin.'''
        return typing.cast(builtins.str, jsii.get(self, "version"))


@jsii.implements(IResourceProvider)
class CodeBuildFactoryProvider(
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdklabs/cdk-cicd-wrapper.CodeBuildFactoryProvider",
):
    '''Provides HTTPProxy settings for the pipeline.'''

    def __init__(self) -> None:
        jsii.create(self.__class__, self, [])

    @jsii.member(jsii_name="provide")
    def provide(self, context: ResourceContext) -> typing.Any:
        '''Provides the DefaultCodeBuildFactory instance.

        :param context: The ResourceContext object containing blueprint properties and other resources.

        :return: The DefaultCodeBuildFactory instance
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2848d58e405e850d9b6dfe0b20fc027b41ccc89257e2305bc72c21d664ca9460)
            check_type(argname="argument context", value=context, expected_type=type_hints["context"])
        return typing.cast(typing.Any, jsii.invoke(self, "provide", [context]))


@jsii.data_type(
    jsii_type="@cdklabs/cdk-cicd-wrapper.CodeCommitRepositoryConstructProps",
    jsii_struct_bases=[RepositoryConfig],
    name_mapping={
        "branch": "branch",
        "name": "name",
        "repository_type": "repositoryType",
        "code_build_clone_output": "codeBuildCloneOutput",
        "description": "description",
        "application_name": "applicationName",
        "application_qualifier": "applicationQualifier",
        "pr": "pr",
    },
)
class CodeCommitRepositoryConstructProps(RepositoryConfig):
    def __init__(
        self,
        *,
        branch: builtins.str,
        name: builtins.str,
        repository_type: builtins.str,
        code_build_clone_output: typing.Optional[builtins.bool] = None,
        description: typing.Optional[builtins.str] = None,
        application_name: builtins.str,
        application_qualifier: builtins.str,
        pr: typing.Optional[typing.Union[PRCheckConfig, typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''Properties for creating a new CodeCommit repository construct.

        :param branch: The branch for the repository.
        :param name: The name of the repository.
        :param repository_type: The type of the repository.
        :param code_build_clone_output: Enforce full clone for the repository.
        :param description: The description of the repository (optional).
        :param application_name: The name of the application.
        :param application_qualifier: A qualifier for the application name.
        :param pr: Optional configuration for enabling pull request checks.
        '''
        if isinstance(pr, dict):
            pr = PRCheckConfig(**pr)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5b84906c38447fcf4014b0f405a4b327d895512ba64ea6887c7ae01fec239a61)
            check_type(argname="argument branch", value=branch, expected_type=type_hints["branch"])
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
            check_type(argname="argument repository_type", value=repository_type, expected_type=type_hints["repository_type"])
            check_type(argname="argument code_build_clone_output", value=code_build_clone_output, expected_type=type_hints["code_build_clone_output"])
            check_type(argname="argument description", value=description, expected_type=type_hints["description"])
            check_type(argname="argument application_name", value=application_name, expected_type=type_hints["application_name"])
            check_type(argname="argument application_qualifier", value=application_qualifier, expected_type=type_hints["application_qualifier"])
            check_type(argname="argument pr", value=pr, expected_type=type_hints["pr"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "branch": branch,
            "name": name,
            "repository_type": repository_type,
            "application_name": application_name,
            "application_qualifier": application_qualifier,
        }
        if code_build_clone_output is not None:
            self._values["code_build_clone_output"] = code_build_clone_output
        if description is not None:
            self._values["description"] = description
        if pr is not None:
            self._values["pr"] = pr

    @builtins.property
    def branch(self) -> builtins.str:
        '''The branch for the repository.'''
        result = self._values.get("branch")
        assert result is not None, "Required property 'branch' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def name(self) -> builtins.str:
        '''The name of the repository.'''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def repository_type(self) -> builtins.str:
        '''The type of the repository.'''
        result = self._values.get("repository_type")
        assert result is not None, "Required property 'repository_type' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def code_build_clone_output(self) -> typing.Optional[builtins.bool]:
        '''Enforce full clone for the repository.'''
        result = self._values.get("code_build_clone_output")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def description(self) -> typing.Optional[builtins.str]:
        '''The description of the repository (optional).'''
        result = self._values.get("description")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def application_name(self) -> builtins.str:
        '''The name of the application.'''
        result = self._values.get("application_name")
        assert result is not None, "Required property 'application_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def application_qualifier(self) -> builtins.str:
        '''A qualifier for the application name.'''
        result = self._values.get("application_qualifier")
        assert result is not None, "Required property 'application_qualifier' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def pr(self) -> typing.Optional[PRCheckConfig]:
        '''Optional configuration for enabling pull request checks.'''
        result = self._values.get("pr")
        return typing.cast(typing.Optional[PRCheckConfig], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CodeCommitRepositoryConstructProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class CodeCommitRepositorySource(
    RepositorySource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdklabs/cdk-cicd-wrapper.CodeCommitRepositorySource",
):
    def __init__(
        self,
        *,
        enable_code_guru_reviewer: typing.Optional[builtins.bool] = None,
        enable_pull_request_checks: typing.Optional[builtins.bool] = None,
        branch: typing.Optional[builtins.str] = None,
        code_build_clone_output: typing.Optional[builtins.bool] = None,
        description: typing.Optional[builtins.str] = None,
        repository_name: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param enable_code_guru_reviewer: Enable CodeGuru Reviewer. Default: - false
        :param enable_pull_request_checks: Enable pull request checks. Default: - true
        :param branch: The branch of the repository. Default: - 'main'
        :param code_build_clone_output: Enforce full clone for the repository. Tools like semgrep and pre-commit hooks require a full clone. Default: - false
        :param description: The description of the repository. Default: - No description.
        :param repository_name: The name of the repository. Default: - The name of the application. other options to configure: in package.json file "config": { "repositoryName": "my-repo", }
        '''
        options = CodeCommitRepositorySourceOptions(
            enable_code_guru_reviewer=enable_code_guru_reviewer,
            enable_pull_request_checks=enable_pull_request_checks,
            branch=branch,
            code_build_clone_output=code_build_clone_output,
            description=description,
            repository_name=repository_name,
        )

        jsii.create(self.__class__, self, [options])

    @jsii.member(jsii_name="produceSourceConfig")
    def produce_source_config(self, context: ResourceContext) -> IRepositoryStack:
        '''
        :param context: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3c7e75e0fcfe482753dd9afbe1d8aa1e962787966e8173daaa5498c31e88fdc4)
            check_type(argname="argument context", value=context, expected_type=type_hints["context"])
        return typing.cast(IRepositoryStack, jsii.invoke(self, "produceSourceConfig", [context]))


@jsii.data_type(
    jsii_type="@cdklabs/cdk-cicd-wrapper.CodeCommitRepositorySourceOptions",
    jsii_struct_bases=[RepositorySourceOptions],
    name_mapping={
        "branch": "branch",
        "code_build_clone_output": "codeBuildCloneOutput",
        "description": "description",
        "repository_name": "repositoryName",
        "enable_code_guru_reviewer": "enableCodeGuruReviewer",
        "enable_pull_request_checks": "enablePullRequestChecks",
    },
)
class CodeCommitRepositorySourceOptions(RepositorySourceOptions):
    def __init__(
        self,
        *,
        branch: typing.Optional[builtins.str] = None,
        code_build_clone_output: typing.Optional[builtins.bool] = None,
        description: typing.Optional[builtins.str] = None,
        repository_name: typing.Optional[builtins.str] = None,
        enable_code_guru_reviewer: typing.Optional[builtins.bool] = None,
        enable_pull_request_checks: typing.Optional[builtins.bool] = None,
    ) -> None:
        '''
        :param branch: The branch of the repository. Default: - 'main'
        :param code_build_clone_output: Enforce full clone for the repository. Tools like semgrep and pre-commit hooks require a full clone. Default: - false
        :param description: The description of the repository. Default: - No description.
        :param repository_name: The name of the repository. Default: - The name of the application. other options to configure: in package.json file "config": { "repositoryName": "my-repo", }
        :param enable_code_guru_reviewer: Enable CodeGuru Reviewer. Default: - false
        :param enable_pull_request_checks: Enable pull request checks. Default: - true
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__724a8ca2b7f125912ae200cacbb2ac8f9962c6a4e6bd4ec40c8be4aac16ae42a)
            check_type(argname="argument branch", value=branch, expected_type=type_hints["branch"])
            check_type(argname="argument code_build_clone_output", value=code_build_clone_output, expected_type=type_hints["code_build_clone_output"])
            check_type(argname="argument description", value=description, expected_type=type_hints["description"])
            check_type(argname="argument repository_name", value=repository_name, expected_type=type_hints["repository_name"])
            check_type(argname="argument enable_code_guru_reviewer", value=enable_code_guru_reviewer, expected_type=type_hints["enable_code_guru_reviewer"])
            check_type(argname="argument enable_pull_request_checks", value=enable_pull_request_checks, expected_type=type_hints["enable_pull_request_checks"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if branch is not None:
            self._values["branch"] = branch
        if code_build_clone_output is not None:
            self._values["code_build_clone_output"] = code_build_clone_output
        if description is not None:
            self._values["description"] = description
        if repository_name is not None:
            self._values["repository_name"] = repository_name
        if enable_code_guru_reviewer is not None:
            self._values["enable_code_guru_reviewer"] = enable_code_guru_reviewer
        if enable_pull_request_checks is not None:
            self._values["enable_pull_request_checks"] = enable_pull_request_checks

    @builtins.property
    def branch(self) -> typing.Optional[builtins.str]:
        '''The branch of the repository.

        :default: - 'main'
        '''
        result = self._values.get("branch")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def code_build_clone_output(self) -> typing.Optional[builtins.bool]:
        '''Enforce full clone for the repository.

        Tools like semgrep and pre-commit hooks require a full clone.

        :default: - false
        '''
        result = self._values.get("code_build_clone_output")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def description(self) -> typing.Optional[builtins.str]:
        '''The description of the repository.

        :default: - No description.
        '''
        result = self._values.get("description")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def repository_name(self) -> typing.Optional[builtins.str]:
        '''The name of the repository.

        :default:

        - The name of the application.

        other options to configure:
        in  package.json file

        "config": {
        "repositoryName": "my-repo",
        }
        '''
        result = self._values.get("repository_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def enable_code_guru_reviewer(self) -> typing.Optional[builtins.bool]:
        '''Enable CodeGuru Reviewer.

        :default: - false
        '''
        result = self._values.get("enable_code_guru_reviewer")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def enable_pull_request_checks(self) -> typing.Optional[builtins.bool]:
        '''Enable pull request checks.

        :default: - true
        '''
        result = self._values.get("enable_pull_request_checks")
        return typing.cast(typing.Optional[builtins.bool], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CodeCommitRepositorySourceOptions(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdklabs/cdk-cicd-wrapper.CodeStarConfig",
    jsii_struct_bases=[RepositoryConfig],
    name_mapping={
        "branch": "branch",
        "name": "name",
        "repository_type": "repositoryType",
        "code_build_clone_output": "codeBuildCloneOutput",
        "description": "description",
        "code_star_connection_arn": "codeStarConnectionArn",
    },
)
class CodeStarConfig(RepositoryConfig):
    def __init__(
        self,
        *,
        branch: builtins.str,
        name: builtins.str,
        repository_type: builtins.str,
        code_build_clone_output: typing.Optional[builtins.bool] = None,
        description: typing.Optional[builtins.str] = None,
        code_star_connection_arn: builtins.str,
    ) -> None:
        '''Configuration properties for the CodeStarConnectionConstruct.

        :param branch: The branch for the repository.
        :param name: The name of the repository.
        :param repository_type: The type of the repository.
        :param code_build_clone_output: Enforce full clone for the repository.
        :param description: The description of the repository (optional).
        :param code_star_connection_arn: The Amazon Resource Name (ARN) of the CodeStar connection.

        :extends: RepositoryConfig
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1326f9afc6ac1394d551fb7ae30a9bc313236ff9e699e0a6c605861c1ff2ca54)
            check_type(argname="argument branch", value=branch, expected_type=type_hints["branch"])
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
            check_type(argname="argument repository_type", value=repository_type, expected_type=type_hints["repository_type"])
            check_type(argname="argument code_build_clone_output", value=code_build_clone_output, expected_type=type_hints["code_build_clone_output"])
            check_type(argname="argument description", value=description, expected_type=type_hints["description"])
            check_type(argname="argument code_star_connection_arn", value=code_star_connection_arn, expected_type=type_hints["code_star_connection_arn"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "branch": branch,
            "name": name,
            "repository_type": repository_type,
            "code_star_connection_arn": code_star_connection_arn,
        }
        if code_build_clone_output is not None:
            self._values["code_build_clone_output"] = code_build_clone_output
        if description is not None:
            self._values["description"] = description

    @builtins.property
    def branch(self) -> builtins.str:
        '''The branch for the repository.'''
        result = self._values.get("branch")
        assert result is not None, "Required property 'branch' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def name(self) -> builtins.str:
        '''The name of the repository.'''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def repository_type(self) -> builtins.str:
        '''The type of the repository.'''
        result = self._values.get("repository_type")
        assert result is not None, "Required property 'repository_type' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def code_build_clone_output(self) -> typing.Optional[builtins.bool]:
        '''Enforce full clone for the repository.'''
        result = self._values.get("code_build_clone_output")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def description(self) -> typing.Optional[builtins.str]:
        '''The description of the repository (optional).'''
        result = self._values.get("description")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def code_star_connection_arn(self) -> builtins.str:
        '''The Amazon Resource Name (ARN) of the CodeStar connection.'''
        result = self._values.get("code_star_connection_arn")
        assert result is not None, "Required property 'code_star_connection_arn' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CodeStarConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.implements(IRepositoryStack)
class CodeStarConnectRepositoryStack(
    _aws_cdk_ceddda9d.Stack,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdklabs/cdk-cicd-wrapper.CodeStarConnectRepositoryStack",
):
    '''Stack that sets up a CodeStar connection and provides the pipeline input and environment variables.'''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        application_name: builtins.str,
        application_qualifier: builtins.str,
        analytics_reporting: typing.Optional[builtins.bool] = None,
        cross_region_references: typing.Optional[builtins.bool] = None,
        description: typing.Optional[builtins.str] = None,
        env: typing.Optional[typing.Union[_aws_cdk_ceddda9d.Environment, typing.Dict[builtins.str, typing.Any]]] = None,
        notification_arns: typing.Optional[typing.Sequence[builtins.str]] = None,
        permissions_boundary: typing.Optional[_aws_cdk_ceddda9d.PermissionsBoundary] = None,
        stack_name: typing.Optional[builtins.str] = None,
        suppress_template_indentation: typing.Optional[builtins.bool] = None,
        synthesizer: typing.Optional[_aws_cdk_ceddda9d.IStackSynthesizer] = None,
        tags: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        termination_protection: typing.Optional[builtins.bool] = None,
        code_star_connection_arn: builtins.str,
        branch: builtins.str,
        name: builtins.str,
        repository_type: builtins.str,
        code_build_clone_output: typing.Optional[builtins.bool] = None,
    ) -> None:
        '''Constructs a new instance of the CodeStarConnectRepositoryStack.

        :param scope: The scope in which the stack is created.
        :param id: The ID of the stack.
        :param application_name: The name of the application.
        :param application_qualifier: The qualifier for the application.
        :param analytics_reporting: Include runtime versioning information in this Stack. Default: ``analyticsReporting`` setting of containing ``App``, or value of 'aws:cdk:version-reporting' context key
        :param cross_region_references: Enable this flag to allow native cross region stack references. Enabling this will create a CloudFormation custom resource in both the producing stack and consuming stack in order to perform the export/import This feature is currently experimental Default: false
        :param description: A description of the stack. Default: - No description.
        :param env: The AWS environment (account/region) where this stack will be deployed. Set the ``region``/``account`` fields of ``env`` to either a concrete value to select the indicated environment (recommended for production stacks), or to the values of environment variables ``CDK_DEFAULT_REGION``/``CDK_DEFAULT_ACCOUNT`` to let the target environment depend on the AWS credentials/configuration that the CDK CLI is executed under (recommended for development stacks). If the ``Stack`` is instantiated inside a ``Stage``, any undefined ``region``/``account`` fields from ``env`` will default to the same field on the encompassing ``Stage``, if configured there. If either ``region`` or ``account`` are not set nor inherited from ``Stage``, the Stack will be considered "*environment-agnostic*"". Environment-agnostic stacks can be deployed to any environment but may not be able to take advantage of all features of the CDK. For example, they will not be able to use environmental context lookups such as ``ec2.Vpc.fromLookup`` and will not automatically translate Service Principals to the right format based on the environment's AWS partition, and other such enhancements. Default: - The environment of the containing ``Stage`` if available, otherwise create the stack will be environment-agnostic.
        :param notification_arns: SNS Topic ARNs that will receive stack events. Default: - no notfication arns.
        :param permissions_boundary: Options for applying a permissions boundary to all IAM Roles and Users created within this Stage. Default: - no permissions boundary is applied
        :param stack_name: Name to deploy the stack with. Default: - Derived from construct path.
        :param suppress_template_indentation: Enable this flag to suppress indentation in generated CloudFormation templates. If not specified, the value of the ``@aws-cdk/core:suppressTemplateIndentation`` context key will be used. If that is not specified, then the default value ``false`` will be used. Default: - the value of ``@aws-cdk/core:suppressTemplateIndentation``, or ``false`` if that is not set.
        :param synthesizer: Synthesis method to use while deploying this stack. The Stack Synthesizer controls aspects of synthesis and deployment, like how assets are referenced and what IAM roles to use. For more information, see the README of the main CDK package. If not specified, the ``defaultStackSynthesizer`` from ``App`` will be used. If that is not specified, ``DefaultStackSynthesizer`` is used if ``@aws-cdk/core:newStyleStackSynthesis`` is set to ``true`` or the CDK major version is v2. In CDK v1 ``LegacyStackSynthesizer`` is the default if no other synthesizer is specified. Default: - The synthesizer specified on ``App``, or ``DefaultStackSynthesizer`` otherwise.
        :param tags: Stack tags that will be applied to all the taggable resources and the stack itself. Default: {}
        :param termination_protection: Whether to enable termination protection for this stack. Default: false
        :param code_star_connection_arn: The Amazon Resource Name (ARN) of the CodeStar connection.
        :param branch: The branch for the repository.
        :param name: The name of the repository.
        :param repository_type: The type of the repository.
        :param code_build_clone_output: Enforce full clone for the repository.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c39fbb1da05a0f6be7186d8b68e74ecbc5ad47e74517ae1b69b180809fc3cf1a)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = CodeStarConnectRepositoryStackProps(
            application_name=application_name,
            application_qualifier=application_qualifier,
            analytics_reporting=analytics_reporting,
            cross_region_references=cross_region_references,
            description=description,
            env=env,
            notification_arns=notification_arns,
            permissions_boundary=permissions_boundary,
            stack_name=stack_name,
            suppress_template_indentation=suppress_template_indentation,
            synthesizer=synthesizer,
            tags=tags,
            termination_protection=termination_protection,
            code_star_connection_arn=code_star_connection_arn,
            branch=branch,
            name=name,
            repository_type=repository_type,
            code_build_clone_output=code_build_clone_output,
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @builtins.property
    @jsii.member(jsii_name="pipelineEnvVars")
    def pipeline_env_vars(self) -> typing.Mapping[builtins.str, builtins.str]:
        '''The environment variables to be used by the pipeline.'''
        return typing.cast(typing.Mapping[builtins.str, builtins.str], jsii.get(self, "pipelineEnvVars"))

    @builtins.property
    @jsii.member(jsii_name="pipelineInput")
    def pipeline_input(self) -> _aws_cdk_pipelines_ceddda9d.IFileSetProducer:
        '''The pipeline input (file set producer) for this stack.'''
        return typing.cast(_aws_cdk_pipelines_ceddda9d.IFileSetProducer, jsii.get(self, "pipelineInput"))

    @builtins.property
    @jsii.member(jsii_name="repositoryBranch")
    def repository_branch(self) -> builtins.str:
        '''The branch of the repository.'''
        return typing.cast(builtins.str, jsii.get(self, "repositoryBranch"))


@jsii.data_type(
    jsii_type="@cdklabs/cdk-cicd-wrapper.CodeStarConnectRepositoryStackProps",
    jsii_struct_bases=[_aws_cdk_ceddda9d.StackProps, CodeStarConfig],
    name_mapping={
        "analytics_reporting": "analyticsReporting",
        "cross_region_references": "crossRegionReferences",
        "description": "description",
        "env": "env",
        "notification_arns": "notificationArns",
        "permissions_boundary": "permissionsBoundary",
        "stack_name": "stackName",
        "suppress_template_indentation": "suppressTemplateIndentation",
        "synthesizer": "synthesizer",
        "tags": "tags",
        "termination_protection": "terminationProtection",
        "branch": "branch",
        "name": "name",
        "repository_type": "repositoryType",
        "code_build_clone_output": "codeBuildCloneOutput",
        "code_star_connection_arn": "codeStarConnectionArn",
        "application_name": "applicationName",
        "application_qualifier": "applicationQualifier",
    },
)
class CodeStarConnectRepositoryStackProps(_aws_cdk_ceddda9d.StackProps, CodeStarConfig):
    def __init__(
        self,
        *,
        analytics_reporting: typing.Optional[builtins.bool] = None,
        cross_region_references: typing.Optional[builtins.bool] = None,
        description: typing.Optional[builtins.str] = None,
        env: typing.Optional[typing.Union[_aws_cdk_ceddda9d.Environment, typing.Dict[builtins.str, typing.Any]]] = None,
        notification_arns: typing.Optional[typing.Sequence[builtins.str]] = None,
        permissions_boundary: typing.Optional[_aws_cdk_ceddda9d.PermissionsBoundary] = None,
        stack_name: typing.Optional[builtins.str] = None,
        suppress_template_indentation: typing.Optional[builtins.bool] = None,
        synthesizer: typing.Optional[_aws_cdk_ceddda9d.IStackSynthesizer] = None,
        tags: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        termination_protection: typing.Optional[builtins.bool] = None,
        branch: builtins.str,
        name: builtins.str,
        repository_type: builtins.str,
        code_build_clone_output: typing.Optional[builtins.bool] = None,
        code_star_connection_arn: builtins.str,
        application_name: builtins.str,
        application_qualifier: builtins.str,
    ) -> None:
        '''Properties for the CodeStarConnectRepositoryStack.

        :param analytics_reporting: Include runtime versioning information in this Stack. Default: ``analyticsReporting`` setting of containing ``App``, or value of 'aws:cdk:version-reporting' context key
        :param cross_region_references: Enable this flag to allow native cross region stack references. Enabling this will create a CloudFormation custom resource in both the producing stack and consuming stack in order to perform the export/import This feature is currently experimental Default: false
        :param description: The description of the repository (optional).
        :param env: The AWS environment (account/region) where this stack will be deployed. Set the ``region``/``account`` fields of ``env`` to either a concrete value to select the indicated environment (recommended for production stacks), or to the values of environment variables ``CDK_DEFAULT_REGION``/``CDK_DEFAULT_ACCOUNT`` to let the target environment depend on the AWS credentials/configuration that the CDK CLI is executed under (recommended for development stacks). If the ``Stack`` is instantiated inside a ``Stage``, any undefined ``region``/``account`` fields from ``env`` will default to the same field on the encompassing ``Stage``, if configured there. If either ``region`` or ``account`` are not set nor inherited from ``Stage``, the Stack will be considered "*environment-agnostic*"". Environment-agnostic stacks can be deployed to any environment but may not be able to take advantage of all features of the CDK. For example, they will not be able to use environmental context lookups such as ``ec2.Vpc.fromLookup`` and will not automatically translate Service Principals to the right format based on the environment's AWS partition, and other such enhancements. Default: - The environment of the containing ``Stage`` if available, otherwise create the stack will be environment-agnostic.
        :param notification_arns: SNS Topic ARNs that will receive stack events. Default: - no notfication arns.
        :param permissions_boundary: Options for applying a permissions boundary to all IAM Roles and Users created within this Stage. Default: - no permissions boundary is applied
        :param stack_name: Name to deploy the stack with. Default: - Derived from construct path.
        :param suppress_template_indentation: Enable this flag to suppress indentation in generated CloudFormation templates. If not specified, the value of the ``@aws-cdk/core:suppressTemplateIndentation`` context key will be used. If that is not specified, then the default value ``false`` will be used. Default: - the value of ``@aws-cdk/core:suppressTemplateIndentation``, or ``false`` if that is not set.
        :param synthesizer: Synthesis method to use while deploying this stack. The Stack Synthesizer controls aspects of synthesis and deployment, like how assets are referenced and what IAM roles to use. For more information, see the README of the main CDK package. If not specified, the ``defaultStackSynthesizer`` from ``App`` will be used. If that is not specified, ``DefaultStackSynthesizer`` is used if ``@aws-cdk/core:newStyleStackSynthesis`` is set to ``true`` or the CDK major version is v2. In CDK v1 ``LegacyStackSynthesizer`` is the default if no other synthesizer is specified. Default: - The synthesizer specified on ``App``, or ``DefaultStackSynthesizer`` otherwise.
        :param tags: Stack tags that will be applied to all the taggable resources and the stack itself. Default: {}
        :param termination_protection: Whether to enable termination protection for this stack. Default: false
        :param branch: The branch for the repository.
        :param name: The name of the repository.
        :param repository_type: The type of the repository.
        :param code_build_clone_output: Enforce full clone for the repository.
        :param code_star_connection_arn: The Amazon Resource Name (ARN) of the CodeStar connection.
        :param application_name: The name of the application.
        :param application_qualifier: The qualifier for the application.
        '''
        if isinstance(env, dict):
            env = _aws_cdk_ceddda9d.Environment(**env)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__35b5626df5f6ac2c68b5bf6f14bb1ad28ac054b7cf50018f01d7404a733907a2)
            check_type(argname="argument analytics_reporting", value=analytics_reporting, expected_type=type_hints["analytics_reporting"])
            check_type(argname="argument cross_region_references", value=cross_region_references, expected_type=type_hints["cross_region_references"])
            check_type(argname="argument description", value=description, expected_type=type_hints["description"])
            check_type(argname="argument env", value=env, expected_type=type_hints["env"])
            check_type(argname="argument notification_arns", value=notification_arns, expected_type=type_hints["notification_arns"])
            check_type(argname="argument permissions_boundary", value=permissions_boundary, expected_type=type_hints["permissions_boundary"])
            check_type(argname="argument stack_name", value=stack_name, expected_type=type_hints["stack_name"])
            check_type(argname="argument suppress_template_indentation", value=suppress_template_indentation, expected_type=type_hints["suppress_template_indentation"])
            check_type(argname="argument synthesizer", value=synthesizer, expected_type=type_hints["synthesizer"])
            check_type(argname="argument tags", value=tags, expected_type=type_hints["tags"])
            check_type(argname="argument termination_protection", value=termination_protection, expected_type=type_hints["termination_protection"])
            check_type(argname="argument branch", value=branch, expected_type=type_hints["branch"])
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
            check_type(argname="argument repository_type", value=repository_type, expected_type=type_hints["repository_type"])
            check_type(argname="argument code_build_clone_output", value=code_build_clone_output, expected_type=type_hints["code_build_clone_output"])
            check_type(argname="argument code_star_connection_arn", value=code_star_connection_arn, expected_type=type_hints["code_star_connection_arn"])
            check_type(argname="argument application_name", value=application_name, expected_type=type_hints["application_name"])
            check_type(argname="argument application_qualifier", value=application_qualifier, expected_type=type_hints["application_qualifier"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "branch": branch,
            "name": name,
            "repository_type": repository_type,
            "code_star_connection_arn": code_star_connection_arn,
            "application_name": application_name,
            "application_qualifier": application_qualifier,
        }
        if analytics_reporting is not None:
            self._values["analytics_reporting"] = analytics_reporting
        if cross_region_references is not None:
            self._values["cross_region_references"] = cross_region_references
        if description is not None:
            self._values["description"] = description
        if env is not None:
            self._values["env"] = env
        if notification_arns is not None:
            self._values["notification_arns"] = notification_arns
        if permissions_boundary is not None:
            self._values["permissions_boundary"] = permissions_boundary
        if stack_name is not None:
            self._values["stack_name"] = stack_name
        if suppress_template_indentation is not None:
            self._values["suppress_template_indentation"] = suppress_template_indentation
        if synthesizer is not None:
            self._values["synthesizer"] = synthesizer
        if tags is not None:
            self._values["tags"] = tags
        if termination_protection is not None:
            self._values["termination_protection"] = termination_protection
        if code_build_clone_output is not None:
            self._values["code_build_clone_output"] = code_build_clone_output

    @builtins.property
    def analytics_reporting(self) -> typing.Optional[builtins.bool]:
        '''Include runtime versioning information in this Stack.

        :default:

        ``analyticsReporting`` setting of containing ``App``, or value of
        'aws:cdk:version-reporting' context key
        '''
        result = self._values.get("analytics_reporting")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def cross_region_references(self) -> typing.Optional[builtins.bool]:
        '''Enable this flag to allow native cross region stack references.

        Enabling this will create a CloudFormation custom resource
        in both the producing stack and consuming stack in order to perform the export/import

        This feature is currently experimental

        :default: false
        '''
        result = self._values.get("cross_region_references")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def description(self) -> typing.Optional[builtins.str]:
        '''The description of the repository (optional).'''
        result = self._values.get("description")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def env(self) -> typing.Optional[_aws_cdk_ceddda9d.Environment]:
        '''The AWS environment (account/region) where this stack will be deployed.

        Set the ``region``/``account`` fields of ``env`` to either a concrete value to
        select the indicated environment (recommended for production stacks), or to
        the values of environment variables
        ``CDK_DEFAULT_REGION``/``CDK_DEFAULT_ACCOUNT`` to let the target environment
        depend on the AWS credentials/configuration that the CDK CLI is executed
        under (recommended for development stacks).

        If the ``Stack`` is instantiated inside a ``Stage``, any undefined
        ``region``/``account`` fields from ``env`` will default to the same field on the
        encompassing ``Stage``, if configured there.

        If either ``region`` or ``account`` are not set nor inherited from ``Stage``, the
        Stack will be considered "*environment-agnostic*"". Environment-agnostic
        stacks can be deployed to any environment but may not be able to take
        advantage of all features of the CDK. For example, they will not be able to
        use environmental context lookups such as ``ec2.Vpc.fromLookup`` and will not
        automatically translate Service Principals to the right format based on the
        environment's AWS partition, and other such enhancements.

        :default:

        - The environment of the containing ``Stage`` if available,
        otherwise create the stack will be environment-agnostic.

        Example::

            // Use a concrete account and region to deploy this stack to:
            // `.account` and `.region` will simply return these values.
            new Stack(app, 'Stack1', {
              env: {
                account: '123456789012',
                region: 'us-east-1'
              },
            });
            
            // Use the CLI's current credentials to determine the target environment:
            // `.account` and `.region` will reflect the account+region the CLI
            // is configured to use (based on the user CLI credentials)
            new Stack(app, 'Stack2', {
              env: {
                account: process.env.CDK_DEFAULT_ACCOUNT,
                region: process.env.CDK_DEFAULT_REGION
              },
            });
            
            // Define multiple stacks stage associated with an environment
            const myStage = new Stage(app, 'MyStage', {
              env: {
                account: '123456789012',
                region: 'us-east-1'
              }
            });
            
            // both of these stacks will use the stage's account/region:
            // `.account` and `.region` will resolve to the concrete values as above
            new MyStack(myStage, 'Stack1');
            new YourStack(myStage, 'Stack2');
            
            // Define an environment-agnostic stack:
            // `.account` and `.region` will resolve to `{ "Ref": "AWS::AccountId" }` and `{ "Ref": "AWS::Region" }` respectively.
            // which will only resolve to actual values by CloudFormation during deployment.
            new MyStack(app, 'Stack1');
        '''
        result = self._values.get("env")
        return typing.cast(typing.Optional[_aws_cdk_ceddda9d.Environment], result)

    @builtins.property
    def notification_arns(self) -> typing.Optional[typing.List[builtins.str]]:
        '''SNS Topic ARNs that will receive stack events.

        :default: - no notfication arns.
        '''
        result = self._values.get("notification_arns")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def permissions_boundary(
        self,
    ) -> typing.Optional[_aws_cdk_ceddda9d.PermissionsBoundary]:
        '''Options for applying a permissions boundary to all IAM Roles and Users created within this Stage.

        :default: - no permissions boundary is applied
        '''
        result = self._values.get("permissions_boundary")
        return typing.cast(typing.Optional[_aws_cdk_ceddda9d.PermissionsBoundary], result)

    @builtins.property
    def stack_name(self) -> typing.Optional[builtins.str]:
        '''Name to deploy the stack with.

        :default: - Derived from construct path.
        '''
        result = self._values.get("stack_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def suppress_template_indentation(self) -> typing.Optional[builtins.bool]:
        '''Enable this flag to suppress indentation in generated CloudFormation templates.

        If not specified, the value of the ``@aws-cdk/core:suppressTemplateIndentation``
        context key will be used. If that is not specified, then the
        default value ``false`` will be used.

        :default: - the value of ``@aws-cdk/core:suppressTemplateIndentation``, or ``false`` if that is not set.
        '''
        result = self._values.get("suppress_template_indentation")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def synthesizer(self) -> typing.Optional[_aws_cdk_ceddda9d.IStackSynthesizer]:
        '''Synthesis method to use while deploying this stack.

        The Stack Synthesizer controls aspects of synthesis and deployment,
        like how assets are referenced and what IAM roles to use. For more
        information, see the README of the main CDK package.

        If not specified, the ``defaultStackSynthesizer`` from ``App`` will be used.
        If that is not specified, ``DefaultStackSynthesizer`` is used if
        ``@aws-cdk/core:newStyleStackSynthesis`` is set to ``true`` or the CDK major
        version is v2. In CDK v1 ``LegacyStackSynthesizer`` is the default if no
        other synthesizer is specified.

        :default: - The synthesizer specified on ``App``, or ``DefaultStackSynthesizer`` otherwise.
        '''
        result = self._values.get("synthesizer")
        return typing.cast(typing.Optional[_aws_cdk_ceddda9d.IStackSynthesizer], result)

    @builtins.property
    def tags(self) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        '''Stack tags that will be applied to all the taggable resources and the stack itself.

        :default: {}
        '''
        result = self._values.get("tags")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], result)

    @builtins.property
    def termination_protection(self) -> typing.Optional[builtins.bool]:
        '''Whether to enable termination protection for this stack.

        :default: false
        '''
        result = self._values.get("termination_protection")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def branch(self) -> builtins.str:
        '''The branch for the repository.'''
        result = self._values.get("branch")
        assert result is not None, "Required property 'branch' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def name(self) -> builtins.str:
        '''The name of the repository.'''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def repository_type(self) -> builtins.str:
        '''The type of the repository.'''
        result = self._values.get("repository_type")
        assert result is not None, "Required property 'repository_type' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def code_build_clone_output(self) -> typing.Optional[builtins.bool]:
        '''Enforce full clone for the repository.'''
        result = self._values.get("code_build_clone_output")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def code_star_connection_arn(self) -> builtins.str:
        '''The Amazon Resource Name (ARN) of the CodeStar connection.'''
        result = self._values.get("code_star_connection_arn")
        assert result is not None, "Required property 'code_star_connection_arn' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def application_name(self) -> builtins.str:
        '''The name of the application.'''
        result = self._values.get("application_name")
        assert result is not None, "Required property 'application_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def application_qualifier(self) -> builtins.str:
        '''The qualifier for the application.'''
        result = self._values.get("application_qualifier")
        assert result is not None, "Required property 'application_qualifier' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CodeStarConnectRepositoryStackProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class CodeStarConnectionRepositorySource(
    RepositorySource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdklabs/cdk-cicd-wrapper.CodeStarConnectionRepositorySource",
):
    def __init__(
        self,
        *,
        code_star_connection_arn: typing.Optional[builtins.str] = None,
        branch: typing.Optional[builtins.str] = None,
        code_build_clone_output: typing.Optional[builtins.bool] = None,
        description: typing.Optional[builtins.str] = None,
        repository_name: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param code_star_connection_arn: The ARN of the CodeStar connection. Default: - The value of the CODESTAR_CONNECTION_ARN environment variable.
        :param branch: The branch of the repository. Default: - 'main'
        :param code_build_clone_output: Enforce full clone for the repository. Tools like semgrep and pre-commit hooks require a full clone. Default: - false
        :param description: The description of the repository. Default: - No description.
        :param repository_name: The name of the repository. Default: - The name of the application. other options to configure: in package.json file "config": { "repositoryName": "my-repo", }
        '''
        options = CodeStarConnectionRepositorySourceOptions(
            code_star_connection_arn=code_star_connection_arn,
            branch=branch,
            code_build_clone_output=code_build_clone_output,
            description=description,
            repository_name=repository_name,
        )

        jsii.create(self.__class__, self, [options])

    @jsii.member(jsii_name="produceSourceConfig")
    def produce_source_config(self, context: ResourceContext) -> IRepositoryStack:
        '''
        :param context: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4804255bea2ce295164feac477ca108fe8c328e4cb773738fb1d69a11270d5b5)
            check_type(argname="argument context", value=context, expected_type=type_hints["context"])
        return typing.cast(IRepositoryStack, jsii.invoke(self, "produceSourceConfig", [context]))


@jsii.data_type(
    jsii_type="@cdklabs/cdk-cicd-wrapper.CodeStarConnectionRepositorySourceOptions",
    jsii_struct_bases=[RepositorySourceOptions],
    name_mapping={
        "branch": "branch",
        "code_build_clone_output": "codeBuildCloneOutput",
        "description": "description",
        "repository_name": "repositoryName",
        "code_star_connection_arn": "codeStarConnectionArn",
    },
)
class CodeStarConnectionRepositorySourceOptions(RepositorySourceOptions):
    def __init__(
        self,
        *,
        branch: typing.Optional[builtins.str] = None,
        code_build_clone_output: typing.Optional[builtins.bool] = None,
        description: typing.Optional[builtins.str] = None,
        repository_name: typing.Optional[builtins.str] = None,
        code_star_connection_arn: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param branch: The branch of the repository. Default: - 'main'
        :param code_build_clone_output: Enforce full clone for the repository. Tools like semgrep and pre-commit hooks require a full clone. Default: - false
        :param description: The description of the repository. Default: - No description.
        :param repository_name: The name of the repository. Default: - The name of the application. other options to configure: in package.json file "config": { "repositoryName": "my-repo", }
        :param code_star_connection_arn: The ARN of the CodeStar connection. Default: - The value of the CODESTAR_CONNECTION_ARN environment variable.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__39757b982173f6e8faa868b6e0695e31306a24bc7802ca9986a92fd2255d1aba)
            check_type(argname="argument branch", value=branch, expected_type=type_hints["branch"])
            check_type(argname="argument code_build_clone_output", value=code_build_clone_output, expected_type=type_hints["code_build_clone_output"])
            check_type(argname="argument description", value=description, expected_type=type_hints["description"])
            check_type(argname="argument repository_name", value=repository_name, expected_type=type_hints["repository_name"])
            check_type(argname="argument code_star_connection_arn", value=code_star_connection_arn, expected_type=type_hints["code_star_connection_arn"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if branch is not None:
            self._values["branch"] = branch
        if code_build_clone_output is not None:
            self._values["code_build_clone_output"] = code_build_clone_output
        if description is not None:
            self._values["description"] = description
        if repository_name is not None:
            self._values["repository_name"] = repository_name
        if code_star_connection_arn is not None:
            self._values["code_star_connection_arn"] = code_star_connection_arn

    @builtins.property
    def branch(self) -> typing.Optional[builtins.str]:
        '''The branch of the repository.

        :default: - 'main'
        '''
        result = self._values.get("branch")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def code_build_clone_output(self) -> typing.Optional[builtins.bool]:
        '''Enforce full clone for the repository.

        Tools like semgrep and pre-commit hooks require a full clone.

        :default: - false
        '''
        result = self._values.get("code_build_clone_output")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def description(self) -> typing.Optional[builtins.str]:
        '''The description of the repository.

        :default: - No description.
        '''
        result = self._values.get("description")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def repository_name(self) -> typing.Optional[builtins.str]:
        '''The name of the repository.

        :default:

        - The name of the application.

        other options to configure:
        in  package.json file

        "config": {
        "repositoryName": "my-repo",
        }
        '''
        result = self._values.get("repository_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def code_star_connection_arn(self) -> typing.Optional[builtins.str]:
        '''The ARN of the CodeStar connection.

        :default: - The value of the CODESTAR_CONNECTION_ARN environment variable.
        '''
        result = self._values.get("code_star_connection_arn")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CodeStarConnectionRepositorySourceOptions(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.implements(IResourceProvider)
class ComplianceBucketProvider(
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdklabs/cdk-cicd-wrapper.ComplianceBucketProvider",
):
    '''Compliance bucket provider which uses existing previously created buckets.

    This class is responsible for providing a compliance bucket resource using an existing bucket.
    '''

    def __init__(self, *, run_on_vpc: typing.Optional[builtins.bool] = None) -> None:
        '''
        :param run_on_vpc: Run the Custom resource on the VPC. Default: false
        '''
        options = ComplianceBucketProviderOptions(run_on_vpc=run_on_vpc)

        jsii.create(self.__class__, self, [options])

    @jsii.member(jsii_name="provide")
    def provide(self, context: ResourceContext) -> typing.Any:
        '''Provides the compliance bucket resource based on the given context.

        :param context: The resource context containing environment information and blueprint properties.

        :return: The ComplianceLogBucketStack instance representing the compliance bucket resource.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__12917dbc84e8123087989167705cf322c6ae2663326b7b46acacf342571bbafd)
            check_type(argname="argument context", value=context, expected_type=type_hints["context"])
        return typing.cast(typing.Any, jsii.invoke(self, "provide", [context]))

    @builtins.property
    @jsii.member(jsii_name="runOnVpc")
    def run_on_vpc(self) -> builtins.bool:
        return typing.cast(builtins.bool, jsii.get(self, "runOnVpc"))

    @builtins.property
    @jsii.member(jsii_name="scope")
    def scope(self) -> typing.Optional[Scope]:
        '''The scope of the provider, which is set to PER_STAGE by default.

        This means that the provider will create a separate resource for each stage.
        '''
        return typing.cast(typing.Optional[Scope], jsii.get(self, "scope"))

    @scope.setter
    def scope(self, value: typing.Optional[Scope]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__220eb1325496b5bc5cc9cc79a36b4bccd6fa21a4fd90ee24c693f371cbcac63f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "scope", value) # pyright: ignore[reportArgumentType]


@jsii.implements(IComplianceBucket)
class ComplianceLogBucketStack(
    _aws_cdk_ceddda9d.Stack,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdklabs/cdk-cicd-wrapper.ComplianceLogBucketStack",
):
    '''Stack for creating a compliance log bucket.

    Implements the IComplianceBucketConfig interface to provide the bucket name.
    '''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        compliance_log_bucket_name: builtins.str,
        security_group: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.ISecurityGroup] = None,
        subnet_selection: typing.Optional[typing.Union[_aws_cdk_aws_ec2_ceddda9d.SubnetSelection, typing.Dict[builtins.str, typing.Any]]] = None,
        vpc: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.IVpc] = None,
        analytics_reporting: typing.Optional[builtins.bool] = None,
        cross_region_references: typing.Optional[builtins.bool] = None,
        description: typing.Optional[builtins.str] = None,
        env: typing.Optional[typing.Union[_aws_cdk_ceddda9d.Environment, typing.Dict[builtins.str, typing.Any]]] = None,
        notification_arns: typing.Optional[typing.Sequence[builtins.str]] = None,
        permissions_boundary: typing.Optional[_aws_cdk_ceddda9d.PermissionsBoundary] = None,
        stack_name: typing.Optional[builtins.str] = None,
        suppress_template_indentation: typing.Optional[builtins.bool] = None,
        synthesizer: typing.Optional[_aws_cdk_ceddda9d.IStackSynthesizer] = None,
        tags: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        termination_protection: typing.Optional[builtins.bool] = None,
    ) -> None:
        '''Constructs a new instance of the ComplianceLogBucketStack.

        :param scope: The scope in which to define this construct.
        :param id: The unique identifier for this construct.
        :param compliance_log_bucket_name: The name of the compliance log bucket to be created.
        :param security_group: The security group of the vpc.
        :param subnet_selection: The subnet selection of the vpc.
        :param vpc: The vpc where the ComplianceLogBucket CR Lambda must be attached to.
        :param analytics_reporting: Include runtime versioning information in this Stack. Default: ``analyticsReporting`` setting of containing ``App``, or value of 'aws:cdk:version-reporting' context key
        :param cross_region_references: Enable this flag to allow native cross region stack references. Enabling this will create a CloudFormation custom resource in both the producing stack and consuming stack in order to perform the export/import This feature is currently experimental Default: false
        :param description: A description of the stack. Default: - No description.
        :param env: The AWS environment (account/region) where this stack will be deployed. Set the ``region``/``account`` fields of ``env`` to either a concrete value to select the indicated environment (recommended for production stacks), or to the values of environment variables ``CDK_DEFAULT_REGION``/``CDK_DEFAULT_ACCOUNT`` to let the target environment depend on the AWS credentials/configuration that the CDK CLI is executed under (recommended for development stacks). If the ``Stack`` is instantiated inside a ``Stage``, any undefined ``region``/``account`` fields from ``env`` will default to the same field on the encompassing ``Stage``, if configured there. If either ``region`` or ``account`` are not set nor inherited from ``Stage``, the Stack will be considered "*environment-agnostic*"". Environment-agnostic stacks can be deployed to any environment but may not be able to take advantage of all features of the CDK. For example, they will not be able to use environmental context lookups such as ``ec2.Vpc.fromLookup`` and will not automatically translate Service Principals to the right format based on the environment's AWS partition, and other such enhancements. Default: - The environment of the containing ``Stage`` if available, otherwise create the stack will be environment-agnostic.
        :param notification_arns: SNS Topic ARNs that will receive stack events. Default: - no notfication arns.
        :param permissions_boundary: Options for applying a permissions boundary to all IAM Roles and Users created within this Stage. Default: - no permissions boundary is applied
        :param stack_name: Name to deploy the stack with. Default: - Derived from construct path.
        :param suppress_template_indentation: Enable this flag to suppress indentation in generated CloudFormation templates. If not specified, the value of the ``@aws-cdk/core:suppressTemplateIndentation`` context key will be used. If that is not specified, then the default value ``false`` will be used. Default: - the value of ``@aws-cdk/core:suppressTemplateIndentation``, or ``false`` if that is not set.
        :param synthesizer: Synthesis method to use while deploying this stack. The Stack Synthesizer controls aspects of synthesis and deployment, like how assets are referenced and what IAM roles to use. For more information, see the README of the main CDK package. If not specified, the ``defaultStackSynthesizer`` from ``App`` will be used. If that is not specified, ``DefaultStackSynthesizer`` is used if ``@aws-cdk/core:newStyleStackSynthesis`` is set to ``true`` or the CDK major version is v2. In CDK v1 ``LegacyStackSynthesizer`` is the default if no other synthesizer is specified. Default: - The synthesizer specified on ``App``, or ``DefaultStackSynthesizer`` otherwise.
        :param tags: Stack tags that will be applied to all the taggable resources and the stack itself. Default: {}
        :param termination_protection: Whether to enable termination protection for this stack. Default: false
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2de0d0202c5209fccc689112158e98bf084388feb7436a5ce74ae3f6bab809d4)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = ComplianceLogBucketStackProps(
            compliance_log_bucket_name=compliance_log_bucket_name,
            security_group=security_group,
            subnet_selection=subnet_selection,
            vpc=vpc,
            analytics_reporting=analytics_reporting,
            cross_region_references=cross_region_references,
            description=description,
            env=env,
            notification_arns=notification_arns,
            permissions_boundary=permissions_boundary,
            stack_name=stack_name,
            suppress_template_indentation=suppress_template_indentation,
            synthesizer=synthesizer,
            tags=tags,
            termination_protection=termination_protection,
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @jsii.member(jsii_name="createVpcConfig")
    def create_vpc_config(
        self,
    ) -> typing.Optional[typing.Mapping[typing.Any, typing.Any]]:
        return typing.cast(typing.Optional[typing.Mapping[typing.Any, typing.Any]], jsii.invoke(self, "createVpcConfig", []))

    @builtins.property
    @jsii.member(jsii_name="bucketName")
    def bucket_name(self) -> builtins.str:
        '''The name of the bucket created by this stack.'''
        return typing.cast(builtins.str, jsii.get(self, "bucketName"))

    @builtins.property
    @jsii.member(jsii_name="securityGroup")
    def security_group(
        self,
    ) -> typing.Optional[_aws_cdk_aws_ec2_ceddda9d.ISecurityGroup]:
        return typing.cast(typing.Optional[_aws_cdk_aws_ec2_ceddda9d.ISecurityGroup], jsii.get(self, "securityGroup"))

    @builtins.property
    @jsii.member(jsii_name="subnetSelection")
    def subnet_selection(
        self,
    ) -> typing.Optional[_aws_cdk_aws_ec2_ceddda9d.SubnetSelection]:
        return typing.cast(typing.Optional[_aws_cdk_aws_ec2_ceddda9d.SubnetSelection], jsii.get(self, "subnetSelection"))

    @builtins.property
    @jsii.member(jsii_name="vpc")
    def vpc(self) -> typing.Optional[_aws_cdk_aws_ec2_ceddda9d.IVpc]:
        return typing.cast(typing.Optional[_aws_cdk_aws_ec2_ceddda9d.IVpc], jsii.get(self, "vpc"))


@jsii.implements(ICodeBuildFactory)
class DefaultCodeBuildFactory(
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdklabs/cdk-cicd-wrapper.DefaultCodeBuildFactory",
):
    '''Default implementation of the ICodeBuildFactory interface Provides CodeBuild options for the pipeline, including proxy and NPM registry configurations.'''

    def __init__(
        self,
        *,
        application_qualifier: builtins.str,
        parameter_provider: IParameterConstruct,
        region: builtins.str,
        res_account: builtins.str,
        additional_role_policies: typing.Optional[typing.Sequence[_aws_cdk_aws_iam_ceddda9d.PolicyStatement]] = None,
        code_build_env_settings: typing.Optional[typing.Union[_aws_cdk_aws_codebuild_ceddda9d.BuildEnvironment, typing.Dict[builtins.str, typing.Any]]] = None,
        install_commands: typing.Optional[typing.Sequence[builtins.str]] = None,
        npm_registry: typing.Optional[typing.Union[NPMRegistryConfig, typing.Dict[builtins.str, typing.Any]]] = None,
        proxy_config: typing.Optional[IProxyConfig] = None,
        vpc: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.IVpc] = None,
    ) -> None:
        '''
        :param application_qualifier: The applicationQualifier used for the pipeline.
        :param parameter_provider: Provider for Parameter Store parameters.
        :param region: The AWS region to set.
        :param res_account: The account ID of the RES stage.
        :param additional_role_policies: Additional IAM policy statements to be added to the CodeBuild project role Default value is undefined.
        :param code_build_env_settings: Environment settings for the CodeBuild project Default value is undefined.
        :param install_commands: The install commands to run before the build phase.
        :param npm_registry: Configuration for an NPM registry Default value is undefined.
        :param proxy_config: Configuration for an HTTP proxy Default value is undefined.
        :param vpc: The VPC to use for the CodeBuild project Default value is undefined (no VPC).
        '''
        props = DefaultCodeBuildFactoryProps(
            application_qualifier=application_qualifier,
            parameter_provider=parameter_provider,
            region=region,
            res_account=res_account,
            additional_role_policies=additional_role_policies,
            code_build_env_settings=code_build_env_settings,
            install_commands=install_commands,
            npm_registry=npm_registry,
            proxy_config=proxy_config,
            vpc=vpc,
        )

        jsii.create(self.__class__, self, [props])

    @jsii.member(jsii_name="generateBuildEnvironmentVariables")
    def _generate_build_environment_variables(
        self,
        *,
        application_qualifier: builtins.str,
        parameter_provider: IParameterConstruct,
        region: builtins.str,
        res_account: builtins.str,
        additional_role_policies: typing.Optional[typing.Sequence[_aws_cdk_aws_iam_ceddda9d.PolicyStatement]] = None,
        code_build_env_settings: typing.Optional[typing.Union[_aws_cdk_aws_codebuild_ceddda9d.BuildEnvironment, typing.Dict[builtins.str, typing.Any]]] = None,
        install_commands: typing.Optional[typing.Sequence[builtins.str]] = None,
        npm_registry: typing.Optional[typing.Union[NPMRegistryConfig, typing.Dict[builtins.str, typing.Any]]] = None,
        proxy_config: typing.Optional[IProxyConfig] = None,
        vpc: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.IVpc] = None,
    ) -> typing.Mapping[builtins.str, builtins.str]:
        '''Generates build environment variables for the CodeBuild project based on the provided proxy configuration.

        :param application_qualifier: The applicationQualifier used for the pipeline.
        :param parameter_provider: Provider for Parameter Store parameters.
        :param region: The AWS region to set.
        :param res_account: The account ID of the RES stage.
        :param additional_role_policies: Additional IAM policy statements to be added to the CodeBuild project role Default value is undefined.
        :param code_build_env_settings: Environment settings for the CodeBuild project Default value is undefined.
        :param install_commands: The install commands to run before the build phase.
        :param npm_registry: Configuration for an NPM registry Default value is undefined.
        :param proxy_config: Configuration for an HTTP proxy Default value is undefined.
        :param vpc: The VPC to use for the CodeBuild project Default value is undefined (no VPC).

        :return: An object containing the build environment variables
        '''
        props = DefaultCodeBuildFactoryProps(
            application_qualifier=application_qualifier,
            parameter_provider=parameter_provider,
            region=region,
            res_account=res_account,
            additional_role_policies=additional_role_policies,
            code_build_env_settings=code_build_env_settings,
            install_commands=install_commands,
            npm_registry=npm_registry,
            proxy_config=proxy_config,
            vpc=vpc,
        )

        return typing.cast(typing.Mapping[builtins.str, builtins.str], jsii.invoke(self, "generateBuildEnvironmentVariables", [props]))

    @jsii.member(jsii_name="generateCodeBuildSecretsManager")
    def _generate_code_build_secrets_manager(
        self,
        *,
        application_qualifier: builtins.str,
        parameter_provider: IParameterConstruct,
        region: builtins.str,
        res_account: builtins.str,
        additional_role_policies: typing.Optional[typing.Sequence[_aws_cdk_aws_iam_ceddda9d.PolicyStatement]] = None,
        code_build_env_settings: typing.Optional[typing.Union[_aws_cdk_aws_codebuild_ceddda9d.BuildEnvironment, typing.Dict[builtins.str, typing.Any]]] = None,
        install_commands: typing.Optional[typing.Sequence[builtins.str]] = None,
        npm_registry: typing.Optional[typing.Union[NPMRegistryConfig, typing.Dict[builtins.str, typing.Any]]] = None,
        proxy_config: typing.Optional[IProxyConfig] = None,
        vpc: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.IVpc] = None,
    ) -> typing.Mapping[builtins.str, builtins.str]:
        '''Generates Secrets Manager values for the CodeBuild project based on the provided proxy configuration.

        :param application_qualifier: The applicationQualifier used for the pipeline.
        :param parameter_provider: Provider for Parameter Store parameters.
        :param region: The AWS region to set.
        :param res_account: The account ID of the RES stage.
        :param additional_role_policies: Additional IAM policy statements to be added to the CodeBuild project role Default value is undefined.
        :param code_build_env_settings: Environment settings for the CodeBuild project Default value is undefined.
        :param install_commands: The install commands to run before the build phase.
        :param npm_registry: Configuration for an NPM registry Default value is undefined.
        :param proxy_config: Configuration for an HTTP proxy Default value is undefined.
        :param vpc: The VPC to use for the CodeBuild project Default value is undefined (no VPC).

        :return: An object containing Secrets Manager values
        '''
        props = DefaultCodeBuildFactoryProps(
            application_qualifier=application_qualifier,
            parameter_provider=parameter_provider,
            region=region,
            res_account=res_account,
            additional_role_policies=additional_role_policies,
            code_build_env_settings=code_build_env_settings,
            install_commands=install_commands,
            npm_registry=npm_registry,
            proxy_config=proxy_config,
            vpc=vpc,
        )

        return typing.cast(typing.Mapping[builtins.str, builtins.str], jsii.invoke(self, "generateCodeBuildSecretsManager", [props]))

    @jsii.member(jsii_name="generateInstallCommands")
    def _generate_install_commands(
        self,
        *,
        application_qualifier: builtins.str,
        parameter_provider: IParameterConstruct,
        region: builtins.str,
        res_account: builtins.str,
        additional_role_policies: typing.Optional[typing.Sequence[_aws_cdk_aws_iam_ceddda9d.PolicyStatement]] = None,
        code_build_env_settings: typing.Optional[typing.Union[_aws_cdk_aws_codebuild_ceddda9d.BuildEnvironment, typing.Dict[builtins.str, typing.Any]]] = None,
        install_commands: typing.Optional[typing.Sequence[builtins.str]] = None,
        npm_registry: typing.Optional[typing.Union[NPMRegistryConfig, typing.Dict[builtins.str, typing.Any]]] = None,
        proxy_config: typing.Optional[IProxyConfig] = None,
        vpc: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.IVpc] = None,
    ) -> typing.List[builtins.str]:
        '''Generates install commands for the CodeBuild project based on the provided proxy configuration.

        :param application_qualifier: The applicationQualifier used for the pipeline.
        :param parameter_provider: Provider for Parameter Store parameters.
        :param region: The AWS region to set.
        :param res_account: The account ID of the RES stage.
        :param additional_role_policies: Additional IAM policy statements to be added to the CodeBuild project role Default value is undefined.
        :param code_build_env_settings: Environment settings for the CodeBuild project Default value is undefined.
        :param install_commands: The install commands to run before the build phase.
        :param npm_registry: Configuration for an NPM registry Default value is undefined.
        :param proxy_config: Configuration for an HTTP proxy Default value is undefined.
        :param vpc: The VPC to use for the CodeBuild project Default value is undefined (no VPC).

        :return: An array of install commands
        '''
        props = DefaultCodeBuildFactoryProps(
            application_qualifier=application_qualifier,
            parameter_provider=parameter_provider,
            region=region,
            res_account=res_account,
            additional_role_policies=additional_role_policies,
            code_build_env_settings=code_build_env_settings,
            install_commands=install_commands,
            npm_registry=npm_registry,
            proxy_config=proxy_config,
            vpc=vpc,
        )

        return typing.cast(typing.List[builtins.str], jsii.invoke(self, "generateInstallCommands", [props]))

    @jsii.member(jsii_name="generatePartialBuildSpec")
    def _generate_partial_build_spec(
        self,
        *,
        application_qualifier: builtins.str,
        parameter_provider: IParameterConstruct,
        region: builtins.str,
        res_account: builtins.str,
        additional_role_policies: typing.Optional[typing.Sequence[_aws_cdk_aws_iam_ceddda9d.PolicyStatement]] = None,
        code_build_env_settings: typing.Optional[typing.Union[_aws_cdk_aws_codebuild_ceddda9d.BuildEnvironment, typing.Dict[builtins.str, typing.Any]]] = None,
        install_commands: typing.Optional[typing.Sequence[builtins.str]] = None,
        npm_registry: typing.Optional[typing.Union[NPMRegistryConfig, typing.Dict[builtins.str, typing.Any]]] = None,
        proxy_config: typing.Optional[IProxyConfig] = None,
        vpc: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.IVpc] = None,
    ) -> _aws_cdk_aws_codebuild_ceddda9d.BuildSpec:
        '''Generates a partial CodeBuild buildspec based on the provided properties.

        :param application_qualifier: The applicationQualifier used for the pipeline.
        :param parameter_provider: Provider for Parameter Store parameters.
        :param region: The AWS region to set.
        :param res_account: The account ID of the RES stage.
        :param additional_role_policies: Additional IAM policy statements to be added to the CodeBuild project role Default value is undefined.
        :param code_build_env_settings: Environment settings for the CodeBuild project Default value is undefined.
        :param install_commands: The install commands to run before the build phase.
        :param npm_registry: Configuration for an NPM registry Default value is undefined.
        :param proxy_config: Configuration for an HTTP proxy Default value is undefined.
        :param vpc: The VPC to use for the CodeBuild project Default value is undefined (no VPC).

        :return: The partially constructed buildspec
        '''
        props = DefaultCodeBuildFactoryProps(
            application_qualifier=application_qualifier,
            parameter_provider=parameter_provider,
            region=region,
            res_account=res_account,
            additional_role_policies=additional_role_policies,
            code_build_env_settings=code_build_env_settings,
            install_commands=install_commands,
            npm_registry=npm_registry,
            proxy_config=proxy_config,
            vpc=vpc,
        )

        return typing.cast(_aws_cdk_aws_codebuild_ceddda9d.BuildSpec, jsii.invoke(self, "generatePartialBuildSpec", [props]))

    @jsii.member(jsii_name="generateRolePolicies")
    def _generate_role_policies(
        self,
        *,
        application_qualifier: builtins.str,
        parameter_provider: IParameterConstruct,
        region: builtins.str,
        res_account: builtins.str,
        additional_role_policies: typing.Optional[typing.Sequence[_aws_cdk_aws_iam_ceddda9d.PolicyStatement]] = None,
        code_build_env_settings: typing.Optional[typing.Union[_aws_cdk_aws_codebuild_ceddda9d.BuildEnvironment, typing.Dict[builtins.str, typing.Any]]] = None,
        install_commands: typing.Optional[typing.Sequence[builtins.str]] = None,
        npm_registry: typing.Optional[typing.Union[NPMRegistryConfig, typing.Dict[builtins.str, typing.Any]]] = None,
        proxy_config: typing.Optional[IProxyConfig] = None,
        vpc: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.IVpc] = None,
    ) -> typing.List[_aws_cdk_aws_iam_ceddda9d.PolicyStatement]:
        '''Generates IAM role policies for the CodeBuild project based on the provided properties.

        :param application_qualifier: The applicationQualifier used for the pipeline.
        :param parameter_provider: Provider for Parameter Store parameters.
        :param region: The AWS region to set.
        :param res_account: The account ID of the RES stage.
        :param additional_role_policies: Additional IAM policy statements to be added to the CodeBuild project role Default value is undefined.
        :param code_build_env_settings: Environment settings for the CodeBuild project Default value is undefined.
        :param install_commands: The install commands to run before the build phase.
        :param npm_registry: Configuration for an NPM registry Default value is undefined.
        :param proxy_config: Configuration for an HTTP proxy Default value is undefined.
        :param vpc: The VPC to use for the CodeBuild project Default value is undefined (no VPC).

        :return: An array of IAM policy statements
        '''
        props = DefaultCodeBuildFactoryProps(
            application_qualifier=application_qualifier,
            parameter_provider=parameter_provider,
            region=region,
            res_account=res_account,
            additional_role_policies=additional_role_policies,
            code_build_env_settings=code_build_env_settings,
            install_commands=install_commands,
            npm_registry=npm_registry,
            proxy_config=proxy_config,
            vpc=vpc,
        )

        return typing.cast(typing.List[_aws_cdk_aws_iam_ceddda9d.PolicyStatement], jsii.invoke(self, "generateRolePolicies", [props]))

    @jsii.member(jsii_name="generateVPCCodeBuildDefaults")
    def generate_vpc_code_build_defaults(
        self,
        vpc: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.IVpc] = None,
    ) -> typing.Mapping[typing.Any, typing.Any]:
        '''Generates default options for a CodeBuild project in a VPC.

        :param vpc: The VPC to use for the CodeBuild project, default is undefined (no VPC).

        :return: An object containing default options for a CodeBuild project in a VPC
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a915644e96548f8c49985ce17dcb7602e2e81454516719822ed7dd0fc868c6d7)
            check_type(argname="argument vpc", value=vpc, expected_type=type_hints["vpc"])
        return typing.cast(typing.Mapping[typing.Any, typing.Any], jsii.invoke(self, "generateVPCCodeBuildDefaults", [vpc]))

    @jsii.member(jsii_name="provideCodeBuildOptions")
    def provide_code_build_options(
        self,
    ) -> _aws_cdk_pipelines_ceddda9d.CodeBuildOptions:
        '''Provides the CodeBuild options for the pipeline.

        :return: The CodeBuildOptions object containing options for the CodeBuild project
        '''
        return typing.cast(_aws_cdk_pipelines_ceddda9d.CodeBuildOptions, jsii.invoke(self, "provideCodeBuildOptions", []))


class DefaultStackProvider(
    BaseStackProvider,
    metaclass=jsii.JSIIAbstractClass,
    jsii_type="@cdklabs/cdk-cicd-wrapper.DefaultStackProvider",
):
    '''An abstract class that extends BaseStackProvider and provides default functionality for registering and retrieving values in a stage store.'''

    def __init__(
        self,
        *,
        normalize_stack_names: typing.Optional[builtins.bool] = None,
        provider_name: typing.Optional[builtins.str] = None,
        use_application_name: typing.Optional[builtins.bool] = None,
    ) -> None:
        '''Creates a new instance of the DefaultStackProvider class.

        :param normalize_stack_names: Enable stack name normalization to replace hyphens and forward slashes. Default: false
        :param provider_name: The name of the provider.
        :param use_application_name: Indicates whether to use the application name or not. Default: false
        '''
        options = DefaultStackProviderOptions(
            normalize_stack_names=normalize_stack_names,
            provider_name=provider_name,
            use_application_name=use_application_name,
        )

        jsii.create(self.__class__, self, [options])

    @jsii.member(jsii_name="get")
    def get(self, key: builtins.str) -> typing.Any:
        '''Retrieves a value from the stage store.

        :param key: The key to retrieve the value for.

        :return: The stored value.

        :throws: {Error} If the value is not found.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ce6ce5a098480ff0d1a1c203388008c361fcc1de8159085b433019ed695eabd0)
            check_type(argname="argument key", value=key, expected_type=type_hints["key"])
        return typing.cast(typing.Any, jsii.invoke(self, "get", [key]))

    @jsii.member(jsii_name="provide")
    def provide(self, context: ResourceContext) -> None:
        '''Provides resources based on the given context.

        :param context: The resource context.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7fa3c9cfb86b42272a3d7f1966918be279e419c78daa9716a0e8d6ca14beb20e)
            check_type(argname="argument context", value=context, expected_type=type_hints["context"])
        return typing.cast(None, jsii.invoke(self, "provide", [context]))

    @jsii.member(jsii_name="register")
    def register(self, key: builtins.str, value: typing.Any) -> None:
        '''Registers a value in the stage store.

        :param key: The key to store the value under.
        :param value: The value to store.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__22a92f379c1f9445ba4bbb41f71efcddc5629f34b781303f9c1477ace2c73318)
            check_type(argname="argument key", value=key, expected_type=type_hints["key"])
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "register", [key, value]))

    @jsii.member(jsii_name="resolve")
    def resolve(self, ssm_parameter_name: builtins.str) -> builtins.str:
        '''Resolves the value of an SSM parameter.

        :param ssm_parameter_name: The name of the SSM parameter.

        :return: The resolved value of the SSM parameter.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__02ee6e1f0bd70b2378db88bb600d8149ec073b2a79027c54c6bd9f84e7f9098b)
            check_type(argname="argument ssm_parameter_name", value=ssm_parameter_name, expected_type=type_hints["ssm_parameter_name"])
        return typing.cast(builtins.str, jsii.invoke(self, "resolve", [ssm_parameter_name]))

    @builtins.property
    @jsii.member(jsii_name="scope")
    def _scope(self) -> _constructs_77d1e7e8.Construct:
        '''Returns the scope for the provider.

        :return: The provider scope.
        '''
        return typing.cast(_constructs_77d1e7e8.Construct, jsii.get(self, "scope"))

    @builtins.property
    @jsii.member(jsii_name="providerName")
    def _provider_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "providerName"))

    @_provider_name.setter
    def _provider_name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__91d483e4c682667e3f7d1b0a57ab6f835e3a24bc0bffb4b60a09c3cdff496f52)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "providerName", value) # pyright: ignore[reportArgumentType]


class _DefaultStackProviderProxy(
    DefaultStackProvider,
    jsii.proxy_for(BaseStackProvider), # type: ignore[misc]
):
    pass

# Adding a "__jsii_proxy_class__(): typing.Type" function to the abstract class
typing.cast(typing.Any, DefaultStackProvider).__jsii_proxy_class__ = lambda : _DefaultStackProviderProxy


class DestroyEncryptionKeysOnDeletePlugin(
    PluginBase,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdklabs/cdk-cicd-wrapper.DestroyEncryptionKeysOnDeletePlugin",
):
    '''Plugin to destroy encryption keys on delete.'''

    def __init__(
        self,
        stages_to_retain: typing.Optional[typing.Sequence[Stage]] = None,
    ) -> None:
        '''
        :param stages_to_retain: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__19d8a58b1e48b086e3155e9ddc9840649f85a6635efed013249ac3d74ccf63a9)
            check_type(argname="argument stages_to_retain", value=stages_to_retain, expected_type=type_hints["stages_to_retain"])
        jsii.create(self.__class__, self, [stages_to_retain])

    @jsii.member(jsii_name="afterStage")
    def after_stage(
        self,
        scope: _constructs_77d1e7e8.Construct,
        context: ResourceContext,
    ) -> None:
        '''The method called after the stage is created.

        :param scope: -
        :param context: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8358c26cfd747f2c7fe43168ac10397ebecf40fff59d497154bf4ab8e383d62a)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument context", value=context, expected_type=type_hints["context"])
        return typing.cast(None, jsii.invoke(self, "afterStage", [scope, context]))

    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        '''The name of the plugin.'''
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @builtins.property
    @jsii.member(jsii_name="stagesToRetain")
    def stages_to_retain(self) -> typing.List[Stage]:
        return typing.cast(typing.List[Stage], jsii.get(self, "stagesToRetain"))

    @builtins.property
    @jsii.member(jsii_name="version")
    def version(self) -> builtins.str:
        '''The version of the plugin.'''
        return typing.cast(builtins.str, jsii.get(self, "version"))


class DisablePublicIPAssignmentForEC2Plugin(
    PluginBase,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdklabs/cdk-cicd-wrapper.DisablePublicIPAssignmentForEC2Plugin",
):
    '''Plugin to disable public IP assignment for EC2 instances.'''

    def __init__(self) -> None:
        jsii.create(self.__class__, self, [])

    @jsii.member(jsii_name="afterStage")
    def after_stage(
        self,
        scope: _constructs_77d1e7e8.Construct,
        _: ResourceContext,
    ) -> None:
        '''The method called after the stage is created.

        :param scope: -
        :param _: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4d4edbc4bcc588d61a77bc1e5e4f4b126ebf81c93609fe668c80ac85a444e1a7)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument _", value=_, expected_type=type_hints["_"])
        return typing.cast(None, jsii.invoke(self, "afterStage", [scope, _]))

    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        '''The name of the plugin.'''
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @builtins.property
    @jsii.member(jsii_name="version")
    def version(self) -> builtins.str:
        '''The version of the plugin.'''
        return typing.cast(builtins.str, jsii.get(self, "version"))


class EncryptBucketOnTransitPlugin(
    PluginBase,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdklabs/cdk-cicd-wrapper.EncryptBucketOnTransitPlugin",
):
    '''Plugin to enforce encryption in transit for an S3 bucket.'''

    def __init__(self) -> None:
        jsii.create(self.__class__, self, [])

    @jsii.member(jsii_name="afterStage")
    def after_stage(
        self,
        scope: _constructs_77d1e7e8.Construct,
        _: ResourceContext,
    ) -> None:
        '''The method called after the stage is created.

        :param scope: -
        :param _: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__047a62344f9b1536ce8b5cfa3fd0d931c2eca2cd82bdd1814461d92ad21fb0be)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument _", value=_, expected_type=type_hints["_"])
        return typing.cast(None, jsii.invoke(self, "afterStage", [scope, _]))

    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        '''The name of the plugin.'''
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @builtins.property
    @jsii.member(jsii_name="version")
    def version(self) -> builtins.str:
        '''The version of the plugin.'''
        return typing.cast(builtins.str, jsii.get(self, "version"))


class EncryptCloudWatchLogGroupsPlugin(
    PluginBase,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdklabs/cdk-cicd-wrapper.EncryptCloudWatchLogGroupsPlugin",
):
    '''Plugin to encrypt CloudWatch Log Groups.'''

    def __init__(self) -> None:
        jsii.create(self.__class__, self, [])

    @jsii.member(jsii_name="afterStage")
    def after_stage(
        self,
        scope: _constructs_77d1e7e8.Construct,
        context: ResourceContext,
    ) -> None:
        '''The method called after the stage is created.

        :param scope: -
        :param context: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__fe160cb43bd5f12a3ca4c8d9fc854aa9058809ac0b25420ecd88e7726ce77323)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument context", value=context, expected_type=type_hints["context"])
        return typing.cast(None, jsii.invoke(self, "afterStage", [scope, context]))

    @jsii.member(jsii_name="create")
    def create(self, context: ResourceContext) -> None:
        '''The method called when the Pipeline configuration finalized.

        :param context: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__028fb517a10e173f74d514f0406278a143b5f58ed07ac0a9c7b8c2dc245d61c1)
            check_type(argname="argument context", value=context, expected_type=type_hints["context"])
        return typing.cast(None, jsii.invoke(self, "create", [context]))

    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        '''The name of the plugin.'''
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @builtins.property
    @jsii.member(jsii_name="version")
    def version(self) -> builtins.str:
        '''The version of the plugin.'''
        return typing.cast(builtins.str, jsii.get(self, "version"))


class EncryptSNSTopicOnTransitPlugin(
    PluginBase,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdklabs/cdk-cicd-wrapper.EncryptSNSTopicOnTransitPlugin",
):
    '''Plugin to enable encryption for SNS topics.'''

    def __init__(self) -> None:
        jsii.create(self.__class__, self, [])

    @jsii.member(jsii_name="afterStage")
    def after_stage(
        self,
        scope: _constructs_77d1e7e8.Construct,
        _: ResourceContext,
    ) -> None:
        '''The method called after the stage is created.

        :param scope: -
        :param _: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__669d5be1b700c984a733eea9443531988c2838ce13fb185332f986ce8d542243)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument _", value=_, expected_type=type_hints["_"])
        return typing.cast(None, jsii.invoke(self, "afterStage", [scope, _]))

    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        '''The name of the plugin.'''
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @builtins.property
    @jsii.member(jsii_name="version")
    def version(self) -> builtins.str:
        '''The version of the plugin.'''
        return typing.cast(builtins.str, jsii.get(self, "version"))


@jsii.implements(IResourceProvider)
class EncryptionProvider(
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdklabs/cdk-cicd-wrapper.EncryptionProvider",
):
    '''A provider for encryption resources that creates dedicated encryption stacks in each stage.'''

    def __init__(self) -> None:
        jsii.create(self.__class__, self, [])

    @jsii.member(jsii_name="provide")
    def provide(self, context: ResourceContext) -> typing.Any:
        '''Provides the encryption resources based on the given context.

        :param context: The resource context containing information about the current scope, blueprint properties, stage, and environment.

        :return: The EncryptionStack construct containing the encryption resources.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0540fc47da38399d846aa93316691212c809019de8e7312ff7acc9b1495bd4ff)
            check_type(argname="argument context", value=context, expected_type=type_hints["context"])
        return typing.cast(typing.Any, jsii.invoke(self, "provide", [context]))

    @builtins.property
    @jsii.member(jsii_name="scope")
    def scope(self) -> typing.Optional[Scope]:
        '''The scope in which the resource provider is available.

        Defaults to ``Scope.GLOBAL``.
        '''
        return typing.cast(typing.Optional[Scope], jsii.get(self, "scope"))

    @scope.setter
    def scope(self, value: typing.Optional[Scope]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__cb2b064ff8c3178537c895edb9e0bf06a6a1745f4df62465359709f72b9a1089)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "scope", value) # pyright: ignore[reportArgumentType]


class GitHubPipelinePlugin(
    PluginBase,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdklabs/cdk-cicd-wrapper.GitHubPipelinePlugin",
):
    def __init__(
        self,
        *,
        build_container: typing.Optional[typing.Union[_cdk_pipelines_github_fc0d05f7.ContainerOptions, typing.Dict[builtins.str, typing.Any]]] = None,
        cdk_cli_version: typing.Optional[builtins.str] = None,
        concurrency: typing.Optional[typing.Union[_cdk_pipelines_github_fc0d05f7.ConcurrencyOptions, typing.Dict[builtins.str, typing.Any]]] = None,
        docker_asset_job_settings: typing.Optional[typing.Union[_cdk_pipelines_github_fc0d05f7.DockerAssetJobSettings, typing.Dict[builtins.str, typing.Any]]] = None,
        docker_credentials: typing.Optional[typing.Sequence[_cdk_pipelines_github_fc0d05f7.DockerCredential]] = None,
        job_settings: typing.Optional[typing.Union[_cdk_pipelines_github_fc0d05f7.JobSettings, typing.Dict[builtins.str, typing.Any]]] = None,
        open_id_connect_provider_arn: typing.Optional[builtins.str] = None,
        post_build_steps: typing.Optional[typing.Sequence[typing.Union[_cdk_pipelines_github_fc0d05f7.JobStep, typing.Dict[builtins.str, typing.Any]]]] = None,
        pre_build_steps: typing.Optional[typing.Sequence[typing.Union[_cdk_pipelines_github_fc0d05f7.JobStep, typing.Dict[builtins.str, typing.Any]]]] = None,
        pre_synthed: typing.Optional[builtins.bool] = None,
        publish_assets_auth_region: typing.Optional[builtins.str] = None,
        repository_name: typing.Optional[builtins.str] = None,
        role_name: typing.Optional[builtins.str] = None,
        runner: typing.Optional[_cdk_pipelines_github_fc0d05f7.Runner] = None,
        subject_claims: typing.Optional[typing.Sequence[builtins.str]] = None,
        thumbprints: typing.Optional[typing.Sequence[builtins.str]] = None,
        workflow_name: typing.Optional[builtins.str] = None,
        workflow_path: typing.Optional[builtins.str] = None,
        workflow_triggers: typing.Optional[typing.Union[_cdk_pipelines_github_fc0d05f7.WorkflowTriggers, typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''
        :param build_container: Build container options. Default: - GitHub defaults
        :param cdk_cli_version: Version of the CDK CLI to use. Default: - automatic
        :param concurrency: GitHub workflow concurrency. Default: - no concurrency settings
        :param docker_asset_job_settings: Job level settings applied to all docker asset publishing jobs in the workflow. Default: - no additional settings
        :param docker_credentials: The Docker Credentials to use to login. If you set this variable, you will be logged in to docker when you upload Docker Assets.
        :param job_settings: Job level settings that will be applied to all jobs in the workflow, including synth and asset deploy jobs. Currently the only valid setting is 'if'. You can use this to run jobs only in specific repositories.
        :param open_id_connect_provider_arn: 
        :param post_build_steps: GitHub workflow steps to execute after build. Default: []
        :param pre_build_steps: GitHub workflow steps to execute before build. Default: []
        :param pre_synthed: Indicates if the repository already contains a synthesized ``cdk.out`` directory, in which case we will simply checkout the repo in jobs that require ``cdk.out``. Default: false
        :param publish_assets_auth_region: Will assume the GitHubActionRole in this region when publishing assets. This is NOT the region in which the assets are published. In most cases, you do not have to worry about this property, and can safely ignore it. Default: "us-west-2"
        :param repository_name: 
        :param role_name: 
        :param runner: The type of runner to run the job on. The runner can be either a GitHub-hosted runner or a self-hosted runner. Default: Runner.UBUNTU_LATEST
        :param subject_claims: A list of subject claims allowed to access the IAM role. See https://docs.github.com/en/actions/deployment/security-hardening-your-deployments/about-security-hardening-with-openid-connect A subject claim can include ``*`` and ``?`` wildcards according to the ``StringLike`` condition operator. For example, ``['repo:owner/repo1:ref:refs/heads/branch1', 'repo:owner/repo1:environment:prod']``
        :param thumbprints: Thumbprints of GitHub's certificates. Every time GitHub rotates their certificates, this value will need to be updated. Default value is up-to-date to June 27, 2023 as per https://github.blog/changelog/2023-06-27-github-actions-update-on-oidc-integration-with-aws/ Default: - Use built-in keys
        :param workflow_name: Name of the workflow. Default: "deploy"
        :param workflow_path: File path for the GitHub workflow. Default: ".github/workflows/deploy.yml"
        :param workflow_triggers: GitHub workflow triggers. Default: - By default, workflow is triggered on push to the ``main`` branch and can also be triggered manually (``workflow_dispatch``).
        '''
        options = GitHubPipelinePluginOptions(
            build_container=build_container,
            cdk_cli_version=cdk_cli_version,
            concurrency=concurrency,
            docker_asset_job_settings=docker_asset_job_settings,
            docker_credentials=docker_credentials,
            job_settings=job_settings,
            open_id_connect_provider_arn=open_id_connect_provider_arn,
            post_build_steps=post_build_steps,
            pre_build_steps=pre_build_steps,
            pre_synthed=pre_synthed,
            publish_assets_auth_region=publish_assets_auth_region,
            repository_name=repository_name,
            role_name=role_name,
            runner=runner,
            subject_claims=subject_claims,
            thumbprints=thumbprints,
            workflow_name=workflow_name,
            workflow_path=workflow_path,
            workflow_triggers=workflow_triggers,
        )

        jsii.create(self.__class__, self, [options])

    @jsii.member(jsii_name="create")
    def create(self, context: ResourceContext) -> None:
        '''The method called when the Pipeline configuration finalized.

        :param context: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c1080415412bd6e7b2504d0411274a849872efcb7c3901ccf9aa16146de22f4b)
            check_type(argname="argument context", value=context, expected_type=type_hints["context"])
        return typing.cast(None, jsii.invoke(self, "create", [context]))

    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        '''The name of the plugin.'''
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @builtins.property
    @jsii.member(jsii_name="version")
    def version(self) -> builtins.str:
        '''The version of the plugin.'''
        return typing.cast(builtins.str, jsii.get(self, "version"))


@jsii.implements(IResourceProvider)
class HookProvider(
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdklabs/cdk-cicd-wrapper.HookProvider",
):
    def __init__(self) -> None:
        jsii.create(self.__class__, self, [])

    @jsii.member(jsii_name="provide")
    def provide(self, _: ResourceContext) -> typing.Any:
        '''Provides resources based on the given context.

        :param _: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__827a764561f31950abeb68084c9028591d15c18dbb0a2187b65a519aff70867a)
            check_type(argname="argument _", value=_, expected_type=type_hints["_"])
        return typing.cast(typing.Any, jsii.invoke(self, "provide", [_]))

    @builtins.property
    @jsii.member(jsii_name="scope")
    def scope(self) -> typing.Optional[Scope]:
        '''The scope in which the resource provider is available.

        Defaults to ``Scope.GLOBAL``.
        '''
        return typing.cast(typing.Optional[Scope], jsii.get(self, "scope"))

    @scope.setter
    def scope(self, value: typing.Optional[Scope]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7c12bda7dc1c95ff1a70f98683618c7eea0656f0c17c7a0647dcc347b6399a1c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "scope", value) # pyright: ignore[reportArgumentType]


@jsii.implements(IResourceProvider)
class HttpProxyProvider(
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdklabs/cdk-cicd-wrapper.HttpProxyProvider",
):
    '''Provides HTTPProxy settings for the pipeline.'''

    def __init__(self, proxy: typing.Optional[IProxyConfig] = None) -> None:
        '''Creates a new instance of the HttpProxyProvider class.

        :param proxy: The proxy configuration. If not provided, the default configuration will be used.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ecc53ad44cbcc0f50d405beb52281fa83322ff4a33577168b4604a3d83fe50c1)
            check_type(argname="argument proxy", value=proxy, expected_type=type_hints["proxy"])
        jsii.create(self.__class__, self, [proxy])

    @jsii.member(jsii_name="provide")
    def provide(self, context: ResourceContext) -> typing.Any:
        '''Provides the proxy configuration for the pipeline.

        :param context: The resource context.

        :return: The proxy configuration.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__df10f7ff5493bafbe8f8f8dca717218594fbf22a76fa4b494cfdb381710e909c)
            check_type(argname="argument context", value=context, expected_type=type_hints["context"])
        return typing.cast(typing.Any, jsii.invoke(self, "provide", [context]))

    @builtins.property
    @jsii.member(jsii_name="proxy")
    def proxy(self) -> IProxyConfig:
        '''The proxy configuration.

        If not provided, the default configuration will be used.
        '''
        return typing.cast(IProxyConfig, jsii.get(self, "proxy"))


@jsii.interface(jsii_type="@cdklabs/cdk-cicd-wrapper.IPipelineBlueprintProps")
class IPipelineBlueprintProps(IPipelineConfig, typing_extensions.Protocol):
    '''Interface for Pipeline Blueprint configuration properties.'''

    @builtins.property
    @jsii.member(jsii_name="plugins")
    def plugins(self) -> typing.Mapping[builtins.str, IPlugin]:
        '''The plugins configured for the pipeline.'''
        ...

    @plugins.setter
    def plugins(self, value: typing.Mapping[builtins.str, IPlugin]) -> None:
        ...

    @builtins.property
    @jsii.member(jsii_name="resourceProviders")
    def resource_providers(self) -> typing.Mapping[builtins.str, IResourceProvider]:
        '''Named resource providers to leverage for cluster resources.

        The resource can represent Vpc, Hosting Zones or other resources, see {@link spi.ResourceType }.
        VPC for the cluster can be registered under the name of 'vpc' or as a single provider of type
        '''
        ...

    @resource_providers.setter
    def resource_providers(
        self,
        value: typing.Mapping[builtins.str, IResourceProvider],
    ) -> None:
        ...


class _IPipelineBlueprintPropsProxy(
    jsii.proxy_for(IPipelineConfig), # type: ignore[misc]
):
    '''Interface for Pipeline Blueprint configuration properties.'''

    __jsii_type__: typing.ClassVar[str] = "@cdklabs/cdk-cicd-wrapper.IPipelineBlueprintProps"

    @builtins.property
    @jsii.member(jsii_name="plugins")
    def plugins(self) -> typing.Mapping[builtins.str, IPlugin]:
        '''The plugins configured for the pipeline.'''
        return typing.cast(typing.Mapping[builtins.str, IPlugin], jsii.get(self, "plugins"))

    @plugins.setter
    def plugins(self, value: typing.Mapping[builtins.str, IPlugin]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0d334a5c6d5a97a3af61d05ad5a6d5c5f9b605704f1c2a8eaaddcaef4db4fd73)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "plugins", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="resourceProviders")
    def resource_providers(self) -> typing.Mapping[builtins.str, IResourceProvider]:
        '''Named resource providers to leverage for cluster resources.

        The resource can represent Vpc, Hosting Zones or other resources, see {@link spi.ResourceType }.
        VPC for the cluster can be registered under the name of 'vpc' or as a single provider of type
        '''
        return typing.cast(typing.Mapping[builtins.str, IResourceProvider], jsii.get(self, "resourceProviders"))

    @resource_providers.setter
    def resource_providers(
        self,
        value: typing.Mapping[builtins.str, IResourceProvider],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__337cfe2eae32578f1f1b4c1bb33ff5a3aabc56d4881314c8658ef235f6e15e9e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "resourceProviders", value) # pyright: ignore[reportArgumentType]

# Adding a "__jsii_proxy_class__(): typing.Type" function to the interface
typing.cast(typing.Any, IPipelineBlueprintProps).__jsii_proxy_class__ = lambda : _IPipelineBlueprintPropsProxy


class LambdaDLQPlugin(
    PluginBase,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdklabs/cdk-cicd-wrapper.LambdaDLQPlugin",
):
    def __init__(self, props: typing.Optional[ILambdaDLQPluginProps] = None) -> None:
        '''
        :param props: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d7fa09ea6358c5696485e0b2589ab8f938310242e6dc708bf485c7f9bcd7867a)
            check_type(argname="argument props", value=props, expected_type=type_hints["props"])
        jsii.create(self.__class__, self, [props])

    @jsii.member(jsii_name="afterStage")
    def after_stage(
        self,
        scope: _constructs_77d1e7e8.Construct,
        context: ResourceContext,
    ) -> None:
        '''The method called after the stage is created.

        :param scope: -
        :param context: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5d5a045ea22c85dd4513115acec16db15622b1cde47c7ddae0b7eeb3c22f3796)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument context", value=context, expected_type=type_hints["context"])
        return typing.cast(None, jsii.invoke(self, "afterStage", [scope, context]))

    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        '''The name of the plugin.'''
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @builtins.property
    @jsii.member(jsii_name="retentionPeriod")
    def retention_period(self) -> _aws_cdk_ceddda9d.Duration:
        return typing.cast(_aws_cdk_ceddda9d.Duration, jsii.get(self, "retentionPeriod"))

    @builtins.property
    @jsii.member(jsii_name="version")
    def version(self) -> builtins.str:
        '''The version of the plugin.'''
        return typing.cast(builtins.str, jsii.get(self, "version"))


__all__ = [
    "AccessLogsForBucketPlugin",
    "AddStageOpts",
    "AppStage",
    "AppStageProps",
    "BaseCIDefinition",
    "BaseRepositoryProviderProps",
    "BaseStackProvider",
    "BasicRepositoryProvider",
    "BuildOptions",
    "CDKPipeline",
    "CDKPipelineProps",
    "CIDefinitionProvider",
    "CodeArtifactPlugin",
    "CodeArtifactPluginProps",
    "CodeArtifactRepositoryTypes",
    "CodeBuildFactoryProvider",
    "CodeCommitRepositoryConstruct",
    "CodeCommitRepositoryConstructProps",
    "CodeCommitRepositorySource",
    "CodeCommitRepositorySourceOptions",
    "CodeGuruSeverityThreshold",
    "CodeStarConfig",
    "CodeStarConnectRepositoryStack",
    "CodeStarConnectRepositoryStackProps",
    "CodeStarConnectionConstruct",
    "CodeStarConnectionRepositorySource",
    "CodeStarConnectionRepositorySourceOptions",
    "ComplianceBucketProvider",
    "ComplianceBucketProviderOptions",
    "ComplianceLogBucketStack",
    "ComplianceLogBucketStackProps",
    "DefaultCodeBuildFactory",
    "DefaultCodeBuildFactoryProps",
    "DefaultStackProvider",
    "DefaultStackProviderOptions",
    "DeploymentDefinition",
    "DeploymentHookConfig",
    "DestroyEncryptionKeysOnDeletePlugin",
    "DisablePublicIPAssignmentForEC2Plugin",
    "EncryptBucketOnTransitPlugin",
    "EncryptCloudWatchLogGroupsPlugin",
    "EncryptSNSTopicOnTransitPlugin",
    "EncryptionProvider",
    "EncryptionStack",
    "EncryptionStackProps",
    "Environment",
    "GitHubPipelinePlugin",
    "GitHubPipelinePluginOptions",
    "GlobalResources",
    "Hook",
    "HookProvider",
    "HttpProxyProvider",
    "ICIDefinition",
    "ICodeBuildFactory",
    "IComplianceBucket",
    "IDeploymentHookConfigProvider",
    "IEncryptionKey",
    "ILambdaDLQPluginProps",
    "ILogger",
    "IManagedVpcConfig",
    "IParameterConstruct",
    "IPhaseCommand",
    "IPhaseCommandSettings",
    "IPipelineBlueprintProps",
    "IPipelineConfig",
    "IPipelinePhases",
    "IPlugin",
    "IProxyConfig",
    "IRepositoryStack",
    "IResourceProvider",
    "IStackProvider",
    "IStageConfig",
    "IStageDefinition",
    "IVpcConfig",
    "IVpcConfigFromLookUp",
    "IVpcConstruct",
    "InlineShellPhaseCommand",
    "LambdaDLQPlugin",
    "LoggingProvider",
    "ManagedVPCStack",
    "ManagedVPCStackProps",
    "NPMPhaseCommand",
    "NPMRegistryConfig",
    "NoVPCStack",
    "PRCheckConfig",
    "ParameterProvider",
    "ParameterResolver",
    "PhaseCommandProvider",
    "PipelineBlueprint",
    "PipelineBlueprintBuilder",
    "PipelineOptions",
    "PipelinePhases",
    "PipelineProps",
    "PluginBase",
    "Plugins",
    "PostDeployBuildStep",
    "PostDeployExecutorStack",
    "PostDeployExecutorStackProps",
    "PreDeployBuildStep",
    "ProxyProps",
    "PythonPhaseCommand",
    "RepositoryConfig",
    "RepositorySource",
    "RepositorySourceOptions",
    "ResourceContext",
    "RotateEncryptionKeysPlugin",
    "RuntimeVersionOptions",
    "S3RepositorySource",
    "S3RepositorySourceOptions",
    "SSMParameterStack",
    "SSMParameterStackProps",
    "Scope",
    "ShellCommandPhaseCommand",
    "ShellScriptPhaseCommand",
    "Stage",
    "StageProvider",
    "VPCFromLookUpStack",
    "VPCFromLookUpStackProps",
    "VPCProvider",
    "VpcProps",
    "WorkbenchConfig",
    "WorkbenchOptions",
]

publication.publish()

def _typecheckingstub__fcc51638b65f56e1cec2fe849b835e401809055e38ebabeda2276f1ed766fe16(
    *,
    post: typing.Optional[typing.Sequence[_aws_cdk_pipelines_ceddda9d.Step]] = None,
    pre: typing.Optional[typing.Sequence[_aws_cdk_pipelines_ceddda9d.Step]] = None,
    stack_steps: typing.Optional[typing.Sequence[typing.Union[_aws_cdk_pipelines_ceddda9d.StackSteps, typing.Dict[builtins.str, typing.Any]]]] = None,
    before_entry: typing.Optional[typing.Union[_aws_cdk_aws_codepipeline_ceddda9d.Conditions, typing.Dict[builtins.str, typing.Any]]] = None,
    on_failure: typing.Optional[typing.Union[_aws_cdk_aws_codepipeline_ceddda9d.FailureConditions, typing.Dict[builtins.str, typing.Any]]] = None,
    on_success: typing.Optional[typing.Union[_aws_cdk_aws_codepipeline_ceddda9d.Conditions, typing.Dict[builtins.str, typing.Any]]] = None,
    transition_disabled_reason: typing.Optional[builtins.str] = None,
    transition_to_enabled: typing.Optional[builtins.bool] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__77654defeaf3698a9aadb8849bbb10f6cdf215c08f96e4208e74f268a4647f53(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    env: typing.Optional[typing.Union[_aws_cdk_ceddda9d.Environment, typing.Dict[builtins.str, typing.Any]]] = None,
    outdir: typing.Optional[builtins.str] = None,
    permissions_boundary: typing.Optional[_aws_cdk_ceddda9d.PermissionsBoundary] = None,
    policy_validation_beta1: typing.Optional[typing.Sequence[_aws_cdk_ceddda9d.IPolicyValidationPluginBeta1]] = None,
    stage_name: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8cf96545be51eec6264fb0287e08c9badf0113db4c6d6cb6b85879bba5bfac78(
    reason: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__268d48de282b6f8137f8c004fc74599cd87b57ce07891625172bb54fd640c1b4(
    *,
    env: typing.Optional[typing.Union[_aws_cdk_ceddda9d.Environment, typing.Dict[builtins.str, typing.Any]]] = None,
    outdir: typing.Optional[builtins.str] = None,
    permissions_boundary: typing.Optional[_aws_cdk_ceddda9d.PermissionsBoundary] = None,
    policy_validation_beta1: typing.Optional[typing.Sequence[_aws_cdk_ceddda9d.IPolicyValidationPluginBeta1]] = None,
    stage_name: typing.Optional[builtins.str] = None,
    context: ResourceContext,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__feab7d5c7f161a2021e30e139c542a8cd7ed813103cd0ffc4280adedcb2ce429(
    *,
    code_build_defaults: typing.Optional[typing.Union[_aws_cdk_pipelines_ceddda9d.CodeBuildOptions, typing.Dict[builtins.str, typing.Any]]] = None,
    run_time_versions: typing.Optional[typing.Union[RuntimeVersionOptions, typing.Dict[builtins.str, typing.Any]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__99bfefc0b03a54a957572378463c1ece234bab54b79ba7eaa99c7f9d7034a4e5(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    application_qualifier: builtins.str,
    pipeline_name: builtins.str,
    role_policies: typing.Optional[typing.Sequence[_aws_cdk_aws_iam_ceddda9d.PolicyStatement]] = None,
    branch: builtins.str,
    ci_build_spec: _aws_cdk_aws_codebuild_ceddda9d.BuildSpec,
    code_build_defaults: typing.Union[_aws_cdk_pipelines_ceddda9d.CodeBuildOptions, typing.Dict[builtins.str, typing.Any]],
    primary_output_directory: builtins.str,
    repository_input: _aws_cdk_pipelines_ceddda9d.IFileSetProducer,
    build_image: typing.Optional[_aws_cdk_aws_codebuild_ceddda9d.IBuildImage] = None,
    code_guru_scan_threshold: typing.Optional[CodeGuruSeverityThreshold] = None,
    install_commands: typing.Optional[typing.Sequence[builtins.str]] = None,
    is_docker_enabled_for_synth: typing.Optional[builtins.bool] = None,
    options: typing.Optional[typing.Union[PipelineOptions, typing.Dict[builtins.str, typing.Any]]] = None,
    pipeline_variables: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
    synth_code_build_defaults: typing.Optional[typing.Union[_aws_cdk_pipelines_ceddda9d.CodeBuildOptions, typing.Dict[builtins.str, typing.Any]]] = None,
    vpc_props: typing.Optional[typing.Union[VpcProps, typing.Dict[builtins.str, typing.Any]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e306cc57ea84dcf20fb796679fd0a84b1178f92467322896b08f88a7962453dd(
    stage: _aws_cdk_ceddda9d.Stage,
    *,
    before_entry: typing.Optional[typing.Union[_aws_cdk_aws_codepipeline_ceddda9d.Conditions, typing.Dict[builtins.str, typing.Any]]] = None,
    on_failure: typing.Optional[typing.Union[_aws_cdk_aws_codepipeline_ceddda9d.FailureConditions, typing.Dict[builtins.str, typing.Any]]] = None,
    on_success: typing.Optional[typing.Union[_aws_cdk_aws_codepipeline_ceddda9d.Conditions, typing.Dict[builtins.str, typing.Any]]] = None,
    transition_disabled_reason: typing.Optional[builtins.str] = None,
    transition_to_enabled: typing.Optional[builtins.bool] = None,
    post: typing.Optional[typing.Sequence[_aws_cdk_pipelines_ceddda9d.Step]] = None,
    pre: typing.Optional[typing.Sequence[_aws_cdk_pipelines_ceddda9d.Step]] = None,
    stack_steps: typing.Optional[typing.Sequence[typing.Union[_aws_cdk_pipelines_ceddda9d.StackSteps, typing.Dict[builtins.str, typing.Any]]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4d291da8d58e12fa244bd82f53b17eeb5979e60f82bd74fd6b25150552161ae0(
    *,
    domain: builtins.str,
    repository_name: builtins.str,
    account: typing.Optional[builtins.str] = None,
    npm_scope: typing.Optional[builtins.str] = None,
    region: typing.Optional[builtins.str] = None,
    repository_types: typing.Optional[typing.Sequence[CodeArtifactRepositoryTypes]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ee6b85606ca87dcdfd0961983691019b43620792a1e43f832a4f4be34e01ced8(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    application_name: builtins.str,
    application_qualifier: builtins.str,
    pr: typing.Optional[typing.Union[PRCheckConfig, typing.Dict[builtins.str, typing.Any]]] = None,
    branch: builtins.str,
    name: builtins.str,
    repository_type: builtins.str,
    code_build_clone_output: typing.Optional[builtins.bool] = None,
    description: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3bdb055e914f501dcd1f46d960aba1897f20cabc108a50ab9c44dca3b5d8e445(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    code_star_connection_arn: builtins.str,
    branch: builtins.str,
    name: builtins.str,
    repository_type: builtins.str,
    code_build_clone_output: typing.Optional[builtins.bool] = None,
    description: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6e76287addf40fe1e284454aa367bd1be88653807a3626bb749d72809b390b85(
    *,
    run_on_vpc: typing.Optional[builtins.bool] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9d486671678cc2237ca4931916d6e48bdaa0ac31591dcbe5f31ac3d5b64a7e4a(
    *,
    analytics_reporting: typing.Optional[builtins.bool] = None,
    cross_region_references: typing.Optional[builtins.bool] = None,
    description: typing.Optional[builtins.str] = None,
    env: typing.Optional[typing.Union[_aws_cdk_ceddda9d.Environment, typing.Dict[builtins.str, typing.Any]]] = None,
    notification_arns: typing.Optional[typing.Sequence[builtins.str]] = None,
    permissions_boundary: typing.Optional[_aws_cdk_ceddda9d.PermissionsBoundary] = None,
    stack_name: typing.Optional[builtins.str] = None,
    suppress_template_indentation: typing.Optional[builtins.bool] = None,
    synthesizer: typing.Optional[_aws_cdk_ceddda9d.IStackSynthesizer] = None,
    tags: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
    termination_protection: typing.Optional[builtins.bool] = None,
    compliance_log_bucket_name: builtins.str,
    security_group: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.ISecurityGroup] = None,
    subnet_selection: typing.Optional[typing.Union[_aws_cdk_aws_ec2_ceddda9d.SubnetSelection, typing.Dict[builtins.str, typing.Any]]] = None,
    vpc: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.IVpc] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__bff0f10e7606a0a87c519b6fcae1d08c136a64f8d8e54d9f80b5e2a05af96b56(
    *,
    application_qualifier: builtins.str,
    parameter_provider: IParameterConstruct,
    region: builtins.str,
    res_account: builtins.str,
    additional_role_policies: typing.Optional[typing.Sequence[_aws_cdk_aws_iam_ceddda9d.PolicyStatement]] = None,
    code_build_env_settings: typing.Optional[typing.Union[_aws_cdk_aws_codebuild_ceddda9d.BuildEnvironment, typing.Dict[builtins.str, typing.Any]]] = None,
    install_commands: typing.Optional[typing.Sequence[builtins.str]] = None,
    npm_registry: typing.Optional[typing.Union[NPMRegistryConfig, typing.Dict[builtins.str, typing.Any]]] = None,
    proxy_config: typing.Optional[IProxyConfig] = None,
    vpc: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.IVpc] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__879d91301c994b130bf98b102f5dbef2d7de3db448d53f91e484a57446966c75(
    *,
    normalize_stack_names: typing.Optional[builtins.bool] = None,
    provider_name: typing.Optional[builtins.str] = None,
    use_application_name: typing.Optional[builtins.bool] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__999876a0c3379f5aa69e4245b2f46b1895daf317efa1aeff5757edbdc3e84312(
    *,
    env: typing.Union[Environment, typing.Dict[builtins.str, typing.Any]],
    manual_approval_required: builtins.bool,
    stacks_providers: typing.Sequence[IStackProvider],
    compliance_log_bucket_name: typing.Optional[builtins.str] = None,
    vpc: typing.Optional[IVpcConfig] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__aac68b76c52f782b91345396d1418c376cefb2aa1f8cb3220a139f1350630c8d(
    *,
    post: typing.Optional[typing.Sequence[_aws_cdk_pipelines_ceddda9d.Step]] = None,
    pre: typing.Optional[typing.Sequence[_aws_cdk_pipelines_ceddda9d.Step]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__38c7f4fd3ab929f5ee80acccce8dc16c2fd2df647519d109ca1eabfae51e8751(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    application_name: builtins.str,
    stage_name: builtins.str,
    analytics_reporting: typing.Optional[builtins.bool] = None,
    cross_region_references: typing.Optional[builtins.bool] = None,
    description: typing.Optional[builtins.str] = None,
    env: typing.Optional[typing.Union[_aws_cdk_ceddda9d.Environment, typing.Dict[builtins.str, typing.Any]]] = None,
    notification_arns: typing.Optional[typing.Sequence[builtins.str]] = None,
    permissions_boundary: typing.Optional[_aws_cdk_ceddda9d.PermissionsBoundary] = None,
    stack_name: typing.Optional[builtins.str] = None,
    suppress_template_indentation: typing.Optional[builtins.bool] = None,
    synthesizer: typing.Optional[_aws_cdk_ceddda9d.IStackSynthesizer] = None,
    tags: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
    termination_protection: typing.Optional[builtins.bool] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__bf3596ec2168345e555b782e9234fda57f79681275af693c143827db9f54dcce(
    *,
    analytics_reporting: typing.Optional[builtins.bool] = None,
    cross_region_references: typing.Optional[builtins.bool] = None,
    description: typing.Optional[builtins.str] = None,
    env: typing.Optional[typing.Union[_aws_cdk_ceddda9d.Environment, typing.Dict[builtins.str, typing.Any]]] = None,
    notification_arns: typing.Optional[typing.Sequence[builtins.str]] = None,
    permissions_boundary: typing.Optional[_aws_cdk_ceddda9d.PermissionsBoundary] = None,
    stack_name: typing.Optional[builtins.str] = None,
    suppress_template_indentation: typing.Optional[builtins.bool] = None,
    synthesizer: typing.Optional[_aws_cdk_ceddda9d.IStackSynthesizer] = None,
    tags: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
    termination_protection: typing.Optional[builtins.bool] = None,
    application_name: builtins.str,
    stage_name: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__16ab79c02fa419c536c6e7e716bb6a0e3c1e64d99da80fae59f90884f09827a1(
    *,
    account: builtins.str,
    region: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a6ec7da65576fb7c11b896d62212c5d7433b3776f713753d7800049328a9fb62(
    *,
    build_container: typing.Optional[typing.Union[_cdk_pipelines_github_fc0d05f7.ContainerOptions, typing.Dict[builtins.str, typing.Any]]] = None,
    cdk_cli_version: typing.Optional[builtins.str] = None,
    concurrency: typing.Optional[typing.Union[_cdk_pipelines_github_fc0d05f7.ConcurrencyOptions, typing.Dict[builtins.str, typing.Any]]] = None,
    docker_asset_job_settings: typing.Optional[typing.Union[_cdk_pipelines_github_fc0d05f7.DockerAssetJobSettings, typing.Dict[builtins.str, typing.Any]]] = None,
    docker_credentials: typing.Optional[typing.Sequence[_cdk_pipelines_github_fc0d05f7.DockerCredential]] = None,
    job_settings: typing.Optional[typing.Union[_cdk_pipelines_github_fc0d05f7.JobSettings, typing.Dict[builtins.str, typing.Any]]] = None,
    open_id_connect_provider_arn: typing.Optional[builtins.str] = None,
    post_build_steps: typing.Optional[typing.Sequence[typing.Union[_cdk_pipelines_github_fc0d05f7.JobStep, typing.Dict[builtins.str, typing.Any]]]] = None,
    pre_build_steps: typing.Optional[typing.Sequence[typing.Union[_cdk_pipelines_github_fc0d05f7.JobStep, typing.Dict[builtins.str, typing.Any]]]] = None,
    pre_synthed: typing.Optional[builtins.bool] = None,
    publish_assets_auth_region: typing.Optional[builtins.str] = None,
    repository_name: typing.Optional[builtins.str] = None,
    role_name: typing.Optional[builtins.str] = None,
    runner: typing.Optional[_cdk_pipelines_github_fc0d05f7.Runner] = None,
    subject_claims: typing.Optional[typing.Sequence[builtins.str]] = None,
    thumbprints: typing.Optional[typing.Sequence[builtins.str]] = None,
    workflow_name: typing.Optional[builtins.str] = None,
    workflow_path: typing.Optional[builtins.str] = None,
    workflow_triggers: typing.Optional[typing.Union[_cdk_pipelines_github_fc0d05f7.WorkflowTriggers, typing.Dict[builtins.str, typing.Any]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5e2b9bc3c52f053417c3721aa8305630c0720cf192c9323d73d9be0bc289fbfd(
    hook: _aws_cdk_pipelines_ceddda9d.Step,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f73a1ba7c6489e87fc48407aba8b61e9c0e5a5f93e4092cc322069e7f2c5dd66(
    hook: _aws_cdk_pipelines_ceddda9d.Step,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8ca7176508a22cb3577a93b4645cf33b04614c2dc3248b61d34b176dac90562c(
    policy_statements: typing.Sequence[_aws_cdk_aws_iam_ceddda9d.PolicyStatement],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3a34c635ac1e3f9a8abe9d73266c9e37b01209f16085b0e3b8175b8ef1b549e9(
    partial_build_spec: _aws_cdk_aws_codebuild_ceddda9d.BuildSpec,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4e38b5a9769ad5e10befcdb5f024343ce008d3d7cf81d6fed1986e7f4b9e9ba2(
    hook: _aws_cdk_pipelines_ceddda9d.Step,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0a60bb57fecf6818ab286e39d1a1d3e6f4aff613aa3ff7fc917a9fbebc54a7c2(
    hook: _aws_cdk_pipelines_ceddda9d.Step,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__77be351f74bdc1d9aa8d3b24592f69235ed8c7b3b241a48df933f1a0b25f3d9a(
    value: typing.Optional[_aws_cdk_ceddda9d.Duration],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__542e1655521dfb9d0015022e610e443ae7a3cab28a1954b773273bc7f4c802e7(
    message: builtins.str,
    on: typing.Optional[_constructs_77d1e7e8.IConstruct] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3318d9da2949330eb99da5d1d63de125d49cb94b4d896faae8cedc4fa560becf(
    message: builtins.str,
    on: typing.Optional[_constructs_77d1e7e8.IConstruct] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e17d7ae556b313f3fd1389a85e577e38787f8cd2d7f76d0adedc932d0c838443(
    message: builtins.str,
    on: typing.Optional[_constructs_77d1e7e8.IConstruct] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__50a2cc20300c757258682193b62ea04043ea0368b9031fa5eccb8b785ffd73fc(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2cb3175d7f2fc722b6ad91b7a384bd93f61754432ba397bb1b90b464f20fe1fa(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__17da2a9a1c9b7838abc12539c72e276d381f752d01c5ca6d3326ce372ab8c70b(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5fee80111a77172c533d99c1978fc9affa7ad9185f9969ba4c8a2c0624a9abdc(
    parameter_name: builtins.str,
    parameter_value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9827465564253a29afb24e4bd204809318dd1f35375199c9e6b05f3fb9ef64b0(
    *phases: PipelinePhases,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ac21a8ef1a621af75f9fab526106bbceb4aefa596dcfc4e0232123329d831c72(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7fe8c9486db1a4fee462a7e9cd2567bb977e4a3d40b6693b74ecef1fec175938(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__82c7ae901f54587ddb19d2d4a3daca6a3842def49e2e1da1d6edd8f9b954f9fd(
    value: _aws_cdk_aws_codebuild_ceddda9d.BuildEnvironment,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8dc5710d462f0e42105a4b72c65820f51a4c9f0b668ac3e2eb01fb0081afa90a(
    value: typing.Mapping[builtins.str, DeploymentDefinition],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d6be3e88255ba58405c48da5f4389446b865e3b5457e8f98dbea9c7b8c98167d(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__30669fd3818c6b466c688d5608bfeb950055e0227f66dd176c5554c2ff065d87(
    value: IPipelinePhases,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ec731bcac61bf306eb4427799ffc86a8f892b71d643afffa11bc02d90434d58b(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__526bfd98bbde27a6d1545002d8d91bb55a8f10596cf8df91996c097469154ebb(
    value: typing.Optional[BuildOptions],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3c056af3b7aac401e23c5be3a1c6d9eea34bb543add73eef7c6d5d7afa32d6ba(
    value: typing.Optional[_aws_cdk_aws_codebuild_ceddda9d.BuildSpec],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9bd62c07b36992dacbf46dcfedad6ad0d0cd1528ff4b2f31927e25d5537a2a02(
    value: typing.Optional[CodeGuruSeverityThreshold],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3c082033088fdf175de944baef880cfbf7fca7751fa7a5a18dbb95b0b4ada9bb(
    value: typing.Optional[NPMRegistryConfig],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5ebc5edfa8c4cd954d295925b9c796bb6a5456ce28520c943bc3a389a777c112(
    value: typing.Optional[PipelineOptions],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__20f19231b8487de7ecb479bd9371b34eb7ef6551bd840b1646bf463e07f3916b(
    value: typing.Optional[RepositorySource],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e9574ab90d10366386281cc97183ea9a6f0a5443ec34916ceb7bc4ddb933f36d(
    value: typing.Optional[WorkbenchConfig],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1452e71847823a6e2646dca9a540f47256b2312d6d4623405a93404e5e19c776(
    value: typing.Optional[typing.List[IPhaseCommand]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3900856b9fd1866808653d0e68254a2f33a82ce094368d16049583ba0692bf85(
    value: typing.Optional[typing.List[IPhaseCommand]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__795369e6a94c2a8ef896db52ec821e6100dc66a54fc858db52f22771f37bdc0b(
    value: typing.Optional[typing.List[IPhaseCommand]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__274d7cac8ee21a62e3c54506d377d90d81b683bfa5c6c598f4d22afa3488704f(
    value: typing.Optional[typing.List[IPhaseCommand]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a025d8e732e84f8b766b536c39242e4d3fe88ba835679bff9beebce34ec7e478(
    value: typing.Optional[typing.List[IPhaseCommand]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a0676eef9c1c4648a6480b76bd9b555e8d9355db5a8d8a21f9c7d82dabddf50f(
    value: typing.Optional[typing.List[IPhaseCommand]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b54c4e8eb6f3938b81207e513aa93d587c0e2aee5261debf5c4cede5b3385534(
    scope: _constructs_77d1e7e8.Construct,
    context: ResourceContext,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__82244cc4dc2cff3aadc9fc4456862f35c41f0e4afe338270aa6892f6b7fdfe30(
    scope: _constructs_77d1e7e8.Construct,
    context: ResourceContext,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__68c5b356d31650cf6c7b3fd5811af6fe87e079f3e59edf5b48908c8fa08af0d8(
    context: ResourceContext,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9a6b3845b744da23ba38e1b6281e204353917bb487cc52023ade063112f9f59f(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1131a520d2dc76a1bcfbaed53b1f95afaff9ac3a65961418dfdebc191897adb6(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__64426f347056475ac5a95fc546ed489ca1146101a69b1a55bddf6f2324795ef5(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c3cdeb8d8e912d222a6a0c078ddbd381679a36ef6e9af3d179d5b759d3e067a4(
    value: typing.Optional[Scope],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__022ec6359bf8623c4688f9a50b7ac61d91f90bf6874c5425473c5b2e8526d5e6(
    context: ResourceContext,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__aa2e2be5ef472df4931cbf5b7c7b1c429d3de6bc51a4f31d378667667b6b598b(
    context: ResourceContext,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__38774dcd02360477515624272bb81ed33fde51cf44e30ab3dab6ba31840e7d75(
    value: typing.Optional[_aws_cdk_aws_codepipeline_ceddda9d.Conditions],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__45fd062d2880c7d2f6a1339fd957b3bfc14fefdd7dc4212484f5704b7884509e(
    value: typing.Optional[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5ea7872f6e9107d85d053109eb71cf88244ac183e0b4c7d0a4a79492013efba5(
    value: typing.Optional[_aws_cdk_aws_codepipeline_ceddda9d.FailureConditions],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ec27f4d1d4b5c451583b18ecdc4f7645813837553c1ed57a8b7786aa67b2387e(
    value: typing.Optional[_aws_cdk_aws_codepipeline_ceddda9d.Conditions],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__95ec8494f3439f66a2953a04cee921364792a9dc940a239466f2ef996bced85b(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3de0f4e2f3f3f2d0d4fe396ca29e13a0b1727e4721a10ba572b451ce4f2b2ac6(
    value: typing.Optional[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e32989d7e98737acefdbff60d9cc3a0dae0380f19178903630855bb1c6cd6cc2(
    value: typing.Optional[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__20898bda8dea3f7e774078abf74a8bd5cdd475e8e8d4998a22ece9a810e9b725(
    value: typing.Optional[builtins.bool],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__43102f4878e00fc0dd939f2392c826be08b7313d7caa5f66fbbb908dbd1c6464(
    value: typing.Optional[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__aeaa3fd6d391d0d5c2e15332c12810a36da3a2e6c30cd8264446e59e33564d7f(
    value: typing.Optional[IVpcConfig],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ab276d5122a044b23e9a26a526006e8a580af461cf59ea71bd212b6444ffa1ef(
    value: typing.Optional[IManagedVpcConfig],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__cd4ef4e2430712868b0ef23708e30fbe0a8c75850d90e986240da922508be24c(
    value: typing.Optional[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1e61264f328af5c22ce14b5c05013f702dacb0a3b71318edaec256b8018905df(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__29e06bf649dc4df088c99ff0722bc663c408c8bca362dd5e0f006df462e3089d(
    script: builtins.str,
    export_environment: typing.Optional[builtins.bool] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c3cbcac597367da9bcc590c7f19f8e3f7ec75f4e364dfd1590f44bd6da78ef45(
    _: ResourceContext,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__70b0ba31b33d549518a53cba5e179a3e44bdf4061c06fc504716cb5bc90cb540(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    cidr_block: builtins.str,
    max_azs: jsii.Number,
    subnet_cidr_mask: jsii.Number,
    use_proxy: builtins.bool,
    allow_all_outbound: typing.Optional[builtins.bool] = None,
    code_build_vpc_interfaces: typing.Optional[typing.Sequence[_aws_cdk_aws_ec2_ceddda9d.InterfaceVpcEndpointAwsService]] = None,
    flow_logs_bucket_name: typing.Optional[builtins.str] = None,
    restrict_default_security_group: typing.Optional[builtins.bool] = None,
    subnet_type: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.SubnetType] = None,
    analytics_reporting: typing.Optional[builtins.bool] = None,
    cross_region_references: typing.Optional[builtins.bool] = None,
    description: typing.Optional[builtins.str] = None,
    env: typing.Optional[typing.Union[_aws_cdk_ceddda9d.Environment, typing.Dict[builtins.str, typing.Any]]] = None,
    notification_arns: typing.Optional[typing.Sequence[builtins.str]] = None,
    permissions_boundary: typing.Optional[_aws_cdk_ceddda9d.PermissionsBoundary] = None,
    stack_name: typing.Optional[builtins.str] = None,
    suppress_template_indentation: typing.Optional[builtins.bool] = None,
    synthesizer: typing.Optional[_aws_cdk_ceddda9d.IStackSynthesizer] = None,
    tags: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
    termination_protection: typing.Optional[builtins.bool] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__00467d891c9ffdaeb9151b3e4a44fcdfddb5230c8d6204f2f1b47147423de751(
    *,
    analytics_reporting: typing.Optional[builtins.bool] = None,
    cross_region_references: typing.Optional[builtins.bool] = None,
    description: typing.Optional[builtins.str] = None,
    env: typing.Optional[typing.Union[_aws_cdk_ceddda9d.Environment, typing.Dict[builtins.str, typing.Any]]] = None,
    notification_arns: typing.Optional[typing.Sequence[builtins.str]] = None,
    permissions_boundary: typing.Optional[_aws_cdk_ceddda9d.PermissionsBoundary] = None,
    stack_name: typing.Optional[builtins.str] = None,
    suppress_template_indentation: typing.Optional[builtins.bool] = None,
    synthesizer: typing.Optional[_aws_cdk_ceddda9d.IStackSynthesizer] = None,
    tags: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
    termination_protection: typing.Optional[builtins.bool] = None,
    cidr_block: builtins.str,
    max_azs: jsii.Number,
    subnet_cidr_mask: jsii.Number,
    use_proxy: builtins.bool,
    allow_all_outbound: typing.Optional[builtins.bool] = None,
    code_build_vpc_interfaces: typing.Optional[typing.Sequence[_aws_cdk_aws_ec2_ceddda9d.InterfaceVpcEndpointAwsService]] = None,
    flow_logs_bucket_name: typing.Optional[builtins.str] = None,
    restrict_default_security_group: typing.Optional[builtins.bool] = None,
    subnet_type: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.SubnetType] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__db1030ec2131c2e10ada4ffc3ffa92947ac2264b0db04034128174f579f8a1b4(
    script: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b332a03f5cb108af1680ca9f1bb11e08566078c9d97d3aaa9446b3d9b353d466(
    *,
    basic_auth_secret_arn: builtins.str,
    url: builtins.str,
    scope: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c426a119773ac893377d5c58bb29ad5dff6d05abbe71ea3c6591cfd4e44e56a2(
    *,
    build_spec: _aws_cdk_aws_codebuild_ceddda9d.BuildSpec,
    code_build_options: typing.Union[_aws_cdk_pipelines_ceddda9d.CodeBuildOptions, typing.Dict[builtins.str, typing.Any]],
    code_guru_reviewer: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__58d1b1a41267fdc1330544a8fa0937f6e4a0846a56edb48b7b143e3522060932(
    context: ResourceContext,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__88247bee6ba65673ff953f8e7aa6ed1b590a24428384be6dc7c4f7be5a895cc0(
    scope: _constructs_77d1e7e8.Construct,
    param: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2d23320659531364ab50aa4e68cbf0b2eaee552337a74166d327cf86e8c02a08(
    context: ResourceContext,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8d9fa55a35936fc5427ea6cb97e35399c50fe9d7c910859f9325155c91d04b3d(
    props: typing.Optional[IPipelineBlueprintProps] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e3932058d67c1f681d71d3c13f355b985131f752dc26b4907512e65c2359eba8(
    stack_provider: IStackProvider,
    *stages: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0fbe70885993bed3b7e4d20588d3470d2821b2c4a1447d580bac812acd2543be(
    application_name: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__043e03cfcd8bedbdcdb5977d825377a84d25dbbb3d90b3447afbc51874ef4916(
    application_qualifier: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f43a53c89998dc50496696797391217d7f77f7fb8cad74dd75af4ba8a8d18417(
    build_spec: _aws_cdk_aws_codebuild_ceddda9d.BuildSpec,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e66bc7dbb5d232627bdc5724d0e458258fe989d96f52ce58d4544b808cafaf7b(
    file_path: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__dd06b480eec7ac0f096afa8e2f9d8ac3762d239ff97e71c7fcf51b8a4db15a75(
    code_guru_scan_threshold: CodeGuruSeverityThreshold,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__888c0a8d309e0cd70d56652ee163dc6eb42c31955347584a681d25195430b863(
    phase: PipelinePhases,
    commands_to_execute: typing.Sequence[IPhaseCommand],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1a25e970e93c990b233ecb0651d590b18bae77cb11f5a164dd9dbf162940fe8a(
    stage_definition: typing.Sequence[typing.Union[builtins.str, IStageDefinition]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__83c9c30e5c910f8a42c91c2cdfe10b96838427cfad1df0dd0d1f79a25c689743(
    name: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e6c3e7c1ab6370c7e9e1543431006bb4a8f0633c59a8905776483258a8d5e956(
    id: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__069e90c1610d43cb2c6ef43b14042fc85fa26ed52ae992b62ad0cb0c44a3ffba(
    log_retention_in_days: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8a3183666d8c9303b29fc55e929aae211c7873631be8e182ab032d34792ee111(
    plugin: IPlugin,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__de2cafae27b0a8b224592ddb7b3e0c866e606b476cc82a384f7e17b21e903b55(
    primary_output_directory: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__257f02515607ca7b2cbac870b9dc51acd5825eee3eea8b2541d187d31d8c6170(
    proxy: typing.Optional[IProxyConfig] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c4fb5ed816611a8a70f08dd308e0bed206030900f86c7344c801f76c4702132d(
    region: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f4420b671e8440f0a0480eb324d0348d3e070a960cb8c6a0079a8065f84add05(
    repository_source: RepositorySource,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__669b5d7571521122e2a07e6927208f54a1970d3f1499f36240a119a80f76bb11(
    repository_provider: IResourceProvider,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__dc3b4580752fe4a8e1a1b1b27a59031558d39f1726d08d645f3ffb902f8bd8d0(
    name: builtins.str,
    provider: IResourceProvider,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5b82264054c5081c0202d720cf235cc8363756098c9c30b6c77bda9b8563276d(
    app: _aws_cdk_ceddda9d.App,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7a227c2795585c5792f9af4e6d26cb1058d189a051941a517c1dca61b3340a59(
    stack_provider: IStackProvider,
    *,
    stage_to_use: typing.Optional[builtins.str] = None,
    workbench_prefix: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__52896c1bf00490014e35c3e554377df286a6dea674c0a39a8ba117796da24a32(
    *,
    pipeline_type: _aws_cdk_aws_codepipeline_ceddda9d.PipelineType,
    docker_credentials: typing.Optional[typing.Sequence[_aws_cdk_pipelines_ceddda9d.DockerCredential]] = None,
    publish_assets_in_parallel: typing.Optional[builtins.bool] = None,
    self_mutation: typing.Optional[builtins.bool] = None,
    use_change_sets: typing.Optional[builtins.bool] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__eea3324e3b8fd85555f6fdf9982b07417cf8c57ec0fe84753017f088babfdd5f(
    *,
    branch: builtins.str,
    ci_build_spec: _aws_cdk_aws_codebuild_ceddda9d.BuildSpec,
    code_build_defaults: typing.Union[_aws_cdk_pipelines_ceddda9d.CodeBuildOptions, typing.Dict[builtins.str, typing.Any]],
    primary_output_directory: builtins.str,
    repository_input: _aws_cdk_pipelines_ceddda9d.IFileSetProducer,
    build_image: typing.Optional[_aws_cdk_aws_codebuild_ceddda9d.IBuildImage] = None,
    code_guru_scan_threshold: typing.Optional[CodeGuruSeverityThreshold] = None,
    install_commands: typing.Optional[typing.Sequence[builtins.str]] = None,
    is_docker_enabled_for_synth: typing.Optional[builtins.bool] = None,
    options: typing.Optional[typing.Union[PipelineOptions, typing.Dict[builtins.str, typing.Any]]] = None,
    pipeline_variables: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
    synth_code_build_defaults: typing.Optional[typing.Union[_aws_cdk_pipelines_ceddda9d.CodeBuildOptions, typing.Dict[builtins.str, typing.Any]]] = None,
    vpc_props: typing.Optional[typing.Union[VpcProps, typing.Dict[builtins.str, typing.Any]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e719a4ad9cfdd62aa1cb38580c0026d384dfb7fea4f275a417b2bf25a3b5df16(
    scope: _constructs_77d1e7e8.Construct,
    context: ResourceContext,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__49465724184f1e1b2dffd7e1bb267264b426f64fdae78a1e05655cb8ce8bf12b(
    scope: _constructs_77d1e7e8.Construct,
    context: ResourceContext,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__69e2889677167aaaee4e737eacef4ebd7a5a427e276383982069fab8bbaa0b81(
    context: ResourceContext,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9f7afea493adedc2b081e5ea11b7fd108a0c91e0c862989ec3c81f8201106dcd(
    stage: builtins.str,
    props: typing.Union[_aws_cdk_pipelines_ceddda9d.CodeBuildStepProps, typing.Dict[builtins.str, typing.Any]],
    application_name: builtins.str,
    role_arn: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8164c597bc966401bc0fe92404de52ab14230c9c79587bc72ada8435efbedffa(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    name: builtins.str,
    res_account: builtins.str,
    stage_name: builtins.str,
    inline_policies: typing.Optional[typing.Mapping[builtins.str, _aws_cdk_aws_iam_ceddda9d.PolicyDocument]] = None,
    prefix: typing.Optional[builtins.str] = None,
    analytics_reporting: typing.Optional[builtins.bool] = None,
    cross_region_references: typing.Optional[builtins.bool] = None,
    description: typing.Optional[builtins.str] = None,
    env: typing.Optional[typing.Union[_aws_cdk_ceddda9d.Environment, typing.Dict[builtins.str, typing.Any]]] = None,
    notification_arns: typing.Optional[typing.Sequence[builtins.str]] = None,
    permissions_boundary: typing.Optional[_aws_cdk_ceddda9d.PermissionsBoundary] = None,
    stack_name: typing.Optional[builtins.str] = None,
    suppress_template_indentation: typing.Optional[builtins.bool] = None,
    synthesizer: typing.Optional[_aws_cdk_ceddda9d.IStackSynthesizer] = None,
    tags: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
    termination_protection: typing.Optional[builtins.bool] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f6647e09f88c64f99ee4bdc5407591bb186063dc43d2565eb8ce7bbf8b863356(
    *,
    analytics_reporting: typing.Optional[builtins.bool] = None,
    cross_region_references: typing.Optional[builtins.bool] = None,
    description: typing.Optional[builtins.str] = None,
    env: typing.Optional[typing.Union[_aws_cdk_ceddda9d.Environment, typing.Dict[builtins.str, typing.Any]]] = None,
    notification_arns: typing.Optional[typing.Sequence[builtins.str]] = None,
    permissions_boundary: typing.Optional[_aws_cdk_ceddda9d.PermissionsBoundary] = None,
    stack_name: typing.Optional[builtins.str] = None,
    suppress_template_indentation: typing.Optional[builtins.bool] = None,
    synthesizer: typing.Optional[_aws_cdk_ceddda9d.IStackSynthesizer] = None,
    tags: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
    termination_protection: typing.Optional[builtins.bool] = None,
    name: builtins.str,
    res_account: builtins.str,
    stage_name: builtins.str,
    inline_policies: typing.Optional[typing.Mapping[builtins.str, _aws_cdk_aws_iam_ceddda9d.PolicyDocument]] = None,
    prefix: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__cb31b97373db95cd416ca376c1e5eba687bcf3ab942d2569c57bcd982d7f8fd2(
    stage: builtins.str,
    *,
    action_role: typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole] = None,
    build_environment: typing.Optional[typing.Union[_aws_cdk_aws_codebuild_ceddda9d.BuildEnvironment, typing.Dict[builtins.str, typing.Any]]] = None,
    cache: typing.Optional[_aws_cdk_aws_codebuild_ceddda9d.Cache] = None,
    file_system_locations: typing.Optional[typing.Sequence[_aws_cdk_aws_codebuild_ceddda9d.IFileSystemLocation]] = None,
    logging: typing.Optional[typing.Union[_aws_cdk_aws_codebuild_ceddda9d.LoggingOptions, typing.Dict[builtins.str, typing.Any]]] = None,
    partial_build_spec: typing.Optional[_aws_cdk_aws_codebuild_ceddda9d.BuildSpec] = None,
    project_name: typing.Optional[builtins.str] = None,
    role: typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole] = None,
    role_policy_statements: typing.Optional[typing.Sequence[_aws_cdk_aws_iam_ceddda9d.PolicyStatement]] = None,
    security_groups: typing.Optional[typing.Sequence[_aws_cdk_aws_ec2_ceddda9d.ISecurityGroup]] = None,
    subnet_selection: typing.Optional[typing.Union[_aws_cdk_aws_ec2_ceddda9d.SubnetSelection, typing.Dict[builtins.str, typing.Any]]] = None,
    timeout: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
    vpc: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.IVpc] = None,
    commands: typing.Sequence[builtins.str],
    additional_inputs: typing.Optional[typing.Mapping[builtins.str, _aws_cdk_pipelines_ceddda9d.IFileSetProducer]] = None,
    env: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
    env_from_cfn_outputs: typing.Optional[typing.Mapping[builtins.str, _aws_cdk_ceddda9d.CfnOutput]] = None,
    input: typing.Optional[_aws_cdk_pipelines_ceddda9d.IFileSetProducer] = None,
    install_commands: typing.Optional[typing.Sequence[builtins.str]] = None,
    primary_output_directory: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__089ff8ed46011c56913f9c41f507ec457aa745cdbd0b3a78ce5f0d0ffcf63620(
    *,
    no_proxy: typing.Sequence[builtins.str],
    proxy_secret_arn: builtins.str,
    proxy_test_url: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7d8f35a66618d2e7c7f39cff05c118af6defe9c791ae585ca95d4ab2db26e8f5(
    script: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__cd7a11f613d342f1cdb5aecca9a3c81db0760271727f0901a73b8fe466e0463a(
    *,
    branch: builtins.str,
    name: builtins.str,
    repository_type: builtins.str,
    code_build_clone_output: typing.Optional[builtins.bool] = None,
    description: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__21e3be4487767c5d4930911688171dde310cc674a0936577bc4b3cd866aab5e1(
    type: builtins.str,
    *,
    code_guru_reviewer: typing.Optional[builtins.bool] = None,
    code_star_connection_arn: typing.Optional[builtins.str] = None,
    branch: builtins.str,
    name: builtins.str,
    repository_type: builtins.str,
    code_build_clone_output: typing.Optional[builtins.bool] = None,
    description: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__cc5eb055e68eeb38bf802b5bc0ba875fa4dc6a10c324f002a1d11c4bc578047b(
    context: ResourceContext,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__05576ebde777c88feb630da30f74fd9172cf956c6ed229ee91767e043baa752a(
    *,
    branch: typing.Optional[builtins.str] = None,
    code_build_clone_output: typing.Optional[builtins.bool] = None,
    description: typing.Optional[builtins.str] = None,
    repository_name: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6f34ce6664c6ad39a0e84b86392061f5c3ae5df3fb5ddb4a0af4669a6d308354(
    _scope: _constructs_77d1e7e8.Construct,
    pipeline_stack: _constructs_77d1e7e8.Construct,
    blueprint_props: IPipelineBlueprintProps,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__29aaf3e2aee7b9f9ace4d5a07be6ebd6f4fb0befea6f38ea6c643e820f8cb248(
    name: builtins.str,
    value: typing.Any,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__fcc5cf5762c3a9ef4fe5d457152ebb9460335dcd72643bf9aadbb56da7fe06cf(
    name: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__90f8a7950f878afee504f6453182a4b979ba397aef2c71ee1e7deeed98bea3c7(
    name: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4f5471bc22ce257979e8d93c1416387b27683da69dfcac193d2e0d0443496eda(
    stage: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9913f45c0f7fd1459e64a81c3cbf4683133c5a8d2b0f926fc0b4969b16816fcf(
    scope: _constructs_77d1e7e8.Construct,
    _: ResourceContext,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__20c4903b48e4b9702ed6f32f3af88151150aaa993ab2015f582d1238209c6bd9(
    *,
    dotnet: typing.Optional[builtins.str] = None,
    golang: typing.Optional[builtins.str] = None,
    java: typing.Optional[builtins.str] = None,
    nodejs: typing.Optional[builtins.str] = None,
    php: typing.Optional[builtins.str] = None,
    python: typing.Optional[builtins.str] = None,
    ruby: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__836a73b666c09f791e0a9164cd93f9ddfe0ca30834a1bbb22342516c2b0be956(
    context: ResourceContext,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4eb15330d57d57d2fa0906ecf502b8fcc38dfdc05caf6ab104490901b8840cc5(
    *,
    branch: typing.Optional[builtins.str] = None,
    code_build_clone_output: typing.Optional[builtins.bool] = None,
    description: typing.Optional[builtins.str] = None,
    repository_name: typing.Optional[builtins.str] = None,
    bucket_name: typing.Optional[builtins.str] = None,
    prefix: typing.Optional[builtins.str] = None,
    removal_policy: typing.Optional[_aws_cdk_ceddda9d.RemovalPolicy] = None,
    roles: typing.Optional[typing.Sequence[builtins.str]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__79c18121b9902de42722598e43d8a1c359a96c61c2ed36a92b623a474f6282ad(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    application_qualifier: builtins.str,
    parameter: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
    analytics_reporting: typing.Optional[builtins.bool] = None,
    cross_region_references: typing.Optional[builtins.bool] = None,
    description: typing.Optional[builtins.str] = None,
    env: typing.Optional[typing.Union[_aws_cdk_ceddda9d.Environment, typing.Dict[builtins.str, typing.Any]]] = None,
    notification_arns: typing.Optional[typing.Sequence[builtins.str]] = None,
    permissions_boundary: typing.Optional[_aws_cdk_ceddda9d.PermissionsBoundary] = None,
    stack_name: typing.Optional[builtins.str] = None,
    suppress_template_indentation: typing.Optional[builtins.bool] = None,
    synthesizer: typing.Optional[_aws_cdk_ceddda9d.IStackSynthesizer] = None,
    tags: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
    termination_protection: typing.Optional[builtins.bool] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__686c34d5dc18b773af4369d624355d84ebf146e5e3b7ef1e349e08613c781ae4(
    scope: _constructs_77d1e7e8.Construct,
    parameter_name: builtins.str,
    parameter_value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1e6df23de8cdb325667d069a22fc0f33c6721a76eb0e5b0fd929aea2f2e2d328(
    parameter_name: builtins.str,
    parameter_value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__170535cb27d2b150d49bcbe83f3b1688950d0ecffcbf7d1dc5176a715b842332(
    *,
    analytics_reporting: typing.Optional[builtins.bool] = None,
    cross_region_references: typing.Optional[builtins.bool] = None,
    description: typing.Optional[builtins.str] = None,
    env: typing.Optional[typing.Union[_aws_cdk_ceddda9d.Environment, typing.Dict[builtins.str, typing.Any]]] = None,
    notification_arns: typing.Optional[typing.Sequence[builtins.str]] = None,
    permissions_boundary: typing.Optional[_aws_cdk_ceddda9d.PermissionsBoundary] = None,
    stack_name: typing.Optional[builtins.str] = None,
    suppress_template_indentation: typing.Optional[builtins.bool] = None,
    synthesizer: typing.Optional[_aws_cdk_ceddda9d.IStackSynthesizer] = None,
    tags: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
    termination_protection: typing.Optional[builtins.bool] = None,
    application_qualifier: builtins.str,
    parameter: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__97d34fd84710d7e19754b401f9349c4ef78fc6ac154658f21e15f05229da479d(
    command: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__cb3e9a52990b22235a8364f4211bde160966e495fa73cb3bc33fa7047bb09871(
    script: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7220e6b836834a71afbd78df0aace7bd839469e961059ac52d5b7ce7b0236a2d(
    context: ResourceContext,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__32dfdf8b3797d6aa03fe8fe21749e5e347f05045ad36b7481f9686b3e7adfec9(
    value: typing.Optional[Scope],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4d3d82188ff493924bd19bfd03d82068f7bdf03bc8245e19aea750d438e9afe2(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    vpc_id: builtins.str,
    code_build_vpc_interfaces: typing.Optional[typing.Sequence[_aws_cdk_aws_ec2_ceddda9d.InterfaceVpcEndpointAwsService]] = None,
    analytics_reporting: typing.Optional[builtins.bool] = None,
    cross_region_references: typing.Optional[builtins.bool] = None,
    description: typing.Optional[builtins.str] = None,
    env: typing.Optional[typing.Union[_aws_cdk_ceddda9d.Environment, typing.Dict[builtins.str, typing.Any]]] = None,
    notification_arns: typing.Optional[typing.Sequence[builtins.str]] = None,
    permissions_boundary: typing.Optional[_aws_cdk_ceddda9d.PermissionsBoundary] = None,
    stack_name: typing.Optional[builtins.str] = None,
    suppress_template_indentation: typing.Optional[builtins.bool] = None,
    synthesizer: typing.Optional[_aws_cdk_ceddda9d.IStackSynthesizer] = None,
    tags: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
    termination_protection: typing.Optional[builtins.bool] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__568a5801eb6463e97dd95391b7a31bc0cf542050e26818e6fe0fdb7fa00898a6(
    *,
    analytics_reporting: typing.Optional[builtins.bool] = None,
    cross_region_references: typing.Optional[builtins.bool] = None,
    description: typing.Optional[builtins.str] = None,
    env: typing.Optional[typing.Union[_aws_cdk_ceddda9d.Environment, typing.Dict[builtins.str, typing.Any]]] = None,
    notification_arns: typing.Optional[typing.Sequence[builtins.str]] = None,
    permissions_boundary: typing.Optional[_aws_cdk_ceddda9d.PermissionsBoundary] = None,
    stack_name: typing.Optional[builtins.str] = None,
    suppress_template_indentation: typing.Optional[builtins.bool] = None,
    synthesizer: typing.Optional[_aws_cdk_ceddda9d.IStackSynthesizer] = None,
    tags: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
    termination_protection: typing.Optional[builtins.bool] = None,
    vpc_id: builtins.str,
    code_build_vpc_interfaces: typing.Optional[typing.Sequence[_aws_cdk_aws_ec2_ceddda9d.InterfaceVpcEndpointAwsService]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9cb678678c5149ad6421a902df2d3a623600a703dd7c5f18faad8ffa9f15978a(
    legacy_config: typing.Optional[IVpcConfig] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__fdd3c2dd80b7c984a453628a65861222abc4482d8381a85218fecd00f299f006(
    context: ResourceContext,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__622fe918713ec74ba2c1e4ab2f7ed8ae0a4ec65a96fe0e8620746aab99e4a8d9(
    value: typing.Optional[Scope],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__eaeae75044f602086394b1aa0bcd90ce0806f7528969b249d9b40078c36ddab4(
    *,
    vpc: _aws_cdk_aws_ec2_ceddda9d.IVpc,
    proxy: typing.Optional[typing.Union[ProxyProps, typing.Dict[builtins.str, typing.Any]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__34abccea35b03904e80070603d8ca068e8fb7d437444a2dd7d242c1b2bd24fe1(
    *,
    options: typing.Union[WorkbenchOptions, typing.Dict[builtins.str, typing.Any]],
    stack_provider: IStackProvider,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b019ff265121b74fa169874c60cca2bfa4c9422a7c81b457375d95b4e54eefd0(
    *,
    stage_to_use: typing.Optional[builtins.str] = None,
    workbench_prefix: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6e20db3465b69cda662c15c86df02f716061cbc07b8720551fa2bc4bd4008966(
    scope: _constructs_77d1e7e8.Construct,
    context: ResourceContext,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__147924c72866b4c27849d07a0553fb97d12e07a5c4b00c0cbc526dd4e32730e0(
    build_spec: _aws_cdk_aws_codebuild_ceddda9d.BuildSpec,
    *,
    build_environment: typing.Optional[typing.Union[_aws_cdk_aws_codebuild_ceddda9d.BuildEnvironment, typing.Dict[builtins.str, typing.Any]]] = None,
    cache: typing.Optional[_aws_cdk_aws_codebuild_ceddda9d.Cache] = None,
    file_system_locations: typing.Optional[typing.Sequence[_aws_cdk_aws_codebuild_ceddda9d.IFileSystemLocation]] = None,
    logging: typing.Optional[typing.Union[_aws_cdk_aws_codebuild_ceddda9d.LoggingOptions, typing.Dict[builtins.str, typing.Any]]] = None,
    partial_build_spec: typing.Optional[_aws_cdk_aws_codebuild_ceddda9d.BuildSpec] = None,
    role_policy: typing.Optional[typing.Sequence[_aws_cdk_aws_iam_ceddda9d.PolicyStatement]] = None,
    security_groups: typing.Optional[typing.Sequence[_aws_cdk_aws_ec2_ceddda9d.ISecurityGroup]] = None,
    subnet_selection: typing.Optional[typing.Union[_aws_cdk_aws_ec2_ceddda9d.SubnetSelection, typing.Dict[builtins.str, typing.Any]]] = None,
    timeout: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
    vpc: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.IVpc] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5c767dd217b4b30647a569278c238dfe91636e0a122f5bd957e8425fbffad50b(
    policy_statements: typing.Sequence[_aws_cdk_aws_iam_ceddda9d.PolicyStatement],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9c794c113fa8b23b1c4ed1fc05a45fa328039d7ce3dd09f941cf35ce65129096(
    partial_build_spec: _aws_cdk_aws_codebuild_ceddda9d.BuildSpec,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0786935eb8047679ad4ae957c1c92688fa948e80e25c84108fb1f1921638620c(
    *,
    branch: builtins.str,
    name: builtins.str,
    repository_type: builtins.str,
    code_build_clone_output: typing.Optional[builtins.bool] = None,
    description: typing.Optional[builtins.str] = None,
    code_guru_reviewer: typing.Optional[builtins.bool] = None,
    code_star_connection_arn: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d21350111e8f0af91174db10afef8f55217eaad998fd3fa8f831b3ec48a4796c(
    reason: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__93749efec26f6060dadfeee523230f2893d7b4f15df00660a895c33f6aaa036f(
    context: ResourceContext,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d697cdcbe532f07d04b89722be4ec6911b4b2516ffc502aba9f3652ee94e8634(
    ssm_parameter_name: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3d05ec817f774252beefe21c47c48d57bef1a1630540a04f30467dbd7ae53d72(
    context: ResourceContext,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d9f45aee57f132f39a3dbfeafc22b558e4ef6959ec5789e3fa2ec6c8692946af(
    context: ResourceContext,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d620e25e0a083b43dfb5f69b1260b2072f9c44c0a626d98289867d8408743048(
    *,
    branch: builtins.str,
    ci_build_spec: _aws_cdk_aws_codebuild_ceddda9d.BuildSpec,
    code_build_defaults: typing.Union[_aws_cdk_pipelines_ceddda9d.CodeBuildOptions, typing.Dict[builtins.str, typing.Any]],
    primary_output_directory: builtins.str,
    repository_input: _aws_cdk_pipelines_ceddda9d.IFileSetProducer,
    build_image: typing.Optional[_aws_cdk_aws_codebuild_ceddda9d.IBuildImage] = None,
    code_guru_scan_threshold: typing.Optional[CodeGuruSeverityThreshold] = None,
    install_commands: typing.Optional[typing.Sequence[builtins.str]] = None,
    is_docker_enabled_for_synth: typing.Optional[builtins.bool] = None,
    options: typing.Optional[typing.Union[PipelineOptions, typing.Dict[builtins.str, typing.Any]]] = None,
    pipeline_variables: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
    synth_code_build_defaults: typing.Optional[typing.Union[_aws_cdk_pipelines_ceddda9d.CodeBuildOptions, typing.Dict[builtins.str, typing.Any]]] = None,
    vpc_props: typing.Optional[typing.Union[VpcProps, typing.Dict[builtins.str, typing.Any]]] = None,
    application_qualifier: builtins.str,
    pipeline_name: builtins.str,
    role_policies: typing.Optional[typing.Sequence[_aws_cdk_aws_iam_ceddda9d.PolicyStatement]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__40ae53f223487f82ec30681c3f884548ce3854177854807bcbb633fc589950d5(
    context: ResourceContext,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__bc46d45204f1c4a5420d1b824c76ced78e236d677d5566eba693ffb24bbbe500(
    context: ResourceContext,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2848d58e405e850d9b6dfe0b20fc027b41ccc89257e2305bc72c21d664ca9460(
    context: ResourceContext,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5b84906c38447fcf4014b0f405a4b327d895512ba64ea6887c7ae01fec239a61(
    *,
    branch: builtins.str,
    name: builtins.str,
    repository_type: builtins.str,
    code_build_clone_output: typing.Optional[builtins.bool] = None,
    description: typing.Optional[builtins.str] = None,
    application_name: builtins.str,
    application_qualifier: builtins.str,
    pr: typing.Optional[typing.Union[PRCheckConfig, typing.Dict[builtins.str, typing.Any]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3c7e75e0fcfe482753dd9afbe1d8aa1e962787966e8173daaa5498c31e88fdc4(
    context: ResourceContext,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__724a8ca2b7f125912ae200cacbb2ac8f9962c6a4e6bd4ec40c8be4aac16ae42a(
    *,
    branch: typing.Optional[builtins.str] = None,
    code_build_clone_output: typing.Optional[builtins.bool] = None,
    description: typing.Optional[builtins.str] = None,
    repository_name: typing.Optional[builtins.str] = None,
    enable_code_guru_reviewer: typing.Optional[builtins.bool] = None,
    enable_pull_request_checks: typing.Optional[builtins.bool] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1326f9afc6ac1394d551fb7ae30a9bc313236ff9e699e0a6c605861c1ff2ca54(
    *,
    branch: builtins.str,
    name: builtins.str,
    repository_type: builtins.str,
    code_build_clone_output: typing.Optional[builtins.bool] = None,
    description: typing.Optional[builtins.str] = None,
    code_star_connection_arn: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c39fbb1da05a0f6be7186d8b68e74ecbc5ad47e74517ae1b69b180809fc3cf1a(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    application_name: builtins.str,
    application_qualifier: builtins.str,
    analytics_reporting: typing.Optional[builtins.bool] = None,
    cross_region_references: typing.Optional[builtins.bool] = None,
    description: typing.Optional[builtins.str] = None,
    env: typing.Optional[typing.Union[_aws_cdk_ceddda9d.Environment, typing.Dict[builtins.str, typing.Any]]] = None,
    notification_arns: typing.Optional[typing.Sequence[builtins.str]] = None,
    permissions_boundary: typing.Optional[_aws_cdk_ceddda9d.PermissionsBoundary] = None,
    stack_name: typing.Optional[builtins.str] = None,
    suppress_template_indentation: typing.Optional[builtins.bool] = None,
    synthesizer: typing.Optional[_aws_cdk_ceddda9d.IStackSynthesizer] = None,
    tags: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
    termination_protection: typing.Optional[builtins.bool] = None,
    code_star_connection_arn: builtins.str,
    branch: builtins.str,
    name: builtins.str,
    repository_type: builtins.str,
    code_build_clone_output: typing.Optional[builtins.bool] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__35b5626df5f6ac2c68b5bf6f14bb1ad28ac054b7cf50018f01d7404a733907a2(
    *,
    analytics_reporting: typing.Optional[builtins.bool] = None,
    cross_region_references: typing.Optional[builtins.bool] = None,
    description: typing.Optional[builtins.str] = None,
    env: typing.Optional[typing.Union[_aws_cdk_ceddda9d.Environment, typing.Dict[builtins.str, typing.Any]]] = None,
    notification_arns: typing.Optional[typing.Sequence[builtins.str]] = None,
    permissions_boundary: typing.Optional[_aws_cdk_ceddda9d.PermissionsBoundary] = None,
    stack_name: typing.Optional[builtins.str] = None,
    suppress_template_indentation: typing.Optional[builtins.bool] = None,
    synthesizer: typing.Optional[_aws_cdk_ceddda9d.IStackSynthesizer] = None,
    tags: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
    termination_protection: typing.Optional[builtins.bool] = None,
    branch: builtins.str,
    name: builtins.str,
    repository_type: builtins.str,
    code_build_clone_output: typing.Optional[builtins.bool] = None,
    code_star_connection_arn: builtins.str,
    application_name: builtins.str,
    application_qualifier: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4804255bea2ce295164feac477ca108fe8c328e4cb773738fb1d69a11270d5b5(
    context: ResourceContext,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__39757b982173f6e8faa868b6e0695e31306a24bc7802ca9986a92fd2255d1aba(
    *,
    branch: typing.Optional[builtins.str] = None,
    code_build_clone_output: typing.Optional[builtins.bool] = None,
    description: typing.Optional[builtins.str] = None,
    repository_name: typing.Optional[builtins.str] = None,
    code_star_connection_arn: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__12917dbc84e8123087989167705cf322c6ae2663326b7b46acacf342571bbafd(
    context: ResourceContext,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__220eb1325496b5bc5cc9cc79a36b4bccd6fa21a4fd90ee24c693f371cbcac63f(
    value: typing.Optional[Scope],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2de0d0202c5209fccc689112158e98bf084388feb7436a5ce74ae3f6bab809d4(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    compliance_log_bucket_name: builtins.str,
    security_group: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.ISecurityGroup] = None,
    subnet_selection: typing.Optional[typing.Union[_aws_cdk_aws_ec2_ceddda9d.SubnetSelection, typing.Dict[builtins.str, typing.Any]]] = None,
    vpc: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.IVpc] = None,
    analytics_reporting: typing.Optional[builtins.bool] = None,
    cross_region_references: typing.Optional[builtins.bool] = None,
    description: typing.Optional[builtins.str] = None,
    env: typing.Optional[typing.Union[_aws_cdk_ceddda9d.Environment, typing.Dict[builtins.str, typing.Any]]] = None,
    notification_arns: typing.Optional[typing.Sequence[builtins.str]] = None,
    permissions_boundary: typing.Optional[_aws_cdk_ceddda9d.PermissionsBoundary] = None,
    stack_name: typing.Optional[builtins.str] = None,
    suppress_template_indentation: typing.Optional[builtins.bool] = None,
    synthesizer: typing.Optional[_aws_cdk_ceddda9d.IStackSynthesizer] = None,
    tags: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
    termination_protection: typing.Optional[builtins.bool] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a915644e96548f8c49985ce17dcb7602e2e81454516719822ed7dd0fc868c6d7(
    vpc: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.IVpc] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ce6ce5a098480ff0d1a1c203388008c361fcc1de8159085b433019ed695eabd0(
    key: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7fa3c9cfb86b42272a3d7f1966918be279e419c78daa9716a0e8d6ca14beb20e(
    context: ResourceContext,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__22a92f379c1f9445ba4bbb41f71efcddc5629f34b781303f9c1477ace2c73318(
    key: builtins.str,
    value: typing.Any,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__02ee6e1f0bd70b2378db88bb600d8149ec073b2a79027c54c6bd9f84e7f9098b(
    ssm_parameter_name: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__91d483e4c682667e3f7d1b0a57ab6f835e3a24bc0bffb4b60a09c3cdff496f52(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__19d8a58b1e48b086e3155e9ddc9840649f85a6635efed013249ac3d74ccf63a9(
    stages_to_retain: typing.Optional[typing.Sequence[Stage]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8358c26cfd747f2c7fe43168ac10397ebecf40fff59d497154bf4ab8e383d62a(
    scope: _constructs_77d1e7e8.Construct,
    context: ResourceContext,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4d4edbc4bcc588d61a77bc1e5e4f4b126ebf81c93609fe668c80ac85a444e1a7(
    scope: _constructs_77d1e7e8.Construct,
    _: ResourceContext,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__047a62344f9b1536ce8b5cfa3fd0d931c2eca2cd82bdd1814461d92ad21fb0be(
    scope: _constructs_77d1e7e8.Construct,
    _: ResourceContext,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__fe160cb43bd5f12a3ca4c8d9fc854aa9058809ac0b25420ecd88e7726ce77323(
    scope: _constructs_77d1e7e8.Construct,
    context: ResourceContext,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__028fb517a10e173f74d514f0406278a143b5f58ed07ac0a9c7b8c2dc245d61c1(
    context: ResourceContext,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__669d5be1b700c984a733eea9443531988c2838ce13fb185332f986ce8d542243(
    scope: _constructs_77d1e7e8.Construct,
    _: ResourceContext,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0540fc47da38399d846aa93316691212c809019de8e7312ff7acc9b1495bd4ff(
    context: ResourceContext,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__cb2b064ff8c3178537c895edb9e0bf06a6a1745f4df62465359709f72b9a1089(
    value: typing.Optional[Scope],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c1080415412bd6e7b2504d0411274a849872efcb7c3901ccf9aa16146de22f4b(
    context: ResourceContext,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__827a764561f31950abeb68084c9028591d15c18dbb0a2187b65a519aff70867a(
    _: ResourceContext,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7c12bda7dc1c95ff1a70f98683618c7eea0656f0c17c7a0647dcc347b6399a1c(
    value: typing.Optional[Scope],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ecc53ad44cbcc0f50d405beb52281fa83322ff4a33577168b4604a3d83fe50c1(
    proxy: typing.Optional[IProxyConfig] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__df10f7ff5493bafbe8f8f8dca717218594fbf22a76fa4b494cfdb381710e909c(
    context: ResourceContext,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0d334a5c6d5a97a3af61d05ad5a6d5c5f9b605704f1c2a8eaaddcaef4db4fd73(
    value: typing.Mapping[builtins.str, IPlugin],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__337cfe2eae32578f1f1b4c1bb33ff5a3aabc56d4881314c8658ef235f6e15e9e(
    value: typing.Mapping[builtins.str, IResourceProvider],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d7fa09ea6358c5696485e0b2589ab8f938310242e6dc708bf485c7f9bcd7867a(
    props: typing.Optional[ILambdaDLQPluginProps] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5d5a045ea22c85dd4513115acec16db15622b1cde47c7ddae0b7eeb3c22f3796(
    scope: _constructs_77d1e7e8.Construct,
    context: ResourceContext,
) -> None:
    """Type checking stubs"""
    pass

for cls in [ICIDefinition, ICodeBuildFactory, IComplianceBucket, IDeploymentHookConfigProvider, IEncryptionKey, ILambdaDLQPluginProps, ILogger, IManagedVpcConfig, IParameterConstruct, IPhaseCommand, IPhaseCommandSettings, IPipelineBlueprintProps, IPipelineConfig, IPipelinePhases, IPlugin, IProxyConfig, IRepositoryStack, IResourceProvider, IStackProvider, IStageConfig, IStageDefinition, IVpcConfig, IVpcConfigFromLookUp, IVpcConstruct]:
    typing.cast(typing.Any, cls).__protocol_attrs__ = typing.cast(typing.Any, cls).__protocol_attrs__ - set(['__jsii_proxy_class__', '__jsii_type__'])
