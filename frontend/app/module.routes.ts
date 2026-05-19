import { Routes } from '@angular/router';

import { MainComponent,  } from './components/main/main.component';
import { MapListComponent } from './components/map-list/map-list.component';
import { DevicesListComponent } from './components/devices-list/devices-list.component';
import { DevicesInfoComponent } from './components/devices-info/devices-info.component';
import { DevicesResolver, DeviceResolver } from './resolvers/devices.resolver';

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
                resolve:{ data: DevicesResolver },  
            },
            {
                path: 'devices/info/:id_tracking_device',
                component: DevicesInfoComponent,
                resolve:{ data: DeviceResolver },
            }
        ]
    }
];
