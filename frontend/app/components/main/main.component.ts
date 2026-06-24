import { Component, OnInit } from '@angular/core';
import { ConfigService } from '@geonature/services/config.service';

@Component({
  selector: 'gn-module-main',
  templateUrl: 'main.component.html',
  styleUrls: ['main.component.scss'],
  standalone: false,
})
export class MainComponent implements OnInit {
  constructor(private config: ConfigService) {}

  ngOnInit() {}
}
