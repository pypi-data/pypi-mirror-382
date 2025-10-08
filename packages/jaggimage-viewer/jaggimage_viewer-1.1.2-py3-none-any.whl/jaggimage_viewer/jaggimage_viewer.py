#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# This program is free software: you can redistribute it
# and/or modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation, either version 3 of
# the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <https://www.gnu.org/licenses/>.

from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
import sys, os, time

try:
	from jaggimage_viewer._version import version
except ImportError:
	version = "0.0.0"

WINDOW_TITLE = "Jaggimage Viewer"
IMG_EXT = (".jpg", ".jpeg", ".jpe", ".gif", ".png", ".bmp", ".webp", ".tif", ".tiff")

class ImageViewer(QMainWindow):
	def __init__(self, filename=None, filesList=None):
		super().__init__()
		sys.excepthook = self.unhandledException
		self.readConfig()
		self.scaleFactor = 1
		self.imageDescription = ""
		self.windowDecorationSize = QSize(20, 30)
		self.setStyleSheet("#imageLabel, QScrollArea { background-color: black; color: white; }")
		self.imageLabel = QLabel()
		self.imageLabel.setObjectName("imageLabel")
		self.imageLabel.setAlignment(Qt.AlignHCenter|Qt.AlignVCenter)
		self.imageLabel.setSizePolicy(QSizePolicy.Policy.Ignored, QSizePolicy.Policy.Ignored)

		self.scrollArea = CustomMovableScrollArea()
		self.scrollArea.setWidget(self.imageLabel)
		self.setCentralWidget(self.scrollArea)

		self.setAcceptDrops(True)
		if self.fullScreen:
			self.showFullScreen()

		self.statusBar().hide()
		self.setWindowTitle(WINDOW_TITLE)

		self.getDescriptionTimer = QTimer()
		self.getDescriptionTimer.setSingleShot(True)
		self.getDescriptionTimer.timeout.connect(self.getDescription)
		self.preloadNextImageTimer = QTimer()
		self.preloadNextImageTimer.setSingleShot(True)
		self.preloadNextImageTimer.timeout.connect(self.preloadNextImage)
		self.preloadPreviousImageTimer = QTimer()
		self.preloadPreviousImageTimer.setSingleShot(True)
		self.preloadPreviousImageTimer.timeout.connect(self.preloadPreviousImage)
		self.setIconFromPixmapTimer = QTimer()
		self.setIconFromPixmapTimer.setSingleShot(True)
		self.setIconFromPixmapTimer.timeout.connect(self.setIconFromPixmap)

		self.fileIndex = 0
		self.files = []

		# if the filename given is a directory, try to find any file with recognized image extension...
		if filename and os.path.isdir(filename):
			self.files = list_dir_img_abs(filename)
			if len(self.files) == 0:
				QMessageBox.critical(None, WINDOW_TITLE, "No suitable image found in \"%s\" directory." % (filename), QMessageBox.Close )
				exit(1)
			filename = self.files[0]

		# add the files list (if given), try to list files if directories given
		if filesList:
			for f in filesList:
				if os.path.isdir(f):
					for f2 in list_dir_img_abs(f): self.files.append(f2)
				else:
					self.files.append(os.path.abspath(f))

		# last ressort: use the first suitable file in current directory (program ran with w/o args)
		if filename is None:
			if len(self.files) > 0:
				filename = self.files[0]
			else:
				self.files = list_dir_img_abs('.')
				if len(self.files):
					filename = self.files[0]

		self.loadImage(filename, firstRun=True)
		if not self.fullScreen and not self.pixmap.isNull():
			self.resize(self.pixmap.width(), self.pixmap.height())

		self.show()
		self.installEventFilter(self)
		self.scrollTimer = QTimer()
		self.scrollTimer.timeout.connect(self.scrollTimerTimeout)
		self.scrollDeltaX, self.scrollDeltaY = 0, 0

		if len(self.files) == 0:
			QTimer.singleShot(100, self.listImagesInSameDirectory)
		else:
			self.preloadNextImageTimer.start(200)
			self.preloadPreviousImageTimer.start(300)

	def readConfig(self):
		settings = QSettings("Jaggimage-Viewer")
		self.fullScreen       = settings.value("fullScreen",       True,  type=bool)
		self.zoomLock         = settings.value("zoomLock",         False, type=bool)
		self.windowAutoResize = settings.value("windowAutoResize", True,  type=bool)
		self.imgEditor        = settings.value("imgEditor",        "gimp")

	def writeConfig(self):
		settings = QSettings("Jaggimage-Viewer")
		settings.setValue("fullScreen", self.fullScreen)
		settings.setValue("zoomLock", self.zoomLock)
		settings.setValue("windowAutoResize", self.windowAutoResize)
		settings.setValue("imgEditor", self.imgEditor)
		settings.sync()

	def contextMenuExec(self, pos):
		try:
			self.contextMenu.exec(pos)
		except:
			self.contructContextMenu()
			self.contextMenu.exec(pos)

	def contructContextMenu(self):
		self.contextMenu = QMenu(self)
		self.contextMenu.addAction("Previous Image", self.loadPreviousImage, "Backspace")
		self.contextMenu.addAction("Next Image", self.loadNextImage, "Space")
		self.contextMenu.addAction("Reload Image and Relist Directory", self.refresh, "F5")
		self.contextMenu.addSeparator()
		self.fullScreenMenuAction = QAction("Fullscreen")
		self.fullScreenMenuAction.setCheckable(True)
		self.fullScreenMenuAction.setChecked(self.fullScreen)
		self.fullScreenMenuAction.setShortcut(Qt.Key_F)
		self.fullScreenMenuAction.triggered.connect(self.toggleFullScreen)
		self.contextMenu.addAction(self.fullScreenMenuAction)

		self.statusBarMenuAction = QAction("Status Bar")
		self.statusBarMenuAction.setCheckable(True)
		self.statusBarMenuAction.setChecked(False if self.statusBar().isHidden() else True)
		self.statusBarMenuAction.setShortcut(Qt.Key_B)
		self.statusBarMenuAction.triggered.connect(self.toggleStatusBar)
		self.contextMenu.addAction(self.statusBarMenuAction)

		self.contextMenu.addSeparator()
		self.contextMenu.addAction("Zoom In",       lambda: self.setScale(self.scaleFactor*1.2), "+")
		self.contextMenu.addAction("Zoom Out",      lambda: self.setScale(self.scaleFactor*0.8), "-")
		self.contextMenu.addAction("Zoom 1:1",      lambda: self.setScale(1),                    "/")
		self.contextMenu.addAction("Zoom Best Fit", lambda: self.setScaleBestFit(),              "*")

		self.zoomLockMenuAction = QAction("Zoom Lock")
		self.zoomLockMenuAction.setCheckable(True)
		self.zoomLockMenuAction.setChecked(self.zoomLock)
		self.zoomLockMenuAction.setShortcut(Qt.CTRL|Qt.Key_Slash)
		self.zoomLockMenuAction.triggered.connect(self.toggleZoomLock)
		self.contextMenu.addAction(self.zoomLockMenuAction)

		self.windowAutoResizeMenuAction = QAction("Auto-Resize Window")
		self.windowAutoResizeMenuAction.setCheckable(True)
		self.windowAutoResizeMenuAction.setChecked(self.windowAutoResize)
		self.windowAutoResizeMenuAction.triggered.connect(self.toggleWindowAutoResize)
		self.contextMenu.addAction(self.windowAutoResizeMenuAction)

		self.contextMenu.addAction("Save Currents Preferences to Defaults", self.writeConfig)

		self.contextMenu.addSeparator()
		self.contextMenu.addAction("Open...", self.openFileDialog, "Ctrl+O")
		self.contextMenu.addAction("Copy Image to Clipboard", self.clipBoardCopy, "Ctrl+C")
		self.contextMenu.addAction("Edit Description", self.editDescription, "Ctrl+D")
		self.contextMenu.addAction("Run Editor (%s)" % (os.path.basename(self.imgEditor)), self.runEditor, "Ctrl+E")
		self.contextMenu.addAction("Rename", self.renameFile, "F2")
		self.contextMenu.addAction("Delete", self.deleteFile, "Del")

		self.contextMenu.addSeparator()
		self.contextMenu.addAction("About", self.about)
		self.contextMenu.addAction("Close", self.close, "Esc")

	def about(self):
		txt = "Jaggimage Viewer (2025) cLxJaguar\n\n"\
		      "This is an everyday fast and lightweight image viewer in Python and Qt having "\
		      "just the functionalities on the old ACDSee version I was used to.\n\n"\
		      "This program is under free software licence.\n\n"\
		      "Visit GitHub page?"
		a = QMessageBox.information(self, WINDOW_TITLE+' '+version, txt, QMessageBox.Yes|QMessageBox.No)
		if a == QMessageBox.Yes:
			QDesktopServices.openUrl(QUrl("https://github.com/clxjaguar/jaggimage-viewer"))

	def openFileDialog(self):
		filterStr = "Images files (%s);;No filter... (*)" % (" ".join(['*'+ext for ext in IMG_EXT]))
		dirPath = os.path.dirname(self.filename) if self.filename is not None else '.'
		files = QFileDialog.getOpenFileNames(self, "Select one or more files...", dirPath, filter=filterStr)[0]
		if len(files):
			self.files, self.fileIndex = files, 0
			self.loadImage(self.files[self.fileIndex])
			if len(self.files) == 1:
				QTimer.singleShot(100, self.listImagesInSameDirectory)
			else:
				self.preloadNextImageTimer.start(200)
				self.preloadPreviousImageTimer.start(300)

	def loadImage(self, filename, preloadedPixmap=None, firstRun=False):
		self.imageDescription = ""
		if filename is None:
			self.filename, self.pixmap, self.image = None, QPixmap(), None
			self.imageLabel.setText("Nothing to display.")
			self.imageLabel.adjustSize()
			self.updateWindowTitleAndStatusBar()
			return
		elif preloadedPixmap is not None:
			self.filename, self.pixmap, self.image = filename, preloadedPixmap, None
			print("Using PRELOADED pixmap of", filename)
		elif isinstance(filename, QImage):
			self.filename = None
			self.pixmap = QPixmap.fromImage(filename)
		else:
			self.filename = filename
			t = time.time()
			reader = QImageReader(filename)
			reader.setAutoTransform(True)
			self.image = reader.read()
			print("Load file: %.2f ms" % ((time.time() - t)*1000.0))

			if self.image.isNull():
				self.pixmap = QPixmap()
				self.imageLabel.setText("%s:\n%s" % (self.filename, reader.errorString()))
				self.imageLabel.adjustSize()
				self.updateWindowTitleAndStatusBar()
				self.setIconFromPixmapTimer.start(300)
				return

			t = time.time()
			self.pixmap = QPixmap.fromImage(self.image)
			print("Making pixmap: %.2f ms" % ((time.time() - t)*1000.0))

		if self.pixmap.isNull():
			self.imageLabel.setText("Error: Pixmap is empty.")
			self.imageLabel.adjustSize()
		else:
			self.imageLabel.setPixmap(self.pixmap)

			if self.zoomLock:
				self.setScale(self.scaleFactor)
				self.scrollArea.setPositionAbs(0, 0)
			else:
				self.imageLabel.adjustSize()
				self.scaleFactor = 1
				self.setScaleBestFitIfLargerToScreenOnly(firstRun)
				if not self.fullScreen and self.windowAutoResize:
					w, h = int(self.scaleFactor*self.pixmap.width()), int(self.scaleFactor*self.pixmap.height())
					self.resize(w, h)

		self.setIconFromPixmapTimer.start(300)
		self.getDescriptionTimer.start(200)
		self.updateWindowTitleAndStatusBar()

	def setIconFromPixmap(self):
		self.setWindowFilePath(self.filename)
		if self.pixmap.isNull():
			self.setWindowIcon(QIcon())
			return

		icon = QIcon()
		p = self.pixmap.scaled(100, 100)
		icon.addPixmap(p)
		self.setWindowIcon(icon)

	def getDescription(self):
		if self.filename is None:
			self.imageDescription = ""
			return

		try:
			# Try to read a text file for description
			txtFilename = DescriptionEditor.txtFilename(self.filename)
			self.imageDescription = DescriptionEditor.readDescriptionFile(txtFilename)
			self.updateWindowTitleAndStatusBar()
			return
		except FileNotFoundError:
			pass

		try:
			# Legacy ACDSee description file
			self.imageDescription = DescriptionEditor.readAcdDescriptionFile(self.filename)
			self.updateWindowTitleAndStatusBar()
			return
		except (FileNotFoundError, ValueError):
			pass

		self.imageDescription = ""

	def listImagesInSameDirectory(self):
		t = time.time()
		if self.filename is None:
			self.dirname = os.path.abspath(".")
			self.files = list_dir_img_abs(self.dirname)
		else:
			self.dirname, basename = os.path.split(os.path.abspath(self.filename))
			self.files = list_dir_img_abs(self.dirname)
			try:
				self.fileIndex = self.files.index(os.path.abspath(self.filename))
			except ValueError:
				self.fileIndex = 0
				self.files.insert(0, self.filename)

		print("List, filter and sort filenames: %.2f ms" % ((time.time() - t)*1000.0))
		self.updateWindowTitleAndStatusBar()
		self.preloadNextImageTimer.start(100)
		self.preloadPreviousImageTimer.start(150)

	def updateWindowTitleAndStatusBar(self):
		if self.filename is None:
			basename = "(not a file)"
			sizeStr = ""
		else:
			basename = os.path.basename(self.filename)
			try:
				size = os.path.getsize(self.filename)
				if size < 1048576: sizeStr = "%.1f KiB" % (size/1024)
				else:              sizeStr = "%.1f MiB" % (size/1048576)
			except FileNotFoundError:
				sizeStr = "[NOT FOUND]"

		self.setWindowTitle("%s (%d/%d)" % (basename, self.fileIndex+1, len(self.files)))
		self.statusBar().showMessage("%d/%d   %s   %s   %dx%d   %d%%   %s" % (self.fileIndex+1, len(self.files), basename, sizeStr, self.pixmap.width(), self.pixmap.height(), 100*self.scaleFactor, self.imageDescription))

		if self.imageDescription and self.fullScreen:
				self.statusBar().show()

	def preloadPreviousImage(self):
		if len(self.files) == 0: return
		t = time.time()
		i = self.fileIndex - 1
		if i < 0:
			i = len(self.files)-1
		filename = self.files[i]
		print("Start preload of", filename)
		QApplication.setOverrideCursor(Qt.WaitCursor)
		self.prevPixmap = QPixmap(filename)
		QApplication.restoreOverrideCursor()
		if self.prevPixmap.isNull():
			print("Preload \"%s\" into pixmap FAILED" % filename)
			self.prevPixmap = None
			return
		print("Preload \"%s\" into pixmap: %.2f ms" % (filename, (time.time() - t)*1000.0))

	def preloadNextImage(self):
		if len(self.files) == 0: return
		t = time.time()
		i = self.fileIndex + 1
		if i >= len(self.files):
			i = 0
		filename = self.files[i]
		print("Start preload of", filename)
		QApplication.setOverrideCursor(Qt.WaitCursor)
		self.nextPixmap = QPixmap(filename)
		QApplication.restoreOverrideCursor()
		if self.nextPixmap.isNull():
			print("Preload \"%s\" into pixmap FAILED" % filename)
			self.nextPixmap = None
			return
		print("Preload \"%s\" into pixmap: %.2f ms" % (filename, (time.time() - t)*1000.0))

	def loadPreviousImage(self):
		if len(self.files) < 2: return

		self.fileIndex-=1
		if self.fileIndex < 0:
			self.fileIndex = len(self.files)-1

		preloadedPixmap, self.prevPixmap, self.nextPixmap = self.prevPixmap, None, None if self.pixmap.isNull() else self.pixmap
		self.loadImage(self.files[self.fileIndex], preloadedPixmap=preloadedPixmap)
		self.preloadPreviousImageTimer.start(10)

	def loadNextImage(self):
		if len(self.files) < 2: return

		self.fileIndex+=1
		if self.fileIndex >= len(self.files):
			self.fileIndex = 0

		preloadedPixmap, self.prevPixmap, self.nextPixmap = self.nextPixmap, None if self.pixmap.isNull() else self.pixmap, None
		self.loadImage(self.files[self.fileIndex], preloadedPixmap=preloadedPixmap)
		self.preloadNextImageTimer.start(10)

	def loadFirstImage(self):
		if self.fileIndex <= 0:
			return

		self.fileIndex = 0
		self.loadImage(self.files[self.fileIndex])
		self.prevPixmap, self.nextPixmap = None, None
		self.preloadNextImageTimer.start(100)
		self.preloadPreviousImageTimer.start(200)

	def loadLastImage(self):
		if self.fileIndex >= len(self.files) - 1:
			return

		self.fileIndex = len(self.files)-1
		self.loadImage(self.files[self.fileIndex])
		self.prevPixmap, self.nextPixmap = None, None
		self.preloadNextImageTimer.start(100)
		self.preloadPreviousImageTimer.start(200)

	def editDescription(self):
		if os.path.exists(self.filename):
			self.descriptionEditor = DescriptionEditor(self.imageDescription, self.filename)
			self.descriptionEditor.descriptionChanged.connect(self.descriptionChanged)
			if self.fullScreen:
				x = self.geometry().x()
				y = self.geometry().y()
				self.descriptionEditor.move(x+5, y)

	def descriptionChanged(self, descImgFilename, imageDescription):
		print(descImgFilename, self.filename)
		if descImgFilename == self.filename:
			self.imageDescription = imageDescription
			self.updateWindowTitleAndStatusBar()

	def close(self):
		try: self.descriptionEditor.close()
		except: pass

		super().close()

	def setScale(self, scale=None):
		if scale:
			self.scaleFactor = scale
			self.updateWindowTitleAndStatusBar()

		if not self.imageLabel.pixmap():
			return

		w = int(self.scaleFactor * self.imageLabel.pixmap().width())
		h = int(self.scaleFactor * self.imageLabel.pixmap().height())
		xf, yf = self.scrollArea.positionMiddleF()
		self.imageLabel.setScaledContents(True if scale != 1 else False)
		self.imageLabel.resize(w, h)

		if not self.fullScreen and self.windowAutoResize:
			self.resize(w, h)

		self.scrollArea.setPositionMiddleF(xf, yf)

	def setScaleBestFitIfLargerToScreenOnly(self, firstRun=False):
		targetSize = self.getTargetSize(firstRun=firstRun)
		if firstRun:
			# not enough time after show(), so we do not know on what screen will be
			# the window yet (if fullscreen), nor the place taken by window decorations,
			# so, we'll try again soon after that as a workaround
			QTimer.singleShot(1, self.setScaleBestFitIfLargerToScreenOnly)
		targetScaleFactorWidth = targetSize.width() / self.imageLabel.pixmap().width()
		targetScaleFactorHeight = targetSize.height() / self.imageLabel.pixmap().height()
		targetScaleFactor = min(targetScaleFactorWidth, targetScaleFactorHeight)
		if self.scaleFactor > targetScaleFactor: self.setScale(targetScaleFactor)

	def setScaleBestFit(self):
		targetSize = self.getTargetSize()
		targetScaleFactorWidth = targetSize.width() / self.imageLabel.pixmap().width()
		targetScaleFactorHeight = targetSize.height() / self.imageLabel.pixmap().height()

		minTargetScaleFactor = min(targetScaleFactorWidth, targetScaleFactorHeight)
		maxTargetScaleFactor = max(targetScaleFactorWidth, targetScaleFactorHeight)

		if    self.scaleFactor == 1:                   self.setScale(minTargetScaleFactor)
		elif  self.scaleFactor < minTargetScaleFactor: self.setScale(minTargetScaleFactor)
		elif  self.scaleFactor < maxTargetScaleFactor: self.setScale(maxTargetScaleFactor)
		elif  self.scaleFactor > maxTargetScaleFactor: self.setScale(maxTargetScaleFactor)
		else:                                          self.setScale(minTargetScaleFactor)

	def getTargetSize(self, firstRun=False):
		if self.fullScreen:
			return self.screen().size()

		if firstRun or self.windowAutoResize:
			targetSize = self.screen().availableGeometry().size()
			windowDecorationSize = self.frameGeometry().size() - self.size()
			if windowDecorationSize.isValid():
				targetSize-=windowDecorationSize
			return targetSize

		return self.scrollArea.size()


	def toggleFullScreen(self):
		if self.fullScreen:
			self.showNormal()
			if not self.pixmap.isNull():
				w = int(self.pixmap.width()*self.scaleFactor)
				h = int(self.pixmap.height()*self.scaleFactor)
				self.resize(w, h)
			self.fullScreen = False
		else:
			self.showFullScreen()
			self.fullScreen = True

		try: self.fullScreenMenuAction.setChecked(self.fullScreen)
		except: pass

	def toggleStatusBar(self):
		if self.statusBar().isHidden():
			self.statusBar().show()
		else:
			self.statusBar().hide()

		try: self.statusBarMenuAction.setChecked(False if self.statusBar().isHidden() else True)
		except: pass

	def toggleZoomLock(self):
		self.zoomLock = not(self.zoomLock)
		try: self.zoomLockMenuAction.setChecked(self.zoomLock)
		except: pass

	def toggleWindowAutoResize(self):
		self.windowAutoResize = not(self.windowAutoResize)
		try: self.windowAutoResizeMenuAction.setChecked(self.windowAutoResize)
		except: pass
		self.setScale()

	def refresh(self):
		self.listImagesInSameDirectory()
		if self.filename is not None:
			self.loadImage(self.filename)
		else:
			self.loadImage(self.files[0])

	def resize(self, w, h):
		maxSize = self.screen().availableGeometry().size()
		windowDecorationSize = self.frameGeometry().size() - self.size()
		if windowDecorationSize.height() == 0:
			maxSize-=self.windowDecorationSize
		elif windowDecorationSize.isValid():
			self.windowDecorationSize = windowDecorationSize
			maxSize-=windowDecorationSize

		super().resize(min(w, maxSize.width()), min(h, maxSize.height()))

	def runEditor(self):
		self.showNormal()
		self.fullScreen = False
		self.setScale()
		try: self.fullScreenMenuAction.setChecked(False)
		except: pass

		try:
			try:
				Popen([self.imgEditor, self.filename])
			except:
				from subprocess import Popen
				Popen([self.imgEditor, self.filename])

		except Exception as e:
			QMessageBox.warning(self, WINDOW_TITLE, str(e))

	def renameFile(self):
		if self.filename is None: return
		oldFilename = os.path.abspath(self.filename)
		if not os.path.exists(oldFilename): return

		dirPath, oldBasename = os.path.split(oldFilename)

		msg = "Rename \"%s\" to..." % (oldBasename)
		if os.path.exists(DescriptionEditor.txtFilename(oldFilename)):
			renameTxtFile = True
			msg+="\n(the .txt description file will also be renamed)"
		else:
			if self.imageDescription != "":
				msg+="\n(beware: description file NOT FOUND!)"
			renameTxtFile = False

		newFilename, confirm = QInputDialog().getText(self, WINDOW_TITLE, msg, text=oldBasename)
		if not confirm or newFilename == "": return

		newFilename = os.path.abspath("%s/%s" % (dirPath, newFilename))
		if newFilename == oldFilename: return

		if os.path.exists(newFilename):
			QMessageBox.critical(self, WINDOW_TITLE, "\"%s\" already exists in %s" % (os.path.basename(newFilename), dirPath))
			return

		oldFileExt, newFileExt = os.path.splitext(oldFilename)[1], os.path.splitext(newFilename)[1]
		if oldFileExt != newFileExt:
			a = QMessageBox.warning(self, WINDOW_TITLE, "Are you sure you want to change \"%s\" extension to \"%s\"?\n\n(Note: changing filename's extension do not convert file type.)" % (oldFileExt, newFileExt), QMessageBox.Cancel|QMessageBox.Yes, QMessageBox.Cancel)
			if a != QMessageBox.Yes: return

		try:
			os.rename(oldFilename, newFilename)
			self.filename = newFilename
			self.files[self.fileIndex] = newFilename
			self.updateWindowTitleAndStatusBar()
			if renameTxtFile:
				oldTxtFile, newTxtFile = DescriptionEditor.txtFilename(oldFilename), DescriptionEditor.txtFilename(newFilename)
				if oldTxtFile != newTxtFile:
					os.rename(oldTxtFile, newTxtFile)
		except Exception as e:
			QMessageBox.critical(self, WINDOW_TITLE, str(e))

	def deleteFile(self):
		if self.filename is None: return
		filename = self.filename
		a = QMessageBox.warning(self, WINDOW_TITLE, "Are you sure you want to delete the file\n\"%s\"?\n\nThere is NO trash can on this operation." % (filename), QMessageBox.Yes|QMessageBox.Cancel)
		if a == QMessageBox.Yes:
			try:
				os.remove(self.filename)
				self.prevPixmap, self.nextPixmap = None, None
				del self.files[self.fileIndex]
				if self.fileIndex >= len(self.files):
					self.fileIndex = len(self.files)-1
				if len(self.files) == 0:
					self.close()
				else:
					self.loadImage(self.files[self.fileIndex])

			except Exception as e:
				QMessageBox.critical(self, "Delete Error", str(e))

	def clipBoardCopy(self):
		try:
			t = time.time()
			QGuiApplication.clipboard().setPixmap(self.pixmap)
			self.statusBar().showMessage("Copied \"%s\" into clipboard in %.2f ms" % (self.filename, (time.time()-t)*1000.0))
		except Exception as e:
			QMessageBox.warning(self, "Copy error", str(e))

	def clipBoardPaste(self):
		try:
			newImage = QGuiApplication.clipboard().image()
			if newImage.isNull():
				self.statusBar().showMessage("No image in clipboard")
			else:
				self.files, self.fileIndex = [], 0
				self.loadImage(newImage)
		except Exception as e:
			QMessageBox.warning(self, "Paste error", str(e))

	def rotateImage(self, clockWise=False):
		transform = QTransform()
		transform.rotate(90 if clockWise else -90)
		self.pixmap = self.pixmap.transformed(transform)
		self.loadImage(self.filename, self.pixmap)

	def scrollTimerTimeout(self):
		if not self.scrollDeltaX and not self.scrollDeltaY:
			self.scrollTimer.stop()
			return
		self.scrollArea.setPositionDelta(self.scrollDeltaX, self.scrollDeltaY)

	def unhandledException(self, exctype, value, tb):
		import traceback
		print("\n%s: %s" % (exctype.__name__, value))
		tbStr = "\n".join(traceback.extract_tb(tb).format())
		QMessageBox.critical(None, "%s exception at line %d" % (exctype.__name__, tb.tb_lineno), "<p>%s: %s</p><pre>\n%s</pre>" % (exctype.__name__, value, tbStr))

	### Events bellow this line ###

	def dragEnterEvent(self, event):
		if event.mimeData().hasUrls: event.accept()
		else:                        event.ignore()

	def dropEvent(self, event):
		if event.mimeData().hasUrls:
			files = []
			for url in event.mimeData().urls():
				if os.path.isdir(url.toLocalFile()):
					try:
						for f in list_dir_img_abs(url.toLocalFile()):
							files.append(f)
					except Exception as e:
						QMessageBox.critical(self, WINDOW_TITLE, str(e))
				else:
					files.append(url.toLocalFile())

			if len(files) == 0:
				event.ignore()
				return

			event.accept()
			self.prevPixmap, self.nextPixmap = None, None
			self.files, self.fileIndex = files, 0
			self.loadImage(files[self.fileIndex])
			self.preloadNextImageTimer.start(100)
			self.preloadPreviousImageTimer.start(200)
			if len(self.files) == 1:
				QTimer.singleShot(100, self.listImagesInSameDirectory)

		else:
			event.ignore()

	def wheelEvent(self, event):
		d = event.angleDelta().y()

		if event.modifiers() & (Qt.ControlModifier|Qt.ShiftModifier):
			if d > 0 and self.scaleFactor < 10.0:
				self.setScale(min(self.scaleFactor*1.1, 10.0))
			elif d < 0 and self.scaleFactor > 0.05:
				self.setScale(max(self.scaleFactor*0.9, 0.05))
		else:
			if d < 0:
				self.loadNextImage()
			elif d > 0:
				self.loadPreviousImage()

	def mouseDoubleClickEvent(self, event):
		self.toggleFullScreen()

	def contextMenuEvent(self, event):
		self.contextMenuExec(event.globalPos())

	def eventFilter(self, obj, event):
		if isinstance(event, QKeyEvent) and not event.isAutoRepeat():
			match event.type():
				case event.KeyPress:
					if event.modifiers() & (Qt.AltModifier):
						return False

					if event.modifiers() & Qt.ControlModifier: d = 100
					elif event.modifiers() & Qt.ShiftModifier: d = 5
					else:                                      d = 20
				case event.KeyRelease:                         d = 0
				case _: return False

			match event.key():
				case Qt.Key_Left:  self.scrollDeltaX = -d
				case Qt.Key_Right: self.scrollDeltaX = d
				case Qt.Key_Up:    self.scrollDeltaY = -d
				case Qt.Key_Down:  self.scrollDeltaY = d
				case _:            return False

			self.scrollTimer.start(int(1000/60))
			return True
		return False

	def keyPressEvent(self, event):
		match event.key():
			case Qt.Key_Escape | Qt.Key_Q:
				self.close()
				if event.modifiers() & (Qt.ControlModifier|Qt.ShiftModifier):
					QApplication.exit(0)

			case Qt.Key_Asterisk:
				self.setScaleBestFit()

			case Qt.Key_Slash:
				if event.modifiers() & Qt.ControlModifier:
					self.toggleZoomLock()
				else:
					self.setScale(1)

			case Qt.Key_Plus:
				if self.scaleFactor < 10.0:
					self.setScale(min(self.scaleFactor*1.1, 10.0))

			case Qt.Key_Minus:
				if self.scaleFactor > 0.05:
					self.setScale(max(self.scaleFactor*0.9, 0.05))

			case Qt.Key_F2:
				self.renameFile()

			case Qt.Key_F5:
				self.refresh()

			case Qt.Key_F10:
				self.contextMenuExec(self.pos())

			case Qt.Key_B:
				self.toggleStatusBar()

			case Qt.Key_D:
				if event.modifiers() & Qt.ControlModifier:
					self.editDescription()

			case Qt.Key_E:
				if event.modifiers() & Qt.ControlModifier:
					self.runEditor()

			case Qt.Key_F | Qt.Key_F11:
				self.toggleFullScreen()

			case Qt.Key_O:
				if event.modifiers() & Qt.ControlModifier:
					self.openFileDialog()

			case Qt.Key_Home:
				self.loadFirstImage()

			case Qt.Key_End:
				self.loadLastImage()

			case Qt.Key_Space | Qt.Key_PageDown:
				self.loadNextImage()

			case Qt.Key_Backspace | Qt.Key_PageUp:
				self.loadPreviousImage()

			case Qt.Key_Left:
				if event.modifiers() & (Qt.AltModifier):
					self.rotateImage(clockWise=False)

			case Qt.Key_Right:
				if event.modifiers() & (Qt.AltModifier):
					self.rotateImage(clockWise=True)

			case Qt.Key_C:
				if event.modifiers() & Qt.ControlModifier:
					self.clipBoardCopy()

			case Qt.Key_V:
				if event.modifiers() & Qt.ControlModifier:
					self.clipBoardPaste()

			case Qt.Key_W:
				if event.modifiers() & Qt.ControlModifier:
					self.close()

			case Qt.Key_Delete:
				self.deleteFile()


