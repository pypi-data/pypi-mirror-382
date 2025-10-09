# AccountSummaryResponse


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**basic_info** | [**AccountSummaryBasicInfo**](AccountSummaryBasicInfo.md) |  | [optional] 
**bill_to_contact** | [**Contact**](Contact.md) |  | [optional] 
**invoices** | [**List[AccountSummaryInvoice]**](AccountSummaryInvoice.md) | Container for invoices. Only returns the last 6 invoices.  | [optional] 
**payments** | [**List[AccountSummaryPayment]**](AccountSummaryPayment.md) | Container for payments. Only returns the last 6 payments.  | [optional] 
**sold_to_contact** | [**Contact**](Contact.md) |  | [optional] 
**ship_to_contact** | [**Contact**](Contact.md) |  | [optional] 
**subscriptions** | [**List[AccountSummarySubscription]**](AccountSummarySubscription.md) | Container for subscriptions.  | [optional] 
**success** | **bool** | Returns &#x60;true&#x60; if the request was processed successfully.  | [optional] 
**tax_info** | [**TaxInfo**](TaxInfo.md) |  | [optional] 
**usage** | [**List[AccountSummaryUsage]**](AccountSummaryUsage.md) | Container for usage data. Only returns the last 6 months of usage.   **Note:** If the Active Rating feature is enabled, no usage data is returned in the response body field. | [optional] 

## Example

```python
from zuora_sdk.models.account_summary_response import AccountSummaryResponse

# TODO update the JSON string below
json = "{}"
# create an instance of AccountSummaryResponse from a JSON string
account_summary_response_instance = AccountSummaryResponse.from_json(json)
# print the JSON string representation of the object
print(AccountSummaryResponse.to_json())

# convert the object into a dict
account_summary_response_dict = account_summary_response_instance.to_dict()
# create an instance of AccountSummaryResponse from a dict
account_summary_response_from_dict = AccountSummaryResponse.from_dict(account_summary_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


