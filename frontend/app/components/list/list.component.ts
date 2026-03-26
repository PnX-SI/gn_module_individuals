import { Component, OnInit, AfterViewInit, HostListener } from '@angular/core';
import { TranslateService } from '@ngx-translate/core';

import { combineLatest } from 'rxjs';
import { take } from 'rxjs/operators';

import { ConfigService } from '@geonature/services/config.service';
import { ModuleService } from '@geonature/services/module.service';

import { Column, Device } from '../../module.models';

const DEVICE_COLUMNS: Record<keyof Device, true> = {
  id_tracking_device: true,
  id_nomenclature_device_type: true,
  provider_name: true,
  provider_device_id: true,
  id_referer: true,
  comment: true,
  id_digitiser: true,
  meta_create_date: true,
  meta_update_date: true,
  nomenclature_device_type_name: true,
  referer_name: true,
  digitiser_name: true
};

@Component({
  selector: 'gn-individuals-list',
  templateUrl: 'list.component.html',
  styleUrls: ['list.component.scss'],
})
export class ListComponent implements OnInit, AfterViewInit {
  public userCruved: any;
  public contentHeight: number;
  public currentTabCode: string;
  public apiEndPoint: string;
  public displayedColumns: Column<Device>[] = []
  public availableColumns: Column<Device>[] = []

  constructor(
    public config: ConfigService,
    private _moduleService: ModuleService,
    private _translate: TranslateService
  ) {}

  ngOnInit() {
    // Get current module and current user CRUVED
    const currentModule = this._moduleService.currentModule;
    this.userCruved = currentModule.cruved;
    
    // Columns initialization with prop and empty name, to be filled with translations after
    this.availableColumns = (Object.keys(DEVICE_COLUMNS) as (keyof Device)[])
      .map(prop => ({ prop, name: '' }));

    this.displayedColumns = this.availableColumns.filter(column =>
      this.config.INDIVIDUALS.DEVICES.DEFAULT_DISPLAYED_COLUMNS.includes(column.prop)
    );

    // Build an array of translation observables for each column name
    const translateTab$ = (Object.keys(DEVICE_COLUMNS) as (keyof Device)[])
      .map(
        // An observable is returned which emits the translation of this key
        prop => this._translate.get(`Individuals.AvailableFields.${prop}`)
      );

    // Translation with CombineLatest will wait for all translations to be loaded before updating 
    // the column names, avoiding multiple updates and ensuring all names are translated at once.
    combineLatest(translateTab$)
      .subscribe(translations => {
        this.availableColumns = this.availableColumns.map((col, index) => ({
          ...col,
          name: translations[index]
        }));
        
        // Update displayedColumns with the translated names
        this.displayedColumns = this.displayedColumns.map(col =>
          ({ ...col, name: this.availableColumns.find(c => c.prop === col.prop)?.name || '' })
        );
      });
  }

  ngAfterViewInit() {
  }

  // Listen to window resize event to recalculate the content height and resize the map
  @HostListener('window:resize', ['$event'])
  onResize(event) {
    this.calcContentHeight();
  }

  // Fonction that return the size of the content of the card, to set the height of the map
  calcContentHeight() {
    let windowH = window.innerHeight;
    let toolbarH = document.getElementById('individuals-tab')
      ? document.getElementById('individuals-tab').getBoundingClientRect().top
      : 0;
    let height = windowH - (toolbarH + 80);

    this.contentHeight = height >= 350 ? height : 350;
    
    // Resize list after resize container
  }
}


