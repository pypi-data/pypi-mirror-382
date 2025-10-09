# ChangePlanEffectivePolicy

The default value for the `effectivePolicy` field is as follows:   * If the rate plan change (from old to new) is an upgrade, the effective policy is `EffectiveImmediately` by default.   * If the rate plan change (from old to new) is a downgrade, the effective policy is `EffectiveEndOfBillingPeriod` by default.   * Otherwise, the effective policy is `SpecificDate` by default.  Note that if the `effectivePolicy` field is set to `EffectiveEndOfBillingPeriod`, you cannot set the <a href=\"https://knowledgecenter.zuora.com/Zuora_Billing/Subscriptions/Subscriptions/W_Subscription_and_Amendment_Dates#Billing_Trigger_Dates\" target=\"_blank\">billing trigger dates</a> for the subscription as the system will automatically set the trigger dates to the end of billing period, and you cannot set the following billing trigger date settings to `Yes`:   * <a href=\"https://knowledgecenter.zuora.com/Zuora_Billing/Billing_and_Invoicing/Billing_Settings/Define_Default_Subscription_and_Order_Settings#Require_Customer_Acceptance_of_Orders.3F\" target=\"_blank\">Require Customer Acceptance of Orders?</a>   * <a href=\"https://knowledgecenter.zuora.com/Zuora_Billing/Billing_and_Invoicing/Billing_Settings/Define_Default_Subscription_and_Order_Settings#Require_Service_Activation_of_Orders.3F\" target=\"_blank\">Require Service Activation of Orders?</a> 

## Enum

* `EFFECTIVEIMMEDIATELY` (value: `'EffectiveImmediately'`)

* `EFFECTIVEENDOFBILLINGPERIOD` (value: `'EffectiveEndOfBillingPeriod'`)

* `SPECIFICDATE` (value: `'SpecificDate'`)

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


