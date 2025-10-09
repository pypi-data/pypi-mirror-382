# QueryAmendmentsResponse



## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**next_page** | **str** |  | [optional] 
**data** | [**List[ExpandedAmendment]**](ExpandedAmendment.md) |  | [optional] 

## Example

```python
from zuora_sdk.models.query_amendments_response import QueryAmendmentsResponse

# TODO update the JSON string below
json = "{}"
# create an instance of QueryAmendmentsResponse from a JSON string
query_amendments_response_instance = QueryAmendmentsResponse.from_json(json)
# print the JSON string representation of the object
print(QueryAmendmentsResponse.to_json())

# convert the object into a dict
query_amendments_response_dict = query_amendments_response_instance.to_dict()
# create an instance of QueryAmendmentsResponse from a dict
query_amendments_response_from_dict = QueryAmendmentsResponse.from_dict(query_amendments_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


