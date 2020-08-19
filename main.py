from wx import *
from wx.media import MediaCtrl, MEDIABACKEND_WMP10, EVT_MEDIA_LOADED, EVT_MEDIA_STATECHANGED, MEDIASTATE_PLAYING, \
    MEDIASTATE_PAUSED, MEDIASTATE_STOPPED
import os


class MyCallLater(CallLater):
    def __del__(self):
        print('MyCallLater.__del__ called!')


h = 0


def hhmmss(ms):
    global h
    total = ms / 1000
    if total > 3600:
        total_time = total % 3600
        h = total // 3600
    else:
        total_time = total
    minute = total_time // 60
    sec = total_time % 60
    if total > 3600:
        return "%02d:%02d:%02d" % (h, minute, sec)
    else:
        return "%02d:%02d" % (minute, sec)


def on_key(event):
    key = event.GetKeyCode()
    if key == 15:
        my_app.open_files_main()
    elif key == 32:
        my_app.play_media()
    elif key == 98:
        my_app.seek(5000)
    elif key == 118:
        my_app.seek(-5000)
    elif key == 2:
        my_app.seek(60000)
    elif key == 22:
        my_app.seek(-60000)
    elif key == 102:
        my_app.switch_fullscreen()
    elif key == 110:
        my_app.playlist.next()
    elif key == 112:
        my_app.playlist.prev()
    elif key == 109:
        my_app.switch_maximize()
    elif key == WXK_MEDIA_PLAY_PAUSE:
        my_app.play_media()
    elif key == WXK_MEDIA_NEXT_TRACK:
        my_app.playlist.next()
    elif key == WXK_MEDIA_PREV_TRACK:
        my_app.playlist.prev()
    event.Skip()


# custom MediaCtrl Widget
class CustomMediaCtrl(MediaCtrl):

    def __init__(self, parent, key, backend):
        MediaCtrl.__init__(self, parent, key, szBackend=backend)

        self.Bind(EVT_CHAR, on_key)

    def set_focus(self):
        self.SetFocus()


# custom Slider
class VideoSlider(Slider):
    def __init__(self, *args, **kwargs):
        Slider.__init__(self, *args, **kwargs, style=SL_BOTH | SL_SELRANGE)
        self.Bind(EVT_LEFT_DOWN, self.on_click)

    def on_click(self, e):
        max_position = self.GetSize()[0]
        clicked_position = e.GetX()
        my_app.pseudo_label.SetFocus()
        my_app.set_seek(max_position, clicked_position)
        e.Skip()


class PlaylistModel:
    def __init__(self):
        self.current = 0
        self.playlist = []

    def get_len(self):
        return len(self.playlist)

    def set_current(self, val):
        self.current = val
        self.load_media()

    def is_empty(self):
        if self.get_len() == 0:
            return True
        else:
            return False

    def set_current_index(self, index):
        self.current = index

    def current_media(self):
        return self.playlist[self.current]

    def check_next(self):
        if self.current < self.get_len() - 1:
            return True
        else:
            return False

    def check_prev(self):
        if self.current > 0:
            return True
        else:
            return False

    def next(self):
        current = self.current
        if current < self.get_len() - 1:
            self.set_current(current + 1)

    def prev(self):
        current = self.current
        if current > 0:
            self.set_current(current - 1)

    def add_media(self, path):
        self.playlist.append(path)

    def load_media(self):
        my_app.mediaPlayer.Load(self.current_media())


