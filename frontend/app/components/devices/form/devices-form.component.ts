import { Component, OnInit } from '@angular/core';
import { ActivatedRoute, Router } from '@angular/router';
import { Location } from '@angular/common';
import { FormBuilder, FormGroup, Validators } from '@angular/forms';
import { TranslateService } from '@ngx-translate/core';

import { CommonService } from '@geonature_common/service/common.service';
import { ModuleService } from '@geonature/services/module.service';

import { ErrorHandlerService } from '../../../services/errors-handler.service';
import { FormConstraint, AccessResult } from '../../../models/common.models';
import { Device } from '../../../models/devices.models';
import { DEVICE_FORM_CONSTRAINTS } from '../../../utils/constants.util';
import { DevicesService } from '../../../services/devices.service';

@Component({
  selector: 'gn-individuals-devices-form',
  templateUrl: 'devices-form.component.html',
  standalone: false,
})
export class DevicesFormComponent implements OnInit {
  public deviceId!: number;
  public formAction!: string;
  public form!: FormGroup;
  public formConstraints: Record<string, FormConstraint> = DEVICE_FORM_CONSTRAINTS;
  public datatable!: Device;
  public allowedToSave: AccessResult = { id: 0, access: false, message: null };

  constructor(
    private _route: ActivatedRoute,
    private _router: Router,
    private _translate: TranslateService,
    private _commonService: CommonService,
    private _module: ModuleService,
    private _fb: FormBuilder,
    private _service: DevicesService,
    private _location: Location,
    private _errorHandler: ErrorHandlerService
  ) {}

  ngOnInit(): void {
    // Form initialization
    this.form = this._fb.group({
      id_tracking_device: [null],
      id_nomenclature_device_type: [null, Validators.required],
      provider_name: [
        null,
        [
          Validators.required,
          Validators.maxLength(this.formConstraints.provider_name.maxLength),
          Validators.pattern(this.formConstraints.provider_name.pattern),
        ],
      ],
      provider_device_id: [
        null,
        [
          Validators.required,
          Validators.maxLength(this.formConstraints.provider_device_id.maxLength),
          Validators.pattern(this.formConstraints.provider_device_id.pattern),
        ],
      ],
      id_referer: [null, Validators.required],
      comment: [
        null,
        [
          Validators.maxLength(this.formConstraints.comment.maxLength),
          Validators.pattern(this.formConstraints.comment.pattern),
        ],
      ],
    });

    // Patch the form with the datatable resolver
    this._route.data.subscribe(({ datatable }) => {
      if (datatable && datatable['id_tracking_device']) {
        this.datatable = datatable;
        this.deviceId = datatable['id_tracking_device'];
        this.formAction = 'EDIT';
        this.patchForm(datatable);
      } else {
        this.formAction = 'ADD';
      }
    });

    // To be sure to wait translations before setting permissions
    this._translate
      .get([
        'Individuals.ApiErrors.InsufficientPermissions',
        'Individuals.Errors.FormInvalid',
        'Individuals.Errors.FormNotModified',
      ])
      .subscribe(() => {
        this._setPermissions(this.datatable);
      });

    this.form.valueChanges.subscribe(() => {
      this._setPermissions(this.datatable);
    });
  }

  patchForm(device: any): void {
    /// Modifier par : Device au lieu de any et faire le mapping si besoin
    this.form.patchValue(device, { emitEvent: false });

    this.form.patchValue(
      {
        id_nomenclature_device_type: device.nomenclature_device_type.id_nomenclature,
        id_referer: device.referer,
      },
      { emitEvent: false }
    );
  }

  onSave(): void {
    const device = this.form.getRawValue();

    this._service.createOrUpdateDevice(device, this.formAction).subscribe({
      next: (res) => {
        const successKey =
          this.formAction === 'ADD'
            ? 'Individuals.Devices.Messages.Added'
            : 'Individuals.Devices.Messages.Edited';
        this._commonService.translateToaster('info', successKey, { id: this.deviceId });
        this.form.markAsPristine();
        this._location.back();
      },
      error: (err) => {
        this._errorHandler.handleHttpError(
          err,
          { id: this.deviceId },
          'Individuals.Devices.ApiErrors'
        );
      },
    });
  }

  /**
   * Call on cancel event: redirect on devices list
   *
   * @memberof DevicesFormComponent
   */
  onCancel(): void {
    this._router.navigate(['/individuals/devices']);
  }

  /**
   * Set save permissions
   *
   * @private
   * @param {Device} datatable
   * @memberof DevicesFormComponent
   */
  private _setPermissions(datatable: Device): void {
    // Save Access
    if (datatable) {
      // Edit mode
      this.allowedToSave = {
        id: datatable.id_tracking_device ? datatable.id_tracking_device : 0,
        access: datatable.cruved?.U ?? false,
        message:
          (datatable.cruved?.U ?? false)
            ? null
            : this._translate.instant('Individuals.ApiErrors.InsufficientPermissions'),
      };
    } else {
      // Add mode
      const currentObject = this._module.currentModule.module_objects['DEVICES'];
      this.allowedToSave = {
        id: 0,
        access: currentObject?.cruved?.C == 0 ? false : true,
        message:
          currentObject?.cruved?.C == 0
            ? this._translate.instant('Individuals.ApiErrors.InsufficientPermissions')
            : null,
      };
    }

    if (this.allowedToSave.access) {
      if (!this.form.valid) {
        this.allowedToSave.access = false;
        this.allowedToSave.message = this._translate.instant('Individuals.Errors.FormInvalid');
      } else if (this.formAction === 'EDIT' && !this.form.dirty) {
        this.allowedToSave.access = false;
        this.allowedToSave.message = this._translate.instant('Individuals.Errors.FormNotModified');
      }
    }
  }
}
