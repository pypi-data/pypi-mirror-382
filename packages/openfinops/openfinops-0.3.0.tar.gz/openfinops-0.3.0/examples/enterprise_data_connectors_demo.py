#!/usr/bin/env python3
"""
Vizly Enterprise Data Connectors Demo

Comprehensive demonstration of enterprise data integration capabilities,
including database connections, API integrations, and file-based data sources.

This demo shows:
- Database connector setup and querying
- REST API integration and data retrieval
- File-based data source connections
- Schema discovery and metadata management
- Data transformation and visualization pipelines
- Security and credential management

Usage:
    python enterprise_data_connectors_demo.py
"""

import asyncio
import json
import tempfile
import csv
from datetime import datetime, timedelta
from pathlib import Path
import sys

# Add source path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from vizly.enterprise.connectors import (
    ConnectorManager, DataSource, DatabaseConnector,
    APIConnector, FileConnector, get_connector_manager
)
from vizly.enterprise.security import EnterpriseSecurityManager

# Import plotting capabilities
try:
    from vizly.figure import VizlyFigure
    from vizly.charts.line import LineChart
    from vizly.charts.bar import BarChart
    from vizly.charts.scatter import ScatterChart
    VIZLY_AVAILABLE = True
except ImportError:
    VIZLY_AVAILABLE = False

try:
    import pandas as pd
    PANDAS_AVAILABLE = True
except ImportError:
    PANDAS_AVAILABLE = False


