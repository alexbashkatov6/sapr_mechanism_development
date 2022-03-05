from copy import copy

from PyQt5.QtWidgets import QGraphicsScene, QGraphicsView, QMainWindow, QGraphicsPathItem, QGraphicsRectItem, \
    QGraphicsEllipseItem, QGraphicsItem, QGraphicsPolygonItem, QGraphicsSceneMouseEvent, QGraphicsTextItem
from PyQt5.QtGui import QPen, QBrush, QPolygonF, QPainterPath, QFont, QFontMetrics
from PyQt5.QtCore import Qt, QRectF, QLineF, QPointF


GOLDEN_RATIO = 1.618

TR_CONTOUR_WIDTH = 300
TR_CONTOUR_HEIGHT = 500
TR_CONTOUR_CORNER_ROUND = 20
TR_CONTOUR_LINES_WIDTH = 4

TR_HEADER_HEIGHT = TR_CONTOUR_HEIGHT * (1 - 1 / GOLDEN_RATIO) / 2
TR_FOOTER_HEIGHT = TR_HEADER_HEIGHT

TR_HEADER_FOOTER_FONT = "Times"
TR_HEADER_FOOTER_FONT_SIZE = 40
TR_HEADER_FOOTER_FONT_STYLE = QFont.Bold

TR_INTERNAL_GEOMETRY_LINES_WIDTH = 4
TR_INTERNAL_GEOMETRY_REGION_SIZE = 200
TR_ARROW_WIDTH_KOEFF = 0.3

TR_CONN_POINT_RAD = 10
TR_CONN_POINT_FONT_SIZE = 30
TR_CONN_POINT_LABEL_GAP = 10


def flip_horizontal(point: QPointF, center_point: QPointF) -> QPointF:
    return QPointF(2*center_point.x()-point.x(), point.y())


def flip_vertical(point: QPointF, center_point: QPointF) -> QPointF:
    return QPointF(point.x(), 2*center_point.y()-point.y())


class Line(QGraphicsPathItem):
    def __init__(self, *args, **kwargs):
        self.width: float = args[0]
        self.start_point: QPointF = args[1]
        self.end_point: QPointF = args[2]
        super().__init__(*args[3:], **kwargs)
        self.draw_path()

    def draw_path(self):
        poly = QPolygonF(
                [
                    self.start_point,
                    self.end_point
                ])

        self._pen = QPen(Qt.black)
        self._pen.setWidthF(self.width)

        self._base_path = QPainterPath()
        self._base_path.addPolygon(poly)

        self.setPath(self._base_path)
        self.setPen(self._pen)
        self.setBrush(QBrush(Qt.black))

    def flip_horizontal(self, center_point: QPointF):
        self.start_point = flip_horizontal(self.start_point, center_point)
        self.end_point = flip_horizontal(self.end_point, center_point)
        self.draw_path()

    def flip_vertical(self, center_point: QPointF):
        self.start_point = flip_vertical(self.start_point, center_point)
        self.end_point = flip_vertical(self.end_point, center_point)
        self.draw_path()


class Triangle(QGraphicsPathItem):
    def __init__(self, *args, **kwargs):
        self.points: list[QPointF] = list(args[:3])
        super().__init__(*args[3:], **kwargs)
        self.draw_path()

    def draw_path(self):
        poly = QPolygonF(self.points)

        self._base_path = QPainterPath()
        self._base_path.addPolygon(poly)

        self._pen = QPen(Qt.black)

        self.setPath(self._base_path)
        self.setPen(self._pen)
        self.setBrush(QBrush(Qt.black))

    def flip_horizontal(self, center_point: QPointF):
        self.points = [flip_horizontal(point, center_point) for point in self.points]
        self.draw_path()

    def flip_vertical(self, center_point: QPointF):
        self.points = [flip_vertical(point, center_point) for point in self.points]
        self.draw_path()


