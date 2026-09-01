import { Component, OnInit, OnDestroy } from '@angular/core';
import { ActivatedRoute, Router } from '@angular/router';
import { TranslateService } from '@ngx-translate/core';
import { Subject, BehaviorSubject, Observable } from 'rxjs';
import { takeUntil, tap, filter } from 'rxjs/operators';
import { NgbModal } from '@ng-bootstrap/ng-bootstrap';

import { ConfigService } from '@geonature/services/config.service';
import { CommonService } from '@geonature_common/service/common.service';

import { ErrorHandlerService } from '../../services/errors-handler.service';
import { Device, APIDeviceFiltersParams, DEVICE_MODEL } from '../../models/devices.models';
import {
  Sort,
  PaginatedItemCollection,
  APIPaginationParams,
  AccessResult,
} from '../../models/common.models';
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
  private _dataTable$ = new BehaviorSubject<PaginatedItemCollection<Device> | null>(null);
  public dataTable$: Observable<PaginatedItemCollection<Device>> = this._dataTable$.pipe(
    filter((data): data is PaginatedItemCollection<Device> => data !== null)
  );
  public nbRowsToDisplay =
    this._config.INDIVIDUALS?.DEVICES?.DEFAULT_PAGE_SIZE ?? DATATABLE_CONFIG.PER_PAGE_OPTION;
  public fieldsTranslation = 'Individuals.Devices.Fields';
  public sorts: Array<Sort> = [DEVICES_DEFAULT_SORT];
  public allowedToEdit: Record<number, AccessResult> = {};
  public allowedToDelete: Record<number, AccessResult> = {};
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
    private _router: Router,
    private _ngbModal: NgbModal,
    private _errorHandler: ErrorHandlerService,
    private _translate: TranslateService
  ) {}

  ngOnInit(): void {
    // Resolver : First initialisation of the table
    this._activatedRoute.data.pipe(takeUntil(this._destroy$)).subscribe(({ datatable }) => {
      this._dataTable$.next(datatable);
      this._setPermissions(datatable);
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
   * Perform the add action
   *
   * @memberof DevicesListComponent
   */
  onAdd(): void {
    this._router.navigate(['form'], { relativeTo: this._activatedRoute });
  }

  /**
   * Perform the info action for the given row
   *
   * @param {*} $event
   * @memberof DevicesListComponent
   */
  onInfo($event: any): void {
    this._router.navigate(['info', $event.id_tracking_device], { relativeTo: this._activatedRoute });
  }

  /**
   * Perform the edit action for the given row
   *
   * @param {*} $event
   * @memberof DevicesListComponent
   */
  onEdit($event: any): void {
    this._router.navigate(['form', $event.id_tracking_device], { relativeTo: this._activatedRoute });
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

  onFilters(
    $event: { key: keyof APIDeviceFiltersParams; value: string | number | undefined } | null
  ): void {
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
    this._devicesService
      .getDevices(APIParams)
      .pipe(
        tap((data) => this._setPermissions(data)),
        takeUntil(this._destroy$)
      )
      .subscribe((data) => this._dataTable$.next(data));
  }

  /**
   * Set the allowToDelete and allowToEdit variables considering the item cruved.
   * Else, for each item id, if a deployment exists
   * set the corresponding array entry to false, else to true
   *
   * @private
   * @param {PaginatedItemCollection<Device>} data
   * @memberof DevicesListComponent
   */
  private _setPermissions(data: PaginatedItemCollection<Device>): void {
    if (data.items) {
      data.items.forEach((item: Device) => {
        // Delete access
        let deleteAccess: AccessResult = { id: item.id_tracking_device, access: true };

        deleteAccess.access = item.cruved?.D ?? false;
        deleteAccess.message = deleteAccess.access
          ? null
          : this._translate.instant('Individuals.ApiErrors.InsufficientPermissions');

        if (deleteAccess.access) {
          // Not allowed to delete if deployments exists
          deleteAccess.access = item.last_individual_equipped_name == null;
          deleteAccess.message = deleteAccess.access
            ? null
            : this._translate.instant('Individuals.ApiErrors.HasDeployment');
        }

        // Edit access
        let editAccess: AccessResult = { id: item.id_tracking_device, access: true };

        editAccess.access = item.cruved?.U ?? false;
        editAccess.message = editAccess.access
          ? null
          : this._translate.instant('Individuals.ApiErrors.InsufficientPermissions');

        this.allowedToDelete[item.id_tracking_device] = deleteAccess;
        this.allowedToEdit[item.id_tracking_device] = editAccess;
      });
    }
  }
}
