# BulkUpdateCreditMemosRequest


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**memos** | [**List[UpdateCreditMemoWithId]**](UpdateCreditMemoWithId.md) | The container for a list of credit memos. The maximum number of credit memos is 50. | [optional] 

## Example

```python
from zuora_sdk.models.bulk_update_credit_memos_request import BulkUpdateCreditMemosRequest

# TODO update the JSON string below
json = "{}"
# create an instance of BulkUpdateCreditMemosRequest from a JSON string
bulk_update_credit_memos_request_instance = BulkUpdateCreditMemosRequest.from_json(json)
# print the JSON string representation of the object
print(BulkUpdateCreditMemosRequest.to_json())

# convert the object into a dict
bulk_update_credit_memos_request_dict = bulk_update_credit_memos_request_instance.to_dict()
# create an instance of BulkUpdateCreditMemosRequest from a dict
bulk_update_credit_memos_request_from_dict = BulkUpdateCreditMemosRequest.from_dict(bulk_update_credit_memos_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


