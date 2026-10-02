import { Injectable } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { Observable } from 'rxjs';
import { map, tap } from 'rxjs/operators'

import { ConfigService } from '@geonature/services/config.service';
import { ModuleService } from '@geonature/services/module.service';

import {
  Observation,
  APIObservationFiltersParams,
} from '../models/observations.models';
import { ItemCollection, APIPaginationParams, FeatureCollection } from '../models/common.models';
import { DEVICES_DEFAULT_SORT } from '../utils/constants.util';

@Injectable()
export class ObservationsService {
  private _OBJECT_API: string;

  constructor(
    private _http: HttpClient,
    private _config: ConfigService,
    private _moduleService: ModuleService
  ) {
    this._OBJECT_API = `${this._config.API_ENDPOINT}/synthese`;
  }

  getObservations(
    params: APIPaginationParams & APIObservationFiltersParams
  ): Observable<ItemCollection<Observation>> {
    let httpParams = new HttpParams();
    let items = Observable<ItemCollection<Observation>>;
    params.prop ??= DEVICES_DEFAULT_SORT.prop;
    params.dir ??= DEVICES_DEFAULT_SORT.dir;

    Object.keys(params).forEach((key) => {
      if (params[key] != null) {
        httpParams = httpParams.set(key, String(params[key]));
      }
    });

    return this._http.get<FeatureCollection<Observation>>(`${this._OBJECT_API}/for_web`, {
      params: httpParams,
    })
    .pipe(
      // Convert FeatureCollection to ItemCollection for the ListComponent
      map((featureCollection): ItemCollection<Observation> => ({
        items: Object.values(featureCollection.features.map(feature => feature.properties) ?? {}),
      }))
    )
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

    return this._http.get<FeatureCollection<Observation>>(`${this._OBJECT_API}/for_web`, {
      params: httpParams,
    });
  }
}
