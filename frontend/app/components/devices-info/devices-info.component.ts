import { ViewEncapsulation, Component, OnInit, AfterViewInit } from '@angular/core';
import { Location } from '@angular/common';
import { ActivatedRoute } from '@angular/router';
import { Observable, of, forkJoin } from 'rxjs';
import { TranslateService } from '@ngx-translate/core';

import { ConfigService } from '@geonature/services/config.service';
import { CommonService } from '@geonature_common/service/common.service';

import { DATA_TABLE_CONFIG } from '../../utils/constants.util';
import { Device } from '../../models/devices.models';
import { Deployment } from '../../models/deployments.models';
import { Column } from '../../models/common.models';
import { DevicesService } from '../../services/devices.service';

@Component({
  selector: 'gn-individuals-devices-info',
  templateUrl: 'devices-info.component.html',
  styleUrls: ['devices-info.component.scss'],
  // SCSS used only in this component and not in the global CSS
  encapsulation: ViewEncapsulation.None,
  standalone: false,
})
export class DevicesInfoComponent implements OnInit, AfterViewInit {
  public dataTable$: Observable<Device> = new Observable<Device>();
  public deploymentsColumns: Column<Deployment>[] = [];
  public rowHeight: number = DATA_TABLE_CONFIG.TABLE_ROW_HEIGHT;
  public canBedeleted: boolean = false;
  private _deviceId!: number;

  constructor(
    private _config: ConfigService,
    private _commonService: CommonService,
    private _route: ActivatedRoute,
    private _translate: TranslateService,
    private _service: DevicesService,
    private _location: Location
  ) {}

  ngOnInit(): void {
    // First initialisation of the table with the resolver data, to display something while waiting for translations to load and avoid having an empty table at the beginning
    this._route.data.subscribe(({ data }) => {
      this.dataTable$ = of(data);
      this._deviceId = data.id_tracking_device;

      // If they're deployments to display, create the columns table for ngx-datatable with translated fields
      if (data.deployments?.length > 0) {
        const props = this._config.INDIVIDUALS.DEVICES
          .DEFAULT_DEPLOY_DISPLAYED_COLUMNS as (keyof Deployment)[];

        forkJoin(
          props.map((prop) => this._translate.get(`Individuals.Deployments.Fields.${prop}`))
        ).subscribe((translations) => {
          this.deploymentsColumns = props.map((prop, name) => ({
            prop: prop,
            name: translations[name],
            sortable: false,
          }));
        });
        this.canBedeleted = true;
      } else {
        data.deployments = [];
      }

      // Search null values in deployments data and replace them by "-"
      Object.keys(data['deployments']).forEach((dep) => {
        Object.keys(data['deployments'][dep]).forEach((key) => {
          if (data['deployments'][dep][key] == null) {
            data['deployments'][dep][key] = '-';
          }
        });
      });
    });
  }

  ngAfterViewInit(): void {}

  onDelete(): void {
    this._service.deleteDevice(this._deviceId).subscribe({
      next: (res) => {
        this._commonService.translateToaster('info', 'Individuals.Devices.Messages.Deleted', {
          id: this._deviceId,
        });
        this._location.back();
      },
      error: (err) => {
        const msg = err.name + ':' + err.message || JSON.stringify(err);
        this._commonService.translateToaster('error', 'Individuals.Devices.Errors.DeletedNOK', {
          id: this._deviceId,
          error: msg,
        });
      },
    });
  }
}
