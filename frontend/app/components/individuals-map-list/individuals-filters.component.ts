import {
  ViewEncapsulation,
  Component,
  OnInit,
  OnDestroy,
  Output,
  Input,
  EventEmitter,
} from '@angular/core';
import { FormBuilder, FormGroup, Validators } from '@angular/forms';
import { Subject } from 'rxjs';
import { debounceTime, distinctUntilChanged, takeUntil } from 'rxjs/operators';

import { ConfigService } from '@geonature/services/config.service';

import { FormConstraint } from '../../models/common.models';
import { APIIndividualFiltersParams } from '../../models/individuals.models';
import { INDIVIDUALS_FORM_CONSTRAINTS } from '../../utils/constants.util';

@Component({
  selector: 'gn-individuals-individuals-filters',
  templateUrl: 'individuals-filters.component.html',
  styleUrls: ['individuals-filters.component.scss'],
  encapsulation: ViewEncapsulation.None,
  standalone: false,
})
export class IndividualsFiltersComponent implements OnInit, OnDestroy {
  @Output() filters = new EventEmitter<{key: keyof APIIndividualFiltersParams; value: string | number | undefined;} | null>();
  @Input() defaultValues: APIIndividualFiltersParams = {};

  public filtersForm!: FormGroup;
  public formConstraints: Record<string, FormConstraint> = INDIVIDUALS_FORM_CONSTRAINTS;
  public taxonListId: string = this._config.INDIVIDUALS.GLOBAL.ID_TAXON_LIST;
  private _destroy$ = new Subject<void>();

  constructor(
    private _config: ConfigService,
    private _fb: FormBuilder
  ) {}

  ngOnInit(): void {
    // Form initialization
    console.log("default filters values",this.defaultValues);
    this.filtersForm = this._fb.group({
      active: [this.defaultValues?.active, null],
      cd_nom: [null, null],
      id_nomenclature_sex: [null, null],
      individual_name: [null,[Validators.pattern(this.formConstraints.individual_name.pattern)]],
    });

    // Call API on change event
    Object.keys(this.filtersForm.controls).forEach((field) => {
      this.filtersForm
        .get(field)
        ?.valueChanges.pipe(
          debounceTime(500),
          distinctUntilChanged(), // Ignore equals consecutives value
          takeUntil(this._destroy$)
        )
        .subscribe((value) => {
          this.filters.emit({ key: field, value: value?.id_role ?? value?.cd_nom ?? value });
        });
    });
  }

  onResetFilters() {
    this.filtersForm.reset();
    this.filters.emit(null);
  }

  ngOnDestroy() {
    this._destroy$.next();
    this._destroy$.complete();
  }
}
