-- 모든 회사의 코드와 이름 조회
SELECT DISTINCT corp_code, corp_name
FROM fin_data
ORDER BY corp_name;


-- 특정 회사 코드의 재무제표 데이터 확인
SELECT DISTINCT corp_code, corp_name, bsns_year, sj_div, sj_nm
FROM fin_data
WHERE corp_code = '01515323'  -- LG에너지솔루션의 회사 코드
ORDER BY bsns_year DESC, sj_div;


-- 회사 코드와 재무비율 데이터 함께 조회
SELECT 
    s.corp_code,
    s.corp_name,
    s.bsns_year,
    ROUND(s.debt_ratio, 2) as debt_ratio,
    ROUND(s.current_ratio, 2) as current_ratio,
    ROUND(s.interest_coverage_ratio, 2) as interest_coverage_ratio,
    ROUND(s.operating_profit_ratio, 2) as operating_profit_ratio,
    ROUND(s.net_profit_ratio, 2) as net_profit_ratio,
    ROUND(s.roe, 2) as roe,
    ROUND(s.roa, 2) as roa,
    ROUND(s.debt_dependency, 2) as debt_dependency,
    ROUND(s.cash_flow_debt_ratio, 2) as cash_flow_debt_ratio,
    ROUND(s.sales_growth, 2) as sales_growth,
    ROUND(s.operating_profit_growth, 2) as operating_profit_growth,
    ROUND(s.eps_growth, 2) as eps_growth
FROM fin_data s
WHERE s.corp_name = 'LG에너지솔루션'
AND s.sj_div = 'RATIO'
ORDER BY s.bsns_year DESC;