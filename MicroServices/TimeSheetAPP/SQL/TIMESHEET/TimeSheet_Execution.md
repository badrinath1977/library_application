Here are all possible execution examples for spSearchEmployeeAbsence, grouped by scenario:

Basic / Identity Filters

``sql
-- By person number
EXEC spSearchEmployeeAbsence @personNumber = '41556';

-- By personId
EXEC spSearchEmployeeAbsence @personId = 300000287566152;

-- By specific absence entry
EXEC spSearchEmployeeAbsence @personAbsenceEntryId = 300000305036909;

-- All three combined (pinpoint lookup)
EXEC spSearchEmployeeAbsence
    @personNumber         = '41556',
    @personId             = 300000287566152,
    @personAbsenceEntryId = 300000305036909;
`

Absence Type Filters

`sql
-- By absence type name (partial match)
EXEC spSearchEmployeeAbsence @absenceType = 'Vacation';

EXEC spSearchEmployeeAbsence @absenceType = 'Sick Time';

-- By absence type ID
EXEC spSearchEmployeeAbsence @absenceTypeId = 300000009518495;

-- By pattern code
EXEC spSearchEmployeeAbsence @absencePatternCd = 'GENERIC';
EXEC spSearchEmployeeAbsence @absencePatternCd = 'II';

-- Combined type filters
EXEC spSearchEmployeeAbsence
    @absenceType      = 'Sick Time',
    @absencePatternCd = 'II';
`

Status Filters

`sql
-- By absence status
EXEC spSearchEmployeeAbsence @absenceStatusCd = 'SUBMITTED';

-- By approval status
EXEC spSearchEmployeeAbsence @approvalStatusCd = 'APPROVED';
EXEC spSearchEmployeeAbsence @approvalStatusCd = 'AWAITING';

-- By display status
EXEC spSearchEmployeeAbsence @absenceDispStatus = 'COMPLETED';
EXEC spSearchEmployeeAbsence @absenceDispStatus = 'AWAITING';

-- All statuses combined
EXEC spSearchEmployeeAbsence
    @absenceStatusCd   = 'SUBMITTED',
    @approvalStatusCd  = 'APPROVED',
    @absenceDispStatus = 'COMPLETED';

-- Pending/awaiting approvals only
EXEC spSearchEmployeeAbsence
    @approvalStatusCd  = 'AWAITING',
    @absenceDispStatus = 'AWAITING';
`

Date Range Filters

`sql
-- Absences starting in a date range
EXEC spSearchEmployeeAbsence
    @startDateFrom = '2025-09-01',
    @startDateTo   = '2025-12-31';

-- Absences ending in a range
EXEC spSearchEmployeeAbsence
    @endDateFrom = '2025-09-01',
    @endDateTo   = '2025-12-31';

-- Submitted within a range
EXEC spSearchEmployeeAbsence
    @submittedDateFrom = '2025-11-01',
    @submittedDateTo   = '2025-11-30';

-- Created within a datetime range
EXEC spSearchEmployeeAbsence
    @creationDateFrom = '2025-09-01T00:00:00+00:00',
    @creationDateTo   = '2025-12-31T23:59:59+00:00';

-- Last updated range
EXEC spSearchEmployeeAbsence
    @lastUpdateDateFrom = '2025-10-01T00:00:00+00:00',
    @lastUpdateDateTo   = '2025-11-30T23:59:59+00:00';

-- Approved within a range
EXEC spSearchEmployeeAbsence
    @approvalDateFrom = '2025-10-01T00:00:00+00:00',
    @approvalDateTo   = '2025-11-30T23:59:59+00:00';

-- Not yet approved (NULL approval date) — combine with AWAITING status
EXEC spSearchEmployeeAbsence
    @approvalStatusCd = 'AWAITING';

-- Full date range across all fields
EXEC spSearchEmployeeAbsence
    @startDateFrom      = '2025-09-01',
    @startDateTo        = '2025-12-31',
    @submittedDateFrom  = '2025-09-01',
    @submittedDateTo    = '2025-12-31',
    @approvalDateFrom   = '2025-10-01T00:00:00+00:00',
    @approvalDateTo     = '2025-12-31T23:59:59+00:00';
