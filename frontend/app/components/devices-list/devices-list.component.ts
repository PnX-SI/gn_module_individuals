import { ViewEncapsulation, Component, OnInit, OnDestroy, TemplateRef } from '@angular/core';
import { ActivatedRoute } from '@angular/router';

import { Subject, Observable, of } from 'rxjs';
import { takeUntil, tap } from 'rxjs/operators';
import { NgbModal } from '@ng-bootstrap/ng-bootstrap';

import { ConfigService } from '@geonature/services/config.service';
import { CommonService } from '@geonature_common/service/common.service';

import { ErrorHandlerService } from 'app/services/errors-handler.service';
import { Device, DEVICE_COLUMNS } from 'app/models/devices.models';
import { Sort, PaginatedItemCollection, APIParamsPagination } from 'app/models/common.models';
import { DevicesService } from 'app/services/devices.service';
import { DEVICES_DEFAULT_SORT, DATA_TABLE_CONFIG } from 'app/utils/constants.util';

@Component({
  selector: 'gn-individuals-devices-list',
  templateUrl: 'devices-list.component.html',
  styleUrls: ['devices-list.component.scss'],
  encapsulation: ViewEncapsulation.None,
})
export class DevicesListComponent implements OnInit, OnDestroy {
  public availableColumnsParams: Record<keyof Device, true> = DEVICE_COLUMNS;
  public displayedColumnsParams: string[] = [];
  public dataTable$: Observable<PaginatedItemCollection<Device>> = new Observable<
    PaginatedItemCollection<Device>
  >();
  public sorts: Array<Sort> = [DEVICES_DEFAULT_SORT];
  public allowedToEdit: boolean[] = [];
  public allowedToDelete: Record<number, boolean> = {};
  public selectedId!: number;
  // private _per_page: number = DATA_TABLE_CONFIG.PER_PAGE_OPTION;
  private _destroy$ = new Subject<void>();
  private _APIparams!: APIParamsPagination;

  constructor(
    private _config: ConfigService,
    private _devicesService: DevicesService,
    private _commonService: CommonService,
    private _activatedRoute: ActivatedRoute,
    private _ngbModal: NgbModal,
    private _errorHandler: ErrorHandlerService
  ) {}

  ngOnInit(): void {
    // Resolver : First initialisation of the table
    this._activatedRoute.data.pipe(takeUntil(this._destroy$)).subscribe(({ data }) => {
      this.dataTable$ = of(data);
      this._initPermissions(data);
    });

    this.displayedColumnsParams =
      this._config.INDIVIDUALS?.DEVICES?.DEFAULT_DISPLAYED_COLUMNS ?? [];
  }

  ngOnDestroy() {
    this._destroy$.next();
    this._destroy$.complete();
  }

  onPage($event: any): void {
    this._APIparams = {
      page: Number($event.offset ?? 0) + 1,
      per_page: Number($event.limit ?? this._config.INDIVIDUALS.DEVICES.DEFAULT_PAGE_SIZE),
      prop: this.sorts[0].prop,
      dir: this.sorts[0].dir,
    };
    this._loadData();
  }

  onSort($event: any): void {
    this._APIparams = {
      page: Number($event.offset ?? 0) + 1,
      per_page: DATA_TABLE_CONFIG.PER_PAGE_OPTION,
      prop: $event.sorts[0].prop,
      dir: $event.sorts[0].dir,
    };
    this.sorts = $event.sorts;

    this._loadData();
  }

  onDelete($event: any, template: TemplateRef<any>) {
    this.selectedId = $event;
    this._ngbModal.open(template);
  }

  confirmDelete() {
    if (this.selectedId) {
      this._devicesService.deleteDevice(this.selectedId).subscribe({
        next: (res) => {
          this._commonService.translateToaster('info', 'Individuals.Devices.Messages.Deleted', {
            id: this.selectedId,
          });
          this._loadData();
        },
        error: (err) => {
          this._errorHandler.handleHttpError(
            err,
            { id: this.selectedId },
            'Individuals.Devices.ApiErrors'
          );
        },
      });
    }
  }

  private _initPermissions(data: PaginatedItemCollection<Device>): void {
    this.allowedToDelete = [];

    // Not allowed to delete if deployments exists
    // Have to be changed with scope and cruved
    data.items.forEach((item: Device) => {
      this.allowedToDelete[item.id_tracking_device] = item.last_individual_equipped_name == null;
    });

    // Have to be changed with scope and cruved
    this.allowedToEdit = data.items.map(() => true);
  }

  private _loadData(): void {
    this.dataTable$ = this._devicesService
      .getDevices(this._APIparams)
      .pipe(tap((data) => this._initPermissions(data)));
  }
}
