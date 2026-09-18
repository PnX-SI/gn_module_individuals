import { Component, OnInit } from '@angular/core';
import { ActivatedRoute, Router } from '@angular/router';
import { FormBuilder, FormGroup, Validators } from '@angular/forms';
import { Subject, BehaviorSubject, Observable } from 'rxjs';
import { takeUntil, tap, filter } from 'rxjs/operators';
import { TranslateService } from '@ngx-translate/core';
import { NgbModal } from '@ng-bootstrap/ng-bootstrap';

import { ModuleService } from '@geonature/services/module.service';
import { CommonService } from '@geonature_common/service/common.service';
import { ConfigService } from '@geonature/services/config.service';
import { DataFormService } from '@geonature_common/form/data-form.service';

import { ErrorHandlerService } from '../../../services/errors-handler.service';
import { Individual } from '../../../models/individuals.models';
import { DEPLOYMENT_MODEL, Deployment } from '../../../models/deployments.models';
import { FormConstraint, ItemCollection, DatatableColumnLink, AccessResult } from '../../../models/common.models';
import { INDIVIDUALS_FORM_CONSTRAINTS } from '../../../utils/constants.util';
import { IndividualsService } from '../../../services/individuals.service';
import { DeploymentsService } from '../../../services/deployments.service';
import { ModalComponent } from '../../modal/modal.component'
import { DeploymentsFormComponent } from '../../deployments-form/deployments-form.component';
;
@Component({
  selector: 'gn-individuals-individuals-form',
  templateUrl: 'individuals-form.component.html',
  standalone: false,
})
export class IndividualsFormComponent implements OnInit {
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
  public allowedToSave: AccessResult = { id: 0, access: false, message: null };
  public allowedToChangeDeployments: Record<number, AccessResult> = {};
  public allowedToAddDeployments: AccessResult = { id: 0, access: false, message: null };
  private _currentModule!: any;
  private _currentModuleObjectCode = 'INDIVIDUALS';
  public individualsObjectModules: any[] = [];

  constructor(
    private _route: ActivatedRoute,
    private _router: Router,
    private _translate: TranslateService,
    private _config: ConfigService,
    private _commonService: CommonService,
    private _fb: FormBuilder,
    private _service: IndividualsService,
    private _errorHandler: ErrorHandlerService,
    private _module: ModuleService,
    public _deploymentsService: DeploymentsService,
    private _modalService: NgbModal,
    private _dataFormService: DataFormService
  ) {}

