import { Component, OnInit } from '@angular/core';
import { ActivatedRoute, Router } from '@angular/router';
import { Location } from '@angular/common';
import { FormBuilder, FormGroup, Validators } from '@angular/forms';
import { Subject, BehaviorSubject, Observable } from 'rxjs';
import { takeUntil, tap, filter } from 'rxjs/operators';
import { TranslateService } from '@ngx-translate/core';

import { NgbModal } from '@ng-bootstrap/ng-bootstrap';

import { ModuleService } from '@geonature/services/module.service';
import { CommonService } from '@geonature_common/service/common.service';
import { ConfigService } from '@geonature/services/config.service';

import { ErrorHandlerService } from '../../services/errors-handler.service';
import { Individual } from '../../models/individuals.models';
import { DEPLOYMENT_MODEL, Deployment } from '../../models/deployments.models';
import { FormConstraint, ItemCollection, DatatableColumnLink, AccessResult } from '../../models/common.models';
import { INDIVIDUALS_FORM_CONSTRAINTS } from '../../utils/constants.util';
import { IndividualsService } from '../../services/individuals.service';
import { DeploymentsService } from '../../services/deployments.service';
import { ModalComponent } from '../modal/modal.component'
import { DeploymentsFormComponent } from '../deployments-form/deployments-form.component';
;
@Component({
  selector: 'gn-individuals-individuals-form',
  templateUrl: 'individuals-form.component.html',
  standalone: false,
})
export class IndividualsFormComponent implements OnInit {
  public individualId!: number;
  public formAction!: string;
  public form!: FormGroup;
  public formConstraints: Record<string, FormConstraint> = INDIVIDUALS_FORM_CONSTRAINTS;
  public taxonListId: string = this._config.INDIVIDUALS.GLOBAL.ID_TAXON_LIST;
  public datatable!: Individual;
  public additionalFields: Array<any> = [];
  public availableDeploymentsColumnsParams = DEPLOYMENT_MODEL;
  public displayedDeploymentsColumnsParams: string[] = this._config.INDIVIDUALS?.INDIVIDUALS?.DEPLOYMENT_LIST_COLUMNS ?? [];
  private _dataTable_deployments$ = new BehaviorSubject<ItemCollection<Deployment> | null>(null);
  public dataTable_deployments$: Observable<ItemCollection<Deployment>> = this._dataTable_deployments$.pipe(
    filter((data): data is ItemCollection<Deployment> => data !== null)
  );
  private _destroy$ = new Subject<void>();
  public datatableColumnsLink: DatatableColumnLink[] = [
    { 
      column_name: "tracking_device_info",
      link_prefix: "/individuals/devices/info",
      id_field_name: "id_tracking_device" 
    }
  ]
  public allowedToSave!: AccessResult;
  public allowedToChangeDeployments: Record<number, AccessResult> = {};

  constructor(
    private _route: ActivatedRoute,
    private _router: Router,
    private _translate: TranslateService,
    private _config: ConfigService,
    private _commonService: CommonService,
    private _fb: FormBuilder,
    private _service: IndividualsService,
    private _location: Location,
    private _errorHandler: ErrorHandlerService,
    public moduleService: ModuleService,
    public _deploymentsService: DeploymentsService,
    private _modalService: NgbModal,
  ) {}

  ngOnInit(): void {
    // Form initialization
    this.form = this._fb.group({
      id_individual: [null],
      individual_name: [
        null,
        [
          Validators.required,
          Validators.maxLength(this.formConstraints.individual_name.maxLength),
          Validators.pattern(this.formConstraints.individual_name.pattern),
        ],
      ],
      cd_nom: [null, Validators.required],
      id_nomenclature_sex: [null, Validators.required],
      active: [null, Validators.required],
      comment: [
        null,
        [
          Validators.maxLength(this.formConstraints.comment.maxLength),
          Validators.pattern(this.formConstraints.comment.pattern),
        ],
      ],
      deployments: this._fb.array<FormGroup>([]),
      additional_data: this._fb.group({}),
    });

    // Resolver : First initialisation of the datatable and additional fields
    this._route.data.pipe(takeUntil(this._destroy$)).subscribe(({ datatable, additionalFields }) => {
      this.additionalFields = additionalFields;
      this.datatable = datatable;
      this.formAction = datatable?.id_individual ? 'EDIT' : 'ADD';

      if (datatable?.id_individual) {
        this.individualId = datatable.id_individual;
        this.patchForm(datatable);
      }

      // If they're deployments to display, create and ItemCollection for 
      // the ListComponent
      this._dataTable_deployments$.next({
        items: Object.values(datatable?.deployments ?? {})
      });

      this._setPermissions(datatable);
    });

    this.form.valueChanges.subscribe(() => {
      this._setPermissions(this.datatable);
    });
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
        // this._loadData();
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

  patchForm(individual: any): void {
    /// Modifier par : Device au lieu de any et faire le mapping si besoin
    this.form.patchValue(individual);
    this.form.patchValue({
      // En attendant la correction de l'API
      cd_nom: { cd_nom: individual.cd_nom, nom_valide: individual.nom_vern },
      id_nomenclature_sex: individual.nomenclature_sex.id_nomenclature,
    });
  }

  onSave(): void {
    let individual = this.form.getRawValue();
    // individual = this.formToJson(individual);

    this._service
      .createOrUpdateIndividual(individual, this.formAction)
      .subscribe({
        next: (res) => {
          const successKey =
            this.formAction === 'ADD'
              ? 'Individuals.Individuals.Messages.Added'
              : 'Individuals.Individuals.Messages.Edited';
          this._commonService.translateToaster('info', successKey, { id: this.individualId });
          this.form.markAsPristine();
          this._location.back();
        },
        error: (err) => {
          this._errorHandler.handleHttpError(
            err,
            { id: this.individualId },
            'Individuals.Individuals.ApiErrors'
          );
        },
      });
  }

  private _loadDeploymentData(): void {
    this._service
      .getIndividual(this.individualId)
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

  onCancel(): void {
    this._router.navigate(['/individuals/individuals']);
  }

  /**
   * Set edit and delete permissions
   *
   * @private
   * @param {Individual} datatable
   * @memberof IndividualsInfoComponent
   */
  private _setPermissions(datatable: Individual) {
    this.allowedToSave = { id: datatable.id_individual, access: true };
    this.allowedToChangeDeployments = {};
    console.log(this.form.valid, this.form.dirty, datatable.cruved?.U);
    // Edit Access 
    if (datatable.cruved?.U === false) {
      this.allowedToSave.access = datatable.cruved?.U ?? false;
      this.allowedToSave.message = this._translate.instant('Individuals.ApiErrors.InsufficientPermissions');
    }
    else if (!this.form.valid) {
      this.allowedToSave.access = false;
      this.allowedToSave.message = this._translate.instant('Individuals.Errors.FormInvalid');
    }
    else if (this.formAction === 'EDIT' && !this.form.dirty) {
      this.allowedToSave.access = false;
      this.allowedToSave.message = this._translate.instant('Individuals.Errors.FormNotModified');
    }

    datatable.deployments?.forEach((deployment: Deployment) => {
      // Edit and delete deployment actions have the same access rights
      // of the individual 
      this.allowedToChangeDeployments[deployment.id_deployment] = {
        ...this.allowedToSave,
        id: deployment.id_deployment,
      };
    });
  }
}
