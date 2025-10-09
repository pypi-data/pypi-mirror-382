# UpdateSubscriptionChargeCustomFieldsOfASpecifiedVersion


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**charge_id** | **str** | Use either this field or the &#x60;chargeNumber&#x60; field to specify the charge for which you will be updating the custom fields. By using this field you actually specify a specific charge segment of a charge. See [Segmented rate plan charges](https://knowledgecenter.zuora.com/Central_Platform/API/G_SOAP_API/E1_SOAP_API_Object_Reference/RatePlanCharge#Segmented_rate_plan_charges) for more information about charge segments. | [optional] 
**charge_number** | **str** | Use either this field or the &#x60;chargeId&#x60; field to specify the charge for which you will be updating the custom fields. By using this field you actually specify the last charge segment of a charge. See [Segmented rate plan charges](https://knowledgecenter.zuora.com/Central_Platform/API/G_SOAP_API/E1_SOAP_API_Object_Reference/RatePlanCharge#Segmented_rate_plan_charges) for more information about charge segments. | [optional] 
**custom_fields** | **Dict[str, object]** | Container for custom fields of a Rate Plan Charge object.  | [optional] 

## Example

```python
from zuora_sdk.models.update_subscription_charge_custom_fields_of_a_specified_version import UpdateSubscriptionChargeCustomFieldsOfASpecifiedVersion

# TODO update the JSON string below
json = "{}"
# create an instance of UpdateSubscriptionChargeCustomFieldsOfASpecifiedVersion from a JSON string
update_subscription_charge_custom_fields_of_a_specified_version_instance = UpdateSubscriptionChargeCustomFieldsOfASpecifiedVersion.from_json(json)
# print the JSON string representation of the object
print(UpdateSubscriptionChargeCustomFieldsOfASpecifiedVersion.to_json())

# convert the object into a dict
update_subscription_charge_custom_fields_of_a_specified_version_dict = update_subscription_charge_custom_fields_of_a_specified_version_instance.to_dict()
# create an instance of UpdateSubscriptionChargeCustomFieldsOfASpecifiedVersion from a dict
update_subscription_charge_custom_fields_of_a_specified_version_from_dict = UpdateSubscriptionChargeCustomFieldsOfASpecifiedVersion.from_dict(update_subscription_charge_custom_fields_of_a_specified_version_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


