# CS50 Web Capstone Project


## Intro
My goal was to build a useful web app that provides some function that I can use in my other job. 
As an Event Manger I often receive a stock list spreadsheet, sometimes before the event but quite often while I am on-site. 
Usually there is nowhere to print the document and the task of counting and recording the stock and equipment is cumbersome. 
While there are excellent spreadsheet mobile apps available, none of them really provide a suitable interface for counting a list.


## Stocklist
A mobile first web app for counting a list of items, before and after an event. 
The web app should allow the user to:
    - Load a CSV file containing a list of items
    - Count these items before and after some event
    - Export the data back to a CSV file and download it.


## Specification
* Create Store: Allow users to name the store that will contain the items to be counted.
* Load CSV File: If no items are in the store, provide a file input for users to load a local CSV file.
    * Input should be restricted to CSV file types.
    * Design a strategy for successfully parsing CSV files. Files potentially may not contain headers, may be empty, or may not contain suitable data.
    * Safely parse the CSV file and provide feedback to the user highlighting errors.
* Match Headers Fields to Model Fields: Provide an interface for users to match table columns to item names and item quantities.
    * Select item name columns: At least one column should be selected to provide names for the item model. 
        * Candidate columns should contain strings or numbers.
        * Multiple column selections will be concatenated.
    * Select item quantity columns: At most one column should be selected to provide the imported quantity for each item. 
        * Candidate columns should only contain numbers.
        * It should not be possible to select more than one item column at a time.
* Import items: Save the selected table columns into the database. 
    * Allow for three entries for each item: Imported quantity, Start count, End count.
    * Design a model that can be extended beyond three entries for each item.
* Count Items: Provide an interface for users to count each item in turn.
    * The interface should be easy to use and accessible on any screen size.
    * Handle overflow and underflow when traversing the first and last items.
* Select Count: Allow users to select and update each count: Start Count and End Count.
* Export Items: Allow users to export the table data.
    * When viewing the store, the user should be presented with a "Export Items" button that lets them export the table of items.
    * When the user clicks the Export Items button, successfully parse the data to CSV and present a "Download" button to the user. 
* Download CSV File: Allow users to download the CSV file.
* Delete Store: Allow users to delete the store.
    * Users should be returned to the create store page.


## Distinctiveness and Complexity

### Distinctiveness
This project does contain elements from the other projects I have completed for this course, however Stocklist is distinct from the other projects in the following ways: 
1. Uploading, parsing and validating CSV files
2. Matching table columns to multiple models and fields 
3. Fetching data from multiple models for display in a table
4. Creating and downloading the table as a CSV file

### Complexity
While the main function of the web app - counting a list of items - is simple to execute, two factors significantly increase the complexity of the project: 
1. File Handling - Importing an unrelated CSV file to the database by matching with the correct fields 
2. Extending the project - Designing the project to be extended beyond a single 'before and after' count

##### File Handling
File handling involves the following steps:
1. File upload 
2. CSV to JSON parsing 
3. Validating the headers, and columns of data
4. Displaying the parsed CSV file in a table to the user 
5. Field Selections that match with the model fields
6. Saving to the database
7. JSON to CSV parsing
8. File Download

Validation and field selection are two stages that add complexity.
CSV files contain no reference to headers or data types

##### Extending the project
The simplest model design for this project would be two models, List and Item. Item would contain an optional Imported Amount, plus a Start Count and End Count. 
This design is not readily extendible so I added more complexity to the project in order to allow for future development by separating Item into Item and ListItem. This allows for an unlimited Lists, referencing each ListItem to an Item, but complicates fetching, manipulating and displaying the data in table rows.


## Improvements
CSS, localization, reduce the number of database operations with bulk save, add another column that colculates the difference between the two counts.
To extend the use case beyond one event, introduce another model, Stocklist, that represents a document, 


## How to run Stocklist.
To run the Stocklist application from the local directory:

```sh
python manage.py runserver
```

## Any other additional information the staff should know about your project.


!If you’ve added any Python packages add them to a requirements.txt file!
!Though not a hard requirement, 500 words is likely a solid target!


## Documentation

