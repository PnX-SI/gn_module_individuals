import { ViewEncapsulation, Component, OnInit, HostListener, TemplateRef, ViewChild} from '@angular/core';
import { ActivatedRoute, Router } from '@angular/router';
import { Subject, BehaviorSubject, Observable, of } from 'rxjs';
import { takeUntil, tap, filter } from 'rxjs/operators';
import { TranslateService } from '@ngx-translate/core';
import * as L from 'leaflet';

import { NgbModal } from '@ng-bootstrap/ng-bootstrap';

import { ModuleService } from '@geonature/services/module.service';
import { ConfigService } from '@geonature/services/config.service';
import { CommonService } from '@geonature_common/service/common.service';
import { DataFormService } from '@geonature_common/form/data-form.service';
import { SyntheseDataService } from '@geonature/GN2CommonModule/form/synthese-form/synthese-data.service';
import { MapService } from '@geonature/GN2CommonModule/map/map.service';

import { CONTENT_CONFIG, DATATABLE_CONFIG, MAP_CONFIG } from '../../../utils/constants.util';
import { calcContentHeight, dateFormat, timeFormat, getValuesLabels, getRatio } from '../../../utils/functions.util';

import { Individual } from '../../../models/individuals.models';
import { DEPLOYMENT_MODEL, Deployment } from '../../../models/deployments.models';
import { AccessResult, ItemCollection, DatatableColumnLink, Feature, FeatureCollection } from '../../../models/common.models';
import { ModalComponent } from '../../modal/modal.component'
import { IndividualsService } from '../../../services/individuals.service';
import { DeploymentsService } from '../../../services/deployments.service';
import { DeploymentsFormComponent } from '../../deployments-form/deployments-form.component';

@Component({
  selector: 'gn-individuals-individuals-info',
  templateUrl: 'individuals-info.component.html',
  styleUrls: ['individuals-info.component.scss'],
  // SCSS used only in this component and not in the global CSS
  encapsulation: ViewEncapsulation.None,
  standalone: false,
})
export class IndividualsInfoComponent implements OnInit {
  @ViewChild('featurePopupTemplate') featurePopupTemplate!: TemplateRef<{ feature: Feature<unknown> }>;
  public contentHeight: number = CONTENT_CONFIG.MIN_HEIGHT;
  public datatable!: Individual;
  private _datatable_deployments$ = new BehaviorSubject<ItemCollection<Deployment> | null>(null);
  public datatable_deployments$: Observable<ItemCollection<Deployment>> = this._datatable_deployments$.pipe(
    filter((data): data is ItemCollection<Deployment> => data !== null)
  );

  public availableDeploymentsColumnsParams = DEPLOYMENT_MODEL;
  public displayedDeploymentsColumnsParams: string[] = this._config.INDIVIDUALS?.INDIVIDUALS?.DEPLOYMENT_LIST_COLUMNS ?? [];
  public rowHeight: number = DATATABLE_CONFIG.TABLE_ROW_HEIGHT;
  public allowedToDelete: AccessResult = {id: 0, access: false, message: null};
  public allowedToEdit: AccessResult = {id: 0, access: false, message: null};
  public allowedToChangeDeployments: Record<number, AccessResult> = {};
  public defaultLang!: string;
  private _destroy$ = new Subject<void>();
  public additionalFields: Array<any> = [];
  public datatableColumnsLink: DatatableColumnLink[] = [
    { 
      column_name: "tracking_device_info",
      link_prefix: "/individuals/devices/info",
      id_field_name: "id_tracking_device" 
    }
  ]
  private _currentModule!: any;
  private _currentModuleObjectCode = 'INDIVIDUALS';
  private _currentDataset = "";

  public mapReady: boolean = false;
  public noGeometry: boolean = false;
  mapData$: Observable<FeatureCollection<unknown>> = new Observable<
    FeatureCollection<unknown>
  >();
  private _mapLayersById: {id: number, layer: L.Layer | null}[] = [];
  private _mapMoveHandler: (() => void) | null = null;
  private _ignoreNextMapMoveEnd = false;
  private _selectedLayer: L.Layer | null = null;
  private _selectedFeature: Feature<any> | null = null;
  private _selectedObservation!: number;

