import { NgbModule } from '@ng-bootstrap/ng-bootstrap';

import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterModule } from '@angular/router';
import { GN2CommonModule } from '@geonature_common/GN2Common.module';

import { HttpClient } from '@angular/common/http';
import { HttpClientXsrfModule } from '@angular/common/http';

import { ConfigService as cs } from '@geonature/services/config.service';

import { CustomTranslateLoader } from '@geonature/shared/translate/custom-loader';
import { TranslateModule, TranslateLoader, TranslateService } from '@ngx-translate/core';
import { I18nService } from '@geonature/shared/translate/i18n-service';

import { routes } from './module.routes';
import { MainComponent } from './components/main/main.component';
import { DevicesService } from './services/devices.service';
import { DeviceResolver } from './resolvers/devices.resolver';
import { DevicesResolver } from './resolvers/devices.resolver';
import { MapListComponent } from './components/map-list/map-list.component';
import { ListComponent } from './components/list/list.component';
import { DevicesListComponent } from './components/devices-list/devices-list.component';
import { FormComponent } from './components/form/form.component';
import { DevicesFormComponent } from './components/devices-form/devices-form.component';
import { InfoComponent } from './components/info/info.component';
import { DevicesInfoComponent } from './components/devices-info/devices-info.component';

export function createTranslateLoader(http: HttpClient, config: cs) {
  return new CustomTranslateLoader(http, config, { moduleName: 'individuals' });
}
@NgModule({
  declarations: [
    MainComponent,
    MapListComponent,
    ListComponent,
    DevicesListComponent,
    FormComponent,
    DevicesFormComponent,
    InfoComponent,
    DevicesInfoComponent
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
    DevicesService,
    DevicesResolver,
    DeviceResolver
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
