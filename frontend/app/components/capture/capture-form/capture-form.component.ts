import { Component } from '@angular/core';
import {
  AbstractControl,
  ValidatorFn,
  UntypedFormGroup,
  Validators,
  ValidationErrors,
  FormBuilder,
  FormGroup,
  FormControl,
} from '@angular/forms';

@Component({
  selector: 'gn-individuals-capture-form',
  templateUrl: 'capture-form.component.html',
  styleUrls: ['capture-form.component.scss'],
  standalone: false,
})
export class CaptureFormComponent {
  public form_group: UntypedFormGroup = new FormGroup({
    id_nomenclature_protocol: new FormControl<number | null>(null, Validators.required),
    comment: new FormControl<string>(''),
    date: new FormControl<any>(Date.now(), Validators.required),
    observers: new FormControl<any>([]),
    individuals: new FormControl<any[]>([]),
  });
}
