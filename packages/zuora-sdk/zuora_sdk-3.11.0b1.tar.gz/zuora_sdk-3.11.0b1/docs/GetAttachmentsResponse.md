# GetAttachmentsResponse


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**process_id** | **str** | The Id of the process that handle the operation.  | [optional] 
**request_id** | **str** | The request ID of this process.  | [optional] 
**reasons** | [**List[FailedReason]**](FailedReason.md) |  | [optional] 
**success** | **bool** | Returns &#x60;true&#x60; if the request was processed successfully.  | [optional] 
**attachments** | [**List[GetAttachmentResponse]**](GetAttachmentResponse.md) | Container for one or more attachments.  | [optional] 
**next_page** | **str** | URL to retrieve the next page of the response if it exists; otherwise absent. | [optional] 

## Example

```python
from zuora_sdk.models.get_attachments_response import GetAttachmentsResponse

# TODO update the JSON string below
json = "{}"
# create an instance of GetAttachmentsResponse from a JSON string
get_attachments_response_instance = GetAttachmentsResponse.from_json(json)
# print the JSON string representation of the object
print(GetAttachmentsResponse.to_json())

# convert the object into a dict
get_attachments_response_dict = get_attachments_response_instance.to_dict()
# create an instance of GetAttachmentsResponse from a dict
get_attachments_response_from_dict = GetAttachmentsResponse.from_dict(get_attachments_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


