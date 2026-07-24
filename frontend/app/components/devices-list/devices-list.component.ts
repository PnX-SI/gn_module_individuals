import { Component, OnInit, OnDestroy } from '@angular/core';
import { ActivatedRoute } from '@angular/router';
import { TranslateService } from '@ngx-translate/core';
import { Subject, Observable, of } from 'rxjs';
import { takeUntil, tap } from 'rxjs/operators';
import { NgbModal } from '@ng-bootstrap/ng-bootstrap';

import { ConfigService } from '@geonature/services/config.service';
import { CommonService } from '@geonature_common/service/common.service';

import { ErrorHandlerService } from '../../services/errors-handler.service';
import { Device, APIDeviceFiltersParams, DEVICE_MODEL } from '../../models/devices.models';
import { Sort, PaginatedItemCollection, APIPaginationParams } from '../../models/common.models';
import { DevicesService } from '../../services/devices.service';
import { DEVICES_DEFAULT_SORT, DATATABLE_CONFIG } from '../../utils/constants.util';
import { DeleteModalComponent } from '../delete-modal/delete-modal.component';

@Component({
  selector: 'gn-individuals-devices-list',
  templateUrl: 'devices-list.component.html',
  standalone: false,
})
export class DevicesListComponent implements OnInit, OnDestroy {
  public availableColumnsParams = DEVICE_MODEL;
  public displayedColumnsParams: string[] = this._config.INDIVIDUALS?.DEVICES?.LIST_COLUMNS ?? [];
  public dataTable$: Observable<PaginatedItemCollection<Device>> = new Observable<
    PaginatedItemCollection<Device>
  >();
  public nbRowsToDisplay = this._config.INDIVIDUALS?.DEVICES?.DEFAULT_PAGE_SIZE ?? DATATABLE_CONFIG.PER_PAGE_OPTION;
  public fieldsTranslation = "Individuals.Devices.Fields";
  public sorts: Array<Sort> = [DEVICES_DEFAULT_SORT];
  public allowedToEdit: boolean[] = [];
  public allowedToDelete: Record<number, boolean> = {};
  public selectedRow!: Device;
  private _destroy$ = new Subject<void>();
  private _APIPaginationParams: APIPaginationParams = {
    page: 1,
    per_page: this.nbRowsToDisplay,
    prop: DEVICES_DEFAULT_SORT.prop,
    dir: DEVICES_DEFAULT_SORT.dir,
  };
  private _APIFiltersParams: APIDeviceFiltersParams = {};

  constructor(
    private _config: ConfigService,
    private _devicesService: DevicesService,
    private _commonService: CommonService,
    private _activatedRoute: ActivatedRoute,
    private _ngbModal: NgbModal,
    private _errorHandler: ErrorHandlerService,
    private _translate: TranslateService
  ) {
  }

  ngOnInit(): void {
    // Resolver : First initialisation of the table
    this._activatedRoute.data.pipe(takeUntil(this._destroy$)).subscribe(({ datatable }) => {
      this.dataTable$ = of(datatable);
      this._initPermissions(datatable);
    });     
  }

  ngOnDestroy() {
    this._destroy$.next();
    this._destroy$.complete();
  }

  onPage($event: any): void {
    this._APIPaginationParams = {
      page: Number($event.offset ?? 0) + 1,
      per_page: Number($event.limit),
      prop: this.sorts[0].prop,
      dir: this.sorts[0].dir,
    };
    this._loadData();
  }

  onSort($event: any): void {
    this._APIPaginationParams = {
      page: 1,
      per_page: this.nbRowsToDisplay,
      prop: $event.sorts[0].prop,
      dir: $event.sorts[0].dir,
    };
    this.sorts = $event.sorts;

    this._loadData();
  }

  /**
   * Open the delete modal
   *
   * @param {*} $event Current row
   * @param {TemplateRef<any>} template Delete modal Template reference
   * @memberof DevicesListComponent
   */
  openDeleteModal($event: any) {
    this.selectedRow = $event;
    const modalRef = this._ngbModal.open(DeleteModalComponent);

    modalRef.componentInstance.title = this._translate.instant(
      'Individuals.Devices.Titles.Delete',
      { id: this.selectedRow.id_tracking_device }
    );

    modalRef.componentInstance.body = `
      ${this._translate.instant('Individuals.Devices.Fields.provider_name')} : ${this.selectedRow.provider_name}<br>
      ${this._translate.instant('Individuals.Devices.Fields.provider_device_id')} : ${this.selectedRow.provider_device_id}
    `;

    modalRef.componentInstance.confirm.subscribe((id: number) => {
      this.onDelete();
    });
  }

  onFilters($event: {key: keyof APIDeviceFiltersParams; value: string | number | undefined;} | null): void {
    if (!$event) {
      this._APIFiltersParams = {};
    } else {
      if ($event.value != null) {
        this._APIFiltersParams[$event.key] = $event.value;
        this._APIPaginationParams['page'] = 1;
      }
    }
    this._loadData();
  }

  onDelete(): void {
    if (this.selectedRow) {
      const selectedId = this.selectedRow.id_tracking_device;
      this._devicesService.deleteDevice(selectedId).subscribe({
        next: (res) => {
          this._commonService.translateToaster('info', 'Individuals.Devices.Messages.Deleted', {
            id: selectedId,
          });
          this._loadData();
        },
        error: (err) => {
          this._errorHandler.handleHttpError(
            err,
            { id: selectedId },
            'Individuals.Devices.ApiErrors'
          );
        },
      });
    }
  }

  private _loadData(): void {
    const APIParams = {
      ...this._APIPaginationParams,
      ...this._APIFiltersParams,
    };
    this.dataTable$ = this._devicesService
      .getDevices(APIParams)
      .pipe(tap((data) => this._initPermissions(data)));
  }

  private _initPermissions(data: PaginatedItemCollection<Device>): void {
    this.allowedToDelete = [];

    // Not allowed to delete if deployments exists
    // Have to be changed with scope and cruved
    if (data.items) {
      data.items.forEach((item: Device) => {
        this.allowedToDelete[item.id_tracking_device] = item.last_individual_equipped_name == null;
      });

      // Have to be changed with scope and cruved
      this.allowedToEdit = data.items.map(() => true);
    }
  }
}
