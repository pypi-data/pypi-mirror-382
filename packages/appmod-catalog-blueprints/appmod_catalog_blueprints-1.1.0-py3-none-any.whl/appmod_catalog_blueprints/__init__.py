r'''
# AppMod Use Case Blueprints

Serverless infrastructure components for modern application development. This catalog provides composable building blocks organized by business use cases, enabling rapid deployment of secure, scalable solutions.

## Quick Start

**Deploy a working example in 5 minutes:**

Clone the repository, build the project, then navigate to any example directory and deploy using CDK with your AWS profile and region.

## Core Use Cases

### 1. 📄 Document Processing

Serverless document processing pipeline with AI-powered classification, extraction, and workflow orchestration.

**Architecture:**

```
S3 Upload → SQS → Step Functions → Bedrock Models → DynamoDB
    ↓         ↓         ↓              ↓            ↓
[Storage] [Buffer] [Workflow]    [AI Processing] [Results]
```

**Key Features:**

* **Event-Driven Pipeline**: S3 upload triggers SQS → Step Functions workflow
* **AI-Powered Processing**: Amazon Bedrock for document classification and extraction
* **Multi-format Support**: PDF, JPG, PNG document processing
* **Flexible Workflows**: Base construct with extensible processing steps
* **State Management**: DynamoDB for workflow state and document metadata
* **Error Handling**: Dead letter queues and retry mechanisms with observability

**Available Constructs:**

**BaseDocumentProcessing** - Foundation construct providing:

* S3 bucket with organized prefixes (raw/, processed/, failed/)
* SQS queue with configurable visibility timeout and DLQ
* DynamoDB table for document metadata and workflow state
* Step Functions workflow with customizable processing steps
* Built-in observability and monitoring

**BedrockDocumentProcessing** - AI-powered document analysis:

* Document classification using Claude 3.5 Sonnet
* Entity extraction and content analysis
* Configurable prompts for classification and extraction
* Optional enrichment Lambda function integration
* Automatic workflow state management

**AgenticDocumentProcessing** - Multi-agent document workflows:

* Advanced multi-step processing with agent coordination
* Complex document understanding and analysis
* Configurable agent behaviors and processing flows

### 2. 🌐 Frontend Web Applications

Static web application hosting with CloudFront distribution and security best practices.

**Architecture:**

```
CloudFront → S3 Static Website → Security Headers
     ↓            ↓                    ↓
[Global CDN] [Static Assets]    [Security Functions]
```

**Key Features:**

* **Global Distribution**: CloudFront CDN for low-latency content delivery
* **Security Headers**: Automatic injection of security headers via CloudFront functions
* **SSL/TLS**: Automatic HTTPS with AWS Certificate Manager
* **Custom Domains**: Support for custom domain names with Route 53 integration
* **Error Pages**: Custom 404/403 error page handling
* **Access Logging**: CloudFront access logs for analytics

**Available Constructs:**

**FrontendConstruct** - Complete static website hosting:

* S3 bucket configured for static website hosting
* CloudFront distribution with optimized caching
* Security headers function for OWASP compliance
* Optional custom domain and SSL certificate
* Access logging and monitoring integration

### 3. 📊 Observability & Monitoring

Comprehensive monitoring, logging, and alerting for AWS infrastructure with automatic property injection and Lambda Powertools integration.

**Features:**

* **Property Injection**: Automatic observability configuration across AWS services
* **Lambda Powertools**: Structured logging, metrics, and tracing for Python/Node.js
* **CloudWatch Integration**: Dashboards, alarms, and custom metrics
* **X-Ray Tracing**: End-to-end request flow visualization
* **Bedrock Monitoring**: Specialized observability for Amazon Bedrock workloads
* **Cost Optimization**: Intelligent log retention and metric filtering

**Available Components:**

**Property Injectors:**

* `LambdaObservabilityPropertyInjector` - Auto-enables X-Ray tracing for Lambda functions
* `StateMachineObservabilityPropertyInjector` - Enables logging for Step Functions
* `CloudfrontDistributionObservabilityPropertyInjector` - CDN monitoring and logging

**Observability Constructs:**

* `BedrockObservability` - Comprehensive monitoring for Bedrock workloads with log groups, encryption, and data protection
* `PowertoolsConfig` - Lambda Powertools configuration for structured logging and metrics
* `Observable` interface - Standardized observability contract for constructs

**Data Protection:**

* `LogGroupDataProtectionProps` - Configurable data protection policies for CloudWatch logs

### 4. 🏗️ Foundation & Framework

Core infrastructure components and utilities for building scalable applications.

**Available Components:**

**Network Foundation:**

* `Network` - VPC with public/private subnets, NAT gateways, and security groups
* `AccessLog` - Centralized access logging configuration for AWS services
* `EventBridgeBroker` - Event-driven architecture with custom EventBridge bus

**Utilities:**

* `DataLoader` - Custom resource for loading initial data into databases and services
* `LambdaIamUtils` - Utility functions for Lambda IAM role and policy management
* `DefaultRuntimes` - Standardized Lambda runtime configurations

**Lambda Layers:**

* `DataMasking` - Layer for data masking and PII protection in Lambda functions

## Essential Commands

**Build & Deploy:**

Build entire project with npx projen build. Deploy with specific profile/region using npx cdk deploy --require-approval never. Update CDK CLI if needed with npm install aws-cdk@latest.

**Development:**

Run tests with npm test. Run specific test pattern with npm test -- --testPathPattern="document-processing". Generate CDK Nag compliance reports with npm test -- --testPathPattern="nag.test.ts".

## Repository Structure

```
appmod-usecase-blueprints/
├── use-cases/
│   ├── document-processing/     # Document processing components
│   │   ├── base-document-processing.ts
│   │   ├── bedrock-document-processing.ts
│   │   ├── agentic-document-processing.ts
│   │   ├── resources/          # Lambda functions
│   │   └── tests/              # Unit and CDK Nag tests
│   ├── webapp/                 # Web application components
│   │   ├── frontend-construct.ts
│   │   └── tests/              # Unit and CDK Nag tests
│   ├── framework/              # Core infrastructure
│   │   ├── foundation/         # Network, access logs, EventBridge
│   │   ├── quickstart/         # Base quickstart patterns
│   │   └── custom-resource/    # Default runtimes
│   └── utilities/
│       ├── observability/      # Monitoring components
│       ├── lambda_layers/      # Shared Lambda layers
│       ├── data-loader.ts      # Custom resource for data loading
│       └── lambda-iam-utils.ts # IAM utilities
├── examples/                   # Ready-to-deploy examples
│   └── document-processing/
│       ├── bedrock-document-processing/
│       ├── agentic-document-processing/
│       └── doc-processing-fullstack-webapp/
└── README.md
```

## Security & Compliance

All components include:

* **CDK Nag Integration**: Automated security compliance checking
* **AWS Well-Architected**: Following best practices for security, reliability, performance
* **Encryption**: At-rest and in-transit encryption by default
* **IAM Least Privilege**: Minimal required permissions
* **VPC Isolation**: Private subnets and security groups

**Generate Compliance Reports:**

Run npm test with testPathPattern="nag.test.ts" to generate reports in cdk.out/*-NagReport.csv

## Examples

### Document Processing

* **Bedrock Document Processing**: AI-powered document analysis with Claude 3.5 Sonnet
* **Agentic Document Processing**: Multi-agent document workflows with complex processing
* **Full-Stack Document Processing Webapp**: Complete document processing application with frontend interface

Each example includes deployment scripts, sample files, and comprehensive documentation.

## Key AWS Services

* **Compute**: Lambda, ECS Fargate, Step Functions
* **Storage**: S3, DynamoDB
* **Database**: RDS (MySQL/PostgreSQL)
* **Networking**: VPC, CloudFront, Application Load Balancer
* **AI/ML**: Amazon Bedrock, Textract
* **Monitoring**: CloudWatch, X-Ray
* **Security**: KMS, Secrets Manager, IAM

## Contributing

1. **Add New Use Case**: Create directory under `use-cases/`
2. **Follow Structure**: Include constructs, tests, and documentation
3. **Security First**: All components must pass CDK Nag checks
4. **Include Monitoring**: Include monitoring, error handling, and cost optimization

## Disclaimer

These application solutions are not supported products in their own right, but examples to help our customers use our products from their applications. As our customer, any applications you integrate these examples in should be thoroughly tested, secured, and optimized according to your business's security standards before deploying to production or handling production workloads.

## License

Apache License 2.0 - see [LICENSE](./LICENSE) file for details.
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
import aws_cdk.aws_bedrock as _aws_cdk_aws_bedrock_ceddda9d
import aws_cdk.aws_certificatemanager as _aws_cdk_aws_certificatemanager_ceddda9d
import aws_cdk.aws_cloudfront as _aws_cdk_aws_cloudfront_ceddda9d
import aws_cdk.aws_cloudwatch as _aws_cdk_aws_cloudwatch_ceddda9d
import aws_cdk.aws_dynamodb as _aws_cdk_aws_dynamodb_ceddda9d
import aws_cdk.aws_ec2 as _aws_cdk_aws_ec2_ceddda9d
import aws_cdk.aws_events as _aws_cdk_aws_events_ceddda9d
import aws_cdk.aws_iam as _aws_cdk_aws_iam_ceddda9d
import aws_cdk.aws_kms as _aws_cdk_aws_kms_ceddda9d
import aws_cdk.aws_lambda as _aws_cdk_aws_lambda_ceddda9d
import aws_cdk.aws_lambda_python_alpha as _aws_cdk_aws_lambda_python_alpha_49328424
import aws_cdk.aws_logs as _aws_cdk_aws_logs_ceddda9d
import aws_cdk.aws_rds as _aws_cdk_aws_rds_ceddda9d
import aws_cdk.aws_route53 as _aws_cdk_aws_route53_ceddda9d
import aws_cdk.aws_s3 as _aws_cdk_aws_s3_ceddda9d
import aws_cdk.aws_s3_assets as _aws_cdk_aws_s3_assets_ceddda9d
import aws_cdk.aws_s3_deployment as _aws_cdk_aws_s3_deployment_ceddda9d
import aws_cdk.aws_secretsmanager as _aws_cdk_aws_secretsmanager_ceddda9d
import aws_cdk.aws_stepfunctions as _aws_cdk_aws_stepfunctions_ceddda9d
import aws_cdk.aws_stepfunctions_tasks as _aws_cdk_aws_stepfunctions_tasks_ceddda9d
import aws_cdk.custom_resources as _aws_cdk_custom_resources_ceddda9d
import constructs as _constructs_77d1e7e8


class AccessLog(
    _constructs_77d1e7e8.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdklabs/cdk-appmod-catalog-blueprints.AccessLog",
):
    '''(experimental) AccessLog construct that provides a centralized S3 bucket for storing access logs.

    This construct creates a secure S3 bucket with appropriate policies for AWS services
    to deliver access logs.

    Usage:

    const accessLog = new AccessLog(this, 'AccessLog');
    const bucket = accessLog.bucket;
    const bucketName = accessLog.bucketName;

    :stability: experimental
    '''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        bucket_name: typing.Optional[builtins.str] = None,
        bucket_prefix: typing.Optional[builtins.str] = None,
        lifecycle_rules: typing.Optional[typing.Sequence[typing.Union[_aws_cdk_aws_s3_ceddda9d.LifecycleRule, typing.Dict[builtins.str, typing.Any]]]] = None,
        versioned: typing.Optional[builtins.bool] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param bucket_name: (experimental) The name of the S3 bucket for access logs. Default: 'access-logs'
        :param bucket_prefix: (experimental) Custom bucket prefix for organizing access logs. Default: 'access-logs'
        :param lifecycle_rules: (experimental) Lifecycle rules for the access logs. Default: Transition to IA after 30 days, delete after 90 days
        :param versioned: (experimental) Whether to enable versioning on the access logs bucket. Default: false

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d0c79880c62971c0b94c27211aa57e94a14b8b594133479abb3588b22b301cf7)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = AccessLogProps(
            bucket_name=bucket_name,
            bucket_prefix=bucket_prefix,
            lifecycle_rules=lifecycle_rules,
            versioned=versioned,
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @jsii.member(jsii_name="getLogPath")
    def get_log_path(
        self,
        service_name: builtins.str,
        resource_name: typing.Optional[builtins.str] = None,
    ) -> builtins.str:
        '''(experimental) Get the S3 bucket path for a specific service's access logs.

        :param service_name: The name of the service (e.g., 'alb', 'cloudfront', 's3').
        :param resource_name: Optional resource name for further organization.

        :return: The S3 path for the service's access logs

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__bb3bab7dfdf58893d762b8a3579b2e248b758bf8db791e3986df9451e32ada3e)
            check_type(argname="argument service_name", value=service_name, expected_type=type_hints["service_name"])
            check_type(argname="argument resource_name", value=resource_name, expected_type=type_hints["resource_name"])
        return typing.cast(builtins.str, jsii.invoke(self, "getLogPath", [service_name, resource_name]))

    @jsii.member(jsii_name="getLogUri")
    def get_log_uri(
        self,
        service_name: builtins.str,
        resource_name: typing.Optional[builtins.str] = None,
    ) -> builtins.str:
        '''(experimental) Get the S3 URI for a specific service's access logs.

        :param service_name: The name of the service (e.g., 'alb', 'cloudfront', 's3').
        :param resource_name: Optional resource name for further organization.

        :return: The S3 URI for the service's access logs

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9988cc2b7efe7f7c7c17c94e465c36241770aa21cbe1b07c110b8e2dacedaf59)
            check_type(argname="argument service_name", value=service_name, expected_type=type_hints["service_name"])
            check_type(argname="argument resource_name", value=resource_name, expected_type=type_hints["resource_name"])
        return typing.cast(builtins.str, jsii.invoke(self, "getLogUri", [service_name, resource_name]))

    @builtins.property
    @jsii.member(jsii_name="bucket")
    def bucket(self) -> _aws_cdk_aws_s3_ceddda9d.Bucket:
        '''(experimental) The S3 bucket for storing access logs.

        :stability: experimental
        '''
        return typing.cast(_aws_cdk_aws_s3_ceddda9d.Bucket, jsii.get(self, "bucket"))

    @builtins.property
    @jsii.member(jsii_name="bucketName")
    def bucket_name(self) -> builtins.str:
        '''(experimental) The name of the S3 bucket.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "bucketName"))

    @builtins.property
    @jsii.member(jsii_name="bucketPrefix")
    def bucket_prefix(self) -> builtins.str:
        '''(experimental) The bucket prefix used for organizing access logs.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "bucketPrefix"))


@jsii.data_type(
    jsii_type="@cdklabs/cdk-appmod-catalog-blueprints.AccessLogProps",
    jsii_struct_bases=[],
    name_mapping={
        "bucket_name": "bucketName",
        "bucket_prefix": "bucketPrefix",
        "lifecycle_rules": "lifecycleRules",
        "versioned": "versioned",
    },
)
class AccessLogProps:
    def __init__(
        self,
        *,
        bucket_name: typing.Optional[builtins.str] = None,
        bucket_prefix: typing.Optional[builtins.str] = None,
        lifecycle_rules: typing.Optional[typing.Sequence[typing.Union[_aws_cdk_aws_s3_ceddda9d.LifecycleRule, typing.Dict[builtins.str, typing.Any]]]] = None,
        versioned: typing.Optional[builtins.bool] = None,
    ) -> None:
        '''(experimental) Configuration options for the AccessLog construct.

        :param bucket_name: (experimental) The name of the S3 bucket for access logs. Default: 'access-logs'
        :param bucket_prefix: (experimental) Custom bucket prefix for organizing access logs. Default: 'access-logs'
        :param lifecycle_rules: (experimental) Lifecycle rules for the access logs. Default: Transition to IA after 30 days, delete after 90 days
        :param versioned: (experimental) Whether to enable versioning on the access logs bucket. Default: false

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b0d5807bf69e9243b9fd452b7437cfe9f4102d78752673f223f3ae14073937e1)
            check_type(argname="argument bucket_name", value=bucket_name, expected_type=type_hints["bucket_name"])
            check_type(argname="argument bucket_prefix", value=bucket_prefix, expected_type=type_hints["bucket_prefix"])
            check_type(argname="argument lifecycle_rules", value=lifecycle_rules, expected_type=type_hints["lifecycle_rules"])
            check_type(argname="argument versioned", value=versioned, expected_type=type_hints["versioned"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if bucket_name is not None:
            self._values["bucket_name"] = bucket_name
        if bucket_prefix is not None:
            self._values["bucket_prefix"] = bucket_prefix
        if lifecycle_rules is not None:
            self._values["lifecycle_rules"] = lifecycle_rules
        if versioned is not None:
            self._values["versioned"] = versioned

    @builtins.property
    def bucket_name(self) -> typing.Optional[builtins.str]:
        '''(experimental) The name of the S3 bucket for access logs.

        :default: 'access-logs'

        :stability: experimental
        '''
        result = self._values.get("bucket_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def bucket_prefix(self) -> typing.Optional[builtins.str]:
        '''(experimental) Custom bucket prefix for organizing access logs.

        :default: 'access-logs'

        :stability: experimental
        '''
        result = self._values.get("bucket_prefix")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def lifecycle_rules(
        self,
    ) -> typing.Optional[typing.List[_aws_cdk_aws_s3_ceddda9d.LifecycleRule]]:
        '''(experimental) Lifecycle rules for the access logs.

        :default: Transition to IA after 30 days, delete after 90 days

        :stability: experimental
        '''
        result = self._values.get("lifecycle_rules")
        return typing.cast(typing.Optional[typing.List[_aws_cdk_aws_s3_ceddda9d.LifecycleRule]], result)

    @builtins.property
    def versioned(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Whether to enable versioning on the access logs bucket.

        :default: false

        :stability: experimental
        '''
        result = self._values.get("versioned")
        return typing.cast(typing.Optional[builtins.bool], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "AccessLogProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdklabs/cdk-appmod-catalog-blueprints.AdditionalDistributionProps",
    jsii_struct_bases=[],
    name_mapping={
        "comment": "comment",
        "enabled": "enabled",
        "price_class": "priceClass",
        "web_acl_id": "webAclId",
    },
)
class AdditionalDistributionProps:
    def __init__(
        self,
        *,
        comment: typing.Optional[builtins.str] = None,
        enabled: typing.Optional[builtins.bool] = None,
        price_class: typing.Optional[_aws_cdk_aws_cloudfront_ceddda9d.PriceClass] = None,
        web_acl_id: typing.Optional[builtins.str] = None,
    ) -> None:
        '''(experimental) Additional CloudFront distribution properties.

        :param comment: (experimental) Optional comment for the distribution.
        :param enabled: (experimental) Optional enabled flag for the distribution.
        :param price_class: (experimental) Optional price class for the distribution.
        :param web_acl_id: (experimental) Optional web ACL ID for the distribution.

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__14d3ed5928e5166082cd47a907ab754473c20bb045dc424135b4690811543601)
            check_type(argname="argument comment", value=comment, expected_type=type_hints["comment"])
            check_type(argname="argument enabled", value=enabled, expected_type=type_hints["enabled"])
            check_type(argname="argument price_class", value=price_class, expected_type=type_hints["price_class"])
            check_type(argname="argument web_acl_id", value=web_acl_id, expected_type=type_hints["web_acl_id"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if comment is not None:
            self._values["comment"] = comment
        if enabled is not None:
            self._values["enabled"] = enabled
        if price_class is not None:
            self._values["price_class"] = price_class
        if web_acl_id is not None:
            self._values["web_acl_id"] = web_acl_id

    @builtins.property
    def comment(self) -> typing.Optional[builtins.str]:
        '''(experimental) Optional comment for the distribution.

        :stability: experimental
        '''
        result = self._values.get("comment")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def enabled(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Optional enabled flag for the distribution.

        :stability: experimental
        '''
        result = self._values.get("enabled")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def price_class(
        self,
    ) -> typing.Optional[_aws_cdk_aws_cloudfront_ceddda9d.PriceClass]:
        '''(experimental) Optional price class for the distribution.

        :stability: experimental
        '''
        result = self._values.get("price_class")
        return typing.cast(typing.Optional[_aws_cdk_aws_cloudfront_ceddda9d.PriceClass], result)

    @builtins.property
    def web_acl_id(self) -> typing.Optional[builtins.str]:
        '''(experimental) Optional web ACL ID for the distribution.

        :stability: experimental
        '''
        result = self._values.get("web_acl_id")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "AdditionalDistributionProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdklabs/cdk-appmod-catalog-blueprints.AgentProps",
    jsii_struct_bases=[],
    name_mapping={
        "agent_system_prompt": "agentSystemPrompt",
        "lambda_layers": "lambdaLayers",
        "tools_bucket": "toolsBucket",
        "tools_location": "toolsLocation",
    },
)
class AgentProps:
    def __init__(
        self,
        *,
        agent_system_prompt: typing.Optional[builtins.str] = None,
        lambda_layers: typing.Optional[typing.Sequence[_aws_cdk_aws_lambda_ceddda9d.LayerVersion]] = None,
        tools_bucket: typing.Optional[_aws_cdk_aws_s3_ceddda9d.Bucket] = None,
        tools_location: typing.Optional[typing.Sequence[builtins.str]] = None,
    ) -> None:
        '''
        :param agent_system_prompt: (experimental) System prompt for the agent.
        :param lambda_layers: (experimental) If there are python dependencies that are needed by the provided tools, provide the Lambda Layers with the dependencies.
        :param tools_bucket: (experimental) Bucket where the tools are located in Primarily use to grant read permission to the processing agent to access the tools. Default: No extra IAM permissions would be automatically assigned to the processing agent.
        :param tools_location: (experimental) S3 path where the tools are located. The agent would dynamically load the tools

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e1a82500ee072f393cd9a2ada2f9a3434219c7a51186f26fbba3061bd896d11e)
            check_type(argname="argument agent_system_prompt", value=agent_system_prompt, expected_type=type_hints["agent_system_prompt"])
            check_type(argname="argument lambda_layers", value=lambda_layers, expected_type=type_hints["lambda_layers"])
            check_type(argname="argument tools_bucket", value=tools_bucket, expected_type=type_hints["tools_bucket"])
            check_type(argname="argument tools_location", value=tools_location, expected_type=type_hints["tools_location"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if agent_system_prompt is not None:
            self._values["agent_system_prompt"] = agent_system_prompt
        if lambda_layers is not None:
            self._values["lambda_layers"] = lambda_layers
        if tools_bucket is not None:
            self._values["tools_bucket"] = tools_bucket
        if tools_location is not None:
            self._values["tools_location"] = tools_location

    @builtins.property
    def agent_system_prompt(self) -> typing.Optional[builtins.str]:
        '''(experimental) System prompt for the agent.

        :stability: experimental
        '''
        result = self._values.get("agent_system_prompt")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def lambda_layers(
        self,
    ) -> typing.Optional[typing.List[_aws_cdk_aws_lambda_ceddda9d.LayerVersion]]:
        '''(experimental) If there are python dependencies that are needed by the provided tools, provide the Lambda Layers with the dependencies.

        :stability: experimental
        '''
        result = self._values.get("lambda_layers")
        return typing.cast(typing.Optional[typing.List[_aws_cdk_aws_lambda_ceddda9d.LayerVersion]], result)

    @builtins.property
    def tools_bucket(self) -> typing.Optional[_aws_cdk_aws_s3_ceddda9d.Bucket]:
        '''(experimental) Bucket where the tools are located in Primarily use to grant read permission to the processing agent to access the tools.

        :default:

        No extra IAM permissions would be automatically
        assigned to the processing agent.

        :stability: experimental
        '''
        result = self._values.get("tools_bucket")
        return typing.cast(typing.Optional[_aws_cdk_aws_s3_ceddda9d.Bucket], result)

    @builtins.property
    def tools_location(self) -> typing.Optional[typing.List[builtins.str]]:
        '''(experimental) S3 path where the tools are located.

        The agent would dynamically load the tools

        :stability: experimental
        '''
        result = self._values.get("tools_location")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "AgentProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.enum(
    jsii_type="@cdklabs/cdk-appmod-catalog-blueprints.BedrockCrossRegionInferencePrefix"
)
class BedrockCrossRegionInferencePrefix(enum.Enum):
    '''(experimental) Cross-region inference prefix options for Bedrock models.

    Used to configure inference profiles for improved availability and performance.

    :stability: experimental
    '''

    US = "US"
    '''(experimental) US-based cross-region inference profile.

    :stability: experimental
    '''
    EU = "EU"
    '''(experimental) EU-based cross-region inference profile.

    :stability: experimental
    '''


@jsii.implements(_aws_cdk_ceddda9d.IPropertyInjector)
class CloudfrontDistributionObservabilityPropertyInjector(
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdklabs/cdk-appmod-catalog-blueprints.CloudfrontDistributionObservabilityPropertyInjector",
):
    '''
    :stability: experimental
    '''

    def __init__(self) -> None:
        '''
        :stability: experimental
        '''
        jsii.create(self.__class__, self, [])

    @jsii.member(jsii_name="inject")
    def inject(
        self,
        original_props: typing.Any,
        *,
        id: builtins.str,
        scope: _constructs_77d1e7e8.Construct,
    ) -> typing.Any:
        '''(experimental) The injector to be applied to the constructor properties of the Construct.

        :param original_props: -
        :param id: id from the Construct constructor.
        :param scope: scope from the constructor.

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2270aedab8c9db027e16b28fd9de8610d0f7e47778cdf1d501539d0e440a561d)
            check_type(argname="argument original_props", value=original_props, expected_type=type_hints["original_props"])
        context = _aws_cdk_ceddda9d.InjectionContext(id=id, scope=scope)

        return typing.cast(typing.Any, jsii.invoke(self, "inject", [original_props, context]))

    @builtins.property
    @jsii.member(jsii_name="constructUniqueId")
    def construct_unique_id(self) -> builtins.str:
        '''(experimental) The unique Id of the Construct class.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "constructUniqueId"))


@jsii.data_type(
    jsii_type="@cdklabs/cdk-appmod-catalog-blueprints.CustomDomainConfig",
    jsii_struct_bases=[],
    name_mapping={
        "certificate": "certificate",
        "domain_name": "domainName",
        "hosted_zone": "hostedZone",
    },
)
class CustomDomainConfig:
    def __init__(
        self,
        *,
        certificate: _aws_cdk_aws_certificatemanager_ceddda9d.ICertificate,
        domain_name: builtins.str,
        hosted_zone: typing.Optional[_aws_cdk_aws_route53_ceddda9d.IHostedZone] = None,
    ) -> None:
        '''(experimental) Custom domain configuration for the frontend.

        :param certificate: (experimental) SSL certificate for the domain (required when domainName is provided).
        :param domain_name: (experimental) Domain name for the frontend (e.g., 'app.example.com').
        :param hosted_zone: (experimental) Optional hosted zone for automatic DNS record creation.

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__45e622c5dc8075e1ee5cdf9df72ea9b7ca33e0a7cf348dfaf54f93e635e9dde8)
            check_type(argname="argument certificate", value=certificate, expected_type=type_hints["certificate"])
            check_type(argname="argument domain_name", value=domain_name, expected_type=type_hints["domain_name"])
            check_type(argname="argument hosted_zone", value=hosted_zone, expected_type=type_hints["hosted_zone"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "certificate": certificate,
            "domain_name": domain_name,
        }
        if hosted_zone is not None:
            self._values["hosted_zone"] = hosted_zone

    @builtins.property
    def certificate(self) -> _aws_cdk_aws_certificatemanager_ceddda9d.ICertificate:
        '''(experimental) SSL certificate for the domain (required when domainName is provided).

        :stability: experimental
        '''
        result = self._values.get("certificate")
        assert result is not None, "Required property 'certificate' is missing"
        return typing.cast(_aws_cdk_aws_certificatemanager_ceddda9d.ICertificate, result)

    @builtins.property
    def domain_name(self) -> builtins.str:
        '''(experimental) Domain name for the frontend (e.g., 'app.example.com').

        :stability: experimental
        '''
        result = self._values.get("domain_name")
        assert result is not None, "Required property 'domain_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def hosted_zone(self) -> typing.Optional[_aws_cdk_aws_route53_ceddda9d.IHostedZone]:
        '''(experimental) Optional hosted zone for automatic DNS record creation.

        :stability: experimental
        '''
        result = self._values.get("hosted_zone")
        return typing.cast(typing.Optional[_aws_cdk_aws_route53_ceddda9d.IHostedZone], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CustomDomainConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataLoader(
    _constructs_77d1e7e8.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdklabs/cdk-appmod-catalog-blueprints.DataLoader",
):
    '''(experimental) DataLoader construct for loading data into Aurora/RDS databases.

    This construct provides a simplified solution for loading data from various file formats
    (SQL, mysqldump, pg_dump) into MySQL or PostgreSQL databases. It uses S3 for file storage,
    Step Functions for orchestration, and Lambda for processing.

    Architecture:

    1. Files are uploaded to S3 bucket
    2. Step Function is triggered with list of S3 keys
    3. Step Function iterates over files in execution order
    4. Lambda function processes each file against the database

    Example usage:
    Create a DataLoader with database configuration and file inputs.
    The construct will handle uploading files to S3, creating a Step Function
    to orchestrate processing, and executing the data loading pipeline.

    :stability: experimental
    '''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        database_config: typing.Union["DatabaseConfig", typing.Dict[builtins.str, typing.Any]],
        file_inputs: typing.Sequence[typing.Union["FileInput", typing.Dict[builtins.str, typing.Any]]],
        memory_size: typing.Optional[jsii.Number] = None,
        removal_policy: typing.Optional[_aws_cdk_ceddda9d.RemovalPolicy] = None,
        timeout: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param database_config: (experimental) Database configuration.
        :param file_inputs: (experimental) List of files to load.
        :param memory_size: (experimental) Optional memory size for Lambda function (defaults to 1024 MB).
        :param removal_policy: (experimental) Optional removal policy for resources (defaults to DESTROY).
        :param timeout: (experimental) Optional timeout for Lambda function (defaults to 15 minutes).

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__270a76813d598a503e52c71a882567ace4b31275076ba0bcefcc5ff1011d5018)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = DataLoaderProps(
            database_config=database_config,
            file_inputs=file_inputs,
            memory_size=memory_size,
            removal_policy=removal_policy,
            timeout=timeout,
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @jsii.member(jsii_name="grantExecutionTriggerPermissions")
    def grant_execution_trigger_permissions(
        self,
        statement: _aws_cdk_aws_iam_ceddda9d.PolicyStatement,
    ) -> None:
        '''(experimental) Grants additional IAM permissions to the execution trigger Lambda function.

        :param statement: The IAM policy statement to add.

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__efd46917d5b396c28d8f6ffeea52cc31230f92bb12d3a0b916d59526a781140a)
            check_type(argname="argument statement", value=statement, expected_type=type_hints["statement"])
        return typing.cast(None, jsii.invoke(self, "grantExecutionTriggerPermissions", [statement]))

    @builtins.property
    @jsii.member(jsii_name="bucket")
    def bucket(self) -> _aws_cdk_aws_s3_ceddda9d.Bucket:
        '''(experimental) The S3 bucket used for storing files.

        :stability: experimental
        '''
        return typing.cast(_aws_cdk_aws_s3_ceddda9d.Bucket, jsii.get(self, "bucket"))

    @builtins.property
    @jsii.member(jsii_name="customResourceProvider")
    def custom_resource_provider(self) -> _aws_cdk_custom_resources_ceddda9d.Provider:
        '''(experimental) The custom resource provider for triggering state machine execution.

        :stability: experimental
        '''
        return typing.cast(_aws_cdk_custom_resources_ceddda9d.Provider, jsii.get(self, "customResourceProvider"))

    @builtins.property
    @jsii.member(jsii_name="executionTrigger")
    def execution_trigger(self) -> _aws_cdk_ceddda9d.CustomResource:
        '''(experimental) The custom resource that triggers the state machine.

        :stability: experimental
        '''
        return typing.cast(_aws_cdk_ceddda9d.CustomResource, jsii.get(self, "executionTrigger"))

    @builtins.property
    @jsii.member(jsii_name="processorFunction")
    def processor_function(self) -> _aws_cdk_aws_lambda_ceddda9d.Function:
        '''(experimental) The Lambda function that processes the data loading.

        :stability: experimental
        '''
        return typing.cast(_aws_cdk_aws_lambda_ceddda9d.Function, jsii.get(self, "processorFunction"))

    @builtins.property
    @jsii.member(jsii_name="stateMachine")
    def state_machine(self) -> _aws_cdk_aws_stepfunctions_ceddda9d.StateMachine:
        '''(experimental) The Step Functions state machine for orchestration.

        :stability: experimental
        '''
        return typing.cast(_aws_cdk_aws_stepfunctions_ceddda9d.StateMachine, jsii.get(self, "stateMachine"))

    @builtins.property
    @jsii.member(jsii_name="bucketDeployment")
    def bucket_deployment(
        self,
    ) -> typing.Optional[_aws_cdk_aws_s3_deployment_ceddda9d.BucketDeployment]:
        '''(experimental) The bucket deployment for uploading files.

        :stability: experimental
        '''
        return typing.cast(typing.Optional[_aws_cdk_aws_s3_deployment_ceddda9d.BucketDeployment], jsii.get(self, "bucketDeployment"))

    @bucket_deployment.setter
    def bucket_deployment(
        self,
        value: typing.Optional[_aws_cdk_aws_s3_deployment_ceddda9d.BucketDeployment],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__cd063a11debecd44b792418fb4aa1f7320d173a2fbc3280588266e303321f59e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "bucketDeployment", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdklabs/cdk-appmod-catalog-blueprints.DataLoaderProps",
    jsii_struct_bases=[],
    name_mapping={
        "database_config": "databaseConfig",
        "file_inputs": "fileInputs",
        "memory_size": "memorySize",
        "removal_policy": "removalPolicy",
        "timeout": "timeout",
    },
)
class DataLoaderProps:
    def __init__(
        self,
        *,
        database_config: typing.Union["DatabaseConfig", typing.Dict[builtins.str, typing.Any]],
        file_inputs: typing.Sequence[typing.Union["FileInput", typing.Dict[builtins.str, typing.Any]]],
        memory_size: typing.Optional[jsii.Number] = None,
        removal_policy: typing.Optional[_aws_cdk_ceddda9d.RemovalPolicy] = None,
        timeout: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
    ) -> None:
        '''(experimental) Properties for the DataLoader construct.

        :param database_config: (experimental) Database configuration.
        :param file_inputs: (experimental) List of files to load.
        :param memory_size: (experimental) Optional memory size for Lambda function (defaults to 1024 MB).
        :param removal_policy: (experimental) Optional removal policy for resources (defaults to DESTROY).
        :param timeout: (experimental) Optional timeout for Lambda function (defaults to 15 minutes).

        :stability: experimental
        '''
        if isinstance(database_config, dict):
            database_config = DatabaseConfig(**database_config)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__79385aca2a5a0bb7a2e64dbdad2106a739cca7fbad6670895f995ed402f5a8fe)
            check_type(argname="argument database_config", value=database_config, expected_type=type_hints["database_config"])
            check_type(argname="argument file_inputs", value=file_inputs, expected_type=type_hints["file_inputs"])
            check_type(argname="argument memory_size", value=memory_size, expected_type=type_hints["memory_size"])
            check_type(argname="argument removal_policy", value=removal_policy, expected_type=type_hints["removal_policy"])
            check_type(argname="argument timeout", value=timeout, expected_type=type_hints["timeout"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "database_config": database_config,
            "file_inputs": file_inputs,
        }
        if memory_size is not None:
            self._values["memory_size"] = memory_size
        if removal_policy is not None:
            self._values["removal_policy"] = removal_policy
        if timeout is not None:
            self._values["timeout"] = timeout

    @builtins.property
    def database_config(self) -> "DatabaseConfig":
        '''(experimental) Database configuration.

        :stability: experimental
        '''
        result = self._values.get("database_config")
        assert result is not None, "Required property 'database_config' is missing"
        return typing.cast("DatabaseConfig", result)

    @builtins.property
    def file_inputs(self) -> typing.List["FileInput"]:
        '''(experimental) List of files to load.

        :stability: experimental
        '''
        result = self._values.get("file_inputs")
        assert result is not None, "Required property 'file_inputs' is missing"
        return typing.cast(typing.List["FileInput"], result)

    @builtins.property
    def memory_size(self) -> typing.Optional[jsii.Number]:
        '''(experimental) Optional memory size for Lambda function (defaults to 1024 MB).

        :stability: experimental
        '''
        result = self._values.get("memory_size")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def removal_policy(self) -> typing.Optional[_aws_cdk_ceddda9d.RemovalPolicy]:
        '''(experimental) Optional removal policy for resources (defaults to DESTROY).

        :stability: experimental
        '''
        result = self._values.get("removal_policy")
        return typing.cast(typing.Optional[_aws_cdk_ceddda9d.RemovalPolicy], result)

    @builtins.property
    def timeout(self) -> typing.Optional[_aws_cdk_ceddda9d.Duration]:
        '''(experimental) Optional timeout for Lambda function (defaults to 15 minutes).

        :stability: experimental
        '''
        result = self._values.get("timeout")
        return typing.cast(typing.Optional[_aws_cdk_ceddda9d.Duration], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataLoaderProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdklabs/cdk-appmod-catalog-blueprints.DatabaseConfig",
    jsii_struct_bases=[],
    name_mapping={
        "database_name": "databaseName",
        "engine": "engine",
        "secret": "secret",
        "security_group": "securityGroup",
        "vpc": "vpc",
        "cluster": "cluster",
        "instance": "instance",
    },
)
class DatabaseConfig:
    def __init__(
        self,
        *,
        database_name: builtins.str,
        engine: "DatabaseEngine",
        secret: _aws_cdk_aws_secretsmanager_ceddda9d.ISecret,
        security_group: _aws_cdk_aws_ec2_ceddda9d.ISecurityGroup,
        vpc: _aws_cdk_aws_ec2_ceddda9d.IVpc,
        cluster: typing.Optional[_aws_cdk_aws_rds_ceddda9d.IDatabaseCluster] = None,
        instance: typing.Optional[_aws_cdk_aws_rds_ceddda9d.IDatabaseInstance] = None,
    ) -> None:
        '''(experimental) Database connection configuration.

        :param database_name: (experimental) Database name to connect to.
        :param engine: (experimental) Database engine type.
        :param secret: (experimental) Database credentials secret.
        :param security_group: (experimental) Security group for database access.
        :param vpc: (experimental) VPC where the database is located.
        :param cluster: (experimental) Database cluster (for Aurora).
        :param instance: (experimental) Database instance (for RDS).

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__28429cd4673598c14d3b2db601f7758c41a1c9972a1d3aeb36a73a6d7afffe94)
            check_type(argname="argument database_name", value=database_name, expected_type=type_hints["database_name"])
            check_type(argname="argument engine", value=engine, expected_type=type_hints["engine"])
            check_type(argname="argument secret", value=secret, expected_type=type_hints["secret"])
            check_type(argname="argument security_group", value=security_group, expected_type=type_hints["security_group"])
            check_type(argname="argument vpc", value=vpc, expected_type=type_hints["vpc"])
            check_type(argname="argument cluster", value=cluster, expected_type=type_hints["cluster"])
            check_type(argname="argument instance", value=instance, expected_type=type_hints["instance"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "database_name": database_name,
            "engine": engine,
            "secret": secret,
            "security_group": security_group,
            "vpc": vpc,
        }
        if cluster is not None:
            self._values["cluster"] = cluster
        if instance is not None:
            self._values["instance"] = instance

    @builtins.property
    def database_name(self) -> builtins.str:
        '''(experimental) Database name to connect to.

        :stability: experimental
        '''
        result = self._values.get("database_name")
        assert result is not None, "Required property 'database_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def engine(self) -> "DatabaseEngine":
        '''(experimental) Database engine type.

        :stability: experimental
        '''
        result = self._values.get("engine")
        assert result is not None, "Required property 'engine' is missing"
        return typing.cast("DatabaseEngine", result)

    @builtins.property
    def secret(self) -> _aws_cdk_aws_secretsmanager_ceddda9d.ISecret:
        '''(experimental) Database credentials secret.

        :stability: experimental
        '''
        result = self._values.get("secret")
        assert result is not None, "Required property 'secret' is missing"
        return typing.cast(_aws_cdk_aws_secretsmanager_ceddda9d.ISecret, result)

    @builtins.property
    def security_group(self) -> _aws_cdk_aws_ec2_ceddda9d.ISecurityGroup:
        '''(experimental) Security group for database access.

        :stability: experimental
        '''
        result = self._values.get("security_group")
        assert result is not None, "Required property 'security_group' is missing"
        return typing.cast(_aws_cdk_aws_ec2_ceddda9d.ISecurityGroup, result)

    @builtins.property
    def vpc(self) -> _aws_cdk_aws_ec2_ceddda9d.IVpc:
        '''(experimental) VPC where the database is located.

        :stability: experimental
        '''
        result = self._values.get("vpc")
        assert result is not None, "Required property 'vpc' is missing"
        return typing.cast(_aws_cdk_aws_ec2_ceddda9d.IVpc, result)

    @builtins.property
    def cluster(self) -> typing.Optional[_aws_cdk_aws_rds_ceddda9d.IDatabaseCluster]:
        '''(experimental) Database cluster (for Aurora).

        :stability: experimental
        '''
        result = self._values.get("cluster")
        return typing.cast(typing.Optional[_aws_cdk_aws_rds_ceddda9d.IDatabaseCluster], result)

    @builtins.property
    def instance(self) -> typing.Optional[_aws_cdk_aws_rds_ceddda9d.IDatabaseInstance]:
        '''(experimental) Database instance (for RDS).

        :stability: experimental
        '''
        result = self._values.get("instance")
        return typing.cast(typing.Optional[_aws_cdk_aws_rds_ceddda9d.IDatabaseInstance], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DatabaseConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.enum(jsii_type="@cdklabs/cdk-appmod-catalog-blueprints.DatabaseEngine")
class DatabaseEngine(enum.Enum):
    '''(experimental) Supported database engines.

    :stability: experimental
    '''

    MYSQL = "MYSQL"
    '''
    :stability: experimental
    '''
    POSTGRESQL = "POSTGRESQL"
    '''
    :stability: experimental
    '''


class DefaultDocumentProcessingConfig(
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdklabs/cdk-appmod-catalog-blueprints.DefaultDocumentProcessingConfig",
):
    '''
    :stability: experimental
    '''

    def __init__(self) -> None:
        '''
        :stability: experimental
        '''
        jsii.create(self.__class__, self, [])

    @jsii.python.classproperty
    @jsii.member(jsii_name="DEFAULT_OBSERVABILITY_METRIC_SVC_NAME")
    def DEFAULT_OBSERVABILITY_METRIC_SVC_NAME(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "DEFAULT_OBSERVABILITY_METRIC_SVC_NAME"))


class DefaultObservabilityConfig(
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdklabs/cdk-appmod-catalog-blueprints.DefaultObservabilityConfig",
):
    '''(experimental) Contains default constants for Observability related configuration.

    :stability: experimental
    '''

    def __init__(self) -> None:
        '''
        :stability: experimental
        '''
        jsii.create(self.__class__, self, [])

    @jsii.python.classproperty
    @jsii.member(jsii_name="DEFAULT_METRIC_NAMESPACE")
    def DEFAULT_METRIC_NAMESPACE(cls) -> builtins.str:
        '''(experimental) Default namespace for powertools.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "DEFAULT_METRIC_NAMESPACE"))


class DefaultRuntimes(
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdklabs/cdk-appmod-catalog-blueprints.DefaultRuntimes",
):
    '''(experimental) Contains default runtimes that would be referenced by Lambda functions in the various use cases.

    Updating of
    Runtime versions should be done here.

    :stability: experimental
    '''

    def __init__(self) -> None:
        '''
        :stability: experimental
        '''
        jsii.create(self.__class__, self, [])

    @jsii.python.classproperty
    @jsii.member(jsii_name="NODEJS")
    def NODEJS(cls) -> _aws_cdk_aws_lambda_ceddda9d.Runtime:
        '''(experimental) Default runtime for all Lambda functions in the use cases.

        :stability: experimental
        '''
        return typing.cast(_aws_cdk_aws_lambda_ceddda9d.Runtime, jsii.sget(cls, "NODEJS"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="PYTHON")
    def PYTHON(cls) -> _aws_cdk_aws_lambda_ceddda9d.Runtime:
        '''(experimental) Default runtime for Python based Lambda functions.

        :stability: experimental
        '''
        return typing.cast(_aws_cdk_aws_lambda_ceddda9d.Runtime, jsii.sget(cls, "PYTHON"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="PYTHON_BUNDLING_IMAGE")
    def PYTHON_BUNDLING_IMAGE(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "PYTHON_BUNDLING_IMAGE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="PYTHON_FUNCTION_BUNDLING")
    def PYTHON_FUNCTION_BUNDLING(
        cls,
    ) -> _aws_cdk_aws_lambda_python_alpha_49328424.BundlingOptions:
        '''(experimental) Default bundling arguments for Python function.

        :stability: experimental
        '''
        return typing.cast(_aws_cdk_aws_lambda_python_alpha_49328424.BundlingOptions, jsii.sget(cls, "PYTHON_FUNCTION_BUNDLING"))


class EventbridgeBroker(
    _constructs_77d1e7e8.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdklabs/cdk-appmod-catalog-blueprints.EventbridgeBroker",
):
    '''
    :stability: experimental
    '''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        event_source: builtins.str,
        kms_key: typing.Optional[_aws_cdk_aws_kms_ceddda9d.Key] = None,
        name: typing.Optional[builtins.str] = None,
        removal_policy: typing.Optional[_aws_cdk_ceddda9d.RemovalPolicy] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param event_source: 
        :param kms_key: 
        :param name: 
        :param removal_policy: 

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5391a3753ae12822ab842065b2f29fede1c6b75f7e0ba6cdca1be351c9c104c3)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = EventbridgeBrokerProps(
            event_source=event_source,
            kms_key=kms_key,
            name=name,
            removal_policy=removal_policy,
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @jsii.member(jsii_name="sendViaSfnChain")
    def send_via_sfn_chain(
        self,
        detail_type: builtins.str,
        event_detail: typing.Any,
    ) -> _aws_cdk_aws_stepfunctions_tasks_ceddda9d.EventBridgePutEvents:
        '''
        :param detail_type: -
        :param event_detail: -

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__71a910ff106734bd214c5973b84305b89274d3d6adbe4eedaa2c546cb060d0d7)
            check_type(argname="argument detail_type", value=detail_type, expected_type=type_hints["detail_type"])
            check_type(argname="argument event_detail", value=event_detail, expected_type=type_hints["event_detail"])
        return typing.cast(_aws_cdk_aws_stepfunctions_tasks_ceddda9d.EventBridgePutEvents, jsii.invoke(self, "sendViaSfnChain", [detail_type, event_detail]))

    @builtins.property
    @jsii.member(jsii_name="eventbus")
    def eventbus(self) -> _aws_cdk_aws_events_ceddda9d.EventBus:
        '''
        :stability: experimental
        '''
        return typing.cast(_aws_cdk_aws_events_ceddda9d.EventBus, jsii.get(self, "eventbus"))

    @builtins.property
    @jsii.member(jsii_name="kmsKey")
    def kms_key(self) -> _aws_cdk_aws_kms_ceddda9d.Key:
        '''
        :stability: experimental
        '''
        return typing.cast(_aws_cdk_aws_kms_ceddda9d.Key, jsii.get(self, "kmsKey"))


@jsii.data_type(
    jsii_type="@cdklabs/cdk-appmod-catalog-blueprints.EventbridgeBrokerProps",
    jsii_struct_bases=[],
    name_mapping={
        "event_source": "eventSource",
        "kms_key": "kmsKey",
        "name": "name",
        "removal_policy": "removalPolicy",
    },
)
class EventbridgeBrokerProps:
    def __init__(
        self,
        *,
        event_source: builtins.str,
        kms_key: typing.Optional[_aws_cdk_aws_kms_ceddda9d.Key] = None,
        name: typing.Optional[builtins.str] = None,
        removal_policy: typing.Optional[_aws_cdk_ceddda9d.RemovalPolicy] = None,
    ) -> None:
        '''
        :param event_source: 
        :param kms_key: 
        :param name: 
        :param removal_policy: 

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ecd91fa4cae79b6f27bdbae2c38230e7edda9cec831ac503ca3b7c01b0311241)
            check_type(argname="argument event_source", value=event_source, expected_type=type_hints["event_source"])
            check_type(argname="argument kms_key", value=kms_key, expected_type=type_hints["kms_key"])
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
            check_type(argname="argument removal_policy", value=removal_policy, expected_type=type_hints["removal_policy"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "event_source": event_source,
        }
        if kms_key is not None:
            self._values["kms_key"] = kms_key
        if name is not None:
            self._values["name"] = name
        if removal_policy is not None:
            self._values["removal_policy"] = removal_policy

    @builtins.property
    def event_source(self) -> builtins.str:
        '''
        :stability: experimental
        '''
        result = self._values.get("event_source")
        assert result is not None, "Required property 'event_source' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def kms_key(self) -> typing.Optional[_aws_cdk_aws_kms_ceddda9d.Key]:
        '''
        :stability: experimental
        '''
        result = self._values.get("kms_key")
        return typing.cast(typing.Optional[_aws_cdk_aws_kms_ceddda9d.Key], result)

    @builtins.property
    def name(self) -> typing.Optional[builtins.str]:
        '''
        :stability: experimental
        '''
        result = self._values.get("name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def removal_policy(self) -> typing.Optional[_aws_cdk_ceddda9d.RemovalPolicy]:
        '''
        :stability: experimental
        '''
        result = self._values.get("removal_policy")
        return typing.cast(typing.Optional[_aws_cdk_ceddda9d.RemovalPolicy], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "EventbridgeBrokerProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdklabs/cdk-appmod-catalog-blueprints.FileInput",
    jsii_struct_bases=[],
    name_mapping={
        "file_path": "filePath",
        "file_type": "fileType",
        "continue_on_error": "continueOnError",
        "execution_order": "executionOrder",
    },
)
class FileInput:
    def __init__(
        self,
        *,
        file_path: builtins.str,
        file_type: "FileType",
        continue_on_error: typing.Optional[builtins.bool] = None,
        execution_order: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''(experimental) File input configuration.

        :param file_path: (experimental) Path to the file (local path or S3 URI).
        :param file_type: (experimental) Type of file.
        :param continue_on_error: (experimental) Whether to continue on error.
        :param execution_order: (experimental) Execution order (lower numbers execute first).

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f22614c3ee9aff68919f8ac64743fb8c255ed9c33337d90d40c2622733942ed5)
            check_type(argname="argument file_path", value=file_path, expected_type=type_hints["file_path"])
            check_type(argname="argument file_type", value=file_type, expected_type=type_hints["file_type"])
            check_type(argname="argument continue_on_error", value=continue_on_error, expected_type=type_hints["continue_on_error"])
            check_type(argname="argument execution_order", value=execution_order, expected_type=type_hints["execution_order"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "file_path": file_path,
            "file_type": file_type,
        }
        if continue_on_error is not None:
            self._values["continue_on_error"] = continue_on_error
        if execution_order is not None:
            self._values["execution_order"] = execution_order

    @builtins.property
    def file_path(self) -> builtins.str:
        '''(experimental) Path to the file (local path or S3 URI).

        :stability: experimental
        '''
        result = self._values.get("file_path")
        assert result is not None, "Required property 'file_path' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def file_type(self) -> "FileType":
        '''(experimental) Type of file.

        :stability: experimental
        '''
        result = self._values.get("file_type")
        assert result is not None, "Required property 'file_type' is missing"
        return typing.cast("FileType", result)

    @builtins.property
    def continue_on_error(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Whether to continue on error.

        :stability: experimental
        '''
        result = self._values.get("continue_on_error")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def execution_order(self) -> typing.Optional[jsii.Number]:
        '''(experimental) Execution order (lower numbers execute first).

        :stability: experimental
        '''
        result = self._values.get("execution_order")
        return typing.cast(typing.Optional[jsii.Number], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "FileInput(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.enum(jsii_type="@cdklabs/cdk-appmod-catalog-blueprints.FileType")
class FileType(enum.Enum):
    '''(experimental) Supported file types for data loading.

    :stability: experimental
    '''

    SQL = "SQL"
    '''(experimental) Standard SQL file.

    :stability: experimental
    '''
    MYSQLDUMP = "MYSQLDUMP"
    '''(experimental) MySQL dump file generated by mysqldump.

    :stability: experimental
    '''
    PGDUMP = "PGDUMP"
    '''(experimental) PostgreSQL dump file generated by pg_dump.

    :stability: experimental
    '''


class Frontend(
    _constructs_77d1e7e8.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdklabs/cdk-appmod-catalog-blueprints.Frontend",
):
    '''(experimental) Frontend construct that deploys a frontend application to S3 and CloudFront.

    This construct provides a complete solution for hosting static frontend applications
    with the following features:

    - S3 bucket for hosting static assets with security best practices
    - CloudFront distribution for global content delivery
    - Optional custom domain with SSL certificate
    - Automatic build process execution
    - SPA-friendly error handling by default
    - Security configurations

    :stability: experimental
    '''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        source_directory: builtins.str,
        build_command: typing.Optional[builtins.str] = None,
        build_output_directory: typing.Optional[builtins.str] = None,
        custom_domain: typing.Optional[typing.Union[CustomDomainConfig, typing.Dict[builtins.str, typing.Any]]] = None,
        distribution_props: typing.Optional[typing.Union[AdditionalDistributionProps, typing.Dict[builtins.str, typing.Any]]] = None,
        enable_observability: typing.Optional[builtins.bool] = None,
        error_responses: typing.Optional[typing.Sequence[typing.Union[_aws_cdk_aws_cloudfront_ceddda9d.ErrorResponse, typing.Dict[builtins.str, typing.Any]]]] = None,
        removal_policy: typing.Optional[_aws_cdk_ceddda9d.RemovalPolicy] = None,
        skip_build: typing.Optional[builtins.bool] = None,
    ) -> None:
        '''(experimental) Creates a new Frontend.

        :param scope: The construct scope.
        :param id: The construct ID.
        :param source_directory: (experimental) Base directory of the frontend source code.
        :param build_command: (experimental) Optional build command (defaults to 'npm run build').
        :param build_output_directory: (experimental) Directory where build artifacts are located after build command completes (defaults to '{sourceDirectory}/build').
        :param custom_domain: (experimental) Optional custom domain configuration.
        :param distribution_props: (experimental) Optional additional CloudFront distribution properties.
        :param enable_observability: (experimental) Enable logging and tracing for all supporting resource. Default: false
        :param error_responses: (experimental) Optional CloudFront error responses (defaults to SPA-friendly responses).
        :param removal_policy: (experimental) Optional removal policy for all resources (defaults to DESTROY).
        :param skip_build: (experimental) Optional flag to skip the build process (useful for pre-built artifacts).

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__59f5637ea312a9fb8090cc497bbaa3fb29d31e5a16d1958df0e9a4337936da88)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = FrontendProps(
            source_directory=source_directory,
            build_command=build_command,
            build_output_directory=build_output_directory,
            custom_domain=custom_domain,
            distribution_props=distribution_props,
            enable_observability=enable_observability,
            error_responses=error_responses,
            removal_policy=removal_policy,
            skip_build=skip_build,
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @jsii.member(jsii_name="bucketName")
    def bucket_name(self) -> builtins.str:
        '''(experimental) Gets the S3 bucket name.

        :return: The S3 bucket name

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.invoke(self, "bucketName", []))

    @jsii.member(jsii_name="distributionDomainName")
    def distribution_domain_name(self) -> builtins.str:
        '''(experimental) Gets the CloudFront distribution domain name.

        :return: The CloudFront domain name

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.invoke(self, "distributionDomainName", []))

    @jsii.member(jsii_name="url")
    def url(self) -> builtins.str:
        '''(experimental) Gets the URL of the frontend application.

        :return: The frontend URL

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.invoke(self, "url", []))

    @builtins.property
    @jsii.member(jsii_name="bucket")
    def bucket(self) -> _aws_cdk_aws_s3_ceddda9d.Bucket:
        '''(experimental) The S3 bucket hosting the frontend assets.

        :stability: experimental
        '''
        return typing.cast(_aws_cdk_aws_s3_ceddda9d.Bucket, jsii.get(self, "bucket"))

    @builtins.property
    @jsii.member(jsii_name="bucketDeployment")
    def bucket_deployment(self) -> _aws_cdk_aws_s3_deployment_ceddda9d.BucketDeployment:
        '''(experimental) The bucket deployment that uploads the frontend assets.

        :stability: experimental
        '''
        return typing.cast(_aws_cdk_aws_s3_deployment_ceddda9d.BucketDeployment, jsii.get(self, "bucketDeployment"))

    @builtins.property
    @jsii.member(jsii_name="distribution")
    def distribution(self) -> _aws_cdk_aws_cloudfront_ceddda9d.Distribution:
        '''(experimental) The CloudFront distribution.

        :stability: experimental
        '''
        return typing.cast(_aws_cdk_aws_cloudfront_ceddda9d.Distribution, jsii.get(self, "distribution"))

    @builtins.property
    @jsii.member(jsii_name="asset")
    def asset(self) -> typing.Optional[_aws_cdk_aws_s3_assets_ceddda9d.Asset]:
        '''(experimental) The Asset containing the frontend source code.

        :stability: experimental
        '''
        return typing.cast(typing.Optional[_aws_cdk_aws_s3_assets_ceddda9d.Asset], jsii.get(self, "asset"))

    @builtins.property
    @jsii.member(jsii_name="domainName")
    def domain_name(self) -> typing.Optional[builtins.str]:
        '''(experimental) The custom domain name (if configured).

        :stability: experimental
        '''
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "domainName"))


@jsii.data_type(
    jsii_type="@cdklabs/cdk-appmod-catalog-blueprints.FrontendProps",
    jsii_struct_bases=[],
    name_mapping={
        "source_directory": "sourceDirectory",
        "build_command": "buildCommand",
        "build_output_directory": "buildOutputDirectory",
        "custom_domain": "customDomain",
        "distribution_props": "distributionProps",
        "enable_observability": "enableObservability",
        "error_responses": "errorResponses",
        "removal_policy": "removalPolicy",
        "skip_build": "skipBuild",
    },
)
class FrontendProps:
    def __init__(
        self,
        *,
        source_directory: builtins.str,
        build_command: typing.Optional[builtins.str] = None,
        build_output_directory: typing.Optional[builtins.str] = None,
        custom_domain: typing.Optional[typing.Union[CustomDomainConfig, typing.Dict[builtins.str, typing.Any]]] = None,
        distribution_props: typing.Optional[typing.Union[AdditionalDistributionProps, typing.Dict[builtins.str, typing.Any]]] = None,
        enable_observability: typing.Optional[builtins.bool] = None,
        error_responses: typing.Optional[typing.Sequence[typing.Union[_aws_cdk_aws_cloudfront_ceddda9d.ErrorResponse, typing.Dict[builtins.str, typing.Any]]]] = None,
        removal_policy: typing.Optional[_aws_cdk_ceddda9d.RemovalPolicy] = None,
        skip_build: typing.Optional[builtins.bool] = None,
    ) -> None:
        '''(experimental) Properties for the Frontend construct.

        :param source_directory: (experimental) Base directory of the frontend source code.
        :param build_command: (experimental) Optional build command (defaults to 'npm run build').
        :param build_output_directory: (experimental) Directory where build artifacts are located after build command completes (defaults to '{sourceDirectory}/build').
        :param custom_domain: (experimental) Optional custom domain configuration.
        :param distribution_props: (experimental) Optional additional CloudFront distribution properties.
        :param enable_observability: (experimental) Enable logging and tracing for all supporting resource. Default: false
        :param error_responses: (experimental) Optional CloudFront error responses (defaults to SPA-friendly responses).
        :param removal_policy: (experimental) Optional removal policy for all resources (defaults to DESTROY).
        :param skip_build: (experimental) Optional flag to skip the build process (useful for pre-built artifacts).

        :stability: experimental
        '''
        if isinstance(custom_domain, dict):
            custom_domain = CustomDomainConfig(**custom_domain)
        if isinstance(distribution_props, dict):
            distribution_props = AdditionalDistributionProps(**distribution_props)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2648a6f2c6f02177f5b324264b7de549aa23b0c1d93c8d6cccbc307a85e0c0fc)
            check_type(argname="argument source_directory", value=source_directory, expected_type=type_hints["source_directory"])
            check_type(argname="argument build_command", value=build_command, expected_type=type_hints["build_command"])
            check_type(argname="argument build_output_directory", value=build_output_directory, expected_type=type_hints["build_output_directory"])
            check_type(argname="argument custom_domain", value=custom_domain, expected_type=type_hints["custom_domain"])
            check_type(argname="argument distribution_props", value=distribution_props, expected_type=type_hints["distribution_props"])
            check_type(argname="argument enable_observability", value=enable_observability, expected_type=type_hints["enable_observability"])
            check_type(argname="argument error_responses", value=error_responses, expected_type=type_hints["error_responses"])
            check_type(argname="argument removal_policy", value=removal_policy, expected_type=type_hints["removal_policy"])
            check_type(argname="argument skip_build", value=skip_build, expected_type=type_hints["skip_build"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "source_directory": source_directory,
        }
        if build_command is not None:
            self._values["build_command"] = build_command
        if build_output_directory is not None:
            self._values["build_output_directory"] = build_output_directory
        if custom_domain is not None:
            self._values["custom_domain"] = custom_domain
        if distribution_props is not None:
            self._values["distribution_props"] = distribution_props
        if enable_observability is not None:
            self._values["enable_observability"] = enable_observability
        if error_responses is not None:
            self._values["error_responses"] = error_responses
        if removal_policy is not None:
            self._values["removal_policy"] = removal_policy
        if skip_build is not None:
            self._values["skip_build"] = skip_build

    @builtins.property
    def source_directory(self) -> builtins.str:
        '''(experimental) Base directory of the frontend source code.

        :stability: experimental
        '''
        result = self._values.get("source_directory")
        assert result is not None, "Required property 'source_directory' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def build_command(self) -> typing.Optional[builtins.str]:
        '''(experimental) Optional build command (defaults to 'npm run build').

        :stability: experimental
        '''
        result = self._values.get("build_command")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def build_output_directory(self) -> typing.Optional[builtins.str]:
        '''(experimental) Directory where build artifacts are located after build command completes (defaults to '{sourceDirectory}/build').

        :stability: experimental
        '''
        result = self._values.get("build_output_directory")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def custom_domain(self) -> typing.Optional[CustomDomainConfig]:
        '''(experimental) Optional custom domain configuration.

        :stability: experimental
        '''
        result = self._values.get("custom_domain")
        return typing.cast(typing.Optional[CustomDomainConfig], result)

    @builtins.property
    def distribution_props(self) -> typing.Optional[AdditionalDistributionProps]:
        '''(experimental) Optional additional CloudFront distribution properties.

        :stability: experimental
        '''
        result = self._values.get("distribution_props")
        return typing.cast(typing.Optional[AdditionalDistributionProps], result)

    @builtins.property
    def enable_observability(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Enable logging and tracing for all supporting resource.

        :default: false

        :stability: experimental
        '''
        result = self._values.get("enable_observability")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def error_responses(
        self,
    ) -> typing.Optional[typing.List[_aws_cdk_aws_cloudfront_ceddda9d.ErrorResponse]]:
        '''(experimental) Optional CloudFront error responses (defaults to SPA-friendly responses).

        :stability: experimental
        '''
        result = self._values.get("error_responses")
        return typing.cast(typing.Optional[typing.List[_aws_cdk_aws_cloudfront_ceddda9d.ErrorResponse]], result)

    @builtins.property
    def removal_policy(self) -> typing.Optional[_aws_cdk_ceddda9d.RemovalPolicy]:
        '''(experimental) Optional removal policy for all resources (defaults to DESTROY).

        :stability: experimental
        '''
        result = self._values.get("removal_policy")
        return typing.cast(typing.Optional[_aws_cdk_ceddda9d.RemovalPolicy], result)

    @builtins.property
    def skip_build(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Optional flag to skip the build process (useful for pre-built artifacts).

        :stability: experimental
        '''
        result = self._values.get("skip_build")
        return typing.cast(typing.Optional[builtins.bool], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "FrontendProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.interface(jsii_type="@cdklabs/cdk-appmod-catalog-blueprints.IAdapter")
class IAdapter(typing_extensions.Protocol):
    '''(experimental) Abstraction to enable different types of source triggers for the intelligent document processing workflow.

    :stability: experimental
    '''

    @jsii.member(jsii_name="createFailedChain")
    def create_failed_chain(
        self,
        scope: _constructs_77d1e7e8.Construct,
    ) -> _aws_cdk_aws_stepfunctions_ceddda9d.Chain:
        '''(experimental) Create the adapter specific handler for failed processing.

        :param scope: Scope to use in relation to the CDK hierarchy.

        :return: Chain to be added to the state machine to handle failure scenarios

        :stability: experimental
        '''
        ...

    @jsii.member(jsii_name="createIngressTrigger")
    def create_ingress_trigger(
        self,
        scope: _constructs_77d1e7e8.Construct,
        state_machine: _aws_cdk_aws_stepfunctions_ceddda9d.StateMachine,
        *,
        document_processing_table: typing.Optional[_aws_cdk_aws_dynamodb_ceddda9d.Table] = None,
        enable_observability: typing.Optional[builtins.bool] = None,
        encryption_key: typing.Optional[_aws_cdk_aws_kms_ceddda9d.Key] = None,
        eventbridge_broker: typing.Optional[EventbridgeBroker] = None,
        ingress_adapter: typing.Optional["IAdapter"] = None,
        network: typing.Optional["Network"] = None,
        removal_policy: typing.Optional[_aws_cdk_ceddda9d.RemovalPolicy] = None,
        workflow_timeout: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
        log_group_data_protection: typing.Optional[typing.Union["LogGroupDataProtectionProps", typing.Dict[builtins.str, typing.Any]]] = None,
        metric_namespace: typing.Optional[builtins.str] = None,
        metric_service_name: typing.Optional[builtins.str] = None,
    ) -> typing.Mapping[builtins.str, typing.Any]:
        '''(experimental) Create resources that would receive the data and trigger the workflow.

        Important: resource created should trigger the state machine

        :param scope: Scope to use in relation to the CDK hierarchy.
        :param state_machine: The workflow of the document processor.
        :param document_processing_table: (experimental) DynamoDB table for storing document processing metadata and workflow state. If not provided, a new table will be created with DocumentId as partition key.
        :param enable_observability: (experimental) Enable logging and tracing for all supporting resource. Default: false
        :param encryption_key: (experimental) KMS key to be used. Default: A new key would be created
        :param eventbridge_broker: (experimental) Optional EventBridge broker for publishing custom events during processing. If not provided, no custom events will be sent out.
        :param ingress_adapter: (experimental) Adapter that defines how the document processing workflow is triggered. Default: QueuedS3Adapter
        :param network: (experimental) Resources that can run inside a VPC will follow the provided network configuration. Default: resources will run outside of a VPC
        :param removal_policy: (experimental) Removal policy for created resources (bucket, table, queue). Default: RemovalPolicy.DESTROY
        :param workflow_timeout: (experimental) Maximum execution time for the Step Functions workflow. Default: Duration.minutes(30)
        :param log_group_data_protection: (experimental) Data protection related configuration. Default: a new KMS key would be generated
        :param metric_namespace: (experimental) Business metric namespace. Default: would be defined per use case
        :param metric_service_name: (experimental) Business metric service name dimension. Default: would be defined per use case

        :return: Resources that are created

        :stability: experimental
        '''
        ...

    @jsii.member(jsii_name="createSuccessChain")
    def create_success_chain(
        self,
        scope: _constructs_77d1e7e8.Construct,
    ) -> _aws_cdk_aws_stepfunctions_ceddda9d.Chain:
        '''(experimental) Create the adapter specific handler for successful processing.

        :param scope: Scope to use in relation to the CDK hierarchy.

        :return: Chain to be added to the state machine to handle successful scenarios

        :stability: experimental
        '''
        ...

    @jsii.member(jsii_name="generateAdapterIAMPolicies")
    def generate_adapter_iam_policies(
        self,
        additional_iam_actions: typing.Optional[typing.Sequence[builtins.str]] = None,
        narrow_actions: typing.Optional[builtins.bool] = None,
    ) -> typing.List[_aws_cdk_aws_iam_ceddda9d.PolicyStatement]:
        '''(experimental) Generate IAM statements that can be used by other resources to access the storage.

        :param additional_iam_actions: (Optional) list of additional actions in relation to the underlying storage for the adapter.
        :param narrow_actions: (Optional) whether the resulting permissions would only be the IAM actions indicated in the ``additionalIAMActions`` parameter.

        :default: false

        :return: PolicyStatement[] IAM policy statements that would included in the state machine IAM role

        :stability: experimental
        '''
        ...

    @jsii.member(jsii_name="init")
    def init(
        self,
        scope: _constructs_77d1e7e8.Construct,
        *,
        document_processing_table: typing.Optional[_aws_cdk_aws_dynamodb_ceddda9d.Table] = None,
        enable_observability: typing.Optional[builtins.bool] = None,
        encryption_key: typing.Optional[_aws_cdk_aws_kms_ceddda9d.Key] = None,
        eventbridge_broker: typing.Optional[EventbridgeBroker] = None,
        ingress_adapter: typing.Optional["IAdapter"] = None,
        network: typing.Optional["Network"] = None,
        removal_policy: typing.Optional[_aws_cdk_ceddda9d.RemovalPolicy] = None,
        workflow_timeout: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
        log_group_data_protection: typing.Optional[typing.Union["LogGroupDataProtectionProps", typing.Dict[builtins.str, typing.Any]]] = None,
        metric_namespace: typing.Optional[builtins.str] = None,
        metric_service_name: typing.Optional[builtins.str] = None,
    ) -> None:
        '''(experimental) Initializes the adapter.

        :param scope: Scope to use in relation to the CDK hierarchy.
        :param document_processing_table: (experimental) DynamoDB table for storing document processing metadata and workflow state. If not provided, a new table will be created with DocumentId as partition key.
        :param enable_observability: (experimental) Enable logging and tracing for all supporting resource. Default: false
        :param encryption_key: (experimental) KMS key to be used. Default: A new key would be created
        :param eventbridge_broker: (experimental) Optional EventBridge broker for publishing custom events during processing. If not provided, no custom events will be sent out.
        :param ingress_adapter: (experimental) Adapter that defines how the document processing workflow is triggered. Default: QueuedS3Adapter
        :param network: (experimental) Resources that can run inside a VPC will follow the provided network configuration. Default: resources will run outside of a VPC
        :param removal_policy: (experimental) Removal policy for created resources (bucket, table, queue). Default: RemovalPolicy.DESTROY
        :param workflow_timeout: (experimental) Maximum execution time for the Step Functions workflow. Default: Duration.minutes(30)
        :param log_group_data_protection: (experimental) Data protection related configuration. Default: a new KMS key would be generated
        :param metric_namespace: (experimental) Business metric namespace. Default: would be defined per use case
        :param metric_service_name: (experimental) Business metric service name dimension. Default: would be defined per use case

        :stability: experimental
        '''
        ...


class _IAdapterProxy:
    '''(experimental) Abstraction to enable different types of source triggers for the intelligent document processing workflow.

    :stability: experimental
    '''

    __jsii_type__: typing.ClassVar[str] = "@cdklabs/cdk-appmod-catalog-blueprints.IAdapter"

    @jsii.member(jsii_name="createFailedChain")
    def create_failed_chain(
        self,
        scope: _constructs_77d1e7e8.Construct,
    ) -> _aws_cdk_aws_stepfunctions_ceddda9d.Chain:
        '''(experimental) Create the adapter specific handler for failed processing.

        :param scope: Scope to use in relation to the CDK hierarchy.

        :return: Chain to be added to the state machine to handle failure scenarios

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5998f6c7e16512d92cd00097e77d737333304685208eb36a522c156f8378a9e7)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
        return typing.cast(_aws_cdk_aws_stepfunctions_ceddda9d.Chain, jsii.invoke(self, "createFailedChain", [scope]))

    @jsii.member(jsii_name="createIngressTrigger")
    def create_ingress_trigger(
        self,
        scope: _constructs_77d1e7e8.Construct,
        state_machine: _aws_cdk_aws_stepfunctions_ceddda9d.StateMachine,
        *,
        document_processing_table: typing.Optional[_aws_cdk_aws_dynamodb_ceddda9d.Table] = None,
        enable_observability: typing.Optional[builtins.bool] = None,
        encryption_key: typing.Optional[_aws_cdk_aws_kms_ceddda9d.Key] = None,
        eventbridge_broker: typing.Optional[EventbridgeBroker] = None,
        ingress_adapter: typing.Optional[IAdapter] = None,
        network: typing.Optional["Network"] = None,
        removal_policy: typing.Optional[_aws_cdk_ceddda9d.RemovalPolicy] = None,
        workflow_timeout: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
        log_group_data_protection: typing.Optional[typing.Union["LogGroupDataProtectionProps", typing.Dict[builtins.str, typing.Any]]] = None,
        metric_namespace: typing.Optional[builtins.str] = None,
        metric_service_name: typing.Optional[builtins.str] = None,
    ) -> typing.Mapping[builtins.str, typing.Any]:
        '''(experimental) Create resources that would receive the data and trigger the workflow.

        Important: resource created should trigger the state machine

        :param scope: Scope to use in relation to the CDK hierarchy.
        :param state_machine: The workflow of the document processor.
        :param document_processing_table: (experimental) DynamoDB table for storing document processing metadata and workflow state. If not provided, a new table will be created with DocumentId as partition key.
        :param enable_observability: (experimental) Enable logging and tracing for all supporting resource. Default: false
        :param encryption_key: (experimental) KMS key to be used. Default: A new key would be created
        :param eventbridge_broker: (experimental) Optional EventBridge broker for publishing custom events during processing. If not provided, no custom events will be sent out.
        :param ingress_adapter: (experimental) Adapter that defines how the document processing workflow is triggered. Default: QueuedS3Adapter
        :param network: (experimental) Resources that can run inside a VPC will follow the provided network configuration. Default: resources will run outside of a VPC
        :param removal_policy: (experimental) Removal policy for created resources (bucket, table, queue). Default: RemovalPolicy.DESTROY
        :param workflow_timeout: (experimental) Maximum execution time for the Step Functions workflow. Default: Duration.minutes(30)
        :param log_group_data_protection: (experimental) Data protection related configuration. Default: a new KMS key would be generated
        :param metric_namespace: (experimental) Business metric namespace. Default: would be defined per use case
        :param metric_service_name: (experimental) Business metric service name dimension. Default: would be defined per use case

        :return: Resources that are created

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b61e74ddd8982f4b30ae59307c9fb3adaff26122ddc7f5faabc2cc8e1e2da034)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument state_machine", value=state_machine, expected_type=type_hints["state_machine"])
        props = BaseDocumentProcessingProps(
            document_processing_table=document_processing_table,
            enable_observability=enable_observability,
            encryption_key=encryption_key,
            eventbridge_broker=eventbridge_broker,
            ingress_adapter=ingress_adapter,
            network=network,
            removal_policy=removal_policy,
            workflow_timeout=workflow_timeout,
            log_group_data_protection=log_group_data_protection,
            metric_namespace=metric_namespace,
            metric_service_name=metric_service_name,
        )

        return typing.cast(typing.Mapping[builtins.str, typing.Any], jsii.invoke(self, "createIngressTrigger", [scope, state_machine, props]))

    @jsii.member(jsii_name="createSuccessChain")
    def create_success_chain(
        self,
        scope: _constructs_77d1e7e8.Construct,
    ) -> _aws_cdk_aws_stepfunctions_ceddda9d.Chain:
        '''(experimental) Create the adapter specific handler for successful processing.

        :param scope: Scope to use in relation to the CDK hierarchy.

        :return: Chain to be added to the state machine to handle successful scenarios

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__cd0aad7a5879633fca8d89cbf92e8f5a13e31615116036f29a82a58c1bb4727d)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
        return typing.cast(_aws_cdk_aws_stepfunctions_ceddda9d.Chain, jsii.invoke(self, "createSuccessChain", [scope]))

    @jsii.member(jsii_name="generateAdapterIAMPolicies")
    def generate_adapter_iam_policies(
        self,
        additional_iam_actions: typing.Optional[typing.Sequence[builtins.str]] = None,
        narrow_actions: typing.Optional[builtins.bool] = None,
    ) -> typing.List[_aws_cdk_aws_iam_ceddda9d.PolicyStatement]:
        '''(experimental) Generate IAM statements that can be used by other resources to access the storage.

        :param additional_iam_actions: (Optional) list of additional actions in relation to the underlying storage for the adapter.
        :param narrow_actions: (Optional) whether the resulting permissions would only be the IAM actions indicated in the ``additionalIAMActions`` parameter.

        :default: false

        :return: PolicyStatement[] IAM policy statements that would included in the state machine IAM role

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__82a45114a0ff76d4b9d091edd6674d4e762dc5ca19631d61579cf1aa47e30b5e)
            check_type(argname="argument additional_iam_actions", value=additional_iam_actions, expected_type=type_hints["additional_iam_actions"])
            check_type(argname="argument narrow_actions", value=narrow_actions, expected_type=type_hints["narrow_actions"])
        return typing.cast(typing.List[_aws_cdk_aws_iam_ceddda9d.PolicyStatement], jsii.invoke(self, "generateAdapterIAMPolicies", [additional_iam_actions, narrow_actions]))

    @jsii.member(jsii_name="init")
    def init(
        self,
        scope: _constructs_77d1e7e8.Construct,
        *,
        document_processing_table: typing.Optional[_aws_cdk_aws_dynamodb_ceddda9d.Table] = None,
        enable_observability: typing.Optional[builtins.bool] = None,
        encryption_key: typing.Optional[_aws_cdk_aws_kms_ceddda9d.Key] = None,
        eventbridge_broker: typing.Optional[EventbridgeBroker] = None,
        ingress_adapter: typing.Optional[IAdapter] = None,
        network: typing.Optional["Network"] = None,
        removal_policy: typing.Optional[_aws_cdk_ceddda9d.RemovalPolicy] = None,
        workflow_timeout: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
        log_group_data_protection: typing.Optional[typing.Union["LogGroupDataProtectionProps", typing.Dict[builtins.str, typing.Any]]] = None,
        metric_namespace: typing.Optional[builtins.str] = None,
        metric_service_name: typing.Optional[builtins.str] = None,
    ) -> None:
        '''(experimental) Initializes the adapter.

        :param scope: Scope to use in relation to the CDK hierarchy.
        :param document_processing_table: (experimental) DynamoDB table for storing document processing metadata and workflow state. If not provided, a new table will be created with DocumentId as partition key.
        :param enable_observability: (experimental) Enable logging and tracing for all supporting resource. Default: false
        :param encryption_key: (experimental) KMS key to be used. Default: A new key would be created
        :param eventbridge_broker: (experimental) Optional EventBridge broker for publishing custom events during processing. If not provided, no custom events will be sent out.
        :param ingress_adapter: (experimental) Adapter that defines how the document processing workflow is triggered. Default: QueuedS3Adapter
        :param network: (experimental) Resources that can run inside a VPC will follow the provided network configuration. Default: resources will run outside of a VPC
        :param removal_policy: (experimental) Removal policy for created resources (bucket, table, queue). Default: RemovalPolicy.DESTROY
        :param workflow_timeout: (experimental) Maximum execution time for the Step Functions workflow. Default: Duration.minutes(30)
        :param log_group_data_protection: (experimental) Data protection related configuration. Default: a new KMS key would be generated
        :param metric_namespace: (experimental) Business metric namespace. Default: would be defined per use case
        :param metric_service_name: (experimental) Business metric service name dimension. Default: would be defined per use case

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__17f7e7f35ea8e49cf6ded248435aa1e1dcf416e61c549f3e7b74baad3ac399e7)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
        props = BaseDocumentProcessingProps(
            document_processing_table=document_processing_table,
            enable_observability=enable_observability,
            encryption_key=encryption_key,
            eventbridge_broker=eventbridge_broker,
            ingress_adapter=ingress_adapter,
            network=network,
            removal_policy=removal_policy,
            workflow_timeout=workflow_timeout,
            log_group_data_protection=log_group_data_protection,
            metric_namespace=metric_namespace,
            metric_service_name=metric_service_name,
        )

        return typing.cast(None, jsii.invoke(self, "init", [scope, props]))

# Adding a "__jsii_proxy_class__(): typing.Type" function to the interface
typing.cast(typing.Any, IAdapter).__jsii_proxy_class__ = lambda : _IAdapterProxy


@jsii.interface(jsii_type="@cdklabs/cdk-appmod-catalog-blueprints.IObservable")
class IObservable(typing_extensions.Protocol):
    '''(experimental) Interface providing configuration parameters for constructs that support Observability.

    :stability: experimental
    '''

    @builtins.property
    @jsii.member(jsii_name="logGroupDataProtection")
    def log_group_data_protection(self) -> "LogGroupDataProtectionProps":
        '''
        :stability: experimental
        '''
        ...

    @builtins.property
    @jsii.member(jsii_name="metricNamespace")
    def metric_namespace(self) -> builtins.str:
        '''
        :stability: experimental
        '''
        ...

    @builtins.property
    @jsii.member(jsii_name="metricServiceName")
    def metric_service_name(self) -> builtins.str:
        '''
        :stability: experimental
        '''
        ...

    @jsii.member(jsii_name="metrics")
    def metrics(self) -> typing.List[_aws_cdk_aws_cloudwatch_ceddda9d.IMetric]:
        '''
        :stability: experimental
        '''
        ...


class _IObservableProxy:
    '''(experimental) Interface providing configuration parameters for constructs that support Observability.

    :stability: experimental
    '''

    __jsii_type__: typing.ClassVar[str] = "@cdklabs/cdk-appmod-catalog-blueprints.IObservable"

    @builtins.property
    @jsii.member(jsii_name="logGroupDataProtection")
    def log_group_data_protection(self) -> "LogGroupDataProtectionProps":
        '''
        :stability: experimental
        '''
        return typing.cast("LogGroupDataProtectionProps", jsii.get(self, "logGroupDataProtection"))

    @builtins.property
    @jsii.member(jsii_name="metricNamespace")
    def metric_namespace(self) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "metricNamespace"))

    @builtins.property
    @jsii.member(jsii_name="metricServiceName")
    def metric_service_name(self) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "metricServiceName"))

    @jsii.member(jsii_name="metrics")
    def metrics(self) -> typing.List[_aws_cdk_aws_cloudwatch_ceddda9d.IMetric]:
        '''
        :stability: experimental
        '''
        return typing.cast(typing.List[_aws_cdk_aws_cloudwatch_ceddda9d.IMetric], jsii.invoke(self, "metrics", []))

