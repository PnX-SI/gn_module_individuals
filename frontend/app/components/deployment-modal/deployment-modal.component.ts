import { Component, Output, EventEmitter, Input, OnInit } from '@angular/core';
import { FormGroup, FormBuilder } from '@angular/forms';
import { DeploymentsService } from '../../services/deployments.service';
import { NgbActiveModal } from '@ng-bootstrap/ng-bootstrap';

import { CommonService } from '@geonature_common/service/common.service';
import { ErrorHandlerService } from '../../services/errors-handler.service';

@Component({
  selector: 'gn-individuals-deployment-modal',
  templateUrl: './deployment-modal.component.html',
  standalone: false,
})
export class DeploymentModalComponent implements OnInit {
  @Input() deployment;
  @Output() onSave = new EventEmitter();
  public form!: FormGroup;
  
  constructor(
    public _activeModal: NgbActiveModal,
    private _deploymentsService: DeploymentsService,
    private _commonService: CommonService,
    private _errorHandler: ErrorHandlerService,
    private _fb: FormBuilder
  ) {}

  ngOnInit() {
    this.form = this._deploymentsService.generateDeploymentForm();
    this.form.patchValue(this.deployment);
  }
  cancelCreate() {
    this._activeModal.close();
  }
  createDeployment() {
    const formAction = this.deployment.id_deployment ? 'EDIT' : 'ADD';
    this._deploymentsService
      .createOrUpdateDeployment(this.form.value, formAction, this.deployment.id_deployment)
      .subscribe({
        next: (res) => {
          const successKey =
            formAction === 'ADD'
              ? 'Individuals.Deployments.Messages.Added'
              : 'Individuals.Deployments.Messages.Edited';
          this._commonService.translateToaster('info', successKey, { id: res.id_deployment });
          this.form.markAsPristine();
          this.onSave.emit(this.form.value);
          this._activeModal.close();
        },
        error: (err) => {
          this._errorHandler.handleHttpError(
            err,
            { id: this.form.value.id_deployment },
            'Individuals.Deployments.ApiErrors'
          );
        },
      });
  }
}
