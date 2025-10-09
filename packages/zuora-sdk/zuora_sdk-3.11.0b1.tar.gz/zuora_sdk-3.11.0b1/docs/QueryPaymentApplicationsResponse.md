# QueryPaymentApplicationsResponse



## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**next_page** | **str** |  | [optional] 
**data** | [**List[ExpandedPaymentApplication]**](ExpandedPaymentApplication.md) |  | [optional] 

## Example

```python
from zuora_sdk.models.query_payment_applications_response import QueryPaymentApplicationsResponse

# TODO update the JSON string below
json = "{}"
# create an instance of QueryPaymentApplicationsResponse from a JSON string
query_payment_applications_response_instance = QueryPaymentApplicationsResponse.from_json(json)
# print the JSON string representation of the object
print(QueryPaymentApplicationsResponse.to_json())

# convert the object into a dict
query_payment_applications_response_dict = query_payment_applications_response_instance.to_dict()
# create an instance of QueryPaymentApplicationsResponse from a dict
query_payment_applications_response_from_dict = QueryPaymentApplicationsResponse.from_dict(query_payment_applications_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


