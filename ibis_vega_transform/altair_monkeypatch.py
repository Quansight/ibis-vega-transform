from ibis_vega_transform.globals import reset_debug
import warnings

import altair
import ibis
import pandas

__all__ = ["monkeypatch_altair"]


def monkeypatch_altair():
    """
    Needed until https://github.com/altair-viz/altair/issues/843 is fixed to let Altair
    handle ibis inputs
    """
    original_chart_init = altair.Chart.__init__
    original_chart_to_dict = altair.Chart.to_dict

    def updated_chart_init(self, data=None, *args, **kwargs):
        """
        If user passes in a Ibis expression, create an empty dataframe with
        those types and set the `ibis` attribute to the original ibis expression.
        """
        if data is not None and isinstance(data, ibis.Expr):
            reset_debug()
            expr = data
            data = empty_dataframe(expr)
            data.ibis = expr

        return original_chart_init(self, data=data, *args, **kwargs)

    def updated_chart_to_dict(self, *args, **kwargs):
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", UserWarning)
            spec = original_chart_to_dict(self, *args, **kwargs)
        return spec

    altair.Chart.__init__ = updated_chart_init
    altair.Chart.to_dict = updated_chart_to_dict


def empty_dataframe(expr: ibis.Expr) -> pandas.DataFrame:
    """
    Creates an empty DF for a ibis expression, based on the schema

    https://github.com/ibis-project/ibis/issues/1676#issuecomment-441472528
    """
    return expr.schema().apply_to(pandas.DataFrame(columns=expr.columns))
