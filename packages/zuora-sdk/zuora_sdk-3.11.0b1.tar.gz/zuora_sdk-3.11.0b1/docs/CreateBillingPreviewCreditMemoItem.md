# CreateBillingPreviewCreditMemoItem


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**amount** | **float** | The amount of the credit memo item. For tax-inclusive credit memo items, the amount indicates the credit memo item amount including tax. For tax-exclusive credit memo items, the amount indicates the credit memo item amount excluding tax | [optional] 
**amount_without_tax** | **float** | The credit memo item amount excluding tax.  | [optional] 
**applied_to_item_id** | **str** | The unique ID of the credit memo item that the discount charge is applied to. | [optional] 
**charge_date** | **str** | The date when the credit memo item is created.  | [optional] 
**charge_number** | **str** | Number of the charge.  | [optional] 
**charge_type** | **str** | The type of charge.   Possible values are &#x60;OneTime&#x60;, &#x60;Recurring&#x60;, and &#x60;Usage&#x60;.  | [optional] 
**comment** | **str** | Comment of the credit memo item.  | [optional] 
**id** | **str** | Credit memo item id.  | [optional] 
**number_of_deliveries** | **decimal.Decimal** | The number of delivery for charge.  **Note**: This field is available only if you have the Delivery Pricing feature enabled.  | [optional] 
**processing_type** | **str** | Identifies the kind of charge.   Possible values: * charge * discount * prepayment * tax  | [optional] 
**quantity** | **decimal.Decimal** | Quantity of this item, in the configured unit of measure for the charge.  | [optional] 
**rate_plan_charge_id** | **str** | Id of the rate plan charge associated with this item.  | [optional] 
**service_end_date** | **date** | End date of the service period for this item, i.e., the last day of the service period, in yyyy-mm-dd format. | [optional] 
**service_start_date** | **date** | Start date of the service period for this item, in yyyy-mm-dd format. If the charge is a one-time fee, this is the date of that charge. | [optional] 
**sku** | **str** | Unique SKU for the product associated with this item.  | [optional] 
**sku_name** | **str** | Name of the unique SKU for the product associated with this item.  | [optional] 
**subscription_id** | **str** | ID of the subscription associated with this item.  | [optional] 
**subscription_number** | **str** | Name of the subscription associated with this item.  | [optional] 
**unit_of_measure** | **str** | Unit used to measure consumption.  | [optional] 

## Example

```python
from zuora_sdk.models.create_billing_preview_credit_memo_item import CreateBillingPreviewCreditMemoItem

# TODO update the JSON string below
json = "{}"
# create an instance of CreateBillingPreviewCreditMemoItem from a JSON string
create_billing_preview_credit_memo_item_instance = CreateBillingPreviewCreditMemoItem.from_json(json)
# print the JSON string representation of the object
print(CreateBillingPreviewCreditMemoItem.to_json())

# convert the object into a dict
create_billing_preview_credit_memo_item_dict = create_billing_preview_credit_memo_item_instance.to_dict()
# create an instance of CreateBillingPreviewCreditMemoItem from a dict
create_billing_preview_credit_memo_item_from_dict = CreateBillingPreviewCreditMemoItem.from_dict(create_billing_preview_credit_memo_item_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


