# PostAttachmentResponse


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**process_id** | **str** | The Id of the process that handle the operation.  | [optional] 
**request_id** | **str** | The request ID of this process.  | [optional] 
**reasons** | [**List[FailedReason]**](FailedReason.md) |  | [optional] 
**success** | **bool** | Returns &#x60;true&#x60; if the request was processed successfully.  | [optional] 
**file_id** | **str** | ID to identify the attached file. Use this file ID with [Get files](https://www.zuora.com/developer/api-references/api/operation/Get_Files) to download the file. | [optional] 
**id** | **str** | Attachment id.  | [optional] 

## Example

```python
from zuora_sdk.models.post_attachment_response import PostAttachmentResponse

# TODO update the JSON string below
json = "{}"
# create an instance of PostAttachmentResponse from a JSON string
post_attachment_response_instance = PostAttachmentResponse.from_json(json)
# print the JSON string representation of the object
print(PostAttachmentResponse.to_json())

# convert the object into a dict
post_attachment_response_dict = post_attachment_response_instance.to_dict()
# create an instance of PostAttachmentResponse from a dict
post_attachment_response_from_dict = PostAttachmentResponse.from_dict(post_attachment_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


