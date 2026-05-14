IF NOT EXISTS (SELECT 1 FROM sys.schemas WHERE name = 'GenAI_V1')
BEGIN
    EXEC('CREATE SCHEMA GenAI_V1');
END;
GO

IF OBJECT_ID('GenAI_V1.ErrorLog', 'U') IS NULL
BEGIN
    CREATE TABLE GenAI_V1.ErrorLog
    (
        Id BIGINT IDENTITY(1,1) NOT NULL PRIMARY KEY,
        CorrelationId NVARCHAR(100) NULL,
        SessionId NVARCHAR(100) NULL,
        UserId NVARCHAR(100) NULL,
        ApplicationName NVARCHAR(200) NULL,
        ModuleName NVARCHAR(200) NULL,
        ErrorType NVARCHAR(300) NULL,
        ErrorCode NVARCHAR(100) NULL,
        ErrorMessage NVARCHAR(MAX) NULL,
        StackTrace NVARCHAR(MAX) NULL,
        RequestPath NVARCHAR(1000) NULL,
        RequestPayload NVARCHAR(MAX) NULL,
        AdditionalInfoJson NVARCHAR(MAX) NULL,
        IPAddress NVARCHAR(100) NULL,
        CreatedDate DATETIME2(7) NOT NULL
    );
END;
GO