class TextPath(QGraphicsPathItem):
    def __init__(self, base_point: QPointF, text: str, size: int, font_type: str, text_style: int,
                 h_align_type: str, h_align_padding: int, v_align_type: str, v_align_padding: int, *args, **kwargs):
        self.base_point_: QPointF = base_point
        self.text_: str = text
        self.size_: int = size
        self.font_type_: str = font_type
        self.text_style_: int = text_style
        self.h_align_type_: str = h_align_type
        self.h_align_padding_: int = h_align_padding
        self.v_align_type_: str = v_align_type
        self.v_align_padding_: int = v_align_padding
        super().__init__(*args, **kwargs)

        font_ = QFont(self.font_type_, self.size_, self.text_style_)
        fontMetrics = QFontMetrics(font_)
        self.text_rect_size_ = fontMetrics.size(0, self.text_)

        self.path_ = QPainterPath()
        self.path_.addText(self.left_bottom_corner_evaluation(), font_, self.text_)

        self.setPath(self.path_)
        self.setPen(QPen(Qt.black))
        self.setBrush(QBrush(Qt.black))

    def left_bottom_corner_evaluation(self) -> QPointF:
        x = 0
        y = 0
        return QPointF(x, y)

class AdaptiveTextPath(TextPath):
    def __init__(self, base_point: QPointF, text: str, size: int, font_type: str, text_style: int,
                 h_align_type: str, h_align_padding: int, v_align_type: str, v_align_padding: int, *args, **kwargs):
        super().__init__(base_point, text, size, font_type, text_style, h_align_type, h_align_padding, v_align_type, v_align_padding, *args, **kwargs)


class HeaderFooterTextPath(AdaptiveTextPath):
    def __init__(self, base_point: QPointF, text: str, size: int, font_type: str, text_style: int,
                 h_align_type: str, h_align_padding: int, v_align_type: str, v_align_padding: int, *args, **kwargs):
        super().__init__(base_point, text, TR_HEADER_FOOTER_FONT_SIZE, TR_HEADER_FOOTER_FONT, TR_HEADER_FOOTER_FONT_STYLE, 'center', 0, 'center', 0, *args, **kwargs)

# halign = center, left, right

class FlipableTextPath(TextPath):
    pass


class MainContourTopologyRect(QGraphicsPathItem):
    def __init__(self, *args, **kwargs):
        # self._header_text: str = args[0]
        # self._footer_text: str = args[1]
        # super().__init__(*args[2:], **kwargs)
        super().__init__(*args, **kwargs)

        self._center_point = QPointF(TR_CONTOUR_WIDTH / 2, TR_CONTOUR_HEIGHT / 2)
        self._header_text_path = HeaderText("text")
        # self._header_text_path = HeaderText(self._header_text)
        self._header_text_path.setParentItem(self)
        self._footer_text_path = FooterText("text")
        # self._footer_text_path = FooterText(self._footer_text)
        self._footer_text_path.setParentItem(self)
        self._rp = RailPoint(TR_INTERNAL_GEOMETRY_REGION_SIZE, QPointF(TR_CONTOUR_WIDTH / 2, TR_CONTOUR_HEIGHT / 2))
        self._rp.setParentItem(self)

        self._base_path = QPainterPath()
        self._base_path.addRoundedRect(QRectF(0, 0, TR_CONTOUR_WIDTH, TR_CONTOUR_HEIGHT), TR_CONTOUR_CORNER_ROUND, TR_CONTOUR_CORNER_ROUND)
        self._base_path.addRect(QRectF(0, TR_HEADER_HEIGHT, TR_CONTOUR_WIDTH, TR_CONTOUR_HEIGHT - TR_HEADER_HEIGHT - TR_FOOTER_HEIGHT))

        self._pen = QPen(Qt.black)
        self._pen.setWidthF(TR_CONTOUR_LINES_WIDTH)

        self.setPath(self._base_path)
        self.setPen(self._pen)
        self.setFlags(QGraphicsItem.ItemIsMovable | QGraphicsItem.ItemIsSelectable)

    def flip_rp_horizontal(self):
        self._rp.flip_horizontal(self._center_point)

    def flip_rp_vertical(self):
        self._rp.flip_vertical(self._center_point)


