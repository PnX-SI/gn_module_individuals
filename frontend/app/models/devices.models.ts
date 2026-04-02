export interface Device {
  id_tracking_device: number
  id_nomenclature_device_type: number,
  provider_name: string,
  provider_device_id: string,
  id_referer: number,
  comment: string,
  nomenclature_device_type_name: string,
  referer_name: string,
  last_individual_equipped_name: string,
  id_digitiser : number,
  digitiser_name: string,
  meta_create_date : string,
  meta_update_date : string,
}

export const DEVICE_COLUMNS: Record<keyof Device, true> = {
  id_tracking_device: true,
  id_nomenclature_device_type: true,
  provider_name: true,
  provider_device_id: true,
  id_referer: true,
  comment: true,
  nomenclature_device_type_name: true,
  referer_name: true,
  last_individual_equipped_name: true,
  id_digitiser: true,
  digitiser_name: true,
  meta_create_date: true,
  meta_update_date: true,
};

export interface DevicesAPIParams {
  page?: number,
  per_page?: number,
  // id_tracking_device?: number,
  // id_nomenclature_device_type?: number,
  // provider_name?: string,
  // provider_device_id?: string,
  // id_referer?: number,
  // comment?: string,
  // id_digitiser?: number,
}