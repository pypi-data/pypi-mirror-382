# CreditMemoItemPart


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**amount** | **float** | The amount of the credit memo part item.  | [optional] 
**created_by_id** | **str** | The ID of the Zuora user who created the credit memo part item.  | [optional] 
**created_date** | **str** | The date and time when the credit memo part item was created, in &#x60;yyyy-mm-dd hh:mm:ss&#x60; format. For example, 2017-03-01 15:31:10. | [optional] 
**credit_memo_item_id** | **str** | The ID of the credit memo item associated with the credit memo part item.  | [optional] 
**credit_tax_item_id** | **str** | The ID of the credit memo taxation item.  | [optional] 
**debit_memo_item_id** | **str** | The ID of the debit memo item associated with the credit memo part item.  | [optional] 
**id** | **str** | The ID of the credit memo part item.  | [optional] 
**invoice_item_id** | **str** | The ID of the invoice item associated with the credit memo part item.  | [optional] 
**tax_item_id** | **str** | The ID of the invoice or debit memo taxation item associated with the credit memo taxation item. | [optional] 
**updated_by_id** | **str** | The ID of the Zuora user who last updated the credit memo part item.  | [optional] 
**updated_date** | **str** | The date and time when the credit memo part item was last updated, in &#x60;yyyy-mm-dd hh:mm:ss&#x60; format. For example, 2017-03-02 15:36:10. | [optional] 
**organization_label** | **str** | organizationLabel.  | [optional] 

## Example

```python
from zuora_sdk.models.credit_memo_item_part import CreditMemoItemPart

# TODO update the JSON string below
json = "{}"
# create an instance of CreditMemoItemPart from a JSON string
credit_memo_item_part_instance = CreditMemoItemPart.from_json(json)
# print the JSON string representation of the object
print(CreditMemoItemPart.to_json())

# convert the object into a dict
credit_memo_item_part_dict = credit_memo_item_part_instance.to_dict()
# create an instance of CreditMemoItemPart from a dict
credit_memo_item_part_from_dict = CreditMemoItemPart.from_dict(credit_memo_item_part_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


