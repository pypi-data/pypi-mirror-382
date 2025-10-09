# ExpandedAmendment


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**id** | **str** |  | [optional] 
**auto_renew** | **bool** |  | [optional] 
**code** | **str** |  | [optional] 
**contract_effective_date** | **date** |  | [optional] 
**current_term** | **int** |  | [optional] 
**current_term_period_type** | **str** |  | [optional] 
**customer_acceptance_date** | **date** |  | [optional] 
**description** | **str** |  | [optional] 
**effective_date** | **date** |  | [optional] 
**effective_policy** | **str** |  | [optional] 
**name** | **str** |  | [optional] 
**new_rate_plan_id** | **str** |  | [optional] 
**removed_rate_plan_id** | **str** |  | [optional] 
**renewal_setting** | **str** |  | [optional] 
**renewal_term** | **int** |  | [optional] 
**renewal_term_period_type** | **str** |  | [optional] 
**resume_date** | **date** |  | [optional] 
**service_activation_date** | **date** |  | [optional] 
**specific_update_date** | **date** |  | [optional] 
**status** | **str** |  | [optional] 
**subscription_id** | **str** |  | [optional] 
**suspend_date** | **date** |  | [optional] 
**term_start_date** | **date** |  | [optional] 
**term_type** | **str** |  | [optional] 
**type** | **str** |  | [optional] 
**sub_type** | **str** |  | [optional] 
**created_by_id** | **str** |  | [optional] 
**created_date** | **str** |  | [optional] 
**updated_by_id** | **str** |  | [optional] 
**updated_date** | **str** |  | [optional] 
**booking_date** | **date** |  | [optional] 

## Example

```python
from zuora_sdk.models.expanded_amendment import ExpandedAmendment

# TODO update the JSON string below
json = "{}"
# create an instance of ExpandedAmendment from a JSON string
expanded_amendment_instance = ExpandedAmendment.from_json(json)
# print the JSON string representation of the object
print(ExpandedAmendment.to_json())

# convert the object into a dict
expanded_amendment_dict = expanded_amendment_instance.to_dict()
# create an instance of ExpandedAmendment from a dict
expanded_amendment_from_dict = ExpandedAmendment.from_dict(expanded_amendment_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


