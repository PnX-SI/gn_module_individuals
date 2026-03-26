// Used to declare avilable columns and their name in the table header
export interface Column<T> {
  prop: keyof T;
  name: string;
}

export interface Device {
  id_tracking_device: number
  id_nomenclature_device_type: number,
  provider_name: string,
  provider_device_id: string,
  id_referer: number,
  comment: string,
  id_digitiser : number,
  meta_create_date : string,
  meta_update_date : string,
  nomenclature_device_type_name: string,
  referer_name: string,
  digitiser_name: string,
}