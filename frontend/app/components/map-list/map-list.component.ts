import { Component, OnInit, AfterViewInit, HostListener } from '@angular/core';
import { ActivatedRoute } from '@angular/router';

import { MapListService } from '@geonature/GN2CommonModule/map-list/map-list.service';
import { MapService } from '@geonature/GN2CommonModule/map/map.service';
import { ModuleService } from '@geonature/services/module.service';

@Component({
  selector: 'gn-individuals-map-list',
  templateUrl: 'map-list.component.html',
  styleUrls: ['map-list.component.scss'],
})
export class MapListComponent implements OnInit, AfterViewInit {
  public userCruved: any;
  public contentHeight: number;
  public currentTabCode: string;
  public apiEndPoint: string;

  constructor(
    public mapListService: MapListService,
    private _moduleService: ModuleService,
    private _mapService: MapService,
    private _route: ActivatedRoute
  ) {}

  ngOnInit() {
    // Get current module and current user CRUVED
    const currentModule = this._moduleService.currentModule;
    this.userCruved = currentModule.cruved;
    // Get current url to know if we are on devices, individuals, observations or captures
    this.currentTabCode = this._route.snapshot.url[0].path;

    this.mapListService.refreshUrlQuery();
    // Set zoom on layer to true
    // zoom only when search data
    this.mapListService.zoomOnLayer = true;

    // mapListService config
    this.mapListService.idName = 'id_tracking_device';
    this.apiEndPoint = `${this._moduleService.currentModule.module_url}/${this.currentTabCode}`;
    console.log('API endpoint:', this.apiEndPoint);

    this.mapListService.displayColumns = [
      { name: 'Individu', prop: 'name' },
      { name: 'CD Nom', prop: 'cd_nom' },
      { name: 'Sexe', prop: 'id_nomenclature_sex' },
    ];

    this.mapListService.refreshUrlQuery();
    this.mapListService.getData(this.apiEndPoint, [{ param: 'limit', value: 1 }]);
  }

  ngAfterViewInit() {
    setTimeout(() => this.calcContentHeight(), 500);
    if (this._mapService.currentExtend) {
      this._mapService.map.setView(
        this._mapService.currentExtend.center,
        this._mapService.currentExtend.zoom
      );
    }
    this._mapService.removeLayerFeatureGroups([this._mapService.fileLayerFeatureGroup]);
  }

  // Listen to window resize event to recalculate the content height and resize the map
  @HostListener('window:resize', ['$event'])
  onResize(event) {
    this.calcContentHeight();
  }

  // Fonction that return the size of the content of the card, to set the height of the map
  calcContentHeight() {
    let windowH = window.innerHeight;
    let toolbarH = document.getElementById('individuals-tab')
      ? document.getElementById('individuals-tab').getBoundingClientRect().top
      : 0;
    let height = windowH - (toolbarH + 80);

    this.contentHeight = height >= 350 ? height : 350;
    // Resize map after resize container
    if (this._mapService.map) {
      setTimeout(() => {
        this._mapService.map.invalidateSize();
      }, 10);
    }
  }
}
