import { ViewEncapsulation, Component, OnInit, AfterViewInit } from '@angular/core';
import { ActivatedRoute } from '@angular/router';
import { FormBuilder, FormGroup, Validators } from '@angular/forms';
import { Observable, of } from 'rxjs';

import { ConfigService } from '@geonature/services/config.service';

import { Device, DEVICE_COLUMNS } from '../../models/devices.models';

import { DevicesService } from '../../services/devices.service';  

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

  constructor(
    public config: ConfigService,
    private _route: ActivatedRoute,
    private _fb: FormBuilder,
  ) {}

  ngOnInit() : void {
    const id = this._route.snapshot.paramMap.get('id_tracking_device');
    this.deviceId = id !== null ? Number(id) : null;
    this.formAction = this.deviceId ? 'EDIT' : 'ADD';

    // First initialisation of the table with the resolver data, to display something while waiting for translations to load and avoid having an empty table at the beginning
    if(this.formAction === 'UPDATE') {
      this._route.data.subscribe(({data}) => {
        this.dataTable$ = of(data);
      });
    }

    // Form initialization
    this.form = this._fb.group({
      id_tracking_device: null,
      id_nomenclature_device_type: [null, Validators.required],
      provider_name: [null, Validators.required, Validators.maxLength(50), Validators.pattern(/^[a-zA-Z0-9_-]*$/)],
      provider_device_id: [null, Validators.required, Validators.maxLength(50), Validators.pattern(/^[a-zA-Z0-9_-]*$/)],
      id_referer: [null, Validators.required],
      comment: [null, [Validators.required, Validators.maxLength(255), Validators.pattern(/^[^<>]*$/)]], // or [a-zA-Z0-9À-ÿ\s.,!?'"()_- ... to test
      id_digitiser : [null, Validators.required],
    });

    console.log(this.form.get('comment'));
  }

  ngAfterViewInit() : void {
  }
}


