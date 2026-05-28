export const CONTENT_CONFIG = {
    "MIN_HEIGHT": 350,
}

export const DATA_TABLE_CONFIG = {
    "TABLE_ROW_HEIGHT": 40, // Think to change the list.component.css .ngx-datatable .datatable-header-cell line-height if you change this value
    "PER_PAGE_OPTION": 5,
    "ACTION_COLUMNS_WIDTH": 10,
    "COLUMN_MAX_WIDTH": 50,
}

export const DEVICE_FORM_CONSTRAINTS = {
    "provider_name": {
        "maxLength": 50,
        "pattern": /^[a-zA-Z0-9 _-]*$/,
    },
    "provider_device_id": {
        "maxLength": 50,
        "pattern": /^[a-zA-Z0-9_-]*$/,
    },
    "comment": {
        "maxLength": 255,
        "pattern": /^[^<>]*$/, // or /^[a-zA-Z0-9À-ÿ\s.,!?'"()_-]*$/ to test
    }
}