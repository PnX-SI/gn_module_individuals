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
import { ModuleService } from '@geonature/services/module.service';

@Component({
  selector: 'gn-individuals-form',
  templateUrl: 'form.component.html',
  styleUrls: ['form.component.scss'],
  encapsulation: ViewEncapsulation.None,
})
export class FormComponent implements OnInit, AfterViewInit {
  @Output() save: EventEmitter<any> = new EventEmitter();
  @Input() formTemplate!: TemplateRef<any>;
  @Input() formTitle: string = '';
  @Input() formAction: string = '';
  @Input() canSave: boolean = false;
  @Input() dataTable: any;
  @Input() objectName: string = '';
  public moduleName: string = this._moduleService.currentModule.module_url;

  constructor(
    public config: ConfigService,
    private _moduleService: ModuleService
  ) {}

  ngOnInit(): void {}

  ngAfterViewInit(): void {}
}
