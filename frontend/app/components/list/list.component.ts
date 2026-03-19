import { Component, OnInit, AfterViewInit, HostListener } from '@angular/core';
import { ActivatedRoute } from '@angular/router';

import { ModuleService } from '@geonature/services/module.service';

@Component({
  selector: 'gn-individuals-list',
  templateUrl: 'list.component.html',
  styleUrls: ['list.component.scss'],
})
export class ListComponent implements OnInit, AfterViewInit {
  public userCruved: any;
  public contentHeight: number;
  public currentTabCode: string;
  public apiEndPoint: string;

  constructor(
    private _moduleService: ModuleService,
    private _route: ActivatedRoute
  ) {}

  ngOnInit() {
    // Get current module and current user CRUVED
    const currentModule = this._moduleService.currentModule;
    this.userCruved = currentModule.cruved;
    // Get current url to know if we are on devices, individuals, observations or captures
    this.currentTabCode = this._route.snapshot.url[0].path;
  }

  ngAfterViewInit() {
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
    
    // Resize list after resize container
  }
}


