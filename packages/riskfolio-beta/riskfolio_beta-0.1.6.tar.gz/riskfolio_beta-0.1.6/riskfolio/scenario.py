# -------- Scenario（解耦情景与引擎） --------
@dataclass
class Scenario:
    weights: Dict[str, float]
    level: str = "product"
    col: str = "notional"

class ScenarioEngine:
    def apply(self, pf: Portfolio, scenario: Scenario) -> Portfolio:
        df = pf.df.copy()
        keys = set(df[scenario.level].unique())
        for k, v in scenario.weights.items():
            if k in keys:
                m = df[scenario.level] == k
                df.loc[m, scenario.col] = df.loc[m, scenario.col] * float(v)
                if "EAD" in df.columns:
                    df.loc[m, "EAD"] = df.loc[m, "EAD"] * float(v)
        return Portfolio.from_df(df)