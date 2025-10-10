# SCGraph Utils
from scgraph.spanning import SpanningTree as SCSpanning
# Other Utilities
from pamda.pamda_timer import pamda_timer

# Local Imports and Utils
from bmsspy.solvers import bmssp
from .graphs import get_nx_shortest_path, get_igraph_shortest_path
from .vanilla_dijkstra import vanilla_dijkstra
from .sc_dijkstra import pure_python_sc_dijkstra, pure_python_heapdict_sc_dijkstra
from .bmssp_heap import bmssp_heap


def time_case(graph_name, case_name, origin, scgraph, nxgraph=None, igraph=None, test_vanilla_dijkstra:bool=False, print_console:bool=True, iterations:int=10):

    output = {
        'graph_name': graph_name,
        'case_name': case_name,
        'graph_nodes': len(scgraph),
        'graph_edges': sum(len(neighbors) for neighbors in scgraph),
        'iterations': iterations,
    }

    if print_console:
        print(f"\nTesting {case_name}...")

    # BMSSP Timing
    bmssp_spantree_time_stats = pamda_timer(bmssp, iterations = iterations).get_time_stats(graph=scgraph, origin_id=origin)
    if print_console:
        print(f"BMSSP time: {bmssp_spantree_time_stats['avg']:.2f} ms (stdev: {bmssp_spantree_time_stats['std']:.2f})")
    output['bmssp_spantree_time_ms'] = bmssp_spantree_time_stats['avg']
    output['bmssp_spantree_stdev'] = bmssp_spantree_time_stats['std']

    # BMSSP Heap Timing
    bmssp_heap_time_stats = pamda_timer(bmssp_heap, iterations = iterations).get_time_stats(graph=scgraph, node_id=origin)
    if print_console:
        print(f"BMSSP Heap time: {bmssp_heap_time_stats['avg']:.2f} ms (stdev: {bmssp_heap_time_stats['std']:.2f})")
    output['bmssp_heap_time_ms'] = bmssp_heap_time_stats['avg']
    output['bmssp_heap_stdev'] = bmssp_heap_time_stats['std']

    # Vanilla Dijkstra Timing
    if test_vanilla_dijkstra:
        if len(scgraph) > 80000:
            if print_console:
                print("Skipping Vanilla Dijkstra due to large graph size (> 80000 nodes).")
            output['vanilla_dijkstra_time_ms'] = float('nan')
            output['vanilla_dijkstra_stdev'] = float('nan')
        else:
            vanilla_dijkstra_time_stats = pamda_timer(vanilla_dijkstra, iterations = iterations).get_time_stats(graph=scgraph, origin_id=origin)
            if print_console:
                print(f"Vanilla Dijkstra time: {vanilla_dijkstra_time_stats['avg']:.2f} ms (stdev: {vanilla_dijkstra_time_stats['std']:.2f})")
            output['vanilla_dijkstra_time_ms'] = vanilla_dijkstra_time_stats['avg']
            output['vanilla_dijkstra_stdev'] = vanilla_dijkstra_time_stats['std']


    # SCGraph Dijkstra Timing
    sc_dijkstra_spantree_time_stats = pamda_timer(SCSpanning.makowskis_spanning_tree, iterations = iterations).get_time_stats(graph=scgraph, node_id=origin)
    if print_console:
        print(f"SCGraph Dijkstra Modified spantree Tree time: {sc_dijkstra_spantree_time_stats['avg']:.2f} ms (stdev: {sc_dijkstra_spantree_time_stats['std']:.2f})")
    output['sc_dijkstra_spantree_time_ms'] = sc_dijkstra_spantree_time_stats['avg']
    output['sc_dijkstra_spantree_stdev'] = sc_dijkstra_spantree_time_stats['std']

    # Pure Python SCGraph Dijkstra Timing to compare apples to apples with BMSSPy
    pure_python_sc_dijkstra_time_stats = pamda_timer(pure_python_sc_dijkstra, iterations = iterations).get_time_stats(graph=scgraph, node_id=origin)
    if print_console:
        print(f"Pure Python SCGraph Dijkstra time: {pure_python_sc_dijkstra_time_stats['avg']:.2f} ms (stdev: {pure_python_sc_dijkstra_time_stats['std']:.2f})")
    output['pure_python_sc_dijkstra_time_ms'] = pure_python_sc_dijkstra_time_stats['avg']
    output['pure_python_sc_dijkstra_stdev'] = pure_python_sc_dijkstra_time_stats['std']

    # Pure Python SCGraph Dijkstra with HeapDict Timing to compare apples to apples with BMSSPy
    pure_python_heapdict_sc_dijkstra_time_stats = pamda_timer(pure_python_heapdict_sc_dijkstra, iterations = iterations).get_time_stats(graph=scgraph, node_id=origin)
    if print_console:
        print(f"Pure Python SCGraph Dijkstra with HeapDict time: {pure_python_heapdict_sc_dijkstra_time_stats['avg']:.2f} ms (stdev: {pure_python_heapdict_sc_dijkstra_time_stats['std']:.2f})")
    output['pure_python_heapdict_sc_dijkstra_time_ms'] = pure_python_heapdict_sc_dijkstra_time_stats['avg']
    output['pure_python_heapdict_sc_dijkstra_stdev'] = pure_python_heapdict_sc_dijkstra_time_stats['std']

    # NetworkX Dijkstra Timing
    if nxgraph:
        nx_dijkstra_spantree_time_stats = pamda_timer(get_nx_shortest_path, iterations = iterations).get_time_stats(graph=nxgraph, origin=origin)
        if print_console:
            print(f"NetworkX Dijkstra time: {nx_dijkstra_spantree_time_stats['avg']:.2f} ms (stdev: {nx_dijkstra_spantree_time_stats['std']:.2f})")
        output['nx_dijkstra_spantree_time_ms'] = nx_dijkstra_spantree_time_stats['avg']
        output['nx_dijkstra_spantree_stdev'] = nx_dijkstra_spantree_time_stats['std']

    # iGraph Dijkstra Timing
    if igraph:
        if len(scgraph) > 80000:
            if print_console:
                print("Skipping iGraph due to large graph size (> 80000 nodes).")
            output['ig_spantree_time_ms'] = float('nan')
            output['ig_spantree_stdev'] = float('nan')
        else:
            try:

                ig_spantree_time_stats = pamda_timer(get_igraph_shortest_path, iterations = iterations).get_time_stats(graph=igraph, origin=origin)
                if print_console:
                    print(f"iGraph spantree time: {ig_spantree_time_stats['avg']:.2f} ms (stdev: {ig_spantree_time_stats['std']:.2f})")
            except Exception as e:
                ig_spantree_time_stats = {'avg': float('nan'), 'std': float('nan')}
                if print_console:
                    print(f"iGraph spantree time: {ig_spantree_time_stats['avg']:.2f} ms (stdev: {ig_spantree_time_stats['std']:.2f})")

            if print_console:
                print(f"Speed Ratio (BMSSP / SCGraph): {bmssp_spantree_time_stats['avg'] / sc_dijkstra_spantree_time_stats['avg']:.2f}")
            output['ig_spantree_time_ms'] = ig_spantree_time_stats['avg']
            output['ig_spantree_stdev'] = ig_spantree_time_stats['std']
    

    return output