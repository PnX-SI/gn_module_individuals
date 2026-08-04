import { Component, Input } from '@angular/core';
import { Capture } from '../../../models/capture.model';
import { Individual } from '../../../models/individuals.models';
import { CaptureService } from '../../../services/capture.service';
import { ActivatedRoute } from '@angular/router';

const DUMMY_INDIVIDUAL: Individual = {
  id_individual: 1,
  uuid_individual: 'a1b2c3d4-e5f6-7890-abcd-ef1234567890',
  individual_name: 'Renard-01',
  cd_nom: 60015,
  id_nomenclature_sex: 1,
  active: true,
  comment: 'Individu capturé en bonne santé',
  id_digitiser: 1,
  meta_create_date: '2024-01-10T08:00:00',
  meta_update_date: '2024-01-10T08:00:00',
  digitiser_name: 'Jean Dupont',
  nomenclature_sex_name: 'Mâle',
  last_observation_date: '2024-06-15T10:30:00',
  last_observation_observers_name: 'Jean Dupont',
  taxref_nom_vern: 'Renard roux',
  taxref_lb_nom: 'Vulpes vulpes (Linnaeus, 1758)',
  taxref_cd_nom: '60015',
  deployed_markings: 'Boucle auriculaire n°42',
  deployed_devices: 'Collier GPS n°7',
  cruved: { C: true, R: true, U: true, V: true, E: true, D: false },
};

const DUMMY_CAPTURE: Capture = {
  id_capture: 1,
  id_nomenclature_protocole: 12,
  comment: 'Capture réalisée dans le cadre du suivi annuel de la population',
  date: new Date('2024-06-15T10:30:00'),
  geom: null,
  id_digitiser: 1,
  meta_create_date: new Date('2024-06-15T11:00:00'),
  meta_update_date: new Date('2024-06-16T09:15:00'),
  observers: [
    { id_role: 1, nom_complet: 'Jean Dupont' },
    { id_role: 2, nom_complet: 'Marie Martin' },
  ],
  individuals: [
    { individual: DUMMY_INDIVIDUAL, additional_data: { poids: '4.2kg', taille: '65cm' } },
  ],
};

@Component({
  selector: 'gn-individuals-capture-info',
  templateUrl: 'capture-info.component.html',
  styleUrls: ['capture-info.component.scss'],
  standalone: false,
})
export class CaptureInfoComponent {
  @Input() capture: Capture;

  constructor(
    private _captureService: CaptureService,
    private _route: ActivatedRoute
  ) {
    this._route.data.subscribe(({ capture }) => {
      this.capture = capture;
    });
  }
}
