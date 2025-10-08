# h2o_featurestore.gen.OnlineServiceApi

All URIs are relative to *http://localhost*

Method | HTTP request | Description
------------- | ------------- | -------------
[**online_service_online_ingestion**](OnlineServiceApi.md#online_service_online_ingestion) | **POST** /v1/ingestion/feature-sets/{featureSetId}/{featureSetMajorVersion} | 
[**online_service_online_retrieve**](OnlineServiceApi.md#online_service_online_retrieve) | **GET** /v1/retrieve/feature-sets/{featureSetId}/{featureSetMajorVersion} | 


# **online_service_online_ingestion**
> V1OnlineIngestionResponse online_service_online_ingestion(feature_set_id, feature_set_major_version, body)



### Example


```python
import time
import h2o_featurestore.gen
from h2o_featurestore.gen.api import online_service_api
from h2o_featurestore.gen.model.online_service_online_ingestion_body import OnlineServiceOnlineIngestionBody
from h2o_featurestore.gen.model.v1_online_ingestion_response import V1OnlineIngestionResponse
from h2o_featurestore.gen.model.rpc_status import RpcStatus
from pprint import pprint
# Defining the host is optional and defaults to http://localhost
# See configuration.py for a list of all supported configuration parameters.
configuration = h2o_featurestore.gen.Configuration(
    host = "http://localhost"
)


# Enter a context with an instance of the API client
with h2o_featurestore.gen.ApiClient() as api_client:
    # Create an instance of the API class
    api_instance = online_service_api.OnlineServiceApi(api_client)
    feature_set_id = "featureSetId_example" # str | 
    feature_set_major_version = "featureSetMajorVersion_example" # str | 
    body = OnlineServiceOnlineIngestionBody(
        token="token_example",
        signature="signature_example",
        rows=[
            "rows_example",
        ],
    ) # OnlineServiceOnlineIngestionBody | 

    # example passing only required values which don't have defaults set
    try:
        api_response = api_instance.online_service_online_ingestion(feature_set_id, feature_set_major_version, body)
        pprint(api_response)
    except h2o_featurestore.gen.ApiException as e:
        print("Exception when calling OnlineServiceApi->online_service_online_ingestion: %s\n" % e)
```


### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **feature_set_id** | **str**|  |
 **feature_set_major_version** | **str**|  |
 **body** | [**OnlineServiceOnlineIngestionBody**](OnlineServiceOnlineIngestionBody.md)|  |

### Return type

[**V1OnlineIngestionResponse**](V1OnlineIngestionResponse.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json


### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | A successful response. |  -  |
**0** | An unexpected error response. |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **online_service_online_retrieve**
> V1OnlineRetrieveResponse online_service_online_retrieve(feature_set_id, feature_set_major_version)



### Example


```python
import time
import h2o_featurestore.gen
from h2o_featurestore.gen.api import online_service_api
from h2o_featurestore.gen.model.v1_online_retrieve_response import V1OnlineRetrieveResponse
from h2o_featurestore.gen.model.rpc_status import RpcStatus
from pprint import pprint
# Defining the host is optional and defaults to http://localhost
# See configuration.py for a list of all supported configuration parameters.
configuration = h2o_featurestore.gen.Configuration(
    host = "http://localhost"
)


# Enter a context with an instance of the API client
with h2o_featurestore.gen.ApiClient() as api_client:
    # Create an instance of the API class
    api_instance = online_service_api.OnlineServiceApi(api_client)
    feature_set_id = "featureSetId_example" # str | 
    feature_set_major_version = "featureSetMajorVersion_example" # str | 
    token = "token_example" # str |  (optional)
    signature = "signature_example" # str |  (optional)
    key = [
        "key_example",
    ] # [str] |  (optional)

    # example passing only required values which don't have defaults set
    try:
        api_response = api_instance.online_service_online_retrieve(feature_set_id, feature_set_major_version)
        pprint(api_response)
    except h2o_featurestore.gen.ApiException as e:
        print("Exception when calling OnlineServiceApi->online_service_online_retrieve: %s\n" % e)

    # example passing only required values which don't have defaults set
    # and optional values
    try:
        api_response = api_instance.online_service_online_retrieve(feature_set_id, feature_set_major_version, token=token, signature=signature, key=key)
        pprint(api_response)
    except h2o_featurestore.gen.ApiException as e:
        print("Exception when calling OnlineServiceApi->online_service_online_retrieve: %s\n" % e)
```


### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **feature_set_id** | **str**|  |
 **feature_set_major_version** | **str**|  |
 **token** | **str**|  | [optional]
 **signature** | **str**|  | [optional]
 **key** | **[str]**|  | [optional]

### Return type

[**V1OnlineRetrieveResponse**](V1OnlineRetrieveResponse.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json


### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | A successful response. |  -  |
**0** | An unexpected error response. |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