`

Duration Filters

`sql
-- Exact duration
EXEC spSearchEmployeeAbsence @durationMin = 1, @durationMax = 1;  -- 1-day absences
EXEC spSearchEmployeeAbsence @durationMin = 7, @durationMax = 7;  -- 7-day absences

-- Duration range
EXEC spSearchEmployeeAbsence @durationMin = 3, @durationMax = 10;

-- Long absences (5+ days)
EXEC spSearchEmployeeAbsence @durationMin = 5;

-- Short absences (1–2 days)
EXEC spSearchEmployeeAbsence @durationMin = 1, @durationMax = 2;

-- By unit of measure
EXEC spSearchEmployeeAbsence @unitOfMeasure = 'D';

-- Duration + unit combined
EXEC spSearchEmployeeAbsence
    @durationMin    = 3,
    @durationMax    = 7,
    @unitOfMeasure  = 'D';
`

Comments / Keyword Search

`sql
-- Search by keyword in comments
EXEC spSearchEmployeeAbsence @commentsKeyword = 'fever';
EXEC spSearchEmployeeAbsence @commentsKeyword = 'Vacation';
EXEC spSearchEmployeeAbsence @commentsKeyword = 'doctor';
EXEC spSearchEmployeeAbsence @commentsKeyword = 'headache';
EXEC spSearchEmployeeAbsence @commentsKeyword = 'cold';
`

Employer / Entity Filters

`sql
-- By employer (partial match)
EXEC spSearchEmployeeAbsence @employer = 'India';
EXEC spSearchEmployeeAbsence @employer = 'xyz Information Systems';

-- By legal entity ID
EXEC spSearchEmployeeAbsence @legalEntityId = 300000004016017;

-- By legislation code
EXEC spSearchEmployeeAbsence @legislationCode = 'IN';

-- All entity filters combined
EXEC spSearchEmployeeAbsence
    @employer        = 'xyz Information Systems',
    @legalEntityId   = 300000004016017,
    @legislationCode = 'IN';
`

Flag Filters

`sql
-- Basic absence entries only
EXEC spSearchEmployeeAbsence @absenceEntryBasicFlag = 1;

-- Shift-based absences
EXEC spSearchEmployeeAbsence @employeeShiftFlag = 1;

-- Single-day absences only
EXEC spSearchEmployeeAbsence @singleDayFlag = 1;

-- Multi-day absences (singleDayFlag = 0)
EXEC spSearchEmployeeAbsence @singleDayFlag = 0;

-- Open-ended absences
EXEC spSearchEmployeeAbsence @openEndedFlag = 1;

-- Updatable absences
EXEC spSearchEmployeeAbsence @absenceUpdatableFlag = 1;

-- Multiple flags combined
EXEC spSearchEmployeeAbsence
    @absenceEntryBasicFlag = 1,
    @singleDayFlag         = 0,
    @absenceUpdatableFlag  = 1;
`

Audit Filters

`sql
-- By creator
EXEC spSearchEmployeeAbsence @createdBy = 'name@xyz.com';

-- By last updater
EXEC spSearchEmployeeAbsence @lastUpdatedBy = 'name@xyz.com';

-- By object version
EXEC spSearchEmployeeAbsence @objectVersionNumber = 1;  -- never updated
EXEC spSearchEmployeeAbsence @objectVersionNumber = 6;  -- updated multiple times

-- Creator + updater combined
EXEC spSearchEmployeeAbsence
    @createdBy     = 'name@xyz.com',
    @lastUpdatedBy = 'name@xyz.com';
`

Pagination

`sql
-- Page 1, default size (20)
EXEC spSearchEmployeeAbsence @personNumber = '41556';

-- Custom page size
EXEC spSearchEmployeeAbsence
    @personNumber = '41556',
    @pageNumber   = 1,
    @pageSize     = 5;

-- Navigate to page 2
EXEC spSearchEmployeeAbsence
    @personNumber = '41556',
    @pageNumber   = 2,
    @pageSize     = 5;

