import logging
import pyqtgraph as pg
import numpy as np

from PyQt5 import QtCore, QtWidgets, QtGui
from matplotlib import colormaps

from qt_dataviewer.utils.qt_utils import qt_log_exception
from .plots import BasePlot
from .smart_format import SmartFormatter


logger = logging.getLogger(__name__)


class Plot2D(BasePlot):
    def create(self):
        self.plot = pg.PlotItem()
        self.plot.setDefaultPadding(0.01)

        self.img = pg.ImageItem()
        # set some image data. This is required for pyqtgraph > 0.11
        self.img.setImage(np.zeros((1, 1)))

        hist = pg.HistogramLUTWidget()
        hist.setImageItem(self.img)
        hist.gradient.setColorMap(get_color_map())
        hist.hide()
        self.hist = hist
        self.plot.addItem(self.img)
        self.widget = pg.PlotWidget(plotItem=self.plot)
        self.layout_widget = QtWidgets.QWidget()
        self.h_layout = QtWidgets.QHBoxLayout(self.layout_widget)
        self.h_layout.addWidget(self.widget)
        self.h_layout.addWidget(self.hist)
        self._layout.addWidget(self.layout_widget)

        self._plot_mode = 'uniform'

        self.label = QtWidgets.QLabel()
        self.label.setAlignment(QtCore.Qt.AlignRight)

        self._layout.addWidget(self.label)

        self._log_mode = {}

        self.proxy = pg.SignalProxy(self.plot.scene().sigMouseMoved, rateLimit=60, slot=self.mouseMoved)
        try:
            self.update()
            self.plot.setAspectLocked(False)
        except Exception:
            logger.error("Failed to create plot", exc_info=True)

    def show_sidebar(self, show):
        histogram = self.hist
        if not show:
            if not histogram.isHidden():
                histogram.hide()
        else:
            if histogram.isHidden():
                histogram.show()

    @qt_log_exception
    def update(self):
        plot_model = self._plot_model
        self.show_sidebar(plot_model.show_sidebar)

        data = plot_model.get_data()
        self._data = data
        x_array = data[data.dims[0]]
        y_array = data[data.dims[1]]

        x_scale = x_array.attrs.get('scale', '')
        y_scale = y_array.attrs.get('scale', '')
        if x_scale.endswith("_unsorted"):
            x_scale = x_scale[:-9]
            data = data.sortby(x_array.name)
            x_array = data[data.dims[0]]
        if y_scale.endswith("_unsorted"):
            y_scale = y_scale[:-9]
            data = data.sortby(y_array.name)
            y_array = data[data.dims[1]]

        x = x_array.data
        y = y_array.data

        x_formatter = SmartFormatter(x_array.attrs)
        self._x_formatter = x_formatter
        y_formatter = SmartFormatter(y_array.attrs)
        self._y_formatter = y_formatter
        z_formatter = SmartFormatter(data.attrs)
        self._z_formatter = z_formatter

        x = x * x_formatter.scale
        y = y * y_formatter.scale
        z = data.data
        if not np.any(np.isfinite(z)):
            logger.info("no valid data to plot")
            return

        plot = self.plot
        x_formatter.set_plot_axis(plot.getAxis('bottom'))
        y_formatter.set_plot_axis(plot.getAxis('left'))

        x_args = np.argwhere(np.isfinite(x)).T[0]
        y_args = np.argwhere(np.isfinite(y)).T[0]
        if len(x_args) == 0 or len(y_args) == 0:
            # No data yet. Nothing to update.
            return
        x_limit = [np.min(x_args), np.max(x_args)]
        y_limit = [np.min(y_args), np.max(y_args)]
        x_slice = slice(x_limit[0], x_limit[1]+1)
        y_slice = slice(y_limit[0], y_limit[1]+1)

        if x_scale == 'irregular' or y_scale == 'irregular':
            plot_mode = 'irregular'
        else:
            plot_mode = 'uniform'

        if plot_mode == 'uniform':
            if self._plot_mode != 'uniform':
                self.plot.removeItem(self.mesh)
                self.mesh = None
                self.img = pg.ImageItem()
                # set some image data. This is required for pyqtgraph > 0.11
                self.img.setImage(np.zeros((1, 1)))
                self.plot.addItem(self.img)
                self.hist.setImageItem(self.img)
                self._plot_mode = 'uniform'

            log_mode = {}
            if x_scale == 'log':
                log_mode['x'] = True
                x = np.log10(x)
            if y_scale == 'log':
                log_mode['y'] = True
                y = np.log10(y)
            self._log_mode = log_mode

            x_limit_num = (x[x_limit[0]], x[x_limit[1]])
            y_limit_num = (y[y_limit[0]], y[y_limit[1]])

            x_offset = np.min(x[x_args])
            y_offset = np.min(y[y_args])
            with np.errstate(divide='ignore', invalid='ignore'):
                x_scale = abs(x_limit_num[1] - x_limit_num[0])/(x_limit[1] - x_limit[0])
                y_scale = abs(y_limit_num[1] - y_limit_num[0])/(y_limit[1] - y_limit[0])

            if x_scale == 0 or np.isnan(x_scale):
                x_scale = 1
            else:
                x_offset -= 0.5*x_scale

            if y_scale == 0 or np.isnan(y_scale):
                y_scale = 1
            else:
                y_offset -= 0.5*y_scale

            # flip axis if scan from postive to negative value
            if x_limit_num[0] > x_limit_num[1]:
                z = z[::-1, :]
                x_offset -= (len(x)-x_limit[1]-1)*x_scale
            else:
                x_offset -= x_limit[0]*x_scale
            if y_limit_num[0] > y_limit_num[1]:
                z = z[:, ::-1]
                y_offset -= (len(y)-y_limit[1]-1)*y_scale
            else:
                y_offset -= y_limit[0]*y_scale

            rect = QtCore.QRectF(
                x_offset,
                y_offset,
                x_scale * len(x),
                y_scale * len(y),
            )
            plot.setLogMode(**log_mode)
            plot.invertY(False)
            self.img.setImage(z)
            self.img.setRect(rect)

        # TODO Cleanup !!
        if plot_mode == 'irregular':
            if self._plot_mode != 'irregular':
                self.plot.removeItem(self.img)
                self.img = None
                self.mesh = MyPColorMesh()
                self.hist.setImageItem(self.mesh)
                self.plot.addItem(self.mesh)
                self._plot_mode = 'irregular'

            log_mode = {
                'x': x_array.attrs.get('log', False),
                'y': y_array.attrs.get('log', False),
                }
            plot.setLogMode(**log_mode)
            self._log_mode = log_mode

            x_valid = x[x_slice]
            if log_mode.get('x'):
                if np.any(x_valid <= 0.0):
                    logger.warning("Skipping values <= 0 on x-axis")
                    x_args = np.argwhere(np.isfinite(x) & (x > 0)).T[0]
                    if len(x_args) == 0:
                        logger.warning("No data left on x-axis")
                        return
                    x_limit = [np.min(x_args), np.max(x_args)]
                    x_slice = slice(x_limit[0], x_limit[1]+1)
                    x_valid = x[x_slice]
                x_valid = np.log10(x_valid)

            y_valid = y[y_slice]
            if log_mode.get('y'):
                if np.any(y_valid <= 0.0):
                    logger.warning("Skipping values <= 0 on y-axis")
                    y_args = np.argwhere(np.isfinite(y) & (y > 0)).T[0]
                    if len(y_args) == 0:
                        logger.warning("No data left on y-axis")
                        return
                    y_limit = [np.min(y_args), np.max(y_args)]
                    y_slice = slice(y_limit[0], y_limit[1]+1)
                    y_valid = y[y_slice]
                y_valid = np.log10(y_valid)

            x_edges = self._get_edges(x_valid)
            y_edges = self._get_edges(y_valid)

            x_grid = x_edges[:, None] * np.ones(len(y_edges))
            y_grid = y_edges * np.ones(len(x_edges))[:, None]

            z = data.data[x_slice, y_slice]
            # determine z-levels.
            if np.any(np.isfinite(z)):
                self.mesh.setLevels((np.nanmin(z), np.nanmax(z)), update=False)

            self.mesh.setData(x_grid, y_grid, z, autoLevels=False)
            self.hist.setImageItem(self.mesh)

            # Calculate min/max values to show data with small empty border.
            # Default behavior of pyqtgraph is to select 'notural' values on axis.
            # This behavior can result in a big white space around the data.
            x_min, x_max = self._get_axis_limits(x_edges)
            y_min, y_max = self._get_axis_limits(y_edges)

            self.plot.setLimits(xMin=x_min, xMax=x_max, yMin=y_min, yMax=y_max)
            self.plot.invertY(False)

    def _get_edges(self, x):
        nx = len(x)+1
        edges = np.zeros(nx)
        edges[1:-1] = (x[1:] + x[:-1])/2
        edges[0] = 2*x[0] - edges[1]
        edges[-1] = 2*x[-1] - edges[-2]
        return edges

    def _get_axis_limits(self, values):
        x_min = min(values)
        x_max = max(values)
        delta = (x_max - x_min) * 0.02
        x_min -= delta
        x_max += delta
        return x_min, x_max

    @qt_log_exception
    def mouseMoved(self, evt):
        vb = self.plot.vb
        pos = evt[0]  # using signal proxy turns original arguments into a tuple
        if self.plot.sceneBoundingRect().contains(pos):
            mousePoint = vb.mapSceneToView(pos)
            x_val = mousePoint.x()
            y_val = mousePoint.y()
            if self._log_mode.get('x'):
                x_val = 10**x_val
            if self._log_mode.get('y'):
                y_val = 10**y_val

            data = self._data
            z = data * self._z_formatter.scale
            x = data[data.dims[0]] * self._x_formatter.scale
            y = data[data.dims[1]] * self._y_formatter.scale

            # Note: numpy 1.22 has nanargmin, but we're still on python 3.7. # @@@ CHANGE!
            # So use a[isnan(a)] = np.inf to remove nans
            d = np.abs(x.data-x_val)
            d[np.isnan(d)] = np.inf
            ix = d.argmin()
            d = np.abs(y.data-y_val)
            d[np.isnan(d)] = np.inf
            iy = d.argmin()
            value = z.data[ix, iy]
            x_val = x.data[ix]
            y_val = y.data[iy]

            x_str = self._x_formatter.with_units(x_val, x)
            y_str = self._y_formatter.with_units(y_val, y)
            z_str = self._z_formatter.with_units(value, z)

            self.label.setText(f"x={x_str}, y={y_str}: {z_str}")


