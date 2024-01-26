import os
from datetime import datetime
from pathlib import Path
import getpass
import shutil
import pytest
from selenium import webdriver
from selenium.webdriver.chrome.service import Service

driver = None

def pytest_addoption(parser):
    parser.addoption("--browser_name", action="store", default="chrome")

@pytest.fixture(scope="class")
def setup(request):
    global driver
    browser_name = request.config.getoption("browser_name")
    chrome_options = None

    if browser_name == "chrome":
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument('--disable-application-cache')
        chrome_options.add_argument('--ignore-ssl-errors=yes')
        chrome_options.add_argument('--ignore-certificate-errors')
        service_obj = Service("C:/Users/Manu123/Downloads/chromedriver-win64/chromedriver-win64/chromedriver.exe")
        driver = webdriver.Chrome(service=service_obj, options=chrome_options)
        driver.implicitly_wait(5)
    elif browser_name == "firefox":
        service_obj = Service("C:/Users/Manu123/Downloads/geckodriver-v0.34.0-win-aarch64/geckodriver.exe")
        driver = webdriver.Firefox(service=service_obj, options=chrome_options)
    elif browser_name == "IE":
        service_obj = Service("C:/Users/Manu123/Downloads/edgedriver_win64/edgedriver.exe")
        driver = webdriver.Ie(service=service_obj, options=chrome_options)

    driver.get("https://rahulshettyacademy.com/angularpractice")
    driver.maximize_window()
    request.cls.driver = driver
    yield
    driver.close()


@pytest.mark.hookwrapper
def pytest_runtest_makereport(item):
    """
        Extends the PyTest Plugin to take and embed screenshot in html report, whenever test fails.
        :param item:
        """
    pytest_html = item.config.pluginmanager.getplugin('html')
    outcome = yield
    report = outcome.get_result()
    extra = getattr(report, 'extra', [])

    if report.when == 'call' or report.when == "setup":
        #Add your URL to report 
        extra.append(pytest_html.extras.url(driver.current_url))
        xfail = hasattr(report, 'wasxfail')
        if (report.skipped and xfail) or (report.failed and not xfail):
            #only add adition html on failure
            #report_directoty=os.path.dirname(item.config.option.htmlpath)
            #file_name=str(int(round(time.time()*1000)))+".png"
            file_name = report.nodeid.replace("::", "_") + ".png"
            #destinationFile=os.path.join(report_directoty,file_name)
            _capture_screenshot(file_name)
            if file_name:
                html = '<div><img src="%s" alt="screenshot" style="width:304px;height:228px;" ' \
                       'onclick="window.open(this.src)" align="right"/></div>' % file_name
                extra.append(pytest_html.extras.html(html))
        report.extra = extra

def pytest_html_report_title(report):
    report.title = "FNB Test Report"
    

def _capture_screenshot(name):
    driver.get_screenshot_as_file(name)

@pytest.hookimpl(tryfirst=True)
def pytest_configure(config):
    # Getting the username
    username = getpass.getuser()

    # getting python version
    from platform import python_version
    py_version = python_version()
    # overwriting old parameters with  new parameters
    config._metadata =  {
        "user_name": username,
        "python_version": py_version,
    }
    # set custom options only if none are provided from command line
    if not config.option.htmlpath:
        now = datetime.now()
        # Create the report target directory
        reports_dir = Path('report', now.strftime('%Y_%m_%d'))
        reports_dir.mkdir(parents=True, exist_ok=True)

        # Custom report file with the specified format
        report = reports_dir / f"report_{now.strftime('report_%Y-%m-%d-%H-%M-%S')}.html"
        # adjust plugin options
        imagess_dir = Path(reports_dir,f'Packages')
        imagess_dir.mkdir(parents=True, exist_ok=True)
        config.option.htmlpath = report
        config.option.self_contained_html = True
