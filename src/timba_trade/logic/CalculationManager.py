import numpy as np
import pandas as pd


class CalcManager:
    def __init__(self, data:pd.DataFrame):
        self.AE = 1
        self.data = data

    def _calc_price_share(self):
        df = self.data
        df["P_share_growth"] = df.P_share - df.P_share_lag + 1
        df["LD"] = df.P_q_o - df.X_q_o + df.M_q_o
        df["LD_lag"] = df.P_q_o_lag - df.X_q_o_lag + df.M_q_o_lag
        df["LD_growth"] = df.LD / df.LD_lag

        df.rename(
            columns={
                "Country":"Reporter"
            },
            inplace=True
        )

        self.results = df[[
            "Reporter", "Partner", "Commodity", "Period",
            "X_q_o", "M_q_o", "X_q_p", "M_q_p",
            "P_share_growth","LD_growth"
        ]]

    def clip_shares(self,cols:list,lb_fix:float=None,ub_fix:float=None):
        df = self.results
        for col in cols:
            df[col] = df[col].replace([np.inf, -np.inf, np.nan], 1)
            q1 = df[col].quantile(0.25)
            q3 = df[col].quantile(0.75)
            iqr = (q3 - q1)

            lb = lb_fix if lb_fix is not None else q1 - iqr * 5
            ub = ub_fix if ub_fix is not None else q3 + iqr * 5
                
            df[col] = df[col].clip(lower=lb, upper=ub)

    def _combined_effect(self):
        self.results["M_growth"] = self.results["LD_growth"] * self.results["P_share_growth"] ** (self.AE)
        
    def main(self)->pd.DataFrame:
        self._calc_price_share()
        self.clip_shares(cols=["P_share_growth"],lb_fix=0.5,ub_fix=2)
        self.clip_shares(cols=["LD_growth"])
        self._combined_effect()
        #self.clip_shares(cols=["M_growth"])
        return self.results
