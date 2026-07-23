import { Component, OnInit, OnDestroy } from '@angular/core';
import { ActivatedRoute } from '@angular/router';
import { TranslateService } from '@ngx-translate/core';
import { Subject, Observable, of } from 'rxjs';
import { takeUntil, tap } from 'rxjs/operators';
import { NgbModal } from '@ng-bootstrap/ng-bootstrap';

import { ConfigService } from '@geonature/services/config.service';
import { CommonService } from '@geonature_common/service/common.service';

import { ErrorHandlerService } from '../../services/errors-handler.service';
import { Individual, INDIVIDUAL_MODEL, APIIndividualFiltersParams } from '../../models/individuals.models';
import { Sort, PaginatedItemCollection, APIPaginationParams, FeatureCollection } from '../../models/common.models';
import { IndividualsService } from '../../services/individuals.service';
import { INDIVIDUALS_DEFAULT_SORT, DATATABLE_CONFIG } from '../../utils/constants.util';
// import { DeleteModalComponent } from '../delete-modal/delete-modal.component';

@Component({
  selector: 'gn-individuals-individuals-map-list',
  templateUrl: 'individuals-map-list.component.html',
  standalone: false,
})
export class IndividualsMapListComponent implements OnInit, OnDestroy {
  public availableColumnsParams = INDIVIDUAL_MODEL;
  public displayedColumnsParams: string[] = this._config.INDIVIDUALS?.INDIVIDUALS?.DEFAULT_DISPLAYED_COLUMNS ?? [];
  public datatable$: Observable<PaginatedItemCollection<Individual>> = new Observable<
    PaginatedItemCollection<Individual>
  >();
  public nbRowsToDisplay = this._config.INDIVIDUALS?.INDIVIDUALS?.DEFAULT_PAGE_SIZE ?? DATATABLE_CONFIG.PER_PAGE_OPTION;
  public fieldsTranslation = "Individuals.Individuals.Fields";
  public sorts: Array<Sort> = [INDIVIDUALS_DEFAULT_SORT];
  public allowedToEdit: boolean[] = [];
  public allowedToDelete: Record<number, boolean> = {};
  public selectedRows: Individual[] = [];
  public mapData$: Observable<FeatureCollection<Individual>> = new Observable<FeatureCollection<Individual>>();
  public defaultFilters: APIIndividualFiltersParams = {};
  private _destroy$ = new Subject<void>();
  private _APIPaginationParams: APIPaginationParams = {
    page: 1,
    per_page: this.nbRowsToDisplay,
    prop: INDIVIDUALS_DEFAULT_SORT.prop,
    dir: INDIVIDUALS_DEFAULT_SORT.dir,
  };
  private _APIFiltersParams: APIIndividualFiltersParams = {'active': 'true'};
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
    this._activatedRoute.data.pipe(takeUntil(this._destroy$)).subscribe(({ datatable, mapData }) => {
      this.datatable$ = of(datatable);
      this.mapData$ = of(mapData);
      // this._initPermissions(data);
    });

    this.defaultFilters = this._APIFiltersParams;
  }

  ngOnDestroy(): void {
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
      page: Number($event.offset ?? 0) + 1,
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
  }

  /**
   * Call API with given filter value
   *
   * @param {({key: keyof APIIndividualFiltersParams; value: string | number | undefined;} | null)} $event Filter value {key, value} or null to reset filters
   * @memberof IndividualsMapListComponent
   */
  onFilters($event: {key: keyof APIIndividualFiltersParams; value: string | number | undefined;} | null): void {
      if (!$event) {
        this._APIFiltersParams = {};
      } else {
        if ($event.value) {
          this._APIFiltersParams[$event.key] = $event.value;
          this._APIPaginationParams['page'] = 1;
        }
      }
      this._loadData();
  }

  onDelete(): void {
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
      // ...this._APIFiltersParams,
    };

    if ($event) {
      const IdRankAndPage$ = this._individualsService.getIndividualRankAndPage($event, APIParams);

      IdRankAndPage$.subscribe((rankAndPage) => {
        this._APIPaginationParams.page = rankAndPage.page;
        console.log('onPageId called with id:', $event, ' get page:', rankAndPage, ' with params:', APIParams);
        this._loadData();
      });
    }
  }

  private _loadData(): void {
    const APIParams = {
      ...this._APIPaginationParams,
      ...this._APIFiltersParams,
    };
    this.datatable$ = this._individualsService
      .getIndividuals(APIParams).pipe(
        tap((data) => {
          if (this._selectedId !== null) {
            const selected = data.items.find(
              (item) => item.id_individual === this._selectedId
            );
            this.selectedRows = selected ? [selected] : [];
          } else {
            this.selectedRows = [];
          }
          // this._initPermissions(data)
        })
      )
  }

  private loadMapData(): void {
    const APIParams = {
      ...this._APIFiltersParams,
      // bbox: this.getMapBbox(), 
    }

    this.mapData$ = this._individualsService
      .getIndividualsForMap(APIParams)
      // .subscribe((featureCollection) => {
      //   this.mapLayerByIndividualId = {};
      //   this._selectedLayer = null;
      //   this.featureCollection = featureCollection;
      // });
  }

  // private _initPermissions(data: PaginatedItemCollection<Device>): void {
  //   this.allowedToDelete = [];

  //   // Not allowed to delete if deployments exists
  //   // Have to be changed with scope and cruved
  //   if (data.items) {
  //     data.items.forEach((item: Device) => {
  //       this.allowedToDelete[item.id_tracking_device] = item.last_individual_equipped_name == null;
  //     });

  //     // Have to be changed with scope and cruved
  //     this.allowedToEdit = data.items.map(() => true);
  //   }
  // }
}
