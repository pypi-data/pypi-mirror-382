# RegenerateBillingRequest


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**type** | **str** |  | 
**id** | **str** | Id of Invoice, CreditMemo, DebitMemo, or InvoiceItemAdjustment  | [optional] 
**number** | **str** | Number of Invoice, CreditMemo, DebitMemo, or InvoiceItemAdjustment  | [optional] 

## Example

```python
from zuora_sdk.models.regenerate_billing_request import RegenerateBillingRequest

# TODO update the JSON string below
json = "{}"
# create an instance of RegenerateBillingRequest from a JSON string
regenerate_billing_request_instance = RegenerateBillingRequest.from_json(json)
# print the JSON string representation of the object
print(RegenerateBillingRequest.to_json())

# convert the object into a dict
regenerate_billing_request_dict = regenerate_billing_request_instance.to_dict()
# create an instance of RegenerateBillingRequest from a dict
regenerate_billing_request_from_dict = RegenerateBillingRequest.from_dict(regenerate_billing_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