  public dateFormat = dateFormat;
  public getValuesLabels = getValuesLabels;
  public timeFormat = timeFormat;


  constructor(
    private _config: ConfigService,
    private _commonService: CommonService,
    private _route: ActivatedRoute,
    private _router: Router,
    private _translate: TranslateService,
    private _service: IndividualsService,
    private _modalService: NgbModal,
    private _individualsService: IndividualsService,
    private _deploymentsService: DeploymentsService,
    private _module: ModuleService,
    private _dataFormService: DataFormService,
    private _syntheseService: SyntheseDataService,
    private _mapService: MapService,
  ) {}

  ngOnInit(): void {
    this._currentModule = this._module.currentModule;

    // First initialisation of the datatable (resolver) and
    // additional data
    this._route.data.pipe(takeUntil(this._destroy$))
      .subscribe(({ datatable }) => {
        this.datatable = datatable;

        // If they're deployments to display, create and ItemCollection for 
        // the ListComponent
        this._datatable_deployments$.next({
          items: Object.values(datatable?.deployments ?? {})
        });

        this._setPermissions(datatable);

        // Get the temporaly configured dataset for the curent cd_nom
        this._currentDataset = this._config.INDIVIDUALS.INDIVIDUALS?.TAXON_DATASET?.find((taxonDataset: { CD_NOM: number; DATASET_SHORT_NAME: string }) => taxonDataset.CD_NOM === datatable.cd_nom).ID_DATASET;

        // Get additional data if exists
        this._dataFormService
          .getadditionalFields({
            module_code: this._currentModule.module_code,
            object_code: this._currentModuleObjectCode,
            // En attente des devs pour pouvoir sélectionner le taxon
            id_dataset: this._currentDataset,
            // cd_nom: [datatable.cd_nom]
          })
          .pipe(takeUntil(this._destroy$))
          .subscribe ((additionalFields) => {
            this.additionalFields = additionalFields;
          });
    });

    // To be sure to wait translations before setting permissions
    this._translate
      .get([
        'Individuals.ApiErrors.InsufficientPermissions',
        'Individuals.ApiErrors.HasObservation',
        'Individuals.ApiErrors.HasDeployment'
      ])
      .subscribe(() => {
        this._setPermissions(this.datatable);
      });

    this.defaultLang = this._config['DEFAULT_LANGUAGE'];

    // Get Individual geometries
    this._syntheseService.getSyntheseData(
      { 
        limit: this._config.INDIVIDUALS.INDIVIDUALS.MAX_OBS_NB ?? null,
        modif_since_validation: false, 
        individuals: [this.datatable.id_individual]
      },
      { "format": "ungrouped_geom" },
    ).subscribe((mapData) => {
      this.mapData$ = of(mapData);

      mapData.features
        // Copy befor change
        .slice()
        // To have a table sorted in descending order of observation date, used for display
        // .reverse() 
        .forEach((feature: any) => {
          this._mapLayersById.push({id: feature.properties.id_synthese, layer: null});
        });
    });
  }

  ngAfterViewInit(): void {
    setTimeout(() => { // Usefull to wait the DOM build before calculation
      this.contentHeight = calcContentHeight();
      this._zoomOnFeatures();
      this._bindMapMove();
    }, 0);
  }

  // Listen to window resize event to recalculate the content height and resize the map
  @HostListener('window:resize', ['$event'])
    onWindowResize($event: any): void {
      this.contentHeight = calcContentHeight();
  }

  ngOnDestroy() {
    this._destroy$.next();
    this._destroy$.complete();
  }

