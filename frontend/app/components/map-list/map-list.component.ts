import { Component, OnInit, AfterViewInit, HostListener, Input, Output, EventEmitter, TemplateRef } from '@angular/core';
import { Observable } from 'rxjs';

import { MapService } from '@geonature/GN2CommonModule/map/map.service';
import { ModuleService } from '@geonature/services/module.service';
import { ConfigService } from '@geonature/services/config.service';

import { Feature, FeatureCollection, PaginatedItemCollection } from '../../models/common.models';
import { Individual } from '../../models/individuals.models';
import { CONTENT_CONFIG, MAP_CONFIG } from '../../utils/constants.util';
import { calcContentHeight } from '../../utils/functions.util';

@Component({
  selector: 'gn-individuals-map-list',
  templateUrl: 'map-list.component.html',
  styleUrls: ['map-list.component.scss'],
  standalone: false,
})
export class MapListComponent implements OnInit, AfterViewInit {
  // public userCruved: any;
  public contentHeight: number = CONTENT_CONFIG.MIN_HEIGHT;
  // public currentTabCode: string;
  // public apiEndPoint: string;
  @Output() pagination: EventEmitter<any> = new EventEmitter();
  @Output() sort: EventEmitter<any> = new EventEmitter();
  @Input() objectName!: string;
  @Input() idFieldName!: string;
  @Input() availableColumnsParams!: Record<string, unknown>;
  @Input() displayedColumnsParams: string[] = [];
  @Input() dataTable$: Observable<PaginatedItemCollection<unknown>> = new Observable<
    PaginatedItemCollection<unknown>
  >();
  @Input() nbRowsToDisplay!: number;
  @Input() fieldsTranslation: string = ''
  @Input() sorts: Array<Object> = [];
  @Input() allowedToEdit: boolean[] = [];
  @Input() allowedToDelete: Record<number, boolean> = {};
  @Input() summaryTemplate!: TemplateRef<any>;
  @Input() filtersTemplate!: TemplateRef<any>;
  @Input() mapData$: Observable<FeatureCollection<unknown>> = new Observable<FeatureCollection<unknown>>(); 
  
  public mapReady: boolean = false;
  public mapLayersById: Record<number, L.Layer> = {};
  private _selectedId: number | null = null;

  constructor(
    private _moduleService: ModuleService,
    private _mapService: MapService,
    private _config: ConfigService
  ) {}

  ngOnInit() {
    this.contentHeight = calcContentHeight();
    // // Get current module and current user CRUVED
    // const currentModule = this._moduleService.currentModule;
    // this.userCruved = currentModule.cruved;
    // // Get current url to know if we are on devices, individuals, observations or captures
    // this.currentTabCode = this._route.snapshot.url[0].path;

    // this.mapListService.refreshUrlQuery();
    // // Set zoom on layer to true
    // // zoom only when search data
    // this.mapListService.zoomOnLayer = true;

    // // mapListService config
    // this.mapListService.idName = 'id_tracking_device';
    // this.apiEndPoint = `${this._moduleService.currentModule.module_url}/${this.currentTabCode}`;
    // console.log('API endpoint:', this.apiEndPoint);

    // this.mapListService.displayColumns = [
    //   { name: 'Individu', prop: 'name' },
    //   { name: 'CD Nom', prop: 'cd_nom' },
    //   { name: 'Sexe', prop: 'id_nomenclature_sex' },
    // ];

    // this.mapListService.refreshUrlQuery();
    // this.mapListService.getData(this.apiEndPoint, [{ param: 'limit', value: 1 }]);
  }

  ngAfterViewInit(): void {
    setTimeout(() => {
      this.mapReady = true;
      // this.bindMapMove();
      // this.loadMapFeatures();
      // this.resizeMap();
    }, 0);
  }

  // Listen to window resize event to recalculate the content height and resize the map
  @HostListener('window:resize', ['$event'])
  onWindowResize($event: any): void {
    this.contentHeight = calcContentHeight();
  }

  // Fonction that return the size of the content of the card, to set the height of the map
  // calcContentHeight() {
  //   let windowH = window.innerHeight;
  //   let toolbarH = document.getElementById('individuals-tab')
  //     ? document.getElementById('individuals-tab').getBoundingClientRect().top
  //     : 0;
  //   let height = windowH - (toolbarH + 80);

  //   this.contentHeight = height >= 350 ? height : 350;
  //   // Resize map after resize container
  //   if (this._mapService.map) {
  //     setTimeout(() => {
  //       this._mapService.map.invalidateSize();
  //     }, 10);
  //   }
  // }

  onPage($event: any): void {
    this.pagination.emit($event);
  }

  onSort($event: any): void {
    this.sort.emit($event);
  }

  openDeleteModal($event: any): void {
  }

  /**
   * Prepare each feature display: Style, actions on event, popup information, etc.
   *
   * @param {Feature<Individual>} feature
   * @param {L.Layer} layer
   * @return {*}  {void}
   * @memberof MapListComponent
   */
  onEachFeature(feature: Feature<Individual>, layer: L.Layer): void {
    // Access the identifier dynamically. `idFieldName` is configured by the parent,
    // so TypeScript cannot verify the property at compile time. The identifier field
    // is guaranteed by the component contract to be a number.
    const id = (feature.properties as Record<string, unknown>)[this.idFieldName] as number;
    this.mapLayersById[id] = layer;
    this._setLayerStyle(layer, id === this._selectedId);
    layer.on('click', () => this.onMapFeatureClick(feature, layer));

    // if (feature.properties) {
    //   layer.bindPopup(this.buildPopup(feature));
    // }

    // if (id === this._selectedId) {
    //   this._selectedLayer = layer;
    //   this.openLayerPopup(layer);
    // }
  }

  /**
   * Set the layer style according to the selected parameter
   *
   * @private
   * @param {L.Layer} layer
   * @param {boolean} selected
   * @return {*}  {void}
   * @memberof MapListComponent
   */
  private _setLayerStyle(layer: L.Layer, selected: boolean): void {
    if (!(layer as any).setStyle) {
      return;
    }
    console.log("color:",this._config.INDIVIDUALS.GLOBAL.SELECTED_LAYER_COLOR);
    
    (layer as any).setStyle({
      color: selected ? 
      this._config.INDIVIDUALS.GLOBAL.SELECTED_LAYER_COLOR ?? MAP_CONFIG.SELECTED_LAYER_COLOR : this._config.INDIVIDUALS.GLOBAL.UNSELECTED_LAYER_COLOR ?? MAP_CONFIG.UNSELECTED_LAYER_COLOR,
      fillColor: selected ? this._config.INDIVIDUALS.GLOBAL.SELECTED_LAYER_COLOR ?? MAP_CONFIG.SELECTED_LAYER_COLOR : this._config.INDIVIDUALS.GLOBAL.UNSELECTED_LAYER_COLOR ?? MAP_CONFIG.UNSELECTED_LAYER_COLOR,
      fillOpacity: selected ? this._config.INDIVIDUALS.GLOBAL.SELECTED_LAYER_OPACITY ?? MAP_CONFIG.SELECTED_LAYER_OPACITY : this._config.INDIVIDUALS.GLOBAL.UNSELECTED_LAYER_OPACITY ?? MAP_CONFIG.UNSELECTED_LAYER_OPACITY,
      radius: selected ? 8 : 6,
      weight: selected ? 3 : 2,
    });
  }

  private onMapFeatureClick(feature: Feature<unknown>, layer: L.Layer): void {
  }
}