import sys
import sqlite3
import datetime
import os
import re
import random

from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QFileDialog
from PyQt5.QtWidgets import QLineEdit, QListWidget, QListWidgetItem, QProgressBar
from PyQt5.QtCore import QDate, QSize
from PyQt5.QtGui import QIcon, QImage, QPalette, QBrush


def get_days(x):
    today = datetime.date.today().weekday()
    if today < x:
        td = datetime.timedelta(days=x - today)
        today = datetime.date.today()
        return today + td
    elif today == x:
        return datetime.date.today()
    td = datetime.timedelta(days=today - x)
    today = datetime.date.today()
    return plus_one_week(today - td)


def plus_one_week(date):
    td = datetime.timedelta(days=7)
    return date + td


if not os.path.exists(os.getcwd() + "\\planner_data.db"):
    file = open("planner_data.db", "w")
    file.close()
    with open("zero_data_db.db", "w") as db:
        pass
    con = sqlite3.connect("zero_data_db.db")
    cur = con.cursor()
    reqest = """CREATE TABLE plans (
                                    id         INTEGER PRIMARY KEY AUTOINCREMENT
                                                       NOT NULL,
                                    title      STRING  NOT NULL,
                                    date       DATE    NOT NULL,
                                    time       TIME    NOT NULL,
                                    done       BOOLEAN,
                                    importance BOOLEAN
                                );
                                """
    cur.execute(reqest)
    con.commit()
    con.close()
    con = sqlite3.connect("planner_data.db")
    cur = con.cursor()
    request = """CREATE TABLE planner_data (
                                            id           INTEGER PRIMARY KEY AUTOINCREMENT
                                                                 UNIQUE
                                                                 NOT NULL,
                                            name_of_file STRING  UNIQUE
                                                                 NOT NULL,
                                            aim          STRING
                                            );
                                            """
    cur.execute(request)
    fname = os.getcwd().replace("\\", "/") + "/zero_data_db.db"
    request = f"""INSERT INTO planner_data (name_of_file, aim) VALUES ('{fname}', '-')"""
    cur.execute(request)
    con.commit()
    con.close()

TABLE_PARAMETER = "{TABLE_PARAMETER}"
DROP_TABLE_SQL = f"DROP TABLE {TABLE_PARAMETER};"
GET_TABLES_SQL = "SELECT name FROM sqlite_master WHERE type='table';"


def delete_all_tables(con):
    tables = get_tables(con)
    delete_tables(con, tables)


def get_tables(con):
    cur = con.cursor()
    cur.execute(GET_TABLES_SQL)
    tables = cur.fetchall()
    cur.close()
    return tables


def delete_tables(con, tables):
    cur = con.cursor()
    for table, in tables:
        request = DROP_TABLE_SQL.replace(TABLE_PARAMETER, table)
        if "sqlite_sequence" not in request:
            cur.execute(request)
    cur.close()



if not os.path.exists(os.getcwd() + "\\slogans.txt"):
    with open('slogans.txt', "w") as file:
        slogans = ["Не сдавайся, всё получится!",
                   "Неудачники сдаются, потерпев поражение. Победители терпят неудачи до тех пор, пока не добьются успеха.",
                   "Легко не будет, но это того стоит."]
        for slogan in slogans:
            file.write(slogan + "\n")


class BaseWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(1024, 768)
        MainWindow.setMinimumSize(QtCore.QSize(1024, 768))
        MainWindow.setStyleSheet("QPushButton {\n"
                                 "border: 1px solid grey;\n"
                                 "border-radius: 5px;\n"
                                 "background-color: white;\n"
                                 "font-size: 15px;\n"
                                 "}\n"
                                 "QListWidget {font-size: 15px; outline: none}\n"
                                 "QListWidget::item:selected {outline: none; border: 1px solid;\n"
                                 "border-radius: 5px;\n"
                                 "background-color: #7FB5B5}\n"
                                 "QListWidget::item:hover {outline: none; border: 1px solid; border-radius: 5px; "
                                 "background-color: rgba(199, 252, 236, 95);}"
                                 "QPushButton:hover {\n"
                                 "background-color: lightblue;\n"
                                 "}\n"
                                 "\n"
                                 "QPushButton:pressed {\n"
                                 "background-color: lightgray\n"
                                 "}"
                                 "slogan: {font: italic;}")
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setEnabled(True)
        self.centralwidget.setObjectName("centralwidget")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.centralwidget)
        self.verticalLayout.setObjectName("verticalLayout")
        self.gridLayout = QtWidgets.QGridLayout()
        self.gridLayout.setSizeConstraint(QtWidgets.QLayout.SetMinimumSize)
        self.gridLayout.setContentsMargins(5, 5, 5, 5)
        self.gridLayout.setHorizontalSpacing(5)
        self.gridLayout.setObjectName("gridLayout")
        self.unfinished_tasks = QtWidgets.QListWidget(self.centralwidget)
        self.unfinished_tasks.setMinimumSize(QtCore.QSize(402, 0))
        self.unfinished_tasks.setStyleSheet("background-color: #ffb961; border-radius: 10px;")
        self.unfinished_tasks.setObjectName("unfinished_tasks")
        self.gridLayout.addWidget(self.unfinished_tasks, 5, 1, 1, 1)
        self.aim_label = QtWidgets.QLabel(self.centralwidget)
        font = QtGui.QFont()
        font.setPointSize(12)
        self.aim_label.setFont(font)
        self.aim_label.setAlignment(QtCore.Qt.AlignCenter)
        self.aim_label.setObjectName("aim_label")
        self.gridLayout.addWidget(self.aim_label, 0, 1, 1, 2)
        self.line = QtWidgets.QFrame(self.centralwidget)
        self.line.setFrameShape(QtWidgets.QFrame.HLine)
        self.line.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line.setObjectName("line")
        self.gridLayout.addWidget(self.line, 3, 1, 1, 2)
        self.finished_tasks_text = QtWidgets.QLabel(self.centralwidget)
        self.finished_tasks_text.setEnabled(True)
        font = QtGui.QFont()
        font.setPointSize(12)
        self.finished_tasks_text.setFont(font)
        self.finished_tasks_text.setAlignment(QtCore.Qt.AlignCenter)
        self.finished_tasks_text.setObjectName("finished_tasks_text")
        self.gridLayout.addWidget(self.finished_tasks_text, 4, 2, 1, 1)
        self.finished_tasks = QtWidgets.QListWidget(self.centralwidget)
        self.finished_tasks.setAutoFillBackground(False)
        self.finished_tasks.setStyleSheet("background-color: rgb(250, 167, 108); border-radius: 10px;")
        self.finished_tasks.setObjectName("finished_tasks")
        self.gridLayout.addWidget(self.finished_tasks, 5, 2, 1, 1)
        self.unfinished_tasks_text = QtWidgets.QLabel(self.centralwidget)
        font = QtGui.QFont()
        font.setPointSize(12)
        self.unfinished_tasks_text.setFont(font)
        self.unfinished_tasks_text.setAlignment(QtCore.Qt.AlignCenter)
        self.unfinished_tasks_text.setObjectName("unfinished_tasks_text")
        self.gridLayout.addWidget(self.unfinished_tasks_text, 4, 1, 1, 1)
        self.change_status_btn = QtWidgets.QPushButton(self.centralwidget)
        self.change_status_btn.setStyleSheet("")
        self.change_status_btn.setObjectName("change_status_btn")
        self.gridLayout.addWidget(self.change_status_btn, 6, 1, 1, 1)
        self.add_event_btn = QtWidgets.QPushButton(self.centralwidget)
        self.add_event_btn.setObjectName("add_event_btn")
        self.gridLayout.addWidget(self.add_event_btn, 6, 2, 1, 1)
        self.progress_bar = QtWidgets.QProgressBar(self.centralwidget)
        self.progress_bar.setProperty("value", 24)
        self.progress_bar.setObjectName("progress_bar")
        self.gridLayout.addWidget(self.progress_bar, 1, 1, 1, 2)
        self.slogan = QtWidgets.QLabel(self.centralwidget)
        font = QtGui.QFont()
        font.setPointSize(11)
        self.slogan.setFont(font)
        self.slogan.setAlignment(QtCore.Qt.AlignCenter)
        self.slogan.setObjectName("slogan")
        self.gridLayout.addWidget(self.slogan, 2, 1, 1, 2)
        self.verticalLayout.addLayout(self.gridLayout)
        MainWindow.setCentralWidget(self.centralwidget)
        self.menu_bar = QtWidgets.QMenuBar(MainWindow)
        self.menu_bar.setGeometry(QtCore.QRect(0, 0, 1024, 21))
        self.menu_bar.setObjectName("menu_bar")
        self.new_aim_menu = QtWidgets.QMenu(self.menu_bar)
        self.new_aim_menu.setObjectName("new_aim_menu")
        MainWindow.setMenuBar(self.menu_bar)
        self.new_aim_menu_btn = QtWidgets.QAction(MainWindow)
        self.new_aim_menu_btn.setObjectName("new_aim_menu_btn")
        self.load_aim_menu_btn = QtWidgets.QAction(MainWindow)
        self.load_aim_menu_btn.setObjectName("load_aim_menu_btn")
        self.new_aim_menu.addAction(self.new_aim_menu_btn)
        self.new_aim_menu.addAction(self.load_aim_menu_btn)
        self.menu_bar.addAction(self.new_aim_menu.menuAction())

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.aim_label.setText(_translate("MainWindow", "Здесь написана цель"))
        self.finished_tasks_text.setText(_translate("MainWindow", "Завершённые дела"))
        self.unfinished_tasks_text.setText(_translate("MainWindow", "Предстоящие дела"))
        self.change_status_btn.setText(_translate("MainWindow", "Выбранное дело сделано/не сделано"))
        self.add_event_btn.setText(_translate("MainWindow", "Добавить/Удалить событие"))
        self.slogan.setText(_translate("MainWindow", "NEVER GIVE UP!"))
        self.new_aim_menu.setTitle(_translate("MainWindow", "Поменять цель"))
        self.new_aim_menu_btn.setText(_translate("MainWindow", "Создать новую"))
        self.load_aim_menu_btn.setText(_translate("MainWindow", "Загрузить имеющуюся"))


