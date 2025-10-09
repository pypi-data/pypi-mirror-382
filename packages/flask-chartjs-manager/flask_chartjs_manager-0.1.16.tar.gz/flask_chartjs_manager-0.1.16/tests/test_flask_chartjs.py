"""
Pytest test suite for flask-chartjs extension
"""

from flask import Flask, render_template_string

from flask_chartjs import Chart, ChartJS, DataSet


class TestChartJ:
    """Test suite for ChartJSManager class."""

    def test_manager_initialization(self, app, chartjs_manager):
        """Test that ChartJSManager initializes correctly."""
        assert chartjs_manager is not None
        assert "chartjs" in app.extensions

    def test_manager_init_app(self):
        """Test init_app method."""
        app = Flask(__name__)
        manager = ChartJS()
        manager.init_app(app)

        assert "chartjs" in app.extensions
        assert app.extensions["chartjs"] == manager

    def test_chartjs_context_processor(self, app, chartjs_manager):
        """Test that chartjs object is available in template context."""
        with app.app_context():
            template = "{{ chartjs }}"
            result = render_template_string(template)
            assert result  # Should not be empty

    def test_chartjs_load_method(self, app, chartjs_manager):
        """Test that chartjs.load() generates correct script tag."""
        with app.app_context():
            template = "{{ chartjs.load() }}"
            result = render_template_string(template)
            assert "<script" in result
            assert "chart.js" in result.lower() or "chartjs" in result.lower()

    def test_custom_chartjs_path(self, app):
        """Test custom CHARTJS_LOCAL_PATH configuration."""
        app.config["CHARTJS_LOCAL_PATH"] = "/custom/path/chart.js"

        manager = ChartJS()
        manager.init_app(app)

        with app.app_context():
            template = "{{ chartjs.load() }}"
            result = render_template_string(template)
            assert "/custom/path/chart.js" in result


class TestChart:
    """Test suite for Chart class."""

    def test_chart_creation(self):
        """Test basic chart creation."""
        chart = Chart("test-chart", "bar")
        assert chart.id == "test-chart"
        assert chart.type == "bar"

    def test_chart_types(self):
        """Test different chart types."""
        chart_types = ["bar", "line", "pie", "doughnut", "radar", "polarArea", "scatter"]

        for chart_type in chart_types:
            chart = Chart(f"{chart_type}-chart", chart_type)
            assert chart.type == chart_type

    def test_chart_data_labels(self):
        """Test adding labels to chart data."""
        chart = Chart("test-chart", "bar")
        chart.data.add_labels("Jan", "Feb", "Mar")

        assert len(chart.data.labels) == 3
        assert "Jan" in chart.data.labels
        assert "Feb" in chart.data.labels
        assert "Mar" in chart.data.labels

    def test_chart_add_dataset(self):
        """Test adding datasets to chart."""
        chart = Chart("test-chart", "bar")
        dataset = DataSet("Sales", [100, 200, 300])

        chart.data.add_dataset(dataset)
        assert len(chart.data.datasets) == 1
        assert chart.data.datasets[0] == dataset

    def test_chart_multiple_datasets(self):
        """Test adding multiple datasets."""
        chart = Chart("test-chart", "bar")

        dataset1 = DataSet("Income", [100, 200, 300])
        dataset2 = DataSet("Outcome", [50, 100, 150])

        chart.data.add_dataset(dataset1)
        chart.data.add_dataset(dataset2)

        assert len(chart.data.datasets) == 2
        assert chart.data.datasets[0].label == "Income"
        assert chart.data.datasets[1].label == "Outcome"


class TestDataSet:
    """Test suite for DataSet class."""

    def test_dataset_creation(self):
        """Test basic dataset creation."""
        dataset = DataSet("Sales", [100, 200, 300])
        assert dataset.label == "Sales"
        assert dataset.data == [100, 200, 300]

    def test_dataset_with_empty_data(self):
        """Test dataset with empty data."""
        dataset = DataSet("Empty", [])
        assert dataset.label == "Empty"
        assert dataset.data == []

    def test_dataset_with_options(self):
        """Test dataset with additional options."""
        dataset = DataSet("Sales", [100, 200, 300], background_color="rgba(255, 99, 132, 0.2)")

        assert dataset.label == "Sales"
        assert hasattr(dataset, "background_color")

    def test_dataset_data_types(self):
        """Test dataset with different data types."""
        # Integers
        dataset1 = DataSet("Int Data", [1, 2, 3])
        assert all(isinstance(x, int) for x in dataset1.data)

        # Floats
        dataset2 = DataSet("Float Data", [1.5, 2.5, 3.5])
        assert all(isinstance(x, float) for x in dataset2.data)

        # Mixed
        dataset3 = DataSet("Mixed Data", [1, 2.5, 3])
        assert len(dataset3.data) == 3


