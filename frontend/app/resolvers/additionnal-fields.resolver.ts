import { Injectable } from '@angular/core';
import { Resolve, ActivatedRouteSnapshot, RouterStateSnapshot } from '@angular/router';
import { Observable } from 'rxjs';

import { ModuleService } from '@geonature/services/module.service';
import { DataFormService } from '@geonature_common/form/data-form.service';


@Injectable({ providedIn: 'root' })
export class AdditionalFieldsResolver implements Resolve<Array<any>> {
  constructor(
    private _module: ModuleService,
    private _service: DataFormService
  ) {}

  resolve(
    route: ActivatedRouteSnapshot,
    state: RouterStateSnapshot
  ): Observable<Array<any>> {
    return this._service.getadditionalFields({
      module_code: [this._module.currentModule.module_code],
    });
  }
}
