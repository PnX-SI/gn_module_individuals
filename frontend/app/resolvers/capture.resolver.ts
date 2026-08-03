import { Injectable } from '@angular/core';
import { Resolve, ActivatedRouteSnapshot, RouterStateSnapshot } from '@angular/router';
import { Observable } from 'rxjs';

import { ConfigService } from '@geonature/services/config.service';

import { FeatureCollection, PaginatedItemCollection } from '../models/common.models';
import { CaptureService } from '../services/capture.service';
import { Capture } from '../models/capture.model';
import { DATATABLE_CONFIG } from '../utils/constants.util';

@Injectable({ providedIn: 'root' })
export class CapturesResolver implements Resolve<PaginatedItemCollection<Capture>> {
  constructor(
    private _config: ConfigService,
    private _service: CaptureService
  ) {}

  resolve(
    route: ActivatedRouteSnapshot,
    state: RouterStateSnapshot
  ): Observable<PaginatedItemCollection<Capture>> {
    const params = {
      page: 1,
      per_page:
        this._config.INDIVIDUALS?.CAPTURES?.DEFAULT_PAGE_SIZE ?? DATATABLE_CONFIG.PER_PAGE_OPTION,
    };

    return this._service.getCaptures(params);
  }
}

@Injectable({ providedIn: 'root' })
export class CapturesMapResolver implements Resolve<FeatureCollection<Capture>> {
  constructor(private _service: CaptureService) {}

  resolve(
    route: ActivatedRouteSnapshot,
    state: RouterStateSnapshot
  ): Observable<FeatureCollection<Capture>> {
    return this._service.getCapturesforMap({});
  }
}

@Injectable({
  providedIn: 'root',
})
export class CaptureResolver implements Resolve<Capture> {
  constructor(private _service: CaptureService) {}

  resolve(route: ActivatedRouteSnapshot, state: RouterStateSnapshot): Observable<Capture> {
    return this._service.getCapture(route.params.id_capture);
  }
}
