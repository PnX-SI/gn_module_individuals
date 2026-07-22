import { Injectable } from '@angular/core';
import { HttpHeaders, HttpClient, HttpParams } from '@angular/common/http';
import { Observable, of } from 'rxjs';

import { ConfigService } from '@geonature/services/config.service';
import { ModuleService } from '@geonature/services/module.service';

import { Individual, APIIndividualFiltersParams, IndividualRankAndPage } from '../models/individuals.models';
import { PaginatedItemCollection, APIPaginationParams, FeatureCollection } from '../models/common.models';
import { DATATABLE_CONFIG, INDIVIDUALS_DEFAULT_SORT } from '../utils/constants.util';

@Injectable()
export class IndividualsService {
  private _OBJECT_API: string;
  // Désactive l'interceptor global (MyCustomInterceptor) pour que le composant
  // puisse afficher un toast traduit à partir du code d'erreur backend.
  private _headers = new HttpHeaders({ 'not-to-handle': 'true' });

  constructor(
    private _http: HttpClient,
    private _config: ConfigService,
    private _moduleService: ModuleService
  ) {
    this._OBJECT_API = `${this._config.API_ENDPOINT}/${this._moduleService.currentModule.module_url}/individuals`;
  }

  getIndividuals(
    params: APIPaginationParams & APIIndividualFiltersParams
  ): Observable<PaginatedItemCollection<Individual>> {
    let httpParams = new HttpParams();
    params.prop ??= INDIVIDUALS_DEFAULT_SORT.prop;
    params.dir ??= INDIVIDUALS_DEFAULT_SORT.dir;

    console.log('Parameters sent to API (Individuals)', params);

    Object.keys(params).forEach((key) => {
      if (params[key] != null) {
        httpParams = httpParams.set(key, String(params[key]));
      }
    });

    return this._http.get<PaginatedItemCollection<Individual>>(`${this._OBJECT_API}`, {
      params: httpParams,
    });
  }

  getIndividualsForMap(
    params: APIIndividualFiltersParams
  ): Observable<FeatureCollection<Individual>> {
    let httpParams = new HttpParams();
    console.log('Parameters sent to API (Individuals Geometry)', params);

    Object.keys(params).forEach((key) => {
      if (params[key] != null) {
        httpParams = httpParams.set(key, String(params[key]));
      }
    });

    return this._http.get<FeatureCollection<Individual>>(`${this._OBJECT_API}/geometry`, {
      params: httpParams,
    });
  }
  
  /**
   * Return un observable with the rank and page in the individuals list of the individual given id
   * with current filters and sort applied.
   *
   * @param {number} id
   * @param {(APIPaginationParams & APIIndividualFiltersParams)} params
   * @return {*}  {Observable<IndividualRankAndPage>}
   * @memberof IndividualsService
   */
  getIndividualRankAndPage(id: number, params: APIPaginationParams & APIIndividualFiltersParams): Observable<IndividualRankAndPage> {
    let httpParams = new HttpParams();

    Object.keys(params).forEach((key) => {
      if (params[key] != null) {
        httpParams = httpParams.set(key, String(params[key]));
      }
    });
    console.log('Parameters sent to API (Individual Rank and Page)', params, 'for individual id', id);
    return this._http.get<IndividualRankAndPage>(`${this._OBJECT_API}/${id}/page`, {
      params: httpParams,
    });
  }

//   getDevice(id_tracking_device: number): Observable<Device> {
//     return this._http.get<Device>(`${this._OBJECT_API}/${id_tracking_device}`);
//   }

//   createOrUpdateDevice(
//     device: any,
//     formAction: string,
//     id: number | null = null,
//     params: Record<string, string> = {}
//   ): Observable<Device> {
//     params['format'] = 'json';
//     // Map form to Dto
//     let payload: CreateDeviceDto | UpdateDeviceDto = {
//       id_nomenclature_device_type: device.id_nomenclature_device_type,
//       provider_name: device.provider_name,
//       provider_device_id: device.provider_device_id,
//       id_referer: device.id_referer.id_role,
//       comment: device.comment,
//     };

//     if (formAction === 'EDIT') {
//       payload = {
//         ...payload,
//         id_tracking_device: device.id,
//       };
//     }
//     if (formAction === 'ADD') {
//       return this._http.post<Device>(`${this._OBJECT_API}`, payload, {
//         params: params,
//         headers: this._headers,
//       });
//     } else {
//       return this._http.put<Device>(`${this._OBJECT_API}/${id}`, payload, {
//         params: params,
//         headers: this._headers,
//       });
//     }
//   }

//   deleteDevice(id: number): Observable<Device> {
//     return this._http.delete<Device>(`${this._OBJECT_API}/${id}`);
//   }
}
