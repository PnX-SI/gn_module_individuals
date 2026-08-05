import { Individual } from './individuals.models';

export interface GeoJSON {}

// Mirrors IndividualsCaptureObservationsSchema (backend/gn_module_individuals/schemas/captures.py)
export interface IndividualCaptured {
  id_capture: number;
  id_individual: number;
  individual: Individual;
  additional_data: any;
}

// DTO for POST /observations
export interface CreateCaptureObservationDto {
  id_capture: number;
  id_individual: number;
  additional_data?: any;
}

// DTO for PATCH /observations/<id_capture>/<id_individual>
export interface UpdateCaptureObservationDto {
  additional_data?: any;
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

