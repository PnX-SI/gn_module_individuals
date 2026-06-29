import { Injectable } from '@angular/core';
import { Resolve, ActivatedRouteSnapshot, RouterStateSnapshot } from '@angular/router';
import { Observable } from 'rxjs';

import { PaginatedItemCollection } from '../models/common.models';
import { DevicesService } from '../services/devices.service';
import { Device } from '../models/devices.models';
import { DATA_TABLE_CONFIG } from '../utils/constants.util';

@Injectable({ providedIn: 'root' })
export class DevicesResolver implements Resolve<PaginatedItemCollection<Device>> {
  constructor(private _service: DevicesService) {}

  resolve(
    route: ActivatedRouteSnapshot,
    state: RouterStateSnapshot
  ): Observable<PaginatedItemCollection<Device>> {
    const params = {
      page: 1,
      per_page: DATA_TABLE_CONFIG.PER_PAGE_OPTION,
    };

    return this._service.getDevices(params);
  }
}

@Injectable({
  providedIn: 'root',
})
export class DeviceResolver implements Resolve<Device> {
  constructor(private _service: DevicesService) {}

  resolve(route: ActivatedRouteSnapshot, state: RouterStateSnapshot): Observable<Device> {
    return this._service.getDevice(route.params.id_tracking_device);
  }
}
