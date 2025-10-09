# UpdateAccountingPeriodRequest


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**end_date** | **date** | The end date of the accounting period in yyyy-mm-dd format, for example, \&quot;2016-02-19\&quot;. | [optional] 
**fiscal_year** | **str** | Fiscal year of the accounting period in yyyy format, for example, \&quot;2016\&quot;. | [optional] 
**fiscal_quarter** | **int** |  | [optional] 
**name** | **str** | Name of the accounting period.  Accounting period name must be unique. Maximum of 100 characters.  | [optional] 
**notes** | **str** | Notes about the accounting period.  Maximum of 255 characters.  | [optional] 
**start_date** | **date** | The start date of the accounting period in yyyy-mm-dd format, for example, \&quot;2016-02-19\&quot;. | [optional] 

## Example

```python
from zuora_sdk.models.update_accounting_period_request import UpdateAccountingPeriodRequest

# TODO update the JSON string below
json = "{}"
# create an instance of UpdateAccountingPeriodRequest from a JSON string
update_accounting_period_request_instance = UpdateAccountingPeriodRequest.from_json(json)
# print the JSON string representation of the object
print(UpdateAccountingPeriodRequest.to_json())

# convert the object into a dict
update_accounting_period_request_dict = update_accounting_period_request_instance.to_dict()
# create an instance of UpdateAccountingPeriodRequest from a dict
update_accounting_period_request_from_dict = UpdateAccountingPeriodRequest.from_dict(update_accounting_period_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


