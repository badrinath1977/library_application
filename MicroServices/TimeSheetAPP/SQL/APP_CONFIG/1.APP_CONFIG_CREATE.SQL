USE [genai_db]
GO

/****** Object:  Table [GenAI].[AppConfig]    Script Date: 5/18/2026 1:12:31 PM ******/
SET ANSI_NULLS ON
GO

SET QUOTED_IDENTIFIER ON
GO

CREATE TABLE [GenAI].[AppConfig](
	[ConfigId] [bigint] IDENTITY(1,1) NOT NULL,
	[ConfigKey] [nvarchar](200) NOT NULL,
	[ConfigValue] [nvarchar](max) NOT NULL,
	[ConfigType] [nvarchar](100) NOT NULL,
	[ApplicationName] [nvarchar](100) NOT NULL,
	[EnvironmentName] [nvarchar](50) NOT NULL,
	[IsSensitive] [bit] NOT NULL,
	[IsActive] [bit] NOT NULL,
	[Description] [nvarchar](500) NULL,
	[CreatedBy] [nvarchar](200) NOT NULL,
	[CreatedDate] [datetime2](7) NOT NULL,
	[ModifiedBy] [nvarchar](200) NULL,
	[ModifiedDate] [datetime2](7) NULL,
PRIMARY KEY CLUSTERED 
(
	[ConfigId] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
) ON [PRIMARY] TEXTIMAGE_ON [PRIMARY]
GO

ALTER TABLE [GenAI].[AppConfig] ADD  DEFAULT ((0)) FOR [IsSensitive]
GO

ALTER TABLE [GenAI].[AppConfig] ADD  DEFAULT ((1)) FOR [IsActive]
GO

ALTER TABLE [GenAI].[AppConfig] ADD  DEFAULT (sysutcdatetime()) FOR [CreatedDate]
GO


