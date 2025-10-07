import networkx as nx
import matplotlib.pyplot as plt
from graph_thanhchinh.algorithms import path_to_edges
from pathlib import Path
import base64
import io

#Hàm lưu ảnh đồ thị
def save_graph_image(graph, image_name, pos = None):
    """
    Vẽ đồ thị NetworkX và lưu nó thành file ảnh vào thư mục 'img'.

    Hàm này tạo một Figure Matplotlib từ đối tượng đồ thị NetworkX, 
    sau đó lưu Figure này vào thư mục 'img' (ngang hàng với main.py). 
    Thư mục 'img' sẽ được tạo nếu nó chưa tồn tại.

    Args:
        graph: Đối tượng đồ thị NetworkX đã được khởi tạo 
        image_name: Tên file ảnh muốn lưu
        pos: (Optional) Một dictionary chứa vị trí tùy chỉnh của các đỉnh.  
             Nếu None, hàm sẽ sử dụng nx.spring_layout() để tự động tính toán.

    Returns:
        None: Hàm không trả về giá trị, nhưng in ra thông báo thành công hoặc lỗi.
        
    Raises:
        IOError: Nếu xảy ra lỗi trong quá trình tạo thư mục hoặc lưu file.
    """
    
    # 1. KHỞI TẠO FIGURE
    # fig là đối tượng Figure mà Matplotlib dùng để lưu ảnh
    fig, ax = plt.subplots() # Giữ kích thước mặc định (6.4, 4.8 inches)
    
    # 2. XỬ LÝ VỊ TRÍ ĐỈNH (Layout)
    if pos is None:
        try:
            pos = nx.spring_layout(graph, seed=42)
        except Exception as e:
            print(f"Lỗi khi tính toán layout: {e}")
            plt.close(fig)
            return

    # 3. VẼ ĐỒ THỊ (Sử dụng thuộc tính cơ bản nhất của nx.draw)
    nx.draw(
        graph, 
        pos, 
        with_labels=True, # Hiển thị nhãn đỉnh
        ax=ax # Đảm bảo vẽ lên đối tượng Axes đã tạo
    )

    # Tắt trục tọa độ
    ax.axis('off')
    
    # 4. QUẢN LÝ ĐƯỜNG DẪN VÀ LƯU ẢNH
    from pathlib import Path

    current_dir = Path.cwd()
    image_dir = current_dir / "img"
    save_path = image_dir / image_name
    
    # Tạo thư mục 'img' nếu chưa có
    try:
        image_dir.mkdir(exist_ok=True)
    except Exception as e:
        print(f"❌ Lỗi (IOError): Không thể tạo thư mục '{image_dir.name}': {e}")
        plt.close(fig)
        return

    # Lưu và đóng figure
    try:
        fig.savefig(save_path, bbox_inches='tight') 
        plt.close(fig)
        
        print("---" * 15)
        print(f"✅ Đồ thị đã được lưu thành công tại: {save_path.relative_to(current_dir)}")
        print("---" * 15)
        
    except Exception as e:
        print(f"❌ Lỗi (IOError): Không thể lưu ảnh '{image_name}': {e}")
        
