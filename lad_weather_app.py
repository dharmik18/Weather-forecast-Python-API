import sys
import os
import requests
import logging
from PyQt5.QtWidgets import QApplication, QWidget, QLineEdit, QPushButton, QLabel, QVBoxLayout, QHBoxLayout
from PyQt5.QtGui import QPixmap, QPainter, QFont
from PyQt5.QtCore import Qt, QDateTime
from PyQt5.QtCore import qInstallMessageHandler

# Configuration for environment variables for display scaling
os.environ["QT_AUTO_SCREEN_SCALE_FACTOR"] = "1"
os.environ["QT_SCREEN_SCALE_FACTORS"] = "1"
os.environ["QT_SCALE_FACTOR"] = "1"

# Configure logging to log warnings
logging.basicConfig(filename='app_warnings.log', level=logging.WARNING)

# Define a Qt message handler to filter out ICC profile warnings
def qt_message_handler(mode, context, message):
    if "icc" in message:
        logging.warning(message)  # Log ICC profile warnings
    else:
        sys.stderr.write(f"{mode}: {message}\n")

qInstallMessageHandler(qt_message_handler)

class WeatherApp(QWidget):
    def __init__(self):
        super().__init__()
        self.backgroundPixmap = None
        self.initUI()
        
    def initUI(self):
        self.setWindowTitle('LAD Weather APP')
        self.setGeometry(350, 100, 450, 600)

        # Main layout
        self.main_layout = QVBoxLayout()
        self.setLayout(self.main_layout)

        # Input layout for user input
        self.input_layout = QVBoxLayout()
        self.input_layout.setAlignment(Qt.AlignCenter)

        # Create a QLineEdit for city input with larger font
        self.cityInput = QLineEdit(self)
        input_font = QFont('Arial', 14)
        self.cityInput.setFont(input_font)
        self.cityInput.setPlaceholderText('Enter city name...')
        self.input_layout.addWidget(self.cityInput)

        # Create a QPushButton for triggering the weather fetch
        self.searchButton = QPushButton('Get Weather', self)
        self.searchButton.setFont(input_font)
        self.searchButton.clicked.connect(self.get_weather)
        self.input_layout.addWidget(self.searchButton)

        self.main_layout.addLayout(self.input_layout)

        # Font settings for labels
        font = QFont('Arial', 14, QFont.Bold)
        self.result_font = QFont('Arial', 20, QFont.Bold)  # Larger font for results
        small_font = QFont('Arial', 12)  # Smaller font for additional info

        # Labels for displaying the results
        self.lblCity = QLabel('', self)
        self.lblCity.setFont(font)
        self.lblCity.setAlignment(Qt.AlignCenter)

        self.lblTemp = QLabel('', self)
        self.lblTemp.setFont(font)
        self.lblTemp.setAlignment(Qt.AlignCenter)

        self.lblWind = QLabel('', self)
        self.lblWind.setFont(font)
        self.lblWind.setAlignment(Qt.AlignCenter)

        self.lblSunrise = QLabel('', self)
        self.lblSunrise.setFont(small_font)
        self.lblSunrise.setAlignment(Qt.AlignCenter)

        self.lblSunset = QLabel('', self)
        self.lblSunset.setFont(small_font)
        self.lblSunset.setAlignment(Qt.AlignCenter)

        self.lblPrecipitation = QLabel('', self)
        self.lblPrecipitation.setFont(small_font)
        self.lblPrecipitation.setAlignment(Qt.AlignCenter)

        self.lblError = QLabel('', self)
        self.lblError.setFont(font)
        self.lblError.setAlignment(Qt.AlignCenter)

        # Layouts for additional info
        self.additional_info_layout = QHBoxLayout()
        self.additional_info_layout.addWidget(self.lblSunrise)
        self.additional_info_layout.addWidget(self.lblSunset)
        self.additional_info_layout.addWidget(self.lblPrecipitation)

        # Results layout (initially empty)
        self.results_layout = QVBoxLayout()
        self.results_layout.setAlignment(Qt.AlignCenter)
        self.results_layout.addWidget(self.lblCity)
        self.results_layout.addWidget(self.lblTemp)
        self.results_layout.addWidget(self.lblWind)
        self.results_layout.addLayout(self.additional_info_layout)
        self.results_layout.addWidget(self.lblError)

    def paintEvent(self, event):
        painter = QPainter(self)
        if self.backgroundPixmap:
            scaledPixmap = self.backgroundPixmap.scaled(self.size(), Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation)
            painter.drawPixmap(self.rect(), scaledPixmap)

    def get_city_image(self, city):
        client_id = "8wOf194oMNU_T6csv_69gFnS8zg5P6pLallRK-I90ns"  # Unsplash API key
        url = f"https://api.unsplash.com/search/photos?query={city}&client_id={client_id}"
        response = requests.get(url)
        if response.status_code == 200:
            results = response.json()
            if results['results']:
                image_url = results['results'][0]['urls']['regular']
                image_response = requests.get(image_url)
                if image_response.status_code == 200:
                    pixmap = QPixmap()
                    pixmap.loadFromData(image_response.content)
                    self.backgroundPixmap = pixmap
                    self.update()  # Trigger a repaint to display the new background
                else:
                    print("Failed to load image data.")
            else:
                print("No images found for this city.")
                self.backgroundPixmap = None
                self.update()
        else:
            print("Failed to fetch image:", response.status_code)

    def get_weather(self):
        city = self.cityInput.text().strip()
        if city == "":
            self.lblError.setText("City Name Required")
            return
        
        self.get_city_image(city)  # Fetch and display the city image

        api_key = "76c75e345c1a10014eae6156e7775cd9"  # OpenWeatherMap API key
        url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}"
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            if data.get('weather'):
                city_name = data["name"]
                country = data["sys"]["country"]
                temp_c = data["main"]["temp"] - 273.15
                temp_f = (temp_c * 9/5) + 32
                weather_description = data["weather"][0]["description"]
                wind_speed = data["wind"]["speed"]
                sunrise = QDateTime.fromSecsSinceEpoch(data["sys"]["sunrise"]).toString('hh:mm:ss AP')
                sunset = QDateTime.fromSecsSinceEpoch(data["sys"]["sunset"]).toString('hh:mm:ss AP')
                precipitation = data.get("rain", {}).get("1h", 0)
                
                self.lblCity.setText(f"{city_name}, {country}")
                self.lblTemp.setText(f"Temp: {temp_c:.1f}°C ({temp_f:.1f}°F), {weather_description}")
                self.lblWind.setText(f"Wind Speed: {wind_speed} m/s")
                self.lblSunrise.setText(f"Sunrise: {sunrise}")
                self.lblSunset.setText(f"Sunset: {sunset}")
                self.lblPrecipitation.setText(f"Precipitation: {precipitation} mm")

                # Increase font size for weather details
                self.lblCity.setFont(self.result_font)
                self.lblTemp.setFont(self.result_font)
                self.lblWind.setFont(self.result_font)
                # Move results layout to the top and add input layout below it
                self.main_layout.removeItem(self.input_layout)
                self.main_layout.insertLayout(0, self.results_layout)
                self.main_layout.insertLayout(1, self.input_layout)
            else:
                self.lblError.setText("No weather data available for this location.")
        else:
            self.lblError.setText("Invalid City Name")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = WeatherApp()
    ex.show()
    sys.exit(app.exec_())
