import {
  Component,
  OnInit,
  AfterViewInit,
  HostListener,
  Input,
  Output,
  EventEmitter,
  TemplateRef,
} from '@angular/core';
import { Observable } from 'rxjs';
import * as L from 'leaflet';
import { TranslateService } from '@ngx-translate/core';

import { MapService } from '@geonature/GN2CommonModule/map/map.service';
import { ModuleService } from '@geonature/services/module.service';
import { ConfigService } from '@geonature/services/config.service';

import {
  Feature,
  FeatureCollection,
  PaginatedItemCollection,
  AccessResult,
} from '../../models/common.models';
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
  @Output() delete: EventEmitter<any> = new EventEmitter();
  @Output() idPage: EventEmitter<number> = new EventEmitter();
  @Output() bbox: EventEmitter<string> = new EventEmitter();
  @Input() objectName!: string;
  @Input() idFieldName!: string;
  @Input() availableColumnsParams!: Record<string, unknown>;
  @Input() displayedColumnsParams: string[] = [];
  @Input() datatable$: Observable<PaginatedItemCollection<unknown>> = new Observable<
    PaginatedItemCollection<unknown>
  >();
  @Input() nbRowsToDisplay!: number;
  @Input() fieldsTranslation: string = '';
  @Input() sorts: Array<Object> = [];
  @Input() allowedToEdit: Record<number, AccessResult> = {};
  @Input() allowedToDelete: Record<number, AccessResult> = {};
  @Input() summaryTemplate!: TemplateRef<any>;
  @Input() filtersTemplate!: TemplateRef<any>;
  @Input() selectedRows: unknown[] = [];
  @Input() mapData$: Observable<FeatureCollection<unknown>> = new Observable<
    FeatureCollection<unknown>
  >();
  @Input() featurePopupTemplate!: TemplateRef<{ feature: Feature<unknown> }>;
  @Input() noGeometryMessage: string | null = null;

  public mapReady: boolean = false;
  public noGeometry: boolean = false;

  private _selectedId: number | null = null;
  private _selectedLayer: L.Layer | null = null;
  private _mapLayersById: Record<number, L.Layer> = {};
  // private _lastBbox: string | null = null;
  private _mapMoveHandler: (() => void) | null = null;
  private _ignoreNextMapMoveEnd = false;

  constructor(
    private _moduleService: ModuleService,
    private _mapService: MapService,
    private _config: ConfigService,
    private _translate: TranslateService
  ) {}

  ngOnInit() {
    // No geometry default message translation
    if (!this.noGeometryMessage) {
      this._translate.get('Individuals.Messages.NoGeometry').subscribe((translations) => {
        this.noGeometryMessage = translations;
      });
    }
  }

  ngAfterViewInit(): void {
    setTimeout(() => {
      this.mapReady = true;
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

  onTableSelect($event: any): void {
    const selected = $event.selected?.[0];
    if (!selected) {
      return;
    }
    this.selectedRows = [selected];
    this._selectedId = selected[this.idFieldName];
    if (this._selectedId) {
      this._selectMapFeature(this._selectedId, true);
    }
  }

  onPage($event: any): void {
    this.pagination.emit($event);
  }

  onSort($event: any): void {
    this.sort.emit($event);
  }

  onDelete($event: any): void {
    this.delete.emit($event);
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
    this._mapLayersById[id] = layer;
    this._setLayerStyle(layer, id === this._selectedId);
    layer.on('click', () => this.onMapFeatureClick(feature, layer));

    if (feature.properties) {
      layer.bindPopup(this._buildPopupContent(feature));
    }

    if (id === this._selectedId) {
      this._selectedLayer = layer;
      this._openLayerPopup(layer);
    }
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

    (layer as any).setStyle({
      color: selected
        ? (this._config.INDIVIDUALS.GLOBAL.SELECTED_LAYER_COLOR ?? MAP_CONFIG.SELECTED_LAYER_COLOR)
        : (this._config.INDIVIDUALS.GLOBAL.UNSELECTED_LAYER_COLOR ??
          MAP_CONFIG.UNSELECTED_LAYER_COLOR),
      fillColor: selected
        ? (this._config.INDIVIDUALS.GLOBAL.SELECTED_LAYER_COLOR ?? MAP_CONFIG.SELECTED_LAYER_COLOR)
        : (this._config.INDIVIDUALS.GLOBAL.UNSELECTED_LAYER_COLOR ??
          MAP_CONFIG.UNSELECTED_LAYER_COLOR),
      fillOpacity: selected
        ? (this._config.INDIVIDUALS.GLOBAL.SELECTED_LAYER_OPACITY ??
          MAP_CONFIG.SELECTED_LAYER_OPACITY)
        : (this._config.INDIVIDUALS.GLOBAL.UNSELECTED_LAYER_OPACITY ??
          MAP_CONFIG.UNSELECTED_LAYER_OPACITY),
      radius: selected ? 8 : 6,
      weight: selected ? 3 : 2,
    });
  }

  public onMapFeatureClick(feature: Feature<unknown>, layer: L.Layer): void {
    const id = (feature.properties as Record<string, unknown>)[this.idFieldName] as number;
    this._selectedId = id;
    this._highlightLayer(layer);

    // Emit the selected id to the parent component,
    // which call the API to get the page, reload the datatable with it,
    // set the selectRows attribute to the corresponding row in the datatable
    this.idPage.emit(id);
  }

  /**
   * Toggle the layers colors (selected or not) and the layer position (bring to front or not)
   *
   * @private
   * @param {L.Layer} layer
   * @memberof MapListComponent
   */
  private _highlightLayer(layer: L.Layer): void {
    // Old selected layer: reset style
    if (this._selectedLayer) {
      this._setLayerStyle(this._selectedLayer, false);
    }
    // New selected layer: set style and bring to front
    this._selectedLayer = layer;
    this._setLayerStyle(layer, true);
    if ((layer as any).bringToFront) {
      (layer as any).bringToFront();
    }
  }

  /**
   * Zoom the map on current features
   *
   * @private
   * @memberof MapListComponent
   */
  private _zoomOnFeatures(): void {
    this.mapData$.subscribe((mapData) => {
      const layer = L.geoJSON(mapData);

      if (layer.getBounds().isValid()) {
        this._ignoreNextMapMoveEnd = true;
        this._mapService
          .getMap()
          ?.fitBounds(layer.getBounds(), { padding: [20, 20], animate: false });
      }
    });
  }

  /**
   * Reload data whenever the map extent changes (bbox).
   *
   * @private
   * @return {*}  {void}
   * @memberof MapListComponent
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

      const bbox = this._getMapBbox();
      if (bbox) {
        this.bbox.emit(bbox);
      }
    };

    // Install a listner on the moveend event
    map.on('moveend', this._mapMoveHandler);
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
   * @memberof MapListComponent
   */
  private _openLayerPopup(layer: L.Layer): void {
    if ((layer as any).openPopup) {
      (layer as any).openPopup();
    }
  }

  /**
   * According to the given id, highlight the layer
   * and open it's popup.
   *
   * @private
   * @param {number} id
   * @param {boolean} zoom
   * @return {*}  {void}
   * @memberof MapListComponent
   */
  private _selectMapFeature(id: number, zoom: boolean): void {
    const layer = this._mapLayersById[id];

    if (!layer) {
      this._showNoGeometryMessage();
      this._selectedLayer?.closePopup();
      return;
    }
    this._selectedId = id;
    this._highlightLayer(layer);
    this._openLayerPopup(layer);
  }

  /**
   * Show a message explaining that the selected list element as no corresponding geometry
   *
   * @private
   * @memberof MapListComponent
   */
  private _showNoGeometryMessage(): void {
    this.noGeometry = true;
    setTimeout(() => {
      this.noGeometry = false;
    }, 1000);
  }

  /**
   * Return the bbox of current map
   *
   * @private
   * @return {*}  {(string | undefined)}
   * @memberof MapListComponent
   */
  private _getMapBbox(): string | undefined {
    const map = this._mapService.getMap();
    if (!map) {
      return undefined;
    }
    const bounds = map.getBounds();
    return [bounds.getWest(), bounds.getSouth(), bounds.getEast(), bounds.getNorth()]
      .map((value) => value.toFixed(6))
      .join(',');
  }

  /**
   * Ask leaflet to recalculate the size of the map
   *
   * @private
   * @memberof MapListComponent
   */
  // private _resizeMap(): void {
  //   setTimeout(() => {
  //     const map = this._mapService.getMap();
  //     if (map) {
  //       // Wait for the view to finish rendering, then force Leaflet to recalculate
  //       // the map size in case the container dimensions have changed.
  //       map.invalidateSize();
  //     }
  //   }, 10);
  // }
}
