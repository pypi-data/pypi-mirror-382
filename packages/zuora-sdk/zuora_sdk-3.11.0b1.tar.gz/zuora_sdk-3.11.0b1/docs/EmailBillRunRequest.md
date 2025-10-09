# EmailBillRunRequest


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**resend** | **bool** | Whether to send out emails for all the billing documents that are associated with the bill run. If the value is &#x60;false&#x60;, emails are sent out only for the billing documents that never have emails sent out. | [optional] [default to False]

## Example

```python
from zuora_sdk.models.email_bill_run_request import EmailBillRunRequest

# TODO update the JSON string below
json = "{}"
# create an instance of EmailBillRunRequest from a JSON string
email_bill_run_request_instance = EmailBillRunRequest.from_json(json)
# print the JSON string representation of the object
print(EmailBillRunRequest.to_json())

# convert the object into a dict
email_bill_run_request_dict = email_bill_run_request_instance.to_dict()
# create an instance of EmailBillRunRequest from a dict
email_bill_run_request_from_dict = EmailBillRunRequest.from_dict(email_bill_run_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


