# GetPaymentRunSummaryTotalValuesResponse


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**total_value_of_credit_balance** | **str** | **Note:** This field is only available if you have the Credit Balance feature enabled.   The total amount of credit balance after the payment run is completed. | [optional] 
**total_value_of_credit_memos** | **str** | **Note:** This field is only available if you have the Invoice Settlement feature enabled.   The total amount of credit memos that are successfully processed in the payment run. | [optional] 
**total_value_of_debit_memos** | **str** | **Note:** This field is only available if you have the Invoice Settlement feature enabled.   The total amount of debit memos that are picked up for processing in the payment run. | [optional] 
**total_value_of_errors** | **str** | The total amount of receivables associated with the payments with the status of &#x60;Error&#x60; and &#x60;Processing&#x60;. | [optional] 
**total_value_of_invoices** | **str** | **Note:** This field is only available if you have the Invoice Settlement feature enabled.   The total amount of invoices that are picked up for processing in the payment run. | [optional] 
**total_value_of_payments** | **str** | The total amount of payments that are successfully processed in the payment run. | [optional] 
**total_value_of_receivables** | **str** | The total amount of receivables associated with the payment run.   The value of this field is the sum of the value of the &#x60;totalValueOfInvoices&#x60; field and that of the &#x60;totalValueOfDebitMemos&#x60; field. | [optional] 
**total_value_of_unapplied_payments** | **str** | **Note:** This field is only available if you have the Invoice Settlement feature enabled.   The total amount of unapplied payments that are successfully processed in the payment run. | [optional] 
**total_value_of_unprocessed_debit_memos** | **str** | **Note:** This field is only available if you have the Invoice Settlement feature enabled.   The total amount of debit memos with remaining positive balances after the payment run is completed. | [optional] 
**total_value_of_unprocessed_invoices** | **str** | **Note:** This field is only available if you have the Invoice Settlement feature enabled.   The total amount of invoices with remaining positive balances after the payment run is completed. | [optional] 
**total_value_of_unprocessed_receivables** | **str** | The total amount of receivables with remaining positive balances after the payment run is completed. | [optional] 

## Example

```python
from zuora_sdk.models.get_payment_run_summary_total_values_response import GetPaymentRunSummaryTotalValuesResponse

# TODO update the JSON string below
json = "{}"
# create an instance of GetPaymentRunSummaryTotalValuesResponse from a JSON string
get_payment_run_summary_total_values_response_instance = GetPaymentRunSummaryTotalValuesResponse.from_json(json)
# print the JSON string representation of the object
print(GetPaymentRunSummaryTotalValuesResponse.to_json())

# convert the object into a dict
get_payment_run_summary_total_values_response_dict = get_payment_run_summary_total_values_response_instance.to_dict()
# create an instance of GetPaymentRunSummaryTotalValuesResponse from a dict
get_payment_run_summary_total_values_response_from_dict = GetPaymentRunSummaryTotalValuesResponse.from_dict(get_payment_run_summary_total_values_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


