import {
  ViewEncapsulation,
  Component,
  OnInit,
  ViewChild,
  EventEmitter,
  Output,
  Input,
  TemplateRef,
} from '@angular/core';
import { TranslateService } from '@ngx-translate/core';
import { ActivatedRoute } from '@angular/router';
import { Observable, combineLatest, of } from 'rxjs';
import { DatatableComponent, SelectionType } from '@swimlane/ngx-datatable';

import { ConfigService } from '@geonature/services/config.service';
import { ModuleService } from '@geonature/services/module.service';

import { CONTENT_CONFIG, DATA_TABLE_CONFIG } from '../../utils/constants.util';
import { Column, PaginatedItemCollection } from '../../models/common.models';

@Component({
  selector: 'gn-individuals-list',
  templateUrl: 'list.component.html',
  styleUrls: ['list.component.scss'],
  // SCSS used only in this component and not in the global CSS
  encapsulation: ViewEncapsulation.None,
  standalone: false,
})
export class ListComponent implements OnInit {
  // ViewChild : To be visible dynamicaly in the parent component linked with the #dataTable reference in the child template
  @ViewChild('dataTable') dataTable: DatatableComponent | undefined;
  @Output() pagination: EventEmitter<any> = new EventEmitter();
  @Output() sort: EventEmitter<any> = new EventEmitter();
  @Output() rows: EventEmitter<any> = new EventEmitter();
  @Output() select: EventEmitter<any> = new EventEmitter();
  @Output() delete: EventEmitter<any> = new EventEmitter();
  @Input() objectName: string = '';
  @Input() idFieldName: string = '';
  @Input() availableColumnsParams!: Record<keyof any, true>;
  @Input() displayedColumnsParams: string[] = [];
  @Input() dataTable$: Observable<PaginatedItemCollection<unknown>> = new Observable<
    PaginatedItemCollection<unknown>
  >();
  @Input() sorts: Array<Object> = [];
  @Input() allowedToEdit: boolean[] = [];
  @Input() allowedToDelete: Record<number, boolean> = {};
  @Input() summaryTemplate!: TemplateRef<any>;
  @Input() filtersTemplate!: TemplateRef<any>;

  public contentHeight: number = CONTENT_CONFIG.MIN_HEIGHT;
  public rowHeight: number = DATA_TABLE_CONFIG.TABLE_ROW_HEIGHT;
  public nbRowsToDisplay: number = DATA_TABLE_CONFIG.PER_PAGE_OPTION;
  public actionColumnsWidth: number = DATA_TABLE_CONFIG.ACTION_COLUMNS_WIDTH;
  public columnMaxWidth: number = DATA_TABLE_CONFIG.COLUMN_MAX_WIDTH;
  public displayedColumns!: Column<undefined>[];
  public availableColumns!: Column<undefined>[];
  public moduleName: string = this._moduleService.currentModule.module_url;
  public selectionType = SelectionType;
  public showFilters: boolean = false;

  constructor(
    public config: ConfigService,
    private _translate: TranslateService,
    private _activatedRoute: ActivatedRoute,
    private _moduleService: ModuleService
  ) {}

  ngOnInit(): void {
    this._activatedRoute.data.subscribe(({ data }) => {
      this.dataTable$ = of(data);
    });

    // Columns initialization with prop and empty name, to be filled with translations after
    this.availableColumns = (Object.keys(this.availableColumnsParams) as (keyof undefined)[]).map(
      (prop) => ({ prop, name: '' })
    );

    this.displayedColumns = this.availableColumns.filter((column) =>
      this.displayedColumnsParams.includes(column.prop)
    );

    // Build an array of translation observables for each column name
    const translateTab$ = this.availableColumns.map(
      // An observable is returned which emits the translation of this key
      (column) => this._translate.get(`Individuals.Devices.Fields.${column.prop}`)
    );

    // Translation with CombineLatest will wait for all translations to be loaded before updating
    // the column names, avoiding multiple updates and ensuring all names are translated at once.
    combineLatest(translateTab$).subscribe((translations) => {
      this.availableColumns = this.availableColumns.map((col, index) => ({
        ...col,
        name: translations[index],
      }));

      // Update displayedColumns with the translated names
      this.displayedColumns = this.displayedColumns.map((col) => ({
        ...col,
        name: this.availableColumns.find((c) => c.prop === col.prop)?.name || '',
      }));
    });
  }

  onPage($event: any): void {
    this.pagination.emit($event);
  }

  onSort($event: any): void {
    this.sort.emit($event);
  }

  toggleExpandRow(row: any): void {
    if (this.dataTable) {
      this.dataTable.rowDetail.toggleExpandRow(row);
    }
  }

  /**
   * Emit a delete event
   *
   * @param {*} $event Current row.
   * @memberof ListComponent
   */
  onDelete($event: any): void {
    this.delete.emit($event);
  }

  /**
   * Show the filters
   *
   * @memberof ListComponent
   */
  toggleShowFilters(): void {
    this.showFilters = !this.showFilters;
  }
}
