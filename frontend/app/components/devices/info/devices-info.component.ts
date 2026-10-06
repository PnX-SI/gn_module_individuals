import { ViewEncapsulation, Component, OnInit } from '@angular/core';
import { ActivatedRoute, Router } from '@angular/router';
import { forkJoin } from 'rxjs';
import { TranslateService } from '@ngx-translate/core';

import { ConfigService } from '@geonature/services/config.service';
import { CommonService } from '@geonature_common/service/common.service';

import { DATATABLE_CONFIG } from '../../../utils/constants.util';
import { Device } from '../../../models/devices.models';
import { Deployment } from '../../../models/deployments.models';
import { Column, AccessResult } from '../../../models/common.models';
import { DevicesService } from '../../../services/devices.service';

@Component({
  selector: 'gn-individuals-devices-info',
  templateUrl: 'devices-info.component.html',
  styleUrls: ['devices-info.component.scss'],
  // SCSS used only in this component and not in the global CSS
  encapsulation: ViewEncapsulation.None,
  standalone: false,
})
export class DevicesInfoComponent implements OnInit {
  public datatable!: Device;
  public deploymentsColumns: Column<Deployment>[] = [];
  public rowHeight: number = DATATABLE_CONFIG.TABLE_ROW_HEIGHT;
  public allowedToDelete: AccessResult = { id: 0, access: false, message: null };
  public allowedToEdit: AccessResult = { id: 0, access: false, message: null };
  private _deviceId!: number;

  constructor(
    private _config: ConfigService,
    private _commonService: CommonService,
    private _route: ActivatedRoute,
    private _router: Router,
    private _translate: TranslateService,
    private _service: DevicesService
  ) {}

  ngOnInit(): void {
    // First initialisation of the table with the resolver data, to display something while waiting for translations to load and avoid having an empty table at the beginning
    this._route.data.subscribe(({ datatable }) => {
      this.datatable = datatable;
      this._deviceId = datatable.id_tracking_device;

      // If they're deployments to display, create the columns table for ngx-datatable with translated fields
      if (datatable.deployments?.length > 0) {
        const props = this._config.INDIVIDUALS.DEVICES
          .DEPLOYMENT_LIST_COLUMNS as (keyof Deployment)[];

        forkJoin(
          props.map((prop) => this._translate.get(`Individuals.Deployments.Fields.${prop}`))
        ).subscribe((translations) => {
          this.deploymentsColumns = props.map((prop, name) => ({
            prop: prop,
            name: translations[name],
          }));
        });
      } else {
        datatable.deployments = [];
      }
    });

    // To be sure to wait translations before setting permissions
    this._translate
      .get(['Individuals.ApiErrors.InsufficientPermissions', 'Individuals.ApiErrors.HasDeployment'])
      .subscribe(() => {
        this._setPermissions(this.datatable);
      });
  }

  onDelete(): void {
    this._service.deleteDevice(this._deviceId).subscribe({
      next: (res) => {
        this._commonService.translateToaster('info', 'Individuals.Devices.Messages.Deleted', {
          id: this._deviceId,
        });
        this._router.navigate(['/individuals/devices']);
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

  /**
   * Set edit and delete permissions
   *
   * @private
   * @param {Device} datatable Device object to set button access
   * @memberof DevicesInfoComponent
   */
  private _setPermissions(datatable: Device) {
    // Edit Access
    this.allowedToEdit = {
      id: datatable.id_tracking_device,
      access: datatable.cruved?.U ?? false,
      message:
        (datatable.cruved?.U ?? false)
          ? null
          : this._translate.instant('Individuals.ApiErrors.InsufficientPermissions'),
    };

    // Delete access
    this.allowedToDelete = {
      id: datatable.id_tracking_device,
      access: datatable.cruved?.D ?? false,
      message:
        (datatable.cruved?.D ?? false)
          ? null
          : this._translate.instant('Individuals.ApiErrors.InsufficientPermissions'),
    };

    // Check if device has deployments, if yes : no access
    if (this.allowedToDelete.access && datatable.deployments?.length > 0) {
      this.allowedToDelete.access = false;
      this.allowedToDelete.message = this._translate.instant('Individuals.ApiErrors.HasDeployment');
    }
  }
}
