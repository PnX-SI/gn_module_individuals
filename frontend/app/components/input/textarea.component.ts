import { Component, Input } from '@angular/core';
import { AbstractControl, ɵInternalFormsSharedModule } from '@angular/forms';

@Component({
  selector: 'gn-individuals-textarea',
  templateUrl: './textarea.component.html',
  standalone: false,
})
export class TextareaComponent {
  /**
   * Input Label
   */
  @Input() label = '';

  /**
   * Reactive form control bound to the input field.
   */
  @Input() parentFormControl!: AbstractControl | null;

  /**
   * Maximum number of characters allowed in the input.
   */
  @Input() maxLength: number | null = null;

  /**
   * Validation error message displayed when the field is invalid.
   */
  @Input() errorKey: string | null = null;

  /**
   * CSS classes added to the component container classes (form-group).
   */
  @Input() containerClass = '';

  /**
   * CSS classes added to the input element classes (form-control and form-control-sm).
   */
  @Input() inputClass = '';

  /**
   * Place holder for the textarea. Default set with label
   */
  @Input() placeHolder: string | null = null;
}
