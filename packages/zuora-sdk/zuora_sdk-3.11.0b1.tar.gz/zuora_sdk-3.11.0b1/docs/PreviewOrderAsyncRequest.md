# PreviewOrderAsyncRequest


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**category** | [**OrderCategory**](OrderCategory.md) |  | [optional] [default to OrderCategory.NEWSALES]
**custom_fields** | **Dict[str, object]** | Container for custom fields of an Order object.  | [optional] 
**description** | **str** | A description of the order. | [optional] 
**existing_account_number** | **str** | The account number that this order will be created under. It can be either the accountNumber or the account info. It will return an error if both are specified. Note that invoice owner account of the subscriptions included in this order should be the same with the account of the order.  | [optional] 
**order_date** | **date** | The date when the order is signed. All of the order actions under this order will use this order date as the contract effective date. | 
**order_line_items** | [**List[CreateOrderOrderLineItem]**](CreateOrderOrderLineItem.md) | [Order Line Items](https://knowledgecenter.zuora.com/Billing/Subscriptions/Orders/Order_Line_Items/AA_Overview_of_Order_Line_Items) are non subscription based items created by an Order, representing transactional charges such as one-time fees, physical goods, or professional service charges that are not sold as subscription services.   With the Order Line Items feature enabled, you can now launch non-subscription and unified monetization business models in Zuora, in addition to subscription business models.   **Note:** The [Order Line Items](https://knowledgecenter.zuora.com/Billing/Subscriptions/Orders/Order_Line_Items/AA_Overview_of_Order_Line_Items) feature is now generally available to all Zuora customers. You need to enable the [Orders](https://knowledgecenter.zuora.com/BC_Subscription_Management/Orders/AA_Overview_of_Orders#Orders) feature to access the [Order Line Items](https://knowledgecenter.zuora.com/Billing/Subscriptions/Orders/Order_Line_Items/AA_Overview_of_Order_Line_Items) feature. As of Zuora Billing Release 313 (November 2021), new customers who onboard on [Orders](https://knowledgecenter.zuora.com/Billing/Subscriptions/Orders/AA_Overview_of_Orders) will have the [Order Line Items](https://knowledgecenter.zuora.com/Billing/Subscriptions/Orders/Order_Line_Items) feature enabled by default.         | [optional] 
**order_number** | **str** | The order number of this order.    **Note:** Make sure the order number does not contain a slash.  | [optional] 
**preview_account_info** | [**PreviewAccountInfo**](PreviewAccountInfo.md) |  | [optional] 
**preview_options** | [**PreviewOptions**](PreviewOptions.md) |  | 
**reason_code** | **str** | Values of reason code configured in **Billing Settings** &gt; **Configure Reason Codes** through Zuora UI. Indicates the reason when a return order line item occurs.  | [optional] 
**subscriptions** | [**List[PreviewOrderSubscriptionsAsync]**](PreviewOrderSubscriptionsAsync.md) | Each item includes a set of order actions, which will be applied to the same base subscription. | [optional] 

## Example

```python
from zuora_sdk.models.preview_order_async_request import PreviewOrderAsyncRequest

# TODO update the JSON string below
json = "{}"
# create an instance of PreviewOrderAsyncRequest from a JSON string
preview_order_async_request_instance = PreviewOrderAsyncRequest.from_json(json)
# print the JSON string representation of the object
print(PreviewOrderAsyncRequest.to_json())

# convert the object into a dict
preview_order_async_request_dict = preview_order_async_request_instance.to_dict()
# create an instance of PreviewOrderAsyncRequest from a dict
preview_order_async_request_from_dict = PreviewOrderAsyncRequest.from_dict(preview_order_async_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


