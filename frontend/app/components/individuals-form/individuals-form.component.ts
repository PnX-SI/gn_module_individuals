import { Component, OnInit } from '@angular/core';
import { ActivatedRoute } from '@angular/router';
import { Location } from '@angular/common';
import { FormBuilder, FormGroup, Validators } from '@angular/forms';

import { combineLatest } from 'rxjs';

import { ModuleService } from '@geonature/services/module.service';
import { CommonService } from '@geonature_common/service/common.service';
import { ConfigService } from '@geonature/services/config.service';
import { DataFormService } from '@geonature_common/form/data-form.service';

import { ErrorHandlerService } from '../../services/errors-handler.service';
import { Individual } from '../../models/individuals.models';
import { FormConstraint } from '../../models/common.models';
import { INDIVIDUALS_FORM_CONSTRAINTS } from '../../utils/constants.util';
import { IndividualsService } from '../../services/individuals.service';

@Component({
  selector: 'gn-individuals-individuals-form',
  templateUrl: 'individuals-form.component.html',
  standalone: false,
})
export class IndividualsFormComponent implements OnInit {
  public availableFields!: Individual;
  public individualId!: number;
  public formAction!: string;
  public form!: FormGroup;
  public formConstraints: Record<string, FormConstraint> = INDIVIDUALS_FORM_CONSTRAINTS;
  public taxonListId: string = this._config.INDIVIDUALS.GLOBAL.ID_TAXON_LIST;

  public additionalFields: Array<any> = [];

  constructor(
    private _route: ActivatedRoute,
    private _config: ConfigService,
    private _commonService: CommonService,
    private _fb: FormBuilder,
    private _service: IndividualsService,
    private _location: Location,
    private _errorHandler: ErrorHandlerService,
    private _dfs: DataFormService,
    public moduleService: ModuleService
  ) {}

  ngOnInit(): void {
    // Form initialization
    this.form = this._fb.group({
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
      additional_data: this._fb.group({}),
    });

    combineLatest([
      this._dfs.getadditionalFields({
        module_code: [this.moduleService.currentModule.module_code],
      }),
      this._route.data,
    ]).subscribe(([additionalFields, individualData]) => {
      this.additionalFields = additionalFields;
      const individual = individualData?.datatable;
      if (individual?.id_individual) {
        this.individualId = individual.id_individual;
        this.formAction = 'EDIT';
        this.patchForm(individual);
        // Patch additional fields with individual data
        this.additionalFields.forEach((field) => {
          field.value = individual.additional_data?.[field.attribut_name] ?? field.value;
        });
      } else {
        this.formAction = 'ADD';
      }
    });
  }

  patchForm(individual: any): void {
    /// Modifier par : Device au lieu de any et faire le mapping si besoin
    this.form.patchValue(individual);
    this.form.patchValue({
      // En attendant la correction de l'API
      cd_nom: { cd_nom: individual.cd_nom, nom_valide: 'Bouquetin' },
      id_nomenclature_sex: individual.nomenclature_sex.id_nomenclature,
    });
  }

  onSave(): void {
    const individual = this.form.getRawValue();
    this._service
      .createOrUpdateIndividual(individual, this.formAction, this.individualId)
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
}
