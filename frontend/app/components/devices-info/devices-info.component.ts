import { ViewEncapsulation, Component, OnInit, AfterViewInit } from '@angular/core';
import { ActivatedRoute } from '@angular/router';

import { Observable, of } from 'rxjs';

import { ConfigService } from '@geonature/services/config.service';

import { Device, DEVICE_COLUMNS } from '../../models/devices.models';

import { DevicesService } from '../../services/devices.service';  

@Component({
  selector: 'gn-individuals-devices-info',
  templateUrl: 'devices-info.component.html',
  styleUrls: ['devices-info.component.scss'],
  encapsulation: ViewEncapsulation.None,
})
export class DevicesInfoComponent implements OnInit, AfterViewInit {
  public dataTable$: Observable<Device> = new Observable<Device>();
  public availableFields!: Device;

  constructor(
    public config: ConfigService,
    private _devicesService: DevicesService,
    private activatedRoute: ActivatedRoute,
  ) {}

  ngOnInit() : void {
    // First initialisation of the table with the resolver data, to display something while waiting for translations to load and avoid having an empty table at the beginning
    this.activatedRoute.data.subscribe(({data}) => {
       this.dataTable$ = of(data);
       console.log(data);
    });
    
  }

  ngAfterViewInit() : void {
  }
}


