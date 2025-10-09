# PaymentRunResponse


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**account_id** | **str** | The ID of the customer account associated with the payment run.  | [optional] 
**apply_credit_balance** | **bool** | **Note:** This field is only available if you have the Credit Balance feature enabled and the Invoice Settlement feature disabled.  Whether to apply credit balances in the payment run. This field is only available when you have Invoice Settlement feature disabled.  | [optional] 
**auto_apply_credit_memo** | **bool** | **Note:** This field is only available if you have [Invoice Settlement](https://knowledgecenter.zuora.com/Billing/Billing_and_Payments/Invoice_Settlement) enabled. The Invoice Settlement feature is generally available as of Zuora Billing Release 296 (March 2021). This feature includes Unapplied Payments, Credit and Debit Memo, and Invoice Item Settlement. If you want to enable Invoice Settlement, see [Invoice Settlement Enablement and Checklist Guide](https://knowledgecenter.zuora.com/Billing/Billing_and_Payments/Invoice_Settlement/Invoice_Settlement_Migration_Checklist_and_Guide) for more information.  Whether to automatically apply a posted credit memo to one or more receivables in the payment run.  | [optional] 
**auto_apply_unapplied_payment** | **bool** | **Note:** This field is only available if you have [Invoice Settlement](https://knowledgecenter.zuora.com/Billing/Billing_and_Payments/Invoice_Settlement) enabled. The Invoice Settlement feature is generally available as of Zuora Billing Release 296 (March 2021). This feature includes Unapplied Payments, Credit and Debit Memo, and Invoice Item Settlement. If you want to enable Invoice Settlement, see [Invoice Settlement Enablement and Checklist Guide](https://knowledgecenter.zuora.com/Billing/Billing_and_Payments/Invoice_Settlement/Invoice_Settlement_Migration_Checklist_and_Guide) for more information.  Whether to automatically apply unapplied payments to  one or more receivables in the payment run.  | [optional] 
**batch** | **str** | The alias name given to a batch.  | [optional] 
**bill_cycle_day** | **str** | The billing cycle day (BCD), the day of the month when a bill run generates invoices for the account.   | [optional] 
**billing_run_id** | **str** | The ID of the bill run.  | [optional] 
**collect_payment** | **bool** | Whether to process electronic payments during the execution of payment runs.   | [optional] 
**completed_on** | **str** | The date and time when the payment run is completed, in &#x60;yyyy-mm-dd hh:mm:ss&#x60; format. For example, 2017-03-01 11:39:58.  | [optional] 
**consolidated_payment** | **bool** | **Note:** The **Process Electronic Payment** permission also needs to be allowed for a Manage Payment Runs role to work. See [Payments Roles](https://knowledgecenter.zuora.com/CF_Users_and_Administrators/A_Administrator_Settings/User_Roles/e_Payments_Roles) for more information.   Whether to process a single payment for all receivables that are due on an account.  | [optional] 
**created_by_id** | **str** | The ID of the Zuora user who created the payment run.  | [optional] 
**created_date** | **str** | The date and time when the payment run was created, in &#x60;yyyy-mm-dd hh:mm:ss&#x60; format. For example, 2017-03-01 15:31:10.  | [optional] 
**currency** | **str** | A currency defined in the web-based UI administrative settings.  | [optional] 
**executed_on** | **str** | The date and time when the payment run is executed, in &#x60;yyyy-mm-dd hh:mm:ss&#x60; format. For example, 2017-03-01 11:30:37.  | [optional] 
**id** | **str** | The ID of the payment run.  | [optional] 
**number** | **str** | The identification number of the payment run.  | [optional] 
**payment_gateway_id** | **str** | The ID of the gateway instance that processes the payment.  | [optional] 
**process_payment_with_closed_pm** | **bool** | **Note:** The **Process Electronic Payment** permission also needs to be allowed for a Manage Payment Runs role to work. See [Payments Roles](https://knowledgecenter.zuora.com/CF_Users_and_Administrators/A_Administrator_Settings/User_Roles/e_Payments_Roles) for more information.   Whether to process payments even if the default payment method is closed.  | [optional] 
**run_date** | **str** | The date and time when the scheduled payment run is to be executed for collecting payments.  | [optional] 
**payment_gateway_number** | **str** |  | [optional] 
**status** | [**PaymentRunStatus**](PaymentRunStatus.md) |  | [optional] 
**target_date** | **str** | The target date used to determine which receivables to be collected in the payment run.   | [optional] 
**updated_by_id** | **str** | The ID of the Zuora user who last updated the payment run.  | [optional] 
**updated_date** | **str** | The date and time when the payment run was last updated, in &#x60;yyyy-mm-dd hh:mm:ss&#x60; format. For example, 2017-03-02 15:36:10.  | [optional] 
**organization_labels** | [**List[OrganizationLabel]**](OrganizationLabel.md) | The organization(s) that the payment run is created for.  For each item in the array, either the &#x60;organizationId&#x60; or the &#x60;organizationName&#x60; field is required.  This field is only required when you have already turned on Multi-Org feature.  | [optional] 
**process_id** | **str** | The Id of the process that handle the operation.  | [optional] 
**request_id** | **str** | Unique request identifier. If you need to contact us about a specific request, providing the request identifier will ensure the fastest possible resolution.  | [optional] 
**reasons** | [**List[FailedReason]**](FailedReason.md) |  | [optional] 
**success** | **bool** | Indicates whether the call succeeded.  | [optional] [default to True]

## Example

```python
from zuora_sdk.models.payment_run_response import PaymentRunResponse

# TODO update the JSON string below
json = "{}"
# create an instance of PaymentRunResponse from a JSON string
payment_run_response_instance = PaymentRunResponse.from_json(json)
# print the JSON string representation of the object
print(PaymentRunResponse.to_json())

# convert the object into a dict
payment_run_response_dict = payment_run_response_instance.to_dict()
# create an instance of PaymentRunResponse from a dict
payment_run_response_from_dict = PaymentRunResponse.from_dict(payment_run_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


