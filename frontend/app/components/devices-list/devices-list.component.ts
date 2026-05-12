import { ViewEncapsulation, Component, OnInit, AfterViewInit } from '@angular/core';
import { ActivatedRoute } from '@angular/router';

import { Observable, of } from 'rxjs';

import { ConfigService } from '@geonature/services/config.service';

import { Device, DEVICE_COLUMNS } from '../../models/devices.models';
import { Sort, PaginatedItemCollection, SimplePaginationWithSort } from '../../models/common.models';

import { DevicesService } from '../../services/devices.service';  

@Component({
  selector: 'gn-individuals-devices-list',
  templateUrl: 'devices-list.component.html',
  styleUrls: ['devices-list.component.scss'],
  encapsulation: ViewEncapsulation.None,
})
export class DevicesListComponent implements OnInit, AfterViewInit {
  // ViewChild : To be visible dynamicaly in the parent component linked with the #dataTable reference in the child template
  // @ViewChild("dataTable") dataTable: DatatableComponent | undefined;
  public availableColumnsParams: Record<keyof Device, true> = DEVICE_COLUMNS;
  public displayedColumnsParams: Array<String> = [];
  public dataTable$: Observable<PaginatedItemCollection<Device>> = new Observable<PaginatedItemCollection<Device>>();
  public sorts: Array<Sort> = [{ prop: "id_tracking_device", dir: "asc" }];

  constructor(
    public config: ConfigService,
    // private _moduleService: ModuleService,
    // private _translate: TranslateService,
    private _devicesService: DevicesService,
    private activatedRoute: ActivatedRoute,
  ) {}

  ngOnInit() : void {
    // First initialisation of the table with the resolver data, to display something while waiting for translations to load and avoid having an empty table at the beginning
    this.activatedRoute.data.subscribe(({data}) => {
       this.dataTable$ = of(data);
    });

    // Columns initialization with prop and empty name, to be filled with translations after
    // this.availableColumns = (Object.keys(DEVICE_COLUMNS) as (keyof Device)[])
    //   .map(prop => ({ prop, name: '' }));

    // this.displayedColumns = this.availableColumns.filter(column =>
    //   this.config.INDIVIDUALS.DEVICES.DEFAULT_DISPLAYED_COLUMNS.includes(column.prop)
    // );
    this.displayedColumnsParams = this.config.INDIVIDUALS.DEVICES.DEFAULT_DISPLAYED_COLUMNS;
    
    // Build an array of translation observables for each column name
    // const translateTab$ = (Object.keys(DEVICE_COLUMNS) as (keyof Device)[])
    //   .map(
    //     // An observable is returned which emits the translation of this key
    //     prop => this._translate.get(`Individuals.AvailableFields.${prop}`)
    //   );

    // Translation with CombineLatest will wait for all translations to be loaded before updating 
    // the column names, avoiding multiple updates and ensuring all names are translated at once.
    // combineLatest(translateTab$)
    //   .subscribe(translations => {
    //     this.availableColumns = this.availableColumns.map((col, index) => ({
    //       ...col,
    //       name: translations[index]
    //     }));
        
    //     // Update displayedColumns with the translated names
    //     this.displayedColumns = this.displayedColumns.map(col =>
    //       ({ ...col, name: this.availableColumns.find(c => c.prop === col.prop)?.name || '' })
    //     );
    //   });

    // Calculate the height of the content and the number of rows to display in the table, based on the viewport height
    // this.contentHeight = this.calcContentHeight();
    // this.rowNumber = this.calcRowNumber();

    // this.dataTable$ = this._pagination$.pipe(
    //   switchMap(params => this._devicesService.getDevices(params)),
    //   shareReplay(1)
    // );
  }

  ngAfterViewInit() : void {
  }

  onPage($event: any) : void {
    let params: SimplePaginationWithSort = {
        page: Number($event.offset ?? 0) + 1,
        limit: Number($event.limit ?? this.config.INDIVIDUALS.DEVICES.DEFAULT_PAGE_SIZE),
        prop: this.sorts[0].prop,
        dir: this.sorts[0].dir,
    }; 
    this.dataTable$ = this._devicesService.getDevices(params);
  }

  onSort($event: any) : void {
    let params: SimplePaginationWithSort = {
        page: Number($event.offset ?? 0) + 1,
        limit: Number($event.limit ?? this.config.INDIVIDUALS.DEVICES.DEFAULT_PAGE_SIZE),
        prop: $event.sorts[0].prop,
        dir: $event.sorts[0].dir,
    };
    this.dataTable$ = this._devicesService.getDevices(params);
    this.sorts = $event.sorts;
  }

  onNbRowsReceived(nbRowsPerPage: number) {
    console.log('nbRows reçu:', nbRowsPerPage);
        let params: SimplePaginationWithSort = {
        page: 1,
        limit: nbRowsPerPage,
        prop: this.sorts[0].prop,
        dir: this.sorts[0].dir,
    }; 
    this.dataTable$ = this._devicesService.getDevices(params);
  } 
}


