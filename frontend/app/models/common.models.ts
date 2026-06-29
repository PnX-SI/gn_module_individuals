// Used to declare avilable columns and their name in the table header
export interface Column<T> {
  prop: keyof T;
  name: string;
}

export interface Sort {
  prop: string;
  dir: string;
}

// Partial : Sort attributes not mandatory
export interface APIPaginationParams extends Partial<Sort> {
  page: number;
  per_page: number;
}

export interface PaginatedItemCollection<T> extends APIPaginationParams {
  items: T[];
  total: number;
  pages: number;
  prev_num: number | null;
  next_num: number | null;
  has_next: boolean;
  has_prev: boolean;
}

export interface ApiError {
  name: string;
  description: string;
  params?: Record<string, unknown>;
}

export interface FormConstraint {
  maxLength: number;
  pattern: string;
  help: string;
}

// export interface SimplePagination {
//   page: number;
//   per_page: number; // Alias for per_page, to be used in the frontend for consistency with other modules
// }

// export interface SimplePaginationWithSort extends SimplePagination, Sort {
// }

// export interface PaginatedItemCollection<T> extends SimplePagination {
//   items: T[];
//   total: number;
//   pages: number;
//   prev_num: number | null;
//   next_num: number | null;
//   has_next: boolean;
//   has_prev: boolean;
// }

// export interface StationFeature {
//   id?: number;
//   type: 'Feature';
//   geometry: {
//     type: string;
//     coordinates: [number, number];
//   };
//   properties: Station;
// }

// export interface StationFeatureCollection {
//   type: 'FeatureCollection';
//   features: Array<StationFeature>;
// }
