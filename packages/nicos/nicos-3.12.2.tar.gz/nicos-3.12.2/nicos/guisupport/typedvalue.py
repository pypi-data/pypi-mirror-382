# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-2025 by the NICOS contributors (see AUTHORS)
#
# This program is free software; you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free Software
# Foundation; either version 2 of the License, or (at your option) any later
# version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more
# details.
#
# You should have received a copy of the GNU General Public License along with
# this program; if not, write to the Free Software Foundation, Inc.,
# 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#
# Module authors:
#   Georg Brandl <g.brandl@fz-juelich.de>
#
# *****************************************************************************

"""Widgets for entering values of different NICOS parameter/value types.

The supported types are defined in `nicos.core.params`.
"""

import numpy as np

from nicos.core import anytype, params
from nicos.devices.sxtal.xtal.sxtalcell import SXTalCellType
from nicos.guisupport.qt import QCheckBox, QComboBox, QFormLayout, QFrame, \
    QGridLayout, QHBoxLayout, QIcon, QIntValidator, QLabel, QLineEdit, \
    QPushButton, QScrollArea, QSizePolicy, QSpinBox, Qt, QTableWidget, \
    QTableWidgetItem, QVBoxLayout, QWidget, pyqtSignal
from nicos.guisupport.utils import DoubleValidator
from nicos.guisupport.widget import NicosWidget, PropDef
from nicos.protocols.cache import cache_dump, cache_load


class DeviceValueEdit(NicosWidget, QWidget):

    designer_description = 'Editor for a device value with the right kind ' \
        'of widget'

    valueModified = pyqtSignal()
    valueChosen = pyqtSignal(object)

    dev = PropDef('dev', str, '', 'Device name')
    useButtons = PropDef('useButtons', bool, False,
                         'Use buttons for values with few choices?')
    allowEnter = PropDef('allowEnter', bool, True,
                         'Emit valueChosen signal on pressing Enter?')
    updateValue = PropDef('updateValue', bool, False,
                          'Update the editor when the device value changes?')
    showUnit = PropDef('showUnit', bool, True, 'Show the unit next to the input')
    initDefault = PropDef('initDefault', bool, False,
                          'Initialize with a default value instead of the '
                          'current device value?')

    def __init__(self, parent, designMode=False, **kwds):
        self._inner = None
        QWidget.__init__(self, parent, **kwds)
        NicosWidget.__init__(self)
        self._layout = QHBoxLayout()
        self._layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self._layout)
        if designMode:
            self._layout.insertWidget(0, QLabel('(Value Editor)', self))

    def setFocus(self):
        if self._inner is not None:
            self._inner.setFocus()
        else:
            QWidget.setFocus(self)

    def propertyUpdated(self, pname, value):
        if pname == 'dev':
            self._reinit()
        NicosWidget.propertyUpdated(self, pname, value)

    def setClient(self, client):
        NicosWidget.setClient(self, client)
        self._reinit()

    def on_client_connected(self):
        self._reinit()

    def registerKeys(self):
        if self.props['updateValue'] and self.props['dev']:
            self.registerDevice(self.props['dev'])

    def on_devValueChange(self, dev, value, strvalue, unitvalue, expired):
        self._reinit(value)

    def on_devMetaChange(self, dev, fmtstr, unit, fixed):
        self._reinit()

    def _reinit(self, curvalue=None):
        if not self._client or not self._client.isconnected:
            return
        devname = str(self.props['dev'])
        if devname:
            params = self._client.getDeviceParams(devname)
            valuetype = self._client.getDeviceValuetype(devname)
            valueinfo = self._client.eval('session.getDevice(%r).valueInfo()' %
                                          devname, None)
            unit = params.get('unit', '') if self.props['showUnit'] else ''
            fmtstr = params.get('fmtstr', '%s')
            if curvalue is None:
                curvalue = params.get('target')
            if (self.props['initDefault'] or curvalue is None) \
               and valuetype is not None:
                curvalue = valuetype()
        else:
            valuetype = str
            curvalue = ''
            fmtstr = '%s'
            unit = ''
            valueinfo = None

        self._inner = create(self, valuetype, curvalue, fmtstr, unit,
                             allow_buttons=self.props['useButtons'],
                             allow_enter=self.props['allowEnter'],
                             client=self._client, valinfo=valueinfo)
        last = self._layout.takeAt(0)
        if last:
            last.widget().deleteLater()
        self._layout.insertWidget(0, self._inner)
        self._inner.valueModified.connect(self.valueModified)
        self._inner.valueChosen.connect(self.valueChosen)

    def getValue(self):
        if self._inner:
            return self._inner.getValue()

    def setValue(self, value):
        self._reinit(value)


