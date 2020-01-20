import pyqtgraph as pg
from pyqtgraph import QtCore, QtGui
import numpy as np


# Create a subclass of GraphicsObject.
# The only required methods are paint() and boundingRect()
# (see QGraphicsItem documentation)
class HeatMap(pg.GraphicsObject):
    def __init__(self, bmi_state, colormap, grid):
        pg.GraphicsObject.__init__(self)
        self.bmi_state = bmi_state
        self.headcolors = colormap.mapToQColor(self.bmi_state.plotarray)
        
        self.grid = grid
        self.generatePicture()

    def generatePicture(self):
        # pre-computing a QPicture object allows paint() to run much more quickly,
        # rather than re-drawing the shapes every time.
        self.picture = QtGui.QPicture()
        p = QtGui.QPainter(self.picture)

        if self.grid:
            # 'k' seems to be black
            p.setPen(pg.mkPen("k"))
        else:
            p.setPen(pg.mkPen(None))

        polygon = QtGui.QPolygonF()
        grid_x = self.bmi_state.grid_x
        grid_y = self.bmi_state.grid_y
        if self.bmi_state.grid_type == "rectilinear":
            for i_x in range(len(grid_x) - 1):
                for i_y in range(len(grid_y) - 1):
                    polygon.append(QtCore.QPointF(grid_x[i_x], grid_y[i_y]))
                    polygon.append(QtCore.QPointF(grid_x[i_x + 1], grid_y[i_y]))
                    polygon.append(QtCore.QPointF(grid_x[i_x + 1], grid_y[i_y + 1]))
                    polygon.append(QtCore.QPointF(grid_x[i_x], grid_y[i_y + 1]))
                    
                    color = self.headcolors[i_x * (len(grid_y) - 1) + i_y]
                    p.setBrush(pg.mkBrush(color))
                    p.drawPolygon(polygon)
                    polygon.clear()
            p.end()
        elif self.bmi_state.grid_type == "unstructured":
            face_index = 0
            for i, node_count in enumerate(self.bmi_state.nodes_per_face):
                for j in range(node_count):
                    face_node = self.bmi_state.face_nodes[face_index + j]
                    polygon.append(QtCore.QPointF(grid_x[face_node], grid_y[face_node]))
                face_index += node_count + 1
                p.setBrush(pg.mkBrush(self.headcolors[i]))
                p.drawPolygon(polygon)
                polygon.clear()
            p.end()

    def paint(self, p, *args):
        p.drawPicture(0, 0, self.picture)

    def boundingRect(self):
        # boundingRect _must_ indicate the entire area that will be drawn on
        # or else we will get artifacts and possibly crashing.
        # (in this case, QPicture does all the work of computing the bounding rect for us)
        return QtCore.QRectF(self.picture.boundingRect())


# Adapted from https://gist.github.com/maedoc/b61090021d2a5161c5b9
class ColorBar(pg.GraphicsObject):
    def __init__(self, cmap, width, height, ticks=None, tick_labels=None, label=None):
        pg.GraphicsObject.__init__(self)

        # handle args
        label = label or ""
        w, h = width, height
        stops, colors = cmap.getStops("float")
        smn, spp = stops.min(), stops.ptp()
        stops = (stops - stops.min()) / stops.ptp()
        if ticks is None:
            ticks = np.r_[0.0:1.0:5j, 1.0] * spp + smn
        tick_labels = tick_labels or ["%0.2g" % (t,) for t in ticks]

        # setup picture
        self.pic = pg.QtGui.QPicture()
        p = pg.QtGui.QPainter(self.pic)

        # draw bar with gradient following colormap
        p.setPen(pg.mkPen("k"))
        grad = pg.QtGui.QLinearGradient(w / 2.0, 0.0, w / 2.0, h * 1.0)
        for stop, color in zip(stops, colors):
            grad.setColorAt(1.0 - stop, pg.QtGui.QColor(*[255 * c for c in color]))
        p.setBrush(pg.QtGui.QBrush(grad))
        p.drawRect(pg.QtCore.QRectF(0, 0, w, h))

        # draw ticks & tick labels
        mintx = 0.0
        for tick, tick_label in zip(ticks, tick_labels):
            y_ = (1.0 - (tick - smn) / spp) * h
            p.drawLine(0.0, y_, -5.0, y_)
            br = p.boundingRect(0, 0, 0, 0, pg.QtCore.Qt.AlignRight, tick_label)
            if br.x() < mintx:
                mintx = br.x()
            p.drawText(br.x() - 10.0, y_ + br.height() / 4.0, tick_label)

        # draw label
        br = p.boundingRect(0, 0, 0, 0, pg.QtCore.Qt.AlignRight, label)
        p.drawText(-br.width() / 2.0, h + br.height() + 5.0, label)

        # done
        p.end()

        # compute rect bounds for underlying mask
        self.zone = mintx - 12.0, -15.0, br.width() - mintx, h + br.height() + 30.0

    def paint(self, p, *args):
        # paint underlying mask
        p.setPen(pg.QtGui.QColor(255, 255, 255, 0))
        p.setBrush(pg.QtGui.QColor(255, 255, 255, 200))
        p.drawRoundedRect(*(self.zone + (9.0, 9.0)))

        # paint colorbar
        p.drawPicture(0, 0, self.pic)

    def boundingRect(self):
        return pg.QtCore.QRectF(self.pic.boundingRect())
