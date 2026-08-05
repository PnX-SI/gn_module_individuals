import { Component, OnInit, OnDestroy } from '@angular/core';
import { ActivatedRoute } from '@angular/router';
import { TranslateService } from '@ngx-translate/core';
import { Subject, BehaviorSubject, Observable, of } from 'rxjs';
import { takeUntil, tap, filter } from 'rxjs/operators';
import { NgbModal } from '@ng-bootstrap/ng-bootstrap';

import { ConfigService } from '@geonature/services/config.service';
import { CommonService } from '@geonature_common/service/common.service';

import { ErrorHandlerService } from '../../services/errors-handler.service';
import {
  Individual,
  INDIVIDUAL_MODEL,
  APIIndividualFiltersParams,
} from '../../models/individuals.models';
import {
  Sort,
  PaginatedItemCollection,
  APIPaginationParams,
  FeatureCollection,
  AccessResult,
} from '../../models/common.models';
import { IndividualsService } from '../../services/individuals.service';
import { INDIVIDUALS_DEFAULT_SORT, DATATABLE_CONFIG } from '../../utils/constants.util';
import { DeleteModalComponent } from '../delete-modal/delete-modal.component';

@Component({
  selector: 'gn-individuals-individuals-map-list',
  templateUrl: 'individuals-map-list.component.html',
  standalone: false,
})
export class IndividualsMapListComponent implements OnInit, OnDestroy {
  public availableColumnsParams = INDIVIDUAL_MODEL;
  public displayedColumnsParams: string[] =
    this._config.INDIVIDUALS?.INDIVIDUALS?.LIST_COLUMNS ?? [];
  private _datatable$ = new BehaviorSubject<PaginatedItemCollection<Individual> | null>(null);
  public datatable$: Observable<PaginatedItemCollection<Individual>> = this._datatable$.pipe(
    filter((data): data is PaginatedItemCollection<Individual> => data !== null)
  );
  public nbRowsToDisplay =
    this._config.INDIVIDUALS?.INDIVIDUALS?.DEFAULT_PAGE_SIZE ?? DATATABLE_CONFIG.PER_PAGE_OPTION;
  public fieldsTranslation = 'Individuals.Individuals.Fields';
  public sorts: Array<Sort> = [INDIVIDUALS_DEFAULT_SORT];
  public allowedToEdit: Record<number, AccessResult> = {};
  public allowedToDelete: Record<number, AccessResult> = {};
  public selectedRows: Individual[] = [];
  public mapData$: Observable<FeatureCollection<Individual>> = new Observable<
    FeatureCollection<Individual>
  >();
  public defaultFilters: APIIndividualFiltersParams = {};
  private _destroy$ = new Subject<void>();
  private _APIPaginationParams: APIPaginationParams = {
    page: 1,
    per_page: this.nbRowsToDisplay,
    prop: INDIVIDUALS_DEFAULT_SORT.prop,
    dir: INDIVIDUALS_DEFAULT_SORT.dir,
  };
  private _APIFiltersParams: APIIndividualFiltersParams = { active: 'true' };
  private _selectedId: number | null = null;

