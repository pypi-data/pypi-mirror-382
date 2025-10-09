# CancelSubscriptionResponse


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**cancelled_date** | **date** | The date that the subscription was canceled. It is available for Orders Harmonization and Subscribe/Amend tenants.  | [optional] 
**credit_memo_id** | **str** | The credit memo ID, if a credit memo is generated during the subscription process.   **Note:** This container is only available if you set the Zuora REST API minor version to 207.0 or later in the request header, and you have  [Invoice Settlement](https://knowledgecenter.zuora.com/Billing/Billing_and_Payments/Invoice_Settlement) enabled. The Invoice Settlement feature is generally available as of Zuora Billing Release 296 (March 2021). This feature includes Unapplied Payments, Credit and Debit Memo, and Invoice Item Settlement. If you want to enable Invoice Settlement, see [Invoice Settlement Enablement and Checklist Guide](https://knowledgecenter.zuora.com/Billing/Billing_and_Payments/Invoice_Settlement/Invoice_Settlement_Migration_Checklist_and_Guide) for more information. | [optional] 
**invoice_id** | **str** | ID of the invoice, if one is generated.  | [optional] 
**paid_amount** | **float** | Amount paid.  | [optional] 
**payment_id** | **str** | ID of the payment, if a payment is collected.  | [optional] 
**subscription_id** | **str** | The subscription ID. It is available for Orders Harmonization and Subscribe/Amend Tenants.  | [optional] 
**success** | **bool** | Returns &#x60;true&#x60; if the request was processed successfully.  | [optional] 
**total_delta_mrr** | **float** | Change in the subscription monthly recurring revenue as a result of the update. It is available for Orders Harmonization and Subscribe/Amend tenants. | [optional] 
**total_delta_tcv** | **float** | Change in the total contracted value of the subscription as a result of the update. It is available for Orders Harmonization and Subscribe/Amend tenants. | [optional] 
**order_number** | **str** | The order number. It is available for Orders Tenants.  | [optional] 
**status** | [**OrderStatus**](OrderStatus.md) |  | [optional] 
**account_number** | **str** | The account number that this order has been created under. This is also the invoice owner of the subscriptions included in this order. It is available for Orders Tenants. | [optional] 
**subscription_numbers** | **List[str]** | The subscription numbers. It is available for Orders Tenants. This field is in Zuora REST API version control. Supported max version is 206.0.  | [optional] 
**subscriptions** | [**List[CreateOrderResponseSubscriptions]**](CreateOrderResponseSubscriptions.md) | This field is in Zuora REST API version control. Supported minor versions are 223.0 or later. It is available for Orders Tenants.  | [optional] 

## Example

```python
from zuora_sdk.models.cancel_subscription_response import CancelSubscriptionResponse

# TODO update the JSON string below
json = "{}"
# create an instance of CancelSubscriptionResponse from a JSON string
cancel_subscription_response_instance = CancelSubscriptionResponse.from_json(json)
# print the JSON string representation of the object
print(CancelSubscriptionResponse.to_json())

# convert the object into a dict
cancel_subscription_response_dict = cancel_subscription_response_instance.to_dict()
# create an instance of CancelSubscriptionResponse from a dict
cancel_subscription_response_from_dict = CancelSubscriptionResponse.from_dict(cancel_subscription_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