class FooterText(QGraphicsPathItem):
    def __init__(self, *args, **kwargs):
        text: str = args[0]
        super().__init__(*args[1:], **kwargs)

        self._base_path = QPainterPath()
        times_font = QFont("Times", TR_HEADER_FOOTER_FONT_SIZE)  # , QFont.Bold
        fontMetrics = QFontMetrics(times_font)
        self._footer_text = text
        header_size = fontMetrics.size(0, self._footer_text)
        header_text_base_point = QPointF(TR_CONTOUR_WIDTH / 2 - header_size.width() / 2, TR_CONTOUR_HEIGHT - TR_FOOTER_HEIGHT / 2 + header_size.height() / 2)
        self._base_path.addText(header_text_base_point, times_font, self._footer_text)

        self._pen = QPen(Qt.black)

        self.setPath(self._base_path)
        self.setPen(self._pen)
        self.setBrush(QBrush(Qt.black))


class HeaderText(QGraphicsPathItem):
    def __init__(self, *args, **kwargs):
        text: str = args[0]
        super().__init__(*args[1:], **kwargs)

        self._base_path = QPainterPath()
        times_font = QFont("Times", TR_HEADER_FOOTER_FONT_SIZE, QFont.Bold)
        fontMetrics = QFontMetrics(times_font)
        self._header_text = text
        header_size = fontMetrics.size(0, self._header_text)
        header_text_base_point = QPointF(TR_CONTOUR_WIDTH / 2 - header_size.width() / 2, TR_HEADER_HEIGHT / 2 + header_size.height() / 2)
        self._base_path.addText(header_text_base_point, times_font, self._header_text)

        self._pen = QPen(Qt.black)

        self.setPath(self._base_path)
        self.setPen(self._pen)
        self.setBrush(QBrush(Qt.black))


class ConnPntLabel(QGraphicsPathItem):
    def __init__(self, *args, **kwargs):
        text: str = args[0]
        orientation: str = args[1]
        conn_point_coords: QPointF = args[2]
        super().__init__(*args[3:], **kwargs)

        self._base_path = QPainterPath()
        times_font = QFont("Times", TR_CONN_POINT_FONT_SIZE, QFont.Bold)
        fontMetrics = QFontMetrics(times_font)
        text_size = fontMetrics.size(0, text)
        base_point = QPointF(0, 0)
        if orientation == "left":
            base_point = QPointF(conn_point_coords.x() - TR_CONN_POINT_LABEL_GAP - text_size.width(), conn_point_coords.y() - TR_CONN_POINT_LABEL_GAP)
        if orientation == "right":
            base_point = QPointF(conn_point_coords.x() + TR_CONN_POINT_LABEL_GAP, conn_point_coords.y() - TR_CONN_POINT_LABEL_GAP)
        if orientation == "top":
            base_point = QPointF(conn_point_coords.x() + TR_CONN_POINT_LABEL_GAP, conn_point_coords.y() - TR_CONN_POINT_LABEL_GAP)
        if orientation == "bottom":
            base_point = QPointF(conn_point_coords.x() - TR_CONN_POINT_LABEL_GAP - text_size.width(), conn_point_coords.y() + TR_CONN_POINT_LABEL_GAP + text_size.height())
        self._base_path.addText(base_point, times_font, text)

        self._pen = QPen(Qt.black)

        self.setPath(self._base_path)
        self.setPen(self._pen)
        self.setBrush(QBrush(Qt.black))


class ConnPntEllipse(QGraphicsPathItem):
    def __init__(self, *args, **kwargs):
        self.center_point: QPointF = args[0]
        super().__init__(*args[1:], **kwargs)
        self.draw_path()

    def draw_path(self):
        self.circle_rect = QRectF(self.center_point.x() - TR_CONN_POINT_RAD,
                                  self.center_point.y() - TR_CONN_POINT_RAD,
                                  2 * TR_CONN_POINT_RAD,
                                  2 * TR_CONN_POINT_RAD)
        self._base_path = QPainterPath()
        self._base_path.addEllipse(self.circle_rect)

        self._pen = QPen(Qt.black)

        self.setPath(self._base_path)
        self.setPen(self._pen)
        self.setBrush(QBrush(Qt.black))


