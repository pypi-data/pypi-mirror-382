# ExpandedCreditMemoApplication


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**id** | **str** |  | [optional] 
**created_by_id** | **str** |  | [optional] 
**created_date** | **str** |  | [optional] 
**updated_by_id** | **str** |  | [optional] 
**updated_date** | **str** |  | [optional] 
**amount** | **float** |  | [optional] 
**effective_date** | **date** |  | [optional] 
**credit_memo_id** | **str** |  | [optional] 
**account_id** | **str** |  | [optional] 
**application_group_id** | **str** |  | [optional] 
**debit_memo_id** | **str** |  | [optional] 
**invoice_id** | **str** |  | [optional] 
**credit_memo** | [**ExpandedCreditMemo**](ExpandedCreditMemo.md) |  | [optional] 

## Example

```python
from zuora_sdk.models.expanded_credit_memo_application import ExpandedCreditMemoApplication

# TODO update the JSON string below
json = "{}"
# create an instance of ExpandedCreditMemoApplication from a JSON string
expanded_credit_memo_application_instance = ExpandedCreditMemoApplication.from_json(json)
# print the JSON string representation of the object
print(ExpandedCreditMemoApplication.to_json())

# convert the object into a dict
expanded_credit_memo_application_dict = expanded_credit_memo_application_instance.to_dict()
# create an instance of ExpandedCreditMemoApplication from a dict
expanded_credit_memo_application_from_dict = ExpandedCreditMemoApplication.from_dict(expanded_credit_memo_application_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


