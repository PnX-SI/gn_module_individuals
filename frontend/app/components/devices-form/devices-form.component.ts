import { ViewEncapsulation, Component, OnInit, AfterViewInit } from '@angular/core';
import { ActivatedRoute } from '@angular/router';
import { FormBuilder, FormGroup, Validators } from '@angular/forms';
import { Observable, combineLatest } from 'rxjs';
import { filter, take, switchMap, map } from 'rxjs/operators';

import { ConfigService } from '@geonature/services/config.service';

import { Device } from '../../models/devices.models';
import { DEVICE_FORM_CONSTRAINTS } from '../../utils/constants.util';
import { DevicesService } from '../../services/devices.service';
import { NomenclaturesService } from '../../services/nomenclature.service';

@Component({
  selector: 'gn-individuals-devices-form',
  templateUrl: 'devices-form.component.html',
  styleUrls: ['devices-form.component.scss'],
  encapsulation: ViewEncapsulation.None,
})
export class DevicesFormComponent implements OnInit, AfterViewInit {
  public dataTable$: Observable<Device> = new Observable<Device>();
  public availableFields!: Device;
  public deviceId!: number | null;
  public formAction!: string;
  public form!: FormGroup;
  public formConstraints = DEVICE_FORM_CONSTRAINTS;
  public lang = this._config.DEFAULT_LANGUAGE;

  constructor(
    private _config: ConfigService,
    private _route: ActivatedRoute,
    private _fb: FormBuilder,
    public nomenclatureService: NomenclaturesService,
    private _service: DevicesService
  ) {}

  ngOnInit() : void {
    // Form initialization
    this.form = this._fb.group({
      id_nomenclature_device_type: [null, Validators.required],
      provider_name: [
        null, 
        [
          Validators.required, 
          Validators.maxLength(this.formConstraints.provider_name.maxLength),
          Validators.pattern(this.formConstraints.provider_name.pattern)
        ]
      ],
      provider_device_id: [
        null, 
        [
          Validators.required, 
          Validators.maxLength(this.formConstraints.provider_device_id.maxLength), 
          Validators.pattern(this.formConstraints.provider_device_id.pattern)
        ]
      ],
      id_referer: [
        null, 
        Validators.required
      ],
      comment: [
        null, 
        [
          Validators.maxLength(this.formConstraints.comment.maxLength),
          Validators.pattern(this.formConstraints.comment.pattern)
        ]
      ],
    });

    // this.form.statusChanges.subscribe(status => {
    //   console.log('FORM STATUS:', status);

    //   Object.entries(this.form.controls).forEach(([name, control]) => {
    //     console.log(
    //       name,
    //       'value=', control.value,
    //       'valid=', control.valid,
    //       'errors=', control.errors
    //     );
    //   });
    // });
  }

  ngAfterViewInit() : void {
    this._route.params.subscribe((params) => {
        if (params['id_tracking_device']) {
          this.deviceId = params['id_tracking_device'];
          this.formAction = 'EDIT';
          // Peut-être pas utile le dataTable$
          this.dataTable$ = this._service.getDevice(params['id_tracking_device']);
          this._service.getDevice(params['id_tracking_device'])
            .subscribe((device: any) => {
  //   //           const deviceTypeId = device.id_nomenclature_device_type
  //   //           this.form.patchValue({
  //   //              id_nomenclature_device_type: device.id_nomenclature_device_type
  //   //           });
              this.patchForm(device);
            });
        } else {
          this.formAction = 'ADD';
        }
    });
  }
  
  patchForm(device: any) : void { /// Modifier par : Device au lieu de any et faire le mapping si besoin
    // this.form.patchValue({
    //   id_nomenclature_device_type: device.id_nomenclature_device_type,
    console.log('Device à patcher dans le form :', device);
    // console.log('Device à patcher dans le form :', device.nomenclature_device_type.cd_nomenclature);
    this.form.patchValue(device);
    this.form.patchValue({
      id_nomenclature_device_type: device.nomenclature_device_type,
      id_referer: device.referer
    });
    // this.form.patchValue(device);
    // this.form.patchValue({
    //    id_referer: device.referer_name
    // });
    
  }

  onSave() : void {
    const device = this.form.getRawValue();

    this._service.createDevice(device).subscribe({
      next: (res) => {
        console.log('Device créé', res);
      },
      error: (err) => {
        console.error(err);
      }
    });
  }
}