# Adding a "__jsii_proxy_class__(): typing.Type" function to the interface
typing.cast(typing.Any, IObservable).__jsii_proxy_class__ = lambda : _IObservableProxy


class LambdaIamUtils(
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdklabs/cdk-appmod-catalog-blueprints.LambdaIamUtils",
):
    '''(experimental) Utility class for creating secure Lambda IAM policy statements with minimal permissions.

    :stability: experimental
    '''

    def __init__(self) -> None:
        '''
        :stability: experimental
        '''
        jsii.create(self.__class__, self, [])

    @jsii.member(jsii_name="createDynamoDbPolicyStatement")
    @builtins.classmethod
    def create_dynamo_db_policy_statement(
        cls,
        table_arn: builtins.str,
        actions: typing.Optional[typing.Sequence[builtins.str]] = None,
    ) -> _aws_cdk_aws_iam_ceddda9d.PolicyStatement:
        '''(experimental) Creates a policy statement for DynamoDB table access.

        :param table_arn: The ARN of the DynamoDB table.
        :param actions: The DynamoDB actions to allow.

        :return: PolicyStatement for DynamoDB access

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8fea74c9846ad0c5bdddcbfe10063247cb7bcf58aac91e0be80d1226246784e4)
            check_type(argname="argument table_arn", value=table_arn, expected_type=type_hints["table_arn"])
            check_type(argname="argument actions", value=actions, expected_type=type_hints["actions"])
        return typing.cast(_aws_cdk_aws_iam_ceddda9d.PolicyStatement, jsii.sinvoke(cls, "createDynamoDbPolicyStatement", [table_arn, actions]))

    @jsii.member(jsii_name="createKmsPolicyStatement")
    @builtins.classmethod
    def create_kms_policy_statement(
        cls,
        key_arn: builtins.str,
        actions: typing.Optional[typing.Sequence[builtins.str]] = None,
    ) -> _aws_cdk_aws_iam_ceddda9d.PolicyStatement:
        '''(experimental) Creates a policy statement for KMS key access.

        :param key_arn: The ARN of the KMS key.
        :param actions: The KMS actions to allow.

        :return: PolicyStatement for KMS access

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ef86294be8c776ba98bebc269fab82304f75649efab35cf030d999168ba5d690)
            check_type(argname="argument key_arn", value=key_arn, expected_type=type_hints["key_arn"])
            check_type(argname="argument actions", value=actions, expected_type=type_hints["actions"])
        return typing.cast(_aws_cdk_aws_iam_ceddda9d.PolicyStatement, jsii.sinvoke(cls, "createKmsPolicyStatement", [key_arn, actions]))

    @jsii.member(jsii_name="createLogsPermissions")
    @builtins.classmethod
    def create_logs_permissions(
        cls,
        *,
        account: builtins.str,
        function_name: builtins.str,
        region: builtins.str,
        scope: _constructs_77d1e7e8.Construct,
        enable_observability: typing.Optional[builtins.bool] = None,
        log_group_name: typing.Optional[builtins.str] = None,
    ) -> "LambdaLogsPermissionsResult":
        '''(experimental) Creates CloudWatch Logs policy statements for Lambda execution.

        :param account: (experimental) AWS account ID for the log group ARN.
        :param function_name: (experimental) The base name of the Lambda function.
        :param region: (experimental) AWS region for the log group ARN.
        :param scope: (experimental) The construct scope (used to generate unique names).
        :param enable_observability: (experimental) Whether observability is enabled or not. This would have an impact on the result IAM policy for the LogGroup for the Lambda function Default: false
        :param log_group_name: (experimental) Custom log group name pattern. Default: '/aws/lambda/{uniqueFunctionName}'

        :return: Object containing policy statements and the unique function name

        :stability: experimental
        '''
        props = LambdaLogsPermissionsProps(
            account=account,
            function_name=function_name,
            region=region,
            scope=scope,
            enable_observability=enable_observability,
            log_group_name=log_group_name,
        )

        return typing.cast("LambdaLogsPermissionsResult", jsii.sinvoke(cls, "createLogsPermissions", [props]))

    @jsii.member(jsii_name="createS3PolicyStatement")
    @builtins.classmethod
    def create_s3_policy_statement(
        cls,
        bucket_arn: builtins.str,
        actions: typing.Optional[typing.Sequence[builtins.str]] = None,
        include_objects: typing.Optional[builtins.bool] = None,
    ) -> _aws_cdk_aws_iam_ceddda9d.PolicyStatement:
        '''(experimental) Creates a policy statement for S3 bucket access.

        :param bucket_arn: The ARN of the S3 bucket.
        :param actions: The S3 actions to allow.
        :param include_objects: Whether to include object-level permissions.

        :return: PolicyStatement for S3 access

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7762a976633c1cec438c3058cfc410cab5cdbf541350c2fdcb64bcfd9599e7fb)
            check_type(argname="argument bucket_arn", value=bucket_arn, expected_type=type_hints["bucket_arn"])
            check_type(argname="argument actions", value=actions, expected_type=type_hints["actions"])
            check_type(argname="argument include_objects", value=include_objects, expected_type=type_hints["include_objects"])
        return typing.cast(_aws_cdk_aws_iam_ceddda9d.PolicyStatement, jsii.sinvoke(cls, "createS3PolicyStatement", [bucket_arn, actions, include_objects]))

    @jsii.member(jsii_name="createSecretsManagerPolicyStatement")
    @builtins.classmethod
    def create_secrets_manager_policy_statement(
        cls,
        secret_arn: builtins.str,
        actions: typing.Optional[typing.Sequence[builtins.str]] = None,
    ) -> _aws_cdk_aws_iam_ceddda9d.PolicyStatement:
        '''(experimental) Creates a policy statement for Secrets Manager access.

        :param secret_arn: The ARN of the secret.
        :param actions: The Secrets Manager actions to allow.

        :return: PolicyStatement for Secrets Manager access

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__cb1398e35974542f1ff1f03b7872981aa0ef2bb90eed20673a20914f5c7e567c)
            check_type(argname="argument secret_arn", value=secret_arn, expected_type=type_hints["secret_arn"])
            check_type(argname="argument actions", value=actions, expected_type=type_hints["actions"])
        return typing.cast(_aws_cdk_aws_iam_ceddda9d.PolicyStatement, jsii.sinvoke(cls, "createSecretsManagerPolicyStatement", [secret_arn, actions]))

    @jsii.member(jsii_name="createSnsPolicyStatement")
    @builtins.classmethod
    def create_sns_policy_statement(
        cls,
        topic_arn: builtins.str,
        actions: typing.Optional[typing.Sequence[builtins.str]] = None,
    ) -> _aws_cdk_aws_iam_ceddda9d.PolicyStatement:
        '''(experimental) Creates a policy statement for SNS topic access.

        :param topic_arn: The ARN of the SNS topic.
        :param actions: The SNS actions to allow.

        :return: PolicyStatement for SNS access

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8aa3558a2d320688189fd59ffa216e00f3b66d4b1a02026a2dc9bd5fd61c5f36)
            check_type(argname="argument topic_arn", value=topic_arn, expected_type=type_hints["topic_arn"])
            check_type(argname="argument actions", value=actions, expected_type=type_hints["actions"])
        return typing.cast(_aws_cdk_aws_iam_ceddda9d.PolicyStatement, jsii.sinvoke(cls, "createSnsPolicyStatement", [topic_arn, actions]))

    @jsii.member(jsii_name="createSqsPolicyStatement")
    @builtins.classmethod
    def create_sqs_policy_statement(
        cls,
        queue_arn: builtins.str,
        actions: typing.Optional[typing.Sequence[builtins.str]] = None,
    ) -> _aws_cdk_aws_iam_ceddda9d.PolicyStatement:
        '''(experimental) Creates a policy statement for SQS queue access.

        :param queue_arn: The ARN of the SQS queue.
        :param actions: The SQS actions to allow.

        :return: PolicyStatement for SQS access

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5ed421dddfcb3e375ee01a9efb4d503dd54b5351b630f200cd829438bb6c9c89)
            check_type(argname="argument queue_arn", value=queue_arn, expected_type=type_hints["queue_arn"])
            check_type(argname="argument actions", value=actions, expected_type=type_hints["actions"])
        return typing.cast(_aws_cdk_aws_iam_ceddda9d.PolicyStatement, jsii.sinvoke(cls, "createSqsPolicyStatement", [queue_arn, actions]))

    @jsii.member(jsii_name="createStepFunctionsPolicyStatement")
    @builtins.classmethod
    def create_step_functions_policy_statement(
        cls,
        state_machine_arn: builtins.str,
        actions: typing.Optional[typing.Sequence[builtins.str]] = None,
    ) -> _aws_cdk_aws_iam_ceddda9d.PolicyStatement:
        '''(experimental) Creates a policy statement for Step Functions execution.

        :param state_machine_arn: The ARN of the Step Functions state machine.
        :param actions: The Step Functions actions to allow.

        :return: PolicyStatement for Step Functions access

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__cbdc1926ad0aa5c4b79aa48c962c929c8e50b7236860f58373b511defa1fca97)
            check_type(argname="argument state_machine_arn", value=state_machine_arn, expected_type=type_hints["state_machine_arn"])
            check_type(argname="argument actions", value=actions, expected_type=type_hints["actions"])
        return typing.cast(_aws_cdk_aws_iam_ceddda9d.PolicyStatement, jsii.sinvoke(cls, "createStepFunctionsPolicyStatement", [state_machine_arn, actions]))

    @jsii.member(jsii_name="createVpcPermissions")
    @builtins.classmethod
    def create_vpc_permissions(
        cls,
    ) -> typing.List[_aws_cdk_aws_iam_ceddda9d.PolicyStatement]:
        '''(experimental) Creates VPC permissions for Lambda functions running in VPC.

        :return: Array of IAM PolicyStatements for VPC access

        :stability: experimental
        '''
        return typing.cast(typing.List[_aws_cdk_aws_iam_ceddda9d.PolicyStatement], jsii.sinvoke(cls, "createVpcPermissions", []))

    @jsii.member(jsii_name="createXRayPermissions")
    @builtins.classmethod
    def create_x_ray_permissions(
        cls,
    ) -> typing.List[_aws_cdk_aws_iam_ceddda9d.PolicyStatement]:
        '''(experimental) Creates X-Ray tracing permissions for Lambda functions.

        :return: Array of IAM PolicyStatements for X-Ray tracing

        :stability: experimental
        '''
        return typing.cast(typing.List[_aws_cdk_aws_iam_ceddda9d.PolicyStatement], jsii.sinvoke(cls, "createXRayPermissions", []))

    @jsii.member(jsii_name="generateLambdaVPCPermissions")
    @builtins.classmethod
    def generate_lambda_vpc_permissions(
        cls,
    ) -> _aws_cdk_aws_iam_ceddda9d.PolicyStatement:
        '''
        :stability: experimental
        '''
        return typing.cast(_aws_cdk_aws_iam_ceddda9d.PolicyStatement, jsii.sinvoke(cls, "generateLambdaVPCPermissions", []))

    @jsii.member(jsii_name="generateUniqueFunctionName")
    @builtins.classmethod
    def generate_unique_function_name(
        cls,
        scope: _constructs_77d1e7e8.Construct,
        base_name: builtins.str,
    ) -> builtins.str:
        '''(experimental) Generates a unique function name using CDK's built-in functionality.

        :param scope: The construct scope.
        :param base_name: The base name for the function.

        :return: Unique function name

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__56aa9ee6986a4b2052d36311105a3c43214029d77a8db5f3ca96f5b23dd95f36)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument base_name", value=base_name, expected_type=type_hints["base_name"])
        return typing.cast(builtins.str, jsii.sinvoke(cls, "generateUniqueFunctionName", [scope, base_name]))

    @jsii.member(jsii_name="getStackInfo")
    @builtins.classmethod
    def get_stack_info(
        cls,
        scope: _constructs_77d1e7e8.Construct,
    ) -> "LambdaIamUtilsStackInfo":
        '''(experimental) Helper method to get region and account from a construct.

        :param scope: The construct scope.

        :return: LambdaIamUtilsStackInfo

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__555f78633564658fa9ba3d47cbfcf9615db101bbba832804f67bcce2b828f673)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
        return typing.cast("LambdaIamUtilsStackInfo", jsii.sinvoke(cls, "getStackInfo", [scope]))

    @jsii.python.classproperty
    @jsii.member(jsii_name="OBSERVABILITY_SUFFIX")
    def OBSERVABILITY_SUFFIX(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "OBSERVABILITY_SUFFIX"))


@jsii.data_type(
    jsii_type="@cdklabs/cdk-appmod-catalog-blueprints.LambdaIamUtilsStackInfo",
    jsii_struct_bases=[],
    name_mapping={"account": "account", "region": "region"},
)
class LambdaIamUtilsStackInfo:
    def __init__(self, *, account: builtins.str, region: builtins.str) -> None:
        '''(experimental) Stack information.

        :param account: 
        :param region: 

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1dcdad24849926b01541cd5e3a49b2718bca23f70268629b13a2467789ce6acc)
            check_type(argname="argument account", value=account, expected_type=type_hints["account"])
            check_type(argname="argument region", value=region, expected_type=type_hints["region"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "account": account,
            "region": region,
        }

    @builtins.property
    def account(self) -> builtins.str:
        '''
        :stability: experimental
        '''
        result = self._values.get("account")
        assert result is not None, "Required property 'account' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def region(self) -> builtins.str:
        '''
        :stability: experimental
        '''
        result = self._values.get("region")
        assert result is not None, "Required property 'region' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "LambdaIamUtilsStackInfo(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdklabs/cdk-appmod-catalog-blueprints.LambdaLogsPermissionsProps",
    jsii_struct_bases=[],
    name_mapping={
        "account": "account",
        "function_name": "functionName",
        "region": "region",
        "scope": "scope",
        "enable_observability": "enableObservability",
        "log_group_name": "logGroupName",
    },
)
class LambdaLogsPermissionsProps:
    def __init__(
        self,
        *,
        account: builtins.str,
        function_name: builtins.str,
        region: builtins.str,
        scope: _constructs_77d1e7e8.Construct,
        enable_observability: typing.Optional[builtins.bool] = None,
        log_group_name: typing.Optional[builtins.str] = None,
    ) -> None:
        '''(experimental) Configuration options for Lambda CloudWatch Logs permissions.

        :param account: (experimental) AWS account ID for the log group ARN.
        :param function_name: (experimental) The base name of the Lambda function.
        :param region: (experimental) AWS region for the log group ARN.
        :param scope: (experimental) The construct scope (used to generate unique names).
        :param enable_observability: (experimental) Whether observability is enabled or not. This would have an impact on the result IAM policy for the LogGroup for the Lambda function Default: false
        :param log_group_name: (experimental) Custom log group name pattern. Default: '/aws/lambda/{uniqueFunctionName}'

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__47564dc2777638ca33ba53983ac385b2dd8b03133d66569da912ae1ce7e55503)
            check_type(argname="argument account", value=account, expected_type=type_hints["account"])
            check_type(argname="argument function_name", value=function_name, expected_type=type_hints["function_name"])
            check_type(argname="argument region", value=region, expected_type=type_hints["region"])
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument enable_observability", value=enable_observability, expected_type=type_hints["enable_observability"])
            check_type(argname="argument log_group_name", value=log_group_name, expected_type=type_hints["log_group_name"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "account": account,
            "function_name": function_name,
            "region": region,
            "scope": scope,
        }
        if enable_observability is not None:
            self._values["enable_observability"] = enable_observability
        if log_group_name is not None:
            self._values["log_group_name"] = log_group_name

    @builtins.property
    def account(self) -> builtins.str:
        '''(experimental) AWS account ID for the log group ARN.

        :stability: experimental
        '''
        result = self._values.get("account")
        assert result is not None, "Required property 'account' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def function_name(self) -> builtins.str:
        '''(experimental) The base name of the Lambda function.

        :stability: experimental
        '''
        result = self._values.get("function_name")
        assert result is not None, "Required property 'function_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def region(self) -> builtins.str:
        '''(experimental) AWS region for the log group ARN.

        :stability: experimental
        '''
        result = self._values.get("region")
        assert result is not None, "Required property 'region' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def scope(self) -> _constructs_77d1e7e8.Construct:
        '''(experimental) The construct scope (used to generate unique names).

        :stability: experimental
        '''
        result = self._values.get("scope")
        assert result is not None, "Required property 'scope' is missing"
        return typing.cast(_constructs_77d1e7e8.Construct, result)

    @builtins.property
    def enable_observability(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Whether observability is enabled or not.

        This would have an impact
        on the result IAM policy for the LogGroup for the Lambda function

        :default: false

        :stability: experimental
        '''
        result = self._values.get("enable_observability")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def log_group_name(self) -> typing.Optional[builtins.str]:
        '''(experimental) Custom log group name pattern.

        :default: '/aws/lambda/{uniqueFunctionName}'

        :stability: experimental
        '''
        result = self._values.get("log_group_name")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "LambdaLogsPermissionsProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdklabs/cdk-appmod-catalog-blueprints.LambdaLogsPermissionsResult",
    jsii_struct_bases=[],
    name_mapping={
        "policy_statements": "policyStatements",
        "unique_function_name": "uniqueFunctionName",
    },
)
class LambdaLogsPermissionsResult:
    def __init__(
        self,
        *,
        policy_statements: typing.Sequence[_aws_cdk_aws_iam_ceddda9d.PolicyStatement],
        unique_function_name: builtins.str,
    ) -> None:
        '''(experimental) Result of creating Lambda logs permissions.

        :param policy_statements: (experimental) The policy statements for CloudWatch Logs.
        :param unique_function_name: (experimental) The unique function name that was generated.

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2180e53f0ba520cfa92d16443491985db8ed304d09797b9d758ad70b55d7b617)
            check_type(argname="argument policy_statements", value=policy_statements, expected_type=type_hints["policy_statements"])
            check_type(argname="argument unique_function_name", value=unique_function_name, expected_type=type_hints["unique_function_name"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "policy_statements": policy_statements,
            "unique_function_name": unique_function_name,
        }

    @builtins.property
    def policy_statements(
        self,
    ) -> typing.List[_aws_cdk_aws_iam_ceddda9d.PolicyStatement]:
        '''(experimental) The policy statements for CloudWatch Logs.

        :stability: experimental
        '''
        result = self._values.get("policy_statements")
        assert result is not None, "Required property 'policy_statements' is missing"
        return typing.cast(typing.List[_aws_cdk_aws_iam_ceddda9d.PolicyStatement], result)

    @builtins.property
    def unique_function_name(self) -> builtins.str:
        '''(experimental) The unique function name that was generated.

        :stability: experimental
        '''
        result = self._values.get("unique_function_name")
        assert result is not None, "Required property 'unique_function_name' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "LambdaLogsPermissionsResult(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.implements(_aws_cdk_ceddda9d.IPropertyInjector)
class LambdaObservabilityPropertyInjector(
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdklabs/cdk-appmod-catalog-blueprints.LambdaObservabilityPropertyInjector",
):
    '''
    :stability: experimental
    '''

    def __init__(
        self,
        *,
        data_protection_identifiers: typing.Optional[typing.Sequence[_aws_cdk_aws_logs_ceddda9d.DataIdentifier]] = None,
        log_group_encryption_key: typing.Optional[_aws_cdk_aws_kms_ceddda9d.Key] = None,
    ) -> None:
        '''
        :param data_protection_identifiers: (experimental) List of DataIdentifiers that would be used as part of the Data Protection Policy that would be created for the log group. Default: Data Protection Policy won't be enabled
        :param log_group_encryption_key: (experimental) Encryption key that would be used to encrypt the relevant log group. Default: a new KMS key would automatically be created

        :stability: experimental
        '''
        log_group_data_protection = LogGroupDataProtectionProps(
            data_protection_identifiers=data_protection_identifiers,
            log_group_encryption_key=log_group_encryption_key,
        )

        jsii.create(self.__class__, self, [log_group_data_protection])

    @jsii.member(jsii_name="inject")
    def inject(
        self,
        original_props: typing.Any,
        *,
        id: builtins.str,
        scope: _constructs_77d1e7e8.Construct,
    ) -> typing.Any:
        '''(experimental) The injector to be applied to the constructor properties of the Construct.

        :param original_props: -
        :param id: id from the Construct constructor.
        :param scope: scope from the constructor.

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__97c5107ef8c7184168153144168438a4ff4ae054305d1a82db0a0514c98b6d0b)
            check_type(argname="argument original_props", value=original_props, expected_type=type_hints["original_props"])
        _context = _aws_cdk_ceddda9d.InjectionContext(id=id, scope=scope)

        return typing.cast(typing.Any, jsii.invoke(self, "inject", [original_props, _context]))

    @builtins.property
    @jsii.member(jsii_name="constructUniqueId")
    def construct_unique_id(self) -> builtins.str:
        '''(experimental) The unique Id of the Construct class.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "constructUniqueId"))

    @builtins.property
    @jsii.member(jsii_name="logGroupDataProtection")
    def log_group_data_protection(self) -> "LogGroupDataProtectionProps":
        '''
        :stability: experimental
        '''
        return typing.cast("LogGroupDataProtectionProps", jsii.get(self, "logGroupDataProtection"))


@jsii.data_type(
    jsii_type="@cdklabs/cdk-appmod-catalog-blueprints.LogGroupDataProtectionProps",
    jsii_struct_bases=[],
    name_mapping={
        "data_protection_identifiers": "dataProtectionIdentifiers",
        "log_group_encryption_key": "logGroupEncryptionKey",
    },
)
class LogGroupDataProtectionProps:
    def __init__(
        self,
        *,
        data_protection_identifiers: typing.Optional[typing.Sequence[_aws_cdk_aws_logs_ceddda9d.DataIdentifier]] = None,
        log_group_encryption_key: typing.Optional[_aws_cdk_aws_kms_ceddda9d.Key] = None,
    ) -> None:
        '''(experimental) Props to enable various data protection configuration for CloudWatch Log Groups.

        :param data_protection_identifiers: (experimental) List of DataIdentifiers that would be used as part of the Data Protection Policy that would be created for the log group. Default: Data Protection Policy won't be enabled
        :param log_group_encryption_key: (experimental) Encryption key that would be used to encrypt the relevant log group. Default: a new KMS key would automatically be created

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__544372751dab1bedee4ed043bef50312abd2658c1142e4b4809c0617165dc597)
            check_type(argname="argument data_protection_identifiers", value=data_protection_identifiers, expected_type=type_hints["data_protection_identifiers"])
            check_type(argname="argument log_group_encryption_key", value=log_group_encryption_key, expected_type=type_hints["log_group_encryption_key"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if data_protection_identifiers is not None:
            self._values["data_protection_identifiers"] = data_protection_identifiers
        if log_group_encryption_key is not None:
            self._values["log_group_encryption_key"] = log_group_encryption_key

    @builtins.property
    def data_protection_identifiers(
        self,
    ) -> typing.Optional[typing.List[_aws_cdk_aws_logs_ceddda9d.DataIdentifier]]:
        '''(experimental) List of DataIdentifiers that would be used as part of the Data Protection Policy that would be created for the log group.

        :default: Data Protection Policy won't be enabled

        :stability: experimental
        '''
        result = self._values.get("data_protection_identifiers")
        return typing.cast(typing.Optional[typing.List[_aws_cdk_aws_logs_ceddda9d.DataIdentifier]], result)

    @builtins.property
    def log_group_encryption_key(
        self,
    ) -> typing.Optional[_aws_cdk_aws_kms_ceddda9d.Key]:
        '''(experimental) Encryption key that would be used to encrypt the relevant log group.

        :default: a new KMS key would automatically be created

        :stability: experimental
        '''
        result = self._values.get("log_group_encryption_key")
        return typing.cast(typing.Optional[_aws_cdk_aws_kms_ceddda9d.Key], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "LogGroupDataProtectionProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class Network(
    _constructs_77d1e7e8.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdklabs/cdk-appmod-catalog-blueprints.Network",
):
    '''
    :stability: experimental
    '''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        ip_addresses: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.IIpAddresses] = None,
        max_azs: typing.Optional[jsii.Number] = None,
        nat_gateway_provider: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.NatProvider] = None,
        nat_gateways: typing.Optional[jsii.Number] = None,
        nat_gateway_subnets: typing.Optional[typing.Union[_aws_cdk_aws_ec2_ceddda9d.SubnetSelection, typing.Dict[builtins.str, typing.Any]]] = None,
        private: typing.Optional[builtins.bool] = None,
        subnet_configuration: typing.Optional[typing.Sequence[typing.Union[_aws_cdk_aws_ec2_ceddda9d.SubnetConfiguration, typing.Dict[builtins.str, typing.Any]]]] = None,
        vpc_name: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param ip_addresses: 
        :param max_azs: 
        :param nat_gateway_provider: 
        :param nat_gateways: 
        :param nat_gateway_subnets: 
        :param private: 
        :param subnet_configuration: 
        :param vpc_name: 

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6ad9a3df68ffea56f493c494b7c642fca53d11a7de99864bb5e94dffe00ed330)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = NetworkProps(
            ip_addresses=ip_addresses,
            max_azs=max_azs,
            nat_gateway_provider=nat_gateway_provider,
            nat_gateways=nat_gateways,
            nat_gateway_subnets=nat_gateway_subnets,
            private=private,
            subnet_configuration=subnet_configuration,
            vpc_name=vpc_name,
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @jsii.member(jsii_name="applicationSubnetSelection")
    def application_subnet_selection(self) -> _aws_cdk_aws_ec2_ceddda9d.SubnetSelection:
        '''
        :stability: experimental
        '''
        return typing.cast(_aws_cdk_aws_ec2_ceddda9d.SubnetSelection, jsii.invoke(self, "applicationSubnetSelection", []))

    @jsii.member(jsii_name="createServiceEndpoint")
    def create_service_endpoint(
        self,
        id: builtins.str,
        service: _aws_cdk_aws_ec2_ceddda9d.InterfaceVpcEndpointService,
        peer: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.IPeer] = None,
    ) -> _aws_cdk_aws_ec2_ceddda9d.InterfaceVpcEndpoint:
        '''
        :param id: -
        :param service: -
        :param peer: -

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__014347d1e11f93271eb3a6b34bc02d137814401023f915adcd8e379b691810e9)
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
            check_type(argname="argument service", value=service, expected_type=type_hints["service"])
            check_type(argname="argument peer", value=peer, expected_type=type_hints["peer"])
        return typing.cast(_aws_cdk_aws_ec2_ceddda9d.InterfaceVpcEndpoint, jsii.invoke(self, "createServiceEndpoint", [id, service, peer]))

    @builtins.property
    @jsii.member(jsii_name="vpc")
    def vpc(self) -> _aws_cdk_aws_ec2_ceddda9d.Vpc:
        '''
        :stability: experimental
        '''
        return typing.cast(_aws_cdk_aws_ec2_ceddda9d.Vpc, jsii.get(self, "vpc"))


@jsii.data_type(
    jsii_type="@cdklabs/cdk-appmod-catalog-blueprints.NetworkProps",
    jsii_struct_bases=[],
    name_mapping={
        "ip_addresses": "ipAddresses",
        "max_azs": "maxAzs",
        "nat_gateway_provider": "natGatewayProvider",
        "nat_gateways": "natGateways",
        "nat_gateway_subnets": "natGatewaySubnets",
        "private": "private",
        "subnet_configuration": "subnetConfiguration",
        "vpc_name": "vpcName",
    },
)
class NetworkProps:
    def __init__(
        self,
        *,
        ip_addresses: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.IIpAddresses] = None,
        max_azs: typing.Optional[jsii.Number] = None,
        nat_gateway_provider: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.NatProvider] = None,
        nat_gateways: typing.Optional[jsii.Number] = None,
        nat_gateway_subnets: typing.Optional[typing.Union[_aws_cdk_aws_ec2_ceddda9d.SubnetSelection, typing.Dict[builtins.str, typing.Any]]] = None,
        private: typing.Optional[builtins.bool] = None,
        subnet_configuration: typing.Optional[typing.Sequence[typing.Union[_aws_cdk_aws_ec2_ceddda9d.SubnetConfiguration, typing.Dict[builtins.str, typing.Any]]]] = None,
        vpc_name: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param ip_addresses: 
        :param max_azs: 
        :param nat_gateway_provider: 
        :param nat_gateways: 
        :param nat_gateway_subnets: 
        :param private: 
        :param subnet_configuration: 
        :param vpc_name: 

        :stability: experimental
        '''
        if isinstance(nat_gateway_subnets, dict):
            nat_gateway_subnets = _aws_cdk_aws_ec2_ceddda9d.SubnetSelection(**nat_gateway_subnets)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0c7413b984143840b4fc2e4fe5dd9854fed611c52a71931a04773289b6f1fdde)
            check_type(argname="argument ip_addresses", value=ip_addresses, expected_type=type_hints["ip_addresses"])
            check_type(argname="argument max_azs", value=max_azs, expected_type=type_hints["max_azs"])
            check_type(argname="argument nat_gateway_provider", value=nat_gateway_provider, expected_type=type_hints["nat_gateway_provider"])
            check_type(argname="argument nat_gateways", value=nat_gateways, expected_type=type_hints["nat_gateways"])
            check_type(argname="argument nat_gateway_subnets", value=nat_gateway_subnets, expected_type=type_hints["nat_gateway_subnets"])
            check_type(argname="argument private", value=private, expected_type=type_hints["private"])
            check_type(argname="argument subnet_configuration", value=subnet_configuration, expected_type=type_hints["subnet_configuration"])
            check_type(argname="argument vpc_name", value=vpc_name, expected_type=type_hints["vpc_name"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if ip_addresses is not None:
            self._values["ip_addresses"] = ip_addresses
        if max_azs is not None:
            self._values["max_azs"] = max_azs
        if nat_gateway_provider is not None:
            self._values["nat_gateway_provider"] = nat_gateway_provider
        if nat_gateways is not None:
            self._values["nat_gateways"] = nat_gateways
        if nat_gateway_subnets is not None:
            self._values["nat_gateway_subnets"] = nat_gateway_subnets
        if private is not None:
            self._values["private"] = private
        if subnet_configuration is not None:
            self._values["subnet_configuration"] = subnet_configuration
        if vpc_name is not None:
            self._values["vpc_name"] = vpc_name

    @builtins.property
    def ip_addresses(self) -> typing.Optional[_aws_cdk_aws_ec2_ceddda9d.IIpAddresses]:
        '''
        :stability: experimental
        '''
        result = self._values.get("ip_addresses")
        return typing.cast(typing.Optional[_aws_cdk_aws_ec2_ceddda9d.IIpAddresses], result)

    @builtins.property
    def max_azs(self) -> typing.Optional[jsii.Number]:
        '''
        :stability: experimental
        '''
        result = self._values.get("max_azs")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def nat_gateway_provider(
        self,
    ) -> typing.Optional[_aws_cdk_aws_ec2_ceddda9d.NatProvider]:
        '''
        :stability: experimental
        '''
        result = self._values.get("nat_gateway_provider")
        return typing.cast(typing.Optional[_aws_cdk_aws_ec2_ceddda9d.NatProvider], result)

    @builtins.property
    def nat_gateways(self) -> typing.Optional[jsii.Number]:
        '''
        :stability: experimental
        '''
        result = self._values.get("nat_gateways")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def nat_gateway_subnets(
        self,
    ) -> typing.Optional[_aws_cdk_aws_ec2_ceddda9d.SubnetSelection]:
        '''
        :stability: experimental
        '''
        result = self._values.get("nat_gateway_subnets")
        return typing.cast(typing.Optional[_aws_cdk_aws_ec2_ceddda9d.SubnetSelection], result)

    @builtins.property
    def private(self) -> typing.Optional[builtins.bool]:
        '''
        :stability: experimental
        '''
        result = self._values.get("private")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def subnet_configuration(
        self,
    ) -> typing.Optional[typing.List[_aws_cdk_aws_ec2_ceddda9d.SubnetConfiguration]]:
        '''
        :stability: experimental
        '''
        result = self._values.get("subnet_configuration")
        return typing.cast(typing.Optional[typing.List[_aws_cdk_aws_ec2_ceddda9d.SubnetConfiguration]], result)

    @builtins.property
    def vpc_name(self) -> typing.Optional[builtins.str]:
        '''
        :stability: experimental
        '''
        result = self._values.get("vpc_name")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "NetworkProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdklabs/cdk-appmod-catalog-blueprints.ObservableProps",
    jsii_struct_bases=[],
    name_mapping={
        "log_group_data_protection": "logGroupDataProtection",
        "metric_namespace": "metricNamespace",
        "metric_service_name": "metricServiceName",
    },
)
class ObservableProps:
    def __init__(
        self,
        *,
        log_group_data_protection: typing.Optional[typing.Union[LogGroupDataProtectionProps, typing.Dict[builtins.str, typing.Any]]] = None,
        metric_namespace: typing.Optional[builtins.str] = None,
        metric_service_name: typing.Optional[builtins.str] = None,
    ) -> None:
        '''(experimental) Additional properties that constructs implementing the IObservable interface should extend as part of their input props.

        :param log_group_data_protection: (experimental) Data protection related configuration. Default: a new KMS key would be generated
        :param metric_namespace: (experimental) Business metric namespace. Default: would be defined per use case
        :param metric_service_name: (experimental) Business metric service name dimension. Default: would be defined per use case

        :stability: experimental
        '''
        if isinstance(log_group_data_protection, dict):
            log_group_data_protection = LogGroupDataProtectionProps(**log_group_data_protection)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__31fd1e05df7b558405e183d7153d9217ec52b5d7deb1bd88be445a2930061329)
            check_type(argname="argument log_group_data_protection", value=log_group_data_protection, expected_type=type_hints["log_group_data_protection"])
            check_type(argname="argument metric_namespace", value=metric_namespace, expected_type=type_hints["metric_namespace"])
            check_type(argname="argument metric_service_name", value=metric_service_name, expected_type=type_hints["metric_service_name"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if log_group_data_protection is not None:
            self._values["log_group_data_protection"] = log_group_data_protection
        if metric_namespace is not None:
            self._values["metric_namespace"] = metric_namespace
        if metric_service_name is not None:
            self._values["metric_service_name"] = metric_service_name

    @builtins.property
    def log_group_data_protection(self) -> typing.Optional[LogGroupDataProtectionProps]:
        '''(experimental) Data protection related configuration.

        :default: a new KMS key would be generated

        :stability: experimental
        '''
        result = self._values.get("log_group_data_protection")
        return typing.cast(typing.Optional[LogGroupDataProtectionProps], result)

    @builtins.property
    def metric_namespace(self) -> typing.Optional[builtins.str]:
        '''(experimental) Business metric namespace.

        :default: would be defined per use case

        :stability: experimental
        '''
        result = self._values.get("metric_namespace")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def metric_service_name(self) -> typing.Optional[builtins.str]:
        '''(experimental) Business metric service name dimension.

        :default: would be defined per use case

        :stability: experimental
        '''
        result = self._values.get("metric_service_name")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ObservableProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class PowertoolsConfig(
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdklabs/cdk-appmod-catalog-blueprints.PowertoolsConfig",
):
    '''
    :stability: experimental
    '''

    def __init__(self) -> None:
        '''
        :stability: experimental
        '''
        jsii.create(self.__class__, self, [])

    @jsii.member(jsii_name="generateDefaultLambdaConfig")
    @builtins.classmethod
    def generate_default_lambda_config(
        cls,
        enable_observability: typing.Optional[builtins.bool] = None,
        metrics_namespace: typing.Optional[builtins.str] = None,
        service_name: typing.Optional[builtins.str] = None,
    ) -> typing.Mapping[builtins.str, builtins.str]:
        '''
        :param enable_observability: -
        :param metrics_namespace: -
        :param service_name: -

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e065c545d4fce5c4fc2579c3efea8203f50b6d3c8b39aa1595ea3577d04bc025)
            check_type(argname="argument enable_observability", value=enable_observability, expected_type=type_hints["enable_observability"])
            check_type(argname="argument metrics_namespace", value=metrics_namespace, expected_type=type_hints["metrics_namespace"])
            check_type(argname="argument service_name", value=service_name, expected_type=type_hints["service_name"])
        return typing.cast(typing.Mapping[builtins.str, builtins.str], jsii.sinvoke(cls, "generateDefaultLambdaConfig", [enable_observability, metrics_namespace, service_name]))


@jsii.implements(IAdapter)
class QueuedS3Adapter(
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdklabs/cdk-appmod-catalog-blueprints.QueuedS3Adapter",
):
    '''(experimental) This adapter allows the intelligent document processing workflow to be triggered by files that are uploaded into a S3 Bucket.

    :stability: experimental
    '''

    def __init__(
        self,
        *,
        bucket: typing.Optional[_aws_cdk_aws_s3_ceddda9d.Bucket] = None,
        dlq_max_receive_count: typing.Optional[jsii.Number] = None,
        failed_prefix: typing.Optional[builtins.str] = None,
        processed_prefix: typing.Optional[builtins.str] = None,
        queue_visibility_timeout: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
        raw_prefix: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param bucket: (experimental) S3 bucket for document storage with organized prefixes (raw/, processed/, failed/). If not provided, a new bucket will be created with auto-delete enabled based on removalPolicy. Default: create a new bucket
        :param dlq_max_receive_count: (experimental) The number of times a message can be unsuccessfully dequeued before being moved to the dead-letter queue. Default: 5
        :param failed_prefix: (experimental) S3 prefix where the files that failed processing would be stored. Default: "failed/"
        :param processed_prefix: (experimental) S3 prefix where the processed files would be stored. Default: "processed/"
        :param queue_visibility_timeout: (experimental) SQS queue visibility timeout for processing messages. Should be longer than expected processing time to prevent duplicate processing. Default: Duration.seconds(300)
        :param raw_prefix: (experimental) S3 prefix where the raw files would be stored. This serves as the trigger point for processing Default: "raw/"

        :stability: experimental
        '''
        adapter_props = QueuedS3AdapterProps(
            bucket=bucket,
            dlq_max_receive_count=dlq_max_receive_count,
            failed_prefix=failed_prefix,
            processed_prefix=processed_prefix,
            queue_visibility_timeout=queue_visibility_timeout,
            raw_prefix=raw_prefix,
        )

        jsii.create(self.__class__, self, [adapter_props])

    @jsii.member(jsii_name="createFailedChain")
    def create_failed_chain(
        self,
        scope: _constructs_77d1e7e8.Construct,
    ) -> _aws_cdk_aws_stepfunctions_ceddda9d.Chain:
        '''(experimental) Create the adapter specific handler for failed processing.

        :param scope: -

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b95daf862a9819daa9b25cecfc08214dc429ef07ac6de3920b5dea59e01616eb)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
        return typing.cast(_aws_cdk_aws_stepfunctions_ceddda9d.Chain, jsii.invoke(self, "createFailedChain", [scope]))

    @jsii.member(jsii_name="createIngressTrigger")
    def create_ingress_trigger(
        self,
        scope: _constructs_77d1e7e8.Construct,
        state_machine: _aws_cdk_aws_stepfunctions_ceddda9d.StateMachine,
        *,
        document_processing_table: typing.Optional[_aws_cdk_aws_dynamodb_ceddda9d.Table] = None,
        enable_observability: typing.Optional[builtins.bool] = None,
        encryption_key: typing.Optional[_aws_cdk_aws_kms_ceddda9d.Key] = None,
        eventbridge_broker: typing.Optional[EventbridgeBroker] = None,
        ingress_adapter: typing.Optional[IAdapter] = None,
        network: typing.Optional[Network] = None,
        removal_policy: typing.Optional[_aws_cdk_ceddda9d.RemovalPolicy] = None,
        workflow_timeout: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
        log_group_data_protection: typing.Optional[typing.Union[LogGroupDataProtectionProps, typing.Dict[builtins.str, typing.Any]]] = None,
        metric_namespace: typing.Optional[builtins.str] = None,
        metric_service_name: typing.Optional[builtins.str] = None,
    ) -> typing.Mapping[builtins.str, typing.Any]:
        '''(experimental) Create resources that would receive the data and trigger the workflow.

        Important: resource created should trigger the state machine

        :param scope: -
        :param state_machine: -
        :param document_processing_table: (experimental) DynamoDB table for storing document processing metadata and workflow state. If not provided, a new table will be created with DocumentId as partition key.
        :param enable_observability: (experimental) Enable logging and tracing for all supporting resource. Default: false
        :param encryption_key: (experimental) KMS key to be used. Default: A new key would be created
        :param eventbridge_broker: (experimental) Optional EventBridge broker for publishing custom events during processing. If not provided, no custom events will be sent out.
        :param ingress_adapter: (experimental) Adapter that defines how the document processing workflow is triggered. Default: QueuedS3Adapter
        :param network: (experimental) Resources that can run inside a VPC will follow the provided network configuration. Default: resources will run outside of a VPC
        :param removal_policy: (experimental) Removal policy for created resources (bucket, table, queue). Default: RemovalPolicy.DESTROY
        :param workflow_timeout: (experimental) Maximum execution time for the Step Functions workflow. Default: Duration.minutes(30)
        :param log_group_data_protection: (experimental) Data protection related configuration. Default: a new KMS key would be generated
        :param metric_namespace: (experimental) Business metric namespace. Default: would be defined per use case
        :param metric_service_name: (experimental) Business metric service name dimension. Default: would be defined per use case

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__fb0e9adf74054c1b0a1974cab45642af57cb1651ef8052310a0229dae1eac178)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument state_machine", value=state_machine, expected_type=type_hints["state_machine"])
        props = BaseDocumentProcessingProps(
            document_processing_table=document_processing_table,
            enable_observability=enable_observability,
            encryption_key=encryption_key,
            eventbridge_broker=eventbridge_broker,
            ingress_adapter=ingress_adapter,
            network=network,
            removal_policy=removal_policy,
            workflow_timeout=workflow_timeout,
            log_group_data_protection=log_group_data_protection,
            metric_namespace=metric_namespace,
            metric_service_name=metric_service_name,
        )

        return typing.cast(typing.Mapping[builtins.str, typing.Any], jsii.invoke(self, "createIngressTrigger", [scope, state_machine, props]))

    @jsii.member(jsii_name="createSuccessChain")
    def create_success_chain(
        self,
        scope: _constructs_77d1e7e8.Construct,
    ) -> _aws_cdk_aws_stepfunctions_ceddda9d.Chain:
        '''(experimental) Create the adapter specific handler for successful processing.

        :param scope: -

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__76aa2fd577ace3b2507bf11a33f4d039ae5ac0af0d5d3edede30c4515a1a0986)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
        return typing.cast(_aws_cdk_aws_stepfunctions_ceddda9d.Chain, jsii.invoke(self, "createSuccessChain", [scope]))

    @jsii.member(jsii_name="generateAdapterIAMPolicies")
    def generate_adapter_iam_policies(
        self,
        additional_iam_actions: typing.Optional[typing.Sequence[builtins.str]] = None,
        narrow_actions: typing.Optional[builtins.bool] = None,
    ) -> typing.List[_aws_cdk_aws_iam_ceddda9d.PolicyStatement]:
        '''(experimental) Generate IAM statements that can be used by other resources to access the storage.

        :param additional_iam_actions: -
        :param narrow_actions: -

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__308867c51abfbbc08d0fba9125db9b86eddda969dc95de8546e6f8cb242ee8a9)
            check_type(argname="argument additional_iam_actions", value=additional_iam_actions, expected_type=type_hints["additional_iam_actions"])
            check_type(argname="argument narrow_actions", value=narrow_actions, expected_type=type_hints["narrow_actions"])
        return typing.cast(typing.List[_aws_cdk_aws_iam_ceddda9d.PolicyStatement], jsii.invoke(self, "generateAdapterIAMPolicies", [additional_iam_actions, narrow_actions]))

    @jsii.member(jsii_name="init")
    def init(
        self,
        scope: _constructs_77d1e7e8.Construct,
        *,
        document_processing_table: typing.Optional[_aws_cdk_aws_dynamodb_ceddda9d.Table] = None,
        enable_observability: typing.Optional[builtins.bool] = None,
        encryption_key: typing.Optional[_aws_cdk_aws_kms_ceddda9d.Key] = None,
        eventbridge_broker: typing.Optional[EventbridgeBroker] = None,
        ingress_adapter: typing.Optional[IAdapter] = None,
        network: typing.Optional[Network] = None,
        removal_policy: typing.Optional[_aws_cdk_ceddda9d.RemovalPolicy] = None,
        workflow_timeout: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
        log_group_data_protection: typing.Optional[typing.Union[LogGroupDataProtectionProps, typing.Dict[builtins.str, typing.Any]]] = None,
        metric_namespace: typing.Optional[builtins.str] = None,
        metric_service_name: typing.Optional[builtins.str] = None,
    ) -> None:
        '''(experimental) Initializes the adapter.

        :param scope: -
        :param document_processing_table: (experimental) DynamoDB table for storing document processing metadata and workflow state. If not provided, a new table will be created with DocumentId as partition key.
        :param enable_observability: (experimental) Enable logging and tracing for all supporting resource. Default: false
        :param encryption_key: (experimental) KMS key to be used. Default: A new key would be created
        :param eventbridge_broker: (experimental) Optional EventBridge broker for publishing custom events during processing. If not provided, no custom events will be sent out.
        :param ingress_adapter: (experimental) Adapter that defines how the document processing workflow is triggered. Default: QueuedS3Adapter
        :param network: (experimental) Resources that can run inside a VPC will follow the provided network configuration. Default: resources will run outside of a VPC
        :param removal_policy: (experimental) Removal policy for created resources (bucket, table, queue). Default: RemovalPolicy.DESTROY
        :param workflow_timeout: (experimental) Maximum execution time for the Step Functions workflow. Default: Duration.minutes(30)
        :param log_group_data_protection: (experimental) Data protection related configuration. Default: a new KMS key would be generated
        :param metric_namespace: (experimental) Business metric namespace. Default: would be defined per use case
        :param metric_service_name: (experimental) Business metric service name dimension. Default: would be defined per use case

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3fe79d0c4a3a771012bc95cea6a690155ea89fa70073f87564e65aad5cdfdb64)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
        props = BaseDocumentProcessingProps(
            document_processing_table=document_processing_table,
            enable_observability=enable_observability,
            encryption_key=encryption_key,
            eventbridge_broker=eventbridge_broker,
            ingress_adapter=ingress_adapter,
            network=network,
            removal_policy=removal_policy,
            workflow_timeout=workflow_timeout,
            log_group_data_protection=log_group_data_protection,
            metric_namespace=metric_namespace,
            metric_service_name=metric_service_name,
        )

        return typing.cast(None, jsii.invoke(self, "init", [scope, props]))


@jsii.data_type(
    jsii_type="@cdklabs/cdk-appmod-catalog-blueprints.QueuedS3AdapterProps",
    jsii_struct_bases=[],
    name_mapping={
        "bucket": "bucket",
        "dlq_max_receive_count": "dlqMaxReceiveCount",
        "failed_prefix": "failedPrefix",
        "processed_prefix": "processedPrefix",
        "queue_visibility_timeout": "queueVisibilityTimeout",
        "raw_prefix": "rawPrefix",
    },
)
class QueuedS3AdapterProps:
    def __init__(
        self,
        *,
        bucket: typing.Optional[_aws_cdk_aws_s3_ceddda9d.Bucket] = None,
        dlq_max_receive_count: typing.Optional[jsii.Number] = None,
        failed_prefix: typing.Optional[builtins.str] = None,
        processed_prefix: typing.Optional[builtins.str] = None,
        queue_visibility_timeout: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
        raw_prefix: typing.Optional[builtins.str] = None,
    ) -> None:
        '''(experimental) Props for the Queued S3 Adapter.

        :param bucket: (experimental) S3 bucket for document storage with organized prefixes (raw/, processed/, failed/). If not provided, a new bucket will be created with auto-delete enabled based on removalPolicy. Default: create a new bucket
        :param dlq_max_receive_count: (experimental) The number of times a message can be unsuccessfully dequeued before being moved to the dead-letter queue. Default: 5
        :param failed_prefix: (experimental) S3 prefix where the files that failed processing would be stored. Default: "failed/"
        :param processed_prefix: (experimental) S3 prefix where the processed files would be stored. Default: "processed/"
        :param queue_visibility_timeout: (experimental) SQS queue visibility timeout for processing messages. Should be longer than expected processing time to prevent duplicate processing. Default: Duration.seconds(300)
        :param raw_prefix: (experimental) S3 prefix where the raw files would be stored. This serves as the trigger point for processing Default: "raw/"

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c2db7ec0d4b3e93062e1f20f29f9821e5a0fd526ecf05f9ccaa6db663fb1e8de)
            check_type(argname="argument bucket", value=bucket, expected_type=type_hints["bucket"])
            check_type(argname="argument dlq_max_receive_count", value=dlq_max_receive_count, expected_type=type_hints["dlq_max_receive_count"])
            check_type(argname="argument failed_prefix", value=failed_prefix, expected_type=type_hints["failed_prefix"])
            check_type(argname="argument processed_prefix", value=processed_prefix, expected_type=type_hints["processed_prefix"])
            check_type(argname="argument queue_visibility_timeout", value=queue_visibility_timeout, expected_type=type_hints["queue_visibility_timeout"])
            check_type(argname="argument raw_prefix", value=raw_prefix, expected_type=type_hints["raw_prefix"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if bucket is not None:
            self._values["bucket"] = bucket
        if dlq_max_receive_count is not None:
            self._values["dlq_max_receive_count"] = dlq_max_receive_count
        if failed_prefix is not None:
            self._values["failed_prefix"] = failed_prefix
        if processed_prefix is not None:
            self._values["processed_prefix"] = processed_prefix
        if queue_visibility_timeout is not None:
            self._values["queue_visibility_timeout"] = queue_visibility_timeout
        if raw_prefix is not None:
            self._values["raw_prefix"] = raw_prefix

    @builtins.property
    def bucket(self) -> typing.Optional[_aws_cdk_aws_s3_ceddda9d.Bucket]:
        '''(experimental) S3 bucket for document storage with organized prefixes (raw/, processed/, failed/).

        If not provided, a new bucket will be created with auto-delete enabled based on removalPolicy.

        :default: create a new bucket

        :stability: experimental
        '''
        result = self._values.get("bucket")
        return typing.cast(typing.Optional[_aws_cdk_aws_s3_ceddda9d.Bucket], result)

    @builtins.property
    def dlq_max_receive_count(self) -> typing.Optional[jsii.Number]:
        '''(experimental) The number of times a message can be unsuccessfully dequeued before being moved to the dead-letter queue.

        :default: 5

        :stability: experimental
        '''
        result = self._values.get("dlq_max_receive_count")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def failed_prefix(self) -> typing.Optional[builtins.str]:
        '''(experimental) S3 prefix where the files that failed processing would be stored.

        :default: "failed/"

        :stability: experimental
        '''
        result = self._values.get("failed_prefix")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def processed_prefix(self) -> typing.Optional[builtins.str]:
        '''(experimental) S3 prefix where the processed files would be stored.

        :default: "processed/"

        :stability: experimental
        '''
        result = self._values.get("processed_prefix")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def queue_visibility_timeout(self) -> typing.Optional[_aws_cdk_ceddda9d.Duration]:
        '''(experimental) SQS queue visibility timeout for processing messages.

        Should be longer than expected processing time to prevent duplicate processing.

        :default: Duration.seconds(300)

        :stability: experimental
        '''
        result = self._values.get("queue_visibility_timeout")
        return typing.cast(typing.Optional[_aws_cdk_ceddda9d.Duration], result)

    @builtins.property
    def raw_prefix(self) -> typing.Optional[builtins.str]:
        '''(experimental) S3 prefix where the raw files would be stored.

        This serves as the trigger point for processing

        :default: "raw/"

        :stability: experimental
        '''
        result = self._values.get("raw_prefix")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "QueuedS3AdapterProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.implements(_aws_cdk_ceddda9d.IPropertyInjector)
class StateMachineObservabilityPropertyInjector(
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdklabs/cdk-appmod-catalog-blueprints.StateMachineObservabilityPropertyInjector",
):
    '''
    :stability: experimental
    '''

    def __init__(
        self,
        *,
        data_protection_identifiers: typing.Optional[typing.Sequence[_aws_cdk_aws_logs_ceddda9d.DataIdentifier]] = None,
        log_group_encryption_key: typing.Optional[_aws_cdk_aws_kms_ceddda9d.Key] = None,
    ) -> None:
        '''
        :param data_protection_identifiers: (experimental) List of DataIdentifiers that would be used as part of the Data Protection Policy that would be created for the log group. Default: Data Protection Policy won't be enabled
        :param log_group_encryption_key: (experimental) Encryption key that would be used to encrypt the relevant log group. Default: a new KMS key would automatically be created

        :stability: experimental
        '''
        log_group_data_protection = LogGroupDataProtectionProps(
            data_protection_identifiers=data_protection_identifiers,
            log_group_encryption_key=log_group_encryption_key,
        )

        jsii.create(self.__class__, self, [log_group_data_protection])

    @jsii.member(jsii_name="inject")
    def inject(
        self,
        original_props: typing.Any,
        *,
        id: builtins.str,
        scope: _constructs_77d1e7e8.Construct,
    ) -> typing.Any:
        '''(experimental) The injector to be applied to the constructor properties of the Construct.

        :param original_props: -
        :param id: id from the Construct constructor.
        :param scope: scope from the constructor.

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__011b55520774139b52c951d9cc59273f686e377b5415ee42a57650da571d43e7)
            check_type(argname="argument original_props", value=original_props, expected_type=type_hints["original_props"])
        _context = _aws_cdk_ceddda9d.InjectionContext(id=id, scope=scope)

        return typing.cast(typing.Any, jsii.invoke(self, "inject", [original_props, _context]))

    @builtins.property
    @jsii.member(jsii_name="constructUniqueId")
    def construct_unique_id(self) -> builtins.str:
        '''(experimental) The unique Id of the Construct class.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "constructUniqueId"))

    @builtins.property
    @jsii.member(jsii_name="logGroupDataProtection")
    def log_group_data_protection(self) -> LogGroupDataProtectionProps:
        '''
        :stability: experimental
        '''
        return typing.cast(LogGroupDataProtectionProps, jsii.get(self, "logGroupDataProtection"))


