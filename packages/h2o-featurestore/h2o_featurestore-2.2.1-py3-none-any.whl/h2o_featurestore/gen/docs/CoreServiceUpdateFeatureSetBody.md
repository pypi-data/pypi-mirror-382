# CoreServiceUpdateFeatureSetBody


## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**feature_set_version** | **str** |  | [optional] 
**tags** | **[str]** |  | [optional] 
**data_source_domains** | **[str]** |  | [optional] 
**description** | **str** |  | [optional] 
**type** | [**V1FeatureSetType**](V1FeatureSetType.md) |  | [optional] 
**deprecated** | **bool** |  | [optional] 
**process_interval** | **int** |  | [optional] 
**process_interval_unit** | [**V1ProcessIntervalUnit**](V1ProcessIntervalUnit.md) |  | [optional] 
**time_to_live_offline_interval** | **int** |  | [optional] 
**time_to_live_offline_interval_unit** | [**V1OfflineTimeToLiveInterval**](V1OfflineTimeToLiveInterval.md) |  | [optional] 
**time_to_live_online_interval** | **int** |  | [optional] 
**time_to_live_online_interval_unit** | [**V1OnlineTimeToLiveInterval**](V1OnlineTimeToLiveInterval.md) |  | [optional] 
**legal_approved** | **bool** |  | [optional] 
**legal_approved_notes** | **str** |  | [optional] 
**state** | **str** |  | [optional] 
**flow** | **str** |  | [optional] 
**application_name** | **str** |  | [optional] 
**application_id** | **str** |  | [optional] 
**custom_data** | **bool, date, datetime, dict, float, int, list, str, none_type** |  | [optional] 
**online_namespace** | **str** |  | [optional] 
**online_topic** | **str** |  | [optional] 
**online_connection_type** | **str** |  | [optional] 
**fields_to_update** | [**[V1UpdatableFeatureSetField]**](V1UpdatableFeatureSetField.md) |  | [optional] 
**any string name** | **bool, date, datetime, dict, float, int, list, str, none_type** | any string name can be used but the value must be the correct type | [optional]

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


