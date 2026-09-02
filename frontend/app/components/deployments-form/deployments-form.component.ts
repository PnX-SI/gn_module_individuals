import { Component, OnInit, Inject } from '@angular/core';
import { FormBuilder, FormGroup, Validators, AbstractControl, ValidationErrors, ValidatorFn } from '@angular/forms';
import { NgbActiveModal } from '@ng-bootstrap/ng-bootstrap';

import { CommonService } from '@geonature_common/service/common.service';
import { ModuleService } from '@geonature/services/module.service';
import { ConfigService } from '@geonature/services/config.service';

import { ErrorHandlerService } from '../../services/errors-handler.service';

import { FormConstraint } from '../../models/common.models';
import { Device } from '../../models/devices.models';
import { DEPLOYMENTS_FORM_CONSTRAINTS } from '../../utils/constants.util';
import { DevicesService } from '../../services/devices.service';
import { DeploymentsService } from '../../services/deployments.service';
import { MODAL_BODY_DATA } from '../modal/modal.component';
import { Deployment } from '../../models/deployments.models';

@Component({
  selector: 'gn-individuals-deployments-form',
  templateUrl: 'deployments-form.component.html',
  standalone: false,
})
export class DeploymentsFormComponent implements OnInit {
  public formAction!: string;
  public form!: FormGroup;
  public formConstraints: Record<string, FormConstraint> = DEPLOYMENTS_FORM_CONSTRAINTS;
  public devicesApiEndPoint: string = '';
  public showDevice: boolean = true;

  private dateRangeValidator: ValidatorFn = (control: AbstractControl): ValidationErrors | null => {
    const installDate = control.get('install_date')?.value;
    const removalDate = control.get('removal_date')?.value;

    const dateMin = installDate ? new Date(installDate) : null;
    const dateMax = removalDate ? new Date(removalDate) : null;
    const today = new Date();

    if (dateMin && (dateMin > today || dateMax && dateMin >= dateMax)) {
      return { invalidStartDate: true };
    }
    else if (dateMax && (dateMax > today || dateMin && dateMax <= dateMin)) {
      return { invalidEndDate: true };
    }
    return null;
  };

  constructor(
    private _commonService: CommonService,
    private _fb: FormBuilder,
    private _module: ModuleService,
    private _config: ConfigService,
    private _devicesService: DevicesService,
    private _deploymentsService: DeploymentsService,
    private _errorHandler: ErrorHandlerService,
    private _activeModal: NgbActiveModal,
    // Tells Angular to inject the value 
    // associated with the MODAL_BODY_DATA de the datatable property
    @Inject(MODAL_BODY_DATA) public datatable: Deployment,
  ) {}

  ngOnInit(): void {
    this.devicesApiEndPoint = `${this._config.API_ENDPOINT}/${this._module.currentModule.module_url}/devices`;

    // Form initialization
    this.form = this._fb.group(
      {
        id_deployment: [null],
        id_individual: [null],
        id_nomenclature_deployment_type: [null, Validators.required],
        id_nomenclature_deployment_location: [null, Validators.required],
        id_tracking_device: [null],
        marking_code: [
          null,
          [
            Validators.maxLength(this.formConstraints.marking_code.maxLength),
            Validators.pattern(this.formConstraints.marking_code.pattern)
          ],
        ],
        install_date: [null],
        removal_date: [null],
        comment: [
          null,
          [
            Validators.maxLength(this.formConstraints.comment.maxLength),
            Validators.pattern(this.formConstraints.comment.pattern),
          ],
        ],
      },
      {
        validators: [this.dateRangeValidator],
      }
    );

    // Patch the form with the datatable
    if (this.datatable && this.datatable.id_individual) {
      this.formAction = this.datatable.id_deployment ? 'EDIT' : 'ADD';
      this.patchForm(this.datatable);
    }
  }

  patchForm(deployment: any): void {
    this.form.patchValue(deployment);

    // Get tracking device
    if (this.form.value.id_tracking_device) {
      this._devicesService
        .getDevice(this.form.value.id_tracking_device)
        .subscribe((device) => {
          this.form.patchValue({ id_tracking_device: device });
      });
    }
  }

  devicesFormatter(item: Device) {
    return item.device_label;
  }

  toogleTrakingDevice($event: string) {
    const control = this.form.get('id_tracking_device');
    if ($event === '4') {
      control?.setValidators([Validators.required]);
      this.showDevice = true;
    } else {
      control?.clearValidators();
      control?.setValue(null);
      this.showDevice = false;
    }
  }

  onSave(): void {
    const deployment = this.form.getRawValue();

    this._deploymentsService.createOrUpdateDeployment(deployment, this.formAction).subscribe({
      next: (res) => {
        const successKey =
          this.formAction === 'ADD'
            ? 'Individuals.Deployments.Messages.Added'
            : 'Individuals.Deployments.Messages.Edited';
        this._commonService.translateToaster('info', successKey, { id: this.datatable.id_deployment });
        this.form.markAsPristine();
        // The close method emits the value true to the modalRef.result promise in the parent component
        this._activeModal.close(true);
      },
      error: (err) => {
        this._errorHandler.handleHttpError(
          err,
          { id: this.datatable.id_deployment },
          'Individuals.Deployments.ApiErrors'
        );
      },
    });
  }

  onCancel(): void {
    this._activeModal.dismiss();
  }
}