class DeviceParamEdit(DeviceValueEdit):

    designer_description = 'Editor for a device parameter with the right ' \
        'kind of widget'

    param = PropDef('param', str, '', 'Parameter name')

    def propertyUpdated(self, pname, value):
        if pname in ('dev', 'param'):
            self._reinit()
        NicosWidget.propertyUpdated(self, pname, value)

    def registerKeys(self):
        if self.props['dev'] and self.props['param']:
            self.registerKey(self.props['dev'] + '.' + self.props['param'])

    def on_devValueChange(self, dev, value, strvalue, unitvalue, expired):
        if self.props['updateValue']:
            self._reinit(value)

    def _reinit(self, curvalue=None):
        if not self._client:
            return
        devname = str(self.props['dev'])
        parname = str(self.props['param'])
        if devname and parname:
            pvals = self._client.getDeviceParams(devname)
            pinfo = self._client.getDeviceParamInfo(devname) or {}
            mainunit = pvals.get('unit', 'main')
            if parname not in pinfo:
                punit = ''
                valuetype = str
            else:
                punit = (pinfo[parname]['unit'] or '').replace('main', mainunit)
                valuetype = pinfo[parname]['type']
            if curvalue is None:
                curvalue = pvals.get(parname)
            if curvalue is None and valuetype is not None:
                curvalue = valuetype()
        else:
            valuetype = str
            curvalue = ''
            punit = ''
        self._inner = create(self, valuetype, curvalue, unit=punit,
                             client=self._client)
        last = self._layout.takeAt(0)
        if last:
            last.widget().deleteLater()
        self._layout.insertWidget(0, self._inner)
        self._inner.valueModified.connect(self.valueModified)


