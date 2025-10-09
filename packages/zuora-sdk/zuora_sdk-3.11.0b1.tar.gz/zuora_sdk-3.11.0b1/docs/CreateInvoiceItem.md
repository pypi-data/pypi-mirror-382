# CreateInvoiceItem


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**integration_id__ns** | **str** | ID of the corresponding object in NetSuite. Only available if you have installed the [Zuora Connector for NetSuite](https://www.zuora.com/connect/app/?appId&#x3D;265). | [optional] 
**integration_status__ns** | **str** | Status of the invoice item&#39;s synchronization with NetSuite. Only available if you have installed the [Zuora Connector for NetSuite](https://www.zuora.com/connect/app/?appId&#x3D;265). | [optional] 
**sync_date__ns** | **str** | Date when the invoice item was synchronized with NetSuite. Only available if you have installed the [Zuora Connector for NetSuite](https://www.zuora.com/connect/app/?appId&#x3D;265). | [optional] 
**accounting_code** | **str** | The accounting code associated with the invoice item.  | [optional] 
**adjustment_liability_accounting_code** | **str** | The accounting code for adjustment liability.         **Note**: This field is only available if you have the Billing - Revenue Integration feature enabled.   | [optional] 
**adjustment_revenue_accounting_code** | **str** | The accounting code for adjustment revenue.         **Note**: This field is only available if you have the Billing - Revenue Integration feature enabled.   | [optional] 
**amount** | **decimal.Decimal** | The amount of the invoice item.   - For tax-inclusive invoice items, the amount indicates the invoice item amount including tax.  - For tax-exclusive invoice items, the amount indicates the invoice item amount excluding tax.  | 
**booking_reference** | **str** | The booking reference of the invoice item. | [optional] 
**charge_date** | **str** | The date when the invoice item is charged, in &#x60;yyyy-mm-dd hh:mm:ss&#x60; format. | [optional] 
**charge_name** | **str** | The name of the charge associated with the invoice item.   This field is required if the &#x60;productRatePlanChargeId&#x60; field is not specified in the request.  | [optional] 
**contract_asset_accounting_code** | **str** | The accounting code for contract asset.         **Note**: This field is only available if you have the Billing - Revenue Integration feature enabled.   | [optional] 
**contract_liability_accounting_code** | **str** | The accounting code for contract liability.         **Note**: This field is only available if you have the Billing - Revenue Integration feature enabled.   | [optional] 
**contract_recognized_revenue_accounting_code** | **str** | The accounting code for contract recognized revenue.         **Note**: This field is only available if you have the Billing - Revenue Integration feature enabled.   | [optional] 
**deferred_revenue_accounting_code** | **str** | The accounting code for the deferred revenue, such as Monthly Recurring Liability.  **Note:** This field is only available if you have Zuora Finance enabled.  | [optional] 
**description** | **str** | The description of the invoice item.  | [optional] 
**discount_items** | [**List[CreateDiscountItem]**](CreateDiscountItem.md) | Container for discount items. The maximum number of discount items is 10.  | [optional] 
**exclude_item_billing_from_revenue_accounting** | **bool** | The flag to exclude the invoice item from revenue accounting.  **Note**: This field is only available if you have the Billing - Revenue Integration feature enabled.   | [optional] 
**item_type** | **str** | The type of the invoice item.  | [optional] 
**product_rate_plan_charge_id** | **str** | The ID of the product rate plan charge that the invoice item is created from.  If you specify a value for the &#x60;productRatePlanChargeId&#x60; field in the request, Zuora directly copies the values of the following fields from the corresponding product rate plan charge, regardless of the values specified in the request body: - &#x60;chargeName&#x60; - &#x60;sku&#x60; - &#x60;uom&#x60; - &#x60;taxCode&#x60; - &#x60;taxMode&#x60; - &#x60;accountingCode&#x60; - &#x60;deferredRevenueAccountingCode&#x60;  - &#x60;recognizedRevenueAccountingCode&#x60;  | [optional] 
**purchase_order_number** | **str** | The purchase order number associated with the invoice item.  | [optional] 
**quantity** | **float** | The number of units for the invoice item. | [optional] [default to 1]
**recognized_revenue_accounting_code** | **str** | The accounting code for the recognized revenue, such as Monthly Recurring Charges or Overage Charges.  **Note:** This field is only available if you have Zuora Finance enabled.  | [optional] 
**rev_rec_code** | **str** | The revenue recognition code.  | [optional] 
**rev_rec_trigger_condition** | [**RevRecTrigger**](RevRecTrigger.md) |  | [optional] 
**revenue_recognition_rule_name** | **str** | The name of the revenue recognition rule governing the revenue schedule.  **Note:** This field is only available if you have Zuora Finance enabled.  | [optional] 
**service_end_date** | **date** | The service end date of the invoice item.  | [optional] 
**service_start_date** | **date** | The service start date of the invoice item.  | 
**sku** | **str** | The SKU of the invoice item. The SKU of the invoice item must be different from the SKU of any existing product.  | [optional] 
**tax_code** | **str** | The tax code identifies which tax rules and tax rates to apply to the invoice item.  **Note**: This field is only available only if you have Taxation enabled.  | [optional] 
**tax_items** | [**List[CreateTaxationItem]**](CreateTaxationItem.md) | Container for taxation items. The maximum number of taxation items is 5.  **Note**: This field is only available only if you have Taxation enabled.  | [optional] 
**tax_mode** | [**TaxMode**](TaxMode.md) |  | [optional] 
**unbilled_receivables_accounting_code** | **str** | The accounting code for unbilled receivables.         **Note**: This field is only available if you have the Billing - Revenue Integration feature enabled.   | [optional] 
**unit_price** | **float** | The per-unit price of the invoice item. To pass Level 3 data to the gateway, this field is required and must be greater than zero.  | [optional] 
**uom** | **str** | The unit of measure.  | [optional] 

## Example

```python
from zuora_sdk.models.create_invoice_item import CreateInvoiceItem

# TODO update the JSON string below
json = "{}"
# create an instance of CreateInvoiceItem from a JSON string
create_invoice_item_instance = CreateInvoiceItem.from_json(json)
# print the JSON string representation of the object
print(CreateInvoiceItem.to_json())

# convert the object into a dict
create_invoice_item_dict = create_invoice_item_instance.to_dict()
# create an instance of CreateInvoiceItem from a dict
create_invoice_item_from_dict = CreateInvoiceItem.from_dict(create_invoice_item_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


