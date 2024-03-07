import os as _os
from typing import List, Tuple
import click as _click
import networkx as _nx
import matplotlib.pyplot as _plt
import dev_helper.database_handler as _db_helper


"""
Database Visualizer

Small script to graphical show how the tables are realted.

Author: ElCaptaine
Version: 0.1

Usage:
    python database_visualizer --db_spec <spec> --path <optional> --layout <optional/choice>

"""


def clean_data(
    data: List[Tuple[str, ...]],
) -> List[Tuple[str, str]]:
    """
    This function hust filters the retrieved data, and returns only the needed two fields of the output:
    The name of the Table and the name of the Table which uses data of the previous tables as Foreignkeys.

    Args:
    - data (List[Tuple[str, ...]]): List of tuples which contains
                                    the tables which have a relationshio (and the direction);
                                    also the IDs and the Foreignkeys
    returns:
    - List[Tuple[[str, str]]]:      The data but without Primarykey and name of the Foreignkeys
    """
    return [(row[1], row[3]) for row in data]


def create_graph(
    sql_result: List,
) -> _nx.Graph:
    return _nx.DiGraph(sql_result)


def get_relations_of_db(
    db_spec: str,
) -> List:
    """
    Fetches the relationship out ouf the database

    args:
    - db_spec (str):    spec of the desired database

    returns:
        result (List):  SQL-Result/Relations of the tables
    """

    with _db_helper.DatabaseHandler(
        section=db_spec,
        use_context_manager=True,
    ) as session:
        result = session.execute_query(create_statement())

    return result


def create_statement():
    sql_statement = """
        SELECT
            conname AS constraint_name,
            conrelid::regclass AS table_or_view_name,
            a.attname AS column_name,
            confrelid::regclass AS referenced_table_name,
            af.attname AS referenced_column_name
        FROM
            pg_constraint AS c
            JOIN pg_attribute AS a ON a.attnum = ANY(c.conkey) AND a.attrelid = c.conrelid
            JOIN pg_attribute AS af ON af.attnum = ANY(c.confkey) AND af.attrelid = c.confrelid
        WHERE
            conrelid::regclass::text IN (SELECT table_name FROM information_schema.tables WHERE table_schema = 'public')
        ORDER BY
            conrelid, conkey;
    """
    return sql_statement


def plot_graph(
    di_graph: _nx.Graph,
    layout: str,
    path: str,
    show: bool,
):
    """
    Function creates a plot of the database graph, with a given layout.

    Args:
    - di_graph (_nx.Graph): Graph to be plot
    - layout (str):         Layout which should be used while drawing graph

    returns
    - None
    """
    layout_function = getattr(_nx, layout)
    pos = layout_function(di_graph)  # You can use different layout algorithms
    _nx.draw(
        di_graph,
        pos,
        with_labels=True,
        node_size=700,
        node_color="skyblue",
        font_size=10,
        font_color="black",
        font_weight="bold",
        arrows=True,
    )
    if show:
        _plt.show()
    path = f"{path}{_os.sep}graph.png"
    _plt.savefig(path, format="PNG")


@_click.command()
@_click.option(
    "--db_spec",
    "-s",
    help="Specify which database should be used",
)
@_click.option(
    "--path",
    "-p",
    default=_os.getcwd(),
    help="Path where the network file should be saved, if nothing is given, the current working directory is used",
)
@_click.option(
    "--layout",
    "-l",
    default="shell_layout",
    type=_click.Choice(
        [
            "circular_layout",
            "shell_layout",
            "spiral_layout",
            "spring_layout",
            "spectral_layout",
            "planar_layout",
            "random_layout",
        ]
    ),
    multiple=False,
    help="Chose the Layout for the Graph",
)
@_click.option(
    "--show",
    "-s",
    is_flag=True,
    help="Should the plot be also displayed at run time or only create a file; By default it wont show the plot"

)
def main(
    db_spec: str,
    path: str,
    layout: str,
    show: bool
):
    """
    Invokes the main process and encapsulate all functions, which are neccessary
    to create a visualization of the database and the structure.

    args:
    - db_spec (str): Spec name of the database which should be visualized
    - all_tables (bool): Boolean value to define if tables and views should
                         be visualized.
    returns:
    - None
    """
    result = clean_data(
        get_relations_of_db(
            db_spec=db_spec,
        ),
    )
    di_graph = create_graph(result)
    plot_graph(
        di_graph,
        layout,
        path,
        show,
    )


if __name__ == "__main__":
    main()
