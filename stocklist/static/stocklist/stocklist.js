document.addEventListener('DOMContentLoaded', function() {

    console.log('DOM ready')

    // Enable Show Selected File Name
    bsCustomFileInput.init();
    
    // set up
    set_up_load_csv_action();
    set_up_export_csv_action();
    set_up_count_items_action();
    set_up_count_next_item_action();
    set_up_count_prev_item_action();

    document.querySelector('#items-view').style.display = 'none';
    document.querySelector('#import-csv-view').style.display = 'none';

    // fetch items
    fetch_items();
});



// ************** SET UP **************** 

function set_up_load_csv_action() {

    // Load CSV Action
    var load_csv_input = document.querySelector('#load-csv-input');
    if (load_csv_input) {
        load_csv_input.addEventListener('click', function(event) {
            console.log('load-csv-input click') 
            event.preventDefault();
            parse_csv(load_csv_input);
        });
    }
}

function set_up_export_csv_action() {

    // Delete Store Action
    var export_csv_button = document.querySelector('#export-csv-button');
    if (export_csv_button) {
        export_csv_button.addEventListener('click', function(event) {
            console.log('export-csv-button click') 
            event.preventDefault();
            export_csv(export_csv_button);
        });
    }
}

// function set_up_cancel_export_csv_action() {

//     // Cancel Delete Store Action
//     var export_csv_button = document.querySelector('#export-csv-button');
//     if (export_csv_button) {
//         export_csv_button.addEventListener('click', function(event) {
//             console.log('cancel-export-csv-button click') 
//             event.preventDefault();
//             cancel_export_csv(export_csv_button);
//         });
//     }
// }

function set_up_count_items_action() {

    // Count Items Action
    var count_items_button = document.querySelector('#count-items-button');
    if (count_items_button) {
        count_items_button.addEventListener('click', function(event) {
            console.log('"count_items_button" click') 
            event.preventDefault();

            count_items(count_items_button);
        });
    }
}
function set_up_count_next_item_action() {

    // Count Next Item Action
    var count_next_item_button = document.querySelector('#count-item-next-button');
    if (count_next_item_button) {
        count_next_item_button.addEventListener('click', function(event) {
            console.log('count-item-next-button click') 
            event.preventDefault();
            count_item(count_next_item_button);
        });
    }
}
function set_up_count_prev_item_action() {

    // Count Prev Item Action
    var count_prev_item_button = document.querySelector('#count-item-previous-button');
    if (count_prev_item_button) {
        count_prev_item_button.addEventListener('click', function(event) {
            console.log('count-item-prev-button click') 
            event.preventDefault();
            count_item(count_prev_item_button);
        });
    }
}


// ************** ITEMS **************** 

function fetch_items() {

    // csrf token from cookie
    const csrftoken = getCookie('csrftoken');
        
    // Import Items
    store_id = document.querySelector('#title').dataset.store_id;
    const path = '/items/' + store_id;
    fetch(path, {
        method: 'GET',
        headers: { 'X-CSRFToken': csrftoken },
        mode: 'same-origin',
    })
    .then(response => response.json())
    .then(data => {

        // Print result
        console.log(data);

        if (data.items.length) {
            // Display Table View
            document.querySelector('#items-view').style.display = 'block';
            document.querySelector('#import-csv-view').style.display = 'none';

            // Save Data
            localStorage.setItem('items', JSON.stringify(data.items));
            localStorage.setItem('lists', JSON.stringify(data.lists));

            // Load Data
            load_table_with_data(data);
        }
        else {
            // Display Import CSV View
            document.querySelector('#items-view').style.display = 'none';
            document.querySelector('#import-csv-view').style.display = 'block';
        }

    })
    // Catch any errors and log them to the console
    .catch(error => {
      console.log('Error:', error);
    });
}

