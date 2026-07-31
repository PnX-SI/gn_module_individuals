import { Cruved } from '@geonature/modules/imports/models/cruved.model';

// This model is only used to read data
export const DEVICE_MODEL = {
  id_tracking_device: 0,
  id_nomenclature_device_type: 0,
  provider_name: '',
  provider_device_id: '',
  id_referer: 0,
  comment: '',
  id_digitiser: 0,
  meta_create_date: '',
  meta_update_date: '',
  nomenclature_device_type_name: '',
  last_individual_equipped_name: '',
  referer_name: '',
  digitiser_name: '',
  deployments: '',
};

export type Device = typeof DEVICE_MODEL & { cruved: Cruved };

export interface APIDeviceFiltersParams {
  // This line help to use
  // $event: {
  //   key: keyof APIDeviceFiltersParams;
  //   value: string | number | undefined;
  // }
  [key: string]: string | number | undefined;

  cd_nom?: number;
  id_nomenclature_device_type?: number;
  provider_name?: string;
  id_referer?: number;
}

// This model is only used to POST data to the API (dto = data transfer object)
export interface CreateDeviceDto {
  id_nomenclature_device_type: number;
  provider_name: string;
  provider_device_id: string;
  id_referer: number;
  comment: string;
}

// This model is only used to PUT data to the API (dto = data transfer object)
export interface UpdateDeviceDto extends CreateDeviceDto {
  id_tracking_device: number;
}
