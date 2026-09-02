import { Injectable } from '@angular/core';
import { Observable, of } from 'rxjs';
import { HttpHeaders, HttpClient } from '@angular/common/http';
import { FormBuilder, FormGroup, Validators } from '@angular/forms';
import { ConfigService } from '@geonature/services/config.service';
import { ModuleService } from '@geonature/services/module.service';

import { Deployment, CreateDeploymentDto, UpdateDeploymentDto } from '../models/deployments.models';
import { AbstractControl, ValidationErrors, ValidatorFn } from '@angular/forms';
@Injectable()
export class DeploymentsService {
  private _OBJECT_API: string;
  // Désactive l'interceptor global (MyCustomInterceptor) pour que le composant
  // puisse afficher un toast traduit à partir du code d'erreur backend.
  private _headers = new HttpHeaders({ 'not-to-handle': 'true' });

  constructor(
    private _fb: FormBuilder,
    private _http: HttpClient,
    private _config: ConfigService,
    private _moduleService: ModuleService
  ) {
    this._OBJECT_API = `${this._config.API_ENDPOINT}/${this._moduleService.currentModule.module_url}/deployments`;
  }

  private dateRangeValidator: ValidatorFn = (group: AbstractControl): ValidationErrors | null => {
    const dateMin = group.get('install_date')?.value;
    const dateMax = group.get('removal_date')?.value;
    if (!dateMin || !dateMax) {
      return null;
    }
    return new Date(dateMin) <= new Date(dateMax) ? null : { invalidDateRange: true };
  };

  generateDeploymentForm(): FormGroup {
    const form = this._fb.group(
      {
        comment: [null],
        id_deployment: [null],
        id_individual: [null],
        id_nomenclature_deployment_location: [null, Validators.required],
        id_nomenclature_deployment_type: [null, Validators.required],
        id_tracking_device: [null],
        install_date: [null, Validators.required],
        marking_code: [null],
        removal_date: [null],
      },
      {
        validators: [this.dateRangeValidator],
      }
    );
    return form;
  }
  
  formToJson(deployment: any): any {
    if (deployment.id_tracking_device) {
      deployment.id_tracking_device = deployment.id_tracking_device.id_tracking_device;
    }
    return deployment;
  }

  createOrUpdateDeployment(
    deployment: any,
    formAction: string,
    params: Record<string, string> = {}
  ): Observable<Deployment> {
    params['format'] = 'json';
    
    // Map form to Dto
    let payload: CreateDeploymentDto | UpdateDeploymentDto = {
      id_individual: deployment.id_individual,
      id_tracking_device: deployment.id_tracking_device ? deployment.id_tracking_device.id_tracking_device : null,
      id_nomenclature_deployment_type: deployment.id_nomenclature_deployment_type,
      id_nomenclature_deployment_location: deployment.id_nomenclature_deployment_location,
      marking_code: deployment.marking_code < 0 ? null : deployment.marking_code,
      // If we cancel the date with the calendar, it becomes an empty string and not set to null
      install_date: deployment.install_date && deployment.install_date.length > 0 ? deployment.install_date : null,
      removal_date: deployment.removal_date && deployment.removal_date.length > 0 ? deployment.removal_date : null,
      comment: deployment.comment,
    };

    if (formAction === 'ADD') {
      return this._http.post<Deployment>(`${this._OBJECT_API}`, payload, {
        params: params,
        headers: this._headers,
      });
    } else {
      payload = {
        ...payload,
        id_deployment: deployment.id_deployment,
      };
      return this._http.put<Deployment>(`${this._OBJECT_API}/${deployment.id_deployment}`, payload, {
        params: params,
        headers: this._headers,
      });
    }
  }

  deleteDeployment(id: number): Observable<Deployment> {
    return this._http.delete<Deployment>(`${this._OBJECT_API}/${id}`);
  }
}
