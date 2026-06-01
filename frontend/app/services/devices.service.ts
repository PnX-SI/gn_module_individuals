import { Injectable } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { Observable, of } from 'rxjs';
import { ConfigService } from '@geonature/services/config.service';
import { ModuleService } from '@geonature/services/module.service';

import { Device, CreateDeviceDto } from '../models/devices.models';
import { PaginatedItemCollection, PaginationAPIParams } from '../models/common.models';
import { DATA_TABLE_CONFIG } from '..//utils/constants.util';

@Injectable()
export class DevicesService {
  private OBJECT_API: string;

  constructor(
    private _http: HttpClient,
    private _config: ConfigService,
    private _moduleService: ModuleService
  ) {
    this.OBJECT_API = `${this._config.API_ENDPOINT}/${this._moduleService.currentModule.module_url}/devices`;
  }

  getDevices(params: PaginationAPIParams = {}): Observable<PaginatedItemCollection<Device>> {
    let httpParams = new HttpParams();
    params.page ??= 1
    params.per_page ??= DATA_TABLE_CONFIG.PER_PAGE_OPTION  

    Object.keys(params).forEach(key => {
      const value = params[key as keyof PaginationAPIParams];
      if (value != null) { 
        httpParams = httpParams.set(key, String(value));
      }
    });

    return this._http.get<PaginatedItemCollection<Device>>(
      `${this.OBJECT_API}`, { params: httpParams }
    );
  }

  getDevice(id_tracking_device: number): Observable<Device> {
    return this._http.get<Device>(
      `${this.OBJECT_API}/${id_tracking_device}`
    );
  }

  createDevice(device: any, params: Record<string, string> = {}): Observable<Device> {
    params['format'] = 'json';

    // Map form to Dto
    const payload: CreateDeviceDto = {
      id_nomenclature_device_type: device.id_nomenclature_device_type.id_nomenclature,
      provider_name: device.provider_name,
      provider_device_id: device.provider_device_id,
      id_referer: device.id_referer.id_role,
      comment: device.comment,
    };

    console.log(
      'POST payload JSON:',
      JSON.stringify(payload, null, 2)
    );

    return of(device as Device);
    // return this._http.post<Device>(
    //   `${this.OBJECT_API}`,
    //   device,
    //   {params: params}
    // );
  }
}
