import { Component, OnInit } from '@angular/core';
import { ActivatedRoute } from '@angular/router';
import { Location } from '@angular/common';
import { FormBuilder, FormGroup, Validators } from '@angular/forms';
import { Observable } from 'rxjs';

import { CommonService } from '@geonature_common/service/common.service';
import { ConfigService } from '@geonature/services/config.service';

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
  public dataTable$: Observable<Individual> = new Observable<Individual>();
  public availableFields!: Individual;
  public individualId!: number;
  public formAction!: string;
  public form!: FormGroup;
  public formConstraints: Record<string, FormConstraint> = INDIVIDUALS_FORM_CONSTRAINTS;
  public taxonListId: string = this._config.INDIVIDUALS.GLOBAL.ID_TAXON_LIST;

  constructor (
    private _route: ActivatedRoute,
    private _config: ConfigService,
    private _commonService: CommonService,
    private _fb: FormBuilder,
    private _service: IndividualsService,
    private _location: Location,
    private _errorHandler: ErrorHandlerService
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
    });

    // First initialisation of the table with the resolver data
    this._route.data.subscribe(({ datatable }) => {
      if (datatable && datatable['id_individual']) {
        this.individualId = datatable['id_individual'];
        this.formAction = 'EDIT';
        console.log(datatable)
        this.patchForm(datatable);
      }
      else {
        this.formAction = 'ADD';
      }
    });

    // this._route.params.subscribe((params) => {
    //   if (params['id_individual']) {
    //     console.log(params['id_individual'])
    //     this.individualId = params['id_individual'];
    //     this.formAction = 'EDIT';
    //     // // Peut-être pas utile le dataTable$
    //     this.dataTable$ = this._service.getIndividual(this.individualId);
    //     this._service.getIndividual(this.individualId).subscribe((individual: any) => {
    //       this.patchForm(individual);
    //     });
    //   } else {
    //     this.formAction = 'ADD';
    //   }
    // });
  }

  patchForm(individual: any): void {
    /// Modifier par : Device au lieu de any et faire le mapping si besoin
    this.form.patchValue(individual);
    this.form.patchValue({
      cd_nom: { cd_nom:individual.cd_nom, nom_valide:'Bouquetin'},
      id_nomenclature_sex: individual.nomenclature_sex.id_nomenclature,
    });
  }

  onSave(): void {
    const individual = this.form.getRawValue();

    this._service.createOrUpdateIndividual(individual, this.formAction, this.individualId).subscribe({
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