@jsii.implements(IObservable)
class BaseDocumentProcessing(
    _constructs_77d1e7e8.Construct,
    metaclass=jsii.JSIIAbstractClass,
    jsii_type="@cdklabs/cdk-appmod-catalog-blueprints.BaseDocumentProcessing",
):
    '''(experimental) Abstract base class for serverless document processing workflows.

    Provides a complete document processing pipeline with:

    - **S3 Storage**: Organized with prefixes (raw/, processed/, failed/) for document lifecycle management
    - **SQS Queue**: Reliable message processing with configurable visibility timeout and dead letter queue
    - **DynamoDB Table**: Workflow metadata tracking with DocumentId as partition key
    - **Step Functions**: Orchestrated workflow with automatic file movement based on processing outcome
    - **Auto-triggering**: S3 event notifications automatically start processing when files are uploaded to raw/ prefix
    - **Error Handling**: Failed documents are moved to failed/ prefix with error details stored in DynamoDB
    - **EventBridge Integration**: Optional custom event publishing for workflow state changes



    Architecture Flow

    S3 Upload (raw/) → SQS → Lambda Consumer → Step Functions → Processing Steps → S3 (processed/failed/)


    Implementation Requirements

    Subclasses must implement four abstract methods to define the processing workflow:

    - ``classificationStep()``: Document type classification
    - ``extractionStep()``: Data extraction from documents
    - ``enrichmentStep()``: Optional data enrichment (return undefined to skip)
    - ``postProcessingStep()``: Optional post-processing (return undefined to skip)

    :stability: experimental
    '''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        document_processing_table: typing.Optional[_aws_cdk_aws_dynamodb_ceddda9d.Table] = None,
        enable_observability: typing.Optional[builtins.bool] = None,
        encryption_key: typing.Optional[_aws_cdk_aws_kms_ceddda9d.Key] = None,
        eventbridge_broker: typing.Optional[EventbridgeBroker] = None,
        ingress_adapter: typing.Optional[IAdapter] = None,
        network: typing.Optional[Network] = None,
        removal_policy: typing.Optional[_aws_cdk_ceddda9d.RemovalPolicy] = None,
        workflow_timeout: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
        log_group_data_protection: typing.Optional[typing.Union[LogGroupDataProtectionProps, typing.Dict[builtins.str, typing.Any]]] = None,
        metric_namespace: typing.Optional[builtins.str] = None,
        metric_service_name: typing.Optional[builtins.str] = None,
    ) -> None:
        '''(experimental) Creates a new BaseDocumentProcessing construct.

        Initializes the complete document processing infrastructure including S3 bucket,
        SQS queue, DynamoDB table, and sets up S3 event notifications to trigger processing.

        :param scope: - The scope in which to define this construct.
        :param id: - The scoped construct ID. Must be unique within the scope.
        :param document_processing_table: (experimental) DynamoDB table for storing document processing metadata and workflow state. If not provided, a new table will be created with DocumentId as partition key.
        :param enable_observability: (experimental) Enable logging and tracing for all supporting resource. Default: false
        :param encryption_key: (experimental) KMS key to be used. Default: A new key would be created
        :param eventbridge_broker: (experimental) Optional EventBridge broker for publishing custom events during processing. If not provided, no custom events will be sent out.
        :param ingress_adapter: (experimental) Adapter that defines how the document processing workflow is triggered. Default: QueuedS3Adapter
        :param network: (experimental) Resources that can run inside a VPC will follow the provided network configuration. Default: resources will run outside of a VPC
        :param removal_policy: (experimental) Removal policy for created resources (bucket, table, queue). Default: RemovalPolicy.DESTROY
        :param workflow_timeout: (experimental) Maximum execution time for the Step Functions workflow. Default: Duration.minutes(30)
        :param log_group_data_protection: (experimental) Data protection related configuration. Default: a new KMS key would be generated
        :param metric_namespace: (experimental) Business metric namespace. Default: would be defined per use case
        :param metric_service_name: (experimental) Business metric service name dimension. Default: would be defined per use case

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__117c249a26f3e7532983afc9123fadff3e20effcc69408df0f45a03eb720ea8a)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = BaseDocumentProcessingProps(
            document_processing_table=document_processing_table,
            enable_observability=enable_observability,
            encryption_key=encryption_key,
            eventbridge_broker=eventbridge_broker,
            ingress_adapter=ingress_adapter,
            network=network,
            removal_policy=removal_policy,
            workflow_timeout=workflow_timeout,
            log_group_data_protection=log_group_data_protection,
            metric_namespace=metric_namespace,
            metric_service_name=metric_service_name,
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @jsii.member(jsii_name="classificationStep")
    @abc.abstractmethod
    def _classification_step(
        self,
    ) -> typing.Union[_aws_cdk_aws_stepfunctions_tasks_ceddda9d.LambdaInvoke, _aws_cdk_aws_stepfunctions_tasks_ceddda9d.BedrockInvokeModel, _aws_cdk_aws_stepfunctions_tasks_ceddda9d.StepFunctionsStartExecution]:
        '''(experimental) Defines the document classification step of the workflow.

        **CRITICAL**: Must set ``outputPath`` to preserve workflow state for subsequent steps.
        The classification result should be available at ``$.classificationResult`` for DynamoDB storage.

        :return: Step Functions task for document classification

        :stability: experimental
        '''
        ...

    @jsii.member(jsii_name="enrichmentStep")
    @abc.abstractmethod
    def _enrichment_step(
        self,
    ) -> typing.Optional[typing.Union[_aws_cdk_aws_stepfunctions_tasks_ceddda9d.LambdaInvoke, _aws_cdk_aws_stepfunctions_tasks_ceddda9d.BedrockInvokeModel, _aws_cdk_aws_stepfunctions_tasks_ceddda9d.StepFunctionsStartExecution]]:
        '''(experimental) Defines the optional document enrichment step of the workflow.

        **CRITICAL**: If implemented, must set ``outputPath`` to preserve workflow state.
        The enrichment result should be available at ``$.enrichedResult`` for DynamoDB storage.

        :return: Step Functions task for document enrichment, or undefined to skip this step

        :stability: experimental
        '''
        ...

    @jsii.member(jsii_name="handleStateMachineCreation")
    def _handle_state_machine_creation(
        self,
        state_machine_id: builtins.str,
    ) -> _aws_cdk_aws_stepfunctions_ceddda9d.StateMachine:
        '''
        :param state_machine_id: -

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__900aa9de379313a2a9a3e24a2901f803dec0a30dde90b7255d9f180e263b020d)
            check_type(argname="argument state_machine_id", value=state_machine_id, expected_type=type_hints["state_machine_id"])
        return typing.cast(_aws_cdk_aws_stepfunctions_ceddda9d.StateMachine, jsii.invoke(self, "handleStateMachineCreation", [state_machine_id]))

    @jsii.member(jsii_name="metrics")
    def metrics(self) -> typing.List[_aws_cdk_aws_cloudwatch_ceddda9d.IMetric]:
        '''
        :stability: experimental
        '''
        return typing.cast(typing.List[_aws_cdk_aws_cloudwatch_ceddda9d.IMetric], jsii.invoke(self, "metrics", []))

    @jsii.member(jsii_name="postProcessingStep")
    @abc.abstractmethod
    def _post_processing_step(
        self,
    ) -> typing.Optional[typing.Union[_aws_cdk_aws_stepfunctions_tasks_ceddda9d.LambdaInvoke, _aws_cdk_aws_stepfunctions_tasks_ceddda9d.BedrockInvokeModel, _aws_cdk_aws_stepfunctions_tasks_ceddda9d.StepFunctionsStartExecution]]:
        '''(experimental) Defines the optional post-processing step of the workflow.

        **CRITICAL**: If implemented, must set ``outputPath`` to preserve workflow state.
        The post-processing result should be available at ``$.postProcessedResult`` for DynamoDB storage.

        :return: Step Functions task for post-processing, or undefined to skip this step

        :stability: experimental
        '''
        ...

    @jsii.member(jsii_name="processingStep")
    @abc.abstractmethod
    def _processing_step(
        self,
    ) -> typing.Union[_aws_cdk_aws_stepfunctions_tasks_ceddda9d.LambdaInvoke, _aws_cdk_aws_stepfunctions_tasks_ceddda9d.BedrockInvokeModel, _aws_cdk_aws_stepfunctions_tasks_ceddda9d.StepFunctionsStartExecution]:
        '''(experimental) Defines the document processing step of the workflow.

        **CRITICAL**: Must set ``outputPath`` to preserve workflow state for subsequent steps.
        The extraction result should be available at ``$.processingResult`` for DynamoDB storage.

        :return: Step Functions task for document extraction

        :stability: experimental
        '''
        ...

    @builtins.property
    @jsii.member(jsii_name="documentProcessingTable")
    def document_processing_table(self) -> _aws_cdk_aws_dynamodb_ceddda9d.Table:
        '''(experimental) DynamoDB table for storing document processing metadata and workflow state.

        :stability: experimental
        '''
        return typing.cast(_aws_cdk_aws_dynamodb_ceddda9d.Table, jsii.get(self, "documentProcessingTable"))

    @builtins.property
    @jsii.member(jsii_name="encryptionKey")
    def encryption_key(self) -> _aws_cdk_aws_kms_ceddda9d.Key:
        '''(experimental) KMS key.

        :stability: experimental
        '''
        return typing.cast(_aws_cdk_aws_kms_ceddda9d.Key, jsii.get(self, "encryptionKey"))

    @builtins.property
    @jsii.member(jsii_name="ingressAdapter")
    def ingress_adapter(self) -> IAdapter:
        '''(experimental) Ingress adapter, responsible for triggering workflow.

        :stability: experimental
        '''
        return typing.cast(IAdapter, jsii.get(self, "ingressAdapter"))

    @builtins.property
    @jsii.member(jsii_name="logGroupDataProtection")
    def log_group_data_protection(self) -> LogGroupDataProtectionProps:
        '''(experimental) log group data protection configuration.

        :stability: experimental
        '''
        return typing.cast(LogGroupDataProtectionProps, jsii.get(self, "logGroupDataProtection"))

    @builtins.property
    @jsii.member(jsii_name="metricNamespace")
    def metric_namespace(self) -> builtins.str:
        '''(experimental) Business metric namespace.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "metricNamespace"))

    @builtins.property
    @jsii.member(jsii_name="metricServiceName")
    def metric_service_name(self) -> builtins.str:
        '''(experimental) Business metric service name.

        This is part of the initial service dimension

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "metricServiceName"))


