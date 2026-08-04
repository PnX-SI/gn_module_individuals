import {
  ViewEncapsulation,
  Component,
  OnInit,
  OnDestroy,
  Output,
  Input,
  EventEmitter,
} from '@angular/core';
import { FormBuilder, FormGroup } from '@angular/forms';
import { Subject } from 'rxjs';
import { debounceTime, distinctUntilChanged, takeUntil } from 'rxjs/operators';

import { APICaptureFiltersParams } from '../../../models/capture.model';

@Component({
  selector: 'gn-individuals-capture-filters',
  templateUrl: 'capture-filters.component.html',
  styleUrls: ['capture-filters.component.scss'],
  encapsulation: ViewEncapsulation.None,
  standalone: false,
})
export class CaptureFiltersComponent implements OnInit, OnDestroy {
  @Output() filters = new EventEmitter<{
    key: keyof APICaptureFiltersParams;
    value: string | number | undefined;
  } | null>();
  @Input() defaultValues: APICaptureFiltersParams = {};

  public filtersForm!: FormGroup;
  private _destroy$ = new Subject<void>();

  constructor(private _fb: FormBuilder) {}

  ngOnInit(): void {
    this.filtersForm = this._fb.group({
      id_nomenclature_protocole: [this.defaultValues?.id_nomenclature_protocole ?? null, null],
      date: [this.defaultValues?.date ?? null, null],
      id_role: [null, null],
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
          // Emit a change only if filtersForm change due to user action : genericForm.component emit
          // changes when it call setValue()
          if (!this.filtersForm.get(field)?.dirty) {
            return;
          }

          // Emit to CaptureList :
          // If the value comes from pnx-observers, get the value.id_role
          // Else get the value
          this.filters.emit({
            key: field as keyof APICaptureFiltersParams,
            value: value?.id_role ?? value,
          });
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
