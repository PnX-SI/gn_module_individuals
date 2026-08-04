import { Injectable } from '@angular/core';
import { FormBuilder, FormGroup, Validators } from '@angular/forms';

@Injectable()
export class DeployementsService {
  constructor(private _fb: FormBuilder) {}

  generateDeploymentForm(): FormGroup {
    return this._fb.group({
      comment: [null],
      id_deployment: [null],
      id_individual: [null],
      id_nomenclature_deployment_location: [null, Validators.required],
      id_nomenclature_deployment_type: [null, Validators.required],
      id_tracking_device: [null],
      install_date: [null, Validators.required],
      marking_code: [null],
      removal_date: [null],
      tracking_device_info: [null],
    });
  }
  formToJson(deployment: any): any {
    if (deployment.id_tracking_device) {
      deployment.id_tracking_device = deployment.id_tracking_device.id_tracking_device;
    }
    return deployment;
  }
}
