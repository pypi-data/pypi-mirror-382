# RefundPart


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**amount** | **float** | The amount of the refund part.  | [optional] 
**created_by_id** | **str** | The ID of the Zuora user who created the refund part.  | [optional] 
**created_date** | **str** | The date and time when the refund part was created, in &#x60;yyyy-mm-dd hh:mm:ss&#x60; format. For example, 2017-03-01 15:31:10. | [optional] 
**credit_memo_id** | **str** | The ID of the credit memo associated with the refund part.  | [optional] 
**id** | **str** | The ID of the refund part.  | [optional] 
**payment_id** | **str** | The ID of the payment associated with the refund part.  | [optional] 
**updated_by_id** | **str** | The ID of the Zuora user who last updated the refund part.  | [optional] 
**updated_date** | **str** | The date and time when the refund part was last updated, in &#x60;yyyy-mm-dd hh:mm:ss&#x60; format. For example, 2017-03-02 15:36:10. | [optional] 
**organization_label** | **str** |  | [optional] 

## Example

```python
from zuora_sdk.models.refund_part import RefundPart

# TODO update the JSON string below
json = "{}"
# create an instance of RefundPart from a JSON string
refund_part_instance = RefundPart.from_json(json)
# print the JSON string representation of the object
print(RefundPart.to_json())

# convert the object into a dict
refund_part_dict = refund_part_instance.to_dict()
# create an instance of RefundPart from a dict
refund_part_from_dict = RefundPart.from_dict(refund_part_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


