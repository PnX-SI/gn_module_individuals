import { Component, OnInit, OnDestroy } from '@angular/core';
import { Subject, BehaviorSubject, Observable, of } from 'rxjs';
import { takeUntil, tap, filter } from 'rxjs/operators';

import { ConfigService } from '@geonature/services/config.service';

import {
  Observation,
  OBSERVATION_MODEL,
  APIObservationFiltersParams,
} from '../../models/observations.models';
import {
  Sort,
  ItemCollection,
  APIPaginationParams,
  FeatureCollection,
  AccessResult,
  DatatableColumnLink,
} from '../../models/common.models';
import { ObservationsService } from '../../services/observations.service';
import { INDIVIDUALS_DEFAULT_SORT, DATATABLE_CONFIG } from '../../utils/constants.util';
import { convertDateTimeToDateStr } from '../../utils/functions.util';

@Component({
  selector: 'gn-individuals-observations-map-list',
  templateUrl: 'observations-map-list.component.html',
  standalone: false,
})
export class ObservationsMapListComponent implements OnInit, OnDestroy {
  public availableColumnsParams = OBSERVATION_MODEL;
  public displayedColumnsParams: string[] =
    this._config.INDIVIDUALS?.OBSERVATIONS?.LIST_COLUMNS ?? [];
  private _datatable$ = new BehaviorSubject<ItemCollection<Observation> | null>(null);
  public datatable$: Observable<ItemCollection<Observation>> = this._datatable$.pipe(
    filter((data): data is ItemCollection<Observation> => data !== null)
  );
  private _destroy$ = new Subject<void>();
  // private _APIPaginationParams: APIPaginationParams = {
  // page: 1,
  // per_page: this.nbRowsToDisplay,
  // prop: INDIVIDUALS_DEFAULT_SORT.prop,
  // dir: INDIVIDUALS_DEFAULT_SORT.dir,
  // };
  private _APIFiltersParams: APIObservationFiltersParams = { active: 'true' };
  private _selectedId: number | null = null;
  public nbRowsToDisplay =
    this._config.INDIVIDUALS?.OBSERVATIONS?.DEFAULT_PAGE_SIZE ?? DATATABLE_CONFIG.PER_PAGE_OPTION;
  public sorts: Array<Sort> = [INDIVIDUALS_DEFAULT_SORT];
  public allowedToAdd: AccessResult = { id: 0, access: false, message: null };
  public allowedToEdit: Record<number, AccessResult> = {};
  public allowedToDelete: Record<number, AccessResult> = {};
  public selectedRows: Observation[] = [];
  public mapData$: Observable<FeatureCollection<Observation>> = new Observable<
    FeatureCollection<Observation>
  >();
  public defaultFilters: APIObservationFiltersParams = {};
  public datatableColumnsLink: DatatableColumnLink[] = [
    {
      column_name: 'dataset_name',
      link_prefix: '/metadata/dataset_detail/',
      id_field_name: 'id_dataset',
      target: '_blank',
    },
  ];
  public convertDateTimeToDateStr = convertDateTimeToDateStr;

  constructor(
    private _config: ConfigService,
    private _observationsService: ObservationsService
  ) {}

  ngOnInit(): void {
    this._loadData();
    this.defaultFilters = this._APIFiltersParams;
  }

  ngOnDestroy(): void {
    this._destroy$.next();
    this._destroy$.complete();
  }

  // onPage($event: any): void {
  //   this._APIPaginationParams = {
  //     page: Number($event.offset ?? 0) + 1,
  //     per_page: Number($event.limit),
  //     prop: this.sorts[0].prop,
  //     dir: this.sorts[0].dir,
  //   };
  //   this._loadData();
  // }

  onSort($event: any): void {
    // this._APIPaginationParams = {
    //   page: Number($event.offset ?? 0) + 1,
    //   per_page: this.nbRowsToDisplay,
    //   prop: $event.sorts[0].prop,
    //   dir: $event.sorts[0].dir,
    // };
    this.sorts = $event.sorts;

    this._loadData();
  }

  /**
   * Call API with the new bbox parametter
   *
   * @param {string} $event Current bbox
   * @memberof ObservationsMapListComponent
   */
  onBbox($event: string): void {
    // this._APIFiltersParams = {
    //   bbox: $event
    // }
    this._loadData();
  }

  /**
   * Perform the info action for the given row
   *
   * @param {*} $event
   * @memberof ObservationsMapListComponent
   */
  onInfo($event: Observation): void {
    window.open(
      $event.url_source + '/' + $event.entity_source_pk_value,
      '_blank',
      'noopener,noreferrer'
    );
  }

  /**
   * Call API with given filter value
   *
   * @param {({key: keyof APIIndividualFiltersParams; value: any;} | null)} $event Filter value {key, value} or null to reset filters
   * @memberof ObservationsMapListComponent
   */
  public onFilters($event: { key: keyof APIObservationFiltersParams; value: any } | null): void {
    if (!$event) {
      this._APIFiltersParams = {};
    } else {
      this._APIFiltersParams[$event.key] = $event.value;
      // this._APIPaginationParams['page'] = 1;
    }
    this._loadData();
  }

  /**
   * API call to get the page corresponding to the given id and reload data with this page.
   * Used when a map feature is clicked and want to display the corresponding row in the paginated table.
   *
   * @param {*} $event
   * @memberof ObservationsMapListComponent
   */
  // public onIdPage($event: any): void {
  //   this._selectedId = $event;
  //   const APIParams = {
  //     ...this._APIPaginationParams,
  //     ...this._APIFiltersParams,
  //   };

  //   if ($event) {
  //     const IdRankAndPage$ = this._individualsService.getIndividualRankAndPage($event, APIParams);

  //     IdRankAndPage$.subscribe((rankAndPage) => {
  //       this._APIPaginationParams.page = rankAndPage.page;
  //       this._loadData();
  //     });
  //   }
  // }

  private _loadData(): void {
    const APIParams = {
      // ...this._APIPaginationParams,
      ...this._APIFiltersParams,
    };
    this._observationsService
      .getObservations(APIParams)
      .pipe(
        tap((datatable) => {
          this.selectedRows = this._selectedId
            ? datatable.items.filter((item) => item.id_synthese === this._selectedId)
            : [];
        }),
        takeUntil(this._destroy$)
      )
      .subscribe({
        next: (datatable) => {
          this._datatable$.next(datatable); // Met à jour le BehaviorSubject
        },
        error: (err) => {
          console.error('Erreur lors du chargement des observations :', err);
          // Optionnel : émettre une valeur par défaut ou null pour gérer l'erreur dans le template
          this._datatable$.next(null);
        },
      });

    this._observationsService
      .getObservationsForMap(APIParams)
      .pipe(takeUntil(this._destroy$))
      .subscribe((data) => (this.mapData$ = of(data)));
  }
}
