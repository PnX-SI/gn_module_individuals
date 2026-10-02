import { Injectable } from '@angular/core';
import { HttpHeaders, HttpClient, HttpParams } from '@angular/common/http';
import { Observable } from 'rxjs';

import { ConfigService } from '@geonature/services/config.service';
import { ModuleService } from '@geonature/services/module.service';
import { DataFormService } from '@geonature_common/form/data-form.service';

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
    private _moduleService: ModuleService,
    private _dataFormService: DataFormService
  ) {
    this._OBJECT_API = `${this._config.API_ENDPOINT}/${this._moduleService.currentModule.module_url}/individuals`;
  }

  getIndividuals(
    params: APIPaginationParams & APIIndividualFiltersParams
  ): Observable<PaginatedItemCollection<Individual>> {
    let httpParams = new HttpParams();
    params.prop ??= INDIVIDUALS_DEFAULT_SORT.prop;
    params.dir ??= INDIVIDUALS_DEFAULT_SORT.dir;

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
      additional_data: individual.additional_data,
      deployments: individual.deployments,
      modules: individual.modules.map((id: number) => ({"id_module": id}))
    }

    if (formAction === 'ADD') {
      return this._http.post<Individual>(`${this._OBJECT_API}`, payload, {
        params: params,
        headers: this._headers,
      });
    } else {
      payload = {
        ...payload,
        id_individual: individual.id_individual,
      };

      return this._http.put<Individual>(`${this._OBJECT_API}/${individual.id_individual}`, payload, {
        params: params,
        headers: this._headers,
      });
    }
  }

  deleteIndividual(id: number): Observable<Individual> {
    return this._http.delete<Individual>(`${this._OBJECT_API}/${id}`);
  }

  /**
   * Export the individuals list in the given format, with the same filters
   * and sort currently applied to the list/map (no pagination: the backend
   * exports the whole filtered list, bounded by its own NB_MAX_EXPORT).
   * Triggers a browser download once the file is received.
   *
   * @param {string} format One of config.INDIVIDUALS.INDIVIDUALS.EXPORT_FORMAT
   * @param {APIIndividualFiltersParams} filters Currently applied filters
   * @param {{ prop?: string; dir?: string }} [sort] Currently applied sort
   * @memberof IndividualsService
   */
  exportIndividuals(
    format: string,
    filters: APIIndividualFiltersParams,
    sort?: { prop?: string; dir?: string }
  ): void {
    let httpParams = new HttpParams();
    const params: Record<string, string | number | undefined> = { ...filters, ...sort };
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

    this._dataFormService.subscribeAndDownload(source, 'individuals', format);
  }
}
