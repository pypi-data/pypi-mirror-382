# PreviewOrderAsyncResponse


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**job_id** | **str** | The ID of an asynchronous job that will be returned for tracking the status and result of the job. | [optional] 

## Example

```python
from zuora_sdk.models.preview_order_async_response import PreviewOrderAsyncResponse

# TODO update the JSON string below
json = "{}"
# create an instance of PreviewOrderAsyncResponse from a JSON string
preview_order_async_response_instance = PreviewOrderAsyncResponse.from_json(json)
# print the JSON string representation of the object
print(PreviewOrderAsyncResponse.to_json())

# convert the object into a dict
preview_order_async_response_dict = preview_order_async_response_instance.to_dict()
# create an instance of PreviewOrderAsyncResponse from a dict
preview_order_async_response_from_dict = PreviewOrderAsyncResponse.from_dict(preview_order_async_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