class CustomMovableScrollArea(QScrollArea):
	def __init__(self):
		super().__init__()
		self.setStyleSheet("border: 0px;")
		self.horizontalScrollBar().setStyleSheet("QScrollBar { height:0px; }");
		self.verticalScrollBar().setStyleSheet("QScrollBar { width:0px; }");
		self.setAlignment(Qt.AlignVCenter|Qt.AlignHCenter)
		self.setCursor(Qt.OpenHandCursor)

	def setPositionDelta(self, dx, dy):
		self.horizontalScrollBar().setValue(self.horizontalScrollBar().value() + dx)
		self.verticalScrollBar().setValue(self.verticalScrollBar().value() + dy)

	def setPositionAbs(self, x, y):
		self.horizontalScrollBar().setValue(x)
		self.verticalScrollBar().setValue(y)

	def positionMiddleF(self):
		x = (self.horizontalScrollBar().value()+self.size().width()/2) / (self.horizontalScrollBar().maximum()+self.size().width())
		y = (self.verticalScrollBar().value()+self.size().height()/2) / (self.verticalScrollBar().maximum()+self.size().height())
		return x, y

	def setPositionMiddleF(self, x=.5, y=.5):
		self.horizontalScrollBar().setValue(int(x*(self.horizontalScrollBar().maximum() + self.size().width()) - self.size().width()/2))
		self.verticalScrollBar().setValue(int(y*(self.verticalScrollBar().maximum() + self.size().height()) - self.size().height()/2))

	def mouseMoveEvent(self, event):
		cursorPos = QCursor().pos()
		newScrollBarPos = self.scrollBarRef - cursorPos + self.refPos

		self.horizontalScrollBar().setValue(newScrollBarPos.x())
		self.verticalScrollBar().setValue(newScrollBarPos.y())

		if not self.parent().fullScreen:
			windowMove = QPoint()
			if newScrollBarPos.x() > self.horizontalScrollBar().maximum():
				windowMove.setX(newScrollBarPos.x() - self.horizontalScrollBar().maximum())
			elif newScrollBarPos.x() < 0:
				windowMove.setX(newScrollBarPos.x())
			if newScrollBarPos.y() > self.verticalScrollBar().maximum():
				windowMove.setY(newScrollBarPos.y() - self.verticalScrollBar().maximum())
			elif newScrollBarPos.y() < 0:
				windowMove.setY(newScrollBarPos.y())

			if windowMove:
				newParentPosition = self.parentRefPos - windowMove
				self.parent().move(newParentPosition)
				self.refPos, self.parentRefPos = cursorPos, newParentPosition
				self.scrollBarRef = QPoint(self.horizontalScrollBar().value(), self.verticalScrollBar().value())

		event.ignore()

	def mousePressEvent(self, event):
		self.refPos, self.parentRefPos = QCursor().pos(), self.parent().pos()
		self.scrollBarRef = QPoint(self.horizontalScrollBar().value(), self.verticalScrollBar().value())
		self.setCursor(Qt.ClosedHandCursor)

	def mouseReleaseEvent(self, event):
		self.setCursor(Qt.OpenHandCursor)

	def wheelEvent(self, event):
		event.ignore()

	def keyPressEvent(self, event):
		self.setCursor(Qt.OpenHandCursor)
		event.ignore()


