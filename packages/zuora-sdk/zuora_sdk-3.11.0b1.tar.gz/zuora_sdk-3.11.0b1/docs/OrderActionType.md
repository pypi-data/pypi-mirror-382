# OrderActionType

Type of order action.  Unless the type of order action is `RenewSubscription`, you must use the corresponding field to provide information about the order action. For example, if the type of order action is `AddProduct`, you must set the `addProduct` field.  Zuora returns an error if you set a field that corresponds to a different type of order action. For example, if the type of order action is `AddProduct`, Zuora returns an error if you set the `updateProduct` field.  A [pending order](https://knowledgecenter.zuora.com/BC_Subscription_Management/Orders/Pending_Order_and_Subscription) supports the following order actions:  * CreateSubscription  * AddProduct  * UpdateProduct  * RemoveProduct  * RenewSubscription  * TermsAndConditions  * ChangePlan  However, pending orders created through all order actions except for \"Create new subscription\":  * Do not impact the subscription status.  * Are in **Limited Availability**. If you want to have access to the feature, submit a request at [Zuora Global Support](https://support.zuora.com).   A pending order is created in either of the following conditions:  * [Zuora is configured to require service activation](https://knowledgecenter.zuora.com/CB_Billing/Billing_Settings/Define_Default_Subscription_Settings#Require_Service_Activation_of_Orders.3F) and the service activation date is not set in your \"Create an order\" call.  * [Zuora is configured to require customer acceptance](https://knowledgecenter.zuora.com/CB_Billing/Billing_Settings/Define_Default_Subscription_Settings#Require_Customer_Acceptance_of_Orders.3F) and the customer acceptance date is not set in your \"Create an order\" call.  * When a charge in the subscription has its `triggerEvent` field set as `SpecificDate` and the `specificTriggerDate` field is not set in your \"Create an order\" API call.  **Note**: The change plan type of order action is currently not supported for Billing - Revenue Integration. When Billing - Revenue Integration is enabled, the change plan type of order action will no longer be applicable in Zuora Billing. 

## Enum

* `CREATESUBSCRIPTION` (value: `'CreateSubscription'`)

* `TERMSANDCONDITIONS` (value: `'TermsAndConditions'`)

* `ADDPRODUCT` (value: `'AddProduct'`)

* `UPDATEPRODUCT` (value: `'UpdateProduct'`)

* `REMOVEPRODUCT` (value: `'RemoveProduct'`)

* `RENEWSUBSCRIPTION` (value: `'RenewSubscription'`)

* `CANCELSUBSCRIPTION` (value: `'CancelSubscription'`)

* `OWNERTRANSFER` (value: `'OwnerTransfer'`)

* `SUSPEND` (value: `'Suspend'`)

* `RESUME` (value: `'Resume'`)

* `CHANGEPLAN` (value: `'ChangePlan'`)

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