class _BaseDocumentProcessingProxy(BaseDocumentProcessing):
    @jsii.member(jsii_name="classificationStep")
    def _classification_step(
        self,
    ) -> typing.Union[_aws_cdk_aws_stepfunctions_tasks_ceddda9d.LambdaInvoke, _aws_cdk_aws_stepfunctions_tasks_ceddda9d.BedrockInvokeModel, _aws_cdk_aws_stepfunctions_tasks_ceddda9d.StepFunctionsStartExecution]:
        '''(experimental) Defines the document classification step of the workflow.

        **CRITICAL**: Must set ``outputPath`` to preserve workflow state for subsequent steps.
        The classification result should be available at ``$.classificationResult`` for DynamoDB storage.

        :return: Step Functions task for document classification

        :stability: experimental
        '''
        return typing.cast(typing.Union[_aws_cdk_aws_stepfunctions_tasks_ceddda9d.LambdaInvoke, _aws_cdk_aws_stepfunctions_tasks_ceddda9d.BedrockInvokeModel, _aws_cdk_aws_stepfunctions_tasks_ceddda9d.StepFunctionsStartExecution], jsii.invoke(self, "classificationStep", []))

    @jsii.member(jsii_name="enrichmentStep")
    def _enrichment_step(
        self,
    ) -> typing.Optional[typing.Union[_aws_cdk_aws_stepfunctions_tasks_ceddda9d.LambdaInvoke, _aws_cdk_aws_stepfunctions_tasks_ceddda9d.BedrockInvokeModel, _aws_cdk_aws_stepfunctions_tasks_ceddda9d.StepFunctionsStartExecution]]:
        '''(experimental) Defines the optional document enrichment step of the workflow.

        **CRITICAL**: If implemented, must set ``outputPath`` to preserve workflow state.
        The enrichment result should be available at ``$.enrichedResult`` for DynamoDB storage.

        :return: Step Functions task for document enrichment, or undefined to skip this step

        :stability: experimental
        '''
        return typing.cast(typing.Optional[typing.Union[_aws_cdk_aws_stepfunctions_tasks_ceddda9d.LambdaInvoke, _aws_cdk_aws_stepfunctions_tasks_ceddda9d.BedrockInvokeModel, _aws_cdk_aws_stepfunctions_tasks_ceddda9d.StepFunctionsStartExecution]], jsii.invoke(self, "enrichmentStep", []))

    @jsii.member(jsii_name="postProcessingStep")
    def _post_processing_step(
        self,
    ) -> typing.Optional[typing.Union[_aws_cdk_aws_stepfunctions_tasks_ceddda9d.LambdaInvoke, _aws_cdk_aws_stepfunctions_tasks_ceddda9d.BedrockInvokeModel, _aws_cdk_aws_stepfunctions_tasks_ceddda9d.StepFunctionsStartExecution]]:
        '''(experimental) Defines the optional post-processing step of the workflow.

        **CRITICAL**: If implemented, must set ``outputPath`` to preserve workflow state.
        The post-processing result should be available at ``$.postProcessedResult`` for DynamoDB storage.

        :return: Step Functions task for post-processing, or undefined to skip this step

        :stability: experimental
        '''
        return typing.cast(typing.Optional[typing.Union[_aws_cdk_aws_stepfunctions_tasks_ceddda9d.LambdaInvoke, _aws_cdk_aws_stepfunctions_tasks_ceddda9d.BedrockInvokeModel, _aws_cdk_aws_stepfunctions_tasks_ceddda9d.StepFunctionsStartExecution]], jsii.invoke(self, "postProcessingStep", []))

    @jsii.member(jsii_name="processingStep")
    def _processing_step(
        self,
    ) -> typing.Union[_aws_cdk_aws_stepfunctions_tasks_ceddda9d.LambdaInvoke, _aws_cdk_aws_stepfunctions_tasks_ceddda9d.BedrockInvokeModel, _aws_cdk_aws_stepfunctions_tasks_ceddda9d.StepFunctionsStartExecution]:
        '''(experimental) Defines the document processing step of the workflow.

        **CRITICAL**: Must set ``outputPath`` to preserve workflow state for subsequent steps.
        The extraction result should be available at ``$.processingResult`` for DynamoDB storage.

        :return: Step Functions task for document extraction

        :stability: experimental
        '''
        return typing.cast(typing.Union[_aws_cdk_aws_stepfunctions_tasks_ceddda9d.LambdaInvoke, _aws_cdk_aws_stepfunctions_tasks_ceddda9d.BedrockInvokeModel, _aws_cdk_aws_stepfunctions_tasks_ceddda9d.StepFunctionsStartExecution], jsii.invoke(self, "processingStep", []))