# pylint: disable=comparison-with-callable
def create(parent, typ, curvalue, fmtstr='', unit='',
           allow_buttons=False, allow_enter=True, client=None, valinfo=None):
    # make sure the type is correct
    try:
        curvalue = typ(curvalue)
    except ValueError:
        curvalue = typ()
    except TypeError:
        return MissingWidget(parent, curvalue, 'device not found')
    if unit:
        inner = create(parent, typ, curvalue, fmtstr, unit='', client=client,
                       allow_buttons=allow_buttons,
                       allow_enter=allow_enter, valinfo=valinfo)
        return AnnotatedWidget(parent, inner, unit)
    if isinstance(typ, params.oneof):
        if allow_buttons and len(typ.vals) <= 3:
            return ButtonWidget(parent, typ.vals)
        return ComboWidget(parent, typ.vals, curvalue)
    elif isinstance(typ, params.oneofdict):
        if allow_buttons and len(typ.vals) <= 3:
            return ButtonWidget(parent, list(typ.vals.values()))
        return ComboWidget(parent, list(typ.vals.values()), curvalue)
    elif isinstance(typ, params.oneofdict_or):
        inner = create(parent, typ.conv, curvalue, fmtstr, unit,
                       allow_buttons, allow_enter, client, valinfo)
        if allow_buttons and len(typ.named_vals) <= 3:
            selector = ButtonWidget(parent, typ.named_vals)
            return OneofdictOrWidget(parent, inner, selector, buttons=True)
        else:
            for (name, value) in typ.named_vals.items():
                if value == curvalue:
                    curvalue = name
                    break
            selector = ComboWidget(parent, list(typ.named_vals), curvalue,
                                   add_other=True)
            return OneofdictOrWidget(parent, inner, selector, buttons=False)
    elif isinstance(typ, params.none_or):
        return CheckWidget(parent, typ.conv, curvalue, client)
    elif isinstance(typ, params.nonzero):
        return NonzeroWidget(parent, typ.conv, curvalue, client)
    elif isinstance(typ, params.tupleof):
        return MultiWidget(parent, typ.types, curvalue, client,
                           allow_enter=allow_enter, valinfo=valinfo)
    elif isinstance(typ, params.dictwith):
        return DictWithWidget(parent, typ.convs.keys(), typ.convs.values(),
                              curvalue, client, allow_enter=allow_enter)
    elif typ == params.limits:
        return LimitsWidget(parent, curvalue, client, allow_enter=allow_enter)
    elif isinstance(typ, params.floatrange):
        edw = EditWidget(parent, float, curvalue, fmtstr or '%.4g',
                         minmax=(typ.fr, typ.to), allow_enter=allow_enter)
        annotation = '(range: %.5g to %.5g)' % (typ.fr, typ.to) \
            if typ.to is not None else '(must be >= %.5g)' % typ.fr
        return AnnotatedWidget(parent, edw, annotation)
    elif isinstance(typ, params.intrange):
        edw = SpinBoxWidget(parent, curvalue, (typ.fr, typ.to),
                            fmtstr=fmtstr or '%.4g', allow_enter=allow_enter)
        return AnnotatedWidget(parent, edw, '(range: %d to %d)' %
                               (typ.fr, typ.to))
    elif typ in (int, float, str, params.string):
        return EditWidget(parent, typ, curvalue, fmtstr or '%.4g',
                          allow_enter=allow_enter)
    elif typ in (bool, params.boolean):
        if allow_buttons:
            return ButtonWidget(parent, [True, False])
        return ComboWidget(parent, [True, False], curvalue)
    elif typ == params.vec3:
        return MultiWidget(parent, (float, float, float), curvalue, client,
                           allow_enter=allow_enter)
    elif typ == params.nicosdev:
        return DeviceComboWidget(parent, curvalue, client,
                                 allow_enter=allow_enter)
    elif typ in (params.tangodev, params.mailaddress,
                 params.ipv4, params.subdir, params.relative_path,
                 params.absolute_path):
        # XXX validate via regexp
        return EditWidget(parent, str, curvalue, allow_enter=allow_enter)
    elif isinstance(typ, params.host):
        # XXX validate via regexp
        return EditWidget(parent, str, curvalue, allow_enter=allow_enter)
    elif typ == anytype:
        return ExprWidget(parent, curvalue, allow_enter=allow_enter)
    elif isinstance(typ, params.setof):
        return SetOfWidget(parent, typ.vals, curvalue, client)
    elif isinstance(typ, params.listof):
        return ListOfWidget(parent, typ.conv, curvalue, client,
                            allow_enter=allow_enter)
    elif isinstance(typ, params.nonemptylistof):
        return ListOfWidget(parent, typ.conv, curvalue, client, nmin=1,
                            allow_enter=allow_enter)
    elif isinstance(typ, params.dictof):
        return DictOfWidget(parent, typ.keyconv, typ.valconv, curvalue,
                            client, allow_enter=allow_enter)
    elif typ == SXTalCellType:
        return TableWidget(parent, float, curvalue.rmat.T.round(10), '%.4g',
                           client, allow_enter=allow_enter)
    elif typ == list:
        if curvalue:
            ltype = type(curvalue[0])
            if all(isinstance(sub, ltype) for sub in curvalue):
                return ListOfWidget(parent, ltype, curvalue, client,
                                    allow_enter=allow_enter)
        else:
            return ListOfWidget(parent, str, curvalue, client,
                                allow_enter=allow_enter)
    return MissingWidget(parent, curvalue)


class AnnotatedWidget(QWidget):

    valueModified = pyqtSignal()
    valueChosen = pyqtSignal(object)

    def __init__(self, parent, inner, annotation):
        QWidget.__init__(self, parent)
        layout = self._layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        self._inner = inner
        self._inner.valueModified.connect(self.valueModified)
        self._inner.valueChosen.connect(self.valueChosen)
        layout.addWidget(inner)
        layout.addWidget(QLabel(annotation, parent))
        self.setLayout(layout)

    def getValue(self):
        return self._inner.getValue()

    def setFocus(self):
        self._inner.setFocus()


