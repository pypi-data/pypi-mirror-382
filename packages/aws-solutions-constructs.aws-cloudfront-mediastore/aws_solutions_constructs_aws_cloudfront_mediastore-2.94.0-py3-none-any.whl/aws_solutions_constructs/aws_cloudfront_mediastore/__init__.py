r'''
Documentation for this pattern can be found [here](https://github.com/awslabs/aws-solutions-constructs/blob/main/source/patterns/%40aws-solutions-constructs/aws-cloudfront-mediastore/README.adoc)
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

import aws_cdk.aws_cloudfront as _aws_cdk_aws_cloudfront_ceddda9d
import aws_cdk.aws_mediastore as _aws_cdk_aws_mediastore_ceddda9d
import aws_cdk.aws_s3 as _aws_cdk_aws_s3_ceddda9d
import constructs as _constructs_77d1e7e8


class CloudFrontToMediaStore(
    _constructs_77d1e7e8.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="@aws-solutions-constructs/aws-cloudfront-mediastore.CloudFrontToMediaStore",
):
    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        cloud_front_distribution_props: typing.Any = None,
        cloud_front_logging_bucket_props: typing.Optional[typing.Union[_aws_cdk_aws_s3_ceddda9d.BucketProps, typing.Dict[builtins.str, typing.Any]]] = None,
        existing_media_store_container_obj: typing.Optional[_aws_cdk_aws_mediastore_ceddda9d.CfnContainer] = None,
        insert_http_security_headers: typing.Optional[builtins.bool] = None,
        media_store_container_props: typing.Optional[typing.Union[_aws_cdk_aws_mediastore_ceddda9d.CfnContainerProps, typing.Dict[builtins.str, typing.Any]]] = None,
        response_headers_policy_props: typing.Optional[typing.Union[_aws_cdk_aws_cloudfront_ceddda9d.ResponseHeadersPolicyProps, typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''
        :param scope: - represents the scope for all the resources.
        :param id: - this is a scope-unique id.
        :param cloud_front_distribution_props: Optional user provided props to override the default props for the CloudFront. Default: - Default props are used
        :param cloud_front_logging_bucket_props: Optional user provided props to override the default props for the CloudFront Logging Bucket. Default: - Default props are used
        :param existing_media_store_container_obj: Existing instance of mediastore.CfnContainer object. Default: - None
        :param insert_http_security_headers: Optional user provided props to turn on/off the automatic injection of best practice HTTP security headers in all responses from cloudfront. Turning this on will inject default headers and is mutually exclusive with passing custom security headers via the responseHeadersPolicyProps parameter. Default: - true
        :param media_store_container_props: Optional user provided props to override the default props for the MediaStore. Default: - Default props are used
        :param response_headers_policy_props: Optional user provided configuration that cloudfront applies to all http responses. Can be used to pass a custom ResponseSecurityHeadersBehavior, ResponseCustomHeadersBehavior or ResponseHeadersCorsBehavior to the cloudfront distribution. Passing a custom ResponseSecurityHeadersBehavior is mutually exclusive with turning on the default security headers via ``insertHttpSecurityHeaders`` prop. Will throw an error if both ``insertHttpSecurityHeaders`` is set to ``true`` and ResponseSecurityHeadersBehavior is passed. Default: - undefined

        :access: public
        :since: 1.76.0
        :summary: Constructs a new instance of CloudFrontToMediaStore class.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7437ce689f4f0c8bcce19a9f24f6d85ab2e5133c551b0fc77d0d61eeb969839b)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = CloudFrontToMediaStoreProps(
            cloud_front_distribution_props=cloud_front_distribution_props,
            cloud_front_logging_bucket_props=cloud_front_logging_bucket_props,
            existing_media_store_container_obj=existing_media_store_container_obj,
            insert_http_security_headers=insert_http_security_headers,
            media_store_container_props=media_store_container_props,
            response_headers_policy_props=response_headers_policy_props,
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @builtins.property
    @jsii.member(jsii_name="cloudFrontOriginRequestPolicy")
    def cloud_front_origin_request_policy(
        self,
    ) -> _aws_cdk_aws_cloudfront_ceddda9d.OriginRequestPolicy:
        return typing.cast(_aws_cdk_aws_cloudfront_ceddda9d.OriginRequestPolicy, jsii.get(self, "cloudFrontOriginRequestPolicy"))

    @builtins.property
    @jsii.member(jsii_name="cloudFrontWebDistribution")
    def cloud_front_web_distribution(
        self,
    ) -> _aws_cdk_aws_cloudfront_ceddda9d.Distribution:
        return typing.cast(_aws_cdk_aws_cloudfront_ceddda9d.Distribution, jsii.get(self, "cloudFrontWebDistribution"))

    @builtins.property
    @jsii.member(jsii_name="mediaStoreContainer")
    def media_store_container(self) -> _aws_cdk_aws_mediastore_ceddda9d.CfnContainer:
        return typing.cast(_aws_cdk_aws_mediastore_ceddda9d.CfnContainer, jsii.get(self, "mediaStoreContainer"))

    @builtins.property
    @jsii.member(jsii_name="cloudFrontFunction")
    def cloud_front_function(
        self,
    ) -> typing.Optional[_aws_cdk_aws_cloudfront_ceddda9d.Function]:
        return typing.cast(typing.Optional[_aws_cdk_aws_cloudfront_ceddda9d.Function], jsii.get(self, "cloudFrontFunction"))

    @builtins.property
    @jsii.member(jsii_name="cloudFrontLoggingBucket")
    def cloud_front_logging_bucket(
        self,
    ) -> typing.Optional[_aws_cdk_aws_s3_ceddda9d.Bucket]:
        return typing.cast(typing.Optional[_aws_cdk_aws_s3_ceddda9d.Bucket], jsii.get(self, "cloudFrontLoggingBucket"))

    @builtins.property
    @jsii.member(jsii_name="cloudFrontOriginAccessIdentity")
    def cloud_front_origin_access_identity(
        self,
    ) -> typing.Optional[_aws_cdk_aws_cloudfront_ceddda9d.OriginAccessIdentity]:
        return typing.cast(typing.Optional[_aws_cdk_aws_cloudfront_ceddda9d.OriginAccessIdentity], jsii.get(self, "cloudFrontOriginAccessIdentity"))


@jsii.data_type(
    jsii_type="@aws-solutions-constructs/aws-cloudfront-mediastore.CloudFrontToMediaStoreProps",
    jsii_struct_bases=[],
    name_mapping={
        "cloud_front_distribution_props": "cloudFrontDistributionProps",
        "cloud_front_logging_bucket_props": "cloudFrontLoggingBucketProps",
        "existing_media_store_container_obj": "existingMediaStoreContainerObj",
        "insert_http_security_headers": "insertHttpSecurityHeaders",
        "media_store_container_props": "mediaStoreContainerProps",
        "response_headers_policy_props": "responseHeadersPolicyProps",
    },
)
class CloudFrontToMediaStoreProps:
    def __init__(
        self,
        *,
        cloud_front_distribution_props: typing.Any = None,
        cloud_front_logging_bucket_props: typing.Optional[typing.Union[_aws_cdk_aws_s3_ceddda9d.BucketProps, typing.Dict[builtins.str, typing.Any]]] = None,
        existing_media_store_container_obj: typing.Optional[_aws_cdk_aws_mediastore_ceddda9d.CfnContainer] = None,
        insert_http_security_headers: typing.Optional[builtins.bool] = None,
        media_store_container_props: typing.Optional[typing.Union[_aws_cdk_aws_mediastore_ceddda9d.CfnContainerProps, typing.Dict[builtins.str, typing.Any]]] = None,
        response_headers_policy_props: typing.Optional[typing.Union[_aws_cdk_aws_cloudfront_ceddda9d.ResponseHeadersPolicyProps, typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''
        :param cloud_front_distribution_props: Optional user provided props to override the default props for the CloudFront. Default: - Default props are used
        :param cloud_front_logging_bucket_props: Optional user provided props to override the default props for the CloudFront Logging Bucket. Default: - Default props are used
        :param existing_media_store_container_obj: Existing instance of mediastore.CfnContainer object. Default: - None
        :param insert_http_security_headers: Optional user provided props to turn on/off the automatic injection of best practice HTTP security headers in all responses from cloudfront. Turning this on will inject default headers and is mutually exclusive with passing custom security headers via the responseHeadersPolicyProps parameter. Default: - true
        :param media_store_container_props: Optional user provided props to override the default props for the MediaStore. Default: - Default props are used
        :param response_headers_policy_props: Optional user provided configuration that cloudfront applies to all http responses. Can be used to pass a custom ResponseSecurityHeadersBehavior, ResponseCustomHeadersBehavior or ResponseHeadersCorsBehavior to the cloudfront distribution. Passing a custom ResponseSecurityHeadersBehavior is mutually exclusive with turning on the default security headers via ``insertHttpSecurityHeaders`` prop. Will throw an error if both ``insertHttpSecurityHeaders`` is set to ``true`` and ResponseSecurityHeadersBehavior is passed. Default: - undefined

        :summary: The properties for the CloudFrontToMediaStore Construct
        '''
        if isinstance(cloud_front_logging_bucket_props, dict):
            cloud_front_logging_bucket_props = _aws_cdk_aws_s3_ceddda9d.BucketProps(**cloud_front_logging_bucket_props)
        if isinstance(media_store_container_props, dict):
            media_store_container_props = _aws_cdk_aws_mediastore_ceddda9d.CfnContainerProps(**media_store_container_props)
        if isinstance(response_headers_policy_props, dict):
            response_headers_policy_props = _aws_cdk_aws_cloudfront_ceddda9d.ResponseHeadersPolicyProps(**response_headers_policy_props)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e4eb071d044bbbdbcd70b34164c41ffbfadd12ac9e1276cbe91fef9540ef6bd1)
            check_type(argname="argument cloud_front_distribution_props", value=cloud_front_distribution_props, expected_type=type_hints["cloud_front_distribution_props"])
            check_type(argname="argument cloud_front_logging_bucket_props", value=cloud_front_logging_bucket_props, expected_type=type_hints["cloud_front_logging_bucket_props"])
            check_type(argname="argument existing_media_store_container_obj", value=existing_media_store_container_obj, expected_type=type_hints["existing_media_store_container_obj"])
            check_type(argname="argument insert_http_security_headers", value=insert_http_security_headers, expected_type=type_hints["insert_http_security_headers"])
            check_type(argname="argument media_store_container_props", value=media_store_container_props, expected_type=type_hints["media_store_container_props"])
            check_type(argname="argument response_headers_policy_props", value=response_headers_policy_props, expected_type=type_hints["response_headers_policy_props"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if cloud_front_distribution_props is not None:
            self._values["cloud_front_distribution_props"] = cloud_front_distribution_props
        if cloud_front_logging_bucket_props is not None:
            self._values["cloud_front_logging_bucket_props"] = cloud_front_logging_bucket_props
        if existing_media_store_container_obj is not None:
            self._values["existing_media_store_container_obj"] = existing_media_store_container_obj
        if insert_http_security_headers is not None:
            self._values["insert_http_security_headers"] = insert_http_security_headers
        if media_store_container_props is not None:
            self._values["media_store_container_props"] = media_store_container_props
        if response_headers_policy_props is not None:
            self._values["response_headers_policy_props"] = response_headers_policy_props

    @builtins.property
    def cloud_front_distribution_props(self) -> typing.Any:
        '''Optional user provided props to override the default props for the CloudFront.

        :default: - Default props are used
        '''
        result = self._values.get("cloud_front_distribution_props")
        return typing.cast(typing.Any, result)

    @builtins.property
    def cloud_front_logging_bucket_props(
        self,
    ) -> typing.Optional[_aws_cdk_aws_s3_ceddda9d.BucketProps]:
        '''Optional user provided props to override the default props for the CloudFront Logging Bucket.

        :default: - Default props are used
        '''
        result = self._values.get("cloud_front_logging_bucket_props")
        return typing.cast(typing.Optional[_aws_cdk_aws_s3_ceddda9d.BucketProps], result)

    @builtins.property
    def existing_media_store_container_obj(
        self,
    ) -> typing.Optional[_aws_cdk_aws_mediastore_ceddda9d.CfnContainer]:
        '''Existing instance of mediastore.CfnContainer object.

        :default: - None
        '''
        result = self._values.get("existing_media_store_container_obj")
        return typing.cast(typing.Optional[_aws_cdk_aws_mediastore_ceddda9d.CfnContainer], result)

    @builtins.property
    def insert_http_security_headers(self) -> typing.Optional[builtins.bool]:
        '''Optional user provided props to turn on/off the automatic injection of best practice HTTP security headers in all responses from cloudfront.

        Turning this on will inject default headers and is mutually exclusive with passing custom security headers
        via the responseHeadersPolicyProps parameter.

        :default: - true
        '''
        result = self._values.get("insert_http_security_headers")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def media_store_container_props(
        self,
    ) -> typing.Optional[_aws_cdk_aws_mediastore_ceddda9d.CfnContainerProps]:
        '''Optional user provided props to override the default props for the MediaStore.

        :default: - Default props are used
        '''
        result = self._values.get("media_store_container_props")
        return typing.cast(typing.Optional[_aws_cdk_aws_mediastore_ceddda9d.CfnContainerProps], result)

    @builtins.property
    def response_headers_policy_props(
        self,
    ) -> typing.Optional[_aws_cdk_aws_cloudfront_ceddda9d.ResponseHeadersPolicyProps]:
        '''Optional user provided configuration that cloudfront applies to all http responses.

        Can be used to pass a custom ResponseSecurityHeadersBehavior, ResponseCustomHeadersBehavior or
        ResponseHeadersCorsBehavior to the cloudfront distribution.

        Passing a custom ResponseSecurityHeadersBehavior is mutually exclusive with turning on the default security headers
        via ``insertHttpSecurityHeaders`` prop. Will throw an error if both ``insertHttpSecurityHeaders`` is set to ``true``
        and ResponseSecurityHeadersBehavior is passed.

        :default: - undefined
        '''
        result = self._values.get("response_headers_policy_props")
        return typing.cast(typing.Optional[_aws_cdk_aws_cloudfront_ceddda9d.ResponseHeadersPolicyProps], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CloudFrontToMediaStoreProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


__all__ = [
    "CloudFrontToMediaStore",
    "CloudFrontToMediaStoreProps",
]

publication.publish()

def _typecheckingstub__7437ce689f4f0c8bcce19a9f24f6d85ab2e5133c551b0fc77d0d61eeb969839b(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    cloud_front_distribution_props: typing.Any = None,
    cloud_front_logging_bucket_props: typing.Optional[typing.Union[_aws_cdk_aws_s3_ceddda9d.BucketProps, typing.Dict[builtins.str, typing.Any]]] = None,
    existing_media_store_container_obj: typing.Optional[_aws_cdk_aws_mediastore_ceddda9d.CfnContainer] = None,
    insert_http_security_headers: typing.Optional[builtins.bool] = None,
    media_store_container_props: typing.Optional[typing.Union[_aws_cdk_aws_mediastore_ceddda9d.CfnContainerProps, typing.Dict[builtins.str, typing.Any]]] = None,
    response_headers_policy_props: typing.Optional[typing.Union[_aws_cdk_aws_cloudfront_ceddda9d.ResponseHeadersPolicyProps, typing.Dict[builtins.str, typing.Any]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e4eb071d044bbbdbcd70b34164c41ffbfadd12ac9e1276cbe91fef9540ef6bd1(
    *,
    cloud_front_distribution_props: typing.Any = None,
    cloud_front_logging_bucket_props: typing.Optional[typing.Union[_aws_cdk_aws_s3_ceddda9d.BucketProps, typing.Dict[builtins.str, typing.Any]]] = None,
    existing_media_store_container_obj: typing.Optional[_aws_cdk_aws_mediastore_ceddda9d.CfnContainer] = None,
    insert_http_security_headers: typing.Optional[builtins.bool] = None,
    media_store_container_props: typing.Optional[typing.Union[_aws_cdk_aws_mediastore_ceddda9d.CfnContainerProps, typing.Dict[builtins.str, typing.Any]]] = None,
    response_headers_policy_props: typing.Optional[typing.Union[_aws_cdk_aws_cloudfront_ceddda9d.ResponseHeadersPolicyProps, typing.Dict[builtins.str, typing.Any]]] = None,
) -> None:
    """Type checking stubs"""
    pass
