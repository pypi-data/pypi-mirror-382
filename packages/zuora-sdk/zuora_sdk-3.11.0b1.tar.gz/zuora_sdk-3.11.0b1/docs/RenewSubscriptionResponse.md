# RenewSubscriptionResponse


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**subscription_id** | **str** | Subscription ID, It is available for Orders Harmonization and Subscribe/Amend tenants.  | [optional] 
**credit_memo_id** | **str** | The credit memo ID, if a credit memo is generated during the subscription process.   **Note:** This container is only available if you set the Zuora REST API minor version to 207.0 or later in the request header, and you have  [Invoice Settlement](https://knowledgecenter.zuora.com/Billing/Billing_and_Payments/Invoice_Settlement) enabled. The Invoice Settlement feature is generally available as of Zuora Billing Release 296 (March 2021). This feature includes Unapplied Payments, Credit and Debit Memo, and Invoice Item Settlement. If you want to enable Invoice Settlement, see [Invoice Settlement Enablement and Checklist Guide](https://knowledgecenter.zuora.com/Billing/Billing_and_Payments/Invoice_Settlement/Invoice_Settlement_Migration_Checklist_and_Guide) for more information. | [optional] 
**invoice_id** | **str** | Invoice ID, if one is generated.  | [optional] 
**paid_amount** | **float** | Payment amount, if payment is collected.  | [optional] 
**payment_id** | **str** | Payment ID, if payment is collected.  | [optional] 
**success** | **bool** | Returns &#x60;true&#x60; if the request was processed successfully.  | [optional] 
**term_end_date** | **date** | Date the new subscription term ends, as yyyy-mm-dd. It is available for Orders Harmonization and Subscribe/Amend tenants.  | [optional] 
**term_start_date** | **date** | Date the new subscription term begins, as yyyy-mm-dd. It is available for Orders Harmonization and Subscribe/Amend tenants.  | [optional] 
**total_delta_mrr** | **float** | Change in the subscription monthly recurring revenue as a result of the update. For a renewal, this is the MRR of the subscription in the new term. It is available for Orders Harmonization and Subscribe/Amend tenants. | [optional] 
**total_delta_tcv** | **float** | Change in the total contracted value of the subscription as a result of the update. For a renewal, this is the TCV of the subscription in the new term. It is available for Orders Harmonization and Subscribe/Amend tenants. | [optional] 
**order_number** | **str** | The order number. It is available for Orders Tenants.  | [optional] 
**status** | [**OrderStatus**](OrderStatus.md) |  | [optional] 
**account_number** | **str** | The account number that this order has been created under. This is also the invoice owner of the subscriptions included in this order. It is available for Orders Tenants. | [optional] 
**subscription_numbers** | **List[str]** | The subscription numbers. It is available for Orders Tenants. This field is in Zuora REST API version control. Supported max version is 206.0.  | [optional] 
**subscriptions** | [**List[CreateOrderResponseSubscriptions]**](CreateOrderResponseSubscriptions.md) | This field is in Zuora REST API version control. Supported minor versions are 223.0 or later. It is available for Orders Tenants.  | [optional] 

## Example

```python
from zuora_sdk.models.renew_subscription_response import RenewSubscriptionResponse

# TODO update the JSON string below
json = "{}"
# create an instance of RenewSubscriptionResponse from a JSON string
renew_subscription_response_instance = RenewSubscriptionResponse.from_json(json)
# print the JSON string representation of the object
print(RenewSubscriptionResponse.to_json())

# convert the object into a dict
renew_subscription_response_dict = renew_subscription_response_instance.to_dict()
# create an instance of RenewSubscriptionResponse from a dict
renew_subscription_response_from_dict = RenewSubscriptionResponse.from_dict(renew_subscription_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


