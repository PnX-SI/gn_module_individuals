import { Injectable } from '@angular/core';
import { Resolve, ActivatedRouteSnapshot, RouterStateSnapshot, Router } from '@angular/router';
import { Observable, of } from 'rxjs';

import { CommonService } from '@geonature_common/service/common.service';

import { DevicesService } from '../services/devices.service';
import { Device } from '../models/devices.models';
import  { PaginatedItemCollection } from '../models/common.models';

@Injectable({ providedIn: 'root' })
export class DevicesResolver implements Resolve<PaginatedItemCollection<Device>> {
  constructor(
    private service: DevicesService,
    private commonService: CommonService,
    private router: Router
  ) {}

  resolve(route: ActivatedRouteSnapshot, state: RouterStateSnapshot): Observable<PaginatedItemCollection<Device>> {
    return this.service.getDevices();
  }
}