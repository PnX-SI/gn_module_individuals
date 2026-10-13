import { Injectable } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { Observable } from 'rxjs';

import { ConfigService } from '@geonature/services/config.service';
import { ModuleService } from '@geonature/services/module.service';
import { DataFormService } from '@geonature_common/form/data-form.service';

import {
  Observation,
  ObservationRankAndPage,
  APIObservationFiltersParams,
} from '../models/observations.models';
import {
  ItemCollection,
  APIPaginationParams,
  APISortParams,
  FeatureCollection,
} from '../models/common.models';
import { OBSERVATIONS_DEFAULT_SORT } from '../utils/constants.util';

@Injectable()
export class ObservationsService {
  private _OBJECT_API: string;

  constructor(
    private _http: HttpClient,
    private _config: ConfigService,
    private _moduleService: ModuleService,
    private _dataFormService: DataFormService
  ) {
    this._OBJECT_API = `${this._config.API_ENDPOINT}/${this._moduleService.currentModule.module_url}/observations`;
  }

  getObservations(
    params: APIPaginationParams & APIObservationFiltersParams
  ): Observable<ItemCollection<Observation>> {
    let httpParams = new HttpParams();
    params.prop ??= OBSERVATIONS_DEFAULT_SORT.prop;
    params.dir ??= OBSERVATIONS_DEFAULT_SORT.dir;

    Object.keys(params).forEach((key) => {
      if (params[key] != null) {
        httpParams = httpParams.set(key, String(params[key]));
      }
    });

    return this._http.get<ItemCollection<Observation>>(`${this._OBJECT_API}`, {
      params: httpParams,
    });
  }

  getObservationsForMap(
    params: APIObservationFiltersParams
  ): Observable<FeatureCollection<Observation>> {
    let httpParams = new HttpParams();

    Object.keys(params).forEach((key) => {
      if (params[key] != null) {
        httpParams = httpParams.set(key, String(params[key]));
      }
    });

    return this._http.get<FeatureCollection<Observation>>(`${this._OBJECT_API}/geometry`, {
      params: httpParams,
    });
  }

  /**
   * Return un observable with the rank and page in the individuals list of the individual given id
   * with current filters and sort applied.
   *
   * @param {number} id
   * @param {(APIPaginationParams & APIObservationFiltersParams)} params : pagination, sort and filter params
   * @return {*}  {Observable<ObservationRankAndPage>}
   * @memberof ObservationsService
   */
  getObservationRankAndPage(
    id: number,
    params: APIPaginationParams & APIObservationFiltersParams
  ): Observable<ObservationRankAndPage> {
    let httpParams = new HttpParams();

    Object.keys(params).forEach((key) => {
      if (params[key] != null) {
        httpParams = httpParams.set(key, String(params[key]));
      }
    });

    return this._http.get<ObservationRankAndPage>(`${this._OBJECT_API}/${id}/page`, {
      params: httpParams,
    });
  }

  /**
   * Export the individuals list in the given format, with the same filters
   * and sort currently applied to the list/map (no pagination: the backend
   * exports the whole filtered and sorted list, bounded by its own NB_MAX_EXPORT).
   * Triggers a browser download once the file is received.
   *
   * @param {string} format One of config.INDIVIDUALS.OBSERVATIONS.EXPORT_FORMAT
   * @param {APIObservationFiltersParams & APISortParams} params Currently applied filters and sorts
   * @memberof IndividualsService
   */
  exportObservations(format: string, params: APIObservationFiltersParams & APISortParams): void {
    let httpParams = new HttpParams();
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

    this._dataFormService.subscribeAndDownload(source, 'observations', format);
  }
}
