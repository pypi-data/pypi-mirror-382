# core.py
from __future__ import annotations
import pandas as pd
import numpy as np
from dataclasses import dataclass
from typing import Tuple, Dict, Iterable, Optional

# -------- Policies (接口/默认实现) --------
class EADPolicy:
    def compute_ead(self, df: pd.DataFrame) -> pd.Series:
        """
        返回与 df 同索引的 EAD 序列。
        默认：若存在 EAD 列则直接返回；否则用简化口径：
          - repo: notional * (1 + haircut * 0.2)  (示例，按需替换)
          - bond: notional
        """
        if "EAD" in df.columns:
            return df["EAD"]
        is_repo = df["product"].str.contains("Repo", na=False)
        ead = pd.Series(index=df.index, dtype="float64")
        ead[is_repo] = df.loc[is_repo, "notional"] * (1 + df.loc[is_repo, "haircut_pct"].fillna(0)/100 * 0.2)
        ead[~is_repo] = df.loc[~is_repo, "notional"]
        return ead

class RiskWeightPolicy:
    def __init__(self, table: Dict[str, Dict[str, float]]):
        self.table = table

    def lookup(self, product: str, asset_rating: Optional[str]) -> float:
        mapping = self.table.get(product, {})
        if "ANY" in mapping:
            return mapping["ANY"]
        if asset_rating in mapping:
            return mapping[asset_rating]
        return 1.0  # fallback

    def compute_risk_weight(self, df: pd.DataFrame) -> pd.Series:
        return df.apply(lambda r: self.lookup(r["product"], r.get("asset_rating")), axis=1)

@dataclass(frozen=True)
class CapitalPolicy:
    capital_ratio: float = 0.12
    equity_floor: float = 5e8

class GsibPolicy:
    def score(self, df: pd.DataFrame) -> Dict[str, float]:
        size = df["EAD"].sum()
        size_score = 100 * (size / (size + 1e6))
        repo_share = (df["desk"] == "Repo").mean()
        unique_cp = max(df["cp_rating"].nunique(), 1)
        cp_disp = df.groupby("cp_rating")["notional"].sum().shape[0] / unique_cp
        interconnectedness = 100 * (0.7*repo_share + 0.3*cp_disp)
        structured = df["product"].isin(["NonAgency_MBS","HY_Bond"]).mean()
        long_mty = (df["maturity_days"] > 365*5).mean()
        complexity = 100 * (0.6*structured + 0.4*long_mty)
        cross_juris = 100 * (df["country"] != "US").mean()
        total = 0.4*size_score + 0.25*interconnectedness + 0.2*complexity + 0.15*cross_juris
        return {
            "size_score": float(size_score),
            "interconnectedness_score": float(interconnectedness),
            "complexity_score": float(complexity),
            "cross_jurisdiction_score": float(cross_juris),
            "G_SIB_total": float(total),
        }


# -------- Attribution Engine --------
class AttributionEngine:
    def __init__(
        self,
        ead_policy: Optional[EADPolicy] = None,
        rw_policy: Optional[RiskWeightPolicy] = None,
        cap_policy: Optional[CapitalPolicy] = None,
        gsib_policy: Optional[GsibPolicy] = None,
    ):
        self.ead_policy = ead_policy or EADPolicy()
        self.rw_policy = rw_policy or RiskWeightPolicy(table={})
        self.cap_policy = cap_policy or CapitalPolicy()
        self.gsib_policy = gsib_policy or GsibPolicy()

    def compute_rwa(df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()
        if not {"EAD","risk_weight"}.issubset(df.columns):
            raise ValueError("DataFrame must contain columns EAD and risk_weight")
        df["RWA"] = df["EAD"] * df["risk_weight"]
        return df

    def allocate_tce(df: pd.DataFrame, capital_ratio: float = 0.12, equity_floor: float = 5e8) -> pd.DataFrame:
        df = df.copy()
        total_rwa = df["RWA"].sum()
        total_equity = max(capital_ratio * total_rwa, equity_floor)
        if total_rwa <= 0:
            df["TCE_alloc"] = 0.0
            return df
        df["TCE_alloc"] = total_equity * (df["RWA"] / total_rwa)
        return df

    def compute_capital_charge(df: pd.DataFrame, cost_of_capital: float = 0.12) -> pd.DataFrame:
        df = df.copy()
        if "TCE_alloc" not in df.columns:
            raise ValueError("Run allocate_tce first")
        df["capital_charge"] = df["TCE_alloc"] * cost_of_capital
        df["Net_Income"] = df.get("PnL", 0.0) - df["capital_charge"]
        return df

    def attribution_table(df: pd.DataFrame, dims=("desk",), metrics=None) -> pd.DataFrame:
        if metrics is None:
            metrics = {
                "notional": ("notional","sum"),
                "EAD": ("EAD","sum"),
                "RWA": ("RWA","sum"),
                "PnL": ("PnL","sum"),
                "TCE_alloc": ("TCE_alloc","sum"),
                "Net_Income": ("Net_Income","sum"),
            }
        gb = df.groupby(list(dims)).agg(**metrics).reset_index()
        gb["Return_on_TCE"] = np.where(gb["TCE_alloc"]!=0, gb["Net_Income"]/gb["TCE_alloc"], np.nan)
        gb["RWA_Return"] = np.where(gb["RWA"]!=0, gb["Net_Income"]/gb["RWA"], np.nan)
        if gb["RWA"].sum() != 0:
            gb["RWA_Share"] = gb["RWA"] / gb["RWA"].sum()
        else:
            gb["RWA_Share"] = np.nan
        return gb

    def compute_gsib_toy(df: pd.DataFrame) -> dict:
        size = df["EAD"].sum()
        size_score = 100 * (size / (size + 1e6))
        repo_share = (df["desk"] == "Repo").mean()
        # dispersion proxy
        unique_cp = max(df["cp_rating"].nunique(), 1)
        cp_dispersion = df.groupby("cp_rating")["notional"].sum().shape[0] / unique_cp
        interconnectedness_score = 100 * (0.7*repo_share + 0.3*cp_dispersion)

        structured = df["product"].isin(["NonAgency_MBS","HY_Bond"]).mean()
        long_maturity = (df["maturity_days"] > 365*5).mean()
        complexity_score = 100 * (0.6*structured + 0.4*long_maturity)

        cross_juris = (df["country"] != "US").mean()
        cross_jurisdiction_score = 100 * cross_juris

        total = 0.4*size_score + 0.25*interconnectedness_score + 0.2*complexity_score + 0.15*cross_jurisdiction_score
        return {
            "size_score": float(size_score),
            "interconnectedness_score": float(interconnectedness_score),
            "complexity_score": float(complexity_score),
            "cross_jurisdiction_score": float(cross_jurisdiction_score),
            "G_SIB_total": float(total)
        }

# -------- Scenario（解耦情景与引擎） --------
@dataclass
class Scenario:
    weights: Dict[str, float]
    level: str = "product"
    col: str = "notional"

class ScenarioEngine:
    def apply(self, pf: Portfolio, scenario: Scenario) -> pd.DataFrame:
        df = df.copy()
        keys = set(df[scenario.level].unique())
        for k, v in scenario.weights.items():
            if k in keys:
                m = df[scenario.level] == k
                df.loc[m, scenario.col] = df.loc[m, scenario.col] * float(v)
                if "EAD" in df.columns:
                    df.loc[m, "EAD"] = df.loc[m, "EAD"] * float(v)
        return df