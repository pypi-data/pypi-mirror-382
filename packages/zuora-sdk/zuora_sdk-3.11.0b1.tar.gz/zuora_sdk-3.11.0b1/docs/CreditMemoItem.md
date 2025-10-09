# CreditMemoItem


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**amount** | **float** | The amount of the credit memo item. For tax-inclusive credit memo items, the amount indicates the credit memo item amount including tax. For tax-exclusive credit memo items, the amount indicates the credit memo item amount excluding tax. | [optional] 
**amount_without_tax** | **float** | The credit memo item amount excluding tax. | [optional] 
**applied_amount** | **float** | The applied amount of the credit memo item. | [optional] 
**applied_to_item_id** | **str** | The unique ID of the credit memo item that the discount charge is applied to. | [optional] 
**comment** | **str** | Comments about the credit memo item. **Note**: This field is not available if you set the &#x60;zuora-version&#x60; request header to &#x60;257.0&#x60; or later. | [optional] 
**created_by_id** | **str** | The ID of the Zuora user who created the credit memo item. | [optional] 
**created_date** | **str** | The date and time when the credit memo item was created, in &#x60;yyyy-mm-dd hh:mm:ss&#x60; format. For example, 2017-03-01 15:31:10. | [optional] 
**credit_from_item_id** | **str** | The ID of the credit from item. | [optional] 
**credit_from_item_source** | **str** | The type of the credit from item. | [optional] 
**credit_tax_items** | [**List[GetCreditMemoTaxItemResponse]**](GetCreditMemoTaxItemResponse.md) | Container for the taxation items of the credit memo item.   **Note**: This field is not available if you set the &#x60;zuora-version&#x60; request header to &#x60;239.0&#x60; or later.  | [optional] 
**description** | **str** | The description of the credit memo item. **Note**: This field is only available if you set the &#x60;zuora-version&#x60; request header to &#x60;257.0&#x60; or later. | [optional] 
**exclude_item_billing_from_revenue_accounting** | **bool** | The flag to exclude the credit memo item from revenue accounting.  **Note**: This field is only available if you have the Billing - Revenue Integration feature enabled.   | [optional] 
**finance_information** | [**CreditMemoItemFinanceInformation**](CreditMemoItemFinanceInformation.md) |  | [optional] 
**id** | **str** | The ID of the credit memo item. | [optional] 
**invoice_schedule_id** | **str** | The ID of the invoice schedule associated with the credit memo item.   **Note**: This field is available only if you have the &lt;a href&#x3D;\&quot;https://knowledgecenter.zuora.com/Billing/Billing_and_Payments/Billing_Schedule\&quot; target&#x3D;\&quot;_blank\&quot;&gt;Billing Schedule&lt;/a&gt; feature enabled.  | [optional] 
**invoice_schedule_item_id** | **str** | The ID of the invoice schedule item associated with the credit memo item. The credit memo item is generated during the processing of the invoice schedule item. **Note**: This field is available only if you have the &lt;a href&#x3D;\&quot;https://knowledgecenter.zuora.com/Billing/Billing_and_Payments/Billing_Schedule\&quot; target&#x3D;\&quot;_blank\&quot;&gt;Billing Schedule&lt;/a&gt; feature enabled. | [optional] 
**processing_type** | [**BillingDocumentItemProcessingType**](BillingDocumentItemProcessingType.md) |  | [optional] 
**quantity** | **float** | The number of units for the credit memo item. | [optional] 
**refund_amount** | **float** | The amount of the refund on the credit memo item. | [optional] 
**service_end_date** | **date** | The service end date of the credit memo item.   | [optional] 
**service_start_date** | **date** | The service start date of the credit memo item. | [optional] 
**ship_to_contact_id** | **str** | The ID of the ship-to contact associated with the credit memo item. **Note**: If you have the Flexible Billing Attributes feature disabled, the value of this field is &#x60;null&#x60;. | [optional] 
**sku** | **str** | The SKU for the product associated with the credit memo item. | [optional] 
**sku_name** | **str** | The name of the SKU. | [optional] 
**sold_to_contact_id** | **str** | The ID of the sold-to contact associated with the credit memo item. **Note**: If you have the Flexible Billing Attributes feature disabled, the value of this field is &#x60;null&#x60;. | [optional] 
**sold_to_contact_snapshot_id** | **str** | The ID of the sold-to contact snapshot associated with the credit memo item. **Note**: If you have the Flexible Billing Attributes feature disabled, the value of this field is &#x60;null&#x60;. | [optional] 
**source_item_id** | **str** | The ID of the source item. - If the value of the &#x60;sourceItemType&#x60; field is &#x60;SubscriptionComponent&#x60; , the value of this field is the ID of the corresponding rate plan charge. - If the value of the &#x60;sourceItemType&#x60; field is &#x60;InvoiceDetail&#x60;, the value of this field is the ID of the corresponding invoice item. - If the value of the &#x60;sourceItemType&#x60; field is &#x60;ProductRatePlanCharge&#x60; , the value of this field is the ID of the corresponding product rate plan charge. - If the value of the &#x60;sourceItemType&#x60; field is &#x60;OrderLineItem&#x60; , the value of this field is the ID of the corresponding return order line item.  | [optional] 
**source_item_type** | [**BillingDocumentItemSourceType**](BillingDocumentItemSourceType.md) |  | [optional] 
**subscription_id** | **str** | The ID of the subscription associated with the credit memo item. | [optional] 
**tax_mode** | [**TaxMode**](TaxMode.md) |  | [optional] 
**taxation_items** | [**GetCreditMemoItemTaxationItems**](GetCreditMemoItemTaxationItems.md) |  | [optional] 
**unapplied_amount** | **float** | The unapplied amount of the credit memo item. | [optional] 
**unit_of_measure** | **str** | The units to measure usage. | [optional] 
**unit_price** | **float** | The per-unit price of the credit memo item. | [optional] 
**updated_by_id** | **str** | The ID of the Zuora user who last updated the credit memo item. | [optional] 
**updated_date** | **str** | The date and time when the credit memo item was last updated, in &#x60;yyyy-mm-dd hh:mm:ss&#x60; format. For example, 2017-03-02 15:36:10. | [optional] 
**order_line_item_id** | **str** | orderLineItemId  | [optional] 
**item_type** | **str** | itemType  | [optional] 
**purchase_order_number** | **str** | purchaseOrderNumber  | [optional] 
**fulfillment_id** | **str** | fulfillmentId  | [optional] 
**number_of_deliveries** | **float** | The number of delivery for charge.  **Note**: This field is available only if you have the Delivery Pricing feature enabled.  | [optional] 
**reflect_discount_in_net_amount** | **bool** | The flag to reflect Discount in Apply To Charge Net Amount.  | [optional] 
**revenue_impacting** | [**MemoDetailRevenueImpacting**](MemoDetailRevenueImpacting.md) |  | [optional] 

## Example

```python
from zuora_sdk.models.credit_memo_item import CreditMemoItem

# TODO update the JSON string below
json = "{}"
# create an instance of CreditMemoItem from a JSON string
credit_memo_item_instance = CreditMemoItem.from_json(json)
# print the JSON string representation of the object
print(CreditMemoItem.to_json())

# convert the object into a dict
credit_memo_item_dict = credit_memo_item_instance.to_dict()
# create an instance of CreditMemoItem from a dict
credit_memo_item_from_dict = CreditMemoItem.from_dict(credit_memo_item_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


