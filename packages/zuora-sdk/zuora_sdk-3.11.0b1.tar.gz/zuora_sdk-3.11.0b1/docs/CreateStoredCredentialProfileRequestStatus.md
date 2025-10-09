# CreateStoredCredentialProfileRequestStatus

Specifies the status of the stored credential profile.  - `Active` - Use this value if you are creating the stored credential profile after receiving the customer's consent, or if the stored credential profile represents a stored credential profile in an external system.    You can use the `action` field to specify how Zuora activates the stored credential profile.   - `Agreed` - Use this value if you are migrating the payment method to the stored credential transaction framework.    In this case, Zuora will not send a cardholder-initiated transaction (CIT) to the payment gateway to validate the stored credential profile. 

## Enum

* `AGREED` (value: `'Agreed'`)

* `ACTIVE` (value: `'Active'`)

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