#Hàm lưu ảnh đồ thị với cạnh đánh dấu
def save_graph_image_with_highlights(graph, image_name, edges_to_highlight, pos = None):
    """
    Vẽ đồ thị NetworkX và lưu nó thành file ảnh vào thư mục 'img'.

    Hàm này tạo một Figure Matplotlib từ đối tượng đồ thị NetworkX, 
    sau đó lưu Figure này vào thư mục 'img' (ngang hàng với main.py). 
    Thư mục 'img' sẽ được tạo nếu nó chưa tồn tại.

    Args:
        graph: Đối tượng đồ thị NetworkX đã được khởi tạo 
        image_name: Tên file ảnh muốn lưu
        edges_to_highlight: Danh sách các cạnh cần tô sáng.
        pos: (Optional) Một dictionary chứa vị trí tùy chỉnh của các đỉnh.  
             Nếu None, hàm sẽ sử dụng nx.spring_layout() để tự động tính toán.

    Returns:
        None: Hàm không trả về giá trị, nhưng in ra thông báo thành công hoặc lỗi.
        
    Raises:
        IOError: Nếu xảy ra lỗi trong quá trình tạo thư mục hoặc lưu file.
    """
    
    # 1. Khởi tạo figure
    # fig là đối tượng Figure mà Matplotlib dùng để lưu ảnh
    fig, ax = plt.subplots() # Giữ kích thước mặc định (6.4, 4.8 inches)
    
    # 2. Xử lý vị trí đỉnh (Layout)
    if pos is None:
        try:
            pos = nx.spring_layout(graph, seed=42)
        except Exception as e:
            print(f"Lỗi khi tính toán layout: {e}")
            plt.close(fig)
            return

    # 3. Xử lý tập hợp các cạnh cần tô sáng
    # Tạo một tập hợp (set) để kiểm tra nhanh hơn, thêm cả thứ tự ngược (v, u)
    highlight_set = set()
    for u, v in edges_to_highlight:
        highlight_set.add((u, v))
        # Nếu là đồ thị vô hướng, thêm cả chiều ngược
        if not graph.is_directed():
             highlight_set.add((v, u))

    # 4. Tạo danh sách màu cho TẤT CẢ các cạnh
    edge_colors = []
    for u, v in graph.edges():
        # Kiểm tra xem cạnh hiện tại có nằm trong tập hợp nổi bật không
        if (u, v) in highlight_set:
            edge_colors.append('red') # Màu cho cạnh nổi bật
        else:
            edge_colors.append('black') # Màu mặc định cho các cạnh khác
    
    # 5. Vẽ đồ thị (Sử dụng thuộc tính cơ bản nhất của nx.draw)
    nx.draw(graph, pos,
            with_labels=True,        # Hiển thị nhãn nút
            node_color='skyblue',    # Màu nút
            node_size=800,           # Kích thước nút
            edge_color=edge_colors,  # Danh sách cạnh và màu
            width=2)                 # Độ dày của cạnh

    # Tắt trục tọa độ
    ax.axis('off')
    
    # 6. Quản lý đường dẫn và lưu ảnh
    from pathlib import Path

    current_dir = Path.cwd()
    image_dir = current_dir / "img"
    save_path = image_dir / image_name
    
    # Tạo thư mục 'img' nếu chưa có
    try:
        image_dir.mkdir(exist_ok=True)
    except Exception as e:
        print(f"❌ Lỗi (IOError): Không thể tạo thư mục '{image_dir.name}': {e}")
        plt.close(fig)
        return

    # Lưu và đóng figure
    try:
        fig.savefig(save_path, bbox_inches='tight') 
        plt.close(fig)
        
        print("---" * 15)
        print(f"✅ Đồ thị đã được lưu thành công tại: {save_path.relative_to(current_dir)}")
        print("---" * 15)
        
    except Exception as e:
        print(f"❌ Lỗi (IOError): Không thể lưu ảnh '{image_name}': {e}")
        
# --- HÀM TIỆN ÍCH 1: Khởi tạo/Đặt lại Màu sắc Gốc ---
def _initialize_edge_colors(graph, default_color='black'):
    """Khởi tạo màu sắc mặc định cho tất cả các cạnh."""
    global _EDGE_COLOR_MAP
    _EDGE_COLOR_MAP = {}
    for u, v in graph.edges():
        edge_key = tuple(sorted((u, v)))
        _EDGE_COLOR_MAP[edge_key] = default_color

# --- HÀM TIỆN ÍCH 2: Cập nhật Màu Cạnh Vĩnh viễn ---
def update_edge_color(u, v, color):
    """
    Cập nhật màu sắc vĩnh viễn cho một cạnh trong map màu gốc (Sử dụng cho trang Admin).
    """
    global _EDGE_COLOR_MAP
    edge_key = tuple(sorted((u, v)))
    if edge_key in _EDGE_COLOR_MAP:
        _EDGE_COLOR_MAP[edge_key] = color
    else:
        print(f"Cảnh báo: Cạnh {u}-{v} không tồn tại trong map màu.")
        
