import { Injectable } from '@angular/core';
import { HttpErrorResponse } from '@angular/common/http';
import { TranslateService } from '@ngx-translate/core';

import { CommonService } from '@geonature_common/service/common.service';

import { ApiError } from '../models/common.models';


/**
 * Traduit et affiche les erreurs HTTP du module individuals.
 *
 * Résolution de clé en deux niveaux :
 *   1. Clé spécifique à l'entité : `<entityPrefix>.<code>`
 *      ex. Individuals.Devices.ApiErrors.VALIDATION_ERROR
 *   2. Clé générique (fallback)  : `Individuals.ApiErrors.<code>`
 *
 * ngx-translate retourne la clé elle-même quand elle n'est pas trouvée,
 * ce comportement sert de signal de "traduction absente" pour décider
 * si on passe au fallback générique.
 */
@Injectable()
export class ErrorHandlerService {
  private readonly GENERIC_PREFIX = 'Individuals.ApiErrors';
  private readonly FALLBACK_KEY   = 'Individuals.ApiErrors.UNKNOWN_ERROR';

  constructor(
    private _commonService: CommonService,
    private _translateService: TranslateService,
  ) {}

  /**
   * @param err          Erreur HTTP Angular
   * @param params       Paramètres interpolés dans le message (ex. { id: 42 })
   * @param entityPrefix Préfixe de l'entité pour la clé spécifique
   *                     (ex. 'Individuals.Devices.ApiErrors')
   *                     Si absent, utilise uniquement le générique.
   */
  handleHttpError(
    err: HttpErrorResponse,
    params: Record<string, unknown> = {},
    entityPrefix?: string,
  ): void {
    const apiError = this._extractApiError(err);
    const mergedParams = { ...(apiError?.params ?? {}), ...params };
    const code     = apiError?.name ?? 'UNKNOWN_ERROR';
    const key      = this._resolveKey(code, mergedParams, entityPrefix);
    this._commonService.translateToaster('error', key, mergedParams);
  }

  private _resolveKey(
    code: string,
    params: Record<string, unknown>,
    entityPrefix?: string,
  ): string {
    if (entityPrefix) {
      const specificKey = `${entityPrefix}.${code}`;
      // instant() retourne la clé elle-même si la traduction est absente
      const resolved = this._translateService.instant(specificKey, params);
      if (resolved !== specificKey) {
        return specificKey;
      }
    }
    const genericKey = `${this.GENERIC_PREFIX}.${code}`;
    const resolved   = this._translateService.instant(genericKey, params);
    return resolved !== genericKey ? genericKey : this.FALLBACK_KEY;
  }

  private _extractApiError(err: HttpErrorResponse): ApiError | null {
    const body = err.error;
    if (body && typeof body === 'object' && 'name' in body && 'description' in body) {
      return body as ApiError;
    }
    return null;
  }
}
