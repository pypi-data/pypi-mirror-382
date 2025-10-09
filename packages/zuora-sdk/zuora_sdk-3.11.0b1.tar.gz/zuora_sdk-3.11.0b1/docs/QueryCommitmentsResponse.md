# QueryCommitmentsResponse



## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**next_page** | **str** |  | [optional] 
**data** | [**List[ExpandedCommitment]**](ExpandedCommitment.md) |  | [optional] 

## Example

```python
from zuora_sdk.models.query_commitments_response import QueryCommitmentsResponse

# TODO update the JSON string below
json = "{}"
# create an instance of QueryCommitmentsResponse from a JSON string
query_commitments_response_instance = QueryCommitmentsResponse.from_json(json)
# print the JSON string representation of the object
print(QueryCommitmentsResponse.to_json())

# convert the object into a dict
query_commitments_response_dict = query_commitments_response_instance.to_dict()
# create an instance of QueryCommitmentsResponse from a dict
query_commitments_response_from_dict = QueryCommitmentsResponse.from_dict(query_commitments_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


