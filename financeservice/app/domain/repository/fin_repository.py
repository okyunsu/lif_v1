from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
import logging
from typing import Optional, List, Dict, Any

logger = logging.getLogger(__name__)

async def delete_financial_statements(
    db_session: AsyncSession,
    corp_code: str,
    bsns_year: str
) -> None:
    """재무제표 데이터를 삭제합니다.
    
    Args:
        db_session: 데이터베이스 세션
        corp_code: 회사 코드
        bsns_year: 삭제할 사업연도
    """
    try:
        delete_query = text("""
            DELETE FROM financials 
            WHERE corp_code = :corp_code 
            AND bsns_year = :bsns_year
        """)
        await db_session.execute(delete_query, {
            "corp_code": corp_code,
            "bsns_year": bsns_year
        })
        await db_session.commit()
    except Exception as e:
        await db_session.rollback()
        raise

async def insert_financial_statement(db_session: AsyncSession, data: Dict[str, Any]) -> None:
    """재무제표 데이터를 저장합니다."""
    query = text("""
        INSERT INTO fin_data (
            corp_code, corp_name, stock_code, bsns_year, sj_div, sj_nm, 
            account_nm, thstrm_amount, frmtrm_amount, bfefrmtrm_amount, ord
        ) VALUES (
            :corp_code, :corp_name, :stock_code, :bsns_year, :sj_div, :sj_nm,
            :account_nm, :thstrm_amount, :frmtrm_amount, :bfefrmtrm_amount, :ord
        )
    """)
    await db_session.execute(query, data)
    await db_session.commit()

async def get_statement_summary(db_session: AsyncSession) -> List[Dict[str, Any]]:
    """회사별 재무제표 종류와 데이터 수를 조회합니다."""
    query = text("""
        SELECT corp_code, corp_name, sj_div, sj_nm, COUNT(*) as count
        FROM fin_data
        GROUP BY corp_code, corp_name, sj_div, sj_nm
        ORDER BY corp_code, sj_div
    """)
    result = await db_session.execute(query)
    return [dict(row) for row in result]

async def get_key_financial_items(db_session: AsyncSession) -> List[Dict[str, Any]]:
    """주요 재무 항목을 조회합니다."""
    query = text("""
        SELECT 
            corp_code, corp_name, bsns_year, sj_div, sj_nm,
            account_nm, thstrm_amount, frmtrm_amount, bfefrmtrm_amount
        FROM fin_data
        WHERE account_nm IN (
            '자산총계', '부채총계', '자본총계', '유동자산', '유동부채',
            '매출액', '영업이익', '당기순이익', '영업활동현금흐름'
        )
        ORDER BY corp_code, bsns_year DESC, sj_div, account_nm
    """)
    result = await db_session.execute(query)
    return [dict(row) for row in result]

async def get_company_by_name(db_session: AsyncSession, company_name: str) -> Optional[Dict[str, Any]]:
    """회사명으로 회사 정보를 조회합니다."""
    query = text("""
        SELECT DISTINCT corp_code, corp_name, stock_code
        FROM fin_data
        WHERE corp_name = :company_name
        LIMIT 1
    """)
    result = await db_session.execute(query, {"company_name": company_name})
    row = result.fetchone()
    if row:
        if isinstance(row, dict):
            return row
        return dict(zip(result.keys(), row))
    return None

async def get_financial_statements_by_corp_code(db_session: AsyncSession, corp_code: str) -> List[Dict[str, Any]]:
    """회사 코드로 재무제표 데이터를 조회합니다."""
    query = text("""
        SELECT 
            corp_code, corp_name, stock_code, rcept_no, reprt_code,
            bsns_year, sj_div, sj_nm, account_nm, thstrm_nm,
            thstrm_amount, frmtrm_nm, frmtrm_amount, bfefrmtrm_nm,
            bfefrmtrm_amount, ord, currency
        FROM fin_data
        WHERE corp_code = :corp_code
        ORDER BY bsns_year DESC, sj_div, ord
    """)
    result = await db_session.execute(query, {"corp_code": corp_code})
    return [dict(row) for row in result]

