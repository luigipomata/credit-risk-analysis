-- Query esplorative sul tasso di default, per la dashboard finale.
-- Da eseguire sul database CreditRiskAnalysis (tabella credit_applications).
--
-- Ogni query è delimitata da un marcatore "-- QUERY: <nome>" che
-- sql/export_analysis_results.py usa per individuarle ed eseguirle
-- singolarmente: non rimuovere o rinominare i marcatori senza aggiornare
-- anche quello script.
--
-- Nota: AVG() su una colonna INT/TINYINT in SQL Server tronca il risultato
-- a un intero (divisione intera), quindi il cast a FLOAT prima di AVG() è
-- necessario per ottenere una percentuale corretta, non un arrotondamento a 0/1.


-- ============================================================
-- QUERY: tasso_default_per_fascia_reddito
-- Tasso di default per quartile di MonthlyIncome (NTILE(4): Q1 = redditi
-- più bassi, Q4 = redditi più alti).
-- ============================================================
WITH redditi_quartili AS (
    SELECT
        SeriousDlqin2yrs,
        MonthlyIncome,
        NTILE(4) OVER (ORDER BY MonthlyIncome) AS quartile_reddito
    FROM credit_applications
)
SELECT
    quartile_reddito,
    MIN(MonthlyIncome)                                             AS reddito_minimo,
    MAX(MonthlyIncome)                                             AS reddito_massimo,
    COUNT(*)                                                       AS numero_clienti,
    SUM(CAST(SeriousDlqin2yrs AS INT))                             AS numero_insolventi,
    CAST(AVG(CAST(SeriousDlqin2yrs AS FLOAT)) * 100 AS DECIMAL(5, 2)) AS tasso_default_pct
FROM redditi_quartili
GROUP BY quartile_reddito
ORDER BY quartile_reddito;


-- ============================================================
-- QUERY: tasso_default_per_fascia_eta
-- Tasso di default per fascia d'età (decadi).
-- ============================================================
SELECT
    CASE
        WHEN age < 20 THEN 'under 20'
        WHEN age BETWEEN 20 AND 29 THEN '20-29'
        WHEN age BETWEEN 30 AND 39 THEN '30-39'
        WHEN age BETWEEN 40 AND 49 THEN '40-49'
        WHEN age BETWEEN 50 AND 59 THEN '50-59'
        WHEN age BETWEEN 60 AND 69 THEN '60-69'
        WHEN age BETWEEN 70 AND 79 THEN '70-79'
        ELSE '80+'
    END                                                             AS fascia_eta,
    MIN(age)                                                        AS eta_minima,
    MAX(age)                                                        AS eta_massima,
    COUNT(*)                                                        AS numero_clienti,
    SUM(CAST(SeriousDlqin2yrs AS INT))                              AS numero_insolventi,
    CAST(AVG(CAST(SeriousDlqin2yrs AS FLOAT)) * 100 AS DECIMAL(5, 2)) AS tasso_default_pct
FROM credit_applications
GROUP BY
    CASE
        WHEN age < 20 THEN 'under 20'
        WHEN age BETWEEN 20 AND 29 THEN '20-29'
        WHEN age BETWEEN 30 AND 39 THEN '30-39'
        WHEN age BETWEEN 40 AND 49 THEN '40-49'
        WHEN age BETWEEN 50 AND 59 THEN '50-59'
        WHEN age BETWEEN 60 AND 69 THEN '60-69'
        WHEN age BETWEEN 70 AND 79 THEN '70-79'
        ELSE '80+'
    END
ORDER BY MIN(age);


-- ============================================================
-- QUERY: tasso_default_per_prestiti_aperti
-- Tasso di default per fasce di NumberOfOpenCreditLinesAndLoans
-- (fasce di ampiezza 5, definite sulla base della distribuzione osservata:
-- mediana 8, 90° percentile 15, 99° percentile 24).
-- ============================================================
SELECT
    CASE
        WHEN NumberOfOpenCreditLinesAndLoans BETWEEN 0 AND 4 THEN '0-4'
        WHEN NumberOfOpenCreditLinesAndLoans BETWEEN 5 AND 9 THEN '5-9'
        WHEN NumberOfOpenCreditLinesAndLoans BETWEEN 10 AND 14 THEN '10-14'
        WHEN NumberOfOpenCreditLinesAndLoans BETWEEN 15 AND 19 THEN '15-19'
        WHEN NumberOfOpenCreditLinesAndLoans BETWEEN 20 AND 24 THEN '20-24'
        ELSE '25+'
    END                                                             AS fascia_prestiti_aperti,
    MIN(NumberOfOpenCreditLinesAndLoans)                            AS minimo,
    MAX(NumberOfOpenCreditLinesAndLoans)                            AS massimo,
    COUNT(*)                                                        AS numero_clienti,
    SUM(CAST(SeriousDlqin2yrs AS INT))                              AS numero_insolventi,
    CAST(AVG(CAST(SeriousDlqin2yrs AS FLOAT)) * 100 AS DECIMAL(5, 2)) AS tasso_default_pct
FROM credit_applications
GROUP BY
    CASE
        WHEN NumberOfOpenCreditLinesAndLoans BETWEEN 0 AND 4 THEN '0-4'
        WHEN NumberOfOpenCreditLinesAndLoans BETWEEN 5 AND 9 THEN '5-9'
        WHEN NumberOfOpenCreditLinesAndLoans BETWEEN 10 AND 14 THEN '10-14'
        WHEN NumberOfOpenCreditLinesAndLoans BETWEEN 15 AND 19 THEN '15-19'
        WHEN NumberOfOpenCreditLinesAndLoans BETWEEN 20 AND 24 THEN '20-24'
        ELSE '25+'
    END
ORDER BY MIN(NumberOfOpenCreditLinesAndLoans);