class MultiWidget(QWidget):

    valueModified = pyqtSignal()
    valueChosen = pyqtSignal(object)

    def __init__(self, parent, types, curvalue, client, allow_enter=False,
                 valinfo=None):
        QWidget.__init__(self, parent)
        layout = self._layout = QGridLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        self._widgets = []
        if valinfo is not None:
            for i, info in enumerate(valinfo):
                layout.addWidget(QLabel(info.name), 0, i)
        for i, (typ, val) in enumerate(zip(types, curvalue)):
            widget = create(self, typ, val, client=client,
                            allow_enter=allow_enter)
            self._widgets.append(widget)
            widget.valueModified.connect(self.valueModified)
            if allow_enter:
                widget.valueChosen.connect(
                    lambda val: self.valueChosen.emit(self.getValue()))
            layout.addWidget(widget, 1, i)
        self.setLayout(layout)

    def getValue(self):
        return tuple(w.getValue() for w in self._widgets)


class LimitsWidget(MultiWidget):

    def __init__(self, parent, curvalue, client, allow_enter=False):
        MultiWidget.__init__(self, parent, (float, float), curvalue, client,
                             allow_enter=allow_enter)
        self._layout.addWidget(QLabel('from', self), 0, 0)
        self._layout.addWidget(QLabel('to', self), 0, 1)


class DictWithWidget(QWidget):

    valueModified = pyqtSignal()
    valueChosen = pyqtSignal(object)

    def __init__(self, parent, keys, types, curvalue, client,
                 allow_enter=False):
        QWidget.__init__(self, parent)
        layout = self._layout = QFormLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        self.keys = keys
        self._widgets = []
        for (key, typ, val) in zip(keys, types, curvalue.values()):
            widget = create(self, typ, val, client=client,
                            allow_enter=allow_enter)
            self._widgets.append(widget)
            widget.valueModified.connect(self.valueModified)
            if allow_enter:
                widget.valueChosen.connect(
                    lambda val: self.valueChosen.emit(self.getValue()))
            layout.addRow(key, widget)
        self.setLayout(layout)

    def getValue(self):
        return {k: w.getValue() for k, w in zip(self.keys, self._widgets)}


class ComboWidget(QComboBox):

    valueModified = pyqtSignal()
    valueChosen = pyqtSignal(object)

    def __init__(self, parent, values, curvalue, add_other=False):
        QComboBox.__init__(self, parent)
        self._values = values
        self._textvals = list(map(str, self._values))
        self._add_other = add_other
        if add_other:
            self._values.append(Ellipsis)
            self._textvals.append('<other value>')
        self.addItems(self._textvals)
        if curvalue in self._values:
            self.setCurrentIndex(self._values.index(curvalue))
        elif add_other:
            self.setCurrentIndex(len(self._values) - 1)
        self.currentIndexChanged['int'].connect(
            lambda idx: self.valueModified.emit())

    def getValue(self):
        return self._values[self._textvals.index(self.currentText())]


class OneofdictOrWidget(QWidget):

    valueModified = pyqtSignal()
    valueChosen = pyqtSignal(object)

    def __init__(self, parent, inner, selector, buttons):
        QWidget.__init__(self, parent)
        self._inner = inner
        self._selector = selector

        layout = self._layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        inner.valueModified.connect(self.valueModified)
        inner.valueChosen.connect(self.valueChosen)
        if not buttons:
            selector.valueModified.connect(self.on_selector_valueModified)
            inner.setVisible(selector.getValue() is Ellipsis)
        else:
            selector.valueChosen.connect(self.valueChosen)
        layout.addWidget(selector)
        layout.addWidget(inner)
        self.setLayout(layout)

    def on_selector_valueModified(self):
        val = self._selector.getValue()
        self._inner.setVisible(val is Ellipsis)
        self.valueModified.emit()

    def getValue(self):
        val = self._selector.getValue()
        if val is Ellipsis:
            return self._inner.getValue()
        return val


