# CreatePaymentMethodCardholderInfo

Container for cardholder information. This container field is required for credit card payment methods. The nested `cardHolderName` field is required. 

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**address_line1** | **str** | First address line, 255 characters or less.  | [optional] 
**address_line2** | **str** | Second address line, 255 characters or less.  | [optional] 
**card_holder_name** | **str** | The card holder&#39;s full name as it appears on the card, e.g., \&quot;John J Smith\&quot;, 50 characters or less. | [optional] 
**city** | **str** | City, 40 characters or less.  It is recommended to provide the city and country information when creating a payment method. The information will be used to process payments. If the information is not provided during payment method creation, the city and country data will be missing during payment processing. | [optional] 
**country** | **str** | Country, must be a valid country name or abbreviation.  It is recommended to provide the city and country information when creating a payment method. The information will be used to process payments. If the information is not provided during payment method creation, the city and country data will be missing during payment processing. | [optional] 
**email** | **str** | Card holder&#39;s email address, 80 characters or less.  | [optional] 
**phone** | **str** | Phone number, 40 characters or less.  | [optional] 
**state** | **str** | State; must be a valid state name or 2-character abbreviation.  | [optional] 
**zip_code** | **str** | Zip code, 20 characters or less.  | [optional] 

## Example

```python
from zuora_sdk.models.create_payment_method_cardholder_info import CreatePaymentMethodCardholderInfo

# TODO update the JSON string below
json = "{}"
# create an instance of CreatePaymentMethodCardholderInfo from a JSON string
create_payment_method_cardholder_info_instance = CreatePaymentMethodCardholderInfo.from_json(json)
# print the JSON string representation of the object
print(CreatePaymentMethodCardholderInfo.to_json())

# convert the object into a dict
create_payment_method_cardholder_info_dict = create_payment_method_cardholder_info_instance.to_dict()
# create an instance of CreatePaymentMethodCardholderInfo from a dict
create_payment_method_cardholder_info_from_dict = CreatePaymentMethodCardholderInfo.from_dict(create_payment_method_cardholder_info_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


