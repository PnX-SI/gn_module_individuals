import { Injectable } from '@angular/core';
import { HttpHeaders, HttpClient, HttpParams } from '@angular/common/http';
import { Observable, of } from 'rxjs';

import { ConfigService } from '@geonature/services/config.service';
import { ModuleService } from '@geonature/services/module.service';

import {
  Individual,
  APIIndividualFiltersParams,
  IndividualRankAndPage,
  CreateIndividualDto,
  UpdateIndividualDto,
} from '../models/individuals.models';
import {
  PaginatedItemCollection,
  APIPaginationParams,
  FeatureCollection,
} from '../models/common.models';
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
  getIndividualRankAndPage(
    id: number,
    params: APIPaginationParams & APIIndividualFiltersParams
  ): Observable<IndividualRankAndPage> {
    let httpParams = new HttpParams();

    Object.keys(params).forEach((key) => {
      if (params[key] != null) {
        httpParams = httpParams.set(key, String(params[key]));
      }
    });
    console.log(
      'Parameters sent to API (Individual Rank and Page)',
      params,
      'for individual id',
      id
    );
    return this._http.get<IndividualRankAndPage>(`${this._OBJECT_API}/${id}/page`, {
      params: httpParams,
    });
  }

  getIndividual(id_individual: number): Observable<Individual> {
    return this._http.get<Individual>(`${this._OBJECT_API}/${id_individual}`);
  }

  createOrUpdateIndividual(
    individual: any,
    formAction: string,
    id: number | null = null,
    params: Record<string, string> = {}
  ): Observable<Individual> {
    params['format'] = 'json';
    // Map form to Dto
    let payload: CreateIndividualDto | UpdateIndividualDto = {
      individual_name: individual.individual_name,
      cd_nom: individual.cd_nom.cd_nom,
      id_nomenclature_sex: individual.id_nomenclature_sex,
      active: individual.active,
      comment: individual.comment,
    };

    if (formAction === 'EDIT') {
      payload = {
        ...payload,
        id_individual: individual.id,
      };
    }
    console.log('Parameters sent to API params:', params, 'payload', payload);

    if (formAction === 'ADD') {
      return this._http.post<Individual>(`${this._OBJECT_API}`, payload, {
        params: params,
        headers: this._headers,
      });
    } else {
      return this._http.put<Individual>(`${this._OBJECT_API}/${id}`, payload, {
        params: params,
        headers: this._headers,
      });
    }
    // return of();
  }

  deleteIndividual(id: number): Observable<Individual> {
    return this._http.delete<Individual>(`${this._OBJECT_API}/${id}`);
  }
}