function load_table_with_data(data) {

    const items = data.items;
    const lists = data.lists;

    // Cells
    for (var i = 0, item; item = items[i]; i++) {

        var item_id = item['id'];
        var list_items = item['list_items'];
        
        // Table Row
        var table_row = document.createElement('tr');
        table_row.setAttribute('id', item_id);

        // row_header_cell_with_item_list_name(item, list_name)
        var header_cell = document.createElement('th');
        header_cell.setAttribute('scope', 'row');
        header_cell.setAttribute('id', item_id + '_Name');
        header_cell.innerHTML = item['name'];
        table_row.append(header_cell);

        // row cells
        for (var j = 0, list; list = lists[j]; j++) {
            
            var cell = document.createElement('td');
            cell.setAttribute('id', item_id + '_' + list.name);

            // add list_item.amount
            const list_item = list_items.find((list_item) => list_item.list_id == list.id);
            if (typeof list_item !== "undefined") {
                cell.innerHTML = Number(list_item.amount).toString();
            }
            table_row.append(cell);  
        }

        // Append Row
        document.querySelector('#items-table-body').append(table_row);
    }

    // current_list(items_count, lists, )
    const items_count = items.length;

    // current list
    var current_list_index = lists.findIndex((list) => list.count != items_count);
    if (current_list_index < 0) {
        current_list_index = lists.length - 1;
    }
    console.log('current_list_index: ' + current_list_index);
    const current_list = lists[current_list_index];

    // Save Data
    localStorage.setItem('current_list_index', JSON.stringify(current_list_index)); 
    localStorage.setItem('current_item_index', JSON.stringify(0)); 

    // Header Selection
    set_up_header_selections(lists, current_list_index);

    // Button
    update_count_button(current_list, items_count);
}

function set_up_header_selections(lists, current_list_index) {

    const items_table_headers = document.getElementsByClassName('items-table-header'); 
    for (var i = 0, list; list = lists[i]; i++) {
        if (list.type == 'Count') {

            const header = items_table_headers[i];
            header.classList.add('selectable-enabled');
            header.addEventListener('click', function() {
                select_col_header(header);
            });

            if (current_list_index == i) {
                header.classList.add('selected');
            }
        }
    }
}



// ************** User Input **************** 

function select_col_header(header) {

    let current_list_index = JSON.parse(localStorage.getItem('current_list_index')); 
    let selected_index = header.dataset.list_index;

    if (selected_index != current_list_index) {

        // Remove selected
        const items_table_headers = document.getElementsByClassName('items-table-header'); 
        const current_header_cell = items_table_headers[current_list_index];
        current_header_cell.classList.remove('selected');

        // Add selected
        header.classList.add('selected');
        localStorage.setItem('current_list_index', JSON.stringify(selected_index)); 
        let lists = JSON.parse(localStorage.getItem('lists')); 
        let items = JSON.parse(localStorage.getItem('items')); 
        let current_list = lists[selected_index];
        let current_item_index = JSON.parse(localStorage.getItem('current_item_index')); 

        update_count_button(current_list, items.length);
        update_count_form(items[current_item_index], current_list.id);
    }
}

function count_items(button) {

    // items
    let items = JSON.parse(localStorage.getItem('items')); 
    let current_list_index = JSON.parse(localStorage.getItem('current_list_index')); 
    let lists = JSON.parse(localStorage.getItem('lists')); 
    let current_list = lists[current_list_index];

    // TODO - first one without list_item
    update_count_form(items[0], current_list.id);
}

