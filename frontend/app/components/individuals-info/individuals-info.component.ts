import { ViewEncapsulation, Component, OnInit } from '@angular/core';
import { Location } from '@angular/common';
import { ActivatedRoute } from '@angular/router';
import { Observable, of, forkJoin } from 'rxjs';
import { TranslateService } from '@ngx-translate/core';

import { ConfigService } from '@geonature/services/config.service';
import { CommonService } from '@geonature_common/service/common.service';

import { DATATABLE_CONFIG } from '../../utils/constants.util';
import { Individual } from '../../models/individuals.models';
import { Deployment } from '../../models/deployments.models';
import { Column } from '../../models/common.models';
import { IndividualsService } from '../../services/individuals.service';

@Component({
  selector: 'gn-individuals-individuals-info',
  templateUrl: 'individuals-info.component.html',
  styleUrls: ['individuals-info.component.scss'],
  // SCSS used only in this component and not in the global CSS
  encapsulation: ViewEncapsulation.None,
  standalone: false,
})
export class IndividualsInfoComponent implements OnInit {
  public dataTable$: Observable<Individual> = new Observable<Individual>();
  public deploymentsColumns: Column<Deployment>[] = [];
  public rowHeight: number = DATATABLE_CONFIG.TABLE_ROW_HEIGHT;
  public canBeDeleted: boolean = false;
  public defaultLang!: string; 
  private _individualId!: number;

  constructor(
    private _config: ConfigService,
    private _commonService: CommonService,
    private _route: ActivatedRoute,
    private _translate: TranslateService,
    private _service: IndividualsService,
    private _location: Location
  ) {}

  ngOnInit(): void {
    // First initialisation of the table with the resolver data, to display something while waiting for translations to load and avoid having an empty table at the beginning
    this._route.data.subscribe(({ datatable }) => {
      // If they're deployments to display, create the columns table for ngx-datatable with translated fields
      if (datatable.deployments?.length > 0) {
        const props = this._config.INDIVIDUALS.INDIVIDUALS
          .DEPLOYMENT_LIST_COLUMNS as (keyof Deployment)[];

        forkJoin(
          props.map((prop) => this._translate.get(`Individuals.Deployments.Fields.${prop}`))
        ).subscribe((translations) => {
          this.deploymentsColumns = props.map((prop, name) => ({
            prop: prop,
            name: translations[name],
          }));
        });
        this.canBeDeleted = true;
      } else {
        datatable.deployments = [];
      }

      this.dataTable$ = of(datatable);
      this._individualId = datatable.id_individual;
    });
    
    this.defaultLang = this._config['DEFAULT_LANGUAGE'];
  }

  onDelete(): void {
    // this._service.deleteDevice(this._individualId).subscribe({
    //   next: (res) => {
    //     this._commonService.translateToaster('info', 'Individuals.Devices.Messages.Deleted', {
    //       id: this._individualId,
    //     });
    //     this._location.back();
    //   },
    //   error: (err) => {
    //     const msg = err.name + ':' + err.message || JSON.stringify(err);
    //     this._commonService.translateToaster('error', 'Individuals.Devices.Errors.DeletedNOK', {
    //       id: this._deviceId,
    //       error: msg,
    //     });
    //   },
    // });
  }
}
