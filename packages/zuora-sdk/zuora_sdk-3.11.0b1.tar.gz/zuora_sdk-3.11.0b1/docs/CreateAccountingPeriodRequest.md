# CreateAccountingPeriodRequest


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**end_date** | **date** | The end date of the accounting period in yyyy-mm-dd format, for example, \&quot;2016-02-19\&quot;. | 
**fiscal_year** | **int** | Fiscal year of the accounting period in yyyy format. | 
**fiscal_quarter** | **int** |  | [optional] 
**name** | **str** | Name of the accounting period.  Accounting period name must be unique. Maximum of 100 characters.  | 
**notes** | **str** | Notes about the accounting period.  Maximum of 255 characters.  | [optional] 
**start_date** | **date** | The start date of the accounting period in yyyy-mm-dd format, for example, \&quot;2016-02-19\&quot;. | 
**organization_labels** | [**List[OrganizationLabel]**](OrganizationLabel.md) | Organization labels.  | [optional] 

## Example

```python
from zuora_sdk.models.create_accounting_period_request import CreateAccountingPeriodRequest

# TODO update the JSON string below
json = "{}"
# create an instance of CreateAccountingPeriodRequest from a JSON string
create_accounting_period_request_instance = CreateAccountingPeriodRequest.from_json(json)
# print the JSON string representation of the object
print(CreateAccountingPeriodRequest.to_json())

# convert the object into a dict
create_accounting_period_request_dict = create_accounting_period_request_instance.to_dict()
# create an instance of CreateAccountingPeriodRequest from a dict
create_accounting_period_request_from_dict = CreateAccountingPeriodRequest.from_dict(create_accounting_period_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


