# HostedPagesResponse


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**hostedpages** | [**List[HostedPageResponse]**](HostedPageResponse.md) | Container for the hosted page information.  | [optional] 
**success** | **bool** | Returns &#x60;true&#x60; if the request was processed successfully.  | [optional] 

## Example

```python
from zuora_sdk.models.hosted_pages_response import HostedPagesResponse

# TODO update the JSON string below
json = "{}"
# create an instance of HostedPagesResponse from a JSON string
hosted_pages_response_instance = HostedPagesResponse.from_json(json)
# print the JSON string representation of the object
print(HostedPagesResponse.to_json())

# convert the object into a dict
hosted_pages_response_dict = hosted_pages_response_instance.to_dict()
# create an instance of HostedPagesResponse from a dict
hosted_pages_response_from_dict = HostedPagesResponse.from_dict(hosted_pages_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


