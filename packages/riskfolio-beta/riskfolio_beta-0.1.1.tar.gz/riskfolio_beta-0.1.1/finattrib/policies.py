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

# -------- Portfolio 容器 --------
@dataclass(frozen=True)
class Portfolio:
    df: pd.DataFrame

    @staticmethod
    def from_df(df: pd.DataFrame) -> "Portfolio":
        # 这里可加字段校验/标准化（列名小写化、类型转换等）
        return Portfolio(df.copy())

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

    def compute_rwa(self, pf: Portfolio) -> Portfolio:
        df = pf.df.copy()
        df["EAD"] = self.ead_policy.compute_ead(df)
        df["risk_weight"] = self.rw_policy.compute_risk_weight(df)
        df["RWA"] = df["EAD"] * df["risk_weight"]
        return Portfolio.from_df(df)

    def allocate_tce(self, pf: Portfolio) -> Portfolio:
        df = pf.df.copy()
        total_rwa = df["RWA"].sum()
        total_equity = max(self.cap_policy.capital_ratio * total_rwa, self.cap_policy.equity_floor)
        df["TCE_alloc"] = 0.0 if total_rwa <= 0 else total_equity * (df["RWA"] / total_rwa)
        return Portfolio.from_df(df)

    def capital_charge(self, pf: Portfolio, cost_of_capital: float = 0.12) -> Portfolio:
        df = pf.df.copy()
        if "TCE_alloc" not in df.columns:
            raise ValueError("Run allocate_tce first")
        df["capital_charge"] = df["TCE_alloc"] * cost_of_capital
        df["Net_Income"] = df.get("PnL", 0.0) - df["capital_charge"]
        return Portfolio.from_df(df)

    def attribution_table(
        self, pf: Portfolio, dims: Tuple[str, ...] = ("desk",), metrics: Optional[Dict[str, Tuple[str, str]]] = None
    ) -> pd.DataFrame:
        df = pf.df
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
        gb["Return_on_TCE"] = np.where(gb["TCE_alloc"] != 0, gb["Net_Income"]/gb["TCE_alloc"], np.nan)
        gb["RWA_Return"]   = np.where(gb["RWA"] != 0, gb["Net_Income"]/gb["RWA"], np.nan)
        total_rwa = gb["RWA"].sum()
        gb["RWA_Share"]    = gb["RWA"]/total_rwa if total_rwa != 0 else np.nan
        return gb

    def gsib(self, pf: Portfolio) -> Dict[str, float]:
        return self.gsib_policy.score(pf.df)