from manim import *

def draw_polygon(
    scene,
    threeDAxes,
    vertices,
    edges=None,
    faces=None,
    vertices_color=RED,
    edge_color=BLUE,
    face_color=YELLOW,
    face_opacity=0.5,
    rt=5
):
    """
    - vertices: danh sách toạ độ 3D [[x,y,z], ...]
    - edges: [(i,j), (i,j,"dl"), ...]   # cạnh thường hoặc nét đứt
    - faces: [[i1,i2,i3,...], ...]      # danh sách mặt, mỗi mặt là list các đỉnh
    """

    # Vẽ cạnh
    if edges:
        for e in edges:
            if len(e) == 2:
                start, end = e
                style = "l"
            else:
                start, end, style = e

            start_line = threeDAxes.c2p(*vertices[start])
            end_line = threeDAxes.c2p(*vertices[end])

            if style == "l":
                line = Line(start_line, end_line, color=edge_color)
            elif style == "dl":
                line = DashedLine(start_line, end_line, color=edge_color, dash_length=0.2)

            scene.play(Create(line), run_time=rt/len(edges))

    # Vẽ đỉnh
    for v in vertices:
        sphere = Sphere(radius=0.1, color=vertices_color).move_to(threeDAxes.c2p(*v))
        scene.play(Create(sphere), run_time=rt/len(faces))

    # Vẽ mặt
    if faces:
        for f in faces:
            pts = [threeDAxes.c2p(*vertices[i]) for i in f]
            poly = Polygon(*pts, color=face_color, fill_opacity=face_opacity)
            scene.play(Create(poly), run_time=rt/len(faces))

def animate_edges(self, threeDAxes, vertices, edges, edge_color=BLUE):
    """
    Animate nhiều cạnh đồng thời.
    edges = [(start, end, target_style), ...]
    target_style: "l" hoặc "dl"
    """
    animations = []

    if not hasattr(self, "edge_lines"):
        self.edge_lines = {}  # Lưu trạng thái các cạnh

    for start, end, target_style in edges:
        start_line = threeDAxes.c2p(*vertices[start])
        end_line = threeDAxes.c2p(*vertices[end])

        # Nếu cạnh chưa tồn tại thì tạo luôn
        if (start, end) not in self.edge_lines:
            if target_style == "l":
                line_now = Line(start_line, end_line, color=edge_color)
            else:
                line_now = DashedLine(start_line, end_line, color=edge_color, dash_length=0.2)
            self.add(line_now)
            self.edge_lines[(start, end)] = line_now
            continue

        line_now = self.edge_lines[(start, end)]

        # Nếu style giống style hiện tại → bỏ qua
        if isinstance(line_now, Line) and target_style == "l":
            continue
        if isinstance(line_now, DashedLine) and target_style == "dl":
            continue

        # Tạo cạnh mục tiêu
        if target_style == "l":
            line_target = Line(start_line, end_line, color=edge_color)
        else:
            line_target = DashedLine(start_line, end_line, color=edge_color, dash_length=0.2)

        animations.append(Transform(line_now, line_target))
        self.edge_lines[(start, end)] = line_target

    # Chạy tất cả animation cùng lúc
    if animations:
        self.play(*animations, run_time=1)
