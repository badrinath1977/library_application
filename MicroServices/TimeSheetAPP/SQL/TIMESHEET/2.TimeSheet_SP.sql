CREATE PROCEDURE genai.sp_SearchEmployeeAbsence
    -- Person Filters
    @personNumber           VARCHAR(20)     = NULL,
    @personId               BIGINT          = NULL,
    @personAbsenceEntryId   BIGINT          = NULL,

    -- Absence Type Filters
    @absenceType            VARCHAR(100)    = NULL,
    @absenceTypeId          BIGINT          = NULL,
    @absencePatternCd       VARCHAR(20)     = NULL,

    -- Status Filters
    @absenceStatusCd        VARCHAR(20)     = NULL,
    @approvalStatusCd       VARCHAR(20)     = NULL,
    @absenceDispStatus      VARCHAR(20)     = NULL,

    -- Date Range Filters
    @startDateFrom          DATE            = NULL,
    @startDateTo            DATE            = NULL,
    @endDateFrom            DATE            = NULL,
    @endDateTo              DATE            = NULL,
    @submittedDateFrom      DATE            = NULL,
    @submittedDateTo        DATE            = NULL,
    @creationDateFrom       DATETIMEOFFSET  = NULL,
    @creationDateTo         DATETIMEOFFSET  = NULL,
    @lastUpdateDateFrom     DATETIMEOFFSET  = NULL,
    @lastUpdateDateTo       DATETIMEOFFSET  = NULL,
    @approvalDateFrom       DATETIMEOFFSET  = NULL,
    @approvalDateTo         DATETIMEOFFSET  = NULL,

    -- Duration Filters
    @durationMin            DECIMAL(10,2)   = NULL,
    @durationMax            DECIMAL(10,2)   = NULL,
    @unitOfMeasure          VARCHAR(5)      = NULL,

    -- Detail Filters
    @commentsKeyword        VARCHAR(500)    = NULL,
    @employer               VARCHAR(200)    = NULL,
    @legalEntityId          BIGINT          = NULL,
    @legislationCode        VARCHAR(10)     = NULL,

    -- Flag Filters
    @absenceEntryBasicFlag  TINYINT         = NULL,
    @employeeShiftFlag      TINYINT         = NULL,
    @singleDayFlag          TINYINT         = NULL,
    @openEndedFlag          TINYINT         = NULL,
    @absenceUpdatableFlag   TINYINT         = NULL,

    -- Audit Filters
    @createdBy              VARCHAR(100)    = NULL,
    @lastUpdatedBy          VARCHAR(100)    = NULL,
    @objectVersionNumber    INT             = NULL,

    -- Pagination
    @pageNumber             INT             = 1,
    @pageSize               INT             = 20,

    -- Sorting
    @sortColumn             VARCHAR(50)     = 'startDate',
    @sortDirection          VARCHAR(4)      = 'DESC'
