import { Injectable } from '@angular/core';
import { HttpHeaders, HttpClient, HttpParams } from '@angular/common/http';
import { Observable } from 'rxjs';

import { ConfigService } from '@geonature/services/config.service';
import { ModuleService } from '@geonature/services/module.service';
import { DataFormService } from '@geonature_common/form/data-form.service';

import {
  Device,
  CreateDeviceDto,
  UpdateDeviceDto,
  APIDeviceFiltersParams,
} from '../models/devices.models';
import { PaginatedItemCollection, APIPaginationParams } from '../models/common.models';
import { DEVICES_DEFAULT_SORT } from '../utils/constants.util';

@Injectable()
export class DevicesService {
  private _OBJECT_API: string;
  // Désactive l'interceptor global (MyCustomInterceptor) pour que le composant
  // puisse afficher un toast traduit à partir du code d'erreur backend.
  private _headers = new HttpHeaders({ 'not-to-handle': 'true' });

  constructor(
    private _http: HttpClient,
    private _config: ConfigService,
    private _moduleService: ModuleService,
    private _dataFormService: DataFormService
  ) {
    this._OBJECT_API = `${this._config.API_ENDPOINT}/${this._moduleService.currentModule.module_url}/devices`;
  }

  getDevices(
    params: APIPaginationParams & APIDeviceFiltersParams
  ): Observable<PaginatedItemCollection<Device>> {
    let httpParams = new HttpParams();
    params.prop ??= DEVICES_DEFAULT_SORT.prop;
    params.dir ??= DEVICES_DEFAULT_SORT.dir;

    Object.keys(params).forEach((key) => {
      if (params[key] != null) {
        httpParams = httpParams.set(key, String(params[key]));
      }
    });

    return this._http.get<PaginatedItemCollection<Device>>(`${this._OBJECT_API}`, {
      params: httpParams,
    });
  }

  getDevice(id_tracking_device: number): Observable<Device> {
    return this._http.get<Device>(`${this._OBJECT_API}/${id_tracking_device}`);
  }

  createOrUpdateDevice(
    device: any,
    formAction: string,
    params: Record<string, string> = {}
  ): Observable<Device> {
    params['format'] = 'json';
    // Map form to Dto
    let payload: CreateDeviceDto | UpdateDeviceDto = {
      id_nomenclature_device_type: device.id_nomenclature_device_type,
      provider_name: device.provider_name,
      provider_device_id: device.provider_device_id,
      id_referer: device.id_referer.id_role,
      comment: device.comment,
    };

    if (formAction === 'ADD') {
      return this._http.post<Device>(`${this._OBJECT_API}`, payload, {
        params: params,
        headers: this._headers,
      });
    } else {
      payload = {
        ...payload,
        id_tracking_device: device.id_tracking_device,
      };
      return this._http.put<Device>(`${this._OBJECT_API}/${device.id_tracking_device}`, payload, {
        params: params,
        headers: this._headers,
      });
    }
  }

  deleteDevice(id: number): Observable<Device> {
    return this._http.delete<Device>(`${this._OBJECT_API}/${id}`);
  }

  /**
   * Export the devices list in the given format, with the same filters and
   * sort currently applied to the list (no pagination: the backend exports
   * the whole filtered list, bounded by its own NB_MAX_EXPORT). Triggers a
   * browser download once the file is received.
   *
   * @param {string} format One of config.INDIVIDUALS.DEVICES.EXPORT_FORMAT
   * @param {APIDeviceFiltersParams} filters Currently applied filters
   * @param {{ prop?: string; dir?: string }} [sort] Currently applied sort
   * @memberof DevicesService
   */
  exportDevices(
    format: string,
    filters: APIDeviceFiltersParams,
    sort?: { prop?: string; dir?: string }
  ): void {
    let httpParams = new HttpParams();
    const params: Record<string, string | number | undefined> = { ...filters, ...sort };
    Object.keys(params).forEach((key) => {
      if (params[key] != null && params[key] !== '') {
        httpParams = httpParams.set(key, String(params[key]));
      }
    });

    const source = this._http.post(`${this._OBJECT_API}/export/${format}`, null, {
      params: httpParams,
      observe: 'events',
      responseType: 'blob',
      reportProgress: true,
    });

    this._dataFormService.subscribeAndDownload(source, 'devices', format);
  }
}
