export interface Deployment {
  id_deployment: number;
  id_tracking_device: string;
  id_individual: number;
  id_nomenclature_deployment_type: number;
  id_nomenclature_deployment_location: number;
  marking_code: string;
  install_date: string;
  removal_date: string;
  comment: string;
  id_digitiser: number;
  meta_create_date: string;
  meta_update_date: string;
  deployment_type_name: string;
  deployment_location_name: string;
  name_digitiser: string;
  // Only present on the devices detail route (not on the individual detail route).
  individual_name?: string;
}

// This model is only used to POST data to the API (dto = data transfer object)
export interface CreateDeploymentDto {
  id_tracking_device: string;
  id_individual: number;
  id_nomenclature_deployment_type: number;
  id_nomenclature_deployment_location: number;
  marking_code: string;
  install_date: string;
  removal_date: string;
  comment: string;
  id_digitiser: number;
}

// This model is only used to PUT data to the API (dto = data transfer object)
export interface UpdateDeploymentDto extends CreateDeploymentDto {
  id_deployment: number;
}