class ButtonWidget(QWidget):

    valueModified = pyqtSignal()
    valueChosen = pyqtSignal(object)

    def __init__(self, parent, values):
        QWidget.__init__(self, parent)
        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        self._values = {}
        for value in values:
            btn = QPushButton(str(value), self)
            self._values[btn] = value
            btn.clicked.connect(self.on_button_pressed)
            layout.addWidget(btn)
        self.setLayout(layout)

    def on_button_pressed(self):
        self.valueChosen.emit(self._values[self.sender()])

    def getValue(self):
        return Ellipsis


class EditWidget(QLineEdit):

    valueModified = pyqtSignal()
    valueChosen = pyqtSignal(object)

    def __init__(self, parent, typ, curvalue, fmtstr='%.4g', minmax=None,
                 allow_enter=False):
        QLineEdit.__init__(self, parent)
        self._typ = typ
        if typ is float:
            val = DoubleValidator(self)
            if minmax:
                # setRange doesn't work correctly in some Qt versions...
                val.setBottom(minmax[0])
                if minmax[1] is not None:
                    val.setTop(minmax[1])
            self.setValidator(val)
            self.setText(fmtstr % curvalue)
        elif typ is int:
            val = QIntValidator(self)
            if minmax:
                val.setRange(minmax[0], minmax[1])
            self.setValidator(val)
            self.setText(str(curvalue))
        else:
            self.setText(str(curvalue))
        self.textChanged.connect(lambda txt: self.valueModified.emit())
        if allow_enter:
            self.returnPressed.connect(
                lambda: self.valueChosen.emit(self._typ(self.text())))

    def getValue(self):
        return self._typ(self.text())


class SpinBoxWidget(QSpinBox):

    valueModified = pyqtSignal()
    valueChosen = pyqtSignal(object)

    def __init__(self, parent, curvalue, minmax, fmtstr='%.4g',
                 allow_enter=False):
        QSpinBox.__init__(self, parent)
        self.setRange(minmax[0], minmax[1])
        self.setValue(curvalue)
        self.valueChanged['int'].connect(lambda val: self.valueModified.emit())
        if allow_enter:
            self.lineEdit().returnPressed.connect(
                lambda: self.valueChosen.emit(self.value()))

    def getValue(self):
        return self.value()


class ExprWidget(QLineEdit):

    valueModified = pyqtSignal()
    valueChosen = pyqtSignal(object)

    def __init__(self, parent, curvalue, allow_enter=False):
        QLineEdit.__init__(self, parent)
        self.setText(cache_dump(curvalue))
        self.textChanged.connect(lambda txt: self.valueModified.emit())
        if allow_enter:
            self.returnPressed.connect(
                lambda: self.valueChosen.emit(cache_load(self.text())))

    def getValue(self):
        return cache_load(self.text())


class NonzeroWidget(QWidget):

    valueModified = pyqtSignal()
    valueChosen = pyqtSignal(object)

    def __init__(self, parent, inner, curvalue, client):
        QWidget.__init__(self, parent)
        self.inner = inner
        layout = self._layout = QHBoxLayout()
        self.inner_widget = create(self, inner, curvalue, client=client)
        self.inner_widget.valueModified.connect(self.valueModified)
        layout.addWidget(self.inner_widget)
        layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)

    def getValue(self):
        return self.inner(self.inner_widget.getValue())


class CheckWidget(QWidget):

    valueModified = pyqtSignal()
    valueChosen = pyqtSignal(object)

    def __init__(self, parent, inner, curvalue, client):
        QWidget.__init__(self, parent)
        layout = self._layout = QHBoxLayout()
        self.checkbox = QCheckBox(self)
        if curvalue is not None:
            self.checkbox.setCheckState(Qt.CheckState.Checked)
        if curvalue is None:
            curvalue = inner()  # generate a dummy value
        self.inner_widget = create(self, inner, curvalue, client=client)
        self.inner_widget.setEnabled(self.checkbox.isChecked())
        self.inner_widget.valueModified.connect(self.valueModified)
        layout.addWidget(self.checkbox)
        layout.addWidget(self.inner_widget)
        layout.setContentsMargins(0, 0, 0, 0)
        self.checkbox.stateChanged.connect(self.on_checkbox_stateChanged)
        self.setLayout(layout)

    def on_checkbox_stateChanged(self, state):
        self.inner_widget.setEnabled(state == Qt.CheckState.Checked)
        self.valueModified.emit()

    def getValue(self):
        if self.checkbox.isChecked():
            return self.inner_widget.getValue()
        return None


