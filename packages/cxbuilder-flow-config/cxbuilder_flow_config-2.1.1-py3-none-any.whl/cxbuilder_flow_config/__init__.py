r'''
# @cxbuilder/flow-config

[![CI/CD Pipeline](https://github.com/cxbuilder/flow-config/actions/workflows/ci-cd.yml/badge.svg)](https://github.com/cxbuilder/flow-config/actions/workflows/ci-cd.yml)
[![npm version](https://badge.fury.io/js/@cxbuilder%2Fflow-config.svg)](https://badge.fury.io/js/@cxbuilder%2Fflow-config)
[![PyPI version](https://badge.fury.io/py/cxbuilder-flow-config.svg)](https://badge.fury.io/py/cxbuilder-flow-config)
[![View on Construct Hub](https://constructs.dev/badge?package=%40cxbuilder%2Fflow-config)](https://constructs.dev/packages/@cxbuilder/flow-config)

AWS CDK constructs for Amazon Connect FlowConfig - a third-party app for configuring variables and prompts in Connect contact flows.

## Links

* [Screenshots](./docs/screenshots/)
* [Architecture](./docs/Architecture.md)
* [DataModel](./docs/DataModel.md)

## Installation

```bash
npm install @cxbuilder/flow-config
```

## Usage

### Standard Deployment (Public)

```python
import { FlowConfigStack } from '@cxbuilder/flow-config';
import * as cdk from 'aws-cdk-lib';

const app = new cdk.App();
new FlowConfigStack(app, 'FlowConfigStack', {
  prefix: 'my-flow-config',
  env: {
    region: 'us-east-1',
    account: 'YOUR_ACCOUNT_ID',
  },
  cognito: {
    domain: 'https://your-auth-domain.com',
    userPoolId: 'us-east-1_YourPoolId',
  },
  connectInstanceArn:
    'arn:aws:connect:us-east-1:YOUR_ACCOUNT:instance/YOUR_INSTANCE_ID',
  alertEmails: ['admin@yourcompany.com'],
});
```

### VPC Private Deployment

For enhanced security, you can deploy the application to run entirely within a VPC with private endpoints:

```python
import { FlowConfigStack, VpcConfig } from '@cxbuilder/flow-config';
import * as cdk from 'aws-cdk-lib';

const app = new cdk.App();

// Configure VPC using string IDs - the stack will resolve these to CDK objects
const vpcConfig: VpcConfig = {
  vpcId: 'vpc-12345678',
  lambdaSecurityGroupIds: ['sg-lambda123'],
  privateSubnetIds: ['subnet-12345', 'subnet-67890'],
  vpcEndpointSecurityGroupIds: ['sg-endpoint123'],
};

new FlowConfigStack(app, 'FlowConfigStack', {
  prefix: 'my-flow-config',
  env: {
    region: 'us-east-1',
    account: 'YOUR_ACCOUNT_ID',
  },
  cognito: {
    domain: 'https://your-auth-domain.com',
    userPoolId: 'us-east-1_YourPoolId',
  },
  connectInstanceArn:
    'arn:aws:connect:us-east-1:YOUR_ACCOUNT:instance/YOUR_INSTANCE_ID',
  alertEmails: ['admin@yourcompany.com'],
  vpc: vpcConfig, // Enable VPC private deployment
});
```

### Multi-Region Global Table Deployment

For global resilience, deploy the application across multiple regions with DynamoDB Global Tables:

#### Primary Region Setup

```python
import { FlowConfigStack, GlobalTableConfig } from '@cxbuilder/flow-config';
import * as cdk from 'aws-cdk-lib';

const app = new cdk.App();

// Primary region creates the global table with replicas
const primaryGlobalTable: GlobalTableConfig = {
  isPrimaryRegion: true,
  replicaRegions: ['us-west-2', 'eu-west-1'],
};

new FlowConfigStack(app, 'FlowConfigStack-Primary', {
  prefix: 'my-flow-config',
  env: {
    region: 'us-east-1',
    account: 'YOUR_ACCOUNT_ID',
  },
  cognito: {
    domain: 'https://your-auth-domain.com',
    userPoolId: 'us-east-1_YourPoolId',
  },
  connectInstanceArn:
    'arn:aws:connect:us-east-1:YOUR_ACCOUNT:instance/YOUR_INSTANCE_ID',
  alertEmails: ['admin@yourcompany.com'],
  globalTable: primaryGlobalTable, // Enable global table
});
```

#### Secondary Region Setup

```python
new FlowConfigStack(app, 'FlowConfigStack-Secondary', {
  prefix: 'my-flow-config',
  env: {
    region: 'us-west-2',
    account: 'YOUR_ACCOUNT_ID',
  },
  cognito: {
    domain: 'https://your-auth-domain.com',
    userPoolId: 'us-west-2_YourPoolId',
  },
  connectInstanceArn:
    'arn:aws:connect:us-west-2:YOUR_ACCOUNT:instance/YOUR_INSTANCE_ID',
  alertEmails: ['admin@yourcompany.com'],
  globalTable: {
    isPrimaryRegion: false, // Reference global table
  },
});
```

## Features

* **Serverless Architecture**: Built with AWS Lambda, DynamoDB, and API Gateway
* **Amazon Connect Integration**: GetConfig Lambda function integrated directly with Connect contact flows
* **Third-Party App**: Web-based interface embedded in Amazon Connect Agent Workspace
* **Multi-Language Support**: Configure prompts for different languages and channels (voice/chat)
* **Real-time Preview**: Text-to-speech preview using Amazon Polly
* **Secure Access**: Integration with Amazon Connect and AWS Verified Permissions
* **Flexible Deployment Options**:

  * **Single-Region**: Standard deployment with regional DynamoDB table
  * **Multi-Region**: Global table support with automatic replication across regions
  * **Public Deployment**: Standard internet-accessible API Gateway and Lambda functions
  * **VPC Private Deployment**: Private API Gateway endpoints, VPC-enabled Lambda functions, and VPC endpoints for enhanced security

## GetConfig Lambda Integration

The GetConfig Lambda function is used within contact flows to access your flow configs. This function is automatically integrated with your Amazon Connect instance during deployment.

### Contact Flow Event Structure

The Lambda function handles Amazon Connect Contact Flow events with the following structure:

```json
{
  "Details": {
    "Parameters": {
      "id": "main-queue",
      "lang": "es-US"
    },
    "ContactData": {
      "Channel": "VOICE",
      "LanguageCode": "en-US"
    }
  }
}
```

### Input Parameters and Priority

1. **Required Parameters**:

   * **`id`**: Flow configuration identifier (always required)

     * Provided via `Details.Parameters.id`
2. **Optional Language Selection** (in order of precedence):

   * `Details.Parameters.lang` (highest priority)
   * `Details.ContactData.LanguageCode`
   * Defaults to `"en-US"`
3. **Channel Detection**:

   * Automatically read from `Details.ContactData.Channel`
   * Supports `"VOICE"` and `"CHAT"`
   * Defaults to `"voice"`

### Alternative Input Format (Testing)

For direct testing or non-Connect invocation:

```json
{
  "id": "main-queue",
  "lang": "es-US",
  "channel": "voice"
}
```

### Function Behavior

1. **Parameter Resolution**:

   * Extracts `id` from Connect event parameters (required)
   * Resolves language from parameters → attributes → default
   * Determines channel from Contact Flow event data
2. **Processing Steps**:

   * Retrieves the flow config from DynamoDB using the provided ID
   * Includes all variables from the flow config in the result
   * For each prompt in the flow config:

     * Selects the appropriate language version
     * Uses voice content by default
     * For chat channel:

       * Uses chat-specific content if available
       * Strips SSML tags from voice content if no chat content exists
3. **Output**:

   * Returns a flattened object containing:

     * All variable key-value pairs from the flow config
     * All prompt values resolved for the specified language and channel

### Setting Up in Contact Flow

1. **Add "Invoke AWS Lambda function" block** to your contact flow
2. **Select the GetConfig Lambda function** (deployed as `${prefix}`)
3. **Configure parameters**:

```json
{
  "id": "main-queue"
}
```

Or with explicit language:

```json
{
  "id": "main-queue",
  "lang": "es-US"
}
```

### Using Returned Data

The Lambda response is automatically available in subsequent blocks:

* **Set contact attributes**: Use `$.External.variableName`
* **Play prompt**: Use `$.External.promptName`
* **Check contact attributes**: Reference returned variables for routing decisions

### Example Contact Flow Integration

```
[Get customer input] → [Invoke Lambda: GetConfig]
                           ↓
                      [Set contact attributes]
                           ↓
                      [Play prompt: $.External.welcomeMessage]
                           ↓
                      [Route based on: $.External.routingMode]
```

### Size Considerations

* Amazon Connect has a Lambda response size limit of 32KB
* The combined size of returned variables and prompts should be less than this limit
* For large flow configs with many prompts or languages, consider implementing pagination or selective loading

### Logger

[Lambda PowerTools Logger](https://docs.powertools.aws.dev/lambda/typescript/latest/core/logger/) provides a lightweight logger implementation with JSON output.

Tips:

* Use the `appendKeys()` method to add `ContactId` to your connect log lambda output.

### Open API Spec

This template defines an Open API Spec for the API GW Lambdas. This allows use to generate a TypeScript api client to be used by the frontend app. We can also generate a API client in any language from the same spec to allow the client to better integrate with our apps.

* [constructs/aws-openapigateway-lambda](https://docs.aws.amazon.com/solutions/latest/constructs/aws-openapigateway-lambda.html)
* [OpenAPI Editor](https://marketplace.visualstudio.com/items?itemName=42Crunch.vscode-openapi)
* [OpenApy TypeScript Generator](https://openapi-ts.pages.dev/introduction)

## Development

### Frontend Development

The frontend React application integrates with Amazon Connect Agent Workspace using the Connect SDK:

```bash
# Start local development server
npm start

# Build for production
npm run build
```

For local development, point your Amazon Connect third-party app configuration to `localhost:3000`. The application requires execution within Agent Workspace for Connect SDK functionality.

### Lambda Development

Lambda functions are bundled automatically during the build process:

```bash
# Bundle Lambda functions
npm run build:lambdas

# Full build (CDK + Frontend + Lambdas)
npm run build
```
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
import aws_cdk.aws_cognito as _aws_cdk_aws_cognito_ceddda9d
import aws_cdk.aws_dynamodb as _aws_cdk_aws_dynamodb_ceddda9d
import aws_cdk.aws_sns as _aws_cdk_aws_sns_ceddda9d
import constructs as _constructs_77d1e7e8


@jsii.data_type(
    jsii_type="@cxbuilder/flow-config.ApiVpcConfig",
    jsii_struct_bases=[],
    name_mapping={"vpc_endpoint_id": "vpcEndpointId", "vpc_id": "vpcId"},
)
class ApiVpcConfig:
    def __init__(self, *, vpc_endpoint_id: builtins.str, vpc_id: builtins.str) -> None:
        '''VPC configuration for API Gateway If provided, the API will be deployed in a private VPC.

        :param vpc_endpoint_id: The VPC endpoint ID to use for the API.
        :param vpc_id: The VPC ID to use for the API.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__47e62f7d60550c4362367009c9f9b9eeb6c29e12c73fa022b3ca687bcd5825c5)
            check_type(argname="argument vpc_endpoint_id", value=vpc_endpoint_id, expected_type=type_hints["vpc_endpoint_id"])
            check_type(argname="argument vpc_id", value=vpc_id, expected_type=type_hints["vpc_id"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "vpc_endpoint_id": vpc_endpoint_id,
            "vpc_id": vpc_id,
        }

    @builtins.property
    def vpc_endpoint_id(self) -> builtins.str:
        '''The VPC endpoint ID to use for the API.'''
        result = self._values.get("vpc_endpoint_id")
        assert result is not None, "Required property 'vpc_endpoint_id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def vpc_id(self) -> builtins.str:
        '''The VPC ID to use for the API.'''
        result = self._values.get("vpc_id")
        assert result is not None, "Required property 'vpc_id' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ApiVpcConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cxbuilder/flow-config.CognitoConfig",
    jsii_struct_bases=[],
    name_mapping={
        "domain": "domain",
        "user_pool_id": "userPoolId",
        "sso_provider_name": "ssoProviderName",
    },
)
class CognitoConfig:
    def __init__(
        self,
        *,
        domain: builtins.str,
        user_pool_id: builtins.str,
        sso_provider_name: typing.Optional[builtins.str] = None,
    ) -> None:
        '''Cognito configuration for FlowConfig stack.

        :param domain: Full domain name.
        :param user_pool_id: 
        :param sso_provider_name: If provided, client will auth to SSO. Otherwise will auth to user pool
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8a8d1dc5169a6979db20fa84537dd83b4e39d8f33ae09998177c6901c5402374)
            check_type(argname="argument domain", value=domain, expected_type=type_hints["domain"])
            check_type(argname="argument user_pool_id", value=user_pool_id, expected_type=type_hints["user_pool_id"])
            check_type(argname="argument sso_provider_name", value=sso_provider_name, expected_type=type_hints["sso_provider_name"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "domain": domain,
            "user_pool_id": user_pool_id,
        }
        if sso_provider_name is not None:
            self._values["sso_provider_name"] = sso_provider_name

    @builtins.property
    def domain(self) -> builtins.str:
        '''Full domain name.'''
        result = self._values.get("domain")
        assert result is not None, "Required property 'domain' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def user_pool_id(self) -> builtins.str:
        result = self._values.get("user_pool_id")
        assert result is not None, "Required property 'user_pool_id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def sso_provider_name(self) -> typing.Optional[builtins.str]:
        '''If provided, client will auth to SSO.

        Otherwise will auth to user pool
        '''
        result = self._values.get("sso_provider_name")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CognitoConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class FlowConfigStack(
    _aws_cdk_ceddda9d.Stack,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cxbuilder/flow-config.FlowConfigStack",
):
    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        alert_emails: typing.Sequence[builtins.str],
        cognito: typing.Union[CognitoConfig, typing.Dict[builtins.str, typing.Any]],
        connect_instance_arn: builtins.str,
        prefix: builtins.str,
        api_vpc_config: typing.Optional[typing.Union[ApiVpcConfig, typing.Dict[builtins.str, typing.Any]]] = None,
        associate3p_app: typing.Optional[builtins.bool] = None,
        branding: typing.Optional[builtins.bool] = None,
        global_table: typing.Optional[typing.Union["GlobalTableConfig", typing.Dict[builtins.str, typing.Any]]] = None,
        lambda_vpc_config: typing.Optional[typing.Union["LambdaVpcConfig", typing.Dict[builtins.str, typing.Any]]] = None,
        prod: typing.Optional[builtins.bool] = None,
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
        :param alert_emails: Who to notify for unhandled exceptions.
        :param cognito: 
        :param connect_instance_arn: 
        :param prefix: Used for resource naming. Will also be the name of the Connect Lambda
        :param api_vpc_config: If provided, the API will be deployed in a VPC.
        :param associate3p_app: Whether to associate the app with the Connect Agent Workspace. Set to false to disable automatic association. Default: true
        :param branding: Set to false to remove CXBuilder branding from the web app. Default: true
        :param global_table: Global table configuration for multi-region deployments. If provided, enables global table support. If undefined, creates a single-region table.
        :param lambda_vpc_config: If provided, the Lambda functions will be deployed in a VPC. Note: VPC should contain endpoints to: CloudFormation, Lambda, DynamoDB, SNS, and Polly.
        :param prod: 
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
            type_hints = typing.get_type_hints(_typecheckingstub__98249ce999a2ceaa5c924d743cca4b3c73d1deee69861f65f40468c97af84d0d)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = FlowConfigStackProps(
            alert_emails=alert_emails,
            cognito=cognito,
            connect_instance_arn=connect_instance_arn,
            prefix=prefix,
            api_vpc_config=api_vpc_config,
            associate3p_app=associate3p_app,
            branding=branding,
            global_table=global_table,
            lambda_vpc_config=lambda_vpc_config,
            prod=prod,
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

    @jsii.member(jsii_name="associate3pApp")
    def associate3p_app(self) -> None:
        '''Associate FlowConfig as Agent Workspace app.'''
        return typing.cast(None, jsii.invoke(self, "associate3pApp", []))

    @jsii.member(jsii_name="createUserPoolClient")
    def create_user_pool_client(self) -> _aws_cdk_aws_cognito_ceddda9d.UserPoolClient:
        return typing.cast(_aws_cdk_aws_cognito_ceddda9d.UserPoolClient, jsii.invoke(self, "createUserPoolClient", []))

    @jsii.member(jsii_name="createUserPoolGroups")
    def create_user_pool_groups(self) -> None:
        '''Create Cognito User Groups for role-based access control.'''
        return typing.cast(None, jsii.invoke(self, "createUserPoolGroups", []))

    @builtins.property
    @jsii.member(jsii_name="appUrl")
    def app_url(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "appUrl"))

    @builtins.property
    @jsii.member(jsii_name="alertTopic")
    def alert_topic(self) -> _aws_cdk_aws_sns_ceddda9d.Topic:
        return typing.cast(_aws_cdk_aws_sns_ceddda9d.Topic, jsii.get(self, "alertTopic"))

    @alert_topic.setter
    def alert_topic(self, value: _aws_cdk_aws_sns_ceddda9d.Topic) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e09197dd779e78a66d42a90f7cd054fba67453aa0026144aeca380beab52ca7d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "alertTopic", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="props")
    def props(self) -> "FlowConfigStackProps":
        return typing.cast("FlowConfigStackProps", jsii.get(self, "props"))

    @props.setter
    def props(self, value: "FlowConfigStackProps") -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a0ea9cf14e71cb22d154a64ad3f2d29e48113e66e457130b87e97d4e33fe174d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "props", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="table")
    def table(self) -> _aws_cdk_aws_dynamodb_ceddda9d.ITable:
        return typing.cast(_aws_cdk_aws_dynamodb_ceddda9d.ITable, jsii.get(self, "table"))

    @table.setter
    def table(self, value: _aws_cdk_aws_dynamodb_ceddda9d.ITable) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__57a9d04fe3c6a50dfeb0826707097cac273960f16ff4e111cedc4cda8cefc691)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "table", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="userPool")
    def user_pool(self) -> _aws_cdk_aws_cognito_ceddda9d.IUserPool:
        return typing.cast(_aws_cdk_aws_cognito_ceddda9d.IUserPool, jsii.get(self, "userPool"))

    @user_pool.setter
    def user_pool(self, value: _aws_cdk_aws_cognito_ceddda9d.IUserPool) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e083ade3aee28a14beca2baffec247d997b72f5564c2a07944ba16561beb38cf)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "userPool", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="userPoolClient")
    def user_pool_client(self) -> _aws_cdk_aws_cognito_ceddda9d.UserPoolClient:
        return typing.cast(_aws_cdk_aws_cognito_ceddda9d.UserPoolClient, jsii.get(self, "userPoolClient"))

    @user_pool_client.setter
    def user_pool_client(
        self,
        value: _aws_cdk_aws_cognito_ceddda9d.UserPoolClient,
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b4c27a8d9b9492db1bd2cf00de68024d3fbd47d511d1fad5c59bd2267e12b287)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "userPoolClient", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cxbuilder/flow-config.FlowConfigStackProps",
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
        "alert_emails": "alertEmails",
        "cognito": "cognito",
        "connect_instance_arn": "connectInstanceArn",
        "prefix": "prefix",
        "api_vpc_config": "apiVpcConfig",
        "associate3p_app": "associate3pApp",
        "branding": "branding",
        "global_table": "globalTable",
        "lambda_vpc_config": "lambdaVpcConfig",
        "prod": "prod",
    },
)
class FlowConfigStackProps(_aws_cdk_ceddda9d.StackProps):
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
        alert_emails: typing.Sequence[builtins.str],
        cognito: typing.Union[CognitoConfig, typing.Dict[builtins.str, typing.Any]],
        connect_instance_arn: builtins.str,
        prefix: builtins.str,
        api_vpc_config: typing.Optional[typing.Union[ApiVpcConfig, typing.Dict[builtins.str, typing.Any]]] = None,
        associate3p_app: typing.Optional[builtins.bool] = None,
        branding: typing.Optional[builtins.bool] = None,
        global_table: typing.Optional[typing.Union["GlobalTableConfig", typing.Dict[builtins.str, typing.Any]]] = None,
        lambda_vpc_config: typing.Optional[typing.Union["LambdaVpcConfig", typing.Dict[builtins.str, typing.Any]]] = None,
        prod: typing.Optional[builtins.bool] = None,
    ) -> None:
        '''
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
        :param alert_emails: Who to notify for unhandled exceptions.
        :param cognito: 
        :param connect_instance_arn: 
        :param prefix: Used for resource naming. Will also be the name of the Connect Lambda
        :param api_vpc_config: If provided, the API will be deployed in a VPC.
        :param associate3p_app: Whether to associate the app with the Connect Agent Workspace. Set to false to disable automatic association. Default: true
        :param branding: Set to false to remove CXBuilder branding from the web app. Default: true
        :param global_table: Global table configuration for multi-region deployments. If provided, enables global table support. If undefined, creates a single-region table.
        :param lambda_vpc_config: If provided, the Lambda functions will be deployed in a VPC. Note: VPC should contain endpoints to: CloudFormation, Lambda, DynamoDB, SNS, and Polly.
        :param prod: 
        '''
        if isinstance(env, dict):
            env = _aws_cdk_ceddda9d.Environment(**env)
        if isinstance(cognito, dict):
            cognito = CognitoConfig(**cognito)
        if isinstance(api_vpc_config, dict):
            api_vpc_config = ApiVpcConfig(**api_vpc_config)
        if isinstance(global_table, dict):
            global_table = GlobalTableConfig(**global_table)
        if isinstance(lambda_vpc_config, dict):
            lambda_vpc_config = LambdaVpcConfig(**lambda_vpc_config)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2b448b1e5fee6d3422498d060f9a3329915cc1e9e7bfa74353aacff385ecb459)
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
            check_type(argname="argument alert_emails", value=alert_emails, expected_type=type_hints["alert_emails"])
            check_type(argname="argument cognito", value=cognito, expected_type=type_hints["cognito"])
            check_type(argname="argument connect_instance_arn", value=connect_instance_arn, expected_type=type_hints["connect_instance_arn"])
            check_type(argname="argument prefix", value=prefix, expected_type=type_hints["prefix"])
            check_type(argname="argument api_vpc_config", value=api_vpc_config, expected_type=type_hints["api_vpc_config"])
            check_type(argname="argument associate3p_app", value=associate3p_app, expected_type=type_hints["associate3p_app"])
            check_type(argname="argument branding", value=branding, expected_type=type_hints["branding"])
            check_type(argname="argument global_table", value=global_table, expected_type=type_hints["global_table"])
            check_type(argname="argument lambda_vpc_config", value=lambda_vpc_config, expected_type=type_hints["lambda_vpc_config"])
            check_type(argname="argument prod", value=prod, expected_type=type_hints["prod"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "alert_emails": alert_emails,
            "cognito": cognito,
            "connect_instance_arn": connect_instance_arn,
            "prefix": prefix,
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
        if api_vpc_config is not None:
            self._values["api_vpc_config"] = api_vpc_config
        if associate3p_app is not None:
            self._values["associate3p_app"] = associate3p_app
        if branding is not None:
            self._values["branding"] = branding
        if global_table is not None:
            self._values["global_table"] = global_table
        if lambda_vpc_config is not None:
            self._values["lambda_vpc_config"] = lambda_vpc_config
        if prod is not None:
            self._values["prod"] = prod

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
    def alert_emails(self) -> typing.List[builtins.str]:
        '''Who to notify for unhandled exceptions.'''
        result = self._values.get("alert_emails")
        assert result is not None, "Required property 'alert_emails' is missing"
        return typing.cast(typing.List[builtins.str], result)

    @builtins.property
    def cognito(self) -> CognitoConfig:
        result = self._values.get("cognito")
        assert result is not None, "Required property 'cognito' is missing"
        return typing.cast(CognitoConfig, result)

    @builtins.property
    def connect_instance_arn(self) -> builtins.str:
        result = self._values.get("connect_instance_arn")
        assert result is not None, "Required property 'connect_instance_arn' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def prefix(self) -> builtins.str:
        '''Used for resource naming.

        Will also be the name of the Connect Lambda

        Example::

            `cxbuilder-flow-config`
        '''
        result = self._values.get("prefix")
        assert result is not None, "Required property 'prefix' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def api_vpc_config(self) -> typing.Optional[ApiVpcConfig]:
        '''If provided, the API will be deployed in a VPC.'''
        result = self._values.get("api_vpc_config")
        return typing.cast(typing.Optional[ApiVpcConfig], result)

    @builtins.property
    def associate3p_app(self) -> typing.Optional[builtins.bool]:
        '''Whether to associate the app with the Connect Agent Workspace.

        Set to false to disable automatic association.

        :default: true
        '''
        result = self._values.get("associate3p_app")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def branding(self) -> typing.Optional[builtins.bool]:
        '''Set to false to remove CXBuilder branding from the web app.

        :default: true
        '''
        result = self._values.get("branding")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def global_table(self) -> typing.Optional["GlobalTableConfig"]:
        '''Global table configuration for multi-region deployments.

        If provided, enables global table support.
        If undefined, creates a single-region table.
        '''
        result = self._values.get("global_table")
        return typing.cast(typing.Optional["GlobalTableConfig"], result)

    @builtins.property
    def lambda_vpc_config(self) -> typing.Optional["LambdaVpcConfig"]:
        '''If provided, the Lambda functions will be deployed in a VPC.

        Note: VPC should contain endpoints to: CloudFormation, Lambda, DynamoDB, SNS, and Polly.
        '''
        result = self._values.get("lambda_vpc_config")
        return typing.cast(typing.Optional["LambdaVpcConfig"], result)

    @builtins.property
    def prod(self) -> typing.Optional[builtins.bool]:
        result = self._values.get("prod")
        return typing.cast(typing.Optional[builtins.bool], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "FlowConfigStackProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cxbuilder/flow-config.GlobalTableConfig",
    jsii_struct_bases=[],
    name_mapping={
        "is_primary_region": "isPrimaryRegion",
        "replica_regions": "replicaRegions",
    },
)
class GlobalTableConfig:
    def __init__(
        self,
        *,
        is_primary_region: builtins.bool,
        replica_regions: typing.Optional[typing.Sequence[builtins.str]] = None,
    ) -> None:
        '''Global table configuration for multi-region deployments.

        :param is_primary_region: Whether this is the primary region that creates the global table.
        :param replica_regions: List of all regions that should have replicas Only used by the primary region.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e44cc4281f5eae64096245a9d13eb836449d00688457c301fa74702c291b4582)
            check_type(argname="argument is_primary_region", value=is_primary_region, expected_type=type_hints["is_primary_region"])
            check_type(argname="argument replica_regions", value=replica_regions, expected_type=type_hints["replica_regions"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "is_primary_region": is_primary_region,
        }
        if replica_regions is not None:
            self._values["replica_regions"] = replica_regions

    @builtins.property
    def is_primary_region(self) -> builtins.bool:
        '''Whether this is the primary region that creates the global table.'''
        result = self._values.get("is_primary_region")
        assert result is not None, "Required property 'is_primary_region' is missing"
        return typing.cast(builtins.bool, result)

    @builtins.property
    def replica_regions(self) -> typing.Optional[typing.List[builtins.str]]:
        '''List of all regions that should have replicas Only used by the primary region.'''
        result = self._values.get("replica_regions")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "GlobalTableConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cxbuilder/flow-config.LambdaVpcConfig",
    jsii_struct_bases=[],
    name_mapping={
        "security_group_ids": "securityGroupIds",
        "subnet_ids": "subnetIds",
        "vpc_id": "vpcId",
    },
)
class LambdaVpcConfig:
    def __init__(
        self,
        *,
        security_group_ids: typing.Sequence[builtins.str],
        subnet_ids: typing.Sequence[builtins.str],
        vpc_id: builtins.str,
    ) -> None:
        '''Lambda VPC configuration.

        :param security_group_ids: Security group IDs for Lambda functions.
        :param subnet_ids: Private subnet IDs for Lambda functions.
        :param vpc_id: The VPC ID to deploy resources into.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__dd7e8f9c0a063708d1cda3321e24318104186f7f6a23b62ef5d5cf5a527fd88f)
            check_type(argname="argument security_group_ids", value=security_group_ids, expected_type=type_hints["security_group_ids"])
            check_type(argname="argument subnet_ids", value=subnet_ids, expected_type=type_hints["subnet_ids"])
            check_type(argname="argument vpc_id", value=vpc_id, expected_type=type_hints["vpc_id"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "security_group_ids": security_group_ids,
            "subnet_ids": subnet_ids,
            "vpc_id": vpc_id,
        }

    @builtins.property
    def security_group_ids(self) -> typing.List[builtins.str]:
        '''Security group IDs for Lambda functions.'''
        result = self._values.get("security_group_ids")
        assert result is not None, "Required property 'security_group_ids' is missing"
        return typing.cast(typing.List[builtins.str], result)

    @builtins.property
    def subnet_ids(self) -> typing.List[builtins.str]:
        '''Private subnet IDs for Lambda functions.'''
        result = self._values.get("subnet_ids")
        assert result is not None, "Required property 'subnet_ids' is missing"
        return typing.cast(typing.List[builtins.str], result)

    @builtins.property
    def vpc_id(self) -> builtins.str:
        '''The VPC ID to deploy resources into.'''
        result = self._values.get("vpc_id")
        assert result is not None, "Required property 'vpc_id' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "LambdaVpcConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


__all__ = [
    "ApiVpcConfig",
    "CognitoConfig",
    "FlowConfigStack",
    "FlowConfigStackProps",
    "GlobalTableConfig",
    "LambdaVpcConfig",
]

publication.publish()

def _typecheckingstub__47e62f7d60550c4362367009c9f9b9eeb6c29e12c73fa022b3ca687bcd5825c5(
    *,
    vpc_endpoint_id: builtins.str,
    vpc_id: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8a8d1dc5169a6979db20fa84537dd83b4e39d8f33ae09998177c6901c5402374(
    *,
    domain: builtins.str,
    user_pool_id: builtins.str,
    sso_provider_name: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__98249ce999a2ceaa5c924d743cca4b3c73d1deee69861f65f40468c97af84d0d(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    alert_emails: typing.Sequence[builtins.str],
    cognito: typing.Union[CognitoConfig, typing.Dict[builtins.str, typing.Any]],
    connect_instance_arn: builtins.str,
    prefix: builtins.str,
    api_vpc_config: typing.Optional[typing.Union[ApiVpcConfig, typing.Dict[builtins.str, typing.Any]]] = None,
    associate3p_app: typing.Optional[builtins.bool] = None,
    branding: typing.Optional[builtins.bool] = None,
    global_table: typing.Optional[typing.Union[GlobalTableConfig, typing.Dict[builtins.str, typing.Any]]] = None,
    lambda_vpc_config: typing.Optional[typing.Union[LambdaVpcConfig, typing.Dict[builtins.str, typing.Any]]] = None,
    prod: typing.Optional[builtins.bool] = None,
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

def _typecheckingstub__e09197dd779e78a66d42a90f7cd054fba67453aa0026144aeca380beab52ca7d(
    value: _aws_cdk_aws_sns_ceddda9d.Topic,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a0ea9cf14e71cb22d154a64ad3f2d29e48113e66e457130b87e97d4e33fe174d(
    value: FlowConfigStackProps,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__57a9d04fe3c6a50dfeb0826707097cac273960f16ff4e111cedc4cda8cefc691(
    value: _aws_cdk_aws_dynamodb_ceddda9d.ITable,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e083ade3aee28a14beca2baffec247d997b72f5564c2a07944ba16561beb38cf(
    value: _aws_cdk_aws_cognito_ceddda9d.IUserPool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b4c27a8d9b9492db1bd2cf00de68024d3fbd47d511d1fad5c59bd2267e12b287(
    value: _aws_cdk_aws_cognito_ceddda9d.UserPoolClient,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2b448b1e5fee6d3422498d060f9a3329915cc1e9e7bfa74353aacff385ecb459(
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
    alert_emails: typing.Sequence[builtins.str],
    cognito: typing.Union[CognitoConfig, typing.Dict[builtins.str, typing.Any]],
    connect_instance_arn: builtins.str,
    prefix: builtins.str,
    api_vpc_config: typing.Optional[typing.Union[ApiVpcConfig, typing.Dict[builtins.str, typing.Any]]] = None,
    associate3p_app: typing.Optional[builtins.bool] = None,
    branding: typing.Optional[builtins.bool] = None,
    global_table: typing.Optional[typing.Union[GlobalTableConfig, typing.Dict[builtins.str, typing.Any]]] = None,
    lambda_vpc_config: typing.Optional[typing.Union[LambdaVpcConfig, typing.Dict[builtins.str, typing.Any]]] = None,
    prod: typing.Optional[builtins.bool] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e44cc4281f5eae64096245a9d13eb836449d00688457c301fa74702c291b4582(
    *,
    is_primary_region: builtins.bool,
    replica_regions: typing.Optional[typing.Sequence[builtins.str]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__dd7e8f9c0a063708d1cda3321e24318104186f7f6a23b62ef5d5cf5a527fd88f(
    *,
    security_group_ids: typing.Sequence[builtins.str],
    subnet_ids: typing.Sequence[builtins.str],
    vpc_id: builtins.str,
) -> None:
    """Type checking stubs"""
    pass
