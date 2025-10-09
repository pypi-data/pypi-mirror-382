# PostBillRunRequest


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**invoice_date** | **date** | The date that appears on the invoice being created, in &#x60;yyyy-mm-dd&#x60; format.    The value cannot fall in a closed accounting period. | 

## Example

```python
from zuora_sdk.models.post_bill_run_request import PostBillRunRequest

# TODO update the JSON string below
json = "{}"
# create an instance of PostBillRunRequest from a JSON string
post_bill_run_request_instance = PostBillRunRequest.from_json(json)
# print the JSON string representation of the object
print(PostBillRunRequest.to_json())

# convert the object into a dict
post_bill_run_request_dict = post_bill_run_request_instance.to_dict()
# create an instance of PostBillRunRequest from a dict
post_bill_run_request_from_dict = PostBillRunRequest.from_dict(post_bill_run_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


