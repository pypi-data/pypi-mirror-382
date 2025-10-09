from typing import Any, Callable, Optional

from flask import Blueprint, Flask, render_template
from markupsafe import Markup

from .chart import Chart, DataSet

__all__ = ("ChartJS", "Chart", "DataSet")

CSPNonceCallback = Callable[[], str]


class ChartJS:
    app: Optional[Flask]
    local_path: Optional[str] = None
    config: Optional[dict] = None
    __csp_nonce_callback: Optional[CSPNonceCallback] = None

    def __init__(self, app: Optional[Flask] = None) -> None:
        if app is not None:
            self.init_app(app)

    def __register_blueprint(self, app: Flask) -> None:
        blueprint = Blueprint(
            "chartjs",
            __name__,
            template_folder="templates",
            static_folder="static",
            static_url_path="/chartjs/static",
        )
        app.register_blueprint(blueprint)

    def init_app(self, app: Flask) -> None:
        if "chartjs" in app.extensions:
            raise RuntimeError("ChartJS extension is already registered on this Flask app.")

        app.extensions["chartjs"] = self
        self.__register_blueprint(app)
        self.local_path = app.config.get("CHARTJS_LOCAL_PATH", None)

        @app.context_processor
        def _() -> dict:
            return {"chartjs": self}

    def csp_nonce_callback(self, func: CSPNonceCallback) -> None:
        """Define a function that returns a nonce token for script safety

        >>> @csp_nonce_callback
        >>> def get_csp_nonce():
        >>>     ...
        >>>     return random_nonce
        """
        self.__csp_nonce_callback = func

    def load(self) -> Markup:
        return Markup(render_template("load_chartjs.jinja", local_path=self.local_path, csp_nonce_callback=self.__csp_nonce_callback))

    def render(
        self,
        chart: Chart,
        options: Optional[dict[str, Any]] = None,
        plugins: Optional[dict[str, Any]] = None,
        datasets: Optional[dict[str, Any]] = None,
        html_only: bool = False,
        js_only: bool = False,
    ) -> Markup:
        chart_data = chart.as_dict()

        if datasets:
            for key, val in datasets.items():
                chart_data["data"]["datasets"][key].update(val)

        if options:
            chart_data.update(options=options)
        if plugins:
            chart_data.update(plugins=plugins)

        html_str, js_str = "", ""
        if not js_only:
            html_str = render_template("html.jinja", chart=chart)

        if not html_only:
            js_str = render_template("js.jinja", chart=chart, chart_data=chart_data)

        return Markup("\n".join([html_str, js_str]))