  constructor(
    private _config: ConfigService,
    private _individualsService: IndividualsService,
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
        this._datatable$.next(datatable);
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
   * @memberof IndividualsMapListComponent
   */
  public onBbox($event: string): void {
    // this._APIFiltersParams = {
    //   bbox: $event
    // }
    this._loadData();
  }

  /**
   * Open the delete modal with Individual properties
   *
   * @param {Individual} $event The selected Individual to delete
   * @memberof IndividualsMapListComponent
   */
  public openDeleteModal($event: Individual) {
    this.selectedRows = [$event];
    const modalRef = this._ngbModal.open(DeleteModalComponent);

    modalRef.componentInstance.title = this._translate.instant(
      'Individuals.Individuals.Titles.Delete',
      { id: this.selectedRows[0].id_individual }
    );

    modalRef.componentInstance.body = `
        ${this._translate.instant('Individuals.Individuals.Fields.individual_name')} : ${this.selectedRows[0].individual_name}<br>
        ${this._translate.instant('Individuals.Individuals.Fields.taxref_nom_vern')} : ${this.selectedRows[0].taxref_nom_vern}<br>
        ${this._translate.instant('Individuals.Individuals.Fields.nomenclature_sex_name')} : ${this.selectedRows[0].nomenclature_sex_name}<br>
      `;

    modalRef.componentInstance.confirm.subscribe((id: number) => {
      this._onDelete();
    });
  }

  /**
   * Call API with given filter value
   *
   * @param {({key: keyof APIIndividualFiltersParams; value: any;} | null)} $event Filter value {key, value} or null to reset filters
   * @memberof IndividualsMapListComponent
   */
  public onFilters($event: { key: keyof APIIndividualFiltersParams; value: any } | null): void {
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
      const selectedId = this.selectedRows[0].id_individual;
      this._individualsService.deleteIndividual(selectedId).subscribe({
        next: (res) => {
          this._commonService.translateToaster('info', 'Individuals.Individuals.Messages.Deleted', {
            id: selectedId,
          });
          this._loadData();
        },
        error: (err) => {
          this._errorHandler.handleHttpError(
            err,
            { id: selectedId },
            'Individuals.Individuals.ApiErrors'
          );
        },
      });
    }
  }

  /**
   * API call to get the page corresponding to the given id and reload data with this page.
   * Used when a map feature is clicked and want to display the corresponding row in the paginated table.
   *
   * @param {*} $event
   * @memberof IndividualsMapListComponent
   */
  public onIdPage($event: any): void {
    this._selectedId = $event;
    const APIParams = {
      ...this._APIPaginationParams,
      ...this._APIFiltersParams,
    };

    if ($event) {
      const IdRankAndPage$ = this._individualsService.getIndividualRankAndPage($event, APIParams);

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
    this._individualsService
      .getIndividuals(APIParams)
      .pipe(
        tap((data) => {
          if (this._selectedId !== null) {
            const selected = data.items.find((item) => item.id_individual === this._selectedId);
            this.selectedRows = selected ? [selected] : [];
          } else {
            this.selectedRows = [];
          }
          this._setPermissions(data);
        }),
        takeUntil(this._destroy$)
      )
      .subscribe((data) => this._datatable$.next(data));
  }

  /**
   * Set the allowToDelete and allowToEdit variables considering the item cruved.
   * Else, for each item id, if a deployment or observation exists
   * set the corresponding array entry to false, else to true
   *
   * @private
   * @param {PaginatedItemCollection<Individual>} data
   * @memberof IndividualsMapListComponent
   */
  private _setPermissions(data: PaginatedItemCollection<Individual>): void {
    if (data.items) {
      data.items.forEach((item: Individual) => {
        // Delete access
        let deleteAccess: AccessResult = { id: item.id_individual, access: true };
        console.log(item.id_individual, ' ', item.cruved);
        deleteAccess.access = item.cruved?.D ?? false;
        deleteAccess.message = deleteAccess.access
          ? null
          : this._translate.instant('Individuals.ApiErrors.InsufficientPermissions');

        if (deleteAccess.access) {
          // Not allowed to delete if deployments exists
          if (item.last_observation_date) {
            deleteAccess.access = false;
            deleteAccess.message = this._translate.instant('Individuals.ApiErrors.HasObservation');
          }
          // Not Allowed to delete if observations exists
          else if (
            Object.keys(item.deployed_devices).length > 0 ||
            Object.keys(item.deployed_markings).length > 0
          ) {
            deleteAccess.access = false;
            deleteAccess.message = this._translate.instant('Individuals.ApiErrors.HasDeployment');
          }
        }

        // Edit access
        let editAccess: AccessResult = { id: item.id_individual, access: true };

        editAccess.access = item.cruved?.D ?? false;
        editAccess.message = editAccess.access
          ? null
          : this._translate.instant('Individuals.ApiErrors.InsufficientPermissions');

        this.allowedToDelete[item.id_individual] = deleteAccess;
        this.allowedToEdit[item.id_individual] = editAccess;
      });
    }
  }
}
