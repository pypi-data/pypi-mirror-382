from .bmssp_solver import BmsspSolver
from .helpers.utils import input_check, reconstruct_path


def bmssp(
    graph: list[dict[int, int | float]],
    origin_id: int | set[int],
    destination_id: int = None,
):
    """
    Function:

    - A Full BMSSP-style shortest path solver.
    - Return a dictionary of various path information including:
        - `id_path`: A list of node ids in the order they are visited
        - `path`: A list of node dictionaries (lat + long) in the order they are visited

    Required Arguments:

    - `graph`:
        - Type: list of dictionaries
    - `origin_id`
        - Type: int | set of int
        - What: The id of the origin node from the graph dictionary to start the shortest path from
        - Note: If you pass a set, only the first id in the set will be checked for input validation
    - `destination_id`
        - Type: int | None
        - What: The id of the destination node from the graph dictionary to end the shortest path at
        - Note: If None, returns the distance matrix and predecessor list for the origin node
        - Note: If provided, returns the shortest path [origin_id, ..., destination_id] and its length

    Optional Arguments:

    - None

    Returns:

    - A dictionary with the following keys
        - `origin_id`: The id of the origin node or a list of ids if a set was provided
        - `destination_id`: The id of the destination node (or None)
        - `predecessor`: The predecessor list for path reconstruction
        - `distance_matrix`: The distance matrix from the origin node to all other nodes
        - `path`: The shortest path from origin_id to destination_id (or None)
        - `length`: The length of the shortest path from origin_id to destination_id (or None)
    """
    if isinstance(origin_id, set):
        if len(origin_id) < 1:
            raise ValueError(
                "Your provided origin_id set must have at least 1 node"
            )
        origin_id_check = next(iter(origin_id))
    else:
        origin_id_check = origin_id
    # Input Validation
    input_check(
        graph=graph, origin_id=origin_id_check, destination_id=destination_id
    )
    # Run the BMSSP Algorithm to relax as many edges as possible.
    solver = BmsspSolver(graph, origin_id)
    if destination_id is not None:
        if solver.distance_matrix[destination_id] == float("inf"):
            raise Exception(
                "Something went wrong, the origin and destination nodes are not connected."
            )

    return {
        "origin_id": (
            origin_id if isinstance(origin_id, int) else list(origin_id)
        ),
        "destination_id": destination_id,
        "predecessor": solver.predecessor,
        "distance_matrix": solver.distance_matrix,
        "path": (
            reconstruct_path(
                destination_id=destination_id, predecessor=solver.predecessor
            )
            if destination_id
            else None
        ),
        "length": (
            solver.distance_matrix[destination_id] if destination_id else None
        ),
    }
