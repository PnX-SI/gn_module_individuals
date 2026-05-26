import { Routes } from '@angular/router';

import { DevicesResolver } from './resolvers/devices.resolver';
import { MainComponent,  } from './components/main/main.component';
import { MapListComponent } from './components/map-list/map-list.component';
import { DevicesListComponent } from './components/devices-list/devices-list.component';
<<<<<<< HEAD
import { DevicesInfoComponent } from './components/devices-info/devices-info.component';
import { DevicesResolver, DeviceResolver } from './resolvers/devices.resolver';
=======
import { DevicesFormComponent } from './components/devices-form/devices-form.component';
>>>>>>> f889c9e (feat: Create form component architecture)

export const routes: Routes = [
    { 
        path: '', 
        component: MainComponent ,
        children: [
            { 
                path: '', 
                redirectTo: 'devices', // Next will be 'individuals'
                pathMatch: 'full'
            },
            {
                path: 'individuals',
                component: MapListComponent,
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
<<<<<<< HEAD
                resolve:{ data: DevicesResolver },  
=======
                resolve: { data: DevicesResolver }
            },
            {
                path: 'devices/form',
                component: DevicesFormComponent,
                // resolve: { data: DevicesResolver }
            },
            {
                path: 'devices/form/:id_tracking_device',
                component: DevicesFormComponent,
                // resolve: { data: DevicesResolver }
>>>>>>> f889c9e (feat: Create form component architecture)
            },
            {
                path: 'devices/info/:id_tracking_device',
                component: DevicesInfoComponent,
                resolve:{ data: DeviceResolver },
            }
        ]
    }
];
