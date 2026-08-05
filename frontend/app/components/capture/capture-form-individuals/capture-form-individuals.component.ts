import { Component } from '@angular/core';
import { FormArray, FormGroup, FormControl, Validators } from '@angular/forms';

import { ConfigService } from '@geonature/services/config.service';
import { ModuleService } from '@geonature/services/module.service';

@Component({
  selector: 'gn-individuals-capture-form-individuals',
  templateUrl: 'capture-form-individuals.component.html',
  styleUrls: ['capture-form-individuals.component.scss'],
  standalone: false,
})
export class CaptureFormIndividualsComponent {
  public additionalFieldsForm: Array<any> = [];
  public form_group: FormGroup = new FormGroup({
    cd_nom: new FormControl<any>(null, Validators.required),
    individuals: new FormControl<any[]>([]),
    media: new FormControl<any[]>([]),
    additional_fields: new FormControl<any[]>([]),
    individuals_captured: new FormArray([]),
  });

  constructor(
    public config: ConfigService,
    private _moduleService: ModuleService
  ) {}

  get individualsCaptured(): FormArray {
    return this.form_group.get('individuals_captured') as FormArray;
  }

  get idModule(): number {
    return this._moduleService.currentModule?.id_module;
  }

  removeIndividualCaptured(index: number): void {
    this.individualsCaptured.removeAt(index);
  }

  public individualFieldLabels: Record<string, string> = {
    individual_name: 'Individuals.Individuals.Fields.individual_name',
    cd_nom: 'Individuals.Individuals.Filters.cd_nom',
    id_nomenclature_sex: 'Individuals.Individuals.Fields.nomenclature_sex_name',
    active: 'Individuals.Individuals.Fields.active',
    comment: 'Individuals.Individuals.Fields.comment',
  };

  // Keeps the FormGroup's own field order instead of the keyvalue pipe's default alphabetical sort.
  public keepFieldOrder(): number {
    return 0;
  }

  getIndividualFieldValue(value: any): string {
    if (value === null || value === undefined || value === '') {
      return '-';
    }
    if (typeof value === 'boolean') {
      return value ? 'Oui' : 'Non';
    }
    if (typeof value === 'object') {
      return value.nom_valide ?? value.label_fr ?? value.individual_name ?? JSON.stringify(value);
    }
    return value;
  }
}
