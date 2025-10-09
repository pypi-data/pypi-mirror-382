# AccountPMMandateInfo

The mandate information for the Credit Card, Apple Pay, Google Pay, Credit Card Reference Transaction, ACH, or Bank Transfer payment method.  The following mandate fields are common to all supported payment methods: * `mandateId` * `mandateReason` * `mandateStatus`  The following mandate fields are specific to the ACH and Bank Transfer payment methods: * `mandateReceivedStatus` * `existingMandateStatus` * `mandateCreationDate` * `mandateUpdateDate`  The following mandate fields are specific to the Credit Card, Apple Pay, and Google Pay payment methods: * `mitTransactionId` * `mitProfileAgreedOn` * `mitConsentAgreementRef` * `mitConsentAgreementSrc` * `mitProfileType` * `mitProfileAction` 

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**existing_mandate_status** | [**PaymentMethodMandateInfoMandateStatus**](PaymentMethodMandateInfoMandateStatus.md) |  | [optional] 
**mandate_creation_date** | **date** | The date on which the mandate was created.  | [optional] 
**mandate_id** | **str** | The mandate ID.  | [optional] 
**mandate_reason** | **str** | The reason of the mandate from the gateway side.  | [optional] 
**mandate_received_status** | [**PaymentMethodMandateInfoMandateStatus**](PaymentMethodMandateInfoMandateStatus.md) |  | [optional] 
**mandate_status** | **str** | The status of the mandate from the gateway side.  | [optional] 
**mandate_update_date** | **date** | The date on which the mandate was updated.  | [optional] 
**mit_consent_agreement_ref** | **str** | Reference for the consent agreement that you have established with the customer.    | [optional] 
**mit_consent_agreement_src** | [**StoredCredentialProfileConsentAgreementSrc**](StoredCredentialProfileConsentAgreementSrc.md) |  | [optional] 
**mit_profile_action** | [**StoredCredentialProfileAction**](StoredCredentialProfileAction.md) |  | [optional] 
**mit_profile_agreed_on** | **date** | The date on which the stored credential profile is agreed. The date format is &#x60;yyyy-mm-dd&#x60;.  | [optional] 
**mit_profile_type** | **str** | Indicates the type of the stored credential profile. If you do not specify the &#x60;mitProfileAction&#x60; field, Zuora will automatically create a stored credential profile for the payment method, with the default value &#x60;Recurring&#x60; set to this field.  | [optional] 
**mit_transaction_id** | **str** | Specifies the ID of the transaction. Only applicable if you set the &#x60;mitProfileAction&#x60; field to &#x60;Persist&#x60;.  | [optional] 

## Example

```python
from zuora_sdk.models.account_pm_mandate_info import AccountPMMandateInfo

# TODO update the JSON string below
json = "{}"
# create an instance of AccountPMMandateInfo from a JSON string
account_pm_mandate_info_instance = AccountPMMandateInfo.from_json(json)
# print the JSON string representation of the object
print(AccountPMMandateInfo.to_json())

# convert the object into a dict
account_pm_mandate_info_dict = account_pm_mandate_info_instance.to_dict()
# create an instance of AccountPMMandateInfo from a dict
account_pm_mandate_info_from_dict = AccountPMMandateInfo.from_dict(account_pm_mandate_info_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


