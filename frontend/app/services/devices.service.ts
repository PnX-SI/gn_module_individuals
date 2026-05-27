import { Injectable } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { Observable } from 'rxjs';
import { ConfigService } from '@geonature/services/config.service';
import { ModuleService } from '@geonature/services/module.service';

import { Device, DevicesAPIParams } from '../models/devices.models';
import { PaginatedItemCollection } from '../models/common.models';
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

  getDevices(params: DevicesAPIParams = {}): Observable<PaginatedItemCollection<Device>> {
    let httpParams = new HttpParams();
    params.page ??= 1
    params.limit ??= DATA_TABLE_CONFIG.PER_PAGE_OPTION  

    Object.keys(params).forEach(key => {
      const value = params[key as keyof DevicesAPIParams];
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

  createDevice(device: Omit<Device, 'id_tracking_device'>): Observable<Device> {
    return this._http.post<Device>(
      `${this.OBJECT_API}`,
      device
    );
  }
}
