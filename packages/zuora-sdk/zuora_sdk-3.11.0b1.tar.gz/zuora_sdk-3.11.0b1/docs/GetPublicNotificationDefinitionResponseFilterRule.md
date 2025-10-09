# GetPublicNotificationDefinitionResponseFilterRule



## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**condition** | **str** | The filter rule conditions, written in [JEXL](http://commons.apache.org/proper/commons-jexl/).  The rule might contain event context merge fields and data source merge fields. Data source merge fields must be from [the base object of the event or from the joined objects of the base object](https://knowledgecenter.zuora.com/DC_Developers/M_Export_ZOQL#Data_Sources_and_Objects). Notifications with invalid merge fields will fail to evaluate, thus will not be invoked. For example, to trigger an event when an invoice is posted with the amount over 1000, you would define the following condition on the &#x60;Invoice&#x60; object:   &#x60;&#x60;&#x60;changeType &#x3D;&#x3D; &#39;UPDATE&#39; &amp;&amp; Invoice.Status &#x3D;&#x3D; &#39;Posted&#39; &amp;&amp; Invoice.Status_old !&#x3D; &#39;Posted&#39; &amp;&amp; Invoice.Amount &gt; 1000&#x60;&#x60;&#x60;   There are conventions and keywords you need to be aware of. For example:   * &#x60;changeType&#x60; is a keyword to specify what kind of change happened to the object. Allowed values are &#x60;INSERT&#x60;, &#x60;UPDATE&#x60; or &#x60;Delete&#x60;.   * &#x60;Invoice.Status&#x60; refers to field &#x60;Status&#x60; of the Zuora object &#x60;Invoice&#x60;.   * A variable with the &#x60;_old&#x60; suffix means it’s a previous value of the corresponding object field. The \&quot;_old\&quot; fields are only available on the base objects. | [optional] 
**description** | **str** | The description of the filter rule. | [optional] 
**event_type_name** | **str** | The value is &#x60;null&#x60;. | [optional] 
**id** | **str** | The ID of the filter rule. If not specified or null, the notification definition is always qualified to process events of \&quot;eventType\&quot;. | [optional] 
**created_by** | **str** | The user who created the notification definition. | [optional] 
**created_on** | **str** | The user who created the notification definition. | [optional] 
**parameters** | [**Dict[str, FilterRuleParameterDefinition]**](FilterRuleParameterDefinition.md) | The parameters of the filter rule and their name must match those in the filter rule. And all parameters must be defined in the event type payload. The name of parameters can&#39;t be duplicate. The following reserved keywords should not be used as a parameter name: &#x60;AttachmentList&#x60;, &#x60;RecipientList&#x60;, &#x60;RecipientType&#x60;, &#x60;Exceptions&#x60;, &#x60;OCP_OBJECT_TYPE&#x60;, &#x60;OCP_OBJECT_ID&#x60;, &#x60;OCP_TRIGGER_BY&#x60; | [optional] 

## Example

```python
from zuora_sdk.models.get_public_notification_definition_response_filter_rule import GetPublicNotificationDefinitionResponseFilterRule

# TODO update the JSON string below
json = "{}"
# create an instance of GetPublicNotificationDefinitionResponseFilterRule from a JSON string
get_public_notification_definition_response_filter_rule_instance = GetPublicNotificationDefinitionResponseFilterRule.from_json(json)
# print the JSON string representation of the object
print(GetPublicNotificationDefinitionResponseFilterRule.to_json())

# convert the object into a dict
get_public_notification_definition_response_filter_rule_dict = get_public_notification_definition_response_filter_rule_instance.to_dict()
# create an instance of GetPublicNotificationDefinitionResponseFilterRule from a dict
get_public_notification_definition_response_filter_rule_from_dict = GetPublicNotificationDefinitionResponseFilterRule.from_dict(get_public_notification_definition_response_filter_rule_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


