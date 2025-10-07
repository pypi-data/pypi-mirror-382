import networkx as nx
import matplotlib.pyplot as plt
from pathlib import Path
import sys
import heapq

#Hàm tìm đường đi ngắn nhất
def find_shortest_path(adj_list, start_node, goal_node):
    """
    Tìm đường đi ngắn nhất (ít cạnh nhất) từ nút bắt đầu đến nút kết thúc
    sử dụng thuật toán Duyệt theo Chiều Rộng (Breadth-First Search - BFS).
    Args:
        adj_list (dict): Danh sách kề của đồ thị
        start_node: Tên của nút bắt đầu.
        goal_node: Tên của nút đích.

    Returns:
        tuple: Tuple (Đường đi ngắn nhất).
               Trả về [] nếu không tìm thấy đường đi hoặc nút không hợp lệ.
    """
    # 1. Kiểm tra và Khởi tạo
    if start_node not in adj_list or goal_node not in adj_list:
        if start_node == goal_node:
            return [start_node]
        return []
    from collections import deque
    
    queue = deque([start_node])
    visited = {start_node}
    # came_from: Lưu trữ nút tiền nhiệm (predecessor)
    came_from = {node: None for node in adj_list}

    # 2. Vòng lặp BFS
    while queue:
        current_node = queue.popleft()

        if current_node == goal_node:
            break

        for neighbor in adj_list.get(current_node, []):
            if neighbor not in visited:
                came_from[neighbor] = current_node
                visited.add(neighbor)
                queue.append(neighbor)
    
    # 3. Tái tạo đường đi
    # Nếu nút đích không có nút tiền nhiệm, nghĩa là không thể đến được (trừ khi start=goal)
    if came_from.get(goal_node) is None and start_node != goal_node:
        return []
    
    path = []
    current = goal_node
    
    while current is not None:
        path.append(current)
        current = came_from.get(current)
    
    path.reverse()
    
    return path

#Hàm chuyển path thành edges
def path_to_edges(path):
    """
    Chuyển đổi danh sách các đỉnh của một đường đi thành danh sách các cạnh có hướng.

    Hàm tạo ra các cặp (u, v) liên tiếp từ danh sách các nút,
    biểu diễn thứ tự các cạnh trong đường đi.

    Args:
        path (list): Danh sách các nút theo thứ tự của đường đi.

    Returns:
        list of tuple: Danh sách các cặp tuple (nút nguồn, nút đích) biểu diễn 
                       các cạnh của đường đi.
    """
    edges = []
    
    # Lặp qua danh sách từ nút đầu tiên đến nút kế cuối.
    # Mỗi lần lặp tạo ra một cạnh nối nút hiện tại với nút kế tiếp.
    for i in range(len(path) - 1):
        source_node = path[i]
        target_node = path[i + 1]
        
        edges.append((source_node, target_node))
        
    return edges

