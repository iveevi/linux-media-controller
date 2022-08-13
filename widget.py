import subprocess
import sys

from pathlib import Path

from PyQt5 import QtCore, QtGui, QtWidgets

from PyQt5.QtWidgets import QApplication
from PyQt5.QtWidgets import QHBoxLayout
from PyQt5.QtWidgets import QLabel
from PyQt5.QtWidgets import QVBoxLayout
from PyQt5.QtWidgets import QWidget
from PyQt5.QtWidgets import QFrame

from PyQt5.QtGui import QPixmap

app = QApplication(sys.argv)

# TODO: skip the script step

# Commands
next_cmd       = 'playerctl -p spotify next'
play_pause_cmd = 'playerctl -p spotify play-pause'
prev_cmd       = 'playerctl -p spotify previous'
repeat_cmd     = 'playerctl -p spotify loop'
script_cmd     = './media_status.sh'
shuffle_cmd    = 'playerctl -p spotify shuffle'
status_cmd     = 'playerctl -p spotify status'

def do_cmd(cmd):
    ret = ''
    try:
        ret = subprocess \
            .check_output(cmd, shell=True, timeout=1) \
            .decode('utf-8').strip()
    except subprocess.CalledProcessError as e:
        ret = '?'
    except subprocess.TimeoutExpired as e:
        ret = '?'

    return ret

# Paths
image_path = str(Path.home()) + '/.cache/media_album_cover'

play_icon            = QtGui.QIcon('./icons/media-playback-start.svg')
pause_icon           = QtGui.QIcon('./icons/media-playback-pause.svg')
next_icon            = QtGui.QIcon('./icons/media-skip-forward.svg')
prev_icon            = QtGui.QIcon('./icons/media-skip-backward.svg')
shuffle_icon         = QtGui.QIcon('./icons/media-playlist-shuffle.svg')
repeat_off_icon      = QtGui.QIcon('./icons/media-playlist-repeat.svg')
repeat_track_icon    = QtGui.QIcon('./icons/media-playlist-repeat-track.svg')
repeat_playlist_icon = QtGui.QIcon('./icons/media-playlist-repeat.svg')
spotify_icon         = QtGui.QIcon('./images/spotify_logo.png')
chrome_icon          = QtGui.QIcon('./images/chrome_logo.png')

def get_shuffle_status():
    status = do_cmd(shuffle_cmd)
    return status == 'On'

def get_repeat_status():
    status = do_cmd(repeat_cmd)
    return status

def get_repeat_icon():
    status = get_repeat_status()
    if status == 'None':
        return repeat_off_icon
    elif status == 'Track':
        return repeat_track_icon
    elif status == 'Playlist':
        return repeat_playlist_icon

    return repeat_off_icon

# Seconds to minute:second format
def format_time(seconds):
    minutes = seconds // 60
    seconds = seconds % 60
    return '{:02d}:{:02d}'.format(minutes, seconds)

