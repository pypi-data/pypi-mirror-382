# CancelBillRunRequest


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**cancel_once** | **bool** | Whether to cancel the current bill run or cancel all future recurring bill runs, only valid for a scheduled bill run. | [optional] [default to True]

## Example

```python
from zuora_sdk.models.cancel_bill_run_request import CancelBillRunRequest

# TODO update the JSON string below
json = "{}"
# create an instance of CancelBillRunRequest from a JSON string
cancel_bill_run_request_instance = CancelBillRunRequest.from_json(json)
# print the JSON string representation of the object
print(CancelBillRunRequest.to_json())

# convert the object into a dict
cancel_bill_run_request_dict = cancel_bill_run_request_instance.to_dict()
# create an instance of CancelBillRunRequest from a dict
cancel_bill_run_request_from_dict = CancelBillRunRequest.from_dict(cancel_bill_run_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