function count_item(button) {

    // data
    const items = JSON.parse(localStorage.getItem('items'));
    const lists = JSON.parse(localStorage.getItem('lists'));
    const current_list_index = JSON.parse(localStorage.getItem('current_list_index'));
    const current_item_index = JSON.parse(localStorage.getItem('current_item_index'));

    // curent column and row
    const current_list = lists[current_list_index];
    const current_item = items[current_item_index];
    const items_length = items.length;


    // next Index
    var next_index = next_row_index(button, current_item_index, items.length);
    localStorage.setItem('current_item_index', JSON.stringify(next_index)); 

    // next item
    var next_item = items[next_index];


    // input
    var count_item_amount_input = document.querySelector('#count-item-amount-input')
    var amount = count_item_amount_input.value;
   
    // Save Amount
    const list_item = current_item.list_items.find((list_item) => list_item.list_id == current_list.id);

    if (amount.length > 0 && (typeof list_item === "undefined" || (Number(list_item.amount).toString() != amount))) {
        console.log('save list_item.amount');


        // csrf token from cookie
        const csrftoken = getCookie('csrftoken');

        // data to save
        let new_list_item = { 'amount': Number(amount) };
            
        // Import Lists & Items
        const path = '/create_list_item/' + current_list.id + '/' + current_item.id;
        fetch(path, {
            method: 'POST',
            body: JSON.stringify(new_list_item),
            headers: { 'X-CSRFToken': csrftoken },
            mode: 'same-origin',
        })
        .then(response => response.json())
        .then(result => {
            // Print result
            console.log(result);
    
            // insert list_item into items
            current_item.list_items.push({ "list_id":current_list.id, "amount":amount });
            items[current_item_index] = current_item;
            localStorage.setItem('items', JSON.stringify(items));
            
            if (result.created) {
                
                // update list.count
                current_list.count = current_list.count + 1;
                lists[current_list_index] = current_list;
                localStorage.setItem('lists', JSON.stringify(lists));

                // update ui
                update_count_button(current_list, items.length);
            }

            // update ui
            update_count_form(next_item, current_list.id);
            update_table_cell(current_item.id, current_list.name, amount);

        })
        // Catch any errors and log them to the console
        .catch(error => {
        console.log('Error:', error);
        });

    }
    else {
        update_count_form(next_item, current_list.id);
    }

}

function next_row_index(button, index, items_length) {

    if (button.id == 'count-item-next-button') {
        index++;
        if (index >= items_length) {    
            // out of range
            index = 0;
        }
    }
    else if (button.id == 'count-item-previous-button') {
        index--;
        if (index < 0) {   
            // out of range
            index = items_length - 1;
        }
    }
    return index;
}



// ************** Update UI **************** 

function update_count_button(current_list, items_count) {

    // button
    const count_items_button = document.querySelector('#count-items-button'); 
    var list_count = current_list.count; //here!! undefined
    var badge_string = list_count.toString() + '/' + items_count.toString();
    count_items_button.innerHTML = current_list.name + ' ' + current_list.type + ' ' + badge_string;


    // count_items_button.removeAttribute("disabled");
    // count_items_button.classList.remove('btn-secondary');
    // count_items_button.classList.add('btn-primary');
}

function update_count_form(item, current_list_id) {

    // Label: item.name
    var count_item_name_label = document.querySelector('#count-item-name-label')
    count_item_name_label.innerHTML = item['name'];

    // Input
    var count_item_amount_input = document.querySelector('#count-item-amount-input')
    const list_item = item.list_items.find((list_item) => list_item.list_id == current_list_id);
    let amount;
    if (typeof list_item !== "undefined") { 
        amount = Number(list_item.amount).toString();
    }
    count_item_amount_input.value = amount;

    // 
    count_item_amount_input.focus();
}

function update_table_cell(item_id, list_name, amount) {

    var cell_id = item_id.toString() + "_" + list_name;
    document.getElementById(cell_id).innerHTML = amount;
}






// ************** CSV **************** 

function parse_csv() {

    const input_file = document.querySelector('#input-file');
    const selected_file = input_file.files[0];
    console.log(selected_file);

    if (typeof selected_file === 'undefined') {
        return false;
    }

    const file_name = selected_file['name'];
    const file_type = selected_file['type'];

    // Parse local CSV file
    Papa.parse(selected_file,  {
        header: true,
        dynamicTyping: true,
        complete: function(results) {
            console.log("Finished:", results.data);
            // console.log("Meta:", results.meta);
            // console.log("Fields:", results.meta.fields);
            
            display_parsed_csv_table(results);

            // save data to local storage
            localStorage.setItem('data', JSON.stringify(results.data));
            // localStorage.setItem('fields', JSON.stringify(results.meta.fields));
        }
    });    
}

