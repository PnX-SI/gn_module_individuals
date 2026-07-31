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
import { Observable, combineLatest, of } from 'rxjs';
import { DatatableComponent, SelectionType } from '@swimlane/ngx-datatable';

import { ModuleService } from '@geonature/services/module.service';

import { CONTENT_CONFIG, DATATABLE_CONFIG } from '../../utils/constants.util';
import { Column, PaginatedItemCollection, AccessResult } from '../../models/common.models';

@Component({
  selector: 'gn-individuals-list',
  templateUrl: 'list.component.html',
  styleUrls: ['list.component.scss'],
  encapsulation: ViewEncapsulation.None, // SCSS used only in this component and not in the global CSS
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
  @Input() availableColumnsParams!: Record<string, unknown>;
  @Input() displayedColumnsParams: string[] = [];
  @Input() dataTable$: Observable<PaginatedItemCollection<unknown>> = of();
  @Input() nbRowsToDisplay: number = DATATABLE_CONFIG.PER_PAGE_OPTION;
  @Input() fieldsTranslation: string = '';
  @Input() sorts: Array<Object> = [];
  @Input() allowedToEdit: Record<number, AccessResult> = {};
  @Input() allowedToDelete: Record<number, AccessResult> = {};
  @Input() summaryTemplate!: TemplateRef<any>;
  @Input() filtersTemplate!: TemplateRef<any>;
  @Input() selectedRows: unknown[] = [];

  public contentHeight: number = CONTENT_CONFIG.MIN_HEIGHT;
  public rowHeight: number = DATATABLE_CONFIG.TABLE_ROW_HEIGHT;
  public actionColumnsWidth: number = DATATABLE_CONFIG.ACTION_COLUMNS_WIDTH;
  public columnMaxWidth: number = DATATABLE_CONFIG.COLUMN_MAX_WIDTH;
  public displayedColumns!: Column[];
  public moduleName: string = this._moduleService.currentModule.module_url;
  public selectionType = SelectionType;
  public tableMessages = {};

  public showFilters: boolean = false;

  constructor(
    private _translate: TranslateService,
    private _moduleService: ModuleService
  ) {}

  ngOnInit(): void {
    if (!this.availableColumnsParams) {
      return;
    }

    // ngx-datatable messages translation
    this._translate
      .get(['Individuals.Messages.EmptyList', 'Individuals.Messages.TotalList'])
      .subscribe((translations) => {
        this.tableMessages = {
          emptyMessage: translations['Individuals.Messages.EmptyList'],
          totalMessage: translations['Individuals.Messages.TotalList'],
          selectedMessage: '',
        };
      });

    const availableColumns = Object.keys(this.availableColumnsParams).map((prop) => ({
      prop,
      name: '',
    }));

    this.displayedColumns = this.displayedColumnsParams
      .map((prop) => availableColumns.find((column) => column.prop === prop))
      .filter((column): column is Column => column !== undefined);

    if (this.displayedColumns.length === 0) {
      return;
    }

    combineLatest(
      // Translate the displayed column labels.
      this.displayedColumns.map((column) =>
        // An observable is returned which emits the translation of this key
        this._translate.get(`${this.fieldsTranslation}.${column.prop}`)
      )
    ).subscribe((labels) => {
      this.displayedColumns = this.displayedColumns.map((column, index) => ({
        ...column,
        name: labels[index],
      }));
    });
  }

  /**
   * Emit a select event
   *
   * @param {*} $event Current row.
   * @memberof ListComponent
   */
  onSelect($event: any): void {
    this.select.emit($event);
  }
  /**
   * Emit a pagination event
   *
   * @param {*} $event
   * @memberof ListComponent
   */
  onPage($event: any): void {
    this.pagination.emit($event);
  }

  /**
   * Emit a sort event
   *
   * @param {*} $event
   * @memberof ListComponent
   */
  onSort($event: any): void {
    this.sort.emit($event);
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
   * Expand or not the row detail
   *
   * @param {*} row
   * @memberof ListComponent
   */
  toggleExpandRow(row: any): void {
    if (this.dataTable) {
      this.dataTable.rowDetail.toggleExpandRow(row);
    }
    this.selectedRows = [row];
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
