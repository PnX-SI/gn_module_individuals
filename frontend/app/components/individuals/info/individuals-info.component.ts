import { ViewEncapsulation, Component, OnInit } from '@angular/core';
import { ActivatedRoute, Router } from '@angular/router';
import { Subject, BehaviorSubject, Observable, of } from 'rxjs';
import { takeUntil, tap, filter } from 'rxjs/operators';
import { TranslateService } from '@ngx-translate/core';

import { NgbModal } from '@ng-bootstrap/ng-bootstrap';

import { ModuleService } from '@geonature/services/module.service';
import { ConfigService } from '@geonature/services/config.service';
import { CommonService } from '@geonature_common/service/common.service';
import { DataFormService } from '@geonature_common/form/data-form.service';

import { DATATABLE_CONFIG } from '../../../utils/constants.util';
import { dateFormat, timeFormat, getValuesLabels } from '../../../utils/functions.util';

import { Individual } from '../../../models/individuals.models';
import { DEPLOYMENT_MODEL, Deployment } from '../../../models/deployments.models';
import { AccessResult, ItemCollection, DatatableColumnLink } from '../../../models/common.models';
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
    private _dataFormService: DataFormService
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
}
