# CreateOrderResume

Information about an order action of type `Resume`. 

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**extends_term** | **bool** | Specifies whether to extend the subscription term by the length of time the suspension is in effect.  | [optional] 
**resume_periods** | **int** | This field is applicable only when the &#x60;resumePolicy&#x60; field is set to &#x60;FixedPeriodsFromToday&#x60; or &#x60;FixedPeriodsFromSuspendDate&#x60;. It must be used together with the &#x60;resumePeriodsType&#x60; field.   The total number of the periods used to specify when a subscription resumption takes effect. The subscription resumption will take place after the specified time frame (&#x60;suspendPeriods&#x60; multiplied by &#x60;suspendPeriodsType&#x60;) from today&#39;s date.   | [optional] 
**resume_periods_type** | [**ResumePeriodsType**](ResumePeriodsType.md) |  | [optional] 
**resume_policy** | [**ResumePolicy**](ResumePolicy.md) |  | 
**resume_specific_date** | **date** | This field is applicable only when the &#x60;resumePolicy&#x60; field is set to &#x60;SpecificDate&#x60;.  A specific date when the subscription resumption takes effect, in YYYY-MM-DD format. The value should not be earlier than the subscription suspension date.  | [optional] 

## Example

```python
from zuora_sdk.models.create_order_resume import CreateOrderResume

# TODO update the JSON string below
json = "{}"
# create an instance of CreateOrderResume from a JSON string
create_order_resume_instance = CreateOrderResume.from_json(json)
# print the JSON string representation of the object
print(CreateOrderResume.to_json())

# convert the object into a dict
create_order_resume_dict = create_order_resume_instance.to_dict()
# create an instance of CreateOrderResume from a dict
create_order_resume_from_dict = CreateOrderResume.from_dict(create_order_resume_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


