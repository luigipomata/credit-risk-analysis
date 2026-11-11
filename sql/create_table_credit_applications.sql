-- DDL di riferimento per la tabella credit_applications.
-- Creata automaticamente da import_credit_data.py se non esiste già;
-- questo file serve come riferimento/versione da poter eseguire anche a mano
-- (es. in SSMS) sul database CreditRiskAnalysis.
--
-- I nomi delle colonne originali del dataset "Give Me Some Credit" che
-- contenevano un trattino (es. NumberOfTime30-59DaysPastDueNotWorse) sono
-- stati riscritti con underscore, non validi i trattini come identificatori
-- SQL Server senza racchiuderli tra parentesi quadre.

CREATE TABLE credit_applications (
    id                                      INT             NOT NULL PRIMARY KEY,
    SeriousDlqin2yrs                        TINYINT         NOT NULL,
    RevolvingUtilizationOfUnsecuredLines    FLOAT           NOT NULL,
    age                                     INT             NOT NULL,
    NumberOfTime30_59DaysPastDueNotWorse    INT             NOT NULL,
    DebtRatio                               FLOAT           NOT NULL,
    MonthlyIncome                           DECIMAL(12, 2)  NOT NULL,
    NumberOfOpenCreditLinesAndLoans         INT             NOT NULL,
    NumberOfTimes90DaysLate                 INT             NOT NULL,
    NumberRealEstateLoansOrLines            INT             NOT NULL,
    NumberOfTime60_89DaysPastDueNotWorse    INT             NOT NULL,
    NumberOfDependents                      INT             NOT NULL
);
