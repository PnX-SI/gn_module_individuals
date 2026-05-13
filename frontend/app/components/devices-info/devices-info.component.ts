import { ViewEncapsulation, Component, OnInit, AfterViewInit } from '@angular/core';
import { ActivatedRoute } from '@angular/router';

import { Observable, of } from 'rxjs';

import { ConfigService } from '@geonature/services/config.service';

import { Device, DEVICE_COLUMNS } from '../../models/devices.models';
import { Sort, PaginatedItemCollection, SimplePaginationWithSort } from '../../models/common.models';

import { DevicesService } from '../../services/devices.service';  

@Component({
  selector: 'gn-individuals-devices-info',
  templateUrl: 'devices-info.component.html',
  styleUrls: ['devices-info.component.scss'],
  encapsulation: ViewEncapsulation.None,
})
export class DevicesInfoComponent implements OnInit, AfterViewInit {

  constructor(
    public config: ConfigService,
    private _devicesService: DevicesService,
    private activatedRoute: ActivatedRoute,
  ) {}

  ngOnInit() : void {
  }

  ngAfterViewInit() : void {
  }
}


