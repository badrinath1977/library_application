EXEC sp_SearchEmployeeAbsence @personNumber = '41556';


EXEC sp_SearchEmployeeAbsence
    @approvalStatusCd = 'APPROVED',
    @startDateFrom    = '2025-09-01',
    @startDateTo      = '2025-12-31';


EXEC sp_SearchEmployeeAbsence
    @commentsKeyword = 'fever',
    @pageNumber      = 1,
    @pageSize        = 10;


EXEC sp_SearchEmployeeAbsence
    @personNumber  = '41556',
    @sortColumn    = 'duration',
    @sortDirection = 'DESC';