#### `models.py`: Contains model definitions, validators, constraints and serializers.
* `User` 
* `Store` - A container for Items, and Lists
    - Fields: `user`, `name`
    - Constraints: `Unique Constraint` : "Store name must be unique for User."
    - Methods: 
        - `__str__()`
* `List` - A container for ListItems
    - Fields: `store`, `name`, `type`, `date_added`
    - Choices: `LIST_TYPE_CHOICES : ADDITION, SUBTRACTION, COUNT`
    - Methods: 
        - `__str__()`
        - `save()` Raises `Validation Error` : Invalid Type
        - `serialize()`
* `Item` - Anything that needs to be counted
    - Fields: `store`, `name`
    - Constraints: `Unique Constraint` : "Item name must be unique for Store."
    - Methods: 
        - `__str__()`
        - `serialize()`
* `ListItem` - An amount of an Item in a List
    - Fields: `list`, `item`, `amount`
    - Constraints: `Unique Constraint` : "Item must be unique for List."
    - Methods: 
        - `__str__()`
        - `name()` : returns `item.name`


#### `forms.py` - Contains the ModelForm for creating a store.
* `StoreNameForm` - A ModelForm for creating a Store
    - models: `Store`
    - Fields: `name`
    - Widgets: `TextInput`
    - Labels: `name`


#### `views.py` - Contains methods for receiving a web request and returning a web response. 
* `index(request)` - The landing page for Stocklist
    * `GET` - Checks `User.stores`
        * None: returns `StoreNameForm()` with template `stocklist/index.html`
        * Found: redirects to `/store/{id}`
    * `POST` - Saves a new `Store`
        * Store Exists: returns `StoreNameForm()` with error message
        * Form Invalid: returns `StoreNameForm()` 
        * Save Validation Error: returns `StoreNameForm()` with error message
        * Saved: redirects to `/store/{id}`

* `store(request, store_id)` - Displays the Stores Items, or CSV file loading
    * Invalid Store: returns `404`
    * `GET` - returns `Store` with template `stocklist/index.html`
    * `POST` - deletes `Store`, reverses to `index`

* `update_store(request, store_id)` - API call to update the store name
    * Invalid Store: returns `404`
    * `PUT` - Updates `Store.name`
        * Empty string: returns `JSONResponse` with Validation Error message
        * No change needed: returns `JSONResponse` with message 
        * Not unique for `Store`: returns `JSONResponse` with Integrity Error message
        * Save Validation Error: returns `JSONResponse` with Validation Error message
    * returns `JSONResponse` with message: `PUT` request required

* `import_items(request, store_id)` - Creates multiple List, Item, ListItem objects in the database
    * Invalid Store: returns `404`
    * `POST` - Creates `List`, `ListItem`, `Item` objects from `JSON` data
        * Save List Validation Error: returns `JSONResponse` with Validation Error message
        * Save Item Validation Error: returns `JSONResponse` with Validation Error message
        * Save ListItem Validation Error: returns `JSONResponse` with Validation Error message
        * Saved: returns `JSONResponse` with Success message
    * returns `JSONResponse` with message: `POST` request required

* `items(request, store_id)` - Returns a Store's List, Item serialized
    * Invalid Store: returns `404`
    * `GET` - Returns serialized arrays of `Item` and `List` for `store.id` 
    * returns `JSONResponse` with message: `POST` request required

* `create_lists(request, store_id)` - Creates multiple List objects in the database
    * Invalid Store: returns `404`
    * `POST` - Creates `List` objects from `JSON` data
        * Save List Validation Error: returns `JSONResponse` with Validation Error message message
        * Saved: returns `JSONResponse` with Success message
    * returns `JSONResponse` with message: `POST` request required

* `create_item(request, store_id)` - Creates an Item in the database
    * Invalid Store: returns `404`
    * `POST` - Creates `Item` object from `JSON` data
        * Save Item Validation Error: returns `JSONResponse` with Validation Error message
        * Saved: returns `JSONResponse` with Success message
    * returns `JSONResponse` with message: `POST` request required

