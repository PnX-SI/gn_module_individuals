import { Injectable } from "@angular/core";
import { DataFormService } from "@geonature_common/form/data-form.service";
import { Observable, BehaviorSubject } from "rxjs";
import { ConfigService } from "@geonature/services/config.service";

@Injectable()
export class NomenclaturesService {
  public nomenclatureItems = <any>{};
  public firstMessageMapList = true;
  private _defaultNomenclature$: BehaviorSubject<any> = new BehaviorSubject(null);
  public defaultNomenclature$: Observable<any> = this._defaultNomenclature$.asObservable();
  
  constructor(
    private _gnDataService: DataFormService,
    public config: ConfigService
) {
    this._gnDataService
      .getNomenclatures([
        "TYPE_DISPO_SUIVI",
      ])
      .subscribe((data) => {
        data.forEach((element: any) => {
          this.nomenclatureItems[element.mnemonique] = element.values;
        });
      });

    // this._gnDataService
    //   .getDefaultNomenclatureValue("occhab")
    //   .subscribe((data) => {
    //     this._defaultNomenclature$.next(data);
    //   });
  }

  // get defaultNomenclature() {
  //   return this._defaultNomenclature$.getValue();
  // }
}
