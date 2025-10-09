# PreviewOrderCreateSubscriptionTerms

Container for the terms and renewal settings of the subscription. 

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**auto_renew** | **bool** | Specifies whether the subscription automatically renews at the end of the each term. Only applicable if the type of the first term is &#x60;TERMED&#x60;.  | [optional] 
**initial_term** | [**InitialTerm**](InitialTerm.md) |  | 
**renewal_setting** | [**RenewalSetting**](RenewalSetting.md) |  | [optional] 
**renewal_terms** | [**List[RenewalTerm]**](RenewalTerm.md) | List of renewal terms of the subscription. Only applicable if the type of the first term is &#x60;TERMED&#x60; and the value of the &#x60;renewalSetting&#x60; field is &#x60;RENEW_WITH_SPECIFIC_TERM&#x60;.  | [optional] 

## Example

```python
from zuora_sdk.models.preview_order_create_subscription_terms import PreviewOrderCreateSubscriptionTerms

# TODO update the JSON string below
json = "{}"
# create an instance of PreviewOrderCreateSubscriptionTerms from a JSON string
preview_order_create_subscription_terms_instance = PreviewOrderCreateSubscriptionTerms.from_json(json)
# print the JSON string representation of the object
print(PreviewOrderCreateSubscriptionTerms.to_json())

# convert the object into a dict
preview_order_create_subscription_terms_dict = preview_order_create_subscription_terms_instance.to_dict()
# create an instance of PreviewOrderCreateSubscriptionTerms from a dict
preview_order_create_subscription_terms_from_dict = PreviewOrderCreateSubscriptionTerms.from_dict(preview_order_create_subscription_terms_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


