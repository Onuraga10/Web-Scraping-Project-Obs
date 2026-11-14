import sys
import pandas as pd
from PySide6.QtCore import QObject, Property, Signal, Slot, QAbstractListModel, Qt, QModelIndex
from PySide6.QtGui import QGuiApplication
from PySide6.QtQml import QQmlApplicationEngine
import obs


class GradesModel(QAbstractListModel):
    CourseRole = Qt.UserRole + 1
    Vize1Role = Qt.UserRole + 2
    OdevRole = Qt.UserRole + 3
    FinalGradeRole = Qt.UserRole + 4
    HarfRole = Qt.UserRole + 5

    def __init__(self, parent=None):
        super().__init__(parent)
        self._grades = []

    def rowCount(self, parent=QModelIndex()):
        return len(self._grades)

    def data(self, index, role=Qt.DisplayRole):
        if not index.isValid():
            return None
        row = index.row()
        grade = self._grades[row]

        if role == self.CourseRole:
            return grade.get('course', '')
        elif role == self.Vize1Role:
            return grade.get('vize1', '--')
        elif role == self.OdevRole:
            return grade.get('ödev', '--')
        elif role == self.FinalGradeRole:
            return grade.get('final', '0.0')
        elif role == self.HarfRole:
            return grade.get('harf', '--')
        return None

    def roleNames(self):
        return {
            self.CourseRole: b'course',
            self.Vize1Role: b'vize1',
            self.OdevRole: b'odev',
            self.FinalGradeRole: b'final_grade',
            self.HarfRole: b'harf'
        }

    def update_grades(self, grades_list):
        self.beginResetModel()
        self._grades = grades_list
        self.endResetModel()


class Backend(QObject):
    hasChangesChanged = Signal()
    changeMessageChanged = Signal()

    def __init__(self):
        super().__init__()
        self._has_changes = False
        self._change_message = ""
        self.grades_model = GradesModel()

    @Property(bool, notify=hasChangesChanged)
    def hasChanges(self):
        return self._has_changes

    @Property(str, notify=changeMessageChanged)
    def changeMessage(self):
        return self._change_message

    def set_changes(self, has_changes, message):
        self._has_changes = has_changes
        self._change_message = message
        self.hasChangesChanged.emit()
        self.changeMessageChanged.emit()


def fetch_data(backend):
    print("Fetching grades from OBS...")
    grades_data = obs.login_and_fetch_grades()
    if not grades_data:
        backend.set_changes(False, "Veri alınamadı. (Giriş Başarısız)")
        return

    new_table, difference = obs.process_grades(grades_data)
    if new_table is None:
        return

    # Convert new_table (Pandas DataFrame) to a list of dicts for the QML model
    grades_list = []
    for course, row in new_table.iterrows():
        def clean(val, default):
            if pd.isna(val) or val == "":
                return default
            try:
                if float(val).is_integer():
                    return str(int(float(val)))
            except Exception:
                pass
            return str(val)

        grades_list.append({
            'course': str(course),
            'vize1': clean(row.get('1.Ara Sınav', '--'), '--'),
            'odev': clean(row.get('Ödev', '--'), '--'),
            'final_grade': clean(row.get('Başarı Notu', '0.0'), '0.0'),
            'harf': clean(row.get('Harf', '--'), '--')
        })

    # Update the QML Model
    backend.grades_model.update_grades(grades_list)

    # Check for changes
    if not difference.empty:
        changes_str = []
        for course, row in difference.iterrows():
            changes_str.append(f"{course} güncellendi.")

        msg = "\n".join(changes_str)
        backend.set_changes(True, msg)
    else:
        backend.set_changes(False, "")
    print("Data processing complete!")


if __name__ == "__main__":
    app = QGuiApplication(sys.argv)

    backend = Backend()

    # Initial data fetch
    fetch_data(backend)

    engine = QQmlApplicationEngine()

    # Expose the backend object and grades model to QML
    engine.rootContext().setContextProperty("backend", backend)
    engine.rootContext().setContextProperty("gradesModel", backend.grades_model)

    engine.load("design.qml")

    if not engine.rootObjects():
        sys.exit(-1)

    sys.exit(app.exec())
