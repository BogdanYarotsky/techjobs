SELECT 
    t.TagName AS Language, 
    COUNT(*) AS ReportsCount,
    AVG(sr.ConvertedCompYearly) AS AverageSalary
FROM SalaryReports sr
JOIN SalaryReportTags srt ON srt.ReportID = sr.ReportID
JOIN Tags t ON t.TagID = srt.TagID
WHERE sr.Country = 'Germany' 
AND t.TagType = 'Language'
AND sr.YearsCodePro BETWEEN 2 AND 7
GROUP BY t.TagName
HAVING ReportsCount > 100
ORDER BY AverageSalary DESC