# HostedPageResponse


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**page_id** | **str** | Page ID of the Payment Page that Zuora assigns when it is created.  | [optional] 
**page_name** | **str** | Name of the Payment Page that specified during the page configuration.  | [optional] 
**page_type** | **str** | Payment method type of this Payment Page, e.g. &#39;Credit Card&#39;, &#39;ACH&#39;, or &#39;Bank Transfer&#39;. | [optional] 
**page_version** | **str** | Version of the Payment Page. 2 for Payment Pages 2.0.  | [optional] 

## Example

```python
from zuora_sdk.models.hosted_page_response import HostedPageResponse

# TODO update the JSON string below
json = "{}"
# create an instance of HostedPageResponse from a JSON string
hosted_page_response_instance = HostedPageResponse.from_json(json)
# print the JSON string representation of the object
print(HostedPageResponse.to_json())

# convert the object into a dict
hosted_page_response_dict = hosted_page_response_instance.to_dict()
# create an instance of HostedPageResponse from a dict
hosted_page_response_from_dict = HostedPageResponse.from_dict(hosted_page_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


