from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver import ActionChains
from selenium.webdriver.common.keys import Keys
from PyQt5.QtWidgets import QWidget, QApplication, QTableWidgetItem, QTableWidget, QProgressBar, QPushButton
from PyQt5 import uic
from PyQt5.QtCore import pyqtSignal, QThread
from PyQt5 import QtCore
import time


class TSN:

    def __init__(self):
        options = Options();
        options.add_experimental_option('detach', True)
        self.chrome_driver = webdriver.Chrome(options=options);
        self.chrome_driver.get('https://www.tsn.ca/live')
        time.sleep(5)

    def login(self, user, pword):
        self.chrome_driver.find_element(By.CSS_SELECTOR, '.videoLogin').click()
        time.sleep(1)
        self.chrome_driver.find_element(By.ID, 'email').send_keys(user)
        time.sleep(1)
        self.chrome_driver.find_element(By.ID, 'password').send_keys(pword)
        time.sleep(1)
        self.chrome_driver.find_element(By.XPATH, "//*[contains(text(), 'CONTINUE')]").click()
        time.sleep(10)
        self.chrome_driver.get('https://www.tsn.ca/fifa-world-cup/games-on-demand')
        time.sleep(2)
        self.page_down()
        time.sleep(10)

    def find_game(self, team_1, team_2) -> str:
        game_ul_container = self.chrome_driver.find_element(By.CSS_SELECTOR, '.playlist')
        games = game_ul_container.find_elements(By.CSS_SELECTOR, 'li')
        found = False
        for game in games:
            txt = game.text.splitlines()
            game_title = txt[3]
            if team_1 in game_title and team_2 in game_title:
                found = True
                game.find_element(By.CSS_SELECTOR, '.media-overlay').click()
                play_game = self.chrome_driver.find_element(By.CSS_SELECTOR, '.video-outer-wrapper')
                # play_game.click()
                # time.sleep(2)
                # keep scores hidden
                self.page_down()
                # wait out ads
                time.sleep(60)
                # go full screen and pause
                ActionChains(self.chrome_driver).double_click(play_game).perform()
                break
        if found:
            return 'TSN has the game, enjoy!'
        else:
            return 'TSN sucks, they do not have this game yet, file a lawsuit.'

    def page_down(self):
        body = self.chrome_driver.find_element(By.XPATH, '/html/body')
        body.click()
        ActionChains(self.chrome_driver).send_keys(Keys.PAGE_DOWN).perform()


class TsnUi(QWidget):
    def __init__(self):
        super().__init__()
        uic.loadUi('tsn.ui', self)
        self.execute_button.clicked.connect(self.execute_clicked)

    def execute_clicked(self):
        user = self.email_tf.text()
        pword = self.password_tf.text()
        team_1 = self.team_1.toPlainText()
        team_2 = self.team_2.toPlainText()
        self.tsn_thread = TSNThread(user, pword, team_1, team_2)
        self.tsn_thread.progress_signal.connect(self.update_ui)
        self.tsn_thread.start()

    def update_ui(self, msg):
        self.status_text.setText(msg)


class TSNThread(QThread):
    progress_signal = pyqtSignal(str)

    def __init__(self, user, pword, team_1, team_2):
        super().__init__()
        self.user = user
        self.pword = pword
        self.team_1 = team_1
        self.team_2 = team_2

    def run(self) -> None:
        self.progress_signal.emit('Launching browser...')
        tsn = TSN()
        tsn.login(self.user, self.pword)
        self.progress_signal.emit('Successfully logged in, now searching for match!')
        game_found = tsn.find_game(self.team_1, self.team_2)
        self.progress_signal.emit(game_found)


app = QApplication([])
tsn_ui = TsnUi()

tsn_ui.show()
app.exec()
