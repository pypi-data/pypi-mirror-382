# CustomObjectRecordBatchAction

The batch action on custom object records

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**allow_partial_success** | **bool** | Indicates whether the records that pass the schema validation should be updated when not all records in the request pass the schema validation.  Only applicable when &#x60;type&#x60; is &#x60;update&#x60;.  | [optional] [default to False]
**ids** | **List[str]** | Ids of the custom object records that you want to delete. Each ID must be a string of 36 characters. Only applicable when &#x60;type&#x60; is &#x60;delete&#x60;. | [optional] 
**records** | **Dict[str, object]** | Object records that you want to update. Only applicable when &#x60;type&#x60; is &#x60;update&#x60;. | [optional] 
**type** | [**CustomObjectRecordBatchActionType**](CustomObjectRecordBatchActionType.md) |  | 

## Example

```python
from zuora_sdk.models.custom_object_record_batch_action import CustomObjectRecordBatchAction

# TODO update the JSON string below
json = "{}"
# create an instance of CustomObjectRecordBatchAction from a JSON string
custom_object_record_batch_action_instance = CustomObjectRecordBatchAction.from_json(json)
# print the JSON string representation of the object
print(CustomObjectRecordBatchAction.to_json())

# convert the object into a dict
custom_object_record_batch_action_dict = custom_object_record_batch_action_instance.to_dict()
# create an instance of CustomObjectRecordBatchAction from a dict
custom_object_record_batch_action_from_dict = CustomObjectRecordBatchAction.from_dict(custom_object_record_batch_action_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


