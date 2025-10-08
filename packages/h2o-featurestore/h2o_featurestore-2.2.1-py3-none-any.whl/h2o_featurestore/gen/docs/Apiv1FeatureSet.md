# Apiv1FeatureSet


## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**project** | **str** |  | [optional] 
**feature_set_name** | **str** |  | [optional] 
**version** | **str** |  | [optional] 
**version_change** | **str** |  | [optional] 
**time_travel_column** | **str** |  | [optional] 
**time_travel_column_format** | **str** |  | [optional] 
**feature_set_type** | [**V1FeatureSetType**](V1FeatureSetType.md) |  | [optional] 
**description** | **str** |  | [optional] 
**author** | [**V1UserBasicInfo**](V1UserBasicInfo.md) |  | [optional] 
**created_date_time** | **datetime** |  | [optional] 
**last_update_date_time** | **datetime** |  | [optional] 
**application_name** | **str** |  | [optional] 
**deprecated** | **bool** |  | [optional] 
**deprecated_date** | **datetime** |  | [optional] 
**data_source_domains** | **[str]** |  | [optional] 
**tags** | **[str]** |  | [optional] 
**process_interval** | **int** |  | [optional] 
**process_interval_unit** | [**V1ProcessIntervalUnit**](V1ProcessIntervalUnit.md) |  | [optional] 
**flow** | **str** |  | [optional] 
**time_to_live** | [**V1TimeToLive**](V1TimeToLive.md) |  | [optional] 
**features** | [**[V1Feature]**](V1Feature.md) |  | [optional] 
**statistics** | [**FeatureSetStatistics**](FeatureSetStatistics.md) |  | [optional] 
**special_data** | [**V1FeatureSetSpecialData**](V1FeatureSetSpecialData.md) |  | [optional] 
**primary_key** | **[str]** |  | [optional] 
**id** | **str** |  | [optional] 
**time_travel_scope** | [**V1Scope**](V1Scope.md) |  | [optional] 
**application_id** | **str** |  | [optional] 
**feature_set_state** | **str** |  | [optional] 
**online** | [**V1FeatureSetOnline**](V1FeatureSetOnline.md) |  | [optional] 
**project_id** | **str** |  | [optional] 
**partition_by** | **[str]** |  | [optional] 
**custom_data** | **bool, date, datetime, dict, float, int, list, str, none_type** |  | [optional] 
**online_materialization_scope** | [**V1Scope**](V1Scope.md) |  | [optional] 
**derived_from** | [**V1DerivedInformation**](V1DerivedInformation.md) |  | [optional] 
**feature_classifiers** | **[str]** |  | [optional] 
**last_updated_by** | [**V1UserBasicInfo**](V1UserBasicInfo.md) |  | [optional] 
**storage_optimization** | [**V1StorageOptimization**](V1StorageOptimization.md) |  | [optional] 
**any string name** | **bool, date, datetime, dict, float, int, list, str, none_type** | any string name can be used but the value must be the correct type | [optional]

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


