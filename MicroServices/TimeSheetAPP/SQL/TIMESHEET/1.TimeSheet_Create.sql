CREATE TABLE genai.EmployeeAbsence (
    -- Identity / Person
    personNumber          VARCHAR(20)     NOT NULL,
    personId              BIGINT          NOT NULL,
    personAbsenceEntryId  BIGINT          NOT NULL,

    -- Absence Type
    absenceType           VARCHAR(100)    NOT NULL,
    absenceTypeId         BIGINT          NOT NULL,
    absencePatternCd      VARCHAR(20)     NOT NULL,

    -- Status Codes
    absenceStatusCd       VARCHAR(20)     NOT NULL,
    approvalStatusCd      VARCHAR(20)     NOT NULL,
    absenceDispStatus     VARCHAR(20)     NOT NULL,

    -- Date / Time
    startDate             DATE            NOT NULL,
    endDate               DATE            NOT NULL,
    startDateTime         DATETIMEOFFSET  NOT NULL,
    endDateTime           DATETIMEOFFSET  NOT NULL,
    submittedDate         DATE            NOT NULL,
    creationDate          DATETIMEOFFSET  NOT NULL,
    lastUpdateDate        DATETIMEOFFSET  NOT NULL,
    ApprovalDatetime      DATETIMEOFFSET  NULL,

    -- Duration
    duration              DECIMAL(10, 2)  NOT NULL,
    unitOfMeasure         VARCHAR(5)      NOT NULL,
    formattedDuration     VARCHAR(50)     NOT NULL,

    -- Details
    comments              VARCHAR(500)    NULL,
    employer              VARCHAR(200)    NOT NULL,
    legalEntityId         BIGINT          NOT NULL,
    legislationCode       VARCHAR(10)     NOT NULL,

    -- Flags (0/1 booleans)
    absenceEntryBasicFlag TINYINT         NOT NULL DEFAULT 0,
    employeeShiftFlag     TINYINT         NOT NULL DEFAULT 0,
    singleDayFlag         TINYINT         NOT NULL DEFAULT 0,
    openEndedFlag         TINYINT         NOT NULL DEFAULT 0,
    absenceUpdatableFlag  TINYINT         NOT NULL DEFAULT 0,

    -- Audit
    createdBy             VARCHAR(100)    NOT NULL,
    lastUpdatedBy         VARCHAR(100)    NOT NULL,
    objectVersionNumber   INT             NOT NULL,

    -- Primary Key
    CONSTRAINT PK_EmployeeAbsence PRIMARY KEY (personAbsenceEntryId)
);
