# UpdateDebitMemoItem


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**amount** | **float** | The amount of the debit memo item. For tax-inclusive debit memo items, the amount indicates the debit memo item amount including tax. For tax-exclusive debit memo items, the amount indicates the debit memo item amount excluding tax. | [optional] 
**comment** | **str** | Comments about the debit memo item. | [optional] 
**delete** | **bool** | Whether to delete the existing debit memo item. **Note**: This field is available only if id is not null. | [optional] 
**exclude_item_billing_from_revenue_accounting** | **bool** | The flag to exclude the debit memo item from revenue accounting.  **Note**: This field is only available if you have the Billing - Revenue Integration feature enabled.              | [optional] 
**finance_information** | [**DebitMemoItemFromInvoiceItemFinanceInformation**](DebitMemoItemFromInvoiceItemFinanceInformation.md) |  | [optional] 
**id** | **str** | The ID of the debit memo item. | 
**product_rate_plan_charge_id** | **str** | The ID of the product rate plan charge that the debit memo is created from. **Note**: This field is available only if id is null. | [optional] 
**quantity** | **float** | The number of units for the debit memo item. | [optional] 
**service_end_date** | **date** | The service end date of the debit memo item. | [optional] 
**service_start_date** | **date** | The service start date of the debit memo item.   | [optional] 
**sku_name** | **str** | The name of the SKU. | [optional] 
**tax_items** | [**List[UpdateDebitMemoTaxItemRequest]**](UpdateDebitMemoTaxItemRequest.md) | Container for debit memo taxation items. | [optional] 
**unit_of_measure** | **str** | The definable unit that you measure when determining charges. | [optional] 

## Example

```python
from zuora_sdk.models.update_debit_memo_item import UpdateDebitMemoItem

# TODO update the JSON string below
json = "{}"
# create an instance of UpdateDebitMemoItem from a JSON string
update_debit_memo_item_instance = UpdateDebitMemoItem.from_json(json)
# print the JSON string representation of the object
print(UpdateDebitMemoItem.to_json())

# convert the object into a dict
update_debit_memo_item_dict = update_debit_memo_item_instance.to_dict()
# create an instance of UpdateDebitMemoItem from a dict
update_debit_memo_item_from_dict = UpdateDebitMemoItem.from_dict(update_debit_memo_item_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


