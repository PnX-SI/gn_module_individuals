import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Routes, RouterModule } from '@angular/router';
import { HttpClientXsrfModule } from '@angular/common/http';
import { GN2CommonModule } from '@geonature_common/GN2Common.module';
import { NgbModule } from '@ng-bootstrap/ng-bootstrap';
import { IndividualListComponent } from './components/individual-list/individual-list.component';


export const routes: Routes = [
  {
    path: "",
    component: IndividualListComponent,
  },
];

@NgModule({
  imports: [
    HttpClientXsrfModule.withOptions({
      cookieName: 'token',
      headerName: 'token',
    }),
    CommonModule,
    GN2CommonModule,
    NgbModule,
    RouterModule.forChild(routes),
    // Module component
    
  ],
  providers: [],
  bootstrap: [],
})
export class GeonatureModule {}
