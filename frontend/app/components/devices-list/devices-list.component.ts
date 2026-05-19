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
  public availableColumnsParams: Record<keyof Device, true> = DEVICE_COLUMNS;
  public displayedColumnsParams: Array<String> = [];
  public dataTable$: Observable<PaginatedItemCollection<Device>> = new Observable<PaginatedItemCollection<Device>>();
  public sorts: Array<Sort> = [{ prop: "id_tracking_device", dir: "asc" }];
  public idName: string = "id_tracking_device";

  private _limit: number = this.config.INDIVIDUALS.DEVICES.DEFAULT_PAGE_SIZE;

  constructor(
    public config: ConfigService,
    private _devicesService: DevicesService,
    private activatedRoute: ActivatedRoute,
  ) {}

  ngOnInit() : void {
    // First initialisation of the table with the resolver data, to display something while waiting for translations to load and avoid having an empty table at the beginning
    this.activatedRoute.data.subscribe(({data}) => {
       this.dataTable$ = of(data);
    });

    this.displayedColumnsParams = this.config.INDIVIDUALS.DEVICES.DEFAULT_DISPLAYED_COLUMNS;
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
    this._limit = params.limit;
    this.dataTable$ = this._devicesService.getDevices(params);
  }

  onSort($event: any) : void {
    let params: SimplePaginationWithSort = {
        page: Number($event.offset ?? 0) + 1,
        limit: this._limit,
        prop: $event.sorts[0].prop,
        dir: $event.sorts[0].dir,
    };
    console.log('Sorting with params :', params);
    this.dataTable$ = this._devicesService.getDevices(params);
    this.sorts = $event.sorts;
  }

  onRowSelect($event: any) : void {
    // console.log('Row selected:', $event.selected[0]["id_tracking_device"]);
    // if (row instanceof Object && row.selected.length > 0) {
    //   this.tableSelected.next(row.selected[0][this.idName]);
    // } else {
    //   this.tableSelected.next(row);
    // }
  }

  onNbRowsReceived(nbRowsPerPage: number) {
    let params: SimplePaginationWithSort = {
      page: 1,
      limit: nbRowsPerPage,
      prop: this.sorts[0].prop,
      dir: this.sorts[0].dir,
    }; 
    this._limit = nbRowsPerPage;
    this.dataTable$ = this._devicesService.getDevices(params);
  } 
}


