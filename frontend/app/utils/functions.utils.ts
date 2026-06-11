  import { CONTENT_CONFIG, DATA_TABLE_CONFIG } from './constants.util';
  
  // Fonction that sets the size of the content of the card, to set the height of the map
  // and calculate the number of rows to display in the table based on the viewport height
  export function calcContentHeight() : number {
    let windowH = window.innerHeight;
    const toolbarElement = document.getElementById('individuals-tab');
    let toolbarH = toolbarElement
      ? toolbarElement.getBoundingClientRect().top
      : 0;
    let height = windowH - (toolbarH + 80);

    return height >= CONTENT_CONFIG.MIN_HEIGHT ? height : CONTENT_CONFIG.MIN_HEIGHT;
  }

  export function calcRowNumber(contentHeight: number) : number {
    // We remove 5px for the header border
    // We remove 2 rows for the header and footer lines and 2 for the action buttons div
    let num = Math.trunc((contentHeight - 5) / DATA_TABLE_CONFIG.TABLE_ROW_HEIGHT) - 4;
    return num;
  }