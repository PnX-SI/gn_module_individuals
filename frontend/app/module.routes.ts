import { Routes } from '@angular/router';

import { MainComponent } from './components/main/main.component';
import { MapListComponent } from './components/map-list/map-list.component';

import { DevicesListComponent } from './components/devices-list/devices-list.component';
import { DevicesInfoComponent } from './components/devices-info/devices-info.component';
import { DevicesFormComponent } from './components/devices-form/devices-form.component';
import { DevicesResolver, DeviceResolver } from './resolvers/devices.resolver';

import { IndividualsMapListComponent } from './components/individuals-map-list/individuals-map-list.component';
import {
  IndividualsResolver,
  IndividualsMapResolver,
  IndividualResolver,
} from './resolvers/individuals.resolver';
import { IndividualsInfoComponent } from './components/individuals-info/individuals-info.component';
import { IndividualsFormComponent } from './components/individuals-form/individuals-form.component';

export const routes: Routes = [
  {
    path: '',
    component: MainComponent,
    children: [
      {
        path: '',
        redirectTo: 'individuals',
        pathMatch: 'full',
      },
      {
        path: 'individuals',
        component: IndividualsMapListComponent,
        resolve: {
          datatable: IndividualsResolver,
          mapData: IndividualsMapResolver,
        },
      },
      {
        path: 'individuals/info/:id_individual',
        component: IndividualsInfoComponent,
        resolve: { datatable: IndividualResolver },
      },
      {
        path: 'individuals/form',
        component: IndividualsFormComponent,
      },
      {
        path: 'individuals/form/:id_individual',
        component: IndividualsFormComponent,
        resolve: { datatable: IndividualResolver },
      },
      {
        path: 'observations',
        component: MapListComponent,
      },
      {
        path: 'captures',
        component: MapListComponent,
      },
      {
        path: 'devices',
        component: DevicesListComponent,
        resolve: { datatable: DevicesResolver },
      },
      {
        path: 'devices/form',
        component: DevicesFormComponent,
      },
      {
        path: 'devices/form/:id_tracking_device',
        component: DevicesFormComponent,
        resolve: { datatable: DeviceResolver },
      },
      {
        path: 'devices/info/:id_tracking_device',
        component: DevicesInfoComponent,
        resolve: { datatable: DeviceResolver },
      },
    ],
  },
];
