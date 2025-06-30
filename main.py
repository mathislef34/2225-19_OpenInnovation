import networkx as nx
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
import os

def get_vlan(ip):
    return ".".join(ip.split(".")[:3])

def get_infected_subnet(graph, infected_ips):
    infected_subnet = set()
    for ip in infected_ips:
        if ip in graph:
            infected_subnet.update(nx.node_connected_component(graph, ip))
    return infected_subnet

def draw_graph(G, vlan_colors, filename, title):
    pos = nx.spring_layout(G, seed=42)

    fig, ax = plt.subplots(figsize=(10, 8))

    std_edges = [(u, v) for u, v, d in G.edges(data=True) if d.get('type', 'standard') == 'standard']
    vpn_edges = [(u, v) for u, v, d in G.edges(data=True) if d.get('type') == 'VPN']

    node_colors = []
    for n in G.nodes():
        vlan = G.nodes[n].get("vlan") or get_vlan(n)
        node_colors.append(vlan_colors.get(vlan, "gray"))

    nx.draw(G, pos, edgelist=std_edges, node_color=node_colors, with_labels=True,
            node_size=700, edge_color='black', ax=ax)

    nx.draw(G, pos, edgelist=vpn_edges, node_color=node_colors, style='dashed',
            with_labels=False, edge_color='gray', ax=ax)

    legend = [Line2D([0], [0], color='black', lw=2, label='Standard'),
              Line2D([0], [0], color='gray', lw=2, linestyle='dashed', label='VPN')]
    
    for vlan, color in vlan_colors.items():
        legend.append(Line2D([0], [0], marker='o', color='w', markerfacecolor=color,
                             markersize=10, label=f'VLAN {vlan}'))

    ax.legend(handles=legend, loc='lower left')
    ax.set_title(title)
    plt.tight_layout()
    plt.savefig(filename)
    plt.close()

def process_network(data, output_dir):
    G = nx.Graph()
    vlan_colors = {}
    color_list = ['red', 'green', 'blue', 'orange', 'purple', 'cyan', 'magenta', 'brown']

    # Ajouter les machines si présentes
    if "machines" in data:
        for machine in data["machines"]:
            ip = machine.get("ip")
            vlan = machine.get("vlan", get_vlan(ip))
            if ip:
                G.add_node(ip, vlan=vlan)
                if vlan not in vlan_colors and color_list:
                    vlan_colors[vlan] = color_list.pop(0)

    # Ajouter les noeuds depuis les connexions si non définis
    for link in data.get("connections", []):
        src = link.get("Source") or link.get("source")
        tgt = link.get("Target") or link.get("target")
        if src and src not in G:
            vlan = get_vlan(src)
            G.add_node(src, vlan=vlan)
            if vlan not in vlan_colors and color_list:
                vlan_colors[vlan] = color_list.pop(0)
        if tgt and tgt not in G:
            vlan = get_vlan(tgt)
            G.add_node(tgt, vlan=vlan)
            if vlan not in vlan_colors and color_list:
                vlan_colors[vlan] = color_list.pop(0)

    # Ajouter les arêtes
    for link in data.get("connections", []):
        src = link.get("Source") or link.get("source")
        tgt = link.get("Target") or link.get("target")
        edge_type = link.get("Type") or link.get("type") or "standard"
        if src and tgt:
            G.add_edge(src, tgt, type=edge_type)

    # Image 1 : Architecture complète
    full_output = os.path.join(output_dir, "network_full.png")
    draw_graph(G, vlan_colors, full_output, "Architecture complète du réseau")

    # Image 2 : Propagation
    infected_ips = data.get("infected_ips") or data.get("infected") or []
    infected_subnet = get_infected_subnet(G, infected_ips)
    infected_graph = G.subgraph(infected_subnet).copy()

    infected_output = os.path.join(output_dir, "network_infected.png")
    draw_graph(infected_graph, vlan_colors, infected_output, "Propagation depuis les machines infectées")
