-- 회사 정보 테이블
-- 기업의 기본 정보를 저장하는 테이블
CREATE TABLE companies (
    corp_code VARCHAR(20) PRIMARY KEY,    -- 고유한 기업 코드
    corp_name VARCHAR(100) NOT NULL,      -- 기업명
    stock_code VARCHAR(20)                -- 주식 코드 (상장사인 경우)
);

-- 재무제표 유형 테이블
-- 재무제표의 종류를 정의하는 테이블 (예: 재무상태표, 손익계산서 등)
CREATE TABLE statement (
    sj_div VARCHAR(10) PRIMARY KEY,       -- 재무제표 구분 코드
    sj_nm VARCHAR(100) NOT NULL           -- 재무제표 구분명
);

-- 보고서 정보 테이블
-- 공시된 재무제표 보고서의 메타데이터를 저장하는 테이블
CREATE TABLE reports (
    rcept_no VARCHAR(20) PRIMARY KEY,     -- 접수번호 (공시 문서의 고유 식별자)
    reprt_code VARCHAR(20) NOT NULL       -- 보고서 코드
);

-- 재무 데이터 (기본)
-- 기업의 실제 재무 데이터를 저장하는 메인 테이블
CREATE TABLE financials (
    id SERIAL PRIMARY KEY,                -- 자동 증가하는 고유 식별자
    corp_code VARCHAR(20) NOT NULL,       -- 기업 코드
    bsns_year VARCHAR(4) NOT NULL,        -- 사업연도
    sj_div VARCHAR(10) NOT NULL,          -- 재무제표 구분
    account_nm VARCHAR(100) NOT NULL,     -- 계정명 (예: 자산총계, 매출액 등)
    thstrm_nm VARCHAR(20),                -- 당기명
    thstrm_amount NUMERIC,                -- 당기금액
    frmtrm_nm VARCHAR(20),                -- 전기명
    frmtrm_amount NUMERIC,                -- 전기금액
    bfefrmtrm_nm VARCHAR(20),             -- 전전기명
    bfefrmtrm_amount NUMERIC,             -- 전전기금액
    ord INTEGER,                          -- 정렬 순서
    currency VARCHAR(10),                 -- 통화 단위
    rcept_no VARCHAR(20),                 -- 접수번호
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,    -- 레코드 생성 시간
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,    -- 레코드 수정 시간
    FOREIGN KEY (corp_code) REFERENCES companies(corp_code),
    FOREIGN KEY (sj_div) REFERENCES statement(sj_div),
    FOREIGN KEY (rcept_no) REFERENCES reports(rcept_no),
    UNIQUE(corp_code, bsns_year, sj_div, account_nm)  -- 동일한 재무 데이터 중복 방지
);

-- 재무 비율 테이블
-- 기업의 주요 재무 비율을 계산하여 저장하는 테이블
CREATE TABLE metrics (
    id SERIAL PRIMARY KEY,                -- 자동 증가하는 고유 식별자
    corp_code VARCHAR(20) NOT NULL,       -- 기업 코드
    bsns_year VARCHAR(4) NOT NULL,        -- 사업연도
    debt_ratio NUMERIC,                   -- 부채비율
    current_ratio NUMERIC,                -- 유동비율
    operating_profit_ratio NUMERIC,       -- 영업이익률
    net_profit_ratio NUMERIC,             -- 순이익률
    roe NUMERIC,                          -- 자기자본이익률
    roa NUMERIC,                          -- 총자산이익률
    debt_dependency NUMERIC,              -- 부채의존도
    sales_growth NUMERIC,                 -- 매출성장률
    operating_profit_growth NUMERIC,      -- 영업이익성장률
    eps_growth NUMERIC,                   -- 주당순이익성장률
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,    -- 레코드 생성 시간
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,    -- 레코드 수정 시간
    FOREIGN KEY (corp_code) REFERENCES companies(corp_code),
    UNIQUE(corp_code, bsns_year)          -- 동일 연도의 중복 데이터 방지
);