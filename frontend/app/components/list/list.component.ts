import { ViewEncapsulation, Component, OnInit, ViewChild, AfterViewInit, HostListener } from '@angular/core';
import { TranslateService } from '@ngx-translate/core';

import { BehaviorSubject, Observable, combineLatest } from 'rxjs';
import { switchMap, shareReplay, tap } from 'rxjs/operators';

import { DatatableComponent } from '@swimlane/ngx-datatable';

import { ConfigService } from '@geonature/services/config.service';
import { ModuleService } from '@geonature/services/module.service';

import { ContentConfig, DataTableConfig } from '../../module.config';
import { Device, DEVICE_COLUMNS, DevicesAPIParams } from '../../models/devices.models';
import { Column, SimplePagination, PaginatedItemCollection } from '../../models/common.models';

import { DevicesService } from '../../services/devices.service';  

@Component({
  selector: 'gn-individuals-list',
  templateUrl: 'list.component.html',
  styleUrls: ['list.component.scss'],
  encapsulation: ViewEncapsulation.None
})
export class ListComponent implements OnInit, AfterViewInit {
  //@ViewChild('dataTable') dataTable: DatatableComponent;
  public userCruved: any;
  public contentHeight: number = ContentConfig.MIN_HEIGHT;
  public rowHeight: number = DataTableConfig.TABLE_ROW_HEIGHT;
  public headerFooterHeight = DataTableConfig.TABLE_ROW_HEIGHT < 50 ? 50 : DataTableConfig.TABLE_ROW_HEIGHT;
  public rowNumber: number = DataTableConfig.PER_PAGE_OPTION;
  public displayedColumns: Column<Device>[] = []
  public availableColumns: Column<Device>[] = []
  private _pagination$ = new BehaviorSubject<SimplePagination>({
    page: 1,
    limit: DataTableConfig.PER_PAGE_OPTION,
  });
  public dataTable$: Observable<PaginatedItemCollection<Device>>;
  
  constructor(
    public config: ConfigService,
    private _moduleService: ModuleService,
    private _translate: TranslateService,
    private _devicesService: DevicesService
  ) {}

  ngOnInit() : void {
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

    // Calculate the height of the content and the number of rows to display in the table, based on the viewport height
    this.contentHeight = this.calcContentHeight();
    this.rowNumber = this.calcRowNumber();

    this.dataTable$ = this._pagination$.pipe(
      // Transform the emitted value (pagination) into an API call
      switchMap(({ page, limit }) => 
        this._devicesService.getDevices({page, per_page: limit})
      ),
      tap(data => console.log('Devices JSON:', data)),
      // Set in cache the last emitted value, If the same is called,
      // no need to call the API again
      shareReplay({ bufferSize: 1, refCount: true })
    );
  }

  ngAfterViewInit() : void {
  }

  // Listen to window resize event to recalculate the content height and resize the map
  // @HostListener('window:resize', ['$event'])
  // onResize(event) : void {
  //   this.contentHeight = this.calcContentHeight();
  // }

  // Fonction that sets the size of the content of the card, to set the height of the map
  // and calculate the number of rows to display in the table based on the viewport height
  calcContentHeight() : number {
    let windowH = window.innerHeight;
    const toolbarElement = document.getElementById('individuals-tab');
    let toolbarH = toolbarElement
      ? toolbarElement.getBoundingClientRect().top
      : 0;
    let height = windowH - (toolbarH + 80);

    return height >= ContentConfig.MIN_HEIGHT ? height : ContentConfig.MIN_HEIGHT;
  }

  calcRowNumber() : number {
    let num = Math.trunc(this.contentHeight / DataTableConfig.TABLE_ROW_HEIGHT);
    num = num > DataTableConfig.PER_PAGE_OPTION ? DataTableConfig.PER_PAGE_OPTION : num;
    return num;
  }

  onPage($event: any) : void {
    console.log('Page event:', $event);
    this._pagination$.next({
      page: Number($event.offset ?? 0) + 1,
      limit: Number($event.limit ?? this._pagination$.getValue().limit),
    });
  }
}


