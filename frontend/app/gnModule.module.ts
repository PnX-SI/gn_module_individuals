import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterModule } from '@angular/router';
import { HttpClient, HttpClientXsrfModule } from '@angular/common/http';
import { NgbModule } from '@ng-bootstrap/ng-bootstrap';

import { GN2CommonModule } from '@geonature_common/GN2Common.module';
import { ConfigService as cs } from '@geonature/services/config.service';
import { CustomTranslateLoader } from '@geonature/shared/translate/custom-loader';
import { TranslateModule, TranslateLoader, TranslateService } from '@ngx-translate/core';
import { I18nService } from '@geonature/shared/translate/i18n-service';

import { routes } from './module.routes';

import { ErrorHandlerService } from './services/errors-handler.service';
import { MainComponent } from './components/main/main.component';

import { MapListComponent } from './components/map-list/map-list.component';
import { ListComponent } from './components/list/list.component';
import { InfoComponent } from './components/info/info.component';
import { DeleteModalComponent } from './components/delete-modal/delete-modal.component';
import { FormComponent } from './components/form/form.component';
import { FormInputTextComponent } from './components/form/form-input-text.component';
import { FormTextareaComponent } from './components/form/form-textarea.component';

import { DevicesService } from './services/devices.service';
import { DevicesResolver, DeviceResolver } from './resolvers/devices.resolver';
import { DevicesListComponent } from './components/devices-list/devices-list.component';
import { DevicesListFiltersComponent } from './components/devices-list/devices-list-filters.component';
import { DevicesFormComponent } from './components/devices-form/devices-form.component';
import { DevicesInfoComponent } from './components/devices-info/devices-info.component';

import { IndividualsMapListComponent } from './components/individuals-map-list/individuals-map-list.component';
import { IndividualsService } from './services/individuals.service';
import { IndividualsMapResolver, IndividualsResolver } from './resolvers/individuals.resolver';

export function createTranslateLoader(http: HttpClient, config: cs) {
  return new CustomTranslateLoader(http, config, { moduleName: 'individuals' });
}
@NgModule({
  declarations: [
    MainComponent,
    ListComponent,
    MapListComponent,
    InfoComponent,
    FormComponent,
    FormInputTextComponent,
    FormTextareaComponent,
    DeleteModalComponent,
    DevicesListComponent,
    DevicesListFiltersComponent,
    DevicesInfoComponent,
    DevicesFormComponent,
    IndividualsMapListComponent,
  ],
  imports: [
    HttpClientXsrfModule.withOptions({
      cookieName: 'token',
      headerName: 'token',
    }),
    CommonModule,
    GN2CommonModule,
    NgbModule,
    RouterModule.forChild(routes),
    TranslateModule.forChild({
      loader: {
        provide: TranslateLoader,
        useFactory: createTranslateLoader,
        deps: [HttpClient, cs],
      },
      isolate: true,
    }),
  ],
  providers: [
    ErrorHandlerService,
    DevicesService,
    DevicesResolver,
    DeviceResolver,
    IndividualsService,
    IndividualsResolver,
    IndividualsMapResolver
  ],
})
export class GeonatureModule {
  constructor(
    private translateService: TranslateService,
    private i18nService: I18nService
  ) {
    // Workaround to force translation loaded for LazyModule.
    // See: https://github.com/ngx-translate/core/issues/1302
    this.i18nService.initializeModuleTranslateService(this.translateService);
  }
}
