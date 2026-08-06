import { Injectable } from '@angular/core';
import { Observable } from 'rxjs';
import { HttpHeaders, HttpClient } from '@angular/common/http';
import { FormBuilder, FormGroup, Validators } from '@angular/forms';
import { ConfigService } from '@geonature/services/config.service';
import { ModuleService } from '@geonature/services/module.service';

import { Deployment, CreateDeploymentDto, UpdateDeploymentDto } from '../models/deployments.models';

@Injectable()
export class DeployementsService {
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

  generateDeploymentForm(): FormGroup {
    return this._fb.group({
      comment: [null],
      id_deployment: [null],
      id_individual: [null],
      id_nomenclature_deployment_location: [null, Validators.required],
      id_nomenclature_deployment_type: [null, Validators.required],
      id_tracking_device: [null],
      install_date: [null, Validators.required],
      marking_code: [null],
      removal_date: [null],
      tracking_device_info: [null],
    });
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
    id: number | null = null,
    params: Record<string, string> = {}
  ): Observable<Deployment> {
    console.log('deployment', deployment);
    params['format'] = 'json';
    deployment = this.formToJson(deployment);
    // Map form to Dto
    let payload: CreateDeploymentDto | UpdateDeploymentDto = {
      id_tracking_device: deployment.id_tracking_device,
      id_individual: deployment.id_individual,
      id_nomenclature_deployment_type: deployment.id_nomenclature_deployment_type,
      id_nomenclature_deployment_location: deployment.id_nomenclature_deployment_location,
      marking_code: deployment.marking_code,
      install_date: deployment.install_date,
      removal_date: deployment.removal_date,
      comment: deployment.comment,
      id_digitiser: deployment.id_digitiser,
    };

    if (formAction === 'EDIT') {
      payload = {
        ...payload,
        id_deployment: deployment.id_deployment,
      };
    }
    if (formAction === 'ADD') {
      return this._http.post<Deployment>(`${this._OBJECT_API}`, payload, {
        params: params,
        headers: this._headers,
      });
    } else {
      return this._http.put<Deployment>(`${this._OBJECT_API}/${id}`, payload, {
        params: params,
        headers: this._headers,
      });
    }
  }
  
  deleteDeployment(id: number): Observable<Deployment> {
    return this._http.delete<Deployment>(`${this._OBJECT_API}/${id}`);
  }
}
