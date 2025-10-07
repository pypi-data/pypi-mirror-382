import json
from typing import List, Dict, Tuple, Any

#Hàm đọc dữ liệu từ file json
def load_graph_data(filename):
    """
    Đọc dữ liệu đồ thị từ file JSON và trả về 5 giá trị: 
    nodes, edges_w_dynamic, edges_w_original, pos, edges_label.
    
    Nếu có lỗi, hàm trả về các cấu trúc dữ liệu rỗng tương ứng.

    Args:
        filename: Tên file JSON chứa dữ liệu đồ thị.

    Returns:
        Tuple chứa: (nodes, edges_w_dynamic, edges_w_original, pos, edges_label)
    """
    import json
    from typing import List, Dict, Tuple, Any

    # Giá trị mặc định khi có lỗi
    nodes_default: List[str] = []
    edges_w_dynamic_default: List[List[Any]] = []
    edges_w_original_default: List[List[Any]] = [] # Khởi tạo mặc định cho trọng số gốc
    pos_default: Dict[str, Tuple[float, float]] = {}
    edges_label_default: Dict[Tuple[str, str], str] = {}
    
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except FileNotFoundError:
        print(f"❌ Lỗi: Không tìm thấy file '{filename}'. Trả về dữ liệu rỗng.")
        return nodes_default, edges_w_dynamic_default, edges_w_original_default, pos_default, edges_label_default
    except json.JSONDecodeError:
        print(f"❌ Lỗi: File '{filename}' không phải là JSON hợp lệ. Trả về dữ liệu rỗng.")
        return nodes_default, edges_w_dynamic_default, edges_w_original_default, pos_default, edges_label_default
    except Exception as e:
        print(f"❌ Lỗi không xác định khi đọc file: {e}. Trả về dữ liệu rỗng.")
        return nodes_default, edges_w_dynamic_default, edges_w_original_default, pos_default, edges_label_default

    # 1. Xử lý Trọng số
    edges_w_dynamic = data.get("edges_w_dynamic", edges_w_dynamic_default)
    edges_w_original = data.get("edges_w_original", edges_w_original_default) # Đọc trọng số gốc
        
    # 2. Xử lý Vị trí Đỉnh (pos)
    current_pos = data.get("pos", pos_default)
    if current_pos:
        for node, coords in current_pos.items():
            current_pos[node] = tuple(coords)
        
    # 3. Xử lý Nhãn Cạnh (edges_label)
    converted_labels = {}
    current_labels = data.get("edges_label", edges_label_default)
    if current_labels:
        for edge_str, label in current_labels.items():
            try:
                u, v = edge_str.split(',')
                converted_labels[(u, v)] = label
            except ValueError:
                print(f"⚠️ Cảnh báo: Key nhãn cạnh '{edge_str}' không đúng định dạng 'u,v' và bị bỏ qua.")
        current_labels = converted_labels
        
    # 4. Trả về 5 giá trị
    return (
        data.get("nodes", nodes_default),
        edges_w_dynamic, # Trọng số động (Dijkstra)
        edges_w_original, # Trọng số gốc (Chi phí KM)
        current_pos,
        current_labels
    )

#Hàm ghi dữ liệu vào file json
def save_graph_data(
    filename, 
    nodes: List[str] = [], 
    edges_w_dynamic: List[List[Any]] = [], 
    edges_w_original: List[List[Any]] = [], 
    pos: Dict[str, Tuple[float, float]] = {}, 
    edges_label: Dict[Tuple[str, str], str] = {}
):
    """
    Ghi dữ liệu đồ thị (nodes, edges_w_dynamic, edges_w_original, pos, edges_label) vào file JSON, 
    thực hiện chuyển đổi định dạng cần thiết cho JSON.

    Args:
        filename: Tên file JSON để ghi dữ liệu.
        # ... (Các Args khác giữ nguyên)
    """
    import json
    from typing import List, Dict, Tuple, Any
    
    # --- CHUYỂN ĐỔI DỮ LIỆU ĐỂ LƯU ---
    
    # 1. Xử lý Vị trí Đỉnh (pos): Chuyển tuple (x, y) thành list [x, y]
    json_pos = {node: list(coords) for node, coords in pos.items()}
        
    # 2. Xử lý Nhãn Cạnh (edges_label): Chuyển key tuple (u, v) thành key string "u,v"
    json_labels = {f"{u},{v}": label for (u, v), label in edges_label.items()}
        
    # 3. TỔNG HỢP DỮ LIỆU (edges_w_... được truyền vào dưới dạng List[List[...]])
    data_to_save = {
        "nodes": nodes,
        "edges_w_dynamic": edges_w_dynamic, 
        "edges_w_original": edges_w_original, 
        "pos": json_pos,
        "edges_label": json_labels
    }
    
    # 4. Ghi vào file JSON
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            # indent=4: Đảm bảo định dạng DỄ ĐỌC (đẹp)
            # ensure_ascii=False: Giúp các ký tự không phải ASCII (tiếng Việt) được lưu đúng
            json.dump(data_to_save, f, indent=4, ensure_ascii=False) 
        print(f"✅ Đã ghi thành công dữ liệu đồ thị vào file: '{filename}'.")
    except Exception as e:
        print(f"❌ Lỗi khi ghi file JSON '{filename}': {e}")