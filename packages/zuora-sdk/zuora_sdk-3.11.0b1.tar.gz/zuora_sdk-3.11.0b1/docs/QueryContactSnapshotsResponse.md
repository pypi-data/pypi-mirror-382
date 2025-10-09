# QueryContactSnapshotsResponse



## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**next_page** | **str** |  | [optional] 
**data** | [**List[ExpandedContactSnapshot]**](ExpandedContactSnapshot.md) |  | [optional] 

## Example

```python
from zuora_sdk.models.query_contact_snapshots_response import QueryContactSnapshotsResponse

# TODO update the JSON string below
json = "{}"
# create an instance of QueryContactSnapshotsResponse from a JSON string
query_contact_snapshots_response_instance = QueryContactSnapshotsResponse.from_json(json)
# print the JSON string representation of the object
print(QueryContactSnapshotsResponse.to_json())

# convert the object into a dict
query_contact_snapshots_response_dict = query_contact_snapshots_response_instance.to_dict()
# create an instance of QueryContactSnapshotsResponse from a dict
query_contact_snapshots_response_from_dict = QueryContactSnapshotsResponse.from_dict(query_contact_snapshots_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


