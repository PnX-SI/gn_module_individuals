import {
  ViewEncapsulation,
  Component,
  OnInit,
  OnDestroy,
  Output,
  EventEmitter,
} from '@angular/core';
import { FormBuilder, FormGroup, Validators } from '@angular/forms';
import { Subject } from 'rxjs';
import { debounceTime, distinctUntilChanged, takeUntil } from 'rxjs/operators';

import { ConfigService } from '@geonature/services/config.service';

import { FormConstraint } from '../../models/common.models';
import { APIDeviceFiltersParams } from '../../models/devices.models';
import { DEVICE_FORM_CONSTRAINTS } from '../../utils/constants.util';

@Component({
  selector: 'gn-individuals-devices-filters',
  templateUrl: 'devices-filters.component.html',
  styleUrls: ['devices-filters.component.scss'],
  encapsulation: ViewEncapsulation.None,
  standalone: false,
})
export class DevicesFiltersComponent implements OnInit, OnDestroy {
  @Output() filters = new EventEmitter<{
    key: keyof APIDeviceFiltersParams;
    value: string | number | undefined;
  } | null>();
  public filtersForm!: FormGroup;
  public formConstraints: Record<string, FormConstraint> = DEVICE_FORM_CONSTRAINTS;
  public taxonListId: string = this._config.INDIVIDUALS.GLOBAL.ID_TAXON_LIST;
  private _destroy$ = new Subject<void>();

  constructor(
    private _config: ConfigService,
    private _fb: FormBuilder
  ) {}

  ngOnInit(): void {
    // Form initialization
    this.filtersForm = this._fb.group({
      cd_nom: [null, null],
      id_nomenclature_device_type: [null, null],
      provider_name: [null, [Validators.pattern(this.formConstraints.provider_name.pattern)]],
      id_referer: [null, null],
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

          // Emit to IndividualsMapList
          // If the value comes from pnx-taxonomy, get the value.cd_nom
          // If the value comes from pnx-observers, get the value.id_role
          // Else get the value
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
