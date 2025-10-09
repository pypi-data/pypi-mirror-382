# CreateStoredCredentialProfileRequest


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**action** | [**StoredCredentialProfileAction**](StoredCredentialProfileAction.md) |  | [optional] 
**agreed_on** | **date** | The date on which the profile is agreed. The date format is &#x60;yyyy-mm-dd&#x60;.  | [optional] 
**auth_gateway** | **str** | Specifies the ID of the payment gateway that Zuora will use when activating the stored credential profile.  | [optional] 
**card_security_code** | **str** | The security code of the credit card.  | [optional] 
**consent_agreement_ref** | **str** | Specifies your reference for the consent agreement that you have established with the customer.  | [optional] 
**consent_agreement_src** | [**StoredCredentialProfileConsentAgreementSrc**](StoredCredentialProfileConsentAgreementSrc.md) |  | 
**network_transaction_id** | **str** | The ID of a network transaction. Only applicable if you set the &#x60;action&#x60; field to &#x60;Persist&#x60;.  | [optional] 
**status** | [**CreateStoredCredentialProfileRequestStatus**](CreateStoredCredentialProfileRequestStatus.md) |  | 
**type** | [**StoredCredentialProfileType**](StoredCredentialProfileType.md) |  | 

## Example

```python
from zuora_sdk.models.create_stored_credential_profile_request import CreateStoredCredentialProfileRequest

# TODO update the JSON string below
json = "{}"
# create an instance of CreateStoredCredentialProfileRequest from a JSON string
create_stored_credential_profile_request_instance = CreateStoredCredentialProfileRequest.from_json(json)
# print the JSON string representation of the object
print(CreateStoredCredentialProfileRequest.to_json())

# convert the object into a dict
create_stored_credential_profile_request_dict = create_stored_credential_profile_request_instance.to_dict()
# create an instance of CreateStoredCredentialProfileRequest from a dict
create_stored_credential_profile_request_from_dict = CreateStoredCredentialProfileRequest.from_dict(create_stored_credential_profile_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


