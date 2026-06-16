import { ViewEncapsulation, Component, OnInit, ViewChild, 
  AfterViewInit, EventEmitter, Output, Input, TemplateRef,
  HostListener
} from '@angular/core';
import { TranslateService } from '@ngx-translate/core';
import { ActivatedRoute } from '@angular/router';
import { Subject, Observable, combineLatest, of } from 'rxjs';
import { debounceTime } from 'rxjs/operators';

import { DatatableComponent } from '@swimlane/ngx-datatable';
import {NgbModal} from '@ng-bootstrap/ng-bootstrap';

import { ConfigService } from '@geonature/services/config.service';
import { ModuleService } from '@geonature/services/module.service';

import { CONTENT_CONFIG, DATA_TABLE_CONFIG } from '../../utils/constants.util';
import { calcContentHeight, calcRowNumber} from '../../utils/functions.utils';
import { Column, PaginatedItemCollection } from '../../models/common.models';

@Component({
  selector: 'gn-individuals-list',
  templateUrl: 'list.component.html',
  styleUrls: ['list.component.scss'],
  encapsulation: ViewEncapsulation.None,
})
export class ListComponent implements OnInit, AfterViewInit {
  // ViewChild : To be visible dynamicaly in the parent component linked with the #dataTable reference in the child template
  @ViewChild("dataTable") dataTable: DatatableComponent | undefined;
  @Output() pagination: EventEmitter<any> = new EventEmitter();
  @Output() sort: EventEmitter<any> = new EventEmitter();
  @Output() rows: EventEmitter<any> = new EventEmitter();
  @Output() select: EventEmitter<any> = new EventEmitter();
  @Input() availableColumnsParams!: Record<keyof any, true>;
  @Input() displayedColumnsParams: string[] = [];
  @Input() dataTable$: Observable<PaginatedItemCollection<unknown>> = new Observable<PaginatedItemCollection<unknown>>();
  @Input() sorts: Array<Object> = [];
  @Input() idName: string = "";
  @Input() summaryTemplate!: TemplateRef<any>;
  @Input() objectName: string = "";
  
  private _resizeWindow$ = new Subject<void>();
  public contentHeight: number = CONTENT_CONFIG.MIN_HEIGHT;
  public rowHeight: number = DATA_TABLE_CONFIG.TABLE_ROW_HEIGHT;
  public nbRowsToDisplay: number = DATA_TABLE_CONFIG.PER_PAGE_OPTION;
  public actionColumnsWidth: number = DATA_TABLE_CONFIG.ACTION_COLUMNS_WIDTH;
  public columnMaxWidth: number = DATA_TABLE_CONFIG.COLUMN_MAX_WIDTH;
  public displayedColumns!: Column<undefined>[];
  public availableColumns!: Column<undefined>[];
  public moduleName: string = this._moduleService.currentModule.module_url;

  constructor(
    public config: ConfigService,
    private _translate: TranslateService,
    private _activatedRoute: ActivatedRoute,
    private _moduleService: ModuleService,
    private _ngbModal: NgbModal,
  ) {}

  ngOnInit() : void {
    this._activatedRoute.data.subscribe(({data}) => {
      this.dataTable$ = of(data);
    });

    // Columns initialization with prop and empty name, to be filled with translations after
    this.availableColumns = (Object.keys(this.availableColumnsParams) as (keyof undefined)[])
      .map(prop => ({ prop, name: '' }));
    
    this.displayedColumns = this.availableColumns.filter(column =>
       this.displayedColumnsParams.includes(column.prop)
    );

    // // Build an array of translation observables for each column name
    const translateTab$ = this.availableColumns.map(
        // An observable is returned which emits the translation of this key
        column => this._translate.get(`Individuals.Devices.Fields.${column.prop}`)
    );

    // Translation with CombineLatest will wait for all translations to be loaded before updating 
    // the column names, avoiding multiple updates and ensuring all names are translated at once.
    combineLatest(translateTab$)
      .subscribe(translations => {
        this.availableColumns = this.availableColumns.map((col, index) => ({
          ...col,
          name: translations[index]
        }));
        
        // Update displayedColumns with the translated names
        this.displayedColumns = this.displayedColumns.map(col =>
          ({ ...col, name: this.availableColumns.find(c => c.prop === col.prop)?.name || '' })
        );
      });

    this._resizeWindow$
      .pipe(debounceTime(300))
      .subscribe(() => {
        this.contentHeight = calcContentHeight();
        this.nbRowsToDisplay = calcRowNumber(this.contentHeight);
        this.sendRowNumber();
      });
  }

  ngAfterViewInit() : void {
  }

  // Listen to window resize event to recalculate the content height and resize the map
  @HostListener('window:resize', ['$event'])
  onResize($event: any) : void {
    this._resizeWindow$.next();
  }

  onPage($event: any) : void {
    this.pagination.emit($event);
  }

  onSort($event: any) : void {
    this.sort.emit($event);
  }

  sendRowNumber() {
    this.rows.emit(this.nbRowsToDisplay);
  }

  toggleExpandRow(row: any) : void {
    if (this.dataTable) {
      this.dataTable.rowDetail.toggleExpandRow(row);
    }
  }

  openDeleteModal(event, modal, iElement, row) {
    // this.mapListService.urlQuery;
    // this.mapListService.selectedRow = [];
    // this.mapListService.selectedRow.push(row);
    // event.stopPropagation();
    // // prevent erreur link to the component
    // iElement?.parentElement?.parentElement?.blur();
    // this._ngbModal.open(modal);
  }
}


