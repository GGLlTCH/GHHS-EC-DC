"""
GHHS-EC&DC - Secure Encryption/Decryption Tool
Modern AES-256-GCM encryption with theme switching.
"""

import sys
import os
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, 
    QTextEdit, QPushButton, QLabel, QWidget, QFileDialog, 
    QMessageBox, QProgressBar, QGroupBox, QTabWidget,
    QFrame, QSizePolicy
)
from PyQt6.QtCore import QThread, pyqtSignal, Qt
from PyQt6.QtGui import QFont, QIcon, QPalette, QColor

# Добавляем импорт функций шифрования
from secure_crypto import aes_encrypt, aes_decrypt, DecryptionError


class CryptoThread(QThread):
    """Thread for encryption/decryption operations."""
    
    finished_signal = pyqtSignal(bytes, str)  # data, operation_type
    error_signal = pyqtSignal(str)
    progress_signal = pyqtSignal(int)
    
    def __init__(self, operation_type, data, password):
        super().__init__()
        self.operation_type = operation_type
        self.data = data
        self.password = password
    
    def run(self):
        try:
            self.progress_signal.emit(30)
            
            if self.operation_type == 'encrypt':
                result = aes_encrypt(self.data, self.password)
            else:
                result = aes_decrypt(self.data, self.password)
            
            self.progress_signal.emit(100)
            self.finished_signal.emit(result, self.operation_type)
            
        except Exception as e:
            self.error_signal.emit(str(e))


class Translation:
    """Translation class for multilingual support."""
    
    translations = {
        'en': {
            'app_title': 'GHHS-EC&DC - Secure Encryption Tool',
            'encryption_tab': 'ENCRYPTION',
            'decryption_tab': 'DECRYPTION',
            'encryption_key': 'Encryption Key',
            'decryption_key': 'Decryption Key',
            'input_text': 'Input Text',
            'encrypted_text': 'Encrypted Text',
            'encrypt_button': 'Encrypt',
            'decrypt_button': 'Decrypt',
            'clear_button': 'Clear All',
            'result': 'Result',
            'encryption_success': 'Encryption successful!',
            'decryption_success': 'Decryption successful!',
            'file_operations': 'File Operations',
            'select_file_encrypt': 'Select File to Encrypt',
            'select_file_decrypt': 'Select Encrypted File',
            'encrypt_file': 'Encrypt File',
            'decrypt_file': 'Decrypt File',
            'no_file_selected': 'No file selected',
            'file_selected': 'File selected: {}',
            'language': 'Language',
            'theme': 'Theme',
            'dark_theme': 'Dark Theme',
            'light_theme': 'Light Theme',
            'switch_theme': 'Switch Theme',
            'switch_language': 'Switch Language',
            'enter_password': 'Enter your encryption key...',
            'enter_text_encrypt': 'Enter text to encrypt...',
            'enter_text_decrypt': 'Enter encrypted text (hex)...',
            'output_placeholder': 'Result will appear here...',
            'error_no_password': 'Please enter encryption key',
            'error_no_input': 'Please enter text to process',
            'error_invalid_hex': 'Invalid hex format',
            'error_no_file': 'Please select a file first',
            'success_file_saved': 'File saved successfully! Size: {} bytes'
        },
        'ru': {
            'app_title': 'GHHS-EC&DC - Программа Шифрования',
            'encryption_tab': 'ШИФРОВАНИЕ',
            'decryption_tab': 'ДЕШИФРОВАНИЕ',
            'encryption_key': 'Ключ шифрования',
            'decryption_key': 'Ключ дешифрования',
            'input_text': 'Исходный текст',
            'encrypted_text': 'Зашифрованный текст',
            'encrypt_button': 'Зашифровать',
            'decrypt_button': 'Расшифровать',
            'clear_button': 'Очистить всё',
            'result': 'Результат',
            'encryption_success': 'Шифрование успешно!',
            'decryption_success': 'Дешифрование успешно!',
            'file_operations': 'Работа с файлами',
            'select_file_encrypt': 'Выбрать файл для шифрования',
            'select_file_decrypt': 'Выбрать зашифрованный файл',
            'encrypt_file': 'Зашифровать файл',
            'decrypt_file': 'Расшифровать файл',
            'no_file_selected': 'Файл не выбран',
            'file_selected': 'Выбран файл: {}',
            'language': 'Язык',
            'theme': 'Тема',
            'dark_theme': 'Тёмная Тема',
            'light_theme': 'Светлая Тема',
            'switch_theme': 'Сменить Тему',
            'switch_language': 'Сменить Язык',
            'enter_password': 'Введите ключ шифрования...',
            'enter_text_encrypt': 'Введите текст для шифрования...',
            'enter_text_decrypt': 'Введите зашифрованный текст (hex)...',
            'output_placeholder': 'Результат появится здесь...',
            'error_no_password': 'Пожалуйста, введите ключ шифрования',
            'error_no_input': 'Пожалуйста, введите текст для обработки',
            'error_invalid_hex': 'Неверный hex формат',
            'error_no_file': 'Пожалуйста, сначала выберите файл',
            'success_file_saved': 'Файл сохранен успешно! Размер: {} байт'
        }
    }
    
    def __init__(self):
        self.current_lang = 'en'
    
    def set_language(self, lang):
        """Set current language."""
        self.current_lang = lang
    
    def tr(self, key):
        """Translate key to current language."""
        return self.translations[self.current_lang].get(key, key)