# Widget
class MediaWidget(QWidget):
    def __init__(self):
        super().__init__()

        # Initialize the widget
        media_status = subprocess \
            .check_output(script_cmd, shell=False) \
            .decode('utf-8') \
            .split(':')

        artist = media_status[0]
        title = media_status[1]
        album = media_status[2]

        total_time = media_status[3]
        current_time = media_status[4]

        # Font family
        font_family = 'Gotham'

        # Song progress
        self.song_progress_layout = QHBoxLayout()

        self.song_progress = QFrame(self)
        self.song_progress.setLayout(self.song_progress_layout)

        self.total_time = QLabel(format_time(int(total_time)))
        self.current_time = QLabel(format_time(int(current_time)))

        time_style_sheet = f'''
            font-family: {font_family};
            font-size: 12px;
            color: #fff;
        '''

        self.total_time.setStyleSheet(time_style_sheet)
        self.current_time.setStyleSheet(time_style_sheet)

        self.progress = QtWidgets.QProgressBar(self)
        self.progress.setValue(int(current_time))
        self.progress.setMaximum(int(total_time))
        self.progress.setTextVisible(False)

        # Make the progress bar look like a slider
        self.progress.setStyleSheet('''
            QProgressBar {
                border: 0px;
                border-radius: 2px;
                background: #aaa;
                height: 5px;
                width: 20px;
            }

            QProgressBar::chunk {
                border: 0px;
                border-radius: 2px;
                background: #00ff73;
            }
        ''')

        self.progress.setFixedWidth(200)
        self.progress.setFixedHeight(5)

        self.song_progress_layout.addWidget(self.current_time)
        self.song_progress_layout.addWidget(self.progress)
        self.song_progress_layout.addWidget(self.total_time)

        # Media control
        self.media_control_layout = QHBoxLayout()

        self.media_control = QFrame(self)
        self.media_control.setLayout(self.media_control_layout)

        self.play_pause_button = QtWidgets.QPushButton('', self)
        self.shuffle_button = QtWidgets.QPushButton('', self)
        self.repeat_button = QtWidgets.QPushButton('', self)
        self.prev_button = QtWidgets.QPushButton('', self)
        self.next_button = QtWidgets.QPushButton('', self)

        button_style_sheet = '''
            QPushButton {
                border: none;
                background-color: transparent;
                padding: 5px;
                border-radius: 2px;
            }

            QPushButton:hover {
                background-color: grey;
            }
        '''

        self.play_pause_button.setStyleSheet(button_style_sheet)
        self.shuffle_button.setStyleSheet(button_style_sheet)
        self.repeat_button.setStyleSheet(button_style_sheet)
        self.prev_button.setStyleSheet(button_style_sheet)
        self.next_button.setStyleSheet(button_style_sheet)

        # Icons
        status = do_cmd(status_cmd)
        if status == 'Playing':
            self.play_pause_button.setIcon(pause_icon)
        else:
            self.play_pause_button.setIcon(play_icon)

        self.prev_button.setIcon(prev_icon)
        self.next_button.setIcon(next_icon)
        self.shuffle_button.setIcon(shuffle_icon)
        self.repeat_button.setIcon(get_repeat_icon())

        # Connect
        self.play_pause_button.clicked.connect(self.play_pause_button_clicked)
        self.prev_button.clicked.connect(self.prev_button_clicked)
        self.next_button.clicked.connect(self.next_button_clicked)

        # Layout
        self.media_control_layout.addWidget(self.shuffle_button)
        self.media_control_layout.addWidget(self.prev_button)
        self.media_control_layout.addWidget(self.play_pause_button)
        self.media_control_layout.addWidget(self.next_button)
        self.media_control_layout.addWidget(self.repeat_button)

        # Song info
        self.song_info_layout = QVBoxLayout(self)

        self.song_info = QFrame(self)
        self.song_info.setLayout(self.song_info_layout)

        self.artist = QLabel(artist)
        self.title = QLabel(title)
        self.album = QLabel(album)

        self.artist.setAlignment(QtCore.Qt.AlignCenter)
        self.artist.setStyleSheet(f'''
            font-size: 18px;
            font-family: {font_family};
            color: #fff;
        ''')

        self.title.setAlignment(QtCore.Qt.AlignCenter)
        self.title.setStyleSheet(f'''
            font-size: 20px;
            font-family: {font_family};
            font-weight: bold;
            color: #fff;
        ''')

        self.album.setAlignment(QtCore.Qt.AlignCenter)
        self.album.setStyleSheet(f'''
            font-size: 16px;
            font-family: {font_family};
            font-style: italic;
            color: #fff;
        ''')

        self.song_info_layout.addWidget(self.title)
        self.song_info_layout.addWidget(self.artist)
        self.song_info_layout.addWidget(self.album)
        self.song_info_layout.addWidget(self.song_progress)
        self.song_info_layout.addWidget(self.media_control)
        
        # Set the image
        self.image = QLabel()

        pixmap = QPixmap(image_path)
        pixmap = pixmap.scaled(200, 200, QtCore.Qt.KeepAspectRatio)
        self.image.setPixmap(pixmap)

        self.image.setStyleSheet(f'''
            border: 1px solid #fff;
        ''')

        # Media box
        self.media_layout = QHBoxLayout(self)

        self.media = QFrame(self)
        self.media.setLayout(self.media_layout)

        self.media_layout.addWidget(self.image)
        self.media_layout.addWidget(self.song_info)

        # Media player selection
        self.media_player_selection = QHBoxLayout(self)

        self.media_players = QFrame(self)
        self.media_players.setLayout(self.media_player_selection)

        icon_size = QtCore.QSize(32, 32)

        self.spotify_button = QtWidgets.QPushButton('', self)
        self.spotify_button.setIcon(spotify_icon)
        self.spotify_button.setIconSize(icon_size)
        self.spotify_button.setStyleSheet(button_style_sheet)

        self.chrome_button = QtWidgets.QPushButton('', self)
        self.chrome_button.setIcon(chrome_icon)
        self.chrome_button.setIconSize(icon_size)
        self.chrome_button.setStyleSheet(button_style_sheet)

        self.media_player_selection.addWidget(self.spotify_button)
        self.media_player_selection.addWidget(self.chrome_button)

        # Final widget
        self.main = QVBoxLayout(self)
        self.main.addWidget(self.media_players)
        self.main.addWidget(self.media)

        self.setStyleSheet('''
            QWidget {
                background-color: #2e2e2e;
            }
        ''')

        # Timer to update the widget
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.update_widget)
        self.timer.start(1000)

    def update_widget(self):
        # Run the script to get the latest status
        media_status = do_cmd(script_cmd).split(':')

        if len(media_status) != 5:
            return

        # Get the relevant data
        artist = media_status[0]
        title = media_status[1]
        album = media_status[2]

        total_time = '0' + media_status[3]
        current_time = '0' + media_status[4]

        # Update labels
        self.total_time.setText(format_time(int(total_time)))
        self.current_time.setText(format_time(int(current_time)))
        self.progress.setValue(int(current_time))
        self.progress.setMaximum(int(total_time))

        self.artist.setText(artist)
        self.title.setText(title)
        self.album.setText(album)
        
        # Update buttons
        status = do_cmd(status_cmd)
        if status == 'Playing':
            self.play_pause_button.setIcon(pause_icon)
        else:
            self.play_pause_button.setIcon(play_icon)

        # Update image
        pixmap = QPixmap(image_path)
        pixmap = pixmap.scaled(200, 200, QtCore.Qt.KeepAspectRatio)
        self.image.setPixmap(pixmap)

    def play_pause_button_clicked(self):
        do_cmd(play_pause_cmd)

        # Update the widget
        self.update_widget()

    def prev_button_clicked(self):
        do_cmd(prev_cmd)

        # Update the widget
        self.update_widget()

    def next_button_clicked(self):
        do_cmd(next_cmd)

        # Update the widget
        self.update_widget()

if __name__ == '__main__':
    widget = MediaWidget()
    widget.show()

    sys.exit(app.exec_())
