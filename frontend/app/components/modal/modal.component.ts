import { Component, EventEmitter, Input, Output, Type, Injector, InjectionToken } from '@angular/core';
import { NgbActiveModal } from '@ng-bootstrap/ng-bootstrap';

export const MODAL_BODY_DATA = new InjectionToken<any>('MODAL_BODY_DATA');

@Component({
  selector: 'gn-individuals-modal',
  templateUrl: './modal.component.html',
  standalone: false,
})
export class ModalComponent {
  /**
   * Modal title displayed in the header
   *
   * @type {string}
   * @memberof ModalComponent
   */
  @Input() title: string | null = null;

  /**
   * HTML content displayed in the modal body
   *
   * @type {string}
   * @memberof ModalComponent
   */
  @Input() bodyHTML: string = '';

  /**
   * Component displayed in the modal body.
   *
   * @type {Type<any>}
   * @memberof ModalComponent
   */
  @Input() bodyComponent?: Type<any>;

  /**
   * Data to inject to the body component.
   *
   * @type {*}
   * @memberof ModalComponent
   */
  @Input() bodyComponentData?: any;

  /**
   * Define the validate button tag
   *
   * @type {('delete' | 'save')}
   * @memberof DeleteModalComponent
   */
  @Input() validateButtonType: 'delete' | 'save' | null = null;

  /**
   * Emits when the user select by click the validate action
   *
   * @memberof ModalComponent
   */
  @Output() validate = new EventEmitter<void>();

  public bodyInjector!: Injector;

  constructor(
    private _activeModal: NgbActiveModal,
    private _injector: Injector
  ) {}

  ngOnInit() {
    this.bodyInjector = Injector.create({
      providers: [
        {
          provide: MODAL_BODY_DATA,
          useValue: this.bodyComponentData,
        },
      ],
      parent: this._injector,
    });
  }

  onValidate(): void {
    this.validate.emit();
    this._activeModal.close(true);
  }

  onCancel(): void {
    this._activeModal.dismiss();
  }
}
