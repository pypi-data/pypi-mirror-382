# PreviewOrderCreateSubscription

Information about an order action of type `CreateSubscription`. 

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**bill_to_contact_id** | **str** | The ID of the bill-to contact associated with the subscription.  **Note**:    - If you have the &lt;a href&#x3D;\&quot;https://knowledgecenter.zuora.com/Zuora_Billing/Bill_your_customers/Bill_customers_at_subscription_level/Flexible_Billing_Attributes\&quot; target&#x3D;\&quot;_blank\&quot;&gt;Flexible Billing Attributes&lt;/a&gt; feature disabled, this field is unavailable in the request body and the value of this field is &#x60;null&#x60; in the response body.    - If you have the Flexible Billing Attributes feature enabled, and you do not specify this field in the request or you select **Default Contact from Account** for this field during subscription creation, the value of this field is automatically set to &#x60;null&#x60; in the response body.  | [optional] 
**invoice_separately** | **bool** | Specifies whether the subscription appears on a separate invoice when Zuora generates invoices. | [optional] 
**invoice_template_id** | **str** | The ID of the invoice template associated with the subscription.  **Note**:    - If you have the &lt;a href&#x3D;\&quot;https://knowledgecenter.zuora.com/Zuora_Billing/Bill_your_customers/Bill_customers_at_subscription_level/Flexible_Billing_Attributes\&quot; target&#x3D;\&quot;_blank\&quot;&gt;Flexible Billing Attributes&lt;/a&gt; feature disabled, this field is unavailable in the request body and the value of this field is &#x60;null&#x60; in the response body.    - If you have the Flexible Billing Attributes feature enabled, and you do not specify this field in the request or you select **Default Template from Account** for this field during subscription creation, the value of this field is automatically set to &#x60;null&#x60; in the response body.  | [optional] 
**new_subscription_owner_account** | [**PreviewOrderSubscriptionOwnerAccount**](PreviewOrderSubscriptionOwnerAccount.md) |  | [optional] 
**notes** | **str** | Notes about the subscription. These notes are only visible to Zuora users.  | [optional] 
**payment_term** | **str** | The name of the payment term associated with the subscription. For example, &#x60;Net 30&#x60;. The payment term determines the due dates of invoices.   **Note**:    - If you have the &lt;a href&#x3D;\&quot;https://knowledgecenter.zuora.com/Zuora_Billing/Bill_your_customers/Bill_customers_at_subscription_level/Flexible_Billing_Attributes\&quot; target&#x3D;\&quot;_blank\&quot;&gt;Flexible Billing Attributes&lt;/a&gt; feature disabled, this field is unavailable in the request body and the value of this field is &#x60;null&#x60; in the response body.    - If you have the Flexible Billing Attributes feature enabled, and you do not specify this field in the request or you select **Default Term from Account** for this field during subscription creation, the value of this field is automatically set to &#x60;null&#x60; in the response body. | [optional] 
**sequence_set_id** | **str** | The ID of the sequence set associated with the subscription.  **Note**:    - If you have the &lt;a href&#x3D;\&quot;https://knowledgecenter.zuora.com/Zuora_Billing/Bill_your_customers/Bill_customers_at_subscription_level/Flexible_Billing_Attributes\&quot; target&#x3D;\&quot;_blank\&quot;&gt;Flexible Billing Attributes&lt;/a&gt; feature disabled, this field is unavailable in the request body and the value of this field is &#x60;null&#x60; in the response body.    - If you have the Flexible Billing Attributes feature enabled, and you do not specify this field in the request or you select **Default Set from Account** for this field during subscription creation, the value of this field is automatically set to &#x60;null&#x60; in the response body.  | [optional] 
**sold_to_contact_id** | **str** | The ID of the sold-to contact associated with the subscription.  **Note**:    - If you have the &lt;a href&#x3D;\&quot;https://knowledgecenter.zuora.com/Zuora_Billing/Bill_your_customers/Bill_customers_at_subscription_level/Flexible_Billing_Attributes\&quot; target&#x3D;\&quot;_blank\&quot;&gt;Flexible Billing Attributes&lt;/a&gt; feature disabled, this field is unavailable in the request body and the value of this field is &#x60;null&#x60; in the response body.    - If you have the Flexible Billing Attributes feature enabled, and you do not specify this field in the request or you select **Default Contact from Account** for this field during subscription creation, the value of this field is automatically set to &#x60;null&#x60; in the response body.  | [optional] 
**ship_to_contact_id** | **str** | The ID of the ship-to contact associated with the subscription.  | [optional] 
**subscribe_to_rate_plans** | [**List[PreviewOrderRatePlanOverride]**](PreviewOrderRatePlanOverride.md) | List of rate plans associated with the subscription.  | [optional] 
**subscription_number** | **str** | Subscription number of the subscription. For example, A-S00000001.  If you do not set this field, Zuora will generate the subscription number.  | [optional] 
**subscription_owner_account_number** | **str** | Account number of an existing account that will own the subscription. For example, A00000001.   If you do not set this field or the &#x60;newSubscriptionOwnerAccount&#x60; field, the account that owns the order will also own the subscription. Zuora will return an error if you set this field and the &#x60;newSubscriptionOwnerAccount&#x60; field. | [optional] 
**invoice_owner_account_number** | **str** | Account number of an existing account that will own the invoice. For example, A00000001. If you do not set this field, the account that owns the order will also own this invoice.  | [optional] 
**terms** | [**PreviewOrderCreateSubscriptionTerms**](PreviewOrderCreateSubscriptionTerms.md) |  | [optional] 
**communication_profile_id** | **str** | The ID of the communication profile associated with the subscription.  **Note**: This field is available only if you have the &lt;a href&#x3D;\&quot;https://knowledgecenter.zuora.com/Zuora_Billing/Bill_your_customers/Bill_customers_at_subscription_level/Flexible_Billing_Attributes\&quot; target&#x3D;\&quot;_blank\&quot;&gt;Flexible Billing Attributes&lt;/a&gt; feature enabled.  | [optional] 
**currency** | **str** | The code of currency that is used for this subscription. If the currency is not selected, the default currency from the account will be used. All subscriptions in the same order must use the same currency. The currency for a subscription cannot be changed.  **Note**: This field is available only if you have the &lt;a href&#x3D;\&quot;https://knowledgecenter.zuora.com/Zuora_Billing/Bill_your_customers/Flexible_Billing/Multiple_Currencies\&quot; target&#x3D;\&quot;_blank\&quot;&gt;Multiple Currencies&lt;/a&gt; feature enabled.   | [optional] 
**invoice_group_number** | **str** | The number of invoice group associated with the subscription.  **Note**: This field is available only if you have the &lt;a href&#x3D;\&quot;https://knowledgecenter.zuora.com/Zuora_Billing/Bill_your_customers/Bill_customers_at_subscription_level/Flexible_Billing_Attributes\&quot; target&#x3D;\&quot;_blank\&quot;&gt;Flexible Billing Attributes&lt;/a&gt; feature enabled.  | [optional] 

## Example

```python
from zuora_sdk.models.preview_order_create_subscription import PreviewOrderCreateSubscription

# TODO update the JSON string below
json = "{}"
# create an instance of PreviewOrderCreateSubscription from a JSON string
preview_order_create_subscription_instance = PreviewOrderCreateSubscription.from_json(json)
# print the JSON string representation of the object
print(PreviewOrderCreateSubscription.to_json())

# convert the object into a dict
preview_order_create_subscription_dict = preview_order_create_subscription_instance.to_dict()
# create an instance of PreviewOrderCreateSubscription from a dict
preview_order_create_subscription_from_dict = PreviewOrderCreateSubscription.from_dict(preview_order_create_subscription_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