def dijkstra_shortest_path(adj_list_weighted, start_node, goal_node):
    """
    Tìm đường đi ngắn nhất giữa hai nút trong đồ thị vô hướng có trọng số bằng thuật toán Dijkstra.
    
    Hàm xử lý các trường hợp đặc biệt (nút không tồn tại, nút bắt đầu và kết thúc trùng nhau) 
    và trả về chi phí tối đa (sys.maxsize) nếu không tìm thấy đường đi.
    
    Args:
        adj_list_weighted (Dict[str, List[Tuple[str, Any]]]): Danh sách kề có trọng số 
            của đồ thị, được tạo bởi hàm `create_adj_list_w`. Format: {u: [(v, wt), ...], ...}.
        start_node (str): Nút bắt đầu của đường đi.
        goal_node (str): Nút đích của đường đi.
        
    Returns:
        Tuple[List[str], Any]: Một tuple chứa hai phần tử:
            - Đường đi ngắn nhất (List[str]): Danh sách các nút theo thứ tự từ start_node đến goal_node.
                                            (Trả về List rỗng [] nếu không tìm thấy đường đi hoặc nút không hợp lệ).
            - Chi phí ngắn nhất (Any): Tổng trọng số của đường đi. 
                                     (Trả về sys.maxsize nếu không tìm thấy đường đi, hoặc 0 cho các trường hợp đặc biệt).
    """
    # 1. Khởi tạo và Kiểm tra

    # KIỂM TRA 1: Nếu start_node hoặc goal_node KHÔNG tồn tại trong đồ thị
    # (Tức là không có trong danh sách kề)
    if start_node not in adj_list_weighted or goal_node not in adj_list_weighted:
        # Trả về [ ], 0 (Theo yêu cầu mới của bạn cho trường hợp nút không hợp lệ)
        return [], 0 
    
    # KIỂM TRA 2: Nếu nút bắt đầu trùng với nút kết thúc (và đã được xác nhận là tồn tại ở bước trên)
    if start_node == goal_node:
        # Trả về [ ], 0 (Theo yêu cầu mới của bạn, ngay cả khi nút hợp lệ)
        return [], 0
    
    # ... (Các bước khởi tạo dist, came_from, pq giữ nguyên) ...
    # dist: Lưu trữ khoảng cách ngắn nhất hiện tại từ start_node
    # Khởi tạo tất cả bằng vô cực (sys.maxsize)
    dist = {node: sys.maxsize for node in adj_list_weighted}
    dist[start_node] = 0
    
    # came_from: Lưu trữ nút tiền nhiệm (predecessor) để tái tạo đường đi
    came_from = {node: None for node in adj_list_weighted}
    
    # priority_queue (pq): Format: [khoảng cách, nút]
    pq = [[0, start_node]]

    # 2. Vòng lặp Dijkstra (Giữ nguyên)
    while pq:
        # Lấy nút có khoảng cách ngắn nhất hiện tại
        current_distance, current_node = heapq.heappop(pq)

        # Optimization: Nếu khoảng cách hiện tại lớn hơn khoảng cách ngắn nhất đã biết
        if current_distance > dist[current_node]:
            continue

        # Dừng sớm nếu đã đến nút đích
        # (Không cần break ở đây vì đã kiểm tra start_node == goal_node ở trên)

        # Thư giãn các cạnh
        for neighbor, weight in adj_list_weighted.get(current_node, []):
            distance = current_distance + weight
            
            # Bước Thư giãn (Relaxation)
            if distance < dist[neighbor]:
                dist[neighbor] = distance
                came_from[neighbor] = current_node
                heapq.heappush(pq, [distance, neighbor])

    # 3. Tái tạo đường đi và Chi phí
    final_cost = dist[goal_node]
    
    # Nếu chi phí vẫn là maxsize, không có đường đi (trong trường hợp start != goal)
    if final_cost == sys.maxsize:
        return [], sys.maxsize # Trả về sys.maxsize khi không tìm thấy đường đi (phù hợp hơn 0)

    # Tái tạo đường đi bằng cách truy ngược từ nút đích
    path = []
    current = goal_node
    while current is not None:
        path.append(current)
        current = came_from.get(current)

    path.reverse()
    
    # Trả về tuple (Đường đi, Chi phí)
    return path, final_cost

def find_euler_cycle_hierholzer(adj_list, nodes, start_node):
    """
    Tìm Chu trình Euler bằng Thuật toán Hierholzer (Tối ưu).
    
    Args:
        graph_dict (dict): Danh sách kề của đồ thị VÔ HƯỚNG. 
        start_node (hashable): Đỉnh bắt đầu của chu trình.

    Returns:
        list or str: Danh sách các đỉnh theo thứ tự của chu trình Euler (path), 
                     hoặc []
    """
    if start_node not in nodes:
        return []
    # Tạo bản sao để thao tác, sử dụng list() để dễ dàng dùng pop()
    current_graph = {node: neighbors[:] for node, neighbors in adj_list.items()}
    
    # Tính tổng số cạnh ban đầu (đếm mỗi cạnh một lần)
    total_edges = sum(len(neighbors) for neighbors in adj_list.values()) // 2

    current_path = [start_node]
    euler_cycle = []

    # Vòng lặp chính: Sử dụng ngăn xếp để tìm và hợp nhất các chu trình con
    while current_path:
        u = current_path[-1]

        if current_graph.get(u):
            # Lấy đỉnh kề v và xóa cạnh (u, v)
            v = current_graph[u].pop()
            
            # Xóa cạnh ngược lại (v, u) cho đồ thị VÔ HƯỚNG
            try:
                current_graph[v].remove(u)
            except ValueError:
                pass 
            
            # Mở rộng đường đi
            current_path.append(v)
        else:
            # Đỉnh u không còn cạnh chưa thăm. Hoàn thành chu trình con.
            # Đẩy đỉnh vào danh sách kết quả (theo thứ tự ngược)
            current_node = current_path.pop()
            euler_cycle.append(current_node)

    # Đảo ngược danh sách để có thứ tự chu trình đúng
    euler_cycle.reverse()

    # --- Kiểm tra và Trả về ---
    # Kiểm tra xem chu trình có đi qua tất cả các cạnh hay không (len(path) == total_edges + 1)
    if len(euler_cycle) == total_edges + 1:
        return euler_cycle
    else:
        return []