class SecureCryptoGUI(QMainWindow):
    """Main application window with modern design and theme switching."""
    
    def __init__(self):
        super().__init__()
        self.translator = Translation()
        self.dark_theme = True  # По умолчанию тёмная тема
        self.current_language = 'en'  # По умолчанию английский
        self.init_ui()
        
    def init_ui(self):
        """Initialize the user interface."""
        self.setWindowTitle(self.translator.tr('app_title'))
        # Уменьшаем размер окна
        self.setGeometry(100, 100, 900, 650)
        
        # Set window icon
        if os.path.exists("icon.png"):
            self.setWindowIcon(QIcon("icon.png"))
        
        # Apply the default dark theme
        self.apply_theme()
        
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout with consistent spacing
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)
        
        # Header with language and theme selection
        header_frame = QFrame()
        header_frame.setObjectName("headerFrame")
        header_frame.setFixedHeight(80)  # Увеличиваем высоту хедера
        header_layout = QHBoxLayout(header_frame)
        header_layout.setContentsMargins(20, 15, 20, 15)  # Увеличиваем вертикальные отступы
        header_layout.setSpacing(15)
        
        # App title - исправляем логотип
        title_label = QLabel("GHHS-EC&DC")
        title_label.setObjectName("titleLabel")
        title_label.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        header_layout.addWidget(title_label)
        
        # Control buttons layout
        controls_layout = QHBoxLayout()
        controls_layout.setSpacing(10)
        
        # Theme switch button
        self.theme_button = QPushButton(self.translator.tr('switch_theme'))
        self.theme_button.setObjectName("themeButton")
        self.theme_button.setFixedSize(140, 40)  # Увеличиваем высоту кнопки
        self.theme_button.clicked.connect(self.switch_theme)
        
        # Language switch button
        self.language_button = QPushButton(self.translator.tr('switch_language'))
        self.language_button.setObjectName("languageButton")
        self.language_button.setFixedSize(140, 40)  # Увеличиваем высоту кнопки
        self.language_button.clicked.connect(self.switch_language)
        
        controls_layout.addWidget(self.theme_button)
        controls_layout.addWidget(self.language_button)
        header_layout.addLayout(controls_layout)
        
        main_layout.addWidget(header_frame)
        
        # Create tabs
        self.tabs = QTabWidget()
        self.tabs.setObjectName("mainTabs")
        
        # Encryption tab
        encrypt_tab = QWidget()
        self.setup_encrypt_tab(encrypt_tab)
        self.tabs.addTab(encrypt_tab, self.translator.tr('encryption_tab'))
        
        # Decryption tab
        decrypt_tab = QWidget()
        self.setup_decrypt_tab(decrypt_tab)
        self.tabs.addTab(decrypt_tab, self.translator.tr('decryption_tab'))
        
        main_layout.addWidget(self.tabs)
        
    def apply_theme(self):
        """Apply the current theme (dark or light)."""
        if self.dark_theme:
            # High contrast dark theme - убираем неподдерживаемые свойства
            self.setStyleSheet("""
                QMainWindow {
                    background-color: #0d1117;
                    color: #ffffff;
                }
                QFrame#headerFrame {
                    background-color: #161b22;
                    border-radius: 12px;
                    border: 2px solid #30363d;
                }
                QLabel#titleLabel {
                    font-size: 28px;
                    font-weight: 800;
                    color: #58a6ff;
                    padding: 0px;
                }
                QPushButton#themeButton, QPushButton#languageButton {
                    background-color: #21262d;
                    color: #c9d1d9;
                    border: 2px solid #30363d;
                    border-radius: 10px;
                    font-weight: 600;
                    font-size: 13px;
                    padding: 8px 4px;  /* Добавляем внутренние отступы */
                }
                QPushButton#themeButton:hover, QPushButton#languageButton:hover {
                    background-color: #30363d;
                    border: 2px solid #58a6ff;
                }
                QPushButton#themeButton:pressed, QPushButton#languageButton:pressed {
                    background-color: #0d1117;
                    border: 2px solid #8e6cff;
                }
                QTabWidget#mainTabs::pane {
                    border: 2px solid #30363d;
                    border-radius: 12px;
                    background-color: #161b22;
                }
                QTabBar::tab {
                    background-color: #21262d;
                    color: #8b949e;
                    padding: 12px 24px;
                    margin: 3px;
                    border: 2px solid #30363d;
                    border-radius: 10px;
                    font-weight: 600;
                    font-size: 13px;
                }
                QTabBar::tab:selected {
                    background-color: #1f6feb;
                    color: #ffffff;
                    border: 2px solid #58a6ff;
                }
                QTabBar::tab:hover {
                    background-color: #30363d;
                    color: #c9d1d9;
                }
                QGroupBox {
                    font-weight: 700;
                    border: 2px solid #30363d;
                    border-radius: 12px;
                    margin-top: 15px;
                    padding-top: 20px;
                    color: #f0f6fc;
                    background-color: #21262d;
                    font-size: 14px;
                }
                QGroupBox::title {
                    subcontrol-origin: margin;
                    left: 15px;
                    padding: 0 12px 0 12px;
                    color: #58a6ff;
                    background-color: #21262d;
                    font-weight: 700;
                }
                QTextEdit {
                    background-color: #0d1117;
                    color: #f0f6fc;
                    border: 2px solid #30363d;
                    border-radius: 10px;
                    padding: 12px;
                    font-family: 'Segoe UI', system-ui, sans-serif;
                    font-size: 13px;
                    selection-background-color: #1f6feb;
                    selection-color: #ffffff;
                }
                QTextEdit:focus {
                    border: 2px solid #58a6ff;
                    background-color: #161b22;
                }
                QPushButton {
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #1f6feb, stop:1 #8e6cff);
                    color: #ffffff;
                    border: none;
                    padding: 12px 24px;
                    border-radius: 10px;
                    font-weight: 700;
                    font-size: 13px;
                    min-width: 120px;
                }
                QPushButton:hover {
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #58a6ff, stop:1 #a371f7);
                }
                QPushButton:pressed {
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #0d419d, stop:1 #6e40c9);
                }
                QPushButton:disabled {
                    background-color: #30363d;
                    color: #8b949e;
                }
                QLabel {
                    color: #f0f6fc;
                    font-weight: 600;
                    font-size: 13px;
                    background-color: transparent;
                }
                QProgressBar {
                    border: 2px solid #30363d;
                    border-radius: 10px;
                    text-align: center;
                    color: #ffffff;
                    font-weight: 600;
                    background-color: #0d1117;
                    font-size: 11px;
                    height: 18px;
                }
                QProgressBar::chunk {
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #1f6feb, stop:1 #8e6cff);
                    border-radius: 8px;
                }
                QMessageBox {
                    background-color: #161b22;
                    color: #ffffff;
                    border: 2px solid #30363d;
                    border-radius: 12px;
                }
                QMessageBox QLabel {
                    color: #ffffff;
                }
                QMessageBox QPushButton {
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #1f6feb, stop:1 #8e6cff);
                    color: #ffffff;
                    border: none;
                    padding: 8px 16px;
                    border-radius: 8px;
                    min-width: 70px;
                    font-weight: 600;
                }
                QMessageBox QPushButton:hover {
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #58a6ff, stop:1 #a371f7);
                }
            """)
        else:
            # High contrast light theme - убираем неподдерживаемые свойства
            self.setStyleSheet("""
                QMainWindow {
                    background-color: #ffffff;
                    color: #24292f;
                }
                QFrame#headerFrame {
                    background-color: #f6f8fa;
                    border-radius: 12px;
                    border: 2px solid #d0d7de;
                }
                QLabel#titleLabel {
                    font-size: 28px;
                    font-weight: 800;
                    color: #0969da;
                    padding: 0px;
                }
                QPushButton#themeButton, QPushButton#languageButton {
                    background-color: #ffffff;
                    color: #24292f;
                    border: 2px solid #d0d7de;
                    border-radius: 10px;
                    font-weight: 600;
                    font-size: 13px;
                    padding: 8px 4px;  /* Добавляем внутренние отступы */
                }
                QPushButton#themeButton:hover, QPushButton#languageButton:hover {
                    background-color: #f6f8fa;
                    border: 2px solid #0969da;
                }
                QPushButton#themeButton:pressed, QPushButton#languageButton:pressed {
                    background-color: #eaeef2;
                    border: 2px solid #8250df;
                }
                QTabWidget#mainTabs::pane {
                    border: 2px solid #d0d7de;
                    border-radius: 12px;
                    background-color: #ffffff;
                }
                QTabBar::tab {
                    background-color: #f6f8fa;
                    color: #656d76;
                    padding: 12px 24px;
                    margin: 3px;
                    border: 2px solid #d0d7de;
                    border-radius: 10px;
                    font-weight: 600;
                    font-size: 13px;
                }
                QTabBar::tab:selected {
                    background-color: #0969da;
                    color: #ffffff;
                    border: 2px solid #0969da;
                }
                QTabBar::tab:hover {
                    background-color: #eaeef2;
                    color: #24292f;
                }
                QGroupBox {
                    font-weight: 700;
                    border: 2px solid #d0d7de;
                    border-radius: 12px;
                    margin-top: 15px;
                    padding-top: 20px;
                    color: #24292f;
                    background-color: #f6f8fa;
                    font-size: 14px;
                }
                QGroupBox::title {
                    subcontrol-origin: margin;
                    left: 15px;
                    padding: 0 12px 0 12px;
                    color: #0969da;
                    background-color: #f6f8fa;
                    font-weight: 700;
                }
                QTextEdit {
                    background-color: #ffffff;
                    color: #24292f;
                    border: 2px solid #d0d7de;
                    border-radius: 10px;
                    padding: 12px;
                    font-family: 'Segoe UI', system-ui, sans-serif;
                    font-size: 13px;
                    selection-background-color: #0969da;
                    selection-color: #ffffff;
                }
                QTextEdit:focus {
                    border: 2px solid #0969da;
                    background-color: #f6f8fa;
                }
                QPushButton {
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #0969da, stop:1 #8250df);
                    color: #ffffff;
                    border: none;
                    padding: 12px 24px;
                    border-radius: 10px;
                    font-weight: 700;
                    font-size: 13px;
                    min-width: 120px;
                }
                QPushButton:hover {
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #1a7de8, stop:1 #8a63e0);
                }
                QPushButton:pressed {
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #0757b8, stop:1 #6b45b5);
                }
                QPushButton:disabled {
                    background-color: #d0d7de;
                    color: #8c959f;
                }
                QLabel {
                    color: #24292f;
                    font-weight: 600;
                    font-size: 13px;
                    background-color: transparent;
                }
                QProgressBar {
                    border: 2px solid #d0d7de;
                    border-radius: 10px;
                    text-align: center;
                    color: #24292f;
                    font-weight: 600;
                    background-color: #ffffff;
                    font-size: 11px;
                    height: 18px;
                }
                QProgressBar::chunk {
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #0969da, stop:1 #8250df);
                    border-radius: 8px;
                }
                QMessageBox {
                    background-color: #ffffff;
                    color: #24292f;
                    border: 2px solid #d0d7de;
                    border-radius: 12px;
                }
                QMessageBox QLabel {
                    color: #24292f;
                }
                QMessageBox QPushButton {
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #0969da, stop:1 #8250df);
                    color: #ffffff;
                    border: none;
                    padding: 8px 16px;
                    border-radius: 8px;
                    min-width: 70px;
                    font-weight: 600;
                }
                QMessageBox QPushButton:hover {
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #1a7de8, stop:1 #8a63e0);
                }
            """)
        
    def setup_encrypt_tab(self, tab):
        """Setup the encryption tab."""
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        # Encryption Key
        self.key_group_encrypt = QGroupBox(self.translator.tr('encryption_key'))
        key_layout = QVBoxLayout(self.key_group_encrypt)
        key_layout.setContentsMargins(15, 25, 15, 15)
        key_layout.setSpacing(12)
        self.encrypt_password = QTextEdit()
        self.encrypt_password.setMaximumHeight(80)
        self.encrypt_password.setPlaceholderText(self.translator.tr('enter_password'))
        key_layout.addWidget(self.encrypt_password)
        layout.addWidget(self.key_group_encrypt)
        
        # Input Text
        self.input_group_encrypt = QGroupBox(self.translator.tr('input_text'))
        input_layout = QVBoxLayout(self.input_group_encrypt)
        input_layout.setContentsMargins(15, 25, 15, 15)
        input_layout.setSpacing(12)
        self.encrypt_input = QTextEdit()
        self.encrypt_input.setMinimumHeight(120)
        self.encrypt_input.setPlaceholderText(self.translator.tr('enter_text_encrypt'))
        input_layout.addWidget(self.encrypt_input)
        layout.addWidget(self.input_group_encrypt)
        
        # Buttons
        button_layout = QHBoxLayout()
        button_layout.setSpacing(12)
        self.encrypt_btn = QPushButton(self.translator.tr('encrypt_button'))
        self.encrypt_btn.clicked.connect(self.encrypt_text)
        
        self.clear_encrypt_btn = QPushButton(self.translator.tr('clear_button'))
        self.clear_encrypt_btn.clicked.connect(self.clear_encrypt)
        
        button_layout.addWidget(self.encrypt_btn)
        button_layout.addWidget(self.clear_encrypt_btn)
        button_layout.addStretch()
        layout.addLayout(button_layout)
        
        # Progress
        self.encrypt_progress = QProgressBar()
        self.encrypt_progress.setVisible(False)
        layout.addWidget(self.encrypt_progress)
        
        # Result
        self.result_group_encrypt = QGroupBox(self.translator.tr('result'))
        result_layout = QVBoxLayout(self.result_group_encrypt)
        result_layout.setContentsMargins(15, 25, 15, 15)
        result_layout.setSpacing(12)
        self.encrypt_output = QTextEdit()
        self.encrypt_output.setReadOnly(True)
        self.encrypt_output.setMinimumHeight(120)
        self.encrypt_output.setPlaceholderText(self.translator.tr('output_placeholder'))
        result_layout.addWidget(self.encrypt_output)
        layout.addWidget(self.result_group_encrypt)
        
        # File operations
        self.file_group_encrypt = QGroupBox(self.translator.tr('file_operations'))
        file_layout = QVBoxLayout(self.file_group_encrypt)
        file_layout.setContentsMargins(15, 25, 15, 15)
        file_layout.setSpacing(12)
        
        self.encrypt_file_info = QLabel(self.translator.tr('no_file_selected'))
        if self.dark_theme:
            self.encrypt_file_info.setStyleSheet("color: #8b949e; font-style: italic; font-weight: 500;")
        else:
            self.encrypt_file_info.setStyleSheet("color: #656d76; font-style: italic; font-weight: 500;")
        
        file_btn_layout = QHBoxLayout()
        file_btn_layout.setSpacing(12)
        self.select_encrypt_file_btn = QPushButton(self.translator.tr('select_file_encrypt'))
        self.select_encrypt_file_btn.clicked.connect(self.select_file_for_encryption)
        
        self.encrypt_file_btn = QPushButton(self.translator.tr('encrypt_file'))
        self.encrypt_file_btn.clicked.connect(self.encrypt_file)
        
        file_btn_layout.addWidget(self.select_encrypt_file_btn)
        file_btn_layout.addWidget(self.encrypt_file_btn)
        
        file_layout.addWidget(self.encrypt_file_info)
        file_layout.addLayout(file_btn_layout)
        layout.addWidget(self.file_group_encrypt)
        
        layout.addStretch()
        self.encrypt_file_path = None
        
    def setup_decrypt_tab(self, tab):
        """Setup the decryption tab."""
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        # Decryption Key
        self.key_group_decrypt = QGroupBox(self.translator.tr('decryption_key'))
        key_layout = QVBoxLayout(self.key_group_decrypt)
        key_layout.setContentsMargins(15, 25, 15, 15)
        key_layout.setSpacing(12)
        self.decrypt_password = QTextEdit()
        self.decrypt_password.setMaximumHeight(80)
        self.decrypt_password.setPlaceholderText(self.translator.tr('enter_password'))
        key_layout.addWidget(self.decrypt_password)
        layout.addWidget(self.key_group_decrypt)
        
        # Encrypted Text
        self.input_group_decrypt = QGroupBox(self.translator.tr('encrypted_text'))
        input_layout = QVBoxLayout(self.input_group_decrypt)
        input_layout.setContentsMargins(15, 25, 15, 15)
        input_layout.setSpacing(12)
        self.decrypt_input = QTextEdit()
        self.decrypt_input.setMinimumHeight(120)
        self.decrypt_input.setPlaceholderText(self.translator.tr('enter_text_decrypt'))
        input_layout.addWidget(self.decrypt_input)
        layout.addWidget(self.input_group_decrypt)
        
        # Buttons
        button_layout = QHBoxLayout()
        button_layout.setSpacing(12)
        self.decrypt_btn = QPushButton(self.translator.tr('decrypt_button'))
        self.decrypt_btn.clicked.connect(self.decrypt_text)
        
        self.clear_decrypt_btn = QPushButton(self.translator.tr('clear_button'))
        self.clear_decrypt_btn.clicked.connect(self.clear_decrypt)
        
        button_layout.addWidget(self.decrypt_btn)
        button_layout.addWidget(self.clear_decrypt_btn)
        button_layout.addStretch()
        layout.addLayout(button_layout)
        
        # Progress
        self.decrypt_progress = QProgressBar()
        self.decrypt_progress.setVisible(False)
        layout.addWidget(self.decrypt_progress)
        
        # Result
        self.result_group_decrypt = QGroupBox(self.translator.tr('result'))
        result_layout = QVBoxLayout(self.result_group_decrypt)
        result_layout.setContentsMargins(15, 25, 15, 15)
        result_layout.setSpacing(12)
        self.decrypt_output = QTextEdit()
        self.decrypt_output.setReadOnly(True)
        self.decrypt_output.setMinimumHeight(120)
        self.decrypt_output.setPlaceholderText(self.translator.tr('output_placeholder'))
        result_layout.addWidget(self.decrypt_output)
        layout.addWidget(self.result_group_decrypt)
        
        # File operations
        self.file_group_decrypt = QGroupBox(self.translator.tr('file_operations'))
        file_layout = QVBoxLayout(self.file_group_decrypt)
        file_layout.setContentsMargins(15, 25, 15, 15)
        file_layout.setSpacing(12)
        
        self.decrypt_file_info = QLabel(self.translator.tr('no_file_selected'))
        if self.dark_theme:
            self.decrypt_file_info.setStyleSheet("color: #8b949e; font-style: italic; font-weight: 500;")
        else:
            self.decrypt_file_info.setStyleSheet("color: #656d76; font-style: italic; font-weight: 500;")
        
        file_btn_layout = QHBoxLayout()
        file_btn_layout.setSpacing(12)
        self.select_decrypt_file_btn = QPushButton(self.translator.tr('select_file_decrypt'))
        self.select_decrypt_file_btn.clicked.connect(self.select_file_for_decryption)
        
        self.decrypt_file_btn = QPushButton(self.translator.tr('decrypt_file'))
        self.decrypt_file_btn.clicked.connect(self.decrypt_file)
        
        file_btn_layout.addWidget(self.select_decrypt_file_btn)
        file_btn_layout.addWidget(self.decrypt_file_btn)
        
        file_layout.addWidget(self.decrypt_file_info)
        file_layout.addLayout(file_btn_layout)
        layout.addWidget(self.file_group_decrypt)
        
        layout.addStretch()
        self.decrypt_file_path = None
        
    def switch_theme(self):
        """Switch between dark and light theme."""
        self.dark_theme = not self.dark_theme
        self.apply_theme()
        self.update_dynamic_styles()
        
    def switch_language(self):
        """Switch between English and Russian."""
        if self.current_language == 'en':
            self.current_language = 'ru'
        else:
            self.current_language = 'en'
        
        self.translator.set_language(self.current_language)
        self.retranslate_ui()
        
    def update_dynamic_styles(self):
        """Update styles that need to be changed dynamically."""
        if self.dark_theme:
            style_selected = "color: #3fb950; font-weight: 600;"
            style_placeholder = "color: #8b949e; font-style: italic; font-weight: 500;"
        else:
            style_selected = "color: #1a7f37; font-weight: 600;"
            style_placeholder = "color: #656d76; font-style: italic; font-weight: 500;"
            
        # Update file info labels
        if hasattr(self, 'encrypt_file_info'):
            if self.encrypt_file_path:
                self.encrypt_file_info.setStyleSheet(style_selected)
            else:
                self.encrypt_file_info.setStyleSheet(style_placeholder)
                
        if hasattr(self, 'decrypt_file_info'):
            if self.decrypt_file_path:
                self.decrypt_file_info.setStyleSheet(style_selected)
            else:
                self.decrypt_file_info.setStyleSheet(style_placeholder)
        
    def retranslate_ui(self):
        """Update all UI texts with current language."""
        self.setWindowTitle(self.translator.tr('app_title'))
        
        # Update tab names
        self.tabs.setTabText(0, self.translator.tr('encryption_tab'))
        self.tabs.setTabText(1, self.translator.tr('decryption_tab'))
        
        # Update control buttons
        self.theme_button.setText(self.translator.tr('switch_theme'))
        self.language_button.setText(self.translator.tr('switch_language'))
        
        # Encryption tab
        self.key_group_encrypt.setTitle(self.translator.tr('encryption_key'))
        self.input_group_encrypt.setTitle(self.translator.tr('input_text'))
        self.result_group_encrypt.setTitle(self.translator.tr('result'))
        self.file_group_encrypt.setTitle(self.translator.tr('file_operations'))
        
        self.encrypt_btn.setText(self.translator.tr('encrypt_button'))
        self.clear_encrypt_btn.setText(self.translator.tr('clear_button'))
        self.select_encrypt_file_btn.setText(self.translator.tr('select_file_encrypt'))
        self.encrypt_file_btn.setText(self.translator.tr('encrypt_file'))
        
        # Update placeholders
        self.encrypt_password.setPlaceholderText(self.translator.tr('enter_password'))
        self.encrypt_input.setPlaceholderText(self.translator.tr('enter_text_encrypt'))
        self.encrypt_output.setPlaceholderText(self.translator.tr('output_placeholder'))
        
        # Decryption tab
        self.key_group_decrypt.setTitle(self.translator.tr('decryption_key'))
        self.input_group_decrypt.setTitle(self.translator.tr('encrypted_text'))
        self.result_group_decrypt.setTitle(self.translator.tr('result'))
        self.file_group_decrypt.setTitle(self.translator.tr('file_operations'))
        
        self.decrypt_btn.setText(self.translator.tr('decrypt_button'))
        self.clear_decrypt_btn.setText(self.translator.tr('clear_button'))
        self.select_decrypt_file_btn.setText(self.translator.tr('select_file_decrypt'))
        self.decrypt_file_btn.setText(self.translator.tr('decrypt_file'))
        
        # Update placeholders
        self.decrypt_password.setPlaceholderText(self.translator.tr('enter_password'))
        self.decrypt_input.setPlaceholderText(self.translator.tr('enter_text_decrypt'))
        self.decrypt_output.setPlaceholderText(self.translator.tr('output_placeholder'))
        
        # Update file info labels
        if self.encrypt_file_path:
            self.encrypt_file_info.setText(self.translator.tr('file_selected').format(os.path.basename(self.encrypt_file_path)))
        else:
            self.encrypt_file_info.setText(self.translator.tr('no_file_selected'))
            
        if self.decrypt_file_path:
            self.decrypt_file_info.setText(self.translator.tr('file_selected').format(os.path.basename(self.decrypt_file_path)))
        else:
            self.decrypt_file_info.setText(self.translator.tr('no_file_selected'))
        
        self.update_dynamic_styles()

    # Остальные методы остаются без изменений
    def encrypt_text(self):
        """Encrypt text from input field."""
        password = self.encrypt_password.toPlainText().strip()
        if not password:
            QMessageBox.warning(self, "Error", self.translator.tr('error_no_password'))
            return
        
        input_data = self.encrypt_input.toPlainText().encode('utf-8')
        if not input_data:
            QMessageBox.warning(self, "Error", self.translator.tr('error_no_input'))
            return
        
        self.start_operation('encrypt', input_data, password, 'encrypt')
    
    def decrypt_text(self):
        """Decrypt text from input field."""
        password = self.decrypt_password.toPlainText().strip()
        if not password:
            QMessageBox.warning(self, "Error", self.translator.tr('error_no_password'))
            return
        
        try:
            input_hex = self.decrypt_input.toPlainText().strip()
            if not input_hex:
                QMessageBox.warning(self, "Error", self.translator.tr('error_no_input'))
                return
            
            input_hex = ''.join(input_hex.split())
            input_data = bytes.fromhex(input_hex)
            
            self.start_operation('decrypt', input_data, password, 'decrypt')
            
        except ValueError:
            QMessageBox.critical(self, "Error", self.translator.tr('error_invalid_hex'))
    
    def select_file_for_encryption(self):
        """Select file for encryption."""
        file_path, _ = QFileDialog.getOpenFileName(self, self.translator.tr('select_file_encrypt'))
        if file_path:
            self.encrypt_file_path = file_path
            self.encrypt_file_info.setText(self.translator.tr('file_selected').format(os.path.basename(file_path)))
            self.update_dynamic_styles()
    
    def select_file_for_decryption(self):
        """Select file for decryption."""
        file_path, _ = QFileDialog.getOpenFileName(self, self.translator.tr('select_file_decrypt'))
        if file_path:
            self.decrypt_file_path = file_path
            self.decrypt_file_info.setText(self.translator.tr('file_selected').format(os.path.basename(file_path)))
            self.update_dynamic_styles()
    
    def encrypt_file(self):
        """Encrypt selected file."""
        if not self.encrypt_file_path:
            QMessageBox.warning(self, "Error", self.translator.tr('error_no_file'))
            return
        
        password = self.encrypt_password.toPlainText().strip()
        if not password:
            QMessageBox.warning(self, "Error", self.translator.tr('error_no_password'))
            return
        
        try:
            with open(self.encrypt_file_path, 'rb') as f:
                file_data = f.read()
            
            self.encrypt_progress.setVisible(True)
            self.start_operation('encrypt', file_data, password, 'encrypt')
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to read file: {str(e)}")
    
    def decrypt_file(self):
        """Decrypt selected file."""
        if not self.decrypt_file_path:
            QMessageBox.warning(self, "Error", self.translator.tr('error_no_file'))
            return
        
        password = self.decrypt_password.toPlainText().strip()
        if not password:
            QMessageBox.warning(self, "Error", self.translator.tr('error_no_password'))
            return
        
        try:
            with open(self.decrypt_file_path, 'rb') as f:
                file_data = f.read()
            
            self.decrypt_progress.setVisible(True)
            self.start_operation('decrypt', file_data, password, 'decrypt')
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to read file: {str(e)}")
    
    def start_operation(self, operation_type, data, password, tab_type):
        """Start encryption/decryption operation."""
        if tab_type == 'encrypt':
            progress_bar = self.encrypt_progress
        else:
            progress_bar = self.decrypt_progress
        
        progress_bar.setVisible(True)
        
        self.thread = CryptoThread(operation_type, data, password)
        self.thread.finished_signal.connect(
            lambda result, op: self.operation_finished(result, op, tab_type))
        self.thread.error_signal.connect(
            lambda error: self.operation_error(error, tab_type))
        self.thread.progress_signal.connect(progress_bar.setValue)
        self.thread.start()
        
        self.set_buttons_enabled(False)
    
    def operation_finished(self, result, operation_type, tab_type):
        """Handle completed operation."""
        if tab_type == 'encrypt':
            self.encrypt_progress.setVisible(False)
            self.handle_encrypt_result(result, operation_type)
        else:
            self.decrypt_progress.setVisible(False)
            self.handle_decrypt_result(result, operation_type)
        
        self.set_buttons_enabled(True)
    
    def handle_encrypt_result(self, result, operation_type):
        """Handle encryption result."""
        hex_result = result.hex()
        self.encrypt_output.setPlainText(hex_result)
        QMessageBox.information(self, "Success", self.translator.tr('encryption_success'))
    
    def handle_decrypt_result(self, result, operation_type):
        """Handle decryption result."""
        try:
            text_result = result.decode('utf-8')
            self.decrypt_output.setPlainText(text_result)
        except UnicodeDecodeError:
            hex_result = result.hex()
            self.decrypt_output.setPlainText(hex_result)
        
        QMessageBox.information(self, "Success", self.translator.tr('decryption_success'))
    
    def operation_error(self, error_message, tab_type):
        """Handle operation error."""
        if tab_type == 'encrypt':
            self.encrypt_progress.setVisible(False)
        else:
            self.decrypt_progress.setVisible(False)
        
        QMessageBox.critical(self, "Error", f"Operation failed:\n{error_message}")
        self.set_buttons_enabled(True)
    
    def set_buttons_enabled(self, enabled):
        """Enable/disable all buttons."""
        buttons = [
            self.encrypt_btn, self.clear_encrypt_btn, self.select_encrypt_file_btn, self.encrypt_file_btn,
            self.decrypt_btn, self.clear_decrypt_btn, self.select_decrypt_file_btn, self.decrypt_file_btn
        ]
        for btn in buttons:
            btn.setEnabled(enabled)
    
    def clear_encrypt(self):
        """Clear encryption tab."""
        self.encrypt_password.clear()
        self.encrypt_input.clear()
        self.encrypt_output.clear()
        self.encrypt_file_info.setText(self.translator.tr('no_file_selected'))
        self.encrypt_file_path = None
        self.update_dynamic_styles()
    
    def clear_decrypt(self):
        """Clear decryption tab."""
        self.decrypt_password.clear()
        self.decrypt_input.clear()
        self.decrypt_output.clear()
        self.decrypt_file_info.setText(self.translator.tr('no_file_selected'))
        self.decrypt_file_path = None
        self.update_dynamic_styles()


def main():
    """Application entry point."""
    app = QApplication(sys.argv)
    app.setApplicationName("GHHS-EC&DC")
    app.setApplicationVersion("1.0.0")
    
    window = SecureCryptoGUI()
    window.show()
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()