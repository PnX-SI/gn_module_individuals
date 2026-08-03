import { Individual } from './individuals.models';

export interface GeoJSON {}

export interface IndividualCaptured {
  individual: Individual;
  additional_data: any;
}

export interface Capture {
  id_capture: number;
  id_nomenclature_protocole: number;
  comment: string;
  date: Date;
  geom: any;
  id_digitiser: number;
  meta_create_date: Date;
  meta_update_date: Date;
  observers: any[];
  individuals: IndividualCaptured[];
}
