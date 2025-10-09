# DebitMemoItemsResponse


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**process_id** | **str** | The Id of the process that handle the operation.  | [optional] 
**request_id** | **str** | Unique request identifier. If you need to contact us about a specific request, providing the request identifier will ensure the fastest possible resolution.  | [optional] 
**reasons** | [**List[FailedReason]**](FailedReason.md) |  | [optional] 
**success** | **bool** | Indicates whether the call succeeded.  | [optional] [default to True]
**items** | [**List[DebitMemoItem]**](DebitMemoItem.md) | Container for debit memo items.  | [optional] 
**next_page** | **str** | URL to retrieve the next page of the response if it exists; otherwise absent. | [optional] 

## Example

```python
from zuora_sdk.models.debit_memo_items_response import DebitMemoItemsResponse

# TODO update the JSON string below
json = "{}"
# create an instance of DebitMemoItemsResponse from a JSON string
debit_memo_items_response_instance = DebitMemoItemsResponse.from_json(json)
# print the JSON string representation of the object
print(DebitMemoItemsResponse.to_json())

# convert the object into a dict
debit_memo_items_response_dict = debit_memo_items_response_instance.to_dict()
# create an instance of DebitMemoItemsResponse from a dict
debit_memo_items_response_from_dict = DebitMemoItemsResponse.from_dict(debit_memo_items_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