function display_parsed_csv_table(results) {
    // console.log("display_parsed_csv_table")
    // console.log(results.meta.fields)

    const data = results.data;
    const fields = results.meta.fields;

    // Clear table inner HTML
    document.querySelector('#import-csv-table-head').innerHTML = "";
    document.querySelector('#import-csv-table-body').innerHTML = "";
    document.querySelector('#import-csv-table-caption').innerHTML = "";
    document.querySelector('#import-items-button-div').innerHTML = "";

    // Show table
    document.querySelector('#import-csv-table-div').hidden = false;
    

    // peek at data types
    let column_types = [];
    const sample_row_data = data[0]
    fields.forEach(field => {
        console.log(sample_row_data[field] + ' ' + (typeof sample_row_data[field]));
    });


    //  Display Table Header
    const table_header_row = document.createElement('tr');
    fields.forEach(element => {
        const table_header = document.createElement('th');
        table_header.setAttribute('scope', 'col');
        table_header.innerHTML = element;
        table_header_row.append(table_header);
    });
    document.querySelector('#import-csv-table-head').append(table_header_row);
    
    
    // Display first 4 Table Rows
    let num_display_rows = 4;
    for (let i = 0; i < num_display_rows; i++) {
        const table_row = document.createElement('tr');
        fields.forEach(element => {
            const table_cell = document.createElement('td');
            table_cell.innerHTML = data[i][element];
            table_row.append(table_cell);
        });
        document.querySelector('#import-csv-table-body').append(table_row);
    }

    
    // Display Column DropDowns
    const table_col_select_row = document.createElement('tr');
    fields.forEach(field => {

        // select
        const select = select_element_for_field(typeof sample_row_data[field])
        select.setAttribute('data-field', field);
        select.setAttribute('id', 'import-csv-table-column-select');
        select.addEventListener(
            'change',
            function() { toggleDisability(this); },
            false
         );

        // Table Header
        const table_header = document.createElement('th');
        table_header.setAttribute('scope', 'col');
        table_header.append(select);
        table_col_select_row.append(table_header);
    });
    document.querySelector('#import-csv-table-head').prepend(table_col_select_row);

    // Caption
    document.querySelector('#import-csv-table-caption').innerHTML = "Showing " + num_display_rows + " of " + data.length + " Rows";
   
    // Import Items Button
    document.querySelector('#import-items-button-div').append(import_items_button());
}

function select_element_for_field(typeof_field) {
    const select = document.createElement('SELECT');
    select.classList.add('form-select');
    
    const ignore_option = document.createElement("OPTION");
    ignore_option.innerHTML = 'Ignore';
    ignore_option.value = '0';
    select.append(ignore_option)

    if (typeof_field == 'string' || typeof_field == 'number' ) {
        
        const name_option = document.createElement("OPTION");
        name_option.innerHTML = "Item Name";
        name_option.value = '1';
        select.append(name_option)

        if (typeof_field == 'number') {
            const quantity_option = document.createElement("OPTION");
            quantity_option.innerHTML = "Item Quantity";
            quantity_option.value = '2';
            select.append(quantity_option)
        } 
    }
    return select;
}

function toggleDisability(selected) {
    selected_index = selected.selectedIndex;
    if (selected_index == 2) {
        document.querySelectorAll('#import-csv-table-column-select').forEach(function(select) {
            if (select.options[selected_index]) {
                select.options[selected_index].disabled = true;
            }
        });
        selected.options[selected_index].disabled = false;
        selected.classList.add('selected-amount');
    } else if (selected.classList.contains('selected-amount')) {
        document.querySelectorAll('#import-csv-table-column-select').forEach(function(select) {
            if (select.options[2]) {
                select.options[2].disabled = false;
            }
        });
        selected.classList.remove('selected-amount');
    }
}

function import_items_button() {

    // reply button
    const button = document.createElement('button');
    button.textContent = 'Import Items';
    button.classList.add('btn');
    button.classList.add('btn-primary');
  
    button.addEventListener('click', function() {
        validate_selections(button);
    });
  
    return button;
}