class MiniPlanner(object):
    def load_MiniPlanner(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(1107, 787)
        MainWindow.setMinimumSize(QtCore.QSize(1024, 768))
        MainWindow.setStyleSheet("#qt_calendar_prevmonth, #qt_calendar_nextmonth {\n"
                                 "    border: none;                     /* убрать границу */\n"
                                 "    margin-top: 64px;\n"
                                 "    color: white;\n"
                                 "    min-width: 36px;\n"
                                 "    max-width: 36px;\n"
                                 "    min-height: 36px;\n"
                                 "    max-height: 36px;\n"
                                 "    border-radius: 18px;            /* выглядит как эллипс */\n"
                                 "    font-weight: bold;              /* шрифт полужирный    */\n"
                                 "    \n"
                                 "    /* Удалить стандартное изображение клавиши со стрелкой. \n"
                                 "       Вы также можете настроить                           */\n"
                                 "    qproperty-icon: none;    \n"
                                 "    background-color: transparent; /* Цвет фона прозрачный */\n"
                                 "}\n"
                                 "\n"
                                 "#qt_calendar_prevmonth {\n"
                                 "    qproperty-text: \"<\";         /* Изменить текст кнопки  */\n"
                                 "}\n"
                                 "\n"
                                 "#qt_calendar_nextmonth {\n"
                                 "    qproperty-text: \">\";\n"
                                 "}\n"
                                 "\n"
                                 "QPushButton {\n"
                                 "border: 1px solid grey;\n"
                                 "border-radius: 5px;\n"
                                 "background-color: white;\n"
                                 "font-size: 12px;\n"
                                 "}\n"
                                 "\n"
                                 "QPushButton:hover {\n"
                                 "background-color: lightblue;\n"
                                 "}\n"
                                 "\n"
                                 "QPushButton:pressed {\n"
                                 "background-color: lightgrey\n"
                                 "}"
                                 "QListWidget::item:selected {outline: none; border: 1px solid;\n"
                                 "border-radius: 5px;\n"
                                 "background-color: #7FB5B5}\n"
                                 "QListWidget::item:hover {outline: none; border: 1px solid; border-radius: 5px; "
                                 "background-color: rgba(199, 252, 236, 95);}"
                                 "QListWidget {outline:none}"
                                 )
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setLayoutDirection(QtCore.Qt.LeftToRight)
        self.centralwidget.setObjectName("centralwidget")
        self.horizontalLayout = QtWidgets.QHBoxLayout(self.centralwidget)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.gridLayout = QtWidgets.QGridLayout()
        self.gridLayout.setObjectName("gridLayout")
        self.check_box = QtWidgets.QCheckBox(self.centralwidget)
        self.check_box.setMaximumSize(QtCore.QSize(144, 16777215))
        self.check_box.setStyleSheet("font-size: 12px")
        self.check_box.setObjectName("check_box")
        self.gridLayout.addWidget(self.check_box, 4, 1, 1, 1)
        self.back_btn = QtWidgets.QPushButton(self.centralwidget)
        self.back_btn.setStyleSheet("")
        self.back_btn.setObjectName("back_btn")
        self.gridLayout.addWidget(self.back_btn, 5, 3, 1, 1)
        self.label = QtWidgets.QLabel(self.centralwidget)
        font = QtGui.QFont()
        font.setFamily("MS Shell Dlg 2")
        font.setPointSize(15)
        self.label.setFont(font)
        self.label.setObjectName("label")
        self.gridLayout.addWidget(self.label, 1, 2, 1, 2)
        self.add_event_btn = QtWidgets.QPushButton(self.centralwidget)
        self.add_event_btn.setObjectName("add_event_btn")
        self.gridLayout.addWidget(self.add_event_btn, 5, 0, 1, 1)
        self.del_btn = QtWidgets.QPushButton(self.centralwidget)
        self.del_btn.setObjectName("del_btn")
        self.gridLayout.addWidget(self.del_btn, 5, 1, 1, 2)
        self.time_edit = QtWidgets.QTimeEdit(self.centralwidget)
        self.time_edit.setMaximumSize(QtCore.QSize(960, 16777215))
        self.time_edit.setStyleSheet("font-size: 20px;\n"
                                     "font-face: \'Roboto\';\n"
                                     "\n"
                                     "")
        self.time_edit.setObjectName("time_edit")
        self.gridLayout.addWidget(self.time_edit, 1, 0, 1, 2)
        self.check_list = QtWidgets.QListWidget(self.centralwidget)
        self.check_list.setMinimumSize(QtCore.QSize(0, 0))
        self.check_list.setStyleSheet("background-color: #ffb841; border-radius: 10px; font-size: 15px;")
        self.check_list.setObjectName("check_list")
        self.gridLayout.addWidget(self.check_list, 2, 2, 3, 2)
        self.inputer = QtWidgets.QLineEdit(self.centralwidget)
        self.inputer.setMaximumSize(QtCore.QSize(830, 16777215))
        self.inputer.setText("")
        self.inputer.setObjectName("inputer")
        self.gridLayout.addWidget(self.inputer, 4, 0, 1, 1)
        self.calendar = QtWidgets.QCalendarWidget(self.centralwidget)
        self.calendar.setMaximumSize(QtCore.QSize(960, 900))
        self.calendar.setContextMenuPolicy(QtCore.Qt.DefaultContextMenu)
        self.calendar.setLayoutDirection(QtCore.Qt.LeftToRight)
        self.calendar.setStyleSheet("#qt_calendar_navigationbar {\n"
                                    "    background-color:#AFDAFC;\n"
                                    "    font-size: 20px;\n"
                                    "    color: black;\n"
                                    "}\n"
                                    "\n"
                                    "#qt_calendar_prevmonth, #qt_calendar_nextmonth {\n"
                                    "    margin-top: 64px;\n"
                                    "    color: black;\n"
                                    "    min-width: 36px;\n"
                                    "    max-width: 36px;\n"
                                    "    min-height: 36px;\n"
                                    "    max-height: 36px;\n"
                                    "    border-radius: 18px;            /* выглядит как эллипс */\n"
                                    "    font-weight: bold;              /* шрифт полужирный    */  \n"
                                    "}\n"
                                    "\n"
                                    "#qt_calendar_prevmonth {\n"
                                    "    qproperty-text: \"<\";\n"
                                    "}\n"
                                    "\n"
                                    "#qt_calendar_nextmonth {\n"
                                    "    qproperty-text: \">\";\n"
                                    "}\n"
                                    "\n"
                                    "#qt_calendar_prevmonth:hover, #qt_calendar_nextmonth:hover {\n"
                                    "    background-color: rgba(225, 225, 225, 100);\n"
                                    "}\n"
                                    "\n"
                                    "#qt_calendar_prevmonth:pressed, #qt_calendar_nextmonth:pressed {\n"
                                    "    background-color: rgba(235, 235, 235, 100);\n"
                                    "}\n"
                                    "\n"
                                    "/*  год, месяц  */\n"
                                    "#qt_calendar_yearbutton, #qt_calendar_monthbutton {\n"
                                    "    color: black;\n"
                                    "    margin: 18px;\n"
                                    "    min-width: 60px;\n"
                                    "    border-radius: 30px;\n"
                                    "}\n"
                                    "#qt_calendar_yearbutton:hover, #qt_calendar_monthbutton:hover {\n"
                                    "    background-color: rgba(225, 225, 225, 100);\n"
                                    "}\n"
                                    "#qt_calendar_yearbutton:pressed, #qt_calendar_monthbutton:pressed {\n"
                                    "    background-color: rgba(235, 235, 235, 100);\n"
                                    "}\n"
                                    "\n"
                                    "/* Поле ввода года  */\n"
                                    "#qt_calendar_yearedit {\n"
                                    "    min-width: 70px;\n"
                                    "    color: black;\n"
                                    "    background: transparent;         /* Сделать фон окна ввода прозрачным */\n"
                                    "}\n"
                                    "#qt_calendar_yearedit::up-button {   /* Кнопка вверх                      */\n"
                                    "    width: 25px;\n"
                                    "    subcontrol-position: right;      \n"
                                    "}\n"
                                    "#qt_calendar_yearedit::down-button { /* Кнопка вниз     */\n"
                                    "    width: 25px;\n"
                                    "    subcontrol-position: left;       \n"
                                    "}\n"
                                    "\n"
                                    "/* меню выбора месяца                                          */\n"
                                    "CalendarWidget QToolButton QMenu {\n"
                                    "    background-color: white;\n"
                                    "    icon-image: none;\n"
                                    "}\n"
                                    "CalendarWidget QToolButton QMenu::item {\n"
                                    "    padding: 10px;\n"
                                    "}\n"
                                    "CalendarWidget QToolButton QMenu::item:selected:enabled {\n"
                                    "    background-color: rgb(230, 230, 230);\n"
                                    "}\n"
                                    "CalendarWidget QToolButton::menu-indicator {\n"
                                    "    subcontrol-position: right center;                /* Право по центру */\n"
                                    "}\n"
                                    "\n"
                                    "/* ниже календарной формы */\n"
                                    "QToolButton#qt_calendar_monthbutton::menu-indicator{\n"
                                    "subcontrol-origin: padding;\n"
                                    "subcontrol-position: center bottom;\n"
                                    "right: 5px;\n"
                                    "width: 15px;\n"
                                    "}\n"
                                    "\n"
                                    "QAbstractItemView {\n"
                                    "color: black;\n"
                                    "outline: 1px;\n"
                                    "selection-background-color: #042944; \n"
                                    "selection-color: white;\n"
                                    "font: 15px;}")
        self.calendar.setVerticalHeaderFormat(QtWidgets.QCalendarWidget.NoVerticalHeader)
        self.calendar.setNavigationBarVisible(True)
        self.calendar.setDateEditEnabled(True)
        self.calendar.setObjectName("calendar")
        self.gridLayout.addWidget(self.calendar, 2, 0, 1, 2)
        self.horizontalLayout.addLayout(self.gridLayout)
        MainWindow.setCentralWidget(self.centralwidget)
        self.save_btn = QtWidgets.QAction(MainWindow)
        self.save_btn.setObjectName("save_btn")
        self.load_btn = QtWidgets.QAction(MainWindow)
        self.load_btn.setObjectName("load_btn")

        self.retranslateUi2(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi2(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.check_box.setText(_translate("MainWindow", "Влияет на прогресс"))
        self.back_btn.setText(_translate("MainWindow", "Вернуться"))
        self.label.setText(_translate("MainWindow", "Запланированные события на выбранную дату:"))
        self.add_event_btn.setText(_translate("MainWindow", "Добавить"))
        self.del_btn.setText(_translate("MainWindow", "Удалить выбранный элемент"))
        self.save_btn.setText(_translate("MainWindow", "Сохранить"))
        self.load_btn.setText(_translate("MainWindow", "Загрузить"))


class NewPlan(object):
    def setupNewPlan(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(1024, 768)
        MainWindow.setMinimumSize(QtCore.QSize(1024, 768))
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.centralwidget)
        self.verticalLayout.setObjectName("verticalLayout")
        self.gridLayout = QtWidgets.QGridLayout()
        self.gridLayout.setObjectName("gridLayout")
        self.continue_btn = QtWidgets.QPushButton(self.centralwidget)
        self.continue_btn.setObjectName("continue_btn")
        self.gridLayout.addWidget(self.continue_btn, 8, 0, 1, 1)
        self.label_2 = QtWidgets.QLabel(self.centralwidget)
        font = QtGui.QFont()
        font.setPointSize(15)
        self.label_2.setFont(font)
        self.label_2.setAlignment(QtCore.Qt.AlignCenter)
        self.label_2.setObjectName("label_2")
        self.gridLayout.addWidget(self.label_2, 4, 0, 1, 1)
        self.date_edit = QtWidgets.QDateEdit(self.centralwidget)
        self.date_edit.setObjectName("date_edit")
        self.gridLayout.addWidget(self.date_edit, 5, 0, 1, 1)
        self.label_3 = QtWidgets.QLabel(self.centralwidget)
        font = QtGui.QFont()
        font.setPointSize(15)
        self.label_3.setFont(font)
        self.label_3.setAlignment(QtCore.Qt.AlignCenter)
        self.label_3.setObjectName("label_3")
        self.gridLayout.addWidget(self.label_3, 0, 0, 1, 1)
        self.date_edit_2 = QtWidgets.QDateEdit(self.centralwidget)
        self.date_edit_2.setObjectName("date_edit_2")
        self.gridLayout.addWidget(self.date_edit_2, 1, 0, 1, 1)
        self.label_4 = QtWidgets.QLabel(self.centralwidget)
        font = QtGui.QFont()
        font.setPointSize(15)
        self.label_4.setFont(font)
        self.label_4.setAlignment(QtCore.Qt.AlignCenter)
        self.label_4.setObjectName("label_4")
        self.gridLayout.addWidget(self.label_4, 2, 0, 1, 1)
        self.aim_edit = QtWidgets.QLineEdit(self.centralwidget)
        self.aim_edit.setObjectName("aim_edit")
        self.gridLayout.addWidget(self.aim_edit, 3, 0, 1, 1)
        self.verticalLayout.addLayout(self.gridLayout)
        MainWindow.setCentralWidget(self.centralwidget)

        self.retranslateNewPlan(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateNewPlan(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.continue_btn.setText(_translate("MainWindow", "Continue"))
        self.label_2.setText(_translate("MainWindow", "Укажите дату, когда Вы должны будете прийти к цели"))
        self.label_3.setText(_translate("MainWindow", "Укажите дату, начала"))
        self.label_4.setText(_translate("MainWindow", "Введите название цели"))


class Timetable(object):
    def setupTimetable(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(1024, 768)
        MainWindow.setMinimumSize(QtCore.QSize(1024, 768))
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.centralwidget)
        self.verticalLayout.setSpacing(5)
        self.verticalLayout.setObjectName("verticalLayout")
        self.text = QtWidgets.QLabel(self.centralwidget)
        font = QtGui.QFont()
        font.setPointSize(18)
        self.text.setFont(font)
        self.text.setAlignment(QtCore.Qt.AlignCenter)
        self.text.setObjectName("text")
        self.verticalLayout.addWidget(self.text)
        self.gridLayout = QtWidgets.QGridLayout()
        self.gridLayout.setObjectName("gridLayout")
        self.sunday = QtWidgets.QLabel(self.centralwidget)
        font = QtGui.QFont()
        font.setPointSize(15)
        self.sunday.setFont(font)
        self.sunday.setObjectName("sunday")
        self.gridLayout.addWidget(self.sunday, 0, 6, 1, 1)
        self.friday = QtWidgets.QLabel(self.centralwidget)
        font = QtGui.QFont()
        font.setPointSize(15)
        self.friday.setFont(font)
        self.friday.setObjectName("friday")
        self.gridLayout.addWidget(self.friday, 0, 4, 1, 1)
        self.wednsday = QtWidgets.QLabel(self.centralwidget)
        font = QtGui.QFont()
        font.setPointSize(15)
        self.wednsday.setFont(font)
        self.wednsday.setObjectName("wednsday")
        self.gridLayout.addWidget(self.wednsday, 0, 2, 1, 1)
        self.saturday = QtWidgets.QLabel(self.centralwidget)
        font = QtGui.QFont()
        font.setPointSize(15)
        self.saturday.setFont(font)
        self.saturday.setObjectName("saturday")
        self.gridLayout.addWidget(self.saturday, 0, 5, 1, 1)
        self.tuesday = QtWidgets.QLabel(self.centralwidget)
        font = QtGui.QFont()
        font.setPointSize(15)
        self.tuesday.setFont(font)
        self.tuesday.setObjectName("tuesday")
        self.gridLayout.addWidget(self.tuesday, 0, 1, 1, 1)
        self.monday = QtWidgets.QLabel(self.centralwidget)
        font = QtGui.QFont()
        font.setPointSize(15)
        self.monday.setFont(font)
        self.monday.setObjectName("monday")
        self.gridLayout.addWidget(self.monday, 0, 0, 1, 1)
        self.monday_list = QtWidgets.QListWidget(self.centralwidget)
        self.monday_list.setObjectName("monday_list")
        self.gridLayout.addWidget(self.monday_list, 1, 0, 1, 1)
        self.wednsday_list = QtWidgets.QListWidget(self.centralwidget)
        self.wednsday_list.setObjectName("wednsday_list")
        self.gridLayout.addWidget(self.wednsday_list, 1, 2, 1, 1)
        self.thursday_list = QtWidgets.QListWidget(self.centralwidget)
        self.thursday_list.setObjectName("thursday_list")
        self.gridLayout.addWidget(self.thursday_list, 1, 3, 1, 1)
        self.tuesday_list = QtWidgets.QListWidget(self.centralwidget)
        self.tuesday_list.setObjectName("tuesday_list")
        self.gridLayout.addWidget(self.tuesday_list, 1, 1, 1, 1)
        self.friday_list = QtWidgets.QListWidget(self.centralwidget)
        self.friday_list.setObjectName("friday_list")
        self.gridLayout.addWidget(self.friday_list, 1, 4, 1, 1)
        self.saturday_list = QtWidgets.QListWidget(self.centralwidget)
        self.saturday_list.setObjectName("saturday_list")
        self.gridLayout.addWidget(self.saturday_list, 1, 5, 1, 1)
        self.sunday_list = QtWidgets.QListWidget(self.centralwidget)
        self.sunday_list.setObjectName("sunday_list")
        self.gridLayout.addWidget(self.sunday_list, 1, 6, 1, 1)
        self.thursday = QtWidgets.QLabel(self.centralwidget)
        font = QtGui.QFont()
        font.setPointSize(15)
        self.thursday.setFont(font)
        self.thursday.setObjectName("thursday")
        self.gridLayout.addWidget(self.thursday, 0, 3, 1, 1)
        self.verticalLayout.addLayout(self.gridLayout)
        self.gridLayout_2 = QtWidgets.QGridLayout()
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.time_edit = QtWidgets.QTimeEdit(self.centralwidget)
        self.time_edit.setObjectName("time_edit")
        self.gridLayout_2.addWidget(self.time_edit, 0, 1, 1, 1)
        self.add_btn = QtWidgets.QPushButton(self.centralwidget)
        self.add_btn.setObjectName("add_btn")
        self.gridLayout_2.addWidget(self.add_btn, 0, 2, 1, 1)
        self.event_title = QtWidgets.QLineEdit(self.centralwidget)
        self.event_title.setObjectName("event_title")
        self.gridLayout_2.addWidget(self.event_title, 0, 0, 1, 1)
        self.remove_btn = QtWidgets.QPushButton(self.centralwidget)
        self.remove_btn.setObjectName("remove_btn")
        self.gridLayout_2.addWidget(self.remove_btn, 1, 2, 1, 1)
        self.day_box = QtWidgets.QComboBox(self.centralwidget)
        self.day_box.setMaximumSize(QtCore.QSize(16777215, 20))
        self.day_box.setObjectName("day_box")
        self.day_box.addItem("")
        self.day_box.addItem("")
        self.day_box.addItem("")
        self.day_box.addItem("")
        self.day_box.addItem("")
        self.day_box.addItem("")
        self.day_box.addItem("")
        self.gridLayout_2.addWidget(self.day_box, 1, 0, 1, 2)
        self.verticalLayout.addLayout(self.gridLayout_2)
        self.continue_btn = QtWidgets.QPushButton(self.centralwidget)
        self.continue_btn.setObjectName("continue_btn")
        self.verticalLayout.addWidget(self.continue_btn)
        MainWindow.setCentralWidget(self.centralwidget)

        self.retranslateTimetable(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateTimetable(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.text.setText(_translate("MainWindow", "Теперь составьте своё недельное расписание"))
        self.sunday.setText(_translate("MainWindow", "Воскресенье"))
        self.friday.setText(_translate("MainWindow", "Пятница"))
        self.wednsday.setText(_translate("MainWindow", "Среда"))
        self.saturday.setText(_translate("MainWindow", "Суббота"))
        self.tuesday.setText(_translate("MainWindow", "Вторник"))
        self.monday.setText(_translate("MainWindow", "Понедельник"))
        self.thursday.setText(_translate("MainWindow", "Четверг"))
        self.add_btn.setText(_translate("MainWindow", "Добавить"))
        self.remove_btn.setText(_translate("MainWindow", "Удалить выбранный"))
        self.day_box.setItemText(0, _translate("MainWindow", "Понедельник"))
        self.day_box.setItemText(1, _translate("MainWindow", "Вторник"))
        self.day_box.setItemText(2, _translate("MainWindow", "Среда"))
        self.day_box.setItemText(3, _translate("MainWindow", "Четверг"))
        self.day_box.setItemText(4, _translate("MainWindow", "Пятница"))
        self.day_box.setItemText(5, _translate("MainWindow", "Суббота"))
        self.day_box.setItemText(6, _translate("MainWindow", "Воскресенье"))
        self.continue_btn.setText(_translate("MainWindow", "Далее"))


class LastCheck(object):
    def setupLastCheck(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.setEnabled(True)
        MainWindow.resize(787, 637)
        MainWindow.setMinimumSize(QtCore.QSize(787, 637))
        MainWindow.setMaximumSize(QtCore.QSize(787, 637))
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.next_btn = QtWidgets.QPushButton(self.centralwidget)
        self.next_btn.setGeometry(QtCore.QRect(703, 605, 75, 23))
        self.next_btn.setMaximumSize(QtCore.QSize(75, 23))
        self.next_btn.setLayoutDirection(QtCore.Qt.RightToLeft)
        self.next_btn.setObjectName("next_btn")
        self.horizontalLayoutWidget = QtWidgets.QWidget(self.centralwidget)
        self.horizontalLayoutWidget.setGeometry(QtCore.QRect(160, 340, 491, 80))
        self.horizontalLayoutWidget.setObjectName("horizontalLayoutWidget")
        self.horizontalLayout = QtWidgets.QHBoxLayout(self.horizontalLayoutWidget)
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.path = QtWidgets.QLineEdit(self.horizontalLayoutWidget)
        self.path.setEnabled(False)
        self.path.setMaximumSize(QtCore.QSize(438, 20))
        self.path.setPlaceholderText("")
        self.path.setCursorMoveStyle(QtCore.Qt.VisualMoveStyle)
        self.path.setClearButtonEnabled(False)
        self.path.setObjectName("path")
        self.horizontalLayout.addWidget(self.path)
        self.browse_btn = QtWidgets.QPushButton(self.horizontalLayoutWidget)
        self.browse_btn.setMaximumSize(QtCore.QSize(75, 23))
        self.browse_btn.setObjectName("browse_btn")
        self.horizontalLayout.addWidget(self.browse_btn)
        self.label = QtWidgets.QLabel(self.centralwidget)
        self.label.setEnabled(True)
        self.label.setGeometry(QtCore.QRect(190, 210, 427, 24))
        self.label.setMaximumSize(QtCore.QSize(16777215, 100))
        font = QtGui.QFont()
        font.setPointSize(15)
        self.label.setFont(font)
        self.label.setAlignment(QtCore.Qt.AlignCenter)
        self.label.setObjectName("label")
        MainWindow.setCentralWidget(self.centralwidget)

        self.retranslateLastCheck(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateLastCheck(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.next_btn.setText(_translate("MainWindow", "Далее"))
        self.browse_btn.setText(_translate("MainWindow", "Обзор"))
        self.label.setText(_translate("MainWindow", "Выберите путь сохранения своего расписания"))


class Slogans(object):
    def setupSlogans(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(1024, 768)
        MainWindow.setMinimumSize(QtCore.QSize(1024, 768))
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.centralwidget)
        self.verticalLayout.setObjectName("verticalLayout")
        spacerItem = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout.addItem(spacerItem)
        self.label = QtWidgets.QLabel(self.centralwidget)
        font = QtGui.QFont()
        font.setPointSize(20)
        self.label.setFont(font)
        self.label.setAlignment(QtCore.Qt.AlignCenter)
        self.label.setObjectName("label")
        self.verticalLayout.addWidget(self.label)
        spacerItem1 = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout.addItem(spacerItem1)
        self.line_edit = QtWidgets.QLineEdit(self.centralwidget)
        self.line_edit.setObjectName("line_edit")
        self.verticalLayout.addWidget(self.line_edit)
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.add_btn = QtWidgets.QPushButton(self.centralwidget)
        self.add_btn.setObjectName("add_btn")
        self.horizontalLayout.addWidget(self.add_btn)
        self.delete_btn = QtWidgets.QPushButton(self.centralwidget)
        self.delete_btn.setObjectName("delete_btn")
        self.horizontalLayout.addWidget(self.delete_btn)
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.gridLayout = QtWidgets.QGridLayout()
        self.gridLayout.setObjectName("gridLayout")
        self.listWidget = QtWidgets.QListWidget(self.centralwidget)
        font = QtGui.QFont()
        font.setPointSize(12)
        self.listWidget.setFont(font)
        self.listWidget.setObjectName("listWidget")
        self.gridLayout.addWidget(self.listWidget, 0, 0, 1, 1)
        self.verticalLayout.addLayout(self.gridLayout)
        self.continue_btn = QtWidgets.QPushButton(self.centralwidget)
        self.continue_btn.setMinimumSize(QtCore.QSize(0, 0))
        self.continue_btn.setMaximumSize(QtCore.QSize(75, 16777215))
        self.continue_btn.setLayoutDirection(QtCore.Qt.RightToLeft)
        self.continue_btn.setObjectName("continue_btn")
        self.verticalLayout.addWidget(self.continue_btn)
        MainWindow.setCentralWidget(self.centralwidget)

        self.retranslateSlogans(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateSlogans(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.label.setText(_translate("MainWindow", "Теперь, если хотите, введите мотивационные слоганы"))
        self.add_btn.setText(_translate("MainWindow", "Добавить"))
        self.delete_btn.setText(_translate("MainWindow", "Удалить выбранный"))
        self.continue_btn.setText(_translate("MainWindow", "Далее"))


class MakerNewPlan(QMainWindow, MiniPlanner, NewPlan, Timetable, LastCheck, Slogans):
    def __init__(self):
        super().__init__()
        self.setupNewPlan(self)
        self.initUI()
        self.setWindowIcon(QIcon("./data./icon.ico"))

    def initUI(self):
        self.setWindowTitle("Road To The Dream")
        today = QDate.currentDate().toPyDate()
        self.date_edit.setMinimumDate(today)
        self.date_edit_2.setMinimumDate(today)
        self.continue_btn.clicked.connect(self.continue_do)
        background_image = QImage('data/back.jpg')
        background_image = background_image.scaled(QSize(1920, 1080))
        palette = QPalette()
        palette.setBrush(QPalette.Window, QBrush(background_image))
        self.setPalette(palette)

    def continue_do(self):
        self.date_of_end = self.date_edit.date()
        self.date_of_start = self.date_edit_2.date()
        self.aim_name = self.aim_edit.text()
        if self.date_of_start > self.date_of_end:
            return
        if not self.aim_name:
            self.aim_name = "-"
        self.setupSlogans(self)
        self.setWindowTitle("Slogans")
        self.add_btn.clicked.connect(self.add_slogan)
        self.delete_btn.clicked.connect(self.delete_slogan)
        self.continue_btn.clicked.connect(self.set_timetable)
        self.print_slogans()

    def print_slogans(self):
        self.listWidget.clear()
        with open("slogans.txt", "r") as file:
            data = file.readlines()
            for i in data:
                self.listWidget.addItem(i)

    def add_slogan(self):
        slogan = self.line_edit.text()
        if slogan:
            self.line_edit.setText("")
            with open("slogans.txt", "r+") as file:
                file.write(slogan + "\n")
            self.print_slogans()

    def delete_slogan(self):
        items = self.listWidget.selectedItems()
        if items:
            for item in items:
                self.listWidget.takeItem(self.listWidget.row(item))
                text = item.text()
                pattern = re.compile(re.escape(text))
                with open('slogans.txt', 'r+') as f:
                    lines = f.readlines()
                    f.seek(0)
                    for line in lines:
                        result = pattern.search(line)
                        if result is None:
                            f.write(line)
                        f.truncate()
                self.print_slogans()
        return

    def set_timetable(self):
        self.setupTimetable(self)
        self.setWindowTitle("Timetable")
        self.add_btn.clicked.connect(self.add_item)
        self.remove_btn.clicked.connect(self.remove_item)
        self.continue_btn.clicked.connect(self.last_check)

    def add_item(self):
        dictionary = {"Понедельник": self.monday_list, "Вторник": self.tuesday_list,
                      "Среда": self.wednsday_list, "Четверг": self.thursday_list,
                      "Пятница": self.friday_list, "Суббота": self.saturday_list, "Воскресенье": self.sunday_list}
        day = dictionary[self.day_box.currentText()]
        time = self.time_edit.time().toString("HH:mm")
        if self.event_title.text():
            day.addItem(self.event_title.text() + " | " + time)

    def remove_item(self):
        lists = [self.monday_list, self.tuesday_list, self.wednsday_list,
                 self.thursday_list, self.friday_list, self.saturday_list, self.sunday_list]
        for i in lists:
            items = i.selectedItems()
            if items:
                for item in items:
                    i.takeItem(i.row(item))
        return

    def last_check(self):
        self.monday = [self.monday_list.item(i).text() for i in range(self.monday_list.count())]
        self.tuesday = [self.tuesday_list.item(i).text() for i in range(self.tuesday_list.count())]
        self.wednsday = [self.wednsday_list.item(i).text() for i in range(self.wednsday_list.count())]
        self.thursday = [self.thursday_list.item(i).text() for i in range(self.thursday_list.count())]
        self.friday = [self.friday_list.item(i).text() for i in range(self.friday_list.count())]
        self.saturday = [self.saturday_list.item(i).text() for i in range(self.saturday_list.count())]
        self.sunday = [self.sunday_list.item(i).text() for i in range(self.sunday_list.count())]
        self.week = [self.monday, self.tuesday, self.wednsday, self.thursday, self.friday, self.saturday, self.sunday]
        self.setupLastCheck(self)
        self.setWindowTitle("Path To Save Timetable")
        self.path.setText("")
        self.fname = self.path.text()
        self.browse_btn.clicked.connect(self.browse)
        self.next_btn.clicked.connect(self.next)

    def browse(self):
        self.fname = QFileDialog.getSaveFileName(self, "Путь сохранения файла", "", "База данных SQL (*.db)")
        if self.fname:
            self.path.setText(f"{self.fname[0]}")

    def next(self):
        if not self.path.text():
            return
        con = sqlite3.connect(self.fname[0])
        cur = con.cursor()
        reqest = """CREATE TABLE plans (
                    id         INTEGER PRIMARY KEY AUTOINCREMENT
                                       NOT NULL,
                    title      STRING  NOT NULL,
                    date       DATE    NOT NULL,
                    time       TIME    NOT NULL,
                    done       BOOLEAN,
                    importance BOOLEAN
                );
                """
        try:
            cur.execute(reqest)
        except sqlite3.OperationalError:
            delete_all_tables(con)
            cur.execute(reqest)

        for i in range(len(self.week)):
            if self.week[i]:
                for j in self.week[i]:
                    date = get_days(i)
                    while date < self.date_of_start:
                        plus_one_week(date)
                    title = j[:j.index(" | ")]
                    time = j[j.index(" | ") + 3:]
                    while date <= self.date_of_end:
                        reqest = f"""INSERT INTO plans(title, date, time, done, importance)
                                VALUES ('{title}', '{date}', '{time}', 0, 1)"""
                        cur.execute(reqest)
                        date = plus_one_week(date)
        con.commit()
        con.close()
        con = sqlite3.connect("planner_data.db")
        cur = con.cursor()
        for i in cur.execute("SELECT name_of_file FROM planner_data").fetchall():
            if self.fname[0] in i:
                request = f"""DELETE FROM planner_data WHERE name_of_file = '{self.fname[0]}'"""
                cur.execute(request)
        request = f"""INSERT INTO planner_data(name_of_file, aim) VALUES ('{self.fname[0]}', '{self.aim_name}')"""
        cur.execute(request)
        con.commit()
        con.close()
        self.close()
        self.aim = AimAchieve()
        self.aim.show()


class AimAchieve(QMainWindow, BaseWindow, MiniPlanner):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        con = sqlite3.connect("planner_data.db")
        cur = con.cursor()
        request = """SELECT name_of_file, aim FROM planner_data WHERE id = (SELECT MAX(id) FROM planner_data)"""
        res = cur.execute(request).fetchone()
        self.fname, self.aim_name = (res[0],), res[1]
        self.initUI()

    def initUI(self):
        self.setWindowTitle("Road To The Dream")
        self.setWindowIcon(QIcon("./data/icon.ico"))
        self.aim_label.setText(self.aim_name)
        self.get_tasks()
        self.add_event_btn.clicked.connect(self.add_or_delete_event)
        self.change_status_btn.clicked.connect(self.change_status)
        self.new_aim_menu_btn.triggered.connect(self.make_new_plan)
        self.load_aim_menu_btn.triggered.connect(self.ready_plan)
        background_image = QImage('data/hello_kitty_back.jpg')
        background_image = background_image.scaled(QSize(1920, 1080))
        palette = QPalette()
        palette.setBrush(QPalette.Window, QBrush(background_image))
        self.setPalette(palette)
        self.set_slogan()

    def set_slogan(self):
        with open("slogans.txt", "r") as file:
            data = list(file)
            if data:
                self.slogan.setText(f"{data[random.randint(0, len(data) - 1)]}")


    def get_tasks(self):
        con = sqlite3.connect(self.fname[0])
        cur = con.cursor()
        request = """SELECT * FROM plans"""
        self.total = len(cur.execute(request).fetchall())
        date = datetime.date.today().strftime("%Y-%m-%d")
        request = f"""SELECT title, time FROM plans WHERE (done = 0) AND (date = '{date}')"""
        res = cur.execute(request).fetchall()
        for i in res:
            self.unfinished_tasks.addItem(f"{i[0]} | {i[1]}")
        request = f"""SELECT title, time FROM plans WHERE (done = 1) AND (date = '{date}')"""
        res = cur.execute(request).fetchall()
        for i in res:
            self.finished_tasks.addItem(f"{i[0]} | {i[1]}")
        request = """SELECT * FROM plans WHERE done = 1"""
        res = len(cur.execute(request).fetchall())
        if self.total > 0:
            self.progress_bar.setValue(round(res / self.total * 100))
        else:
            self.progress_bar.setValue(0)
        con.close()

    def change_status(self):
        if self.finished_tasks.selectedItems():
            con = sqlite3.connect(self.fname[0])
            cur = con.cursor()
            items = self.finished_tasks.selectedItems()
            for item in items:
                date = datetime.date.today()
                title = item.text()[:item.text().index(" | ")]
                time = item.text()[item.text().index(" | ") + 3:]
                request = f"""UPDATE plans SET done = 0 WHERE date = '{date}'
                 AND title = "{title}" AND time = '{time}'"""
                cur.execute(request)
                con.commit()
                con.close()
            for item in self.finished_tasks.selectedItems():
                self.finished_tasks.takeItem(self.finished_tasks.row(item))
                self.unfinished_tasks.addItem(item)
        elif self.unfinished_tasks.selectedItems():
            con = sqlite3.connect(self.fname[0])
            cur = con.cursor()
            items = self.unfinished_tasks.selectedItems()
            for item in items:
                date = datetime.date.today()
                title = item.text()[:item.text().index(" | ")]
                time = item.text()[item.text().index(" | ") + 3:]
                request = f"""UPDATE plans SET done = 1 WHERE date = '{date}'
                             AND title = "{title}" AND time = '{time}'"""
                cur.execute(request)
                con.commit()
                con.close()
            for item in self.unfinished_tasks.selectedItems():
                self.unfinished_tasks.takeItem(self.unfinished_tasks.row(item))
                self.finished_tasks.addItem(item)
        con = sqlite3.connect(self.fname[0])
        cur = con.cursor()
        request = """SELECT * FROM plans WHERE done = 1 AND importance = 1"""
        res = len(cur.execute(request).fetchall())
        if res == 0 or self.total <= 0:
            self.progress_bar.setValue(0)
        else:
            self.progress_bar.setValue(round(res / self.total * 100))
        return

    def add_or_delete_event(self):
        self.load_MiniPlanner(self)
        self.setWindowTitle("Road To The Dream")
        self.calendar.selectionChanged.connect(self.print_events)
        self.back_btn.clicked.connect(self.back)
        self.add_event_btn.clicked.connect(self.add_event)
        self.del_btn.clicked.connect(self.delete_event)

    def print_events(self):
        self.check_list.clear()
        date = self.calendar.selectedDate().toString("yyyy-MM-dd")
        con = sqlite3.connect(self.fname[0])
        cur = con.cursor()
        request = f"""SELECT title, time, importance FROM plans WHERE date = '{date}'"""
        res = cur.execute(request).fetchall()
        con.close()
        for i in res:
            self.check_list.addItem(f"{i[0]} | {i[1]} | {i[2]}")

    def add_event(self):
        text = self.inputer.text()
        time = self.time_edit.time().toString("HH:mm")
        date = self.calendar.selectedDate().toString("yyyy-MM-dd")
        con = sqlite3.connect(self.fname[0])
        cur = con.cursor()
        if self.check_box.isChecked():
            request = f"""INSERT INTO plans(title, date, time, done, importance) 
                VALUES ('{text}', '{date}', '{time}', 0, 1)"""
            importance = 1
        else:
            request = f"""INSERT INTO plans(title, date, time, done, importance) 
                VALUES ('{text}', '{date}', '{time}', 0, 0)"""
            importance = 0
        cur.execute(request)
        con.commit()
        con.close()
        self.check_list.addItem(f"{text} | {time} | {importance}")

    def delete_event(self):
        listItems = self.check_list.selectedItems()
        if not listItems:
            return
        for item in listItems:
            self.check_list.takeItem(self.check_list.row(item))
            con = sqlite3.connect(self.fname[0])
            cur = con.cursor()
            date = self.calendar.selectedDate().toString("yyyy-MM-dd")
            text = item.text()[:item.text().index(" | ")]
            time = item.text()[item.text().index(" | ") + 3:-4]
            request = f"""DELETE FROM plans WHERE date = '{date}' AND title = '{text}' AND time = '{time}'"""
            cur.execute(request)
            con.commit()
            con.close()

    def back(self):
        self.close()
        self.aim = AimAchieve()
        self.aim.show()

    def make_new_plan(self):
        self.close()
        self.make = MakerNewPlan()
        self.make.show()

    def ready_plan(self):
        self.fname = QFileDialog.getOpenFileName(self, "Выберите базу данных", "",
                                                 "База данных (*.db *.sqlite3 *.sqlite)")
        if self.fname[0]:
            con = sqlite3.connect("planner_data.db")
            cur = con.cursor()
            request = f"""SELECT aim FROM planner_data
            WHERE name_of_file = '{self.fname[0]}'"""
            self.aim_name = cur.execute(request).fetchall()[0]
            request = f"""DELETE FROM planner_data WHERE name_of_file = '{self.fname[0]}'"""
            cur.execute(request)
            request = f"""INSERT INTO planner_data(name_of_file, aim) VALUES ('{self.fname[0]}', '{self.aim_name}')"""
            cur.execute(request)
            con.commit()
            con.close()
            self.close()
            self.aim_achieve = AimAchieve()
            self.aim_achieve.show()
        return


if __name__ == "__main__":
    app = QApplication(sys.argv)
    base = AimAchieve()
    base.show()
    sys.exit(app.exec_())