# Adding a "__jsii_proxy_class__(): typing.Type" function to the abstract class
typing.cast(typing.Any, BaseDocumentProcessing).__jsii_proxy_class__ = lambda : _BaseDocumentProcessingProxy


@jsii.data_type(
    jsii_type="@cdklabs/cdk-appmod-catalog-blueprints.BaseDocumentProcessingProps",
    jsii_struct_bases=[ObservableProps],
    name_mapping={
        "log_group_data_protection": "logGroupDataProtection",
        "metric_namespace": "metricNamespace",
        "metric_service_name": "metricServiceName",
        "document_processing_table": "documentProcessingTable",
        "enable_observability": "enableObservability",
        "encryption_key": "encryptionKey",
        "eventbridge_broker": "eventbridgeBroker",
        "ingress_adapter": "ingressAdapter",
        "network": "network",
        "removal_policy": "removalPolicy",
        "workflow_timeout": "workflowTimeout",
    },
)
class BaseDocumentProcessingProps(ObservableProps):
    def __init__(
        self,
        *,
        log_group_data_protection: typing.Optional[typing.Union[LogGroupDataProtectionProps, typing.Dict[builtins.str, typing.Any]]] = None,
        metric_namespace: typing.Optional[builtins.str] = None,
        metric_service_name: typing.Optional[builtins.str] = None,
        document_processing_table: typing.Optional[_aws_cdk_aws_dynamodb_ceddda9d.Table] = None,
        enable_observability: typing.Optional[builtins.bool] = None,
        encryption_key: typing.Optional[_aws_cdk_aws_kms_ceddda9d.Key] = None,
        eventbridge_broker: typing.Optional[EventbridgeBroker] = None,
        ingress_adapter: typing.Optional[IAdapter] = None,
        network: typing.Optional[Network] = None,
        removal_policy: typing.Optional[_aws_cdk_ceddda9d.RemovalPolicy] = None,
        workflow_timeout: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
    ) -> None:
        '''(experimental) Configuration properties for BaseDocumentProcessing construct.

        :param log_group_data_protection: (experimental) Data protection related configuration. Default: a new KMS key would be generated
        :param metric_namespace: (experimental) Business metric namespace. Default: would be defined per use case
        :param metric_service_name: (experimental) Business metric service name dimension. Default: would be defined per use case
        :param document_processing_table: (experimental) DynamoDB table for storing document processing metadata and workflow state. If not provided, a new table will be created with DocumentId as partition key.
        :param enable_observability: (experimental) Enable logging and tracing for all supporting resource. Default: false
        :param encryption_key: (experimental) KMS key to be used. Default: A new key would be created
        :param eventbridge_broker: (experimental) Optional EventBridge broker for publishing custom events during processing. If not provided, no custom events will be sent out.
        :param ingress_adapter: (experimental) Adapter that defines how the document processing workflow is triggered. Default: QueuedS3Adapter
        :param network: (experimental) Resources that can run inside a VPC will follow the provided network configuration. Default: resources will run outside of a VPC
        :param removal_policy: (experimental) Removal policy for created resources (bucket, table, queue). Default: RemovalPolicy.DESTROY
        :param workflow_timeout: (experimental) Maximum execution time for the Step Functions workflow. Default: Duration.minutes(30)

        :stability: experimental
        '''
        if isinstance(log_group_data_protection, dict):
            log_group_data_protection = LogGroupDataProtectionProps(**log_group_data_protection)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__75e07bce24d48571be58cad69f751b10a17a738fdb9db601acdc689ff1e6da22)
            check_type(argname="argument log_group_data_protection", value=log_group_data_protection, expected_type=type_hints["log_group_data_protection"])
            check_type(argname="argument metric_namespace", value=metric_namespace, expected_type=type_hints["metric_namespace"])
            check_type(argname="argument metric_service_name", value=metric_service_name, expected_type=type_hints["metric_service_name"])
            check_type(argname="argument document_processing_table", value=document_processing_table, expected_type=type_hints["document_processing_table"])
            check_type(argname="argument enable_observability", value=enable_observability, expected_type=type_hints["enable_observability"])
            check_type(argname="argument encryption_key", value=encryption_key, expected_type=type_hints["encryption_key"])
            check_type(argname="argument eventbridge_broker", value=eventbridge_broker, expected_type=type_hints["eventbridge_broker"])
            check_type(argname="argument ingress_adapter", value=ingress_adapter, expected_type=type_hints["ingress_adapter"])
            check_type(argname="argument network", value=network, expected_type=type_hints["network"])
            check_type(argname="argument removal_policy", value=removal_policy, expected_type=type_hints["removal_policy"])
            check_type(argname="argument workflow_timeout", value=workflow_timeout, expected_type=type_hints["workflow_timeout"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if log_group_data_protection is not None:
            self._values["log_group_data_protection"] = log_group_data_protection
        if metric_namespace is not None:
            self._values["metric_namespace"] = metric_namespace
        if metric_service_name is not None:
            self._values["metric_service_name"] = metric_service_name
        if document_processing_table is not None:
            self._values["document_processing_table"] = document_processing_table
        if enable_observability is not None:
            self._values["enable_observability"] = enable_observability
        if encryption_key is not None:
            self._values["encryption_key"] = encryption_key
        if eventbridge_broker is not None:
            self._values["eventbridge_broker"] = eventbridge_broker
        if ingress_adapter is not None:
            self._values["ingress_adapter"] = ingress_adapter
        if network is not None:
            self._values["network"] = network
        if removal_policy is not None:
            self._values["removal_policy"] = removal_policy
        if workflow_timeout is not None:
            self._values["workflow_timeout"] = workflow_timeout

    @builtins.property
    def log_group_data_protection(self) -> typing.Optional[LogGroupDataProtectionProps]:
        '''(experimental) Data protection related configuration.

        :default: a new KMS key would be generated

        :stability: experimental
        '''
        result = self._values.get("log_group_data_protection")
        return typing.cast(typing.Optional[LogGroupDataProtectionProps], result)

    @builtins.property
    def metric_namespace(self) -> typing.Optional[builtins.str]:
        '''(experimental) Business metric namespace.

        :default: would be defined per use case

        :stability: experimental
        '''
        result = self._values.get("metric_namespace")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def metric_service_name(self) -> typing.Optional[builtins.str]:
        '''(experimental) Business metric service name dimension.

        :default: would be defined per use case

        :stability: experimental
        '''
        result = self._values.get("metric_service_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def document_processing_table(
        self,
    ) -> typing.Optional[_aws_cdk_aws_dynamodb_ceddda9d.Table]:
        '''(experimental) DynamoDB table for storing document processing metadata and workflow state.

        If not provided, a new table will be created with DocumentId as partition key.

        :stability: experimental
        '''
        result = self._values.get("document_processing_table")
        return typing.cast(typing.Optional[_aws_cdk_aws_dynamodb_ceddda9d.Table], result)

    @builtins.property
    def enable_observability(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Enable logging and tracing for all supporting resource.

        :default: false

        :stability: experimental
        '''
        result = self._values.get("enable_observability")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def encryption_key(self) -> typing.Optional[_aws_cdk_aws_kms_ceddda9d.Key]:
        '''(experimental) KMS key to be used.

        :default: A new key would be created

        :stability: experimental
        '''
        result = self._values.get("encryption_key")
        return typing.cast(typing.Optional[_aws_cdk_aws_kms_ceddda9d.Key], result)

    @builtins.property
    def eventbridge_broker(self) -> typing.Optional[EventbridgeBroker]:
        '''(experimental) Optional EventBridge broker for publishing custom events during processing.

        If not provided, no custom events will be sent out.

        :stability: experimental
        '''
        result = self._values.get("eventbridge_broker")
        return typing.cast(typing.Optional[EventbridgeBroker], result)

    @builtins.property
    def ingress_adapter(self) -> typing.Optional[IAdapter]:
        '''(experimental) Adapter that defines how the document processing workflow is triggered.

        :default: QueuedS3Adapter

        :stability: experimental
        '''
        result = self._values.get("ingress_adapter")
        return typing.cast(typing.Optional[IAdapter], result)

    @builtins.property
    def network(self) -> typing.Optional[Network]:
        '''(experimental) Resources that can run inside a VPC will follow the provided network configuration.

        :default: resources will run outside of a VPC

        :stability: experimental
        '''
        result = self._values.get("network")
        return typing.cast(typing.Optional[Network], result)

    @builtins.property
    def removal_policy(self) -> typing.Optional[_aws_cdk_ceddda9d.RemovalPolicy]:
        '''(experimental) Removal policy for created resources (bucket, table, queue).

        :default: RemovalPolicy.DESTROY

        :stability: experimental
        '''
        result = self._values.get("removal_policy")
        return typing.cast(typing.Optional[_aws_cdk_ceddda9d.RemovalPolicy], result)

    @builtins.property
    def workflow_timeout(self) -> typing.Optional[_aws_cdk_ceddda9d.Duration]:
        '''(experimental) Maximum execution time for the Step Functions workflow.

        :default: Duration.minutes(30)

        :stability: experimental
        '''
        result = self._values.get("workflow_timeout")
        return typing.cast(typing.Optional[_aws_cdk_ceddda9d.Duration], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "BaseDocumentProcessingProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class BedrockDocumentProcessing(
    BaseDocumentProcessing,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdklabs/cdk-appmod-catalog-blueprints.BedrockDocumentProcessing",
):
    '''(experimental) Document processing workflow powered by Amazon Bedrock foundation models.

    Extends BaseDocumentProcessing to provide AI-powered document classification and extraction
    using Amazon Bedrock foundation models. This implementation offers:


    Key Features

    - **AI-Powered Classification**: Uses Claude 3.7 Sonnet (configurable) to classify document types
    - **Intelligent Extraction**: Extracts structured data from documents using foundation models
    - **Cross-Region Inference**: Optional support for improved availability via inference profiles
    - **Flexible Processing**: Optional enrichment and post-processing Lambda functions
    - **Cost Optimized**: Configurable timeouts and model selection for cost control



    Processing Workflow

    S3 Upload → Classification (Bedrock) → Extraction (Bedrock) → [Enrichment] → [Post-Processing] → Results


    Default Models

    - Classification: Claude 3.7 Sonnet (anthropic.claude-3-7-sonnet-20250219-v1:0)
    - Extraction: Claude 3.7 Sonnet (anthropic.claude-3-7-sonnet-20250219-v1:0)



    Prompt Templates

    The construct uses default prompts that can be customized:

    - **Classification**: Analyzes document and returns JSON with documentClassification field
    - **Extraction**: Uses classification result to extract entities in structured JSON format



    Cross-Region Inference

    When enabled, uses Bedrock inference profiles for improved availability:

    - US prefix: Routes to US-based regions for lower latency
    - EU prefix: Routes to EU-based regions for data residency compliance

    :stability: experimental
    '''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        classification_model_id: typing.Optional[_aws_cdk_aws_bedrock_ceddda9d.FoundationModelIdentifier] = None,
        classification_prompt: typing.Optional[builtins.str] = None,
        cross_region_inference_prefix: typing.Optional[BedrockCrossRegionInferencePrefix] = None,
        enrichment_lambda_function: typing.Optional[_aws_cdk_aws_lambda_ceddda9d.Function] = None,
        post_processing_lambda_function: typing.Optional[_aws_cdk_aws_lambda_ceddda9d.Function] = None,
        processing_model_id: typing.Optional[_aws_cdk_aws_bedrock_ceddda9d.FoundationModelIdentifier] = None,
        processing_prompt: typing.Optional[builtins.str] = None,
        step_timeouts: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
        use_cross_region_inference: typing.Optional[builtins.bool] = None,
        document_processing_table: typing.Optional[_aws_cdk_aws_dynamodb_ceddda9d.Table] = None,
        enable_observability: typing.Optional[builtins.bool] = None,
        encryption_key: typing.Optional[_aws_cdk_aws_kms_ceddda9d.Key] = None,
        eventbridge_broker: typing.Optional[EventbridgeBroker] = None,
        ingress_adapter: typing.Optional[IAdapter] = None,
        network: typing.Optional[Network] = None,
        removal_policy: typing.Optional[_aws_cdk_ceddda9d.RemovalPolicy] = None,
        workflow_timeout: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
        log_group_data_protection: typing.Optional[typing.Union[LogGroupDataProtectionProps, typing.Dict[builtins.str, typing.Any]]] = None,
        metric_namespace: typing.Optional[builtins.str] = None,
        metric_service_name: typing.Optional[builtins.str] = None,
    ) -> None:
        '''(experimental) Creates a new BedrockDocumentProcessing construct.

        Initializes the Bedrock-powered document processing pipeline with AI classification
        and extraction capabilities. Creates Lambda functions with appropriate IAM roles
        for Bedrock model invocation and S3 access.

        :param scope: - The scope in which to define this construct.
        :param id: - The scoped construct ID. Must be unique within the scope.
        :param classification_model_id: (experimental) Bedrock foundation model for document classification step. Default: FoundationModelIdentifier.ANTHROPIC_CLAUDE_3_7_SONNET_20250219_V1_0
        :param classification_prompt: (experimental) Custom prompt template for document classification. Must include placeholder for document content. Default: DEFAULT_CLASSIFICATION_PROMPT
        :param cross_region_inference_prefix: (experimental) Prefix for cross-region inference configuration. Only used when useCrossRegionInference is true. Default: BedrockCrossRegionInferencePrefix.US
        :param enrichment_lambda_function: (experimental) Optional Lambda function for document enrichment step. If provided, will be invoked after extraction with workflow state.
        :param post_processing_lambda_function: (experimental) Optional Lambda function for post-processing step. If provided, will be invoked after enrichment with workflow state.
        :param processing_model_id: (experimental) Bedrock foundation model for document extraction step. Default: FoundationModelIdentifier.ANTHROPIC_CLAUDE_3_7_SONNET_20250219_V1_0
        :param processing_prompt: (experimental) Custom prompt template for document extraction. Must include placeholder for document content and classification result. Default: DEFAULT_EXTRACTION_PROMPT
        :param step_timeouts: (experimental) Timeout for individual Step Functions tasks (classification, extraction, etc.). Default: Duration.minutes(5)
        :param use_cross_region_inference: (experimental) Enable cross-region inference for Bedrock models to improve availability and performance. When enabled, uses inference profiles instead of direct model invocation. Default: false
        :param document_processing_table: (experimental) DynamoDB table for storing document processing metadata and workflow state. If not provided, a new table will be created with DocumentId as partition key.
        :param enable_observability: (experimental) Enable logging and tracing for all supporting resource. Default: false
        :param encryption_key: (experimental) KMS key to be used. Default: A new key would be created
        :param eventbridge_broker: (experimental) Optional EventBridge broker for publishing custom events during processing. If not provided, no custom events will be sent out.
        :param ingress_adapter: (experimental) Adapter that defines how the document processing workflow is triggered. Default: QueuedS3Adapter
        :param network: (experimental) Resources that can run inside a VPC will follow the provided network configuration. Default: resources will run outside of a VPC
        :param removal_policy: (experimental) Removal policy for created resources (bucket, table, queue). Default: RemovalPolicy.DESTROY
        :param workflow_timeout: (experimental) Maximum execution time for the Step Functions workflow. Default: Duration.minutes(30)
        :param log_group_data_protection: (experimental) Data protection related configuration. Default: a new KMS key would be generated
        :param metric_namespace: (experimental) Business metric namespace. Default: would be defined per use case
        :param metric_service_name: (experimental) Business metric service name dimension. Default: would be defined per use case

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7393f9c6b2af93f7d8668b32cec54ba8c77259644ab01f57b3fbd50c78923134)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = BedrockDocumentProcessingProps(
            classification_model_id=classification_model_id,
            classification_prompt=classification_prompt,
            cross_region_inference_prefix=cross_region_inference_prefix,
            enrichment_lambda_function=enrichment_lambda_function,
            post_processing_lambda_function=post_processing_lambda_function,
            processing_model_id=processing_model_id,
            processing_prompt=processing_prompt,
            step_timeouts=step_timeouts,
            use_cross_region_inference=use_cross_region_inference,
            document_processing_table=document_processing_table,
            enable_observability=enable_observability,
            encryption_key=encryption_key,
            eventbridge_broker=eventbridge_broker,
            ingress_adapter=ingress_adapter,
            network=network,
            removal_policy=removal_policy,
            workflow_timeout=workflow_timeout,
            log_group_data_protection=log_group_data_protection,
            metric_namespace=metric_namespace,
            metric_service_name=metric_service_name,
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @jsii.member(jsii_name="classificationStep")
    def _classification_step(
        self,
    ) -> typing.Union[_aws_cdk_aws_stepfunctions_tasks_ceddda9d.LambdaInvoke, _aws_cdk_aws_stepfunctions_tasks_ceddda9d.BedrockInvokeModel, _aws_cdk_aws_stepfunctions_tasks_ceddda9d.StepFunctionsStartExecution]:
        '''(experimental) Implements the document classification step using Amazon Bedrock.

        Creates a Lambda function that invokes the configured Bedrock model to classify
        the document type. The function reads the document from S3 and sends it to
        Bedrock with the classification prompt.

        :return: LambdaInvoke task configured for document classification

        :stability: experimental
        '''
        return typing.cast(typing.Union[_aws_cdk_aws_stepfunctions_tasks_ceddda9d.LambdaInvoke, _aws_cdk_aws_stepfunctions_tasks_ceddda9d.BedrockInvokeModel, _aws_cdk_aws_stepfunctions_tasks_ceddda9d.StepFunctionsStartExecution], jsii.invoke(self, "classificationStep", []))

    @jsii.member(jsii_name="enrichmentStep")
    def _enrichment_step(
        self,
    ) -> typing.Optional[typing.Union[_aws_cdk_aws_stepfunctions_tasks_ceddda9d.LambdaInvoke, _aws_cdk_aws_stepfunctions_tasks_ceddda9d.BedrockInvokeModel, _aws_cdk_aws_stepfunctions_tasks_ceddda9d.StepFunctionsStartExecution]]:
        '''(experimental) Implements the optional document enrichment step.

        If an enrichment Lambda function is provided in the props, creates a LambdaInvoke
        task to perform additional processing on the extracted data. This step is useful
        for data validation, transformation, or integration with external systems.

        :return: LambdaInvoke task for enrichment, or undefined to skip this step

        :stability: experimental
        '''
        return typing.cast(typing.Optional[typing.Union[_aws_cdk_aws_stepfunctions_tasks_ceddda9d.LambdaInvoke, _aws_cdk_aws_stepfunctions_tasks_ceddda9d.BedrockInvokeModel, _aws_cdk_aws_stepfunctions_tasks_ceddda9d.StepFunctionsStartExecution]], jsii.invoke(self, "enrichmentStep", []))

    @jsii.member(jsii_name="generateLambdaRoleForBedrock")
    def _generate_lambda_role_for_bedrock(
        self,
        fm_model: _aws_cdk_aws_bedrock_ceddda9d.FoundationModelIdentifier,
        id: builtins.str,
    ) -> _aws_cdk_aws_iam_ceddda9d.Role:
        '''
        :param fm_model: -
        :param id: -

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b765dc24cd888585470934e534f4d8e979ddebd46e42601cc8b50c73499e7d4e)
            check_type(argname="argument fm_model", value=fm_model, expected_type=type_hints["fm_model"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        return typing.cast(_aws_cdk_aws_iam_ceddda9d.Role, jsii.invoke(self, "generateLambdaRoleForBedrock", [fm_model, id]))

    @jsii.member(jsii_name="postProcessingStep")
    def _post_processing_step(
        self,
    ) -> typing.Optional[typing.Union[_aws_cdk_aws_stepfunctions_tasks_ceddda9d.LambdaInvoke, _aws_cdk_aws_stepfunctions_tasks_ceddda9d.BedrockInvokeModel, _aws_cdk_aws_stepfunctions_tasks_ceddda9d.StepFunctionsStartExecution]]:
        '''(experimental) Implements the optional post-processing step.

        If a post-processing Lambda function is provided in the props, creates a LambdaInvoke
        task to perform final processing on the workflow results. This step is useful for
        data formatting, notifications, or integration with downstream systems.

        :return: LambdaInvoke task for post-processing, or undefined to skip this step

        :stability: experimental
        '''
        return typing.cast(typing.Optional[typing.Union[_aws_cdk_aws_stepfunctions_tasks_ceddda9d.LambdaInvoke, _aws_cdk_aws_stepfunctions_tasks_ceddda9d.BedrockInvokeModel, _aws_cdk_aws_stepfunctions_tasks_ceddda9d.StepFunctionsStartExecution]], jsii.invoke(self, "postProcessingStep", []))

    @jsii.member(jsii_name="processingStep")
    def _processing_step(
        self,
    ) -> typing.Union[_aws_cdk_aws_stepfunctions_tasks_ceddda9d.LambdaInvoke, _aws_cdk_aws_stepfunctions_tasks_ceddda9d.BedrockInvokeModel, _aws_cdk_aws_stepfunctions_tasks_ceddda9d.StepFunctionsStartExecution]:
        '''(experimental) Implements the document extraction step using Amazon Bedrock.

        Creates a Lambda function that invokes the configured Bedrock model to extract
        structured data from the document. Uses the classification result from the
        previous step to provide context for more accurate extraction.

        :return: LambdaInvoke task configured for document extraction

        :stability: experimental
        '''
        return typing.cast(typing.Union[_aws_cdk_aws_stepfunctions_tasks_ceddda9d.LambdaInvoke, _aws_cdk_aws_stepfunctions_tasks_ceddda9d.BedrockInvokeModel, _aws_cdk_aws_stepfunctions_tasks_ceddda9d.StepFunctionsStartExecution], jsii.invoke(self, "processingStep", []))

    @jsii.python.classproperty
    @jsii.member(jsii_name="DEFAULT_CLASSIFICATION_MODEL_ID")
    def DEFAULT_CLASSIFICATION_MODEL_ID(
        cls,
    ) -> _aws_cdk_aws_bedrock_ceddda9d.FoundationModelIdentifier:
        '''
        :stability: experimental
        '''
        return typing.cast(_aws_cdk_aws_bedrock_ceddda9d.FoundationModelIdentifier, jsii.sget(cls, "DEFAULT_CLASSIFICATION_MODEL_ID"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="DEFAULT_CLASSIFICATION_PROMPT")
    def DEFAULT_CLASSIFICATION_PROMPT(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "DEFAULT_CLASSIFICATION_PROMPT"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="DEFAULT_PROCESSING_MODEL_ID")
    def DEFAULT_PROCESSING_MODEL_ID(
        cls,
    ) -> _aws_cdk_aws_bedrock_ceddda9d.FoundationModelIdentifier:
        '''
        :stability: experimental
        '''
        return typing.cast(_aws_cdk_aws_bedrock_ceddda9d.FoundationModelIdentifier, jsii.sget(cls, "DEFAULT_PROCESSING_MODEL_ID"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="DEFAULT_PROCESSING_PROMPT")
    def DEFAULT_PROCESSING_PROMPT(cls) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "DEFAULT_PROCESSING_PROMPT"))

    @builtins.property
    @jsii.member(jsii_name="bedrockDocumentProcessingProps")
    def _bedrock_document_processing_props(self) -> "BedrockDocumentProcessingProps":
        '''(experimental) Configuration properties specific to Bedrock document processing.

        :stability: experimental
        '''
        return typing.cast("BedrockDocumentProcessingProps", jsii.get(self, "bedrockDocumentProcessingProps"))

    @builtins.property
    @jsii.member(jsii_name="crossRegionInferencePrefix")
    def _cross_region_inference_prefix(self) -> BedrockCrossRegionInferencePrefix:
        '''(experimental) Cross-region inference prefix for Bedrock model routing.

        :stability: experimental
        '''
        return typing.cast(BedrockCrossRegionInferencePrefix, jsii.get(self, "crossRegionInferencePrefix"))

    @builtins.property
    @jsii.member(jsii_name="stateMachine")
    def state_machine(self) -> _aws_cdk_aws_stepfunctions_ceddda9d.StateMachine:
        '''(experimental) The Step Functions state machine that orchestrates the document processing workflow.

        :stability: experimental
        '''
        return typing.cast(_aws_cdk_aws_stepfunctions_ceddda9d.StateMachine, jsii.get(self, "stateMachine"))


@jsii.data_type(
    jsii_type="@cdklabs/cdk-appmod-catalog-blueprints.BedrockDocumentProcessingProps",
    jsii_struct_bases=[BaseDocumentProcessingProps],
    name_mapping={
        "log_group_data_protection": "logGroupDataProtection",
        "metric_namespace": "metricNamespace",
        "metric_service_name": "metricServiceName",
        "document_processing_table": "documentProcessingTable",
        "enable_observability": "enableObservability",
        "encryption_key": "encryptionKey",
        "eventbridge_broker": "eventbridgeBroker",
        "ingress_adapter": "ingressAdapter",
        "network": "network",
        "removal_policy": "removalPolicy",
        "workflow_timeout": "workflowTimeout",
        "classification_model_id": "classificationModelId",
        "classification_prompt": "classificationPrompt",
        "cross_region_inference_prefix": "crossRegionInferencePrefix",
        "enrichment_lambda_function": "enrichmentLambdaFunction",
        "post_processing_lambda_function": "postProcessingLambdaFunction",
        "processing_model_id": "processingModelId",
        "processing_prompt": "processingPrompt",
        "step_timeouts": "stepTimeouts",
        "use_cross_region_inference": "useCrossRegionInference",
    },
)
class BedrockDocumentProcessingProps(BaseDocumentProcessingProps):
    def __init__(
        self,
        *,
        log_group_data_protection: typing.Optional[typing.Union[LogGroupDataProtectionProps, typing.Dict[builtins.str, typing.Any]]] = None,
        metric_namespace: typing.Optional[builtins.str] = None,
        metric_service_name: typing.Optional[builtins.str] = None,
        document_processing_table: typing.Optional[_aws_cdk_aws_dynamodb_ceddda9d.Table] = None,
        enable_observability: typing.Optional[builtins.bool] = None,
        encryption_key: typing.Optional[_aws_cdk_aws_kms_ceddda9d.Key] = None,
        eventbridge_broker: typing.Optional[EventbridgeBroker] = None,
        ingress_adapter: typing.Optional[IAdapter] = None,
        network: typing.Optional[Network] = None,
        removal_policy: typing.Optional[_aws_cdk_ceddda9d.RemovalPolicy] = None,
        workflow_timeout: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
        classification_model_id: typing.Optional[_aws_cdk_aws_bedrock_ceddda9d.FoundationModelIdentifier] = None,
        classification_prompt: typing.Optional[builtins.str] = None,
        cross_region_inference_prefix: typing.Optional[BedrockCrossRegionInferencePrefix] = None,
        enrichment_lambda_function: typing.Optional[_aws_cdk_aws_lambda_ceddda9d.Function] = None,
        post_processing_lambda_function: typing.Optional[_aws_cdk_aws_lambda_ceddda9d.Function] = None,
        processing_model_id: typing.Optional[_aws_cdk_aws_bedrock_ceddda9d.FoundationModelIdentifier] = None,
        processing_prompt: typing.Optional[builtins.str] = None,
        step_timeouts: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
        use_cross_region_inference: typing.Optional[builtins.bool] = None,
    ) -> None:
        '''(experimental) Configuration properties for BedrockDocumentProcessing construct.

        Extends BaseDocumentProcessingProps with Bedrock-specific options.

        :param log_group_data_protection: (experimental) Data protection related configuration. Default: a new KMS key would be generated
        :param metric_namespace: (experimental) Business metric namespace. Default: would be defined per use case
        :param metric_service_name: (experimental) Business metric service name dimension. Default: would be defined per use case
        :param document_processing_table: (experimental) DynamoDB table for storing document processing metadata and workflow state. If not provided, a new table will be created with DocumentId as partition key.
        :param enable_observability: (experimental) Enable logging and tracing for all supporting resource. Default: false
        :param encryption_key: (experimental) KMS key to be used. Default: A new key would be created
        :param eventbridge_broker: (experimental) Optional EventBridge broker for publishing custom events during processing. If not provided, no custom events will be sent out.
        :param ingress_adapter: (experimental) Adapter that defines how the document processing workflow is triggered. Default: QueuedS3Adapter
        :param network: (experimental) Resources that can run inside a VPC will follow the provided network configuration. Default: resources will run outside of a VPC
        :param removal_policy: (experimental) Removal policy for created resources (bucket, table, queue). Default: RemovalPolicy.DESTROY
        :param workflow_timeout: (experimental) Maximum execution time for the Step Functions workflow. Default: Duration.minutes(30)
        :param classification_model_id: (experimental) Bedrock foundation model for document classification step. Default: FoundationModelIdentifier.ANTHROPIC_CLAUDE_3_7_SONNET_20250219_V1_0
        :param classification_prompt: (experimental) Custom prompt template for document classification. Must include placeholder for document content. Default: DEFAULT_CLASSIFICATION_PROMPT
        :param cross_region_inference_prefix: (experimental) Prefix for cross-region inference configuration. Only used when useCrossRegionInference is true. Default: BedrockCrossRegionInferencePrefix.US
        :param enrichment_lambda_function: (experimental) Optional Lambda function for document enrichment step. If provided, will be invoked after extraction with workflow state.
        :param post_processing_lambda_function: (experimental) Optional Lambda function for post-processing step. If provided, will be invoked after enrichment with workflow state.
        :param processing_model_id: (experimental) Bedrock foundation model for document extraction step. Default: FoundationModelIdentifier.ANTHROPIC_CLAUDE_3_7_SONNET_20250219_V1_0
        :param processing_prompt: (experimental) Custom prompt template for document extraction. Must include placeholder for document content and classification result. Default: DEFAULT_EXTRACTION_PROMPT
        :param step_timeouts: (experimental) Timeout for individual Step Functions tasks (classification, extraction, etc.). Default: Duration.minutes(5)
        :param use_cross_region_inference: (experimental) Enable cross-region inference for Bedrock models to improve availability and performance. When enabled, uses inference profiles instead of direct model invocation. Default: false

        :stability: experimental
        '''
        if isinstance(log_group_data_protection, dict):
            log_group_data_protection = LogGroupDataProtectionProps(**log_group_data_protection)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9606a6418d69bde20176ec33b27eaa22c0e0cdb6b105d382e9d038566f7a29f3)
            check_type(argname="argument log_group_data_protection", value=log_group_data_protection, expected_type=type_hints["log_group_data_protection"])
            check_type(argname="argument metric_namespace", value=metric_namespace, expected_type=type_hints["metric_namespace"])
            check_type(argname="argument metric_service_name", value=metric_service_name, expected_type=type_hints["metric_service_name"])
            check_type(argname="argument document_processing_table", value=document_processing_table, expected_type=type_hints["document_processing_table"])
            check_type(argname="argument enable_observability", value=enable_observability, expected_type=type_hints["enable_observability"])
            check_type(argname="argument encryption_key", value=encryption_key, expected_type=type_hints["encryption_key"])
            check_type(argname="argument eventbridge_broker", value=eventbridge_broker, expected_type=type_hints["eventbridge_broker"])
            check_type(argname="argument ingress_adapter", value=ingress_adapter, expected_type=type_hints["ingress_adapter"])
            check_type(argname="argument network", value=network, expected_type=type_hints["network"])
            check_type(argname="argument removal_policy", value=removal_policy, expected_type=type_hints["removal_policy"])
            check_type(argname="argument workflow_timeout", value=workflow_timeout, expected_type=type_hints["workflow_timeout"])
            check_type(argname="argument classification_model_id", value=classification_model_id, expected_type=type_hints["classification_model_id"])
            check_type(argname="argument classification_prompt", value=classification_prompt, expected_type=type_hints["classification_prompt"])
            check_type(argname="argument cross_region_inference_prefix", value=cross_region_inference_prefix, expected_type=type_hints["cross_region_inference_prefix"])
            check_type(argname="argument enrichment_lambda_function", value=enrichment_lambda_function, expected_type=type_hints["enrichment_lambda_function"])
            check_type(argname="argument post_processing_lambda_function", value=post_processing_lambda_function, expected_type=type_hints["post_processing_lambda_function"])
            check_type(argname="argument processing_model_id", value=processing_model_id, expected_type=type_hints["processing_model_id"])
            check_type(argname="argument processing_prompt", value=processing_prompt, expected_type=type_hints["processing_prompt"])
            check_type(argname="argument step_timeouts", value=step_timeouts, expected_type=type_hints["step_timeouts"])
            check_type(argname="argument use_cross_region_inference", value=use_cross_region_inference, expected_type=type_hints["use_cross_region_inference"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if log_group_data_protection is not None:
            self._values["log_group_data_protection"] = log_group_data_protection
        if metric_namespace is not None:
            self._values["metric_namespace"] = metric_namespace
        if metric_service_name is not None:
            self._values["metric_service_name"] = metric_service_name
        if document_processing_table is not None:
            self._values["document_processing_table"] = document_processing_table
        if enable_observability is not None:
            self._values["enable_observability"] = enable_observability
        if encryption_key is not None:
            self._values["encryption_key"] = encryption_key
        if eventbridge_broker is not None:
            self._values["eventbridge_broker"] = eventbridge_broker
        if ingress_adapter is not None:
            self._values["ingress_adapter"] = ingress_adapter
        if network is not None:
            self._values["network"] = network
        if removal_policy is not None:
            self._values["removal_policy"] = removal_policy
        if workflow_timeout is not None:
            self._values["workflow_timeout"] = workflow_timeout
        if classification_model_id is not None:
            self._values["classification_model_id"] = classification_model_id
        if classification_prompt is not None:
            self._values["classification_prompt"] = classification_prompt
        if cross_region_inference_prefix is not None:
            self._values["cross_region_inference_prefix"] = cross_region_inference_prefix
        if enrichment_lambda_function is not None:
            self._values["enrichment_lambda_function"] = enrichment_lambda_function
        if post_processing_lambda_function is not None:
            self._values["post_processing_lambda_function"] = post_processing_lambda_function
        if processing_model_id is not None:
            self._values["processing_model_id"] = processing_model_id
        if processing_prompt is not None:
            self._values["processing_prompt"] = processing_prompt
        if step_timeouts is not None:
            self._values["step_timeouts"] = step_timeouts
        if use_cross_region_inference is not None:
            self._values["use_cross_region_inference"] = use_cross_region_inference

    @builtins.property
    def log_group_data_protection(self) -> typing.Optional[LogGroupDataProtectionProps]:
        '''(experimental) Data protection related configuration.

        :default: a new KMS key would be generated

        :stability: experimental
        '''
        result = self._values.get("log_group_data_protection")
        return typing.cast(typing.Optional[LogGroupDataProtectionProps], result)

    @builtins.property
    def metric_namespace(self) -> typing.Optional[builtins.str]:
        '''(experimental) Business metric namespace.

        :default: would be defined per use case

        :stability: experimental
        '''
        result = self._values.get("metric_namespace")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def metric_service_name(self) -> typing.Optional[builtins.str]:
        '''(experimental) Business metric service name dimension.

        :default: would be defined per use case

        :stability: experimental
        '''
        result = self._values.get("metric_service_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def document_processing_table(
        self,
    ) -> typing.Optional[_aws_cdk_aws_dynamodb_ceddda9d.Table]:
        '''(experimental) DynamoDB table for storing document processing metadata and workflow state.

        If not provided, a new table will be created with DocumentId as partition key.

        :stability: experimental
        '''
        result = self._values.get("document_processing_table")
        return typing.cast(typing.Optional[_aws_cdk_aws_dynamodb_ceddda9d.Table], result)

    @builtins.property
    def enable_observability(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Enable logging and tracing for all supporting resource.

        :default: false

        :stability: experimental
        '''
        result = self._values.get("enable_observability")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def encryption_key(self) -> typing.Optional[_aws_cdk_aws_kms_ceddda9d.Key]:
        '''(experimental) KMS key to be used.

        :default: A new key would be created

        :stability: experimental
        '''
        result = self._values.get("encryption_key")
        return typing.cast(typing.Optional[_aws_cdk_aws_kms_ceddda9d.Key], result)

    @builtins.property
    def eventbridge_broker(self) -> typing.Optional[EventbridgeBroker]:
        '''(experimental) Optional EventBridge broker for publishing custom events during processing.

        If not provided, no custom events will be sent out.

        :stability: experimental
        '''
        result = self._values.get("eventbridge_broker")
        return typing.cast(typing.Optional[EventbridgeBroker], result)

    @builtins.property
    def ingress_adapter(self) -> typing.Optional[IAdapter]:
        '''(experimental) Adapter that defines how the document processing workflow is triggered.

        :default: QueuedS3Adapter

        :stability: experimental
        '''
        result = self._values.get("ingress_adapter")
        return typing.cast(typing.Optional[IAdapter], result)

    @builtins.property
    def network(self) -> typing.Optional[Network]:
        '''(experimental) Resources that can run inside a VPC will follow the provided network configuration.

        :default: resources will run outside of a VPC

        :stability: experimental
        '''
        result = self._values.get("network")
        return typing.cast(typing.Optional[Network], result)

    @builtins.property
    def removal_policy(self) -> typing.Optional[_aws_cdk_ceddda9d.RemovalPolicy]:
        '''(experimental) Removal policy for created resources (bucket, table, queue).

        :default: RemovalPolicy.DESTROY

        :stability: experimental
        '''
        result = self._values.get("removal_policy")
        return typing.cast(typing.Optional[_aws_cdk_ceddda9d.RemovalPolicy], result)

    @builtins.property
    def workflow_timeout(self) -> typing.Optional[_aws_cdk_ceddda9d.Duration]:
        '''(experimental) Maximum execution time for the Step Functions workflow.

        :default: Duration.minutes(30)

        :stability: experimental
        '''
        result = self._values.get("workflow_timeout")
        return typing.cast(typing.Optional[_aws_cdk_ceddda9d.Duration], result)

    @builtins.property
    def classification_model_id(
        self,
    ) -> typing.Optional[_aws_cdk_aws_bedrock_ceddda9d.FoundationModelIdentifier]:
        '''(experimental) Bedrock foundation model for document classification step.

        :default: FoundationModelIdentifier.ANTHROPIC_CLAUDE_3_7_SONNET_20250219_V1_0

        :stability: experimental
        '''
        result = self._values.get("classification_model_id")
        return typing.cast(typing.Optional[_aws_cdk_aws_bedrock_ceddda9d.FoundationModelIdentifier], result)

    @builtins.property
    def classification_prompt(self) -> typing.Optional[builtins.str]:
        '''(experimental) Custom prompt template for document classification.

        Must include placeholder for document content.

        :default: DEFAULT_CLASSIFICATION_PROMPT

        :stability: experimental
        '''
        result = self._values.get("classification_prompt")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def cross_region_inference_prefix(
        self,
    ) -> typing.Optional[BedrockCrossRegionInferencePrefix]:
        '''(experimental) Prefix for cross-region inference configuration.

        Only used when useCrossRegionInference is true.

        :default: BedrockCrossRegionInferencePrefix.US

        :stability: experimental
        '''
        result = self._values.get("cross_region_inference_prefix")
        return typing.cast(typing.Optional[BedrockCrossRegionInferencePrefix], result)

    @builtins.property
    def enrichment_lambda_function(
        self,
    ) -> typing.Optional[_aws_cdk_aws_lambda_ceddda9d.Function]:
        '''(experimental) Optional Lambda function for document enrichment step.

        If provided, will be invoked after extraction with workflow state.

        :stability: experimental
        '''
        result = self._values.get("enrichment_lambda_function")
        return typing.cast(typing.Optional[_aws_cdk_aws_lambda_ceddda9d.Function], result)

    @builtins.property
    def post_processing_lambda_function(
        self,
    ) -> typing.Optional[_aws_cdk_aws_lambda_ceddda9d.Function]:
        '''(experimental) Optional Lambda function for post-processing step.

        If provided, will be invoked after enrichment with workflow state.

        :stability: experimental
        '''
        result = self._values.get("post_processing_lambda_function")
        return typing.cast(typing.Optional[_aws_cdk_aws_lambda_ceddda9d.Function], result)

    @builtins.property
    def processing_model_id(
        self,
    ) -> typing.Optional[_aws_cdk_aws_bedrock_ceddda9d.FoundationModelIdentifier]:
        '''(experimental) Bedrock foundation model for document extraction step.

        :default: FoundationModelIdentifier.ANTHROPIC_CLAUDE_3_7_SONNET_20250219_V1_0

        :stability: experimental
        '''
        result = self._values.get("processing_model_id")
        return typing.cast(typing.Optional[_aws_cdk_aws_bedrock_ceddda9d.FoundationModelIdentifier], result)

    @builtins.property
    def processing_prompt(self) -> typing.Optional[builtins.str]:
        '''(experimental) Custom prompt template for document extraction.

        Must include placeholder for document content and classification result.

        :default: DEFAULT_EXTRACTION_PROMPT

        :stability: experimental
        '''
        result = self._values.get("processing_prompt")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def step_timeouts(self) -> typing.Optional[_aws_cdk_ceddda9d.Duration]:
        '''(experimental) Timeout for individual Step Functions tasks (classification, extraction, etc.).

        :default: Duration.minutes(5)

        :stability: experimental
        '''
        result = self._values.get("step_timeouts")
        return typing.cast(typing.Optional[_aws_cdk_ceddda9d.Duration], result)

    @builtins.property
    def use_cross_region_inference(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Enable cross-region inference for Bedrock models to improve availability and performance.

        When enabled, uses inference profiles instead of direct model invocation.

        :default: false

        :stability: experimental
        '''
        result = self._values.get("use_cross_region_inference")
        return typing.cast(typing.Optional[builtins.bool], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "BedrockDocumentProcessingProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class AgenticDocumentProcessing(
    BedrockDocumentProcessing,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdklabs/cdk-appmod-catalog-blueprints.AgenticDocumentProcessing",
):
    '''
    :stability: experimental
    '''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        processing_agent_parameters: typing.Optional[typing.Union[AgentProps, typing.Dict[builtins.str, typing.Any]]] = None,
        classification_model_id: typing.Optional[_aws_cdk_aws_bedrock_ceddda9d.FoundationModelIdentifier] = None,
        classification_prompt: typing.Optional[builtins.str] = None,
        cross_region_inference_prefix: typing.Optional[BedrockCrossRegionInferencePrefix] = None,
        enrichment_lambda_function: typing.Optional[_aws_cdk_aws_lambda_ceddda9d.Function] = None,
        post_processing_lambda_function: typing.Optional[_aws_cdk_aws_lambda_ceddda9d.Function] = None,
        processing_model_id: typing.Optional[_aws_cdk_aws_bedrock_ceddda9d.FoundationModelIdentifier] = None,
        processing_prompt: typing.Optional[builtins.str] = None,
        step_timeouts: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
        use_cross_region_inference: typing.Optional[builtins.bool] = None,
        document_processing_table: typing.Optional[_aws_cdk_aws_dynamodb_ceddda9d.Table] = None,
        enable_observability: typing.Optional[builtins.bool] = None,
        encryption_key: typing.Optional[_aws_cdk_aws_kms_ceddda9d.Key] = None,
        eventbridge_broker: typing.Optional[EventbridgeBroker] = None,
        ingress_adapter: typing.Optional[IAdapter] = None,
        network: typing.Optional[Network] = None,
        removal_policy: typing.Optional[_aws_cdk_ceddda9d.RemovalPolicy] = None,
        workflow_timeout: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
        log_group_data_protection: typing.Optional[typing.Union[LogGroupDataProtectionProps, typing.Dict[builtins.str, typing.Any]]] = None,
        metric_namespace: typing.Optional[builtins.str] = None,
        metric_service_name: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param processing_agent_parameters: 
        :param classification_model_id: (experimental) Bedrock foundation model for document classification step. Default: FoundationModelIdentifier.ANTHROPIC_CLAUDE_3_7_SONNET_20250219_V1_0
        :param classification_prompt: (experimental) Custom prompt template for document classification. Must include placeholder for document content. Default: DEFAULT_CLASSIFICATION_PROMPT
        :param cross_region_inference_prefix: (experimental) Prefix for cross-region inference configuration. Only used when useCrossRegionInference is true. Default: BedrockCrossRegionInferencePrefix.US
        :param enrichment_lambda_function: (experimental) Optional Lambda function for document enrichment step. If provided, will be invoked after extraction with workflow state.
        :param post_processing_lambda_function: (experimental) Optional Lambda function for post-processing step. If provided, will be invoked after enrichment with workflow state.
        :param processing_model_id: (experimental) Bedrock foundation model for document extraction step. Default: FoundationModelIdentifier.ANTHROPIC_CLAUDE_3_7_SONNET_20250219_V1_0
        :param processing_prompt: (experimental) Custom prompt template for document extraction. Must include placeholder for document content and classification result. Default: DEFAULT_EXTRACTION_PROMPT
        :param step_timeouts: (experimental) Timeout for individual Step Functions tasks (classification, extraction, etc.). Default: Duration.minutes(5)
        :param use_cross_region_inference: (experimental) Enable cross-region inference for Bedrock models to improve availability and performance. When enabled, uses inference profiles instead of direct model invocation. Default: false
        :param document_processing_table: (experimental) DynamoDB table for storing document processing metadata and workflow state. If not provided, a new table will be created with DocumentId as partition key.
        :param enable_observability: (experimental) Enable logging and tracing for all supporting resource. Default: false
        :param encryption_key: (experimental) KMS key to be used. Default: A new key would be created
        :param eventbridge_broker: (experimental) Optional EventBridge broker for publishing custom events during processing. If not provided, no custom events will be sent out.
        :param ingress_adapter: (experimental) Adapter that defines how the document processing workflow is triggered. Default: QueuedS3Adapter
        :param network: (experimental) Resources that can run inside a VPC will follow the provided network configuration. Default: resources will run outside of a VPC
        :param removal_policy: (experimental) Removal policy for created resources (bucket, table, queue). Default: RemovalPolicy.DESTROY
        :param workflow_timeout: (experimental) Maximum execution time for the Step Functions workflow. Default: Duration.minutes(30)
        :param log_group_data_protection: (experimental) Data protection related configuration. Default: a new KMS key would be generated
        :param metric_namespace: (experimental) Business metric namespace. Default: would be defined per use case
        :param metric_service_name: (experimental) Business metric service name dimension. Default: would be defined per use case

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b7f396236f637ec7234d81b355cf773497392b537455f3d888c4b7170ceed70a)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = AgenticDocumentProcessingProps(
            processing_agent_parameters=processing_agent_parameters,
            classification_model_id=classification_model_id,
            classification_prompt=classification_prompt,
            cross_region_inference_prefix=cross_region_inference_prefix,
            enrichment_lambda_function=enrichment_lambda_function,
            post_processing_lambda_function=post_processing_lambda_function,
            processing_model_id=processing_model_id,
            processing_prompt=processing_prompt,
            step_timeouts=step_timeouts,
            use_cross_region_inference=use_cross_region_inference,
            document_processing_table=document_processing_table,
            enable_observability=enable_observability,
            encryption_key=encryption_key,
            eventbridge_broker=eventbridge_broker,
            ingress_adapter=ingress_adapter,
            network=network,
            removal_policy=removal_policy,
            workflow_timeout=workflow_timeout,
            log_group_data_protection=log_group_data_protection,
            metric_namespace=metric_namespace,
            metric_service_name=metric_service_name,
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @jsii.member(jsii_name="processingStep")
    def _processing_step(
        self,
    ) -> typing.Union[_aws_cdk_aws_stepfunctions_tasks_ceddda9d.LambdaInvoke, _aws_cdk_aws_stepfunctions_tasks_ceddda9d.BedrockInvokeModel, _aws_cdk_aws_stepfunctions_tasks_ceddda9d.StepFunctionsStartExecution]:
        '''(experimental) Implements the document extraction step using Amazon Bedrock.

        Creates a Lambda function that invokes the configured Bedrock model to extract
        structured data from the document. Uses the classification result from the
        previous step to provide context for more accurate extraction.

        :stability: experimental
        '''
        return typing.cast(typing.Union[_aws_cdk_aws_stepfunctions_tasks_ceddda9d.LambdaInvoke, _aws_cdk_aws_stepfunctions_tasks_ceddda9d.BedrockInvokeModel, _aws_cdk_aws_stepfunctions_tasks_ceddda9d.StepFunctionsStartExecution], jsii.invoke(self, "processingStep", []))


@jsii.data_type(
    jsii_type="@cdklabs/cdk-appmod-catalog-blueprints.AgenticDocumentProcessingProps",
    jsii_struct_bases=[BedrockDocumentProcessingProps],
    name_mapping={
        "log_group_data_protection": "logGroupDataProtection",
        "metric_namespace": "metricNamespace",
        "metric_service_name": "metricServiceName",
        "document_processing_table": "documentProcessingTable",
        "enable_observability": "enableObservability",
        "encryption_key": "encryptionKey",
        "eventbridge_broker": "eventbridgeBroker",
        "ingress_adapter": "ingressAdapter",
        "network": "network",
        "removal_policy": "removalPolicy",
        "workflow_timeout": "workflowTimeout",
        "classification_model_id": "classificationModelId",
        "classification_prompt": "classificationPrompt",
        "cross_region_inference_prefix": "crossRegionInferencePrefix",
        "enrichment_lambda_function": "enrichmentLambdaFunction",
        "post_processing_lambda_function": "postProcessingLambdaFunction",
        "processing_model_id": "processingModelId",
        "processing_prompt": "processingPrompt",
        "step_timeouts": "stepTimeouts",
        "use_cross_region_inference": "useCrossRegionInference",
        "processing_agent_parameters": "processingAgentParameters",
    },
)
class AgenticDocumentProcessingProps(BedrockDocumentProcessingProps):
    def __init__(
        self,
        *,
        log_group_data_protection: typing.Optional[typing.Union[LogGroupDataProtectionProps, typing.Dict[builtins.str, typing.Any]]] = None,
        metric_namespace: typing.Optional[builtins.str] = None,
        metric_service_name: typing.Optional[builtins.str] = None,
        document_processing_table: typing.Optional[_aws_cdk_aws_dynamodb_ceddda9d.Table] = None,
        enable_observability: typing.Optional[builtins.bool] = None,
        encryption_key: typing.Optional[_aws_cdk_aws_kms_ceddda9d.Key] = None,
        eventbridge_broker: typing.Optional[EventbridgeBroker] = None,
        ingress_adapter: typing.Optional[IAdapter] = None,
        network: typing.Optional[Network] = None,
        removal_policy: typing.Optional[_aws_cdk_ceddda9d.RemovalPolicy] = None,
        workflow_timeout: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
        classification_model_id: typing.Optional[_aws_cdk_aws_bedrock_ceddda9d.FoundationModelIdentifier] = None,
        classification_prompt: typing.Optional[builtins.str] = None,
        cross_region_inference_prefix: typing.Optional[BedrockCrossRegionInferencePrefix] = None,
        enrichment_lambda_function: typing.Optional[_aws_cdk_aws_lambda_ceddda9d.Function] = None,
        post_processing_lambda_function: typing.Optional[_aws_cdk_aws_lambda_ceddda9d.Function] = None,
        processing_model_id: typing.Optional[_aws_cdk_aws_bedrock_ceddda9d.FoundationModelIdentifier] = None,
        processing_prompt: typing.Optional[builtins.str] = None,
        step_timeouts: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
        use_cross_region_inference: typing.Optional[builtins.bool] = None,
        processing_agent_parameters: typing.Optional[typing.Union[AgentProps, typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''
        :param log_group_data_protection: (experimental) Data protection related configuration. Default: a new KMS key would be generated
        :param metric_namespace: (experimental) Business metric namespace. Default: would be defined per use case
        :param metric_service_name: (experimental) Business metric service name dimension. Default: would be defined per use case
        :param document_processing_table: (experimental) DynamoDB table for storing document processing metadata and workflow state. If not provided, a new table will be created with DocumentId as partition key.
        :param enable_observability: (experimental) Enable logging and tracing for all supporting resource. Default: false
        :param encryption_key: (experimental) KMS key to be used. Default: A new key would be created
        :param eventbridge_broker: (experimental) Optional EventBridge broker for publishing custom events during processing. If not provided, no custom events will be sent out.
        :param ingress_adapter: (experimental) Adapter that defines how the document processing workflow is triggered. Default: QueuedS3Adapter
        :param network: (experimental) Resources that can run inside a VPC will follow the provided network configuration. Default: resources will run outside of a VPC
        :param removal_policy: (experimental) Removal policy for created resources (bucket, table, queue). Default: RemovalPolicy.DESTROY
        :param workflow_timeout: (experimental) Maximum execution time for the Step Functions workflow. Default: Duration.minutes(30)
        :param classification_model_id: (experimental) Bedrock foundation model for document classification step. Default: FoundationModelIdentifier.ANTHROPIC_CLAUDE_3_7_SONNET_20250219_V1_0
        :param classification_prompt: (experimental) Custom prompt template for document classification. Must include placeholder for document content. Default: DEFAULT_CLASSIFICATION_PROMPT
        :param cross_region_inference_prefix: (experimental) Prefix for cross-region inference configuration. Only used when useCrossRegionInference is true. Default: BedrockCrossRegionInferencePrefix.US
        :param enrichment_lambda_function: (experimental) Optional Lambda function for document enrichment step. If provided, will be invoked after extraction with workflow state.
        :param post_processing_lambda_function: (experimental) Optional Lambda function for post-processing step. If provided, will be invoked after enrichment with workflow state.
        :param processing_model_id: (experimental) Bedrock foundation model for document extraction step. Default: FoundationModelIdentifier.ANTHROPIC_CLAUDE_3_7_SONNET_20250219_V1_0
        :param processing_prompt: (experimental) Custom prompt template for document extraction. Must include placeholder for document content and classification result. Default: DEFAULT_EXTRACTION_PROMPT
        :param step_timeouts: (experimental) Timeout for individual Step Functions tasks (classification, extraction, etc.). Default: Duration.minutes(5)
        :param use_cross_region_inference: (experimental) Enable cross-region inference for Bedrock models to improve availability and performance. When enabled, uses inference profiles instead of direct model invocation. Default: false
        :param processing_agent_parameters: 

        :stability: experimental
        '''
        if isinstance(log_group_data_protection, dict):
            log_group_data_protection = LogGroupDataProtectionProps(**log_group_data_protection)
        if isinstance(processing_agent_parameters, dict):
            processing_agent_parameters = AgentProps(**processing_agent_parameters)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__da9ccab0035a06d18b5aa3f2de69201b3bbd6e30f7707a291977a0e4f83a72f4)
            check_type(argname="argument log_group_data_protection", value=log_group_data_protection, expected_type=type_hints["log_group_data_protection"])
            check_type(argname="argument metric_namespace", value=metric_namespace, expected_type=type_hints["metric_namespace"])
            check_type(argname="argument metric_service_name", value=metric_service_name, expected_type=type_hints["metric_service_name"])
            check_type(argname="argument document_processing_table", value=document_processing_table, expected_type=type_hints["document_processing_table"])
            check_type(argname="argument enable_observability", value=enable_observability, expected_type=type_hints["enable_observability"])
            check_type(argname="argument encryption_key", value=encryption_key, expected_type=type_hints["encryption_key"])
            check_type(argname="argument eventbridge_broker", value=eventbridge_broker, expected_type=type_hints["eventbridge_broker"])
            check_type(argname="argument ingress_adapter", value=ingress_adapter, expected_type=type_hints["ingress_adapter"])
            check_type(argname="argument network", value=network, expected_type=type_hints["network"])
            check_type(argname="argument removal_policy", value=removal_policy, expected_type=type_hints["removal_policy"])
            check_type(argname="argument workflow_timeout", value=workflow_timeout, expected_type=type_hints["workflow_timeout"])
            check_type(argname="argument classification_model_id", value=classification_model_id, expected_type=type_hints["classification_model_id"])
            check_type(argname="argument classification_prompt", value=classification_prompt, expected_type=type_hints["classification_prompt"])
            check_type(argname="argument cross_region_inference_prefix", value=cross_region_inference_prefix, expected_type=type_hints["cross_region_inference_prefix"])
            check_type(argname="argument enrichment_lambda_function", value=enrichment_lambda_function, expected_type=type_hints["enrichment_lambda_function"])
            check_type(argname="argument post_processing_lambda_function", value=post_processing_lambda_function, expected_type=type_hints["post_processing_lambda_function"])
            check_type(argname="argument processing_model_id", value=processing_model_id, expected_type=type_hints["processing_model_id"])
            check_type(argname="argument processing_prompt", value=processing_prompt, expected_type=type_hints["processing_prompt"])
            check_type(argname="argument step_timeouts", value=step_timeouts, expected_type=type_hints["step_timeouts"])
            check_type(argname="argument use_cross_region_inference", value=use_cross_region_inference, expected_type=type_hints["use_cross_region_inference"])
            check_type(argname="argument processing_agent_parameters", value=processing_agent_parameters, expected_type=type_hints["processing_agent_parameters"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if log_group_data_protection is not None:
            self._values["log_group_data_protection"] = log_group_data_protection
        if metric_namespace is not None:
            self._values["metric_namespace"] = metric_namespace
        if metric_service_name is not None:
            self._values["metric_service_name"] = metric_service_name
        if document_processing_table is not None:
            self._values["document_processing_table"] = document_processing_table
        if enable_observability is not None:
            self._values["enable_observability"] = enable_observability
        if encryption_key is not None:
            self._values["encryption_key"] = encryption_key
        if eventbridge_broker is not None:
            self._values["eventbridge_broker"] = eventbridge_broker
        if ingress_adapter is not None:
            self._values["ingress_adapter"] = ingress_adapter
        if network is not None:
            self._values["network"] = network
        if removal_policy is not None:
            self._values["removal_policy"] = removal_policy
        if workflow_timeout is not None:
            self._values["workflow_timeout"] = workflow_timeout
        if classification_model_id is not None:
            self._values["classification_model_id"] = classification_model_id
        if classification_prompt is not None:
            self._values["classification_prompt"] = classification_prompt
        if cross_region_inference_prefix is not None:
            self._values["cross_region_inference_prefix"] = cross_region_inference_prefix
        if enrichment_lambda_function is not None:
            self._values["enrichment_lambda_function"] = enrichment_lambda_function
        if post_processing_lambda_function is not None:
            self._values["post_processing_lambda_function"] = post_processing_lambda_function
        if processing_model_id is not None:
            self._values["processing_model_id"] = processing_model_id
        if processing_prompt is not None:
            self._values["processing_prompt"] = processing_prompt
        if step_timeouts is not None:
            self._values["step_timeouts"] = step_timeouts
        if use_cross_region_inference is not None:
            self._values["use_cross_region_inference"] = use_cross_region_inference
        if processing_agent_parameters is not None:
            self._values["processing_agent_parameters"] = processing_agent_parameters

    @builtins.property
    def log_group_data_protection(self) -> typing.Optional[LogGroupDataProtectionProps]:
        '''(experimental) Data protection related configuration.

        :default: a new KMS key would be generated

        :stability: experimental
        '''
        result = self._values.get("log_group_data_protection")
        return typing.cast(typing.Optional[LogGroupDataProtectionProps], result)

    @builtins.property
    def metric_namespace(self) -> typing.Optional[builtins.str]:
        '''(experimental) Business metric namespace.

        :default: would be defined per use case

        :stability: experimental
        '''
        result = self._values.get("metric_namespace")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def metric_service_name(self) -> typing.Optional[builtins.str]:
        '''(experimental) Business metric service name dimension.

        :default: would be defined per use case

        :stability: experimental
        '''
        result = self._values.get("metric_service_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def document_processing_table(
        self,
    ) -> typing.Optional[_aws_cdk_aws_dynamodb_ceddda9d.Table]:
        '''(experimental) DynamoDB table for storing document processing metadata and workflow state.

        If not provided, a new table will be created with DocumentId as partition key.

        :stability: experimental
        '''
        result = self._values.get("document_processing_table")
        return typing.cast(typing.Optional[_aws_cdk_aws_dynamodb_ceddda9d.Table], result)

    @builtins.property
    def enable_observability(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Enable logging and tracing for all supporting resource.

        :default: false

        :stability: experimental
        '''
        result = self._values.get("enable_observability")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def encryption_key(self) -> typing.Optional[_aws_cdk_aws_kms_ceddda9d.Key]:
        '''(experimental) KMS key to be used.

        :default: A new key would be created

        :stability: experimental
        '''
        result = self._values.get("encryption_key")
        return typing.cast(typing.Optional[_aws_cdk_aws_kms_ceddda9d.Key], result)

    @builtins.property
    def eventbridge_broker(self) -> typing.Optional[EventbridgeBroker]:
        '''(experimental) Optional EventBridge broker for publishing custom events during processing.

        If not provided, no custom events will be sent out.

        :stability: experimental
        '''
        result = self._values.get("eventbridge_broker")
        return typing.cast(typing.Optional[EventbridgeBroker], result)

    @builtins.property
    def ingress_adapter(self) -> typing.Optional[IAdapter]:
        '''(experimental) Adapter that defines how the document processing workflow is triggered.

        :default: QueuedS3Adapter

        :stability: experimental
        '''
        result = self._values.get("ingress_adapter")
        return typing.cast(typing.Optional[IAdapter], result)

    @builtins.property
    def network(self) -> typing.Optional[Network]:
        '''(experimental) Resources that can run inside a VPC will follow the provided network configuration.

        :default: resources will run outside of a VPC

        :stability: experimental
        '''
        result = self._values.get("network")
        return typing.cast(typing.Optional[Network], result)

    @builtins.property
    def removal_policy(self) -> typing.Optional[_aws_cdk_ceddda9d.RemovalPolicy]:
        '''(experimental) Removal policy for created resources (bucket, table, queue).

        :default: RemovalPolicy.DESTROY

        :stability: experimental
        '''
        result = self._values.get("removal_policy")
        return typing.cast(typing.Optional[_aws_cdk_ceddda9d.RemovalPolicy], result)

    @builtins.property
    def workflow_timeout(self) -> typing.Optional[_aws_cdk_ceddda9d.Duration]:
        '''(experimental) Maximum execution time for the Step Functions workflow.

        :default: Duration.minutes(30)

        :stability: experimental
        '''
        result = self._values.get("workflow_timeout")
        return typing.cast(typing.Optional[_aws_cdk_ceddda9d.Duration], result)

    @builtins.property
    def classification_model_id(
        self,
    ) -> typing.Optional[_aws_cdk_aws_bedrock_ceddda9d.FoundationModelIdentifier]:
        '''(experimental) Bedrock foundation model for document classification step.

        :default: FoundationModelIdentifier.ANTHROPIC_CLAUDE_3_7_SONNET_20250219_V1_0

        :stability: experimental
        '''
        result = self._values.get("classification_model_id")
        return typing.cast(typing.Optional[_aws_cdk_aws_bedrock_ceddda9d.FoundationModelIdentifier], result)

    @builtins.property
    def classification_prompt(self) -> typing.Optional[builtins.str]:
        '''(experimental) Custom prompt template for document classification.

        Must include placeholder for document content.

        :default: DEFAULT_CLASSIFICATION_PROMPT

        :stability: experimental
        '''
        result = self._values.get("classification_prompt")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def cross_region_inference_prefix(
        self,
    ) -> typing.Optional[BedrockCrossRegionInferencePrefix]:
        '''(experimental) Prefix for cross-region inference configuration.

        Only used when useCrossRegionInference is true.

        :default: BedrockCrossRegionInferencePrefix.US

        :stability: experimental
        '''
        result = self._values.get("cross_region_inference_prefix")
        return typing.cast(typing.Optional[BedrockCrossRegionInferencePrefix], result)

    @builtins.property
    def enrichment_lambda_function(
        self,
    ) -> typing.Optional[_aws_cdk_aws_lambda_ceddda9d.Function]:
        '''(experimental) Optional Lambda function for document enrichment step.

        If provided, will be invoked after extraction with workflow state.

        :stability: experimental
        '''
        result = self._values.get("enrichment_lambda_function")
        return typing.cast(typing.Optional[_aws_cdk_aws_lambda_ceddda9d.Function], result)

    @builtins.property
    def post_processing_lambda_function(
        self,
    ) -> typing.Optional[_aws_cdk_aws_lambda_ceddda9d.Function]:
        '''(experimental) Optional Lambda function for post-processing step.

        If provided, will be invoked after enrichment with workflow state.

        :stability: experimental
        '''
        result = self._values.get("post_processing_lambda_function")
        return typing.cast(typing.Optional[_aws_cdk_aws_lambda_ceddda9d.Function], result)

    @builtins.property
    def processing_model_id(
        self,
    ) -> typing.Optional[_aws_cdk_aws_bedrock_ceddda9d.FoundationModelIdentifier]:
        '''(experimental) Bedrock foundation model for document extraction step.

        :default: FoundationModelIdentifier.ANTHROPIC_CLAUDE_3_7_SONNET_20250219_V1_0

        :stability: experimental
        '''
        result = self._values.get("processing_model_id")
        return typing.cast(typing.Optional[_aws_cdk_aws_bedrock_ceddda9d.FoundationModelIdentifier], result)

    @builtins.property
    def processing_prompt(self) -> typing.Optional[builtins.str]:
        '''(experimental) Custom prompt template for document extraction.

        Must include placeholder for document content and classification result.

        :default: DEFAULT_EXTRACTION_PROMPT

        :stability: experimental
        '''
        result = self._values.get("processing_prompt")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def step_timeouts(self) -> typing.Optional[_aws_cdk_ceddda9d.Duration]:
        '''(experimental) Timeout for individual Step Functions tasks (classification, extraction, etc.).

        :default: Duration.minutes(5)

        :stability: experimental
        '''
        result = self._values.get("step_timeouts")
        return typing.cast(typing.Optional[_aws_cdk_ceddda9d.Duration], result)

    @builtins.property
    def use_cross_region_inference(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Enable cross-region inference for Bedrock models to improve availability and performance.

        When enabled, uses inference profiles instead of direct model invocation.

        :default: false

        :stability: experimental
        '''
        result = self._values.get("use_cross_region_inference")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def processing_agent_parameters(self) -> typing.Optional[AgentProps]:
        '''
        :stability: experimental
        '''
        result = self._values.get("processing_agent_parameters")
        return typing.cast(typing.Optional[AgentProps], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "AgenticDocumentProcessingProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


__all__ = [
    "AccessLog",
    "AccessLogProps",
    "AdditionalDistributionProps",
    "AgentProps",
    "AgenticDocumentProcessing",
    "AgenticDocumentProcessingProps",
    "BaseDocumentProcessing",
    "BaseDocumentProcessingProps",
    "BedrockCrossRegionInferencePrefix",
    "BedrockDocumentProcessing",
    "BedrockDocumentProcessingProps",
    "CloudfrontDistributionObservabilityPropertyInjector",
    "CustomDomainConfig",
    "DataLoader",
    "DataLoaderProps",
    "DatabaseConfig",
    "DatabaseEngine",
    "DefaultDocumentProcessingConfig",
    "DefaultObservabilityConfig",
    "DefaultRuntimes",
    "EventbridgeBroker",
    "EventbridgeBrokerProps",
    "FileInput",
    "FileType",
    "Frontend",
    "FrontendProps",
    "IAdapter",
    "IObservable",
    "LambdaIamUtils",
    "LambdaIamUtilsStackInfo",
    "LambdaLogsPermissionsProps",
    "LambdaLogsPermissionsResult",
    "LambdaObservabilityPropertyInjector",
    "LogGroupDataProtectionProps",
    "Network",
    "NetworkProps",
    "ObservableProps",
    "PowertoolsConfig",
    "QueuedS3Adapter",
    "QueuedS3AdapterProps",
    "StateMachineObservabilityPropertyInjector",
]

publication.publish()

def _typecheckingstub__d0c79880c62971c0b94c27211aa57e94a14b8b594133479abb3588b22b301cf7(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    bucket_name: typing.Optional[builtins.str] = None,
    bucket_prefix: typing.Optional[builtins.str] = None,
    lifecycle_rules: typing.Optional[typing.Sequence[typing.Union[_aws_cdk_aws_s3_ceddda9d.LifecycleRule, typing.Dict[builtins.str, typing.Any]]]] = None,
    versioned: typing.Optional[builtins.bool] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__bb3bab7dfdf58893d762b8a3579b2e248b758bf8db791e3986df9451e32ada3e(
    service_name: builtins.str,
    resource_name: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9988cc2b7efe7f7c7c17c94e465c36241770aa21cbe1b07c110b8e2dacedaf59(
    service_name: builtins.str,
    resource_name: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b0d5807bf69e9243b9fd452b7437cfe9f4102d78752673f223f3ae14073937e1(
    *,
    bucket_name: typing.Optional[builtins.str] = None,
    bucket_prefix: typing.Optional[builtins.str] = None,
    lifecycle_rules: typing.Optional[typing.Sequence[typing.Union[_aws_cdk_aws_s3_ceddda9d.LifecycleRule, typing.Dict[builtins.str, typing.Any]]]] = None,
    versioned: typing.Optional[builtins.bool] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__14d3ed5928e5166082cd47a907ab754473c20bb045dc424135b4690811543601(
    *,
    comment: typing.Optional[builtins.str] = None,
    enabled: typing.Optional[builtins.bool] = None,
    price_class: typing.Optional[_aws_cdk_aws_cloudfront_ceddda9d.PriceClass] = None,
    web_acl_id: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e1a82500ee072f393cd9a2ada2f9a3434219c7a51186f26fbba3061bd896d11e(
    *,
    agent_system_prompt: typing.Optional[builtins.str] = None,
    lambda_layers: typing.Optional[typing.Sequence[_aws_cdk_aws_lambda_ceddda9d.LayerVersion]] = None,
    tools_bucket: typing.Optional[_aws_cdk_aws_s3_ceddda9d.Bucket] = None,
    tools_location: typing.Optional[typing.Sequence[builtins.str]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2270aedab8c9db027e16b28fd9de8610d0f7e47778cdf1d501539d0e440a561d(
    original_props: typing.Any,
    *,
    id: builtins.str,
    scope: _constructs_77d1e7e8.Construct,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__45e622c5dc8075e1ee5cdf9df72ea9b7ca33e0a7cf348dfaf54f93e635e9dde8(
    *,
    certificate: _aws_cdk_aws_certificatemanager_ceddda9d.ICertificate,
    domain_name: builtins.str,
    hosted_zone: typing.Optional[_aws_cdk_aws_route53_ceddda9d.IHostedZone] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__270a76813d598a503e52c71a882567ace4b31275076ba0bcefcc5ff1011d5018(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    database_config: typing.Union[DatabaseConfig, typing.Dict[builtins.str, typing.Any]],
    file_inputs: typing.Sequence[typing.Union[FileInput, typing.Dict[builtins.str, typing.Any]]],
    memory_size: typing.Optional[jsii.Number] = None,
    removal_policy: typing.Optional[_aws_cdk_ceddda9d.RemovalPolicy] = None,
    timeout: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__efd46917d5b396c28d8f6ffeea52cc31230f92bb12d3a0b916d59526a781140a(
    statement: _aws_cdk_aws_iam_ceddda9d.PolicyStatement,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__cd063a11debecd44b792418fb4aa1f7320d173a2fbc3280588266e303321f59e(
    value: typing.Optional[_aws_cdk_aws_s3_deployment_ceddda9d.BucketDeployment],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__79385aca2a5a0bb7a2e64dbdad2106a739cca7fbad6670895f995ed402f5a8fe(
    *,
    database_config: typing.Union[DatabaseConfig, typing.Dict[builtins.str, typing.Any]],
    file_inputs: typing.Sequence[typing.Union[FileInput, typing.Dict[builtins.str, typing.Any]]],
    memory_size: typing.Optional[jsii.Number] = None,
    removal_policy: typing.Optional[_aws_cdk_ceddda9d.RemovalPolicy] = None,
    timeout: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__28429cd4673598c14d3b2db601f7758c41a1c9972a1d3aeb36a73a6d7afffe94(
    *,
    database_name: builtins.str,
    engine: DatabaseEngine,
    secret: _aws_cdk_aws_secretsmanager_ceddda9d.ISecret,
    security_group: _aws_cdk_aws_ec2_ceddda9d.ISecurityGroup,
    vpc: _aws_cdk_aws_ec2_ceddda9d.IVpc,
    cluster: typing.Optional[_aws_cdk_aws_rds_ceddda9d.IDatabaseCluster] = None,
    instance: typing.Optional[_aws_cdk_aws_rds_ceddda9d.IDatabaseInstance] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5391a3753ae12822ab842065b2f29fede1c6b75f7e0ba6cdca1be351c9c104c3(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    event_source: builtins.str,
    kms_key: typing.Optional[_aws_cdk_aws_kms_ceddda9d.Key] = None,
    name: typing.Optional[builtins.str] = None,
    removal_policy: typing.Optional[_aws_cdk_ceddda9d.RemovalPolicy] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__71a910ff106734bd214c5973b84305b89274d3d6adbe4eedaa2c546cb060d0d7(
    detail_type: builtins.str,
    event_detail: typing.Any,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ecd91fa4cae79b6f27bdbae2c38230e7edda9cec831ac503ca3b7c01b0311241(
    *,
    event_source: builtins.str,
    kms_key: typing.Optional[_aws_cdk_aws_kms_ceddda9d.Key] = None,
    name: typing.Optional[builtins.str] = None,
    removal_policy: typing.Optional[_aws_cdk_ceddda9d.RemovalPolicy] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f22614c3ee9aff68919f8ac64743fb8c255ed9c33337d90d40c2622733942ed5(
    *,
    file_path: builtins.str,
    file_type: FileType,
    continue_on_error: typing.Optional[builtins.bool] = None,
    execution_order: typing.Optional[jsii.Number] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__59f5637ea312a9fb8090cc497bbaa3fb29d31e5a16d1958df0e9a4337936da88(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    source_directory: builtins.str,
    build_command: typing.Optional[builtins.str] = None,
    build_output_directory: typing.Optional[builtins.str] = None,
    custom_domain: typing.Optional[typing.Union[CustomDomainConfig, typing.Dict[builtins.str, typing.Any]]] = None,
    distribution_props: typing.Optional[typing.Union[AdditionalDistributionProps, typing.Dict[builtins.str, typing.Any]]] = None,
    enable_observability: typing.Optional[builtins.bool] = None,
    error_responses: typing.Optional[typing.Sequence[typing.Union[_aws_cdk_aws_cloudfront_ceddda9d.ErrorResponse, typing.Dict[builtins.str, typing.Any]]]] = None,
    removal_policy: typing.Optional[_aws_cdk_ceddda9d.RemovalPolicy] = None,
    skip_build: typing.Optional[builtins.bool] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2648a6f2c6f02177f5b324264b7de549aa23b0c1d93c8d6cccbc307a85e0c0fc(
    *,
    source_directory: builtins.str,
    build_command: typing.Optional[builtins.str] = None,
    build_output_directory: typing.Optional[builtins.str] = None,
    custom_domain: typing.Optional[typing.Union[CustomDomainConfig, typing.Dict[builtins.str, typing.Any]]] = None,
    distribution_props: typing.Optional[typing.Union[AdditionalDistributionProps, typing.Dict[builtins.str, typing.Any]]] = None,
    enable_observability: typing.Optional[builtins.bool] = None,
    error_responses: typing.Optional[typing.Sequence[typing.Union[_aws_cdk_aws_cloudfront_ceddda9d.ErrorResponse, typing.Dict[builtins.str, typing.Any]]]] = None,
    removal_policy: typing.Optional[_aws_cdk_ceddda9d.RemovalPolicy] = None,
    skip_build: typing.Optional[builtins.bool] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5998f6c7e16512d92cd00097e77d737333304685208eb36a522c156f8378a9e7(
    scope: _constructs_77d1e7e8.Construct,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b61e74ddd8982f4b30ae59307c9fb3adaff26122ddc7f5faabc2cc8e1e2da034(
    scope: _constructs_77d1e7e8.Construct,
    state_machine: _aws_cdk_aws_stepfunctions_ceddda9d.StateMachine,
    *,
    document_processing_table: typing.Optional[_aws_cdk_aws_dynamodb_ceddda9d.Table] = None,
    enable_observability: typing.Optional[builtins.bool] = None,
    encryption_key: typing.Optional[_aws_cdk_aws_kms_ceddda9d.Key] = None,
    eventbridge_broker: typing.Optional[EventbridgeBroker] = None,
    ingress_adapter: typing.Optional[IAdapter] = None,
    network: typing.Optional[Network] = None,
    removal_policy: typing.Optional[_aws_cdk_ceddda9d.RemovalPolicy] = None,
    workflow_timeout: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
    log_group_data_protection: typing.Optional[typing.Union[LogGroupDataProtectionProps, typing.Dict[builtins.str, typing.Any]]] = None,
    metric_namespace: typing.Optional[builtins.str] = None,
    metric_service_name: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__cd0aad7a5879633fca8d89cbf92e8f5a13e31615116036f29a82a58c1bb4727d(
    scope: _constructs_77d1e7e8.Construct,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__82a45114a0ff76d4b9d091edd6674d4e762dc5ca19631d61579cf1aa47e30b5e(
    additional_iam_actions: typing.Optional[typing.Sequence[builtins.str]] = None,
    narrow_actions: typing.Optional[builtins.bool] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__17f7e7f35ea8e49cf6ded248435aa1e1dcf416e61c549f3e7b74baad3ac399e7(
    scope: _constructs_77d1e7e8.Construct,
    *,
    document_processing_table: typing.Optional[_aws_cdk_aws_dynamodb_ceddda9d.Table] = None,
    enable_observability: typing.Optional[builtins.bool] = None,
    encryption_key: typing.Optional[_aws_cdk_aws_kms_ceddda9d.Key] = None,
    eventbridge_broker: typing.Optional[EventbridgeBroker] = None,
    ingress_adapter: typing.Optional[IAdapter] = None,
    network: typing.Optional[Network] = None,
    removal_policy: typing.Optional[_aws_cdk_ceddda9d.RemovalPolicy] = None,
    workflow_timeout: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
    log_group_data_protection: typing.Optional[typing.Union[LogGroupDataProtectionProps, typing.Dict[builtins.str, typing.Any]]] = None,
    metric_namespace: typing.Optional[builtins.str] = None,
    metric_service_name: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8fea74c9846ad0c5bdddcbfe10063247cb7bcf58aac91e0be80d1226246784e4(
    table_arn: builtins.str,
    actions: typing.Optional[typing.Sequence[builtins.str]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ef86294be8c776ba98bebc269fab82304f75649efab35cf030d999168ba5d690(
    key_arn: builtins.str,
    actions: typing.Optional[typing.Sequence[builtins.str]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7762a976633c1cec438c3058cfc410cab5cdbf541350c2fdcb64bcfd9599e7fb(
    bucket_arn: builtins.str,
    actions: typing.Optional[typing.Sequence[builtins.str]] = None,
    include_objects: typing.Optional[builtins.bool] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__cb1398e35974542f1ff1f03b7872981aa0ef2bb90eed20673a20914f5c7e567c(
    secret_arn: builtins.str,
    actions: typing.Optional[typing.Sequence[builtins.str]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8aa3558a2d320688189fd59ffa216e00f3b66d4b1a02026a2dc9bd5fd61c5f36(
    topic_arn: builtins.str,
    actions: typing.Optional[typing.Sequence[builtins.str]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5ed421dddfcb3e375ee01a9efb4d503dd54b5351b630f200cd829438bb6c9c89(
    queue_arn: builtins.str,
    actions: typing.Optional[typing.Sequence[builtins.str]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__cbdc1926ad0aa5c4b79aa48c962c929c8e50b7236860f58373b511defa1fca97(
    state_machine_arn: builtins.str,
    actions: typing.Optional[typing.Sequence[builtins.str]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__56aa9ee6986a4b2052d36311105a3c43214029d77a8db5f3ca96f5b23dd95f36(
    scope: _constructs_77d1e7e8.Construct,
    base_name: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__555f78633564658fa9ba3d47cbfcf9615db101bbba832804f67bcce2b828f673(
    scope: _constructs_77d1e7e8.Construct,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1dcdad24849926b01541cd5e3a49b2718bca23f70268629b13a2467789ce6acc(
    *,
    account: builtins.str,
    region: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__47564dc2777638ca33ba53983ac385b2dd8b03133d66569da912ae1ce7e55503(
    *,
    account: builtins.str,
    function_name: builtins.str,
    region: builtins.str,
    scope: _constructs_77d1e7e8.Construct,
    enable_observability: typing.Optional[builtins.bool] = None,
    log_group_name: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2180e53f0ba520cfa92d16443491985db8ed304d09797b9d758ad70b55d7b617(
    *,
    policy_statements: typing.Sequence[_aws_cdk_aws_iam_ceddda9d.PolicyStatement],
    unique_function_name: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__97c5107ef8c7184168153144168438a4ff4ae054305d1a82db0a0514c98b6d0b(
    original_props: typing.Any,
    *,
    id: builtins.str,
    scope: _constructs_77d1e7e8.Construct,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__544372751dab1bedee4ed043bef50312abd2658c1142e4b4809c0617165dc597(
    *,
    data_protection_identifiers: typing.Optional[typing.Sequence[_aws_cdk_aws_logs_ceddda9d.DataIdentifier]] = None,
    log_group_encryption_key: typing.Optional[_aws_cdk_aws_kms_ceddda9d.Key] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6ad9a3df68ffea56f493c494b7c642fca53d11a7de99864bb5e94dffe00ed330(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    ip_addresses: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.IIpAddresses] = None,
    max_azs: typing.Optional[jsii.Number] = None,
    nat_gateway_provider: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.NatProvider] = None,
    nat_gateways: typing.Optional[jsii.Number] = None,
    nat_gateway_subnets: typing.Optional[typing.Union[_aws_cdk_aws_ec2_ceddda9d.SubnetSelection, typing.Dict[builtins.str, typing.Any]]] = None,
    private: typing.Optional[builtins.bool] = None,
    subnet_configuration: typing.Optional[typing.Sequence[typing.Union[_aws_cdk_aws_ec2_ceddda9d.SubnetConfiguration, typing.Dict[builtins.str, typing.Any]]]] = None,
    vpc_name: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__014347d1e11f93271eb3a6b34bc02d137814401023f915adcd8e379b691810e9(
    id: builtins.str,
    service: _aws_cdk_aws_ec2_ceddda9d.InterfaceVpcEndpointService,
    peer: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.IPeer] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0c7413b984143840b4fc2e4fe5dd9854fed611c52a71931a04773289b6f1fdde(
    *,
    ip_addresses: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.IIpAddresses] = None,
    max_azs: typing.Optional[jsii.Number] = None,
    nat_gateway_provider: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.NatProvider] = None,
    nat_gateways: typing.Optional[jsii.Number] = None,
    nat_gateway_subnets: typing.Optional[typing.Union[_aws_cdk_aws_ec2_ceddda9d.SubnetSelection, typing.Dict[builtins.str, typing.Any]]] = None,
    private: typing.Optional[builtins.bool] = None,
    subnet_configuration: typing.Optional[typing.Sequence[typing.Union[_aws_cdk_aws_ec2_ceddda9d.SubnetConfiguration, typing.Dict[builtins.str, typing.Any]]]] = None,
    vpc_name: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__31fd1e05df7b558405e183d7153d9217ec52b5d7deb1bd88be445a2930061329(
    *,
    log_group_data_protection: typing.Optional[typing.Union[LogGroupDataProtectionProps, typing.Dict[builtins.str, typing.Any]]] = None,
    metric_namespace: typing.Optional[builtins.str] = None,
    metric_service_name: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e065c545d4fce5c4fc2579c3efea8203f50b6d3c8b39aa1595ea3577d04bc025(
    enable_observability: typing.Optional[builtins.bool] = None,
    metrics_namespace: typing.Optional[builtins.str] = None,
    service_name: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b95daf862a9819daa9b25cecfc08214dc429ef07ac6de3920b5dea59e01616eb(
    scope: _constructs_77d1e7e8.Construct,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__fb0e9adf74054c1b0a1974cab45642af57cb1651ef8052310a0229dae1eac178(
    scope: _constructs_77d1e7e8.Construct,
    state_machine: _aws_cdk_aws_stepfunctions_ceddda9d.StateMachine,
    *,
    document_processing_table: typing.Optional[_aws_cdk_aws_dynamodb_ceddda9d.Table] = None,
    enable_observability: typing.Optional[builtins.bool] = None,
    encryption_key: typing.Optional[_aws_cdk_aws_kms_ceddda9d.Key] = None,
    eventbridge_broker: typing.Optional[EventbridgeBroker] = None,
    ingress_adapter: typing.Optional[IAdapter] = None,
    network: typing.Optional[Network] = None,
    removal_policy: typing.Optional[_aws_cdk_ceddda9d.RemovalPolicy] = None,
    workflow_timeout: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
    log_group_data_protection: typing.Optional[typing.Union[LogGroupDataProtectionProps, typing.Dict[builtins.str, typing.Any]]] = None,
    metric_namespace: typing.Optional[builtins.str] = None,
    metric_service_name: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__76aa2fd577ace3b2507bf11a33f4d039ae5ac0af0d5d3edede30c4515a1a0986(
    scope: _constructs_77d1e7e8.Construct,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__308867c51abfbbc08d0fba9125db9b86eddda969dc95de8546e6f8cb242ee8a9(
    additional_iam_actions: typing.Optional[typing.Sequence[builtins.str]] = None,
    narrow_actions: typing.Optional[builtins.bool] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3fe79d0c4a3a771012bc95cea6a690155ea89fa70073f87564e65aad5cdfdb64(
    scope: _constructs_77d1e7e8.Construct,
    *,
    document_processing_table: typing.Optional[_aws_cdk_aws_dynamodb_ceddda9d.Table] = None,
    enable_observability: typing.Optional[builtins.bool] = None,
    encryption_key: typing.Optional[_aws_cdk_aws_kms_ceddda9d.Key] = None,
    eventbridge_broker: typing.Optional[EventbridgeBroker] = None,
    ingress_adapter: typing.Optional[IAdapter] = None,
    network: typing.Optional[Network] = None,
    removal_policy: typing.Optional[_aws_cdk_ceddda9d.RemovalPolicy] = None,
    workflow_timeout: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
    log_group_data_protection: typing.Optional[typing.Union[LogGroupDataProtectionProps, typing.Dict[builtins.str, typing.Any]]] = None,
    metric_namespace: typing.Optional[builtins.str] = None,
    metric_service_name: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c2db7ec0d4b3e93062e1f20f29f9821e5a0fd526ecf05f9ccaa6db663fb1e8de(
    *,
    bucket: typing.Optional[_aws_cdk_aws_s3_ceddda9d.Bucket] = None,
    dlq_max_receive_count: typing.Optional[jsii.Number] = None,
    failed_prefix: typing.Optional[builtins.str] = None,
    processed_prefix: typing.Optional[builtins.str] = None,
    queue_visibility_timeout: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
    raw_prefix: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__011b55520774139b52c951d9cc59273f686e377b5415ee42a57650da571d43e7(
    original_props: typing.Any,
    *,
    id: builtins.str,
    scope: _constructs_77d1e7e8.Construct,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__117c249a26f3e7532983afc9123fadff3e20effcc69408df0f45a03eb720ea8a(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    document_processing_table: typing.Optional[_aws_cdk_aws_dynamodb_ceddda9d.Table] = None,
    enable_observability: typing.Optional[builtins.bool] = None,
    encryption_key: typing.Optional[_aws_cdk_aws_kms_ceddda9d.Key] = None,
    eventbridge_broker: typing.Optional[EventbridgeBroker] = None,
    ingress_adapter: typing.Optional[IAdapter] = None,
    network: typing.Optional[Network] = None,
    removal_policy: typing.Optional[_aws_cdk_ceddda9d.RemovalPolicy] = None,
    workflow_timeout: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
    log_group_data_protection: typing.Optional[typing.Union[LogGroupDataProtectionProps, typing.Dict[builtins.str, typing.Any]]] = None,
    metric_namespace: typing.Optional[builtins.str] = None,
    metric_service_name: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__900aa9de379313a2a9a3e24a2901f803dec0a30dde90b7255d9f180e263b020d(
    state_machine_id: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__75e07bce24d48571be58cad69f751b10a17a738fdb9db601acdc689ff1e6da22(
    *,
    log_group_data_protection: typing.Optional[typing.Union[LogGroupDataProtectionProps, typing.Dict[builtins.str, typing.Any]]] = None,
    metric_namespace: typing.Optional[builtins.str] = None,
    metric_service_name: typing.Optional[builtins.str] = None,
    document_processing_table: typing.Optional[_aws_cdk_aws_dynamodb_ceddda9d.Table] = None,
    enable_observability: typing.Optional[builtins.bool] = None,
    encryption_key: typing.Optional[_aws_cdk_aws_kms_ceddda9d.Key] = None,
    eventbridge_broker: typing.Optional[EventbridgeBroker] = None,
    ingress_adapter: typing.Optional[IAdapter] = None,
    network: typing.Optional[Network] = None,
    removal_policy: typing.Optional[_aws_cdk_ceddda9d.RemovalPolicy] = None,
    workflow_timeout: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7393f9c6b2af93f7d8668b32cec54ba8c77259644ab01f57b3fbd50c78923134(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    classification_model_id: typing.Optional[_aws_cdk_aws_bedrock_ceddda9d.FoundationModelIdentifier] = None,
    classification_prompt: typing.Optional[builtins.str] = None,
    cross_region_inference_prefix: typing.Optional[BedrockCrossRegionInferencePrefix] = None,
    enrichment_lambda_function: typing.Optional[_aws_cdk_aws_lambda_ceddda9d.Function] = None,
    post_processing_lambda_function: typing.Optional[_aws_cdk_aws_lambda_ceddda9d.Function] = None,
    processing_model_id: typing.Optional[_aws_cdk_aws_bedrock_ceddda9d.FoundationModelIdentifier] = None,
    processing_prompt: typing.Optional[builtins.str] = None,
    step_timeouts: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
    use_cross_region_inference: typing.Optional[builtins.bool] = None,
    document_processing_table: typing.Optional[_aws_cdk_aws_dynamodb_ceddda9d.Table] = None,
    enable_observability: typing.Optional[builtins.bool] = None,
    encryption_key: typing.Optional[_aws_cdk_aws_kms_ceddda9d.Key] = None,
    eventbridge_broker: typing.Optional[EventbridgeBroker] = None,
    ingress_adapter: typing.Optional[IAdapter] = None,
    network: typing.Optional[Network] = None,
    removal_policy: typing.Optional[_aws_cdk_ceddda9d.RemovalPolicy] = None,
    workflow_timeout: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
    log_group_data_protection: typing.Optional[typing.Union[LogGroupDataProtectionProps, typing.Dict[builtins.str, typing.Any]]] = None,
    metric_namespace: typing.Optional[builtins.str] = None,
    metric_service_name: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b765dc24cd888585470934e534f4d8e979ddebd46e42601cc8b50c73499e7d4e(
    fm_model: _aws_cdk_aws_bedrock_ceddda9d.FoundationModelIdentifier,
    id: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9606a6418d69bde20176ec33b27eaa22c0e0cdb6b105d382e9d038566f7a29f3(
    *,
    log_group_data_protection: typing.Optional[typing.Union[LogGroupDataProtectionProps, typing.Dict[builtins.str, typing.Any]]] = None,
    metric_namespace: typing.Optional[builtins.str] = None,
    metric_service_name: typing.Optional[builtins.str] = None,
    document_processing_table: typing.Optional[_aws_cdk_aws_dynamodb_ceddda9d.Table] = None,
    enable_observability: typing.Optional[builtins.bool] = None,
    encryption_key: typing.Optional[_aws_cdk_aws_kms_ceddda9d.Key] = None,
    eventbridge_broker: typing.Optional[EventbridgeBroker] = None,
    ingress_adapter: typing.Optional[IAdapter] = None,
    network: typing.Optional[Network] = None,
    removal_policy: typing.Optional[_aws_cdk_ceddda9d.RemovalPolicy] = None,
    workflow_timeout: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
    classification_model_id: typing.Optional[_aws_cdk_aws_bedrock_ceddda9d.FoundationModelIdentifier] = None,
    classification_prompt: typing.Optional[builtins.str] = None,
    cross_region_inference_prefix: typing.Optional[BedrockCrossRegionInferencePrefix] = None,
    enrichment_lambda_function: typing.Optional[_aws_cdk_aws_lambda_ceddda9d.Function] = None,
    post_processing_lambda_function: typing.Optional[_aws_cdk_aws_lambda_ceddda9d.Function] = None,
    processing_model_id: typing.Optional[_aws_cdk_aws_bedrock_ceddda9d.FoundationModelIdentifier] = None,
    processing_prompt: typing.Optional[builtins.str] = None,
    step_timeouts: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
    use_cross_region_inference: typing.Optional[builtins.bool] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b7f396236f637ec7234d81b355cf773497392b537455f3d888c4b7170ceed70a(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    processing_agent_parameters: typing.Optional[typing.Union[AgentProps, typing.Dict[builtins.str, typing.Any]]] = None,
    classification_model_id: typing.Optional[_aws_cdk_aws_bedrock_ceddda9d.FoundationModelIdentifier] = None,
    classification_prompt: typing.Optional[builtins.str] = None,
    cross_region_inference_prefix: typing.Optional[BedrockCrossRegionInferencePrefix] = None,
    enrichment_lambda_function: typing.Optional[_aws_cdk_aws_lambda_ceddda9d.Function] = None,
    post_processing_lambda_function: typing.Optional[_aws_cdk_aws_lambda_ceddda9d.Function] = None,
    processing_model_id: typing.Optional[_aws_cdk_aws_bedrock_ceddda9d.FoundationModelIdentifier] = None,
    processing_prompt: typing.Optional[builtins.str] = None,
    step_timeouts: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
    use_cross_region_inference: typing.Optional[builtins.bool] = None,
    document_processing_table: typing.Optional[_aws_cdk_aws_dynamodb_ceddda9d.Table] = None,
    enable_observability: typing.Optional[builtins.bool] = None,
    encryption_key: typing.Optional[_aws_cdk_aws_kms_ceddda9d.Key] = None,
    eventbridge_broker: typing.Optional[EventbridgeBroker] = None,
    ingress_adapter: typing.Optional[IAdapter] = None,
    network: typing.Optional[Network] = None,
    removal_policy: typing.Optional[_aws_cdk_ceddda9d.RemovalPolicy] = None,
    workflow_timeout: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
    log_group_data_protection: typing.Optional[typing.Union[LogGroupDataProtectionProps, typing.Dict[builtins.str, typing.Any]]] = None,
    metric_namespace: typing.Optional[builtins.str] = None,
    metric_service_name: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__da9ccab0035a06d18b5aa3f2de69201b3bbd6e30f7707a291977a0e4f83a72f4(
    *,
    log_group_data_protection: typing.Optional[typing.Union[LogGroupDataProtectionProps, typing.Dict[builtins.str, typing.Any]]] = None,
    metric_namespace: typing.Optional[builtins.str] = None,
    metric_service_name: typing.Optional[builtins.str] = None,
    document_processing_table: typing.Optional[_aws_cdk_aws_dynamodb_ceddda9d.Table] = None,
    enable_observability: typing.Optional[builtins.bool] = None,
    encryption_key: typing.Optional[_aws_cdk_aws_kms_ceddda9d.Key] = None,
    eventbridge_broker: typing.Optional[EventbridgeBroker] = None,
    ingress_adapter: typing.Optional[IAdapter] = None,
    network: typing.Optional[Network] = None,
    removal_policy: typing.Optional[_aws_cdk_ceddda9d.RemovalPolicy] = None,
    workflow_timeout: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
    classification_model_id: typing.Optional[_aws_cdk_aws_bedrock_ceddda9d.FoundationModelIdentifier] = None,
    classification_prompt: typing.Optional[builtins.str] = None,
    cross_region_inference_prefix: typing.Optional[BedrockCrossRegionInferencePrefix] = None,
    enrichment_lambda_function: typing.Optional[_aws_cdk_aws_lambda_ceddda9d.Function] = None,
    post_processing_lambda_function: typing.Optional[_aws_cdk_aws_lambda_ceddda9d.Function] = None,
    processing_model_id: typing.Optional[_aws_cdk_aws_bedrock_ceddda9d.FoundationModelIdentifier] = None,
    processing_prompt: typing.Optional[builtins.str] = None,
    step_timeouts: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
    use_cross_region_inference: typing.Optional[builtins.bool] = None,
    processing_agent_parameters: typing.Optional[typing.Union[AgentProps, typing.Dict[builtins.str, typing.Any]]] = None,
) -> None:
    """Type checking stubs"""
    pass

for cls in [IAdapter, IObservable]:
    typing.cast(typing.Any, cls).__protocol_attrs__ = typing.cast(typing.Any, cls).__protocol_attrs__ - set(['__jsii_proxy_class__', '__jsii_type__'])
