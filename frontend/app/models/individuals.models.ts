import { Cruved } from '@geonature/modules/imports/models/cruved.model';

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
  taxref_nom_vern: '',
  taxref_lb_nom: '',
  taxref_cd_nom: '',
  deployed_markings: '',
  deployed_devices: '',
  additional_data: {},
};

export type Individual = typeof INDIVIDUAL_MODEL & { cruved: Cruved };

export interface IndividualRankAndPage extends RankAndPage {
  id_individual: 36;
}

export interface APIIndividualFiltersParams {
  // This line help to use
  // $event: {
  //   key: keyof APIIndividualsFiltersParams;
  //   value: string | number | undefined;
  // }
  [key: string]: string | number | undefined;

  individual_name?: string;
  cd_nom?: number;
  id_nomenclature_sex?: number;
  active?: string;
}

// This model is only used to POST data to the API (dto = data transfer object)
export interface CreateIndividualDto {
  individual_name: string;
  cd_nom: number;
  id_nomenclature_sex: number;
  active: false;
  comment: string;
  deployments: [];
  additional_data: {};
}

// This model is only used to PUT data to the API (dto = data transfer object)
export interface UpdateIndividualDto extends CreateIndividualDto {
  id_individual: number;
}
