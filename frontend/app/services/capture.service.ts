import { Injectable } from '@angular/core';
import { HttpHeaders, HttpClient, HttpParams } from '@angular/common/http';
import { Observable, of } from 'rxjs';

import { ConfigService } from '@geonature/services/config.service';
import { ModuleService } from '@geonature/services/module.service';
import { Capture, APICaptureFiltersParams, CaptureRankAndPage } from '../models/capture.model';
import { PaginatedItemCollection, APIPaginationParams } from '../models/common.models';

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
    return of({});
  }

  getCaptures(params: APIPaginationParams): Observable<PaginatedItemCollection<Capture> | any> {
    return of({});
  }

  getCapturesforMap(
    params: APIPaginationParams | any
  ): Observable<PaginatedItemCollection<Capture> | any> {
    return of({});
  }

  /**
   * Return an observable with the rank and page in the captures list of the given capture id
   * with current filters and sort applied.
   */
  getCaptureRankAndPage(
    id: number,
    params: APIPaginationParams & APICaptureFiltersParams
  ): Observable<CaptureRankAndPage> {
    return of({} as CaptureRankAndPage);
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