AS
BEGIN
    SET NOCOUNT ON;

    -- Validate pagination inputs
    IF @pageNumber < 1  SET @pageNumber = 1;
    IF @pageSize   < 1  SET @pageSize   = 20;
    IF @pageSize   > 200 SET @pageSize  = 200;

    -- Validate sort direction
    IF UPPER(@sortDirection) NOT IN ('ASC', 'DESC')
        SET @sortDirection = 'DESC';

    -- Validate sort column (whitelist to prevent SQL injection)
    IF @sortColumn NOT IN (
        'personNumber', 'startDate', 'endDate', 'submittedDate',
        'creationDate', 'lastUpdateDate', 'ApprovalDatetime',
        'duration', 'absenceStatusCd', 'approvalStatusCd',
        'absenceType', 'absenceDispStatus'
    )
        SET @sortColumn = 'startDate';

    -- Total count for pagination metadata
    DECLARE @totalRecords INT;

    SELECT @totalRecords = COUNT(*)
    FROM EmployeeAbsence
    WHERE
        -- Person Filters
        (@personNumber          IS NULL OR personNumber         = @personNumber)
        AND (@personId          IS NULL OR personId             = @personId)
        AND (@personAbsenceEntryId IS NULL OR personAbsenceEntryId = @personAbsenceEntryId)

        -- Absence Type Filters
        AND (@absenceType       IS NULL OR absenceType          LIKE '%' + @absenceType + '%')
        AND (@absenceTypeId     IS NULL OR absenceTypeId        = @absenceTypeId)
        AND (@absencePatternCd  IS NULL OR absencePatternCd     = @absencePatternCd)

        -- Status Filters
        AND (@absenceStatusCd   IS NULL OR absenceStatusCd      = @absenceStatusCd)
        AND (@approvalStatusCd  IS NULL OR approvalStatusCd     = @approvalStatusCd)
        AND (@absenceDispStatus IS NULL OR absenceDispStatus     = @absenceDispStatus)

        -- Date Range Filters
        AND (@startDateFrom     IS NULL OR startDate            >= @startDateFrom)
        AND (@startDateTo       IS NULL OR startDate            <= @startDateTo)
        AND (@endDateFrom       IS NULL OR endDate              >= @endDateFrom)
        AND (@endDateTo         IS NULL OR endDate              <= @endDateTo)
        AND (@submittedDateFrom IS NULL OR submittedDate        >= @submittedDateFrom)
        AND (@submittedDateTo   IS NULL OR submittedDate        <= @submittedDateTo)
        AND (@creationDateFrom  IS NULL OR creationDate         >= @creationDateFrom)
        AND (@creationDateTo    IS NULL OR creationDate         <= @creationDateTo)
        AND (@lastUpdateDateFrom IS NULL OR lastUpdateDate      >= @lastUpdateDateFrom)
        AND (@lastUpdateDateTo  IS NULL OR lastUpdateDate       <= @lastUpdateDateTo)
        AND (@approvalDateFrom  IS NULL OR ApprovalDatetime     >= @approvalDateFrom)
        AND (@approvalDateTo    IS NULL OR ApprovalDatetime     <= @approvalDateTo)

        -- Duration Filters
        AND (@durationMin       IS NULL OR duration             >= @durationMin)
        AND (@durationMax       IS NULL OR duration             <= @durationMax)
        AND (@unitOfMeasure     IS NULL OR unitOfMeasure        = @unitOfMeasure)

        -- Detail Filters
        AND (@commentsKeyword   IS NULL OR comments             LIKE '%' + @commentsKeyword + '%')
        AND (@employer          IS NULL OR employer             LIKE '%' + @employer + '%')
        AND (@legalEntityId     IS NULL OR legalEntityId        = @legalEntityId)
        AND (@legislationCode   IS NULL OR legislationCode      = @legislationCode)

        -- Flag Filters
        AND (@absenceEntryBasicFlag IS NULL OR absenceEntryBasicFlag = @absenceEntryBasicFlag)
        AND (@employeeShiftFlag IS NULL OR employeeShiftFlag    = @employeeShiftFlag)
        AND (@singleDayFlag     IS NULL OR singleDayFlag        = @singleDayFlag)
        AND (@openEndedFlag     IS NULL OR openEndedFlag        = @openEndedFlag)
        AND (@absenceUpdatableFlag IS NULL OR absenceUpdatableFlag = @absenceUpdatableFlag)

        -- Audit Filters
        AND (@createdBy         IS NULL OR createdBy            = @createdBy)
        AND (@lastUpdatedBy     IS NULL OR lastUpdatedBy        = @lastUpdatedBy)
        AND (@objectVersionNumber IS NULL OR objectVersionNumber = @objectVersionNumber);

    -- Main result with dynamic sorting + pagination
    SELECT
        -- Person Info
        personNumber,
        personId,
        personAbsenceEntryId,

        -- Absence Type
        absenceType,
        absenceTypeId,
        absencePatternCd,

        -- Statuses
        absenceStatusCd,
        approvalStatusCd,
        absenceDispStatus,

        -- Dates
        startDate,
        endDate,
        startDateTime,
        endDateTime,
        submittedDate,
        creationDate,
        lastUpdateDate,
        ApprovalDatetime,

        -- Duration
        duration,
        unitOfMeasure,
        formattedDuration,

        -- Details
        comments,
        employer,
        legalEntityId,
        legislationCode,

        -- Flags
        absenceEntryBasicFlag,
        employeeShiftFlag,
        singleDayFlag,
        openEndedFlag,
        absenceUpdatableFlag,

        -- Audit
        createdBy,
        lastUpdatedBy,
        objectVersionNumber,

        -- Pagination Metadata
        @totalRecords           AS totalRecords,
        @pageNumber             AS currentPage,
        @pageSize               AS pageSize,
        CEILING(CAST(@totalRecords AS FLOAT) / @pageSize) AS totalPages

    FROM EmployeeAbsence
    WHERE
        (@personNumber          IS NULL OR personNumber         = @personNumber)
        AND (@personId          IS NULL OR personId             = @personId)
        AND (@personAbsenceEntryId IS NULL OR personAbsenceEntryId = @personAbsenceEntryId)
        AND (@absenceType       IS NULL OR absenceType          LIKE '%' + @absenceType + '%')
        AND (@absenceTypeId     IS NULL OR absenceTypeId        = @absenceTypeId)
        AND (@absencePatternCd  IS NULL OR absencePatternCd     = @absencePatternCd)
        AND (@absenceStatusCd   IS NULL OR absenceStatusCd      = @absenceStatusCd)
        AND (@approvalStatusCd  IS NULL OR approvalStatusCd     = @approvalStatusCd)
        AND (@absenceDispStatus IS NULL OR absenceDispStatus     = @absenceDispStatus)
        AND (@startDateFrom     IS NULL OR startDate            >= @startDateFrom)
        AND (@startDateTo       IS NULL OR startDate            <= @startDateTo)
        AND (@endDateFrom       IS NULL OR endDate              >= @endDateFrom)
        AND (@endDateTo         IS NULL OR endDate              <= @endDateTo)
        AND (@submittedDateFrom IS NULL OR submittedDate        >= @submittedDateFrom)
        AND (@submittedDateTo   IS NULL OR submittedDate        <= @submittedDateTo)
        AND (@creationDateFrom  IS NULL OR creationDate         >= @creationDateFrom)
        AND (@creationDateTo    IS NULL OR creationDate         <= @creationDateTo)
        AND (@lastUpdateDateFrom IS NULL OR lastUpdateDate      >= @lastUpdateDateFrom)
        AND (@lastUpdateDateTo  IS NULL OR lastUpdateDate       <= @lastUpdateDateTo)
        AND (@approvalDateFrom  IS NULL OR ApprovalDatetime     >= @approvalDateFrom)
        AND (@approvalDateTo    IS NULL OR ApprovalDatetime     <= @approvalDateTo)
        AND (@durationMin       IS NULL OR duration             >= @durationMin)
        AND (@durationMax       IS NULL OR duration             <= @durationMax)
        AND (@unitOfMeasure     IS NULL OR unitOfMeasure        = @unitOfMeasure)
        AND (@commentsKeyword   IS NULL OR comments             LIKE '%' + @commentsKeyword + '%')
        AND (@employer          IS NULL OR employer             LIKE '%' + @employer + '%')
        AND (@legalEntityId     IS NULL OR legalEntityId        = @legalEntityId)
        AND (@legislationCode   IS NULL OR legislationCode      = @legislationCode)
        AND (@absenceEntryBasicFlag IS NULL OR absenceEntryBasicFlag = @absenceEntryBasicFlag)
        AND (@employeeShiftFlag IS NULL OR employeeShiftFlag    = @employeeShiftFlag)
        AND (@singleDayFlag     IS NULL OR singleDayFlag        = @singleDayFlag)
        AND (@openEndedFlag     IS NULL OR openEndedFlag        = @openEndedFlag)
        AND (@absenceUpdatableFlag IS NULL OR absenceUpdatableFlag = @absenceUpdatableFlag)
        AND (@createdBy         IS NULL OR createdBy            = @createdBy)
        AND (@lastUpdatedBy     IS NULL OR lastUpdatedBy        = @lastUpdatedBy)
        AND (@objectVersionNumber IS NULL OR objectVersionNumber = @objectVersionNumber)

    ORDER BY
        CASE WHEN @sortColumn = 'startDate'        AND @sortDirection = 'ASC'  THEN startDate        END ASC,
        CASE WHEN @sortColumn = 'startDate'        AND @sortDirection = 'DESC' THEN startDate        END DESC,
        CASE WHEN @sortColumn = 'endDate'          AND @sortDirection = 'ASC'  THEN endDate          END ASC,
        CASE WHEN @sortColumn = 'endDate'          AND @sortDirection = 'DESC' THEN endDate          END DESC,
        CASE WHEN @sortColumn = 'submittedDate'    AND @sortDirection = 'ASC'  THEN submittedDate    END ASC,
        CASE WHEN @sortColumn = 'submittedDate'    AND @sortDirection = 'DESC' THEN submittedDate    END DESC,
        CASE WHEN @sortColumn = 'duration'         AND @sortDirection = 'ASC'  THEN duration         END ASC,
        CASE WHEN @sortColumn = 'duration'         AND @sortDirection = 'DESC' THEN duration         END DESC,
        CASE WHEN @sortColumn = 'creationDate'     AND @sortDirection = 'ASC'  THEN creationDate     END ASC,
        CASE WHEN @sortColumn = 'creationDate'     AND @sortDirection = 'DESC' THEN creationDate     END DESC,
        CASE WHEN @sortColumn = 'lastUpdateDate'   AND @sortDirection = 'ASC'  THEN lastUpdateDate   END ASC,
        CASE WHEN @sortColumn = 'lastUpdateDate'   AND @sortDirection = 'DESC' THEN lastUpdateDate   END DESC,
        CASE WHEN @sortColumn = 'ApprovalDatetime' AND @sortDirection = 'ASC'  THEN ApprovalDatetime END ASC,
        CASE WHEN @sortColumn = 'ApprovalDatetime' AND @sortDirection = 'DESC' THEN ApprovalDatetime END DESC,
        -- String columns
        CASE WHEN @sortColumn = 'personNumber'     AND @sortDirection = 'ASC'  THEN personNumber     END ASC,
        CASE WHEN @sortColumn = 'personNumber'     AND @sortDirection = 'DESC' THEN personNumber     END DESC,
        CASE WHEN @sortColumn = 'absenceStatusCd'  AND @sortDirection = 'ASC'  THEN absenceStatusCd  END ASC,
        CASE WHEN @sortColumn = 'absenceStatusCd'  AND @sortDirection = 'DESC' THEN absenceStatusCd  END DESC,
        CASE WHEN @sortColumn = 'approvalStatusCd' AND @sortDirection = 'ASC'  THEN approvalStatusCd END ASC,
        CASE WHEN @sortColumn = 'approvalStatusCd' AND @sortDirection = 'DESC' THEN approvalStatusCd END DESC,
        CASE WHEN @sortColumn = 'absenceType'      AND @sortDirection = 'ASC'  THEN absenceType      END ASC,
        CASE WHEN @sortColumn = 'absenceType'      AND @sortDirection = 'DESC' THEN absenceType      END DESC,
        CASE WHEN @sortColumn = 'absenceDispStatus' AND @sortDirection = 'ASC' THEN absenceDispStatus END ASC,
        CASE WHEN @sortColumn = 'absenceDispStatus' AND @sortDirection = 'DESC' THEN absenceDispStatus END DESC

    OFFSET (@pageNumber - 1) * @pageSize ROWS
    FETCH NEXT @pageSize ROWS ONLY;

END;
GO
