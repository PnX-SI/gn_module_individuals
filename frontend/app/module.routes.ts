import { Routes } from '@angular/router';

import { MainComponent,  } from './components/main/main.component';
import { MapListComponent } from './components/map-list/map-list.component';
import { ListComponent } from './components/list/list.component';

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
                component: MapListComponent, // To change
            },
                        {
                path: 'observations',
                component: MapListComponent, // To change
            },
                        {
                path: 'captures',
                component: MapListComponent, // To change
            },
            {
                path: 'devices',
                component: ListComponent,
            },
        ]
    }
];
