import { Component, OnInit } from '@angular/core';

import { ConfigService } from '@geonature/services/config.service';

@Component({
  selector: 'ng-individuals-tab',
  templateUrl: 'tab.component.html',
  styleUrls: ['tab.component.scss'],
})
export class TabComponent implements OnInit {
  
  constructor(
    private config: ConfigService,
  ) {}

  ngOnInit() {
    console.log('Config:', this.config);
  }

}