import json
import os
from collections import defaultdict
from pathlib import Path

import click
import jpype
import jpype.imports

"""
Java Project Metrics Analyzer

This script analyzes Java source code files in a given directory and computes
various object-oriented metrics for each class or record. It uses JavaParser
via JPype to parse Java files and extract metrics such as:

- LOC (Lines of Code): Number of non-empty, non-comment lines in the class file.
- CBO (Coupling Between Objects): Number of distinct classes a class is coupled to via method calls.
- RFC (Response For a Class): Number of methods in the class plus number of methods called by the class.
- NOM (Number of Methods): Number of methods declared in the class.
- WMC (Weighted Methods per Class): Sum of cyclomatic complexities of all methods in the class.
- LCOM (Lack of Cohesion of Methods): Placeholder, currently 0 (requires advanced analysis).
- DIT (Depth of Inheritance Tree): Distance from the class to the root of the inheritance tree.
- NOC (Number of Children): Number of immediate subclasses.

Use case:
- To analyze code quality and design complexity of Java projects.
- To generate metrics per class and optionally aggregate metrics for the entire project.

| KPI (Abbreviation) | KPI Full Name               | Good         | Warning    | Bad    | Explanation                                      |
| ------------------ | --------------------------- | ------------ | ---------- | ------ | ------------------------------------------------ |
| LOC                | Lines of Code               | <= 100       | 101 - 300  | > 300  | Large classes are harder to maintain             |
| CBO                | Coupling Between Objects    | <= 5         | 6 - 10     | > 10   | High coupling reduces modularity                 |
| RFC                | Response For a Class        | <= 50        | 51 - 100   | > 100  | High response set indicates complexity           |
| NOM                | Number of Methods           | <= 10        | 11 - 20    | > 20   | Too many methods may be a sign of a God Class    |
| WMC                | Weighted Methods per Class  | <= 15        | 16 - 30    | > 30   | Measures complexity; higher is riskier           |
| LCOM               | Lack of Cohesion of Methods | <= 0.5 (low) | 0.5 - 0.75 | > 0.75 | Cohesion measure; higher means less cohesion     |
| DIT                | Depth of Inheritance Tree   | <= 3         | 4 - 6      | > 6    | Deep inheritance may increase complexity         |
| NOC                | Number of Children          | <= 5         | 6 - 10     | > 10   | Many children might mean too much responsibility |

Example usage:
    python java_analyzer.py ./my-java-project --output metrics.json --aggregate
"""

# Update these paths accordingly
CORE_JAR = Path("/Users/carl_neundorf/GIT/privat/lib/javaparser-core-3.25.9.jar")
SYMBOL_SOLVER_JAR = Path("/Users/carl_neundorf/GIT/privat/lib/javaparser-symbol-solver-core-3.25.9.jar")
GUAVA_JAR = Path("/Users/carl_neundorf/GIT/privat/lib/guava-31.1-jre.jar")


