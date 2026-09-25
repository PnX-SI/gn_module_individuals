import { Component, OnInit, OnDestroy } from '@angular/core';
import { ActivatedRoute, Router } from '@angular/router';
import { TranslateService } from '@ngx-translate/core';
import { Subject, BehaviorSubject, Observable } from 'rxjs';
import { takeUntil, tap, filter } from 'rxjs/operators';
import { NgbModal } from '@ng-bootstrap/ng-bootstrap';

import { ConfigService } from '@geonature/services/config.service';
import { CommonService } from '@geonature_common/service/common.service';
import { ModuleService } from '@geonature/services/module.service';

import { ErrorHandlerService } from '../../../services/errors-handler.service';
import { Device, APIDeviceFiltersParams, DEVICE_MODEL } from '../../../models/devices.models';
import {
  Sort,
  PaginatedItemCollection,
  APIPaginationParams,
  AccessResult,
} from '../../../models/common.models';
import { DevicesService } from '../../../services/devices.service';
import { DEVICES_DEFAULT_SORT, DATATABLE_CONFIG } from '../../../utils/constants.util';
import { ModalComponent } from '../../modal/modal.component';

@Component({
  selector: 'gn-individuals-devices-list',
  templateUrl: 'devices-list.component.html',
  standalone: false,
})
export class DevicesListComponent implements OnInit, OnDestroy {
  public availableColumnsParams = DEVICE_MODEL;
  public displayedColumnsParams: string[] = this._config.INDIVIDUALS?.DEVICES?.LIST_COLUMNS ?? [];
  private _datatable$ = new BehaviorSubject<PaginatedItemCollection<Device> | null>(null);
  public datatable$: Observable<PaginatedItemCollection<Device>> = this._datatable$.pipe(
    filter((data): data is PaginatedItemCollection<Device> => data !== null)
  );
  private _datatable!: PaginatedItemCollection<Device>;
  public nbRowsToDisplay =
    this._config.INDIVIDUALS?.DEVICES?.DEFAULT_PAGE_SIZE ?? DATATABLE_CONFIG.PER_PAGE_OPTION;
  public fieldsTranslation = 'Individuals.Devices.Fields';
  public sorts: Array<Sort> = [DEVICES_DEFAULT_SORT];
  public allowedToEdit: Record<number, AccessResult> = {};
  public allowedToDelete: Record<number, AccessResult> = {};
  public allowedToAdd: AccessResult = { id: 0, access: false, message: null };
  public selectedRow!: Device;
  private _destroy$ = new Subject<void>();
  private _APIPaginationParams: APIPaginationParams = {
    page: 1,
    per_page: this.nbRowsToDisplay,
    prop: DEVICES_DEFAULT_SORT.prop,
    dir: DEVICES_DEFAULT_SORT.dir,
  };
  private _APIFiltersParams: APIDeviceFiltersParams = {};
  public exportFormats: string[] = this._config.INDIVIDUALS?.DEVICES?.EXPORT_FORMAT ?? [];

  constructor(
    private _config: ConfigService,
    private _devicesService: DevicesService,
    private _commonService: CommonService,
    private _module: ModuleService,
    private _activatedRoute: ActivatedRoute,
    private _router: Router,
    private _ngbModal: NgbModal,
    private _errorHandler: ErrorHandlerService,
    private _translate: TranslateService
  ) {}

  ngOnInit(): void {
    // Resolver : First initialisation of the table
    this._activatedRoute.data.pipe(takeUntil(this._destroy$)).subscribe(({ datatable }) => {
      this._datatable = datatable;
      this._datatable$.next(datatable);
    });

    // To be sure to wait translations before setting permissions
    this._translate
      .get([
        'Individuals.Individuals.Titles.Delete',
        'Individuals.Devices.Fields.provider_name',
        'Individuals.Devices.Fields.provider_device_id',
        'Individuals.ApiErrors.InsufficientPermissions',
        'Individuals.ApiErrors.HasDeployment',
      ])
      .subscribe(() => {
        this._setPermissions(this._datatable);
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
    this._router.navigate(['info', $event.id_tracking_device], {
      relativeTo: this._activatedRoute,
    });
  }

  /**
   * Perform the edit action for the given row
   *
   * @param {*} $event
   * @memberof DevicesListComponent
   */
  onEdit($event: any): void {
    this._router.navigate(['form', $event.id_tracking_device], {
      relativeTo: this._activatedRoute,
    });
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
    const modalRef = this._ngbModal.open(ModalComponent);

    modalRef.componentInstance.title = this._translate.instant(
      'Individuals.Devices.Titles.Delete',
      { id: this.selectedRow.id_tracking_device }
    );
    modalRef.componentInstance.bodyHTML = `
      ${this._translate.instant('Individuals.Devices.Fields.provider_name')} : ${this.selectedRow.provider_name}<br>
      ${this._translate.instant('Individuals.Devices.Fields.provider_device_id')} : ${this.selectedRow.provider_device_id}
    `;
    modalRef.componentInstance.validateButtonType = 'delete';
    modalRef.componentInstance.validate.subscribe((id: number) => {
      this._onDelete();
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

  /**
   * Export the devices list in the given format, with the filters and sort
   * currently applied to the list (not the pagination: the export always
   * covers the whole filtered list).
   *
   * @param {string} format
   * @memberof DevicesListComponent
   */
  onExport(format: string): void {
    this._devicesService.exportDevices(format, this._APIFiltersParams, {
      prop: this._APIPaginationParams.prop,
      dir: this._APIPaginationParams.dir,
    });
  }

  private _onDelete(): void {
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
      .subscribe((data) => this._datatable$.next(data));
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
  private _setPermissions(datatable: PaginatedItemCollection<Device>): void {
    if (datatable.items) {
      this.allowedToDelete = {};
      this.allowedToEdit = {};

      // Add access
      const currentObject = this._module.currentModule.module_objects['DEVICES'];
      this.allowedToAdd = {
        id: 0,
        access: currentObject?.cruved?.C == 0 ? false : true,
        message:
          currentObject?.cruved?.C == 0
            ? this._translate.instant('Individuals.ApiErrors.InsufficientPermissions')
            : null,
      };

      datatable.items.forEach((item: Device) => {
        // Edit access
        this.allowedToEdit[item.id_tracking_device] = {
          id: item.id_tracking_device,
          access: item.cruved?.U ?? false,
          message:
            (item.cruved?.U ?? false)
              ? null
              : this._translate.instant('Individuals.ApiErrors.InsufficientPermissions'),
        };

        // Delete access
        this.allowedToDelete[item.id_tracking_device] = {
          id: item.id_tracking_device,
          access: item.cruved?.D ?? false,
          message:
            (item.cruved?.D ?? false)
              ? null
              : this._translate.instant('Individuals.ApiErrors.InsufficientPermissions'),
        };

        // Not allowed to delete if deployments exists
        if (
          this.allowedToDelete[item.id_tracking_device].access &&
          item.last_individual_equipped_name != null
        ) {
          this.allowedToDelete[item.id_tracking_device].access = false;
          this.allowedToDelete[item.id_tracking_device].message = this._translate.instant(
            'Individuals.ApiErrors.HasDeployment'
          );
        }
      });
    }
  }
}
