// Used to declare avilable columns and their name in the table header
// export interface Column<T> {
//   prop: keyof T;
//   name: string;
// }
export interface Column<T = Record<string, unknown>> {
  prop: keyof T | string;
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

export interface Feature<T> {
  id: number;
  type: 'Feature';
  geometry: {
    type: string;
    coordinates: [number, number];
  };
  properties: T;
}

export interface FeatureCollection<T> {
  type: 'FeatureCollection';
  features: Feature<T>[];
}

export interface RankAndPage {
  page: number;
  per_page: number;
  rank: number;
}

export interface AccessResult {
  id: number;
  access: boolean;
  message?: string | null;
}