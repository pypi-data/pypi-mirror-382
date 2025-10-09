# PaymentMethodACHBankAccountType

The type of bank account associated with the ACH payment. This field is only required if the `type` field is set to `ACH`.  When creating an ACH payment method on Adyen, this field is required by Zuora but it is not required by Adyen. To create the ACH payment method successfully, specify a real value for this field if you can. If it is not possible to get the real value for it, specify any of the allowed values as a dummy value, `Checking` preferably. 

## Enum

* `BUSINESSCHECKING` (value: `'BusinessChecking'`)

* `BUSINESSSAVING` (value: `'BusinessSaving'`)

* `CHECKING` (value: `'Checking'`)

* `SAVING` (value: `'Saving'`)

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


