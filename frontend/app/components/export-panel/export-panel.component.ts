import { Component, OnInit, Input, Output, EventEmitter } from '@angular/core';

@Component({
  selector: 'gn-individuals-export-panel',
  templateUrl: 'export-panel.component.html',
  styleUrls: ['export-panel.component.scss'],
  standalone: false,
})
export class ExportPanelComponent implements OnInit {
  /**
   * Export formats offered to the user (e.g. ['csv', 'geojson', 'gpkg'])
   */
  @Input() exportFormats: string[] = [];
  /**
   * Emits the chosen format when the user confirms the download.
   */
  @Output() export: EventEmitter<string> = new EventEmitter();

  public selectedExportFormat: string | null = null;

  ngOnInit(): void {
    // Default the selection to the first configured format so the
    // "Télécharger" button is usable right away
    this.selectedExportFormat = this.exportFormats[0] ?? null;
  }

  /**
   * Emit the export event with the currently selected format.
   *
   * @memberof ExportPanelComponent
   */
  onExport(): void {
    if (!this.selectedExportFormat) {
      return;
    }
    this.export.emit(this.selectedExportFormat);
  }
}
