# PaymentPart


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**amount** | **float** | The amount of the payment part.  | [optional] 
**created_by_id** | **str** | The ID of the Zuora user who created the payment part.  | [optional] 
**created_date** | **str** | The date and time when the payment part was created, in &#x60;yyyy-mm-dd hh:mm:ss&#x60; format. For example, 2017-03-01 15:31:10. | [optional] 
**debit_memo_id** | **str** | The ID of the debit memo associated with the payment part.  | [optional] 
**id** | **str** | The ID of the payment part.  | [optional] 
**invoice_id** | **str** | The ID of the invoice associated with the payment part.  | [optional] 
**updated_by_id** | **str** | The ID of the Zuora user who last updated the payment part.  | [optional] 
**updated_date** | **str** | The date and time when the payment part was last updated, in &#x60;yyyy-mm-dd hh:mm:ss&#x60; format. For example, 2017-03-02 15:36:10. | [optional] 
**organization_label** | **str** |  | [optional] 
**billing_document_owner_id** | **str** |  | [optional] 

## Example

```python
from zuora_sdk.models.payment_part import PaymentPart

# TODO update the JSON string below
json = "{}"
# create an instance of PaymentPart from a JSON string
payment_part_instance = PaymentPart.from_json(json)
# print the JSON string representation of the object
print(PaymentPart.to_json())

# convert the object into a dict
payment_part_dict = payment_part_instance.to_dict()
# create an instance of PaymentPart from a dict
payment_part_from_dict = PaymentPart.from_dict(payment_part_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


