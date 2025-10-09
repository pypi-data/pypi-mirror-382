# RenewalSetting

Specifies the type of the terms that follow the first term if the subscription is renewed. Only applicable if the type of the first term is `TERMED`.  * `RENEW_WITH_SPECIFIC_TERM` - Each renewal term has a predefined duration. The first entry in `renewalTerms` specifies the duration of the second term of the subscription, the second entry in `renewalTerms` specifies the duration of the third term of the subscription, and so on. The last entry in `renewalTerms` specifies the ultimate duration of each renewal term. * `RENEW_TO_EVERGREEN` - The second term of the subscription does not have a predefined duration. 

## Enum

* `RENEW_WITH_SPECIFIC_TERM` (value: `'RENEW_WITH_SPECIFIC_TERM'`)

* `RENEW_TO_EVERGREEN` (value: `'RENEW_TO_EVERGREEN'`)

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


