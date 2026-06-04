import { Injectable } from "@angular/core";
import { DataFormService } from "@geonature_common/form/data-form.service";
import { Observable, BehaviorSubject } from "rxjs";
import { ConfigService } from "@geonature/services/config.service";

@Injectable()
export class NomenclaturesService {
  public items = <any>{};

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
          this.items[element.mnemonique] = element.values;
        });
      });
  }
}