async def save_financial_statements(db_session: AsyncSession, statements: List[Dict[str, Any]]) -> None:
    """재무제표 데이터를 저장합니다."""
    try:
        # 1. statement 테이블에 재무제표 유형 저장
        for stmt in statements:
            insert_statement_query = text("""
                INSERT INTO statement (sj_div, sj_nm)
                VALUES (:sj_div, :sj_nm)
                ON CONFLICT (sj_div) DO NOTHING
            """)
            await db_session.execute(insert_statement_query, {
                "sj_div": stmt["sj_div"],
                "sj_nm": stmt["sj_nm"]
            })

        # 2. companies 테이블에 회사 정보 저장
        if statements:
            insert_company_query = text("""
                INSERT INTO companies (corp_code, corp_name, stock_code)
                VALUES (:corp_code, :corp_name, :stock_code)
                ON CONFLICT (corp_code) DO UPDATE SET
                    corp_name = EXCLUDED.corp_name,
                    stock_code = EXCLUDED.stock_code
            """)
            await db_session.execute(insert_company_query, {
                "corp_code": statements[0]["corp_code"],
                "corp_name": statements[0]["corp_name"],
                "stock_code": statements[0].get("stock_code", "")
            })

        # 3. reports 테이블에 보고서 정보 저장
        if statements:
            insert_report_query = text("""
                INSERT INTO reports (rcept_no, reprt_code)
                VALUES (:rcept_no, :reprt_code)
                ON CONFLICT (rcept_no) DO NOTHING
            """)
            await db_session.execute(insert_report_query, {
                "rcept_no": statements[0]["rcept_no"],
                "reprt_code": "11011"  # 사업보고서 코드
            })

        # 4. financials 테이블에 재무제표 데이터 저장
        for stmt in statements:
            insert_financial_query = text("""
                INSERT INTO financials (
                    corp_code, bsns_year, sj_div, account_nm,
                    thstrm_nm, thstrm_amount,
                    frmtrm_nm, frmtrm_amount,
                    bfefrmtrm_nm, bfefrmtrm_amount,
                    ord, currency, rcept_no
                ) VALUES (
                    :corp_code, :bsns_year, :sj_div, :account_nm,
                    :thstrm_nm, :thstrm_amount,
                    :frmtrm_nm, :frmtrm_amount,
                    :bfefrmtrm_nm, :bfefrmtrm_amount,
                    :ord, :currency, :rcept_no
                )
                ON CONFLICT (corp_code, bsns_year, sj_div, account_nm) DO UPDATE SET
                    thstrm_nm = EXCLUDED.thstrm_nm,
                    thstrm_amount = EXCLUDED.thstrm_amount,
                    frmtrm_nm = EXCLUDED.frmtrm_nm,
                    frmtrm_amount = EXCLUDED.frmtrm_amount,
                    bfefrmtrm_nm = EXCLUDED.bfefrmtrm_nm,
                    bfefrmtrm_amount = EXCLUDED.bfefrmtrm_amount,
                    ord = EXCLUDED.ord,
                    currency = EXCLUDED.currency,
                    rcept_no = EXCLUDED.rcept_no,
                    updated_at = CURRENT_TIMESTAMP
            """)
            await db_session.execute(insert_financial_query, stmt)

        await db_session.commit()

    except Exception as e:
        await db_session.rollback()
        raise

async def save_financial_ratios(db_session: AsyncSession, ratios: Dict[str, Any]) -> None:
    """재무비율을 저장합니다."""
    query = text("""
        INSERT INTO fin_data (
            corp_code, corp_name, bsns_year,
            debt_ratio, current_ratio, interest_coverage_ratio,
            operating_profit_ratio, net_profit_ratio, roe, roa,
            debt_dependency, cash_flow_debt_ratio,
            sales_growth, operating_profit_growth, eps_growth
        ) VALUES (
            :corp_code, :corp_name, :bsns_year,
            :debt_ratio, :current_ratio, :interest_coverage_ratio,
            :operating_profit_ratio, :net_profit_ratio, :roe, :roa,
            :debt_dependency, :cash_flow_debt_ratio,
            :sales_growth, :operating_profit_growth, :eps_growth
        )
        ON CONFLICT (corp_code, bsns_year) 
        DO UPDATE SET
            debt_ratio = EXCLUDED.debt_ratio,
            current_ratio = EXCLUDED.current_ratio,
            interest_coverage_ratio = EXCLUDED.interest_coverage_ratio,
            operating_profit_ratio = EXCLUDED.operating_profit_ratio,
            net_profit_ratio = EXCLUDED.net_profit_ratio,
            roe = EXCLUDED.roe,
            roa = EXCLUDED.roa,
            debt_dependency = EXCLUDED.debt_dependency,
            cash_flow_debt_ratio = EXCLUDED.cash_flow_debt_ratio,
            sales_growth = EXCLUDED.sales_growth,
            operating_profit_growth = EXCLUDED.operating_profit_growth,
            eps_growth = EXCLUDED.eps_growth
    """)
    await db_session.execute(query, ratios)
    await db_session.commit()

async def get_financial_statements(db_session: AsyncSession, corp_code: str, bsns_year: str) -> List[Dict[str, Any]]:
    """회사 코드와 사업연도로 재무제표 데이터를 조회합니다."""
    query = text("""
        SELECT 
            corp_code,
            corp_name,
            stock_code,
            rcept_no,
            reprt_code,
            bsns_year,
            sj_div,
            sj_nm,
            account_nm,
            thstrm_nm,
            thstrm_amount,
            frmtrm_nm,
            frmtrm_amount,
            bfefrmtrm_nm,
            bfefrmtrm_amount,
            ord,
            currency
        FROM fin_data
        WHERE corp_code = :corp_code
        AND bsns_year = :bsns_year
        ORDER BY sj_div, ord
    """)
    result = await db_session.execute(query, {"corp_code": corp_code, "bsns_year": bsns_year})
    rows = result.fetchall()
    return [dict(zip(result.keys(), row)) for row in rows]