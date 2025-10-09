# CreateAccountingCodeResponse


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**id** | **str** | ID of the newly created accounting code.  | [optional] 
**success** | **bool** | Returns &#x60;true&#x60; if the request was processed successfully.  | [optional] 

## Example

```python
from zuora_sdk.models.create_accounting_code_response import CreateAccountingCodeResponse

# TODO update the JSON string below
json = "{}"
# create an instance of CreateAccountingCodeResponse from a JSON string
create_accounting_code_response_instance = CreateAccountingCodeResponse.from_json(json)
# print the JSON string representation of the object
print(CreateAccountingCodeResponse.to_json())

# convert the object into a dict
create_accounting_code_response_dict = create_accounting_code_response_instance.to_dict()
# create an instance of CreateAccountingCodeResponse from a dict
create_accounting_code_response_from_dict = CreateAccountingCodeResponse.from_dict(create_accounting_code_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


