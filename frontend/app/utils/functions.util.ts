import { CONTENT_CONFIG } from './constants.util';

// Fonction that sets the size of the content of the card, to set the height of the map
export function calcContentHeight(): number {
  let windowH = window.innerHeight;
  const toolbarElement = document.getElementById('individuals-tab');
  let toolbarH = toolbarElement ? toolbarElement.getBoundingClientRect().height : 0;
  let height = windowH - toolbarH;
  return height >= CONTENT_CONFIG.MIN_HEIGHT ? height : CONTENT_CONFIG.MIN_HEIGHT;
}
