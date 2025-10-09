# PutAttachmentRequest


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**description** | **str** | Description of the attachment. | [optional] 
**file_name** | **str** | File name of the attachment. The value should not contain the file extension.  Only the file name without the extension can be edited. | [optional] 

## Example

```python
from zuora_sdk.models.put_attachment_request import PutAttachmentRequest

# TODO update the JSON string below
json = "{}"
# create an instance of PutAttachmentRequest from a JSON string
put_attachment_request_instance = PutAttachmentRequest.from_json(json)
# print the JSON string representation of the object
print(PutAttachmentRequest.to_json())

# convert the object into a dict
put_attachment_request_dict = put_attachment_request_instance.to_dict()
# create an instance of PutAttachmentRequest from a dict
put_attachment_request_from_dict = PutAttachmentRequest.from_dict(put_attachment_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


