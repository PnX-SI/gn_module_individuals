import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterModule } from '@angular/router';

@Component({
  standalone: true,
  templateUrl: 'individual-list.component.html',
  styleUrls: ['individual-list.component.scss'],
  imports: [CommonModule, RouterModule],
})

export class IndividualListComponent implements OnInit {
  
  constructor() {}

  ngOnInit() {}


}