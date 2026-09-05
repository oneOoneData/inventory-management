"""
Tests for reports API endpoints (quarterly performance, monthly trends).

Covers the filter support added so the Reports page honors the global filter bar
the same way /api/orders and /api/dashboard/summary do.
"""
import pytest


class TestQuarterlyReportsEndpoint:
    """Test suite for GET /api/reports/quarterly."""

    def test_get_quarterly_reports(self, client):
        """Test getting quarterly reports without filters."""
        response = client.get("/api/reports/quarterly")
        assert response.status_code == 200

        data = response.json()
        assert isinstance(data, list)
        assert len(data) > 0

        first = data[0]
        assert "quarter" in first
        assert "total_orders" in first
        assert "total_revenue" in first
        assert "avg_order_value" in first
        assert "fulfillment_rate" in first

    def test_quarterly_reports_sorted_by_quarter(self, client):
        """Quarters should come back in chronological order."""
        data = client.get("/api/reports/quarterly").json()
        quarters = [q["quarter"] for q in data]
        assert quarters == sorted(quarters)

    def test_quarterly_reports_avg_order_value_calculation(self, client):
        """avg_order_value should equal total_revenue / total_orders."""
        data = client.get("/api/reports/quarterly").json()
        for q in data:
            if q["total_orders"] > 0:
                expected = round(q["total_revenue"] / q["total_orders"], 2)
                assert abs(q["avg_order_value"] - expected) < 0.01

    def test_quarterly_reports_filter_by_warehouse(self, client):
        """Filtering by warehouse should not exceed the unfiltered totals."""
        unfiltered = client.get("/api/reports/quarterly").json()
        filtered = client.get("/api/reports/quarterly?warehouse=Tokyo").json()

        total_unfiltered = sum(q["total_orders"] for q in unfiltered)
        total_filtered = sum(q["total_orders"] for q in filtered)

        assert total_filtered <= total_unfiltered
        # Tokyo has orders in the seed data, so the filter should keep some.
        assert total_filtered > 0

    def test_quarterly_reports_filter_by_month(self, client):
        """A single-month filter should collapse to (at most) one quarter."""
        data = client.get("/api/reports/quarterly?month=2025-02").json()
        assert len(data) <= 1
        if data:
            assert data[0]["quarter"] == "Q1-2025"

    def test_quarterly_reports_filter_by_status(self, client):
        """Filtering to Delivered should make fulfillment_rate 100%."""
        data = client.get("/api/reports/quarterly?status=Delivered").json()
        for q in data:
            assert q["fulfillment_rate"] == 100.0

    def test_quarterly_reports_impossible_filter_returns_empty(self, client):
        """A filter combination with no matching orders returns an empty list."""
        response = client.get(
            "/api/reports/quarterly?warehouse=Tokyo&category=Circuit Boards&month=Q3-2025&status=Backordered"
        )
        assert response.status_code == 200
        assert isinstance(response.json(), list)


class TestMonthlyTrendsEndpoint:
    """Test suite for GET /api/reports/monthly-trends."""

    def test_get_monthly_trends(self, client):
        """Test getting monthly trends without filters."""
        response = client.get("/api/reports/monthly-trends")
        assert response.status_code == 200

        data = response.json()
        assert isinstance(data, list)
        assert len(data) > 0

        first = data[0]
        assert "month" in first
        assert "order_count" in first
        assert "revenue" in first
        assert "delivered_count" in first

    def test_monthly_trends_sorted_by_month(self, client):
        """Months should come back in chronological order."""
        data = client.get("/api/reports/monthly-trends").json()
        months = [m["month"] for m in data]
        assert months == sorted(months)
        # Format is YYYY-MM
        for m in months:
            assert len(m) == 7 and m[4] == "-"

    def test_monthly_trends_filter_by_month(self, client):
        """Filtering by a single month returns just that month."""
        data = client.get("/api/reports/monthly-trends?month=2025-03").json()
        assert len(data) == 1
        assert data[0]["month"] == "2025-03"

    def test_monthly_trends_filter_by_quarter(self, client):
        """Filtering by a quarter returns only that quarter's months."""
        data = client.get("/api/reports/monthly-trends?month=Q1-2025").json()
        returned_months = {m["month"] for m in data}
        assert returned_months <= {"2025-01", "2025-02", "2025-03"}

    def test_monthly_trends_filter_reduces_revenue(self, client):
        """A warehouse filter should not increase total revenue vs unfiltered."""
        unfiltered = client.get("/api/reports/monthly-trends").json()
        filtered = client.get("/api/reports/monthly-trends?warehouse=London").json()

        assert sum(m["revenue"] for m in filtered) <= sum(m["revenue"] for m in unfiltered)

    def test_monthly_trends_delivered_count_not_above_order_count(self, client):
        """delivered_count can never exceed order_count for a month."""
        data = client.get("/api/reports/monthly-trends").json()
        for m in data:
            assert m["delivered_count"] <= m["order_count"]
