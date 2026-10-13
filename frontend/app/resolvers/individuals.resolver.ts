import { Injectable } from '@angular/core';
import { Resolve, ActivatedRouteSnapshot, RouterStateSnapshot } from '@angular/router';
import { Observable } from 'rxjs';

import { IndividualsService } from '../services/individuals.service';
import { Individual } from '../models/individuals.models';


@Injectable({
  providedIn: 'root',
})
export class IndividualResolver implements Resolve<Individual> {
  constructor(private _service: IndividualsService) {}

  resolve(route: ActivatedRouteSnapshot, state: RouterStateSnapshot): Observable<Individual> {
    return this._service.getIndividual(route.params.id_individual);
  }
}
