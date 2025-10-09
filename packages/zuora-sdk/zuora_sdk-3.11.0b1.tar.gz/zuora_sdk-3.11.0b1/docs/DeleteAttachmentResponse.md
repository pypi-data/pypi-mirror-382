# DeleteAttachmentResponse


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**process_id** | **str** | The Id of the process that handle the operation.  | [optional] 
**request_id** | **str** | The request ID of this process.  | [optional] 
**reasons** | [**List[FailedReason]**](FailedReason.md) |  | [optional] 
**success** | **bool** | Returns &#x60;true&#x60; if the request was processed successfully.  | [optional] 

## Example

```python
from zuora_sdk.models.delete_attachment_response import DeleteAttachmentResponse

# TODO update the JSON string below
json = "{}"
# create an instance of DeleteAttachmentResponse from a JSON string
delete_attachment_response_instance = DeleteAttachmentResponse.from_json(json)
# print the JSON string representation of the object
print(DeleteAttachmentResponse.to_json())

# convert the object into a dict
delete_attachment_response_dict = delete_attachment_response_instance.to_dict()
# create an instance of DeleteAttachmentResponse from a dict
delete_attachment_response_from_dict = DeleteAttachmentResponse.from_dict(delete_attachment_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


