# LayData Python Client SDK

An async Python SDK for interacting with LayData — an API-first database platform similar to Airtable, but built for developer speed and flexibility.

## Installation

```bash
pip install laydata
```

## Quickstart

A minimal example showing the full high-level flow: connect, navigate the structure, work with records, and close the session.

```python
import asyncio
from laydata import Data

async def main():
    # 1. Connect to LayData
    data = Data(endpoint="http://127.0.0.1:8077")
    
    # 2. Navigate the structure (use PascalCase!)
    MyCompany = await data.space("MyCompany")
    SalesCRM = await MyCompany.base("SalesCRM")
    Customers = await SalesCRM.table("Customers")
    
    # 3. Work with records
    NewCustomer = await Customers.add({
        "CustomerName": "Alice",
        "Email": "alice@example.com",
        "IsActive": True
    })
    
    AllCustomers = await Customers.records(take=10)
    await Customers.delete_record(NewCustomer["id"])
    
    # 4. Close the connection
    await data.close()

asyncio.run(main())
```

**Tip:** Always use PascalCase for Space, Base, Table, and field names. It keeps your data model clean, predictable, and less error-prone.

## Core Concepts

LayData organizes your data in a simple hierarchy:

**Space → Base → Table → Record**

| Entity | Example | Description |
|--------|---------|-------------|
| Space | MyCompany | Top-level workspace (e.g. a company or project) |
| Base | SalesCRM | A database within a Space |
| Table | Customers | A table containing records |
| Record | Customer | A single row inside a table |

All operations are async and follow the same pattern: space → base → table → record

## Common Workflows

### Create and Update Records

**Create a new record:**
```python
Customer = await Customers.add({
    "CustomerName": "Alice",
    "Email": "alice@example.com"
})
```

**Find a record and edit it:**
```python
PlumberJob = await Jobs.get_by("JobName", "Plumber")
await PlumberJob.edit({"JobName": "Plumba"})
```

**Get a specific field value:**
```python
salary = PlumberJob.field("Salary")
print(salary)
```

### Query and Filter Data

**Simple filtering:**
```python
HighValueCustomers = await Customers.where("Value", ">=", 10000).all()
```

**Get the top record:**
```python
TopCustomer = await Customers.desc("Value").first()
```

**Find by field:**
```python
SpecificCustomer = await Customers.get_by("Email", "alice@example.com")
```

### Chained Queries

```python
TopElectronics = await (
    Products
    .contains("Category", "Electronics")
    .gte("Price", 200)
    .is_not_empty("Description")
    .desc("Price")
    .take(10)
    .all()
)
```

## Configuration

Create a `.env` file:

```env
LAYDATA_BASE_URL=http://127.0.0.1:8077
LAYDATA_ALLOW_ATTACHMENTS=1  # for local development only
```

Load it automatically:

```python
from dotenv import load_dotenv
load_dotenv()

data = Data()  # uses LAYDATA_BASE_URL from .env
```

## Requirements

- Python >= 3.10
- httpx – async HTTP client
- python-dotenv (optional)

## Advanced Usage

These features are powerful but not essential for getting started.

### Special Field Types

```python
from laydata import SingleSelect, MultiSelect, Date, Attachment
from datetime import datetime

Employee = await Employees.add({
    "Department": SingleSelect("Engineering"),
    "Skills": MultiSelect(["Python", "React"]),
    "HireDate": Date(datetime(2023, 1, 15)),
    "ProfilePhoto": Attachment("https://example.com/photo.jpg")
})
```

### Table Metadata Management

```python
Tasks = await ProjectBase.table("Tasks", icon="📋", description="Task tracking")
await Tasks.update_icon("✅")
await Tasks.update_description("Updated description")

AllTables = await ProjectBase.tables()
```

### Batch Operations & Error Handling

```python
BatchData = [{"Name": f"Item {i}", "Price": 10 + i} for i in range(10)]

for item in BatchData:
    try:
        await Items.add(item)
    except Exception as e:
        print(f"Failed: {e}")
```

## Best Practices

- Always use PascalCase for Space, Base, Table, and field names
- Treat records as objects — `record.edit()` and `record.field()` are the preferred ways to work with them
- Start with simple queries (`where().all()`, `get_by()`) and build up to more complex filters as needed
- Keep risky or infrequent operations (bulk deletes, `update_icon`) in dedicated functions or scripts

## Next Steps

- Explore Advanced Usage
- Use LayData as a backend for admin panels, CRMs, or internal tools
- Watch for new releases on GitHub