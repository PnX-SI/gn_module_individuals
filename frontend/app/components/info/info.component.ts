import { ViewEncapsulation, Component, OnInit, AfterViewInit, Input, TemplateRef } from '@angular/core';
import { Location } from '@angular/common';

import { ConfigService } from '@geonature/services/config.service';
import { ModuleService } from '@geonature/services/module.service';

@Component({
  selector: 'gn-individuals-info',
  templateUrl: 'info.component.html',
  styleUrls: ['info.component.scss'],
  encapsulation: ViewEncapsulation.None,
})
export class InfoComponent implements OnInit, AfterViewInit {
  @Input() infoTemplate!: TemplateRef<any>;
  @Input() infoTitle: string = "";
  @Input() dataTable: any;
  @Input() objectName: string = "";
  @Input() objectId: number | null = null;
  public moduleName: string = this._moduleService.currentModule.module_url;

  constructor(
    private _config: ConfigService,
    private _moduleService: ModuleService,
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


