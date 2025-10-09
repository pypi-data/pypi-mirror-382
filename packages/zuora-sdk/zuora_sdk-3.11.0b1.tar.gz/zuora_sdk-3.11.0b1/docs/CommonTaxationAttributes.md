# CommonTaxationAttributes


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**taxable** | **bool** | The flag to indicate whether the charge is taxable. If this field is set to true, both the fields &#x60;taxCode&#x60; and &#x60;taxMode&#x60; are required.  | [optional] 
**tax_code** | **str** | The taxCode of a charge. This field is available when the field &#39;taxable&#39; is set to true.  | [optional] 
**tax_mode** | **str** | The taxMode of a charge.  Values: * &#x60;TaxExclusive&#x60; * &#x60;TaxInclusive&#x60; This field is available when the field &#39;taxable&#39; is set to true.  | [optional] 

## Example

```python
from zuora_sdk.models.common_taxation_attributes import CommonTaxationAttributes

# TODO update the JSON string below
json = "{}"
# create an instance of CommonTaxationAttributes from a JSON string
common_taxation_attributes_instance = CommonTaxationAttributes.from_json(json)
# print the JSON string representation of the object
print(CommonTaxationAttributes.to_json())

# convert the object into a dict
common_taxation_attributes_dict = common_taxation_attributes_instance.to_dict()
# create an instance of CommonTaxationAttributes from a dict
common_taxation_attributes_from_dict = CommonTaxationAttributes.from_dict(common_taxation_attributes_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


