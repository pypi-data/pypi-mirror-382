# GetBillingAdjustmentsBySubscriptionNumberResponse


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**process_id** | **str** | The Id of the process that handle the operation.  | [optional] 
**request_id** | **str** | Unique request identifier. If you need to contact us about a specific request, providing the request identifier will ensure the fastest possible resolution.  | [optional] 
**reasons** | [**List[FailedReason]**](FailedReason.md) |  | [optional] 
**success** | **bool** | Indicates whether the call succeeded.  | [optional] [default to True]
**adjustments** | [**List[BillingAdjustment]**](BillingAdjustment.md) | Container for all the adjustments of a subscription.  | [optional] 

## Example

```python
from zuora_sdk.models.get_billing_adjustments_by_subscription_number_response import GetBillingAdjustmentsBySubscriptionNumberResponse

# TODO update the JSON string below
json = "{}"
# create an instance of GetBillingAdjustmentsBySubscriptionNumberResponse from a JSON string
get_billing_adjustments_by_subscription_number_response_instance = GetBillingAdjustmentsBySubscriptionNumberResponse.from_json(json)
# print the JSON string representation of the object
print(GetBillingAdjustmentsBySubscriptionNumberResponse.to_json())

# convert the object into a dict
get_billing_adjustments_by_subscription_number_response_dict = get_billing_adjustments_by_subscription_number_response_instance.to_dict()
# create an instance of GetBillingAdjustmentsBySubscriptionNumberResponse from a dict
get_billing_adjustments_by_subscription_number_response_from_dict = GetBillingAdjustmentsBySubscriptionNumberResponse.from_dict(get_billing_adjustments_by_subscription_number_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


