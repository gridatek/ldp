# Hive vs Iceberg:

## What They Are

**Apache Hive:**
- Traditional data warehouse system built on Hadoop
- Provides SQL-like interface (HiveQL) to query data stored in HDFS/S3
- Uses Hive Metastore to track table schemas and partitions
- Data format: typically stored as files (Parquet, ORC, etc.) organized by partitions

**Apache Iceberg:**
- Modern **table format** (not a query engine)
- Designed to solve limitations of traditional Hive tables
- Works **with** existing engines (Spark, Trino, Flink, Hive)
- Manages metadata at the table level, not just in a metastore

## Key Differences

### 1. Schema Evolution
**Hive:**
- Schema changes are risky and can break queries
- Adding/renaming columns can cause issues with old data

**Iceberg:**
- Full schema evolution support
- Track schema changes with IDs
- Safe column additions, renames, and type changes
- Old queries still work after schema changes

### 2. Partitioning
**Hive:**
- Manual partition management (`ALTER TABLE ADD PARTITION`)
- Users must specify partitions in queries for performance
- Partition columns are physical directories (e.g., `year=2024/month=12/`)

**Iceberg:**
- **Hidden partitioning** - users don't need to know partition scheme
- Automatic partition pruning
- Can change partition scheme without rewriting data
- Supports partition evolution

**Example:**
```sql
-- Hive: User must know partition structure
SELECT * FROM sales WHERE year=2024 AND month=12;

-- Iceberg: Just query normally
SELECT * FROM sales WHERE date = '2024-12-20';
-- Iceberg automatically prunes partitions
```

### 3. ACID Transactions
**Hive:**
- Limited ACID support (requires ORC format and specific configs)
- Complex setup, not widely used
- Struggles with concurrent writes

**Iceberg:**
- Full ACID transactions from day one
- Serializable isolation
- Optimistic concurrency control
- Multiple writers can safely update the table

### 4. Time Travel & Versioning
**Hive:**
- No built-in time travel
- Cannot easily query historical data
- Rollbacks are manual and error-prone

**Iceberg:**
- Built-in **time travel** - query data as it was at any point
- Every write creates a new snapshot
- Easy rollback to previous versions

```sql
-- Iceberg time travel examples
SELECT * FROM sales TIMESTAMP AS OF '2024-12-19 10:00:00';
SELECT * FROM sales VERSION AS OF 12345;

-- Rollback to previous snapshot
CALL catalog.system.rollback_to_snapshot('sales', 12345);
```

### 5. Data Files & Metadata
**Hive:**
- Metastore tracks table location and schema
- Must scan directories to discover files (slow for large tables)
- `MSCK REPAIR TABLE` needed after external file additions

**Iceberg:**
- Tracks **every data file** in metadata
- Knows exactly which files contain which data
- Fast query planning - no directory listing needed
- Automatic file tracking

### 6. Performance Features
**Hive:**
- Basic file pruning based on partitions
- No built-in file compaction

**Iceberg:**
- Advanced data/metadata filtering
- Min/max statistics per file
- Bloom filters for fast lookups
- Built-in file compaction
- Hidden partitioning improves query performance

### 7. Delete & Update Operations
**Hive:**
- INSERT only (traditionally)
- DELETE/UPDATE require ACID tables (complex setup)
- Performance issues with updates

**Iceberg:**
- Efficient DELETE and UPDATE operations
- Row-level deletes using delete files
- Merge-on-read or copy-on-write strategies

## When to Use Each

### Use Hive When:
- You have existing Hive infrastructure
- Simple batch ETL workloads
- Append-only data (no updates/deletes)
- Legacy systems that depend on Hive

### Use Iceberg When:
- Building new data lakes
- Need ACID transactions
- Frequent schema changes
- Need updates/deletes (CDC use cases)
- Want time travel capabilities
- Multiple engines querying same data (Spark, Trino, Flink)
- Modern data lakehouse architecture

## Can They Work Together?

**Yes!** Common patterns:
1. **Iceberg can use Hive Metastore** for catalog management
2. **Migration path**: Gradually migrate Hive tables to Iceberg format
3. **Hybrid approach**: Keep legacy Hive tables, new tables use Iceberg

## Your Setup

In your project, you're using:
- **Iceberg** as the table format (config/iceberg/catalog.properties:3)
- **HadoopCatalog** for metadata (not Hive Metastore)
- This gives you modern Iceberg features without Hive dependency

## Summary

| Feature | Hive | Iceberg |
|---------|------|---------|
| Type | Data warehouse system | Table format |
| Schema Evolution | Limited | Full support |
| Partitioning | Manual, visible | Hidden, automatic |
| ACID | Limited | Full |
| Time Travel | No | Yes |
| Updates/Deletes | Complex | Native |
| Performance | Good | Better |
| Modern Features | Basic | Advanced |

**Bottom line:** Iceberg is the modern evolution designed to fix Hive's limitations while maintaining compatibility with existing data lake tools.
