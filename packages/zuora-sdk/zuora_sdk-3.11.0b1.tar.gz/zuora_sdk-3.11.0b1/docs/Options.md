# Options

Invoice or Payment.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**billing_target_date** | **date** | Date through which to calculate charges if an invoice is generated. See [What is a Target Date?](https://knowledgecenter.zuora.com/Billing/Billing_and_Payments/J_Billing_Operations/G_Bill_Runs/Creating_Bill_Runs#What_is_a_Target_Date.3F). | [optional] 
**collect_payment** | **bool** | Indicates if the current request needs to collect payments. This value can not be &#39;true&#39; when &#39;runBilling&#39; flag is &#39;false&#39;. | [optional] 
**max_subscriptions_per_account** | **float** |  | [optional] 
**run_billing** | **bool** | Indicates if the current request needs to generate an invoice. The invoice will be generated against all subscriptions included in this order. | [optional] 

## Example

```python
from zuora_sdk.models.options import Options

# TODO update the JSON string below
json = "{}"
# create an instance of Options from a JSON string
options_instance = Options.from_json(json)
# print the JSON string representation of the object
print(Options.to_json())

# convert the object into a dict
options_dict = options_instance.to_dict()
# create an instance of Options from a dict
options_from_dict = Options.from_dict(options_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


