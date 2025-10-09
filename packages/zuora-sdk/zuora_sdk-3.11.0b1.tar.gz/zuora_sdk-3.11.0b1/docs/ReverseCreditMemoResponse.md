# ReverseCreditMemoResponse


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**process_id** | **str** | The Id of the process that handle the operation.  | [optional] 
**request_id** | **str** | Unique request identifier. If you need to contact us about a specific request, providing the request identifier will ensure the fastest possible resolution.  | [optional] 
**reasons** | [**List[FailedReason]**](FailedReason.md) |  | [optional] 
**success** | **bool** | Indicates whether the call succeeded.  | [optional] [default to True]
**credit_memo** | [**ReverseCreditMemoResponseCreditMemo**](ReverseCreditMemoResponseCreditMemo.md) |  | [optional] 
**debit_memo** | [**ReverseCreditMemoResponseDebitMemo**](ReverseCreditMemoResponseDebitMemo.md) |  | [optional] 
**id** | **str** | The ID of credit memo | [optional] 
**job_id** | **str** | The ID of the operation job. | [optional] 
**job_status** | [**OperationJobStatus**](OperationJobStatus.md) |  | [optional] 

## Example

```python
from zuora_sdk.models.reverse_credit_memo_response import ReverseCreditMemoResponse

# TODO update the JSON string below
json = "{}"
# create an instance of ReverseCreditMemoResponse from a JSON string
reverse_credit_memo_response_instance = ReverseCreditMemoResponse.from_json(json)
# print the JSON string representation of the object
print(ReverseCreditMemoResponse.to_json())

# convert the object into a dict
reverse_credit_memo_response_dict = reverse_credit_memo_response_instance.to_dict()
# create an instance of ReverseCreditMemoResponse from a dict
reverse_credit_memo_response_from_dict = ReverseCreditMemoResponse.from_dict(reverse_credit_memo_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


