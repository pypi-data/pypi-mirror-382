# UpdateUsageRequest


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**start_date_time** | **datetime** |  The start date and time of a range of time when usage is tracked. Zuora uses this field value to determine the usage date. Unlike the &#x60;EndDateTime&#x60;, the &#x60;StartDateTime&#x60; field does affect usage calculation. **Character limit**: 29 **Values**: a valid date and time value | [optional] 
**end_date_time** | **datetime** |  The end date and time of a range of time when usage is tracked. Use this field for reporting; this field doesn&#39;t affect usage calculation. **Character limit**: 29 **Values**: a valid date and time value | [optional] 
**uom** | **str** |  Specifies the units to measure usage. Units of measure are configured in the web-based UI. Your values depend on your configuration in **Billing Settings**. **Character limit**: **Values**: a valid unit of measure | [optional] 
**quantity** | **float** |  Indicates the number of units used. **Character limit**: 16 **Values**: a valid decimal amount equal to or greater than 0 | [optional] 
**rbe_status** | **str** |  Indicates if the rating and billing engine (RBE) processed usage data for an invoice. **Character limit**: 9 **Values**: automatically generated to be one of the following values: &#x60;Importing&#x60;, &#x60;Pending&#x60;, &#x60;Processed&#x60; | [optional] 

## Example

```python
from zuora_sdk.models.update_usage_request import UpdateUsageRequest

# TODO update the JSON string below
json = "{}"
# create an instance of UpdateUsageRequest from a JSON string
update_usage_request_instance = UpdateUsageRequest.from_json(json)
# print the JSON string representation of the object
print(UpdateUsageRequest.to_json())

# convert the object into a dict
update_usage_request_dict = update_usage_request_instance.to_dict()
# create an instance of UpdateUsageRequest from a dict
update_usage_request_from_dict = UpdateUsageRequest.from_dict(update_usage_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