class DescriptionEditor(QDialog):
	descriptionChanged = pyqtSignal(str, str)
	def __init__(self, description, imgFilename):
		super().__init__()
		self.imgFilename = imgFilename
		layout = QVBoxLayout(self)
		layout.setContentsMargins(0, 0, 0, 0)
		layout.setSpacing(0)
		self.textEdit = self.CustomQPlainTextEdit(description)
		self.textEdit.textChanged.connect(self.textChanged)
		layout.addWidget(self.textEdit)
		hlayout = QHBoxLayout()
		layout.addLayout(hlayout)
		self.cancelBtn = QPushButton("&Close")
		self.cancelBtn.clicked.connect(super().close)
		self.saveBtn = QPushButton("&Save to .txt")
		self.saveBtn.clicked.connect(self.saveToTxt)

		for w in self.cancelBtn, self.saveBtn:
			w.setFocusPolicy(Qt.NoFocus)
			w.hide()
			hlayout.addWidget(w)

		self.setWindowTitle(os.path.basename(self.imgFilename))
		self.show()

	class CustomQPlainTextEdit(QPlainTextEdit):
		def keyPressEvent(self, event):
			key = event.key()
			match key:
				case Qt.Key_Escape:
					self.parent().close()
				case Qt.Key_Plus:
					if event.modifiers() & Qt.ControlModifier:
						self.zoomIn()
						return
				case Qt.Key_Minus:
					if event.modifiers() & Qt.ControlModifier:
						self.zoomOut()
						return

			super().keyPressEvent(event)

		def wheelEvent(self, event):
			if event.modifiers() & (Qt.ControlModifier|Qt.ShiftModifier):
				d = event.angleDelta().y()
				if d > 0:
					self.zoomIn()
					return
				elif d < 0:
					self.zoomOut()
					return

			super().wheelEvent(event)

	def textChanged(self):
		for w in self.cancelBtn, self.saveBtn:
			w.show()

	def saveToTxt(self):
		with open(self.txtFilename(self.imgFilename), 'w') as fd:
			fd.write(self.textEdit.toPlainText()+"\n")
			fd.close()
		for w in self.cancelBtn, self.saveBtn:
			w.hide()
		self.descriptionChanged.emit(self.imgFilename, self.textEdit.toPlainText())


	@staticmethod
	def txtFilename(imgFilename):
		return os.path.splitext(imgFilename)[0]+'.txt'

	@staticmethod
	def readDescriptionFile(txtFilename):
		try:
			return open(txtFilename).read().strip()
		except UnicodeDecodeError:
			return open(txtFilename, encoding="windows-1252", errors="ignore").read().strip()

	@staticmethod
	def readAcdDescriptionFile(imgFilename):
		basename = os.path.basename(imgFilename)
		acdDescFile = os.path.dirname(os.path.abspath(imgFilename))+'/descript.ion'
		for line in open(acdDescFile, 'rb').read().decode('windows-1252', errors='ignore').split('\n'):
			try:
				if line[0] == '"':
					p = line.find('"', 1)
					f, d = line[1:p], line[p+1:]
				else:
					f, d = line.split(' ', 1)
			except:
				continue

			if f == basename:
				imageDescription = "\n\n".join(filter(lambda s: len(s), map(str.strip, d.strip().split('   '))))
				return imageDescription

		raise ValueError


def is_image_ext(filename):
	return os.path.splitext(filename)[1].lower() in IMG_EXT

def list_dir_img_abs(path='.'):
	return list(map(lambda f: os.path.abspath(path+'/'+f), sorted(filter(is_image_ext, os.listdir(path)), key=str.casefold)))

def main():
	app = QApplication(sys.argv)

	files = list(filter(lambda a: not a.startswith('-'), sys.argv[1:]))
	match len(files):
		case 0: # no paths given
			w = ImageViewer()
		case 1: # exactly one path given
			w = ImageViewer(files[0])
		case _: # more than one path in arguments
			w = ImageViewer(files[0], filesList=files)

	sys.exit(app.exec_())

if __name__ == '__main__':
	main()