  ngOnInit(): void {
    this._currentModule = this._module.currentModule;
    this.individualsObjectModules = this._module.getModules()
      .filter(module => !!(module as any).module_objects?.INDIVIDUALS)
      .map(module => ({
            label: (module as any).module_code,
            value: (module as any).id_module
        })
      );

    // First initialisation of the datatable (resolver) and
    // additional data
    this._route.data
      .pipe(takeUntil(this._destroy$))
      .subscribe(({ datatable }) => {
        this.datatable = datatable;
        this.formAction = datatable?.id_individual ? 'EDIT' : 'ADD';

        // If they're deployments to display, create and ItemCollection for 
        // the ListComponent
        this._dataTable_deployments$.next({
          items: Object.values(datatable?.deployments ?? {})
        });

        // Get additional data if exists
        this._dataFormService
          .getadditionalFields({
            module_code: [this._currentModule.module_code],
            object_code: [this._currentModuleObjectCode],
            // En attente des devs pour pouvoir sélectionner le taxon
            // cd_nom: [datatable.cd_nom]
          })
          .pipe(takeUntil(this._destroy$))
          .subscribe ((additionalFields) => {
            this.additionalFields = additionalFields;
            if (datatable?.id_individual) {
                this.patchForm(datatable);
            }
          });
    });

    // Form initialization
    this.form = this._fb.group({
      id_individual: [null],
      modules: [
        this.formAction === 'ADD' ? [this._currentModule.id_module] : [],
        Validators.required
      ],
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
      active: [null, Validators.required], // In DB is nullable
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

    // To be sure to wait translations before setting permissions
    this._translate
      .get([
        'Individuals.ApiErrors.InsufficientPermissions',
        'Individuals.Errors.FormInvalid',
        'Individuals.Errors.FormNotModified',
      ])
      .subscribe(() => {
        this._setPermissions(this.datatable);
        // Angular consider that the form content is not modified
        this.form.markAsPristine();
      });

    // Update permissions when form values change
    this.form.valueChanges
      .pipe(
        filter(() => this.form.dirty),
        takeUntil(this._destroy$)
      )
      .subscribe(() => {
        this._setPermissions(this.datatable);
      });
  }

  ngOnDestroy() {
    this._destroy$.next();
    this._destroy$.complete();
  }

  /**
   * Open a modal with the DeploymentsFormComponent to add or edit a deployment
   * to the given id_individual
   *
   * @param {(Deployment | { id_individual: number })} deployment
   * @memberof IndividualsFormComponent
   */
  addOrEditDeployment(deployment: Deployment | { id_individual: number }) {
    const modalRef = this._modalService.open(ModalComponent);
    modalRef.componentInstance.bodyComponent = DeploymentsFormComponent;
    modalRef.componentInstance.bodyComponentData = deployment;
    modalRef.componentInstance.validateButtonType = null;
    modalRef.result
      .then(() => {
        this._loadDeploymentData();
        this.form.markAsDirty();
      })
      .catch(() => {
        // Modal is closed
      });
  }

  /**
   * Delete the deployment linked to the given id_deployment
   *
   * @param {number} id_deployment
   * @memberof IndividualsFormComponent
   */
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

  /**
   * Path the form with the given individual properties
   *
   * @param {*} individual
   * @memberof IndividualsFormComponent
   */
  patchForm(individual: any): void {
    this.form.patchValue(individual);
    this.form.patchValue(
      {
        cd_nom: { cd_nom: individual.cd_nom, nom_valide: individual.nom_vern },
        id_nomenclature_sex: individual.nomenclature_sex.id_nomenclature,
        modules: individual.modules.map((module: any) => module.id_module)
          // value: individual.modules[0].id_module, // Mettre Individuals par défaut
        // {
        //   label: this._currentModule.module_name,
        //   value: this._currentModule.id_module, // Mettre Individuals par défaut
        // },
      }
    );

    this.additionalFields.forEach((field) => {
      field.value = individual.additional_data?.[field.attribut_name] ?? field.value;
    });
  }

  /**
   * Save the individual after edit or add action. Called when 
   * the save button is clicked
   *
   * @memberof IndividualsFormComponent
   */
  onSave(): void {
    let individual = this.form.getRawValue();

    this._service
      .createOrUpdateIndividual(individual, this.formAction)
      .subscribe({
        next: (result: Individual) => {
          const successKey =
            this.formAction === 'ADD'
              ? 'Individuals.Individuals.Messages.Added'
              : 'Individuals.Individuals.Messages.Edited';
          this._commonService.translateToaster('info', successKey, { name: result.individual_name, id: result.id_individual });
          this.form.markAsPristine();
          this._router.navigate(['/individuals/individuals/info',result.id_individual])
        },
        error: (err) => {
          this._errorHandler.handleHttpError(
            err,
            { id: this.datatable.id_individual, name: this.datatable.individual_name },
            this.formAction === 'ADD' ? 'Individuals.Individuals.Errors.AddedNOK' : 'Individuals.Individuals.Errors.EditedNOK'
          );
        },
      });
  }

  /**
   * Reload the deployments list
   *
   * @private
   * @memberof IndividualsFormComponent
   */
  private _loadDeploymentData(): void {
    this._service
      .getIndividual(this.datatable.id_individual)
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
   * Cancel the add or edit action. Called when the cancel button
   * is clicked
   *
   * @memberof IndividualsFormComponent
   */
  onCancel(): void {
    this._router.navigate(['/individuals/individuals']);
  }

  /**
   * Set access permissions on
   *  - Add and edit individuals
   *  - Add, edit end delete deployments
   *
   * @private
   * @param {Individual} datatable
   * @memberof IndividualsFormComponent
   */
  private _setPermissions(datatable: Individual): void {
    // Save Access
    if (datatable) {
      // Edit mode
      this.allowedToSave = { 
        id: datatable.id_individual? datatable.id_individual : 0, 
        access: datatable.cruved?.U ?? false, 
        message: datatable.cruved?.U ?? false ? null : this._translate.instant(
          'Individuals.ApiErrors.InsufficientPermissions'
        )
      };
    }
    else {
      // Add mode
      const currentObject = this._currentModule.module_objects[this._currentModuleObjectCode];
      this.allowedToSave = {
        id: 0,
        access: currentObject?.cruved?.C == 0 ? false : true,
        message: currentObject?.cruved?.C == 0 ? this._translate.instant('Individuals.ApiErrors.InsufficientPermissions') : null
      };
    }

    if (this.allowedToSave.access) {
      if (!this.form.valid) {
        this.allowedToSave.access = false;
        this.allowedToSave.message = this._translate.instant('Individuals.Errors.FormInvalid');
      }
      else if (this.formAction === 'EDIT' && !this.form.dirty) {
        this.allowedToSave.access = false;
        this.allowedToSave.message = this._translate.instant('Individuals.Errors.FormNotModified');
      }
    }

    // Edit mode : Deployment access rights are the same as the individual edit access rights
    if (datatable) {
      this.allowedToAddDeployments = { 
        id: datatable.id_individual? datatable.id_individual : 0, 
        access: datatable.cruved?.U ?? false, 
        message: datatable.cruved?.U ?? false ? null : this._translate.instant(
          'Individuals.ApiErrors.InsufficientPermissions'
        )
      };

      this.allowedToChangeDeployments = {};
      datatable.deployments?.forEach((deployment: Deployment) => {
        // Edit and delete deployment actions have the same access rights
        // of the individual 
        this.allowedToChangeDeployments[deployment.id_deployment] = {
          id: deployment.id_deployment,
          access: datatable.cruved?.U ?? false,
          message: datatable.cruved?.U ?? false ? this._translate.instant('Individuals.ApiErrors.InsufficientPermissions') : null
        };
      });
    }
  }
}
