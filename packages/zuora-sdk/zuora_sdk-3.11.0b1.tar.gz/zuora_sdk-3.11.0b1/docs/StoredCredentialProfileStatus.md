# StoredCredentialProfileStatus

The status of the stored credential profile.  * `Agreed` - The stored credential profile has not been validated via an authorization transaction with the payment gateway. * `Active` - The stored credential profile has been validated via an authorization transaction with the payment gateway. * `Cancelled` - The stored credentials are no longer valid, per a customer request. Zuora cannot use the stored credentials in transactions. * `Expired` - The stored credentials are no longer valid, per an expiration policy in the stored credential transaction framework. Zuora cannot use the stored credentials in transactions. 

## Enum

* `AGREED` (value: `'Agreed'`)

* `ACTIVE` (value: `'Active'`)

* `CANCELLED` (value: `'Cancelled'`)

* `EXPIRED` (value: `'Expired'`)

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