class SetOfWidget(QWidget):

    valueModified = pyqtSignal()
    valueChosen = pyqtSignal(object)

    def __init__(self, parent, values, curvalue, client):
        QWidget.__init__(self, parent)
        layout = self._layout = QVBoxLayout()
        self.checkboxes = []
        self.values = []
        curvalue = curvalue or set()
        for value in values:
            checkbox = QCheckBox(str(value), self)
            if value in curvalue:
                checkbox.setCheckState(Qt.CheckState.Checked)
            checkbox.stateChanged.connect(self.on_checkbox_stateChanged)
            layout.addWidget(checkbox)
            self.checkboxes.append(checkbox)
            self.values.append(value)
        layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)

    def on_checkbox_stateChanged(self, state):
        self.valueModified.emit()

    def getValue(self):
        result = set()
        for value, checkbox in zip(self.values, self.checkboxes):
            if checkbox.isChecked():
                result.add(value)
        return result


class MissingWidget(QLabel):

    valueModified = pyqtSignal()
    valueChosen = pyqtSignal(object)

    def __init__(self, parent, curvalue, text='editing impossible'):
        QLabel.__init__(self, parent)
        self.setText('(%s)' % text)
        self._value = curvalue

    def getValue(self):
        return self._value


class DeviceComboWidget(QComboBox):

    valueModified = pyqtSignal()
    valueChosen = pyqtSignal(object)

    def __init__(self, parent, curvalue, client,
                 needs_class='nicos.core.device.Device',
                 allow_enter=False):
        QComboBox.__init__(self, parent, editable=True)
        self.setSizePolicy(QSizePolicy(QSizePolicy.Policy.Expanding,
                                       QSizePolicy.Policy.Fixed))
        if client:
            devs = client.getDeviceList(needs_class)
            self.addItems(devs)
            try:
                index = devs.index(curvalue)
                self.setCurrentIndex(index)
            except ValueError:
                self.setEditText(curvalue)
        else:
            self.setEditText(curvalue)
        self.editTextChanged.connect(lambda _: self.valueModified.emit())
        if allow_enter:
            self.lineEdit().returnPressed.connect(
                lambda: self.valueChosen.emit(self.currentText()))

    def getValue(self):
        return self.currentText()


class ItemsWidget(QScrollArea):

    valueModified = pyqtSignal()
    valueChosen = pyqtSignal(object)

    allow_reorder = True

    def __init__(self, parent, nmin, allow_enter=False):
        QScrollArea.__init__(self, parent)
        self.setWidgetResizable(True)
        self.frame = QFrame(self)
        self.layout = QVBoxLayout()
        self.layout.setContentsMargins(2, 2, 2, 2)
        self.addBtn = QPushButton(QIcon(':/add'), '', self.frame)
        self.addBtn.clicked.connect(self.on_addBtn_clicked)
        self.addBtn.setSizePolicy(
            QSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Preferred))
        self.layout.addWidget(self.addBtn)
        self.layout.addStretch()
        self.frame.setLayout(self.layout)
        self.setWidget(self.frame)
        self.items = []
        self.nmin = nmin
        self.allow_enter = allow_enter

    def insertItem(self, *widgets):
        item = QWidget(self.frame)
        item._widgets = widgets
        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        for widget in widgets:
            layout.addWidget(widget)
        if self.allow_reorder:
            btn = QPushButton(QIcon(':/up'), '', item)
            btn._item = item
            btn.clicked.connect(self.on_upBtn_clicked)
            layout.addWidget(btn)
            btn = QPushButton(QIcon(':/down'), '', item)
            btn._item = item
            btn.clicked.connect(self.on_downBtn_clicked)
            layout.addWidget(btn)
        btn = QPushButton(QIcon(':/remove'), '', item)
        btn._item = item
        btn.clicked.connect(self.on_removeBtn_clicked)
        layout.addWidget(btn)
        item.setLayout(layout)
        self.layout.insertWidget(self.layout.count()-2, item)
        self.items.append(item)

    def on_addBtn_clicked(self):
        self.insertItem(*self.createItem())
        self.valueModified.emit()

    def on_removeBtn_clicked(self):
        if len(self.items) <= self.nmin:
            return
        item = self.sender()._item
        index = self.items.index(item)
        del self.items[index]
        self.layout.takeAt(index).widget().deleteLater()
        self.valueModified.emit()

    def on_upBtn_clicked(self):
        item = self.sender()._item
        index = self.items.index(item)
        if index <= 0:
            return
        self._swapItems(index - 1)

    def on_downBtn_clicked(self):
        item = self.sender()._item
        index = self.items.index(item)
        if index >= len(self.items) - 1:
            return
        self._swapItems(index)

    def _swapItems(self, firstindex):
        item1 = self.items[firstindex]
        item2 = self.items[firstindex+1]
        self.layout.takeAt(firstindex)
        self.layout.takeAt(firstindex)  # moved up one
        self.items[firstindex:firstindex+2] = [item2, item1]
        self.layout.insertWidget(firstindex, item2)
        self.layout.insertWidget(firstindex+1, item1)
        self.valueModified.emit()


