import { Injectable } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { Observable } from 'rxjs';
import { ConfigService } from '@geonature/services/config.service';
import { ModuleService } from '@geonature/services/module.service';

import { Device, DevicesAPIParams } from '../models/devices.models';
import { PaginatedItemCollection } from '../models/common.models';
import { DataTableConfig } from '../module.config';

@Injectable()
export class DevicesService {
  private MODULE_API: string;

  constructor(
    private _http: HttpClient,
    private _config: ConfigService,
    private _moduleService: ModuleService
  ) {
    this.MODULE_API = `${this._config.API_ENDPOINT}/${this._moduleService.currentModule.module_url}`;
  }

  getDevices(params: DevicesAPIParams = {}): Observable<PaginatedItemCollection<Device>> {
    let httpParams = new HttpParams();
   
    params.page ??= 1
    params.per_page ??= DataTableConfig.PER_PAGE_OPTION

    Object.keys(params).forEach(key => {
      const value = params[key as keyof DevicesAPIParams];
      if (value != null) { 
        httpParams = httpParams.set(key, String(value));
      }
    });

    // console.log('GET request on :', `${this.MODULE_API}/devices`, 'with params :', params);
    return this._http.get<PaginatedItemCollection<Device>>(
      `${this.MODULE_API}/devices`, { params: httpParams }
    );
  }

  // getIndividual(id_individual: number): Observable<Device> {
  //   return this._http.get<Device>(
  //     `${this._config.API_ENDPOINT}/${this._moduleService.currentModule.module_url}/indiv/${id_individual}`
  //   );
  // }

  // createIndividual(individual: Omit<Device, 'id_tracking_device'>): Observable<Device> {
  //   return this._http.post<Device>(
  //     `${this._config.API_ENDPOINT}/${this._moduleService.currentModule.module_url}/indiv`,
  //     individual
  //   );
  // }
}
