# **Database Visualizer**

A Python script to visualize the relationships between tables in a database graphically.

**Author:** ElCaptaine

**Version:** 0.1

## Usage:

```bash
python database_visualizer.py --db_spec <spec> --path <optional> --layout <optional/choice>
```

## Description:

This script provides a graphical representation of how tables in a database are related. It fetches the relationship data from the specified database and creates a graph showing the connections between tables.

## Dependencies:

- `os`
- `typing`
- `click`
- `networkx`
- `matplotlib`
- `dev_helper.database_handler`

## Functions:

1. **clean_data(data: List[Tuple[str, ...]]) -> List[Tuple[str, str]]:**
   - Cleans the retrieved data and returns only the necessary fields: the name of the table and the name of the table using data from the previous tables as Foreign Keys.

2. **create_graph(sql_result: List) -> nx.Graph:**
   - Creates a directed graph from the SQL result.

3. **get_relations_of_db(db_spec: str) -> List:**
   - Fetches the relationships from the specified database.

4. **create_statement() -> str:**
   - Generates the SQL statement to retrieve relationships from the database.

5. **plot_graph(di_graph: nx.Graph, layout: str, path: str, show: bool):**
   - Plots the database graph using the specified layout and saves the plot as an image.

6. **main(db_spec: str, path: str, layout: str, show: bool):**
   - Main function to invoke the visualization process, encapsulating all necessary functions.

## Command-line Options:

- **--db_spec, -s:** Specify the database to visualize.
- **--path, -p:** Path to save the generated graph image (defaults to current directory if not provided).
- **--layout, -l:** Choose the layout for the graph (options: circular_layout, shell_layout, spiral_layout, spring_layout, spectral_layout, planar_layout, random_layout).
- **--show, -s:** Flag to show the generated graph plot.

## Example:

```bash
python database_visualizer.py --db_spec my_database --path /path/to/save/graph --layout shell_layout --show
```

## Note:

Ensure that the necessary dependencies are installed before running the script. Additionally, provide the appropriate database specifications to visualize the desired database.
