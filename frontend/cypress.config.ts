import * as path from 'path';

import geonatureConfig from '../../geonature/frontend/cypress.config';

export default {
  ...geonatureConfig,

  e2e: {
    ...geonatureConfig.e2e,

    baseUrl: 'http://127.0.0.1:4200',
    specPattern: path.join(__dirname, 'cypress/e2e/**/*.spec.js'),
  },
};