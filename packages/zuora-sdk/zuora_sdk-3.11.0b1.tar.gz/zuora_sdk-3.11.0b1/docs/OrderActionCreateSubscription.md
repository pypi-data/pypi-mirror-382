# OrderActionCreateSubscription

Information about an order action of type `CreateSubscription`. 

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**bill_to_contact_id** | **str** | The ID of the bill-to contact associated with the subscription.  n**Note**:    - If you have the &lt;a href&#x3D;\&quot;https://knowledgecenter.zuora.com/Zuora_Billing/Bill_your_customers/Bill_customers_at_subscription_level/Flexible_Billing_Attributes\&quot; target&#x3D;\&quot;_blank\&quot;&gt;Flexible Billing Attributes&lt;/a&gt; feature disabled, this field is unavailable in the request body and the value of this field is &#x60;null&#x60; in the response body.    - If you have the Flexible Billing Attributes feature enabled, and you do not specify this field in the request or you select **Default Contact from Account** for this field during subscription creation, the value of this field is automatically set to &#x60;null&#x60; in the response body.  | [optional] 
**communication_profile_id** | **str** | The ID of the communication profile associated with the subscription.               **Note**: This field is available only if you have the &lt;a href&#x3D;\&quot;https://knowledgecenter.zuora.com/Zuora_Billing/Bill_your_customers/Bill_customers_at_subscription_level/Flexible_Billing_Attributes\&quot; target&#x3D;\&quot;_blank\&quot;&gt;Flexible Billing Attributes&lt;/a&gt; feature enabled.  | [optional] 
**invoice_group_number** | **str** | The number of invoice group associated with the subscription.  **Note**: This field is available only if you have the &lt;a href&#x3D;\&quot;https://knowledgecenter.zuora.com/Zuora_Billing/Bill_your_customers/Bill_customers_at_subscription_level/Flexible_Billing_Attributes\&quot; target&#x3D;\&quot;_blank\&quot;&gt;Flexible Billing Attributes&lt;/a&gt; feature enabled.  | [optional] 
**invoice_separately** | **bool** | Specifies whether the subscription appears on a separate invoice when Zuora generates invoices.  | [optional] 
**invoice_template_id** | **str** | The ID of the invoice template associated with the subscription.  n**Note**:    - If you have the &lt;a href&#x3D;\&quot;https://knowledgecenter.zuora.com/Zuora_Billing/Bill_your_customers/Bill_customers_at_subscription_level/Flexible_Billing_Attributes\&quot; target&#x3D;\&quot;_blank\&quot;&gt;Flexible Billing Attributes&lt;/a&gt; feature disabled, this field is unavailable in the request body and the value of this field is &#x60;null&#x60; in the response body.    - If you have the Flexible Billing Attributes feature enabled, and you do not specify this field in the request or you select **Default Template from Account** for this field during subscription creation, the value of this field is automatically set to &#x60;null&#x60; in the response body.  | [optional] 
**new_subscription_owner_account** | [**CreateOrderSubscriptionOwnerAccount**](CreateOrderSubscriptionOwnerAccount.md) |  | [optional] 
**notes** | **str** | Notes about the subscription. These notes are only visible to Zuora users.  | [optional] 
**payment_term** | **str** | The name of the payment term associated with the subscription. For example, &#x60;Net 30&#x60;. The payment term determines the due dates of invoices.  n**Note**:    - If you have the &lt;a href&#x3D;\&quot;https://knowledgecenter.zuora.com/Zuora_Billing/Bill_your_customers/Bill_customers_at_subscription_level/Flexible_Billing_Attributes\&quot; target&#x3D;\&quot;_blank\&quot;&gt;Flexible Billing Attributes&lt;/a&gt; feature disabled, this field is unavailable in the request body and the value of this field is &#x60;null&#x60; in the response body.    - If you have the Flexible Billing Attributes feature enabled, and you do not specify this field in the request or you select **Default Term from Account** for this field during subscription creation, the value of this field is automatically set to &#x60;null&#x60; in the response body.  | [optional] 
**sequence_set_id** | **str** | The ID of the sequence set associated with the subscription.  **Note**:    - If you have the &lt;a href&#x3D;\&quot;https://knowledgecenter.zuora.com/Zuora_Billing/Bill_your_customers/Bill_customers_at_subscription_level/Flexible_Billing_Attributes\&quot; target&#x3D;\&quot;_blank\&quot;&gt;Flexible Billing Attributes&lt;/a&gt; feature disabled, this field is unavailable in the request body and the value of this field is &#x60;null&#x60; in the response body.    - If you have the Flexible Billing Attributes feature enabled, and you do not specify this field in the request or you select **Default Set from Account** for this field during subscription creation, the value of this field is automatically set to &#x60;null&#x60; in the response body.  | [optional] 
**sold_to_contact_id** | **str** | The ID of the sold-to contact associated with the subscription.  n**Note**:    - If you have the &lt;a href&#x3D;\&quot;https://knowledgecenter.zuora.com/Zuora_Billing/Bill_your_customers/Bill_customers_at_subscription_level/Flexible_Billing_Attributes\&quot; target&#x3D;\&quot;_blank\&quot;&gt;Flexible Billing Attributes&lt;/a&gt; feature disabled, this field is unavailable in the request body and the value of this field is &#x60;null&#x60; in the response body.    - If you have the Flexible Billing Attributes feature enabled, and you do not specify this field in the request or you select **Default Contact from Account** for this field during subscription creation, the value of this field is automatically set to &#x60;null&#x60; in the response body.  | [optional] 
**ship_to_contact_id** | **str** | The ID of the ship-to contact associated with the subscription. | [optional] 
**subscribe_to_products** | [**List[SubscribeToProduct]**](SubscribeToProduct.md) | For a rate plan, the following fields are available:   - &#x60;chargeOverrides&#x60;  - &#x60;clearingExistingFeatures&#x60;   - &#x60;customFields&#x60;   - &#x60;externallyManagedPlanId&#x60;  - &#x60;newRatePlanId&#x60;   - &#x60;productRatePlanId&#x60;   - &#x60;subscriptionProductFeatures&#x60;  - &#x60;uniqueToken&#x60;     | [optional] 
**subscribe_to_rate_plans** | [**List[RatePlanOverride]**](RatePlanOverride.md) | List of rate plans associated with the subscription.  **Note**: The &#x60;subscribeToRatePlans&#x60; field has been deprecated, this field is replaced by the &#x60;subscribeToProducts&#x60; field that supports Rate Plans. In a new order request, you can use either &#x60;subscribeToRatePlans&#x60; or &#x60;subscribeToProducts&#x60;, not both.  | [optional] 
**subscription_number** | **str** | Subscription number of the subscription. For example, A-S00000001.  If you do not set this field, Zuora will generate the subscription number.  | [optional] 
**subscription_owner_account_number** | **str** | Account number of an existing account that will own the subscription. For example, A00000001.  If you do not set this field or the &#x60;newSubscriptionOwnerAccount&#x60; field, the account that owns the order will also own the subscription. Zuora will return an error if you set this field and the &#x60;newSubscriptionOwnerAccount&#x60; field.  | [optional] 
**invoice_owner_account_number** | **str** | Account number of an existing account that will own the invoice. For example, A00000001.  If you do not set this field, the account that owns the order will also own this invoice.  | [optional] 
**terms** | [**OrderActionCreateSubscriptionTerms**](OrderActionCreateSubscriptionTerms.md) |  | [optional] 
**payment_profile** | [**PaymentProfile**](PaymentProfile.md) |  | [optional] 
**currency** | **str** | The currency of the subscription.  | [optional] 

## Example

```python
from zuora_sdk.models.order_action_create_subscription import OrderActionCreateSubscription

# TODO update the JSON string below
json = "{}"
# create an instance of OrderActionCreateSubscription from a JSON string
order_action_create_subscription_instance = OrderActionCreateSubscription.from_json(json)
# print the JSON string representation of the object
print(OrderActionCreateSubscription.to_json())

# convert the object into a dict
order_action_create_subscription_dict = order_action_create_subscription_instance.to_dict()
# create an instance of OrderActionCreateSubscription from a dict
order_action_create_subscription_from_dict = OrderActionCreateSubscription.from_dict(order_action_create_subscription_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