* `create_list_item(request, store_id)` - Creates a ListItem in the database
    * Invalid Store: returns `404`
    * `POST` - Creates or updates `ListItem` object from `JSON` data
        * Save ListItem Validation Error: returns `JSONResponse` with Validation Error message
        * Saved: returns `JSONResponse` with Success message
    * returns `JSONResponse` with message: `POST` request required

* `login_view(request)` - Login Page
    * `POST` - Logs in `User`
        * Success: reverses to `index` with template `stocklist/index.html`
        * Failure: returns with error message
    * returns to `login`

* `logout_view(request)` - Logout
    * reverses to `index` 

* `register_view(request)` - Register page
    * `POST` - Logs in `User`
        * Mismatched passwords: returns with error message
        * Username taken: returns with error message
        * Saved: reverse to `index`
    * returns to `register`


#### `urls.py` - Contains urls for `views.py`
    


## Static Files


#### `static/stocklist/stocklist.js` - Contains client-side code for controlling the flow of the web app, processing data, updating UI.

##### Load Document
* `document.addEventListener()`
    * Set up button actions for `load_csv`, `export_csv`, `count_items`, `count_next_item`, `count_prev_item`
    * Set display of `#items-view`, `#import-csv-view` to none
    * `fetch_items()`

##### Set up 
* `set_up_load_csv_action()` 
* `set_up_export_csv_action()`
* `set_up_count_items_action()`
* `set_up_count_next_item_action()`
* `set_up_count_prev_item_action()`

##### Items 
* `fetch_items()` from `/items/{store_id}`
    * If items: 
        * Save Data (`items` and `lists`) to localStorage
        * Display `#items-view`
        * `load_table_with_data(data)`
     * No items
         * Display `#import-CSV-View`

* `load_table_with_data(data)`
    * Create and populate table rows for the table
    * Save Data (`current_list_index` and `current_item_index`) to localStorage
    * `set_up_header_selections(lists, current_list_index)`
    * `update_count_button(current_list, items_count)`

* `set_up_header_selections(lists, current_list_index)`
    * Enables selection for each list with `type = COUNT` with event listener: `select_col_header(header)`
    * Adds class `selected` to the relevant header

##### User Input 
* `select_col_header(header)`
    * Switches editing to the selected header
    * Save Data (`current_list_index`) to localStorage
    * `update_count_button(current_list, items.length)`
    * `update_count_form(items[current_item_index], current_list.id)`

* `count_items(button)` 
    * Toggles collapse
    * `update_count_form(items[0], current_list.id)`

* `count_item(button)` 
    * Saves `ListItem`
    * Updates `Item` 
    * Save Data (`items`) to localStorage
    * If created:
        * Update `list.count`
        * Save Data (`lists`) to localStorage
        * `update_count_button(current_list, items.length)`
    * Update UI
        * `update_count_form(next_item, current_list.id)`
        * `update_table_cell(current_item.id, current_list.name, amount)`
    * `update_count_form(next_item, current_list.id)`

* `next_row_index(button, index, items_length)`
    * Calculates the next `Item` index

##### Update UI
* `update_count_button(current_list, items_count)` 
    * Updates button with `list.name`, `list.type_string`, `list.count`
    
* `update_count_form(item, current_list_id)` 
    * Updates label with `item.name`
    * Updates Input with `item.list_item.amount`
    
* `update_table_cell(item_id, list_name, amount)` 
    * Updates the relevant table cell

##### CSV 
* `parse_csv()`
    * Uses PapaParse to parse the CSV file
        * headers, and dynamic typing set to `true`
    * Header fields should all be strings:
        * `display_error('CSV File should contain headers with text: Choose another file!')`
    * One column should be of type string:   
        * `display_error('CSV File should contain a column of text: Choose another file!')`
    * Save Data (`data`) to localStorage
    
* `display_error(message)` 
    * Displays parsing error in `#load-csv-error-message`

* `set_up_on_change_for_file_input(error_p)`
    * helper method for resetting messages when file name changes

* `clear_import_table()` 
    * helper method for resetting csv table when file name changes

* `display_parsed_csv_table(results)` 
    * Display table with data, first 4 Table Rows
    * Display Table Header
    * Display Column DropDowns for selecting fields
    * Display table Caption
    * Display Import Items Button