  addOrEditDeployment(deployment: Deployment | { id_individual: number }) {
    const modalRef = this._modalService.open(ModalComponent);
    modalRef.componentInstance.bodyComponent = DeploymentsFormComponent;
    modalRef.componentInstance.bodyComponentData = deployment;
    modalRef.componentInstance.validateButtonType = null;
    modalRef.result
      .then(() => {
        this._loadDeploymentData();
      })
      .catch(() => {
        // Modal is closed
      });
  }

  deleteDeployment(id_deployment: number) {
    this._deploymentsService.deleteDeployment(id_deployment).subscribe({
      next: () => {
        this._commonService.translateToaster('info', 'Individuals.Deployments.Messages.Deleted', {
          id: id_deployment,
        });
        this._loadDeploymentData();
      },
      error: (err) => {
        const msg = err.name + ':' + err.message || JSON.stringify(err);
        this._commonService.translateToaster('error', 'Individuals.Deployments.Errors.DeletedNOK', {
          id: id_deployment,
          error: msg,
        });
      },
    });
  }

  onDelete(): void {
    this._service.deleteIndividual(this.datatable.id_individual).subscribe({
      next: (res) => {
        this._commonService.translateToaster('info', 'Individuals.Individuals.Messages.Deleted', {
          id: this.datatable.id_individual,
          name: this.datatable.individual_name
        });
        this._router.navigate(['/individuals/individuals']);
      },
      error: (err) => {
        const msg = err.name + ':' + err.message || JSON.stringify(err);
        this._commonService.translateToaster('error', 'Individuals.Individuals.Errors.DeletedNOK', {
          id: this.datatable.id_individual,
          name: this.datatable.individual_name,
          error: msg,
        });
      },
    });
  }

  private _loadDeploymentData(): void {
    this._individualsService
      .getIndividual(this.datatable.id_individual)
      .pipe(
        tap((data) => this._setPermissions(data)),
        takeUntil(this._destroy$)
      )
      .subscribe((data) => this._datatable_deployments$.next(
        data.deployments ? 
          { items: Object.values(data.deployments) } : 
          { items: [] }
      ));
  }

  /**
   * Set edit and delete permissions
   *
   * @private
   * @param {Individual} datatable
   * @memberof IndividualsInfoComponent
   */
  private _setPermissions(datatable: Individual) {
    // Edit Access
    this.allowedToEdit = { 
      id: datatable.id_individual, 
      access: datatable.cruved?.U ?? false,
      message: datatable.cruved?.U ?? false ? null : this._translate.instant('Individuals.ApiErrors.InsufficientPermissions')
    };

    // Deployment access rights are the same as the individual edit access rights
    this.allowedToChangeDeployments = {};
    datatable.deployments?.forEach((deployment: Deployment) => {
      // Edit and delete deployment actions have the same access rights
      // of the individual 
      this.allowedToChangeDeployments[deployment.id_deployment] = {
        ...this.allowedToEdit,
        id: deployment.id_deployment,
      };
    });

    // Delete access
    this.allowedToDelete = { 
      id: datatable.id_individual, 
      access: datatable.cruved?.D ?? false,
      message: datatable.cruved?.D ?? false ? null : this._translate.instant(
        'Individuals.ApiErrors.InsufficientPermissions'
      )
    };
    // Check if individual has observations, if yes : no access
    if (this.allowedToDelete) {
      if (datatable.last_observation_date) {
        this.allowedToDelete.access = false;
        this.allowedToDelete.message = this._translate.instant(
            'Individuals.ApiErrors.HasObservation'
        );
      }
      // Check if individual has deployments, if yes : no access
      else if (datatable.deployed_devices?.length > 0 || datatable.deployed_markings?.length > 0) {
        this.allowedToDelete.access = false;
        this.allowedToDelete.message = this._translate.instant(
          'Individuals.ApiErrors.HasDeployment'
        );
      }
    }
  }

