import { CONTENT_CONFIG } from './constants.util';

// Fonction that sets the size of the content of the card, to set the height of the map
// and calculate the number of rows to display in the table based on the viewport height
export function calcContentHeight(): number {
  let windowH = window.innerHeight;
  const toolbarElement = document.getElementById('individuals-tab');
  let toolbarH = toolbarElement ? toolbarElement.getBoundingClientRect().top : 0;
  let height = windowH - (toolbarH + 80);

  return height >= CONTENT_CONFIG.MIN_HEIGHT ? height : CONTENT_CONFIG.MIN_HEIGHT;
}