def get_color_map():
    numofLines = 5
    colorMap = colormaps['viridis']
    colorList = np.linspace(0, 1, numofLines)
    lineColors = colorMap(colorList)

    lineColors = lineColors * 255
    lineColors = lineColors.astype(int)
    return pg.ColorMap(pos=np.linspace(0.0, 1.0, numofLines), color=lineColors)


class MyPColorMesh(pg.PColorMeshItem):
    """
    Makes PColorMeshItem compatible with ImageItem for the
    interaction with the histogram lut.

    The code is a bit hacky, but works for now.
    """

    def setLookupTable(self, lut, update=True):
        _lut = lut(n=256)
        # print(_lut)
        lut = [
            QtGui.QColor.fromRgb(rgb[0], rgb[1], rgb[2]) for rgb in _lut
            ]
        super().setLookupTable(lut)

    def getHistogram(self):
        data = self.z
        mn = np.nanmin(data)
        mx = np.nanmax(data)

        if mn is None or mx is None:
            # the data are all-nan
            return None, None
        if mx == mn:
            # degenerate image, arange will fail
            mx += 1
        bins = np.linspace(mn, mx, 500)

        data = data[np.isfinite(data)]
        hist = np.histogram(data, bins=bins)
        return hist[1][:-1], hist[0]
