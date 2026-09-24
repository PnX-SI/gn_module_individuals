describe('Individuals main component', () => {
  beforeEach(() => {
    cy.geonatureLogin();
    cy.visit('/#/individuals');
  });

  it('displays the navigation tabs', () => {
    cy.get('#individuals-tab').should('be.visible');

    cy.get('#individuals-tab a[mat-tab-link]').should('have.length', 3);
    cy.get('#individuals-tab a[mat-tab-link]').eq(0).should('contain', 'Individuals');
    cy.get('#individuals-tab a[mat-tab-link]').eq(1).should('contain', 'Observations');
    cy.get('#individuals-tab a[mat-tab-link]').eq(2).should('contain', 'Tracking devices');
  });

  it('links each tab to the expected route', () => {
    cy.get('#individuals-tab a[mat-tab-link]').eq(0).should('have.attr', 'href', '/individuals');
    cy.get('#individuals-tab a[mat-tab-link]').eq(1).should('have.attr', 'href', '/observations');
    cy.get('#individuals-tab a[mat-tab-link]').eq(2).should('have.attr', 'href', '/devices');
  });
});