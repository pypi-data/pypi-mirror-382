# Order

Represents the order information that will be returned in the GET call.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**category** | [**OrderCategory**](OrderCategory.md) |  | [optional] [default to OrderCategory.NEWSALES]
**created_by** | **str** | The ID of the user who created this order. | [optional] 
**created_date** | **str** | The time that the order gets created in the system, in the &#x60;YYYY-MM-DD HH:MM:SS&#x60; format. | [optional] 
**currency** | **str** | Currency code. | [optional] 
**custom_fields** | **Dict[str, object]** | Container for custom fields of an Order object.  | [optional] 
**description** | **str** | A description of the order. | [optional] 
**existing_account_number** | **str** | The account number that this order has been created under. This is also the invoice owner of the subscriptions included in this order. | [optional] 
**existing_account_details** | [**OrderExistingAccountDetails**](OrderExistingAccountDetails.md) |  | [optional] 
**invoice_schedule_id** | **str** | The ID of the invoice schedule associated with the order.  **Note**: This field is available only if you have the &lt;a href&#x3D;\&quot;https://knowledgecenter.zuora.com/Billing/Billing_and_Payments/Billing_Schedule\&quot; target&#x3D;\&quot;_blank\&quot;&gt;Billing Schedule&lt;/a&gt; feature in the **Early Adopter** phase enabled.  | [optional] 
**order_date** | **date** | The date when the order is signed. All the order actions under this order will use this order date as the contract effective date if no additinal contractEffectiveDate is provided. | [optional] 
**order_line_items** | [**List[OrderLineItem]**](OrderLineItem.md) | [Order Line Items](https://knowledgecenter.zuora.com/Billing/Subscriptions/Orders/Order_Line_Items/AA_Overview_of_Order_Line_Items) are non subscription based items created by an Order, representing transactional charges such as one-time fees, physical goods, or professional service charges that are not sold as subscription services.   With the Order Line Items feature enabled, you can now launch non-subscription and unified monetization business models in Zuora, in addition to subscription business models.   **Note:** The [Order Line Items](https://knowledgecenter.zuora.com/Billing/Subscriptions/Orders/Order_Line_Items/AA_Overview_of_Order_Line_Items) feature is now generally available to all Zuora customers. You need to enable the [Orders](https://knowledgecenter.zuora.com/BC_Subscription_Management/Orders/AA_Overview_of_Orders#Orders) feature to access the [Order Line Items](https://knowledgecenter.zuora.com/Billing/Subscriptions/Orders/Order_Line_Items/AA_Overview_of_Order_Line_Items) feature. As of Zuora Billing Release 313 (November 2021), new customers who onboard on [Orders](https://knowledgecenter.zuora.com/Billing/Subscriptions/Orders/AA_Overview_of_Orders) will have the [Order Line Items](https://knowledgecenter.zuora.com/Billing/Subscriptions/Orders/Order_Line_Items) feature enabled by default.         | [optional] 
**order_number** | **str** | The order number of the order. | [optional] 
**reason_code** | **str** | Values of reason code configured in **Billing Settings** &gt; **Configure Reason Codes** through Zuora UI. Indicates the reason when a return order line item occurs.  | [optional] 
**scheduling_options** | [**OrderSchedulingOptions**](OrderSchedulingOptions.md) |  | [optional] 
**scheduled_order_activation_response** | [**CreateOrderResponse**](CreateOrderResponse.md) |  | [optional] 
**status** | [**OrderStatus**](OrderStatus.md) |  | [optional] 
**subscriptions** | [**List[OrderSubscriptions]**](OrderSubscriptions.md) | Represents a processed subscription, including the origin request (order actions) that create this version of subscription and the processing result (order metrics). The reference part in the request will be overridden with the info in the new subscription version. | [optional] 
**commitments** | [**List[UpsertCommitmentInput]**](UpsertCommitmentInput.md) |  | [optional] 
**updated_by** | **str** | The ID of the user who updated this order. | [optional] 
**updated_date** | **str** | The time that the order gets updated in the system(for example, an order description update), in the &#x60;YYYY-MM-DD HH:MM:SS&#x60; format. | [optional] 

## Example

```python
from zuora_sdk.models.order import Order

# TODO update the JSON string below
json = "{}"
# create an instance of Order from a JSON string
order_instance = Order.from_json(json)
# print the JSON string representation of the object
print(Order.to_json())

# convert the object into a dict
order_dict = order_instance.to_dict()
# create an instance of Order from a dict
order_from_dict = Order.from_dict(order_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


