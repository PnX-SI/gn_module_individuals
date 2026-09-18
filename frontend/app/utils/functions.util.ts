import { CONTENT_CONFIG } from './constants.util';

/**
 * Return the size of card content
 *
 * @export
 * @return {*}  {number}
 */
export function calcContentHeight(): number {
  let windowH = window.innerHeight;
  const toolbarElement = document.getElementById('individuals-tab');
  let toolbarBottom = toolbarElement ? toolbarElement.getBoundingClientRect().bottom : 0;
  let height = windowH - (toolbarBottom + 10 + 10); // 10px for the individuals-tab and + 10px for the content padding bottom
  return height >= CONTENT_CONFIG.MIN_HEIGHT ? height - 12 : CONTENT_CONFIG.MIN_HEIGHT;
}

/**
 * Return the date formatted according to the navigator language
 *
 * @export
 * @param {{ day: number; month: number; year: number }} date
 * @return {*}  {string}
 */
export function dateFormat(date: { day: number; month: number; year: number }): string | null {
  if (date && date.day && date.month && date.year) {
    const dateObject = new Date(date.year, date.month - 1, date.day);
    return new Intl.DateTimeFormat(navigator.language).format(dateObject);
  }
  return null;
}

/**
 * Return the time formatted according to the navigator language
 *
 * @export
 * @param {string} time
 * @return {*}  {(string | null)}
 */
export function timeFormat(time: string): string | null {
  if (!time) {
    return null;
  }

  const [hours, minutes] = time.split(':').map(Number);

  if (
    Number.isNaN(hours) ||
    Number.isNaN(minutes) ||
    hours < 0 ||
    hours > 23 ||
    minutes < 0 ||
    minutes > 59
  ) {
    return null;
  }

  const dateObject = new Date();
  dateObject.setHours(hours, minutes, 0, 0);

  return new Intl.DateTimeFormat(navigator.language, {
    hour: 'numeric',
    minute: '2-digit'
  }).format(dateObject);
}

/**
 * Return the label corresponding to the given value found in the 
 * given objects array
 *
 * @export
 * @param {{ label: string; value: number }[]} values
 * @param {string} values Number or numbers arrays
 * @return {*}  {(string | null)}
 */
export function getValuesLabels(
  objectsArray: { label: string; value: number }[],
  values: number | number[]): string | null {
  if (!objectsArray || values == null) {
    return null;
  }

  const valuesArray = Array.isArray(values) ? values : [values];
  const labels = valuesArray
    .map(value => objectsArray.find(v => v.value === value)?.label)
    .filter((label): label is string => !!label);

  return labels.length > 0 ? labels.join(', ') : null;
}