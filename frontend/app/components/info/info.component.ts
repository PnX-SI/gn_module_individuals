import { ViewEncapsulation, Component, OnInit, AfterViewInit, Input, TemplateRef } from '@angular/core';
import { Location } from '@angular/common';
import { TranslateService } from '@ngx-translate/core';
import { ActivatedRoute } from '@angular/router';

import { Observable, of } from 'rxjs';

import { ConfigService } from '@geonature/services/config.service';

import { Device, DEVICE_COLUMNS } from '../../models/devices.models';

import { DevicesService } from '../../services/devices.service';  

@Component({
  selector: 'gn-individuals-info',
  templateUrl: 'info.component.html',
  styleUrls: ['info.component.scss'],
  encapsulation: ViewEncapsulation.None,
})
export class InfoComponent implements OnInit, AfterViewInit {
  @Input() infoTemplate!: TemplateRef<any>;
  @Input() infoTitle: string = "";
  @Input() dataTable: any;

  constructor(
    public config: ConfigService,
    private _location: Location,
  ) {}

  ngOnInit() : void {
  }

  ngAfterViewInit() : void {
  }

  goBack() : void {
    this._location.back();
  }
}


