# PreviewExistingSubscriptionInvoiceItemResult


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**service_start_date** | **date** | Service start date as yyyy-mm-dd. If the charge is a one-time fee, this is the date of that charge. | [optional] 
**service_end_date** | **date** | End date of the service period for this item, i.e., the last day of the period, as yyyy-mm-dd. | [optional] 
**amount_without_tax** | **float** | Invoice amount minus tax. | [optional] 
**tax_amount** | **float** | The tax amount of the invoice item. | [optional] 
**charge_description** | **str** | Description of the charge. | [optional] 
**charge_name** | **str** | Name of the charge. | [optional] 
**charge_number** | **str** | Available when the chargeNumber was specified in the request or when the order is amending an existing subscription. | [optional] 
**product_name** | **str** | Name of the product. | [optional] 
**product_rate_plan_charge_id** | **str** | The ID of the product rate plan charge. | [optional] 
**processing_type** | [**InvoiceItemPreviewResultProcessingType**](InvoiceItemPreviewResultProcessingType.md) |  | [optional] 
**unit_price** | **float** | The unit price of the charge. | [optional] 
**quantity** | **float** | The quantity of the charge. | [optional] 
**unit_of_measure** | **str** | The unit of measure of the charge. | [optional] 
**discount_details** | [**List[PreviewExistingSubscriptionDiscountDetails]**](PreviewExistingSubscriptionDiscountDetails.md) | Container for discount details. | [optional] 

## Example

```python
from zuora_sdk.models.preview_existing_subscription_invoice_item_result import PreviewExistingSubscriptionInvoiceItemResult

# TODO update the JSON string below
json = "{}"
# create an instance of PreviewExistingSubscriptionInvoiceItemResult from a JSON string
preview_existing_subscription_invoice_item_result_instance = PreviewExistingSubscriptionInvoiceItemResult.from_json(json)
# print the JSON string representation of the object
print(PreviewExistingSubscriptionInvoiceItemResult.to_json())

# convert the object into a dict
preview_existing_subscription_invoice_item_result_dict = preview_existing_subscription_invoice_item_result_instance.to_dict()
# create an instance of PreviewExistingSubscriptionInvoiceItemResult from a dict
preview_existing_subscription_invoice_item_result_from_dict = PreviewExistingSubscriptionInvoiceItemResult.from_dict(preview_existing_subscription_invoice_item_result_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


