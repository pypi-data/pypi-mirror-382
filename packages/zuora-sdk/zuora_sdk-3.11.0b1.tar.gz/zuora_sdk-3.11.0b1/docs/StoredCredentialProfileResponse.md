# StoredCredentialProfileResponse


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**activated_on** | **datetime** | The date when the stored credential profile was activated (if applicable).  | [optional] 
**agreed_on** | **datetime** | The date when the stored credential profile was created.  | [optional] 
**brand** | **str** | The stored credential transaction framework. For example, Visa.  | [optional] 
**cancelled_on** | **datetime** | The date when the stored credential profile was cancelled (if applicable).  | [optional] 
**consent_agreement_ref** | **str** | Your reference for the consent agreement that you have established with the customer.  | [optional] 
**consent_agreement_src** | [**StoredCredentialProfileConsentAgreementSrc**](StoredCredentialProfileConsentAgreementSrc.md) |  | [optional] 
**expired_on** | **datetime** | The date when the stored credential profile was expired (if applicable).  | [optional] 
**number** | **int** | The number that identifies the stored credential profile within the payment method.  | [optional] 
**payment_method_id** | **str** | ID of the payment method.  | [optional] 
**status** | [**StoredCredentialProfileStatus**](StoredCredentialProfileStatus.md) |  | [optional] 
**type** | [**StoredCredentialProfileType**](StoredCredentialProfileType.md) |  | [optional] 

## Example

```python
from zuora_sdk.models.stored_credential_profile_response import StoredCredentialProfileResponse

# TODO update the JSON string below
json = "{}"
# create an instance of StoredCredentialProfileResponse from a JSON string
stored_credential_profile_response_instance = StoredCredentialProfileResponse.from_json(json)
# print the JSON string representation of the object
print(StoredCredentialProfileResponse.to_json())

# convert the object into a dict
stored_credential_profile_response_dict = stored_credential_profile_response_instance.to_dict()
# create an instance of StoredCredentialProfileResponse from a dict
stored_credential_profile_response_from_dict = StoredCredentialProfileResponse.from_dict(stored_credential_profile_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


