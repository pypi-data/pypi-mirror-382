# CreateAccountCreditCardHolderInfo

Container for cardholder information. 

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**address_line1** | **str** | First address line, 255 characters or less.  | 
**address_line2** | **str** | Second address line, 255 characters or less.  | [optional] 
**card_holder_name** | **str** | The card holder&#39;s full name as it appears on the card, e.g., \&quot;John J Smith\&quot;, 50 characters or less. | 
**city** | **str** | City, 40 characters or less.  It is recommended to provide the city and country information when creating a payment method. The information will be used to process payments. If the information is not provided during payment method creation, the city and country data will be missing during payment processing. | 
**country** | **str** | Country; must be a valid country name or abbreviation.  It is recommended to provide the city and country information when creating a payment method. The information will be used to process payments. If the information is not provided during payment method creation, the city and country data will be missing during payment processing. | 
**email** | **str** | Card holder&#39;s email address, 80 characters or less.  | [optional] 
**phone** | **str** | Phone number, 40 characters or less.  | [optional] 
**state** | **str** | State; must be a valid state name or 2-character abbreviation.  | 
**zip_code** | **str** | Zip code, 20 characters or less.  | 

## Example

```python
from zuora_sdk.models.create_account_credit_card_holder_info import CreateAccountCreditCardHolderInfo

# TODO update the JSON string below
json = "{}"
# create an instance of CreateAccountCreditCardHolderInfo from a JSON string
create_account_credit_card_holder_info_instance = CreateAccountCreditCardHolderInfo.from_json(json)
# print the JSON string representation of the object
print(CreateAccountCreditCardHolderInfo.to_json())

# convert the object into a dict
create_account_credit_card_holder_info_dict = create_account_credit_card_holder_info_instance.to_dict()
# create an instance of CreateAccountCreditCardHolderInfo from a dict
create_account_credit_card_holder_info_from_dict = CreateAccountCreditCardHolderInfo.from_dict(create_account_credit_card_holder_info_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


