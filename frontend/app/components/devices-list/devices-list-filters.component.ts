import { ViewEncapsulation, Component, OnInit } from '@angular/core';
import { FormBuilder, FormGroup, Validators } from '@angular/forms';
import { Observable } from 'rxjs';

import { ConfigService } from '@geonature/services/config.service';
import { CommonService } from '@geonature_common/service/common.service';

import { ErrorHandlerService } from '../../services/errors-handler.service';
import { Device } from '../../models/devices.models';
import { FormConstraint } from '../../models/common.models';
import { DEVICE_FORM_CONSTRAINTS } from '../../utils/constants.util';
import { DevicesService } from '../../services/devices.service';
import { NomenclaturesService } from '../../services/nomenclature.service';

@Component({
  selector: 'gn-individuals-devices-list-filters',
  templateUrl: 'devices-list-filters.component.html',
  styleUrls: ['devices-list-filters.component.scss'],
  encapsulation: ViewEncapsulation.None,
  standalone: false,
})
export class DevicesListFiltersComponent implements OnInit {
  public filtersForm!: FormGroup;
  public formConstraints: Record<string,FormConstraint> = DEVICE_FORM_CONSTRAINTS;

  constructor(
    private _fb: FormBuilder,
    public nomenclatureService: NomenclaturesService,
    private _service: DevicesService,
  ) {}

  ngOnInit(): void {
    // Form initialization
    this.filtersForm = this._fb.group({
    //   id_nomenclature_device_type: [null, Validators.required],
      provider_name: [
        null,
        [
          Validators.required,
          Validators.maxLength(this.formConstraints.provider_name.maxLength),
          Validators.pattern(this.formConstraints.provider_name.pattern),
        ],
      ],
    });
  }

  onSubmit(): void {
//     const device = this.form.getRawValue();

//     this._service.createOrUpdateDevice(device, this.formAction, this.deviceId).subscribe({
//       next: (res) => {
//         const successKey =
//           this.formAction === 'ADD'
//             ? 'Individuals.Devices.Messages.Added'
//             : 'Individuals.Devices.Messages.Edited';
//         this._commonService.translateToaster('info', successKey, { id: this.deviceId });
//         this.form.markAsPristine();
//         this._location.back();
//       },
//       error: (err) => {
//         this._errorHandler.handleHttpError(
//           err,
//           { id: this.deviceId },
//           'Individuals.Devices.ApiErrors'
//         );
//       },
//     });
  }
}