class ConnectionPoint(QGraphicsPathItem):
    def __init__(self, *args, **kwargs):
        self.center_point_to: QPointF = args[0]
        self.orientation: str = args[1]
        self.label_text: str = args[2]
        super().__init__(*args[3:], **kwargs)
        self.draw_path()

    def draw_path(self):
        conn_point_center = QPointF(0, 0)
        if self.orientation == "left":
            conn_point_center = QPointF(self.center_point_to.x() - TR_CONTOUR_WIDTH / 2, self.center_point_to.y())
            self.label = ConnPntLabel(self.label_text, self.orientation, conn_point_center)
        if self.orientation == "right":
            conn_point_center = QPointF(self.center_point_to.x() + TR_CONTOUR_WIDTH / 2, self.center_point_to.y())
            self.label = ConnPntLabel(self.label_text, self.orientation, conn_point_center)
        if self.orientation == "top":
            conn_point_center = QPointF(self.center_point_to.x(), self.center_point_to.y() - TR_CONTOUR_HEIGHT / 2)
            self.label = ConnPntLabel(self.label_text, self.orientation, conn_point_center)
        if self.orientation == "bottom":
            conn_point_center = QPointF(self.center_point_to.x(), self.center_point_to.y() + TR_CONTOUR_HEIGHT / 2)
            self.label = ConnPntLabel(self.label_text, self.orientation, conn_point_center)
        self.label.setParentItem(self)
        self.cp_ellipse = ConnPntEllipse(conn_point_center)
        self.cp_ellipse.setParentItem(self)

        self._pen = QPen(Qt.black)

        self._base_path = QPainterPath()

        self.setPath(self._base_path)
        self.setPen(self._pen)
        self.setBrush(QBrush(Qt.black))

    def flip_horizontal(self, center_point: QPointF):
        if self.orientation in ["left", "right"]:
            self.label.setParentItem(None)
            self.cp_ellipse.setParentItem(None)
            if self.orientation == "left":
                self.orientation = "right"
            elif self.orientation == "right":
                self.orientation = "left"
            self.draw_path()

    def flip_vertical(self, center_point: QPointF):
        if self.orientation in ["top", "bottom"]:
            self.label.setParentItem(None)
            self.cp_ellipse.setParentItem(None)
            if self.orientation == "top":
                self.orientation = "bottom"
            elif self.orientation == "bottom":
                self.orientation = "top"
            self.draw_path()


class RailPoint(QGraphicsPathItem):
    def __init__(self, *args, **kwargs):
        region_size: float = args[0]
        center: QPointF = args[1]
        super().__init__(*args[2:], **kwargs)
        self._oblique_line = Line(TR_INTERNAL_GEOMETRY_LINES_WIDTH,
                                  center + QPointF(0, -region_size/2),
                                  center + QPointF(-region_size/2, region_size/2))
        self._direct_line = Line(TR_INTERNAL_GEOMETRY_LINES_WIDTH,
                                 center + QPointF(-region_size/2, region_size/2),
                                 center + QPointF(region_size/2, region_size/2))
        self._triangle = Triangle(center + QPointF(0, region_size / 2 - TR_ARROW_WIDTH_KOEFF * region_size / 2),
                                  center + QPointF(0, region_size / 2 + TR_ARROW_WIDTH_KOEFF * region_size / 2),
                                  center + QPointF(region_size/2, region_size/2))

        self._oblique_line.setParentItem(self)
        self._direct_line.setParentItem(self)
        self._triangle.setParentItem(self)

        self.conn_pnt_0 = ConnectionPoint(center, "left", "0")
        self.conn_pnt_1 = ConnectionPoint(center, "right", "1")
        self.conn_pnt_2 = ConnectionPoint(center, "top", "2")
        self.conn_pnt_0.setParentItem(self)
        self.conn_pnt_1.setParentItem(self)
        self.conn_pnt_2.setParentItem(self)

    def flip_horizontal(self, center_point: QPointF):
        self._oblique_line.flip_horizontal(center_point)
        self._direct_line.flip_horizontal(center_point)
        self._triangle.flip_horizontal(center_point)
        self.conn_pnt_0.flip_horizontal(center_point)
        self.conn_pnt_1.flip_horizontal(center_point)
        self.conn_pnt_2.flip_horizontal(center_point)

    def flip_vertical(self, center_point: QPointF):
        self._oblique_line.flip_vertical(center_point)
        self._direct_line.flip_vertical(center_point)
        self._triangle.flip_vertical(center_point)
        self.conn_pnt_0.flip_vertical(center_point)
        self.conn_pnt_1.flip_vertical(center_point)
        self.conn_pnt_2.flip_vertical(center_point)


