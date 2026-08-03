import { Component, OnInit, OnDestroy } from '@angular/core';
import { ActivatedRoute } from '@angular/router';
import { TranslateService } from '@ngx-translate/core';
import { Subject, Observable, of } from 'rxjs';
import { takeUntil, tap } from 'rxjs/operators';
import { NgbModal } from '@ng-bootstrap/ng-bootstrap';

import { ConfigService } from '@geonature/services/config.service';
import { CommonService } from '@geonature_common/service/common.service';

import { ErrorHandlerService } from '../../../services/errors-handler.service';
import { Capture, CAPTURE_MODEL, APICaptureFiltersParams } from '../../../models/capture.model';
import {
  Sort,
  PaginatedItemCollection,
  APIPaginationParams,
  FeatureCollection,
  AccessResult,
} from '../../../models/common.models';
import { CaptureService } from '../../../services/capture.service';
import { CAPTURES_DEFAULT_SORT, DATATABLE_CONFIG } from '../../../utils/constants.util';
import { DeleteModalComponent } from '../../delete-modal/delete-modal.component';

@Component({
  selector: 'gn-individuals-capture-list',
  templateUrl: 'capture-list.component.html',
  styleUrls: ['capture-list.component.scss'],
  standalone: false,
})
export class CaptureListComponent implements OnInit, OnDestroy {
  public availableColumnsParams = CAPTURE_MODEL;
  public displayedColumnsParams: string[] = this._config.INDIVIDUALS?.CAPTURES?.LIST_COLUMNS ?? [];
  public datatable$: Observable<PaginatedItemCollection<Capture>> = new Observable<
    PaginatedItemCollection<Capture>
  >();
  public nbRowsToDisplay =
    this._config.INDIVIDUALS?.CAPTURES?.DEFAULT_PAGE_SIZE ?? DATATABLE_CONFIG.PER_PAGE_OPTION;
  public fieldsTranslation = 'Individuals.Captures.Fields';
  public sorts: Array<Sort> = [CAPTURES_DEFAULT_SORT];
  public allowedToEdit: Record<number, AccessResult> = {};
  public allowedToDelete: Record<number, AccessResult> = {};
  public selectedRows: Capture[] = [];
  public mapData$: Observable<FeatureCollection<Capture>> = new Observable<
    FeatureCollection<Capture>
  >();
  public defaultFilters: APICaptureFiltersParams = {};
  private _destroy$ = new Subject<void>();
  private _APIPaginationParams: APIPaginationParams = {
    page: 1,
    per_page: this.nbRowsToDisplay,
    prop: CAPTURES_DEFAULT_SORT.prop,
    dir: CAPTURES_DEFAULT_SORT.dir,
  };
  private _APIFiltersParams: APICaptureFiltersParams = {};
  private _selectedId: number | null = null;

  constructor(
    private _config: ConfigService,
    private _captureService: CaptureService,
    private _commonService: CommonService,
    private _activatedRoute: ActivatedRoute,
    private _ngbModal: NgbModal,
    private _errorHandler: ErrorHandlerService,
    private _translate: TranslateService
  ) {}

  ngOnInit(): void {
    // Resolver : First initialisation of the table
    this._activatedRoute.data
      .pipe(takeUntil(this._destroy$))
      .subscribe(({ datatable, mapData }) => {
        this.datatable$ = of(datatable);
        this.mapData$ = of(mapData);
        this._setPermissions(datatable);
      });

    this.defaultFilters = this._APIFiltersParams;
  }

  ngOnDestroy(): void {
    this._destroy$.next();
    this._destroy$.complete();
  }

  public onPage($event: any): void {
    this._APIPaginationParams = {
      page: Number($event.offset ?? 0) + 1,
      per_page: Number($event.limit),
      prop: this.sorts[0].prop,
      dir: this.sorts[0].dir,
    };
    this._loadData();
  }

  public onSort($event: any): void {
    this._APIPaginationParams = {
      page: Number($event.offset ?? 0) + 1,
      per_page: this.nbRowsToDisplay,
      prop: $event.sorts[0].prop,
      dir: $event.sorts[0].dir,
    };
    this.sorts = $event.sorts;

    this._loadData();
  }

