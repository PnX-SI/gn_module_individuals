import { Injectable } from '@angular/core';
import { Resolve, ActivatedRouteSnapshot, RouterStateSnapshot } from '@angular/router';
import { Observable } from 'rxjs';

import { ConfigService } from '@geonature/services/config.service';

import { FeatureCollection, PaginatedItemCollection } from '../models/common.models';
import { IndividualsService } from '../services/individuals.service';
import { Individual } from '../models/individuals.models';
import { DATATABLE_CONFIG } from '../utils/constants.util';

@Injectable({ providedIn: 'root' })
export class IndividualsResolver implements Resolve<PaginatedItemCollection<Individual>> {
  constructor(
    private _config: ConfigService,
    private _service: IndividualsService
  ) {}

  resolve(
    route: ActivatedRouteSnapshot,
    state: RouterStateSnapshot
  ): Observable<PaginatedItemCollection<Individual>> {
    const params = {
      page: 1,
      per_page: this._config.INDIVIDUALS.INDIVIDUALS.DEFAULT_PAGE_SIZE ?? DATATABLE_CONFIG.PER_PAGE_OPTION,
    };

    return this._service.getIndividuals(params);
  }
}

@Injectable({ providedIn: 'root' })
export class IndividualsMapResolver implements Resolve<FeatureCollection<Individual>> {
  constructor(
    private _service: IndividualsService
  ) {}

  resolve(
    route: ActivatedRouteSnapshot,
    state: RouterStateSnapshot
  ): Observable<FeatureCollection<Individual>> {
    return this._service.getIndividualsForMap({});
  }
}

@Injectable({
  providedIn: 'root',
})
export class IndividualResolver implements Resolve<Individual> {
  constructor(private _service: IndividualsService) {}

  resolve(route: ActivatedRouteSnapshot, state: RouterStateSnapshot): Observable<Individual> {
    return this._service.getIndividual(route.params.id_individual);
  }
}
