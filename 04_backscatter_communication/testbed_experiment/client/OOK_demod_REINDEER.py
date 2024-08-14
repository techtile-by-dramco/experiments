#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#
# SPDX-License-Identifier: GPL-3.0
#
# GNU Radio Python Flow Graph
# Title: OOK_demod_REINDEER
# Author: BertCox
# GNU Radio version: v3.8.2.0-57-gd71cd177

from distutils.version import StrictVersion

if __name__ == '__main__':
    import ctypes
    import sys
    if sys.platform.startswith('linux'):
        try:
            x11 = ctypes.cdll.LoadLibrary('libX11.so')
            x11.XInitThreads()
        except:
            print("Warning: failed to XInitThreads()")

from PyQt5 import Qt
from gnuradio import qtgui
from gnuradio.filter import firdes
import sip
from gnuradio import analog
from gnuradio import blocks
from gnuradio import digital
from gnuradio import filter
from gnuradio import gr
import sys
import signal
from argparse import ArgumentParser
from gnuradio.eng_arg import eng_float, intx
from gnuradio import eng_notation
from gnuradio import uhd
import time
import threading

from gnuradio import qtgui

class OOK_demod_REINDEER(gr.top_block, Qt.QWidget):

    def __init__(self):
        gr.top_block.__init__(self, "OOK_demod_REINDEER")
        Qt.QWidget.__init__(self)
        self.setWindowTitle("OOK_demod_REINDEER")
        qtgui.util.check_set_qss()
        try:
            self.setWindowIcon(Qt.QIcon.fromTheme('gnuradio-grc'))
        except:
            pass
        self.top_scroll_layout = Qt.QVBoxLayout()
        self.setLayout(self.top_scroll_layout)
        self.top_scroll = Qt.QScrollArea()
        self.top_scroll.setFrameStyle(Qt.QFrame.NoFrame)
        self.top_scroll_layout.addWidget(self.top_scroll)
        self.top_scroll.setWidgetResizable(True)
        self.top_widget = Qt.QWidget()
        self.top_scroll.setWidget(self.top_widget)
        self.top_layout = Qt.QVBoxLayout(self.top_widget)
        self.top_grid_layout = Qt.QGridLayout()
        self.top_layout.addLayout(self.top_grid_layout)

        self.settings = Qt.QSettings("GNU Radio", "OOK_demod_REINDEER")

        try:
            if StrictVersion(Qt.qVersion()) < StrictVersion("5.0.0"):
                self.restoreGeometry(self.settings.value("geometry").toByteArray())
            else:
                self.restoreGeometry(self.settings.value("geometry"))
        except:
            pass

        ##################################################
        # Variables
        ##################################################
        self.transition_width = transition_width = 20e3
        self.samp_rate = samp_rate = 2000000
        self.cutoff_freq = cutoff_freq = 50e3
        self.symbol_rate = symbol_rate = 2000
        self.squelch_treshold = squelch_treshold = -54
        self.samp_rate_divider = samp_rate_divider = 10
        self.moving_average_function_probe = moving_average_function_probe = 0
        self.lowpass_filter = lowpass_filter = firdes.low_pass(1, samp_rate, cutoff_freq, transition_width, firdes.WIN_HAMMING, 6.76)
        self.freq_offset = freq_offset = 512000
        self.freq = freq = 917E6
        self.decimation = decimation = 1

        ##################################################
        # Blocks
        ##################################################
        self.moving_average_probe = blocks.probe_signal_f()
        def _moving_average_function_probe_probe():
            while True:

                val = self.moving_average_probe.level()
                try:
                    self.set_moving_average_function_probe(val)
                except AttributeError:
                    pass
                time.sleep(1.0 / (1))
        _moving_average_function_probe_thread = threading.Thread(target=_moving_average_function_probe_probe)
        _moving_average_function_probe_thread.daemon = True
        _moving_average_function_probe_thread.start()

        self.uhd_usrp_source_0 = uhd.usrp_source(
            ",".join(("", '')),
            uhd.stream_args(
                cpu_format="fc32",
                args='',
                channels=list(range(0,1)),
            ),
        )
        self.uhd_usrp_source_0.set_center_freq(freq, 0)
        self.uhd_usrp_source_0.set_rx_agc(False, 0)
        self.uhd_usrp_source_0.set_gain(20, 0)
        self.uhd_usrp_source_0.set_antenna("RX2", 0)
        self.uhd_usrp_source_0.set_samp_rate(samp_rate)
        # No synchronization enforced.
        self.qtgui_time_sink_x_0_1_0_0_0_1 = qtgui.time_sink_f(
            1000, #size
            1000, #samp_rate
            'Symbol_sync', #name
            1 #number of inputs
        )
        self.qtgui_time_sink_x_0_1_0_0_0_1.set_update_time(0.10)
        self.qtgui_time_sink_x_0_1_0_0_0_1.set_y_axis(-1, 1)

        self.qtgui_time_sink_x_0_1_0_0_0_1.set_y_label('Amplitude', "")

        self.qtgui_time_sink_x_0_1_0_0_0_1.enable_tags(True)
        self.qtgui_time_sink_x_0_1_0_0_0_1.set_trigger_mode(qtgui.TRIG_MODE_FREE, qtgui.TRIG_SLOPE_POS, 0.0, 0, 0, "")
        self.qtgui_time_sink_x_0_1_0_0_0_1.enable_autoscale(True)
        self.qtgui_time_sink_x_0_1_0_0_0_1.enable_grid(False)
        self.qtgui_time_sink_x_0_1_0_0_0_1.enable_axis_labels(True)
        self.qtgui_time_sink_x_0_1_0_0_0_1.enable_control_panel(False)
        self.qtgui_time_sink_x_0_1_0_0_0_1.enable_stem_plot(False)


        labels = ['Signal 1', 'Signal 2', 'Signal 3', 'Signal 4', 'Signal 5',
            'Signal 6', 'Signal 7', 'Signal 8', 'Signal 9', 'Signal 10']
        widths = [1, 1, 1, 1, 1,
            1, 1, 1, 1, 1]
        colors = ['blue', 'red', 'green', 'black', 'cyan',
            'magenta', 'yellow', 'dark red', 'dark green', 'dark blue']
        alphas = [1.0, 1.0, 1.0, 1.0, 1.0,
            1.0, 1.0, 1.0, 1.0, 1.0]
        styles = [1, 1, 1, 1, 1,
            1, 1, 1, 1, 1]
        markers = [-1, -1, -1, -1, -1,
            -1, -1, -1, -1, -1]


        for i in range(1):
            if len(labels[i]) == 0:
                self.qtgui_time_sink_x_0_1_0_0_0_1.set_line_label(i, "Data {0}".format(i))
            else:
                self.qtgui_time_sink_x_0_1_0_0_0_1.set_line_label(i, labels[i])
            self.qtgui_time_sink_x_0_1_0_0_0_1.set_line_width(i, widths[i])
            self.qtgui_time_sink_x_0_1_0_0_0_1.set_line_color(i, colors[i])
            self.qtgui_time_sink_x_0_1_0_0_0_1.set_line_style(i, styles[i])
            self.qtgui_time_sink_x_0_1_0_0_0_1.set_line_marker(i, markers[i])
            self.qtgui_time_sink_x_0_1_0_0_0_1.set_line_alpha(i, alphas[i])

        self._qtgui_time_sink_x_0_1_0_0_0_1_win = sip.wrapinstance(self.qtgui_time_sink_x_0_1_0_0_0_1.pyqwidget(), Qt.QWidget)
        self.top_grid_layout.addWidget(self._qtgui_time_sink_x_0_1_0_0_0_1_win)
        self.low_pass_filter_0 = filter.fir_filter_fff(
            1,
            firdes.low_pass(
                1,
                samp_rate,
                8000,
                10000,
                firdes.WIN_HAMMING,
                6.76))
        self.freq_xlating_fir_filter_lp = filter.freq_xlating_fir_filter_ccc(decimation, lowpass_filter, freq_offset, samp_rate)
        self.digital_symbol_sync_xx_0 = digital.symbol_sync_ff(
            digital.TED_GARDNER,
            2000,
            0.045,
            1.0,
            0.1,
            1.0,
            1,
            digital.constellation_bpsk().base(),
            digital.IR_PFB_NO_MF,
            256,
            [])
        self.blocks_threshold_ff_0_0 = blocks.threshold_ff(0, 0.01, 0)
        self.blocks_threshold_ff_0 = blocks.threshold_ff(moving_average_function_probe*0.5, moving_average_function_probe*1.5, 1)
        self.blocks_moving_average_xx_0 = blocks.moving_average_ff(int(samp_rate/samp_rate_divider), samp_rate_divider/samp_rate, int(samp_rate/samp_rate_divider), 1)
        self.blocks_complex_to_mag_squared_1 = blocks.complex_to_mag_squared(1)
        self.blocks_add_const_vxx_0 = blocks.add_const_ff(-0.5)
        self.analog_pwr_squelch_xx_0_0 = analog.pwr_squelch_ff(squelch_treshold, 1e-4, 0, True)
        self.analog_agc2_xx_1 = analog.agc2_ff(0.001, 0.01, 1.0, 1.0)
        self.analog_agc2_xx_1.set_max_gain(0)



        ##################################################
        # Connections
        ##################################################
        self.connect((self.analog_agc2_xx_1, 0), (self.low_pass_filter_0, 0))
        self.connect((self.analog_pwr_squelch_xx_0_0, 0), (self.blocks_moving_average_xx_0, 0))
        self.connect((self.blocks_add_const_vxx_0, 0), (self.digital_symbol_sync_xx_0, 0))
        self.connect((self.blocks_complex_to_mag_squared_1, 0), (self.analog_agc2_xx_1, 0))
        self.connect((self.blocks_moving_average_xx_0, 0), (self.moving_average_probe, 0))
        self.connect((self.blocks_threshold_ff_0, 0), (self.blocks_add_const_vxx_0, 0))
        self.connect((self.blocks_threshold_ff_0_0, 0), (self.qtgui_time_sink_x_0_1_0_0_0_1, 0))
        self.connect((self.digital_symbol_sync_xx_0, 0), (self.blocks_threshold_ff_0_0, 0))
        self.connect((self.freq_xlating_fir_filter_lp, 0), (self.blocks_complex_to_mag_squared_1, 0))
        self.connect((self.low_pass_filter_0, 0), (self.analog_pwr_squelch_xx_0_0, 0))
        self.connect((self.low_pass_filter_0, 0), (self.blocks_threshold_ff_0, 0))
        self.connect((self.uhd_usrp_source_0, 0), (self.freq_xlating_fir_filter_lp, 0))


    def closeEvent(self, event):
        self.settings = Qt.QSettings("GNU Radio", "OOK_demod_REINDEER")
        self.settings.setValue("geometry", self.saveGeometry())
        event.accept()

    def get_transition_width(self):
        return self.transition_width

    def set_transition_width(self, transition_width):
        self.transition_width = transition_width
        self.set_lowpass_filter(firdes.low_pass(1, self.samp_rate, self.cutoff_freq, self.transition_width, firdes.WIN_HAMMING, 6.76))

    def get_samp_rate(self):
        return self.samp_rate

    def set_samp_rate(self, samp_rate):
        self.samp_rate = samp_rate
        self.set_lowpass_filter(firdes.low_pass(1, self.samp_rate, self.cutoff_freq, self.transition_width, firdes.WIN_HAMMING, 6.76))
        self.blocks_moving_average_xx_0.set_length_and_scale(int(self.samp_rate/self.samp_rate_divider), self.samp_rate_divider/self.samp_rate)
        self.low_pass_filter_0.set_taps(firdes.low_pass(1, self.samp_rate, 8000, 10000, firdes.WIN_HAMMING, 6.76))
        self.uhd_usrp_source_0.set_samp_rate(self.samp_rate)

    def get_cutoff_freq(self):
        return self.cutoff_freq

    def set_cutoff_freq(self, cutoff_freq):
        self.cutoff_freq = cutoff_freq
        self.set_lowpass_filter(firdes.low_pass(1, self.samp_rate, self.cutoff_freq, self.transition_width, firdes.WIN_HAMMING, 6.76))

    def get_symbol_rate(self):
        return self.symbol_rate

    def set_symbol_rate(self, symbol_rate):
        self.symbol_rate = symbol_rate

    def get_squelch_treshold(self):
        return self.squelch_treshold

    def set_squelch_treshold(self, squelch_treshold):
        self.squelch_treshold = squelch_treshold
        self.analog_pwr_squelch_xx_0_0.set_threshold(self.squelch_treshold)

    def get_samp_rate_divider(self):
        return self.samp_rate_divider

    def set_samp_rate_divider(self, samp_rate_divider):
        self.samp_rate_divider = samp_rate_divider
        self.blocks_moving_average_xx_0.set_length_and_scale(int(self.samp_rate/self.samp_rate_divider), self.samp_rate_divider/self.samp_rate)

    def get_moving_average_function_probe(self):
        return self.moving_average_function_probe

    def set_moving_average_function_probe(self, moving_average_function_probe):
        self.moving_average_function_probe = moving_average_function_probe
        self.blocks_threshold_ff_0.set_hi(self.moving_average_function_probe*1.5)
        self.blocks_threshold_ff_0.set_lo(self.moving_average_function_probe*0.5)

    def get_lowpass_filter(self):
        return self.lowpass_filter

    def set_lowpass_filter(self, lowpass_filter):
        self.lowpass_filter = lowpass_filter
        self.freq_xlating_fir_filter_lp.set_taps(self.lowpass_filter)

    def get_freq_offset(self):
        return self.freq_offset

    def set_freq_offset(self, freq_offset):
        self.freq_offset = freq_offset
        self.freq_xlating_fir_filter_lp.set_center_freq(self.freq_offset)

    def get_freq(self):
        return self.freq

    def set_freq(self, freq):
        self.freq = freq
        self.uhd_usrp_source_0.set_center_freq(self.freq, 0)

    def get_decimation(self):
        return self.decimation

    def set_decimation(self, decimation):
        self.decimation = decimation





def main(top_block_cls=OOK_demod_REINDEER, options=None):

    if StrictVersion("4.5.0") <= StrictVersion(Qt.qVersion()) < StrictVersion("5.0.0"):
        style = gr.prefs().get_string('qtgui', 'style', 'raster')
        Qt.QApplication.setGraphicsSystem(style)
    qapp = Qt.QApplication(sys.argv)

    tb = top_block_cls()

    tb.start()

    tb.show()

    def sig_handler(sig=None, frame=None):
        Qt.QApplication.quit()

    signal.signal(signal.SIGINT, sig_handler)
    signal.signal(signal.SIGTERM, sig_handler)

    timer = Qt.QTimer()
    timer.start(500)
    timer.timeout.connect(lambda: None)

    def quitting():
        tb.stop()
        tb.wait()

    qapp.aboutToQuit.connect(quitting)
    qapp.exec_()

if __name__ == '__main__':
    main()
