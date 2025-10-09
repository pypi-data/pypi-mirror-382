# QueryCreditMemoApplicationsResponse



## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**next_page** | **str** |  | [optional] 
**data** | [**List[ExpandedCreditMemoApplication]**](ExpandedCreditMemoApplication.md) |  | [optional] 

## Example

```python
from zuora_sdk.models.query_credit_memo_applications_response import QueryCreditMemoApplicationsResponse

# TODO update the JSON string below
json = "{}"
# create an instance of QueryCreditMemoApplicationsResponse from a JSON string
query_credit_memo_applications_response_instance = QueryCreditMemoApplicationsResponse.from_json(json)
# print the JSON string representation of the object
print(QueryCreditMemoApplicationsResponse.to_json())

# convert the object into a dict
query_credit_memo_applications_response_dict = query_credit_memo_applications_response_instance.to_dict()
# create an instance of QueryCreditMemoApplicationsResponse from a dict
query_credit_memo_applications_response_from_dict = QueryCreditMemoApplicationsResponse.from_dict(query_credit_memo_applications_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


