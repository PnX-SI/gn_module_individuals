// This model is only used to read data and corresponding to the synthese fields
export const OBSERVATION_MODEL = {
  id_synthese: 0,
  id_dataset: 0,
  cd_nom: 0,
  date_min: '',
  entity_source_pk_value: '',
  nom_vern_or_lb_nom: '',
  observers: '',
  dataset_name: '',
  url_source: '',
};

export type Observation = typeof OBSERVATION_MODEL;

export interface APIObservationFiltersParams {
  // This line help to use
  // $event: {
  //   key: keyof APIObservationFiltersParams;
  //   value: string | number | undefined;
  // }
  [key: string]: string | number | undefined;

  cd_nom?: number;
  id_dataset?: number;
  //   date_min?: string;
  //   id_individual?: number;
}
