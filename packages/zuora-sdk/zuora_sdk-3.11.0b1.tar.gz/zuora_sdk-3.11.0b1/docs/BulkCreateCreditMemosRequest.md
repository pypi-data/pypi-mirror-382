# BulkCreateCreditMemosRequest


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**source_type** | **str** |  | [default to 'Standalone']
**memos** | [**List[CreateCreditMemoFromCharge]**](CreateCreditMemoFromCharge.md) | The container for a list of credit memos. The maximum number of credit memos is 50. | [optional] 

## Example

```python
from zuora_sdk.models.bulk_create_credit_memos_request import BulkCreateCreditMemosRequest

# TODO update the JSON string below
json = "{}"
# create an instance of BulkCreateCreditMemosRequest from a JSON string
bulk_create_credit_memos_request_instance = BulkCreateCreditMemosRequest.from_json(json)
# print the JSON string representation of the object
print(BulkCreateCreditMemosRequest.to_json())

# convert the object into a dict
bulk_create_credit_memos_request_dict = bulk_create_credit_memos_request_instance.to_dict()
# create an instance of BulkCreateCreditMemosRequest from a dict
bulk_create_credit_memos_request_from_dict = BulkCreateCreditMemosRequest.from_dict(bulk_create_credit_memos_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


