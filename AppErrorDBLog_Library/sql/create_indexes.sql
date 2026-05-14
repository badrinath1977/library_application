CREATE INDEX IX_ErrorLog_CreatedDate
ON GenAI_V1.ErrorLog (CreatedDate DESC);
GO

CREATE INDEX IX_ErrorLog_CorrelationId
ON GenAI_V1.ErrorLog (CorrelationId)
WHERE CorrelationId IS NOT NULL;
GO

CREATE INDEX IX_ErrorLog_Application_Module
ON GenAI_V1.ErrorLog (ApplicationName, ModuleName, CreatedDate DESC);
GO

