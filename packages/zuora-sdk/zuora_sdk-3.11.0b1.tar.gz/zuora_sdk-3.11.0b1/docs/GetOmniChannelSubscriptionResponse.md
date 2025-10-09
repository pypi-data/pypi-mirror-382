# GetOmniChannelSubscriptionResponse


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**process_id** | **str** | The Id of the process that handle the operation.  | [optional] 
**request_id** | **str** | Unique request identifier. If you need to contact us about a specific request, providing the request identifier will ensure the fastest possible resolution.  | [optional] 
**reasons** | [**List[FailedReason]**](FailedReason.md) |  | [optional] 
**success** | **bool** | Indicates whether the call succeeded.  | [optional] [default to True]
**id** | **str** | The system generated Id in Billing, the subscriptionId.  | [optional] 
**subscription_number** | **str** | The system generated subscription number.  | [optional] 
**account_id** | **str** | The ID of the account associated with this subscription.  | [optional] 
**external_subscription_id** | **str** | The original transaction id of the notification.  | [optional] 
**external_transaction_reason** | **str** | The latest transaction reason.  | [optional] 
**external_source_system** | **str** | For example, Apple, Google, Roku, Amazon.  | [optional] 
**external_state** | **str** | The original status from client, such as active, canceled, expired, pastDue.  | [optional] 
**state** | **str** | The common external subscription state.  | [optional] 
**external_product_id** | **str** | The product id in the external system.  | [optional] 
**external_replace_by_product_id** | **str** | The productId is going to replace the existing productId.  | [optional] 
**external_in_app_ownership_type** | **str** | Such as purchased, family_shared.  | [optional] 
**external_quantity** | **int** | The quantity of the product, must be &gt;&#x3D; 0. Default 1 if not set.  | [optional] 
**currency** | **str** | The currency code of the transaction. If not specified, get value from the Account.  | [optional] 
**auto_renew** | **bool** | If &#x60;true&#x60;, the subscription automatically renews at the end of the term. Default is &#x60;false&#x60;.  | [optional] 
**original_purchase_date** | **str** | The value of externalPurchaseDate when this external subscription firstly created.  UTC time, &#x60;yyyy-mm-dd hh:mm:ss&#x60;.  | [optional] 
**external_purchase_date** | **str** | The App Store charged the user’s account for a purchase, restored product, subscription,  or subscription renewal after a lapse. UTC time, &#x60;yyyy-mm-dd hh:mm:ss&#x60;.  | [optional] 
**external_activation_date** | **str** | When the external subscription was activated on the external platform.  UTC time, &#x60;yyyy-mm-dd hh:mm:ss&#x60;.  | [optional] 
**external_expiration_date** | **str** | The expiresDate is a static value that applies for each transaction. UTC time, &#x60;yyyy-mm-dd hh:mm:ss&#x60;.  | [optional] 
**external_application_id** | **str** | The external application id.  | [optional] 
**external_bundle_id** | **str** | The external bundler id.  | [optional] 
**external_subscriber_id** | **str** | The external subscriber id.  | [optional] 
**external_price** | **float** | The price in external system.  | [optional] 
**external_purchase_type** | **str** | The external purchase type. | [optional] 
**external_last_renewal_date** | **str** | The lastRenewalDate is a static value that applies for each transaction. UTC time, &#x60;yyyy-mm-dd hh:mm:ss&#x60;.  | [optional] 
**external_next_renewal_date** | **str** | The nextRenewalDate is a static value that applies for each transaction.  UTC time, &#x60;yyyy-mm-dd hh:mm:ss&#x60;.  | [optional] 

## Example

```python
from zuora_sdk.models.get_omni_channel_subscription_response import GetOmniChannelSubscriptionResponse

# TODO update the JSON string below
json = "{}"
# create an instance of GetOmniChannelSubscriptionResponse from a JSON string
get_omni_channel_subscription_response_instance = GetOmniChannelSubscriptionResponse.from_json(json)
# print the JSON string representation of the object
print(GetOmniChannelSubscriptionResponse.to_json())

# convert the object into a dict
get_omni_channel_subscription_response_dict = get_omni_channel_subscription_response_instance.to_dict()
# create an instance of GetOmniChannelSubscriptionResponse from a dict
get_omni_channel_subscription_response_from_dict = GetOmniChannelSubscriptionResponse.from_dict(get_omni_channel_subscription_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


