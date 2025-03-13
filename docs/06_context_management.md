# Context Management in MCP

## The Problem
When building tools for LLMs, developers often face these challenges:
1. Users have no idea what's happening during long-running operations
2. No visual feedback during multi-step processes
3. Difficult to track progress of complex operations
4. Error messages are either too technical or not visible to users

Let's see this with a basic example:

```python
# Without Context - Black box experience
@mcp.tool()
def analyze_sales(country: str = None) -> str:
    conn = sqlite3.connect("online_retail.db")
    try:
        query = """SELECT COUNT(*), SUM(Quantity * UnitPrice) 
                  FROM online_retail WHERE Country = ?"""
        result = conn.execute(query, (country,)).fetchone()
        return f"Orders: {result[0]}, Revenue: ${result[1]:.2f}"
    except Exception as e:
        return f"Error: {str(e)}"
```

When using this tool:
- Users wait without knowing what's happening
- No indication of progress
- Can't tell if it's working or stuck
- Error messages are basic

## The Solution: Context
MCP's Context object provides real-time interaction between your tools and users:

```python
# With Context - Interactive experience
@mcp.tool()
async def analyze_sales(country: str = None, ctx: Context = None) -> str:
    if ctx:
        await ctx.info("Starting analysis...")
        await ctx.report_progress(0, 3)
    
    try:
        # Step 1: Count records
        if ctx:
            await ctx.info("📊 Counting records...")
            await ctx.report_progress(1, 3)
        
        # Step 2: Calculate revenue
        if ctx:
            await ctx.info("💰 Computing revenue...")
            await ctx.report_progress(2, 3)
            
        query = """SELECT COUNT(*), SUM(Quantity * UnitPrice) 
                  FROM online_retail WHERE Country = ?"""
        result = conn.execute(query, (country,)).fetchone()
        
        # Step 3: Format results
        if ctx:
            await ctx.info("✅ Analysis complete!")
            await ctx.report_progress(3, 3)
            
        return f"Orders: {result[0]}, Revenue: ${result[1]:.2f}"
        
    except Exception as e:
        if ctx:
            await ctx.error(f"❌ Analysis failed: {str(e)}")
        return f"Error: {str(e)}"
```

## Key Features

### 1. Progress Tracking
```python
await ctx.report_progress(current_step, total_steps)
```
- Shows progress bar in MCP Inspector
- Users can see how much is left
- Makes long operations feel faster

### 2. Status Updates
```python
await ctx.info("Processing step 2...")
```
- Real-time feedback
- Users know what's happening
- Reduces uncertainty

### 3. Error Handling
```python
await ctx.error("❌ Analysis failed")
```
- Clear error messages
- User-friendly notifications
- Better error context

## Real-World Example

Here's a complete example showing Context benefits:

```python
@mcp.tool()
async def analyze_sales(country: str = None, ctx: Context = None) -> str:
    """Analyze sales with user-friendly progress tracking"""
    try:
        # Step 1: Count records
        if ctx:
            await ctx.info("📊 Step 1/3: Counting records...")
            await ctx.report_progress(1, 3)
        
        total = conn.execute(
            "SELECT COUNT(*) FROM online_retail WHERE Country = ?", 
            (country,)
        ).fetchone()[0]
        
        # Step 2: Calculate metrics
        if ctx:
            await ctx.info("💰 Step 2/3: Computing metrics...")
            await ctx.report_progress(2, 3)
            
        result = conn.execute("""
            SELECT 
                COUNT(DISTINCT InvoiceNo) as Orders,
                SUM(Quantity * UnitPrice) as Revenue,
                AVG(Quantity * UnitPrice) as AvgOrder
            FROM online_retail 
            WHERE Country = ?
        """, (country,)).fetchone()
        
        # Step 3: Format report
        if ctx:
            await ctx.info("📝 Step 3/3: Preparing report...")
            await ctx.report_progress(3, 3)
        
        report = [
            f"Analysis for {country}",
            f"Total Records: {total:,}",
            f"Total Orders: {result[0]:,}",
            f"Total Revenue: ${result[1]:,.2f}",
            f"Average Order: ${result[2]:.2f}"
        ]
        
        if ctx:
            await ctx.info("✅ Analysis complete!")
            
        return "\n".join(report)
        
    except Exception as e:
        if ctx:
            await ctx.error(f"❌ Analysis failed: {str(e)}")
        return f"Error: {str(e)}"
```

## Before vs After

### Without Context:
- User runs tool
- Waits without feedback
- Gets result or error
- No progress indication
- No status updates

### With Context:
- User sees each step
- Progress bar shows completion
- Status messages provide updates
- Friendly error messages
- Clear completion indication

## Best Practices

1. **Make Context Optional**
```python
def your_tool(param: str, ctx: Context = None)
```

2. **Check Before Using**
```python
if ctx:
    await ctx.info("Message")
```

3. **Use Clear Step Names**
```python
await ctx.info("Step 1/3: Loading data...")
```

4. **Show Meaningful Progress**
```python
await ctx.report_progress(current, total)
```

## Conclusion

Context management transforms tools from black boxes into interactive, user-friendly experiences:
- Users know what's happening
- Progress is visible
- Errors are clear
- Long operations are more bearable

By implementing Context in your MCP tools, you create a better experience for both LLMs and users, making complex operations more transparent and user-friendly.
