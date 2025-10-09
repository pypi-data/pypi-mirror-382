# QueryAccountsResponse



## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**next_page** | **str** |  | [optional] 
**data** | [**List[ExpandedAccount]**](ExpandedAccount.md) |  | [optional] 

## Example

```python
from zuora_sdk.models.query_accounts_response import QueryAccountsResponse

# TODO update the JSON string below
json = "{}"
# create an instance of QueryAccountsResponse from a JSON string
query_accounts_response_instance = QueryAccountsResponse.from_json(json)
# print the JSON string representation of the object
print(QueryAccountsResponse.to_json())

# convert the object into a dict
query_accounts_response_dict = query_accounts_response_instance.to_dict()
# create an instance of QueryAccountsResponse from a dict
query_accounts_response_from_dict = QueryAccountsResponse.from_dict(query_accounts_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


