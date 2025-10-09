# CreditMemoPart


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**amount** | **float** | The amount of the credit memo part.  | [optional] 
**created_by_id** | **str** | The ID of the Zuora user who created the credit memo part.  | [optional] 
**created_date** | **str** | The date and time when the credit memo part was created, in &#x60;yyyy-mm-dd hh:mm:ss&#x60; format. For example, 2017-03-01 15:31:10. | [optional] 
**debit_memo_id** | **str** | The ID of the debit memo associated with the credit memo part.  | [optional] 
**id** | **str** | The ID of the credit memo part.  | [optional] 
**invoice_id** | **str** | The ID of the invoice associated with the credit memo part.  | [optional] 
**updated_by_id** | **str** | The ID of the Zuora user who last updated the credit memo part.  | [optional] 
**updated_date** | **str** | The date and time when the credit memo part was last upated, in &#x60;yyyy-mm-dd hh:mm:ss&#x60; format. For example, 2017-03-02 15:36:10. | [optional] 
**organization_label** | **str** | organizationLabel.  | [optional] 

## Example

```python
from zuora_sdk.models.credit_memo_part import CreditMemoPart

# TODO update the JSON string below
json = "{}"
# create an instance of CreditMemoPart from a JSON string
credit_memo_part_instance = CreditMemoPart.from_json(json)
# print the JSON string representation of the object
print(CreditMemoPart.to_json())

# convert the object into a dict
credit_memo_part_dict = credit_memo_part_instance.to_dict()
# create an instance of CreditMemoPart from a dict
credit_memo_part_from_dict = CreditMemoPart.from_dict(credit_memo_part_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


