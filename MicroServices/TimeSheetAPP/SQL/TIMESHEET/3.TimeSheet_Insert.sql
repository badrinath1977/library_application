-- Use only if this is test/dev data and a clean reload is acceptable
TRUNCATE TABLE GenAI.EmployeeAbsence;
-- Then re-run your original INSERT


INSERT INTO GenAI.EmployeeAbsence (
    personNumber, personId, personAbsenceEntryId,
    absenceType, absenceTypeId, absencePatternCd,
    absenceStatusCd, approvalStatusCd, absenceDispStatus,
    startDate, endDate, startDateTime, endDateTime,
    submittedDate, creationDate, lastUpdateDate, ApprovalDatetime,
    duration, unitOfMeasure, formattedDuration,
    comments, employer, legalEntityId, legislationCode,
    absenceEntryBasicFlag, employeeShiftFlag, singleDayFlag,
    openEndedFlag, absenceUpdatableFlag,
    createdBy, lastUpdatedBy, objectVersionNumber
)
SELECT
    personNumber, personId, personAbsenceEntryId,
    absenceType, absenceTypeId, absencePatternCd,
    absenceStatusCd, approvalStatusCd, absenceDispStatus,
    startDate, endDate, startDateTime, endDateTime,
    submittedDate, creationDate, lastUpdateDate, ApprovalDatetime,
    duration, unitOfMeasure, formattedDuration,
    comments, employer, legalEntityId, legislationCode,
    absenceEntryBasicFlag, employeeShiftFlag, singleDayFlag,
    openEndedFlag, absenceUpdatableFlag,
    createdBy, lastUpdatedBy, objectVersionNumber
FROM (VALUES
    (
        '41556', 300000287566152, 300000305036909,
        'xyz IN Employee Vacation', 300000009518536, 'GENERIC',
        'SUBMITTED', 'APPROVED', 'COMPLETED',
        '2025-11-28', '2025-12-08',
        '2025-11-28T09:00:00+00:00', '2025-12-08T17:00:00+00:00',
        '2025-11-05', '2025-09-29T17:07:24+00:00', '2025-11-20T07:08:08+00:00', '2025-11-12T23:11:09+00:00',
        7, 'D', '7 Days',
        'Vacation with Family.',
        '516-xyz Information Systems India Private Ltd. [India]',
        300000004016017, 'IN',
        1, 0, 0, 0, 1,
        'name@xyz.com', 'name@xyz.com', 6
    ),
    (
        '41556', 300000287566152, 300000304225802,
        'xyz IN Employee Sick Time', 300000009518495, 'II',
        'SUBMITTED', 'APPROVED', 'COMPLETED',
        '2025-09-24', '2025-09-24',
        '2025-09-24T09:00:00+00:00', '2025-09-24T17:00:00+00:00',
        '2025-09-25', '2025-09-25T07:46:45+00:00', '2025-10-10T16:04:37+00:00', '2025-10-10T16:04:37+00:00',
        1, 'D', '1 Days',
        'feeling unwell today due to fever, cough, and headache',
        '516-xyz Information Systems India Private Ltd. [India]',
        300000004016017, 'IN',
        1, 0, 0, 0, 1,
        'name@xyz.com', 'name@xyz.com', 3
    ),
    (
        '41556', 300000287566152, 300000315084763,
        'xyz IN Employee Sick Time', 300000009518495, 'II',
        'SUBMITTED', 'AWAITING', 'AWAITING',
        '2025-11-17', '2025-11-19',
        '2025-11-17T09:00:00+00:00', '2025-11-19T17:00:00+00:00',
        '2025-11-20', '2025-11-20T07:05:39+00:00', '2025-11-20T07:08:08+00:00', NULL,
        3, 'D', '3 Days',
        'Taking Sick leave due to cold, throat pain, headache. Visited the doctor he said take a rest.',
        '516-xyz Information Systems India Private Ltd. [India]',
        300000004016017, 'IN',
        1, 0, 0, 0, 1,
        'name@xyz.com', 'name@xyz.com', 1
    )
) AS src (
    personNumber, personId, personAbsenceEntryId,
    absenceType, absenceTypeId, absencePatternCd,
    absenceStatusCd, approvalStatusCd, absenceDispStatus,
    startDate, endDate, startDateTime, endDateTime,
    submittedDate, creationDate, lastUpdateDate, ApprovalDatetime,
    duration, unitOfMeasure, formattedDuration,
    comments, employer, legalEntityId, legislationCode,
    absenceEntryBasicFlag, employeeShiftFlag, singleDayFlag,
    openEndedFlag, absenceUpdatableFlag,
    createdBy, lastUpdatedBy, objectVersionNumber
)
WHERE NOT EXISTS (
    SELECT 1 FROM GenAI.EmployeeAbsence t
    WHERE t.personAbsenceEntryId = src.personAbsenceEntryId
);

go

