# CreateDiscountItem


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**integration_id__ns** | **str** | ID of the corresponding object in NetSuite. Only available if you have installed the [Zuora Connector for NetSuite](https://www.zuora.com/connect/app/?appId&#x3D;265). | [optional] 
**integration_status__ns** | **str** | Status of the invoice item&#39;s synchronization with NetSuite. Only available if you have installed the [Zuora Connector for NetSuite](https://www.zuora.com/connect/app/?appId&#x3D;265). | [optional] 
**sync_date__ns** | **str** | Date when the invoice item was synchronized with NetSuite. Only available if you have installed the [Zuora Connector for NetSuite](https://www.zuora.com/connect/app/?appId&#x3D;265). | [optional] 
**accounting_code** | **str** | The accounting code associated with the discount item.  | [optional] 
**accounts_receivable_accounting_code** | **str** | The accounting code for accounts receivable.  | [optional] 
**adjustment_liability_accounting_code** | **str** | The accounting code for adjustment liability. **Note**: This field is only available if you have the Billing - Revenue Integration feature enabled.  | [optional] 
**adjustment_revenue_accounting_code** | **str** | The accounting code for adjustment revenue. **Note**: This field is only available if you have the Billing - Revenue Integration feature enabled.  | [optional] 
**amount** | **decimal.Decimal** | The amount of the discount item. - Should be a negative number. For example, &#x60;-10&#x60;. - Always a fixed amount no matter whether the discount charge associated with the discount item uses the [fixed-amount model or percentage model](https://knowledgecenter.zuora.com/Billing/Subscriptions/Product_Catalog/B_Charge_Models/B_Discount_Charge_Models#Fixed_amount_model_and_percentage_model). - For tax-exclusive discount items, this amount indicates the discount item amount excluding tax. - For tax-inclusive discount items, this amount indicates the discount item amount including tax.  | 
**booking_reference** | **str** | The booking reference of the discount item.  | [optional] 
**charge_date** | **str** | The date when the discount item is charged, in &#x60;yyyy-mm-dd hh:mm:ss&#x60; format. | [optional] 
**charge_name** | **str** | The name of the charge associated with the discount item. This field is required if the &#x60;productRatePlanChargeId&#x60; field is not specified in the request body.  | [optional] 
**contract_asset_accounting_code** | **str** | The accounting code for contract asset. **Note**: This field is only available if you have the Billing - Revenue Integration feature enabled.  | [optional] 
**contract_liability_accounting_code** | **str** | The accounting code for contract liability. **Note**: This field is only available if you have the Billing - Revenue Integration feature enabled.  | [optional] 
**contract_recognized_revenue_accounting_code** | **str** | The accounting code for contract recognized revenue. **Note**: This field is only available if you have the Billing - Revenue Integration feature enabled.  | [optional] 
**deferred_revenue_accounting_code** | **str** | The accounting code for the deferred revenue, such as Monthly Recurring Liability. **Note:** This field is only available if you have Zuora Finance enabled.  | [optional] 
**description** | **str** | The description of the discount item.  | [optional] 
**item_type** | **str** | The type of the discount item.  | [optional] 
**product_rate_plan_charge_id** | **str** | The ID of the product rate plan charge that the discount item is created from.  If you specify a value for the &#x60;productRatePlanChargeId&#x60; field in the request, Zuora directly copies the values of the following fields from the corresponding product rate plan charge, regardless of the values specified in the request body: - &#x60;chargeName&#x60; - &#x60;sku&#x60;  If you specify a value for the &#x60;productRatePlanChargeId&#x60; field in the request, Zuora directly copies the values of the following fields from the corresponding discount charge that [uses discount specific accounting codes, rule and segment to manage revenue](https://knowledgecenter.zuora.com/Billing/Subscriptions/Product_Catalog/B_Charge_Models/Manage_Discount_Charges#Use_discount_specific_accounting_codes.2C_rule_and_segment_to_manage_revenue), regardless of the values specified in the request body: - &#x60;accountingCode&#x60; - &#x60;deferredRevenueAccountingCode&#x60; - &#x60;recognizedRevenueAccountingCode&#x60;  If you specify a value for the &#x60;productRatePlanChargeId&#x60; field in the request, Zuora directly copies the values of the following fields from the corresponding invoice item charge if the discount charge DOES NOT [use discount specific accounting codes, rule and segment to manage revenue](https://knowledgecenter.zuora.com/Billing/Subscriptions/Product_Catalog/B_Charge_Models/Manage_Discount_Charges#Use_discount_specific_accounting_codes.2C_rule_and_segment_to_manage_revenue), regardless of the values specified in the request body: - &#x60;accountingCode&#x60; - &#x60;deferredRevenueAccountingCode&#x60; - &#x60;recognizedRevenueAccountingCode&#x60;  | [optional] 
**purchase_order_number** | **str** | The purchase order number associated with the discount item.  | [optional] 
**recognized_revenue_accounting_code** | **str** | The accounting code for the recognized revenue, such as Monthly Recurring Charges or Overage Charges. **Note:** This field is only available if you have Zuora Finance enabled.  | [optional] 
**rev_rec_code** | **str** | The revenue recognition code.  | [optional] 
**rev_rec_trigger_condition** | [**RevRecTrigger**](RevRecTrigger.md) |  | [optional] 
**revenue_recognition_rule_name** | **str** | The name of the revenue recognition rule governing the revenue schedule. **Note:** This field is only available if you have Zuora Finance enabled.  | [optional] 
**sku** | **str** | The SKU of the invoice item. The SKU of the discount item must be different from the SKU of any existing product.  | [optional] 
**tax_items** | [**List[CreateTaxationItem]**](CreateTaxationItem.md) | Container for taxation items. The maximum number of taxation items is 5.  **Note**: This field is only available only if you have Taxation enabled.  | [optional] 
**unbilled_receivables_accounting_code** | **str** | The accounting code for unbilled receivables. **Note**: This field is only available if you have the Billing - Revenue Integration feature enabled.  | [optional] 
**unit_price** | **decimal.Decimal** | The per-unit price of the discount item. If the discount charge associated with the discount item uses the percentage model, the unit price will display as a percentage amount in PDF. For example: if unit price is 5.00, it will display as 5.00% in PDF.  | [optional] 

## Example

```python
from zuora_sdk.models.create_discount_item import CreateDiscountItem

# TODO update the JSON string below
json = "{}"
# create an instance of CreateDiscountItem from a JSON string
create_discount_item_instance = CreateDiscountItem.from_json(json)
# print the JSON string representation of the object
print(CreateDiscountItem.to_json())

# convert the object into a dict
create_discount_item_dict = create_discount_item_instance.to_dict()
# create an instance of CreateDiscountItem from a dict
create_discount_item_from_dict = CreateDiscountItem.from_dict(create_discount_item_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


