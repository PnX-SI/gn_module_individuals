import { Component, Output, EventEmitter, Input, OnInit } from '@angular/core';
import { FormControl, FormGroup, FormBuilder } from '@angular/forms';
import { DeployementsService } from '../../services/deployments.service';
import { NgbActiveModal } from '@ng-bootstrap/ng-bootstrap';
@Component({
  selector: 'pnx-individuals-deployment-modal',
  templateUrl: './deployment-modal.component.html',
})
export class DeploymentModalComponent implements OnInit {
  @Input() deployment;
  @Output() onSave = new EventEmitter();
  public form!: FormGroup;

  constructor(
    public _activeModal: NgbActiveModal,
    private _deploymentsService: DeployementsService,
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
    console.log('deployment', this.form.value);
    this._deploymentsService
      .createOrUpdateDeployment(
        this.form.value,
        this.deployment.id_deployment ? 'EDIT' : 'ADD',
        this.deployment.id_deployment
      )
      .subscribe(() => {
        this.onSave.emit(this.form.value);
        this._activeModal.close();
      });
    // TODO CATCH exception
  }
}
