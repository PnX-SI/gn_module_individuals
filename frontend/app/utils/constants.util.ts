export const CONTENT_CONFIG = {
  MIN_HEIGHT: 350,
};

export const DATATABLE_CONFIG = {
  TABLE_ROW_HEIGHT: 40, // Think to change the list.component.css .ngx-datatable .datatable-header-cell line-height if you change this value
  PER_PAGE_OPTION: 10,
  ACTION_COLUMNS_WIDTH: 10,
  COLUMN_MAX_WIDTH: 50,
};

export const MAP_CONFIG = {
  SELECTED_LAYER_COLOR: '#d7191c',
  UNSELECTED_LAYER_COLOR: '#2c7bb6',
  SELECTED_LAYER_OPACITY: 0.9,
  UNSELECTED_LAYER_OPACITY: 0.55,
};

export const DEVICE_FORM_CONSTRAINTS = {
  provider_name: {
    maxLength: 50,
    pattern: '^[a-zA-ZÀ-ÖØ-öø-ÿ0-9 _-]*$',
    help: 'PatternText1', // Refer to i18n files
  },
  provider_device_id: {
    maxLength: 50,
    pattern: '^[a-zA-Z0-9_-]*$',
    help: 'PatternText2',
  },
  comment: {
    maxLength: 255,
    pattern: '^[^<>]*$', // or /^[a-zA-Z0-9À-ÿ\s.,!?'"()_-]*$/ to test
    help: 'PatternText3',
  },
};

export const DEVICES_DEFAULT_SORT = { prop: 'meta_create_date', dir: 'desc' };

export const INDIVIDUALS_DEFAULT_SORT = { prop: 'last_observation_date', dir: 'desc' };

export const INDIVIDUALS_FORM_CONSTRAINTS = {
  individual_name: {
    maxLength: 50,
    pattern: '^[a-zA-ZÀ-ÖØ-öø-ÿ0-9 _-]*$',
    help: 'PatternText1', // Refer to i18n files
  },
  comment: {
    maxLength: 255,
    pattern: '^[^<>]*$', // or /^[a-zA-Z0-9À-ÿ\s.,!?'"()_-]*$/ to test
    help: 'PatternText3',
  },
};

export const DEPLOYMENTS_FORM_CONSTRAINTS = {
  marking_code: {
    maxLength: 50,
    pattern: '^[a-zA-ZÀ-ÖØ-öø-ÿ0-9_-]*$',
    help: 'PatternText4', // Refer to i18n files
  },
  comment: {
    maxLength: 255,
    pattern: '^[^<>]*$', // or /^[a-zA-Z0-9À-ÿ\s.,!?'"()_-]*$/ to test
    help: 'PatternText3',
  },
};