class TopologyRectangle(QGraphicsPathItem):
    def __init__(self, *args, **kwargs):
        self.to_type = args[0]
        self.to_tag = args[1]
        super().__init__(*args[2:], **kwargs)
        self._contour = MainContourTopologyRect()
        self._footer = HeaderFooterTextPath(self.to_tag)

        if self.to_type == "Point":
            self._filling = TOPointFilling()

        self._contour.setParentItem(self)
        self._footer.setParentItem(self)
        self._filling.setParentItem(self)


class CustomGC(QGraphicsScene):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.tr = TopologyRectangle()
        self.addItem(self.tr)

        self.selectionChanged.connect(self.dme)
        self.focusItemChanged.connect(self.dme2)

    def dragEnterEvent(self, e):
        print("dragEnterEvent")
        super().dragEnterEvent(e)

    def mouseDoubleClickEvent(self, e: QGraphicsSceneMouseEvent):
        print("mouseDoubleClickEvent")
        super().mouseDoubleClickEvent(e)

    def mousePressEvent(self, e: QGraphicsSceneMouseEvent):
        pos = e.scenePos()
        print("mousePressEvent", pos.x(), pos.y())
        print("items_at", self.items(pos))
        super().mousePressEvent(e)

    def mouseReleaseEvent(self, e: QGraphicsSceneMouseEvent):
        print("mouseReleaseEvent", e.pos().x(), e.pos().y())
        super().mouseReleaseEvent(e)

    def dme(self):
        print("selectionChanged")

    def dme2(self):
        print("focusItemChanged")

    def flip_horizontal(self):
        items = self.selectedItems()
        for item in items:
            print("item_info")
            # item.mapToScene()
            boundingRect = item.boundingRect()
            s_boundingRect = item.sceneBoundingRect()
            # print(boundingRect.x(), boundingRect.y(), boundingRect.height(), boundingRect.width())
            print(s_boundingRect.x(), s_boundingRect.y(), s_boundingRect.height(), s_boundingRect.width())
        print("flip_horizontal", items)
        self.tr._contour.flip_rp_horizontal()

    def flip_vertical(self):
        items = self.selectedItems()
        print("flip_vertical", items)
        self.tr._contour.flip_rp_vertical()


class CustomView(QGraphicsView):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # self.rotate(-45)
        self.scale(0.5, 0.5)


class CustomMW(QMainWindow):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setGeometry(40, 40, 1840, 980)
        self.scene = CustomGC(0, 0, 1800, 900)
        self.view = CustomView(self.scene)
        self.setCentralWidget(self.view)

        # menus
        menu_bar = self.menuBar()

        item_menu = menu_bar.addMenu('&Item')
        flip_h_action = item_menu.addAction("&Flip horizontal")
        flip_h_action.setShortcut("Ctrl+H")
        flip_h_action.triggered.connect(self.scene.flip_horizontal)
        flip_v_action = item_menu.addAction("&Flip vertical")
        flip_v_action.setShortcut("Ctrl+J")
        flip_v_action.triggered.connect(self.scene.flip_vertical)


