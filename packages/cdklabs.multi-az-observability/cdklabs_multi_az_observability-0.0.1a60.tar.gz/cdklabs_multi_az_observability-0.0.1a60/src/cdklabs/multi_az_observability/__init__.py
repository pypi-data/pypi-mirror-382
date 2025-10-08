r'''
![Build Workflow](https://github.com/cdklabs/cdk-multi-az-observability/actions/workflows/build.yml/badge.svg) ![Release Workflow](https://github.com/cdklabs/cdk-multi-az-observability/actions/workflows/release.yml/badge.svg) ![GitHub Release](https://img.shields.io/github/v/release/cdklabs/cdk-multi-az-observability?include_prereleases&sort=semver&logo=github&label=version)

# multi-az-observability

This is a CDK construct for multi-AZ observability to help detect single-AZ impairments. This is currently an `alpha` version, but is being used in the AWS [Advanced Multi-AZ Resilience Patterns](https://catalog.workshops.aws/multi-az-gray-failures/en-US) workshop.

There is a lot of available information to think through and combine to provide signals about single-AZ impact. To simplify the setup and use reasonable defaults, this construct (available in [TypeScript](https://www.npmjs.com/package/@cdklabs/multi-az-observability), [Go](https://github.com/cdklabs/cdk-multi-az-observability-go), [Python](https://pypi.org/project/cdklabs.multi-az-observability/), [.NET](https://www.nuget.org/packages/Cdklabs.MultiAZObservability), and [Java](https://central.sonatype.com/artifact/io.github.cdklabs/cdk-multi-az-observability)) sets up the necessary observability. To use the CDK construct, you first define your service like this:

```python
service = Service(
    service_name="test",
    availability_zone_names=vpc.availability_zones,
    base_url="http://www.example.com",
    fault_count_threshold=25,
    period=Duration.seconds(60),
    load_balancer=load_balancer,
    target_groups=[target_group1, target_group2],
    default_availability_metric_details=ServiceAvailabilityMetricDetails(
        metric_namespace="front-end/metrics",
        success_metric_names=["Success"],
        fault_metric_names=["Fault", "Error"],
        alarm_statistic="Sum",
        unit=Unit.COUNT,
        period=Duration.seconds(60),
        evaluation_periods=5,
        datapoints_to_alarm=3,
        success_alarm_threshold=99.9,
        fault_alarm_threshold=0.1,
        graphed_fault_statistics=["Sum"],
        graphed_success_statistics=["Sum"]
    ),
    default_latency_metric_details=ServiceLatencyMetricDetails(
        metric_namespace="front-end/metrics",
        success_metric_names=["SuccessLatency"],
        fault_metric_names=["FaultLatency"],
        alarm_statistic="p99",
        unit=Unit.MILLISECONDS,
        period=Duration.seconds(60),
        evaluation_periods=5,
        datapoints_to_alarm=3,
        success_alarm_threshold=Duration.millis(150),
        graphed_fault_statistics=["p99"],
        graphed_success_statistics=["p50", "p99", "tm99"]
    ),
    default_contributor_insight_rule_details=ContributorInsightRuleDetails(
        success_latency_metric_json_path="$.SuccessLatency",
        fault_metric_json_path="$.Faults",
        operation_name_json_path="$.Operation",
        instance_id_json_path="$.InstanceId",
        availability_zone_id_json_path="$.AZ-ID",
        log_groups=[log_group]
    ),
    canary_test_props=AddCanaryTestProps(
        request_count=10,
        schedule="rate(1 minute)",
        load_balancer=load_balancer,
        network_configuration=NetworkConfigurationProps(
            vpc=vpc,
            subnet_selection=SubnetSelection(subnet_type=SubnetType.PRIVATE_ISOLATED)
        )
    ),
    minimum_unhealthy_targets=MinimumUnhealthyTargets(
        percentage=0.1
    )
)

ride_operation = {
    "operation_name": "ride",
    "service": service,
    "path": "/ride",
    "critical": True,
    "http_methods": ["GET"],
    "server_side_contributor_insight_rule_details": ContributorInsightRuleDetails(
        log_groups=[log_group],
        success_latency_metric_json_path="$.SuccessLatency",
        fault_metric_json_path="$.Faults",
        operation_name_json_path="$.Operation",
        instance_id_json_path="$.InstanceId",
        availability_zone_id_json_path="$.AZ-ID"
    ),
    "server_side_availability_metric_details": OperationAvailabilityMetricDetails(OperationAvailabilityMetricDetailsProps(
        operation_name="ride",
        metric_dimensions=MetricDimensions({"Operation": "ride"}, "AZ-ID", "Region")
    ), service.default_availability_metric_details),
    "server_side_latency_metric_details": OperationLatencyMetricDetails(OperationLatencyMetricDetailsProps(
        operation_name="ride",
        metric_dimensions=MetricDimensions({"Operation": "ride"}, "AZ-ID", "Region")
    ), service.default_latency_metric_details)
}

pay_operation = {
    "operation_name": "pay",
    "service": service,
    "path": "/pay",
    "critical": True,
    "http_methods": ["GET"],
    "server_side_contributor_insight_rule_details": ContributorInsightRuleDetails(
        log_groups=[log_group],
        success_latency_metric_json_path="$.SuccessLatency",
        fault_metric_json_path="$.Faults",
        operation_name_json_path="$.Operation",
        instance_id_json_path="$.InstanceId",
        availability_zone_id_json_path="$.AZ-ID"
    ),
    "server_side_availability_metric_details": OperationAvailabilityMetricDetails(OperationAvailabilityMetricDetailsProps(
        operation_name="pay",
        metric_dimensions=MetricDimensions({"Operation": "ride"}, "AZ-ID", "Region")
    ), service.default_availability_metric_details),
    "server_side_latency_metric_details": OperationLatencyMetricDetails(OperationLatencyMetricDetailsProps(
        operation_name="pay",
        metric_dimensions=MetricDimensions({"Operation": "ride"}, "AZ-ID", "Region")
    ), service.default_latency_metric_details)
}

service.add_operation(ride_operation)
service.add_operation(pay_operation)
```

Then you provide that service definition to the CDK construct.

```python
InstrumentedServiceMultiAZObservability(stack, "MAZObservability",
    create_dashboards=True,
    service=service,
    interval=Duration.minutes(60)
)
```

You define some characteristics of the service, default values for metrics and alarms, and then add operations as well as any overrides for default values that you need. The construct can also automatically create synthetic canaries that test each operation with a very simple HTTP check, or you can configure your own synthetics and just tell the construct about the metric details and optionally log files. This creates metrics, alarms, and dashboards that can be used to detect single-AZ impact. You can access these alarms from the `multiAvailabilityZoneObservability` object and use them in your CDK project to start automation, send SNS notifications, or incorporate in your own dashboards.

If you don't have service specific logs and custom metrics with per-AZ dimensions, you can still use the construct to evaluate ALB and/or NAT Gateway metrics to find single AZ impairments.

```python
BasicServiceMultiAZObservability(stack, "MAZObservability",
    application_load_balancer_props=ApplicationLoadBalancerDetectionProps(
        alb_target_group_map=[AlbTargetGroupMap(
            application_load_balancer=ApplicationLoadBalancer(stack, "alb",
                vpc=vpc,
                cross_zone_enabled=True
            ),
            target_groups=[target_group1, target_group2
            ]
        )
        ],
        fault_count_percent_threshold=1,
        latency_statistic=Stats.percentile(99),
        latency_threshold=Duration.millis(200),
        latency_outlier_algorithm=ApplicationLoadBalancerLatencyOutlierAlgorithm.STATIC,
        latency_outlier_threshold=45
    ),
    nat_gateway_props=NatGatewayDetectionProps(
        nat_gateways={
            "us-east-1a": [nat_gateway1],
            "us-east-1b": [nat_gateway2],
            "us-east-1c": [nat_gateway3]
        },
        packet_loss_percent_threshold=0.01
    ),
    service_name="test",
    period=Duration.seconds(60),
    create_dashboard=True,
    evaluation_periods=5,
    datapoints_to_alarm=3
)
```

If you provide a load balancer, the construct assumes it is deployed in each AZ of the VPC the load balancer is associated with and will look for HTTP metrics using those AZs as dimensions.

Both options support running workloads on EC2, ECS, Lambda, and EKS.
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
import aws_cdk.aws_cloudwatch as _aws_cdk_aws_cloudwatch_ceddda9d
import aws_cdk.aws_ec2 as _aws_cdk_aws_ec2_ceddda9d
import aws_cdk.aws_elasticloadbalancingv2 as _aws_cdk_aws_elasticloadbalancingv2_ceddda9d
import aws_cdk.aws_lambda as _aws_cdk_aws_lambda_ceddda9d
import aws_cdk.aws_logs as _aws_cdk_aws_logs_ceddda9d
import constructs as _constructs_77d1e7e8


@jsii.data_type(
    jsii_type="@cdklabs/multi-az-observability.AddCanaryTestProps",
    jsii_struct_bases=[],
    name_mapping={
        "load_balancer": "loadBalancer",
        "request_count": "requestCount",
        "schedule": "schedule",
        "headers": "headers",
        "http_methods": "httpMethods",
        "ignore_tls_errors": "ignoreTlsErrors",
        "network_configuration": "networkConfiguration",
        "post_data": "postData",
        "regional_request_count": "regionalRequestCount",
        "timeout": "timeout",
    },
)
class AddCanaryTestProps:
    def __init__(
        self,
        *,
        load_balancer: _aws_cdk_aws_elasticloadbalancingv2_ceddda9d.ILoadBalancerV2,
        request_count: jsii.Number,
        schedule: builtins.str,
        headers: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        http_methods: typing.Optional[typing.Sequence[builtins.str]] = None,
        ignore_tls_errors: typing.Optional[builtins.bool] = None,
        network_configuration: typing.Optional[typing.Union["NetworkConfigurationProps", typing.Dict[builtins.str, typing.Any]]] = None,
        post_data: typing.Optional[builtins.str] = None,
        regional_request_count: typing.Optional[jsii.Number] = None,
        timeout: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
    ) -> None:
        '''(experimental) The props for requesting a canary be made for an operation.

        :param load_balancer: (experimental) The load balancer that will be tested against.
        :param request_count: (experimental) The number of requests to send on each test.
        :param schedule: (experimental) A schedule expression.
        :param headers: (experimental) Any headers to include. Default: - No additional headers are added to the requests
        :param http_methods: (experimental) Defining this will override the methods defined in the operation and will use these instead. Default: - The operation's defined HTTP methods will be used to conduct the canary tests
        :param ignore_tls_errors: (experimental) Whether to ignore TLS validation errors. Default: - false
        :param network_configuration: (experimental) The VPC network configuration. Default: - The Lambda function is not run in a VPC
        :param post_data: (experimental) Data to supply in a POST, PUT, or PATCH operation. Default: - No data is sent in a POST, PUT, or PATCH request
        :param regional_request_count: (experimental) Specifies a separate number of request to send to the regional endpoint. Default: - The same number of requests specified by the requestCount property is used.
        :param timeout: (experimental) The timeout for each individual HTTP request. Default: - Defaults to 2 seconds

        :stability: experimental
        '''
        if isinstance(network_configuration, dict):
            network_configuration = NetworkConfigurationProps(**network_configuration)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__bf7e5362f1ef3a0356b1522d870175b4a00fdf064367124f0e428e97b327a615)
            check_type(argname="argument load_balancer", value=load_balancer, expected_type=type_hints["load_balancer"])
            check_type(argname="argument request_count", value=request_count, expected_type=type_hints["request_count"])
            check_type(argname="argument schedule", value=schedule, expected_type=type_hints["schedule"])
            check_type(argname="argument headers", value=headers, expected_type=type_hints["headers"])
            check_type(argname="argument http_methods", value=http_methods, expected_type=type_hints["http_methods"])
            check_type(argname="argument ignore_tls_errors", value=ignore_tls_errors, expected_type=type_hints["ignore_tls_errors"])
            check_type(argname="argument network_configuration", value=network_configuration, expected_type=type_hints["network_configuration"])
            check_type(argname="argument post_data", value=post_data, expected_type=type_hints["post_data"])
            check_type(argname="argument regional_request_count", value=regional_request_count, expected_type=type_hints["regional_request_count"])
            check_type(argname="argument timeout", value=timeout, expected_type=type_hints["timeout"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "load_balancer": load_balancer,
            "request_count": request_count,
            "schedule": schedule,
        }
        if headers is not None:
            self._values["headers"] = headers
        if http_methods is not None:
            self._values["http_methods"] = http_methods
        if ignore_tls_errors is not None:
            self._values["ignore_tls_errors"] = ignore_tls_errors
        if network_configuration is not None:
            self._values["network_configuration"] = network_configuration
        if post_data is not None:
            self._values["post_data"] = post_data
        if regional_request_count is not None:
            self._values["regional_request_count"] = regional_request_count
        if timeout is not None:
            self._values["timeout"] = timeout

    @builtins.property
    def load_balancer(
        self,
    ) -> _aws_cdk_aws_elasticloadbalancingv2_ceddda9d.ILoadBalancerV2:
        '''(experimental) The load balancer that will be tested against.

        :stability: experimental
        '''
        result = self._values.get("load_balancer")
        assert result is not None, "Required property 'load_balancer' is missing"
        return typing.cast(_aws_cdk_aws_elasticloadbalancingv2_ceddda9d.ILoadBalancerV2, result)

    @builtins.property
    def request_count(self) -> jsii.Number:
        '''(experimental) The number of requests to send on each test.

        :stability: experimental
        '''
        result = self._values.get("request_count")
        assert result is not None, "Required property 'request_count' is missing"
        return typing.cast(jsii.Number, result)

    @builtins.property
    def schedule(self) -> builtins.str:
        '''(experimental) A schedule expression.

        :stability: experimental
        '''
        result = self._values.get("schedule")
        assert result is not None, "Required property 'schedule' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def headers(self) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        '''(experimental) Any headers to include.

        :default: - No additional headers are added to the requests

        :stability: experimental
        '''
        result = self._values.get("headers")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], result)

    @builtins.property
    def http_methods(self) -> typing.Optional[typing.List[builtins.str]]:
        '''(experimental) Defining this will override the methods defined in the operation and will use these instead.

        :default:

        - The operation's defined HTTP methods will be used to
        conduct the canary tests

        :stability: experimental
        '''
        result = self._values.get("http_methods")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def ignore_tls_errors(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Whether to ignore TLS validation errors.

        :default: - false

        :stability: experimental
        '''
        result = self._values.get("ignore_tls_errors")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def network_configuration(self) -> typing.Optional["NetworkConfigurationProps"]:
        '''(experimental) The VPC network configuration.

        :default: - The Lambda function is not run in a VPC

        :stability: experimental
        '''
        result = self._values.get("network_configuration")
        return typing.cast(typing.Optional["NetworkConfigurationProps"], result)

    @builtins.property
    def post_data(self) -> typing.Optional[builtins.str]:
        '''(experimental) Data to supply in a POST, PUT, or PATCH operation.

        :default: - No data is sent in a POST, PUT, or PATCH request

        :stability: experimental
        '''
        result = self._values.get("post_data")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def regional_request_count(self) -> typing.Optional[jsii.Number]:
        '''(experimental) Specifies a separate number of request to send to the regional endpoint.

        :default: - The same number of requests specified by the requestCount property is used.

        :stability: experimental
        '''
        result = self._values.get("regional_request_count")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def timeout(self) -> typing.Optional[_aws_cdk_ceddda9d.Duration]:
        '''(experimental) The timeout for each individual HTTP request.

        :default: - Defaults to 2 seconds

        :stability: experimental
        '''
        result = self._values.get("timeout")
        return typing.cast(typing.Optional[_aws_cdk_ceddda9d.Duration], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "AddCanaryTestProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdklabs/multi-az-observability.AlbTargetGroupMap",
    jsii_struct_bases=[],
    name_mapping={
        "application_load_balancer": "applicationLoadBalancer",
        "target_groups": "targetGroups",
    },
)
class AlbTargetGroupMap:
    def __init__(
        self,
        *,
        application_load_balancer: _aws_cdk_aws_elasticloadbalancingv2_ceddda9d.IApplicationLoadBalancer,
        target_groups: typing.Optional[typing.Sequence[_aws_cdk_aws_elasticloadbalancingv2_ceddda9d.ITargetGroup]] = None,
    ) -> None:
        '''(experimental) An object to map an ALB to its target groups.

        :param application_load_balancer: (experimental) The application load balancer.
        :param target_groups: (experimental) The target groups associated with the ALB. Default: No target groups are associated and will not display anomalous hosts or mitigated hosts on the dashboard

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1c82768e8378134f3b690a00f3e494e9e4e09034637d03093bba5aab2f56095e)
            check_type(argname="argument application_load_balancer", value=application_load_balancer, expected_type=type_hints["application_load_balancer"])
            check_type(argname="argument target_groups", value=target_groups, expected_type=type_hints["target_groups"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "application_load_balancer": application_load_balancer,
        }
        if target_groups is not None:
            self._values["target_groups"] = target_groups

    @builtins.property
    def application_load_balancer(
        self,
    ) -> _aws_cdk_aws_elasticloadbalancingv2_ceddda9d.IApplicationLoadBalancer:
        '''(experimental) The application load balancer.

        :stability: experimental
        '''
        result = self._values.get("application_load_balancer")
        assert result is not None, "Required property 'application_load_balancer' is missing"
        return typing.cast(_aws_cdk_aws_elasticloadbalancingv2_ceddda9d.IApplicationLoadBalancer, result)

    @builtins.property
    def target_groups(
        self,
    ) -> typing.Optional[typing.List[_aws_cdk_aws_elasticloadbalancingv2_ceddda9d.ITargetGroup]]:
        '''(experimental) The target groups associated with the ALB.

        :default: No target groups are associated and will not display anomalous hosts or mitigated hosts on the dashboard

        :stability: experimental
        '''
        result = self._values.get("target_groups")
        return typing.cast(typing.Optional[typing.List[_aws_cdk_aws_elasticloadbalancingv2_ceddda9d.ITargetGroup]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "AlbTargetGroupMap(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.enum(
    jsii_type="@cdklabs/multi-az-observability.ApplicationLoadBalancerAvailabilityOutlierAlgorithm"
)
class ApplicationLoadBalancerAvailabilityOutlierAlgorithm(enum.Enum):
    '''(experimental) The options for calculating if an ALB is an outlier for availability.

    :stability: experimental
    '''

    STATIC = "STATIC"
    '''(experimental) This will take the availability threshold and calculate if one AZ is responsible for that percentage of errors.

    :stability: experimental
    '''


@jsii.data_type(
    jsii_type="@cdklabs/multi-az-observability.ApplicationLoadBalancerDetectionProps",
    jsii_struct_bases=[],
    name_mapping={
        "alb_target_group_map": "albTargetGroupMap",
        "fault_count_percent_threshold": "faultCountPercentThreshold",
        "latency_statistic": "latencyStatistic",
        "latency_threshold": "latencyThreshold",
        "availability_outlier_algorithm": "availabilityOutlierAlgorithm",
        "availability_outlier_threshold": "availabilityOutlierThreshold",
        "latency_outlier_algorithm": "latencyOutlierAlgorithm",
        "latency_outlier_threshold": "latencyOutlierThreshold",
    },
)
class ApplicationLoadBalancerDetectionProps:
    def __init__(
        self,
        *,
        alb_target_group_map: typing.Sequence[typing.Union[AlbTargetGroupMap, typing.Dict[builtins.str, typing.Any]]],
        fault_count_percent_threshold: jsii.Number,
        latency_statistic: builtins.str,
        latency_threshold: _aws_cdk_ceddda9d.Duration,
        availability_outlier_algorithm: typing.Optional[ApplicationLoadBalancerAvailabilityOutlierAlgorithm] = None,
        availability_outlier_threshold: typing.Optional[jsii.Number] = None,
        latency_outlier_algorithm: typing.Optional["ApplicationLoadBalancerLatencyOutlierAlgorithm"] = None,
        latency_outlier_threshold: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''(experimental) The properties for performing zonal impact detection with ALB(s).

        :param alb_target_group_map: (experimental) Map of target groups per ALB to collect metrics from.
        :param fault_count_percent_threshold: (experimental) The percentage of faults for a single ALB to consider an AZ to be unhealthy, a number between 0 and 100. This should align with your availability goal. For example 1% or 5%, provided as 1 or 5.
        :param latency_statistic: (experimental) The statistic used to measure target response latency, like p99, which can be specified using Stats.percentile(99) or "p99".
        :param latency_threshold: (experimental) The threshold in milliseconds for ALB targets whose responses are slower than this value at the specified percentile statistic.
        :param availability_outlier_algorithm: (experimental) The method used to determine if an AZ is an outlier for availability for Application Load Balancer metrics. Default: STATIC
        :param availability_outlier_threshold: (experimental) The threshold for the outlier detection algorithm. Default: "This depends on the algorithm used. STATIC: 66"
        :param latency_outlier_algorithm: (experimental) The method used to determine if an AZ is an outlier for latency for Application Load Balancer metrics. Default: Z_SCORE
        :param latency_outlier_threshold: (experimental) The threshold for the outlier detection algorithm. Default: "This depends on the algorithm used. STATIC: 66. Z_SCORE: 3."

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a93214bdf1fa4f67b237e7c4dcee5992506d690b196458bab06cd4a8e25eee03)
            check_type(argname="argument alb_target_group_map", value=alb_target_group_map, expected_type=type_hints["alb_target_group_map"])
            check_type(argname="argument fault_count_percent_threshold", value=fault_count_percent_threshold, expected_type=type_hints["fault_count_percent_threshold"])
            check_type(argname="argument latency_statistic", value=latency_statistic, expected_type=type_hints["latency_statistic"])
            check_type(argname="argument latency_threshold", value=latency_threshold, expected_type=type_hints["latency_threshold"])
            check_type(argname="argument availability_outlier_algorithm", value=availability_outlier_algorithm, expected_type=type_hints["availability_outlier_algorithm"])
            check_type(argname="argument availability_outlier_threshold", value=availability_outlier_threshold, expected_type=type_hints["availability_outlier_threshold"])
            check_type(argname="argument latency_outlier_algorithm", value=latency_outlier_algorithm, expected_type=type_hints["latency_outlier_algorithm"])
            check_type(argname="argument latency_outlier_threshold", value=latency_outlier_threshold, expected_type=type_hints["latency_outlier_threshold"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "alb_target_group_map": alb_target_group_map,
            "fault_count_percent_threshold": fault_count_percent_threshold,
            "latency_statistic": latency_statistic,
            "latency_threshold": latency_threshold,
        }
        if availability_outlier_algorithm is not None:
            self._values["availability_outlier_algorithm"] = availability_outlier_algorithm
        if availability_outlier_threshold is not None:
            self._values["availability_outlier_threshold"] = availability_outlier_threshold
        if latency_outlier_algorithm is not None:
            self._values["latency_outlier_algorithm"] = latency_outlier_algorithm
        if latency_outlier_threshold is not None:
            self._values["latency_outlier_threshold"] = latency_outlier_threshold

    @builtins.property
    def alb_target_group_map(self) -> typing.List[AlbTargetGroupMap]:
        '''(experimental) Map of target groups per ALB to collect metrics from.

        :stability: experimental
        '''
        result = self._values.get("alb_target_group_map")
        assert result is not None, "Required property 'alb_target_group_map' is missing"
        return typing.cast(typing.List[AlbTargetGroupMap], result)

    @builtins.property
    def fault_count_percent_threshold(self) -> jsii.Number:
        '''(experimental) The percentage of faults for a single ALB to consider an AZ to be unhealthy, a number between 0 and 100.

        This should align with your availability goal. For example
        1% or 5%, provided as 1 or 5.

        :stability: experimental
        '''
        result = self._values.get("fault_count_percent_threshold")
        assert result is not None, "Required property 'fault_count_percent_threshold' is missing"
        return typing.cast(jsii.Number, result)

    @builtins.property
    def latency_statistic(self) -> builtins.str:
        '''(experimental) The statistic used to measure target response latency, like p99,  which can be specified using Stats.percentile(99) or "p99".

        :stability: experimental
        '''
        result = self._values.get("latency_statistic")
        assert result is not None, "Required property 'latency_statistic' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def latency_threshold(self) -> _aws_cdk_ceddda9d.Duration:
        '''(experimental) The threshold in milliseconds for ALB targets whose responses are slower than this value at the specified percentile statistic.

        :stability: experimental
        '''
        result = self._values.get("latency_threshold")
        assert result is not None, "Required property 'latency_threshold' is missing"
        return typing.cast(_aws_cdk_ceddda9d.Duration, result)

    @builtins.property
    def availability_outlier_algorithm(
        self,
    ) -> typing.Optional[ApplicationLoadBalancerAvailabilityOutlierAlgorithm]:
        '''(experimental) The method used to determine if an AZ is an outlier for availability for Application Load Balancer metrics.

        :default: STATIC

        :stability: experimental
        '''
        result = self._values.get("availability_outlier_algorithm")
        return typing.cast(typing.Optional[ApplicationLoadBalancerAvailabilityOutlierAlgorithm], result)

    @builtins.property
    def availability_outlier_threshold(self) -> typing.Optional[jsii.Number]:
        '''(experimental) The threshold for the outlier detection algorithm.

        :default: "This depends on the algorithm used. STATIC: 66"

        :stability: experimental
        '''
        result = self._values.get("availability_outlier_threshold")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def latency_outlier_algorithm(
        self,
    ) -> typing.Optional["ApplicationLoadBalancerLatencyOutlierAlgorithm"]:
        '''(experimental) The method used to determine if an AZ is an outlier for latency for Application Load Balancer metrics.

        :default: Z_SCORE

        :stability: experimental
        '''
        result = self._values.get("latency_outlier_algorithm")
        return typing.cast(typing.Optional["ApplicationLoadBalancerLatencyOutlierAlgorithm"], result)

    @builtins.property
    def latency_outlier_threshold(self) -> typing.Optional[jsii.Number]:
        '''(experimental) The threshold for the outlier detection algorithm.

        :default: "This depends on the algorithm used. STATIC: 66. Z_SCORE: 3."

        :stability: experimental
        '''
        result = self._values.get("latency_outlier_threshold")
        return typing.cast(typing.Optional[jsii.Number], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ApplicationLoadBalancerDetectionProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.enum(
    jsii_type="@cdklabs/multi-az-observability.ApplicationLoadBalancerLatencyOutlierAlgorithm"
)
class ApplicationLoadBalancerLatencyOutlierAlgorithm(enum.Enum):
    '''(experimental) The options for calculating if an AZ is an outlier for latency for ALBs.

    :stability: experimental
    '''

    STATIC = "STATIC"
    '''(experimental) This will take the latency threshold and count the number of requests per AZ  that exceed this threshold and then calculate the percentage of requests exceeding this threshold belong to each AZ.

    This provides a static comparison
    of the number of high latency requests in one AZ versus the others

    :stability: experimental
    '''
    Z_SCORE = "Z_SCORE"
    '''(experimental) This calculates the z score of latency in one AZ against the other AZs.

    It uses
    the target response time of all requests to calculate the standard deviation and
    average for all AZs. This is the default.

    :stability: experimental
    '''


@jsii.data_type(
    jsii_type="@cdklabs/multi-az-observability.AvailabilityZoneMapperProps",
    jsii_struct_bases=[],
    name_mapping={"availability_zone_names": "availabilityZoneNames"},
)
class AvailabilityZoneMapperProps:
    def __init__(
        self,
        *,
        availability_zone_names: typing.Optional[typing.Sequence[builtins.str]] = None,
    ) -> None:
        '''(experimental) Properties for the AZ mapper.

        :param availability_zone_names: (experimental) The currently in use Availability Zone names which constrains the list of AZ IDs that are returned. Default: - No names are provided and the mapper returns all AZs in the region in its lists

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ad282df04042aad52125b287dc88af7a6decbd51da905d665c2df5a7ae36a858)
            check_type(argname="argument availability_zone_names", value=availability_zone_names, expected_type=type_hints["availability_zone_names"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if availability_zone_names is not None:
            self._values["availability_zone_names"] = availability_zone_names

    @builtins.property
    def availability_zone_names(self) -> typing.Optional[typing.List[builtins.str]]:
        '''(experimental) The currently in use Availability Zone names which constrains the list of AZ IDs that are returned.

        :default:

        - No names are provided and the mapper returns
        all AZs in the region in its lists

        :stability: experimental
        '''
        result = self._values.get("availability_zone_names")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "AvailabilityZoneMapperProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdklabs/multi-az-observability.BasicServiceMultiAZObservabilityProps",
    jsii_struct_bases=[],
    name_mapping={
        "datapoints_to_alarm": "datapointsToAlarm",
        "evaluation_periods": "evaluationPeriods",
        "service_name": "serviceName",
        "application_load_balancer_props": "applicationLoadBalancerProps",
        "assets_bucket_parameter_name": "assetsBucketParameterName",
        "assets_bucket_prefix_parameter_name": "assetsBucketPrefixParameterName",
        "create_dashboard": "createDashboard",
        "interval": "interval",
        "nat_gateway_props": "natGatewayProps",
        "period": "period",
    },
)
class BasicServiceMultiAZObservabilityProps:
    def __init__(
        self,
        *,
        datapoints_to_alarm: jsii.Number,
        evaluation_periods: jsii.Number,
        service_name: builtins.str,
        application_load_balancer_props: typing.Optional[typing.Union[ApplicationLoadBalancerDetectionProps, typing.Dict[builtins.str, typing.Any]]] = None,
        assets_bucket_parameter_name: typing.Optional[builtins.str] = None,
        assets_bucket_prefix_parameter_name: typing.Optional[builtins.str] = None,
        create_dashboard: typing.Optional[builtins.bool] = None,
        interval: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
        nat_gateway_props: typing.Optional[typing.Union["NatGatewayDetectionProps", typing.Dict[builtins.str, typing.Any]]] = None,
        period: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
    ) -> None:
        '''(experimental) Properties for creating basic multi-AZ observability.

        :param datapoints_to_alarm: (experimental) The number of datapoints to alarm on for latency and availability alarms.
        :param evaluation_periods: (experimental) The number of evaluation periods for latency and availabiltiy alarms.
        :param service_name: (experimental) The service's name.
        :param application_load_balancer_props: (experimental) Properties for ALBs to detect single AZ impact. You must specify this and/or natGatewayProps. Default: "No ALBs will be used to calculate impact."
        :param assets_bucket_parameter_name: (experimental) If you are not using a static bucket to deploy assets, for example you are synthing this and it gets uploaded to a bucket whose name is unknown to you (maybe used as part of a central CI/CD system) and is provided as a parameter to your stack, specify that parameter name here. It will override the bucket location CDK provides by default for bundled assets. The stack containing this contruct needs to have a parameter defined that uses this name. The underlying stacks in this construct that deploy assets will copy the parent stack's value for this property. Default: "The assets will be uploaded to the default defined asset location."
        :param assets_bucket_prefix_parameter_name: (experimental) If you are not using a static bucket to deploy assets, for example you are synthing this and it gets uploaded to a bucket that uses a prefix that is unknown to you (maybe used as part of a central CI/CD system) and is provided as a parameter to your stack, specify that parameter name here. It will override the bucket prefix CDK provides by default for bundled assets. This property only takes effect if you defined the assetsBucketParameterName. The stack containing this contruct needs to have a parameter defined that uses this name. The underlying stacks in this construct that deploy assets will copy the parent stack's value for this property. Default: "No object prefix will be added to your custom assets location. However, if you have overridden something like the 'BucketPrefix' property in your stack synthesizer with a variable like '${AssetsBucketPrefix}', you will need to define this property so it doesn't cause a reference error even if the prefix value is blank."
        :param create_dashboard: (experimental) Whether to create a dashboard displaying the metrics and alarms. Default: false
        :param interval: (experimental) Dashboard interval. Default: Duration.hours(1)
        :param nat_gateway_props: (experimental) Properties for NAT Gateways to detect single AZ impact. You must specify this and/or applicationLoadBalancerProps. Default: "No NAT Gateways will be used to calculate impact."
        :param period: (experimental) The period to evaluate metrics. Default: Duration.minutes(1)

        :stability: experimental
        '''
        if isinstance(application_load_balancer_props, dict):
            application_load_balancer_props = ApplicationLoadBalancerDetectionProps(**application_load_balancer_props)
        if isinstance(nat_gateway_props, dict):
            nat_gateway_props = NatGatewayDetectionProps(**nat_gateway_props)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__15fe53f0a5b438d27e745fab2f0c65f95e2f6f1d3d09af30af5c2f7f34fc3333)
            check_type(argname="argument datapoints_to_alarm", value=datapoints_to_alarm, expected_type=type_hints["datapoints_to_alarm"])
            check_type(argname="argument evaluation_periods", value=evaluation_periods, expected_type=type_hints["evaluation_periods"])
            check_type(argname="argument service_name", value=service_name, expected_type=type_hints["service_name"])
            check_type(argname="argument application_load_balancer_props", value=application_load_balancer_props, expected_type=type_hints["application_load_balancer_props"])
            check_type(argname="argument assets_bucket_parameter_name", value=assets_bucket_parameter_name, expected_type=type_hints["assets_bucket_parameter_name"])
            check_type(argname="argument assets_bucket_prefix_parameter_name", value=assets_bucket_prefix_parameter_name, expected_type=type_hints["assets_bucket_prefix_parameter_name"])
            check_type(argname="argument create_dashboard", value=create_dashboard, expected_type=type_hints["create_dashboard"])
            check_type(argname="argument interval", value=interval, expected_type=type_hints["interval"])
            check_type(argname="argument nat_gateway_props", value=nat_gateway_props, expected_type=type_hints["nat_gateway_props"])
            check_type(argname="argument period", value=period, expected_type=type_hints["period"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "datapoints_to_alarm": datapoints_to_alarm,
            "evaluation_periods": evaluation_periods,
            "service_name": service_name,
        }
        if application_load_balancer_props is not None:
            self._values["application_load_balancer_props"] = application_load_balancer_props
        if assets_bucket_parameter_name is not None:
            self._values["assets_bucket_parameter_name"] = assets_bucket_parameter_name
        if assets_bucket_prefix_parameter_name is not None:
            self._values["assets_bucket_prefix_parameter_name"] = assets_bucket_prefix_parameter_name
        if create_dashboard is not None:
            self._values["create_dashboard"] = create_dashboard
        if interval is not None:
            self._values["interval"] = interval
        if nat_gateway_props is not None:
            self._values["nat_gateway_props"] = nat_gateway_props
        if period is not None:
            self._values["period"] = period

    @builtins.property
    def datapoints_to_alarm(self) -> jsii.Number:
        '''(experimental) The number of datapoints to alarm on for latency and availability alarms.

        :stability: experimental
        '''
        result = self._values.get("datapoints_to_alarm")
        assert result is not None, "Required property 'datapoints_to_alarm' is missing"
        return typing.cast(jsii.Number, result)

    @builtins.property
    def evaluation_periods(self) -> jsii.Number:
        '''(experimental) The number of evaluation periods for latency and availabiltiy alarms.

        :stability: experimental
        '''
        result = self._values.get("evaluation_periods")
        assert result is not None, "Required property 'evaluation_periods' is missing"
        return typing.cast(jsii.Number, result)

    @builtins.property
    def service_name(self) -> builtins.str:
        '''(experimental) The service's name.

        :stability: experimental
        '''
        result = self._values.get("service_name")
        assert result is not None, "Required property 'service_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def application_load_balancer_props(
        self,
    ) -> typing.Optional[ApplicationLoadBalancerDetectionProps]:
        '''(experimental) Properties for ALBs to detect single AZ impact.

        You must specify this
        and/or natGatewayProps.

        :default: "No ALBs will be used to calculate impact."

        :stability: experimental
        '''
        result = self._values.get("application_load_balancer_props")
        return typing.cast(typing.Optional[ApplicationLoadBalancerDetectionProps], result)

    @builtins.property
    def assets_bucket_parameter_name(self) -> typing.Optional[builtins.str]:
        '''(experimental) If you are not using a static bucket to deploy assets, for example you are synthing this and it gets uploaded to a bucket whose name is unknown to you (maybe used as part of a central CI/CD system) and is provided as a parameter to your stack, specify that parameter name here.

        It will override the bucket location CDK provides by
        default for bundled assets. The stack containing this contruct needs
        to have a parameter defined that uses this name. The underlying
        stacks in this construct that deploy assets will copy the parent stack's
        value for this property.

        :default: "The assets will be uploaded to the default defined asset location."

        :stability: experimental
        '''
        result = self._values.get("assets_bucket_parameter_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def assets_bucket_prefix_parameter_name(self) -> typing.Optional[builtins.str]:
        '''(experimental) If you are not using a static bucket to deploy assets, for example you are synthing this and it gets uploaded to a bucket that uses a prefix that is unknown to you (maybe used as part of a central CI/CD system) and is provided as a parameter to your stack, specify that parameter name here.

        It will override the bucket prefix CDK provides by
        default for bundled assets. This property only takes effect if you
        defined the assetsBucketParameterName. The stack containing this contruct needs
        to have a parameter defined that uses this name. The underlying
        stacks in this construct that deploy assets will copy the parent stack's
        value for this property.

        :default: "No object prefix will be added to your custom assets location. However, if you have overridden something like the 'BucketPrefix' property in your stack synthesizer with a variable like '${AssetsBucketPrefix}', you will need to define this property so it doesn't cause a reference error even if the prefix value is blank."

        :stability: experimental
        '''
        result = self._values.get("assets_bucket_prefix_parameter_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def create_dashboard(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Whether to create a dashboard displaying the metrics and alarms.

        :default: false

        :stability: experimental
        '''
        result = self._values.get("create_dashboard")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def interval(self) -> typing.Optional[_aws_cdk_ceddda9d.Duration]:
        '''(experimental) Dashboard interval.

        :default: Duration.hours(1)

        :stability: experimental
        '''
        result = self._values.get("interval")
        return typing.cast(typing.Optional[_aws_cdk_ceddda9d.Duration], result)

    @builtins.property
    def nat_gateway_props(self) -> typing.Optional["NatGatewayDetectionProps"]:
        '''(experimental) Properties for NAT Gateways to detect single AZ impact.

        You must specify
        this and/or applicationLoadBalancerProps.

        :default: "No NAT Gateways will be used to calculate impact."

        :stability: experimental
        '''
        result = self._values.get("nat_gateway_props")
        return typing.cast(typing.Optional["NatGatewayDetectionProps"], result)

    @builtins.property
    def period(self) -> typing.Optional[_aws_cdk_ceddda9d.Duration]:
        '''(experimental) The period to evaluate metrics.

        :default: Duration.minutes(1)

        :stability: experimental
        '''
        result = self._values.get("period")
        return typing.cast(typing.Optional[_aws_cdk_ceddda9d.Duration], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "BasicServiceMultiAZObservabilityProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdklabs/multi-az-observability.CanaryMetricProps",
    jsii_struct_bases=[],
    name_mapping={
        "canary_availability_metric_details": "canaryAvailabilityMetricDetails",
        "canary_latency_metric_details": "canaryLatencyMetricDetails",
    },
)
class CanaryMetricProps:
    def __init__(
        self,
        *,
        canary_availability_metric_details: "IOperationAvailabilityMetricDetails",
        canary_latency_metric_details: "IOperationLatencyMetricDetails",
    ) -> None:
        '''(experimental) Properties for canary metrics in an operation.

        :param canary_availability_metric_details: (experimental) The canary availability metric details.
        :param canary_latency_metric_details: (experimental) The canary latency metric details.

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__edbe0cdfc777c1880327eb370e72788956edc4a92cd2a9ce3793a8ce03d372e3)
            check_type(argname="argument canary_availability_metric_details", value=canary_availability_metric_details, expected_type=type_hints["canary_availability_metric_details"])
            check_type(argname="argument canary_latency_metric_details", value=canary_latency_metric_details, expected_type=type_hints["canary_latency_metric_details"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "canary_availability_metric_details": canary_availability_metric_details,
            "canary_latency_metric_details": canary_latency_metric_details,
        }

    @builtins.property
    def canary_availability_metric_details(
        self,
    ) -> "IOperationAvailabilityMetricDetails":
        '''(experimental) The canary availability metric details.

        :stability: experimental
        '''
        result = self._values.get("canary_availability_metric_details")
        assert result is not None, "Required property 'canary_availability_metric_details' is missing"
        return typing.cast("IOperationAvailabilityMetricDetails", result)

    @builtins.property
    def canary_latency_metric_details(self) -> "IOperationLatencyMetricDetails":
        '''(experimental) The canary latency metric details.

        :stability: experimental
        '''
        result = self._values.get("canary_latency_metric_details")
        assert result is not None, "Required property 'canary_latency_metric_details' is missing"
        return typing.cast("IOperationLatencyMetricDetails", result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CanaryMetricProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdklabs/multi-az-observability.CanaryTestMetricsOverrideProps",
    jsii_struct_bases=[],
    name_mapping={
        "alarm_statistic": "alarmStatistic",
        "datapoints_to_alarm": "datapointsToAlarm",
        "evaluation_periods": "evaluationPeriods",
        "period": "period",
    },
)
class CanaryTestMetricsOverrideProps:
    def __init__(
        self,
        *,
        alarm_statistic: typing.Optional[builtins.str] = None,
        datapoints_to_alarm: typing.Optional[jsii.Number] = None,
        evaluation_periods: typing.Optional[jsii.Number] = None,
        period: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
    ) -> None:
        '''(experimental) The properties for creating an override.

        :param alarm_statistic: (experimental) The statistic used for alarms, for availability metrics this should be "Sum", for latency metrics it could something like "p99" or "p99.9". Default: - This property will use the default defined for the service
        :param datapoints_to_alarm: (experimental) The number of datapoints to alarm on for latency and availability alarms. Default: - This property will use the default defined for the service
        :param evaluation_periods: (experimental) The number of evaluation periods for latency and availabiltiy alarms. Default: - This property will use the default defined for the service
        :param period: (experimental) The period for the metrics. Default: - This property will use the default defined for the service

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2e332d50e6cba3afaf9d92838759b5d3b619a9c2e8dcdef241b213cde461880c)
            check_type(argname="argument alarm_statistic", value=alarm_statistic, expected_type=type_hints["alarm_statistic"])
            check_type(argname="argument datapoints_to_alarm", value=datapoints_to_alarm, expected_type=type_hints["datapoints_to_alarm"])
            check_type(argname="argument evaluation_periods", value=evaluation_periods, expected_type=type_hints["evaluation_periods"])
            check_type(argname="argument period", value=period, expected_type=type_hints["period"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if alarm_statistic is not None:
            self._values["alarm_statistic"] = alarm_statistic
        if datapoints_to_alarm is not None:
            self._values["datapoints_to_alarm"] = datapoints_to_alarm
        if evaluation_periods is not None:
            self._values["evaluation_periods"] = evaluation_periods
        if period is not None:
            self._values["period"] = period

    @builtins.property
    def alarm_statistic(self) -> typing.Optional[builtins.str]:
        '''(experimental) The statistic used for alarms, for availability metrics this should be "Sum", for latency metrics it could something like "p99" or "p99.9".

        :default: - This property will use the default defined for the service

        :stability: experimental
        '''
        result = self._values.get("alarm_statistic")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def datapoints_to_alarm(self) -> typing.Optional[jsii.Number]:
        '''(experimental) The number of datapoints to alarm on for latency and availability alarms.

        :default: - This property will use the default defined for the service

        :stability: experimental
        '''
        result = self._values.get("datapoints_to_alarm")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def evaluation_periods(self) -> typing.Optional[jsii.Number]:
        '''(experimental) The number of evaluation periods for latency and availabiltiy alarms.

        :default: - This property will use the default defined for the service

        :stability: experimental
        '''
        result = self._values.get("evaluation_periods")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def period(self) -> typing.Optional[_aws_cdk_ceddda9d.Duration]:
        '''(experimental) The period for the metrics.

        :default: - This property will use the default defined for the service

        :stability: experimental
        '''
        result = self._values.get("period")
        return typing.cast(typing.Optional[_aws_cdk_ceddda9d.Duration], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CanaryTestMetricsOverrideProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdklabs/multi-az-observability.ContributorInsightRuleDetailsProps",
    jsii_struct_bases=[],
    name_mapping={
        "availability_zone_id_json_path": "availabilityZoneIdJsonPath",
        "fault_metric_json_path": "faultMetricJsonPath",
        "instance_id_json_path": "instanceIdJsonPath",
        "log_groups": "logGroups",
        "operation_name_json_path": "operationNameJsonPath",
        "success_latency_metric_json_path": "successLatencyMetricJsonPath",
    },
)
class ContributorInsightRuleDetailsProps:
    def __init__(
        self,
        *,
        availability_zone_id_json_path: builtins.str,
        fault_metric_json_path: builtins.str,
        instance_id_json_path: builtins.str,
        log_groups: typing.Sequence[_aws_cdk_aws_logs_ceddda9d.ILogGroup],
        operation_name_json_path: builtins.str,
        success_latency_metric_json_path: builtins.str,
    ) -> None:
        '''(experimental) The contributor insight rule details properties.

        :param availability_zone_id_json_path: (experimental) The path in the log files to the field that identifies the Availability Zone Id that the request was handled in, for example { "AZ-ID": "use1-az1" } would have a path of $.AZ-ID.
        :param fault_metric_json_path: (experimental) The path in the log files to the field that identifies if the response resulted in a fault, for example { "Fault" : 1 } would have a path of $.Fault.
        :param instance_id_json_path: (experimental) The JSON path to the instance id field in the log files, only required for server-side rules.
        :param log_groups: (experimental) The log groups where CloudWatch logs for the operation are located. If this is not provided, Contributor Insight rules cannot be created.
        :param operation_name_json_path: (experimental) The path in the log files to the field that identifies the operation the log file is for.
        :param success_latency_metric_json_path: (experimental) The path in the log files to the field that indicates the latency for the response. This could either be success latency or fault latency depending on the alarms and rules you are creating.

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c8ade43837bde272fae8e0a6676477846373fc1bb25c3d716ae04eab9da138d9)
            check_type(argname="argument availability_zone_id_json_path", value=availability_zone_id_json_path, expected_type=type_hints["availability_zone_id_json_path"])
            check_type(argname="argument fault_metric_json_path", value=fault_metric_json_path, expected_type=type_hints["fault_metric_json_path"])
            check_type(argname="argument instance_id_json_path", value=instance_id_json_path, expected_type=type_hints["instance_id_json_path"])
            check_type(argname="argument log_groups", value=log_groups, expected_type=type_hints["log_groups"])
            check_type(argname="argument operation_name_json_path", value=operation_name_json_path, expected_type=type_hints["operation_name_json_path"])
            check_type(argname="argument success_latency_metric_json_path", value=success_latency_metric_json_path, expected_type=type_hints["success_latency_metric_json_path"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "availability_zone_id_json_path": availability_zone_id_json_path,
            "fault_metric_json_path": fault_metric_json_path,
            "instance_id_json_path": instance_id_json_path,
            "log_groups": log_groups,
            "operation_name_json_path": operation_name_json_path,
            "success_latency_metric_json_path": success_latency_metric_json_path,
        }

    @builtins.property
    def availability_zone_id_json_path(self) -> builtins.str:
        '''(experimental) The path in the log files to the field that identifies the Availability Zone Id that the request was handled in, for example { "AZ-ID": "use1-az1" } would have a path of $.AZ-ID.

        :stability: experimental
        '''
        result = self._values.get("availability_zone_id_json_path")
        assert result is not None, "Required property 'availability_zone_id_json_path' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def fault_metric_json_path(self) -> builtins.str:
        '''(experimental) The path in the log files to the field that identifies if the response resulted in a fault, for example { "Fault" : 1 } would have a path of $.Fault.

        :stability: experimental
        '''
        result = self._values.get("fault_metric_json_path")
        assert result is not None, "Required property 'fault_metric_json_path' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def instance_id_json_path(self) -> builtins.str:
        '''(experimental) The JSON path to the instance id field in the log files, only required for server-side rules.

        :stability: experimental
        '''
        result = self._values.get("instance_id_json_path")
        assert result is not None, "Required property 'instance_id_json_path' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def log_groups(self) -> typing.List[_aws_cdk_aws_logs_ceddda9d.ILogGroup]:
        '''(experimental) The log groups where CloudWatch logs for the operation are located.

        If
        this is not provided, Contributor Insight rules cannot be created.

        :stability: experimental
        '''
        result = self._values.get("log_groups")
        assert result is not None, "Required property 'log_groups' is missing"
        return typing.cast(typing.List[_aws_cdk_aws_logs_ceddda9d.ILogGroup], result)

    @builtins.property
    def operation_name_json_path(self) -> builtins.str:
        '''(experimental) The path in the log files to the field that identifies the operation the log file is for.

        :stability: experimental
        '''
        result = self._values.get("operation_name_json_path")
        assert result is not None, "Required property 'operation_name_json_path' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def success_latency_metric_json_path(self) -> builtins.str:
        '''(experimental) The path in the log files to the field that indicates the latency for the response.

        This could either be success latency or fault
        latency depending on the alarms and rules you are creating.

        :stability: experimental
        '''
        result = self._values.get("success_latency_metric_json_path")
        assert result is not None, "Required property 'success_latency_metric_json_path' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ContributorInsightRuleDetailsProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.interface(jsii_type="@cdklabs/multi-az-observability.IAvailabilityZoneMapper")
class IAvailabilityZoneMapper(
    _constructs_77d1e7e8.IConstruct,
    typing_extensions.Protocol,
):
    '''(experimental) A wrapper for the Availability Zone mapper construct that allows you to translate Availability Zone names to Availability Zone Ids and vice a versa using the mapping in the AWS account where this is deployed.

    :stability: experimental
    '''

    @builtins.property
    @jsii.member(jsii_name="function")
    def function(self) -> _aws_cdk_aws_lambda_ceddda9d.IFunction:
        '''(experimental) The function that does the mapping.

        :stability: experimental
        '''
        ...

    @function.setter
    def function(self, value: _aws_cdk_aws_lambda_ceddda9d.IFunction) -> None:
        ...

    @builtins.property
    @jsii.member(jsii_name="logGroup")
    def log_group(self) -> _aws_cdk_aws_logs_ceddda9d.ILogGroup:
        '''(experimental) The log group for the function's logs.

        :stability: experimental
        '''
        ...

    @log_group.setter
    def log_group(self, value: _aws_cdk_aws_logs_ceddda9d.ILogGroup) -> None:
        ...

    @builtins.property
    @jsii.member(jsii_name="mapper")
    def mapper(self) -> _aws_cdk_ceddda9d.CustomResource:
        '''(experimental) The custom resource that can be referenced to use Fn::GetAtt functions on to retrieve availability zone names and ids.

        :stability: experimental
        '''
        ...

    @mapper.setter
    def mapper(self, value: _aws_cdk_ceddda9d.CustomResource) -> None:
        ...

    @jsii.member(jsii_name="allAvailabilityZoneIdsAsArray")
    def all_availability_zone_ids_as_array(self) -> _aws_cdk_ceddda9d.Reference:
        '''(experimental) Returns a reference that can be cast to a string array with all of the Availability Zone Ids.

        :stability: experimental
        '''
        ...

    @jsii.member(jsii_name="allAvailabilityZoneIdsAsCommaDelimitedList")
    def all_availability_zone_ids_as_comma_delimited_list(self) -> builtins.str:
        '''(experimental) Returns a comma delimited list of Availability Zone Ids for the supplied Availability Zone names.

        You can use this string with Fn.Select(x, Fn.Split(",", azs)) to
        get a specific Availability Zone Id

        :stability: experimental
        '''
        ...

    @jsii.member(jsii_name="allAvailabilityZoneNamesAsCommaDelimitedList")
    def all_availability_zone_names_as_comma_delimited_list(self) -> builtins.str:
        '''(experimental) Gets all of the Availability Zone names in this Region as a comma delimited list.

        You can use this string with Fn.Select(x, Fn.Split(",", azs)) to
        get a specific Availability Zone Name

        :stability: experimental
        '''
        ...

    @jsii.member(jsii_name="availabilityZoneId")
    def availability_zone_id(
        self,
        availability_zone_name: builtins.str,
    ) -> builtins.str:
        '''(experimental) Gets the Availability Zone Id for the given Availability Zone Name in this account.

        :param availability_zone_name: -

        :stability: experimental
        '''
        ...

    @jsii.member(jsii_name="availabilityZoneIdFromAvailabilityZoneLetter")
    def availability_zone_id_from_availability_zone_letter(
        self,
        letter: builtins.str,
    ) -> builtins.str:
        '''(experimental) Given a letter like "f" or "a", returns the Availability Zone Id for that Availability Zone name in this account.

        :param letter: -

        :stability: experimental
        '''
        ...

    @jsii.member(jsii_name="availabilityZoneIdsAsArray")
    def availability_zone_ids_as_array(
        self,
        availability_zone_names: typing.Sequence[builtins.str],
    ) -> typing.List[builtins.str]:
        '''(experimental) Returns an array for Availability Zone Ids for the supplied Availability Zone names, they are returned in the same order the names were provided.

        :param availability_zone_names: -

        :stability: experimental
        '''
        ...

    @jsii.member(jsii_name="availabilityZoneIdsAsCommaDelimitedList")
    def availability_zone_ids_as_comma_delimited_list(
        self,
        availability_zone_names: typing.Sequence[builtins.str],
    ) -> builtins.str:
        '''(experimental) Returns a comma delimited list of Availability Zone Ids for the supplied Availability Zone names.

        You can use this string with Fn.Select(x, Fn.Split(",", azs)) to
        get a specific Availability Zone Id

        :param availability_zone_names: -

        :stability: experimental
        '''
        ...

    @jsii.member(jsii_name="availabilityZoneName")
    def availability_zone_name(
        self,
        availability_zone_id: builtins.str,
    ) -> builtins.str:
        '''(experimental) Gets the Availability Zone Name for the given Availability Zone Id in this account.

        :param availability_zone_id: -

        :stability: experimental
        '''
        ...

    @jsii.member(jsii_name="regionPrefixForAvailabilityZoneIds")
    def region_prefix_for_availability_zone_ids(self) -> builtins.str:
        '''(experimental) Gets the prefix for the region used with Availability Zone Ids, for example in us-east-1, this returns "use1".

        :stability: experimental
        '''
        ...


class _IAvailabilityZoneMapperProxy(
    jsii.proxy_for(_constructs_77d1e7e8.IConstruct), # type: ignore[misc]
):
    '''(experimental) A wrapper for the Availability Zone mapper construct that allows you to translate Availability Zone names to Availability Zone Ids and vice a versa using the mapping in the AWS account where this is deployed.

    :stability: experimental
    '''

    __jsii_type__: typing.ClassVar[str] = "@cdklabs/multi-az-observability.IAvailabilityZoneMapper"

    @builtins.property
    @jsii.member(jsii_name="function")
    def function(self) -> _aws_cdk_aws_lambda_ceddda9d.IFunction:
        '''(experimental) The function that does the mapping.

        :stability: experimental
        '''
        return typing.cast(_aws_cdk_aws_lambda_ceddda9d.IFunction, jsii.get(self, "function"))

    @function.setter
    def function(self, value: _aws_cdk_aws_lambda_ceddda9d.IFunction) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f47430da8c1b9b48d48e5251cab2dae3962dee681f0b90504d563fbc491c9e67)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "function", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="logGroup")
    def log_group(self) -> _aws_cdk_aws_logs_ceddda9d.ILogGroup:
        '''(experimental) The log group for the function's logs.

        :stability: experimental
        '''
        return typing.cast(_aws_cdk_aws_logs_ceddda9d.ILogGroup, jsii.get(self, "logGroup"))

    @log_group.setter
    def log_group(self, value: _aws_cdk_aws_logs_ceddda9d.ILogGroup) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__389da457c25cddefd5704d4a7f76218a8fe049f65f0ca3834af16d010e8d19b5)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "logGroup", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="mapper")
    def mapper(self) -> _aws_cdk_ceddda9d.CustomResource:
        '''(experimental) The custom resource that can be referenced to use Fn::GetAtt functions on to retrieve availability zone names and ids.

        :stability: experimental
        '''
        return typing.cast(_aws_cdk_ceddda9d.CustomResource, jsii.get(self, "mapper"))

    @mapper.setter
    def mapper(self, value: _aws_cdk_ceddda9d.CustomResource) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0029138db755bb79aed43f624548124b5569bf7edbbeb9900ffd1dfe0d717307)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "mapper", value) # pyright: ignore[reportArgumentType]

    @jsii.member(jsii_name="allAvailabilityZoneIdsAsArray")
    def all_availability_zone_ids_as_array(self) -> _aws_cdk_ceddda9d.Reference:
        '''(experimental) Returns a reference that can be cast to a string array with all of the Availability Zone Ids.

        :stability: experimental
        '''
        return typing.cast(_aws_cdk_ceddda9d.Reference, jsii.invoke(self, "allAvailabilityZoneIdsAsArray", []))

    @jsii.member(jsii_name="allAvailabilityZoneIdsAsCommaDelimitedList")
    def all_availability_zone_ids_as_comma_delimited_list(self) -> builtins.str:
        '''(experimental) Returns a comma delimited list of Availability Zone Ids for the supplied Availability Zone names.

        You can use this string with Fn.Select(x, Fn.Split(",", azs)) to
        get a specific Availability Zone Id

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.invoke(self, "allAvailabilityZoneIdsAsCommaDelimitedList", []))

    @jsii.member(jsii_name="allAvailabilityZoneNamesAsCommaDelimitedList")
    def all_availability_zone_names_as_comma_delimited_list(self) -> builtins.str:
        '''(experimental) Gets all of the Availability Zone names in this Region as a comma delimited list.

        You can use this string with Fn.Select(x, Fn.Split(",", azs)) to
        get a specific Availability Zone Name

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.invoke(self, "allAvailabilityZoneNamesAsCommaDelimitedList", []))

    @jsii.member(jsii_name="availabilityZoneId")
    def availability_zone_id(
        self,
        availability_zone_name: builtins.str,
    ) -> builtins.str:
        '''(experimental) Gets the Availability Zone Id for the given Availability Zone Name in this account.

        :param availability_zone_name: -

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6087eb1a38695a37e37bb3ca859f7b1fc4a492230be646c5134e60435e309c78)
            check_type(argname="argument availability_zone_name", value=availability_zone_name, expected_type=type_hints["availability_zone_name"])
        return typing.cast(builtins.str, jsii.invoke(self, "availabilityZoneId", [availability_zone_name]))

    @jsii.member(jsii_name="availabilityZoneIdFromAvailabilityZoneLetter")
    def availability_zone_id_from_availability_zone_letter(
        self,
        letter: builtins.str,
    ) -> builtins.str:
        '''(experimental) Given a letter like "f" or "a", returns the Availability Zone Id for that Availability Zone name in this account.

        :param letter: -

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__413eeebcfa1b3ba0eb35bdb273cf11a8c50b498b97355794c9669484db03fc91)
            check_type(argname="argument letter", value=letter, expected_type=type_hints["letter"])
        return typing.cast(builtins.str, jsii.invoke(self, "availabilityZoneIdFromAvailabilityZoneLetter", [letter]))

    @jsii.member(jsii_name="availabilityZoneIdsAsArray")
    def availability_zone_ids_as_array(
        self,
        availability_zone_names: typing.Sequence[builtins.str],
    ) -> typing.List[builtins.str]:
        '''(experimental) Returns an array for Availability Zone Ids for the supplied Availability Zone names, they are returned in the same order the names were provided.

        :param availability_zone_names: -

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__21f092b9672a220828785aa3c9c3b7b73dce34c057d2d65eeba5296612dadce4)
            check_type(argname="argument availability_zone_names", value=availability_zone_names, expected_type=type_hints["availability_zone_names"])
        return typing.cast(typing.List[builtins.str], jsii.invoke(self, "availabilityZoneIdsAsArray", [availability_zone_names]))

    @jsii.member(jsii_name="availabilityZoneIdsAsCommaDelimitedList")
    def availability_zone_ids_as_comma_delimited_list(
        self,
        availability_zone_names: typing.Sequence[builtins.str],
    ) -> builtins.str:
        '''(experimental) Returns a comma delimited list of Availability Zone Ids for the supplied Availability Zone names.

        You can use this string with Fn.Select(x, Fn.Split(",", azs)) to
        get a specific Availability Zone Id

        :param availability_zone_names: -

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b9f2a2a111a8085b509d0ca8a9a17177229c1f48c38a1a794c99b52592550810)
            check_type(argname="argument availability_zone_names", value=availability_zone_names, expected_type=type_hints["availability_zone_names"])
        return typing.cast(builtins.str, jsii.invoke(self, "availabilityZoneIdsAsCommaDelimitedList", [availability_zone_names]))

    @jsii.member(jsii_name="availabilityZoneName")
    def availability_zone_name(
        self,
        availability_zone_id: builtins.str,
    ) -> builtins.str:
        '''(experimental) Gets the Availability Zone Name for the given Availability Zone Id in this account.

        :param availability_zone_id: -

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5afd920de43091152fe723627d9cebc610c78bce3297e2dfb179fa98803cbbc0)
            check_type(argname="argument availability_zone_id", value=availability_zone_id, expected_type=type_hints["availability_zone_id"])
        return typing.cast(builtins.str, jsii.invoke(self, "availabilityZoneName", [availability_zone_id]))

    @jsii.member(jsii_name="regionPrefixForAvailabilityZoneIds")
    def region_prefix_for_availability_zone_ids(self) -> builtins.str:
        '''(experimental) Gets the prefix for the region used with Availability Zone Ids, for example in us-east-1, this returns "use1".

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.invoke(self, "regionPrefixForAvailabilityZoneIds", []))

# Adding a "__jsii_proxy_class__(): typing.Type" function to the interface
typing.cast(typing.Any, IAvailabilityZoneMapper).__jsii_proxy_class__ = lambda : _IAvailabilityZoneMapperProxy


@jsii.interface(
    jsii_type="@cdklabs/multi-az-observability.IBaseOperationRegionalAlarmsAndRules"
)
class IBaseOperationRegionalAlarmsAndRules(typing_extensions.Protocol):
    '''(experimental) Base regional alarms and rules.

    :stability: experimental
    '''

    @builtins.property
    @jsii.member(jsii_name="availabilityAlarm")
    def availability_alarm(self) -> _aws_cdk_aws_cloudwatch_ceddda9d.IAlarm:
        '''(experimental) Availability alarm for this operation.

        :stability: experimental
        '''
        ...

    @availability_alarm.setter
    def availability_alarm(
        self,
        value: _aws_cdk_aws_cloudwatch_ceddda9d.IAlarm,
    ) -> None:
        ...

    @builtins.property
    @jsii.member(jsii_name="availabilityOrLatencyAlarm")
    def availability_or_latency_alarm(self) -> _aws_cdk_aws_cloudwatch_ceddda9d.IAlarm:
        '''(experimental) Composite alarm for either availabiltiy or latency impact to this operation.

        :stability: experimental
        '''
        ...

    @availability_or_latency_alarm.setter
    def availability_or_latency_alarm(
        self,
        value: _aws_cdk_aws_cloudwatch_ceddda9d.IAlarm,
    ) -> None:
        ...

    @builtins.property
    @jsii.member(jsii_name="latencyAlarm")
    def latency_alarm(self) -> _aws_cdk_aws_cloudwatch_ceddda9d.IAlarm:
        '''(experimental) Latency alarm for this operation.

        :stability: experimental
        '''
        ...

    @latency_alarm.setter
    def latency_alarm(self, value: _aws_cdk_aws_cloudwatch_ceddda9d.IAlarm) -> None:
        ...


class _IBaseOperationRegionalAlarmsAndRulesProxy:
    '''(experimental) Base regional alarms and rules.

    :stability: experimental
    '''

    __jsii_type__: typing.ClassVar[str] = "@cdklabs/multi-az-observability.IBaseOperationRegionalAlarmsAndRules"

    @builtins.property
    @jsii.member(jsii_name="availabilityAlarm")
    def availability_alarm(self) -> _aws_cdk_aws_cloudwatch_ceddda9d.IAlarm:
        '''(experimental) Availability alarm for this operation.

        :stability: experimental
        '''
        return typing.cast(_aws_cdk_aws_cloudwatch_ceddda9d.IAlarm, jsii.get(self, "availabilityAlarm"))

    @availability_alarm.setter
    def availability_alarm(
        self,
        value: _aws_cdk_aws_cloudwatch_ceddda9d.IAlarm,
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e05be40a82825eb9c32d0866f995ce2b4cd2edf02d26ad94ebf5999f9cb147b5)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "availabilityAlarm", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="availabilityOrLatencyAlarm")
    def availability_or_latency_alarm(self) -> _aws_cdk_aws_cloudwatch_ceddda9d.IAlarm:
        '''(experimental) Composite alarm for either availabiltiy or latency impact to this operation.

        :stability: experimental
        '''
        return typing.cast(_aws_cdk_aws_cloudwatch_ceddda9d.IAlarm, jsii.get(self, "availabilityOrLatencyAlarm"))

    @availability_or_latency_alarm.setter
    def availability_or_latency_alarm(
        self,
        value: _aws_cdk_aws_cloudwatch_ceddda9d.IAlarm,
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__24d5ace50e39c0a1c69b63ba511459bc45bc095145599e24e770f270c40ae562)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "availabilityOrLatencyAlarm", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="latencyAlarm")
    def latency_alarm(self) -> _aws_cdk_aws_cloudwatch_ceddda9d.IAlarm:
        '''(experimental) Latency alarm for this operation.

        :stability: experimental
        '''
        return typing.cast(_aws_cdk_aws_cloudwatch_ceddda9d.IAlarm, jsii.get(self, "latencyAlarm"))

    @latency_alarm.setter
    def latency_alarm(self, value: _aws_cdk_aws_cloudwatch_ceddda9d.IAlarm) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__14a910f298c35c3322a0161508009900213ab115071a4bed6ce58e442411261c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "latencyAlarm", value) # pyright: ignore[reportArgumentType]

# Adding a "__jsii_proxy_class__(): typing.Type" function to the interface
typing.cast(typing.Any, IBaseOperationRegionalAlarmsAndRules).__jsii_proxy_class__ = lambda : _IBaseOperationRegionalAlarmsAndRulesProxy


@jsii.interface(
    jsii_type="@cdklabs/multi-az-observability.IBaseOperationZonalAlarmsAndRules"
)
class IBaseOperationZonalAlarmsAndRules(typing_extensions.Protocol):
    '''(experimental) The base operation zonal alarms and rules.

    :stability: experimental
    '''

    @builtins.property
    @jsii.member(jsii_name="availabilityAlarm")
    def availability_alarm(self) -> _aws_cdk_aws_cloudwatch_ceddda9d.IAlarm:
        '''(experimental) Availability alarm for this operation.

        :stability: experimental
        '''
        ...

    @availability_alarm.setter
    def availability_alarm(
        self,
        value: _aws_cdk_aws_cloudwatch_ceddda9d.IAlarm,
    ) -> None:
        ...

    @builtins.property
    @jsii.member(jsii_name="availabilityZoneIsOutlierForFaults")
    def availability_zone_is_outlier_for_faults(
        self,
    ) -> _aws_cdk_aws_cloudwatch_ceddda9d.IAlarm:
        '''(experimental) Alarm that indicates that this AZ is an outlier for fault rate.

        :stability: experimental
        '''
        ...

    @availability_zone_is_outlier_for_faults.setter
    def availability_zone_is_outlier_for_faults(
        self,
        value: _aws_cdk_aws_cloudwatch_ceddda9d.IAlarm,
    ) -> None:
        ...

    @builtins.property
    @jsii.member(jsii_name="availabilityZoneIsOutlierForLatency")
    def availability_zone_is_outlier_for_latency(
        self,
    ) -> _aws_cdk_aws_cloudwatch_ceddda9d.IAlarm:
        '''(experimental) Alarm that indicates this AZ is an outlier for high latency.

        :stability: experimental
        '''
        ...

    @availability_zone_is_outlier_for_latency.setter
    def availability_zone_is_outlier_for_latency(
        self,
        value: _aws_cdk_aws_cloudwatch_ceddda9d.IAlarm,
    ) -> None:
        ...

    @builtins.property
    @jsii.member(jsii_name="latencyAlarm")
    def latency_alarm(self) -> _aws_cdk_aws_cloudwatch_ceddda9d.IAlarm:
        '''(experimental) Latency alarm for this operation.

        :stability: experimental
        '''
        ...

    @latency_alarm.setter
    def latency_alarm(self, value: _aws_cdk_aws_cloudwatch_ceddda9d.IAlarm) -> None:
        ...


class _IBaseOperationZonalAlarmsAndRulesProxy:
    '''(experimental) The base operation zonal alarms and rules.

    :stability: experimental
    '''

    __jsii_type__: typing.ClassVar[str] = "@cdklabs/multi-az-observability.IBaseOperationZonalAlarmsAndRules"

    @builtins.property
    @jsii.member(jsii_name="availabilityAlarm")
    def availability_alarm(self) -> _aws_cdk_aws_cloudwatch_ceddda9d.IAlarm:
        '''(experimental) Availability alarm for this operation.

        :stability: experimental
        '''
        return typing.cast(_aws_cdk_aws_cloudwatch_ceddda9d.IAlarm, jsii.get(self, "availabilityAlarm"))

    @availability_alarm.setter
    def availability_alarm(
        self,
        value: _aws_cdk_aws_cloudwatch_ceddda9d.IAlarm,
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6a92a17530fd7be2abc75031830d6800bf33402fef23fe2dac9fb85b007c9172)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "availabilityAlarm", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="availabilityZoneIsOutlierForFaults")
    def availability_zone_is_outlier_for_faults(
        self,
    ) -> _aws_cdk_aws_cloudwatch_ceddda9d.IAlarm:
        '''(experimental) Alarm that indicates that this AZ is an outlier for fault rate.

        :stability: experimental
        '''
        return typing.cast(_aws_cdk_aws_cloudwatch_ceddda9d.IAlarm, jsii.get(self, "availabilityZoneIsOutlierForFaults"))

    @availability_zone_is_outlier_for_faults.setter
    def availability_zone_is_outlier_for_faults(
        self,
        value: _aws_cdk_aws_cloudwatch_ceddda9d.IAlarm,
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5ae1b64507c6dfd2c11eb88c657a29bd04b6352911706669e4d867484c5470d7)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "availabilityZoneIsOutlierForFaults", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="availabilityZoneIsOutlierForLatency")
    def availability_zone_is_outlier_for_latency(
        self,
    ) -> _aws_cdk_aws_cloudwatch_ceddda9d.IAlarm:
        '''(experimental) Alarm that indicates this AZ is an outlier for high latency.

        :stability: experimental
        '''
        return typing.cast(_aws_cdk_aws_cloudwatch_ceddda9d.IAlarm, jsii.get(self, "availabilityZoneIsOutlierForLatency"))

    @availability_zone_is_outlier_for_latency.setter
    def availability_zone_is_outlier_for_latency(
        self,
        value: _aws_cdk_aws_cloudwatch_ceddda9d.IAlarm,
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7eedac5c883637549b879a716b78731d3fbee047a0725dd575a17b58be872dbb)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "availabilityZoneIsOutlierForLatency", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="latencyAlarm")
    def latency_alarm(self) -> _aws_cdk_aws_cloudwatch_ceddda9d.IAlarm:
        '''(experimental) Latency alarm for this operation.

        :stability: experimental
        '''
        return typing.cast(_aws_cdk_aws_cloudwatch_ceddda9d.IAlarm, jsii.get(self, "latencyAlarm"))

    @latency_alarm.setter
    def latency_alarm(self, value: _aws_cdk_aws_cloudwatch_ceddda9d.IAlarm) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__42cfd81e8009b1f9a1c79c3cddd666296f6bc2404e83f6ce251c0f6de5d6d0a9)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "latencyAlarm", value) # pyright: ignore[reportArgumentType]

# Adding a "__jsii_proxy_class__(): typing.Type" function to the interface
typing.cast(typing.Any, IBaseOperationZonalAlarmsAndRules).__jsii_proxy_class__ = lambda : _IBaseOperationZonalAlarmsAndRulesProxy


@jsii.interface(
    jsii_type="@cdklabs/multi-az-observability.IBasicServiceMultiAZObservability"
)
class IBasicServiceMultiAZObservability(
    _constructs_77d1e7e8.IConstruct,
    typing_extensions.Protocol,
):
    '''(experimental) Properties of a basic service.

    :stability: experimental
    '''

    @builtins.property
    @jsii.member(jsii_name="aggregateZonalIsolatedImpactAlarms")
    def aggregate_zonal_isolated_impact_alarms(
        self,
    ) -> typing.Mapping[builtins.str, _aws_cdk_aws_cloudwatch_ceddda9d.IAlarm]:
        '''(experimental) The alarms indicating if an AZ has isolated impact from either ALB or NAT GW metrics.

        :stability: experimental
        '''
        ...

    @aggregate_zonal_isolated_impact_alarms.setter
    def aggregate_zonal_isolated_impact_alarms(
        self,
        value: typing.Mapping[builtins.str, _aws_cdk_aws_cloudwatch_ceddda9d.IAlarm],
    ) -> None:
        ...

    @builtins.property
    @jsii.member(jsii_name="serviceName")
    def service_name(self) -> builtins.str:
        '''(experimental) The name of the service.

        :stability: experimental
        '''
        ...

    @service_name.setter
    def service_name(self, value: builtins.str) -> None:
        ...

    @builtins.property
    @jsii.member(jsii_name="albZonalIsolatedImpactAlarms")
    def alb_zonal_isolated_impact_alarms(
        self,
    ) -> typing.Optional[typing.Mapping[builtins.str, _aws_cdk_aws_cloudwatch_ceddda9d.IAlarm]]:
        '''(experimental) The alarms indicating if an AZ is an outlier for ALB faults and has isolated impact.

        This will be 1 composite alarm
        per AZ that triggers if any ALB in that AZ sees outlier impact.

        :stability: experimental
        '''
        ...

    @alb_zonal_isolated_impact_alarms.setter
    def alb_zonal_isolated_impact_alarms(
        self,
        value: typing.Optional[typing.Mapping[builtins.str, _aws_cdk_aws_cloudwatch_ceddda9d.IAlarm]],
    ) -> None:
        ...

    @builtins.property
    @jsii.member(jsii_name="applicationLoadBalancers")
    def application_load_balancers(
        self,
    ) -> typing.Optional[typing.List[_aws_cdk_aws_elasticloadbalancingv2_ceddda9d.IApplicationLoadBalancer]]:
        '''(experimental) The application load balancers being used by the service.

        :stability: experimental
        '''
        ...

    @application_load_balancers.setter
    def application_load_balancers(
        self,
        value: typing.Optional[typing.List[_aws_cdk_aws_elasticloadbalancingv2_ceddda9d.IApplicationLoadBalancer]],
    ) -> None:
        ...

    @builtins.property
    @jsii.member(jsii_name="dashboard")
    def dashboard(self) -> typing.Optional[_aws_cdk_aws_cloudwatch_ceddda9d.Dashboard]:
        '''(experimental) The optional dashboard created for observability.

        :stability: experimental
        '''
        ...

    @dashboard.setter
    def dashboard(
        self,
        value: typing.Optional[_aws_cdk_aws_cloudwatch_ceddda9d.Dashboard],
    ) -> None:
        ...

    @builtins.property
    @jsii.member(jsii_name="natGateways")
    def nat_gateways(
        self,
    ) -> typing.Optional[typing.Mapping[builtins.str, typing.List[_aws_cdk_aws_ec2_ceddda9d.CfnNatGateway]]]:
        '''(experimental) The NAT Gateways being used in the service, each set of NAT Gateways are keyed by their Availability Zone Id.

        :stability: experimental
        '''
        ...

    @nat_gateways.setter
    def nat_gateways(
        self,
        value: typing.Optional[typing.Mapping[builtins.str, typing.List[_aws_cdk_aws_ec2_ceddda9d.CfnNatGateway]]],
    ) -> None:
        ...

    @builtins.property
    @jsii.member(jsii_name="natGWZonalIsolatedImpactAlarms")
    def nat_gw_zonal_isolated_impact_alarms(
        self,
    ) -> typing.Optional[typing.Mapping[builtins.str, _aws_cdk_aws_cloudwatch_ceddda9d.IAlarm]]:
        '''(experimental) The alarms indicating if an AZ is an outlier for NAT GW packet loss and has isolated impact.

        This will be 1 composite alarm
        per AZ that triggers if any NAT GW in that AZ sees outlier impact.

        :stability: experimental
        '''
        ...

    @nat_gw_zonal_isolated_impact_alarms.setter
    def nat_gw_zonal_isolated_impact_alarms(
        self,
        value: typing.Optional[typing.Mapping[builtins.str, _aws_cdk_aws_cloudwatch_ceddda9d.IAlarm]],
    ) -> None:
        ...


class _IBasicServiceMultiAZObservabilityProxy(
    jsii.proxy_for(_constructs_77d1e7e8.IConstruct), # type: ignore[misc]
):
    '''(experimental) Properties of a basic service.

    :stability: experimental
    '''

    __jsii_type__: typing.ClassVar[str] = "@cdklabs/multi-az-observability.IBasicServiceMultiAZObservability"

    @builtins.property
    @jsii.member(jsii_name="aggregateZonalIsolatedImpactAlarms")
    def aggregate_zonal_isolated_impact_alarms(
        self,
    ) -> typing.Mapping[builtins.str, _aws_cdk_aws_cloudwatch_ceddda9d.IAlarm]:
        '''(experimental) The alarms indicating if an AZ has isolated impact from either ALB or NAT GW metrics.

        :stability: experimental
        '''
        return typing.cast(typing.Mapping[builtins.str, _aws_cdk_aws_cloudwatch_ceddda9d.IAlarm], jsii.get(self, "aggregateZonalIsolatedImpactAlarms"))

    @aggregate_zonal_isolated_impact_alarms.setter
    def aggregate_zonal_isolated_impact_alarms(
        self,
        value: typing.Mapping[builtins.str, _aws_cdk_aws_cloudwatch_ceddda9d.IAlarm],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__41292a6738a299b0ca8af3a281416324fbf5033e0cf464d6e9ff2a2c726eac6a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "aggregateZonalIsolatedImpactAlarms", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="serviceName")
    def service_name(self) -> builtins.str:
        '''(experimental) The name of the service.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "serviceName"))

    @service_name.setter
    def service_name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f998baa4ed92b2833d645407a865db8211d731915e2ca6e12d6285228b42ba35)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "serviceName", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="albZonalIsolatedImpactAlarms")
    def alb_zonal_isolated_impact_alarms(
        self,
    ) -> typing.Optional[typing.Mapping[builtins.str, _aws_cdk_aws_cloudwatch_ceddda9d.IAlarm]]:
        '''(experimental) The alarms indicating if an AZ is an outlier for ALB faults and has isolated impact.

        This will be 1 composite alarm
        per AZ that triggers if any ALB in that AZ sees outlier impact.

        :stability: experimental
        '''
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, _aws_cdk_aws_cloudwatch_ceddda9d.IAlarm]], jsii.get(self, "albZonalIsolatedImpactAlarms"))

    @alb_zonal_isolated_impact_alarms.setter
    def alb_zonal_isolated_impact_alarms(
        self,
        value: typing.Optional[typing.Mapping[builtins.str, _aws_cdk_aws_cloudwatch_ceddda9d.IAlarm]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__07c61148effad607221bb5da499d3f55322a58946976b9c63de59dd4f1ab0712)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "albZonalIsolatedImpactAlarms", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="applicationLoadBalancers")
    def application_load_balancers(
        self,
    ) -> typing.Optional[typing.List[_aws_cdk_aws_elasticloadbalancingv2_ceddda9d.IApplicationLoadBalancer]]:
        '''(experimental) The application load balancers being used by the service.

        :stability: experimental
        '''
        return typing.cast(typing.Optional[typing.List[_aws_cdk_aws_elasticloadbalancingv2_ceddda9d.IApplicationLoadBalancer]], jsii.get(self, "applicationLoadBalancers"))

    @application_load_balancers.setter
    def application_load_balancers(
        self,
        value: typing.Optional[typing.List[_aws_cdk_aws_elasticloadbalancingv2_ceddda9d.IApplicationLoadBalancer]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0b22969ea384a27c5200ceae28c1f02c3bb680e5fcb566cd00d4c12d9cd5feed)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "applicationLoadBalancers", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="dashboard")
    def dashboard(self) -> typing.Optional[_aws_cdk_aws_cloudwatch_ceddda9d.Dashboard]:
        '''(experimental) The optional dashboard created for observability.

        :stability: experimental
        '''
        return typing.cast(typing.Optional[_aws_cdk_aws_cloudwatch_ceddda9d.Dashboard], jsii.get(self, "dashboard"))

    @dashboard.setter
    def dashboard(
        self,
        value: typing.Optional[_aws_cdk_aws_cloudwatch_ceddda9d.Dashboard],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8ee207809f5cbdb57d53c0cf6b46801ab28117e86e8644052c9277aebdee8860)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "dashboard", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="natGateways")
    def nat_gateways(
        self,
    ) -> typing.Optional[typing.Mapping[builtins.str, typing.List[_aws_cdk_aws_ec2_ceddda9d.CfnNatGateway]]]:
        '''(experimental) The NAT Gateways being used in the service, each set of NAT Gateways are keyed by their Availability Zone Id.

        :stability: experimental
        '''
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, typing.List[_aws_cdk_aws_ec2_ceddda9d.CfnNatGateway]]], jsii.get(self, "natGateways"))

    @nat_gateways.setter
    def nat_gateways(
        self,
        value: typing.Optional[typing.Mapping[builtins.str, typing.List[_aws_cdk_aws_ec2_ceddda9d.CfnNatGateway]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e653e78b064972b23197009e2c4e265c5bc6e983abab5029013f2c8b9f62ad42)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "natGateways", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="natGWZonalIsolatedImpactAlarms")
    def nat_gw_zonal_isolated_impact_alarms(
        self,
    ) -> typing.Optional[typing.Mapping[builtins.str, _aws_cdk_aws_cloudwatch_ceddda9d.IAlarm]]:
        '''(experimental) The alarms indicating if an AZ is an outlier for NAT GW packet loss and has isolated impact.

        This will be 1 composite alarm
        per AZ that triggers if any NAT GW in that AZ sees outlier impact.

        :stability: experimental
        '''
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, _aws_cdk_aws_cloudwatch_ceddda9d.IAlarm]], jsii.get(self, "natGWZonalIsolatedImpactAlarms"))

    @nat_gw_zonal_isolated_impact_alarms.setter
    def nat_gw_zonal_isolated_impact_alarms(
        self,
        value: typing.Optional[typing.Mapping[builtins.str, _aws_cdk_aws_cloudwatch_ceddda9d.IAlarm]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a6aca38ba20e1b6c03131b7d324928febc6618b62c5bee38f28f334430ac4a05)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "natGWZonalIsolatedImpactAlarms", value) # pyright: ignore[reportArgumentType]

# Adding a "__jsii_proxy_class__(): typing.Type" function to the interface
typing.cast(typing.Any, IBasicServiceMultiAZObservability).__jsii_proxy_class__ = lambda : _IBasicServiceMultiAZObservabilityProxy


@jsii.interface(jsii_type="@cdklabs/multi-az-observability.ICanaryMetrics")
class ICanaryMetrics(typing_extensions.Protocol):
    '''(experimental) The metric definitions for metric produced by the canary.

    :stability: experimental
    '''

    @builtins.property
    @jsii.member(jsii_name="canaryAvailabilityMetricDetails")
    def canary_availability_metric_details(
        self,
    ) -> "IOperationAvailabilityMetricDetails":
        '''(experimental) The canary availability metric details.

        :stability: experimental
        '''
        ...

    @builtins.property
    @jsii.member(jsii_name="canaryLatencyMetricDetails")
    def canary_latency_metric_details(self) -> "IOperationLatencyMetricDetails":
        '''(experimental) The canary latency metric details.

        :stability: experimental
        '''
        ...


class _ICanaryMetricsProxy:
    '''(experimental) The metric definitions for metric produced by the canary.

    :stability: experimental
    '''

    __jsii_type__: typing.ClassVar[str] = "@cdklabs/multi-az-observability.ICanaryMetrics"

    @builtins.property
    @jsii.member(jsii_name="canaryAvailabilityMetricDetails")
    def canary_availability_metric_details(
        self,
    ) -> "IOperationAvailabilityMetricDetails":
        '''(experimental) The canary availability metric details.

        :stability: experimental
        '''
        return typing.cast("IOperationAvailabilityMetricDetails", jsii.get(self, "canaryAvailabilityMetricDetails"))

    @builtins.property
    @jsii.member(jsii_name="canaryLatencyMetricDetails")
    def canary_latency_metric_details(self) -> "IOperationLatencyMetricDetails":
        '''(experimental) The canary latency metric details.

        :stability: experimental
        '''
        return typing.cast("IOperationLatencyMetricDetails", jsii.get(self, "canaryLatencyMetricDetails"))

# Adding a "__jsii_proxy_class__(): typing.Type" function to the interface
typing.cast(typing.Any, ICanaryMetrics).__jsii_proxy_class__ = lambda : _ICanaryMetricsProxy


@jsii.interface(
    jsii_type="@cdklabs/multi-az-observability.ICanaryOperationRegionalAlarmsAndRules"
)
class ICanaryOperationRegionalAlarmsAndRules(
    IBaseOperationRegionalAlarmsAndRules,
    typing_extensions.Protocol,
):
    '''(experimental) The canary operation regional alarms and rules.

    :stability: experimental
    '''

    pass


class _ICanaryOperationRegionalAlarmsAndRulesProxy(
    jsii.proxy_for(IBaseOperationRegionalAlarmsAndRules), # type: ignore[misc]
):
    '''(experimental) The canary operation regional alarms and rules.

    :stability: experimental
    '''

    __jsii_type__: typing.ClassVar[str] = "@cdklabs/multi-az-observability.ICanaryOperationRegionalAlarmsAndRules"
    pass

# Adding a "__jsii_proxy_class__(): typing.Type" function to the interface
typing.cast(typing.Any, ICanaryOperationRegionalAlarmsAndRules).__jsii_proxy_class__ = lambda : _ICanaryOperationRegionalAlarmsAndRulesProxy


@jsii.interface(
    jsii_type="@cdklabs/multi-az-observability.ICanaryOperationZonalAlarmsAndRules"
)
class ICanaryOperationZonalAlarmsAndRules(
    IBaseOperationZonalAlarmsAndRules,
    typing_extensions.Protocol,
):
    '''(experimental) Alarms and rules for canary metrics.

    :stability: experimental
    '''

    @builtins.property
    @jsii.member(jsii_name="isolatedImpactAlarm")
    def isolated_impact_alarm(self) -> _aws_cdk_aws_cloudwatch_ceddda9d.IAlarm:
        '''(experimental) Alarm that triggers if either latency or availability breach the specified threshold in this AZ and the AZ is an outlier for faults or latency.

        :stability: experimental
        '''
        ...

    @isolated_impact_alarm.setter
    def isolated_impact_alarm(
        self,
        value: _aws_cdk_aws_cloudwatch_ceddda9d.IAlarm,
    ) -> None:
        ...


class _ICanaryOperationZonalAlarmsAndRulesProxy(
    jsii.proxy_for(IBaseOperationZonalAlarmsAndRules), # type: ignore[misc]
):
    '''(experimental) Alarms and rules for canary metrics.

    :stability: experimental
    '''

    __jsii_type__: typing.ClassVar[str] = "@cdklabs/multi-az-observability.ICanaryOperationZonalAlarmsAndRules"

    @builtins.property
    @jsii.member(jsii_name="isolatedImpactAlarm")
    def isolated_impact_alarm(self) -> _aws_cdk_aws_cloudwatch_ceddda9d.IAlarm:
        '''(experimental) Alarm that triggers if either latency or availability breach the specified threshold in this AZ and the AZ is an outlier for faults or latency.

        :stability: experimental
        '''
        return typing.cast(_aws_cdk_aws_cloudwatch_ceddda9d.IAlarm, jsii.get(self, "isolatedImpactAlarm"))

    @isolated_impact_alarm.setter
    def isolated_impact_alarm(
        self,
        value: _aws_cdk_aws_cloudwatch_ceddda9d.IAlarm,
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d88172cfcb0d0284117e3f0e5b5b04255860769c713a92be3392791c22faa5ea)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "isolatedImpactAlarm", value) # pyright: ignore[reportArgumentType]

# Adding a "__jsii_proxy_class__(): typing.Type" function to the interface
typing.cast(typing.Any, ICanaryOperationZonalAlarmsAndRules).__jsii_proxy_class__ = lambda : _ICanaryOperationZonalAlarmsAndRulesProxy


@jsii.interface(jsii_type="@cdklabs/multi-az-observability.ICanaryTestMetricsOverride")
class ICanaryTestMetricsOverride(typing_extensions.Protocol):
    '''(experimental) Provides overrides for the default metric settings used for the automatically created canary tests.

    :stability: experimental
    '''

    @builtins.property
    @jsii.member(jsii_name="alarmStatistic")
    def alarm_statistic(self) -> typing.Optional[builtins.str]:
        '''(experimental) The statistic used for alarms, for availability metrics this should be "Sum", for latency metrics it could something like "p99" or "p99.9".

        :stability: experimental
        '''
        ...

    @builtins.property
    @jsii.member(jsii_name="datapointsToAlarm")
    def datapoints_to_alarm(self) -> typing.Optional[jsii.Number]:
        '''(experimental) The number of datapoints to alarm on for latency and availability alarms.

        :stability: experimental
        '''
        ...

    @builtins.property
    @jsii.member(jsii_name="evaluationPeriods")
    def evaluation_periods(self) -> typing.Optional[jsii.Number]:
        '''(experimental) The number of evaluation periods for latency and availabiltiy alarms.

        :stability: experimental
        '''
        ...

    @builtins.property
    @jsii.member(jsii_name="period")
    def period(self) -> typing.Optional[_aws_cdk_ceddda9d.Duration]:
        '''(experimental) The period for the metrics.

        :stability: experimental
        '''
        ...


class _ICanaryTestMetricsOverrideProxy:
    '''(experimental) Provides overrides for the default metric settings used for the automatically created canary tests.

    :stability: experimental
    '''

    __jsii_type__: typing.ClassVar[str] = "@cdklabs/multi-az-observability.ICanaryTestMetricsOverride"

    @builtins.property
    @jsii.member(jsii_name="alarmStatistic")
    def alarm_statistic(self) -> typing.Optional[builtins.str]:
        '''(experimental) The statistic used for alarms, for availability metrics this should be "Sum", for latency metrics it could something like "p99" or "p99.9".

        :stability: experimental
        '''
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "alarmStatistic"))

    @builtins.property
    @jsii.member(jsii_name="datapointsToAlarm")
    def datapoints_to_alarm(self) -> typing.Optional[jsii.Number]:
        '''(experimental) The number of datapoints to alarm on for latency and availability alarms.

        :stability: experimental
        '''
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "datapointsToAlarm"))

    @builtins.property
    @jsii.member(jsii_name="evaluationPeriods")
    def evaluation_periods(self) -> typing.Optional[jsii.Number]:
        '''(experimental) The number of evaluation periods for latency and availabiltiy alarms.

        :stability: experimental
        '''
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "evaluationPeriods"))

    @builtins.property
    @jsii.member(jsii_name="period")
    def period(self) -> typing.Optional[_aws_cdk_ceddda9d.Duration]:
        '''(experimental) The period for the metrics.

        :stability: experimental
        '''
        return typing.cast(typing.Optional[_aws_cdk_ceddda9d.Duration], jsii.get(self, "period"))

# Adding a "__jsii_proxy_class__(): typing.Type" function to the interface
typing.cast(typing.Any, ICanaryTestMetricsOverride).__jsii_proxy_class__ = lambda : _ICanaryTestMetricsOverrideProxy


@jsii.interface(
    jsii_type="@cdklabs/multi-az-observability.IContributorInsightRuleDetails"
)
class IContributorInsightRuleDetails(typing_extensions.Protocol):
    '''(experimental) Details for setting up Contributor Insight rules.

    :stability: experimental
    '''

    @builtins.property
    @jsii.member(jsii_name="availabilityZoneIdJsonPath")
    def availability_zone_id_json_path(self) -> builtins.str:
        '''(experimental) The path in the log files to the field that identifies the Availability Zone Id that the request was handled in, for example { "AZ-ID": "use1-az1" } would have a path of $.AZ-ID.

        :stability: experimental
        '''
        ...

    @builtins.property
    @jsii.member(jsii_name="faultMetricJsonPath")
    def fault_metric_json_path(self) -> builtins.str:
        '''(experimental) The path in the log files to the field that identifies if the response resulted in a fault, for example { "Fault" : 1 } would have a path of $.Fault.

        :stability: experimental
        '''
        ...

    @builtins.property
    @jsii.member(jsii_name="instanceIdJsonPath")
    def instance_id_json_path(self) -> builtins.str:
        '''(experimental) The JSON path to the instance id field in the log files, only required for server-side rules.

        :stability: experimental
        '''
        ...

    @builtins.property
    @jsii.member(jsii_name="logGroups")
    def log_groups(self) -> typing.List[_aws_cdk_aws_logs_ceddda9d.ILogGroup]:
        '''(experimental) The log groups where CloudWatch logs for the operation are located.

        If
        this is not provided, Contributor Insight rules cannot be created.

        :stability: experimental
        '''
        ...

    @builtins.property
    @jsii.member(jsii_name="operationNameJsonPath")
    def operation_name_json_path(self) -> builtins.str:
        '''(experimental) The path in the log files to the field that identifies the operation the log file is for.

        :stability: experimental
        '''
        ...

    @builtins.property
    @jsii.member(jsii_name="successLatencyMetricJsonPath")
    def success_latency_metric_json_path(self) -> builtins.str:
        '''(experimental) The path in the log files to the field that indicates the latency for the response.

        This could either be success latency or fault
        latency depending on the alarms and rules you are creating.

        :stability: experimental
        '''
        ...


class _IContributorInsightRuleDetailsProxy:
    '''(experimental) Details for setting up Contributor Insight rules.

    :stability: experimental
    '''

    __jsii_type__: typing.ClassVar[str] = "@cdklabs/multi-az-observability.IContributorInsightRuleDetails"

    @builtins.property
    @jsii.member(jsii_name="availabilityZoneIdJsonPath")
    def availability_zone_id_json_path(self) -> builtins.str:
        '''(experimental) The path in the log files to the field that identifies the Availability Zone Id that the request was handled in, for example { "AZ-ID": "use1-az1" } would have a path of $.AZ-ID.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "availabilityZoneIdJsonPath"))

    @builtins.property
    @jsii.member(jsii_name="faultMetricJsonPath")
    def fault_metric_json_path(self) -> builtins.str:
        '''(experimental) The path in the log files to the field that identifies if the response resulted in a fault, for example { "Fault" : 1 } would have a path of $.Fault.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "faultMetricJsonPath"))

    @builtins.property
    @jsii.member(jsii_name="instanceIdJsonPath")
    def instance_id_json_path(self) -> builtins.str:
        '''(experimental) The JSON path to the instance id field in the log files, only required for server-side rules.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "instanceIdJsonPath"))

    @builtins.property
    @jsii.member(jsii_name="logGroups")
    def log_groups(self) -> typing.List[_aws_cdk_aws_logs_ceddda9d.ILogGroup]:
        '''(experimental) The log groups where CloudWatch logs for the operation are located.

        If
        this is not provided, Contributor Insight rules cannot be created.

        :stability: experimental
        '''
        return typing.cast(typing.List[_aws_cdk_aws_logs_ceddda9d.ILogGroup], jsii.get(self, "logGroups"))

    @builtins.property
    @jsii.member(jsii_name="operationNameJsonPath")
    def operation_name_json_path(self) -> builtins.str:
        '''(experimental) The path in the log files to the field that identifies the operation the log file is for.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "operationNameJsonPath"))

    @builtins.property
    @jsii.member(jsii_name="successLatencyMetricJsonPath")
    def success_latency_metric_json_path(self) -> builtins.str:
        '''(experimental) The path in the log files to the field that indicates the latency for the response.

        This could either be success latency or fault
        latency depending on the alarms and rules you are creating.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "successLatencyMetricJsonPath"))

# Adding a "__jsii_proxy_class__(): typing.Type" function to the interface
typing.cast(typing.Any, IContributorInsightRuleDetails).__jsii_proxy_class__ = lambda : _IContributorInsightRuleDetailsProxy


@jsii.interface(
    jsii_type="@cdklabs/multi-az-observability.IInstrumentedServiceMultiAZObservability"
)
class IInstrumentedServiceMultiAZObservability(
    _constructs_77d1e7e8.IConstruct,
    typing_extensions.Protocol,
):
    '''(experimental) Observability for an instrumented service.

    :stability: experimental
    '''

    @builtins.property
    @jsii.member(jsii_name="perOperationAlarmsAndRules")
    def per_operation_alarms_and_rules(
        self,
    ) -> typing.Mapping[builtins.str, "IOperationAlarmsAndRules"]:
        '''(experimental) Key represents the operation name and the value is the set of zonal alarms and rules for that operation.

        You can get the
        granular alarms that compose the higher level aggregate alarms
        for each operation.

        :stability: experimental
        '''
        ...

    @builtins.property
    @jsii.member(jsii_name="perOperationZonalImpactAlarms")
    def per_operation_zonal_impact_alarms(
        self,
    ) -> typing.Mapping[builtins.str, typing.Mapping[builtins.str, _aws_cdk_aws_cloudwatch_ceddda9d.IAlarm]]:
        '''(experimental) Index into the dictionary by operation name, then by Availability Zone Name to get the alarms that indicate an AZ shows isolated impact from availability or latency as seen by either the server-side or canary.

        This is a shortcut to
        access the same alarms from the perOperationAlarmsAndRules property.

        :stability: experimental
        '''
        ...

    @builtins.property
    @jsii.member(jsii_name="serviceAlarms")
    def service_alarms(self) -> "IServiceAlarmsAndRules":
        '''(experimental) The alarms and rules for the overall service.

        :stability: experimental
        '''
        ...

    @builtins.property
    @jsii.member(jsii_name="canaryLogGroup")
    def canary_log_group(self) -> typing.Optional[_aws_cdk_aws_logs_ceddda9d.ILogGroup]:
        '''(experimental) If the service is configured to have canary tests created, this will be the log group where the canary's logs are stored.

        :default: - No log group is created if the canary is not requested.

        :stability: experimental
        '''
        ...

    @builtins.property
    @jsii.member(jsii_name="operationDashboards")
    def operation_dashboards(
        self,
    ) -> typing.Optional[typing.List[_aws_cdk_aws_cloudwatch_ceddda9d.Dashboard]]:
        '''(experimental) The dashboards for each operation.

        :stability: experimental
        '''
        ...

    @builtins.property
    @jsii.member(jsii_name="serviceDashboard")
    def service_dashboard(
        self,
    ) -> typing.Optional[_aws_cdk_aws_cloudwatch_ceddda9d.Dashboard]:
        '''(experimental) The service level dashboard.

        :stability: experimental
        '''
        ...


class _IInstrumentedServiceMultiAZObservabilityProxy(
    jsii.proxy_for(_constructs_77d1e7e8.IConstruct), # type: ignore[misc]
):
    '''(experimental) Observability for an instrumented service.

    :stability: experimental
    '''

    __jsii_type__: typing.ClassVar[str] = "@cdklabs/multi-az-observability.IInstrumentedServiceMultiAZObservability"

    @builtins.property
    @jsii.member(jsii_name="perOperationAlarmsAndRules")
    def per_operation_alarms_and_rules(
        self,
    ) -> typing.Mapping[builtins.str, "IOperationAlarmsAndRules"]:
        '''(experimental) Key represents the operation name and the value is the set of zonal alarms and rules for that operation.

        You can get the
        granular alarms that compose the higher level aggregate alarms
        for each operation.

        :stability: experimental
        '''
        return typing.cast(typing.Mapping[builtins.str, "IOperationAlarmsAndRules"], jsii.get(self, "perOperationAlarmsAndRules"))

    @builtins.property
    @jsii.member(jsii_name="perOperationZonalImpactAlarms")
    def per_operation_zonal_impact_alarms(
        self,
    ) -> typing.Mapping[builtins.str, typing.Mapping[builtins.str, _aws_cdk_aws_cloudwatch_ceddda9d.IAlarm]]:
        '''(experimental) Index into the dictionary by operation name, then by Availability Zone Name to get the alarms that indicate an AZ shows isolated impact from availability or latency as seen by either the server-side or canary.

        This is a shortcut to
        access the same alarms from the perOperationAlarmsAndRules property.

        :stability: experimental
        '''
        return typing.cast(typing.Mapping[builtins.str, typing.Mapping[builtins.str, _aws_cdk_aws_cloudwatch_ceddda9d.IAlarm]], jsii.get(self, "perOperationZonalImpactAlarms"))

    @builtins.property
    @jsii.member(jsii_name="serviceAlarms")
    def service_alarms(self) -> "IServiceAlarmsAndRules":
        '''(experimental) The alarms and rules for the overall service.

        :stability: experimental
        '''
        return typing.cast("IServiceAlarmsAndRules", jsii.get(self, "serviceAlarms"))

    @builtins.property
    @jsii.member(jsii_name="canaryLogGroup")
    def canary_log_group(self) -> typing.Optional[_aws_cdk_aws_logs_ceddda9d.ILogGroup]:
        '''(experimental) If the service is configured to have canary tests created, this will be the log group where the canary's logs are stored.

        :default: - No log group is created if the canary is not requested.

        :stability: experimental
        '''
        return typing.cast(typing.Optional[_aws_cdk_aws_logs_ceddda9d.ILogGroup], jsii.get(self, "canaryLogGroup"))

    @builtins.property
    @jsii.member(jsii_name="operationDashboards")
    def operation_dashboards(
        self,
    ) -> typing.Optional[typing.List[_aws_cdk_aws_cloudwatch_ceddda9d.Dashboard]]:
        '''(experimental) The dashboards for each operation.

        :stability: experimental
        '''
        return typing.cast(typing.Optional[typing.List[_aws_cdk_aws_cloudwatch_ceddda9d.Dashboard]], jsii.get(self, "operationDashboards"))

    @builtins.property
    @jsii.member(jsii_name="serviceDashboard")
    def service_dashboard(
        self,
    ) -> typing.Optional[_aws_cdk_aws_cloudwatch_ceddda9d.Dashboard]:
        '''(experimental) The service level dashboard.

        :stability: experimental
        '''
        return typing.cast(typing.Optional[_aws_cdk_aws_cloudwatch_ceddda9d.Dashboard], jsii.get(self, "serviceDashboard"))

# Adding a "__jsii_proxy_class__(): typing.Type" function to the interface
typing.cast(typing.Any, IInstrumentedServiceMultiAZObservability).__jsii_proxy_class__ = lambda : _IInstrumentedServiceMultiAZObservabilityProxy


@jsii.interface(jsii_type="@cdklabs/multi-az-observability.IOperation")
class IOperation(typing_extensions.Protocol):
    '''(experimental) Represents an operation in a service.

    :stability: experimental
    '''

    @builtins.property
    @jsii.member(jsii_name="critical")
    def critical(self) -> builtins.bool:
        '''(experimental) Indicates this is a critical operation for the service and will be included in service level metrics and dashboards.

        :stability: experimental
        '''
        ...

    @builtins.property
    @jsii.member(jsii_name="httpMethods")
    def http_methods(self) -> typing.List[builtins.str]:
        '''(experimental) The http methods supported by the operation.

        :stability: experimental
        '''
        ...

    @builtins.property
    @jsii.member(jsii_name="operationName")
    def operation_name(self) -> builtins.str:
        '''(experimental) The name of the operation.

        :stability: experimental
        '''
        ...

    @builtins.property
    @jsii.member(jsii_name="path")
    def path(self) -> builtins.str:
        '''(experimental) The HTTP path for the operation for canaries to run against, something like "/products/list".

        :stability: experimental
        '''
        ...

    @builtins.property
    @jsii.member(jsii_name="serverSideAvailabilityMetricDetails")
    def server_side_availability_metric_details(
        self,
    ) -> "IOperationAvailabilityMetricDetails":
        '''(experimental) The server side availability metric details.

        :stability: experimental
        '''
        ...

    @builtins.property
    @jsii.member(jsii_name="serverSideLatencyMetricDetails")
    def server_side_latency_metric_details(self) -> "IOperationLatencyMetricDetails":
        '''(experimental) The server side latency metric details.

        :stability: experimental
        '''
        ...

    @builtins.property
    @jsii.member(jsii_name="service")
    def service(self) -> "IService":
        '''(experimental) The service the operation is associated with.

        :stability: experimental
        '''
        ...

    @builtins.property
    @jsii.member(jsii_name="canaryMetricDetails")
    def canary_metric_details(self) -> typing.Optional[ICanaryMetrics]:
        '''(experimental) Optional metric details if the service has an existing canary.

        :stability: experimental
        '''
        ...

    @builtins.property
    @jsii.member(jsii_name="canaryTestAvailabilityMetricsOverride")
    def canary_test_availability_metrics_override(
        self,
    ) -> typing.Optional["ICanaryTestAvailabilityMetricsOverride"]:
        '''(experimental) The override values for automatically created canary tests so you can use values other than the service defaults to define the thresholds for availability.

        :stability: experimental
        '''
        ...

    @builtins.property
    @jsii.member(jsii_name="canaryTestLatencyMetricsOverride")
    def canary_test_latency_metrics_override(
        self,
    ) -> typing.Optional["ICanaryTestLatencyMetricsOverride"]:
        '''(experimental) The override values for automatically created canary tests so you can use values other than the service defaults to define the thresholds for latency.

        :stability: experimental
        '''
        ...

    @builtins.property
    @jsii.member(jsii_name="canaryTestProps")
    def canary_test_props(self) -> typing.Optional[AddCanaryTestProps]:
        '''(experimental) If they have been added, the properties for creating new canary tests on this operation.

        :stability: experimental
        '''
        ...

    @builtins.property
    @jsii.member(jsii_name="optOutOfServiceCreatedCanary")
    def opt_out_of_service_created_canary(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Set to true if you have defined CanaryTestProps for your service, which applies to all operations, but you want to opt out of creating the canary test for this operation.

        :default: - The operation is not opted out

        :stability: experimental
        '''
        ...

    @builtins.property
    @jsii.member(jsii_name="serverSideContributorInsightRuleDetails")
    def server_side_contributor_insight_rule_details(
        self,
    ) -> typing.Optional[IContributorInsightRuleDetails]:
        '''(experimental) The server side details for contributor insights rules.

        :stability: experimental
        '''
        ...


class _IOperationProxy:
    '''(experimental) Represents an operation in a service.

    :stability: experimental
    '''

    __jsii_type__: typing.ClassVar[str] = "@cdklabs/multi-az-observability.IOperation"

    @builtins.property
    @jsii.member(jsii_name="critical")
    def critical(self) -> builtins.bool:
        '''(experimental) Indicates this is a critical operation for the service and will be included in service level metrics and dashboards.

        :stability: experimental
        '''
        return typing.cast(builtins.bool, jsii.get(self, "critical"))

    @builtins.property
    @jsii.member(jsii_name="httpMethods")
    def http_methods(self) -> typing.List[builtins.str]:
        '''(experimental) The http methods supported by the operation.

        :stability: experimental
        '''
        return typing.cast(typing.List[builtins.str], jsii.get(self, "httpMethods"))

    @builtins.property
    @jsii.member(jsii_name="operationName")
    def operation_name(self) -> builtins.str:
        '''(experimental) The name of the operation.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "operationName"))

    @builtins.property
    @jsii.member(jsii_name="path")
    def path(self) -> builtins.str:
        '''(experimental) The HTTP path for the operation for canaries to run against, something like "/products/list".

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "path"))

    @builtins.property
    @jsii.member(jsii_name="serverSideAvailabilityMetricDetails")
    def server_side_availability_metric_details(
        self,
    ) -> "IOperationAvailabilityMetricDetails":
        '''(experimental) The server side availability metric details.

        :stability: experimental
        '''
        return typing.cast("IOperationAvailabilityMetricDetails", jsii.get(self, "serverSideAvailabilityMetricDetails"))

    @builtins.property
    @jsii.member(jsii_name="serverSideLatencyMetricDetails")
    def server_side_latency_metric_details(self) -> "IOperationLatencyMetricDetails":
        '''(experimental) The server side latency metric details.

        :stability: experimental
        '''
        return typing.cast("IOperationLatencyMetricDetails", jsii.get(self, "serverSideLatencyMetricDetails"))

    @builtins.property
    @jsii.member(jsii_name="service")
    def service(self) -> "IService":
        '''(experimental) The service the operation is associated with.

        :stability: experimental
        '''
        return typing.cast("IService", jsii.get(self, "service"))

    @builtins.property
    @jsii.member(jsii_name="canaryMetricDetails")
    def canary_metric_details(self) -> typing.Optional[ICanaryMetrics]:
        '''(experimental) Optional metric details if the service has an existing canary.

        :stability: experimental
        '''
        return typing.cast(typing.Optional[ICanaryMetrics], jsii.get(self, "canaryMetricDetails"))

    @builtins.property
    @jsii.member(jsii_name="canaryTestAvailabilityMetricsOverride")
    def canary_test_availability_metrics_override(
        self,
    ) -> typing.Optional["ICanaryTestAvailabilityMetricsOverride"]:
        '''(experimental) The override values for automatically created canary tests so you can use values other than the service defaults to define the thresholds for availability.

        :stability: experimental
        '''
        return typing.cast(typing.Optional["ICanaryTestAvailabilityMetricsOverride"], jsii.get(self, "canaryTestAvailabilityMetricsOverride"))

    @builtins.property
    @jsii.member(jsii_name="canaryTestLatencyMetricsOverride")
    def canary_test_latency_metrics_override(
        self,
    ) -> typing.Optional["ICanaryTestLatencyMetricsOverride"]:
        '''(experimental) The override values for automatically created canary tests so you can use values other than the service defaults to define the thresholds for latency.

        :stability: experimental
        '''
        return typing.cast(typing.Optional["ICanaryTestLatencyMetricsOverride"], jsii.get(self, "canaryTestLatencyMetricsOverride"))

    @builtins.property
    @jsii.member(jsii_name="canaryTestProps")
    def canary_test_props(self) -> typing.Optional[AddCanaryTestProps]:
        '''(experimental) If they have been added, the properties for creating new canary tests on this operation.

        :stability: experimental
        '''
        return typing.cast(typing.Optional[AddCanaryTestProps], jsii.get(self, "canaryTestProps"))

    @builtins.property
    @jsii.member(jsii_name="optOutOfServiceCreatedCanary")
    def opt_out_of_service_created_canary(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Set to true if you have defined CanaryTestProps for your service, which applies to all operations, but you want to opt out of creating the canary test for this operation.

        :default: - The operation is not opted out

        :stability: experimental
        '''
        return typing.cast(typing.Optional[builtins.bool], jsii.get(self, "optOutOfServiceCreatedCanary"))

    @builtins.property
    @jsii.member(jsii_name="serverSideContributorInsightRuleDetails")
    def server_side_contributor_insight_rule_details(
        self,
    ) -> typing.Optional[IContributorInsightRuleDetails]:
        '''(experimental) The server side details for contributor insights rules.

        :stability: experimental
        '''
        return typing.cast(typing.Optional[IContributorInsightRuleDetails], jsii.get(self, "serverSideContributorInsightRuleDetails"))

# Adding a "__jsii_proxy_class__(): typing.Type" function to the interface
typing.cast(typing.Any, IOperation).__jsii_proxy_class__ = lambda : _IOperationProxy


@jsii.interface(jsii_type="@cdklabs/multi-az-observability.IOperationAlarmsAndRules")
class IOperationAlarmsAndRules(typing_extensions.Protocol):
    '''(experimental) Creates alarms and rules for an operation for both regional and zonal metrics.

    :stability: experimental
    '''

    @builtins.property
    @jsii.member(jsii_name="aggregateZonalAlarms")
    def aggregate_zonal_alarms(
        self,
    ) -> typing.Mapping[builtins.str, _aws_cdk_aws_cloudwatch_ceddda9d.IAlarm]:
        '''(experimental) The aggregate, server-side and canary combined, zonal alarm indexed by Availability Zone name.

        :stability: experimental
        '''
        ...

    @builtins.property
    @jsii.member(jsii_name="operation")
    def operation(self) -> IOperation:
        '''(experimental) The operation the alarms and rules are created for.

        :stability: experimental
        '''
        ...

    @builtins.property
    @jsii.member(jsii_name="regionalImpactAlarm")
    def regional_impact_alarm(self) -> _aws_cdk_aws_cloudwatch_ceddda9d.IAlarm:
        '''(experimental) An alarm indicating availability or latency impact has been detected by the server-side  and/or canary (if present) and the impact is regionally scoped, not zonal.

        :stability: experimental
        '''
        ...

    @builtins.property
    @jsii.member(jsii_name="serverSideRegionalAlarmsAndRules")
    def server_side_regional_alarms_and_rules(
        self,
    ) -> "IServerSideOperationRegionalAlarmsAndRules":
        '''(experimental) The server side regional alarms and rules.

        :stability: experimental
        '''
        ...

    @builtins.property
    @jsii.member(jsii_name="serverSideRegionalImpactAlarm")
    def server_side_regional_impact_alarm(
        self,
    ) -> _aws_cdk_aws_cloudwatch_ceddda9d.IAlarm:
        '''(experimental) An alarm indicating availability or latency impact has been detected by the server-side and the impact is regionally scoped, not zonal.

        :stability: experimental
        '''
        ...

    @builtins.property
    @jsii.member(jsii_name="serverSideZonalAlarmsAndRules")
    def server_side_zonal_alarms_and_rules(
        self,
    ) -> typing.Mapping[builtins.str, "IServerSideOperationZonalAlarmsAndRules"]:
        '''(experimental) The server side zonal alarms and rules, indexed by Availability Zone name.

        :stability: experimental
        '''
        ...

    @builtins.property
    @jsii.member(jsii_name="canaryRegionalAlarmsAndRules")
    def canary_regional_alarms_and_rules(
        self,
    ) -> typing.Optional[ICanaryOperationRegionalAlarmsAndRules]:
        '''(experimental) The canary regional alarms and rules.

        :stability: experimental
        '''
        ...

    @builtins.property
    @jsii.member(jsii_name="canaryRegionalImpactAlarm")
    def canary_regional_impact_alarm(
        self,
    ) -> typing.Optional[_aws_cdk_aws_cloudwatch_ceddda9d.IAlarm]:
        '''(experimental) An alarm indicating availability or latency impact has been detected by the canary and the impact is regionally scoped, not zonal.

        :stability: experimental
        '''
        ...

    @builtins.property
    @jsii.member(jsii_name="canaryZonalAlarmsAndRules")
    def canary_zonal_alarms_and_rules(
        self,
    ) -> typing.Optional[typing.Mapping[builtins.str, ICanaryOperationZonalAlarmsAndRules]]:
        '''(experimental) The canary zonal alarms and rules, indexed by Availability Zone name.

        :default: - This is an empty dictionary if canary metric details are not provided

        :stability: experimental
        '''
        ...


class _IOperationAlarmsAndRulesProxy:
    '''(experimental) Creates alarms and rules for an operation for both regional and zonal metrics.

    :stability: experimental
    '''

    __jsii_type__: typing.ClassVar[str] = "@cdklabs/multi-az-observability.IOperationAlarmsAndRules"

    @builtins.property
    @jsii.member(jsii_name="aggregateZonalAlarms")
    def aggregate_zonal_alarms(
        self,
    ) -> typing.Mapping[builtins.str, _aws_cdk_aws_cloudwatch_ceddda9d.IAlarm]:
        '''(experimental) The aggregate, server-side and canary combined, zonal alarm indexed by Availability Zone name.

        :stability: experimental
        '''
        return typing.cast(typing.Mapping[builtins.str, _aws_cdk_aws_cloudwatch_ceddda9d.IAlarm], jsii.get(self, "aggregateZonalAlarms"))

    @builtins.property
    @jsii.member(jsii_name="operation")
    def operation(self) -> IOperation:
        '''(experimental) The operation the alarms and rules are created for.

        :stability: experimental
        '''
        return typing.cast(IOperation, jsii.get(self, "operation"))

    @builtins.property
    @jsii.member(jsii_name="regionalImpactAlarm")
    def regional_impact_alarm(self) -> _aws_cdk_aws_cloudwatch_ceddda9d.IAlarm:
        '''(experimental) An alarm indicating availability or latency impact has been detected by the server-side  and/or canary (if present) and the impact is regionally scoped, not zonal.

        :stability: experimental
        '''
        return typing.cast(_aws_cdk_aws_cloudwatch_ceddda9d.IAlarm, jsii.get(self, "regionalImpactAlarm"))

    @builtins.property
    @jsii.member(jsii_name="serverSideRegionalAlarmsAndRules")
    def server_side_regional_alarms_and_rules(
        self,
    ) -> "IServerSideOperationRegionalAlarmsAndRules":
        '''(experimental) The server side regional alarms and rules.

        :stability: experimental
        '''
        return typing.cast("IServerSideOperationRegionalAlarmsAndRules", jsii.get(self, "serverSideRegionalAlarmsAndRules"))

    @builtins.property
    @jsii.member(jsii_name="serverSideRegionalImpactAlarm")
    def server_side_regional_impact_alarm(
        self,
    ) -> _aws_cdk_aws_cloudwatch_ceddda9d.IAlarm:
        '''(experimental) An alarm indicating availability or latency impact has been detected by the server-side and the impact is regionally scoped, not zonal.

        :stability: experimental
        '''
        return typing.cast(_aws_cdk_aws_cloudwatch_ceddda9d.IAlarm, jsii.get(self, "serverSideRegionalImpactAlarm"))

    @builtins.property
    @jsii.member(jsii_name="serverSideZonalAlarmsAndRules")
    def server_side_zonal_alarms_and_rules(
        self,
    ) -> typing.Mapping[builtins.str, "IServerSideOperationZonalAlarmsAndRules"]:
        '''(experimental) The server side zonal alarms and rules, indexed by Availability Zone name.

        :stability: experimental
        '''
        return typing.cast(typing.Mapping[builtins.str, "IServerSideOperationZonalAlarmsAndRules"], jsii.get(self, "serverSideZonalAlarmsAndRules"))

    @builtins.property
    @jsii.member(jsii_name="canaryRegionalAlarmsAndRules")
    def canary_regional_alarms_and_rules(
        self,
    ) -> typing.Optional[ICanaryOperationRegionalAlarmsAndRules]:
        '''(experimental) The canary regional alarms and rules.

        :stability: experimental
        '''
        return typing.cast(typing.Optional[ICanaryOperationRegionalAlarmsAndRules], jsii.get(self, "canaryRegionalAlarmsAndRules"))

    @builtins.property
    @jsii.member(jsii_name="canaryRegionalImpactAlarm")
    def canary_regional_impact_alarm(
        self,
    ) -> typing.Optional[_aws_cdk_aws_cloudwatch_ceddda9d.IAlarm]:
        '''(experimental) An alarm indicating availability or latency impact has been detected by the canary and the impact is regionally scoped, not zonal.

        :stability: experimental
        '''
        return typing.cast(typing.Optional[_aws_cdk_aws_cloudwatch_ceddda9d.IAlarm], jsii.get(self, "canaryRegionalImpactAlarm"))

    @builtins.property
    @jsii.member(jsii_name="canaryZonalAlarmsAndRules")
    def canary_zonal_alarms_and_rules(
        self,
    ) -> typing.Optional[typing.Mapping[builtins.str, ICanaryOperationZonalAlarmsAndRules]]:
        '''(experimental) The canary zonal alarms and rules, indexed by Availability Zone name.

        :default: - This is an empty dictionary if canary metric details are not provided

        :stability: experimental
        '''
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, ICanaryOperationZonalAlarmsAndRules]], jsii.get(self, "canaryZonalAlarmsAndRules"))

# Adding a "__jsii_proxy_class__(): typing.Type" function to the interface
typing.cast(typing.Any, IOperationAlarmsAndRules).__jsii_proxy_class__ = lambda : _IOperationAlarmsAndRulesProxy


@jsii.interface(jsii_type="@cdklabs/multi-az-observability.IOperationMetricDetails")
class IOperationMetricDetails(typing_extensions.Protocol):
    '''(experimental) Details for operation metrics in one perspective, such as server side latency.

    :stability: experimental
    '''

    @builtins.property
    @jsii.member(jsii_name="alarmStatistic")
    def alarm_statistic(self) -> builtins.str:
        '''(experimental) The statistic used for alarms, for availability metrics this should be "Sum", for latency metrics it could something like "p99" or "p99.9".

        :stability: experimental
        '''
        ...

    @builtins.property
    @jsii.member(jsii_name="datapointsToAlarm")
    def datapoints_to_alarm(self) -> jsii.Number:
        '''(experimental) The number of datapoints to alarm on for latency and availability alarms.

        :stability: experimental
        '''
        ...

    @builtins.property
    @jsii.member(jsii_name="evaluationPeriods")
    def evaluation_periods(self) -> jsii.Number:
        '''(experimental) The number of evaluation periods for latency and availabiltiy alarms.

        :stability: experimental
        '''
        ...

    @builtins.property
    @jsii.member(jsii_name="faultMetricNames")
    def fault_metric_names(self) -> typing.List[builtins.str]:
        '''(experimental) The names of fault indicating metrics.

        :stability: experimental
        '''
        ...

    @builtins.property
    @jsii.member(jsii_name="metricDimensions")
    def metric_dimensions(self) -> "MetricDimensions":
        '''(experimental) The metric dimensions for this operation, must be implemented as a concrete class by the user.

        :stability: experimental
        '''
        ...

    @builtins.property
    @jsii.member(jsii_name="metricNamespace")
    def metric_namespace(self) -> builtins.str:
        '''(experimental) The CloudWatch metric namespace for these metrics.

        :stability: experimental
        '''
        ...

    @builtins.property
    @jsii.member(jsii_name="operationName")
    def operation_name(self) -> builtins.str:
        '''(experimental) The operation these metric details are for.

        :stability: experimental
        '''
        ...

    @builtins.property
    @jsii.member(jsii_name="period")
    def period(self) -> _aws_cdk_ceddda9d.Duration:
        '''(experimental) The period for the metrics.

        :stability: experimental
        '''
        ...

    @builtins.property
    @jsii.member(jsii_name="successMetricNames")
    def success_metric_names(self) -> typing.List[builtins.str]:
        '''(experimental) The names of success indicating metrics.

        :stability: experimental
        '''
        ...

    @builtins.property
    @jsii.member(jsii_name="unit")
    def unit(self) -> _aws_cdk_aws_cloudwatch_ceddda9d.Unit:
        '''(experimental) The unit used for these metrics.

        :stability: experimental
        '''
        ...

    @builtins.property
    @jsii.member(jsii_name="graphedFaultStatistics")
    def graphed_fault_statistics(self) -> typing.Optional[typing.List[builtins.str]]:
        '''(experimental) The statistics for faults you want to appear on dashboards, for example, with latency metrics, you might want p50, p99, and tm99.

        For availability
        metrics this will typically just be "Sum".

        :default: - For availability metrics, this will be "Sum", for latency metrics it will be just "p99"

        :stability: experimental
        '''
        ...

    @builtins.property
    @jsii.member(jsii_name="graphedSuccessStatistics")
    def graphed_success_statistics(self) -> typing.Optional[typing.List[builtins.str]]:
        '''(experimental) The statistics for successes you want to appear on dashboards, for example, with latency metrics, you might want p50, p99, and tm99.

        For availability
        metrics this will typically just be "Sum".

        :default: - For availability metrics, this will be "Sum", for latency metrics it will be just "p99"

        :stability: experimental
        '''
        ...


class _IOperationMetricDetailsProxy:
    '''(experimental) Details for operation metrics in one perspective, such as server side latency.

    :stability: experimental
    '''

    __jsii_type__: typing.ClassVar[str] = "@cdklabs/multi-az-observability.IOperationMetricDetails"

    @builtins.property
    @jsii.member(jsii_name="alarmStatistic")
    def alarm_statistic(self) -> builtins.str:
        '''(experimental) The statistic used for alarms, for availability metrics this should be "Sum", for latency metrics it could something like "p99" or "p99.9".

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "alarmStatistic"))

    @builtins.property
    @jsii.member(jsii_name="datapointsToAlarm")
    def datapoints_to_alarm(self) -> jsii.Number:
        '''(experimental) The number of datapoints to alarm on for latency and availability alarms.

        :stability: experimental
        '''
        return typing.cast(jsii.Number, jsii.get(self, "datapointsToAlarm"))

    @builtins.property
    @jsii.member(jsii_name="evaluationPeriods")
    def evaluation_periods(self) -> jsii.Number:
        '''(experimental) The number of evaluation periods for latency and availabiltiy alarms.

        :stability: experimental
        '''
        return typing.cast(jsii.Number, jsii.get(self, "evaluationPeriods"))

    @builtins.property
    @jsii.member(jsii_name="faultMetricNames")
    def fault_metric_names(self) -> typing.List[builtins.str]:
        '''(experimental) The names of fault indicating metrics.

        :stability: experimental
        '''
        return typing.cast(typing.List[builtins.str], jsii.get(self, "faultMetricNames"))

    @builtins.property
    @jsii.member(jsii_name="metricDimensions")
    def metric_dimensions(self) -> "MetricDimensions":
        '''(experimental) The metric dimensions for this operation, must be implemented as a concrete class by the user.

        :stability: experimental
        '''
        return typing.cast("MetricDimensions", jsii.get(self, "metricDimensions"))

    @builtins.property
    @jsii.member(jsii_name="metricNamespace")
    def metric_namespace(self) -> builtins.str:
        '''(experimental) The CloudWatch metric namespace for these metrics.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "metricNamespace"))

    @builtins.property
    @jsii.member(jsii_name="operationName")
    def operation_name(self) -> builtins.str:
        '''(experimental) The operation these metric details are for.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "operationName"))

    @builtins.property
    @jsii.member(jsii_name="period")
    def period(self) -> _aws_cdk_ceddda9d.Duration:
        '''(experimental) The period for the metrics.

        :stability: experimental
        '''
        return typing.cast(_aws_cdk_ceddda9d.Duration, jsii.get(self, "period"))

    @builtins.property
    @jsii.member(jsii_name="successMetricNames")
    def success_metric_names(self) -> typing.List[builtins.str]:
        '''(experimental) The names of success indicating metrics.

        :stability: experimental
        '''
        return typing.cast(typing.List[builtins.str], jsii.get(self, "successMetricNames"))

    @builtins.property
    @jsii.member(jsii_name="unit")
    def unit(self) -> _aws_cdk_aws_cloudwatch_ceddda9d.Unit:
        '''(experimental) The unit used for these metrics.

        :stability: experimental
        '''
        return typing.cast(_aws_cdk_aws_cloudwatch_ceddda9d.Unit, jsii.get(self, "unit"))

    @builtins.property
    @jsii.member(jsii_name="graphedFaultStatistics")
    def graphed_fault_statistics(self) -> typing.Optional[typing.List[builtins.str]]:
        '''(experimental) The statistics for faults you want to appear on dashboards, for example, with latency metrics, you might want p50, p99, and tm99.

        For availability
        metrics this will typically just be "Sum".

        :default: - For availability metrics, this will be "Sum", for latency metrics it will be just "p99"

        :stability: experimental
        '''
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "graphedFaultStatistics"))

    @builtins.property
    @jsii.member(jsii_name="graphedSuccessStatistics")
    def graphed_success_statistics(self) -> typing.Optional[typing.List[builtins.str]]:
        '''(experimental) The statistics for successes you want to appear on dashboards, for example, with latency metrics, you might want p50, p99, and tm99.

        For availability
        metrics this will typically just be "Sum".

        :default: - For availability metrics, this will be "Sum", for latency metrics it will be just "p99"

        :stability: experimental
        '''
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "graphedSuccessStatistics"))

# Adding a "__jsii_proxy_class__(): typing.Type" function to the interface
typing.cast(typing.Any, IOperationMetricDetails).__jsii_proxy_class__ = lambda : _IOperationMetricDetailsProxy


@jsii.interface(
    jsii_type="@cdklabs/multi-az-observability.IServerSideOperationRegionalAlarmsAndRules"
)
class IServerSideOperationRegionalAlarmsAndRules(
    IBaseOperationRegionalAlarmsAndRules,
    typing_extensions.Protocol,
):
    '''(experimental) The server side operation regional alarms and rules.

    :stability: experimental
    '''

    @builtins.property
    @jsii.member(jsii_name="instanceContributorsToRegionalFaults")
    def instance_contributors_to_regional_faults(
        self,
    ) -> typing.Optional[_aws_cdk_aws_cloudwatch_ceddda9d.CfnInsightRule]:
        '''(experimental) A rule that shows which instances are contributing to faults.

        :stability: experimental
        '''
        ...

    @instance_contributors_to_regional_faults.setter
    def instance_contributors_to_regional_faults(
        self,
        value: typing.Optional[_aws_cdk_aws_cloudwatch_ceddda9d.CfnInsightRule],
    ) -> None:
        ...

    @builtins.property
    @jsii.member(jsii_name="instanceContributorsToRegionalHighLatency")
    def instance_contributors_to_regional_high_latency(
        self,
    ) -> typing.Optional[_aws_cdk_aws_cloudwatch_ceddda9d.CfnInsightRule]:
        '''(experimental) A rule that shows which instances are contributing to high latency responses.

        :stability: experimental
        '''
        ...

    @instance_contributors_to_regional_high_latency.setter
    def instance_contributors_to_regional_high_latency(
        self,
        value: typing.Optional[_aws_cdk_aws_cloudwatch_ceddda9d.CfnInsightRule],
    ) -> None:
        ...


class _IServerSideOperationRegionalAlarmsAndRulesProxy(
    jsii.proxy_for(IBaseOperationRegionalAlarmsAndRules), # type: ignore[misc]
):
    '''(experimental) The server side operation regional alarms and rules.

    :stability: experimental
    '''

    __jsii_type__: typing.ClassVar[str] = "@cdklabs/multi-az-observability.IServerSideOperationRegionalAlarmsAndRules"

    @builtins.property
    @jsii.member(jsii_name="instanceContributorsToRegionalFaults")
    def instance_contributors_to_regional_faults(
        self,
    ) -> typing.Optional[_aws_cdk_aws_cloudwatch_ceddda9d.CfnInsightRule]:
        '''(experimental) A rule that shows which instances are contributing to faults.

        :stability: experimental
        '''
        return typing.cast(typing.Optional[_aws_cdk_aws_cloudwatch_ceddda9d.CfnInsightRule], jsii.get(self, "instanceContributorsToRegionalFaults"))

    @instance_contributors_to_regional_faults.setter
    def instance_contributors_to_regional_faults(
        self,
        value: typing.Optional[_aws_cdk_aws_cloudwatch_ceddda9d.CfnInsightRule],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f3731e5254b7ee08eb4786a65612c2a604de368a146e9e2bdbb5bf339a2c1b71)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "instanceContributorsToRegionalFaults", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="instanceContributorsToRegionalHighLatency")
    def instance_contributors_to_regional_high_latency(
        self,
    ) -> typing.Optional[_aws_cdk_aws_cloudwatch_ceddda9d.CfnInsightRule]:
        '''(experimental) A rule that shows which instances are contributing to high latency responses.

        :stability: experimental
        '''
        return typing.cast(typing.Optional[_aws_cdk_aws_cloudwatch_ceddda9d.CfnInsightRule], jsii.get(self, "instanceContributorsToRegionalHighLatency"))

    @instance_contributors_to_regional_high_latency.setter
    def instance_contributors_to_regional_high_latency(
        self,
        value: typing.Optional[_aws_cdk_aws_cloudwatch_ceddda9d.CfnInsightRule],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b29a1c24e783c9691ec1cb2f40b5f1a99b4d4870af674effec237e9477ce5bf8)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "instanceContributorsToRegionalHighLatency", value) # pyright: ignore[reportArgumentType]

# Adding a "__jsii_proxy_class__(): typing.Type" function to the interface
typing.cast(typing.Any, IServerSideOperationRegionalAlarmsAndRules).__jsii_proxy_class__ = lambda : _IServerSideOperationRegionalAlarmsAndRulesProxy


@jsii.interface(
    jsii_type="@cdklabs/multi-az-observability.IServerSideOperationZonalAlarmsAndRules"
)
class IServerSideOperationZonalAlarmsAndRules(
    IBaseOperationZonalAlarmsAndRules,
    typing_extensions.Protocol,
):
    '''(experimental) Server side opertaion zonal alarms and rules.

    :stability: experimental
    '''

    @builtins.property
    @jsii.member(jsii_name="isolatedImpactAlarm")
    def isolated_impact_alarm(self) -> _aws_cdk_aws_cloudwatch_ceddda9d.IAlarm:
        '''(experimental) Alarm that triggers if either latency or availability breach the specified threshold in this AZ and the AZ is an outlier for faults or latency.

        :stability: experimental
        '''
        ...

    @isolated_impact_alarm.setter
    def isolated_impact_alarm(
        self,
        value: _aws_cdk_aws_cloudwatch_ceddda9d.IAlarm,
    ) -> None:
        ...

    @builtins.property
    @jsii.member(jsii_name="instanceContributorsToFaultsInThisAZ")
    def instance_contributors_to_faults_in_this_az(
        self,
    ) -> typing.Optional[_aws_cdk_aws_cloudwatch_ceddda9d.CfnInsightRule]:
        '''(experimental) Insight rule that measures the number of instances contributing to faults in this AZ.

        :stability: experimental
        '''
        ...

    @instance_contributors_to_faults_in_this_az.setter
    def instance_contributors_to_faults_in_this_az(
        self,
        value: typing.Optional[_aws_cdk_aws_cloudwatch_ceddda9d.CfnInsightRule],
    ) -> None:
        ...

    @builtins.property
    @jsii.member(jsii_name="instanceContributorsToHighLatencyInThisAZ")
    def instance_contributors_to_high_latency_in_this_az(
        self,
    ) -> typing.Optional[_aws_cdk_aws_cloudwatch_ceddda9d.CfnInsightRule]:
        '''(experimental) Insight rule that measures the number of instances contributing to high latency in this AZ.

        :stability: experimental
        '''
        ...

    @instance_contributors_to_high_latency_in_this_az.setter
    def instance_contributors_to_high_latency_in_this_az(
        self,
        value: typing.Optional[_aws_cdk_aws_cloudwatch_ceddda9d.CfnInsightRule],
    ) -> None:
        ...

    @builtins.property
    @jsii.member(jsii_name="instancesHandlingRequestsInThisAZ")
    def instances_handling_requests_in_this_az(
        self,
    ) -> typing.Optional[_aws_cdk_aws_cloudwatch_ceddda9d.CfnInsightRule]:
        '''(experimental) Insight rule that is used to calculate the number of instances in this particular AZ that is used with metric math to calculate the percent of instances contributing to latency or faults.

        :stability: experimental
        '''
        ...

    @instances_handling_requests_in_this_az.setter
    def instances_handling_requests_in_this_az(
        self,
        value: typing.Optional[_aws_cdk_aws_cloudwatch_ceddda9d.CfnInsightRule],
    ) -> None:
        ...

    @builtins.property
    @jsii.member(jsii_name="multipleInstancesProducingFaultsInThisAvailabilityZone")
    def multiple_instances_producing_faults_in_this_availability_zone(
        self,
    ) -> typing.Optional[_aws_cdk_aws_cloudwatch_ceddda9d.IAlarm]:
        '''(experimental) Alarm indicating that there are multiple instances producing faults in this AZ indicating the fault rate is not being caused by a single instance.

        :stability: experimental
        '''
        ...

    @multiple_instances_producing_faults_in_this_availability_zone.setter
    def multiple_instances_producing_faults_in_this_availability_zone(
        self,
        value: typing.Optional[_aws_cdk_aws_cloudwatch_ceddda9d.IAlarm],
    ) -> None:
        ...

    @builtins.property
    @jsii.member(jsii_name="multipleInstancesProducingHighLatencyInThisAZ")
    def multiple_instances_producing_high_latency_in_this_az(
        self,
    ) -> typing.Optional[_aws_cdk_aws_cloudwatch_ceddda9d.IAlarm]:
        '''(experimental) Alarm indicating that there are multiple instances producing high latency responses in this AZ indicating the latency is not being caused by a single instance.

        :stability: experimental
        '''
        ...

    @multiple_instances_producing_high_latency_in_this_az.setter
    def multiple_instances_producing_high_latency_in_this_az(
        self,
        value: typing.Optional[_aws_cdk_aws_cloudwatch_ceddda9d.IAlarm],
    ) -> None:
        ...


class _IServerSideOperationZonalAlarmsAndRulesProxy(
    jsii.proxy_for(IBaseOperationZonalAlarmsAndRules), # type: ignore[misc]
):
    '''(experimental) Server side opertaion zonal alarms and rules.

    :stability: experimental
    '''

    __jsii_type__: typing.ClassVar[str] = "@cdklabs/multi-az-observability.IServerSideOperationZonalAlarmsAndRules"

    @builtins.property
    @jsii.member(jsii_name="isolatedImpactAlarm")
    def isolated_impact_alarm(self) -> _aws_cdk_aws_cloudwatch_ceddda9d.IAlarm:
        '''(experimental) Alarm that triggers if either latency or availability breach the specified threshold in this AZ and the AZ is an outlier for faults or latency.

        :stability: experimental
        '''
        return typing.cast(_aws_cdk_aws_cloudwatch_ceddda9d.IAlarm, jsii.get(self, "isolatedImpactAlarm"))

    @isolated_impact_alarm.setter
    def isolated_impact_alarm(
        self,
        value: _aws_cdk_aws_cloudwatch_ceddda9d.IAlarm,
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__cda6f011758bcaa01bb1134e2bfb4b7093bfa3971462539d142fdba80745fe91)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "isolatedImpactAlarm", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="instanceContributorsToFaultsInThisAZ")
    def instance_contributors_to_faults_in_this_az(
        self,
    ) -> typing.Optional[_aws_cdk_aws_cloudwatch_ceddda9d.CfnInsightRule]:
        '''(experimental) Insight rule that measures the number of instances contributing to faults in this AZ.

        :stability: experimental
        '''
        return typing.cast(typing.Optional[_aws_cdk_aws_cloudwatch_ceddda9d.CfnInsightRule], jsii.get(self, "instanceContributorsToFaultsInThisAZ"))

    @instance_contributors_to_faults_in_this_az.setter
    def instance_contributors_to_faults_in_this_az(
        self,
        value: typing.Optional[_aws_cdk_aws_cloudwatch_ceddda9d.CfnInsightRule],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c22e757753f2980033d3ee81d4db89564cf7262bb7d7ac8894aa77ba67846722)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "instanceContributorsToFaultsInThisAZ", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="instanceContributorsToHighLatencyInThisAZ")
    def instance_contributors_to_high_latency_in_this_az(
        self,
    ) -> typing.Optional[_aws_cdk_aws_cloudwatch_ceddda9d.CfnInsightRule]:
        '''(experimental) Insight rule that measures the number of instances contributing to high latency in this AZ.

        :stability: experimental
        '''
        return typing.cast(typing.Optional[_aws_cdk_aws_cloudwatch_ceddda9d.CfnInsightRule], jsii.get(self, "instanceContributorsToHighLatencyInThisAZ"))

    @instance_contributors_to_high_latency_in_this_az.setter
    def instance_contributors_to_high_latency_in_this_az(
        self,
        value: typing.Optional[_aws_cdk_aws_cloudwatch_ceddda9d.CfnInsightRule],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__80613ae1711b8221870139d7b53d22fe4fc2e22fee224ce46e866eeee886cbf3)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "instanceContributorsToHighLatencyInThisAZ", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="instancesHandlingRequestsInThisAZ")
    def instances_handling_requests_in_this_az(
        self,
    ) -> typing.Optional[_aws_cdk_aws_cloudwatch_ceddda9d.CfnInsightRule]:
        '''(experimental) Insight rule that is used to calculate the number of instances in this particular AZ that is used with metric math to calculate the percent of instances contributing to latency or faults.

        :stability: experimental
        '''
        return typing.cast(typing.Optional[_aws_cdk_aws_cloudwatch_ceddda9d.CfnInsightRule], jsii.get(self, "instancesHandlingRequestsInThisAZ"))

    @instances_handling_requests_in_this_az.setter
    def instances_handling_requests_in_this_az(
        self,
        value: typing.Optional[_aws_cdk_aws_cloudwatch_ceddda9d.CfnInsightRule],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b86f9612bc48c2143188d89622279986e81017cbae19e0f1e20269628149a7a6)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "instancesHandlingRequestsInThisAZ", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="multipleInstancesProducingFaultsInThisAvailabilityZone")
    def multiple_instances_producing_faults_in_this_availability_zone(
        self,
    ) -> typing.Optional[_aws_cdk_aws_cloudwatch_ceddda9d.IAlarm]:
        '''(experimental) Alarm indicating that there are multiple instances producing faults in this AZ indicating the fault rate is not being caused by a single instance.

        :stability: experimental
        '''
        return typing.cast(typing.Optional[_aws_cdk_aws_cloudwatch_ceddda9d.IAlarm], jsii.get(self, "multipleInstancesProducingFaultsInThisAvailabilityZone"))

    @multiple_instances_producing_faults_in_this_availability_zone.setter
    def multiple_instances_producing_faults_in_this_availability_zone(
        self,
        value: typing.Optional[_aws_cdk_aws_cloudwatch_ceddda9d.IAlarm],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8753f6cccdf05b3bf34463787a7285ccc148cc5e2cfc023e6f5b3a2033d189c2)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "multipleInstancesProducingFaultsInThisAvailabilityZone", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="multipleInstancesProducingHighLatencyInThisAZ")
    def multiple_instances_producing_high_latency_in_this_az(
        self,
    ) -> typing.Optional[_aws_cdk_aws_cloudwatch_ceddda9d.IAlarm]:
        '''(experimental) Alarm indicating that there are multiple instances producing high latency responses in this AZ indicating the latency is not being caused by a single instance.

        :stability: experimental
        '''
        return typing.cast(typing.Optional[_aws_cdk_aws_cloudwatch_ceddda9d.IAlarm], jsii.get(self, "multipleInstancesProducingHighLatencyInThisAZ"))

    @multiple_instances_producing_high_latency_in_this_az.setter
    def multiple_instances_producing_high_latency_in_this_az(
        self,
        value: typing.Optional[_aws_cdk_aws_cloudwatch_ceddda9d.IAlarm],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1060beb3750b5928b5aa1d6014d9bf5c99f477f1f89b23ed16537542e068b922)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "multipleInstancesProducingHighLatencyInThisAZ", value) # pyright: ignore[reportArgumentType]

# Adding a "__jsii_proxy_class__(): typing.Type" function to the interface
typing.cast(typing.Any, IServerSideOperationZonalAlarmsAndRules).__jsii_proxy_class__ = lambda : _IServerSideOperationZonalAlarmsAndRulesProxy


@jsii.interface(jsii_type="@cdklabs/multi-az-observability.IService")
class IService(typing_extensions.Protocol):
    '''(experimental) Represents a complete service composed of one or more operations.

    :stability: experimental
    '''

    @builtins.property
    @jsii.member(jsii_name="availabilityZoneNames")
    def availability_zone_names(self) -> typing.List[builtins.str]:
        '''(experimental) A list of the Availability Zone names used by this application.

        :stability: experimental
        '''
        ...

    @builtins.property
    @jsii.member(jsii_name="baseUrl")
    def base_url(self) -> builtins.str:
        '''(experimental) The base endpoint for this service, like "https://www.example.com". Operation paths will be appended to this endpoint for canary testing the service.

        :stability: experimental
        '''
        ...

    @builtins.property
    @jsii.member(jsii_name="defaultAvailabilityMetricDetails")
    def default_availability_metric_details(
        self,
    ) -> "IServiceAvailabilityMetricDetails":
        '''(experimental) The default settings that are used for availability metrics for all operations unless specifically overridden in an operation definition.

        :stability: experimental
        '''
        ...

    @builtins.property
    @jsii.member(jsii_name="defaultLatencyMetricDetails")
    def default_latency_metric_details(self) -> "IServiceLatencyMetricDetails":
        '''(experimental) The default settings that are used for availability metrics for all operations unless specifically overridden in an operation definition.

        :stability: experimental
        '''
        ...

    @builtins.property
    @jsii.member(jsii_name="faultCountThreshold")
    def fault_count_threshold(self) -> jsii.Number:
        '''(experimental) The fault count threshold that indicates the service is unhealthy.

        This is an absolute value of faults
        being produced by all critical operations in aggregate.

        :stability: experimental
        '''
        ...

    @builtins.property
    @jsii.member(jsii_name="operations")
    def operations(self) -> typing.List[IOperation]:
        '''(experimental) The operations that are part of this service.

        :stability: experimental
        '''
        ...

    @builtins.property
    @jsii.member(jsii_name="period")
    def period(self) -> _aws_cdk_ceddda9d.Duration:
        '''(experimental) The period for which metrics for the service should be aggregated.

        :stability: experimental
        '''
        ...

    @builtins.property
    @jsii.member(jsii_name="serviceName")
    def service_name(self) -> builtins.str:
        '''(experimental) The name of your service.

        :stability: experimental
        '''
        ...

    @builtins.property
    @jsii.member(jsii_name="canaryTestProps")
    def canary_test_props(self) -> typing.Optional[AddCanaryTestProps]:
        '''(experimental) Define these settings if you want to automatically add canary tests to your operations.

        Operations can individually opt out
        of canary test creation if you define this setting.

        :default:

        - Automatic canary tests will not be created for
        operations in this service.

        :stability: experimental
        '''
        ...

    @builtins.property
    @jsii.member(jsii_name="defaultContributorInsightRuleDetails")
    def default_contributor_insight_rule_details(
        self,
    ) -> typing.Optional[IContributorInsightRuleDetails]:
        '''(experimental) The default settings that are used for contributor insight rules.

        :default: - No defaults are provided and must be specified per operation

        :stability: experimental
        '''
        ...

    @builtins.property
    @jsii.member(jsii_name="loadBalancer")
    def load_balancer(
        self,
    ) -> typing.Optional[_aws_cdk_aws_elasticloadbalancingv2_ceddda9d.ILoadBalancerV2]:
        '''(experimental) The load balancer this service sits behind.

        :default:

        - No load balancer metrics are included in
        dashboards and its ARN is not added to top level AZ
        alarm descriptions.

        :stability: experimental
        '''
        ...

    @builtins.property
    @jsii.member(jsii_name="minimumUnhealthyTargets")
    def minimum_unhealthy_targets(self) -> typing.Optional["MinimumUnhealthyTargets"]:
        '''(experimental) The minimum number of unhealthy targets to consider an AZ impaired.

        :default: Count of 2

        :stability: experimental
        '''
        ...

    @builtins.property
    @jsii.member(jsii_name="targetGroups")
    def target_groups(
        self,
    ) -> typing.Optional[typing.List[_aws_cdk_aws_elasticloadbalancingv2_ceddda9d.ITargetGroup]]:
        '''(experimental) The target groups registered with the load balancer.

        :default: Anomalous and mitigated host metrics will not be included on dashboards

        :stability: experimental
        '''
        ...

    @jsii.member(jsii_name="addOperation")
    def add_operation(self, operation: IOperation) -> None:
        '''(experimental) Adds an operation to this service.

        :param operation: -

        :stability: experimental
        '''
        ...


class _IServiceProxy:
    '''(experimental) Represents a complete service composed of one or more operations.

    :stability: experimental
    '''

    __jsii_type__: typing.ClassVar[str] = "@cdklabs/multi-az-observability.IService"

    @builtins.property
    @jsii.member(jsii_name="availabilityZoneNames")
    def availability_zone_names(self) -> typing.List[builtins.str]:
        '''(experimental) A list of the Availability Zone names used by this application.

        :stability: experimental
        '''
        return typing.cast(typing.List[builtins.str], jsii.get(self, "availabilityZoneNames"))

    @builtins.property
    @jsii.member(jsii_name="baseUrl")
    def base_url(self) -> builtins.str:
        '''(experimental) The base endpoint for this service, like "https://www.example.com". Operation paths will be appended to this endpoint for canary testing the service.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "baseUrl"))

    @builtins.property
    @jsii.member(jsii_name="defaultAvailabilityMetricDetails")
    def default_availability_metric_details(
        self,
    ) -> "IServiceAvailabilityMetricDetails":
        '''(experimental) The default settings that are used for availability metrics for all operations unless specifically overridden in an operation definition.

        :stability: experimental
        '''
        return typing.cast("IServiceAvailabilityMetricDetails", jsii.get(self, "defaultAvailabilityMetricDetails"))

    @builtins.property
    @jsii.member(jsii_name="defaultLatencyMetricDetails")
    def default_latency_metric_details(self) -> "IServiceLatencyMetricDetails":
        '''(experimental) The default settings that are used for availability metrics for all operations unless specifically overridden in an operation definition.

        :stability: experimental
        '''
        return typing.cast("IServiceLatencyMetricDetails", jsii.get(self, "defaultLatencyMetricDetails"))

    @builtins.property
    @jsii.member(jsii_name="faultCountThreshold")
    def fault_count_threshold(self) -> jsii.Number:
        '''(experimental) The fault count threshold that indicates the service is unhealthy.

        This is an absolute value of faults
        being produced by all critical operations in aggregate.

        :stability: experimental
        '''
        return typing.cast(jsii.Number, jsii.get(self, "faultCountThreshold"))

    @builtins.property
    @jsii.member(jsii_name="operations")
    def operations(self) -> typing.List[IOperation]:
        '''(experimental) The operations that are part of this service.

        :stability: experimental
        '''
        return typing.cast(typing.List[IOperation], jsii.get(self, "operations"))

    @builtins.property
    @jsii.member(jsii_name="period")
    def period(self) -> _aws_cdk_ceddda9d.Duration:
        '''(experimental) The period for which metrics for the service should be aggregated.

        :stability: experimental
        '''
        return typing.cast(_aws_cdk_ceddda9d.Duration, jsii.get(self, "period"))

    @builtins.property
    @jsii.member(jsii_name="serviceName")
    def service_name(self) -> builtins.str:
        '''(experimental) The name of your service.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "serviceName"))

    @builtins.property
    @jsii.member(jsii_name="canaryTestProps")
    def canary_test_props(self) -> typing.Optional[AddCanaryTestProps]:
        '''(experimental) Define these settings if you want to automatically add canary tests to your operations.

        Operations can individually opt out
        of canary test creation if you define this setting.

        :default:

        - Automatic canary tests will not be created for
        operations in this service.

        :stability: experimental
        '''
        return typing.cast(typing.Optional[AddCanaryTestProps], jsii.get(self, "canaryTestProps"))

    @builtins.property
    @jsii.member(jsii_name="defaultContributorInsightRuleDetails")
    def default_contributor_insight_rule_details(
        self,
    ) -> typing.Optional[IContributorInsightRuleDetails]:
        '''(experimental) The default settings that are used for contributor insight rules.

        :default: - No defaults are provided and must be specified per operation

        :stability: experimental
        '''
        return typing.cast(typing.Optional[IContributorInsightRuleDetails], jsii.get(self, "defaultContributorInsightRuleDetails"))

    @builtins.property
    @jsii.member(jsii_name="loadBalancer")
    def load_balancer(
        self,
    ) -> typing.Optional[_aws_cdk_aws_elasticloadbalancingv2_ceddda9d.ILoadBalancerV2]:
        '''(experimental) The load balancer this service sits behind.

        :default:

        - No load balancer metrics are included in
        dashboards and its ARN is not added to top level AZ
        alarm descriptions.

        :stability: experimental
        '''
        return typing.cast(typing.Optional[_aws_cdk_aws_elasticloadbalancingv2_ceddda9d.ILoadBalancerV2], jsii.get(self, "loadBalancer"))

    @builtins.property
    @jsii.member(jsii_name="minimumUnhealthyTargets")
    def minimum_unhealthy_targets(self) -> typing.Optional["MinimumUnhealthyTargets"]:
        '''(experimental) The minimum number of unhealthy targets to consider an AZ impaired.

        :default: Count of 2

        :stability: experimental
        '''
        return typing.cast(typing.Optional["MinimumUnhealthyTargets"], jsii.get(self, "minimumUnhealthyTargets"))

    @builtins.property
    @jsii.member(jsii_name="targetGroups")
    def target_groups(
        self,
    ) -> typing.Optional[typing.List[_aws_cdk_aws_elasticloadbalancingv2_ceddda9d.ITargetGroup]]:
        '''(experimental) The target groups registered with the load balancer.

        :default: Anomalous and mitigated host metrics will not be included on dashboards

        :stability: experimental
        '''
        return typing.cast(typing.Optional[typing.List[_aws_cdk_aws_elasticloadbalancingv2_ceddda9d.ITargetGroup]], jsii.get(self, "targetGroups"))

    @jsii.member(jsii_name="addOperation")
    def add_operation(self, operation: IOperation) -> None:
        '''(experimental) Adds an operation to this service.

        :param operation: -

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__afd14cd0917991cc6cb77ab7f5cd990568300cab8c21fa589a02ec956952541f)
            check_type(argname="argument operation", value=operation, expected_type=type_hints["operation"])
        return typing.cast(None, jsii.invoke(self, "addOperation", [operation]))

# Adding a "__jsii_proxy_class__(): typing.Type" function to the interface
typing.cast(typing.Any, IService).__jsii_proxy_class__ = lambda : _IServiceProxy


@jsii.interface(jsii_type="@cdklabs/multi-az-observability.IServiceAlarmsAndRules")
class IServiceAlarmsAndRules(typing_extensions.Protocol):
    '''(experimental) Service level alarms and rules using critical operations.

    :stability: experimental
    '''

    @builtins.property
    @jsii.member(jsii_name="regionalImpactAlarm")
    def regional_impact_alarm(self) -> _aws_cdk_aws_cloudwatch_ceddda9d.IAlarm:
        '''(experimental) An alarm indicating there is availability or latency impact on a critical operation that is not scoped to a single availability zone as measured by the server-side and/or canary (if present).

        :stability: experimental
        '''
        ...

    @regional_impact_alarm.setter
    def regional_impact_alarm(
        self,
        value: _aws_cdk_aws_cloudwatch_ceddda9d.IAlarm,
    ) -> None:
        ...

    @builtins.property
    @jsii.member(jsii_name="regionalServerSideImpactAlarm")
    def regional_server_side_impact_alarm(
        self,
    ) -> _aws_cdk_aws_cloudwatch_ceddda9d.IAlarm:
        '''(experimental) An alarm indicating there is availability or latency impact on a critical operation that is not scoped to a single availability zone as measured by the server-side.

        :stability: experimental
        '''
        ...

    @regional_server_side_impact_alarm.setter
    def regional_server_side_impact_alarm(
        self,
        value: _aws_cdk_aws_cloudwatch_ceddda9d.IAlarm,
    ) -> None:
        ...

    @builtins.property
    @jsii.member(jsii_name="service")
    def service(self) -> IService:
        '''(experimental) The service these alarms and rules are for.

        :stability: experimental
        '''
        ...

    @service.setter
    def service(self, value: IService) -> None:
        ...

    @builtins.property
    @jsii.member(jsii_name="serviceImpactAlarm")
    def service_impact_alarm(self) -> _aws_cdk_aws_cloudwatch_ceddda9d.IAlarm:
        '''(experimental) This is the top level alarm you should tie notifications/paging/alerting to.

        It triggers
        on any impact to a critical operation either zonally scoped or regionally scoped.

        :stability: experimental
        '''
        ...

    @service_impact_alarm.setter
    def service_impact_alarm(
        self,
        value: _aws_cdk_aws_cloudwatch_ceddda9d.IAlarm,
    ) -> None:
        ...

    @builtins.property
    @jsii.member(jsii_name="zonalAggregateIsolatedImpactAlarms")
    def zonal_aggregate_isolated_impact_alarms(
        self,
    ) -> typing.Mapping[builtins.str, _aws_cdk_aws_cloudwatch_ceddda9d.IAlarm]:
        '''(experimental) The zonal aggregate isolated impact alarms.

        There is 1 alarm per AZ that
        triggers for availability or latency impact to any critical operation in that AZ
        that indicates it has isolated impact as measured by canaries or server-side.

        :stability: experimental
        '''
        ...

    @zonal_aggregate_isolated_impact_alarms.setter
    def zonal_aggregate_isolated_impact_alarms(
        self,
        value: typing.Mapping[builtins.str, _aws_cdk_aws_cloudwatch_ceddda9d.IAlarm],
    ) -> None:
        ...

    @builtins.property
    @jsii.member(jsii_name="zonalServerSideIsolatedImpactAlarms")
    def zonal_server_side_isolated_impact_alarms(
        self,
    ) -> typing.Mapping[builtins.str, _aws_cdk_aws_cloudwatch_ceddda9d.IAlarm]:
        '''(experimental) The zonal server-side isolated impact alarms.

        There is 1 alarm per AZ that triggers
        on availability or latency impact to any critical operation in that AZ. These are useful
        for deployment monitoring to not inadvertently fail when a canary can't contact an AZ
        during a deployment.

        :stability: experimental
        '''
        ...

    @zonal_server_side_isolated_impact_alarms.setter
    def zonal_server_side_isolated_impact_alarms(
        self,
        value: typing.Mapping[builtins.str, _aws_cdk_aws_cloudwatch_ceddda9d.IAlarm],
    ) -> None:
        ...

    @builtins.property
    @jsii.member(jsii_name="regionalCanaryAlarm")
    def regional_canary_alarm(
        self,
    ) -> typing.Optional[_aws_cdk_aws_cloudwatch_ceddda9d.IAlarm]:
        '''(experimental) An alarm indicating the canary has discovered an availability or latency impact on a critical operation while testing the regional endpoint.

        :stability: experimental
        '''
        ...

    @regional_canary_alarm.setter
    def regional_canary_alarm(
        self,
        value: typing.Optional[_aws_cdk_aws_cloudwatch_ceddda9d.IAlarm],
    ) -> None:
        ...


class _IServiceAlarmsAndRulesProxy:
    '''(experimental) Service level alarms and rules using critical operations.

    :stability: experimental
    '''

    __jsii_type__: typing.ClassVar[str] = "@cdklabs/multi-az-observability.IServiceAlarmsAndRules"

    @builtins.property
    @jsii.member(jsii_name="regionalImpactAlarm")
    def regional_impact_alarm(self) -> _aws_cdk_aws_cloudwatch_ceddda9d.IAlarm:
        '''(experimental) An alarm indicating there is availability or latency impact on a critical operation that is not scoped to a single availability zone as measured by the server-side and/or canary (if present).

        :stability: experimental
        '''
        return typing.cast(_aws_cdk_aws_cloudwatch_ceddda9d.IAlarm, jsii.get(self, "regionalImpactAlarm"))

    @regional_impact_alarm.setter
    def regional_impact_alarm(
        self,
        value: _aws_cdk_aws_cloudwatch_ceddda9d.IAlarm,
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a8f0455f87797305bc755c3271060c1f7023ae24d8e8a0ef14ddb7b93494485b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "regionalImpactAlarm", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="regionalServerSideImpactAlarm")
    def regional_server_side_impact_alarm(
        self,
    ) -> _aws_cdk_aws_cloudwatch_ceddda9d.IAlarm:
        '''(experimental) An alarm indicating there is availability or latency impact on a critical operation that is not scoped to a single availability zone as measured by the server-side.

        :stability: experimental
        '''
        return typing.cast(_aws_cdk_aws_cloudwatch_ceddda9d.IAlarm, jsii.get(self, "regionalServerSideImpactAlarm"))

    @regional_server_side_impact_alarm.setter
    def regional_server_side_impact_alarm(
        self,
        value: _aws_cdk_aws_cloudwatch_ceddda9d.IAlarm,
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2070a9428cac03ff47244b1cdc0c9cb54d838c613793a11bc4a4572b4ab14794)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "regionalServerSideImpactAlarm", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="service")
    def service(self) -> IService:
        '''(experimental) The service these alarms and rules are for.

        :stability: experimental
        '''
        return typing.cast(IService, jsii.get(self, "service"))

    @service.setter
    def service(self, value: IService) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5c6785f0b57be0aee34f5f853c036254ca14de1654825c78f261ac607baf9f68)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "service", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="serviceImpactAlarm")
    def service_impact_alarm(self) -> _aws_cdk_aws_cloudwatch_ceddda9d.IAlarm:
        '''(experimental) This is the top level alarm you should tie notifications/paging/alerting to.

        It triggers
        on any impact to a critical operation either zonally scoped or regionally scoped.

        :stability: experimental
        '''
        return typing.cast(_aws_cdk_aws_cloudwatch_ceddda9d.IAlarm, jsii.get(self, "serviceImpactAlarm"))

    @service_impact_alarm.setter
    def service_impact_alarm(
        self,
        value: _aws_cdk_aws_cloudwatch_ceddda9d.IAlarm,
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__83447c8c7ae17fdd5ac2ee70d95fa8012186163553c15c3ff75fbd157e08c4cf)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "serviceImpactAlarm", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="zonalAggregateIsolatedImpactAlarms")
    def zonal_aggregate_isolated_impact_alarms(
        self,
    ) -> typing.Mapping[builtins.str, _aws_cdk_aws_cloudwatch_ceddda9d.IAlarm]:
        '''(experimental) The zonal aggregate isolated impact alarms.

        There is 1 alarm per AZ that
        triggers for availability or latency impact to any critical operation in that AZ
        that indicates it has isolated impact as measured by canaries or server-side.

        :stability: experimental
        '''
        return typing.cast(typing.Mapping[builtins.str, _aws_cdk_aws_cloudwatch_ceddda9d.IAlarm], jsii.get(self, "zonalAggregateIsolatedImpactAlarms"))

    @zonal_aggregate_isolated_impact_alarms.setter
    def zonal_aggregate_isolated_impact_alarms(
        self,
        value: typing.Mapping[builtins.str, _aws_cdk_aws_cloudwatch_ceddda9d.IAlarm],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__88bd2ac9b9df963771c7db9b780890e46e9f7641052e0b975b66d4ce023829af)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "zonalAggregateIsolatedImpactAlarms", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="zonalServerSideIsolatedImpactAlarms")
    def zonal_server_side_isolated_impact_alarms(
        self,
    ) -> typing.Mapping[builtins.str, _aws_cdk_aws_cloudwatch_ceddda9d.IAlarm]:
        '''(experimental) The zonal server-side isolated impact alarms.

        There is 1 alarm per AZ that triggers
        on availability or latency impact to any critical operation in that AZ. These are useful
        for deployment monitoring to not inadvertently fail when a canary can't contact an AZ
        during a deployment.

        :stability: experimental
        '''
        return typing.cast(typing.Mapping[builtins.str, _aws_cdk_aws_cloudwatch_ceddda9d.IAlarm], jsii.get(self, "zonalServerSideIsolatedImpactAlarms"))

    @zonal_server_side_isolated_impact_alarms.setter
    def zonal_server_side_isolated_impact_alarms(
        self,
        value: typing.Mapping[builtins.str, _aws_cdk_aws_cloudwatch_ceddda9d.IAlarm],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c4e4294e497d1a1bbb3c47bb3d6cffa4eee8406b856968fe2348586f2b19bd5f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "zonalServerSideIsolatedImpactAlarms", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="regionalCanaryAlarm")
    def regional_canary_alarm(
        self,
    ) -> typing.Optional[_aws_cdk_aws_cloudwatch_ceddda9d.IAlarm]:
        '''(experimental) An alarm indicating the canary has discovered an availability or latency impact on a critical operation while testing the regional endpoint.

        :stability: experimental
        '''
        return typing.cast(typing.Optional[_aws_cdk_aws_cloudwatch_ceddda9d.IAlarm], jsii.get(self, "regionalCanaryAlarm"))

    @regional_canary_alarm.setter
    def regional_canary_alarm(
        self,
        value: typing.Optional[_aws_cdk_aws_cloudwatch_ceddda9d.IAlarm],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__83f2ac0c7884f1760a3da6cd1bcfc505287df81e5b92e464ae735a748b7cc1c8)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "regionalCanaryAlarm", value) # pyright: ignore[reportArgumentType]

# Adding a "__jsii_proxy_class__(): typing.Type" function to the interface
typing.cast(typing.Any, IServiceAlarmsAndRules).__jsii_proxy_class__ = lambda : _IServiceAlarmsAndRulesProxy


@jsii.interface(jsii_type="@cdklabs/multi-az-observability.IServiceMetricDetails")
class IServiceMetricDetails(typing_extensions.Protocol):
    '''(experimental) Details for the defaults used in a service for metrics in one perspective, such as server side latency.

    :stability: experimental
    '''

    @builtins.property
    @jsii.member(jsii_name="alarmStatistic")
    def alarm_statistic(self) -> builtins.str:
        '''(experimental) The statistic used for alarms, for availability metrics this should be "Sum", for latency metrics it could something like "p99" or "p99.9".

        :stability: experimental
        '''
        ...

    @builtins.property
    @jsii.member(jsii_name="datapointsToAlarm")
    def datapoints_to_alarm(self) -> jsii.Number:
        '''(experimental) The number of datapoints to alarm on for latency and availability alarms.

        :stability: experimental
        '''
        ...

    @builtins.property
    @jsii.member(jsii_name="evaluationPeriods")
    def evaluation_periods(self) -> jsii.Number:
        '''(experimental) The number of evaluation periods for latency and availabiltiy alarms.

        :stability: experimental
        '''
        ...

    @builtins.property
    @jsii.member(jsii_name="faultMetricNames")
    def fault_metric_names(self) -> typing.List[builtins.str]:
        '''(experimental) The names of fault indicating metrics.

        :stability: experimental
        '''
        ...

    @builtins.property
    @jsii.member(jsii_name="metricNamespace")
    def metric_namespace(self) -> builtins.str:
        '''(experimental) The CloudWatch metric namespace for these metrics.

        :stability: experimental
        '''
        ...

    @builtins.property
    @jsii.member(jsii_name="period")
    def period(self) -> _aws_cdk_ceddda9d.Duration:
        '''(experimental) The period for the metrics.

        :stability: experimental
        '''
        ...

    @builtins.property
    @jsii.member(jsii_name="successMetricNames")
    def success_metric_names(self) -> typing.List[builtins.str]:
        '''(experimental) The names of success indicating metrics.

        :stability: experimental
        '''
        ...

    @builtins.property
    @jsii.member(jsii_name="unit")
    def unit(self) -> _aws_cdk_aws_cloudwatch_ceddda9d.Unit:
        '''(experimental) The unit used for these metrics.

        :stability: experimental
        '''
        ...

    @builtins.property
    @jsii.member(jsii_name="graphedFaultStatistics")
    def graphed_fault_statistics(self) -> typing.Optional[typing.List[builtins.str]]:
        '''(experimental) The statistics for faults you want to appear on dashboards, for example, with latency metrics, you might want p50, p99, and tm99.

        For availability
        metrics this will typically just be "Sum".

        :default: - For availability metrics, this will be "Sum", for latency metrics it will be just "p99"

        :stability: experimental
        '''
        ...

    @builtins.property
    @jsii.member(jsii_name="graphedSuccessStatistics")
    def graphed_success_statistics(self) -> typing.Optional[typing.List[builtins.str]]:
        '''(experimental) The statistics for successes you want to appear on dashboards, for example, with latency metrics, you might want p50, p99, and tm99.

        For availability
        metrics this will typically just be "Sum".

        :default: - For availability metrics, this will be "Sum", for latency metrics it will be just "p99"

        :stability: experimental
        '''
        ...


class _IServiceMetricDetailsProxy:
    '''(experimental) Details for the defaults used in a service for metrics in one perspective, such as server side latency.

    :stability: experimental
    '''

    __jsii_type__: typing.ClassVar[str] = "@cdklabs/multi-az-observability.IServiceMetricDetails"

    @builtins.property
    @jsii.member(jsii_name="alarmStatistic")
    def alarm_statistic(self) -> builtins.str:
        '''(experimental) The statistic used for alarms, for availability metrics this should be "Sum", for latency metrics it could something like "p99" or "p99.9".

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "alarmStatistic"))

    @builtins.property
    @jsii.member(jsii_name="datapointsToAlarm")
    def datapoints_to_alarm(self) -> jsii.Number:
        '''(experimental) The number of datapoints to alarm on for latency and availability alarms.

        :stability: experimental
        '''
        return typing.cast(jsii.Number, jsii.get(self, "datapointsToAlarm"))

    @builtins.property
    @jsii.member(jsii_name="evaluationPeriods")
    def evaluation_periods(self) -> jsii.Number:
        '''(experimental) The number of evaluation periods for latency and availabiltiy alarms.

        :stability: experimental
        '''
        return typing.cast(jsii.Number, jsii.get(self, "evaluationPeriods"))

    @builtins.property
    @jsii.member(jsii_name="faultMetricNames")
    def fault_metric_names(self) -> typing.List[builtins.str]:
        '''(experimental) The names of fault indicating metrics.

        :stability: experimental
        '''
        return typing.cast(typing.List[builtins.str], jsii.get(self, "faultMetricNames"))

    @builtins.property
    @jsii.member(jsii_name="metricNamespace")
    def metric_namespace(self) -> builtins.str:
        '''(experimental) The CloudWatch metric namespace for these metrics.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "metricNamespace"))

    @builtins.property
    @jsii.member(jsii_name="period")
    def period(self) -> _aws_cdk_ceddda9d.Duration:
        '''(experimental) The period for the metrics.

        :stability: experimental
        '''
        return typing.cast(_aws_cdk_ceddda9d.Duration, jsii.get(self, "period"))

    @builtins.property
    @jsii.member(jsii_name="successMetricNames")
    def success_metric_names(self) -> typing.List[builtins.str]:
        '''(experimental) The names of success indicating metrics.

        :stability: experimental
        '''
        return typing.cast(typing.List[builtins.str], jsii.get(self, "successMetricNames"))

    @builtins.property
    @jsii.member(jsii_name="unit")
    def unit(self) -> _aws_cdk_aws_cloudwatch_ceddda9d.Unit:
        '''(experimental) The unit used for these metrics.

        :stability: experimental
        '''
        return typing.cast(_aws_cdk_aws_cloudwatch_ceddda9d.Unit, jsii.get(self, "unit"))

    @builtins.property
    @jsii.member(jsii_name="graphedFaultStatistics")
    def graphed_fault_statistics(self) -> typing.Optional[typing.List[builtins.str]]:
        '''(experimental) The statistics for faults you want to appear on dashboards, for example, with latency metrics, you might want p50, p99, and tm99.

        For availability
        metrics this will typically just be "Sum".

        :default: - For availability metrics, this will be "Sum", for latency metrics it will be just "p99"

        :stability: experimental
        '''
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "graphedFaultStatistics"))

    @builtins.property
    @jsii.member(jsii_name="graphedSuccessStatistics")
    def graphed_success_statistics(self) -> typing.Optional[typing.List[builtins.str]]:
        '''(experimental) The statistics for successes you want to appear on dashboards, for example, with latency metrics, you might want p50, p99, and tm99.

        For availability
        metrics this will typically just be "Sum".

        :default: - For availability metrics, this will be "Sum", for latency metrics it will be just "p99"

        :stability: experimental
        '''
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "graphedSuccessStatistics"))

# Adding a "__jsii_proxy_class__(): typing.Type" function to the interface
typing.cast(typing.Any, IServiceMetricDetails).__jsii_proxy_class__ = lambda : _IServiceMetricDetailsProxy


@jsii.implements(IInstrumentedServiceMultiAZObservability)
class InstrumentedServiceMultiAZObservability(
    _constructs_77d1e7e8.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdklabs/multi-az-observability.InstrumentedServiceMultiAZObservability",
):
    '''(experimental) An service that implements its own instrumentation to record availability and latency metrics that can be used to create alarms, rules, and dashboards from.

    :stability: experimental
    '''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        service: IService,
        assets_bucket_parameter_name: typing.Optional[builtins.str] = None,
        assets_bucket_prefix_parameter_name: typing.Optional[builtins.str] = None,
        availability_outlier_detection_algorithm: typing.Optional["OutlierDetectionAlgorithm"] = None,
        availability_outlier_threshold: typing.Optional[jsii.Number] = None,
        create_dashboards: typing.Optional[builtins.bool] = None,
        interval: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
        latency_outlier_detection_algorithm: typing.Optional["OutlierDetectionAlgorithm"] = None,
        latency_outlier_metric_aggregation: typing.Optional["LatencyOutlierMetricAggregation"] = None,
        latency_outlier_threshold: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param service: (experimental) The service that the alarms and dashboards are being crated for.
        :param assets_bucket_parameter_name: (experimental) If you are not using a static bucket to deploy assets, for example you are synthing this and it gets uploaded to a bucket whose name is unknown to you (maybe used as part of a central CI/CD system) and is provided as a parameter to your stack, specify that parameter name here. It will override the bucket location CDK provides by default for bundled assets. The stack containing this contruct needs to have a parameter defined that uses this name. The underlying stacks in this construct that deploy assets will copy the parent stack's value for this property. Default: - The assets will be uploaded to the default defined asset location.
        :param assets_bucket_prefix_parameter_name: (experimental) If you are not using a static bucket to deploy assets, for example you are synthing this and it gets uploaded to a bucket that uses a prefix that is unknown to you (maybe used as part of a central CI/CD system) and is provided as a parameter to your stack, specify that parameter name here. It will override the bucket prefix CDK provides by default for bundled assets. This property only takes effect if you defined the assetsBucketParameterName. The stack containing this contruct needs to have a parameter defined that uses this name. The underlying stacks in this construct that deploy assets will copy the parent stack's value for this property. Default: - No object prefix will be added to your custom assets location. However, if you have overridden something like the 'BucketPrefix' property in your stack synthesizer with a variable like "${AssetsBucketPrefix", you will need to define this property so it doesn't cause a reference error even if the prefix value is blank.
        :param availability_outlier_detection_algorithm: (experimental) The algorithm to use for performing outlier detection for availability metrics. ** Currently only STATIC is supported ** Default: OutlierDetectionAlgorithm.STATIC
        :param availability_outlier_threshold: (experimental) The outlier threshold for determining if an AZ is an outlier for faults. This number is interpreted differently for different outlier algorithms. When used with STATIC, the number should be between 0 and 1 to represent the percentage of errors (like .7) that an AZ must be responsible for to be considered an outlier. When used with CHI_SQUARED, it represents the p value that indicates statistical significance, like 0.05 which means the skew has less than or equal to a 5% chance of occuring. When used with Z_SCORE it indicates how many standard deviations to evaluate for an AZ being an outlier, typically 3 is standard for Z_SCORE. Standard defaults based on the outlier detection algorithm: STATIC: 0.7 CHI_SQUARED: 0.05 Z_SCORE: 3 IQR: 1.5 MAD: 3 Default: - Depends on the outlier detection algorithm selected
        :param create_dashboards: (experimental) Indicates whether to create per operation and overall service dashboards. Default: - No dashboards are created
        :param interval: (experimental) The interval used in the dashboard, defaults to 60 minutes. Default: - 60 minutes
        :param latency_outlier_detection_algorithm: (experimental) The algorithm to use for performing outlier detection for latency metrics. ** Currently only STATIC is supported ** Default: OutlierDetectionAlgorithm.STATIC
        :param latency_outlier_metric_aggregation: (experimental) The metric for latency to use in outlier detection, which means whether the algorithm uses a count of requests exceeding your latency threshold or whether it uses the actual latency values at your latency alarm threshold statistic. Default: LatencyOutlierMetric.COUNT
        :param latency_outlier_threshold: (experimental) The outlier threshold for determining if an AZ is an outlier for latency. This number is interpreted differently for different outlier algorithms. When used with STATIC, the number should be between 0 and 1 to represent the percentage of errors (like .7) that an AZ must be responsible for to be considered an outlier. When used with CHI_SQUARED, it represents the p value that indicates statistical significance, like 0.05 which means the skew has less than or equal to a 5% chance of occuring. When used with Z_SCORE it indicates how many standard deviations to evaluate for an AZ being an outlier, typically 3 is standard for Z_SCORE. Standard defaults based on the outlier detection algorithm: STATIC: 0.7 CHI_SQUARED: 0.05 Z_SCORE: 3 IQR: 1.5 MAD: 3 Default: - Depends on the outlier detection algorithm selected

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__78520ac471f9b9792f6e88a24fe852bdde2ad70bb4d1636d8b022de412343fdc)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = InstrumentedServiceMultiAZObservabilityProps(
            service=service,
            assets_bucket_parameter_name=assets_bucket_parameter_name,
            assets_bucket_prefix_parameter_name=assets_bucket_prefix_parameter_name,
            availability_outlier_detection_algorithm=availability_outlier_detection_algorithm,
            availability_outlier_threshold=availability_outlier_threshold,
            create_dashboards=create_dashboards,
            interval=interval,
            latency_outlier_detection_algorithm=latency_outlier_detection_algorithm,
            latency_outlier_metric_aggregation=latency_outlier_metric_aggregation,
            latency_outlier_threshold=latency_outlier_threshold,
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @builtins.property
    @jsii.member(jsii_name="perOperationAlarmsAndRules")
    def per_operation_alarms_and_rules(
        self,
    ) -> typing.Mapping[builtins.str, IOperationAlarmsAndRules]:
        '''(experimental) Key represents the operation name and the value is the set of zonal alarms and rules for that operation.

        :stability: experimental
        '''
        return typing.cast(typing.Mapping[builtins.str, IOperationAlarmsAndRules], jsii.get(self, "perOperationAlarmsAndRules"))

    @builtins.property
    @jsii.member(jsii_name="perOperationZonalImpactAlarms")
    def per_operation_zonal_impact_alarms(
        self,
    ) -> typing.Mapping[builtins.str, typing.Mapping[builtins.str, _aws_cdk_aws_cloudwatch_ceddda9d.IAlarm]]:
        '''(experimental) Index into the dictionary by operation name, then by Availability Zone Id to get the alarms that indicate an AZ shows isolated impact from availability or latency as seen by either the server-side or canary.

        These are the alarms
        you would want to use to trigger automation to evacuate an AZ.

        :stability: experimental
        '''
        return typing.cast(typing.Mapping[builtins.str, typing.Mapping[builtins.str, _aws_cdk_aws_cloudwatch_ceddda9d.IAlarm]], jsii.get(self, "perOperationZonalImpactAlarms"))

    @builtins.property
    @jsii.member(jsii_name="serviceAlarms")
    def service_alarms(self) -> IServiceAlarmsAndRules:
        '''(experimental) The alarms and rules for the overall service.

        :stability: experimental
        '''
        return typing.cast(IServiceAlarmsAndRules, jsii.get(self, "serviceAlarms"))

    @builtins.property
    @jsii.member(jsii_name="canaryLogGroup")
    def canary_log_group(self) -> typing.Optional[_aws_cdk_aws_logs_ceddda9d.ILogGroup]:
        '''(experimental) If the service is configured to have canary tests created, this will be the log group where the canary's logs are stored.

        :default: - No log group is created if the canary is not requested.

        :stability: experimental
        '''
        return typing.cast(typing.Optional[_aws_cdk_aws_logs_ceddda9d.ILogGroup], jsii.get(self, "canaryLogGroup"))

    @builtins.property
    @jsii.member(jsii_name="operationDashboards")
    def operation_dashboards(
        self,
    ) -> typing.Optional[typing.List[_aws_cdk_aws_cloudwatch_ceddda9d.Dashboard]]:
        '''(experimental) The dashboards for each operation.

        :stability: experimental
        '''
        return typing.cast(typing.Optional[typing.List[_aws_cdk_aws_cloudwatch_ceddda9d.Dashboard]], jsii.get(self, "operationDashboards"))

    @builtins.property
    @jsii.member(jsii_name="serviceDashboard")
    def service_dashboard(
        self,
    ) -> typing.Optional[_aws_cdk_aws_cloudwatch_ceddda9d.Dashboard]:
        '''(experimental) The service level dashboard.

        :stability: experimental
        '''
        return typing.cast(typing.Optional[_aws_cdk_aws_cloudwatch_ceddda9d.Dashboard], jsii.get(self, "serviceDashboard"))


@jsii.data_type(
    jsii_type="@cdklabs/multi-az-observability.InstrumentedServiceMultiAZObservabilityProps",
    jsii_struct_bases=[],
    name_mapping={
        "service": "service",
        "assets_bucket_parameter_name": "assetsBucketParameterName",
        "assets_bucket_prefix_parameter_name": "assetsBucketPrefixParameterName",
        "availability_outlier_detection_algorithm": "availabilityOutlierDetectionAlgorithm",
        "availability_outlier_threshold": "availabilityOutlierThreshold",
        "create_dashboards": "createDashboards",
        "interval": "interval",
        "latency_outlier_detection_algorithm": "latencyOutlierDetectionAlgorithm",
        "latency_outlier_metric_aggregation": "latencyOutlierMetricAggregation",
        "latency_outlier_threshold": "latencyOutlierThreshold",
    },
)
class InstrumentedServiceMultiAZObservabilityProps:
    def __init__(
        self,
        *,
        service: IService,
        assets_bucket_parameter_name: typing.Optional[builtins.str] = None,
        assets_bucket_prefix_parameter_name: typing.Optional[builtins.str] = None,
        availability_outlier_detection_algorithm: typing.Optional["OutlierDetectionAlgorithm"] = None,
        availability_outlier_threshold: typing.Optional[jsii.Number] = None,
        create_dashboards: typing.Optional[builtins.bool] = None,
        interval: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
        latency_outlier_detection_algorithm: typing.Optional["OutlierDetectionAlgorithm"] = None,
        latency_outlier_metric_aggregation: typing.Optional["LatencyOutlierMetricAggregation"] = None,
        latency_outlier_threshold: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''(experimental) The properties for adding alarms and dashboards for an instrumented service.

        :param service: (experimental) The service that the alarms and dashboards are being crated for.
        :param assets_bucket_parameter_name: (experimental) If you are not using a static bucket to deploy assets, for example you are synthing this and it gets uploaded to a bucket whose name is unknown to you (maybe used as part of a central CI/CD system) and is provided as a parameter to your stack, specify that parameter name here. It will override the bucket location CDK provides by default for bundled assets. The stack containing this contruct needs to have a parameter defined that uses this name. The underlying stacks in this construct that deploy assets will copy the parent stack's value for this property. Default: - The assets will be uploaded to the default defined asset location.
        :param assets_bucket_prefix_parameter_name: (experimental) If you are not using a static bucket to deploy assets, for example you are synthing this and it gets uploaded to a bucket that uses a prefix that is unknown to you (maybe used as part of a central CI/CD system) and is provided as a parameter to your stack, specify that parameter name here. It will override the bucket prefix CDK provides by default for bundled assets. This property only takes effect if you defined the assetsBucketParameterName. The stack containing this contruct needs to have a parameter defined that uses this name. The underlying stacks in this construct that deploy assets will copy the parent stack's value for this property. Default: - No object prefix will be added to your custom assets location. However, if you have overridden something like the 'BucketPrefix' property in your stack synthesizer with a variable like "${AssetsBucketPrefix", you will need to define this property so it doesn't cause a reference error even if the prefix value is blank.
        :param availability_outlier_detection_algorithm: (experimental) The algorithm to use for performing outlier detection for availability metrics. ** Currently only STATIC is supported ** Default: OutlierDetectionAlgorithm.STATIC
        :param availability_outlier_threshold: (experimental) The outlier threshold for determining if an AZ is an outlier for faults. This number is interpreted differently for different outlier algorithms. When used with STATIC, the number should be between 0 and 1 to represent the percentage of errors (like .7) that an AZ must be responsible for to be considered an outlier. When used with CHI_SQUARED, it represents the p value that indicates statistical significance, like 0.05 which means the skew has less than or equal to a 5% chance of occuring. When used with Z_SCORE it indicates how many standard deviations to evaluate for an AZ being an outlier, typically 3 is standard for Z_SCORE. Standard defaults based on the outlier detection algorithm: STATIC: 0.7 CHI_SQUARED: 0.05 Z_SCORE: 3 IQR: 1.5 MAD: 3 Default: - Depends on the outlier detection algorithm selected
        :param create_dashboards: (experimental) Indicates whether to create per operation and overall service dashboards. Default: - No dashboards are created
        :param interval: (experimental) The interval used in the dashboard, defaults to 60 minutes. Default: - 60 minutes
        :param latency_outlier_detection_algorithm: (experimental) The algorithm to use for performing outlier detection for latency metrics. ** Currently only STATIC is supported ** Default: OutlierDetectionAlgorithm.STATIC
        :param latency_outlier_metric_aggregation: (experimental) The metric for latency to use in outlier detection, which means whether the algorithm uses a count of requests exceeding your latency threshold or whether it uses the actual latency values at your latency alarm threshold statistic. Default: LatencyOutlierMetric.COUNT
        :param latency_outlier_threshold: (experimental) The outlier threshold for determining if an AZ is an outlier for latency. This number is interpreted differently for different outlier algorithms. When used with STATIC, the number should be between 0 and 1 to represent the percentage of errors (like .7) that an AZ must be responsible for to be considered an outlier. When used with CHI_SQUARED, it represents the p value that indicates statistical significance, like 0.05 which means the skew has less than or equal to a 5% chance of occuring. When used with Z_SCORE it indicates how many standard deviations to evaluate for an AZ being an outlier, typically 3 is standard for Z_SCORE. Standard defaults based on the outlier detection algorithm: STATIC: 0.7 CHI_SQUARED: 0.05 Z_SCORE: 3 IQR: 1.5 MAD: 3 Default: - Depends on the outlier detection algorithm selected

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__102051515d19b7efde161728b5c392ba25f80ba0513d70df8ce3bdebba803655)
            check_type(argname="argument service", value=service, expected_type=type_hints["service"])
            check_type(argname="argument assets_bucket_parameter_name", value=assets_bucket_parameter_name, expected_type=type_hints["assets_bucket_parameter_name"])
            check_type(argname="argument assets_bucket_prefix_parameter_name", value=assets_bucket_prefix_parameter_name, expected_type=type_hints["assets_bucket_prefix_parameter_name"])
            check_type(argname="argument availability_outlier_detection_algorithm", value=availability_outlier_detection_algorithm, expected_type=type_hints["availability_outlier_detection_algorithm"])
            check_type(argname="argument availability_outlier_threshold", value=availability_outlier_threshold, expected_type=type_hints["availability_outlier_threshold"])
            check_type(argname="argument create_dashboards", value=create_dashboards, expected_type=type_hints["create_dashboards"])
            check_type(argname="argument interval", value=interval, expected_type=type_hints["interval"])
            check_type(argname="argument latency_outlier_detection_algorithm", value=latency_outlier_detection_algorithm, expected_type=type_hints["latency_outlier_detection_algorithm"])
            check_type(argname="argument latency_outlier_metric_aggregation", value=latency_outlier_metric_aggregation, expected_type=type_hints["latency_outlier_metric_aggregation"])
            check_type(argname="argument latency_outlier_threshold", value=latency_outlier_threshold, expected_type=type_hints["latency_outlier_threshold"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "service": service,
        }
        if assets_bucket_parameter_name is not None:
            self._values["assets_bucket_parameter_name"] = assets_bucket_parameter_name
        if assets_bucket_prefix_parameter_name is not None:
            self._values["assets_bucket_prefix_parameter_name"] = assets_bucket_prefix_parameter_name
        if availability_outlier_detection_algorithm is not None:
            self._values["availability_outlier_detection_algorithm"] = availability_outlier_detection_algorithm
        if availability_outlier_threshold is not None:
            self._values["availability_outlier_threshold"] = availability_outlier_threshold
        if create_dashboards is not None:
            self._values["create_dashboards"] = create_dashboards
        if interval is not None:
            self._values["interval"] = interval
        if latency_outlier_detection_algorithm is not None:
            self._values["latency_outlier_detection_algorithm"] = latency_outlier_detection_algorithm
        if latency_outlier_metric_aggregation is not None:
            self._values["latency_outlier_metric_aggregation"] = latency_outlier_metric_aggregation
        if latency_outlier_threshold is not None:
            self._values["latency_outlier_threshold"] = latency_outlier_threshold

    @builtins.property
    def service(self) -> IService:
        '''(experimental) The service that the alarms and dashboards are being crated for.

        :stability: experimental
        '''
        result = self._values.get("service")
        assert result is not None, "Required property 'service' is missing"
        return typing.cast(IService, result)

    @builtins.property
    def assets_bucket_parameter_name(self) -> typing.Optional[builtins.str]:
        '''(experimental) If you are not using a static bucket to deploy assets, for example you are synthing this and it gets uploaded to a bucket whose name is unknown to you (maybe used as part of a central CI/CD system) and is provided as a parameter to your stack, specify that parameter name here.

        It will override the bucket location CDK provides by
        default for bundled assets. The stack containing this contruct needs
        to have a parameter defined that uses this name. The underlying
        stacks in this construct that deploy assets will copy the parent stack's
        value for this property.

        :default:

        - The assets will be uploaded to the default defined
        asset location.

        :stability: experimental
        '''
        result = self._values.get("assets_bucket_parameter_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def assets_bucket_prefix_parameter_name(self) -> typing.Optional[builtins.str]:
        '''(experimental) If you are not using a static bucket to deploy assets, for example you are synthing this and it gets uploaded to a bucket that uses a prefix that is unknown to you (maybe used as part of a central CI/CD system) and is provided as a parameter to your stack, specify that parameter name here.

        It will override the bucket prefix CDK provides by
        default for bundled assets. This property only takes effect if you
        defined the assetsBucketParameterName. The stack containing this contruct needs
        to have a parameter defined that uses this name. The underlying
        stacks in this construct that deploy assets will copy the parent stack's
        value for this property.

        :default:

        - No object prefix will be added to your custom assets location.
        However, if you have overridden something like the 'BucketPrefix' property
        in your stack synthesizer with a variable like "${AssetsBucketPrefix",
        you will need to define this property so it doesn't cause a reference error
        even if the prefix value is blank.

        :stability: experimental
        '''
        result = self._values.get("assets_bucket_prefix_parameter_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def availability_outlier_detection_algorithm(
        self,
    ) -> typing.Optional["OutlierDetectionAlgorithm"]:
        '''(experimental) The algorithm to use for performing outlier detection for availability metrics.

        ** Currently only STATIC is supported **

        :default: OutlierDetectionAlgorithm.STATIC

        :stability: experimental
        '''
        result = self._values.get("availability_outlier_detection_algorithm")
        return typing.cast(typing.Optional["OutlierDetectionAlgorithm"], result)

    @builtins.property
    def availability_outlier_threshold(self) -> typing.Optional[jsii.Number]:
        '''(experimental) The outlier threshold for determining if an AZ is an outlier for faults.

        This number is interpreted
        differently for different outlier algorithms. When used with
        STATIC, the number should be between 0 and 1 to represent the
        percentage of errors (like .7) that an AZ must be responsible
        for to be considered an outlier. When used with CHI_SQUARED, it
        represents the p value that indicates statistical significance, like
        0.05 which means the skew has less than or equal to a 5% chance of
        occuring. When used with Z_SCORE it indicates how many standard
        deviations to evaluate for an AZ being an outlier, typically 3 is
        standard for Z_SCORE.

        Standard defaults based on the outlier detection algorithm:
        STATIC: 0.7
        CHI_SQUARED: 0.05
        Z_SCORE: 3
        IQR: 1.5
        MAD: 3

        :default: - Depends on the outlier detection algorithm selected

        :stability: experimental
        '''
        result = self._values.get("availability_outlier_threshold")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def create_dashboards(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Indicates whether to create per operation and overall service dashboards.

        :default: - No dashboards are created

        :stability: experimental
        '''
        result = self._values.get("create_dashboards")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def interval(self) -> typing.Optional[_aws_cdk_ceddda9d.Duration]:
        '''(experimental) The interval used in the dashboard, defaults to 60 minutes.

        :default: - 60 minutes

        :stability: experimental
        '''
        result = self._values.get("interval")
        return typing.cast(typing.Optional[_aws_cdk_ceddda9d.Duration], result)

    @builtins.property
    def latency_outlier_detection_algorithm(
        self,
    ) -> typing.Optional["OutlierDetectionAlgorithm"]:
        '''(experimental) The algorithm to use for performing outlier detection for latency metrics.

        ** Currently only STATIC is supported **

        :default: OutlierDetectionAlgorithm.STATIC

        :stability: experimental
        '''
        result = self._values.get("latency_outlier_detection_algorithm")
        return typing.cast(typing.Optional["OutlierDetectionAlgorithm"], result)

    @builtins.property
    def latency_outlier_metric_aggregation(
        self,
    ) -> typing.Optional["LatencyOutlierMetricAggregation"]:
        '''(experimental) The metric for latency to use in outlier detection, which means whether the algorithm uses a count of requests exceeding your latency threshold or whether it uses the actual latency values at your latency alarm threshold statistic.

        :default: LatencyOutlierMetric.COUNT

        :stability: experimental
        '''
        result = self._values.get("latency_outlier_metric_aggregation")
        return typing.cast(typing.Optional["LatencyOutlierMetricAggregation"], result)

    @builtins.property
    def latency_outlier_threshold(self) -> typing.Optional[jsii.Number]:
        '''(experimental) The outlier threshold for determining if an AZ is an outlier for latency.

        This number is interpreted
        differently for different outlier algorithms. When used with
        STATIC, the number should be between 0 and 1 to represent the
        percentage of errors (like .7) that an AZ must be responsible
        for to be considered an outlier. When used with CHI_SQUARED, it
        represents the p value that indicates statistical significance, like
        0.05 which means the skew has less than or equal to a 5% chance of
        occuring. When used with Z_SCORE it indicates how many standard
        deviations to evaluate for an AZ being an outlier, typically 3 is
        standard for Z_SCORE.

        Standard defaults based on the outlier detection algorithm:
        STATIC: 0.7
        CHI_SQUARED: 0.05
        Z_SCORE: 3
        IQR: 1.5
        MAD: 3

        :default: - Depends on the outlier detection algorithm selected

        :stability: experimental
        '''
        result = self._values.get("latency_outlier_threshold")
        return typing.cast(typing.Optional[jsii.Number], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "InstrumentedServiceMultiAZObservabilityProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.enum(jsii_type="@cdklabs/multi-az-observability.LatencyOutlierMetricAggregation")
class LatencyOutlierMetricAggregation(enum.Enum):
    '''(experimental) The latency metric aggregation to use for latency outlier detection.

    :stability: experimental
    '''

    COUNT = "COUNT"
    '''(experimental) This option will use the count of the number of requests exceeding a latency threshold to make an outlier comparison.

    This option works
    with all outlier detection algorithms

    :stability: experimental
    '''
    VALUE = "VALUE"
    '''(experimental) This option will use the value of your provided latency statistic, like p99, and the value of the latency in each AZ will be compared.

    For example,
    AZ1: p99 = 125ms
    AZ2: p99 = 130ms
    AZ3: p99 = 250ms

    These values will be compared using the provided outlier detection algorithm. This
    option is not compatible with the STATIC outlier detection algorithm.

    :stability: experimental
    '''


class MetricDimensions(
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdklabs/multi-az-observability.MetricDimensions",
):
    '''(experimental) Provides the ability to get operation specific metric dimensions for metrics at the regional level as well as Availability Zone level.

    :stability: experimental
    '''

    def __init__(
        self,
        static_dimensions: typing.Mapping[builtins.str, builtins.str],
        availability_zone_id_key: builtins.str,
        region_key: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param static_dimensions: -
        :param availability_zone_id_key: -
        :param region_key: -

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__bd7b3882b73626eaa6b3b06fcbebe18c8bf307877c05b85e85abb78412d306ce)
            check_type(argname="argument static_dimensions", value=static_dimensions, expected_type=type_hints["static_dimensions"])
            check_type(argname="argument availability_zone_id_key", value=availability_zone_id_key, expected_type=type_hints["availability_zone_id_key"])
            check_type(argname="argument region_key", value=region_key, expected_type=type_hints["region_key"])
        jsii.create(self.__class__, self, [static_dimensions, availability_zone_id_key, region_key])

    @jsii.member(jsii_name="regionalDimensions")
    def regional_dimensions(
        self,
        region: builtins.str,
    ) -> typing.Mapping[builtins.str, builtins.str]:
        '''(experimental) Gets the regional dimensions for these metrics by combining the static metric dimensions with the keys provided the optional Region key, expected to return something like {   "Region": "us-east-1",   "Operation": "ride",   "Service": "WildRydes" }.

        :param region: -

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6c477603807c11fe9f762a28cbadbca8e687bb558fb6741ae91ee87ccb17a4b4)
            check_type(argname="argument region", value=region, expected_type=type_hints["region"])
        return typing.cast(typing.Mapping[builtins.str, builtins.str], jsii.invoke(self, "regionalDimensions", [region]))

    @jsii.member(jsii_name="zonalDimensions")
    def zonal_dimensions(
        self,
        availability_zone_id: builtins.str,
        region: builtins.str,
    ) -> typing.Mapping[builtins.str, builtins.str]:
        '''(experimental) Gets the zonal dimensions for these metrics by combining the static metric dimensions with the keys provided for Availability Zone and optional Region, expected to return something like {   "Region": "us-east-1",   "AZ-ID": "use1-az1",   "Operation": "ride",   "Service": "WildRydes" }.

        :param availability_zone_id: -
        :param region: -

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__35f1a092f9c0d7e57ff0f8a6cf760d1c5b80d37efb34621151454b4da865c3e6)
            check_type(argname="argument availability_zone_id", value=availability_zone_id, expected_type=type_hints["availability_zone_id"])
            check_type(argname="argument region", value=region, expected_type=type_hints["region"])
        return typing.cast(typing.Mapping[builtins.str, builtins.str], jsii.invoke(self, "zonalDimensions", [availability_zone_id, region]))

    @builtins.property
    @jsii.member(jsii_name="availabilityZoneIdKey")
    def availability_zone_id_key(self) -> builtins.str:
        '''(experimental) The key used to specify an Availability Zone specific metric dimension, for example: "AZ-ID".

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "availabilityZoneIdKey"))

    @availability_zone_id_key.setter
    def availability_zone_id_key(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__efa8f1730b98ea1dd1da14300d6e91b137e5e8e9db7af446fa1cf00c69c322c2)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "availabilityZoneIdKey", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="staticDimensions")
    def static_dimensions(self) -> typing.Mapping[builtins.str, builtins.str]:
        '''(experimental) The dimensions that are the same for all Availability Zones for example: {   "Operation": "ride",   "Service": "WildRydes" }.

        :stability: experimental
        '''
        return typing.cast(typing.Mapping[builtins.str, builtins.str], jsii.get(self, "staticDimensions"))

    @static_dimensions.setter
    def static_dimensions(
        self,
        value: typing.Mapping[builtins.str, builtins.str],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ca4cfd20f3782e7ec6430b1c3d943d15eece045928388fcf7e3c3c8ea2e7248b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "staticDimensions", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="regionKey")
    def region_key(self) -> typing.Optional[builtins.str]:
        '''(experimental) The key used for the Region in your dimensions, if you provide one.

        :default:

        - A region specific key and value is not added to your
        zonal and regional metric dimensions

        :stability: experimental
        '''
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "regionKey"))

    @region_key.setter
    def region_key(self, value: typing.Optional[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__39c910d076892eb126ef774ed69b3d8b582d9980d910ee784c923f4284583b9f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "regionKey", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdklabs/multi-az-observability.MinimumUnhealthyTargets",
    jsii_struct_bases=[],
    name_mapping={"count": "count", "percentage": "percentage"},
)
class MinimumUnhealthyTargets:
    def __init__(
        self,
        *,
        count: typing.Optional[jsii.Number] = None,
        percentage: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''(experimental) The minimum unhealthy targets for an AZ to be considered impaired instead of individual targets in the zone.

        You must specify either count or percentage,
        if you specify both, only count will be used.

        :param count: (experimental) The minimum number of targets that must be unhealthy. If the number of unhealthy targets is equal to this, or greater, the impact ot a single AZ is not considered ot be from a "single" target. You must specify either count or percentage, if you specify both, only count will be used. Default: This value is not used
        :param percentage: (experimental) The minimum percentage of targets that must be unhealthy. If the percentage of unhealthy targets is equal to this, or greater, the impact to a single AZ is not considered to be from a "single" target. You must specify either count or percentage, if you specify both, only count will be used. Default: This value is not used

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c006afbf726eab97f48b4f4bef13d8d5072727a47d4387daebd2a545cf7848ce)
            check_type(argname="argument count", value=count, expected_type=type_hints["count"])
            check_type(argname="argument percentage", value=percentage, expected_type=type_hints["percentage"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if count is not None:
            self._values["count"] = count
        if percentage is not None:
            self._values["percentage"] = percentage

    @builtins.property
    def count(self) -> typing.Optional[jsii.Number]:
        '''(experimental) The minimum number of targets that must be unhealthy.

        If the number of
        unhealthy targets is equal to this, or greater, the impact ot a single AZ
        is not considered ot be from a "single" target. You must specify either count or percentage,
        if you specify both, only count will be used.

        :default: This value is not used

        :stability: experimental
        '''
        result = self._values.get("count")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def percentage(self) -> typing.Optional[jsii.Number]:
        '''(experimental) The minimum percentage of targets that must be unhealthy.

        If the percentage
        of unhealthy targets is equal to this, or greater, the impact to a single AZ
        is not considered to be from a "single" target. You must specify either count or percentage,
        if you specify both, only count will be used.

        :default: This value is not used

        :stability: experimental
        '''
        result = self._values.get("percentage")
        return typing.cast(typing.Optional[jsii.Number], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "MinimumUnhealthyTargets(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdklabs/multi-az-observability.NatGatewayDetectionProps",
    jsii_struct_bases=[],
    name_mapping={
        "nat_gateways": "natGateways",
        "packet_loss_outlier_algorithm": "packetLossOutlierAlgorithm",
        "packet_loss_outlier_threshold": "packetLossOutlierThreshold",
        "packet_loss_percent_threshold": "packetLossPercentThreshold",
    },
)
class NatGatewayDetectionProps:
    def __init__(
        self,
        *,
        nat_gateways: typing.Mapping[builtins.str, typing.Sequence[_aws_cdk_aws_ec2_ceddda9d.CfnNatGateway]],
        packet_loss_outlier_algorithm: typing.Optional["PacketLossOutlierAlgorithm"] = None,
        packet_loss_outlier_threshold: typing.Optional[jsii.Number] = None,
        packet_loss_percent_threshold: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''(experimental) The properties for performing zonal impact detection with NAT Gateway(s).

        :param nat_gateways: (experimental) A list of NAT Gateways per Availability Zone (using the AZ name as the key).
        :param packet_loss_outlier_algorithm: (experimental) The algorithm to use to calculate an AZ as an outlier for packet loss. Default: PacketLossOutlierAlgorithm.STATIC
        :param packet_loss_outlier_threshold: (experimental) The threshold used with the outlier calculation. Default: "This depends on the outlier algorithm. STATIC: 66. Z-SCORE: 3."
        :param packet_loss_percent_threshold: (experimental) The percentage of packet loss at which you consider there to be impact. Default: 0.01 (as in 0.01%)

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f2f991a5d8adc37a9d77adea91bbe71bd945c7bed07e41d7890230ee8d1dee4b)
            check_type(argname="argument nat_gateways", value=nat_gateways, expected_type=type_hints["nat_gateways"])
            check_type(argname="argument packet_loss_outlier_algorithm", value=packet_loss_outlier_algorithm, expected_type=type_hints["packet_loss_outlier_algorithm"])
            check_type(argname="argument packet_loss_outlier_threshold", value=packet_loss_outlier_threshold, expected_type=type_hints["packet_loss_outlier_threshold"])
            check_type(argname="argument packet_loss_percent_threshold", value=packet_loss_percent_threshold, expected_type=type_hints["packet_loss_percent_threshold"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "nat_gateways": nat_gateways,
        }
        if packet_loss_outlier_algorithm is not None:
            self._values["packet_loss_outlier_algorithm"] = packet_loss_outlier_algorithm
        if packet_loss_outlier_threshold is not None:
            self._values["packet_loss_outlier_threshold"] = packet_loss_outlier_threshold
        if packet_loss_percent_threshold is not None:
            self._values["packet_loss_percent_threshold"] = packet_loss_percent_threshold

    @builtins.property
    def nat_gateways(
        self,
    ) -> typing.Mapping[builtins.str, typing.List[_aws_cdk_aws_ec2_ceddda9d.CfnNatGateway]]:
        '''(experimental) A list of NAT Gateways per Availability Zone (using the AZ name as the key).

        :stability: experimental
        '''
        result = self._values.get("nat_gateways")
        assert result is not None, "Required property 'nat_gateways' is missing"
        return typing.cast(typing.Mapping[builtins.str, typing.List[_aws_cdk_aws_ec2_ceddda9d.CfnNatGateway]], result)

    @builtins.property
    def packet_loss_outlier_algorithm(
        self,
    ) -> typing.Optional["PacketLossOutlierAlgorithm"]:
        '''(experimental) The algorithm to use to calculate an AZ as an outlier for packet loss.

        :default: PacketLossOutlierAlgorithm.STATIC

        :stability: experimental
        '''
        result = self._values.get("packet_loss_outlier_algorithm")
        return typing.cast(typing.Optional["PacketLossOutlierAlgorithm"], result)

    @builtins.property
    def packet_loss_outlier_threshold(self) -> typing.Optional[jsii.Number]:
        '''(experimental) The threshold used with the outlier calculation.

        :default: "This depends on the outlier algorithm. STATIC: 66. Z-SCORE: 3."

        :stability: experimental
        '''
        result = self._values.get("packet_loss_outlier_threshold")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def packet_loss_percent_threshold(self) -> typing.Optional[jsii.Number]:
        '''(experimental) The percentage of packet loss at which you consider there to be impact.

        :default: 0.01 (as in 0.01%)

        :stability: experimental
        '''
        result = self._values.get("packet_loss_percent_threshold")
        return typing.cast(typing.Optional[jsii.Number], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "NatGatewayDetectionProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdklabs/multi-az-observability.NetworkConfigurationProps",
    jsii_struct_bases=[],
    name_mapping={"subnet_selection": "subnetSelection", "vpc": "vpc"},
)
class NetworkConfigurationProps:
    def __init__(
        self,
        *,
        subnet_selection: typing.Union[_aws_cdk_aws_ec2_ceddda9d.SubnetSelection, typing.Dict[builtins.str, typing.Any]],
        vpc: _aws_cdk_aws_ec2_ceddda9d.IVpc,
    ) -> None:
        '''(experimental) The network configuration for the canary function.

        :param subnet_selection: (experimental) The subnets the Lambda function will be deployed in the VPC.
        :param vpc: (experimental) The VPC to run the canary in. A security group will be created that allows the function to communicate with the VPC as well as the required IAM permissions.

        :stability: experimental
        '''
        if isinstance(subnet_selection, dict):
            subnet_selection = _aws_cdk_aws_ec2_ceddda9d.SubnetSelection(**subnet_selection)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2254e297551a7952836a56c7b1852e846ada986e2dbcb5f68b941d2043fc13c0)
            check_type(argname="argument subnet_selection", value=subnet_selection, expected_type=type_hints["subnet_selection"])
            check_type(argname="argument vpc", value=vpc, expected_type=type_hints["vpc"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "subnet_selection": subnet_selection,
            "vpc": vpc,
        }

    @builtins.property
    def subnet_selection(self) -> _aws_cdk_aws_ec2_ceddda9d.SubnetSelection:
        '''(experimental) The subnets the Lambda function will be deployed in the VPC.

        :stability: experimental
        '''
        result = self._values.get("subnet_selection")
        assert result is not None, "Required property 'subnet_selection' is missing"
        return typing.cast(_aws_cdk_aws_ec2_ceddda9d.SubnetSelection, result)

    @builtins.property
    def vpc(self) -> _aws_cdk_aws_ec2_ceddda9d.IVpc:
        '''(experimental) The VPC to run the canary in.

        A security group will be created
        that allows the function to communicate with the VPC as well
        as the required IAM permissions.

        :stability: experimental
        '''
        result = self._values.get("vpc")
        assert result is not None, "Required property 'vpc' is missing"
        return typing.cast(_aws_cdk_aws_ec2_ceddda9d.IVpc, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "NetworkConfigurationProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.implements(IOperation)
class Operation(
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdklabs/multi-az-observability.Operation",
):
    '''(experimental) A single operation that is part of a service.

    :stability: experimental
    '''

    def __init__(
        self,
        *,
        critical: builtins.bool,
        http_methods: typing.Sequence[builtins.str],
        operation_name: builtins.str,
        path: builtins.str,
        server_side_availability_metric_details: "IOperationAvailabilityMetricDetails",
        server_side_latency_metric_details: "IOperationLatencyMetricDetails",
        service: IService,
        canary_metric_details: typing.Optional[ICanaryMetrics] = None,
        canary_test_availability_metrics_override: typing.Optional[ICanaryTestMetricsOverride] = None,
        canary_test_latency_metrics_override: typing.Optional[ICanaryTestMetricsOverride] = None,
        canary_test_props: typing.Optional[typing.Union[AddCanaryTestProps, typing.Dict[builtins.str, typing.Any]]] = None,
        opt_out_of_service_created_canary: typing.Optional[builtins.bool] = None,
        server_side_contributor_insight_rule_details: typing.Optional[IContributorInsightRuleDetails] = None,
    ) -> None:
        '''
        :param critical: (experimental) Indicates this is a critical operation for the service and will be included in service level metrics and dashboards.
        :param http_methods: (experimental) The http methods supported by the operation.
        :param operation_name: (experimental) The name of the operation.
        :param path: (experimental) The HTTP path for the operation for canaries to run against, something like "/products/list".
        :param server_side_availability_metric_details: (experimental) The server side availability metric details.
        :param server_side_latency_metric_details: (experimental) The server side latency metric details.
        :param service: (experimental) The service the operation is associated with.
        :param canary_metric_details: (experimental) Optional metric details if the service has a canary. Default: - No alarms, rules, or dashboards will be created from canary metrics
        :param canary_test_availability_metrics_override: (experimental) The override values for automatically created canary tests so you can use values other than the service defaults to define the thresholds for availability. Default: - No availability metric details will be overridden and the service defaults will be used for the automatically created canaries
        :param canary_test_latency_metrics_override: (experimental) The override values for automatically created canary tests so you can use values other than the service defaults to define the thresholds for latency. Default: - No latency metric details will be overridden and the service defaults will be used for the automatically created canaries
        :param canary_test_props: (experimental) If you define this property, a synthetic canary will be provisioned to test the operation. Default: - The default for the service will be used, if that is undefined, then no canary will be provisioned for this operation.
        :param opt_out_of_service_created_canary: (experimental) Set to true if you have defined CanaryTestProps for your service, which applies to all operations, but you want to opt out of creating the canary test for this operation. Default: - The operation is not opted out
        :param server_side_contributor_insight_rule_details: (experimental) The server side details for contributor insights rules. Default: - The default service contributor insight rule details will be used. If those are not defined no Contributor Insight rules will be created and the number of instances contributing to AZ faults or high latency will not be considered, so a single bad instance could make the AZ appear to look impaired.

        :stability: experimental
        '''
        props = OperationProps(
            critical=critical,
            http_methods=http_methods,
            operation_name=operation_name,
            path=path,
            server_side_availability_metric_details=server_side_availability_metric_details,
            server_side_latency_metric_details=server_side_latency_metric_details,
            service=service,
            canary_metric_details=canary_metric_details,
            canary_test_availability_metrics_override=canary_test_availability_metrics_override,
            canary_test_latency_metrics_override=canary_test_latency_metrics_override,
            canary_test_props=canary_test_props,
            opt_out_of_service_created_canary=opt_out_of_service_created_canary,
            server_side_contributor_insight_rule_details=server_side_contributor_insight_rule_details,
        )

        jsii.create(self.__class__, self, [props])

    @builtins.property
    @jsii.member(jsii_name="critical")
    def critical(self) -> builtins.bool:
        '''(experimental) Indicates this is a critical operation for the service and will be included in service level metrics and dashboards.

        :stability: experimental
        '''
        return typing.cast(builtins.bool, jsii.get(self, "critical"))

    @builtins.property
    @jsii.member(jsii_name="httpMethods")
    def http_methods(self) -> typing.List[builtins.str]:
        '''(experimental) The http methods supported by the operation.

        :stability: experimental
        '''
        return typing.cast(typing.List[builtins.str], jsii.get(self, "httpMethods"))

    @builtins.property
    @jsii.member(jsii_name="operationName")
    def operation_name(self) -> builtins.str:
        '''(experimental) The name of the operation.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "operationName"))

    @builtins.property
    @jsii.member(jsii_name="path")
    def path(self) -> builtins.str:
        '''(experimental) The HTTP path for the operation for canaries to run against, something like "/products/list".

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "path"))

    @builtins.property
    @jsii.member(jsii_name="serverSideAvailabilityMetricDetails")
    def server_side_availability_metric_details(
        self,
    ) -> "IOperationAvailabilityMetricDetails":
        '''(experimental) The server side availability metric details.

        :stability: experimental
        '''
        return typing.cast("IOperationAvailabilityMetricDetails", jsii.get(self, "serverSideAvailabilityMetricDetails"))

    @builtins.property
    @jsii.member(jsii_name="serverSideLatencyMetricDetails")
    def server_side_latency_metric_details(self) -> "IOperationLatencyMetricDetails":
        '''(experimental) The server side latency metric details.

        :stability: experimental
        '''
        return typing.cast("IOperationLatencyMetricDetails", jsii.get(self, "serverSideLatencyMetricDetails"))

    @builtins.property
    @jsii.member(jsii_name="service")
    def service(self) -> IService:
        '''(experimental) The service the operation is associated with.

        :stability: experimental
        '''
        return typing.cast(IService, jsii.get(self, "service"))

    @builtins.property
    @jsii.member(jsii_name="canaryMetricDetails")
    def canary_metric_details(self) -> typing.Optional[ICanaryMetrics]:
        '''(experimental) Optional metric details if the service has a canary.

        :stability: experimental
        '''
        return typing.cast(typing.Optional[ICanaryMetrics], jsii.get(self, "canaryMetricDetails"))

    @builtins.property
    @jsii.member(jsii_name="canaryTestAvailabilityMetricsOverride")
    def canary_test_availability_metrics_override(
        self,
    ) -> typing.Optional["ICanaryTestAvailabilityMetricsOverride"]:
        '''(experimental) The override values for automatically created canary tests so you can use values other than the service defaults to define the thresholds for availability.

        :stability: experimental
        '''
        return typing.cast(typing.Optional["ICanaryTestAvailabilityMetricsOverride"], jsii.get(self, "canaryTestAvailabilityMetricsOverride"))

    @builtins.property
    @jsii.member(jsii_name="canaryTestLatencyMetricsOverride")
    def canary_test_latency_metrics_override(
        self,
    ) -> typing.Optional["ICanaryTestLatencyMetricsOverride"]:
        '''(experimental) The override values for automatically created canary tests so you can use values other than the service defaults to define the thresholds for latency.

        :stability: experimental
        '''
        return typing.cast(typing.Optional["ICanaryTestLatencyMetricsOverride"], jsii.get(self, "canaryTestLatencyMetricsOverride"))

    @builtins.property
    @jsii.member(jsii_name="canaryTestProps")
    def canary_test_props(self) -> typing.Optional[AddCanaryTestProps]:
        '''(experimental) If they have been added, the properties for creating new canary tests on this operation.

        :stability: experimental
        '''
        return typing.cast(typing.Optional[AddCanaryTestProps], jsii.get(self, "canaryTestProps"))

    @builtins.property
    @jsii.member(jsii_name="optOutOfServiceCreatedCanary")
    def opt_out_of_service_created_canary(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Set to true if you have defined CanaryTestProps for your service, which applies to all operations, but you want to opt out of creating the canary test for this operation.

        :default: - The operation is not opted out

        :stability: experimental
        '''
        return typing.cast(typing.Optional[builtins.bool], jsii.get(self, "optOutOfServiceCreatedCanary"))

    @builtins.property
    @jsii.member(jsii_name="serverSideContributorInsightRuleDetails")
    def server_side_contributor_insight_rule_details(
        self,
    ) -> typing.Optional[IContributorInsightRuleDetails]:
        '''(experimental) The server side details for contributor insights rules.

        :stability: experimental
        '''
        return typing.cast(typing.Optional[IContributorInsightRuleDetails], jsii.get(self, "serverSideContributorInsightRuleDetails"))


@jsii.implements(IOperationMetricDetails)
class OperationMetricDetails(
    metaclass=jsii.JSIIAbstractClass,
    jsii_type="@cdklabs/multi-az-observability.OperationMetricDetails",
):
    '''(experimental) Generic metric details for an operation.

    :stability: experimental
    '''

    def __init__(
        self,
        props: typing.Union["OperationMetricDetailsProps", typing.Dict[builtins.str, typing.Any]],
        default_props: IServiceMetricDetails,
    ) -> None:
        '''
        :param props: -
        :param default_props: -

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__19a022b187025b0dfb90bfc09b2588a136424989f7af6d6d7c8ee11cb7822d6b)
            check_type(argname="argument props", value=props, expected_type=type_hints["props"])
            check_type(argname="argument default_props", value=default_props, expected_type=type_hints["default_props"])
        jsii.create(self.__class__, self, [props, default_props])

    @builtins.property
    @jsii.member(jsii_name="alarmStatistic")
    def alarm_statistic(self) -> builtins.str:
        '''(experimental) The statistic used for alarms, for availability metrics this should be "Sum", for latency metrics it could something like "p99" or "p99.9".

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "alarmStatistic"))

    @builtins.property
    @jsii.member(jsii_name="datapointsToAlarm")
    def datapoints_to_alarm(self) -> jsii.Number:
        '''(experimental) The number of datapoints to alarm on for latency and availability alarms.

        :stability: experimental
        '''
        return typing.cast(jsii.Number, jsii.get(self, "datapointsToAlarm"))

    @builtins.property
    @jsii.member(jsii_name="evaluationPeriods")
    def evaluation_periods(self) -> jsii.Number:
        '''(experimental) The number of evaluation periods for latency and availabiltiy alarms.

        :stability: experimental
        '''
        return typing.cast(jsii.Number, jsii.get(self, "evaluationPeriods"))

    @builtins.property
    @jsii.member(jsii_name="faultMetricNames")
    def fault_metric_names(self) -> typing.List[builtins.str]:
        '''(experimental) The names of fault indicating metrics.

        :stability: experimental
        '''
        return typing.cast(typing.List[builtins.str], jsii.get(self, "faultMetricNames"))

    @builtins.property
    @jsii.member(jsii_name="metricDimensions")
    def metric_dimensions(self) -> MetricDimensions:
        '''(experimental) The metric dimensions for this operation, must be implemented as a concrete class by the user.

        :stability: experimental
        '''
        return typing.cast(MetricDimensions, jsii.get(self, "metricDimensions"))

    @builtins.property
    @jsii.member(jsii_name="metricNamespace")
    def metric_namespace(self) -> builtins.str:
        '''(experimental) The CloudWatch metric namespace for these metrics.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "metricNamespace"))

    @builtins.property
    @jsii.member(jsii_name="operationName")
    def operation_name(self) -> builtins.str:
        '''(experimental) The operation these metric details are for.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "operationName"))

    @builtins.property
    @jsii.member(jsii_name="period")
    def period(self) -> _aws_cdk_ceddda9d.Duration:
        '''(experimental) The period for the metrics.

        :stability: experimental
        '''
        return typing.cast(_aws_cdk_ceddda9d.Duration, jsii.get(self, "period"))

    @builtins.property
    @jsii.member(jsii_name="successMetricNames")
    def success_metric_names(self) -> typing.List[builtins.str]:
        '''(experimental) The names of success indicating metrics.

        :stability: experimental
        '''
        return typing.cast(typing.List[builtins.str], jsii.get(self, "successMetricNames"))

    @builtins.property
    @jsii.member(jsii_name="unit")
    def unit(self) -> _aws_cdk_aws_cloudwatch_ceddda9d.Unit:
        '''(experimental) The unit used for these metrics.

        :stability: experimental
        '''
        return typing.cast(_aws_cdk_aws_cloudwatch_ceddda9d.Unit, jsii.get(self, "unit"))

    @builtins.property
    @jsii.member(jsii_name="graphedFaultStatistics")
    def graphed_fault_statistics(self) -> typing.Optional[typing.List[builtins.str]]:
        '''(experimental) The statistics for faults you want to appear on dashboards, for example, with latency metrics, you might want p50, p99, and tm99.

        For availability
        metrics this will typically just be "Sum".

        :default: - For availability metrics, this will be "Sum", for latency metrics it will be just "p99"

        :stability: experimental
        '''
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "graphedFaultStatistics"))

    @builtins.property
    @jsii.member(jsii_name="graphedSuccessStatistics")
    def graphed_success_statistics(self) -> typing.Optional[typing.List[builtins.str]]:
        '''(experimental) The statistics for successes you want to appear on dashboards, for example, with latency metrics, you might want p50, p99, and tm99.

        For availability
        metrics this will typically just be "Sum".

        :default: - For availability metrics, this will be "Sum", for latency metrics it will be just "p99"

        :stability: experimental
        '''
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "graphedSuccessStatistics"))


class _OperationMetricDetailsProxy(OperationMetricDetails):
    pass

# Adding a "__jsii_proxy_class__(): typing.Type" function to the abstract class
typing.cast(typing.Any, OperationMetricDetails).__jsii_proxy_class__ = lambda : _OperationMetricDetailsProxy


@jsii.data_type(
    jsii_type="@cdklabs/multi-az-observability.OperationMetricDetailsProps",
    jsii_struct_bases=[],
    name_mapping={
        "metric_dimensions": "metricDimensions",
        "operation_name": "operationName",
        "alarm_statistic": "alarmStatistic",
        "datapoints_to_alarm": "datapointsToAlarm",
        "evaluation_periods": "evaluationPeriods",
        "fault_metric_names": "faultMetricNames",
        "graphed_fault_statistics": "graphedFaultStatistics",
        "graphed_success_statistics": "graphedSuccessStatistics",
        "metric_namespace": "metricNamespace",
        "period": "period",
        "success_metric_names": "successMetricNames",
        "unit": "unit",
    },
)
class OperationMetricDetailsProps:
    def __init__(
        self,
        *,
        metric_dimensions: MetricDimensions,
        operation_name: builtins.str,
        alarm_statistic: typing.Optional[builtins.str] = None,
        datapoints_to_alarm: typing.Optional[jsii.Number] = None,
        evaluation_periods: typing.Optional[jsii.Number] = None,
        fault_metric_names: typing.Optional[typing.Sequence[builtins.str]] = None,
        graphed_fault_statistics: typing.Optional[typing.Sequence[builtins.str]] = None,
        graphed_success_statistics: typing.Optional[typing.Sequence[builtins.str]] = None,
        metric_namespace: typing.Optional[builtins.str] = None,
        period: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
        success_metric_names: typing.Optional[typing.Sequence[builtins.str]] = None,
        unit: typing.Optional[_aws_cdk_aws_cloudwatch_ceddda9d.Unit] = None,
    ) -> None:
        '''(experimental) The properties for operation metric details.

        :param metric_dimensions: (experimental) The user implemented functions for providing the metric's dimensions.
        :param operation_name: (experimental) The operation these metric details are for.
        :param alarm_statistic: (experimental) The statistic used for alarms, for availability metrics this should be "Sum", for latency metrics it could something like "p99" or "p99.9". Default: - The service default is used
        :param datapoints_to_alarm: (experimental) The number of datapoints to alarm on for latency and availability alarms. Default: - The service default is used
        :param evaluation_periods: (experimental) The number of evaluation periods for latency and availabiltiy alarms. Default: - The service default is used
        :param fault_metric_names: (experimental) The names of fault indicating metrics. Default: - The service default is used
        :param graphed_fault_statistics: (experimental) The statistics for faults you want to appear on dashboards, for example, with latency metrics, you might want p50, p99, and tm99. For availability metrics this will typically just be "Sum". Default: - The service default is used
        :param graphed_success_statistics: (experimental) The statistics for successes you want to appear on dashboards, for example, with latency metrics, you might want p50, p99, and tm99. For availability metrics this will typically just be "Sum". Default: - The service default is used
        :param metric_namespace: (experimental) The CloudWatch metric namespace for these metrics. Default: - The service default is used
        :param period: (experimental) The period for the metrics. Default: - The service default is used
        :param success_metric_names: (experimental) The names of success indicating metrics. Default: - The service default is used
        :param unit: (experimental) The unit used for these metrics. Default: - The service default is used

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__df81185b60a72d1681cbab65087b8dcadf4c04fe83ae02f1ebdc511a8d73efec)
            check_type(argname="argument metric_dimensions", value=metric_dimensions, expected_type=type_hints["metric_dimensions"])
            check_type(argname="argument operation_name", value=operation_name, expected_type=type_hints["operation_name"])
            check_type(argname="argument alarm_statistic", value=alarm_statistic, expected_type=type_hints["alarm_statistic"])
            check_type(argname="argument datapoints_to_alarm", value=datapoints_to_alarm, expected_type=type_hints["datapoints_to_alarm"])
            check_type(argname="argument evaluation_periods", value=evaluation_periods, expected_type=type_hints["evaluation_periods"])
            check_type(argname="argument fault_metric_names", value=fault_metric_names, expected_type=type_hints["fault_metric_names"])
            check_type(argname="argument graphed_fault_statistics", value=graphed_fault_statistics, expected_type=type_hints["graphed_fault_statistics"])
            check_type(argname="argument graphed_success_statistics", value=graphed_success_statistics, expected_type=type_hints["graphed_success_statistics"])
            check_type(argname="argument metric_namespace", value=metric_namespace, expected_type=type_hints["metric_namespace"])
            check_type(argname="argument period", value=period, expected_type=type_hints["period"])
            check_type(argname="argument success_metric_names", value=success_metric_names, expected_type=type_hints["success_metric_names"])
            check_type(argname="argument unit", value=unit, expected_type=type_hints["unit"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "metric_dimensions": metric_dimensions,
            "operation_name": operation_name,
        }
        if alarm_statistic is not None:
            self._values["alarm_statistic"] = alarm_statistic
        if datapoints_to_alarm is not None:
            self._values["datapoints_to_alarm"] = datapoints_to_alarm
        if evaluation_periods is not None:
            self._values["evaluation_periods"] = evaluation_periods
        if fault_metric_names is not None:
            self._values["fault_metric_names"] = fault_metric_names
        if graphed_fault_statistics is not None:
            self._values["graphed_fault_statistics"] = graphed_fault_statistics
        if graphed_success_statistics is not None:
            self._values["graphed_success_statistics"] = graphed_success_statistics
        if metric_namespace is not None:
            self._values["metric_namespace"] = metric_namespace
        if period is not None:
            self._values["period"] = period
        if success_metric_names is not None:
            self._values["success_metric_names"] = success_metric_names
        if unit is not None:
            self._values["unit"] = unit

    @builtins.property
    def metric_dimensions(self) -> MetricDimensions:
        '''(experimental) The user implemented functions for providing the metric's dimensions.

        :stability: experimental
        '''
        result = self._values.get("metric_dimensions")
        assert result is not None, "Required property 'metric_dimensions' is missing"
        return typing.cast(MetricDimensions, result)

    @builtins.property
    def operation_name(self) -> builtins.str:
        '''(experimental) The operation these metric details are for.

        :stability: experimental
        '''
        result = self._values.get("operation_name")
        assert result is not None, "Required property 'operation_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def alarm_statistic(self) -> typing.Optional[builtins.str]:
        '''(experimental) The statistic used for alarms, for availability metrics this should be "Sum", for latency metrics it could something like "p99" or "p99.9".

        :default: - The service default is used

        :stability: experimental
        '''
        result = self._values.get("alarm_statistic")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def datapoints_to_alarm(self) -> typing.Optional[jsii.Number]:
        '''(experimental) The number of datapoints to alarm on for latency and availability alarms.

        :default: - The service default is used

        :stability: experimental
        '''
        result = self._values.get("datapoints_to_alarm")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def evaluation_periods(self) -> typing.Optional[jsii.Number]:
        '''(experimental) The number of evaluation periods for latency and availabiltiy alarms.

        :default: - The service default is used

        :stability: experimental
        '''
        result = self._values.get("evaluation_periods")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def fault_metric_names(self) -> typing.Optional[typing.List[builtins.str]]:
        '''(experimental) The names of fault indicating metrics.

        :default: - The service default is used

        :stability: experimental
        '''
        result = self._values.get("fault_metric_names")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def graphed_fault_statistics(self) -> typing.Optional[typing.List[builtins.str]]:
        '''(experimental) The statistics for faults you want to appear on dashboards, for example, with latency metrics, you might want p50, p99, and tm99.

        For availability
        metrics this will typically just be "Sum".

        :default: - The service default is used

        :stability: experimental
        '''
        result = self._values.get("graphed_fault_statistics")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def graphed_success_statistics(self) -> typing.Optional[typing.List[builtins.str]]:
        '''(experimental) The statistics for successes you want to appear on dashboards, for example, with latency metrics, you might want p50, p99, and tm99.

        For availability
        metrics this will typically just be "Sum".

        :default: - The service default is used

        :stability: experimental
        '''
        result = self._values.get("graphed_success_statistics")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def metric_namespace(self) -> typing.Optional[builtins.str]:
        '''(experimental) The CloudWatch metric namespace for these metrics.

        :default: - The service default is used

        :stability: experimental
        '''
        result = self._values.get("metric_namespace")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def period(self) -> typing.Optional[_aws_cdk_ceddda9d.Duration]:
        '''(experimental) The period for the metrics.

        :default: - The service default is used

        :stability: experimental
        '''
        result = self._values.get("period")
        return typing.cast(typing.Optional[_aws_cdk_ceddda9d.Duration], result)

    @builtins.property
    def success_metric_names(self) -> typing.Optional[typing.List[builtins.str]]:
        '''(experimental) The names of success indicating metrics.

        :default: - The service default is used

        :stability: experimental
        '''
        result = self._values.get("success_metric_names")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def unit(self) -> typing.Optional[_aws_cdk_aws_cloudwatch_ceddda9d.Unit]:
        '''(experimental) The unit used for these metrics.

        :default: - The service default is used

        :stability: experimental
        '''
        result = self._values.get("unit")
        return typing.cast(typing.Optional[_aws_cdk_aws_cloudwatch_ceddda9d.Unit], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "OperationMetricDetailsProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdklabs/multi-az-observability.OperationProps",
    jsii_struct_bases=[],
    name_mapping={
        "critical": "critical",
        "http_methods": "httpMethods",
        "operation_name": "operationName",
        "path": "path",
        "server_side_availability_metric_details": "serverSideAvailabilityMetricDetails",
        "server_side_latency_metric_details": "serverSideLatencyMetricDetails",
        "service": "service",
        "canary_metric_details": "canaryMetricDetails",
        "canary_test_availability_metrics_override": "canaryTestAvailabilityMetricsOverride",
        "canary_test_latency_metrics_override": "canaryTestLatencyMetricsOverride",
        "canary_test_props": "canaryTestProps",
        "opt_out_of_service_created_canary": "optOutOfServiceCreatedCanary",
        "server_side_contributor_insight_rule_details": "serverSideContributorInsightRuleDetails",
    },
)
class OperationProps:
    def __init__(
        self,
        *,
        critical: builtins.bool,
        http_methods: typing.Sequence[builtins.str],
        operation_name: builtins.str,
        path: builtins.str,
        server_side_availability_metric_details: "IOperationAvailabilityMetricDetails",
        server_side_latency_metric_details: "IOperationLatencyMetricDetails",
        service: IService,
        canary_metric_details: typing.Optional[ICanaryMetrics] = None,
        canary_test_availability_metrics_override: typing.Optional[ICanaryTestMetricsOverride] = None,
        canary_test_latency_metrics_override: typing.Optional[ICanaryTestMetricsOverride] = None,
        canary_test_props: typing.Optional[typing.Union[AddCanaryTestProps, typing.Dict[builtins.str, typing.Any]]] = None,
        opt_out_of_service_created_canary: typing.Optional[builtins.bool] = None,
        server_side_contributor_insight_rule_details: typing.Optional[IContributorInsightRuleDetails] = None,
    ) -> None:
        '''(experimental) Properties for an operation.

        :param critical: (experimental) Indicates this is a critical operation for the service and will be included in service level metrics and dashboards.
        :param http_methods: (experimental) The http methods supported by the operation.
        :param operation_name: (experimental) The name of the operation.
        :param path: (experimental) The HTTP path for the operation for canaries to run against, something like "/products/list".
        :param server_side_availability_metric_details: (experimental) The server side availability metric details.
        :param server_side_latency_metric_details: (experimental) The server side latency metric details.
        :param service: (experimental) The service the operation is associated with.
        :param canary_metric_details: (experimental) Optional metric details if the service has a canary. Default: - No alarms, rules, or dashboards will be created from canary metrics
        :param canary_test_availability_metrics_override: (experimental) The override values for automatically created canary tests so you can use values other than the service defaults to define the thresholds for availability. Default: - No availability metric details will be overridden and the service defaults will be used for the automatically created canaries
        :param canary_test_latency_metrics_override: (experimental) The override values for automatically created canary tests so you can use values other than the service defaults to define the thresholds for latency. Default: - No latency metric details will be overridden and the service defaults will be used for the automatically created canaries
        :param canary_test_props: (experimental) If you define this property, a synthetic canary will be provisioned to test the operation. Default: - The default for the service will be used, if that is undefined, then no canary will be provisioned for this operation.
        :param opt_out_of_service_created_canary: (experimental) Set to true if you have defined CanaryTestProps for your service, which applies to all operations, but you want to opt out of creating the canary test for this operation. Default: - The operation is not opted out
        :param server_side_contributor_insight_rule_details: (experimental) The server side details for contributor insights rules. Default: - The default service contributor insight rule details will be used. If those are not defined no Contributor Insight rules will be created and the number of instances contributing to AZ faults or high latency will not be considered, so a single bad instance could make the AZ appear to look impaired.

        :stability: experimental
        '''
        if isinstance(canary_test_props, dict):
            canary_test_props = AddCanaryTestProps(**canary_test_props)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__fa32274a3568fa84c18fd791770b5897b827a856ccdabe92b6ea778dc52a7894)
            check_type(argname="argument critical", value=critical, expected_type=type_hints["critical"])
            check_type(argname="argument http_methods", value=http_methods, expected_type=type_hints["http_methods"])
            check_type(argname="argument operation_name", value=operation_name, expected_type=type_hints["operation_name"])
            check_type(argname="argument path", value=path, expected_type=type_hints["path"])
            check_type(argname="argument server_side_availability_metric_details", value=server_side_availability_metric_details, expected_type=type_hints["server_side_availability_metric_details"])
            check_type(argname="argument server_side_latency_metric_details", value=server_side_latency_metric_details, expected_type=type_hints["server_side_latency_metric_details"])
            check_type(argname="argument service", value=service, expected_type=type_hints["service"])
            check_type(argname="argument canary_metric_details", value=canary_metric_details, expected_type=type_hints["canary_metric_details"])
            check_type(argname="argument canary_test_availability_metrics_override", value=canary_test_availability_metrics_override, expected_type=type_hints["canary_test_availability_metrics_override"])
            check_type(argname="argument canary_test_latency_metrics_override", value=canary_test_latency_metrics_override, expected_type=type_hints["canary_test_latency_metrics_override"])
            check_type(argname="argument canary_test_props", value=canary_test_props, expected_type=type_hints["canary_test_props"])
            check_type(argname="argument opt_out_of_service_created_canary", value=opt_out_of_service_created_canary, expected_type=type_hints["opt_out_of_service_created_canary"])
            check_type(argname="argument server_side_contributor_insight_rule_details", value=server_side_contributor_insight_rule_details, expected_type=type_hints["server_side_contributor_insight_rule_details"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "critical": critical,
            "http_methods": http_methods,
            "operation_name": operation_name,
            "path": path,
            "server_side_availability_metric_details": server_side_availability_metric_details,
            "server_side_latency_metric_details": server_side_latency_metric_details,
            "service": service,
        }
        if canary_metric_details is not None:
            self._values["canary_metric_details"] = canary_metric_details
        if canary_test_availability_metrics_override is not None:
            self._values["canary_test_availability_metrics_override"] = canary_test_availability_metrics_override
        if canary_test_latency_metrics_override is not None:
            self._values["canary_test_latency_metrics_override"] = canary_test_latency_metrics_override
        if canary_test_props is not None:
            self._values["canary_test_props"] = canary_test_props
        if opt_out_of_service_created_canary is not None:
            self._values["opt_out_of_service_created_canary"] = opt_out_of_service_created_canary
        if server_side_contributor_insight_rule_details is not None:
            self._values["server_side_contributor_insight_rule_details"] = server_side_contributor_insight_rule_details

    @builtins.property
    def critical(self) -> builtins.bool:
        '''(experimental) Indicates this is a critical operation for the service and will be included in service level metrics and dashboards.

        :stability: experimental
        '''
        result = self._values.get("critical")
        assert result is not None, "Required property 'critical' is missing"
        return typing.cast(builtins.bool, result)

    @builtins.property
    def http_methods(self) -> typing.List[builtins.str]:
        '''(experimental) The http methods supported by the operation.

        :stability: experimental
        '''
        result = self._values.get("http_methods")
        assert result is not None, "Required property 'http_methods' is missing"
        return typing.cast(typing.List[builtins.str], result)

    @builtins.property
    def operation_name(self) -> builtins.str:
        '''(experimental) The name of the operation.

        :stability: experimental
        '''
        result = self._values.get("operation_name")
        assert result is not None, "Required property 'operation_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def path(self) -> builtins.str:
        '''(experimental) The HTTP path for the operation for canaries to run against, something like "/products/list".

        :stability: experimental
        '''
        result = self._values.get("path")
        assert result is not None, "Required property 'path' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def server_side_availability_metric_details(
        self,
    ) -> "IOperationAvailabilityMetricDetails":
        '''(experimental) The server side availability metric details.

        :stability: experimental
        '''
        result = self._values.get("server_side_availability_metric_details")
        assert result is not None, "Required property 'server_side_availability_metric_details' is missing"
        return typing.cast("IOperationAvailabilityMetricDetails", result)

    @builtins.property
    def server_side_latency_metric_details(self) -> "IOperationLatencyMetricDetails":
        '''(experimental) The server side latency metric details.

        :stability: experimental
        '''
        result = self._values.get("server_side_latency_metric_details")
        assert result is not None, "Required property 'server_side_latency_metric_details' is missing"
        return typing.cast("IOperationLatencyMetricDetails", result)

    @builtins.property
    def service(self) -> IService:
        '''(experimental) The service the operation is associated with.

        :stability: experimental
        '''
        result = self._values.get("service")
        assert result is not None, "Required property 'service' is missing"
        return typing.cast(IService, result)

    @builtins.property
    def canary_metric_details(self) -> typing.Optional[ICanaryMetrics]:
        '''(experimental) Optional metric details if the service has a canary.

        :default:

        - No alarms, rules, or dashboards will be created
        from canary metrics

        :stability: experimental
        '''
        result = self._values.get("canary_metric_details")
        return typing.cast(typing.Optional[ICanaryMetrics], result)

    @builtins.property
    def canary_test_availability_metrics_override(
        self,
    ) -> typing.Optional[ICanaryTestMetricsOverride]:
        '''(experimental) The override values for automatically created canary tests so you can use values other than the service defaults to define the thresholds for availability.

        :default:

        - No availability metric details will be overridden and the
        service defaults will be used for the automatically created canaries

        :stability: experimental
        '''
        result = self._values.get("canary_test_availability_metrics_override")
        return typing.cast(typing.Optional[ICanaryTestMetricsOverride], result)

    @builtins.property
    def canary_test_latency_metrics_override(
        self,
    ) -> typing.Optional[ICanaryTestMetricsOverride]:
        '''(experimental) The override values for automatically created canary tests so you can use values other than the service defaults to define the thresholds for latency.

        :default:

        - No latency metric details will be overridden and the
        service defaults will be used for the automatically created canaries

        :stability: experimental
        '''
        result = self._values.get("canary_test_latency_metrics_override")
        return typing.cast(typing.Optional[ICanaryTestMetricsOverride], result)

    @builtins.property
    def canary_test_props(self) -> typing.Optional[AddCanaryTestProps]:
        '''(experimental) If you define this property, a synthetic canary will be provisioned to test the operation.

        :default:

        - The default for the service will be used, if that
        is undefined, then no canary will be provisioned for this operation.

        :stability: experimental
        '''
        result = self._values.get("canary_test_props")
        return typing.cast(typing.Optional[AddCanaryTestProps], result)

    @builtins.property
    def opt_out_of_service_created_canary(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Set to true if you have defined CanaryTestProps for your service, which applies to all operations, but you want to opt out of creating the canary test for this operation.

        :default: - The operation is not opted out

        :stability: experimental
        '''
        result = self._values.get("opt_out_of_service_created_canary")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def server_side_contributor_insight_rule_details(
        self,
    ) -> typing.Optional[IContributorInsightRuleDetails]:
        '''(experimental) The server side details for contributor insights rules.

        :default:

        - The default service contributor insight rule
        details will be used. If those are not defined no Contributor Insight
        rules will be created and the number of instances contributing to AZ
        faults or high latency will not be considered, so a single bad instance
        could make the AZ appear to look impaired.

        :stability: experimental
        '''
        result = self._values.get("server_side_contributor_insight_rule_details")
        return typing.cast(typing.Optional[IContributorInsightRuleDetails], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "OperationProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.enum(jsii_type="@cdklabs/multi-az-observability.OutlierDetectionAlgorithm")
class OutlierDetectionAlgorithm(enum.Enum):
    '''(experimental) Available algorithms for performing outlier detection.

    :stability: experimental
    '''

    STATIC = "STATIC"
    '''(experimental) Defines using a static value to compare skew in faults or high latency responses.

    A good default threshold for this is .7 meaning one AZ
    is responsible for 70% of the total errors or high latency responses

    :stability: experimental
    '''
    CHI_SQUARED = "CHI_SQUARED"
    '''(experimental) Uses the chi squared statistic to determine if there is a statistically significant skew in fault rate or high latency distribution.

    A normal default threshold for this is 0.05, which means there is a 5% or
    less chance of the skew in errors or high latency responses occuring

    :stability: experimental
    '''
    Z_SCORE = "Z_SCORE"
    '''(experimental) Uses z-score to determine if the skew in faults or high latency respones exceeds a defined number of standard devations.

    A good default threshold value for this is 2, meaning the outlier value is outside
    95% of the normal distribution. Using 3 means the outlier is outside 99.7% of
    the normal distribution.

    :stability: experimental
    '''
    IQR = "IQR"
    '''(experimental) Uses Interquartile Range Method to determine an outlier for faults or latency.

    No threshold is required for this method and will be ignored

    :stability: experimental
    '''
    MAD = "MAD"
    '''(experimental) Median Absolute Deviation (MAD) to determine an outlier for faults or latency.

    A common default value threshold 3

    :stability: experimental
    '''


@jsii.enum(jsii_type="@cdklabs/multi-az-observability.PacketLossOutlierAlgorithm")
class PacketLossOutlierAlgorithm(enum.Enum):
    '''(experimental) The options for calculating if a NAT Gateway is an outlier for packet loss.

    :stability: experimental
    '''

    STATIC = "STATIC"
    '''(experimental) This will take the availability threshold and calculate if one AZ is responsible for that percentage of packet loss.

    :stability: experimental
    '''


@jsii.implements(IService)
class Service(
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdklabs/multi-az-observability.Service",
):
    '''(experimental) The representation of a service composed of multiple operations.

    :stability: experimental
    '''

    def __init__(
        self,
        *,
        availability_zone_names: typing.Sequence[builtins.str],
        base_url: builtins.str,
        default_availability_metric_details: "IServiceAvailabilityMetricDetails",
        default_latency_metric_details: "IServiceLatencyMetricDetails",
        fault_count_threshold: jsii.Number,
        period: _aws_cdk_ceddda9d.Duration,
        service_name: builtins.str,
        canary_test_props: typing.Optional[typing.Union[AddCanaryTestProps, typing.Dict[builtins.str, typing.Any]]] = None,
        default_contributor_insight_rule_details: typing.Optional[IContributorInsightRuleDetails] = None,
        load_balancer: typing.Optional[_aws_cdk_aws_elasticloadbalancingv2_ceddda9d.ILoadBalancerV2] = None,
        minimum_unhealthy_targets: typing.Optional[typing.Union[MinimumUnhealthyTargets, typing.Dict[builtins.str, typing.Any]]] = None,
        target_groups: typing.Optional[typing.Sequence[_aws_cdk_aws_elasticloadbalancingv2_ceddda9d.ITargetGroup]] = None,
    ) -> None:
        '''
        :param availability_zone_names: (experimental) A list of the Availability Zone names used by this application.
        :param base_url: (experimental) The base endpoint for this service, like "https://www.example.com". Operation paths will be appended to this endpoint for canary testing the service.
        :param default_availability_metric_details: (experimental) The default settings that are used for availability metrics for all operations unless specifically overridden in an operation definition.
        :param default_latency_metric_details: (experimental) The default settings that are used for availability metrics for all operations unless specifically overridden in an operation definition.
        :param fault_count_threshold: (experimental) The fault count threshold that indicates the service is unhealthy. This is an absolute value of faults being produced by all critical operations in aggregate.
        :param period: (experimental) The period for which metrics for the service should be aggregated.
        :param service_name: (experimental) The name of your service.
        :param canary_test_props: (experimental) Define these settings if you want to automatically add canary tests to your operations. Operations can individually opt out of canary test creation if you define this setting. Default: - Automatic canary tests will not be created for operations in this service.
        :param default_contributor_insight_rule_details: (experimental) The default settings that are used for contributor insight rules. Default: - No defaults are provided and must be specified per operation if the operation has logs that can be queried by contributor insights
        :param load_balancer: (experimental) The load balancer this service sits behind. Default: - Load balancer metrics won't be shown on dashboards and its ARN won't be included in top level alarm descriptions that automation can use to implement a zonal shift.
        :param minimum_unhealthy_targets: (experimental) The minimum number of unhealthy targets for an AZ to be considered unhealthy. Default: Count of 2
        :param target_groups: (experimental) The target groups registered with the load balancer. Default: Anomalous and mitigated host metrics will not be included on dashboards

        :stability: experimental
        '''
        props = ServiceProps(
            availability_zone_names=availability_zone_names,
            base_url=base_url,
            default_availability_metric_details=default_availability_metric_details,
            default_latency_metric_details=default_latency_metric_details,
            fault_count_threshold=fault_count_threshold,
            period=period,
            service_name=service_name,
            canary_test_props=canary_test_props,
            default_contributor_insight_rule_details=default_contributor_insight_rule_details,
            load_balancer=load_balancer,
            minimum_unhealthy_targets=minimum_unhealthy_targets,
            target_groups=target_groups,
        )

        jsii.create(self.__class__, self, [props])

    @jsii.member(jsii_name="addOperation")
    def add_operation(self, operation: IOperation) -> None:
        '''(experimental) Adds an operation to this service and sets the operation's service property.

        :param operation: -

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__86ab5febd81bff1f2ae714b61e47a7bc785fb9d9a10d745f05674ab2153b5d3a)
            check_type(argname="argument operation", value=operation, expected_type=type_hints["operation"])
        return typing.cast(None, jsii.invoke(self, "addOperation", [operation]))

    @builtins.property
    @jsii.member(jsii_name="availabilityZoneNames")
    def availability_zone_names(self) -> typing.List[builtins.str]:
        '''(experimental) A list of the Availability Zone names used by this application.

        :stability: experimental
        '''
        return typing.cast(typing.List[builtins.str], jsii.get(self, "availabilityZoneNames"))

    @builtins.property
    @jsii.member(jsii_name="baseUrl")
    def base_url(self) -> builtins.str:
        '''(experimental) The base endpoint for this service, like "https://www.example.com". Operation paths will be appended to this endpoint for canary testing the service.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "baseUrl"))

    @builtins.property
    @jsii.member(jsii_name="defaultAvailabilityMetricDetails")
    def default_availability_metric_details(
        self,
    ) -> "IServiceAvailabilityMetricDetails":
        '''(experimental) The default settings that are used for availability metrics for all operations unless specifically overridden in an operation definition.

        :stability: experimental
        '''
        return typing.cast("IServiceAvailabilityMetricDetails", jsii.get(self, "defaultAvailabilityMetricDetails"))

    @builtins.property
    @jsii.member(jsii_name="defaultLatencyMetricDetails")
    def default_latency_metric_details(self) -> "IServiceLatencyMetricDetails":
        '''(experimental) The default settings that are used for availability metrics for all operations unless specifically overridden in an operation definition.

        :stability: experimental
        '''
        return typing.cast("IServiceLatencyMetricDetails", jsii.get(self, "defaultLatencyMetricDetails"))

    @builtins.property
    @jsii.member(jsii_name="faultCountThreshold")
    def fault_count_threshold(self) -> jsii.Number:
        '''(experimental) The fault count threshold that indicates the service is unhealthy.

        This is an absolute value of faults
        being produced by all critical operations in aggregate.

        :stability: experimental
        '''
        return typing.cast(jsii.Number, jsii.get(self, "faultCountThreshold"))

    @builtins.property
    @jsii.member(jsii_name="operations")
    def operations(self) -> typing.List[IOperation]:
        '''(experimental) The operations that are part of this service.

        :stability: experimental
        '''
        return typing.cast(typing.List[IOperation], jsii.get(self, "operations"))

    @builtins.property
    @jsii.member(jsii_name="period")
    def period(self) -> _aws_cdk_ceddda9d.Duration:
        '''(experimental) The period for which metrics for the service should be aggregated.

        :stability: experimental
        '''
        return typing.cast(_aws_cdk_ceddda9d.Duration, jsii.get(self, "period"))

    @builtins.property
    @jsii.member(jsii_name="serviceName")
    def service_name(self) -> builtins.str:
        '''(experimental) The name of your service.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "serviceName"))

    @builtins.property
    @jsii.member(jsii_name="canaryTestProps")
    def canary_test_props(self) -> typing.Optional[AddCanaryTestProps]:
        '''(experimental) Define these settings if you want to automatically add canary tests to your operations.

        Operations can individually opt out
        of canary test creation if you define this setting.

        :default:

        - Automatic canary tests will not be created for
        operations in this service.

        :stability: experimental
        '''
        return typing.cast(typing.Optional[AddCanaryTestProps], jsii.get(self, "canaryTestProps"))

    @builtins.property
    @jsii.member(jsii_name="defaultContributorInsightRuleDetails")
    def default_contributor_insight_rule_details(
        self,
    ) -> typing.Optional[IContributorInsightRuleDetails]:
        '''(experimental) The default settings that are used for contributor insight rules.

        :default: - No defaults are provided and must be specified per operation

        :stability: experimental
        '''
        return typing.cast(typing.Optional[IContributorInsightRuleDetails], jsii.get(self, "defaultContributorInsightRuleDetails"))

    @builtins.property
    @jsii.member(jsii_name="loadBalancer")
    def load_balancer(
        self,
    ) -> typing.Optional[_aws_cdk_aws_elasticloadbalancingv2_ceddda9d.ILoadBalancerV2]:
        '''(experimental) The load balancer this service sits behind.

        :default:

        - No load balancer metrics will be included in
        dashboards and its ARN will not be added to top level AZ
        alarm descriptions.

        :stability: experimental
        '''
        return typing.cast(typing.Optional[_aws_cdk_aws_elasticloadbalancingv2_ceddda9d.ILoadBalancerV2], jsii.get(self, "loadBalancer"))

    @builtins.property
    @jsii.member(jsii_name="minimumUnhealthyTargets")
    def minimum_unhealthy_targets(self) -> typing.Optional[MinimumUnhealthyTargets]:
        '''(experimental) The minimum number of unhealthy targets to consider an AZ impaired.

        :default: Count of 2

        :stability: experimental
        '''
        return typing.cast(typing.Optional[MinimumUnhealthyTargets], jsii.get(self, "minimumUnhealthyTargets"))

    @builtins.property
    @jsii.member(jsii_name="targetGroups")
    def target_groups(
        self,
    ) -> typing.Optional[typing.List[_aws_cdk_aws_elasticloadbalancingv2_ceddda9d.ITargetGroup]]:
        '''(experimental) The target groups registered with the load balancer.

        :default: Anomalous and mitigated host metrics will not be included on dashboards

        :stability: experimental
        '''
        return typing.cast(typing.Optional[typing.List[_aws_cdk_aws_elasticloadbalancingv2_ceddda9d.ITargetGroup]], jsii.get(self, "targetGroups"))


@jsii.implements(IServiceMetricDetails)
class ServiceMetricDetails(
    metaclass=jsii.JSIIAbstractClass,
    jsii_type="@cdklabs/multi-az-observability.ServiceMetricDetails",
):
    '''(experimental) Default metric details for a service.

    :stability: experimental
    '''

    def __init__(
        self,
        *,
        alarm_statistic: builtins.str,
        datapoints_to_alarm: jsii.Number,
        evaluation_periods: jsii.Number,
        fault_metric_names: typing.Sequence[builtins.str],
        metric_namespace: builtins.str,
        period: _aws_cdk_ceddda9d.Duration,
        success_metric_names: typing.Sequence[builtins.str],
        unit: _aws_cdk_aws_cloudwatch_ceddda9d.Unit,
        graphed_fault_statistics: typing.Optional[typing.Sequence[builtins.str]] = None,
        graphed_success_statistics: typing.Optional[typing.Sequence[builtins.str]] = None,
    ) -> None:
        '''
        :param alarm_statistic: (experimental) The statistic used for alarms, for availability metrics this should be "Sum", for latency metrics it could something like "p99" or "p99.9".
        :param datapoints_to_alarm: (experimental) The number of datapoints to alarm on for latency and availability alarms.
        :param evaluation_periods: (experimental) The number of evaluation periods for latency and availabiltiy alarms.
        :param fault_metric_names: (experimental) The names of fault indicating metrics.
        :param metric_namespace: (experimental) The CloudWatch metric namespace for these metrics.
        :param period: (experimental) The period for the metrics.
        :param success_metric_names: (experimental) The names of success indicating metrics.
        :param unit: (experimental) The unit used for these metrics.
        :param graphed_fault_statistics: (experimental) The statistics for faults you want to appear on dashboards, for example, with latency metrics, you might want p50, p99, and tm99. For availability metrics this will typically just be "Sum". Default: - For availability metrics, this will be "Sum", for latency metrics it will be just "p99"
        :param graphed_success_statistics: (experimental) The statistics for successes you want to appear on dashboards, for example, with latency metrics, you might want p50, p99, and tm99. For availability metrics this will typically just be "Sum". Default: - For availability metrics, this will be "Sum", for latency metrics it will be just "p99"

        :stability: experimental
        '''
        props = ServiceMetricDetailsProps(
            alarm_statistic=alarm_statistic,
            datapoints_to_alarm=datapoints_to_alarm,
            evaluation_periods=evaluation_periods,
            fault_metric_names=fault_metric_names,
            metric_namespace=metric_namespace,
            period=period,
            success_metric_names=success_metric_names,
            unit=unit,
            graphed_fault_statistics=graphed_fault_statistics,
            graphed_success_statistics=graphed_success_statistics,
        )

        jsii.create(self.__class__, self, [props])

    @builtins.property
    @jsii.member(jsii_name="alarmStatistic")
    def alarm_statistic(self) -> builtins.str:
        '''(experimental) The statistic used for alarms, for availability metrics this should be "Sum", for latency metrics it could something like "p99" or "p99.9".

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "alarmStatistic"))

    @builtins.property
    @jsii.member(jsii_name="datapointsToAlarm")
    def datapoints_to_alarm(self) -> jsii.Number:
        '''(experimental) The number of datapoints to alarm on for latency and availability alarms.

        :stability: experimental
        '''
        return typing.cast(jsii.Number, jsii.get(self, "datapointsToAlarm"))

    @builtins.property
    @jsii.member(jsii_name="evaluationPeriods")
    def evaluation_periods(self) -> jsii.Number:
        '''(experimental) The number of evaluation periods for latency and availabiltiy alarms.

        :stability: experimental
        '''
        return typing.cast(jsii.Number, jsii.get(self, "evaluationPeriods"))

    @builtins.property
    @jsii.member(jsii_name="faultMetricNames")
    def fault_metric_names(self) -> typing.List[builtins.str]:
        '''(experimental) The names of fault indicating metrics.

        :stability: experimental
        '''
        return typing.cast(typing.List[builtins.str], jsii.get(self, "faultMetricNames"))

    @builtins.property
    @jsii.member(jsii_name="metricNamespace")
    def metric_namespace(self) -> builtins.str:
        '''(experimental) The CloudWatch metric namespace for these metrics.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "metricNamespace"))

    @builtins.property
    @jsii.member(jsii_name="period")
    def period(self) -> _aws_cdk_ceddda9d.Duration:
        '''(experimental) The period for the metrics.

        :stability: experimental
        '''
        return typing.cast(_aws_cdk_ceddda9d.Duration, jsii.get(self, "period"))

    @builtins.property
    @jsii.member(jsii_name="successMetricNames")
    def success_metric_names(self) -> typing.List[builtins.str]:
        '''(experimental) The names of success indicating metrics.

        :stability: experimental
        '''
        return typing.cast(typing.List[builtins.str], jsii.get(self, "successMetricNames"))

    @builtins.property
    @jsii.member(jsii_name="unit")
    def unit(self) -> _aws_cdk_aws_cloudwatch_ceddda9d.Unit:
        '''(experimental) The unit used for these metrics.

        :stability: experimental
        '''
        return typing.cast(_aws_cdk_aws_cloudwatch_ceddda9d.Unit, jsii.get(self, "unit"))

    @builtins.property
    @jsii.member(jsii_name="graphedFaultStatistics")
    def graphed_fault_statistics(self) -> typing.Optional[typing.List[builtins.str]]:
        '''(experimental) The statistics for faults you want to appear on dashboards, for example, with latency metrics, you might want p50, p99, and tm99.

        For availability
        metrics this will typically just be "Sum".

        :default: - For availability metrics, this will be "Sum", for latency metrics it will be just "p99"

        :stability: experimental
        '''
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "graphedFaultStatistics"))

    @builtins.property
    @jsii.member(jsii_name="graphedSuccessStatistics")
    def graphed_success_statistics(self) -> typing.Optional[typing.List[builtins.str]]:
        '''(experimental) The statistics for successes you want to appear on dashboards, for example, with latency metrics, you might want p50, p99, and tm99.

        For availability
        metrics this will typically just be "Sum".

        :default: - For availability metrics, this will be "Sum", for latency metrics it will be just "p99"

        :stability: experimental
        '''
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "graphedSuccessStatistics"))


class _ServiceMetricDetailsProxy(ServiceMetricDetails):
    pass

# Adding a "__jsii_proxy_class__(): typing.Type" function to the abstract class
typing.cast(typing.Any, ServiceMetricDetails).__jsii_proxy_class__ = lambda : _ServiceMetricDetailsProxy


@jsii.data_type(
    jsii_type="@cdklabs/multi-az-observability.ServiceMetricDetailsProps",
    jsii_struct_bases=[],
    name_mapping={
        "alarm_statistic": "alarmStatistic",
        "datapoints_to_alarm": "datapointsToAlarm",
        "evaluation_periods": "evaluationPeriods",
        "fault_metric_names": "faultMetricNames",
        "metric_namespace": "metricNamespace",
        "period": "period",
        "success_metric_names": "successMetricNames",
        "unit": "unit",
        "graphed_fault_statistics": "graphedFaultStatistics",
        "graphed_success_statistics": "graphedSuccessStatistics",
    },
)
class ServiceMetricDetailsProps:
    def __init__(
        self,
        *,
        alarm_statistic: builtins.str,
        datapoints_to_alarm: jsii.Number,
        evaluation_periods: jsii.Number,
        fault_metric_names: typing.Sequence[builtins.str],
        metric_namespace: builtins.str,
        period: _aws_cdk_ceddda9d.Duration,
        success_metric_names: typing.Sequence[builtins.str],
        unit: _aws_cdk_aws_cloudwatch_ceddda9d.Unit,
        graphed_fault_statistics: typing.Optional[typing.Sequence[builtins.str]] = None,
        graphed_success_statistics: typing.Optional[typing.Sequence[builtins.str]] = None,
    ) -> None:
        '''(experimental) The properties for default service metric details.

        :param alarm_statistic: (experimental) The statistic used for alarms, for availability metrics this should be "Sum", for latency metrics it could something like "p99" or "p99.9".
        :param datapoints_to_alarm: (experimental) The number of datapoints to alarm on for latency and availability alarms.
        :param evaluation_periods: (experimental) The number of evaluation periods for latency and availabiltiy alarms.
        :param fault_metric_names: (experimental) The names of fault indicating metrics.
        :param metric_namespace: (experimental) The CloudWatch metric namespace for these metrics.
        :param period: (experimental) The period for the metrics.
        :param success_metric_names: (experimental) The names of success indicating metrics.
        :param unit: (experimental) The unit used for these metrics.
        :param graphed_fault_statistics: (experimental) The statistics for faults you want to appear on dashboards, for example, with latency metrics, you might want p50, p99, and tm99. For availability metrics this will typically just be "Sum". Default: - For availability metrics, this will be "Sum", for latency metrics it will be just "p99"
        :param graphed_success_statistics: (experimental) The statistics for successes you want to appear on dashboards, for example, with latency metrics, you might want p50, p99, and tm99. For availability metrics this will typically just be "Sum". Default: - For availability metrics, this will be "Sum", for latency metrics it will be just "p99"

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__071b784429d2d3b09d3261502831f299d64879994d3c59a0c43c2ba33adae288)
            check_type(argname="argument alarm_statistic", value=alarm_statistic, expected_type=type_hints["alarm_statistic"])
            check_type(argname="argument datapoints_to_alarm", value=datapoints_to_alarm, expected_type=type_hints["datapoints_to_alarm"])
            check_type(argname="argument evaluation_periods", value=evaluation_periods, expected_type=type_hints["evaluation_periods"])
            check_type(argname="argument fault_metric_names", value=fault_metric_names, expected_type=type_hints["fault_metric_names"])
            check_type(argname="argument metric_namespace", value=metric_namespace, expected_type=type_hints["metric_namespace"])
            check_type(argname="argument period", value=period, expected_type=type_hints["period"])
            check_type(argname="argument success_metric_names", value=success_metric_names, expected_type=type_hints["success_metric_names"])
            check_type(argname="argument unit", value=unit, expected_type=type_hints["unit"])
            check_type(argname="argument graphed_fault_statistics", value=graphed_fault_statistics, expected_type=type_hints["graphed_fault_statistics"])
            check_type(argname="argument graphed_success_statistics", value=graphed_success_statistics, expected_type=type_hints["graphed_success_statistics"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "alarm_statistic": alarm_statistic,
            "datapoints_to_alarm": datapoints_to_alarm,
            "evaluation_periods": evaluation_periods,
            "fault_metric_names": fault_metric_names,
            "metric_namespace": metric_namespace,
            "period": period,
            "success_metric_names": success_metric_names,
            "unit": unit,
        }
        if graphed_fault_statistics is not None:
            self._values["graphed_fault_statistics"] = graphed_fault_statistics
        if graphed_success_statistics is not None:
            self._values["graphed_success_statistics"] = graphed_success_statistics

    @builtins.property
    def alarm_statistic(self) -> builtins.str:
        '''(experimental) The statistic used for alarms, for availability metrics this should be "Sum", for latency metrics it could something like "p99" or "p99.9".

        :stability: experimental
        '''
        result = self._values.get("alarm_statistic")
        assert result is not None, "Required property 'alarm_statistic' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def datapoints_to_alarm(self) -> jsii.Number:
        '''(experimental) The number of datapoints to alarm on for latency and availability alarms.

        :stability: experimental
        '''
        result = self._values.get("datapoints_to_alarm")
        assert result is not None, "Required property 'datapoints_to_alarm' is missing"
        return typing.cast(jsii.Number, result)

    @builtins.property
    def evaluation_periods(self) -> jsii.Number:
        '''(experimental) The number of evaluation periods for latency and availabiltiy alarms.

        :stability: experimental
        '''
        result = self._values.get("evaluation_periods")
        assert result is not None, "Required property 'evaluation_periods' is missing"
        return typing.cast(jsii.Number, result)

    @builtins.property
    def fault_metric_names(self) -> typing.List[builtins.str]:
        '''(experimental) The names of fault indicating metrics.

        :stability: experimental
        '''
        result = self._values.get("fault_metric_names")
        assert result is not None, "Required property 'fault_metric_names' is missing"
        return typing.cast(typing.List[builtins.str], result)

    @builtins.property
    def metric_namespace(self) -> builtins.str:
        '''(experimental) The CloudWatch metric namespace for these metrics.

        :stability: experimental
        '''
        result = self._values.get("metric_namespace")
        assert result is not None, "Required property 'metric_namespace' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def period(self) -> _aws_cdk_ceddda9d.Duration:
        '''(experimental) The period for the metrics.

        :stability: experimental
        '''
        result = self._values.get("period")
        assert result is not None, "Required property 'period' is missing"
        return typing.cast(_aws_cdk_ceddda9d.Duration, result)

    @builtins.property
    def success_metric_names(self) -> typing.List[builtins.str]:
        '''(experimental) The names of success indicating metrics.

        :stability: experimental
        '''
        result = self._values.get("success_metric_names")
        assert result is not None, "Required property 'success_metric_names' is missing"
        return typing.cast(typing.List[builtins.str], result)

    @builtins.property
    def unit(self) -> _aws_cdk_aws_cloudwatch_ceddda9d.Unit:
        '''(experimental) The unit used for these metrics.

        :stability: experimental
        '''
        result = self._values.get("unit")
        assert result is not None, "Required property 'unit' is missing"
        return typing.cast(_aws_cdk_aws_cloudwatch_ceddda9d.Unit, result)

    @builtins.property
    def graphed_fault_statistics(self) -> typing.Optional[typing.List[builtins.str]]:
        '''(experimental) The statistics for faults you want to appear on dashboards, for example, with latency metrics, you might want p50, p99, and tm99.

        For availability
        metrics this will typically just be "Sum".

        :default: - For availability metrics, this will be "Sum", for latency metrics it will be just "p99"

        :stability: experimental
        '''
        result = self._values.get("graphed_fault_statistics")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def graphed_success_statistics(self) -> typing.Optional[typing.List[builtins.str]]:
        '''(experimental) The statistics for successes you want to appear on dashboards, for example, with latency metrics, you might want p50, p99, and tm99.

        For availability
        metrics this will typically just be "Sum".

        :default: - For availability metrics, this will be "Sum", for latency metrics it will be just "p99"

        :stability: experimental
        '''
        result = self._values.get("graphed_success_statistics")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ServiceMetricDetailsProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdklabs/multi-az-observability.ServiceProps",
    jsii_struct_bases=[],
    name_mapping={
        "availability_zone_names": "availabilityZoneNames",
        "base_url": "baseUrl",
        "default_availability_metric_details": "defaultAvailabilityMetricDetails",
        "default_latency_metric_details": "defaultLatencyMetricDetails",
        "fault_count_threshold": "faultCountThreshold",
        "period": "period",
        "service_name": "serviceName",
        "canary_test_props": "canaryTestProps",
        "default_contributor_insight_rule_details": "defaultContributorInsightRuleDetails",
        "load_balancer": "loadBalancer",
        "minimum_unhealthy_targets": "minimumUnhealthyTargets",
        "target_groups": "targetGroups",
    },
)
class ServiceProps:
    def __init__(
        self,
        *,
        availability_zone_names: typing.Sequence[builtins.str],
        base_url: builtins.str,
        default_availability_metric_details: "IServiceAvailabilityMetricDetails",
        default_latency_metric_details: "IServiceLatencyMetricDetails",
        fault_count_threshold: jsii.Number,
        period: _aws_cdk_ceddda9d.Duration,
        service_name: builtins.str,
        canary_test_props: typing.Optional[typing.Union[AddCanaryTestProps, typing.Dict[builtins.str, typing.Any]]] = None,
        default_contributor_insight_rule_details: typing.Optional[IContributorInsightRuleDetails] = None,
        load_balancer: typing.Optional[_aws_cdk_aws_elasticloadbalancingv2_ceddda9d.ILoadBalancerV2] = None,
        minimum_unhealthy_targets: typing.Optional[typing.Union[MinimumUnhealthyTargets, typing.Dict[builtins.str, typing.Any]]] = None,
        target_groups: typing.Optional[typing.Sequence[_aws_cdk_aws_elasticloadbalancingv2_ceddda9d.ITargetGroup]] = None,
    ) -> None:
        '''(experimental) Properties to initialize a service.

        :param availability_zone_names: (experimental) A list of the Availability Zone names used by this application.
        :param base_url: (experimental) The base endpoint for this service, like "https://www.example.com". Operation paths will be appended to this endpoint for canary testing the service.
        :param default_availability_metric_details: (experimental) The default settings that are used for availability metrics for all operations unless specifically overridden in an operation definition.
        :param default_latency_metric_details: (experimental) The default settings that are used for availability metrics for all operations unless specifically overridden in an operation definition.
        :param fault_count_threshold: (experimental) The fault count threshold that indicates the service is unhealthy. This is an absolute value of faults being produced by all critical operations in aggregate.
        :param period: (experimental) The period for which metrics for the service should be aggregated.
        :param service_name: (experimental) The name of your service.
        :param canary_test_props: (experimental) Define these settings if you want to automatically add canary tests to your operations. Operations can individually opt out of canary test creation if you define this setting. Default: - Automatic canary tests will not be created for operations in this service.
        :param default_contributor_insight_rule_details: (experimental) The default settings that are used for contributor insight rules. Default: - No defaults are provided and must be specified per operation if the operation has logs that can be queried by contributor insights
        :param load_balancer: (experimental) The load balancer this service sits behind. Default: - Load balancer metrics won't be shown on dashboards and its ARN won't be included in top level alarm descriptions that automation can use to implement a zonal shift.
        :param minimum_unhealthy_targets: (experimental) The minimum number of unhealthy targets for an AZ to be considered unhealthy. Default: Count of 2
        :param target_groups: (experimental) The target groups registered with the load balancer. Default: Anomalous and mitigated host metrics will not be included on dashboards

        :stability: experimental
        '''
        if isinstance(canary_test_props, dict):
            canary_test_props = AddCanaryTestProps(**canary_test_props)
        if isinstance(minimum_unhealthy_targets, dict):
            minimum_unhealthy_targets = MinimumUnhealthyTargets(**minimum_unhealthy_targets)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__58a30aef490fedfe7ce4413cbf8e0a1aacabbe85251e0c0e292ab462ff466ccf)
            check_type(argname="argument availability_zone_names", value=availability_zone_names, expected_type=type_hints["availability_zone_names"])
            check_type(argname="argument base_url", value=base_url, expected_type=type_hints["base_url"])
            check_type(argname="argument default_availability_metric_details", value=default_availability_metric_details, expected_type=type_hints["default_availability_metric_details"])
            check_type(argname="argument default_latency_metric_details", value=default_latency_metric_details, expected_type=type_hints["default_latency_metric_details"])
            check_type(argname="argument fault_count_threshold", value=fault_count_threshold, expected_type=type_hints["fault_count_threshold"])
            check_type(argname="argument period", value=period, expected_type=type_hints["period"])
            check_type(argname="argument service_name", value=service_name, expected_type=type_hints["service_name"])
            check_type(argname="argument canary_test_props", value=canary_test_props, expected_type=type_hints["canary_test_props"])
            check_type(argname="argument default_contributor_insight_rule_details", value=default_contributor_insight_rule_details, expected_type=type_hints["default_contributor_insight_rule_details"])
            check_type(argname="argument load_balancer", value=load_balancer, expected_type=type_hints["load_balancer"])
            check_type(argname="argument minimum_unhealthy_targets", value=minimum_unhealthy_targets, expected_type=type_hints["minimum_unhealthy_targets"])
            check_type(argname="argument target_groups", value=target_groups, expected_type=type_hints["target_groups"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "availability_zone_names": availability_zone_names,
            "base_url": base_url,
            "default_availability_metric_details": default_availability_metric_details,
            "default_latency_metric_details": default_latency_metric_details,
            "fault_count_threshold": fault_count_threshold,
            "period": period,
            "service_name": service_name,
        }
        if canary_test_props is not None:
            self._values["canary_test_props"] = canary_test_props
        if default_contributor_insight_rule_details is not None:
            self._values["default_contributor_insight_rule_details"] = default_contributor_insight_rule_details
        if load_balancer is not None:
            self._values["load_balancer"] = load_balancer
        if minimum_unhealthy_targets is not None:
            self._values["minimum_unhealthy_targets"] = minimum_unhealthy_targets
        if target_groups is not None:
            self._values["target_groups"] = target_groups

    @builtins.property
    def availability_zone_names(self) -> typing.List[builtins.str]:
        '''(experimental) A list of the Availability Zone names used by this application.

        :stability: experimental
        '''
        result = self._values.get("availability_zone_names")
        assert result is not None, "Required property 'availability_zone_names' is missing"
        return typing.cast(typing.List[builtins.str], result)

    @builtins.property
    def base_url(self) -> builtins.str:
        '''(experimental) The base endpoint for this service, like "https://www.example.com". Operation paths will be appended to this endpoint for canary testing the service.

        :stability: experimental
        '''
        result = self._values.get("base_url")
        assert result is not None, "Required property 'base_url' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def default_availability_metric_details(
        self,
    ) -> "IServiceAvailabilityMetricDetails":
        '''(experimental) The default settings that are used for availability metrics for all operations unless specifically overridden in an operation definition.

        :stability: experimental
        '''
        result = self._values.get("default_availability_metric_details")
        assert result is not None, "Required property 'default_availability_metric_details' is missing"
        return typing.cast("IServiceAvailabilityMetricDetails", result)

    @builtins.property
    def default_latency_metric_details(self) -> "IServiceLatencyMetricDetails":
        '''(experimental) The default settings that are used for availability metrics for all operations unless specifically overridden in an operation definition.

        :stability: experimental
        '''
        result = self._values.get("default_latency_metric_details")
        assert result is not None, "Required property 'default_latency_metric_details' is missing"
        return typing.cast("IServiceLatencyMetricDetails", result)

    @builtins.property
    def fault_count_threshold(self) -> jsii.Number:
        '''(experimental) The fault count threshold that indicates the service is unhealthy.

        This is an absolute value of faults
        being produced by all critical operations in aggregate.

        :stability: experimental
        '''
        result = self._values.get("fault_count_threshold")
        assert result is not None, "Required property 'fault_count_threshold' is missing"
        return typing.cast(jsii.Number, result)

    @builtins.property
    def period(self) -> _aws_cdk_ceddda9d.Duration:
        '''(experimental) The period for which metrics for the service should be aggregated.

        :stability: experimental
        '''
        result = self._values.get("period")
        assert result is not None, "Required property 'period' is missing"
        return typing.cast(_aws_cdk_ceddda9d.Duration, result)

    @builtins.property
    def service_name(self) -> builtins.str:
        '''(experimental) The name of your service.

        :stability: experimental
        '''
        result = self._values.get("service_name")
        assert result is not None, "Required property 'service_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def canary_test_props(self) -> typing.Optional[AddCanaryTestProps]:
        '''(experimental) Define these settings if you want to automatically add canary tests to your operations.

        Operations can individually opt out
        of canary test creation if you define this setting.

        :default:

        - Automatic canary tests will not be created for
        operations in this service.

        :stability: experimental
        '''
        result = self._values.get("canary_test_props")
        return typing.cast(typing.Optional[AddCanaryTestProps], result)

    @builtins.property
    def default_contributor_insight_rule_details(
        self,
    ) -> typing.Optional[IContributorInsightRuleDetails]:
        '''(experimental) The default settings that are used for contributor insight rules.

        :default:

        - No defaults are provided and must be specified per operation
        if the operation has logs that can be queried by contributor insights

        :stability: experimental
        '''
        result = self._values.get("default_contributor_insight_rule_details")
        return typing.cast(typing.Optional[IContributorInsightRuleDetails], result)

    @builtins.property
    def load_balancer(
        self,
    ) -> typing.Optional[_aws_cdk_aws_elasticloadbalancingv2_ceddda9d.ILoadBalancerV2]:
        '''(experimental) The load balancer this service sits behind.

        :default:

        - Load balancer metrics won't be shown on dashboards
        and its ARN won't be included in top level alarm descriptions
        that automation can use to implement a zonal shift.

        :stability: experimental
        '''
        result = self._values.get("load_balancer")
        return typing.cast(typing.Optional[_aws_cdk_aws_elasticloadbalancingv2_ceddda9d.ILoadBalancerV2], result)

    @builtins.property
    def minimum_unhealthy_targets(self) -> typing.Optional[MinimumUnhealthyTargets]:
        '''(experimental) The minimum number of unhealthy targets for an AZ to be considered unhealthy.

        :default: Count of 2

        :stability: experimental
        '''
        result = self._values.get("minimum_unhealthy_targets")
        return typing.cast(typing.Optional[MinimumUnhealthyTargets], result)

    @builtins.property
    def target_groups(
        self,
    ) -> typing.Optional[typing.List[_aws_cdk_aws_elasticloadbalancingv2_ceddda9d.ITargetGroup]]:
        '''(experimental) The target groups registered with the load balancer.

        :default: Anomalous and mitigated host metrics will not be included on dashboards

        :stability: experimental
        '''
        result = self._values.get("target_groups")
        return typing.cast(typing.Optional[typing.List[_aws_cdk_aws_elasticloadbalancingv2_ceddda9d.ITargetGroup]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ServiceProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.implements(IAvailabilityZoneMapper)
class AvailabilityZoneMapper(
    _constructs_77d1e7e8.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdklabs/multi-az-observability.AvailabilityZoneMapper",
):
    '''(experimental) A construct that allows you to map AZ names to ids and back.

    :stability: experimental
    '''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        availability_zone_names: typing.Optional[typing.Sequence[builtins.str]] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param availability_zone_names: (experimental) The currently in use Availability Zone names which constrains the list of AZ IDs that are returned. Default: - No names are provided and the mapper returns all AZs in the region in its lists

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f533f3a490e063cdfef872dde16a1c3bed970e880d7ed597f16c665f83caacba)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = AvailabilityZoneMapperProps(
            availability_zone_names=availability_zone_names
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @jsii.member(jsii_name="allAvailabilityZoneIdsAsArray")
    def all_availability_zone_ids_as_array(self) -> _aws_cdk_ceddda9d.Reference:
        '''(experimental) Returns a reference that can be cast to a string array with all of the Availability Zone Ids.

        :stability: experimental
        '''
        return typing.cast(_aws_cdk_ceddda9d.Reference, jsii.invoke(self, "allAvailabilityZoneIdsAsArray", []))

    @jsii.member(jsii_name="allAvailabilityZoneIdsAsCommaDelimitedList")
    def all_availability_zone_ids_as_comma_delimited_list(self) -> builtins.str:
        '''(experimental) Returns a comma delimited list of Availability Zone Ids for the supplied Availability Zone names.

        You can use this string with Fn.Select(x, Fn.Split(",", azs)) to
        get a specific Availability Zone Id

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.invoke(self, "allAvailabilityZoneIdsAsCommaDelimitedList", []))

    @jsii.member(jsii_name="allAvailabilityZoneNamesAsCommaDelimitedList")
    def all_availability_zone_names_as_comma_delimited_list(self) -> builtins.str:
        '''(experimental) Gets all of the Availability Zone names in this Region as a comma delimited list.

        You can use this string with Fn.Select(x, Fn.Split(",", azs)) to
        get a specific Availability Zone Name

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.invoke(self, "allAvailabilityZoneNamesAsCommaDelimitedList", []))

    @jsii.member(jsii_name="availabilityZoneId")
    def availability_zone_id(
        self,
        availability_zone_name: builtins.str,
    ) -> builtins.str:
        '''(experimental) Gets the Availability Zone Id for the given Availability Zone Name in this account.

        :param availability_zone_name: -

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__013cb7b661a38c5e9e58c44fe2a47e74d9bd5db974b190326cb12941c4203e52)
            check_type(argname="argument availability_zone_name", value=availability_zone_name, expected_type=type_hints["availability_zone_name"])
        return typing.cast(builtins.str, jsii.invoke(self, "availabilityZoneId", [availability_zone_name]))

    @jsii.member(jsii_name="availabilityZoneIdFromAvailabilityZoneLetter")
    def availability_zone_id_from_availability_zone_letter(
        self,
        letter: builtins.str,
    ) -> builtins.str:
        '''(experimental) Given a letter like "f" or "a", returns the Availability Zone Id for that Availability Zone name in this account.

        :param letter: -

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d66625a70b2c57ad713d9f368830723593c9e37af5ce27d5ec0b0d7acd2a499f)
            check_type(argname="argument letter", value=letter, expected_type=type_hints["letter"])
        return typing.cast(builtins.str, jsii.invoke(self, "availabilityZoneIdFromAvailabilityZoneLetter", [letter]))

    @jsii.member(jsii_name="availabilityZoneIdsAsArray")
    def availability_zone_ids_as_array(
        self,
        availability_zone_names: typing.Sequence[builtins.str],
    ) -> typing.List[builtins.str]:
        '''(experimental) Returns an array for Availability Zone Ids for the supplied Availability Zone names, they are returned in the same order the names were provided.

        :param availability_zone_names: -

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__89b736f1d9f4010fb29f411199f74eab2bde27a769908da4ee24ced1683acc97)
            check_type(argname="argument availability_zone_names", value=availability_zone_names, expected_type=type_hints["availability_zone_names"])
        return typing.cast(typing.List[builtins.str], jsii.invoke(self, "availabilityZoneIdsAsArray", [availability_zone_names]))

    @jsii.member(jsii_name="availabilityZoneIdsAsCommaDelimitedList")
    def availability_zone_ids_as_comma_delimited_list(
        self,
        availability_zone_names: typing.Sequence[builtins.str],
    ) -> builtins.str:
        '''(experimental) Returns a comma delimited list of Availability Zone Ids for the supplied Availability Zone names.

        You can use this string with Fn.Select(x, Fn.Split(",", azs)) to
        get a specific Availability Zone Id

        :param availability_zone_names: -

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__df40356aa79474f9245fbe0f5820930e1ac2296860fc7517548f017d885325f1)
            check_type(argname="argument availability_zone_names", value=availability_zone_names, expected_type=type_hints["availability_zone_names"])
        return typing.cast(builtins.str, jsii.invoke(self, "availabilityZoneIdsAsCommaDelimitedList", [availability_zone_names]))

    @jsii.member(jsii_name="availabilityZoneName")
    def availability_zone_name(
        self,
        availability_zone_id: builtins.str,
    ) -> builtins.str:
        '''(experimental) Gets the Availability Zone Name for the given Availability Zone Id in this account.

        :param availability_zone_id: -

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4e121614152110074684b328fd8155e0b55e0fad34a93e31506f46806fc35da1)
            check_type(argname="argument availability_zone_id", value=availability_zone_id, expected_type=type_hints["availability_zone_id"])
        return typing.cast(builtins.str, jsii.invoke(self, "availabilityZoneName", [availability_zone_id]))

    @jsii.member(jsii_name="regionPrefixForAvailabilityZoneIds")
    def region_prefix_for_availability_zone_ids(self) -> builtins.str:
        '''(experimental) Gets the prefix for the region used with Availability Zone Ids, for example in us-east-1, this returns "use1".

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.invoke(self, "regionPrefixForAvailabilityZoneIds", []))

    @builtins.property
    @jsii.member(jsii_name="function")
    def function(self) -> _aws_cdk_aws_lambda_ceddda9d.IFunction:
        '''(experimental) The function that does the mapping.

        :stability: experimental
        '''
        return typing.cast(_aws_cdk_aws_lambda_ceddda9d.IFunction, jsii.get(self, "function"))

    @function.setter
    def function(self, value: _aws_cdk_aws_lambda_ceddda9d.IFunction) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f379431bd49ef8d7d26c145e78b9dcbcd05a5d6a715d2ab10b3184f16bde8e42)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "function", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="logGroup")
    def log_group(self) -> _aws_cdk_aws_logs_ceddda9d.ILogGroup:
        '''(experimental) The log group for the function's logs.

        :stability: experimental
        '''
        return typing.cast(_aws_cdk_aws_logs_ceddda9d.ILogGroup, jsii.get(self, "logGroup"))

    @log_group.setter
    def log_group(self, value: _aws_cdk_aws_logs_ceddda9d.ILogGroup) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__24c3de55c04ae40b7e2a52711618f1b6bdbd534427549ecd64a59d1817539b03)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "logGroup", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="mapper")
    def mapper(self) -> _aws_cdk_ceddda9d.CustomResource:
        '''(experimental) The custom resource that can be referenced to use Fn::GetAtt functions on to retrieve availability zone names and ids.

        :stability: experimental
        '''
        return typing.cast(_aws_cdk_ceddda9d.CustomResource, jsii.get(self, "mapper"))

    @mapper.setter
    def mapper(self, value: _aws_cdk_ceddda9d.CustomResource) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__02620da05be465008d0b0794505b82da4876bfeef27c02bac8dd64882b3af1ff)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "mapper", value) # pyright: ignore[reportArgumentType]


@jsii.implements(IBasicServiceMultiAZObservability)
class BasicServiceMultiAZObservability(
    _constructs_77d1e7e8.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdklabs/multi-az-observability.BasicServiceMultiAZObservability",
):
    '''(experimental) Basic observability for a service using metrics from ALBs and NAT Gateways.

    :stability: experimental
    '''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        datapoints_to_alarm: jsii.Number,
        evaluation_periods: jsii.Number,
        service_name: builtins.str,
        application_load_balancer_props: typing.Optional[typing.Union[ApplicationLoadBalancerDetectionProps, typing.Dict[builtins.str, typing.Any]]] = None,
        assets_bucket_parameter_name: typing.Optional[builtins.str] = None,
        assets_bucket_prefix_parameter_name: typing.Optional[builtins.str] = None,
        create_dashboard: typing.Optional[builtins.bool] = None,
        interval: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
        nat_gateway_props: typing.Optional[typing.Union[NatGatewayDetectionProps, typing.Dict[builtins.str, typing.Any]]] = None,
        period: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param datapoints_to_alarm: (experimental) The number of datapoints to alarm on for latency and availability alarms.
        :param evaluation_periods: (experimental) The number of evaluation periods for latency and availabiltiy alarms.
        :param service_name: (experimental) The service's name.
        :param application_load_balancer_props: (experimental) Properties for ALBs to detect single AZ impact. You must specify this and/or natGatewayProps. Default: "No ALBs will be used to calculate impact."
        :param assets_bucket_parameter_name: (experimental) If you are not using a static bucket to deploy assets, for example you are synthing this and it gets uploaded to a bucket whose name is unknown to you (maybe used as part of a central CI/CD system) and is provided as a parameter to your stack, specify that parameter name here. It will override the bucket location CDK provides by default for bundled assets. The stack containing this contruct needs to have a parameter defined that uses this name. The underlying stacks in this construct that deploy assets will copy the parent stack's value for this property. Default: "The assets will be uploaded to the default defined asset location."
        :param assets_bucket_prefix_parameter_name: (experimental) If you are not using a static bucket to deploy assets, for example you are synthing this and it gets uploaded to a bucket that uses a prefix that is unknown to you (maybe used as part of a central CI/CD system) and is provided as a parameter to your stack, specify that parameter name here. It will override the bucket prefix CDK provides by default for bundled assets. This property only takes effect if you defined the assetsBucketParameterName. The stack containing this contruct needs to have a parameter defined that uses this name. The underlying stacks in this construct that deploy assets will copy the parent stack's value for this property. Default: "No object prefix will be added to your custom assets location. However, if you have overridden something like the 'BucketPrefix' property in your stack synthesizer with a variable like '${AssetsBucketPrefix}', you will need to define this property so it doesn't cause a reference error even if the prefix value is blank."
        :param create_dashboard: (experimental) Whether to create a dashboard displaying the metrics and alarms. Default: false
        :param interval: (experimental) Dashboard interval. Default: Duration.hours(1)
        :param nat_gateway_props: (experimental) Properties for NAT Gateways to detect single AZ impact. You must specify this and/or applicationLoadBalancerProps. Default: "No NAT Gateways will be used to calculate impact."
        :param period: (experimental) The period to evaluate metrics. Default: Duration.minutes(1)

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__91f0b653e00699938976db245f8464d40c1794756876fc19b4ad839855950230)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = BasicServiceMultiAZObservabilityProps(
            datapoints_to_alarm=datapoints_to_alarm,
            evaluation_periods=evaluation_periods,
            service_name=service_name,
            application_load_balancer_props=application_load_balancer_props,
            assets_bucket_parameter_name=assets_bucket_parameter_name,
            assets_bucket_prefix_parameter_name=assets_bucket_prefix_parameter_name,
            create_dashboard=create_dashboard,
            interval=interval,
            nat_gateway_props=nat_gateway_props,
            period=period,
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @builtins.property
    @jsii.member(jsii_name="aggregateZonalIsolatedImpactAlarms")
    def aggregate_zonal_isolated_impact_alarms(
        self,
    ) -> typing.Mapping[builtins.str, _aws_cdk_aws_cloudwatch_ceddda9d.IAlarm]:
        '''(experimental) The alarms indicating if an AZ has isolated impact from either ALB or NAT GW metrics.

        :stability: experimental
        '''
        return typing.cast(typing.Mapping[builtins.str, _aws_cdk_aws_cloudwatch_ceddda9d.IAlarm], jsii.get(self, "aggregateZonalIsolatedImpactAlarms"))

    @aggregate_zonal_isolated_impact_alarms.setter
    def aggregate_zonal_isolated_impact_alarms(
        self,
        value: typing.Mapping[builtins.str, _aws_cdk_aws_cloudwatch_ceddda9d.IAlarm],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a0651d15ed8cdb0e7d4229be009268d3ac4cee784d9665775fe9dbc804061006)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "aggregateZonalIsolatedImpactAlarms", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="serviceName")
    def service_name(self) -> builtins.str:
        '''(experimental) The name of the service.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "serviceName"))

    @service_name.setter
    def service_name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3ec564bcf48b6cda84d0cc41144dba2366731021f9aae2ee9f70c410be101142)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "serviceName", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="albZonalIsolatedImpactAlarms")
    def alb_zonal_isolated_impact_alarms(
        self,
    ) -> typing.Optional[typing.Mapping[builtins.str, _aws_cdk_aws_cloudwatch_ceddda9d.IAlarm]]:
        '''(experimental) The alarms indicating if an AZ is an outlier for ALB faults and has isolated impact.

        :stability: experimental
        '''
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, _aws_cdk_aws_cloudwatch_ceddda9d.IAlarm]], jsii.get(self, "albZonalIsolatedImpactAlarms"))

    @alb_zonal_isolated_impact_alarms.setter
    def alb_zonal_isolated_impact_alarms(
        self,
        value: typing.Optional[typing.Mapping[builtins.str, _aws_cdk_aws_cloudwatch_ceddda9d.IAlarm]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__198f3d5a0022ddac739f5e4a830649083f625017c0892120bd8db43d96eb2ec4)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "albZonalIsolatedImpactAlarms", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="applicationLoadBalancers")
    def application_load_balancers(
        self,
    ) -> typing.Optional[typing.List[_aws_cdk_aws_elasticloadbalancingv2_ceddda9d.IApplicationLoadBalancer]]:
        '''(experimental) The application load balancers being used by the service.

        :stability: experimental
        '''
        return typing.cast(typing.Optional[typing.List[_aws_cdk_aws_elasticloadbalancingv2_ceddda9d.IApplicationLoadBalancer]], jsii.get(self, "applicationLoadBalancers"))

    @application_load_balancers.setter
    def application_load_balancers(
        self,
        value: typing.Optional[typing.List[_aws_cdk_aws_elasticloadbalancingv2_ceddda9d.IApplicationLoadBalancer]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f0269305696627ab6f8671d580a6ffee9c44702b3f76cebabf3f49dac8301227)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "applicationLoadBalancers", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="dashboard")
    def dashboard(self) -> typing.Optional[_aws_cdk_aws_cloudwatch_ceddda9d.Dashboard]:
        '''(experimental) The dashboard that is optionally created.

        :stability: experimental
        '''
        return typing.cast(typing.Optional[_aws_cdk_aws_cloudwatch_ceddda9d.Dashboard], jsii.get(self, "dashboard"))

    @dashboard.setter
    def dashboard(
        self,
        value: typing.Optional[_aws_cdk_aws_cloudwatch_ceddda9d.Dashboard],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d95ca669596eac69b5dcf7e2c14ba72c245e413d581394f643a1d71052218a81)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "dashboard", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="natGateways")
    def nat_gateways(
        self,
    ) -> typing.Optional[typing.Mapping[builtins.str, typing.List[_aws_cdk_aws_ec2_ceddda9d.CfnNatGateway]]]:
        '''(experimental) The NAT Gateways being used in the service, each set of NAT Gateways are keyed by their Availability Zone Id.

        :stability: experimental
        '''
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, typing.List[_aws_cdk_aws_ec2_ceddda9d.CfnNatGateway]]], jsii.get(self, "natGateways"))

    @nat_gateways.setter
    def nat_gateways(
        self,
        value: typing.Optional[typing.Mapping[builtins.str, typing.List[_aws_cdk_aws_ec2_ceddda9d.CfnNatGateway]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a12a9d8eeb0094fca7ab02f796b254b0f2503807dc753010a48c414fd419f8c9)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "natGateways", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="natGWZonalIsolatedImpactAlarms")
    def nat_gw_zonal_isolated_impact_alarms(
        self,
    ) -> typing.Optional[typing.Mapping[builtins.str, _aws_cdk_aws_cloudwatch_ceddda9d.IAlarm]]:
        '''(experimental) The alarms indicating if an AZ is an outlier for NAT GW packet loss and has isolated impact.

        :stability: experimental
        '''
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, _aws_cdk_aws_cloudwatch_ceddda9d.IAlarm]], jsii.get(self, "natGWZonalIsolatedImpactAlarms"))

    @nat_gw_zonal_isolated_impact_alarms.setter
    def nat_gw_zonal_isolated_impact_alarms(
        self,
        value: typing.Optional[typing.Mapping[builtins.str, _aws_cdk_aws_cloudwatch_ceddda9d.IAlarm]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7773e8e939b70c12b72e90bae790068ae53e9f8f988dd695cf81376d5999d8fa)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "natGWZonalIsolatedImpactAlarms", value) # pyright: ignore[reportArgumentType]


@jsii.implements(ICanaryMetrics)
class CanaryMetrics(
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdklabs/multi-az-observability.CanaryMetrics",
):
    '''(experimental) Represents metrics for a canary testing a service.

    :stability: experimental
    '''

    def __init__(
        self,
        *,
        canary_availability_metric_details: "IOperationAvailabilityMetricDetails",
        canary_latency_metric_details: "IOperationLatencyMetricDetails",
    ) -> None:
        '''
        :param canary_availability_metric_details: (experimental) The canary availability metric details.
        :param canary_latency_metric_details: (experimental) The canary latency metric details.

        :stability: experimental
        '''
        props = CanaryMetricProps(
            canary_availability_metric_details=canary_availability_metric_details,
            canary_latency_metric_details=canary_latency_metric_details,
        )

        jsii.create(self.__class__, self, [props])

    @builtins.property
    @jsii.member(jsii_name="canaryAvailabilityMetricDetails")
    def canary_availability_metric_details(
        self,
    ) -> "IOperationAvailabilityMetricDetails":
        '''(experimental) The canary availability metric details.

        :stability: experimental
        '''
        return typing.cast("IOperationAvailabilityMetricDetails", jsii.get(self, "canaryAvailabilityMetricDetails"))

    @builtins.property
    @jsii.member(jsii_name="canaryLatencyMetricDetails")
    def canary_latency_metric_details(self) -> "IOperationLatencyMetricDetails":
        '''(experimental) The canary latency metric details.

        :stability: experimental
        '''
        return typing.cast("IOperationLatencyMetricDetails", jsii.get(self, "canaryLatencyMetricDetails"))


@jsii.data_type(
    jsii_type="@cdklabs/multi-az-observability.CanaryTestAvailabilityMetricsOverrideProps",
    jsii_struct_bases=[CanaryTestMetricsOverrideProps],
    name_mapping={
        "alarm_statistic": "alarmStatistic",
        "datapoints_to_alarm": "datapointsToAlarm",
        "evaluation_periods": "evaluationPeriods",
        "period": "period",
        "fault_alarm_threshold": "faultAlarmThreshold",
        "success_alarm_threshold": "successAlarmThreshold",
    },
)
class CanaryTestAvailabilityMetricsOverrideProps(CanaryTestMetricsOverrideProps):
    def __init__(
        self,
        *,
        alarm_statistic: typing.Optional[builtins.str] = None,
        datapoints_to_alarm: typing.Optional[jsii.Number] = None,
        evaluation_periods: typing.Optional[jsii.Number] = None,
        period: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
        fault_alarm_threshold: typing.Optional[jsii.Number] = None,
        success_alarm_threshold: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''(experimental) Properties for canary metrics in an operation.

        :param alarm_statistic: (experimental) The statistic used for alarms, for availability metrics this should be "Sum", for latency metrics it could something like "p99" or "p99.9". Default: - This property will use the default defined for the service
        :param datapoints_to_alarm: (experimental) The number of datapoints to alarm on for latency and availability alarms. Default: - This property will use the default defined for the service
        :param evaluation_periods: (experimental) The number of evaluation periods for latency and availabiltiy alarms. Default: - This property will use the default defined for the service
        :param period: (experimental) The period for the metrics. Default: - This property will use the default defined for the service
        :param fault_alarm_threshold: (experimental) The threshold for alarms associated with fault metrics, for example if measuring fault rate, the threshold may be 1, meaning you would want an alarm that triggers if the fault rate goes above 1%. Default: - This property will use the default defined for the service
        :param success_alarm_threshold: (experimental) The threshold for alarms associated with success metrics, for example if measuring success rate, the threshold may be 99, meaning you would want an alarm that triggers if success drops below 99%. Default: - This property will use the default defined for the service

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b9b8a9ef35fcd536b16032b7c89ca5b2cca4d9f45968b706c065949eeaf46946)
            check_type(argname="argument alarm_statistic", value=alarm_statistic, expected_type=type_hints["alarm_statistic"])
            check_type(argname="argument datapoints_to_alarm", value=datapoints_to_alarm, expected_type=type_hints["datapoints_to_alarm"])
            check_type(argname="argument evaluation_periods", value=evaluation_periods, expected_type=type_hints["evaluation_periods"])
            check_type(argname="argument period", value=period, expected_type=type_hints["period"])
            check_type(argname="argument fault_alarm_threshold", value=fault_alarm_threshold, expected_type=type_hints["fault_alarm_threshold"])
            check_type(argname="argument success_alarm_threshold", value=success_alarm_threshold, expected_type=type_hints["success_alarm_threshold"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if alarm_statistic is not None:
            self._values["alarm_statistic"] = alarm_statistic
        if datapoints_to_alarm is not None:
            self._values["datapoints_to_alarm"] = datapoints_to_alarm
        if evaluation_periods is not None:
            self._values["evaluation_periods"] = evaluation_periods
        if period is not None:
            self._values["period"] = period
        if fault_alarm_threshold is not None:
            self._values["fault_alarm_threshold"] = fault_alarm_threshold
        if success_alarm_threshold is not None:
            self._values["success_alarm_threshold"] = success_alarm_threshold

    @builtins.property
    def alarm_statistic(self) -> typing.Optional[builtins.str]:
        '''(experimental) The statistic used for alarms, for availability metrics this should be "Sum", for latency metrics it could something like "p99" or "p99.9".

        :default: - This property will use the default defined for the service

        :stability: experimental
        '''
        result = self._values.get("alarm_statistic")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def datapoints_to_alarm(self) -> typing.Optional[jsii.Number]:
        '''(experimental) The number of datapoints to alarm on for latency and availability alarms.

        :default: - This property will use the default defined for the service

        :stability: experimental
        '''
        result = self._values.get("datapoints_to_alarm")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def evaluation_periods(self) -> typing.Optional[jsii.Number]:
        '''(experimental) The number of evaluation periods for latency and availabiltiy alarms.

        :default: - This property will use the default defined for the service

        :stability: experimental
        '''
        result = self._values.get("evaluation_periods")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def period(self) -> typing.Optional[_aws_cdk_ceddda9d.Duration]:
        '''(experimental) The period for the metrics.

        :default: - This property will use the default defined for the service

        :stability: experimental
        '''
        result = self._values.get("period")
        return typing.cast(typing.Optional[_aws_cdk_ceddda9d.Duration], result)

    @builtins.property
    def fault_alarm_threshold(self) -> typing.Optional[jsii.Number]:
        '''(experimental) The threshold for alarms associated with fault metrics, for example if measuring fault rate, the threshold may be 1, meaning you would want an alarm that triggers if the fault rate goes above 1%.

        :default: - This property will use the default defined for the service

        :stability: experimental
        '''
        result = self._values.get("fault_alarm_threshold")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def success_alarm_threshold(self) -> typing.Optional[jsii.Number]:
        '''(experimental) The threshold for alarms associated with success metrics, for example if measuring success rate, the threshold may be 99, meaning you would want an alarm that triggers if success drops below 99%.

        :default: - This property will use the default defined for the service

        :stability: experimental
        '''
        result = self._values.get("success_alarm_threshold")
        return typing.cast(typing.Optional[jsii.Number], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CanaryTestAvailabilityMetricsOverrideProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdklabs/multi-az-observability.CanaryTestLatencyMetricsOverrideProps",
    jsii_struct_bases=[CanaryTestMetricsOverrideProps],
    name_mapping={
        "alarm_statistic": "alarmStatistic",
        "datapoints_to_alarm": "datapointsToAlarm",
        "evaluation_periods": "evaluationPeriods",
        "period": "period",
        "success_alarm_threshold": "successAlarmThreshold",
    },
)
class CanaryTestLatencyMetricsOverrideProps(CanaryTestMetricsOverrideProps):
    def __init__(
        self,
        *,
        alarm_statistic: typing.Optional[builtins.str] = None,
        datapoints_to_alarm: typing.Optional[jsii.Number] = None,
        evaluation_periods: typing.Optional[jsii.Number] = None,
        period: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
        success_alarm_threshold: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
    ) -> None:
        '''(experimental) Properties for canary metrics in an operation.

        :param alarm_statistic: (experimental) The statistic used for alarms, for availability metrics this should be "Sum", for latency metrics it could something like "p99" or "p99.9". Default: - This property will use the default defined for the service
        :param datapoints_to_alarm: (experimental) The number of datapoints to alarm on for latency and availability alarms. Default: - This property will use the default defined for the service
        :param evaluation_periods: (experimental) The number of evaluation periods for latency and availabiltiy alarms. Default: - This property will use the default defined for the service
        :param period: (experimental) The period for the metrics. Default: - This property will use the default defined for the service
        :param success_alarm_threshold: (experimental) The threshold for alarms associated with latency success metrics, for example if success latency exceeds 500 milliseconds. Default: - This property will use the default defined for the service

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9c6b3ad9d94fd146e47feab72d6824e32aa2f19b3ef155d47987ea2f5255fd3a)
            check_type(argname="argument alarm_statistic", value=alarm_statistic, expected_type=type_hints["alarm_statistic"])
            check_type(argname="argument datapoints_to_alarm", value=datapoints_to_alarm, expected_type=type_hints["datapoints_to_alarm"])
            check_type(argname="argument evaluation_periods", value=evaluation_periods, expected_type=type_hints["evaluation_periods"])
            check_type(argname="argument period", value=period, expected_type=type_hints["period"])
            check_type(argname="argument success_alarm_threshold", value=success_alarm_threshold, expected_type=type_hints["success_alarm_threshold"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if alarm_statistic is not None:
            self._values["alarm_statistic"] = alarm_statistic
        if datapoints_to_alarm is not None:
            self._values["datapoints_to_alarm"] = datapoints_to_alarm
        if evaluation_periods is not None:
            self._values["evaluation_periods"] = evaluation_periods
        if period is not None:
            self._values["period"] = period
        if success_alarm_threshold is not None:
            self._values["success_alarm_threshold"] = success_alarm_threshold

    @builtins.property
    def alarm_statistic(self) -> typing.Optional[builtins.str]:
        '''(experimental) The statistic used for alarms, for availability metrics this should be "Sum", for latency metrics it could something like "p99" or "p99.9".

        :default: - This property will use the default defined for the service

        :stability: experimental
        '''
        result = self._values.get("alarm_statistic")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def datapoints_to_alarm(self) -> typing.Optional[jsii.Number]:
        '''(experimental) The number of datapoints to alarm on for latency and availability alarms.

        :default: - This property will use the default defined for the service

        :stability: experimental
        '''
        result = self._values.get("datapoints_to_alarm")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def evaluation_periods(self) -> typing.Optional[jsii.Number]:
        '''(experimental) The number of evaluation periods for latency and availabiltiy alarms.

        :default: - This property will use the default defined for the service

        :stability: experimental
        '''
        result = self._values.get("evaluation_periods")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def period(self) -> typing.Optional[_aws_cdk_ceddda9d.Duration]:
        '''(experimental) The period for the metrics.

        :default: - This property will use the default defined for the service

        :stability: experimental
        '''
        result = self._values.get("period")
        return typing.cast(typing.Optional[_aws_cdk_ceddda9d.Duration], result)

    @builtins.property
    def success_alarm_threshold(self) -> typing.Optional[_aws_cdk_ceddda9d.Duration]:
        '''(experimental) The threshold for alarms associated with latency success metrics, for example if success latency exceeds 500 milliseconds.

        :default: - This property will use the default defined for the service

        :stability: experimental
        '''
        result = self._values.get("success_alarm_threshold")
        return typing.cast(typing.Optional[_aws_cdk_ceddda9d.Duration], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CanaryTestLatencyMetricsOverrideProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.implements(ICanaryTestMetricsOverride)
class CanaryTestMetricsOverride(
    metaclass=jsii.JSIIAbstractClass,
    jsii_type="@cdklabs/multi-az-observability.CanaryTestMetricsOverride",
):
    '''(experimental) Provides overrides for the default metric settings used for the automatically created canary tests.

    :stability: experimental
    '''

    def __init__(
        self,
        *,
        alarm_statistic: typing.Optional[builtins.str] = None,
        datapoints_to_alarm: typing.Optional[jsii.Number] = None,
        evaluation_periods: typing.Optional[jsii.Number] = None,
        period: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
    ) -> None:
        '''
        :param alarm_statistic: (experimental) The statistic used for alarms, for availability metrics this should be "Sum", for latency metrics it could something like "p99" or "p99.9". Default: - This property will use the default defined for the service
        :param datapoints_to_alarm: (experimental) The number of datapoints to alarm on for latency and availability alarms. Default: - This property will use the default defined for the service
        :param evaluation_periods: (experimental) The number of evaluation periods for latency and availabiltiy alarms. Default: - This property will use the default defined for the service
        :param period: (experimental) The period for the metrics. Default: - This property will use the default defined for the service

        :stability: experimental
        '''
        props = CanaryTestMetricsOverrideProps(
            alarm_statistic=alarm_statistic,
            datapoints_to_alarm=datapoints_to_alarm,
            evaluation_periods=evaluation_periods,
            period=period,
        )

        jsii.create(self.__class__, self, [props])

    @builtins.property
    @jsii.member(jsii_name="alarmStatistic")
    def alarm_statistic(self) -> typing.Optional[builtins.str]:
        '''(experimental) The statistic used for alarms, for availability metrics this should be "Sum", for latency metrics it could something like "p99" or "p99.9".

        :stability: experimental
        '''
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "alarmStatistic"))

    @builtins.property
    @jsii.member(jsii_name="datapointsToAlarm")
    def datapoints_to_alarm(self) -> typing.Optional[jsii.Number]:
        '''(experimental) The number of datapoints to alarm on for latency and availability alarms.

        :stability: experimental
        '''
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "datapointsToAlarm"))

    @builtins.property
    @jsii.member(jsii_name="evaluationPeriods")
    def evaluation_periods(self) -> typing.Optional[jsii.Number]:
        '''(experimental) The number of evaluation periods for latency and availabiltiy alarms.

        :stability: experimental
        '''
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "evaluationPeriods"))

    @builtins.property
    @jsii.member(jsii_name="period")
    def period(self) -> typing.Optional[_aws_cdk_ceddda9d.Duration]:
        '''(experimental) The period for the metrics.

        :stability: experimental
        '''
        return typing.cast(typing.Optional[_aws_cdk_ceddda9d.Duration], jsii.get(self, "period"))


class _CanaryTestMetricsOverrideProxy(CanaryTestMetricsOverride):
    pass

# Adding a "__jsii_proxy_class__(): typing.Type" function to the abstract class
typing.cast(typing.Any, CanaryTestMetricsOverride).__jsii_proxy_class__ = lambda : _CanaryTestMetricsOverrideProxy


@jsii.implements(IContributorInsightRuleDetails)
class ContributorInsightRuleDetails(
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdklabs/multi-az-observability.ContributorInsightRuleDetails",
):
    '''(experimental) The contributor insight rule details for creating an insight rule.

    :stability: experimental
    '''

    def __init__(
        self,
        *,
        availability_zone_id_json_path: builtins.str,
        fault_metric_json_path: builtins.str,
        instance_id_json_path: builtins.str,
        log_groups: typing.Sequence[_aws_cdk_aws_logs_ceddda9d.ILogGroup],
        operation_name_json_path: builtins.str,
        success_latency_metric_json_path: builtins.str,
    ) -> None:
        '''
        :param availability_zone_id_json_path: (experimental) The path in the log files to the field that identifies the Availability Zone Id that the request was handled in, for example { "AZ-ID": "use1-az1" } would have a path of $.AZ-ID.
        :param fault_metric_json_path: (experimental) The path in the log files to the field that identifies if the response resulted in a fault, for example { "Fault" : 1 } would have a path of $.Fault.
        :param instance_id_json_path: (experimental) The JSON path to the instance id field in the log files, only required for server-side rules.
        :param log_groups: (experimental) The log groups where CloudWatch logs for the operation are located. If this is not provided, Contributor Insight rules cannot be created.
        :param operation_name_json_path: (experimental) The path in the log files to the field that identifies the operation the log file is for.
        :param success_latency_metric_json_path: (experimental) The path in the log files to the field that indicates the latency for the response. This could either be success latency or fault latency depending on the alarms and rules you are creating.

        :stability: experimental
        '''
        props = ContributorInsightRuleDetailsProps(
            availability_zone_id_json_path=availability_zone_id_json_path,
            fault_metric_json_path=fault_metric_json_path,
            instance_id_json_path=instance_id_json_path,
            log_groups=log_groups,
            operation_name_json_path=operation_name_json_path,
            success_latency_metric_json_path=success_latency_metric_json_path,
        )

        jsii.create(self.__class__, self, [props])

    @builtins.property
    @jsii.member(jsii_name="availabilityZoneIdJsonPath")
    def availability_zone_id_json_path(self) -> builtins.str:
        '''(experimental) The path in the log files to the field that identifies the Availability Zone Id that the request was handled in, for example { "AZ-ID": "use1-az1" } would have a path of $.AZ-ID.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "availabilityZoneIdJsonPath"))

    @builtins.property
    @jsii.member(jsii_name="faultMetricJsonPath")
    def fault_metric_json_path(self) -> builtins.str:
        '''(experimental) The path in the log files to the field that identifies if the response resulted in a fault, for example { "Fault" : 1 } would have a path of $.Fault.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "faultMetricJsonPath"))

    @builtins.property
    @jsii.member(jsii_name="instanceIdJsonPath")
    def instance_id_json_path(self) -> builtins.str:
        '''(experimental) The JSON path to the instance id field in the log files, only required for server-side rules.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "instanceIdJsonPath"))

    @builtins.property
    @jsii.member(jsii_name="logGroups")
    def log_groups(self) -> typing.List[_aws_cdk_aws_logs_ceddda9d.ILogGroup]:
        '''(experimental) The log groups where CloudWatch logs for the operation are located.

        If
        this is not provided, Contributor Insight rules cannot be created.

        :stability: experimental
        '''
        return typing.cast(typing.List[_aws_cdk_aws_logs_ceddda9d.ILogGroup], jsii.get(self, "logGroups"))

    @builtins.property
    @jsii.member(jsii_name="operationNameJsonPath")
    def operation_name_json_path(self) -> builtins.str:
        '''(experimental) The path in the log files to the field that identifies the operation the log file is for.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "operationNameJsonPath"))

    @builtins.property
    @jsii.member(jsii_name="successLatencyMetricJsonPath")
    def success_latency_metric_json_path(self) -> builtins.str:
        '''(experimental) The path in the log files to the field that indicates the latency for the response.

        This could either be success latency or fault
        latency depending on the alarms and rules you are creating.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "successLatencyMetricJsonPath"))


@jsii.interface(
    jsii_type="@cdklabs/multi-az-observability.ICanaryTestAvailabilityMetricsOverride"
)
class ICanaryTestAvailabilityMetricsOverride(
    ICanaryTestMetricsOverride,
    typing_extensions.Protocol,
):
    '''(experimental) Provides overrides for the default metric settings used for the automatically created canary tests.

    :stability: experimental
    '''

    @builtins.property
    @jsii.member(jsii_name="faultAlarmThreshold")
    def fault_alarm_threshold(self) -> typing.Optional[jsii.Number]:
        '''(experimental) The threshold for alarms associated with fault metrics, for example if measuring fault rate, the threshold may be 1, meaning you would want an alarm that triggers if the fault rate goes above 1%.

        :default: - This property will use the default defined for the service

        :stability: experimental
        '''
        ...

    @builtins.property
    @jsii.member(jsii_name="successAlarmThreshold")
    def success_alarm_threshold(self) -> typing.Optional[jsii.Number]:
        '''(experimental) The threshold for alarms associated with success metrics, for example if measuring success rate, the threshold may be 99, meaning you would want an alarm that triggers if success drops below 99%.

        :default: - This property will use the default defined for the service

        :stability: experimental
        '''
        ...


class _ICanaryTestAvailabilityMetricsOverrideProxy(
    jsii.proxy_for(ICanaryTestMetricsOverride), # type: ignore[misc]
):
    '''(experimental) Provides overrides for the default metric settings used for the automatically created canary tests.

    :stability: experimental
    '''

    __jsii_type__: typing.ClassVar[str] = "@cdklabs/multi-az-observability.ICanaryTestAvailabilityMetricsOverride"

    @builtins.property
    @jsii.member(jsii_name="faultAlarmThreshold")
    def fault_alarm_threshold(self) -> typing.Optional[jsii.Number]:
        '''(experimental) The threshold for alarms associated with fault metrics, for example if measuring fault rate, the threshold may be 1, meaning you would want an alarm that triggers if the fault rate goes above 1%.

        :default: - This property will use the default defined for the service

        :stability: experimental
        '''
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "faultAlarmThreshold"))

    @builtins.property
    @jsii.member(jsii_name="successAlarmThreshold")
    def success_alarm_threshold(self) -> typing.Optional[jsii.Number]:
        '''(experimental) The threshold for alarms associated with success metrics, for example if measuring success rate, the threshold may be 99, meaning you would want an alarm that triggers if success drops below 99%.

        :default: - This property will use the default defined for the service

        :stability: experimental
        '''
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "successAlarmThreshold"))

# Adding a "__jsii_proxy_class__(): typing.Type" function to the interface
typing.cast(typing.Any, ICanaryTestAvailabilityMetricsOverride).__jsii_proxy_class__ = lambda : _ICanaryTestAvailabilityMetricsOverrideProxy


@jsii.interface(
    jsii_type="@cdklabs/multi-az-observability.ICanaryTestLatencyMetricsOverride"
)
class ICanaryTestLatencyMetricsOverride(
    ICanaryTestMetricsOverride,
    typing_extensions.Protocol,
):
    '''(experimental) Provides overrides for the default metric settings used for the automatically created canary tests.

    :stability: experimental
    '''

    @builtins.property
    @jsii.member(jsii_name="successAlarmThreshold")
    def success_alarm_threshold(self) -> typing.Optional[_aws_cdk_ceddda9d.Duration]:
        '''(experimental) The threshold for alarms associated with latency success metrics, for example if success latency exceeds 500 milliseconds.

        :stability: experimental
        '''
        ...


class _ICanaryTestLatencyMetricsOverrideProxy(
    jsii.proxy_for(ICanaryTestMetricsOverride), # type: ignore[misc]
):
    '''(experimental) Provides overrides for the default metric settings used for the automatically created canary tests.

    :stability: experimental
    '''

    __jsii_type__: typing.ClassVar[str] = "@cdklabs/multi-az-observability.ICanaryTestLatencyMetricsOverride"

    @builtins.property
    @jsii.member(jsii_name="successAlarmThreshold")
    def success_alarm_threshold(self) -> typing.Optional[_aws_cdk_ceddda9d.Duration]:
        '''(experimental) The threshold for alarms associated with latency success metrics, for example if success latency exceeds 500 milliseconds.

        :stability: experimental
        '''
        return typing.cast(typing.Optional[_aws_cdk_ceddda9d.Duration], jsii.get(self, "successAlarmThreshold"))

# Adding a "__jsii_proxy_class__(): typing.Type" function to the interface
typing.cast(typing.Any, ICanaryTestLatencyMetricsOverride).__jsii_proxy_class__ = lambda : _ICanaryTestLatencyMetricsOverrideProxy


@jsii.interface(
    jsii_type="@cdklabs/multi-az-observability.IOperationAvailabilityMetricDetails"
)
class IOperationAvailabilityMetricDetails(
    IOperationMetricDetails,
    typing_extensions.Protocol,
):
    '''(experimental) Details for operation metrics in one perspective, such as server side latency.

    :stability: experimental
    '''

    @builtins.property
    @jsii.member(jsii_name="faultAlarmThreshold")
    def fault_alarm_threshold(self) -> jsii.Number:
        '''(experimental) The threshold for alarms associated with availability fault metrics, for example if measuring fault rate, the threshold may be 1, meaning you would want an alarm that triggers if the fault rate goes above 1%.

        :stability: experimental
        '''
        ...

    @builtins.property
    @jsii.member(jsii_name="successAlarmThreshold")
    def success_alarm_threshold(self) -> jsii.Number:
        '''(experimental) The threshold for alarms associated with availability success metrics, for example if measuring success rate, the threshold may be 99, meaning you would want an alarm that triggers if success drops below 99%.

        :stability: experimental
        '''
        ...


class _IOperationAvailabilityMetricDetailsProxy(
    jsii.proxy_for(IOperationMetricDetails), # type: ignore[misc]
):
    '''(experimental) Details for operation metrics in one perspective, such as server side latency.

    :stability: experimental
    '''

    __jsii_type__: typing.ClassVar[str] = "@cdklabs/multi-az-observability.IOperationAvailabilityMetricDetails"

    @builtins.property
    @jsii.member(jsii_name="faultAlarmThreshold")
    def fault_alarm_threshold(self) -> jsii.Number:
        '''(experimental) The threshold for alarms associated with availability fault metrics, for example if measuring fault rate, the threshold may be 1, meaning you would want an alarm that triggers if the fault rate goes above 1%.

        :stability: experimental
        '''
        return typing.cast(jsii.Number, jsii.get(self, "faultAlarmThreshold"))

    @builtins.property
    @jsii.member(jsii_name="successAlarmThreshold")
    def success_alarm_threshold(self) -> jsii.Number:
        '''(experimental) The threshold for alarms associated with availability success metrics, for example if measuring success rate, the threshold may be 99, meaning you would want an alarm that triggers if success drops below 99%.

        :stability: experimental
        '''
        return typing.cast(jsii.Number, jsii.get(self, "successAlarmThreshold"))

# Adding a "__jsii_proxy_class__(): typing.Type" function to the interface
typing.cast(typing.Any, IOperationAvailabilityMetricDetails).__jsii_proxy_class__ = lambda : _IOperationAvailabilityMetricDetailsProxy


@jsii.interface(
    jsii_type="@cdklabs/multi-az-observability.IOperationLatencyMetricDetails"
)
class IOperationLatencyMetricDetails(
    IOperationMetricDetails,
    typing_extensions.Protocol,
):
    '''(experimental) Details for operation metrics in one perspective, such as server side latency.

    :stability: experimental
    '''

    @builtins.property
    @jsii.member(jsii_name="successAlarmThreshold")
    def success_alarm_threshold(self) -> _aws_cdk_ceddda9d.Duration:
        '''(experimental) The threshold for alarms associated with latency success metrics, for example if success latency exceeds 500 milliseconds.

        :stability: experimental
        '''
        ...


class _IOperationLatencyMetricDetailsProxy(
    jsii.proxy_for(IOperationMetricDetails), # type: ignore[misc]
):
    '''(experimental) Details for operation metrics in one perspective, such as server side latency.

    :stability: experimental
    '''

    __jsii_type__: typing.ClassVar[str] = "@cdklabs/multi-az-observability.IOperationLatencyMetricDetails"

    @builtins.property
    @jsii.member(jsii_name="successAlarmThreshold")
    def success_alarm_threshold(self) -> _aws_cdk_ceddda9d.Duration:
        '''(experimental) The threshold for alarms associated with latency success metrics, for example if success latency exceeds 500 milliseconds.

        :stability: experimental
        '''
        return typing.cast(_aws_cdk_ceddda9d.Duration, jsii.get(self, "successAlarmThreshold"))

# Adding a "__jsii_proxy_class__(): typing.Type" function to the interface
typing.cast(typing.Any, IOperationLatencyMetricDetails).__jsii_proxy_class__ = lambda : _IOperationLatencyMetricDetailsProxy


@jsii.interface(
    jsii_type="@cdklabs/multi-az-observability.IServiceAvailabilityMetricDetails"
)
class IServiceAvailabilityMetricDetails(
    IServiceMetricDetails,
    typing_extensions.Protocol,
):
    '''(experimental) Details for the defaults used in a service for metrics in one perspective, such as server side latency.

    :stability: experimental
    '''

    @builtins.property
    @jsii.member(jsii_name="faultAlarmThreshold")
    def fault_alarm_threshold(self) -> jsii.Number:
        '''(experimental) The threshold for alarms associated with availability fault metrics, for example if measuring fault rate, the threshold may be 1, meaning you would want an alarm that triggers if the fault rate goes above 1%.

        :stability: experimental
        '''
        ...

    @builtins.property
    @jsii.member(jsii_name="successAlarmThreshold")
    def success_alarm_threshold(self) -> jsii.Number:
        '''(experimental) The threshold for alarms associated with availability success metrics, for example if measuring success rate, the threshold may be 99, meaning you would want an alarm that triggers if success drops below 99%.

        :stability: experimental
        '''
        ...


class _IServiceAvailabilityMetricDetailsProxy(
    jsii.proxy_for(IServiceMetricDetails), # type: ignore[misc]
):
    '''(experimental) Details for the defaults used in a service for metrics in one perspective, such as server side latency.

    :stability: experimental
    '''

    __jsii_type__: typing.ClassVar[str] = "@cdklabs/multi-az-observability.IServiceAvailabilityMetricDetails"

    @builtins.property
    @jsii.member(jsii_name="faultAlarmThreshold")
    def fault_alarm_threshold(self) -> jsii.Number:
        '''(experimental) The threshold for alarms associated with availability fault metrics, for example if measuring fault rate, the threshold may be 1, meaning you would want an alarm that triggers if the fault rate goes above 1%.

        :stability: experimental
        '''
        return typing.cast(jsii.Number, jsii.get(self, "faultAlarmThreshold"))

    @builtins.property
    @jsii.member(jsii_name="successAlarmThreshold")
    def success_alarm_threshold(self) -> jsii.Number:
        '''(experimental) The threshold for alarms associated with availability success metrics, for example if measuring success rate, the threshold may be 99, meaning you would want an alarm that triggers if success drops below 99%.

        :stability: experimental
        '''
        return typing.cast(jsii.Number, jsii.get(self, "successAlarmThreshold"))

# Adding a "__jsii_proxy_class__(): typing.Type" function to the interface
typing.cast(typing.Any, IServiceAvailabilityMetricDetails).__jsii_proxy_class__ = lambda : _IServiceAvailabilityMetricDetailsProxy


@jsii.interface(
    jsii_type="@cdklabs/multi-az-observability.IServiceLatencyMetricDetails"
)
class IServiceLatencyMetricDetails(IServiceMetricDetails, typing_extensions.Protocol):
    '''(experimental) Details for the defaults used in a service for metrics in one perspective, such as server side latency.

    :stability: experimental
    '''

    @builtins.property
    @jsii.member(jsii_name="successAlarmThreshold")
    def success_alarm_threshold(self) -> _aws_cdk_ceddda9d.Duration:
        '''(experimental) The threshold for alarms associated with latency success metrics, for example if success latency exceeds 500 milliseconds.

        :stability: experimental
        '''
        ...


class _IServiceLatencyMetricDetailsProxy(
    jsii.proxy_for(IServiceMetricDetails), # type: ignore[misc]
):
    '''(experimental) Details for the defaults used in a service for metrics in one perspective, such as server side latency.

    :stability: experimental
    '''

    __jsii_type__: typing.ClassVar[str] = "@cdklabs/multi-az-observability.IServiceLatencyMetricDetails"

    @builtins.property
    @jsii.member(jsii_name="successAlarmThreshold")
    def success_alarm_threshold(self) -> _aws_cdk_ceddda9d.Duration:
        '''(experimental) The threshold for alarms associated with latency success metrics, for example if success latency exceeds 500 milliseconds.

        :stability: experimental
        '''
        return typing.cast(_aws_cdk_ceddda9d.Duration, jsii.get(self, "successAlarmThreshold"))

# Adding a "__jsii_proxy_class__(): typing.Type" function to the interface
typing.cast(typing.Any, IServiceLatencyMetricDetails).__jsii_proxy_class__ = lambda : _IServiceLatencyMetricDetailsProxy


@jsii.implements(IOperationAvailabilityMetricDetails)
class OperationAvailabilityMetricDetails(
    OperationMetricDetails,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdklabs/multi-az-observability.OperationAvailabilityMetricDetails",
):
    '''(experimental) Availability metric details for an operation.

    :stability: experimental
    '''

    def __init__(
        self,
        props: typing.Union["OperationAvailabilityMetricDetailsProps", typing.Dict[builtins.str, typing.Any]],
        default_props: IServiceAvailabilityMetricDetails,
    ) -> None:
        '''
        :param props: -
        :param default_props: -

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ba3bfecde875105b94fc5e3d1922b0cf4d9ac970ef13c3f154d11a6e7b103874)
            check_type(argname="argument props", value=props, expected_type=type_hints["props"])
            check_type(argname="argument default_props", value=default_props, expected_type=type_hints["default_props"])
        jsii.create(self.__class__, self, [props, default_props])

    @builtins.property
    @jsii.member(jsii_name="faultAlarmThreshold")
    def fault_alarm_threshold(self) -> jsii.Number:
        '''(experimental) The threshold for alarms associated with availability fault metrics, for example if measuring fault rate, the threshold may be 1, meaning you would want an alarm that triggers if the fault rate goes above 1%.

        :stability: experimental
        '''
        return typing.cast(jsii.Number, jsii.get(self, "faultAlarmThreshold"))

    @builtins.property
    @jsii.member(jsii_name="successAlarmThreshold")
    def success_alarm_threshold(self) -> jsii.Number:
        '''(experimental) The threshold for alarms associated with availability success metrics, for example if measuring success rate, the threshold may be 99, meaning you would want an alarm that triggers if success drops below 99%.

        :stability: experimental
        '''
        return typing.cast(jsii.Number, jsii.get(self, "successAlarmThreshold"))


@jsii.data_type(
    jsii_type="@cdklabs/multi-az-observability.OperationAvailabilityMetricDetailsProps",
    jsii_struct_bases=[OperationMetricDetailsProps],
    name_mapping={
        "metric_dimensions": "metricDimensions",
        "operation_name": "operationName",
        "alarm_statistic": "alarmStatistic",
        "datapoints_to_alarm": "datapointsToAlarm",
        "evaluation_periods": "evaluationPeriods",
        "fault_metric_names": "faultMetricNames",
        "graphed_fault_statistics": "graphedFaultStatistics",
        "graphed_success_statistics": "graphedSuccessStatistics",
        "metric_namespace": "metricNamespace",
        "period": "period",
        "success_metric_names": "successMetricNames",
        "unit": "unit",
        "fault_alarm_threshold": "faultAlarmThreshold",
        "success_alarm_threshold": "successAlarmThreshold",
    },
)
class OperationAvailabilityMetricDetailsProps(OperationMetricDetailsProps):
    def __init__(
        self,
        *,
        metric_dimensions: MetricDimensions,
        operation_name: builtins.str,
        alarm_statistic: typing.Optional[builtins.str] = None,
        datapoints_to_alarm: typing.Optional[jsii.Number] = None,
        evaluation_periods: typing.Optional[jsii.Number] = None,
        fault_metric_names: typing.Optional[typing.Sequence[builtins.str]] = None,
        graphed_fault_statistics: typing.Optional[typing.Sequence[builtins.str]] = None,
        graphed_success_statistics: typing.Optional[typing.Sequence[builtins.str]] = None,
        metric_namespace: typing.Optional[builtins.str] = None,
        period: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
        success_metric_names: typing.Optional[typing.Sequence[builtins.str]] = None,
        unit: typing.Optional[_aws_cdk_aws_cloudwatch_ceddda9d.Unit] = None,
        fault_alarm_threshold: typing.Optional[jsii.Number] = None,
        success_alarm_threshold: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''(experimental) The properties for an operation's availability metric details.

        :param metric_dimensions: (experimental) The user implemented functions for providing the metric's dimensions.
        :param operation_name: (experimental) The operation these metric details are for.
        :param alarm_statistic: (experimental) The statistic used for alarms, for availability metrics this should be "Sum", for latency metrics it could something like "p99" or "p99.9". Default: - The service default is used
        :param datapoints_to_alarm: (experimental) The number of datapoints to alarm on for latency and availability alarms. Default: - The service default is used
        :param evaluation_periods: (experimental) The number of evaluation periods for latency and availabiltiy alarms. Default: - The service default is used
        :param fault_metric_names: (experimental) The names of fault indicating metrics. Default: - The service default is used
        :param graphed_fault_statistics: (experimental) The statistics for faults you want to appear on dashboards, for example, with latency metrics, you might want p50, p99, and tm99. For availability metrics this will typically just be "Sum". Default: - The service default is used
        :param graphed_success_statistics: (experimental) The statistics for successes you want to appear on dashboards, for example, with latency metrics, you might want p50, p99, and tm99. For availability metrics this will typically just be "Sum". Default: - The service default is used
        :param metric_namespace: (experimental) The CloudWatch metric namespace for these metrics. Default: - The service default is used
        :param period: (experimental) The period for the metrics. Default: - The service default is used
        :param success_metric_names: (experimental) The names of success indicating metrics. Default: - The service default is used
        :param unit: (experimental) The unit used for these metrics. Default: - The service default is used
        :param fault_alarm_threshold: (experimental) The threshold for alarms associated with availability fault metrics, for example if measuring fault rate, the threshold may be 1, meaning you would want an alarm that triggers if the fault rate goes above 1%. Default: - The service default is used
        :param success_alarm_threshold: (experimental) The threshold for alarms associated with availability success metrics, for example if measuring success rate, the threshold may be 99, meaning you would want an alarm that triggers if success drops below 99%. Default: - The service default is used

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f3a9c1d6a36b69cb1a011aaf63c41f895ce71b2e79f4e86ddd6d326d5b7c9a94)
            check_type(argname="argument metric_dimensions", value=metric_dimensions, expected_type=type_hints["metric_dimensions"])
            check_type(argname="argument operation_name", value=operation_name, expected_type=type_hints["operation_name"])
            check_type(argname="argument alarm_statistic", value=alarm_statistic, expected_type=type_hints["alarm_statistic"])
            check_type(argname="argument datapoints_to_alarm", value=datapoints_to_alarm, expected_type=type_hints["datapoints_to_alarm"])
            check_type(argname="argument evaluation_periods", value=evaluation_periods, expected_type=type_hints["evaluation_periods"])
            check_type(argname="argument fault_metric_names", value=fault_metric_names, expected_type=type_hints["fault_metric_names"])
            check_type(argname="argument graphed_fault_statistics", value=graphed_fault_statistics, expected_type=type_hints["graphed_fault_statistics"])
            check_type(argname="argument graphed_success_statistics", value=graphed_success_statistics, expected_type=type_hints["graphed_success_statistics"])
            check_type(argname="argument metric_namespace", value=metric_namespace, expected_type=type_hints["metric_namespace"])
            check_type(argname="argument period", value=period, expected_type=type_hints["period"])
            check_type(argname="argument success_metric_names", value=success_metric_names, expected_type=type_hints["success_metric_names"])
            check_type(argname="argument unit", value=unit, expected_type=type_hints["unit"])
            check_type(argname="argument fault_alarm_threshold", value=fault_alarm_threshold, expected_type=type_hints["fault_alarm_threshold"])
            check_type(argname="argument success_alarm_threshold", value=success_alarm_threshold, expected_type=type_hints["success_alarm_threshold"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "metric_dimensions": metric_dimensions,
            "operation_name": operation_name,
        }
        if alarm_statistic is not None:
            self._values["alarm_statistic"] = alarm_statistic
        if datapoints_to_alarm is not None:
            self._values["datapoints_to_alarm"] = datapoints_to_alarm
        if evaluation_periods is not None:
            self._values["evaluation_periods"] = evaluation_periods
        if fault_metric_names is not None:
            self._values["fault_metric_names"] = fault_metric_names
        if graphed_fault_statistics is not None:
            self._values["graphed_fault_statistics"] = graphed_fault_statistics
        if graphed_success_statistics is not None:
            self._values["graphed_success_statistics"] = graphed_success_statistics
        if metric_namespace is not None:
            self._values["metric_namespace"] = metric_namespace
        if period is not None:
            self._values["period"] = period
        if success_metric_names is not None:
            self._values["success_metric_names"] = success_metric_names
        if unit is not None:
            self._values["unit"] = unit
        if fault_alarm_threshold is not None:
            self._values["fault_alarm_threshold"] = fault_alarm_threshold
        if success_alarm_threshold is not None:
            self._values["success_alarm_threshold"] = success_alarm_threshold

    @builtins.property
    def metric_dimensions(self) -> MetricDimensions:
        '''(experimental) The user implemented functions for providing the metric's dimensions.

        :stability: experimental
        '''
        result = self._values.get("metric_dimensions")
        assert result is not None, "Required property 'metric_dimensions' is missing"
        return typing.cast(MetricDimensions, result)

    @builtins.property
    def operation_name(self) -> builtins.str:
        '''(experimental) The operation these metric details are for.

        :stability: experimental
        '''
        result = self._values.get("operation_name")
        assert result is not None, "Required property 'operation_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def alarm_statistic(self) -> typing.Optional[builtins.str]:
        '''(experimental) The statistic used for alarms, for availability metrics this should be "Sum", for latency metrics it could something like "p99" or "p99.9".

        :default: - The service default is used

        :stability: experimental
        '''
        result = self._values.get("alarm_statistic")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def datapoints_to_alarm(self) -> typing.Optional[jsii.Number]:
        '''(experimental) The number of datapoints to alarm on for latency and availability alarms.

        :default: - The service default is used

        :stability: experimental
        '''
        result = self._values.get("datapoints_to_alarm")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def evaluation_periods(self) -> typing.Optional[jsii.Number]:
        '''(experimental) The number of evaluation periods for latency and availabiltiy alarms.

        :default: - The service default is used

        :stability: experimental
        '''
        result = self._values.get("evaluation_periods")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def fault_metric_names(self) -> typing.Optional[typing.List[builtins.str]]:
        '''(experimental) The names of fault indicating metrics.

        :default: - The service default is used

        :stability: experimental
        '''
        result = self._values.get("fault_metric_names")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def graphed_fault_statistics(self) -> typing.Optional[typing.List[builtins.str]]:
        '''(experimental) The statistics for faults you want to appear on dashboards, for example, with latency metrics, you might want p50, p99, and tm99.

        For availability
        metrics this will typically just be "Sum".

        :default: - The service default is used

        :stability: experimental
        '''
        result = self._values.get("graphed_fault_statistics")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def graphed_success_statistics(self) -> typing.Optional[typing.List[builtins.str]]:
        '''(experimental) The statistics for successes you want to appear on dashboards, for example, with latency metrics, you might want p50, p99, and tm99.

        For availability
        metrics this will typically just be "Sum".

        :default: - The service default is used

        :stability: experimental
        '''
        result = self._values.get("graphed_success_statistics")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def metric_namespace(self) -> typing.Optional[builtins.str]:
        '''(experimental) The CloudWatch metric namespace for these metrics.

        :default: - The service default is used

        :stability: experimental
        '''
        result = self._values.get("metric_namespace")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def period(self) -> typing.Optional[_aws_cdk_ceddda9d.Duration]:
        '''(experimental) The period for the metrics.

        :default: - The service default is used

        :stability: experimental
        '''
        result = self._values.get("period")
        return typing.cast(typing.Optional[_aws_cdk_ceddda9d.Duration], result)

    @builtins.property
    def success_metric_names(self) -> typing.Optional[typing.List[builtins.str]]:
        '''(experimental) The names of success indicating metrics.

        :default: - The service default is used

        :stability: experimental
        '''
        result = self._values.get("success_metric_names")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def unit(self) -> typing.Optional[_aws_cdk_aws_cloudwatch_ceddda9d.Unit]:
        '''(experimental) The unit used for these metrics.

        :default: - The service default is used

        :stability: experimental
        '''
        result = self._values.get("unit")
        return typing.cast(typing.Optional[_aws_cdk_aws_cloudwatch_ceddda9d.Unit], result)

    @builtins.property
    def fault_alarm_threshold(self) -> typing.Optional[jsii.Number]:
        '''(experimental) The threshold for alarms associated with availability fault metrics, for example if measuring fault rate, the threshold may be 1, meaning you would want an alarm that triggers if the fault rate goes above 1%.

        :default: - The service default is used

        :stability: experimental
        '''
        result = self._values.get("fault_alarm_threshold")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def success_alarm_threshold(self) -> typing.Optional[jsii.Number]:
        '''(experimental) The threshold for alarms associated with availability success metrics, for example if measuring success rate, the threshold may be 99, meaning you would want an alarm that triggers if success drops below 99%.

        :default: - The service default is used

        :stability: experimental
        '''
        result = self._values.get("success_alarm_threshold")
        return typing.cast(typing.Optional[jsii.Number], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "OperationAvailabilityMetricDetailsProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.implements(IOperationLatencyMetricDetails)
class OperationLatencyMetricDetails(
    OperationMetricDetails,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdklabs/multi-az-observability.OperationLatencyMetricDetails",
):
    '''(experimental) Latency metric details for an operation.

    :stability: experimental
    '''

    def __init__(
        self,
        props: typing.Union["OperationLatencyMetricDetailsProps", typing.Dict[builtins.str, typing.Any]],
        default_props: IServiceLatencyMetricDetails,
    ) -> None:
        '''
        :param props: -
        :param default_props: -

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c8055ed37fd46397f374a68d5b4756d9a2fcd37a50f9f4a9977c721a44a9f981)
            check_type(argname="argument props", value=props, expected_type=type_hints["props"])
            check_type(argname="argument default_props", value=default_props, expected_type=type_hints["default_props"])
        jsii.create(self.__class__, self, [props, default_props])

    @builtins.property
    @jsii.member(jsii_name="successAlarmThreshold")
    def success_alarm_threshold(self) -> _aws_cdk_ceddda9d.Duration:
        '''(experimental) The threshold for alarms associated with latency success metrics, for example if success latency exceeds 500 milliseconds.

        :stability: experimental
        '''
        return typing.cast(_aws_cdk_ceddda9d.Duration, jsii.get(self, "successAlarmThreshold"))


@jsii.data_type(
    jsii_type="@cdklabs/multi-az-observability.OperationLatencyMetricDetailsProps",
    jsii_struct_bases=[OperationMetricDetailsProps],
    name_mapping={
        "metric_dimensions": "metricDimensions",
        "operation_name": "operationName",
        "alarm_statistic": "alarmStatistic",
        "datapoints_to_alarm": "datapointsToAlarm",
        "evaluation_periods": "evaluationPeriods",
        "fault_metric_names": "faultMetricNames",
        "graphed_fault_statistics": "graphedFaultStatistics",
        "graphed_success_statistics": "graphedSuccessStatistics",
        "metric_namespace": "metricNamespace",
        "period": "period",
        "success_metric_names": "successMetricNames",
        "unit": "unit",
        "success_alarm_threshold": "successAlarmThreshold",
    },
)
class OperationLatencyMetricDetailsProps(OperationMetricDetailsProps):
    def __init__(
        self,
        *,
        metric_dimensions: MetricDimensions,
        operation_name: builtins.str,
        alarm_statistic: typing.Optional[builtins.str] = None,
        datapoints_to_alarm: typing.Optional[jsii.Number] = None,
        evaluation_periods: typing.Optional[jsii.Number] = None,
        fault_metric_names: typing.Optional[typing.Sequence[builtins.str]] = None,
        graphed_fault_statistics: typing.Optional[typing.Sequence[builtins.str]] = None,
        graphed_success_statistics: typing.Optional[typing.Sequence[builtins.str]] = None,
        metric_namespace: typing.Optional[builtins.str] = None,
        period: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
        success_metric_names: typing.Optional[typing.Sequence[builtins.str]] = None,
        unit: typing.Optional[_aws_cdk_aws_cloudwatch_ceddda9d.Unit] = None,
        success_alarm_threshold: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
    ) -> None:
        '''(experimental) The properties for an operation's latency metric details.

        :param metric_dimensions: (experimental) The user implemented functions for providing the metric's dimensions.
        :param operation_name: (experimental) The operation these metric details are for.
        :param alarm_statistic: (experimental) The statistic used for alarms, for availability metrics this should be "Sum", for latency metrics it could something like "p99" or "p99.9". Default: - The service default is used
        :param datapoints_to_alarm: (experimental) The number of datapoints to alarm on for latency and availability alarms. Default: - The service default is used
        :param evaluation_periods: (experimental) The number of evaluation periods for latency and availabiltiy alarms. Default: - The service default is used
        :param fault_metric_names: (experimental) The names of fault indicating metrics. Default: - The service default is used
        :param graphed_fault_statistics: (experimental) The statistics for faults you want to appear on dashboards, for example, with latency metrics, you might want p50, p99, and tm99. For availability metrics this will typically just be "Sum". Default: - The service default is used
        :param graphed_success_statistics: (experimental) The statistics for successes you want to appear on dashboards, for example, with latency metrics, you might want p50, p99, and tm99. For availability metrics this will typically just be "Sum". Default: - The service default is used
        :param metric_namespace: (experimental) The CloudWatch metric namespace for these metrics. Default: - The service default is used
        :param period: (experimental) The period for the metrics. Default: - The service default is used
        :param success_metric_names: (experimental) The names of success indicating metrics. Default: - The service default is used
        :param unit: (experimental) The unit used for these metrics. Default: - The service default is used
        :param success_alarm_threshold: (experimental) The threshold for alarms associated with latency success metrics, for example if success latency exceeds 500 milliseconds. Default: "The service default is used"

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9b6e546c66235e53a68265cd01ee63d2bcecaf6761795b96fc1f1bc7757e38cc)
            check_type(argname="argument metric_dimensions", value=metric_dimensions, expected_type=type_hints["metric_dimensions"])
            check_type(argname="argument operation_name", value=operation_name, expected_type=type_hints["operation_name"])
            check_type(argname="argument alarm_statistic", value=alarm_statistic, expected_type=type_hints["alarm_statistic"])
            check_type(argname="argument datapoints_to_alarm", value=datapoints_to_alarm, expected_type=type_hints["datapoints_to_alarm"])
            check_type(argname="argument evaluation_periods", value=evaluation_periods, expected_type=type_hints["evaluation_periods"])
            check_type(argname="argument fault_metric_names", value=fault_metric_names, expected_type=type_hints["fault_metric_names"])
            check_type(argname="argument graphed_fault_statistics", value=graphed_fault_statistics, expected_type=type_hints["graphed_fault_statistics"])
            check_type(argname="argument graphed_success_statistics", value=graphed_success_statistics, expected_type=type_hints["graphed_success_statistics"])
            check_type(argname="argument metric_namespace", value=metric_namespace, expected_type=type_hints["metric_namespace"])
            check_type(argname="argument period", value=period, expected_type=type_hints["period"])
            check_type(argname="argument success_metric_names", value=success_metric_names, expected_type=type_hints["success_metric_names"])
            check_type(argname="argument unit", value=unit, expected_type=type_hints["unit"])
            check_type(argname="argument success_alarm_threshold", value=success_alarm_threshold, expected_type=type_hints["success_alarm_threshold"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "metric_dimensions": metric_dimensions,
            "operation_name": operation_name,
        }
        if alarm_statistic is not None:
            self._values["alarm_statistic"] = alarm_statistic
        if datapoints_to_alarm is not None:
            self._values["datapoints_to_alarm"] = datapoints_to_alarm
        if evaluation_periods is not None:
            self._values["evaluation_periods"] = evaluation_periods
        if fault_metric_names is not None:
            self._values["fault_metric_names"] = fault_metric_names
        if graphed_fault_statistics is not None:
            self._values["graphed_fault_statistics"] = graphed_fault_statistics
        if graphed_success_statistics is not None:
            self._values["graphed_success_statistics"] = graphed_success_statistics
        if metric_namespace is not None:
            self._values["metric_namespace"] = metric_namespace
        if period is not None:
            self._values["period"] = period
        if success_metric_names is not None:
            self._values["success_metric_names"] = success_metric_names
        if unit is not None:
            self._values["unit"] = unit
        if success_alarm_threshold is not None:
            self._values["success_alarm_threshold"] = success_alarm_threshold

    @builtins.property
    def metric_dimensions(self) -> MetricDimensions:
        '''(experimental) The user implemented functions for providing the metric's dimensions.

        :stability: experimental
        '''
        result = self._values.get("metric_dimensions")
        assert result is not None, "Required property 'metric_dimensions' is missing"
        return typing.cast(MetricDimensions, result)

    @builtins.property
    def operation_name(self) -> builtins.str:
        '''(experimental) The operation these metric details are for.

        :stability: experimental
        '''
        result = self._values.get("operation_name")
        assert result is not None, "Required property 'operation_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def alarm_statistic(self) -> typing.Optional[builtins.str]:
        '''(experimental) The statistic used for alarms, for availability metrics this should be "Sum", for latency metrics it could something like "p99" or "p99.9".

        :default: - The service default is used

        :stability: experimental
        '''
        result = self._values.get("alarm_statistic")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def datapoints_to_alarm(self) -> typing.Optional[jsii.Number]:
        '''(experimental) The number of datapoints to alarm on for latency and availability alarms.

        :default: - The service default is used

        :stability: experimental
        '''
        result = self._values.get("datapoints_to_alarm")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def evaluation_periods(self) -> typing.Optional[jsii.Number]:
        '''(experimental) The number of evaluation periods for latency and availabiltiy alarms.

        :default: - The service default is used

        :stability: experimental
        '''
        result = self._values.get("evaluation_periods")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def fault_metric_names(self) -> typing.Optional[typing.List[builtins.str]]:
        '''(experimental) The names of fault indicating metrics.

        :default: - The service default is used

        :stability: experimental
        '''
        result = self._values.get("fault_metric_names")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def graphed_fault_statistics(self) -> typing.Optional[typing.List[builtins.str]]:
        '''(experimental) The statistics for faults you want to appear on dashboards, for example, with latency metrics, you might want p50, p99, and tm99.

        For availability
        metrics this will typically just be "Sum".

        :default: - The service default is used

        :stability: experimental
        '''
        result = self._values.get("graphed_fault_statistics")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def graphed_success_statistics(self) -> typing.Optional[typing.List[builtins.str]]:
        '''(experimental) The statistics for successes you want to appear on dashboards, for example, with latency metrics, you might want p50, p99, and tm99.

        For availability
        metrics this will typically just be "Sum".

        :default: - The service default is used

        :stability: experimental
        '''
        result = self._values.get("graphed_success_statistics")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def metric_namespace(self) -> typing.Optional[builtins.str]:
        '''(experimental) The CloudWatch metric namespace for these metrics.

        :default: - The service default is used

        :stability: experimental
        '''
        result = self._values.get("metric_namespace")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def period(self) -> typing.Optional[_aws_cdk_ceddda9d.Duration]:
        '''(experimental) The period for the metrics.

        :default: - The service default is used

        :stability: experimental
        '''
        result = self._values.get("period")
        return typing.cast(typing.Optional[_aws_cdk_ceddda9d.Duration], result)

    @builtins.property
    def success_metric_names(self) -> typing.Optional[typing.List[builtins.str]]:
        '''(experimental) The names of success indicating metrics.

        :default: - The service default is used

        :stability: experimental
        '''
        result = self._values.get("success_metric_names")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def unit(self) -> typing.Optional[_aws_cdk_aws_cloudwatch_ceddda9d.Unit]:
        '''(experimental) The unit used for these metrics.

        :default: - The service default is used

        :stability: experimental
        '''
        result = self._values.get("unit")
        return typing.cast(typing.Optional[_aws_cdk_aws_cloudwatch_ceddda9d.Unit], result)

    @builtins.property
    def success_alarm_threshold(self) -> typing.Optional[_aws_cdk_ceddda9d.Duration]:
        '''(experimental) The threshold for alarms associated with latency success metrics, for example if success latency exceeds 500 milliseconds.

        :default: "The service default is used"

        :stability: experimental
        '''
        result = self._values.get("success_alarm_threshold")
        return typing.cast(typing.Optional[_aws_cdk_ceddda9d.Duration], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "OperationLatencyMetricDetailsProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.implements(IServiceAvailabilityMetricDetails)
class ServiceAvailabilityMetricDetails(
    ServiceMetricDetails,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdklabs/multi-az-observability.ServiceAvailabilityMetricDetails",
):
    '''(experimental) Default availability metric details for a service.

    :stability: experimental
    '''

    def __init__(
        self,
        *,
        fault_alarm_threshold: jsii.Number,
        success_alarm_threshold: jsii.Number,
        alarm_statistic: builtins.str,
        datapoints_to_alarm: jsii.Number,
        evaluation_periods: jsii.Number,
        fault_metric_names: typing.Sequence[builtins.str],
        metric_namespace: builtins.str,
        period: _aws_cdk_ceddda9d.Duration,
        success_metric_names: typing.Sequence[builtins.str],
        unit: _aws_cdk_aws_cloudwatch_ceddda9d.Unit,
        graphed_fault_statistics: typing.Optional[typing.Sequence[builtins.str]] = None,
        graphed_success_statistics: typing.Optional[typing.Sequence[builtins.str]] = None,
    ) -> None:
        '''
        :param fault_alarm_threshold: (experimental) The threshold for alarms associated with availability fault metrics, for example if measuring fault rate, the threshold may be 1, meaning you would want an alarm that triggers if the fault rate goes above 1%.
        :param success_alarm_threshold: (experimental) The threshold for alarms associated with availability success metrics, for example if measuring success rate, the threshold may be 99, meaning you would want an alarm that triggers if success drops below 99%.
        :param alarm_statistic: (experimental) The statistic used for alarms, for availability metrics this should be "Sum", for latency metrics it could something like "p99" or "p99.9".
        :param datapoints_to_alarm: (experimental) The number of datapoints to alarm on for latency and availability alarms.
        :param evaluation_periods: (experimental) The number of evaluation periods for latency and availabiltiy alarms.
        :param fault_metric_names: (experimental) The names of fault indicating metrics.
        :param metric_namespace: (experimental) The CloudWatch metric namespace for these metrics.
        :param period: (experimental) The period for the metrics.
        :param success_metric_names: (experimental) The names of success indicating metrics.
        :param unit: (experimental) The unit used for these metrics.
        :param graphed_fault_statistics: (experimental) The statistics for faults you want to appear on dashboards, for example, with latency metrics, you might want p50, p99, and tm99. For availability metrics this will typically just be "Sum". Default: - For availability metrics, this will be "Sum", for latency metrics it will be just "p99"
        :param graphed_success_statistics: (experimental) The statistics for successes you want to appear on dashboards, for example, with latency metrics, you might want p50, p99, and tm99. For availability metrics this will typically just be "Sum". Default: - For availability metrics, this will be "Sum", for latency metrics it will be just "p99"

        :stability: experimental
        '''
        props = ServiceAvailabilityMetricDetailsProps(
            fault_alarm_threshold=fault_alarm_threshold,
            success_alarm_threshold=success_alarm_threshold,
            alarm_statistic=alarm_statistic,
            datapoints_to_alarm=datapoints_to_alarm,
            evaluation_periods=evaluation_periods,
            fault_metric_names=fault_metric_names,
            metric_namespace=metric_namespace,
            period=period,
            success_metric_names=success_metric_names,
            unit=unit,
            graphed_fault_statistics=graphed_fault_statistics,
            graphed_success_statistics=graphed_success_statistics,
        )

        jsii.create(self.__class__, self, [props])

    @builtins.property
    @jsii.member(jsii_name="faultAlarmThreshold")
    def fault_alarm_threshold(self) -> jsii.Number:
        '''(experimental) The threshold for alarms associated with availability fault metrics, for example if measuring fault rate, the threshold may be 1, meaning you would want an alarm that triggers if the fault rate goes above 1%.

        :stability: experimental
        '''
        return typing.cast(jsii.Number, jsii.get(self, "faultAlarmThreshold"))

    @builtins.property
    @jsii.member(jsii_name="successAlarmThreshold")
    def success_alarm_threshold(self) -> jsii.Number:
        '''(experimental) The threshold for alarms associated with availability success metrics, for example if measuring success rate, the threshold may be 99, meaning you would want an alarm that triggers if success drops below 99%.

        :stability: experimental
        '''
        return typing.cast(jsii.Number, jsii.get(self, "successAlarmThreshold"))


@jsii.data_type(
    jsii_type="@cdklabs/multi-az-observability.ServiceAvailabilityMetricDetailsProps",
    jsii_struct_bases=[ServiceMetricDetailsProps],
    name_mapping={
        "alarm_statistic": "alarmStatistic",
        "datapoints_to_alarm": "datapointsToAlarm",
        "evaluation_periods": "evaluationPeriods",
        "fault_metric_names": "faultMetricNames",
        "metric_namespace": "metricNamespace",
        "period": "period",
        "success_metric_names": "successMetricNames",
        "unit": "unit",
        "graphed_fault_statistics": "graphedFaultStatistics",
        "graphed_success_statistics": "graphedSuccessStatistics",
        "fault_alarm_threshold": "faultAlarmThreshold",
        "success_alarm_threshold": "successAlarmThreshold",
    },
)
class ServiceAvailabilityMetricDetailsProps(ServiceMetricDetailsProps):
    def __init__(
        self,
        *,
        alarm_statistic: builtins.str,
        datapoints_to_alarm: jsii.Number,
        evaluation_periods: jsii.Number,
        fault_metric_names: typing.Sequence[builtins.str],
        metric_namespace: builtins.str,
        period: _aws_cdk_ceddda9d.Duration,
        success_metric_names: typing.Sequence[builtins.str],
        unit: _aws_cdk_aws_cloudwatch_ceddda9d.Unit,
        graphed_fault_statistics: typing.Optional[typing.Sequence[builtins.str]] = None,
        graphed_success_statistics: typing.Optional[typing.Sequence[builtins.str]] = None,
        fault_alarm_threshold: jsii.Number,
        success_alarm_threshold: jsii.Number,
    ) -> None:
        '''(experimental) Props for service availability metrics.

        :param alarm_statistic: (experimental) The statistic used for alarms, for availability metrics this should be "Sum", for latency metrics it could something like "p99" or "p99.9".
        :param datapoints_to_alarm: (experimental) The number of datapoints to alarm on for latency and availability alarms.
        :param evaluation_periods: (experimental) The number of evaluation periods for latency and availabiltiy alarms.
        :param fault_metric_names: (experimental) The names of fault indicating metrics.
        :param metric_namespace: (experimental) The CloudWatch metric namespace for these metrics.
        :param period: (experimental) The period for the metrics.
        :param success_metric_names: (experimental) The names of success indicating metrics.
        :param unit: (experimental) The unit used for these metrics.
        :param graphed_fault_statistics: (experimental) The statistics for faults you want to appear on dashboards, for example, with latency metrics, you might want p50, p99, and tm99. For availability metrics this will typically just be "Sum". Default: - For availability metrics, this will be "Sum", for latency metrics it will be just "p99"
        :param graphed_success_statistics: (experimental) The statistics for successes you want to appear on dashboards, for example, with latency metrics, you might want p50, p99, and tm99. For availability metrics this will typically just be "Sum". Default: - For availability metrics, this will be "Sum", for latency metrics it will be just "p99"
        :param fault_alarm_threshold: (experimental) The threshold for alarms associated with availability fault metrics, for example if measuring fault rate, the threshold may be 1, meaning you would want an alarm that triggers if the fault rate goes above 1%.
        :param success_alarm_threshold: (experimental) The threshold for alarms associated with availability success metrics, for example if measuring success rate, the threshold may be 99, meaning you would want an alarm that triggers if success drops below 99%.

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__edeeb4ba8bbf8766e8e506e6b85e0ec5a5da470f73258dfb90846d6e9ff343a8)
            check_type(argname="argument alarm_statistic", value=alarm_statistic, expected_type=type_hints["alarm_statistic"])
            check_type(argname="argument datapoints_to_alarm", value=datapoints_to_alarm, expected_type=type_hints["datapoints_to_alarm"])
            check_type(argname="argument evaluation_periods", value=evaluation_periods, expected_type=type_hints["evaluation_periods"])
            check_type(argname="argument fault_metric_names", value=fault_metric_names, expected_type=type_hints["fault_metric_names"])
            check_type(argname="argument metric_namespace", value=metric_namespace, expected_type=type_hints["metric_namespace"])
            check_type(argname="argument period", value=period, expected_type=type_hints["period"])
            check_type(argname="argument success_metric_names", value=success_metric_names, expected_type=type_hints["success_metric_names"])
            check_type(argname="argument unit", value=unit, expected_type=type_hints["unit"])
            check_type(argname="argument graphed_fault_statistics", value=graphed_fault_statistics, expected_type=type_hints["graphed_fault_statistics"])
            check_type(argname="argument graphed_success_statistics", value=graphed_success_statistics, expected_type=type_hints["graphed_success_statistics"])
            check_type(argname="argument fault_alarm_threshold", value=fault_alarm_threshold, expected_type=type_hints["fault_alarm_threshold"])
            check_type(argname="argument success_alarm_threshold", value=success_alarm_threshold, expected_type=type_hints["success_alarm_threshold"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "alarm_statistic": alarm_statistic,
            "datapoints_to_alarm": datapoints_to_alarm,
            "evaluation_periods": evaluation_periods,
            "fault_metric_names": fault_metric_names,
            "metric_namespace": metric_namespace,
            "period": period,
            "success_metric_names": success_metric_names,
            "unit": unit,
            "fault_alarm_threshold": fault_alarm_threshold,
            "success_alarm_threshold": success_alarm_threshold,
        }
        if graphed_fault_statistics is not None:
            self._values["graphed_fault_statistics"] = graphed_fault_statistics
        if graphed_success_statistics is not None:
            self._values["graphed_success_statistics"] = graphed_success_statistics

    @builtins.property
    def alarm_statistic(self) -> builtins.str:
        '''(experimental) The statistic used for alarms, for availability metrics this should be "Sum", for latency metrics it could something like "p99" or "p99.9".

        :stability: experimental
        '''
        result = self._values.get("alarm_statistic")
        assert result is not None, "Required property 'alarm_statistic' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def datapoints_to_alarm(self) -> jsii.Number:
        '''(experimental) The number of datapoints to alarm on for latency and availability alarms.

        :stability: experimental
        '''
        result = self._values.get("datapoints_to_alarm")
        assert result is not None, "Required property 'datapoints_to_alarm' is missing"
        return typing.cast(jsii.Number, result)

    @builtins.property
    def evaluation_periods(self) -> jsii.Number:
        '''(experimental) The number of evaluation periods for latency and availabiltiy alarms.

        :stability: experimental
        '''
        result = self._values.get("evaluation_periods")
        assert result is not None, "Required property 'evaluation_periods' is missing"
        return typing.cast(jsii.Number, result)

    @builtins.property
    def fault_metric_names(self) -> typing.List[builtins.str]:
        '''(experimental) The names of fault indicating metrics.

        :stability: experimental
        '''
        result = self._values.get("fault_metric_names")
        assert result is not None, "Required property 'fault_metric_names' is missing"
        return typing.cast(typing.List[builtins.str], result)

    @builtins.property
    def metric_namespace(self) -> builtins.str:
        '''(experimental) The CloudWatch metric namespace for these metrics.

        :stability: experimental
        '''
        result = self._values.get("metric_namespace")
        assert result is not None, "Required property 'metric_namespace' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def period(self) -> _aws_cdk_ceddda9d.Duration:
        '''(experimental) The period for the metrics.

        :stability: experimental
        '''
        result = self._values.get("period")
        assert result is not None, "Required property 'period' is missing"
        return typing.cast(_aws_cdk_ceddda9d.Duration, result)

    @builtins.property
    def success_metric_names(self) -> typing.List[builtins.str]:
        '''(experimental) The names of success indicating metrics.

        :stability: experimental
        '''
        result = self._values.get("success_metric_names")
        assert result is not None, "Required property 'success_metric_names' is missing"
        return typing.cast(typing.List[builtins.str], result)

    @builtins.property
    def unit(self) -> _aws_cdk_aws_cloudwatch_ceddda9d.Unit:
        '''(experimental) The unit used for these metrics.

        :stability: experimental
        '''
        result = self._values.get("unit")
        assert result is not None, "Required property 'unit' is missing"
        return typing.cast(_aws_cdk_aws_cloudwatch_ceddda9d.Unit, result)

    @builtins.property
    def graphed_fault_statistics(self) -> typing.Optional[typing.List[builtins.str]]:
        '''(experimental) The statistics for faults you want to appear on dashboards, for example, with latency metrics, you might want p50, p99, and tm99.

        For availability
        metrics this will typically just be "Sum".

        :default: - For availability metrics, this will be "Sum", for latency metrics it will be just "p99"

        :stability: experimental
        '''
        result = self._values.get("graphed_fault_statistics")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def graphed_success_statistics(self) -> typing.Optional[typing.List[builtins.str]]:
        '''(experimental) The statistics for successes you want to appear on dashboards, for example, with latency metrics, you might want p50, p99, and tm99.

        For availability
        metrics this will typically just be "Sum".

        :default: - For availability metrics, this will be "Sum", for latency metrics it will be just "p99"

        :stability: experimental
        '''
        result = self._values.get("graphed_success_statistics")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def fault_alarm_threshold(self) -> jsii.Number:
        '''(experimental) The threshold for alarms associated with availability fault metrics, for example if measuring fault rate, the threshold may be 1, meaning you would want an alarm that triggers if the fault rate goes above 1%.

        :stability: experimental
        '''
        result = self._values.get("fault_alarm_threshold")
        assert result is not None, "Required property 'fault_alarm_threshold' is missing"
        return typing.cast(jsii.Number, result)

    @builtins.property
    def success_alarm_threshold(self) -> jsii.Number:
        '''(experimental) The threshold for alarms associated with availability success metrics, for example if measuring success rate, the threshold may be 99, meaning you would want an alarm that triggers if success drops below 99%.

        :stability: experimental
        '''
        result = self._values.get("success_alarm_threshold")
        assert result is not None, "Required property 'success_alarm_threshold' is missing"
        return typing.cast(jsii.Number, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ServiceAvailabilityMetricDetailsProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.implements(IServiceLatencyMetricDetails)
class ServiceLatencyMetricDetails(
    ServiceMetricDetails,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdklabs/multi-az-observability.ServiceLatencyMetricDetails",
):
    '''(experimental) Default latency metric details for a service.

    :stability: experimental
    '''

    def __init__(
        self,
        *,
        success_alarm_threshold: _aws_cdk_ceddda9d.Duration,
        alarm_statistic: builtins.str,
        datapoints_to_alarm: jsii.Number,
        evaluation_periods: jsii.Number,
        fault_metric_names: typing.Sequence[builtins.str],
        metric_namespace: builtins.str,
        period: _aws_cdk_ceddda9d.Duration,
        success_metric_names: typing.Sequence[builtins.str],
        unit: _aws_cdk_aws_cloudwatch_ceddda9d.Unit,
        graphed_fault_statistics: typing.Optional[typing.Sequence[builtins.str]] = None,
        graphed_success_statistics: typing.Optional[typing.Sequence[builtins.str]] = None,
    ) -> None:
        '''
        :param success_alarm_threshold: (experimental) The threshold for alarms associated with latency success metrics, for example if success latency exceeds 500 milliseconds.
        :param alarm_statistic: (experimental) The statistic used for alarms, for availability metrics this should be "Sum", for latency metrics it could something like "p99" or "p99.9".
        :param datapoints_to_alarm: (experimental) The number of datapoints to alarm on for latency and availability alarms.
        :param evaluation_periods: (experimental) The number of evaluation periods for latency and availabiltiy alarms.
        :param fault_metric_names: (experimental) The names of fault indicating metrics.
        :param metric_namespace: (experimental) The CloudWatch metric namespace for these metrics.
        :param period: (experimental) The period for the metrics.
        :param success_metric_names: (experimental) The names of success indicating metrics.
        :param unit: (experimental) The unit used for these metrics.
        :param graphed_fault_statistics: (experimental) The statistics for faults you want to appear on dashboards, for example, with latency metrics, you might want p50, p99, and tm99. For availability metrics this will typically just be "Sum". Default: - For availability metrics, this will be "Sum", for latency metrics it will be just "p99"
        :param graphed_success_statistics: (experimental) The statistics for successes you want to appear on dashboards, for example, with latency metrics, you might want p50, p99, and tm99. For availability metrics this will typically just be "Sum". Default: - For availability metrics, this will be "Sum", for latency metrics it will be just "p99"

        :stability: experimental
        '''
        props = ServiceLatencyMetricDetailsProps(
            success_alarm_threshold=success_alarm_threshold,
            alarm_statistic=alarm_statistic,
            datapoints_to_alarm=datapoints_to_alarm,
            evaluation_periods=evaluation_periods,
            fault_metric_names=fault_metric_names,
            metric_namespace=metric_namespace,
            period=period,
            success_metric_names=success_metric_names,
            unit=unit,
            graphed_fault_statistics=graphed_fault_statistics,
            graphed_success_statistics=graphed_success_statistics,
        )

        jsii.create(self.__class__, self, [props])

    @builtins.property
    @jsii.member(jsii_name="successAlarmThreshold")
    def success_alarm_threshold(self) -> _aws_cdk_ceddda9d.Duration:
        '''(experimental) The threshold for alarms associated with latency success metrics, for example if success latency exceeds 500 milliseconds.

        :stability: experimental
        '''
        return typing.cast(_aws_cdk_ceddda9d.Duration, jsii.get(self, "successAlarmThreshold"))


@jsii.data_type(
    jsii_type="@cdklabs/multi-az-observability.ServiceLatencyMetricDetailsProps",
    jsii_struct_bases=[ServiceMetricDetailsProps],
    name_mapping={
        "alarm_statistic": "alarmStatistic",
        "datapoints_to_alarm": "datapointsToAlarm",
        "evaluation_periods": "evaluationPeriods",
        "fault_metric_names": "faultMetricNames",
        "metric_namespace": "metricNamespace",
        "period": "period",
        "success_metric_names": "successMetricNames",
        "unit": "unit",
        "graphed_fault_statistics": "graphedFaultStatistics",
        "graphed_success_statistics": "graphedSuccessStatistics",
        "success_alarm_threshold": "successAlarmThreshold",
    },
)
class ServiceLatencyMetricDetailsProps(ServiceMetricDetailsProps):
    def __init__(
        self,
        *,
        alarm_statistic: builtins.str,
        datapoints_to_alarm: jsii.Number,
        evaluation_periods: jsii.Number,
        fault_metric_names: typing.Sequence[builtins.str],
        metric_namespace: builtins.str,
        period: _aws_cdk_ceddda9d.Duration,
        success_metric_names: typing.Sequence[builtins.str],
        unit: _aws_cdk_aws_cloudwatch_ceddda9d.Unit,
        graphed_fault_statistics: typing.Optional[typing.Sequence[builtins.str]] = None,
        graphed_success_statistics: typing.Optional[typing.Sequence[builtins.str]] = None,
        success_alarm_threshold: _aws_cdk_ceddda9d.Duration,
    ) -> None:
        '''(experimental) Props for service latency metrics.

        :param alarm_statistic: (experimental) The statistic used for alarms, for availability metrics this should be "Sum", for latency metrics it could something like "p99" or "p99.9".
        :param datapoints_to_alarm: (experimental) The number of datapoints to alarm on for latency and availability alarms.
        :param evaluation_periods: (experimental) The number of evaluation periods for latency and availabiltiy alarms.
        :param fault_metric_names: (experimental) The names of fault indicating metrics.
        :param metric_namespace: (experimental) The CloudWatch metric namespace for these metrics.
        :param period: (experimental) The period for the metrics.
        :param success_metric_names: (experimental) The names of success indicating metrics.
        :param unit: (experimental) The unit used for these metrics.
        :param graphed_fault_statistics: (experimental) The statistics for faults you want to appear on dashboards, for example, with latency metrics, you might want p50, p99, and tm99. For availability metrics this will typically just be "Sum". Default: - For availability metrics, this will be "Sum", for latency metrics it will be just "p99"
        :param graphed_success_statistics: (experimental) The statistics for successes you want to appear on dashboards, for example, with latency metrics, you might want p50, p99, and tm99. For availability metrics this will typically just be "Sum". Default: - For availability metrics, this will be "Sum", for latency metrics it will be just "p99"
        :param success_alarm_threshold: (experimental) The threshold for alarms associated with latency success metrics, for example if success latency exceeds 500 milliseconds.

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__58ebd30f770ec4a7d6eeb284120e352b6c995556fd4c0fa3199c43165e854d29)
            check_type(argname="argument alarm_statistic", value=alarm_statistic, expected_type=type_hints["alarm_statistic"])
            check_type(argname="argument datapoints_to_alarm", value=datapoints_to_alarm, expected_type=type_hints["datapoints_to_alarm"])
            check_type(argname="argument evaluation_periods", value=evaluation_periods, expected_type=type_hints["evaluation_periods"])
            check_type(argname="argument fault_metric_names", value=fault_metric_names, expected_type=type_hints["fault_metric_names"])
            check_type(argname="argument metric_namespace", value=metric_namespace, expected_type=type_hints["metric_namespace"])
            check_type(argname="argument period", value=period, expected_type=type_hints["period"])
            check_type(argname="argument success_metric_names", value=success_metric_names, expected_type=type_hints["success_metric_names"])
            check_type(argname="argument unit", value=unit, expected_type=type_hints["unit"])
            check_type(argname="argument graphed_fault_statistics", value=graphed_fault_statistics, expected_type=type_hints["graphed_fault_statistics"])
            check_type(argname="argument graphed_success_statistics", value=graphed_success_statistics, expected_type=type_hints["graphed_success_statistics"])
            check_type(argname="argument success_alarm_threshold", value=success_alarm_threshold, expected_type=type_hints["success_alarm_threshold"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "alarm_statistic": alarm_statistic,
            "datapoints_to_alarm": datapoints_to_alarm,
            "evaluation_periods": evaluation_periods,
            "fault_metric_names": fault_metric_names,
            "metric_namespace": metric_namespace,
            "period": period,
            "success_metric_names": success_metric_names,
            "unit": unit,
            "success_alarm_threshold": success_alarm_threshold,
        }
        if graphed_fault_statistics is not None:
            self._values["graphed_fault_statistics"] = graphed_fault_statistics
        if graphed_success_statistics is not None:
            self._values["graphed_success_statistics"] = graphed_success_statistics

    @builtins.property
    def alarm_statistic(self) -> builtins.str:
        '''(experimental) The statistic used for alarms, for availability metrics this should be "Sum", for latency metrics it could something like "p99" or "p99.9".

        :stability: experimental
        '''
        result = self._values.get("alarm_statistic")
        assert result is not None, "Required property 'alarm_statistic' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def datapoints_to_alarm(self) -> jsii.Number:
        '''(experimental) The number of datapoints to alarm on for latency and availability alarms.

        :stability: experimental
        '''
        result = self._values.get("datapoints_to_alarm")
        assert result is not None, "Required property 'datapoints_to_alarm' is missing"
        return typing.cast(jsii.Number, result)

    @builtins.property
    def evaluation_periods(self) -> jsii.Number:
        '''(experimental) The number of evaluation periods for latency and availabiltiy alarms.

        :stability: experimental
        '''
        result = self._values.get("evaluation_periods")
        assert result is not None, "Required property 'evaluation_periods' is missing"
        return typing.cast(jsii.Number, result)

    @builtins.property
    def fault_metric_names(self) -> typing.List[builtins.str]:
        '''(experimental) The names of fault indicating metrics.

        :stability: experimental
        '''
        result = self._values.get("fault_metric_names")
        assert result is not None, "Required property 'fault_metric_names' is missing"
        return typing.cast(typing.List[builtins.str], result)

    @builtins.property
    def metric_namespace(self) -> builtins.str:
        '''(experimental) The CloudWatch metric namespace for these metrics.

        :stability: experimental
        '''
        result = self._values.get("metric_namespace")
        assert result is not None, "Required property 'metric_namespace' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def period(self) -> _aws_cdk_ceddda9d.Duration:
        '''(experimental) The period for the metrics.

        :stability: experimental
        '''
        result = self._values.get("period")
        assert result is not None, "Required property 'period' is missing"
        return typing.cast(_aws_cdk_ceddda9d.Duration, result)

    @builtins.property
    def success_metric_names(self) -> typing.List[builtins.str]:
        '''(experimental) The names of success indicating metrics.

        :stability: experimental
        '''
        result = self._values.get("success_metric_names")
        assert result is not None, "Required property 'success_metric_names' is missing"
        return typing.cast(typing.List[builtins.str], result)

    @builtins.property
    def unit(self) -> _aws_cdk_aws_cloudwatch_ceddda9d.Unit:
        '''(experimental) The unit used for these metrics.

        :stability: experimental
        '''
        result = self._values.get("unit")
        assert result is not None, "Required property 'unit' is missing"
        return typing.cast(_aws_cdk_aws_cloudwatch_ceddda9d.Unit, result)

    @builtins.property
    def graphed_fault_statistics(self) -> typing.Optional[typing.List[builtins.str]]:
        '''(experimental) The statistics for faults you want to appear on dashboards, for example, with latency metrics, you might want p50, p99, and tm99.

        For availability
        metrics this will typically just be "Sum".

        :default: - For availability metrics, this will be "Sum", for latency metrics it will be just "p99"

        :stability: experimental
        '''
        result = self._values.get("graphed_fault_statistics")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def graphed_success_statistics(self) -> typing.Optional[typing.List[builtins.str]]:
        '''(experimental) The statistics for successes you want to appear on dashboards, for example, with latency metrics, you might want p50, p99, and tm99.

        For availability
        metrics this will typically just be "Sum".

        :default: - For availability metrics, this will be "Sum", for latency metrics it will be just "p99"

        :stability: experimental
        '''
        result = self._values.get("graphed_success_statistics")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def success_alarm_threshold(self) -> _aws_cdk_ceddda9d.Duration:
        '''(experimental) The threshold for alarms associated with latency success metrics, for example if success latency exceeds 500 milliseconds.

        :stability: experimental
        '''
        result = self._values.get("success_alarm_threshold")
        assert result is not None, "Required property 'success_alarm_threshold' is missing"
        return typing.cast(_aws_cdk_ceddda9d.Duration, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ServiceLatencyMetricDetailsProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class CanaryTestAvailabilityMetricsOverride(
    CanaryTestMetricsOverride,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdklabs/multi-az-observability.CanaryTestAvailabilityMetricsOverride",
):
    '''(experimental) Provides overrides for the default metric settings used for the automatically created canary tests.

    :stability: experimental
    '''

    def __init__(
        self,
        *,
        fault_alarm_threshold: typing.Optional[jsii.Number] = None,
        success_alarm_threshold: typing.Optional[jsii.Number] = None,
        alarm_statistic: typing.Optional[builtins.str] = None,
        datapoints_to_alarm: typing.Optional[jsii.Number] = None,
        evaluation_periods: typing.Optional[jsii.Number] = None,
        period: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
    ) -> None:
        '''
        :param fault_alarm_threshold: (experimental) The threshold for alarms associated with fault metrics, for example if measuring fault rate, the threshold may be 1, meaning you would want an alarm that triggers if the fault rate goes above 1%. Default: - This property will use the default defined for the service
        :param success_alarm_threshold: (experimental) The threshold for alarms associated with success metrics, for example if measuring success rate, the threshold may be 99, meaning you would want an alarm that triggers if success drops below 99%. Default: - This property will use the default defined for the service
        :param alarm_statistic: (experimental) The statistic used for alarms, for availability metrics this should be "Sum", for latency metrics it could something like "p99" or "p99.9". Default: - This property will use the default defined for the service
        :param datapoints_to_alarm: (experimental) The number of datapoints to alarm on for latency and availability alarms. Default: - This property will use the default defined for the service
        :param evaluation_periods: (experimental) The number of evaluation periods for latency and availabiltiy alarms. Default: - This property will use the default defined for the service
        :param period: (experimental) The period for the metrics. Default: - This property will use the default defined for the service

        :stability: experimental
        '''
        props = CanaryTestAvailabilityMetricsOverrideProps(
            fault_alarm_threshold=fault_alarm_threshold,
            success_alarm_threshold=success_alarm_threshold,
            alarm_statistic=alarm_statistic,
            datapoints_to_alarm=datapoints_to_alarm,
            evaluation_periods=evaluation_periods,
            period=period,
        )

        jsii.create(self.__class__, self, [props])

    @builtins.property
    @jsii.member(jsii_name="faultAlarmThreshold")
    def fault_alarm_threshold(self) -> typing.Optional[jsii.Number]:
        '''(experimental) The threshold for alarms associated with availability fault metrics, for example if measuring fault rate, the threshold may be 1, meaning you would want an alarm that triggers if the fault rate goes above 1%.

        :stability: experimental
        '''
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "faultAlarmThreshold"))

    @builtins.property
    @jsii.member(jsii_name="successAlarmThreshold")
    def success_alarm_threshold(self) -> typing.Optional[jsii.Number]:
        '''(experimental) The threshold for alarms associated with availability success metrics, for example if measuring success rate, the threshold may be 99, meaning you would want an alarm that triggers if success drops below 99%.

        :stability: experimental
        '''
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "successAlarmThreshold"))


class CanaryTestLatencyMetricsOverride(
    CanaryTestMetricsOverride,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdklabs/multi-az-observability.CanaryTestLatencyMetricsOverride",
):
    '''(experimental) Provides overrides for the default metric settings used for the automatically created canary tests.

    :stability: experimental
    '''

    def __init__(
        self,
        *,
        success_alarm_threshold: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
        alarm_statistic: typing.Optional[builtins.str] = None,
        datapoints_to_alarm: typing.Optional[jsii.Number] = None,
        evaluation_periods: typing.Optional[jsii.Number] = None,
        period: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
    ) -> None:
        '''
        :param success_alarm_threshold: (experimental) The threshold for alarms associated with latency success metrics, for example if success latency exceeds 500 milliseconds. Default: - This property will use the default defined for the service
        :param alarm_statistic: (experimental) The statistic used for alarms, for availability metrics this should be "Sum", for latency metrics it could something like "p99" or "p99.9". Default: - This property will use the default defined for the service
        :param datapoints_to_alarm: (experimental) The number of datapoints to alarm on for latency and availability alarms. Default: - This property will use the default defined for the service
        :param evaluation_periods: (experimental) The number of evaluation periods for latency and availabiltiy alarms. Default: - This property will use the default defined for the service
        :param period: (experimental) The period for the metrics. Default: - This property will use the default defined for the service

        :stability: experimental
        '''
        props = CanaryTestLatencyMetricsOverrideProps(
            success_alarm_threshold=success_alarm_threshold,
            alarm_statistic=alarm_statistic,
            datapoints_to_alarm=datapoints_to_alarm,
            evaluation_periods=evaluation_periods,
            period=period,
        )

        jsii.create(self.__class__, self, [props])

    @builtins.property
    @jsii.member(jsii_name="successAlarmThreshold")
    def success_alarm_threshold(self) -> typing.Optional[_aws_cdk_ceddda9d.Duration]:
        '''(experimental) The threshold for alarms associated with latency success metrics, for example if success latency exceeds 500 milliseconds.

        :stability: experimental
        '''
        return typing.cast(typing.Optional[_aws_cdk_ceddda9d.Duration], jsii.get(self, "successAlarmThreshold"))


__all__ = [
    "AddCanaryTestProps",
    "AlbTargetGroupMap",
    "ApplicationLoadBalancerAvailabilityOutlierAlgorithm",
    "ApplicationLoadBalancerDetectionProps",
    "ApplicationLoadBalancerLatencyOutlierAlgorithm",
    "AvailabilityZoneMapper",
    "AvailabilityZoneMapperProps",
    "BasicServiceMultiAZObservability",
    "BasicServiceMultiAZObservabilityProps",
    "CanaryMetricProps",
    "CanaryMetrics",
    "CanaryTestAvailabilityMetricsOverride",
    "CanaryTestAvailabilityMetricsOverrideProps",
    "CanaryTestLatencyMetricsOverride",
    "CanaryTestLatencyMetricsOverrideProps",
    "CanaryTestMetricsOverride",
    "CanaryTestMetricsOverrideProps",
    "ContributorInsightRuleDetails",
    "ContributorInsightRuleDetailsProps",
    "IAvailabilityZoneMapper",
    "IBaseOperationRegionalAlarmsAndRules",
    "IBaseOperationZonalAlarmsAndRules",
    "IBasicServiceMultiAZObservability",
    "ICanaryMetrics",
    "ICanaryOperationRegionalAlarmsAndRules",
    "ICanaryOperationZonalAlarmsAndRules",
    "ICanaryTestAvailabilityMetricsOverride",
    "ICanaryTestLatencyMetricsOverride",
    "ICanaryTestMetricsOverride",
    "IContributorInsightRuleDetails",
    "IInstrumentedServiceMultiAZObservability",
    "IOperation",
    "IOperationAlarmsAndRules",
    "IOperationAvailabilityMetricDetails",
    "IOperationLatencyMetricDetails",
    "IOperationMetricDetails",
    "IServerSideOperationRegionalAlarmsAndRules",
    "IServerSideOperationZonalAlarmsAndRules",
    "IService",
    "IServiceAlarmsAndRules",
    "IServiceAvailabilityMetricDetails",
    "IServiceLatencyMetricDetails",
    "IServiceMetricDetails",
    "InstrumentedServiceMultiAZObservability",
    "InstrumentedServiceMultiAZObservabilityProps",
    "LatencyOutlierMetricAggregation",
    "MetricDimensions",
    "MinimumUnhealthyTargets",
    "NatGatewayDetectionProps",
    "NetworkConfigurationProps",
    "Operation",
    "OperationAvailabilityMetricDetails",
    "OperationAvailabilityMetricDetailsProps",
    "OperationLatencyMetricDetails",
    "OperationLatencyMetricDetailsProps",
    "OperationMetricDetails",
    "OperationMetricDetailsProps",
    "OperationProps",
    "OutlierDetectionAlgorithm",
    "PacketLossOutlierAlgorithm",
    "Service",
    "ServiceAvailabilityMetricDetails",
    "ServiceAvailabilityMetricDetailsProps",
    "ServiceLatencyMetricDetails",
    "ServiceLatencyMetricDetailsProps",
    "ServiceMetricDetails",
    "ServiceMetricDetailsProps",
    "ServiceProps",
]

publication.publish()

def _typecheckingstub__bf7e5362f1ef3a0356b1522d870175b4a00fdf064367124f0e428e97b327a615(
    *,
    load_balancer: _aws_cdk_aws_elasticloadbalancingv2_ceddda9d.ILoadBalancerV2,
    request_count: jsii.Number,
    schedule: builtins.str,
    headers: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
    http_methods: typing.Optional[typing.Sequence[builtins.str]] = None,
    ignore_tls_errors: typing.Optional[builtins.bool] = None,
    network_configuration: typing.Optional[typing.Union[NetworkConfigurationProps, typing.Dict[builtins.str, typing.Any]]] = None,
    post_data: typing.Optional[builtins.str] = None,
    regional_request_count: typing.Optional[jsii.Number] = None,
    timeout: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1c82768e8378134f3b690a00f3e494e9e4e09034637d03093bba5aab2f56095e(
    *,
    application_load_balancer: _aws_cdk_aws_elasticloadbalancingv2_ceddda9d.IApplicationLoadBalancer,
    target_groups: typing.Optional[typing.Sequence[_aws_cdk_aws_elasticloadbalancingv2_ceddda9d.ITargetGroup]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a93214bdf1fa4f67b237e7c4dcee5992506d690b196458bab06cd4a8e25eee03(
    *,
    alb_target_group_map: typing.Sequence[typing.Union[AlbTargetGroupMap, typing.Dict[builtins.str, typing.Any]]],
    fault_count_percent_threshold: jsii.Number,
    latency_statistic: builtins.str,
    latency_threshold: _aws_cdk_ceddda9d.Duration,
    availability_outlier_algorithm: typing.Optional[ApplicationLoadBalancerAvailabilityOutlierAlgorithm] = None,
    availability_outlier_threshold: typing.Optional[jsii.Number] = None,
    latency_outlier_algorithm: typing.Optional[ApplicationLoadBalancerLatencyOutlierAlgorithm] = None,
    latency_outlier_threshold: typing.Optional[jsii.Number] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ad282df04042aad52125b287dc88af7a6decbd51da905d665c2df5a7ae36a858(
    *,
    availability_zone_names: typing.Optional[typing.Sequence[builtins.str]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__15fe53f0a5b438d27e745fab2f0c65f95e2f6f1d3d09af30af5c2f7f34fc3333(
    *,
    datapoints_to_alarm: jsii.Number,
    evaluation_periods: jsii.Number,
    service_name: builtins.str,
    application_load_balancer_props: typing.Optional[typing.Union[ApplicationLoadBalancerDetectionProps, typing.Dict[builtins.str, typing.Any]]] = None,
    assets_bucket_parameter_name: typing.Optional[builtins.str] = None,
    assets_bucket_prefix_parameter_name: typing.Optional[builtins.str] = None,
    create_dashboard: typing.Optional[builtins.bool] = None,
    interval: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
    nat_gateway_props: typing.Optional[typing.Union[NatGatewayDetectionProps, typing.Dict[builtins.str, typing.Any]]] = None,
    period: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__edbe0cdfc777c1880327eb370e72788956edc4a92cd2a9ce3793a8ce03d372e3(
    *,
    canary_availability_metric_details: IOperationAvailabilityMetricDetails,
    canary_latency_metric_details: IOperationLatencyMetricDetails,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2e332d50e6cba3afaf9d92838759b5d3b619a9c2e8dcdef241b213cde461880c(
    *,
    alarm_statistic: typing.Optional[builtins.str] = None,
    datapoints_to_alarm: typing.Optional[jsii.Number] = None,
    evaluation_periods: typing.Optional[jsii.Number] = None,
    period: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c8ade43837bde272fae8e0a6676477846373fc1bb25c3d716ae04eab9da138d9(
    *,
    availability_zone_id_json_path: builtins.str,
    fault_metric_json_path: builtins.str,
    instance_id_json_path: builtins.str,
    log_groups: typing.Sequence[_aws_cdk_aws_logs_ceddda9d.ILogGroup],
    operation_name_json_path: builtins.str,
    success_latency_metric_json_path: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f47430da8c1b9b48d48e5251cab2dae3962dee681f0b90504d563fbc491c9e67(
    value: _aws_cdk_aws_lambda_ceddda9d.IFunction,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__389da457c25cddefd5704d4a7f76218a8fe049f65f0ca3834af16d010e8d19b5(
    value: _aws_cdk_aws_logs_ceddda9d.ILogGroup,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0029138db755bb79aed43f624548124b5569bf7edbbeb9900ffd1dfe0d717307(
    value: _aws_cdk_ceddda9d.CustomResource,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6087eb1a38695a37e37bb3ca859f7b1fc4a492230be646c5134e60435e309c78(
    availability_zone_name: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__413eeebcfa1b3ba0eb35bdb273cf11a8c50b498b97355794c9669484db03fc91(
    letter: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__21f092b9672a220828785aa3c9c3b7b73dce34c057d2d65eeba5296612dadce4(
    availability_zone_names: typing.Sequence[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b9f2a2a111a8085b509d0ca8a9a17177229c1f48c38a1a794c99b52592550810(
    availability_zone_names: typing.Sequence[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5afd920de43091152fe723627d9cebc610c78bce3297e2dfb179fa98803cbbc0(
    availability_zone_id: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e05be40a82825eb9c32d0866f995ce2b4cd2edf02d26ad94ebf5999f9cb147b5(
    value: _aws_cdk_aws_cloudwatch_ceddda9d.IAlarm,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__24d5ace50e39c0a1c69b63ba511459bc45bc095145599e24e770f270c40ae562(
    value: _aws_cdk_aws_cloudwatch_ceddda9d.IAlarm,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__14a910f298c35c3322a0161508009900213ab115071a4bed6ce58e442411261c(
    value: _aws_cdk_aws_cloudwatch_ceddda9d.IAlarm,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6a92a17530fd7be2abc75031830d6800bf33402fef23fe2dac9fb85b007c9172(
    value: _aws_cdk_aws_cloudwatch_ceddda9d.IAlarm,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5ae1b64507c6dfd2c11eb88c657a29bd04b6352911706669e4d867484c5470d7(
    value: _aws_cdk_aws_cloudwatch_ceddda9d.IAlarm,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7eedac5c883637549b879a716b78731d3fbee047a0725dd575a17b58be872dbb(
    value: _aws_cdk_aws_cloudwatch_ceddda9d.IAlarm,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__42cfd81e8009b1f9a1c79c3cddd666296f6bc2404e83f6ce251c0f6de5d6d0a9(
    value: _aws_cdk_aws_cloudwatch_ceddda9d.IAlarm,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__41292a6738a299b0ca8af3a281416324fbf5033e0cf464d6e9ff2a2c726eac6a(
    value: typing.Mapping[builtins.str, _aws_cdk_aws_cloudwatch_ceddda9d.IAlarm],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f998baa4ed92b2833d645407a865db8211d731915e2ca6e12d6285228b42ba35(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__07c61148effad607221bb5da499d3f55322a58946976b9c63de59dd4f1ab0712(
    value: typing.Optional[typing.Mapping[builtins.str, _aws_cdk_aws_cloudwatch_ceddda9d.IAlarm]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0b22969ea384a27c5200ceae28c1f02c3bb680e5fcb566cd00d4c12d9cd5feed(
    value: typing.Optional[typing.List[_aws_cdk_aws_elasticloadbalancingv2_ceddda9d.IApplicationLoadBalancer]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8ee207809f5cbdb57d53c0cf6b46801ab28117e86e8644052c9277aebdee8860(
    value: typing.Optional[_aws_cdk_aws_cloudwatch_ceddda9d.Dashboard],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e653e78b064972b23197009e2c4e265c5bc6e983abab5029013f2c8b9f62ad42(
    value: typing.Optional[typing.Mapping[builtins.str, typing.List[_aws_cdk_aws_ec2_ceddda9d.CfnNatGateway]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a6aca38ba20e1b6c03131b7d324928febc6618b62c5bee38f28f334430ac4a05(
    value: typing.Optional[typing.Mapping[builtins.str, _aws_cdk_aws_cloudwatch_ceddda9d.IAlarm]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d88172cfcb0d0284117e3f0e5b5b04255860769c713a92be3392791c22faa5ea(
    value: _aws_cdk_aws_cloudwatch_ceddda9d.IAlarm,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f3731e5254b7ee08eb4786a65612c2a604de368a146e9e2bdbb5bf339a2c1b71(
    value: typing.Optional[_aws_cdk_aws_cloudwatch_ceddda9d.CfnInsightRule],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b29a1c24e783c9691ec1cb2f40b5f1a99b4d4870af674effec237e9477ce5bf8(
    value: typing.Optional[_aws_cdk_aws_cloudwatch_ceddda9d.CfnInsightRule],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__cda6f011758bcaa01bb1134e2bfb4b7093bfa3971462539d142fdba80745fe91(
    value: _aws_cdk_aws_cloudwatch_ceddda9d.IAlarm,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c22e757753f2980033d3ee81d4db89564cf7262bb7d7ac8894aa77ba67846722(
    value: typing.Optional[_aws_cdk_aws_cloudwatch_ceddda9d.CfnInsightRule],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__80613ae1711b8221870139d7b53d22fe4fc2e22fee224ce46e866eeee886cbf3(
    value: typing.Optional[_aws_cdk_aws_cloudwatch_ceddda9d.CfnInsightRule],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b86f9612bc48c2143188d89622279986e81017cbae19e0f1e20269628149a7a6(
    value: typing.Optional[_aws_cdk_aws_cloudwatch_ceddda9d.CfnInsightRule],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8753f6cccdf05b3bf34463787a7285ccc148cc5e2cfc023e6f5b3a2033d189c2(
    value: typing.Optional[_aws_cdk_aws_cloudwatch_ceddda9d.IAlarm],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1060beb3750b5928b5aa1d6014d9bf5c99f477f1f89b23ed16537542e068b922(
    value: typing.Optional[_aws_cdk_aws_cloudwatch_ceddda9d.IAlarm],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__afd14cd0917991cc6cb77ab7f5cd990568300cab8c21fa589a02ec956952541f(
    operation: IOperation,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a8f0455f87797305bc755c3271060c1f7023ae24d8e8a0ef14ddb7b93494485b(
    value: _aws_cdk_aws_cloudwatch_ceddda9d.IAlarm,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2070a9428cac03ff47244b1cdc0c9cb54d838c613793a11bc4a4572b4ab14794(
    value: _aws_cdk_aws_cloudwatch_ceddda9d.IAlarm,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5c6785f0b57be0aee34f5f853c036254ca14de1654825c78f261ac607baf9f68(
    value: IService,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__83447c8c7ae17fdd5ac2ee70d95fa8012186163553c15c3ff75fbd157e08c4cf(
    value: _aws_cdk_aws_cloudwatch_ceddda9d.IAlarm,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__88bd2ac9b9df963771c7db9b780890e46e9f7641052e0b975b66d4ce023829af(
    value: typing.Mapping[builtins.str, _aws_cdk_aws_cloudwatch_ceddda9d.IAlarm],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c4e4294e497d1a1bbb3c47bb3d6cffa4eee8406b856968fe2348586f2b19bd5f(
    value: typing.Mapping[builtins.str, _aws_cdk_aws_cloudwatch_ceddda9d.IAlarm],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__83f2ac0c7884f1760a3da6cd1bcfc505287df81e5b92e464ae735a748b7cc1c8(
    value: typing.Optional[_aws_cdk_aws_cloudwatch_ceddda9d.IAlarm],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__78520ac471f9b9792f6e88a24fe852bdde2ad70bb4d1636d8b022de412343fdc(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    service: IService,
    assets_bucket_parameter_name: typing.Optional[builtins.str] = None,
    assets_bucket_prefix_parameter_name: typing.Optional[builtins.str] = None,
    availability_outlier_detection_algorithm: typing.Optional[OutlierDetectionAlgorithm] = None,
    availability_outlier_threshold: typing.Optional[jsii.Number] = None,
    create_dashboards: typing.Optional[builtins.bool] = None,
    interval: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
    latency_outlier_detection_algorithm: typing.Optional[OutlierDetectionAlgorithm] = None,
    latency_outlier_metric_aggregation: typing.Optional[LatencyOutlierMetricAggregation] = None,
    latency_outlier_threshold: typing.Optional[jsii.Number] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__102051515d19b7efde161728b5c392ba25f80ba0513d70df8ce3bdebba803655(
    *,
    service: IService,
    assets_bucket_parameter_name: typing.Optional[builtins.str] = None,
    assets_bucket_prefix_parameter_name: typing.Optional[builtins.str] = None,
    availability_outlier_detection_algorithm: typing.Optional[OutlierDetectionAlgorithm] = None,
    availability_outlier_threshold: typing.Optional[jsii.Number] = None,
    create_dashboards: typing.Optional[builtins.bool] = None,
    interval: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
    latency_outlier_detection_algorithm: typing.Optional[OutlierDetectionAlgorithm] = None,
    latency_outlier_metric_aggregation: typing.Optional[LatencyOutlierMetricAggregation] = None,
    latency_outlier_threshold: typing.Optional[jsii.Number] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__bd7b3882b73626eaa6b3b06fcbebe18c8bf307877c05b85e85abb78412d306ce(
    static_dimensions: typing.Mapping[builtins.str, builtins.str],
    availability_zone_id_key: builtins.str,
    region_key: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6c477603807c11fe9f762a28cbadbca8e687bb558fb6741ae91ee87ccb17a4b4(
    region: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__35f1a092f9c0d7e57ff0f8a6cf760d1c5b80d37efb34621151454b4da865c3e6(
    availability_zone_id: builtins.str,
    region: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__efa8f1730b98ea1dd1da14300d6e91b137e5e8e9db7af446fa1cf00c69c322c2(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ca4cfd20f3782e7ec6430b1c3d943d15eece045928388fcf7e3c3c8ea2e7248b(
    value: typing.Mapping[builtins.str, builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__39c910d076892eb126ef774ed69b3d8b582d9980d910ee784c923f4284583b9f(
    value: typing.Optional[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c006afbf726eab97f48b4f4bef13d8d5072727a47d4387daebd2a545cf7848ce(
    *,
    count: typing.Optional[jsii.Number] = None,
    percentage: typing.Optional[jsii.Number] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f2f991a5d8adc37a9d77adea91bbe71bd945c7bed07e41d7890230ee8d1dee4b(
    *,
    nat_gateways: typing.Mapping[builtins.str, typing.Sequence[_aws_cdk_aws_ec2_ceddda9d.CfnNatGateway]],
    packet_loss_outlier_algorithm: typing.Optional[PacketLossOutlierAlgorithm] = None,
    packet_loss_outlier_threshold: typing.Optional[jsii.Number] = None,
    packet_loss_percent_threshold: typing.Optional[jsii.Number] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2254e297551a7952836a56c7b1852e846ada986e2dbcb5f68b941d2043fc13c0(
    *,
    subnet_selection: typing.Union[_aws_cdk_aws_ec2_ceddda9d.SubnetSelection, typing.Dict[builtins.str, typing.Any]],
    vpc: _aws_cdk_aws_ec2_ceddda9d.IVpc,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__19a022b187025b0dfb90bfc09b2588a136424989f7af6d6d7c8ee11cb7822d6b(
    props: typing.Union[OperationMetricDetailsProps, typing.Dict[builtins.str, typing.Any]],
    default_props: IServiceMetricDetails,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__df81185b60a72d1681cbab65087b8dcadf4c04fe83ae02f1ebdc511a8d73efec(
    *,
    metric_dimensions: MetricDimensions,
    operation_name: builtins.str,
    alarm_statistic: typing.Optional[builtins.str] = None,
    datapoints_to_alarm: typing.Optional[jsii.Number] = None,
    evaluation_periods: typing.Optional[jsii.Number] = None,
    fault_metric_names: typing.Optional[typing.Sequence[builtins.str]] = None,
    graphed_fault_statistics: typing.Optional[typing.Sequence[builtins.str]] = None,
    graphed_success_statistics: typing.Optional[typing.Sequence[builtins.str]] = None,
    metric_namespace: typing.Optional[builtins.str] = None,
    period: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
    success_metric_names: typing.Optional[typing.Sequence[builtins.str]] = None,
    unit: typing.Optional[_aws_cdk_aws_cloudwatch_ceddda9d.Unit] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__fa32274a3568fa84c18fd791770b5897b827a856ccdabe92b6ea778dc52a7894(
    *,
    critical: builtins.bool,
    http_methods: typing.Sequence[builtins.str],
    operation_name: builtins.str,
    path: builtins.str,
    server_side_availability_metric_details: IOperationAvailabilityMetricDetails,
    server_side_latency_metric_details: IOperationLatencyMetricDetails,
    service: IService,
    canary_metric_details: typing.Optional[ICanaryMetrics] = None,
    canary_test_availability_metrics_override: typing.Optional[ICanaryTestMetricsOverride] = None,
    canary_test_latency_metrics_override: typing.Optional[ICanaryTestMetricsOverride] = None,
    canary_test_props: typing.Optional[typing.Union[AddCanaryTestProps, typing.Dict[builtins.str, typing.Any]]] = None,
    opt_out_of_service_created_canary: typing.Optional[builtins.bool] = None,
    server_side_contributor_insight_rule_details: typing.Optional[IContributorInsightRuleDetails] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__86ab5febd81bff1f2ae714b61e47a7bc785fb9d9a10d745f05674ab2153b5d3a(
    operation: IOperation,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__071b784429d2d3b09d3261502831f299d64879994d3c59a0c43c2ba33adae288(
    *,
    alarm_statistic: builtins.str,
    datapoints_to_alarm: jsii.Number,
    evaluation_periods: jsii.Number,
    fault_metric_names: typing.Sequence[builtins.str],
    metric_namespace: builtins.str,
    period: _aws_cdk_ceddda9d.Duration,
    success_metric_names: typing.Sequence[builtins.str],
    unit: _aws_cdk_aws_cloudwatch_ceddda9d.Unit,
    graphed_fault_statistics: typing.Optional[typing.Sequence[builtins.str]] = None,
    graphed_success_statistics: typing.Optional[typing.Sequence[builtins.str]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__58a30aef490fedfe7ce4413cbf8e0a1aacabbe85251e0c0e292ab462ff466ccf(
    *,
    availability_zone_names: typing.Sequence[builtins.str],
    base_url: builtins.str,
    default_availability_metric_details: IServiceAvailabilityMetricDetails,
    default_latency_metric_details: IServiceLatencyMetricDetails,
    fault_count_threshold: jsii.Number,
    period: _aws_cdk_ceddda9d.Duration,
    service_name: builtins.str,
    canary_test_props: typing.Optional[typing.Union[AddCanaryTestProps, typing.Dict[builtins.str, typing.Any]]] = None,
    default_contributor_insight_rule_details: typing.Optional[IContributorInsightRuleDetails] = None,
    load_balancer: typing.Optional[_aws_cdk_aws_elasticloadbalancingv2_ceddda9d.ILoadBalancerV2] = None,
    minimum_unhealthy_targets: typing.Optional[typing.Union[MinimumUnhealthyTargets, typing.Dict[builtins.str, typing.Any]]] = None,
    target_groups: typing.Optional[typing.Sequence[_aws_cdk_aws_elasticloadbalancingv2_ceddda9d.ITargetGroup]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f533f3a490e063cdfef872dde16a1c3bed970e880d7ed597f16c665f83caacba(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    availability_zone_names: typing.Optional[typing.Sequence[builtins.str]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__013cb7b661a38c5e9e58c44fe2a47e74d9bd5db974b190326cb12941c4203e52(
    availability_zone_name: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d66625a70b2c57ad713d9f368830723593c9e37af5ce27d5ec0b0d7acd2a499f(
    letter: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__89b736f1d9f4010fb29f411199f74eab2bde27a769908da4ee24ced1683acc97(
    availability_zone_names: typing.Sequence[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__df40356aa79474f9245fbe0f5820930e1ac2296860fc7517548f017d885325f1(
    availability_zone_names: typing.Sequence[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4e121614152110074684b328fd8155e0b55e0fad34a93e31506f46806fc35da1(
    availability_zone_id: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f379431bd49ef8d7d26c145e78b9dcbcd05a5d6a715d2ab10b3184f16bde8e42(
    value: _aws_cdk_aws_lambda_ceddda9d.IFunction,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__24c3de55c04ae40b7e2a52711618f1b6bdbd534427549ecd64a59d1817539b03(
    value: _aws_cdk_aws_logs_ceddda9d.ILogGroup,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__02620da05be465008d0b0794505b82da4876bfeef27c02bac8dd64882b3af1ff(
    value: _aws_cdk_ceddda9d.CustomResource,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__91f0b653e00699938976db245f8464d40c1794756876fc19b4ad839855950230(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    datapoints_to_alarm: jsii.Number,
    evaluation_periods: jsii.Number,
    service_name: builtins.str,
    application_load_balancer_props: typing.Optional[typing.Union[ApplicationLoadBalancerDetectionProps, typing.Dict[builtins.str, typing.Any]]] = None,
    assets_bucket_parameter_name: typing.Optional[builtins.str] = None,
    assets_bucket_prefix_parameter_name: typing.Optional[builtins.str] = None,
    create_dashboard: typing.Optional[builtins.bool] = None,
    interval: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
    nat_gateway_props: typing.Optional[typing.Union[NatGatewayDetectionProps, typing.Dict[builtins.str, typing.Any]]] = None,
    period: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a0651d15ed8cdb0e7d4229be009268d3ac4cee784d9665775fe9dbc804061006(
    value: typing.Mapping[builtins.str, _aws_cdk_aws_cloudwatch_ceddda9d.IAlarm],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3ec564bcf48b6cda84d0cc41144dba2366731021f9aae2ee9f70c410be101142(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__198f3d5a0022ddac739f5e4a830649083f625017c0892120bd8db43d96eb2ec4(
    value: typing.Optional[typing.Mapping[builtins.str, _aws_cdk_aws_cloudwatch_ceddda9d.IAlarm]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f0269305696627ab6f8671d580a6ffee9c44702b3f76cebabf3f49dac8301227(
    value: typing.Optional[typing.List[_aws_cdk_aws_elasticloadbalancingv2_ceddda9d.IApplicationLoadBalancer]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d95ca669596eac69b5dcf7e2c14ba72c245e413d581394f643a1d71052218a81(
    value: typing.Optional[_aws_cdk_aws_cloudwatch_ceddda9d.Dashboard],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a12a9d8eeb0094fca7ab02f796b254b0f2503807dc753010a48c414fd419f8c9(
    value: typing.Optional[typing.Mapping[builtins.str, typing.List[_aws_cdk_aws_ec2_ceddda9d.CfnNatGateway]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7773e8e939b70c12b72e90bae790068ae53e9f8f988dd695cf81376d5999d8fa(
    value: typing.Optional[typing.Mapping[builtins.str, _aws_cdk_aws_cloudwatch_ceddda9d.IAlarm]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b9b8a9ef35fcd536b16032b7c89ca5b2cca4d9f45968b706c065949eeaf46946(
    *,
    alarm_statistic: typing.Optional[builtins.str] = None,
    datapoints_to_alarm: typing.Optional[jsii.Number] = None,
    evaluation_periods: typing.Optional[jsii.Number] = None,
    period: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
    fault_alarm_threshold: typing.Optional[jsii.Number] = None,
    success_alarm_threshold: typing.Optional[jsii.Number] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9c6b3ad9d94fd146e47feab72d6824e32aa2f19b3ef155d47987ea2f5255fd3a(
    *,
    alarm_statistic: typing.Optional[builtins.str] = None,
    datapoints_to_alarm: typing.Optional[jsii.Number] = None,
    evaluation_periods: typing.Optional[jsii.Number] = None,
    period: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
    success_alarm_threshold: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ba3bfecde875105b94fc5e3d1922b0cf4d9ac970ef13c3f154d11a6e7b103874(
    props: typing.Union[OperationAvailabilityMetricDetailsProps, typing.Dict[builtins.str, typing.Any]],
    default_props: IServiceAvailabilityMetricDetails,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f3a9c1d6a36b69cb1a011aaf63c41f895ce71b2e79f4e86ddd6d326d5b7c9a94(
    *,
    metric_dimensions: MetricDimensions,
    operation_name: builtins.str,
    alarm_statistic: typing.Optional[builtins.str] = None,
    datapoints_to_alarm: typing.Optional[jsii.Number] = None,
    evaluation_periods: typing.Optional[jsii.Number] = None,
    fault_metric_names: typing.Optional[typing.Sequence[builtins.str]] = None,
    graphed_fault_statistics: typing.Optional[typing.Sequence[builtins.str]] = None,
    graphed_success_statistics: typing.Optional[typing.Sequence[builtins.str]] = None,
    metric_namespace: typing.Optional[builtins.str] = None,
    period: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
    success_metric_names: typing.Optional[typing.Sequence[builtins.str]] = None,
    unit: typing.Optional[_aws_cdk_aws_cloudwatch_ceddda9d.Unit] = None,
    fault_alarm_threshold: typing.Optional[jsii.Number] = None,
    success_alarm_threshold: typing.Optional[jsii.Number] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c8055ed37fd46397f374a68d5b4756d9a2fcd37a50f9f4a9977c721a44a9f981(
    props: typing.Union[OperationLatencyMetricDetailsProps, typing.Dict[builtins.str, typing.Any]],
    default_props: IServiceLatencyMetricDetails,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9b6e546c66235e53a68265cd01ee63d2bcecaf6761795b96fc1f1bc7757e38cc(
    *,
    metric_dimensions: MetricDimensions,
    operation_name: builtins.str,
    alarm_statistic: typing.Optional[builtins.str] = None,
    datapoints_to_alarm: typing.Optional[jsii.Number] = None,
    evaluation_periods: typing.Optional[jsii.Number] = None,
    fault_metric_names: typing.Optional[typing.Sequence[builtins.str]] = None,
    graphed_fault_statistics: typing.Optional[typing.Sequence[builtins.str]] = None,
    graphed_success_statistics: typing.Optional[typing.Sequence[builtins.str]] = None,
    metric_namespace: typing.Optional[builtins.str] = None,
    period: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
    success_metric_names: typing.Optional[typing.Sequence[builtins.str]] = None,
    unit: typing.Optional[_aws_cdk_aws_cloudwatch_ceddda9d.Unit] = None,
    success_alarm_threshold: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__edeeb4ba8bbf8766e8e506e6b85e0ec5a5da470f73258dfb90846d6e9ff343a8(
    *,
    alarm_statistic: builtins.str,
    datapoints_to_alarm: jsii.Number,
    evaluation_periods: jsii.Number,
    fault_metric_names: typing.Sequence[builtins.str],
    metric_namespace: builtins.str,
    period: _aws_cdk_ceddda9d.Duration,
    success_metric_names: typing.Sequence[builtins.str],
    unit: _aws_cdk_aws_cloudwatch_ceddda9d.Unit,
    graphed_fault_statistics: typing.Optional[typing.Sequence[builtins.str]] = None,
    graphed_success_statistics: typing.Optional[typing.Sequence[builtins.str]] = None,
    fault_alarm_threshold: jsii.Number,
    success_alarm_threshold: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__58ebd30f770ec4a7d6eeb284120e352b6c995556fd4c0fa3199c43165e854d29(
    *,
    alarm_statistic: builtins.str,
    datapoints_to_alarm: jsii.Number,
    evaluation_periods: jsii.Number,
    fault_metric_names: typing.Sequence[builtins.str],
    metric_namespace: builtins.str,
    period: _aws_cdk_ceddda9d.Duration,
    success_metric_names: typing.Sequence[builtins.str],
    unit: _aws_cdk_aws_cloudwatch_ceddda9d.Unit,
    graphed_fault_statistics: typing.Optional[typing.Sequence[builtins.str]] = None,
    graphed_success_statistics: typing.Optional[typing.Sequence[builtins.str]] = None,
    success_alarm_threshold: _aws_cdk_ceddda9d.Duration,
) -> None:
    """Type checking stubs"""
    pass

for cls in [IAvailabilityZoneMapper, IBaseOperationRegionalAlarmsAndRules, IBaseOperationZonalAlarmsAndRules, IBasicServiceMultiAZObservability, ICanaryMetrics, ICanaryOperationRegionalAlarmsAndRules, ICanaryOperationZonalAlarmsAndRules, ICanaryTestAvailabilityMetricsOverride, ICanaryTestLatencyMetricsOverride, ICanaryTestMetricsOverride, IContributorInsightRuleDetails, IInstrumentedServiceMultiAZObservability, IOperation, IOperationAlarmsAndRules, IOperationAvailabilityMetricDetails, IOperationLatencyMetricDetails, IOperationMetricDetails, IServerSideOperationRegionalAlarmsAndRules, IServerSideOperationZonalAlarmsAndRules, IService, IServiceAlarmsAndRules, IServiceAvailabilityMetricDetails, IServiceLatencyMetricDetails, IServiceMetricDetails]:
    typing.cast(typing.Any, cls).__protocol_attrs__ = typing.cast(typing.Any, cls).__protocol_attrs__ - set(['__jsii_proxy_class__', '__jsii_type__'])
