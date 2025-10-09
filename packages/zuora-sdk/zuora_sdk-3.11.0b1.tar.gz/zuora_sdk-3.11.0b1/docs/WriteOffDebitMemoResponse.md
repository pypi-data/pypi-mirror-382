# WriteOffDebitMemoResponse


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**process_id** | **str** | The Id of the process that handle the operation.  | [optional] 
**request_id** | **str** | Unique request identifier. If you need to contact us about a specific request, providing the request identifier will ensure the fastest possible resolution.  | [optional] 
**reasons** | [**List[FailedReason]**](FailedReason.md) |  | [optional] 
**success** | **bool** | Indicates whether the call succeeded.  | [optional] [default to True]
**credit_memo** | [**WriteOffInvoiceResponseCreditMemo**](WriteOffInvoiceResponseCreditMemo.md) |  | [optional] 

## Example

```python
from zuora_sdk.models.write_off_debit_memo_response import WriteOffDebitMemoResponse

# TODO update the JSON string below
json = "{}"
# create an instance of WriteOffDebitMemoResponse from a JSON string
write_off_debit_memo_response_instance = WriteOffDebitMemoResponse.from_json(json)
# print the JSON string representation of the object
print(WriteOffDebitMemoResponse.to_json())

# convert the object into a dict
write_off_debit_memo_response_dict = write_off_debit_memo_response_instance.to_dict()
# create an instance of WriteOffDebitMemoResponse from a dict
write_off_debit_memo_response_from_dict = WriteOffDebitMemoResponse.from_dict(write_off_debit_memo_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