def save_custom_graph_image(
    graph, 
    image_name, 
    pos=None, 
    edges_hl=None, 
    edge_labels=None,
    hl_color='red' # Màu mặc định cho cạnh tô sáng
):
    """
    Vẽ đồ thị và lưu thành ảnh.
    Sử dụng màu gốc từ biến toàn cục _EDGE_COLOR_MAP và tô sáng tạm thời edges_hl.

    Args:
        graph (nx.Graph): Đối tượng đồ thị NetworkX.
        image_name (str): Tên file ảnh muốn lưu.
        pos (dict, optional): Vị trí tùy chỉnh của các nút.
        edges_hl (list of tuples, optional): Danh sách các cạnh (u, v) cần tô sáng tạm thời. 
        edge_labels (dict, optional): Dictionary nhãn { (u, v): 'Label' } để hiển thị trên các cạnh.
        hl_color (str): Màu sắc để tô sáng các cạnh trong edges_hl.
    """
    global _EDGE_COLOR_MAP 
    
    # 1. Khởi tạo Figure và Layout
    fig, ax = plt.subplots(figsize=(8, 6))
    if pos is None:
        try:
            pos = nx.spring_layout(graph, seed=42)
        except Exception as e:
            print(f"❌ Lỗi khi tính toán layout: {e}")
            plt.close(fig)
            return

    # 2. Xử lý Màu Sắc Cạnh (ĐÃ SỬ DỤNG _EDGE_COLOR_MAP)
    
    # Đảm bảo _EDGE_COLOR_MAP đã được khởi tạo cho đồ thị hiện tại
    if not _EDGE_COLOR_MAP or set(tuple(sorted(e)) for e in graph.edges()) != set(_EDGE_COLOR_MAP.keys()):
        _initialize_edge_colors(graph)

    # Chuẩn hóa các cạnh cần tô sáng (edges_hl thường là đường đi, nên dùng path_to_edges)
    highlight_set = set()
    if edges_hl:
        # Giả sử edges_hl có thể là danh sách cạnh hoặc danh sách nút của đường đi
        if isinstance(edges_hl[0], tuple): # Nếu là danh sách cạnh (u, v)
            temp_edges = edges_hl
        else: # Nếu là danh sách nút (đường đi)
            temp_edges = path_to_edges(edges_hl)

        for u, v in temp_edges:
             edge_key = tuple(sorted((u, v)))
             highlight_set.add(edge_key)

    edge_color_list = [] 
    for u, v in graph.edges():
        edge_key = tuple(sorted((u, v))) 
        
        if edge_key in highlight_set:
            # Ưu tiên màu tô sáng tạm thời (cho đường đi ngắn nhất, v.v.)
            color = hl_color 
        else:
            # Lấy màu GỐC từ biến toàn cục _EDGE_COLOR_MAP
            color = _EDGE_COLOR_MAP.get(edge_key, 'black')
        
        edge_color_list.append(color)

    # 3. Vẽ Đồ Thị
    nx.draw(
        graph, pos, ax=ax, with_labels=True, node_color='skyblue', 
        node_size=1200, font_size=10, edge_color=edge_color_list, 
        width=2, arrows=graph.is_directed()
    )

    # 4. VẼ NHÃN CẠNH BỔ SUNG (edge_labels)
    if edge_labels:
        bbox_style = {
            "boxstyle": "round,pad=0.3", "fc": "white", "ec": "none", "alpha": 0.8
        }
        
        nx.draw_networkx_edge_labels(
            graph, pos, edge_labels=edge_labels, font_color='orange', 
            font_size=10, label_pos=0.65, bbox=bbox_style
        )

    # 5. Tắt trục tọa độ
    ax.axis('off')

    # 6. Lưu Ảnh
    current_dir = Path.cwd()
    image_dir = current_dir / "img"
    save_path = image_dir / image_name
    
    try:
        image_dir.mkdir(exist_ok=True)
        fig.savefig(save_path, bbox_inches='tight')
        plt.close(fig)
        print("---" * 15)
        print(f"✅ Đồ thị đã được lưu thành công tại: {save_path.relative_to(current_dir)}")
        print("---" * 15)
    except Exception as e:
        print(f"❌ Lỗi khi lưu ảnh: {e}")
        plt.close(fig)
        