function validate_selections(button) {
    var save_button = button;
    save_button.disabled = true;

    // Gather Selections
    let selections = [];
    document.querySelectorAll('#import-csv-table-column-select').forEach(function(select) {
        let selection = {
            'field' : select.dataset.field,
            'value' : select.value 
        };
        selections.push(selection);
    });

    // Filter Selections
    let item_name_selections = selections.filter(selection => selection.value === "1");
    let item_amount_selections = selections.filter(selection => selection.value === "2");


    // ERRORS - No item name field selected
    if (item_name_selections.length == 0) {
        document.querySelector('#save-items-error-message').innerHTML = "Select an Item Name column!";
        save_button.disabled = false;
        return false;
    }

    // Retrieve Data from Local Storage
    let data_text = localStorage.getItem('data');
    let data = JSON.parse(data_text); // console.log(data)

    // Map Selections to Item.Properties
    let items = data.map(item =>{
        let properites = {
            "name": ''
        };
        for (let i = 0; i < item_name_selections.length; i++) {
            name_column_key = item_name_selections[i].field;
            properites["name"] += item[name_column_key];
            properites["name"] += ' ';
        }
        if (item_amount_selections.length) {
            amount_column_key = item_amount_selections[0].field;
            properites["amount"] = item[amount_column_key]
        }
        return properites;
    });
    console.log(items);
    
    import_items(items);
}

function import_items(items) {

    // csrf token from cookie
    const csrftoken = getCookie('csrftoken');

    new_list_array = [
        { 'name':'Import', 'type': 'AD', 'items': items},
        { 'name':'Start' },
        { 'name':'End' }
    ]
        
    // Import Lists & Items
    store_id = document.querySelector('#title').dataset.store_id;
    const path = '/import_items/' + store_id;
    fetch(path, {
        method: 'POST',
        body: JSON.stringify(new_list_array),
        headers: { 'X-CSRFToken': csrftoken },
        mode: 'same-origin',
    })
    .then(response => response.json())
    .then(result => {
        // Print result
        console.log(result);
  
        // Update Template
        fetch_items();
    })
    // Catch any errors and log them to the console
    .catch(error => {
      console.log('Error:', error);
    });
}

function export_csv(export_csv_button) {

    export_csv_button.disabled = true;
    
    // file_name
    var title = document.querySelector('#title').innerText;
    var file_name = title + ".csv";

    // fields
    let lists = JSON.parse(localStorage.getItem('lists')); 
    let fields = ['Item'];
    lists.forEach(list =>{
        fields.push(list.name);
    })
    console.log(fields);

    // data
    let items = JSON.parse(localStorage.getItem('items')); 
    var data = [];
    items.forEach(item =>{
        const result = [item.name];
        for (var j = 0, list; list = lists[j]; j++) {

            const list_item = item.list_items.find((list_item) => list_item.list_id == list.id);
            if (typeof list_item !== "undefined") {
                result.push(list_item.amount);
            }
            else {
                result.push('');
            }
        }
        data.push(result);
    });
    console.log(data);


    // parse data
    var csv = Papa.unparse({
        fields: fields,
        data: data,
    });
    console.log(csv);

    download_csv_link(file_name, csv);
}

function download_csv_link(file_name, csv) {

    // 
    const link = document.createElement('a');
    link.textContent = 'Download';
    link.classList.add('btn', 'btn-primary');
    link.classList.add('col-md-6', 'col-lg-6', 'col-xl-6');
    link.setAttribute('target', "_blank");
    link.setAttribute('download', file_name);
    link.href = 'data:text/csv;charset=utf-8,' + encodeURI(csv);

    document.querySelector('#export-csv-view').append(link);
    document.querySelector('#delete-store-view').style.display = 'none';
  
    link.addEventListener('click', function() {
        link.onclick = function(event) {
            event.preventDefault();
        }

        reset_buttons();
    });

    const reset_buttons = async () => {
        await delay(1800);
        document.querySelector('#delete-store-view').style.display = 'block';
        document.querySelector('#export-csv-button').disabled = false;
        link.remove();
    };
    const delay = ms => new Promise(res => setTimeout(res, ms));
  
    return link;
}



// ************** COOKIE **************** 

function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}