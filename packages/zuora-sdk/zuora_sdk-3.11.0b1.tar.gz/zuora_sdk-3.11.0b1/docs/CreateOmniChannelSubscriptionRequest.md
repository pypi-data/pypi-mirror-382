# CreateOmniChannelSubscriptionRequest


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**account_id** | **str** | The ID of the account associated with this subscription.  | [optional] 
**external_subscription_id** | **str** | The original transaction id of the notification. This must be unique in the tenant.  | 
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
**account_identifier_field** | **str** | The account field used to identify the account in acountData. It could be a custom field. | [optional] 
**account_data** | [**OmniChannelAccountData**](OmniChannelAccountData.md) |  | [optional] 

## Example

```python
from zuora_sdk.models.create_omni_channel_subscription_request import CreateOmniChannelSubscriptionRequest

# TODO update the JSON string below
json = "{}"
# create an instance of CreateOmniChannelSubscriptionRequest from a JSON string
create_omni_channel_subscription_request_instance = CreateOmniChannelSubscriptionRequest.from_json(json)
# print the JSON string representation of the object
print(CreateOmniChannelSubscriptionRequest.to_json())

# convert the object into a dict
create_omni_channel_subscription_request_dict = create_omni_channel_subscription_request_instance.to_dict()
# create an instance of CreateOmniChannelSubscriptionRequest from a dict
create_omni_channel_subscription_request_from_dict = CreateOmniChannelSubscriptionRequest.from_dict(create_omni_channel_subscription_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


