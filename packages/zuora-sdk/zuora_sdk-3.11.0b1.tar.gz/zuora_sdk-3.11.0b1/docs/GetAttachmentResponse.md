# GetAttachmentResponse


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**process_id** | **str** | The Id of the process that handle the operation.  | [optional] 
**request_id** | **str** | The request ID of this process.  | [optional] 
**reasons** | [**List[FailedReason]**](FailedReason.md) |  | [optional] 
**success** | **bool** | Returns &#x60;true&#x60; if the request was processed successfully.  | [optional] 
**created_by** | **str** | Zuora user id who added this attachment to the object.  | [optional] 
**created_on** | **str** | Date and time when the attachment was added to the object.  | [optional] 
**description** | **str** | Description of the attachment.  | [optional] 
**file_content_type** | **str** | File type.  | [optional] 
**file_id** | **str** | File ID of the attached file. Use this file ID with [Get files](https://www.zuora.com/developer/api-references/api/operation/Get_Files) to download the file. | [optional] 
**file_name** | **str** | Attachment file name.  | [optional] 
**id** | **str** | Id of this attachment.  | [optional] 
**updated_by** | **str** | Zuora user id who last updated the attachment.  | [optional] 
**updated_on** | **str** | Date and time when the attachment was last updated.  | [optional] 

## Example

```python
from zuora_sdk.models.get_attachment_response import GetAttachmentResponse

# TODO update the JSON string below
json = "{}"
# create an instance of GetAttachmentResponse from a JSON string
get_attachment_response_instance = GetAttachmentResponse.from_json(json)
# print the JSON string representation of the object
print(GetAttachmentResponse.to_json())

# convert the object into a dict
get_attachment_response_dict = get_attachment_response_instance.to_dict()
# create an instance of GetAttachmentResponse from a dict
get_attachment_response_from_dict = GetAttachmentResponse.from_dict(get_attachment_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


