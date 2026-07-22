import { Component, Input } from '@angular/core';
import { KeyValue } from '@angular/common';
import { AbstractControl } from '@angular/forms';

@Component({
  selector: 'gn-individuals-input-radio',
  templateUrl: './input-radio.component.html',
  standalone: false,
})
export class InputRadioComponent {
  /**
   * Input Label
   */
  @Input() label = '';

  /**
   * Reactive form control bound to the input field.
   */
  @Input() parentFormControl!: AbstractControl | null;

  /**
   * CSS classes added to the component container classes (form-group).
   */
  @Input() containerClass = '';

  /**
   * CSS classes added to the input element classes (form-control and form-control-sm).
   */
  @Input() inputClass = '';

  @Input() options: KeyValue<string, string>[] = [];
}