* `select_element_for_field(typeof_field)`
    * Returns relevant Select for each column header
        * Number options: Item Name, Item Amount, Ignore 
        * String options: Item Name, Ignore 
        * Other type: Ignore

* `toggleDisability(selected)`
    * Ensures only one Item Amount option is selectable 

* `import_items_button()`
    * Returns button with action `validate_selections(button)`

* `validate_selections(button)`
    * ERROR: No item name field selected
        * Displays error "Select an Item Name column!"
    * Maps Selections to Item.Properties
    * `import_items(items)`

* `import_items(items)`
    * Creates three lists:
        * Import, `type=ADDITION', with items name and amounts 
        * Start, `type=COUNT'
        * End, `type=COUNT'
    * `fetch_items()`

* `export_csv(export_csv_button)`
    * File_name
    * Fields names
    * Gather data
    * Unparse data
    * `download_csv_link(file_name, csv)`

* `download_csv_link(file_name, csv)`
    * Set up and display download link
    * Reset buttons asynchronously 

##### COOKIE 
* `getCookie(name)` 
    * Returns cookie with name


#### `static/stocklist/styles.css` - Contains CSS for each page and media queries for responsive layout.
* CSS for `layout.html`
* CSS for `store.html`
* Media Queries


## Templates

#### `templates/stocklist/layout.html` - Contains the base HTML for each page.
* Include Bootstrap CSS, `stocklist.styles.css`
* Navigation
* Main - `{% block body %}`
* Footer
* Include Bootstrap, BS Custom File Input, PapaParse JS 


#### `templates/stocklist/index.html` - Contains the store form.
* `page-title`
* `store-form`


#### `templates/stocklist/store.html` - Contains HTML for file input, the items table, count input, and store actions. 
* `store-name-heading`
* `items-view`
    * `count-items-view`
    * `table-view`
* Actions 
    * `export-csv-button`
    * `delete-store-view`
* `import-csv-view`
    * `import-csv-form`
    * `import-csv-table`


#### `templates/stocklist/register.html` - Contains the register user form HTML.
* `register form`


#### `templates/stocklist/login.html` - Contains the login user form HTML.
* `login-form`


## Tests
#### `tests/test_models.py` - Contains TDD tests for `models.py`

* `UserTestCase` 
    * `test_user()` 

* `StoreTestCase`
    * `test_create_store_missing_store_name()` 
    * `test_create_store()` 
    * `test_unique_store_name_for_owner()` 
    * `test_store_string()` 
    * `test_max_store_name_length()` 

*   `ListTestCase`
    * `test_create_list()` 
    * `test_create_addition_list()`
    * `test_create_count_list()` 
    * `test_create_subtraction_list()` 
    * `test_list_string()` 
    * `test_max_list_name_length()`
    * `test_list_serializer_list_id()`

* `ItemTestCase`
    * `test_create_item()`
    * `test_duplicate_item_name_raises_integrity_error()`
    * `test_duplicate_item_name_for_seperate_stores()`
    * `test_item_string()`
    * `test_max_item_name_length()`
    * `test_item_serializer_item_id()`
    * `test_item_serializer_item_name()`
    * `test_item_serializer_item_list_item_list_id()`
    * `test_item_serializer_item_list_item_amount()`
    * `test_item_serializer_item_list_items_length()`

* `ListItemTestCase`
    * `test_create_list_item()` 
    * `test_list_item_string()` 
    * `test_min_list_item_amount()` 
    * `test_max_list_item_amount()` 
    * `test_unique_item_for_list()` 


#### `tests/test_forms.py` - Contains TDD tests for `forms.py`
* `StoreNameFormTestCase`
    *  `test_empty_form()`
    *  `test_blank_form_data()`
    *  `test_valid_form_data()`
    *  `test_invalid_form_data()`


#### `tests/test_views.py` - Contains TDD tests for `views.py`
* `ImportTestCase()`
    * `JSON` data 
* `ItemsTestCase(ImportTestCase)`
    * `test_GET_items_redirects_to_login_if_not_logged_in(self)`
    * `test_GET_items_returns_404_for_invalid_store(self)`
    * `test_POST_items_returns_400_for_user_logged_in(self)`
    * `test_GET_items_returns_items(self)`
    * `test_GET_items_returns_lists(self)`
* `ImportItemsTestCase(ImportTestCase)`
    * `test_POST_import_items_redirects_to_login_if_not_logged_in(self)`
    * `test_POST_import_items_returns_404_for_invalid_store(self)`
    * `test_GET_import_items_returns_400_for_user_logged_in(self)`
    * `test_POST_import_items_creates_list(self)`
    * `test_POST_import_items_returns_400_for_invalid_list_name_length(self)`
    * `test_POST_import_items_returns_400_for_invalid_list_type(self)`
    * `test_POST_import_items_creates_items(self)`
    * `test_POST_import_items_returns_400_for_invalid_item_name_length(self)`
    * `test_POST_import_items_handles_missing_item_name(self)`
    * `test_POST_import_items_creates_list_items(self)`
    * `test_POST_import_items_returns_400_for_invalid_list_items_amount(self)`
    * `test_POST_import_items_returns_400_for_invalid_list_items_amount2(self)`
    * `test_POST_import_items_creates_listitem_for_missing_item_amount(self)`
    * `test_POST_import_items_doesnt_create_new_item_if_item_already_in_store(self)`
* `CreateListTestCase(ImportTestCase)`
    * `test_POST_create_list_redirects_to_login_if_not_logged_in(self)`
    * `test_GET_create_list_returns_400_for_user_logged_in(self)`
    * `test_POST_create_list_returns_404_for_invalid_store(self)`
    * `test_POST_create_list_returns_201_for_valid_list_type(self)`
    * `test_POST_create_list_returns_400_for_invalid_name(self)`
    * `test_POST_create_list_returns_400_for_empty_name(self)`
    * `test_POST_create_list_returns_400_for_invalid_type(self)`
    * `test_POST_create_list_returns_201_for_multiple_valid_lists(self)`
    * `test_POST_create_list_returns_201_for_missing_type(self)`
    * `test_POST_create_list_returns_201_for_empty_type(self)`
* `CreateListItemTestCase(ImportTestCase)`
    * `test_POST_create_list_item_redirects_to_login_if_not_logged_in(self)`
    * `test_POST_create_list_item_returns_404_for_invalid_list(self)`
    * `test_POST_create_list_item_returns_404_for_invalid_item(self)`
    * `test_GET_create_list_item_returns_400_for_user_logged_in(self)`
    * `test_POST_create_list_item_creates_list_item(self)`
    * `test_POST_create_list_item_creates_list_item_with_decimal_amount(self)`
    * `test_POST_create_list_item_updates_list_item_if_exists(self)`
    * `test_POST_create_list_item_returns_400_for_invalid_list_items_amount_min(self)`
    * `test_POST_create_list_item_returns_400_for_invalid_list_items_amount_max(self)`
* `CreateItemTestCase(BaseTestCase)`
    * `test_POST_create_item_redirects_to_login_if_not_logged_in(self)`
    * `test_POST_create_item_returns_404_for_invalid_store(self)`
    * `test_GET_create_item_returns_400_for_user_logged_in(self)`
    * `test_POST_create_item_returns_400_for_invalid_name(self)`
    * `test_POST_create_item_returns_400_for_empty_name(self)`
    * `test_POST_create_item_name_not_unique_returns_400(self)`
    * `test_POST_create_item_returns_201_for_valid_name_and_store(self)`
* `UpdateStoreTestCase(BaseTestCase)`
    * `test_PUT_returns_201_for_valid_store(self)`
    * `test_PUT_valid_data_returns_201(self)`
    * `test_PUT_no_name_change_returns_201(self)`
    * `test_PUT_empty_data_returns_400(self)`
    * `test_store_name_max_length_returns_400(self)`
    * `test_store_name_not_unique_returns_400(self)`
* `StoreTestCase(ImportTestCase)`
    * `test_store_path_redirects_to_login_if_not_logged_in(self)`
    * `test_PUT_returns_302(self)`
    * `test_invalid_store(self)`
    * `test_valid_store(self)`
    * `test_delete_store(self)`
* `IndexTestCase(BaseTestCase)`
    * `test_GET_renders_index_html(self)`
    * `test_GET_redirects_to_login_when_not_signed_in(self)`
    * `test_GET_redirects_to_store_when_store_exists(self)`
    * `test_get_page_title(self)`
    * `test_GET_forms(self)`
    * `test_PUT_reverse_to_index(self)`
    * `test_POST_valid_store_name(self)`
    * `test_POST_invalid_store_name(self)`
* `LoginTestCase(BaseTestCase)`
    * `test_user_login(self)`
    * `test_login_view(self)`
    * `test_login_view_GET_renders_login_html(self)`
    * `test_login_view_POST_displays_error_message_for_invalid_username_and_or_password(self)`
    * `test_login_view_POST_success_reverse_to_index(self)`
* `LogoutTestCase(BaseTestCase)`
    * `test_user_logout(self)`


#### `tests/test_pages.py` - Contains the integration tests.

* `SeleniumTests(StaticLiveServerTestCase)`
    * `setUpClass(cls)`
    * `tearDownClass(cls)`
* `BaseTests(SeleniumTests)`
    * `setUp(self)` - Create User
* `RegisterTests(BaseTests)`
    * `setUp(self)` - Get `RegisterPage` Page Object Model (POM)
    * `test_register_success(self)`
    * `test_register_fail_username_exists(self)`
    * `test_register_fail_unmatched_passwords(self)`
* `LoginTests(BaseTests)`
    * `setUp(self)` - Get `LoginPage` POM
    * `test_login_success(self)` - `IndexPage` POM
    * `test_login_fail(self)`
* `IndexTests(BaseTests)`
    * `setUp(self)` - Get `LoginPage`, `IndexPage` POM
    * `test_index(self)`
    * `test_set_store_name_success(self)`
* `BaseImportTests(BaseTests)` - CSV Test Files
    * `setUp(self)` - Get `LoginPage`, `IndexPage`, `LoadFileComponent` POM
* `LoadFileTests(BaseImportTests)`
    * `setUp(self)` - Waits for CSV File form
    * `test_load_file_success(self)`
    * `test_load_file_error_no_column_of_strings_detected(self)`
    * `test_load_file_fail_no_header_row(self)`
* `BaseSelectColumnTests(BaseImportTests)`
    * `setUp(self)` - Loads test file, Waits for Import Button
* `SelectTableColumnTests(BaseSelectColumnTests)`
    * `test_table_column_select_options_for_type_string(self)`
    * `test_table_column_select_options_for_type_number(self)`
    * `test_table_column_select_options_for_type_other(self)`
    * `test_table_column_select_options_for_multiple_type_number(self)`
    * `test_table_column_select_options_for_multiple_type_string(self)`
* `ImportItemsTests(BaseSelectColumnTests)`
    * `test_save_items_fail_no_columns_selected(self)`
    * `test_save_items_success_item_name_selected(self)`
    * `test_save_items_success_item_name_and_amount(self)`
    * `test_save_items_success_item_name_from_multiple_columns(self)`
* `BaseFixtureTests(SeleniumTests)` - Fixtures
    * `setUp(self)` - Get `LoginPage`, `IndexPage` POM
* `CountItemsTests(BaseFixtureTests)`
    * `setUp(self)` - Get `ItemsTableComponent` POM, waits for selected header
    * `test_count_items(self)`
* `ExportFileTests(BaseFixtureTests)`
    * `setUp(self)` - Get `ExportFileComponent` POM, waits for export button
    * `test_export_file(self)`
* `DeleteStoreTests(BaseFixtureTests)`
    * `setUp(self)` - Get `DeleteStoreComponent` POM, waits for delete view
    * `test_delete_store(self)`


#### `tests/page_object_model/base_page.py` - Contains the base POM class for testing.

* `BasePage(object)`
    * `__init__(self, driver, live_server_url, navigate=False)`
    * `fill_form_by_css(self, form_css, value)`
    * `fill_form_by_id(self, form_element_id, value)`
    * `clear_and_fill_form_by_id(self, form_element_id, value)`
    * `fill_form_by_name(self, name, value)`
    * `title(self)`
    * `navigate(self)`


#### `tests/page_object_model/user_pages.py` - Contains the user POM classes for login and registration.

* `LoginPage(BasePage)` - url, elements
    * `set_username(self, username)`
    * `set_password(self, password)`
    * `set_user_data(self, username, password)`
    * `get_errors(self)`
    * `login_as(self, username, password)`
    * `submitExpectingFailure(self)`
    * `expect_failure_to_login_as(self, username, password)`

* `RegisterPage(LoginPage)` - url, elements
    * `set_email(self, email)`
    * `set_confirmation(self, confirmation)`
    * `set_user_data(self, username, email, password, confirmation)`
    * `register_as(self, username, email, password, confirmation)`
    * `submitExpectingFailure(self)`
    * `expect_failure_to_register_as(self, username, email, password, confirmation)`


#### `tests/page_object_model/pages.py` - Contains the app specific POM classes.

* `IndexPage(BasePage)` - url, Web elements
    * `get_errors(self)`
    * `get_store_name_form(self)`
    * `set_store_name(self, store_name)`
    * `submit(self)`
    * `create_store_named_as(self, store_name)`
    * `submitExpectingFailure(self)`
    * `expect_failure_to_create_store_named_as(self, store_name)`

* `StorePage(BasePage)` - Web elements
    * `__init__(self, driver, live_server_url, url="/store/1", navigate=False)`
    * `get_store_page_heading_text(self)`

* `LoadFileComponent(StorePage)` - Web elements
    * `get_csv_load_form_locator(self)`
    * `get_csv_load_error_message_locator(self)`
    * `get_csv_load_error_message_text(self)`
    * `set_file_path(self, path)`
    * `submit(self)`
    * `load_file_with_path(self, file_local_path)`
    * `submitExpectingFailure(self)`
    * `expect_failure_to_load_file_with_path(self, file_local_path)`

* `ImportItemsComponent(StorePage)` - Web elements
    * `get_csv_table_column_select_elements(self)`
    * `get_import_items_button_locator(self)`
    * `get_select_at_col_index(self, index)`
    * `get_option_for_select_with_value(self, select, value)`
    * `get_import_items_error_message_locator(self)`
    * `get_import_items_error_message_text(self)`
    * `submit(self)`
    * `save_items(self)`
    * `submitExpectingFailure(self)`
    * `expect_failure_to_save_items(self)`

* `IItemsTableComponent(StorePage)` - Web elements
    * `get_items_table_body_rows(self)`
    * `get_selected_table_header_locator(self)`
    * `get_table_cell_innerHTML_at_index_in_table_row(self, column_index, table_row)`
    * `get_table_header_innerHTML_in_table_row(self, table_row)`
    * `select_end_column_table_header(self)`
    * `get_count_items_button(self)`
    * `get_count_items_collapse_show_locator(self)`
    * `get_count_item_name_label(self)`
    * `set_item_count(self, amount)`
    * `toggle_count_items_collapse(self)`
    * `submit_next(self)`
    * `count_item_next(self, amount)`
    * `submit_previous(self)`
    * `count_item_previous(self, amount)`

* `ExportFileComponent(ItemsTableComponent)` - Web elements
    * `get_export_csv_button_locator(self)`
    * `get_download_file_link_locator(self)`
    * `submit_export(self)`
    * `export_items(self)`
    * `submit_download(self)`
    * `download_file(self)`

* `DeleteStoreComponent(ItemsTableComponent)` - Web elements
    * `get_delete_store_view_locator(self)`
    * `get_delete_store_input_locator(self)`
    * `get_delete_store_input(self)`
    * `submit(self)`
    * `delete_store(self)`


#### `fixtures/db.json` - Contains the test database fixture.
* Test database 


#### `tests/csv_test_files/no_headers.csv` 
* CSV file with header fields

#### `tests/csv_test_files/no_strings.csv`
* CSV file with no string column

#### `tests/csv_test_files/strings_and_numbers.csv`
* CSV file with string and number columns

#### `tests/csv_test_files/multiple_name_columns.csv`
* CSV file with multiple string and number columns