class TestChartRendering:
    """Test suite for chart rendering functionality."""

    def test_render_chart_basic(self, app, chartjs_manager):
        """Test basic chart rendering."""
        chart = Chart("test-chart", "bar")
        dataset = DataSet("Sales", [100, 200, 300])
        chart.data.add_labels("Jan", "Feb", "Mar")
        chart.data.add_dataset(dataset)

        with app.app_context():
            template = "{{ chartjs.render(chart) }}"
            result = render_template_string(template, chart=chart)

            assert "canvas" in result
            assert "test-chart" in result

    def test_render_chart_with_options(self, app, chartjs_manager):
        """Test chart rendering with custom options."""
        chart = Chart("test-chart", "line")
        dataset = DataSet("Data", [10, 20, 30])
        chart.data.add_labels("A", "B", "C")
        chart.data.add_dataset(dataset)

        with app.app_context():
            template = """
            {{ chartjs.render(chart, options={
                'scales': {
                    'y': {
                        'beginAtZero': true
                    }
                }
            }) }}
            """
            result = render_template_string(template, chart=chart)

            assert "canvas" in result
            assert "test-chart" in result

    def test_render_chart_with_dataset_options(self, app, chartjs_manager):
        """Test chart rendering with dataset-specific options."""
        chart = Chart("test-chart", "bar")
        dataset1 = DataSet("Income", [100, 200, 300])
        dataset2 = DataSet("Outcome", [50, 100, 150])

        chart.data.add_labels("Jan", "Feb", "Mar")
        chart.data.add_dataset(dataset1)
        chart.data.add_dataset(dataset2)

        with app.app_context():
            template = """
            {{ chartjs.render(chart, datasets={
                0: {'borderColor': 'rgba(20, 184, 166, 0.8)'},
                1: {'borderColor': 'rgba(239, 68, 68, 0.8)'}
            }) }}
            """
            result = render_template_string(template, chart=chart)

            assert "canvas" in result
            assert "test-chart" in result


class TestIntegration:
    """Integration tests for complete workflows."""

    def test_full_chart_workflow(self, app, chartjs_manager):
        """Test a complete chart creation and rendering workflow."""

        @app.route("/chart")
        def chart_view():
            chart = Chart("income-outcome", "bar")

            dataset_income = DataSet("Income", [100, 200, 300])
            dataset_outcome = DataSet("Outcome", [50, 100, 150])

            chart.data.add_labels("Jan", "Feb", "Mar")
            chart.data.add_dataset(dataset_income)
            chart.data.add_dataset(dataset_outcome)

            template = """
            <!DOCTYPE html>
            <html>
            <head>
                {{ chartjs.load() }}
            </head>
            <body>
                <div>{{ chartjs.render(chart) }}</div>
            </body>
            </html>
            """
            return render_template_string(template, chart=chart)

        client = app.test_client()
        response = client.get("/chart")

        assert response.status_code == 200
        assert b"income-outcome" in response.data
        assert b"canvas" in response.data
        assert b"chart.js" in response.data.lower() or b"chartjs" in response.data.lower()

    def test_multiple_charts_on_page(self, app, chartjs_manager):
        """Test rendering multiple charts on the same page."""

        @app.route("/multiple-charts")
        def multiple_charts_view():
            chart1 = Chart("chart-1", "bar")
            chart1.data.add_labels("A", "B")
            chart1.data.add_dataset(DataSet("Data1", [10, 20]))

            chart2 = Chart("chart-2", "line")
            chart2.data.add_labels("X", "Y")
            chart2.data.add_dataset(DataSet("Data2", [30, 40]))

            template = """
            <!DOCTYPE html>
            <html>
            <head>
                {{ chartjs.load() }}
            </head>
            <body>
                <div>{{ chartjs.render(chart1) }}</div>
                <div>{{ chartjs.render(chart2) }}</div>
            </body>
            </html>
            """
            return render_template_string(template, chart1=chart1, chart2=chart2)

        client = app.test_client()
        response = client.get("/multiple-charts")

        assert response.status_code == 200
        assert b"chart-1" in response.data
        assert b"chart-2" in response.data


class TestEdgeCases:
    """Test edge cases and error handling."""

    def test_chart_with_no_data(self):
        """Test chart creation with no data."""
        chart = Chart("empty-chart", "bar")
        assert chart.id == "empty-chart"
        assert chart.type == "bar"

    def test_dataset_with_mismatched_labels_data(self):
        """Test dataset when labels and data counts don't match."""
        chart = Chart("test-chart", "bar")
        chart.data.add_labels("Jan", "Feb", "Mar")
        dataset = DataSet("Sales", [100, 200])  # Only 2 values for 3 labels
        chart.data.add_dataset(dataset)

        assert len(chart.data.labels) == 3
        assert len(dataset.data) == 2

    def test_javascript_callback_reference(self, app, chartjs_manager):
        """Test using JavaScript callback with % prefix."""
        chart = Chart("test-chart", "bar")
        dataset = DataSet("Sales", [100, 200, 300])
        chart.data.add_labels("Jan", "Feb", "Mar")
        chart.data.add_dataset(dataset)

        with app.app_context():
            template = """
            <script>
            function myCallback(value) {
                return "$" + value;
            }
            </script>
            {{ chartjs.render(chart, options={
                'scales': {
                    'y': {
                        'ticks': {
                            'callback': '%myCallback'
                        }
                    }
                }
            }) }}
            """
            result = render_template_string(template, chart=chart)

            # Should contain the callback reference
            assert "myCallback" in result or "%myCallback" in result
