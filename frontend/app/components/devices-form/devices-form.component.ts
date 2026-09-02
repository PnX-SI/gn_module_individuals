import { Component, OnInit } from '@angular/core';
import { ActivatedRoute } from '@angular/router';
import { Location } from '@angular/common';
import { FormBuilder, FormGroup, Validators } from '@angular/forms';

import { CommonService } from '@geonature_common/service/common.service';

import { ErrorHandlerService } from '../../services/errors-handler.service';
import { Device } from '../../models/devices.models';
import { FormConstraint } from '../../models/common.models';
import { DEVICE_FORM_CONSTRAINTS } from '../../utils/constants.util';
import { DevicesService } from '../../services/devices.service';

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

  constructor(
    private _route: ActivatedRoute,
    private _commonService: CommonService,
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
        this.deviceId = datatable['id_tracking_device'];
        this.formAction = 'EDIT';
        this.patchForm(datatable);
      } else {
        this.formAction = 'ADD';
      }
    });
  }

  patchForm(device: any): void {
    /// Modifier par : Device au lieu de any et faire le mapping si besoin
    this.form.patchValue(device);

    this.form.patchValue({
      id_nomenclature_device_type: device.nomenclature_device_type.id_nomenclature,
      id_referer: device.referer,
    });
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
}
