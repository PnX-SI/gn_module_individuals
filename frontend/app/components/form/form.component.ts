import { ViewEncapsulation, Component, OnInit, AfterViewInit, Input, TemplateRef } from '@angular/core';
import { Location } from '@angular/common';

import { ConfigService } from '@geonature/services/config.service';

@Component({
  selector: 'gn-individuals-form',
  templateUrl: 'form.component.html',
  styleUrls: ['form.component.scss'],
  encapsulation: ViewEncapsulation.None,
})
export class FormComponent implements OnInit, AfterViewInit {
  @Input() formTemplate!: TemplateRef<any>;
  @Input() formTitle: string = "";
  @Input() formAction: string = "";
  // @Input() dataTable: any;

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

  save() : void {
    alert("Save action not implemented yet");
  }
}


