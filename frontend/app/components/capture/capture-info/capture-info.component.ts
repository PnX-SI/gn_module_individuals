import { Component, Input } from '@angular/core';
import { Capture } from '../../../models/capture.model';

@Component({
  selector: 'gn-individuals-capture-info',
  templateUrl: 'capture-info.component.html',
  styleUrls: ['capture-info.component.scss'],
  standalone: false,
})
export class CaptureInfoComponent {
  @Input() capture: Capture;
}
