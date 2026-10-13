import { Component, OnInit, OnDestroy } from '@angular/core';
import { ActivatedRoute, Router } from '@angular/router';
import { TranslateService } from '@ngx-translate/core';
import { Subject, BehaviorSubject, Observable, of } from 'rxjs';
import { takeUntil, tap, filter } from 'rxjs/operators';
import { NgbModal } from '@ng-bootstrap/ng-bootstrap';

import { ConfigService } from '@geonature/services/config.service';
import { CommonService } from '@geonature_common/service/common.service';
import { ModuleService } from '@geonature/services/module.service';

import { ErrorHandlerService } from '../../../services/errors-handler.service';
import {
  Individual,
  INDIVIDUAL_MODEL,
  APIIndividualFiltersParams,
} from '../../../models/individuals.models';
import {
  APISortParams,
  PaginatedItemCollection,
  APIPaginationParams,
  FeatureCollection,
  AccessResult,
} from '../../../models/common.models';
import { IndividualsService } from '../../../services/individuals.service';
import { INDIVIDUALS_DEFAULT_SORT, DATATABLE_CONFIG } from '../../../utils/constants.util';

import { ModalComponent } from '../../modal/modal.component';

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
  private _datatable!: PaginatedItemCollection<Individual>;
  public nbRowsToDisplay =
    this._config.INDIVIDUALS?.INDIVIDUALS?.DEFAULT_PAGE_SIZE ?? DATATABLE_CONFIG.PER_PAGE_OPTION;
  public allowedToAdd: AccessResult = { id: 0, access: false, message: null };
  public allowedToEdit: Record<number, AccessResult> = {};
  public allowedToDelete: Record<number, AccessResult> = {};
  public selectedRows: Individual[] = [];
  private _mapData$ = new BehaviorSubject<FeatureCollection<Individual> | null>(null);
  public mapData$: Observable<FeatureCollection<Individual>> = this._mapData$.pipe(
    filter((data): data is FeatureCollection<Individual> => data !== null)
  );
  public defaultFilters: APIIndividualFiltersParams = {};
  public exportFormats: string[] = this._config.INDIVIDUALS?.INDIVIDUALS?.EXPORT_FORMAT ?? [];
  private _destroy$ = new Subject<void>();
  private _APIPaginationParams: APIPaginationParams = {
    page: 1,
    per_page: this.nbRowsToDisplay,
  };
  public APISortParams: APISortParams = INDIVIDUALS_DEFAULT_SORT;
  private _APIFiltersParams: APIIndividualFiltersParams = { active: 'true' };
  private _selectedId: number | null = null;

  constructor(
    private _config: ConfigService,
    private _individualsService: IndividualsService,
    private _commonService: CommonService,
    private _module: ModuleService,
    private _activatedRoute: ActivatedRoute,
    private _router: Router,
    private _ngbModal: NgbModal,
    private _errorHandler: ErrorHandlerService,
    private _translate: TranslateService
  ) {}

  ngOnInit(): void {
    this._loadData();

    // To be sure to wait translations before setting permissions
    this._translate
      .get([
        'Individuals.Individuals.Titles.Delete',
        'Individuals.Individuals.Fields.individual_name',
        'Individuals.Individuals.Fields.taxref_nom_vern',
        'Individuals.Individuals.Fields.nomenclature_sex_name',
        'Individuals.ApiErrors.InsufficientPermissions',
        'Individuals.ApiErrors.HasObservation',
        'Individuals.ApiErrors.HasDeployment',
      ])
      .subscribe(() => {
        this._setPermissions();
      });

    this.defaultFilters = this._APIFiltersParams;
  }

  ngOnDestroy(): void {
    this._destroy$.next();
    this._destroy$.complete();
    this._mapData$.complete();
  }

  onPage($event: any): void {
    this._APIPaginationParams = {
      page: Number($event.offset ?? 0) + 1,
      per_page: Number($event.limit),
    };

    this._loadData();
  }

  onSort($event: any): void {
    this._APIPaginationParams = {
      page: Number($event.offset ?? 0) + 1,
      per_page: this.nbRowsToDisplay,
    };
    this.APISortParams = {
      prop: $event.sorts[0].prop,
      dir: $event.sorts[0].dir,
    };

    this._loadData();
  }

  /**
   * Call API with the new bbox parametter
   *
   * @param {string} $event Current bbox
   * @memberof IndividualsMapListComponent
   */
  onBbox($event: string): void {
    this._APIFiltersParams = {
      ...this._APIFiltersParams,
      bbox: $event,
    };
    this._loadData();
  }

  /**
   * Perform the add action
   *
   * @memberof IndividualsMapListComponent
   */
  onAdd(): void {
    this._router.navigate(['form'], { relativeTo: this._activatedRoute });
  }

  /**
   * Perform the info action for the given row
   *
   * @param {*} $event
   * @memberof IndividualsMapListComponent
   */
  onInfo($event: any): void {
    this._router.navigate(['info', $event.id_individual], { relativeTo: this._activatedRoute });
  }

  /**
   * Perform the edit action for the given row
   *
   * @param {*} $event
   * @memberof IndividualsMapListComponent
   */
  onEdit($event: any): void {
    this._router.navigate(['form', $event.id_individual], { relativeTo: this._activatedRoute });
  }

  /**
   * Open the delete modal with Individual properties
   *
   * @param {Individual} $event The selected Individual to delete
   * @memberof IndividualsMapListComponent
   */

  public openDeleteModal($event: Individual) {
    this.selectedRows = [$event];
    const modalRef = this._ngbModal.open(ModalComponent);

    modalRef.componentInstance.title = this._translate.instant(
      'Individuals.Individuals.Titles.Delete',
      { id: this.selectedRows[0].id_individual, name: this.selectedRows[0].individual_name }
    );
    modalRef.componentInstance.bodyHTML = `
        ${this._translate.instant('Individuals.Individuals.Fields.individual_name')} : ${this.selectedRows[0].individual_name}<br>
        ${this._translate.instant('Individuals.Individuals.Fields.taxref_nom_vern')} : ${this.selectedRows[0].taxref_nom_vern}<br>
        ${this._translate.instant('Individuals.Individuals.Fields.nomenclature_sex_name')} : ${this.selectedRows[0].nomenclature_sex_name}<br>
      `;
    modalRef.componentInstance.validateButtonType = 'delete';
    modalRef.componentInstance.validate.subscribe((id: number) => {
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

  /**
   * Export the individuals list in the given format, with the filters and
   * sort currently applied to the list/map (not the pagination: the export
   * always covers the whole filtered list).
   *
   * @param {string} format
   * @memberof IndividualsMapListComponent
   */
  public onExport(format: string): void {
    const APIParams = {
      ...this._APIFiltersParams,
      ...this.APISortParams,
    };
    this._individualsService.exportIndividuals(format, APIParams);
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
      ...this.APISortParams,
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
      ...this.APISortParams,
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
        }),
        takeUntil(this._destroy$)
      )
      .subscribe((data) => {
        this._datatable$.next(data);
        this._setPermissions();
      });

    this._individualsService
      .getIndividualsForMap(APIParams)
      .pipe(takeUntil(this._destroy$))
      .subscribe((data) => this._mapData$.next(data));
  }

  /**
   * Set the allowToDelete, allowToEdit and allowToAdd variables
   * considering the item cruved or object cruved
   *
   * For each item id, if a deployment or observation exists
   * set the corresponding array entry to false, else to true
   *
   * @private
   * @memberof IndividualsMapListComponent
   */
  private _setPermissions(): void {
    this.datatable$.subscribe((datatable) => {
      if (!datatable.items) {
        return;
      }

      this.allowedToDelete = {};
      this.allowedToEdit = {};

      // Add access
      const currentObject = this._module.currentModule.module_objects['INDIVIDUALS'];
      this.allowedToAdd = {
        id: 0,
        access: currentObject?.cruved?.C == 0 ? false : true,
        message:
          currentObject?.cruved?.C == 0
            ? this._translate.instant('Individuals.ApiErrors.InsufficientPermissions')
            : null,
      };

      datatable.items.forEach((item: Individual) => {
        // Edit access
        this.allowedToEdit[item.id_individual] = {
          id: item.id_individual,
          access: item.cruved?.U ?? false,
          message:
            (item.cruved?.U ?? false)
              ? null
              : this._translate.instant('Individuals.ApiErrors.InsufficientPermissions'),
        };

        // Delete access
        this.allowedToDelete[item.id_individual] = {
          id: item.id_individual,
          access: item.cruved?.D ?? false,
          message:
            (item.cruved?.D ?? false)
              ? null
              : this._translate.instant('Individuals.ApiErrors.InsufficientPermissions'),
        };

        if (this.allowedToDelete[item.id_individual].access) {
          // Not allowed to delete if observations exists
          if (item.last_observation_date) {
            this.allowedToDelete[item.id_individual].access = false;
            this.allowedToDelete[item.id_individual].message = this._translate.instant(
              'Individuals.ApiErrors.HasObservation'
            );
          }
          // Not allowed to delete if deployments exists
          else if (
            Object.keys(item.deployed_devices).length > 0 ||
            Object.keys(item.deployed_markings).length > 0
          ) {
            this.allowedToDelete[item.id_individual].access = false;
            this.allowedToDelete[item.id_individual].message = this._translate.instant(
              'Individuals.ApiErrors.HasDeployment'
            );
          }
        }
      });
    });
  }
}