  /**
   * Prepare each feature display: Style, actions on event, popup information, etc.
   *
   * @param {Feature<Individual>} feature
   * @param {L.Layer} layer
   * @return {*}  {void}
   * @memberof IndividualsInfoComponent
   */
  onEachFeature(feature: Feature<unknown>, layer: L.Layer): void {
    // Access the identifier dynamically. `idFieldName` is configured by the parent,
    // so TypeScript cannot verify the property at compile time. The identifier field
    // is guaranteed by the component contract to be a number.
    
    const id = (feature.properties as Record<string, unknown>)["id_synthese"] as number;
    let nbFeatures = 0;
    const item = this._mapLayersById.find(item => item.id === id);

    if (item) {
      item.layer = layer;
    }

    this.mapData$.subscribe((featuresCollection) => nbFeatures = featuresCollection.features.length)
    
    // Set layer style
    this._setLayerStyle(layer, id === this._selectedObservation, id);
    layer.on('click', () => this.onMapFeatureClick(feature, layer));

    // Prepare popup
    if (feature.properties) {
      layer.bindPopup(this._buildPopupContent(feature));
    }

    if (id === this._selectedObservation) {
      this._selectedLayer = layer;
      this._selectedFeature = feature;
      this._openLayerPopup(layer);
    }
  }

  /**
   * Reload data whenever the map extent changes (bbox).
   *
   * @private
   * @return {*}  {void}
   * @memberof IndividualsInfoComponent
   */
  private _bindMapMove(): void {
    const map = this._mapService.getMap();
    if (!map) {
      return;
    }
    // Store the map move function in a property so we can remove it later if needed
    this._mapMoveHandler = () => {
      // _zoomOnFeature emit a movenend : we needs to ignore it to avoid an API call
      if (this._ignoreNextMapMoveEnd) {
        this._ignoreNextMapMoveEnd = false;
        return;
      }
    };

    // Install a listner on the moveend event
    map.on('moveend', this._mapMoveHandler);
  }

  /**
   * Zoom the map on current features
   *
   * @private
   * @memberof IndividualsInfoComponent
   */
  private _zoomOnFeatures(): void {
    this.mapData$.subscribe((mapData) => {
      const layer = L.geoJSON(mapData);
      const map = this._mapService.getMap();

      if (!map) {
        return;
      }

      if (layer.getBounds().isValid()) {
        this._ignoreNextMapMoveEnd = true;
        map.fitBounds(layer.getBounds(), { padding: [20, 20], animate: false });
      }
      else {
        this._showNoGeometryMessage();
      }

      this.mapReady = true;
    });
  }

  /**
   *
   * @private
   * @param {L.Layer} layer
   * @param {boolean} selected
   * @return {*}  {void}
   * @memberof IndividualsInfoComponent
   */
  // private _setLayerStyle(layer: L.Layer, selected: boolean, position: number | null = null, coeffForDisplay: number | null = null): void {
  private _setLayerStyle(layer: L.Layer, selected: boolean, id: number | null = null): void {
    if (!(layer as any).setStyle) {
      return;
    }
    
    let nbFeatures = 0;
    let date = "";
    this.mapData$.subscribe((featuresCollection) => {
      nbFeatures = featuresCollection.features.length

      featuresCollection.features.forEach((feature: any) => {
        if(feature.properties.id_synthese === id) {
          date = feature.properties.date_min
        }
      })
    });

    let layerRank = this._mapLayersById.findIndex(item => item.id === id) + 1;
    let coeffForDisplay = getRatio(
      Math.ceil(layerRank / this._config.INDIVIDUALS.INDIVIDUALS.OPACITY_RANGE),
      Math.ceil(nbFeatures / this._config.INDIVIDUALS.INDIVIDUALS.OPACITY_RANGE)
    );

    let layerSelected = {
      color: this._config.INDIVIDUALS.GLOBAL.SELECTED_LAYER_COLOR ?? MAP_CONFIG.SELECTED_LAYER_COLOR,
      fillColor: this._config.INDIVIDUALS.GLOBAL.SELECTED_LAYER_COLOR ?? MAP_CONFIG.SELECTED_LAYER_COLOR,
      fillOpacity: this._config.INDIVIDUALS.GLOBAL.SELECTED_LAYER_OPACITY ?? MAP_CONFIG.SELECTED_LAYER_OPACITY,
      radius: MAP_CONFIG.SELECTED_LAYER_RADIUS,
      weight: MAP_CONFIG.SELECTED_LAYER_WEIGHT
    };

    let layerUnselected = {
      fillColor: layerRank && layerRank == 1 
        ? (this._config.INDIVIDUALS.GLOBAL.FIRST_LAYER_COLOR ?? MAP_CONFIG.FIRST_LAYER_COLOR)
        : (this._config.INDIVIDUALS.GLOBAL.UNSELECTED_LAYER_COLOR ?? MAP_CONFIG.UNSELECTED_LAYER_COLOR),
      color: this._config.INDIVIDUALS.GLOBAL.UNSELECTED_LAYER_COLOR ?? MAP_CONFIG.UNSELECTED_LAYER_COLOR,
      fillOpacity: coeffForDisplay ?? this._config.INDIVIDUALS.GLOBAL.UNSELECTED_LAYER_OPACITY ?? MAP_CONFIG.UNSELECTED_LAYER_OPACITY,
      radius: MAP_CONFIG.UNSELECTED_LAYER_RADIUS,
      weight: MAP_CONFIG.UNSELECTED_LAYER_WEIGHT
    };

    (layer as any).setStyle(selected ? layerSelected : layerUnselected);
  }

