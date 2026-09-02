import {
  ViewEncapsulation,
  Component,
  OnInit,
  AfterViewInit,
  Input,
  TemplateRef,
  Output,
  EventEmitter,
} from '@angular/core';

import { ConfigService } from '@geonature/services/config.service';

import { AccessResult } from '../../models/common.models';

@Component({
  selector: 'gn-individuals-form',
  templateUrl: 'form.component.html',
  styleUrls: ['form.component.scss'],
  // SCSS used only in this component and not in the global CSS
  encapsulation: ViewEncapsulation.None,
  standalone: false,
})
export class FormComponent implements OnInit, AfterViewInit {
  @Output() save: EventEmitter<any> = new EventEmitter();
  @Output() cancel: EventEmitter<any> = new EventEmitter();
  @Input() formTemplate!: TemplateRef<any>;
  @Input() formTitle: string = '';
  @Input() formAction: string = '';
  @Input() allowedToSave: AccessResult = { id: 0, access: true };

  constructor(
    public config: ConfigService,
  ) {}

  ngOnInit(): void {}

  ngAfterViewInit(): void {}
}
