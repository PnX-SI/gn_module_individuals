import { CONTENT_CONFIG } from './constants.util';

// Fonction that sets the size of the content of the card, to set the height of the map
export function calcContentHeight(): number {
  let windowH = window.innerHeight;
  const toolbarElement = document.getElementById('individuals-tab');
  let toolbarBottom = toolbarElement ? toolbarElement.getBoundingClientRect().bottom : 0;
  let height = windowH - (toolbarBottom + 10 + 10); // 10px for the individuals-tab and + 10px for the content padding bottom
  return height >= CONTENT_CONFIG.MIN_HEIGHT ? height - 12 : CONTENT_CONFIG.MIN_HEIGHT;
}
