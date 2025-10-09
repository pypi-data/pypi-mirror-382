# CreateOrderOrderLineItem


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**uom** | **str** | Specifies the units to measure usage.  | [optional] 
**accounting_code** | **str** | The accounting code for the Order Line Item.  | [optional] 
**adjustment_liability_accounting_code** | **str** | The accounting code on the Order Line Item object for customers using [Zuora Billing - Revenue Integration](https://knowledgecenter.zuora.com/Zuora_Revenue/Zuora_Billing_-_Revenue_Integration).  | [optional] 
**adjustment_revenue_accounting_code** | **str** | The accounting code on the Order Line Item object for customers using [Zuora Billing - Revenue Integration](https://knowledgecenter.zuora.com/Zuora_Revenue/Zuora_Billing_-_Revenue_Integration).  | [optional] 
**currency** | **str** | The currency for the Order Line Item. | [optional] 
**payment_term** | **str** | The payment term for the Order Line Item | [optional] 
**invoice_template_id** | **str** | The invoice template id for the Order Line Item | [optional] 
**communication_profile_id** | **str** | The communication profile id for the Order Line Item. | [optional] 
**amount_per_unit** | **float** | The actual charged amount per unit for the Order Line Item.  If you set the &#x60;inlineDiscountType&#x60;, &#x60;inlineDiscountPerUnit&#x60;, and &#x60;listPricePerUnit&#x60; fields, the system will automatically generate the &#x60;amountPerUnit&#x60; field. You shall not set the &#x60;amountPerUnit&#x60; field by yourself.  | [optional] 
**bill_target_date** | **date** | The target date for the Order Line Item to be picked up by bill run for billing.  | [optional] 
**bill_to** | **str** | The ID of a contact that belongs to the billing account of the order line item. Use this field to assign an existing account as the bill-to contact of an order line item.  | [optional] 
**billing_rule** | [**OrderLineItemBillingRule**](OrderLineItemBillingRule.md) |  | [optional] [default to OrderLineItemBillingRule.TRIGGERWITHOUTFULFILLMENT]
**contract_asset_accounting_code** | **str** | The accounting code on the Order Line Item object for customers using [Zuora Billing - Revenue Integration](https://knowledgecenter.zuora.com/Zuora_Revenue/Zuora_Billing_-_Revenue_Integration).  | [optional] 
**contract_liability_accounting_code** | **str** | The accounting code on the Order Line Item object for customers using [Zuora Billing - Revenue Integration](https://knowledgecenter.zuora.com/Zuora_Revenue/Zuora_Billing_-_Revenue_Integration).  | [optional] 
**contract_recognized_revenue_accounting_code** | **str** | The accounting code on the Order Line Item object for customers using [Zuora Billing - Revenue Integration](https://knowledgecenter.zuora.com/Zuora_Revenue/Zuora_Billing_-_Revenue_Integration).  | [optional] 
**custom_fields** | **Dict[str, object]** | Container for custom fields of an Order Line Item object.  | [optional] 
**deferred_revenue_accounting_code** | **str** | The deferred revenue accounting code for the Order Line Item.  | [optional] 
**description** | **str** | The description of the Order Line Item.  | [optional] 
**exclude_item_billing_from_revenue_accounting** | **bool** | The flag to exclude Order Line Item related invoice items, invoice item adjustments, credit memo items, and debit memo items from revenue accounting.   **Note**: This field is only available if you have the Billing - Revenue Integration feature enabled.   | [optional] 
**exclude_item_booking_from_revenue_accounting** | **bool** | The flag to exclude Order Line Item from revenue accounting.  **Note**: This field is only available if you have the Billing - Revenue Integration feature enabled.  | [optional] 
**inline_discount_per_unit** | **float** | Use this field in accordance with the &#x60;inlineDiscountType&#x60; field, in the following manner: * If the &#x60;inlineDiscountType&#x60; field is set as &#x60;Percentage&#x60;, this field specifies the discount percentage for each unit of the order line item. For exmaple, if you specify &#x60;5&#x60; in this field, the discount percentage is 5%. * If the &#x60;inlineDiscountType&#x60; field is set as &#x60;FixedAmount&#x60;, this field specifies the discount amount on each unit of the order line item. For exmaple, if you specify &#x60;10&#x60; in this field, the discount amount on each unit of the order line item is 10.  Once you set the &#x60;inlineDiscountType&#x60;, &#x60;inlineDiscountPerUnit&#x60;, and &#x60;listPricePerUnit&#x60; fields, the system will automatically generate the &#x60;amountPerUnit&#x60; field. You shall not set the &#x60;amountPerUnit&#x60; field by yourself.  | [optional] 
**inline_discount_type** | [**OrderLineItemInlineDiscountType**](OrderLineItemInlineDiscountType.md) |  | [optional] 
**invoice_group_number** | **str** | The invoice group number associated with the order line item.  | [optional] 
**is_allocation_eligible** | **bool** | This field is used to identify if the charge segment is allocation eligible in revenue recognition.  **Note**: This feature is in the **Early Adopter** phase. If you want to use the feature, submit a request at &lt;a href&#x3D;\&quot;https://support.zuora.com/\&quot; target&#x3D;\&quot;_blank\&quot;&gt;Zuora Global Support&lt;/a&gt;, and we will evaluate whether the feature is suitable for your use cases.  | [optional] 
**is_unbilled** | **bool** | This field is used to dictate how to perform the accounting during revenue recognition.  **Note**: This feature is in the **Early Adopter** phase. If you want to use the feature, submit a request at &lt;a href&#x3D;\&quot;https://support.zuora.com/\&quot; target&#x3D;\&quot;_blank\&quot;&gt;Zuora Global Support&lt;/a&gt;, and we will evaluate whether the feature is suitable for your use cases.  | [optional] 
**item_category** | [**OrderLineItemCategory**](OrderLineItemCategory.md) |  | [optional] [default to OrderLineItemCategory.SALES]
**item_name** | **str** | The name of the Order Line Item.  | [optional] 
**item_number** | **str** | The number of the Order Line Item. Use this field to specify a custom item number for your Order Line Item. If you are to use this field,  you must set all the item numbers in an order when there are several order line items in the order.  | [optional] 
**item_state** | [**OrderLineItemState**](OrderLineItemState.md) |  | [optional] 
**item_type** | [**OrderLineItemType**](OrderLineItemType.md) |  | [optional] 
**list_price_per_unit** | **float** | The list price per unit for the Order Line Item.  | [optional] 
**original_order_line_item_number** | **str** | The number of the original sale order line item for a return order line item.   | [optional] 
**original_order_number** | **str** | The number of the original sale order for a return order line item.   | [optional] 
**owner_account_number** | **str** | Use this field to assign an existing account as the owner of an order line item.  | [optional] 
**product_code** | **str** | The product code for the Order Line Item.  | [optional] 
**product_rate_plan_charge_id** | **str** | Id of a Product Rate Plan Charge. Only one-time charges are supported.  | [optional] 
**purchase_order_number** | **str** | Used by customers to specify the Purchase Order Number provided by the buyer.  | [optional] 
**quantity** | **float** | The quantity of units, such as the number of authors in a hosted wiki service.  | [optional] 
**recognized_revenue_accounting_code** | **str** | The recognized revenue accounting code for the Order Line Item.  | [optional] 
**related_subscription_number** | **str** | Use this field to relate an order line item to a subscription when you create the order line item.  * To relate an order line item to a new subscription which is yet to create in the same \&quot;Create an order\&quot; call, use this field in combination with the &#x60;subscriptions&#x60; &gt; &#x60;subscriptionNumber&#x60; field in the \&quot;Create an order\&quot; operation. Specify this field to the same value as that of the &#x60;subscriptions&#x60; &gt; &#x60;subscriptionNumber&#x60; field when you make the \&quot;Create an order\&quot; call. * To relate an order line item to an existing subscription, specify this field to the subscription number of the existing subscription.  | [optional] 
**revenue_recognition_rule** | **str** | The Revenue Recognition rule for the Order Line Item.  | [optional] 
**sequence_set_id** | **str** | The ID of the sequence set associated with the OrderLineItem.  | [optional] 
**sold_to** | **str** | Use this field to assign an existing account as the sold-to contact of an order line item, by the following rules:  * If the &#x60;ownerAccountNumber&#x60; field is set, then this field must be the ID of a contact that belongs to the owner account of the order line item.  * If the &#x60;ownerAccountNumber&#x60; field is not set, then this field must be the ID of a contact that belongs to the billing account of the order line item.  | [optional] 
**ship_to** | **str** | Use this field to assign an existing account contact as the ship-to contact of an order line item | [optional] 
**tax_code** | **str** | The tax code for the Order Line Item.  | [optional] 
**tax_mode** | [**TaxMode**](TaxMode.md) |  | [optional] 
**transaction_end_date** | **date** | The date a transaction is completed. The default value of this field is the transaction start date. Also, the value of this field should always equal or be later than the value of the &#x60;transactionStartDate&#x60; field.  | [optional] 
**transaction_start_date** | **date** | The date a transaction starts. The default value of this field is the order date.  | [optional] 
**unbilled_receivables_accounting_code** | **str** | The accounting code on the Order Line Item object for customers using [Zuora Billing - Revenue Integration](https://knowledgecenter.zuora.com/Zuora_Revenue/Zuora_Billing_-_Revenue_Integration).  | [optional] 
**unique_token** | **str** | uniqueToken of the OLI to set relatedSubscriptionNumber in OLI within same order. Unique token should be a valid value (It should belong to any of the create sub order action with in same order).  | [optional] 

## Example

```python
from zuora_sdk.models.create_order_order_line_item import CreateOrderOrderLineItem

# TODO update the JSON string below
json = "{}"
# create an instance of CreateOrderOrderLineItem from a JSON string
create_order_order_line_item_instance = CreateOrderOrderLineItem.from_json(json)
# print the JSON string representation of the object
print(CreateOrderOrderLineItem.to_json())

# convert the object into a dict
create_order_order_line_item_dict = create_order_order_line_item_instance.to_dict()
# create an instance of CreateOrderOrderLineItem from a dict
create_order_order_line_item_from_dict = CreateOrderOrderLineItem.from_dict(create_order_order_line_item_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