  /**
   * Call API with the new bbox parametter
   *
   * @param {string} $event Current bbox
   * @memberof CaptureListComponent
   */
  public onBbox($event: string): void {
    // this._APIFiltersParams = {
    //   bbox: $event
    // }
    this._loadData();
  }

  /**
   * Open the delete modal with Capture properties
   *
   * @param {Capture} $event The selected Capture to delete
   * @memberof CaptureListComponent
   */
  public openDeleteModal($event: Capture) {
    this.selectedRows = [$event];
    const modalRef = this._ngbModal.open(DeleteModalComponent);

    modalRef.componentInstance.title = this._translate.instant(
      'Individuals.Captures.Titles.Delete',
      { id: this.selectedRows[0].id_capture }
    );

    modalRef.componentInstance.body = `
        ${this._translate.instant('Individuals.Captures.Fields.date')} : ${this.selectedRows[0].date}<br>
        ${this._translate.instant('Individuals.Captures.Fields.comment')} : ${this.selectedRows[0].comment}<br>
      `;

    modalRef.componentInstance.confirm.subscribe((id: number) => {
      this._onDelete();
    });
  }

  /**
   * Call API with given filter value
   *
   * @param {({key: keyof APICaptureFiltersParams; value: any;} | null)} $event Filter value {key, value} or null to reset filters
   * @memberof CaptureListComponent
   */
  public onFilters($event: { key: keyof APICaptureFiltersParams; value: any } | null): void {
    if (!$event) {
      this._APIFiltersParams = {};
    } else {
      this._APIFiltersParams[$event.key] = $event.value;
      this._APIPaginationParams['page'] = 1;
    }
    this._loadData();
  }

  private _onDelete(): void {
    if (this.selectedRows.length > 0) {
      const selectedId = this.selectedRows[0].id_capture;
      this._captureService.deleteCapture(selectedId).subscribe({
        next: (res) => {
          this._commonService.translateToaster('info', 'Individuals.Captures.Messages.Deleted', {
            id: selectedId,
          });
          this._loadData();
        },
        error: (err) => {
          this._errorHandler.handleHttpError(err, { id: selectedId }, 'Individuals.Captures.ApiErrors');
        },
      });
    }
  }

  /**
   * API call to get the page corresponding to the given id and reload data with this page.
   * Used when a map feature is clicked and want to display the corresponding row in the paginated table.
   *
   * @param {*} $event
   * @memberof CaptureListComponent
   */
  public onIdPage($event: any): void {
    this._selectedId = $event;
    const APIParams = {
      ...this._APIPaginationParams,
      ...this._APIFiltersParams,
    };

    if ($event) {
      const IdRankAndPage$ = this._captureService.getCaptureRankAndPage($event, APIParams);

      IdRankAndPage$.subscribe((rankAndPage) => {
        this._APIPaginationParams.page = rankAndPage.page;
        this._loadData();
      });
    }
  }

  private _loadData(): void {
    const APIParams = {
      ...this._APIPaginationParams,
      ...this._APIFiltersParams,
    };
    this.datatable$ = this._captureService.getCaptures(APIParams).pipe(
      tap((data) => {
        if (this._selectedId !== null) {
          const selected = data.items.find((item) => item.id_capture === this._selectedId);
          this.selectedRows = selected ? [selected] : [];
        } else {
          this.selectedRows = [];
        }
        this._setPermissions(data);
      })
    );
  }

  /**
   * Set the allowToDelete and allowToEdit variables.
   * Capture doesn't carry cruved information, so access is granted by default.
   *
   * @private
   * @param {PaginatedItemCollection<Capture>} data
   * @memberof CaptureListComponent
   */
  private _setPermissions(data: PaginatedItemCollection<Capture>): void {
    if (data.items) {
      data.items.forEach((item: Capture) => {
        this.allowedToDelete[item.id_capture] = { id: item.id_capture, access: true };
        this.allowedToEdit[item.id_capture] = { id: item.id_capture, access: true };
      });
    }
  }
}
