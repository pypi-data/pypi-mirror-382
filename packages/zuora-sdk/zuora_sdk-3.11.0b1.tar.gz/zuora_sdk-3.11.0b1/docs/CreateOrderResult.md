# CreateOrderResult


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**account_id** | **str** | The account ID for the order. This field is returned instead of the &#x60;accountNumber&#x60; field if the &#x60;returnIds&#x60; query parameter is set to &#x60;true&#x60;. | [optional] 
**account_number** | **str** | The account number for the order. | [optional] 
**credit_memo_ids** | **List[str]** | An array of the credit memo IDs generated in this order request. The credit memo is only available if you have the Invoice Settlement feature enabled. This field is returned instead of the &#x60;creditMemoNumbers&#x60; field if the &#x60;returnIds&#x60; query parameter is set to &#x60;true&#x60;. | [optional] 
**credit_memo_numbers** | **List[str]** | An array of the credit memo numbers generated in this order request. The credit memo is only available if you have the Invoice Settlement feature enabled. | [optional] 
**invoice_ids** | **List[str]** | An array of the invoice IDs generated in this order request. Normally it includes one invoice ID only, but can include multiple items when a subscription was tagged as invoice separately. This field is returned instead of the &#x60;invoiceNumbers&#x60; field if the &#x60;returnIds&#x60; query parameter is set to &#x60;true&#x60;. | [optional] 
**invoice_numbers** | **List[str]** | An array of the invoice numbers generated in this order request. Normally it includes one invoice number only, but can include multiple items when a subscription was tagged as invoice separately. | [optional] 
**order_id** | **str** | The ID of the order created. This field is returned instead of the &#x60;orderNumber&#x60; field if the &#x60;returnIds&#x60; query parameter is set to &#x60;true&#x60;. | [optional] 
**order_line_items** | [**List[CreateOrderResponseOrderLineItems]**](CreateOrderResponseOrderLineItems.md) |  | [optional] 
**order_number** | **str** | The order number of the order created. | [optional] 
**paid_amount** | **str** | The total amount collected in this order request. | [optional] 
**payment_id** | **str** | The payment Id that is collected in this order request. This field is returned instead of the &#x60;paymentNumber&#x60; field if the &#x60;returnIds&#x60; query parameter is set to &#x60;true&#x60;. | [optional] 
**payment_number** | **str** | The payment number that is collected in this order request. | [optional] 
**ramps** | [**List[CreateOrderResponseRamps]**](CreateOrderResponseRamps.md) | **Note**: This field is only available if you have the Ramps feature enabled. The [Orders](https://knowledgecenter.zuora.com/Billing/Subscriptions/Orders/AA_Overview_of_Orders) feature must be enabled before you can access the [Ramps](https://knowledgecenter.zuora.com/Billing/Subscriptions/Orders/Ramps_and_Ramp_Metrics/A_Overview_of_Ramps_and_Ramp_Metrics) feature. The Ramps feature is available for customers with Enterprise and Nine editions by default. If you are a Growth customer, see [Zuora Editions](https://knowledgecenter.zuora.com/BB_Introducing_Z_Business/C_Zuora_Editions) for pricing information coming October 2020.  The ramp definitions created by this order request.  | [optional] 
**refunds** | [**List[CreateOrderResponseRefunds]**](CreateOrderResponseRefunds.md) |  | [optional] 
**status** | [**OrderStatus**](OrderStatus.md) |  | [optional] 
**subscription_ids** | **List[str]** | Container for the subscription IDs of the subscriptions in an order. This field is returned if the &#x60;returnIds&#x60; query parameter is set to &#x60;true&#x60;. | [optional] 
**subscription_numbers** | **List[str]** | Container for the subscription numbers of the subscriptions in an order. Subscriptions in the response are displayed in the same sequence as the subscriptions defined in the request. This field is in Zuora REST API version control. Supported minor versions are &#x60;206.0&#x60; and earlier. | [optional] 
**subscriptions** | [**List[CreateOrderResponseSubscriptions]**](CreateOrderResponseSubscriptions.md) | **Note:** This field is in Zuora REST API version control. Supported minor versions are 223.0 or later. To use this field in the method, you must set the &#x60;zuora-version&#x60; parameter to the minor version number in the request header.  Container for the subscription numbers and statuses in an order.  | [optional] 
**write_off** | [**List[CreateOrderResponseWriteOff]**](CreateOrderResponseWriteOff.md) |  | [optional] 
**commitments** | [**List[CommitmentOutput]**](CommitmentOutput.md) | The commitments created by this order request. | [optional] 

## Example

```python
from zuora_sdk.models.create_order_result import CreateOrderResult

# TODO update the JSON string below
json = "{}"
# create an instance of CreateOrderResult from a JSON string
create_order_result_instance = CreateOrderResult.from_json(json)
# print the JSON string representation of the object
print(CreateOrderResult.to_json())

# convert the object into a dict
create_order_result_dict = create_order_result_instance.to_dict()
# create an instance of CreateOrderResult from a dict
create_order_result_from_dict = CreateOrderResult.from_dict(create_order_result_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


