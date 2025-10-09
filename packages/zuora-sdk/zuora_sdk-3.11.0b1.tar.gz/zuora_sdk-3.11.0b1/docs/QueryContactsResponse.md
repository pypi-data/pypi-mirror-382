# QueryContactsResponse



## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**next_page** | **str** |  | [optional] 
**data** | [**List[ExpandedContact]**](ExpandedContact.md) |  | [optional] 

## Example

```python
from zuora_sdk.models.query_contacts_response import QueryContactsResponse

# TODO update the JSON string below
json = "{}"
# create an instance of QueryContactsResponse from a JSON string
query_contacts_response_instance = QueryContactsResponse.from_json(json)
# print the JSON string representation of the object
print(QueryContactsResponse.to_json())

# convert the object into a dict
query_contacts_response_dict = query_contacts_response_instance.to_dict()
# create an instance of QueryContactsResponse from a dict
query_contacts_response_from_dict = QueryContactsResponse.from_dict(query_contacts_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