def convert_java_types(obj):
    """
    Recursively convert JPype Java types to native Python types.
    """
    java_string_class = jpype.JClass("java.lang.String")

    if isinstance(obj, dict):
        return {convert_java_types(k): convert_java_types(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [convert_java_types(item) for item in obj]
    elif isinstance(obj, set):
        return [convert_java_types(item) for item in obj]
    elif isinstance(obj, java_string_class):
        return str(obj)
    else:
        return obj


def aggregate_metrics(class_info):
    """
    Aggregate class-level metrics into project-level summary statistics.
    """
    agg = {
        "total_classes": len(class_info),
        "sum_LOC": 0, "avg_LOC": 0,
        "sum_CBO": 0, "avg_CBO": 0,
        "sum_RFC": 0, "avg_RFC": 0,
        "sum_NOM": 0, "avg_NOM": 0,
        "sum_WMC": 0, "avg_WMC": 0,
        "sum_LCOM": 0, "avg_LCOM": 0,
        "max_DIT": 0,
        "max_NOC": 0,
    }

    if agg["total_classes"] == 0:
        return agg

    for metrics in class_info.values():
        agg["sum_LOC"] += metrics["LOC"]
        agg["sum_CBO"] += metrics["CBO"]
        agg["sum_RFC"] += metrics["RFC"]
        agg["sum_NOM"] += metrics["NOM"]
        agg["sum_WMC"] += metrics["WMC"]
        agg["sum_LCOM"] += metrics["LCOM"]
        agg["max_DIT"] = max(agg["max_DIT"], metrics["DIT"])
        agg["max_NOC"] = max(agg["max_NOC"], metrics["NOC"])

    for key in ["LOC", "CBO", "RFC", "NOM", "WMC", "LCOM"]:
        agg[f"avg_{key}"] = agg[f"sum_{key}"] / agg["total_classes"]

    return agg


def calculate_LOC(code):
    """
    Calculate Lines of Code (LOC) excluding empty lines and comments.

    Args:
        code (str): Source code text.

    Returns:
        int: Number of non-empty, non-comment lines.
    """
    return len([line for line in code.splitlines() if line.strip() and not line.strip().startswith("//")])


def calculate_NOM(cid):
    """
    Calculate Number of Methods (NOM) declared in the class.

    Args:
        cid: JavaParser class or record declaration.

    Returns:
        int: Number of methods.
    """
    return cid.getMethods().size()


def calculate_WMC(cid):
    """
    Calculate Weighted Methods per Class (WMC) as sum of cyclomatic complexities.

    Cyclomatic complexity per method is 1 + count of control flow statements.

    Args:
        cid: JavaParser class or record declaration.

    Returns:
        int: Total WMC.
    """
    from com.github.javaparser.ast.stmt import ForStmt, IfStmt, SwitchStmt, WhileStmt

    wmc = 0
    for method in cid.getMethods():
        complexity = 1
        body = method.getBody().orElse(None)
        if body:
            complexity += body.findAll(IfStmt).size()
            complexity += body.findAll(ForStmt).size()
            complexity += body.findAll(WhileStmt).size()
            complexity += body.findAll(SwitchStmt).size()
        wmc += complexity
    return wmc


def calculate_RFC(cid):
    """
    Calculate Response For a Class (RFC) as number of methods plus number of method calls.

    Args:
        cid: JavaParser class or record declaration.

    Returns:
        int: RFC metric.
    """
    from com.github.javaparser.ast.expr import MethodCallExpr

    methods = cid.getMethods()
    rfc = methods.size()
    for method in methods:
        body = method.getBody().orElse(None)
        if body:
            calls = body.findAll(MethodCallExpr)
            rfc += calls.size()
    return rfc


def calculate_CBO(cid):
    """
    Calculate Coupling Between Objects (CBO) as number of distinct classes coupled via method calls.

    Args:
        cid: JavaParser class or record declaration.

    Returns:
        int: CBO metric.
    """
    from com.github.javaparser.ast.expr import MethodCallExpr

    called_classes = set()
    for method in cid.getMethods():
        body = method.getBody().orElse(None)
        if body:
            calls = body.findAll(MethodCallExpr)
            for call in calls:
                scope = call.getScope().orElse(None)
                if scope:
                    called_classes.add(str(scope.toString()))
    return len(called_classes)


def calculate_LCOM(cid):
    """
    Calculate Lack of Cohesion of Methods (LCOM) based on method pairs sharing fields.

    LCOM = max(P - Q, 0) where:
      P = number of method pairs that do NOT share any field
      Q = number of method pairs that share at least one field

    Args:
        cid: JavaParser class or record declaration.

    Returns:
        int: LCOM metric.
    """
    from com.github.javaparser.ast.expr import FieldAccessExpr, NameExpr

    fields = {f.getVariable(0).getNameAsString() for f in cid.getFields()}
    methods = cid.getMethods()
    if methods.size() < 2:
        return 0

    method_field_access = []

    for method in methods:
        accessed_fields = set()
        body = method.getBody().orElse(None)
        if body:
            field_accesses = list(body.findAll(FieldAccessExpr)) + list(body.findAll(NameExpr))
            for fa in field_accesses:
                name = fa.getNameAsString()
                if name in fields:
                    accessed_fields.add(name)
        method_field_access.append(accessed_fields)

    P = 0
    Q = 0
    n = len(method_field_access)
    for i in range(n):
        for j in range(i + 1, n):
            if method_field_access[i].intersection(method_field_access[j]):
                Q += 1
            else:
                P += 1

    return max(P - Q, 0)


def calculate_DIT(cls, inheritance_map):
    """
    Calculate Depth of Inheritance Tree (DIT) for a class.

    Args:
        cls (str): Class name.
        inheritance_map (dict): Map of class to its superclass.

    Returns:
        int: DIT value.
    """
    depth = 0
    while inheritance_map.get(cls):
        cls = inheritance_map[cls]
        depth += 1
    return depth


def calculate_NOC(cls, children_map):
    """
    Calculate Number of Children (NOC) for a class.

    Args:
        cls (str): Class name.
        children_map (dict): Map of class to list of immediate subclasses.

    Returns:
        int: NOC value.
    """
    return len(children_map[cls])


@click.command()
@click.argument("src_dir", type=click.Path(exists=True))
@click.option("--output", type=click.Path(), help="Optional JSON file to save the metrics.")
@click.option("--aggregate/--no-aggregate", default=False, help="Include aggregated project metrics.")
def analyze_java_metrics(src_dir, output, aggregate):
    """
    Analyze Java source files in a directory and compute object-oriented metrics.
    """
    if not jpype.isJVMStarted():
        jpype.startJVM(classpath=[str(CORE_JAR), str(SYMBOL_SOLVER_JAR), str(GUAVA_JAR)])

    from com.github.javaparser import ParserConfiguration, StaticJavaParser
    from com.github.javaparser.ast.body import RecordDeclaration
    from com.github.javaparser.ParserConfiguration import LanguageLevel
    from com.github.javaparser.symbolsolver import JavaSymbolSolver
    from com.github.javaparser.symbolsolver.resolution.typesolvers import (
        CombinedTypeSolver, JavaParserTypeSolver, ReflectionTypeSolver
    )
    from java.nio.file import Paths

    combined_solver = CombinedTypeSolver()
    combined_solver.add(ReflectionTypeSolver())
    combined_solver.add(JavaParserTypeSolver(Paths.get(src_dir)))

    symbol_solver = JavaSymbolSolver(combined_solver)
    config = ParserConfiguration()
    config.setLanguageLevel(LanguageLevel.JAVA_17)
    config.setSymbolResolver(symbol_solver)
    StaticJavaParser.setConfiguration(config)

    parser = StaticJavaParser
    class_info = {}
    inheritance_map = {}
    children_map = defaultdict(list)

    for dirpath, _, filenames in os.walk(src_dir):
        for filename in filenames:
            if filename.endswith(".java"):
                filepath = os.path.join(dirpath, filename)
                with open(filepath, "r", encoding="utf-8") as file:
                    code = file.read()
                    try:
                        cu = parser.parse(code)
                    except Exception as e:
                        print(f"Failed to parse {filename}: {e}")
                        continue

                    for type_decl in cu.getTypes():
                        if type_decl.isClassOrInterfaceDeclaration() and not type_decl.asClassOrInterfaceDeclaration().isInterface():
                            cid = type_decl.asClassOrInterfaceDeclaration()
                            name = str(cid.getNameAsString())
                            superclass = (
                                str(cid.getExtendedTypes()[0].getNameAsString())
                                if not cid.getExtendedTypes().isEmpty() else None
                            )
                        elif isinstance(type_decl, RecordDeclaration):
                            cid = type_decl
                            name = str(cid.getNameAsString())
                            superclass = "java.lang.Record"
                        else:
                            continue

                        if superclass:
                            inheritance_map[name] = superclass
                            children_map[superclass].append(name)

                        loc = calculate_LOC(code)
                        nom = calculate_NOM(cid)
                        wmc = calculate_WMC(cid)
                        rfc = calculate_RFC(cid)
                        cbo = calculate_CBO(cid)
                        lcom = calculate_LCOM(cid)

                        class_info[name] = {
                            "LOC": loc,
                            "CBO": cbo,
                            "RFC": rfc,
                            "NOM": nom,
                            "WMC": wmc,
                            "LCOM": lcom,
                            "Superclass": superclass,
                        }

    for cls in class_info:
        class_info[cls]["DIT"] = calculate_DIT(cls, inheritance_map)
        class_info[cls]["NOC"] = calculate_NOC(cls, children_map)

    output_data = {"classes": convert_java_types(class_info)}

    if aggregate:
        aggregated = aggregate_metrics(class_info)
        output_data["aggregated_metrics"] = convert_java_types(aggregated)

    if output:
        with open(output, "w", encoding="utf-8") as f:
            json.dump(output_data, f, indent=4)
        print(f"Metrics written to {output}")
    else:
        print(json.dumps(output_data, indent=4))

    jpype.shutdownJVM()
    return output_data


if __name__ == "__main__":
    analyze_java_metrics()
