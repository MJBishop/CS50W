

class BasePage(object):
    url = None

    def __init__(self, driver, live_server_url, navigate=False):
        self.driver = driver
        self.live_server_url = live_server_url
        if navigate:
            self.navigate()

    def fill_form_by_css(self, form_css, value):
        elem = self.driver.find(form_css)
        elem.send_keys(value)

    def fill_form_by_id(self, form_element_id, value):
        elem = self.driver.find_element_by_id(form_element_id)
        elem.send_keys(value)

    def fill_form_by_name(self, name, value):
        elem = self.driver.find_element_by_name(name)
        elem.send_keys(value)

    @property
    def title(self):
        return self.driver.title
    
    def navigate(self):
        self.driver.get(
			"{}{}".format(
				self.live_server_url,
				self.url
			)
        )