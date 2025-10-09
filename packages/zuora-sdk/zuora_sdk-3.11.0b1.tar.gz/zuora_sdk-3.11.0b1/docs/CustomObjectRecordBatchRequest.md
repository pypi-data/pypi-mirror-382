# CustomObjectRecordBatchRequest

Request of processing custom object records in batch.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**action** | [**CustomObjectRecordBatchAction**](CustomObjectRecordBatchAction.md) |  | 

## Example

```python
from zuora_sdk.models.custom_object_record_batch_request import CustomObjectRecordBatchRequest

# TODO update the JSON string below
json = "{}"
# create an instance of CustomObjectRecordBatchRequest from a JSON string
custom_object_record_batch_request_instance = CustomObjectRecordBatchRequest.from_json(json)
# print the JSON string representation of the object
print(CustomObjectRecordBatchRequest.to_json())

# convert the object into a dict
custom_object_record_batch_request_dict = custom_object_record_batch_request_instance.to_dict()
# create an instance of CustomObjectRecordBatchRequest from a dict
custom_object_record_batch_request_from_dict = CustomObjectRecordBatchRequest.from_dict(custom_object_record_batch_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


