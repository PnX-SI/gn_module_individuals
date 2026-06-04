import { ViewEncapsulation, Component, OnInit, AfterViewInit, Input, 
  TemplateRef, Output, EventEmitter } from '@angular/core';
import { Location } from '@angular/common';

import { ConfigService } from '@geonature/services/config.service';

@Component({
  selector: 'gn-individuals-form',
  templateUrl: 'form.component.html',
  styleUrls: ['form.component.scss'],
  encapsulation: ViewEncapsulation.None,
})
export class FormComponent implements OnInit, AfterViewInit {
  @Output() save: EventEmitter<any> = new EventEmitter();
  @Input() formTemplate!: TemplateRef<any>;
  @Input() formTitle: string = "";
  @Input() formAction: string = "";
  @Input() canSave: boolean = false;
  @Input() dataTable: any;

  constructor(
    public config: ConfigService,
    private _location: Location,
  ) {}

  ngOnInit() : void {
  }

  ngAfterViewInit() : void {
  }

  goBack() : void {
    this._location.back();
  }
}


