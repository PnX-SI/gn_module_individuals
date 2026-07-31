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
import { InputTextComponent } from './components/input/input-text.component';
import { TextareaComponent } from './components/input/textarea.component';
import { InputRadioComponent } from './components/input/input-radio.component';

import { DevicesService } from './services/devices.service';
import { DevicesResolver, DeviceResolver } from './resolvers/devices.resolver';
import { DevicesListComponent } from './components/devices-list/devices-list.component';
import { DevicesFiltersComponent } from './components/devices-list/devices-filters.component';
import { DevicesFormComponent } from './components/devices-form/devices-form.component';
import { DevicesInfoComponent } from './components/devices-info/devices-info.component';

import { IndividualsService } from './services/individuals.service';
import {
  IndividualsMapResolver,
  IndividualsResolver,
  IndividualResolver,
} from './resolvers/individuals.resolver';
import { IndividualsMapListComponent } from './components/individuals-map-list/individuals-map-list.component';
import { IndividualsFiltersComponent } from './components/individuals-map-list/individuals-filters.component';
import { IndividualsInfoComponent } from './components/individuals-info/individuals-info.component';
import { IndividualsFormComponent } from './components/individuals-form/individuals-form.component';

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
    InputTextComponent,
    TextareaComponent,
    InputRadioComponent,
    DeleteModalComponent,
    DevicesListComponent,
    DevicesFiltersComponent,
    DevicesInfoComponent,
    DevicesFormComponent,
    IndividualsMapListComponent,
    IndividualsFiltersComponent,
    IndividualsInfoComponent,
    IndividualsFormComponent,
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
    IndividualsMapResolver,
    IndividualResolver,
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
