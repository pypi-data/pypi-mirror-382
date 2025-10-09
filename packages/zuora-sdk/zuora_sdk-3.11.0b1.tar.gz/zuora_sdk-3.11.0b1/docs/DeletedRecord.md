# DeletedRecord


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**column** | **str** | Name of the Column in the extracted file that points to the deleted records.  | [optional] 
**format** | **str** | Can be set to either &#x60;Numeric&#x60; or &#x60;Boolean&#x60;. If set to &#x60;Numeric&#x60;, deleted records are marked as &#x60;1&#x60;. If set to &#x60;Boolean&#x60;, deleted records are marked as &#x60;true&#x60;. | [optional] 

## Example

```python
from zuora_sdk.models.deleted_record import DeletedRecord

# TODO update the JSON string below
json = "{}"
# create an instance of DeletedRecord from a JSON string
deleted_record_instance = DeletedRecord.from_json(json)
# print the JSON string representation of the object
print(DeletedRecord.to_json())

# convert the object into a dict
deleted_record_dict = deleted_record_instance.to_dict()
# create an instance of DeletedRecord from a dict
deleted_record_from_dict = DeletedRecord.from_dict(deleted_record_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


