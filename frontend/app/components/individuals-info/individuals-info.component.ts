import { ViewEncapsulation, Component, OnInit } from '@angular/core';
import { Location } from '@angular/common';
import { ActivatedRoute } from '@angular/router';
import { Subject, BehaviorSubject, Observable, of } from 'rxjs';
import { takeUntil, tap, filter } from 'rxjs/operators';
import { TranslateService } from '@ngx-translate/core';

import { NgbModal } from '@ng-bootstrap/ng-bootstrap';

import { ConfigService } from '@geonature/services/config.service';
import { CommonService } from '@geonature_common/service/common.service';

import { DATATABLE_CONFIG } from '../../utils/constants.util';
import { Individual } from '../../models/individuals.models';
import { DEPLOYMENT_MODEL, Deployment } from '../../models/deployments.models';
import { AccessResult, ItemCollection, DatatableColumnLink } from '../../models/common.models';
import { ModalComponent } from '../modal/modal.component'
import { IndividualsService } from '../../services/individuals.service';
import { DeploymentsService } from '../../services/deployments.service';
import { DeploymentsFormComponent } from '../deployments-form/deployments-form.component';
;
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
  private _dataTable_deployments$ = new BehaviorSubject<ItemCollection<Deployment> | null>(null);
  public dataTable_deployments$: Observable<ItemCollection<Deployment>> = this._dataTable_deployments$.pipe(
    filter((data): data is ItemCollection<Deployment> => data !== null)
  );

  public availableDeploymentsColumnsParams = DEPLOYMENT_MODEL;
  public displayedDeploymentsColumnsParams: string[] = this._config.INDIVIDUALS?.INDIVIDUALS?.DEPLOYMENT_LIST_COLUMNS ?? [];
  public rowHeight: number = DATATABLE_CONFIG.TABLE_ROW_HEIGHT;
  public allowedToDelete!: AccessResult;
  public allowedToEdit!: AccessResult;
  public allowedToChangeDeployments: Record<number, AccessResult> = {};
  public defaultLang!: string;
  private _individualId!: number;
  private _destroy$ = new Subject<void>();
  public additionalFields: Array<any> = [];
  public datatableColumnsLink: DatatableColumnLink[] = [
    { 
      column_name: "tracking_device_info",
      link_prefix: "/individuals/devices/info",
      id_field_name: "id_tracking_device" 
    }
  ]

  constructor(
    private _config: ConfigService,
    private _commonService: CommonService,
    private _route: ActivatedRoute,
    private _translate: TranslateService,
    private _service: IndividualsService,
    private _location: Location,
    private _modalService: NgbModal,
    private _individualsService: IndividualsService,
    private _deploymentsService: DeploymentsService
  ) {}

  ngOnInit(): void {
    // Resolver : First initialisation of the datatable and additional fields
    this._route.data.pipe(takeUntil(this._destroy$)).subscribe(({ datatable, additionalFields }) => {
      this.dataTable$ = of(datatable);
      this.additionalFields = additionalFields ?? [];

      // If they're deployments to display, create and ItemCollection for 
      // the ListComponent
      this._dataTable_deployments$.next({
        items: Object.values(datatable?.deployments ?? {})
      });

      this._individualId = datatable.id_individual;
      this._setPermissions(datatable);
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
    modalRef.result.then(() => {
      this._loadDeploymentData();
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

  private _loadDeploymentData(): void {
    this._individualsService
      .getIndividual(this._individualId)
      .pipe(
        tap((data) => this._setPermissions(data)),
        takeUntil(this._destroy$)
      )
      .subscribe((data) => this._dataTable_deployments$.next(
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
    this.allowedToEdit = { id: datatable.id_individual, access: true };
    this.allowedToDelete = { id: datatable.id_individual, access: true };
    this.allowedToChangeDeployments = {};

    this.allowedToDelete.access = datatable.cruved?.D;
    this.allowedToDelete.message = this.allowedToDelete.access
      ? null
      : this._translate.instant('Individuals.ApiErrors.InsufficientPermissions');

    // Delete access
    if (this.allowedToDelete.access) {
      // Check if individual has observations, if yes : no access
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

    // Edit Access 
    this.allowedToEdit.access = datatable.cruved?.U ?? false;
    this.allowedToEdit.message = this.allowedToEdit.access
      ? null
      : this._translate.instant('Individuals.ApiErrors.InsufficientPermissions');

    datatable.deployments?.forEach((deployment: Deployment) => {
      // Edit and delete deployment actions have the same access rights
      // of the individual 
      this.allowedToChangeDeployments[deployment.id_deployment] = {
        ...this.allowedToEdit,
        id: deployment.id_deployment,
      };
    });
  }
}
