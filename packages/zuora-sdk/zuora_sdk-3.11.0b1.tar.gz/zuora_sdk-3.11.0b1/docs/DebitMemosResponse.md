# DebitMemosResponse


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**process_id** | **str** | The Id of the process that handle the operation.  | [optional] 
**request_id** | **str** | Unique request identifier. If you need to contact us about a specific request, providing the request identifier will ensure the fastest possible resolution.  | [optional] 
**reasons** | [**List[FailedReason]**](FailedReason.md) |  | [optional] 
**success** | **bool** | Indicates whether the call succeeded.  | [optional] [default to True]
**debitmemos** | [**List[DebitMemo]**](DebitMemo.md) | Container for debit memos.  | [optional] 
**next_page** | **str** | URL to retrieve the next page of the response if it exists; otherwise absent. | [optional] 

## Example

```python
from zuora_sdk.models.debit_memos_response import DebitMemosResponse

# TODO update the JSON string below
json = "{}"
# create an instance of DebitMemosResponse from a JSON string
debit_memos_response_instance = DebitMemosResponse.from_json(json)
# print the JSON string representation of the object
print(DebitMemosResponse.to_json())

# convert the object into a dict
debit_memos_response_dict = debit_memos_response_instance.to_dict()
# create an instance of DebitMemosResponse from a dict
debit_memos_response_from_dict = DebitMemosResponse.from_dict(debit_memos_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


