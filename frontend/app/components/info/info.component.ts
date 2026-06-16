import { ViewEncapsulation, Component, OnInit, AfterViewInit, Input, 
  Output, EventEmitter, TemplateRef } from '@angular/core';

import { ModuleService } from '@geonature/services/module.service';

@Component({
  selector: 'gn-individuals-info',
  templateUrl: 'info.component.html',
  styleUrls: ['info.component.scss'],
  encapsulation: ViewEncapsulation.None,
})
export class InfoComponent implements OnInit, AfterViewInit {
  @Output() delete: EventEmitter<any> = new EventEmitter();
  @Input() infoTemplate!: TemplateRef<any>;
  @Input() infoTitle: string = "";
  @Input() dataTable: any;
  @Input() objectName: string = "";
  @Input() objectId: number | null = null;
  @Input() canBeDeleted: boolean = false;
  public moduleName: string = this._moduleService.currentModule.module_url;

  constructor(
    private _moduleService: ModuleService,
  ) {}

  ngOnInit() : void {
  }

  ngAfterViewInit() : void {
  }
}


