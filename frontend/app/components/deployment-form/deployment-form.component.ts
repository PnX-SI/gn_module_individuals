import { Component, OnInit, Input } from '@angular/core';
import { FormGroup, Validators } from '@angular/forms';

import { ModuleService } from '@geonature/services/module.service';
import { ConfigService } from '@geonature/services/config.service';

import { DevicesService } from '../../services/devices.service';

@Component({
  selector: 'gn-individuals-deployment-form',
  templateUrl: 'deployment-form.component.html',
  standalone: false,
})
export class DeploymentFormComponent implements OnInit {
  @Input() public deploymentsForm: FormGroup;
  public trackingDevicesApiEndPoint: string = '';
  public trackingDevicesQueryString: string = '';
  public trackingDevicesHidden: boolean = false;

  constructor(
    private _config: ConfigService,
    public _moduleService: ModuleService,
    private _deviceService: DevicesService
  ) {}

  ngOnInit(): void {
    this.trackingDevicesApiEndPoint = `${this._config.API_ENDPOINT}/${this._moduleService.currentModule.module_url}/devices`;
    // Get tracking devices
    if (this.deploymentsForm.value.id_tracking_device) {
      console.log('get tracking devices');
      this._deviceService
        .getDevice(this.deploymentsForm.value.id_tracking_device)
        .subscribe((res) => {
          this.deploymentsForm.patchValue({ id_tracking_device: res });
        });
    }
  }

  trackingDevicesformatter(item) {
    return item.device_label;
  }
  setCdNomenclatureTypeMarquage(value) {
    const ctrTrackingDevice = this.deploymentsForm.get('id_tracking_device');
    if (value === '4') {
      ctrTrackingDevice?.setValidators([Validators.required]);
      this.trackingDevicesHidden = false;
    } else {
      ctrTrackingDevice?.clearValidators();
      ctrTrackingDevice?.setValue(null);
      this.trackingDevicesHidden = true;
    }
  }
}
