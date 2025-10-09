# QueryCommitmentPeriodsResponse



## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**next_page** | **str** |  | [optional] 
**data** | [**List[ExpandedCommitmentPeriod]**](ExpandedCommitmentPeriod.md) |  | [optional] 

## Example

```python
from zuora_sdk.models.query_commitment_periods_response import QueryCommitmentPeriodsResponse

# TODO update the JSON string below
json = "{}"
# create an instance of QueryCommitmentPeriodsResponse from a JSON string
query_commitment_periods_response_instance = QueryCommitmentPeriodsResponse.from_json(json)
# print the JSON string representation of the object
print(QueryCommitmentPeriodsResponse.to_json())

# convert the object into a dict
query_commitment_periods_response_dict = query_commitment_periods_response_instance.to_dict()
# create an instance of QueryCommitmentPeriodsResponse from a dict
query_commitment_periods_response_from_dict = QueryCommitmentPeriodsResponse.from_dict(query_commitment_periods_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