-- Large page size
EXEC spSearchEmployeeAbsence
    @pageNumber = 1,
    @pageSize   = 100;
`

Sorting

`sql
-- Sort by start date ASC
EXEC spSearchEmployeeAbsence @sortColumn = 'startDate', @sortDirection = 'ASC';

-- Sort by duration DESC (longest first)
EXEC spSearchEmployeeAbsence @sortColumn = 'duration', @sortDirection = 'DESC';

-- Sort by approval status
EXEC spSearchEmployeeAbsence @sortColumn = 'approvalStatusCd', @sortDirection = 'ASC';

-- Sort by submission date newest first
EXEC spSearchEmployeeAbsence @sortColumn = 'submittedDate', @sortDirection = 'DESC';

-- Sort by last updated
EXEC spSearchEmployeeAbsence @sortColumn = 'lastUpdateDate', @sortDirection = 'DESC';

-- Sort by creation date oldest first
EXEC spSearchEmployeeAbsence @sortColumn = 'creationDate', @sortDirection = 'ASC';
`

Combined / Real-World Scenarios

`sql
-- All approved vacations for a person this year
EXEC spSearchEmployeeAbsence
    @personNumber      = '41556',
    @absenceType       = 'Vacation',
    @approvalStatusCd  = 'APPROVED',
    @startDateFrom     = '2025-01-01',
    @startDateTo       = '2025-12-31',
    @sortColumn        = 'startDate',
    @sortDirection     = 'ASC';

-- All pending sick leaves awaiting approval
EXEC spSearchEmployeeAbsence
    @absenceType       = 'Sick Time',
    @approvalStatusCd  = 'AWAITING',
    @legislationCode   = 'IN',
    @sortColumn        = 'submittedDate',
    @sortDirection     = 'DESC';

-- Long absences (7+ days) that are approved and completed
EXEC spSearchEmployeeAbsence
    @durationMin       = 7,
    @approvalStatusCd  = 'APPROVED',
    @absenceDispStatus = 'COMPLETED';

-- Recent absences submitted in November 2025
EXEC spSearchEmployeeAbsence
    @submittedDateFrom = '2025-11-01',
    @submittedDateTo   = '2025-11-30',
    @sortColumn        = 'submittedDate',
    @sortDirection     = 'DESC',
    @pageNumber        = 1,
    @pageSize          = 10;

-- Absences with health-related comments, India entity
EXEC spSearchEmployeeAbsence
    @commentsKeyword  = 'fever',
    @legislationCode  = 'IN',
    @legalEntityId    = 300000004016017;

-- All data, paginated, sorted by duration
EXEC spSearchEmployeeAbsence
    @sortColumn    = 'duration',
    @sortDirection = 'DESC',
    @pageNumber    = 1,
    @pageSize      = 20;

-- Full filter — maximum specificity
EXEC spSearchEmployeeAbsence
    @personNumber          = '41556',
    @absenceType           = 'Sick Time',
    @absencePatternCd      = 'II',
    @absenceStatusCd       = 'SUBMITTED',
    @approvalStatusCd      = 'APPROVED',
    @absenceDispStatus     = 'COMPLETED',
    @startDateFrom         = '2025-09-01',
    @startDateTo           = '2025-09-30',
    @durationMin           = 1,
    @durationMax           = 3,
    @unitOfMeasure         = 'D',
    @legislationCode       = 'IN',
    @legalEntityId         = 300000004016017,
    @absenceEntryBasicFlag = 1,
    @absenceUpdatableFlag  = 1,
    @createdBy             = 'name@xyz.com',
    @sortColumn            = 'startDate',
    @sortDirection         = 'ASC',
    @pageNumber            = 1,
    @pageSize              = 10;
``

Quick Reference Summary

| Group | # of Examples |
|---|---|
| Identity filters | 4 |
| Absence type | 6 |
| Status filters | 7 |
| Date ranges | 8 |
| Duration | 6 |
| Comments keyword | 5 |
| Employer / entity | 5 |
| Flag filters | 7 |
| Audit filters | 5 |
| Pagination | 4 |
| Sorting | 6 |
| Combined scenarios | 7 |
| Total | 70 |