def generate_graph_base64(
    graph, 
    pos=None, 
    edges_hl=None, 
    edge_labels=None,
    hl_color='red' # Màu mặc định cho cạnh tô sáng
):
    """
    Vẽ đồ thị, mã hóa thành chuỗi Base64 (Data URI) và trả về.
    Làm nổi bật đường đi (edges_hl) bằng mũi tên có hướng.
    """
    global _EDGE_COLOR_MAP
    
    # 1. Khởi tạo Figure và Layout
    fig, ax = plt.subplots(figsize=(8, 6))
    if pos is None:
        try:
            if graph.nodes:
                pos = nx.spring_layout(graph, seed=42)
            else:
                pos = {}
        except Exception as e:
            print(f"❌ Lỗi khi tính toán layout: {e}")
            plt.close(fig)
            return None

    # 2. Xử lý Màu Sắc Cạnh & Phân tách Cạnh
    
    # Đảm bảo _EDGE_COLOR_MAP đã được khởi tạo
    if not _EDGE_COLOR_MAP or set(tuple(sorted(e)) for e in graph.edges()) != set(_EDGE_COLOR_MAP.keys()):
        _initialize_edge_colors(graph) 

    highlight_set = set()
    highlight_edges_tuple = [] # Danh sách các cạnh CÓ HƯỚNG cần tô sáng (ví dụ: (u, v))
    
    if edges_hl:
        if isinstance(edges_hl[0], tuple): 
            temp_edges = edges_hl
        else:
            # Giả định path_to_edges(edges_hl) tồn tại
            temp_edges = path_to_edges(edges_hl) 

        for u, v in temp_edges:
            edge_key = tuple(sorted((u, v))) 
            highlight_set.add(edge_key)
            highlight_edges_tuple.append((u, v)) # Cạnh CÓ HƯỚNG

    # PHÂN TÁCH CẠNH THƯỜNG (Vô hướng, không tô sáng)
    normal_edges = []
    for u, v in graph.edges():
        edge_key = tuple(sorted((u, v))) 
        if edge_key not in highlight_set:
            normal_edges.append((u, v))

    # 3. VẼ ĐỒ THỊ (Phân tách thành 3 phần để tạo mũi tên)
    
    # 3a. Vẽ các Nút và Nhãn Nút
    nx.draw_networkx_nodes(
        graph, pos, ax=ax, node_color='skyblue', 
        node_size=1200
    )
    nx.draw_networkx_labels(
        graph, pos, ax=ax, font_size=10
    )

    # 3b. Vẽ các Cạnh Thường (Vô hướng, màu gốc)
    nx.draw_networkx_edges(
        graph, pos, ax=ax, edgelist=normal_edges, 
        edge_color='black', width=2, arrows=False
    )

    # 3c. VẼ CẠNH TÔ SÁNG (Có hướng)
    if highlight_edges_tuple:
        
        # ⚠️ TẠO DI-GRAPH TẠM THỜI ĐỂ BUỘC NETWORKX VẼ MŨI TÊN
        highlight_graph = nx.DiGraph()
        highlight_graph.add_edges_from(highlight_edges_tuple)
        
        # Vẽ các cạnh từ đồ thị CÓ HƯỚNG tạm thời này
        nx.draw_networkx_edges(
            highlight_graph, pos, ax=ax, edgelist=highlight_edges_tuple, 
            edge_color=hl_color, width=3, 
            
            # Cấu hình mũi tên
            arrows=True, arrowsize=20, 
            connectionstyle='arc3,rad=0.0'
        )

    # 4. VẼ NHÃN CẠNH BỔ SUNG (edge_labels)
    if edge_labels:
        bbox_style = {
            "boxstyle": "round,pad=0.3", "fc": "white", "ec": "none", "alpha": 0.8
        }
        
        nx.draw_networkx_edge_labels(
            graph, pos, edge_labels=edge_labels, font_color='orange', 
            font_size=10, label_pos=0.65, bbox=bbox_style
        )

    # 5. Tắt trục tọa độ
    ax.axis('off')

    # 6. MÃ HÓA BASE64
    try:
        buffer = io.BytesIO()
        fig.savefig(buffer, format='png', bbox_inches='tight')
        plt.close(fig)
        buffer.seek(0)
        img_base64 = base64.b64encode(buffer.read()).decode('utf-8')
        return f"data:image/png;base64,{img_base64}"
        
    except Exception as e:
        print(f"❌ Lỗi khi mã hóa ảnh Base64: {e}")
        plt.close(fig)
        return None
     