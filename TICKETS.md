Functional requirements

As a member of the bank, I can:

submit a reimbursement with the following details:
Bank account
Amount
Description
receive a confirmation email when my reimbursement is approved by an administrator (NOTE: stub out emailing)
receive a rejection email when my reimbursement is denied by an administrator
fetch a list of submitted reimbursements, with the three details I submitted as well as:
the date when the request was initially submitted by the member
the request’s current status (either pending, approved, denied)
As a bank administrator, I can:

fetch a list of reimbursements for a particular bank
filter to see which reimbursements have a pending status (have not yet been approved or denied by an administrator)
approve or deny a pending reimbursement request


1. Create data model for reimbursements
2. Create data models for bank, admin, account, member
3. Create email client
4. Setup DB client
5. Setup API server (routing, logging, middleware, start up, etc)
6. Create POST /reimbursements
7. Trigger reimbursement processed email (approved or rejected) (scheduled task)
8. Create GET /reimbursements
9. Create GET /reimbursements/:id
10. Create DELETE /reimbursements/:id
11. Create GET /bank/:id/reimbursements
12. Create PATCH /reimbursements/:id
13. Write end to end tests for creating, fetching, and deleting reimbursements
14. Write end to end tests for approving and denying reimbursements