class ListOfWidget(ItemsWidget):

    def __init__(self, parent, inner, curvalue, client, nmin=0,
                 allow_enter=False):
        ItemsWidget.__init__(self, parent, nmin, allow_enter=allow_enter)
        self.inner = inner
        self.client = client

        for item in curvalue:
            self.insertItem(*self.createItem(item))

    def createItem(self, value=None):
        if value is None:
            value = self.inner()
        widget = create(self, self.inner, value, client=self.client,
                        allow_enter=self.allow_enter)
        widget.valueModified.connect(self.valueModified)
        widget.valueChosen.connect(
            lambda val: self.valueChosen.emit(self.getValue()))
        return (widget,)

    def getValue(self):
        return [w._widgets[0].getValue() for w in self.items]


class DictOfWidget(ItemsWidget):

    allow_reorder = False

    def __init__(self, parent, keytype, valtype, curvalue, client, nmin=0,
                 allow_enter=False):
        ItemsWidget.__init__(self, parent, nmin, allow_enter=allow_enter)
        self.keytype = keytype
        self.valtype = valtype
        self.client = client

        for keyval in curvalue.items():
            self.insertItem(*self.createItem(keyval))

    def createItem(self, keyval=None):
        if keyval is None:
            key = self.keytype()
            val = self.valtype()
        else:
            key, val = keyval
        keywidget = create(self, self.keytype, key, client=self.client,
                           allow_enter=self.allow_enter)
        keywidget.valueModified.connect(self.valueModified)
        keywidget.valueChosen.connect(
            lambda val: self.valueChosen.emit(self.getValue()))
        valwidget = create(self, self.valtype, val, client=self.client,
                           allow_enter=self.allow_enter)
        valwidget.valueModified.connect(self.valueModified)
        valwidget.valueChosen.connect(
            lambda val: self.valueChosen.emit(self.getValue()))
        return (keywidget, QLabel('=>', self), valwidget)

    def getValue(self):
        return {w._widgets[0].getValue(): w._widgets[2].getValue()
                for w in self.items}


class TableWidget(QTableWidget):

    valueModified = pyqtSignal()
    valueChosen = pyqtSignal(object)

    def __init__(self, parent, validator, curvalue, fmtstr, client,
                 allow_enter=False):
        self._rows, self._cols = curvalue.shape
        self.validator = validator
        QTableWidget.__init__(self, self._rows, self._cols, parent)
        for i in range(self._rows):
            for j in range(self._cols):
                self.setItem(i, j, QTableWidgetItem(fmtstr % curvalue[i, j]))
        self.cellChanged.connect(lambda i, j: self.valueModified.emit())

    def getValue(self):
        value = np.zeros((self._rows, self._cols))
        for i in range(self._rows):
            for j in range(self._cols):
                value[i, j] = self.validator(self.item(i, j).text())
        return value
