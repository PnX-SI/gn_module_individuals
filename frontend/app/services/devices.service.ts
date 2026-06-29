import { Injectable } from '@angular/core';
import { HttpHeaders, HttpClient, HttpParams } from '@angular/common/http';
import { Observable, of } from 'rxjs';

import { ConfigService } from '@geonature/services/config.service';
import { ModuleService } from '@geonature/services/module.service';

import { Device, CreateDeviceDto, UpdateDeviceDto } from '../models/devices.models';
import { PaginatedItemCollection, APIPaginationParams } from '../models/common.models';
import { DATA_TABLE_CONFIG, DEVICES_DEFAULT_SORT } from '../utils/constants.util';

@Injectable()
export class DevicesService {
  private _OBJECT_API: string;
  // Désactive l'interceptor global (MyCustomInterceptor) pour que le composant
  // puisse afficher un toast traduit à partir du code d'erreur backend.
  private _headers = new HttpHeaders({ 'not-to-handle': 'true' });

  constructor(
    private _http: HttpClient,
    private _config: ConfigService,
    private _moduleService: ModuleService
  ) {
    this._OBJECT_API = `${this._config.API_ENDPOINT}/${this._moduleService.currentModule.module_url}/devices`;
  }

  getDevices(
    params: APIPaginationParams = { page: 1, per_page: DATA_TABLE_CONFIG.PER_PAGE_OPTION }
  ): Observable<PaginatedItemCollection<Device>> {
    let httpParams = new HttpParams();
    console.log('Parameters sent to API', params);
    params.prop ??= DEVICES_DEFAULT_SORT.prop;
    params.dir ??= DEVICES_DEFAULT_SORT.dir;

    Object.keys(params).forEach((key) => {
      const value = params[key as keyof APIPaginationParams];
      if (value != null) {
        httpParams = httpParams.set(key, String(value));
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
    id: number | null = null,
    params: Record<string, string> = {}
  ): Observable<Device> {
    params['format'] = 'json';
    console.log(device);
    // Map form to Dto
    let payload: CreateDeviceDto | UpdateDeviceDto = {
      id_nomenclature_device_type: device.id_nomenclature_device_type,
      provider_name: device.provider_name,
      provider_device_id: device.provider_device_id,
      id_referer: device.id_referer.id_role,
      comment: device.comment,
    };

    if (formAction === 'EDIT') {
      payload = {
        ...payload,
        id_tracking_device: device.id,
      };
    }
    if (formAction === 'ADD') {
      return this._http.post<Device>(`${this._OBJECT_API}`, payload, {
        params: params,
        headers: this._headers,
      });
    } else {
      return this._http.put<Device>(`${this._OBJECT_API}/${id}`, payload, {
        params: params,
        headers: this._headers,
      });
    }
  }

  deleteDevice(id: number): Observable<Device> {
    return this._http.delete<Device>(`${this._OBJECT_API}/${id}`);
  }
}
