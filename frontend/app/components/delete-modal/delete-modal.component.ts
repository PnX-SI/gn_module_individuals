import { Component, EventEmitter, Input, Output } from '@angular/core';
import { NgbActiveModal } from '@ng-bootstrap/ng-bootstrap';

@Component({
  selector: 'gn-individuals-delete-modal',
  templateUrl: './delete-modal.component.html',
  styleUrls: ['delete-modal.component.scss'],
  standalone: false,
})
export class DeleteModalComponent {
  /**
   * Modal title displayed in the header.
   */
  @Input() title: string = '';

  /**
   * HTML content displayed in the modal body.
   */
  @Input() body: string = '';

  /**
   * Emits when the user confirms the deletion.
   */
  @Output() confirm = new EventEmitter<void>();

  constructor(private _activeModal: NgbActiveModal) {}

  onConfirm(): void {
    this.confirm.emit();
    this._activeModal.close(true);
  }

  onCancel(): void {
    this._activeModal.dismiss();
  }
}
