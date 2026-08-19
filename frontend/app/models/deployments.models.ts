import { Cruved } from '@geonature/modules/imports/models/cruved.model';

// This model is only used to read data
export const DEPLOYMENT_MODEL = {
  id_deployment: 0,
  id_tracking_device: 0,
  id_individual: 0,
  id_nomenclature_deployment_type: 0,
  id_nomenclature_deployment_location: 0,
  marking_code: '',
  install_date: '',
  removal_date: '',
  comment: '',
  id_digitiser: 0,
  meta_create_date: '',
  meta_update_date: '',
  deployment_type_name: '',
  deployment_location_name: '',
  name_digitiser: '',
  individual_name: '',
  tracking_device_info: '',
};

export type Deployment  = typeof DEPLOYMENT_MODEL & { cruved: Cruved };

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
