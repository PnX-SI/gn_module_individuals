import { Component, OnInit } from '@angular/core';
import { ActivatedRoute } from '@angular/router';
import { Location } from '@angular/common';
import { UntypedFormGroup, Validators, FormGroup, FormControl } from '@angular/forms';

import { CommonService } from '@geonature_common/service/common.service';

import { CaptureService } from '../../../services/capture.service';
import { ErrorHandlerService } from '../../../services/errors-handler.service';
import { Capture } from '../../../models/capture.model';

@Component({
  selector: 'gn-individuals-capture-form',
  templateUrl: 'capture-form.component.html',
  styleUrls: ['capture-form.component.scss'],
  standalone: false,
})
export class CaptureFormComponent implements OnInit {
  public captureId!: number;
  public formAction: 'ADD' | 'EDIT' = 'ADD';

  public form_group: UntypedFormGroup = new FormGroup({
    id_nomenclature_protocole: new FormControl<number | null>(null, Validators.required),
    comment: new FormControl<string>(''),
    date: new FormControl<any>(Date.now(), Validators.required),
    observers: new FormControl<any>([]),
  });

  constructor(
    private _route: ActivatedRoute,
    private _commonService: CommonService,
    private _captureService: CaptureService,
    private _location: Location,
    private _errorHandler: ErrorHandlerService
  ) {}

  ngOnInit(): void {
    this._route.data.subscribe(({ data }: { data: Capture }) => {
      if (data && data.id_capture) {
        this.captureId = data.id_capture;
        this.formAction = 'EDIT';
        this.patchForm(data);
      } else {
        this.formAction = 'ADD';
      }
    });
  }

  patchForm(capture: Capture): void {
    this.form_group.patchValue(capture);
  }

  onSave(): void {
    const capture = this.form_group.getRawValue();

    this._captureService
      .createOrUpdateCapture(
        capture,
        this.formAction === 'EDIT' ? 'UPDATE' : 'CREATE',
        this.captureId
      )
      .subscribe({
        next: () => {
          const successKey =
            this.formAction === 'ADD'
              ? 'Individuals.Captures.Messages.Added'
              : 'Individuals.Captures.Messages.Edited';
          this._commonService.translateToaster('info', successKey, { id: this.captureId });
          this.form_group.markAsPristine();
          this._location.back();
        },
        error: (err) => {
          this._errorHandler.handleHttpError(
            err,
            { id: this.captureId },
            'Individuals.Captures.ApiErrors'
          );
        },
      });
  }

  onCancel(): void {
    this._location.back();
  }
}