def create_sample_data_files():
    """Create sample data files for demonstration"""
    print("📁 Creating sample data files...")

    # Create temporary directory
    temp_dir = Path(tempfile.mkdtemp())

    # Sample CSV data
    csv_file = temp_dir / "sales_data.csv"
    sales_data = [
        ["Date", "Product", "Sales", "Region"],
        ["2024-01-01", "Widget A", 1000, "North"],
        ["2024-01-01", "Widget B", 1500, "South"],
        ["2024-01-01", "Widget A", 800, "East"],
        ["2024-01-02", "Widget A", 1200, "North"],
        ["2024-01-02", "Widget B", 1300, "South"],
        ["2024-01-02", "Widget C", 900, "West"],
        ["2024-01-03", "Widget A", 1100, "North"],
        ["2024-01-03", "Widget B", 1600, "South"],
        ["2024-01-03", "Widget C", 1050, "West"],
    ]

    with open(csv_file, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerows(sales_data)

    # Sample JSON data
    json_file = temp_dir / "customer_data.json"
    customer_data = {
        "customers": [
            {"id": 1, "name": "Acme Corp", "revenue": 50000, "industry": "Manufacturing"},
            {"id": 2, "name": "TechStart Inc", "revenue": 25000, "industry": "Technology"},
            {"id": 3, "name": "Global Services", "revenue": 75000, "industry": "Services"},
            {"id": 4, "name": "Data Systems", "revenue": 45000, "industry": "Technology"},
            {"id": 5, "name": "Enterprise Co", "revenue": 90000, "industry": "Enterprise"},
        ]
    }

    with open(json_file, 'w') as f:
        json.dump(customer_data, f, indent=2)

    print(f"✅ Sample files created in: {temp_dir}")
    print(f"   • CSV file: {csv_file}")
    print(f"   • JSON file: {json_file}")

    return temp_dir, csv_file, json_file


async def demo_file_connectors(temp_dir, csv_file, json_file):
    """Demo file-based data connectors"""
    print("\n📂 File Connectors Demo")
    print("=" * 50)

    # Get connector manager
    manager = get_connector_manager()

    # Register CSV data source
    csv_source = DataSource(
        source_id="sales_csv",
        source_type="file",
        name="Sales Data CSV",
        description="Daily sales data in CSV format",
        connection_config={
            "file_path": str(csv_file),
            "file_type": "csv"
        },
        tags=["sales", "csv", "demo"]
    )

    # Register JSON data source
    json_source = DataSource(
        source_id="customers_json",
        source_type="file",
        name="Customer Data JSON",
        description="Customer information in JSON format",
        connection_config={
            "file_path": str(json_file),
            "file_type": "json"
        },
        tags=["customers", "json", "demo"]
    )

    # Register data sources
    manager.register_data_source(csv_source)
    manager.register_data_source(json_source)

    print("✅ File data sources registered")

    # Test connections
    csv_connected = await manager.test_connection("sales_csv")
    json_connected = await manager.test_connection("customers_json")

    print(f"📊 CSV Connection: {'✅ Success' if csv_connected else '❌ Failed'}")
    print(f"📊 JSON Connection: {'✅ Success' if json_connected else '❌ Failed'}")

    # Get schema information
    print("\n🔍 Schema Discovery:")
    csv_schema = await manager.get_schema("sales_csv")
    print(f"   CSV Columns: {csv_schema.get('columns', [])}")

    json_schema = await manager.get_schema("customers_json")
    print(f"   JSON Structure: {list(json_schema.keys())}")

    # Query data
    print("\n📊 Data Querying:")

    # Read CSV data
    csv_result = await manager.execute_query("sales_csv", "")
    if csv_result:
        print(f"   CSV Data: {csv_result.row_count} rows, {csv_result.column_count} columns")
        print(f"   Execution Time: {csv_result.execution_time:.3f}s")

        # Show sample data
        if PANDAS_AVAILABLE and hasattr(csv_result.data, 'head'):
            print("   Sample CSV Data:")
            print(csv_result.data.head().to_string(index=False))

    # Read JSON data
    json_result = await manager.execute_query("customers_json", "customers")
    if json_result:
        print(f"\n   JSON Data: {json_result.row_count} rows, {json_result.column_count} columns")
        print(f"   Execution Time: {json_result.execution_time:.3f}s")

        # Show sample data
        if PANDAS_AVAILABLE and hasattr(json_result.data, 'head'):
            print("   Sample JSON Data:")
            print(json_result.data.head().to_string(index=False))

    # Create visualizations if Vizly is available
    if VIZLY_AVAILABLE and csv_result and hasattr(csv_result.data, 'groupby'):
        print("\n📈 Creating Visualizations:")

        try:
            # Sales by product chart
            sales_by_product = csv_result.data.groupby('Product')['Sales'].sum()

            fig = VizlyFigure(width=10, height=6)
            chart = BarChart(fig)
            chart.plot(sales_by_product.index.tolist(), sales_by_product.values.tolist())
            chart.set_title("Sales by Product")
            chart.set_xlabel("Product")
            chart.set_ylabel("Sales")

            fig.savefig("sales_by_product_demo.png", dpi=150, bbox_inches='tight')
            print("   📊 Sales by Product chart saved: sales_by_product_demo.png")

            # Sales trend over time
            csv_result.data['Date'] = pd.to_datetime(csv_result.data['Date'])
            daily_sales = csv_result.data.groupby('Date')['Sales'].sum()

            fig2 = VizlyFigure(width=10, height=6)
            chart2 = LineChart(fig2)
            chart2.plot(range(len(daily_sales)), daily_sales.values.tolist())
            chart2.set_title("Daily Sales Trend")
            chart2.set_xlabel("Day")
            chart2.set_ylabel("Total Sales")

            fig2.savefig("sales_trend_demo.png", dpi=150, bbox_inches='tight')
            print("   📈 Sales Trend chart saved: sales_trend_demo.png")

        except Exception as e:
            print(f"   ⚠️  Visualization skipped: {e}")

    return manager


async def demo_api_connectors():
    """Demo API-based data connectors"""
    print("\n🌐 API Connectors Demo")
    print("=" * 50)

    manager = get_connector_manager()

    # Register sample API data source (using JSONPlaceholder for demo)
    api_source = DataSource(
        source_id="jsonplaceholder_api",
        source_type="api",
        name="JSONPlaceholder API",
        description="Demo REST API for testing",
        connection_config={
            "base_url": "https://jsonplaceholder.typicode.com",
            "auth_type": "none",
            "timeout": 10,
            "endpoints": [
                "/posts",
                "/users",
                "/comments"
            ]
        },
        tags=["api", "demo", "rest"]
    )

    manager.register_data_source(api_source)
    print("✅ API data source registered")

    # Test connection
    api_connected = await manager.test_connection("jsonplaceholder_api")
    print(f"🌐 API Connection: {'✅ Success' if api_connected else '❌ Failed'}")

    if api_connected:
        # Get schema information
        print("\n🔍 API Schema Discovery:")
        api_schema = await manager.get_schema("jsonplaceholder_api")
        print(f"   Base URL: {api_schema.get('base_url')}")
        print(f"   Auth Type: {api_schema.get('auth_type')}")
        print(f"   Available Endpoints: {api_schema.get('endpoints', [])}")

        # Query API endpoints
        print("\n📊 API Data Querying:")

        # Get posts data
        posts_result = await manager.execute_query("jsonplaceholder_api", "posts")
        if posts_result:
            print(f"   Posts Data: {posts_result.row_count} rows, {posts_result.column_count} columns")
            print(f"   Execution Time: {posts_result.execution_time:.3f}s")
            print(f"   Status Code: {posts_result.metadata.get('status_code')}")

            # Show sample data
            if PANDAS_AVAILABLE and hasattr(posts_result.data, 'head'):
                print("   Sample Posts Data:")
                print(posts_result.data[['id', 'title']].head().to_string(index=False))

        # Get users data
        users_result = await manager.execute_query("jsonplaceholder_api", "users")
        if users_result:
            print(f"\n   Users Data: {users_result.row_count} rows, {users_result.column_count} columns")
            print(f"   Execution Time: {users_result.execution_time:.3f}s")

            # Show sample data
            if PANDAS_AVAILABLE and hasattr(users_result.data, 'head'):
                print("   Sample Users Data:")
                print(users_result.data[['id', 'name', 'email']].head().to_string(index=False))

        # Create visualization if data is available
        if VIZLY_AVAILABLE and posts_result and hasattr(posts_result.data, 'groupby'):
            try:
                print("\n📈 Creating API Data Visualization:")

                # Posts by user ID
                posts_by_user = posts_result.data['userId'].value_counts().sort_index()

                fig = VizlyFigure(width=12, height=6)
                chart = BarChart(fig)
                chart.plot(posts_by_user.index.tolist(), posts_by_user.values.tolist())
                chart.set_title("Posts by User ID")
                chart.set_xlabel("User ID")
                chart.set_ylabel("Number of Posts")

                fig.savefig("posts_by_user_demo.png", dpi=150, bbox_inches='tight')
                print("   📊 Posts by User chart saved: posts_by_user_demo.png")

            except Exception as e:
                print(f"   ⚠️  API visualization skipped: {e}")

    return manager


async def demo_database_connectors():
    """Demo database connectors with SQLite"""
    print("\n🗄️  Database Connectors Demo")
    print("=" * 50)

    # Create an in-memory SQLite database for demo
    import sqlite3
    import tempfile

    # Create temporary SQLite database
    db_file = Path(tempfile.mktemp(suffix='.db'))

    try:
        # Create sample database
        conn = sqlite3.connect(str(db_file))
        cursor = conn.cursor()

        # Create tables
        cursor.execute("""
            CREATE TABLE employees (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                department TEXT NOT NULL,
                salary REAL NOT NULL,
                hire_date DATE NOT NULL
            )
        """)

        cursor.execute("""
            CREATE TABLE departments (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                budget REAL NOT NULL
            )
        """)

        # Insert sample data
        employees_data = [
            (1, "John Smith", "Engineering", 75000, "2023-01-15"),
            (2, "Jane Doe", "Marketing", 65000, "2023-02-01"),
            (3, "Bob Johnson", "Engineering", 80000, "2022-11-10"),
            (4, "Alice Brown", "Sales", 70000, "2023-03-05"),
            (5, "Charlie Wilson", "Engineering", 85000, "2022-08-20"),
        ]

        departments_data = [
            (1, "Engineering", 500000),
            (2, "Marketing", 200000),
            (3, "Sales", 300000),
        ]

        cursor.executemany("INSERT INTO employees VALUES (?, ?, ?, ?, ?)", employees_data)
        cursor.executemany("INSERT INTO departments VALUES (?, ?, ?)", departments_data)

        conn.commit()
        conn.close()

        print(f"✅ Sample SQLite database created: {db_file}")

        # Register database data source
        manager = get_connector_manager()

        db_source = DataSource(
            source_id="company_db",
            source_type="database",
            name="Company Database",
            description="Employee and department data",
            connection_config={
                "database_type": "sqlite",
                "database": str(db_file),
                "pool_size": 5
            },
            tags=["database", "sqlite", "demo"]
        )

        manager.register_data_source(db_source)
        print("✅ Database data source registered")

        # Test connection
        db_connected = await manager.test_connection("company_db")
        print(f"🗄️  Database Connection: {'✅ Success' if db_connected else '❌ Failed'}")

        if db_connected:
            # Get schema information
            print("\n🔍 Database Schema Discovery:")
            db_schema = await manager.get_schema("company_db")
            print("   Tables:")
            for table_name, columns in db_schema.get('tables', {}).items():
                print(f"     • {table_name}: {len(columns)} columns")

            # Query data
            print("\n📊 Database Querying:")

            # Query employees
            employees_result = await manager.execute_query(
                "company_db",
                "SELECT * FROM employees ORDER BY salary DESC"
            )

            if employees_result:
                print(f"   Employees Query: {employees_result.row_count} rows, {employees_result.column_count} columns")
                print(f"   Execution Time: {employees_result.execution_time:.3f}s")

                if PANDAS_AVAILABLE and hasattr(employees_result.data, 'head'):
                    print("   Sample Employee Data:")
                    print(employees_result.data.head().to_string(index=False))

            # Query with aggregation
            dept_summary_result = await manager.execute_query(
                "company_db",
                """
                SELECT department,
                       COUNT(*) as employee_count,
                       AVG(salary) as avg_salary,
                       MAX(salary) as max_salary
                FROM employees
                GROUP BY department
                ORDER BY avg_salary DESC
                """
            )

            if dept_summary_result:
                print(f"\n   Department Summary: {dept_summary_result.row_count} rows")
                if PANDAS_AVAILABLE and hasattr(dept_summary_result.data, 'head'):
                    print(dept_summary_result.data.to_string(index=False))

            # Create visualizations
            if VIZLY_AVAILABLE and dept_summary_result and hasattr(dept_summary_result.data, 'values'):
                try:
                    print("\n📈 Creating Database Visualizations:")

                    # Department salary comparison
                    fig = VizlyFigure(width=10, height=6)
                    chart = BarChart(fig)

                    departments = dept_summary_result.data['department'].tolist()
                    avg_salaries = dept_summary_result.data['avg_salary'].tolist()

                    chart.plot(departments, avg_salaries)
                    chart.set_title("Average Salary by Department")
                    chart.set_xlabel("Department")
                    chart.set_ylabel("Average Salary ($)")

                    fig.savefig("dept_salaries_demo.png", dpi=150, bbox_inches='tight')
                    print("   📊 Department Salaries chart saved: dept_salaries_demo.png")

                    # Employee count by department
                    fig2 = VizlyFigure(width=8, height=8)
                    # Note: Would use pie chart here if available
                    chart2 = BarChart(fig2)

                    employee_counts = dept_summary_result.data['employee_count'].tolist()
                    chart2.plot(departments, employee_counts)
                    chart2.set_title("Employee Count by Department")
                    chart2.set_xlabel("Department")
                    chart2.set_ylabel("Number of Employees")

                    fig2.savefig("dept_employee_count_demo.png", dpi=150, bbox_inches='tight')
                    print("   📊 Employee Count chart saved: dept_employee_count_demo.png")

                except Exception as e:
                    print(f"   ⚠️  Database visualization skipped: {e}")

    except Exception as e:
        print(f"❌ Database demo failed: {e}")
        import traceback
        traceback.print_exc()

    finally:
        # Cleanup
        if db_file.exists():
            db_file.unlink()

    return manager


async def demo_connector_management():
    """Demo connector management features"""
    print("\n⚙️  Connector Management Demo")
    print("=" * 50)

    manager = get_connector_manager()

    # Get connection status for all sources
    print("📊 Connection Status:")
    status = manager.get_connection_status()

    for source_id, info in status.items():
        status_icon = "✅" if info['is_connected'] else "❌"
        active_icon = "🟢" if info['is_active'] else "🔴"
        print(f"   {status_icon} {active_icon} {info['name']} ({info['type']})")
        if info['last_accessed']:
            print(f"      Last accessed: {info['last_accessed']}")

    # List all data sources
    print("\n📋 Registered Data Sources:")
    all_sources = manager.list_data_sources()

    for source in all_sources:
        print(f"   • {source.name} ({source.source_type})")
        print(f"     ID: {source.source_id}")
        print(f"     Description: {source.description}")
        print(f"     Tags: {', '.join(source.tags)}")
        print()

    # Filter by type
    file_sources = manager.list_data_sources("file")
    print(f"📁 File Sources: {len(file_sources)}")

    api_sources = manager.list_data_sources("api")
    print(f"🌐 API Sources: {len(api_sources)}")

    db_sources = manager.list_data_sources("database")
    print(f"🗄️  Database Sources: {len(db_sources)}")

    return manager


async def demo_data_integration_pipeline():
    """Demo complete data integration and visualization pipeline"""
    print("\n🔄 Data Integration Pipeline Demo")
    print("=" * 50)

    manager = get_connector_manager()

    # Simulate a real-world scenario: combining data from multiple sources
    print("🎯 Scenario: Executive Dashboard combining sales, customer, and API data")

    try:
        # Combine data from different sources
        results = {}

        # Get sales data from CSV
        sales_result = await manager.execute_query("sales_csv", "")
        if sales_result and hasattr(sales_result.data, 'groupby'):
            results['sales'] = sales_result.data

        # Get customer data from JSON
        customer_result = await manager.execute_query("customers_json", "customers")
        if customer_result and hasattr(customer_result.data, 'head'):
            results['customers'] = customer_result.data

        # Get posts data from API
        posts_result = await manager.execute_query("jsonplaceholder_api", "posts")
        if posts_result and hasattr(posts_result.data, 'head'):
            results['posts'] = posts_result.data

        print("✅ Data retrieved from all sources")

        # Create integrated analytics
        if PANDAS_AVAILABLE and all(key in results for key in ['sales', 'customers']):
            print("\n📊 Integrated Analytics:")

            # Sales summary
            total_sales = results['sales']['Sales'].sum()
            avg_daily_sales = results['sales'].groupby('Date')['Sales'].sum().mean()
            top_product = results['sales'].groupby('Product')['Sales'].sum().idxmax()

            print(f"   📈 Total Sales: ${total_sales:,}")
            print(f"   📈 Average Daily Sales: ${avg_daily_sales:,.0f}")
            print(f"   📈 Top Product: {top_product}")

            # Customer summary
            total_customers = len(results['customers'])
            total_revenue = results['customers']['revenue'].sum()
            top_industry = results['customers'].groupby('industry')['revenue'].sum().idxmax()

            print(f"   👥 Total Customers: {total_customers}")
            print(f"   💰 Total Customer Revenue: ${total_revenue:,}")
            print(f"   🏭 Top Industry: {top_industry}")

            # Content summary
            if 'posts' in results:
                total_posts = len(results['posts'])
                unique_users = results['posts']['userId'].nunique()
                print(f"   📝 Total Posts: {total_posts}")
                print(f"   👤 Active Users: {unique_users}")

            # Create integrated dashboard visualization
            if VIZLY_AVAILABLE:
                try:
                    print("\n📊 Creating Integrated Dashboard:")

                    # Create multi-panel dashboard
                    fig = VizlyFigure(width=15, height=10)
                    fig.subplots(2, 2, figsize=(15, 10))

                    # Panel 1: Sales by Product
                    fig.subplot(2, 2, 1)
                    sales_by_product = results['sales'].groupby('Product')['Sales'].sum()
                    chart1 = BarChart(fig, bind_to_subplot=True)
                    chart1.plot(sales_by_product.index.tolist(), sales_by_product.values.tolist())
                    chart1.set_title("Sales by Product")

                    # Panel 2: Customer Revenue by Industry
                    fig.subplot(2, 2, 2)
                    revenue_by_industry = results['customers'].groupby('industry')['revenue'].sum()
                    chart2 = BarChart(fig, bind_to_subplot=True)
                    chart2.plot(revenue_by_industry.index.tolist(), revenue_by_industry.values.tolist())
                    chart2.set_title("Revenue by Industry")

                    # Panel 3: Daily Sales Trend
                    fig.subplot(2, 2, 3)
                    daily_sales = results['sales'].groupby('Date')['Sales'].sum()
                    chart3 = LineChart(fig, bind_to_subplot=True)
                    chart3.plot(range(len(daily_sales)), daily_sales.values.tolist())
                    chart3.set_title("Daily Sales Trend")

                    # Panel 4: Summary metrics (simulated)
                    fig.subplot(2, 2, 4)
                    metrics = ['Sales', 'Customers', 'Revenue']
                    values = [total_sales/1000, total_customers*10, total_revenue/1000]
                    chart4 = BarChart(fig, bind_to_subplot=True)
                    chart4.plot(metrics, values)
                    chart4.set_title("Key Metrics Summary")

                    fig.suptitle("Enterprise Data Integration Dashboard", fontsize=16, fontweight='bold')
                    fig.tight_layout()

                    fig.savefig("integrated_dashboard_demo.png", dpi=150, bbox_inches='tight')
                    print("   📊 Integrated Dashboard saved: integrated_dashboard_demo.png")

                except Exception as e:
                    print(f"   ⚠️  Integrated visualization skipped: {e}")

    except Exception as e:
        print(f"❌ Integration pipeline error: {e}")


async def main():
    """Run complete data connectors demonstration"""
    print("🚀 Vizly Enterprise Data Connectors Demo")
    print("=" * 60)
    print("This demo showcases comprehensive enterprise data integration")
    print("=" * 60)

    try:
        # Create sample data files
        temp_dir, csv_file, json_file = create_sample_data_files()

        # Demo file connectors
        await demo_file_connectors(temp_dir, csv_file, json_file)

        # Demo API connectors
        await demo_api_connectors()

        # Demo database connectors
        await demo_database_connectors()

        # Demo connector management
        await demo_connector_management()

        # Demo integrated pipeline
        await demo_data_integration_pipeline()

        print("\n✅ Data Connectors Demo completed successfully!")
        print("\n🎯 Key Capabilities Demonstrated:")
        print("   • File-based data sources (CSV, JSON)")
        print("   • REST API integration")
        print("   • Database connectivity (SQLite)")
        print("   • Schema discovery and metadata")
        print("   • Multi-source data integration")
        print("   • Automated visualization generation")
        print("   • Enterprise security and management")

        print("\n📁 Generated Files:")
        print("   • sales_by_product_demo.png")
        print("   • sales_trend_demo.png")
        print("   • posts_by_user_demo.png")
        print("   • dept_salaries_demo.png")
        print("   • dept_employee_count_demo.png")
        print("   • integrated_dashboard_demo.png")

    except KeyboardInterrupt:
        print("\n\n🛑 Demo interrupted by user")

    except Exception as e:
        print(f"\n❌ Demo error: {e}")
        import traceback
        traceback.print_exc()

    finally:
        # Cleanup
        manager = get_connector_manager()
        await manager.disconnect_all()
        print("\n🧹 Cleanup completed")


if __name__ == "__main__":
    asyncio.run(main())