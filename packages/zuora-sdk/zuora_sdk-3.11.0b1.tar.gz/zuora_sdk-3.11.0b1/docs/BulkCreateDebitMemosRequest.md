# BulkCreateDebitMemosRequest


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**source_type** | **str** |  | [default to 'Standalone']
**memos** | [**List[CreateDebitMemoFromCharge]**](CreateDebitMemoFromCharge.md) | The container for a list of debit memos. The maximum number of debit memos is 50. | [optional] 

## Example

```python
from zuora_sdk.models.bulk_create_debit_memos_request import BulkCreateDebitMemosRequest

# TODO update the JSON string below
json = "{}"
# create an instance of BulkCreateDebitMemosRequest from a JSON string
bulk_create_debit_memos_request_instance = BulkCreateDebitMemosRequest.from_json(json)
# print the JSON string representation of the object
print(BulkCreateDebitMemosRequest.to_json())

# convert the object into a dict
bulk_create_debit_memos_request_dict = bulk_create_debit_memos_request_instance.to_dict()
# create an instance of BulkCreateDebitMemosRequest from a dict
bulk_create_debit_memos_request_from_dict = BulkCreateDebitMemosRequest.from_dict(bulk_create_debit_memos_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


