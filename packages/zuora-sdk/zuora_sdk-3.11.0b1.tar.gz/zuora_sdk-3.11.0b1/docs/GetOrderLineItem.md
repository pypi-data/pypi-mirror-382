# GetOrderLineItem


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**id** | **str** | The sytem generated Id for the Order Line Item.  | [optional] 
**amended_by_order_on** | **str** | The date when the rate plan charge is amended through an order or amendment. This field is to standardize the booking date information to increase audit ability and traceability of data between Zuora Billing and Zuora Revenue. It is mapped as the booking date for a sale order line in Zuora Revenue. | [optional] 
**currency** | **str** | The currency for the Order Line Item.  | [optional] 
**payment_term** | **str** | The payment term for the Order Line Item  | [optional] 
**invoice_template_id** | **str** | The invoice template id for the Order Line Item  | [optional] 
**communication_profile_id** | **str** | The communication profile id for the Order Line Item.  | [optional] 
**amount** | **float** | The calculated gross amount for the Order Line Item.  | [optional] 
**amount_without_tax** | **float** | The calculated gross amount for an order line item excluding tax. If the tax mode is tax exclusive, the value of this field equals that of the &#x60;amount&#x60; field.   If the tax mode of an order line item is not set, the system treats it as tax exclusive by default. The value of the &#x60;amountWithoutTax&#x60; field equals that of the &#x60;amount&#x60; field.   If you create an order line item from the product catalog, the tax mode and tax code of the product rate plan charge are used for the order line item by default. You can still overwrite this default set-up by setting the tax mode and tax code of the order line item. | [optional] 
**item_number** | **str** | The number for the Order Line Item.  | [optional] 
**uom** | **str** | Specifies the units to measure usage.  | [optional] 
**amount_per_unit** | **float** | The actual charged amount per unit for the Order Line Item.  | [optional] 
**bill_target_date** | **date** | The target date for the Order Line Item to be picked up by bill run for billing.  | [optional] 
**bill_to** | **str** | The ID of a contact that belongs to the billing account of the order line item. Use this field to assign an existing account as the bill-to contact of an order line item.  | [optional] 
**bill_to_snapshot_id** | **str** | The snapshot of the ID for an account used as the sold-to contact of an order line item. This field is used to store the original information about the account, in case the information about the account is changed after the creation of the order line item. The &#x60;billToSnapshotId&#x60; field is exposed while retrieving the order line item details.  | [optional] 
**billing_rule** | [**OrderLineItemBillingRule**](OrderLineItemBillingRule.md) |  | [optional] [default to OrderLineItemBillingRule.TRIGGERWITHOUTFULFILLMENT]
**accounting_code** | **str** | The accounting code for the Order Line Item.  | [optional] 
**adjustment_liability_accounting_code** | **str** | The accounting code on the Order Line Item object for customers using [Zuora Billing - Revenue Integration](https://knowledgecenter.zuora.com/Zuora_Revenue/Zuora_Billing_-_Revenue_Integration).  | [optional] 
**adjustment_revenue_accounting_code** | **str** | The accounting code on the Order Line Item object for customers using [Zuora Billing - Revenue Integration](https://knowledgecenter.zuora.com/Zuora_Revenue/Zuora_Billing_-_Revenue_Integration).  | [optional] 
**contract_asset_accounting_code** | **str** | The accounting code on the Order Line Item object for customers using [Zuora Billing - Revenue Integration](https://knowledgecenter.zuora.com/Zuora_Revenue/Zuora_Billing_-_Revenue_Integration).  | [optional] 
**contract_liability_accounting_code** | **str** | The accounting code on the Order Line Item object for customers using [Zuora Billing - Revenue Integration](https://knowledgecenter.zuora.com/Zuora_Revenue/Zuora_Billing_-_Revenue_Integration).  | [optional] 
**contract_recognized_revenue_accounting_code** | **str** | The accounting code on the Order Line Item object for customers using [Zuora Billing - Revenue Integration](https://knowledgecenter.zuora.com/Zuora_Revenue/Zuora_Billing_-_Revenue_Integration).  | [optional] 
**deferred_revenue_accounting_code** | **str** | The deferred revenue accounting code for the Order Line Item.  | [optional] 
**custom_fields** | **Dict[str, object]** | Container for custom fields of an Order Line Item object.  | [optional] 
**description** | **str** | The description of the Order Line Item.  | [optional] 
**discount** | **float** | This field shows the total discount amount that is applied to an order line item after the &#x60;inlineDiscountType&#x60;, &#x60;inlineDiscountPerUnit&#x60; and &#x60;quantity&#x60; fields are set.  The inline discount is applied to the list price of an order line item (see the &#x60;listPrice&#x60; field).  | [optional] 
**exclude_item_billing_from_revenue_accounting** | **bool** | The flag to exclude Order Line Item related invoice items, invoice item adjustments, credit memo items, and debit memo items from revenue accounting.  **Note**: This field is only available if you have the [Zuora Billing - Revenue Integration](https://knowledgecenter.zuora.com/Zuora_Revenue/Zuora_Billing_-_Revenue_Integration) feature enabled.   | [optional] 
**exclude_item_booking_from_revenue_accounting** | **bool** | The flag to exclude Order Line Item from revenue accounting.  **Note**: This field is only available if you have the [Zuora Billing - Revenue Integration](https://knowledgecenter.zuora.com/Zuora_Revenue/Zuora_Billing_-_Revenue_Integration) feature enabled.   | [optional] 
**revenue_recognition_timing** | **str** | This field is used to dictate the type of revenue recognition timing. | [optional] 
**revenue_amortization_method** | **str** | This field is used to dictate the type of revenue amortization method. | [optional] 
**inline_discount_per_unit** | **float** | This field is used in accordance with the &#x60;inlineDiscountType&#x60; field, in the following manner: * If the &#x60;inlineDiscountType&#x60; field is set as &#x60;Percentage&#x60;, this field specifies the discount percentage for each unit of the order line item. For exmaple, if you specify &#x60;5&#x60; in this field, the discount percentage is 5%. * If the &#x60;inlineDiscountType&#x60; field is set as &#x60;FixedAmount&#x60;, this field specifies the discount amount on each unit of the order line item. For exmaple, if you specify &#x60;10&#x60; in this field, the discount amount on each unit of the order line item is 10.  Once you set the &#x60;inlineDiscountType&#x60;, &#x60;inlineDiscountPerUnit&#x60;, and &#x60;listPricePerUnit&#x60; fields, the system will automatically generate the &#x60;amountPerUnit&#x60; field. You shall not set the &#x60;amountPerUnit&#x60; field by yourself.  | [optional] 
**inline_discount_type** | [**OrderLineItemInlineDiscountType**](OrderLineItemInlineDiscountType.md) |  | [optional] 
**invoice_group_number** | **str** | The invoice group number associated with the order line item.  | [optional] 
**invoice_owner_account_id** | **str** | The account ID of the invoice owner of the order line item.  | [optional] 
**invoice_owner_account_name** | **str** | The account name of the invoice owner of the order line item.  | [optional] 
**invoice_owner_account_number** | **str** | The account number of the invoice owner of the order line item.  | [optional] 
**is_allocation_eligible** | **bool** | This field is used to identify if the charge segment is allocation eligible in revenue recognition.  **Note**: This feature is in the **Early Adopter** phase. If you want to use the feature, submit a request at &lt;a href&#x3D;\&quot;https://support.zuora.com/\&quot; target&#x3D;\&quot;_blank\&quot;&gt;Zuora Global Support&lt;/a&gt;, and we will evaluate whether the feature is suitable for your use cases.  | [optional] 
**is_unbilled** | **bool** | This field is used to dictate how to perform the accounting during revenue recognition.  **Note**: This feature is in the **Early Adopter** phase. If you want to use the feature, submit a request at &lt;a href&#x3D;\&quot;https://support.zuora.com/\&quot; target&#x3D;\&quot;_blank\&quot;&gt;Zuora Global Support&lt;/a&gt;, and we will evaluate whether the feature is suitable for your use cases.  | [optional] 
**item_category** | [**OrderLineItemCategory**](OrderLineItemCategory.md) |  | [optional] [default to OrderLineItemCategory.SALES]
**item_name** | **str** | The name of the Order Line Item.  | [optional] 
**item_state** | [**OrderLineItemState**](OrderLineItemState.md) |  | [optional] 
**item_type** | [**OrderLineItemType**](OrderLineItemType.md) |  | [optional] 
**list_price** | **float** | The extended list price for an order line item, calculated by the formula: listPrice &#x3D; listPricePerUnit * quantity  | [optional] 
**list_price_per_unit** | **float** | The list price per unit for the Order Line Item.  | [optional] 
**original_order_id** | **str** | The ID of the original sale order for a return order line item.   | [optional] 
**original_order_date** | **date** | The date when the rate plan charge is created through an order or amendment. This field is to standardize the booking date information to increase audit ability and traceability of data between Zuora Billing and Zuora Revenue. It is mapped as the booking date for a sale order line in Zuora Revenue. | [optional] 
**original_order_line_item_id** | **str** | The ID of the original sale order line item for a return order line item.   | [optional] 
**original_order_line_item_number** | **str** | The number of the original sale order line item for a return order line item.   | [optional] 
**original_order_number** | **str** | The number of the original sale order for a return order line item.   | [optional] 
**owner_account_id** | **str** | The account ID of the owner of the order line item.  | [optional] 
**owner_account_name** | **str** | The account name of the owner of the order line item.  | [optional] 
**owner_account_number** | **str** | The account number of the owner of the order line item.  | [optional] 
**product_code** | **str** | The product code for the Order Line Item.  | [optional] 
**product_rate_plan_charge_id** | **str** | Id of a Product Rate Plan Charge. Only one-time charges are supported.  | [optional] 
**purchase_order_number** | **str** | Used by customers to specify the Purchase Order Number provided by the buyer.  | [optional] 
**quantity** | **float** | The quantity of units, such as the number of authors in a hosted wiki service.  | [optional] 
**quantity_available_for_return** | **float** | The quantity that can be returned for an order line item.   | [optional] 
**quantity_fulfilled** | **float** | The quantity that has been fulfilled by fulfillments for the order line item. This field will be updated automatically when related fulfillments become &#39;SentToBilling&#39; or &#39;Complete&#39; state. | [optional] 
**quantity_pending_fulfillment** | **float** | The quantity that&#39;s need to be fulfilled by fulfillments for the order line item. This field will be updated automatically when related fulfillments become &#39;SentToBilling&#39; or &#39;Complete&#39; state. | [optional] 
**recognized_revenue_accounting_code** | **str** | The recognized revenue accounting code for the Order Line Item.  | [optional] 
**related_subscription_number** | **str** | Use this field to relate an order line item to a subscription when you create the order line item.  * To relate an order line item to a new subscription which is yet to create in the same \&quot;Create an order\&quot; call, use this field in combination with the &#x60;subscriptions&#x60; &gt; &#x60;subscriptionNumber&#x60; field in the \&quot;Create order\&quot; operation. Specify this field to the same value as that of the &#39;subscriptions&#39; &gt; &#x60;subscriptionNumber&#x60; field when you make the \&quot;Create order\&quot; call. * To relate an order line item to an existing subscription, specify this field to the subscription number of the existing subscription.  | [optional] 
**requires_fulfillment** | **bool** | The flag to show whether fulfillment is needed or not. It&#39;s derived from billing rule of the Order Line Item.  | [optional] 
**revenue_recognition_rule** | **str** | The Revenue Recognition rule for the Order Line Item.  | [optional] 
**sequence_set_id** | **str** | The ID of the sequence set associated with the OrderLineItem.  | [optional] 
**sold_to** | **str** | The ID of a contact that belongs to the owner acount or billing account of the order line item. Use this field to assign an existing account as the sold-to contact of an order line item.  | [optional] 
**sold_to_snapshot_id** | **str** | The snapshot of the ID for an account used as the sold-to contact of an order line item. This field is used to store the original information about the account, in case the information about the account is changed after the creation of the order line item. The &#x60;soldToSnapshotId&#x60; field is exposed while retrieving the order line item details.  | [optional] 
**ship_to** | **str** | The ID of a contact that belongs to the owner account or billing account of the order line item. Use this field to assign an existing account as the ship-to contact of an order line item.  | [optional] 
**ship_to_snapshot_id** | **str** | The snapshot of the ID for an account used as the ship-to contact of an order line item. This field is used to store the original information about the account, in case the information about the account is changed after the creation of the order line item. The &#x60;shipToSnapshotId&#x60; field is exposed while retrieving the order line item details.  | [optional] 
**tax_code** | **str** | The tax code for the Order Line Item.  | [optional] 
**tax_mode** | [**TaxMode**](TaxMode.md) |  | [optional] 
**transaction_end_date** | **date** | The date a transaction is completed. The default value of this field is the transaction start date. Also, the value of this field should always equal or be later than the value of the &#x60;transactionStartDate&#x60; field.  | [optional] 
**transaction_start_date** | **date** | The date a transaction starts. The default value of this field is the order date.  | [optional] 
**unbilled_receivables_accounting_code** | **str** | The accounting code on the Order Line Item object for customers using [Zuora Billing - Revenue Integration](https://knowledgecenter.zuora.com/Zuora_Revenue/Zuora_Billing_-_Revenue_Integration).  | [optional] 
**fulfillments** | [**List[GetFulfillment]**](GetFulfillment.md) | Container for the fulfillments attached to an order line item.  | [optional] 

## Example

```python
from zuora_sdk.models.get_order_line_item import GetOrderLineItem

# TODO update the JSON string below
json = "{}"
# create an instance of GetOrderLineItem from a JSON string
get_order_line_item_instance = GetOrderLineItem.from_json(json)
# print the JSON string representation of the object
print(GetOrderLineItem.to_json())

# convert the object into a dict
get_order_line_item_dict = get_order_line_item_instance.to_dict()
# create an instance of GetOrderLineItem from a dict
get_order_line_item_from_dict = GetOrderLineItem.from_dict(get_order_line_item_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


