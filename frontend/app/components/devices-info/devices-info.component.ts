import { ViewEncapsulation, Component, OnInit, AfterViewInit } from '@angular/core';
import { ActivatedRoute } from '@angular/router';
import { Observable, of, forkJoin} from 'rxjs';
import { TranslateService } from '@ngx-translate/core';

import { ConfigService } from '@geonature/services/config.service';

import { DATA_TABLE_CONFIG } from '../../utils/constants.util';
import { Device } from '../../models/devices.models';
import { Deployment } from '../../models/deployments.models';
import { Column } from '../../models/common.models';

@Component({
  selector: 'gn-individuals-devices-info',
  templateUrl: 'devices-info.component.html',
  styleUrls: ['devices-info.component.scss'],
  encapsulation: ViewEncapsulation.None,
})
export class DevicesInfoComponent implements OnInit, AfterViewInit {
  public dataTable$: Observable<Device> = new Observable<Device>();
  public deploymentsColumns: Column<Deployment>[] = [];
  public rowHeight: number = DATA_TABLE_CONFIG.TABLE_ROW_HEIGHT;

  constructor(
    public config: ConfigService,
    private activatedRoute: ActivatedRoute,
    private _translate: TranslateService,
  ) {}

  ngOnInit() : void {
    // First initialisation of the table with the resolver data, to display something while waiting for translations to load and avoid having an empty table at the beginning
    this.activatedRoute.data.subscribe(({data}) => {
      this.dataTable$ = of(data);

      // If they're deployments to display, create the columns table for ngx-datatable with translated fields
      if (data.deployments.length > 0) {
        const props = this.config.INDIVIDUALS.DEVICES.DEFAULT_DEPLOY_DISPLAYED_COLUMNS as (keyof Deployment)[];

        forkJoin(
          props.map(
            prop => this._translate.get(`Individuals.DeploymentsFields.${prop}`)
          )
        ).subscribe(translations => {
          this.deploymentsColumns = props.map((prop, name) => ({
            prop: prop,
            name: translations[name],
            sortable: false,
          }));
        });
      }
      console.log(this.deploymentsColumns);
      console.log(data.deployments);
    });
    
  }

  ngAfterViewInit() : void {
  }
}


