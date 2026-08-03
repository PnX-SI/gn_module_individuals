import { Individual } from './individuals.models';
import { RankAndPage } from './common.models';

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

// Used as availableColumnsParams for the captures datatable
export const CAPTURE_MODEL = {
  id_capture: 0,
  id_nomenclature_protocole: 0,
  date: '',
  comment: '',
  observers: [],
  individuals: [],
  id_digitiser: 0,
  meta_create_date: '',
  meta_update_date: '',
};

export interface APICaptureFiltersParams {
  [key: string]: string | number | undefined;

  id_nomenclature_protocole?: number;
  date?: string;
  id_role?: number;
}

export interface CaptureRankAndPage extends RankAndPage {
  id_capture: number;
}