MERGE INTO GenAI.EmployeeAbsence AS target
USING (VALUES
    (300000305036909, '41556', 300000287566152, 'xyz IN Employee Vacation', 300000009518536, 'GENERIC', 'SUBMITTED', 'APPROVED', 'COMPLETED', '2025-11-28', '2025-12-08', '2025-11-28T09:00:00+00:00', '2025-12-08T17:00:00+00:00', '2025-11-05', '2025-09-29T17:07:24+00:00', '2025-11-20T07:08:08+00:00', '2025-11-12T23:11:09+00:00', 7, 'D', '7 Days', 'Vacation with Family.', '516-xyz Information Systems India Private Ltd. [India]', 300000004016017, 'IN', 1, 0, 0, 0, 1, 'name@xyz.com', 'name@xyz.com', 6),
    (300000304225802, '41556', 300000287566152, 'xyz IN Employee Sick Time', 300000009518495, 'II', 'SUBMITTED', 'APPROVED', 'COMPLETED', '2025-09-24', '2025-09-24', '2025-09-24T09:00:00+00:00', '2025-09-24T17:00:00+00:00', '2025-09-25', '2025-09-25T07:46:45+00:00', '2025-10-10T16:04:37+00:00', '2025-10-10T16:04:37+00:00', 1, 'D', '1 Days', 'feeling unwell today due to fever, cough, and headache', '516-xyz Information Systems India Private Ltd. [India]', 300000004016017, 'IN', 1, 0, 0, 0, 1, 'name@xyz.com', 'name@xyz.com', 3),
    (300000315084763, '41556', 300000287566152, 'xyz IN Employee Sick Time', 300000009518495, 'II', 'SUBMITTED', 'AWAITING', 'AWAITING', '2025-11-17', '2025-11-19', '2025-11-17T09:00:00+00:00', '2025-11-19T17:00:00+00:00', '2025-11-20', '2025-11-20T07:05:39+00:00', '2025-11-20T07:08:08+00:00', NULL, 3, 'D', '3 Days', 'Taking Sick leave due to cold, throat pain, headache. Visited the doctor he said take a rest.', '516-xyz Information Systems India Private Ltd. [India]', 300000004016017, 'IN', 1, 0, 0, 0, 1, 'name@xyz.com', 'name@xyz.com', 1)
) AS src (
    personAbsenceEntryId, personNumber, personId,
    absenceType, absenceTypeId, absencePatternCd,
    absenceStatusCd, approvalStatusCd, absenceDispStatus,
    startDate, endDate, startDateTime, endDateTime,
    submittedDate, creationDate, lastUpdateDate, ApprovalDatetime,
    duration, unitOfMeasure, formattedDuration,
    comments, employer, legalEntityId, legislationCode,
    absenceEntryBasicFlag, employeeShiftFlag, singleDayFlag,
    openEndedFlag, absenceUpdatableFlag,
    createdBy, lastUpdatedBy, objectVersionNumber
)
ON target.personAbsenceEntryId = src.personAbsenceEntryId

WHEN MATCHED THEN UPDATE SET
    absenceStatusCd      = src.absenceStatusCd,
    approvalStatusCd     = src.approvalStatusCd,
    absenceDispStatus    = src.absenceDispStatus,
    lastUpdateDate       = src.lastUpdateDate,
    ApprovalDatetime     = src.ApprovalDatetime,
    objectVersionNumber  = src.objectVersionNumber,
    comments             = src.comments

WHEN NOT MATCHED THEN INSERT (
    personNumber, personId, personAbsenceEntryId,
    absenceType, absenceTypeId, absencePatternCd,
    absenceStatusCd, approvalStatusCd, absenceDispStatus,
    startDate, endDate, startDateTime, endDateTime,
    submittedDate, creationDate, lastUpdateDate, ApprovalDatetime,
    duration, unitOfMeasure, formattedDuration,
    comments, employer, legalEntityId, legislationCode,
    absenceEntryBasicFlag, employeeShiftFlag, singleDayFlag,
    openEndedFlag, absenceUpdatableFlag,
    createdBy, lastUpdatedBy, objectVersionNumber
) VALUES (
    src.personNumber, src.personId, src.personAbsenceEntryId,
    src.absenceType, src.absenceTypeId, src.absencePatternCd,
    src.absenceStatusCd, src.approvalStatusCd, src.absenceDispStatus,
    src.startDate, src.endDate, src.startDateTime, src.endDateTime,
    src.submittedDate, src.creationDate, src.lastUpdateDate, src.ApprovalDatetime,
    src.duration, src.unitOfMeasure, src.formattedDuration,
    src.comments, src.employer, src.legalEntityId, src.legislationCode,
    src.absenceEntryBasicFlag, src.employeeShiftFlag, src.singleDayFlag,
    src.openEndedFlag, src.absenceUpdatableFlag,
    src.createdBy, src.lastUpdatedBy, src.objectVersionNumber
);
