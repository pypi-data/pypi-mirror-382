# BulkCreateDebitMemosFromChargeRequest


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**source_type** | **str** |  | [default to 'Standalone']
**memos** | [**List[CreateDebitMemoFromCharge]**](CreateDebitMemoFromCharge.md) | The container for a list of debit memos. The maximum number of debit memos is 50. | [optional] 

## Example

```python
from zuora_sdk.models.bulk_create_debit_memos_from_charge_request import BulkCreateDebitMemosFromChargeRequest

# TODO update the JSON string below
json = "{}"
# create an instance of BulkCreateDebitMemosFromChargeRequest from a JSON string
bulk_create_debit_memos_from_charge_request_instance = BulkCreateDebitMemosFromChargeRequest.from_json(json)
# print the JSON string representation of the object
print(BulkCreateDebitMemosFromChargeRequest.to_json())

# convert the object into a dict
bulk_create_debit_memos_from_charge_request_dict = bulk_create_debit_memos_from_charge_request_instance.to_dict()
# create an instance of BulkCreateDebitMemosFromChargeRequest from a dict
bulk_create_debit_memos_from_charge_request_from_dict = BulkCreateDebitMemosFromChargeRequest.from_dict(bulk_create_debit_memos_from_charge_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


