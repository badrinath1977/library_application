CREATE OR ALTER PROCEDURE GenAI_V1.InsertErrorLog
    @CorrelationId NVARCHAR(100) = NULL,
    @SessionId NVARCHAR(100) = NULL,
    @UserId NVARCHAR(100) = NULL,
    @ApplicationName NVARCHAR(200) = NULL,
    @ModuleName NVARCHAR(200) = NULL,
    @ErrorType NVARCHAR(300) = NULL,
    @ErrorCode NVARCHAR(100) = NULL,
    @ErrorMessage NVARCHAR(MAX) = NULL,
    @StackTrace NVARCHAR(MAX) = NULL,
    @RequestPath NVARCHAR(1000) = NULL,
    @RequestPayload NVARCHAR(MAX) = NULL,
    @AdditionalInfoJson NVARCHAR(MAX) = NULL,
    @IPAddress NVARCHAR(100) = NULL,
    @CreatedDate DATETIME2(7)
AS
BEGIN
    SET NOCOUNT ON;

    INSERT INTO GenAI_V1.ErrorLog
    (
        CorrelationId,
        SessionId,
        UserId,
        ApplicationName,
        ModuleName,
        ErrorType,
        ErrorCode,
        ErrorMessage,
        StackTrace,
        RequestPath,
        RequestPayload,
        AdditionalInfoJson,
        IPAddress,
        CreatedDate
    )
    VALUES
    (
        @CorrelationId,
        @SessionId,
        @UserId,
        @ApplicationName,
        @ModuleName,
        @ErrorType,
        @ErrorCode,
        @ErrorMessage,
        @StackTrace,
        @RequestPath,
        @RequestPayload,
        @AdditionalInfoJson,
        @IPAddress,
        @CreatedDate
    );
END;
GO

