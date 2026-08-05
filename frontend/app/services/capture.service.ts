import { Injectable } from '@angular/core';
import { HttpHeaders, HttpClient, HttpParams } from '@angular/common/http';
import { Observable, of } from 'rxjs';

import { ConfigService } from '@geonature/services/config.service';
import { ModuleService } from '@geonature/services/module.service';
import { Capture, APICaptureFiltersParams, CaptureRankAndPage } from '../models/capture.model';
import { PaginatedItemCollection, APIPaginationParams } from '../models/common.models';
import { CAPTURES_DEFAULT_SORT } from '../utils/constants.util';

// REMOVE any
@Injectable()
export class CaptureService {
  private API_ENDPOINT: string;

  constructor(
    private _http: HttpClient,
    private _config: ConfigService
  ) {
    this.API_ENDPOINT = `${this._config.API_ENDPOINT}/individuals/captures`;
  }

  getCapture(id_capture: number): Observable<Capture | any> {
    return this._http.get<Capture>(`${this.API_ENDPOINT}/${id_capture}`);
  }

  getCaptures(params: APIPaginationParams): Observable<PaginatedItemCollection<Capture> | any> {
    let httpParams = new HttpParams();
    params.prop ??= CAPTURES_DEFAULT_SORT.prop;
    params.dir ??= CAPTURES_DEFAULT_SORT.dir;
    console.log('Parameters sent to API (Captures)', params);

    Object.keys(params).forEach(
      (key) => {
        if (params[key] != null) {
          httpParams = httpParams.set(key, String(params[key]));
        }
      },
      {
        params: httpParams,
      }
    );

    return this._http.get<Capture>(`${this.API_ENDPOINT}`);
  }

  getCapturesforMap(
    params: APIPaginationParams | any
  ): Observable<PaginatedItemCollection<Capture> | any> {
    return this._http.get<Capture>(`${this.API_ENDPOINT}/geometry`);
  }

  createOrUpdateDevice(
    captureData: any,
    formAction: 'CREATE' | 'UPDATE',
    id: number | null = null
  ): Observable<Capture> {
    if (formAction === 'UPDATE') {
      captureData = {
        ...captureData,
        id_capture: id,
      };
      return this._http.put<Capture>(`${this.API_ENDPOINT}/${id}`, captureData);
    }
    return this._http.post<Capture>(`${this.API_ENDPOINT}`, captureData);
  }

  deleteCapture(id: number): Observable<Capture> {
    return this._http.delete<Capture>(`${this.API_ENDPOINT}/${id}`);
  }
}
