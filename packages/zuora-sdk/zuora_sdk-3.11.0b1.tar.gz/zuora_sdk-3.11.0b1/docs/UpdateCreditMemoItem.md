# UpdateCreditMemoItem


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**amount** | **float** | The amount of the credit memo item. For tax-inclusive credit memo items, the amount indicates the credit memo item amount including tax. For tax-exclusive credit memo items, the amount indicates the credit memo item amount excluding tax | [optional] 
**comment** | **str** | Comments about the credit memo item. | [optional] 
**delete** | **bool** | Whether to delete the existing credit memo item. **Note**: This field is available only if id is not null. | [optional] 
**exclude_item_billing_from_revenue_accounting** | **bool** | The flag to exclude the credit memo item from revenue accounting.  **Note**: This field is only available if you have the Billing - Revenue Integration feature enabled.   | [optional] 
**finance_information** | [**CreditMemoItemFromInvoiceItemFinanceInformation**](CreditMemoItemFromInvoiceItemFinanceInformation.md) |  | [optional] 
**id** | **str** | The ID of the credit memo item. | 
**quantity** | **float** | The number of units for the credit memo item. | [optional] 
**product_rate_plan_charge_id** | **str** | The ID of the product rate plan charge that the credit memo is created from. **Note**: This field is available only if id is null. | [optional] 
**service_end_date** | **date** | The service end date of the credit memo item. | [optional] 
**service_start_date** | **date** | The service start date of the credit memo item. | [optional] 
**sku_name** | **str** | The name of the SKU. | [optional] 
**tax_items** | [**List[UpdateCreditMemoTaxItemRequest]**](UpdateCreditMemoTaxItemRequest.md) | Container for credit memo taxation items. | [optional] 
**unit_of_measure** | **str** | The definable unit that you measure when determining charges. | [optional] 

## Example

```python
from zuora_sdk.models.update_credit_memo_item import UpdateCreditMemoItem

# TODO update the JSON string below
json = "{}"
# create an instance of UpdateCreditMemoItem from a JSON string
update_credit_memo_item_instance = UpdateCreditMemoItem.from_json(json)
# print the JSON string representation of the object
print(UpdateCreditMemoItem.to_json())

# convert the object into a dict
update_credit_memo_item_dict = update_credit_memo_item_instance.to_dict()
# create an instance of UpdateCreditMemoItem from a dict
update_credit_memo_item_from_dict = UpdateCreditMemoItem.from_dict(update_credit_memo_item_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


