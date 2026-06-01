import { Injectable } from '@angular/core';
import { Resolve, ActivatedRouteSnapshot, RouterStateSnapshot } from '@angular/router';
import { Observable } from 'rxjs';

import { DevicesService } from '../services/devices.service';
import { Device } from '../models/devices.models';
import  { PaginatedItemCollection } from '../models/common.models';

@Injectable({ providedIn: 'root' })
export class DevicesResolver implements Resolve<PaginatedItemCollection<Device>> {
  constructor(
    private _service: DevicesService
  ) {}

  resolve(route: ActivatedRouteSnapshot, state: RouterStateSnapshot): Observable<PaginatedItemCollection<Device>> {
    return this._service.getDevices();
  }
}

@Injectable({
  providedIn: 'root'
})
export class DeviceResolver implements Resolve<Device> {
  constructor(
    private _service: DevicesService
  ) {}

  resolve(route: ActivatedRouteSnapshot,  state: RouterStateSnapshot): Observable<Device> {
    return this._service.getDevice(route.params.id_tracking_device);
  }
}