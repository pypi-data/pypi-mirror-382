# V1RegisterFeatureSetRequest


## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**feature_set_name** | **str** |  | [optional] 
**project** | [**V1Project**](V1Project.md) |  | [optional] 
**time_travel_column** | **str** |  | [optional] 
**time_travel_column_format** | **str** |  | [optional] 
**primary_key** | **[str]** |  | [optional] 
**schema** | [**[V1FeatureSchema]**](V1FeatureSchema.md) |  | [optional] 
**description** | **str** |  | [optional] 
**partition_by** | **[str]** |  | [optional] 
**time_travel_column_as_partition** | **bool** |  | [optional] 
**feature_set_type** | [**V1FeatureSetType**](V1FeatureSetType.md) |  | [optional] 
**feature_set_state** | **str** |  | [optional] 
**application_name** | **str** |  | [optional] 
**application_id** | **str** |  | [optional] 
**online** | [**V1FeatureSetOnline**](V1FeatureSetOnline.md) |  | [optional] 
**data_source_domains** | **[str]** |  | [optional] 
**tags** | **[str]** |  | [optional] 
**process_interval** | **int** |  | [optional] 
**process_interval_unit** | [**V1ProcessIntervalUnit**](V1ProcessIntervalUnit.md) |  | [optional] 
**flow** | **str** |  | [optional] 
**special_data** | [**V1FeatureSetSpecialData**](V1FeatureSetSpecialData.md) |  | [optional] 
**custom_data** | **bool, date, datetime, dict, float, int, list, str, none_type** |  | [optional] 
**time_to_live** | [**V1TimeToLive**](V1TimeToLive.md) |  | [optional] 
**derived_from** | [**V1DerivedInformation**](V1DerivedInformation.md) |  | [optional] 
**any string name** | **bool, date, datetime, dict, float, int, list, str, none_type** | any string name can be used but the value must be the correct type | [optional]

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


