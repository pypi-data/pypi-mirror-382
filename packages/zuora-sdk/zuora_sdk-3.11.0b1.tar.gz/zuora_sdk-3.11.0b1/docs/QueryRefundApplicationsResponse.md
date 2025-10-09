# QueryRefundApplicationsResponse



## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**next_page** | **str** |  | [optional] 
**data** | [**List[ExpandedRefundApplication]**](ExpandedRefundApplication.md) |  | [optional] 

## Example

```python
from zuora_sdk.models.query_refund_applications_response import QueryRefundApplicationsResponse

# TODO update the JSON string below
json = "{}"
# create an instance of QueryRefundApplicationsResponse from a JSON string
query_refund_applications_response_instance = QueryRefundApplicationsResponse.from_json(json)
# print the JSON string representation of the object
print(QueryRefundApplicationsResponse.to_json())

# convert the object into a dict
query_refund_applications_response_dict = query_refund_applications_response_instance.to_dict()
# create an instance of QueryRefundApplicationsResponse from a dict
query_refund_applications_response_from_dict = QueryRefundApplicationsResponse.from_dict(query_refund_applications_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