  /**
   * Toggle the layers colors (selected or not) and the layer position (bring to front or not)
   *
   * @private
   * @param {L.Layer} layer
   * @memberof IndividualsInfoComponent
   */
  private _highlightLayer(feature: Feature<any>, layer: L.Layer): void {
    // Old selected layer: reset style
    if (this._selectedLayer && this._selectedFeature) {
      this._setLayerStyle(this._selectedLayer, false, this._selectedFeature.properties.id_synthese);
    }

    // New selected layer: set style and bring to front
    this._selectedLayer = layer;
    this._selectedFeature = feature;
    this._setLayerStyle(layer, true, feature.properties.id_synthese);

    if ((layer as any).bringToFront) {
      (layer as any).bringToFront();
    }
  }

  public onMapFeatureClick(feature: Feature<unknown>, layer: L.Layer): void {
    this._selectedObservation = (feature.properties as Record<string, unknown>)["id_synthese"] as number;
    this._highlightLayer(feature, layer);
  }

  /**
   * Build popup content from the parent-provided template.
   *
   * If the parent passes a featurePopupTemplate, this method creates
   * an embedded view for the clicked feature and renders its DOM nodes
   * into a container element. The resulting HTMLElement is returned so
   * Leaflet can display it inside the popup.
   *
   * If no template is provided, the popup content is empty.
   *
   * @param {Feature<unknown>} feature - The clicked GeoJSON feature.
   * @returns {HTMLElement | string} Rendered popup content.
   * @memberof IndividualsInfoComponent
   */
  private _buildPopupContent(feature: Feature<unknown>): HTMLElement | string {
    if (!this.featurePopupTemplate) {
      return '';
    }

    // Create an embedded view using the parent template and the current feature.
    const view = this.featurePopupTemplate.createEmbeddedView({ feature });
    view.detectChanges();

    const HTMLDom = document.createElement('div');

    // Append each rendered DOM node from the template into the container.
    view.rootNodes.forEach((node) => {
      if (node instanceof Node) {
        HTMLDom.appendChild(node);
      }
    });

    return HTMLDom;
  }

  /**
   * Open the given layer popup
   *
   * @private
   * @param {L.Layer} layer
   * @memberof IndividualsInfoComponent
   */
  private _openLayerPopup(layer: L.Layer): void {
    if ((layer as any).openPopup) {
      (layer as any).openPopup();
    }
  }

  /**
   * Show a message explaining that the selected list element as no corresponding geometry
   *
   * @private
   * @memberof MapListComponent
   */
  private _showNoGeometryMessage(): void {
    this.noGeometry = true;
  }
}
