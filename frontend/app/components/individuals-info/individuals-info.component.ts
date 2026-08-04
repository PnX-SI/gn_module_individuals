import { ViewEncapsulation, Component, OnInit } from '@angular/core';
import { Location } from '@angular/common';
import { ActivatedRoute } from '@angular/router';
import { Observable, of, forkJoin, combineLatest } from 'rxjs';
import { TranslateService } from '@ngx-translate/core';

import { ConfigService } from '@geonature/services/config.service';
import { CommonService } from '@geonature_common/service/common.service';
import { ModuleService } from '@geonature/services/module.service';
import { DataFormService } from '@geonature_common/form/data-form.service';

import { DATATABLE_CONFIG } from '../../utils/constants.util';
import { Individual } from '../../models/individuals.models';
import { Deployment } from '../../models/deployments.models';
import { Column, AccessResult } from '../../models/common.models';
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
  public allowedToDelete!: AccessResult;
  public allowedToEdit!: AccessResult;
  public defaultLang!: string;
  private _individualId!: number;
  public additionalFields: Array<any> = [];

  constructor(
    private _config: ConfigService,
    private _commonService: CommonService,
    private _route: ActivatedRoute,
    private _translate: TranslateService,
    private _service: IndividualsService,
    private _location: Location,
    private _dfs: DataFormService,
    public moduleService: ModuleService
  ) {}

  ngOnInit(): void {
    // First initialisation of the table with the resolver data, to display something while waiting
    // for translations to load and avoid having an empty table at the beginning
    combineLatest([
      this._dfs.getadditionalFields({
        module_code: [this.moduleService.currentModule.module_code],
      }),
      this._route.data,
    ]).subscribe(([additionalFields, individualData]) => {
      this.additionalFields = additionalFields;
      const datatable = individualData?.datatable;

      this.dataTable$ = of(datatable);
      this._individualId = datatable.id_individual;

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
      } else {
        datatable.deployments = [];
      }

      this._setPermissions(datatable);
    });

    this.defaultLang = this._config['DEFAULT_LANGUAGE'];
  }

  onDelete(): void {
    this._service.deleteIndividual(this._individualId).subscribe({
      next: (res) => {
        this._commonService.translateToaster('info', 'Individuals.Individuals.Messages.Deleted', {
          id: this._individualId,
        });
        this._location.back();
      },
      error: (err) => {
        const msg = err.name + ':' + err.message || JSON.stringify(err);
        this._commonService.translateToaster('error', 'Individuals.Individuals.Errors.DeletedNOK', {
          id: this._individualId,
          error: msg,
        });
      },
    });
  }

  /**
   * Set edit and delete permissions
   *
   * @private
   * @param {Individual} datatable
   * @memberof IndividualsInfoComponent
   */
  private _setPermissions(datatable: Individual) {
    console.log(datatable.cruved);
    this.allowedToEdit = { id: datatable.id_individual, access: true };
    this.allowedToDelete = { id: datatable.id_individual, access: true };

    this.allowedToDelete.access = datatable.cruved?.D;
    this.allowedToDelete.message = this.allowedToDelete.access
      ? null
      : this._translate.instant('Individuals.ApiErrors.InsufficientPermissions');

    // Delete access
    if (this.allowedToDelete.access) {
      // Check if device has observations, if yes : no access
      if (datatable.last_observation_date) {
        this.allowedToDelete.access = false;
        this.allowedToDelete.message = this._translate.instant(
          'Individuals.ApiErrors.HasObservation'
        );
      }
      // Check if device has deployments, if yes : no access
      else if (datatable.deployed_devices?.length > 0 || datatable.deployed_markings?.length > 0) {
        this.allowedToDelete.access = false;
        this.allowedToDelete.message = this._translate.instant(
          'Individuals.ApiErrors.HasDeployment'
        );
      }
    }

    // Edit Access
    this.allowedToEdit.access = datatable.cruved?.U ?? false;
    this.allowedToEdit.message = this.allowedToEdit.access
      ? null
      : this._translate.instant('Individuals.ApiErrors.InsufficientPermissions');
  }
}
