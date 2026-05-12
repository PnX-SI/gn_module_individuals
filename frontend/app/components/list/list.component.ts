import { ViewEncapsulation, Component, OnInit, ViewChild, AfterViewInit, HostListener, EventEmitter, Output, Input} from '@angular/core';
import { TranslateService } from '@ngx-translate/core';
import { ActivatedRoute } from '@angular/router';

import { Observable, combineLatest, of } from 'rxjs';

import { ConfigService } from '@geonature/services/config.service';
import { ModuleService } from '@geonature/services/module.service';

import { CONTENT_CONFIG, DATA_TABLE_CONFIG } from '../../utils/constants.util';
import { Column, PaginatedItemCollection } from '../../models/common.models';

@Component({
  selector: 'gn-individuals-list',
  templateUrl: 'list.component.html',
  styleUrls: ['list.component.scss'],
  encapsulation: ViewEncapsulation.None,
})
export class ListComponent implements OnInit, AfterViewInit {
  @Output() pagination: EventEmitter<any> = new EventEmitter()
  @Output() sort: EventEmitter<any> = new EventEmitter()
  @Output() rows: EventEmitter<any> = new EventEmitter();
  @Input() availableColumnsParams!: Record<keyof any, true>;
  @Input() displayedColumnsParams!: Array<String>;
  @Input() dataTable$: Observable<PaginatedItemCollection<unknown>> = new Observable<PaginatedItemCollection<unknown>>();
  @Input() sorts: Array<Object> = [];

  public contentHeight: number = CONTENT_CONFIG.MIN_HEIGHT;
  public rowHeight: number = DATA_TABLE_CONFIG.TABLE_ROW_HEIGHT;
  public nbRowsToDisplay: number = DATA_TABLE_CONFIG.PER_PAGE_OPTION;
  public displayedColumns!: Column<undefined>[];
  public availableColumns!: Column<undefined>[];

  constructor(
    public config: ConfigService,
    private _moduleService: ModuleService,
    private _translate: TranslateService,
    private activatedRoute: ActivatedRoute,
  ) {}

  ngOnInit() : void {
    this.activatedRoute.data.subscribe(({data}) => {
      this.dataTable$ = of(data);
      console.log('Resolver data:', data);
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
        column => this._translate.get(`Individuals.AvailableFields.${column.prop}`)
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

    // Calculate the height of the content and the number of rows to display in the table, based on the viewport height
    this.contentHeight = this.calcContentHeight();
    this.nbRowsToDisplay = this.calcRowNumber();
    this.sendRowNumber();

    console.log('Content height:', this.contentHeight, 'Row number:', this.nbRowsToDisplay);
  }

  ngAfterViewInit() : void {
    setTimeout(() => this.calcContentHeight(), 500);
  }

  // Listen to window resize event to recalculate the content height and resize the map
  // @HostListener('window:resize', ['$event'])
  // onResize(event) : void {
  //   this.contentHeight = this.calcContentHeight();
  // }

  // Fonction that sets the size of the content of the card, to set the height of the map
  // and calculate the number of rows to display in the table based on the viewport height
  calcContentHeight() : number {
    let windowH = window.innerHeight;
    const toolbarElement = document.getElementById('individuals-tab');
    let toolbarH = toolbarElement
      ? toolbarElement.getBoundingClientRect().top
      : 0;
    let height = windowH - (toolbarH + 80);

    return height >= CONTENT_CONFIG.MIN_HEIGHT ? height : CONTENT_CONFIG.MIN_HEIGHT;
  }

  calcRowNumber() : number {
    let num = Math.trunc((this.contentHeight - 5) / DATA_TABLE_CONFIG.TABLE_ROW_HEIGHT) - 2; // We remove 5px for the header border and 2 rows for the header and footer of the table
    return num;
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
}


