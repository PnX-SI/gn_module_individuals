import { RankAndPage } from './common.models';

// This model is only used to read data
export const INDIVIDUAL_MODEL = {
    id_individual: 0,
    uuid_individual: '',
    individual_name: '',
    cd_nom: 0,
    id_nomenclature_sex: 0,
    active: false,
    comment: '',
    id_digitiser: 0,
    meta_create_date: '',
    meta_update_date: '',
    digitiser_name: '',
    nomenclature_sex_name: '',
    last_observation_date: '',
    last_observation_observers_name: '',
    nom_ver: '',
    device_type_name_deployments: '',
    marking_codes: ''
}

export type Individual = typeof INDIVIDUAL_MODEL;

export interface IndividualRankAndPage extends RankAndPage { 
    "id_individual": 36,
}

export interface APIIndividualFiltersParams {
  // This line help to use
  // $event: {
  //   key: keyof APIDevicesFiltersParams;
  //   value: string | number | undefined;
  // }
  [key: string]: string | number | undefined;

  cd_nom?: number;
  id_nomenclature_sex?: number;
  active?: string;
}

// This model is only used to POST data to the API (dto = data transfer object)
// export interface CreateDeviceDto {
//   id_nomenclature_device_type: number;
//   provider_name: string;
//   provider_device_id: string;
//   id_referer: number;
//   comment: string;
// }

// // This model is only used to PUT data to the API (dto = data transfer object)
// export interface UpdateDeviceDto extends CreateDeviceDto {
//   id_tracking_device: number;
// }
