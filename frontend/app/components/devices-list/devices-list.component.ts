import { ViewEncapsulation, Component, OnInit, AfterViewInit } from '@angular/core';
import { ActivatedRoute } from '@angular/router';

import { Observable, of } from 'rxjs';

import { ConfigService } from '@geonature/services/config.service';

import { Device, DEVICE_COLUMNS } from '../../models/devices.models';
import { Sort, PaginatedItemCollection, APIParamsPagination } from '../../models/common.models';

import { DevicesService } from '../../services/devices.service';  
import { DEVICES_DEFAULT_SORT } from '../../utils/constants.util';

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
  public sorts: Array<Sort> = [DEVICES_DEFAULT_SORT];
  public idName: string = "id_tracking_device";

  private _per_page: number = this.config.INDIVIDUALS.DEVICES.DEFAULT_PAGE_SIZE;

  constructor(
    public config: ConfigService,
    private _devicesService: DevicesService,
    private _activatedRoute: ActivatedRoute,
  ) {}

  ngOnInit() : void {
    // First initialisation of the table with the resolver data, to display something while waiting for translations to load and avoid having an empty table at the beginning
    this._activatedRoute.data.subscribe(({data}) => {
       this.dataTable$ = of(data);
    });

    this.displayedColumnsParams = this.config.INDIVIDUALS.DEVICES.DEFAULT_DISPLAYED_COLUMNS;
  }

  ngAfterViewInit() : void {}

  onPage($event: any) : void {
    let params: APIParamsPagination = {
        page: Number($event.offset ?? 0) + 1,
        per_page: Number($event.limit ?? this.config.INDIVIDUALS.DEVICES.DEFAULT_PAGE_SIZE),
        prop: this.sorts[0].prop,
        dir: this.sorts[0].dir,
    };
    this._per_page = params.per_page;
    this.dataTable$ = this._devicesService.getDevices(params);
  }

  onSort($event: any) : void {
    let params: APIParamsPagination = {
        page: Number($event.offset ?? 0) + 1,
        per_page: this._per_page,
        prop: $event.sorts[0].prop,
        dir: $event.sorts[0].dir,
    };

    this.dataTable$ = this._devicesService.getDevices(params);
    this.sorts = $event.sorts;
  }

  onNbRowsReceived(nbRowsPerPage: number) {
    let params: APIParamsPagination = {
      page: 1,
      per_page: nbRowsPerPage,
      prop: this.sorts[0].prop,
      dir: this.sorts[0].dir,
    }; 
    this._per_page = nbRowsPerPage;
    this.dataTable$ = this._devicesService.getDevices(params);
  } 
}


