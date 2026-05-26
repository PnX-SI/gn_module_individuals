import { ViewEncapsulation, Component, OnInit, AfterViewInit } from '@angular/core';
import { ActivatedRoute } from '@angular/router';

import { Observable, of } from 'rxjs';

import { ConfigService } from '@geonature/services/config.service';

import { Device, DEVICE_COLUMNS } from '../../models/devices.models';

import { DevicesService } from '../../services/devices.service';  

@Component({
  selector: 'gn-individuals-devices-form',
  templateUrl: 'devices-form.component.html',
  styleUrls: ['devices-form.component.scss'],
  encapsulation: ViewEncapsulation.None,
})
export class DevicesFormComponent implements OnInit, AfterViewInit {
  public dataTable$: Observable<Device> = new Observable<Device>();
  public availableFields!: Device;
  public deviceId!: number | null;
  public formAction!: string;

  constructor(
    public config: ConfigService,
    private _devicesService: DevicesService,
    private _route: ActivatedRoute,
  ) {}

  ngOnInit() : void {
    const id = this._route.snapshot.paramMap.get('id_tracking_device');
    this.deviceId = id !== null ? Number(id) : null;
    this.formAction = this.deviceId ? 'UPDATE' : 'ADD';

    // First initialisation of the table with the resolver data, to display something while waiting for translations to load and avoid having an empty table at the beginning
    // this.activatedRoute.data.subscribe(({data}) => {
    //    this.dataTable$ = of(data);
    //    console.log(data);
    // });
  }

  ngAfterViewInit() : void {
  }
}