# Main Gui Frame
class Application(Frame):
    def __init__(self, parent, title):
        super(Application, self).__init__(parent, title=title, size=(650, 450))
        self.Center()
        self.panel = Panel(self)
        self.panel.SetFocus()

        # timer
        self.timer = Timer(self, 1)
        self.timer.Start(500)

        # Player
        self.mediaPlayer = CustomMediaCtrl(self.panel, 1, MEDIABACKEND_WMP10)

        # PlayLists
        self.playlist = PlaylistModel()

        # Slider Labels
        self.currentTimeLabel = StaticText(self.panel, label='00:00')
        self.totalTimeLabel = StaticText(self.panel, label='00:00')

        # Sliders
        self.videoSlider = VideoSlider(self.panel)
        self.volumeSlider = Slider(self.panel)

        # Buttons
        self.open_btn = Button(self.panel, -1, 'open file')
        self.play_btn = BitmapButton(self.panel, -1, Bitmap("bitmaps/play.png"), style=BORDER_NONE)
        self.prev_btn = BitmapButton(self.panel, -1, Bitmap("bitmaps/prev.png"), style=BORDER_NONE)
        self.stop_btn = BitmapButton(self.panel, -1, Bitmap("bitmaps/stop.png"), style=BORDER_NONE)
        self.next_btn = BitmapButton(self.panel, -1, Bitmap("bitmaps/next.png"), style=BORDER_NONE)

        # Speaker Icon
        self.speaker_label = StaticBitmap(self.panel, -1, Bitmap("bitmaps/speaker-volume.png"))

        # Optional label(Just for set align purpose)
        self.pseudo_label = StaticText(self.panel, label='')

        # Arrange Layouts

        # BoxSizer for current_time, video_slider and total_time
        video_slider_box = BoxSizer(HORIZONTAL)
        video_slider_box.Add(self.currentTimeLabel, 0, LEFT, 20)
        video_slider_box.Add(self.videoSlider, 1, EXPAND | LEFT | RIGHT, 8)
        video_slider_box.Add(self.totalTimeLabel, 0, RIGHT, 20)

        # Layout for prev, stop and next button
        prev_stop_next_box = BoxSizer(HORIZONTAL)
        prev_stop_next_box.Add(self.prev_btn, 0, LEFT, 5)
        prev_stop_next_box.Add(self.stop_btn, 0, LEFT, 5)
        prev_stop_next_box.Add(self.next_btn, 0, LEFT, 5)

        # Layout for volumes widgets
        volume_box = BoxSizer(HORIZONTAL)
        volume_box.Add(self.speaker_label, 0, TOP, 5)
        volume_box.Add(self.volumeSlider)

        # Layout for open_btn, play_btn and for layouts(prev_stop_next_box, volume_box)
        bottom_box = BoxSizer(HORIZONTAL)
        bottom_box.Add(self.open_btn, 0, LEFT, 5)
        bottom_box.Add(self.play_btn, 0, LEFT, 20)
        bottom_box.Add(prev_stop_next_box, 0, LEFT | RIGHT, 20)
        bottom_box.Add(self.pseudo_label, 1, EXPAND)
        bottom_box.Add(volume_box, 0)

        # Main BoxSizer Which hold all widgets and layouts
        main_box = BoxSizer(VERTICAL)
        main_box.Add(self.mediaPlayer, 1, EXPAND | ALL)
        main_box.Add(video_slider_box, 0, EXPAND | ALL, 3)
        main_box.Add(bottom_box, 0, EXPAND | LEFT | RIGHT | BOTTOM, 3)

        # SetColors

        self.panel.SetBackgroundColour("#272727")
        self.open_btn.SetBackgroundColour("#636363")
        self.play_btn.SetBackgroundColour("#272727")
        self.prev_btn.SetBackgroundColour("#272727")
        self.stop_btn.SetBackgroundColour("#272727")
        self.next_btn.SetBackgroundColour("#272727")

        self.currentTimeLabel.SetForegroundColour((255, 255, 255))
        self.totalTimeLabel.SetForegroundColour((255, 255, 255))

        # SetSizer Main BoxSizer in Panel
        self.panel.SetSizer(main_box)

        # Bind Buttons with functions
        self.open_btn.Bind(EVT_BUTTON, self.open_files)
        self.play_btn.Bind(EVT_BUTTON, self.play)
        self.next_btn.Bind(EVT_BUTTON, self.next_media)
        self.stop_btn.Bind(EVT_BUTTON, self.stop_media)
        self.prev_btn.Bind(EVT_BUTTON, self.prev_media)
        self.mediaPlayer.Bind(EVT_MEDIA_STATECHANGED, self.media_state)
        self.mediaPlayer.Bind(EVT_MEDIA_LOADED, self.play)
        self.Bind(EVT_TIMER, self.update_position)
        self.volumeSlider.Bind(EVT_SLIDER, self.volume_ctrl)

        # UI Handler (disable and enable Widgets)
        self.ui_handler()

        # set Volume slider
        self.volumeSlider.SetMax(20)
        self.volumeSlider.SetValue(20)

    def next_media(self, e):
        self.playlist.next()

    def prev_media(self, e):
        self.playlist.prev()

    def open_files(self, e):
        self.open_files_main()

    def open_files_main(self):
        filter_file = "Media (*.mp4,*.mkv,*.mp3)|*.mp4;*.mkv;*.mp3"
        dialog = FileDialog(self.panel, "Open", wildcard=filter_file, style=FD_MULTIPLE)
        if dialog.ShowModal() == ID_OK:
            paths = dialog.GetPaths()
            for path in paths:
                self.playlist.add_media(path)
            if self.mediaPlayer.GetState() != MEDIASTATE_PLAYING:
                self.playlist.load_media()
        self.ui_handler()

    def stop_media(self, event):
        self.stop_media_main()

    def stop_media_main(self):
        player = self.mediaPlayer
        state = player.GetState()
        if state != MEDIASTATE_STOPPED:
            player.Stop()
            my_app.SetLabel("Media Player")
            self.totalTimeLabel.SetLabel('00:00')
            self.currentTimeLabel.SetLabel('00:00')

    def play(self, event):
        self.play_media()

    def play_media(self):
        player = self.mediaPlayer
        state = player.GetState()
        if state == MEDIASTATE_PLAYING:
            player.Pause()
        elif state == MEDIASTATE_PAUSED or state == MEDIASTATE_STOPPED:
            player.Play()

    def media_state(self, event):
        player = self.mediaPlayer
        state = player.GetState()
        if state == MEDIASTATE_PLAYING:
            self.play_btn.SetBitmap(Bitmap("bitmaps/pause.png"))
            path, filename = os.path.split(self.playlist.current_media())
            media_length = self.mediaPlayer.Length()
            self.videoSlider.SetMax(media_length)
            self.totalTimeLabel.SetLabel(hhmmss(media_length))
            self.ui_handler()
            my_app.SetLabel(filename + " - Media Player")
        elif state == MEDIASTATE_PAUSED or state == MEDIASTATE_STOPPED:
            self.play_btn.SetBitmap(Bitmap("bitmaps/play.png"))

    def ui_handler(self):
        playlist = self.playlist
        if playlist.is_empty():
            self.play_btn.Disable()
            self.prev_btn.Disable()
            self.stop_btn.Disable()
            self.next_btn.Disable()
        else:
            self.play_btn.Enable()
            if not playlist.check_prev():
                self.prev_btn.Disable()
            else:
                self.prev_btn.Enable()
            if not playlist.check_next():
                self.next_btn.Disable()
            else:
                self.next_btn.Enable()

    def set_seek(self, max_pos, clicked_pos):
        player = self.mediaPlayer
        media_length = player.Length()
        seek_val = int((media_length / max_pos) * clicked_pos)
        player.Seek(seek_val)
        player.Play()

    def seek(self, val):
        player = self.mediaPlayer
        player.Seek(val, FromCurrent)
        player.Play()

    def update_position(self, e):
        player = self.mediaPlayer
        player.set_focus()
        offset = player.Tell()
        length = player.Length()
        if offset > (length - 700) & player.Length() > 0:
            self.auto_next()
        self.videoSlider.SetValue(offset)
        if offset == 0:
            self.stop_btn.Disable()
        if offset > 0:
            self.stop_btn.Enable()
            self.currentTimeLabel.SetLabel(hhmmss(offset))

    def auto_next(self):
        playlist = self.playlist
        if not playlist.is_empty():
            if playlist.check_next():
                playlist.next()
            else:
                playlist.set_current(0)
                self.stop_media_main()

    def video_slider_ctrl(self, e):
        self.mediaPlayer.Seek(self.videoSlider.GetValue())

    def switch_maximize(self):
        if self.IsMaximized():
            self.Maximize(False)
        else:
            self.Maximize(True)

    def switch_fullscreen(self):
        if self.IsFullScreen():
            self.currentTimeLabel.Show()
            self.videoSlider.Show()
            self.totalTimeLabel.Show()
            self.open_btn.Show()
            self.play_btn.Show()
            self.prev_btn.Show()
            self.stop_btn.Show()
            self.next_btn.Show()
            self.pseudo_label.Show()
            self.speaker_label.Show()
            self.volumeSlider.Show()
            self.ShowFullScreen(False)
        else:
            self.currentTimeLabel.Hide()
            self.videoSlider.Hide()
            self.totalTimeLabel.Hide()
            self.open_btn.Hide()
            self.play_btn.Hide()
            self.prev_btn.Hide()
            self.stop_btn.Hide()
            self.next_btn.Hide()
            self.pseudo_label.Hide()
            self.speaker_label.Hide()
            self.volumeSlider.Hide()
            self.ShowFullScreen(True)

    def volume_up(self, event):
        vol = self.volumeSlider
        if vol.GetValue() < 20:
            val1 = vol.GetValue() + 1
            self.mediaPlayer.SetVolume(val1 / 20)
            vol.SetValue(val1)

    def volume_down(self, event):
        vol = self.volumeSlider
        if vol.GetValue() > 0:
            val1 = vol.GetValue() - 1
            self.mediaPlayer.SetVolume(val1 / 20)
            vol.SetValue(val1)

    def volume_ctrl(self, event):
        vol = self.volumeSlider
        if vol.GetValue() < 20:
            val1 = vol.GetValue()
            self.mediaPlayer.SetVolume(val1 / 20)
        else:
            self.mediaPlayer.SetVolume(1.0)


app = App()
my_app = Application(None, "Media Player")
my_app.Show()
app.MainLoop()
